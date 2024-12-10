use std::sync::Arc;

use anyhow::{Ok, Result};
use state_store::IndexifyState;
use tokio::{self, sync::watch::Receiver};
use tracing::{error, info, info_span};

pub struct SystemTasksExecutor {
    state: Arc<IndexifyState>,
    rx: tokio::sync::watch::Receiver<()>,
    shutdown_rx: Receiver<()>,
}

const MAX_PENDING_TASKS: usize = 10;

impl SystemTasksExecutor {
    pub fn new(state: Arc<IndexifyState>, shutdown_rx: Receiver<()>) -> Self {
        let rx = state.get_system_tasks_watcher();
        Self {
            state,
            rx,
            shutdown_rx,
        }
    }

    pub async fn start(&mut self) -> Result<()> {
        loop {
            // executing a first run on startup
            if let Err(err) = self.run().await {
                error!("error processing system tasks work: {:?}", err);
            }
            tokio::select! {
                _ = self.rx.changed() => {
                       self.rx.borrow_and_update();
                },
                _ = self.shutdown_rx.changed() => {
                    info!("system tasks executor shutting down");
                    break;
                }
            }
        }
        Ok(())
    }

    pub async fn run(&mut self) -> Result<()> {
        // TODO: support concurrent running system tasks
        let (tasks, _) = self.state.reader().get_system_tasks(Some(1))?;

        if let Some(task) = tasks.first() {
            let task_span = info_span!("system_task", task = task.key(), "type" = "replay");
            let _span_guard = task_span.enter();

            // Check if first current system task can be completed.
            if task.waiting_for_running_invocations {
                self.handle_completion(&task.namespace, &task.compute_graph_name)
                    .await?;
                return Ok(());
            }

            let pending_tasks = self.state.reader().get_pending_system_tasks()?;
            if pending_tasks >= MAX_PENDING_TASKS {
                info!(pending_tasks = pending_tasks, "max pending tasks reached");
                return Ok(());
            }

            let all_queued = self.queue_invocations(task, pending_tasks).await?;
            // handle completion right away if all invocations are completed
            if all_queued {
                self.handle_completion(&task.namespace, &task.compute_graph_name)
                    .await?
            }
        } else {
            info!("no system tasks to process");
        }

        Ok(())
    }

    async fn queue_invocations(
        &mut self,
        task: &data_model::SystemTask,
        pending_tasks: usize,
    ) -> Result<bool> {
        let (invocations, restart_key) = self.state.reader().list_invocations(
            &task.namespace,
            &task.compute_graph_name,
            task.restart_key.as_deref(),
            Some(MAX_PENDING_TASKS - pending_tasks),
        )?;

        info!(queuing = invocations.len(), "queueing invocations");

        self.state
            .write(state_store::requests::StateMachineUpdateRequest {
                payload: state_store::requests::RequestPayload::ReplayInvocations(
                    state_store::requests::ReplayInvocationsRequest {
                        namespace: task.namespace.clone(),
                        compute_graph_name: task.compute_graph_name.clone(),
                        graph_version: task.graph_version,
                        invocation_ids: invocations.iter().map(|i| i.id.clone()).collect(),
                        restart_key: restart_key.clone(),
                    },
                ),
                state_changes_processed: vec![],
            })
            .await?;

        Ok(restart_key.is_none())
    }

    async fn handle_completion(&mut self, namespace: &str, compute_graph_name: &str) -> Result<()> {
        if let Some(task) = self
            .state
            .reader()
            .get_system_task(namespace, compute_graph_name)?
        {
            if task.num_running_invocations == 0 {
                info!("completed",);
                // remove the task if reached the end of invocations column
                self.state
                    .write(state_store::requests::StateMachineUpdateRequest {
                        payload: state_store::requests::RequestPayload::RemoveSystemTask(
                            state_store::requests::RemoveSystemTaskRequest {
                                namespace: task.namespace.clone(),
                                compute_graph_name: task.compute_graph_name.clone(),
                            },
                        ),
                        state_changes_processed: vec![],
                    })
                    .await?;
            } else {
                info!(
                    running_invocations = task.num_running_invocations,
                    "waiting for all invotations to finish before completing the task",
                );
                // Mark task as completing so that it gets removed on last finished invocation.
                if !task.waiting_for_running_invocations {
                    self.state
                        .write(state_store::requests::StateMachineUpdateRequest {
                            payload: state_store::requests::RequestPayload::UpdateSystemTask(
                                state_store::requests::UpdateSystemTaskRequest {
                                    namespace: task.namespace.clone(),
                                    compute_graph_name: task.compute_graph_name.clone(),
                                    waiting_for_running_invocations: true,
                                },
                            ),
                            state_changes_processed: vec![],
                        })
                        .await?;
                }
            }
        };

        Ok(())
    }
}

#[cfg(test)]
mod tests {

    use data_model::{
        test_objects::tests::{
            mock_graph_a,
            mock_invocation_payload,
            TEST_EXECUTOR_ID,
            TEST_NAMESPACE,
        },
        DataPayload,
        ExecutorId,
        InvocationPayload,
        InvocationPayloadBuilder,
        NodeOutput,
        NodeOutputBuilder,
        OutputPayload,
        TaskId,
        TaskOutcome,
    };
    use metrics::scheduler_stats;
    use rand::Rng;
    use state_store::requests::{
        CreateOrUpdateComputeGraphRequest,
        FinalizeTaskRequest,
        InvokeComputeGraphRequest,
        ReplayComputeGraphRequest,
        RequestPayload,
        StateMachineUpdateRequest,
    };
    use tracing::subscriber;
    use tracing_subscriber::{layer::SubscriberExt, Layer};
    use uuid::Uuid;

    use super::*;
    use crate::scheduler::Scheduler;

    fn generate_random_hash() -> String {
        let mut rng = rand::thread_rng();
        let bytes: [u8; 32] = rng.gen();
        hex::encode(bytes)
    }

    fn mock_node_fn_output(invocation_id: &str, graph: &str, compute_fn_name: &str) -> NodeOutput {
        NodeOutputBuilder::default()
            .namespace(TEST_NAMESPACE.to_string())
            .compute_fn_name(compute_fn_name.to_string())
            .compute_graph_name(graph.to_string())
            .invocation_id(invocation_id.to_string())
            .payload(OutputPayload::Fn(DataPayload {
                sha256_hash: generate_random_hash(),
                path: Uuid::new_v4().to_string(),
                size: 12,
            }))
            .build()
            .unwrap()
    }

    fn make_finalize_request(
        namespace: &str,
        compute_graph: &str,
        invocation_id: &str,
        compute_fn_name: &str,
        task_id: &TaskId,
    ) -> FinalizeTaskRequest {
        FinalizeTaskRequest {
            namespace: namespace.to_string(),
            compute_graph: compute_graph.to_string(),
            compute_fn: compute_fn_name.to_string(),
            invocation_id: invocation_id.to_string(),
            task_id: task_id.clone(),
            node_outputs: vec![mock_node_fn_output(
                invocation_id,
                compute_graph,
                compute_fn_name,
            )],
            task_outcome: TaskOutcome::Success,
            executor_id: ExecutorId::new(TEST_EXECUTOR_ID.to_string()),
            diagnostics: None,
        }
    }

    #[tokio::test]
    async fn test_graph_replay() -> Result<()> {
        let env_filter = tracing_subscriber::EnvFilter::try_from_default_env()
            .unwrap_or_else(|_| tracing_subscriber::EnvFilter::new("info"));
        let _ = subscriber::set_global_default(
            tracing_subscriber::registry()
                .with(tracing_subscriber::fmt::layer().with_filter(env_filter)),
        );

        let temp_dir = tempfile::tempdir().unwrap();
        let state = IndexifyState::new(temp_dir.path().join("state"))
            .await
            .unwrap();
        let shutdown_rx = tokio::sync::watch::channel(()).1;
        let scheduler = Scheduler::new(
            state.clone(),
            Arc::new(scheduler_stats::Metrics::new(state.metrics.clone())),
        );
        let mut executor = SystemTasksExecutor::new(state.clone(), shutdown_rx);

        let graph = mock_graph_a(None);
        let cg_request = CreateOrUpdateComputeGraphRequest {
            namespace: graph.namespace.clone(),
            compute_graph: graph.clone(),
        };
        state
            .write(StateMachineUpdateRequest {
                payload: RequestPayload::CreateOrUpdateComputeGraph(cg_request),
                state_changes_processed: vec![],
            })
            .await
            .unwrap();
        let invocation_payload = mock_invocation_payload();
        let request = InvokeComputeGraphRequest {
            namespace: graph.namespace.clone(),
            compute_graph_name: graph.name.clone(),
            invocation_payload: invocation_payload.clone(),
        };
        state
            .write(StateMachineUpdateRequest {
                payload: RequestPayload::InvokeComputeGraph(request),
                state_changes_processed: vec![],
            })
            .await
            .unwrap();

        scheduler.run_scheduler().await?;

        let tasks = state
            .reader()
            .list_tasks_by_compute_graph(
                &graph.namespace,
                &graph.name,
                &invocation_payload.id,
                None,
                None,
            )
            .unwrap()
            .0;
        assert_eq!(tasks.len(), 1);
        let task = &tasks[0];

        let request = make_finalize_request(
            &graph.namespace,
            &graph.name,
            &invocation_payload.id,
            &task.compute_fn_name,
            &task.id,
        );
        state
            .write(StateMachineUpdateRequest {
                payload: RequestPayload::FinalizeTask(request),
                state_changes_processed: vec![],
            })
            .await?;
        scheduler.run_scheduler().await?;
        let tasks = state
            .reader()
            .list_tasks_by_compute_graph(
                &graph.namespace,
                &graph.name,
                &invocation_payload.id,
                None,
                None,
            )
            .unwrap()
            .0;
        assert_eq!(tasks.len(), 3);
        let incomplete_tasks = tasks.iter().filter(|t| t.outcome == TaskOutcome::Unknown);
        assert_eq!(incomplete_tasks.clone().count(), 2);

        for task in incomplete_tasks {
            let request = make_finalize_request(
                &graph.namespace,
                &graph.name,
                &invocation_payload.id,
                &task.compute_fn_name,
                &task.id,
            );
            info!("complete task {:?}", task);
            state
                .write(StateMachineUpdateRequest {
                    payload: RequestPayload::FinalizeTask(request),
                    state_changes_processed: vec![],
                })
                .await?;
        }
        scheduler.run_scheduler().await?;
        assert_eq!(tasks.len(), 3);
        let tasks = state
            .reader()
            .list_tasks_by_compute_graph(
                &graph.namespace,
                &graph.name,
                &invocation_payload.id,
                None,
                None,
            )
            .unwrap()
            .0;
        let incomplete_tasks = tasks.iter().filter(|t| t.outcome == TaskOutcome::Unknown);
        assert_eq!(incomplete_tasks.clone().count(), 0);

        scheduler.run_scheduler().await?;

        let state_changes = state.reader().get_unprocessed_state_changes()?;
        assert_eq!(state_changes.len(), 0);

        let graph_ctx =
            state
                .reader()
                .invocation_ctx(&graph.namespace, &graph.name, &invocation_payload.id)?;
        assert_eq!(graph_ctx.unwrap().outstanding_tasks, 0);

        let request = RequestPayload::ReplayComputeGraph(ReplayComputeGraphRequest {
            namespace: graph.namespace.clone(),
            compute_graph_name: graph.name.clone(),
        });
        state
            .write(StateMachineUpdateRequest {
                payload: request,
                state_changes_processed: vec![],
            })
            .await?;

        let system_tasks = state.reader().get_system_tasks(None).unwrap().0;
        assert_eq!(system_tasks.len(), 1);
        let system_task = &system_tasks[0];
        assert_eq!(system_task.namespace, graph.namespace);
        assert_eq!(system_task.compute_graph_name, graph.name);

        executor.run().await?;

        // Since graph version is the same it should generate new tasks
        let state_changes = state.reader().get_unprocessed_state_changes()?;
        assert_eq!(state_changes.len(), 0);

        let system_tasks = state.reader().get_system_tasks(None).unwrap().0;
        assert_eq!(system_tasks.len(), 0);

        // Update graph so version is incremented
        let mut graph = graph;
        graph.code.sha256_hash = generate_random_hash();

        let cg_request = CreateOrUpdateComputeGraphRequest {
            namespace: graph.namespace.clone(),
            compute_graph: graph.clone(),
        };
        state
            .write(StateMachineUpdateRequest {
                payload: RequestPayload::CreateOrUpdateComputeGraph(cg_request),
                state_changes_processed: vec![],
            })
            .await
            .unwrap();

        let (graphs, _) = state
            .reader()
            .list_compute_graphs(&graph.namespace, None, None)?;
        assert_eq!(graphs.len(), 1);
        assert_eq!(graphs[0].version, graph.version.next());

        let graph = graphs[0].clone();

        let request = RequestPayload::ReplayComputeGraph(ReplayComputeGraphRequest {
            namespace: graph.namespace.clone(),
            compute_graph_name: graph.name.clone(),
        });
        state
            .write(StateMachineUpdateRequest {
                payload: request,
                state_changes_processed: vec![],
            })
            .await?;

        let system_tasks = state.reader().get_system_tasks(None).unwrap().0;
        assert_eq!(system_tasks.len(), 1);
        let system_task = &system_tasks[0];
        assert_eq!(system_task.namespace, graph.namespace);
        assert_eq!(system_task.compute_graph_name, graph.name);

        executor.run().await?;

        // task should still exist since there are still invocations to process
        let system_tasks = state.reader().get_system_tasks(None).unwrap().0;
        assert_eq!(system_tasks.len(), 1);

        // Since graph version is different new changes should be generated
        let state_changes = state.reader().get_unprocessed_state_changes()?;
        assert_eq!(state_changes.len(), 1);

        // Number of pending system tasks should be incremented
        let num_pending_tasks = state.reader().get_pending_system_tasks()?;
        assert_eq!(num_pending_tasks, 1);

        scheduler.run_scheduler().await?;

        let tasks = state
            .reader()
            .list_tasks_by_compute_graph(
                &graph.namespace,
                &graph.name,
                &invocation_payload.id,
                None,
                None,
            )
            .unwrap()
            .0;
        let incomplete_tasks = tasks.iter().filter(|t| t.outcome == TaskOutcome::Unknown);
        assert_eq!(incomplete_tasks.clone().count(), 1);

        for task in incomplete_tasks {
            let request = make_finalize_request(
                &graph.namespace,
                &graph.name,
                &invocation_payload.id,
                &task.compute_fn_name,
                &task.id,
            );
            info!("complete task {:?} req {:?}", task, request);
            state
                .write(StateMachineUpdateRequest {
                    payload: RequestPayload::FinalizeTask(request),
                    state_changes_processed: vec![],
                })
                .await?;
        }

        scheduler.run_scheduler().await?;
        let tasks = state
            .reader()
            .list_tasks_by_compute_graph(
                &graph.namespace,
                &graph.name,
                &invocation_payload.id,
                None,
                None,
            )
            .unwrap()
            .0;
        let incomplete_tasks = tasks.iter().filter(|t| t.outcome == TaskOutcome::Unknown);
        assert_eq!(incomplete_tasks.clone().count(), 2);

        for task in incomplete_tasks {
            let request = make_finalize_request(
                &graph.namespace,
                &graph.name,
                &invocation_payload.id,
                &task.compute_fn_name,
                &task.id,
            );
            info!("complete task {:?}", task);
            state
                .write(StateMachineUpdateRequest {
                    payload: RequestPayload::FinalizeTask(request),
                    state_changes_processed: vec![],
                })
                .await?;
        }
        scheduler.run_scheduler().await?;
        let tasks = state
            .reader()
            .list_tasks_by_compute_graph(
                &graph.namespace,
                &graph.name,
                &invocation_payload.id,
                None,
                None,
            )
            .unwrap()
            .0;
        let incomplete_tasks = tasks.iter().filter(|t| t.outcome == TaskOutcome::Unknown);
        assert_eq!(incomplete_tasks.clone().count(), 0);

        scheduler.run_scheduler().await?;

        let state_changes = state.reader().get_unprocessed_state_changes()?;
        assert_eq!(state_changes.len(), 0);

        // Number of pending system tasks should be decremented after graph completion
        let num_pending_tasks = state.reader().get_pending_system_tasks()?;
        assert_eq!(num_pending_tasks, 0);

        executor.run().await?;

        let system_tasks = state.reader().get_system_tasks(None).unwrap().0;
        assert_eq!(
            system_tasks.len(),
            0,
            "task should not exist anymore since all invocations are processed"
        );

        Ok(())
    }

    fn generate_invocation_payload(namespace: &str, graph: &str) -> InvocationPayload {
        InvocationPayloadBuilder::default()
            .namespace(namespace.to_string())
            .compute_graph_name(graph.to_string())
            .payload(DataPayload {
                path: "test".to_string(),
                size: 23,
                sha256_hash: generate_random_hash(),
            })
            .encoding("application/octet-stream".to_string())
            .build()
            .unwrap()
    }

    async fn finalize_incomplete_tasks(
        state: &IndexifyState,
        namespace: &str,
    ) -> Result<(), anyhow::Error> {
        let tasks = state
            .reader()
            .list_tasks_by_namespace(namespace, None, None)
            .unwrap()
            .0;
        let incomplete_tasks = tasks.iter().filter(|t| t.outcome == TaskOutcome::Unknown);
        for task in incomplete_tasks {
            let request = make_finalize_request(
                &task.namespace,
                &task.compute_graph_name,
                task.invocation_id.as_str(),
                &task.compute_fn_name,
                &task.id,
            );
            state
                .write(StateMachineUpdateRequest {
                    payload: RequestPayload::FinalizeTask(request),
                    state_changes_processed: vec![],
                })
                .await?;
        }

        Ok(())
    }

    // test creating more tasks than MAX_PENDING_TASKS
    // tasks in progress should stays at or below MAX_PENDING_TASKS
    // all tasks should complete eventually
    #[tokio::test]
    async fn test_graph_flow_control_replay() -> Result<()> {
        let env_filter = tracing_subscriber::EnvFilter::try_from_default_env()
            .unwrap_or_else(|_| tracing_subscriber::EnvFilter::new("info"));
        let _ = subscriber::set_global_default(
            tracing_subscriber::registry()
                .with(tracing_subscriber::fmt::layer().with_filter(env_filter)),
        );

        let temp_dir = tempfile::tempdir().unwrap();
        let state = IndexifyState::new(temp_dir.path().join("state"))
            .await
            .unwrap();
        let shutdown_rx = tokio::sync::watch::channel(()).1;
        let scheduler = Scheduler::new(
            state.clone(),
            Arc::new(scheduler_stats::Metrics::new(state.metrics.clone())),
        );
        let mut executor = SystemTasksExecutor::new(state.clone(), shutdown_rx);

        let graph = mock_graph_a(None);
        let cg_request = CreateOrUpdateComputeGraphRequest {
            namespace: graph.namespace.clone(),
            compute_graph: graph.clone(),
        };
        state
            .write(StateMachineUpdateRequest {
                payload: RequestPayload::CreateOrUpdateComputeGraph(cg_request),
                state_changes_processed: vec![],
            })
            .await
            .unwrap();

        for _ in 0..MAX_PENDING_TASKS * 3 {
            let request = InvokeComputeGraphRequest {
                namespace: graph.namespace.clone(),
                compute_graph_name: graph.name.clone(),
                invocation_payload: generate_invocation_payload(&graph.namespace, &graph.name),
            };
            state
                .write(StateMachineUpdateRequest {
                    payload: RequestPayload::InvokeComputeGraph(request),
                    state_changes_processed: vec![],
                })
                .await
                .unwrap();
        }

        scheduler.run_scheduler().await?;

        loop {
            finalize_incomplete_tasks(&state, &graph.namespace).await?;

            scheduler.run_scheduler().await?;
            let tasks = state
                .reader()
                .list_tasks_by_namespace(&graph.namespace, None, None)
                .unwrap()
                .0;
            let incomplete_tasks = tasks.iter().filter(|t| t.outcome == TaskOutcome::Unknown);
            let state_changes = state.reader().get_unprocessed_state_changes()?;
            if state_changes.is_empty() && incomplete_tasks.count() == 0 {
                break;
            }
        }

        // Update graph so version is incremented
        let mut graph = graph;
        graph.code.sha256_hash = generate_random_hash();

        let cg_request = CreateOrUpdateComputeGraphRequest {
            namespace: graph.namespace.clone(),
            compute_graph: graph.clone(),
        };
        state
            .write(StateMachineUpdateRequest {
                payload: RequestPayload::CreateOrUpdateComputeGraph(cg_request),
                state_changes_processed: vec![],
            })
            .await
            .unwrap();

        let (graphs, _) = state
            .reader()
            .list_compute_graphs(&graph.namespace, None, None)?;
        assert_eq!(graphs.len(), 1);
        assert_eq!(graphs[0].version, graph.version.next());

        let graph = graphs[0].clone();

        let request = RequestPayload::ReplayComputeGraph(ReplayComputeGraphRequest {
            namespace: graph.namespace.clone(),
            compute_graph_name: graph.name.clone(),
        });
        state
            .write(StateMachineUpdateRequest {
                payload: request,
                state_changes_processed: vec![],
            })
            .await?;

        let system_tasks = state.reader().get_system_tasks(None).unwrap().0;
        assert_eq!(system_tasks.len(), 1);
        let system_task = &system_tasks[0];
        assert_eq!(system_task.namespace, graph.namespace);
        assert_eq!(system_task.compute_graph_name, graph.name);

        loop {
            executor.run().await?;

            let num_pending_tasks = state.reader().get_pending_system_tasks()?;
            info!("num pending tasks {:?}", num_pending_tasks);
            assert!(num_pending_tasks <= MAX_PENDING_TASKS);

            scheduler.run_scheduler().await?;

            finalize_incomplete_tasks(&state, &graph.namespace).await?;

            let tasks = state
                .reader()
                .list_tasks_by_namespace(&graph.namespace, None, None)
                .unwrap()
                .0;
            let num_incomplete_tasks = tasks
                .iter()
                .filter(|t| t.outcome == TaskOutcome::Unknown)
                .count();

            let system_tasks = state.reader().get_system_tasks(None).unwrap().0;

            let state_changes = state.reader().get_unprocessed_state_changes()?;
            if state_changes.is_empty() && num_incomplete_tasks == 0 && system_tasks.is_empty() {
                break;
            }
        }

        // Verify that all outputs are initialized with correct graph version
        let invocations = state
            .reader()
            .list_invocations(&graph.namespace, &graph.name, None, None)?
            .0;
        for invocation in invocations {
            let invocation_ctx = state
                .reader()
                .invocation_ctx(&graph.namespace, &graph.name, &invocation.id)?
                .unwrap();
            assert!(invocation_ctx.graph_version == graph.version);
        }

        Ok(())
    }
}
