from typing import Optional

import nanoid
import structlog
from httpx import Timeout
from pydantic import BaseModel

from indexify.common_util import get_httpx_client
from indexify.executor.api_objects import RouterOutput as ApiRouterOutput
from indexify.executor.api_objects import TaskResult
from indexify.executor.task_store import CompletedTask

logger = structlog.get_logger(__name__)


# https://github.com/psf/requests/issues/1081#issuecomment-428504128
class ForceMultipartDict(dict):
    def __bool__(self):
        return True


FORCE_MULTIPART = ForceMultipartDict()
UTF_8_CONTENT_TYPE = "application/octet-stream"


class ReportingData(BaseModel):
    output_count: int = 0
    output_total_bytes: int = 0
    stdout_count: int = 0
    stdout_total_bytes: int = 0
    stderr_count: int = 0
    stderr_total_bytes: int = 0


class TaskReporter:
    def __init__(
        self, base_url: str, executor_id: str, config_path: Optional[str] = None
    ):
        self._base_url = base_url
        self._executor_id = executor_id
        self._client = get_httpx_client(config_path)

    def report_task_outcome(self, completed_task: CompletedTask):
        report = ReportingData()
        fn_outputs = []

        if completed_task.function_output:
            for output in completed_task.function_output.outputs or []:
                payload = output.bytes if output.HasField("bytes") else output.string
                fn_outputs.append(
                    (
                        "node_outputs",
                        (nanoid.generate(), payload, output.content_type),
                    )
                )
                report.output_count += 1
                report.output_total_bytes += len(payload)

        if completed_task.stdout:
            fn_outputs.append(
                (
                    "stdout",
                    (
                        nanoid.generate(),
                        completed_task.stdout.encode(),
                        UTF_8_CONTENT_TYPE,
                    ),
                )
            )
            report.stdout_count += 1
            report.stdout_total_bytes += len(completed_task.stdout)

        if completed_task.stderr:
            fn_outputs.append(
                (
                    "stderr",
                    (
                        nanoid.generate(),
                        completed_task.stderr.encode(),
                        UTF_8_CONTENT_TYPE,
                    ),
                )
            )
            report.stderr_count += 1
            report.stderr_total_bytes += len(completed_task.stderr)

        router_output = (
            ApiRouterOutput(edges=completed_task.router_output.edges)
            if completed_task.router_output
            else None
        )

        task_result = TaskResult(
            router_output=router_output,
            outcome=completed_task.task_outcome,
            namespace=completed_task.task.namespace,
            compute_graph=completed_task.task.compute_graph,
            compute_fn=completed_task.task.compute_fn,
            invocation_id=completed_task.task.invocation_id,
            executor_id=self._executor_id,
            task_id=completed_task.task.id,
            reducer=completed_task.reducer,
        )
        task_result_data = task_result.model_dump_json(exclude_none=True)

        total_bytes = (
            report.output_total_bytes
            + report.stdout_total_bytes
            + report.stderr_total_bytes
        )

        logger.info(
            "reporting task outcome",
            task_id=completed_task.task.id,
            retries=completed_task.reporting_retries,
            total_bytes=total_bytes,
            total_files=report.output_count + report.stdout_count + report.stderr_count,
            output_files=report.output_count,
            output_bytes=total_bytes,
            stdout_bytes=report.stdout_total_bytes,
            stderr_bytes=report.stderr_total_bytes,
        )
        #
        kwargs = {
            "data": {"task_result": task_result_data},
            # Use httpx default timeout of 5s for all timeout types.
            # For read timeouts, use 5 minutes to allow for large file uploads.
            "timeout": Timeout(
                5.0,
                read=5.0 * 60,
            ),
        }
        if fn_outputs and len(fn_outputs) > 0:
            kwargs["files"] = fn_outputs
        else:
            kwargs["files"] = FORCE_MULTIPART

        response = self._client.post(
            url=f"{self._base_url}/internal/ingest_files",
            **kwargs,
        )

        try:
            response.raise_for_status()
        except Exception as e:
            # Caller catches and logs the exception.
            # Log response details here for easier debugging.
            logger.error(
                "failed to report task outcome",
                task_id=completed_task.task.id,
                retries=completed_task.reporting_retries,
                status_code=response.status_code,
                response_text=response.text,
            )
            raise e
