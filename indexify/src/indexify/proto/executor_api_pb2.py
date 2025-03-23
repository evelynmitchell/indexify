# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: indexify/proto/executor_api.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC, 5, 29, 0, "", "indexify/proto/executor_api.proto"
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n!indexify/proto/executor_api.proto\x12\x0f\x65xecutor_api_pb"e\n\x0cGPUResources\x12\x12\n\x05\x63ount\x18\x01 \x01(\rH\x00\x88\x01\x01\x12-\n\x05model\x18\x02 \x01(\x0e\x32\x19.executor_api_pb.GPUModelH\x01\x88\x01\x01\x42\x08\n\x06_countB\x08\n\x06_model"\xc2\x01\n\rHostResources\x12\x16\n\tcpu_count\x18\x01 \x01(\rH\x00\x88\x01\x01\x12\x19\n\x0cmemory_bytes\x18\x02 \x01(\x04H\x01\x88\x01\x01\x12\x17\n\ndisk_bytes\x18\x03 \x01(\x04H\x02\x88\x01\x01\x12/\n\x03gpu\x18\x04 \x01(\x0b\x32\x1d.executor_api_pb.GPUResourcesH\x03\x88\x01\x01\x42\x0c\n\n_cpu_countB\x0f\n\r_memory_bytesB\r\n\x0b_disk_bytesB\x06\n\x04_gpu"\xbb\x01\n\x0f\x41llowedFunction\x12\x16\n\tnamespace\x18\x01 \x01(\tH\x00\x88\x01\x01\x12\x17\n\ngraph_name\x18\x02 \x01(\tH\x01\x88\x01\x01\x12\x1a\n\rfunction_name\x18\x03 \x01(\tH\x02\x88\x01\x01\x12\x1a\n\rgraph_version\x18\x04 \x01(\tH\x03\x88\x01\x01\x42\x0c\n\n_namespaceB\r\n\x0b_graph_nameB\x10\n\x0e_function_nameB\x10\n\x0e_graph_version"\xb1\x03\n\x1b\x46unctionExecutorDescription\x12\x0f\n\x02id\x18\x01 \x01(\tH\x00\x88\x01\x01\x12\x16\n\tnamespace\x18\x02 \x01(\tH\x01\x88\x01\x01\x12\x17\n\ngraph_name\x18\x03 \x01(\tH\x02\x88\x01\x01\x12\x1a\n\rgraph_version\x18\x04 \x01(\tH\x03\x88\x01\x01\x12\x1a\n\rfunction_name\x18\x05 \x01(\tH\x04\x88\x01\x01\x12\x16\n\timage_uri\x18\x06 \x01(\tH\x05\x88\x01\x01\x12\x14\n\x0csecret_names\x18\x07 \x03(\t\x12<\n\x0fresource_limits\x18\x08 \x01(\x0b\x32\x1e.executor_api_pb.HostResourcesH\x06\x88\x01\x01\x12%\n\x18\x63ustomer_code_timeout_ms\x18\t \x01(\rH\x07\x88\x01\x01\x42\x05\n\x03_idB\x0c\n\n_namespaceB\r\n\x0b_graph_nameB\x10\n\x0e_graph_versionB\x10\n\x0e_function_nameB\x0c\n\n_image_uriB\x12\n\x10_resource_limitsB\x1b\n\x19_customer_code_timeout_ms"\xe8\x01\n\x15\x46unctionExecutorState\x12\x46\n\x0b\x64\x65scription\x18\x01 \x01(\x0b\x32,.executor_api_pb.FunctionExecutorDescriptionH\x00\x88\x01\x01\x12<\n\x06status\x18\x02 \x01(\x0e\x32\'.executor_api_pb.FunctionExecutorStatusH\x01\x88\x01\x01\x12\x1b\n\x0estatus_message\x18\x03 \x01(\tH\x02\x88\x01\x01\x42\x0e\n\x0c_descriptionB\t\n\x07_statusB\x11\n\x0f_status_message"\x9f\x05\n\rExecutorState\x12\x18\n\x0b\x65xecutor_id\x18\x01 \x01(\tH\x00\x88\x01\x01\x12\x1d\n\x10\x64\x65velopment_mode\x18\x02 \x01(\x08H\x01\x88\x01\x01\x12\x15\n\x08hostname\x18\x03 \x01(\tH\x02\x88\x01\x01\x12\x34\n\x06\x66lavor\x18\x04 \x01(\x0e\x32\x1f.executor_api_pb.ExecutorFlavorH\x03\x88\x01\x01\x12\x14\n\x07version\x18\x05 \x01(\tH\x04\x88\x01\x01\x12\x34\n\x06status\x18\x06 \x01(\x0e\x32\x1f.executor_api_pb.ExecutorStatusH\x05\x88\x01\x01\x12;\n\x0e\x66ree_resources\x18\x07 \x01(\x0b\x32\x1e.executor_api_pb.HostResourcesH\x06\x88\x01\x01\x12;\n\x11\x61llowed_functions\x18\x08 \x03(\x0b\x32 .executor_api_pb.AllowedFunction\x12H\n\x18\x66unction_executor_states\x18\t \x03(\x0b\x32&.executor_api_pb.FunctionExecutorState\x12:\n\x06labels\x18\n \x03(\x0b\x32*.executor_api_pb.ExecutorState.LabelsEntry\x12\x17\n\nstate_hash\x18\x0b \x01(\tH\x07\x88\x01\x01\x1a-\n\x0bLabelsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\x42\x0e\n\x0c_executor_idB\x13\n\x11_development_modeB\x0b\n\t_hostnameB\t\n\x07_flavorB\n\n\x08_versionB\t\n\x07_statusB\x11\n\x0f_free_resourcesB\r\n\x0b_state_hash"l\n\x1aReportExecutorStateRequest\x12;\n\x0e\x65xecutor_state\x18\x01 \x01(\x0b\x32\x1e.executor_api_pb.ExecutorStateH\x00\x88\x01\x01\x42\x11\n\x0f_executor_state"\x1d\n\x1bReportExecutorStateResponse"\x88\x03\n\x04Task\x12\x0f\n\x02id\x18\x01 \x01(\tH\x00\x88\x01\x01\x12\x16\n\tnamespace\x18\x02 \x01(\tH\x01\x88\x01\x01\x12\x17\n\ngraph_name\x18\x03 \x01(\tH\x02\x88\x01\x01\x12\x1a\n\rgraph_version\x18\x04 \x01(\tH\x03\x88\x01\x01\x12\x1a\n\rfunction_name\x18\x05 \x01(\tH\x04\x88\x01\x01\x12 \n\x13graph_invocation_id\x18\x06 \x01(\tH\x05\x88\x01\x01\x12\x16\n\tinput_key\x18\x08 \x01(\tH\x06\x88\x01\x01\x12\x1f\n\x12reducer_output_key\x18\t \x01(\tH\x07\x88\x01\x01\x12\x17\n\ntimeout_ms\x18\n \x01(\rH\x08\x88\x01\x01\x42\x05\n\x03_idB\x0c\n\n_namespaceB\r\n\x0b_graph_nameB\x10\n\x0e_graph_versionB\x10\n\x0e_function_nameB\x16\n\x14_graph_invocation_idB\x0c\n\n_input_keyB\x15\n\x13_reducer_output_keyB\r\n\x0b_timeout_ms"\x7f\n\x0eTaskAllocation\x12!\n\x14\x66unction_executor_id\x18\x01 \x01(\tH\x00\x88\x01\x01\x12(\n\x04task\x18\x02 \x01(\x0b\x32\x15.executor_api_pb.TaskH\x01\x88\x01\x01\x42\x17\n\x15_function_executor_idB\x07\n\x05_task"K\n\x1fGetDesiredExecutorStatesRequest\x12\x18\n\x0b\x65xecutor_id\x18\x01 \x01(\tH\x00\x88\x01\x01\x42\x0e\n\x0c_executor_id"\xb9\x01\n\x14\x44\x65siredExecutorState\x12H\n\x12\x66unction_executors\x18\x01 \x03(\x0b\x32,.executor_api_pb.FunctionExecutorDescription\x12\x39\n\x10task_allocations\x18\x02 \x03(\x0b\x32\x1f.executor_api_pb.TaskAllocation\x12\x12\n\x05\x63lock\x18\x03 \x01(\x04H\x00\x88\x01\x01\x42\x08\n\x06_clock"o\n\x0b\x44\x61taPayload\x12\x11\n\x04path\x18\x01 \x01(\tH\x00\x88\x01\x01\x12\x11\n\x04size\x18\x02 \x01(\x04H\x01\x88\x01\x01\x12\x18\n\x0bsha256_hash\x18\x03 \x01(\tH\x02\x88\x01\x01\x42\x07\n\x05_pathB\x07\n\x05_sizeB\x0e\n\x0c_sha256_hash"\x87\x06\n\x18ReportTaskOutcomeRequest\x12\x14\n\x07task_id\x18\x01 \x01(\tH\x00\x88\x01\x01\x12\x16\n\tnamespace\x18\x02 \x01(\tH\x01\x88\x01\x01\x12\x17\n\ngraph_name\x18\x03 \x01(\tH\x02\x88\x01\x01\x12\x1a\n\rfunction_name\x18\x04 \x01(\tH\x03\x88\x01\x01\x12 \n\x13graph_invocation_id\x18\x06 \x01(\tH\x04\x88\x01\x01\x12\x32\n\x07outcome\x18\x07 \x01(\x0e\x32\x1c.executor_api_pb.TaskOutcomeH\x05\x88\x01\x01\x12\x1a\n\rinvocation_id\x18\x08 \x01(\tH\x06\x88\x01\x01\x12\x18\n\x0b\x65xecutor_id\x18\t \x01(\tH\x07\x88\x01\x01\x12\x14\n\x07reducer\x18\n \x01(\x08H\x08\x88\x01\x01\x12\x16\n\x0enext_functions\x18\x0b \x03(\t\x12\x30\n\nfn_outputs\x18\x0c \x03(\x0b\x32\x1c.executor_api_pb.DataPayload\x12\x31\n\x06stdout\x18\x0e \x01(\x0b\x32\x1c.executor_api_pb.DataPayloadH\t\x88\x01\x01\x12\x31\n\x06stderr\x18\x0f \x01(\x0b\x32\x1c.executor_api_pb.DataPayloadH\n\x88\x01\x01\x12=\n\x0foutput_encoding\x18\r \x01(\x0e\x32\x1f.executor_api_pb.OutputEncodingH\x0b\x88\x01\x01\x12$\n\x17output_encoding_version\x18\x05 \x01(\x04H\x0c\x88\x01\x01\x42\n\n\x08_task_idB\x0c\n\n_namespaceB\r\n\x0b_graph_nameB\x10\n\x0e_function_nameB\x16\n\x14_graph_invocation_idB\n\n\x08_outcomeB\x10\n\x0e_invocation_idB\x0e\n\x0c_executor_idB\n\n\x08_reducerB\t\n\x07_stdoutB\t\n\x07_stderrB\x12\n\x10_output_encodingB\x1a\n\x18_output_encoding_version"\x1b\n\x19ReportTaskOutcomeResponse*\x86\x03\n\x08GPUModel\x12\x15\n\x11GPU_MODEL_UNKNOWN\x10\x00\x12"\n\x1eGPU_MODEL_NVIDIA_TESLA_T4_16GB\x10\n\x12$\n GPU_MODEL_NVIDIA_TESLA_V100_16GB\x10\x14\x12\x1d\n\x19GPU_MODEL_NVIDIA_A10_24GB\x10\x1e\x12\x1f\n\x1bGPU_MODEL_NVIDIA_A6000_48GB\x10(\x12#\n\x1fGPU_MODEL_NVIDIA_A100_SXM4_40GB\x10\x32\x12#\n\x1fGPU_MODEL_NVIDIA_A100_SXM4_80GB\x10\x33\x12"\n\x1eGPU_MODEL_NVIDIA_A100_PCI_40GB\x10\x34\x12#\n\x1fGPU_MODEL_NVIDIA_H100_SXM5_80GB\x10<\x12"\n\x1eGPU_MODEL_NVIDIA_H100_PCI_80GB\x10=\x12"\n\x1eGPU_MODEL_NVIDIA_RTX_6000_24GB\x10>*\xca\x03\n\x16\x46unctionExecutorStatus\x12$\n FUNCTION_EXECUTOR_STATUS_UNKNOWN\x10\x00\x12(\n$FUNCTION_EXECUTOR_STATUS_STARTING_UP\x10\x01\x12:\n6FUNCTION_EXECUTOR_STATUS_STARTUP_FAILED_CUSTOMER_ERROR\x10\x02\x12:\n6FUNCTION_EXECUTOR_STATUS_STARTUP_FAILED_PLATFORM_ERROR\x10\x03\x12!\n\x1d\x46UNCTION_EXECUTOR_STATUS_IDLE\x10\x04\x12)\n%FUNCTION_EXECUTOR_STATUS_RUNNING_TASK\x10\x05\x12&\n"FUNCTION_EXECUTOR_STATUS_UNHEALTHY\x10\x06\x12%\n!FUNCTION_EXECUTOR_STATUS_STOPPING\x10\x07\x12$\n FUNCTION_EXECUTOR_STATUS_STOPPED\x10\x08\x12%\n!FUNCTION_EXECUTOR_STATUS_SHUTDOWN\x10\t*\xc3\x01\n\x0e\x45xecutorStatus\x12\x1b\n\x17\x45XECUTOR_STATUS_UNKNOWN\x10\x00\x12\x1f\n\x1b\x45XECUTOR_STATUS_STARTING_UP\x10\x01\x12\x1b\n\x17\x45XECUTOR_STATUS_RUNNING\x10\x02\x12\x1b\n\x17\x45XECUTOR_STATUS_DRAINED\x10\x03\x12\x1c\n\x18\x45XECUTOR_STATUS_STOPPING\x10\x04\x12\x1b\n\x17\x45XECUTOR_STATUS_STOPPED\x10\x05*d\n\x0e\x45xecutorFlavor\x12\x1b\n\x17\x45XECUTOR_FLAVOR_UNKNOWN\x10\x00\x12\x17\n\x13\x45XECUTOR_FLAVOR_OSS\x10\x01\x12\x1c\n\x18\x45XECUTOR_FLAVOR_PLATFORM\x10\x02*[\n\x0bTaskOutcome\x12\x18\n\x14TASK_OUTCOME_UNKNOWN\x10\x00\x12\x18\n\x14TASK_OUTCOME_SUCCESS\x10\x01\x12\x18\n\x14TASK_OUTCOME_FAILURE\x10\x02*\x7f\n\x0eOutputEncoding\x12\x1b\n\x17OUTPUT_ENCODING_UNKNOWN\x10\x00\x12\x18\n\x14OUTPUT_ENCODING_JSON\x10\x01\x12\x1a\n\x16OUTPUT_ENCODING_PICKLE\x10\x02\x12\x1a\n\x16OUTPUT_ENCODING_BINARY\x10\x03\x32\xef\x02\n\x0b\x45xecutorAPI\x12t\n\x15report_executor_state\x12+.executor_api_pb.ReportExecutorStateRequest\x1a,.executor_api_pb.ReportExecutorStateResponse"\x00\x12z\n\x1bget_desired_executor_states\x12\x30.executor_api_pb.GetDesiredExecutorStatesRequest\x1a%.executor_api_pb.DesiredExecutorState"\x00\x30\x01\x12n\n\x13report_task_outcome\x12).executor_api_pb.ReportTaskOutcomeRequest\x1a*.executor_api_pb.ReportTaskOutcomeResponse"\x00\x62\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(
    DESCRIPTOR, "indexify.proto.executor_api_pb2", _globals
)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals["_EXECUTORSTATE_LABELSENTRY"]._loaded_options = None
    _globals["_EXECUTORSTATE_LABELSENTRY"]._serialized_options = b"8\001"
    _globals["_GPUMODEL"]._serialized_start = 3740
    _globals["_GPUMODEL"]._serialized_end = 4130
    _globals["_FUNCTIONEXECUTORSTATUS"]._serialized_start = 4133
    _globals["_FUNCTIONEXECUTORSTATUS"]._serialized_end = 4591
    _globals["_EXECUTORSTATUS"]._serialized_start = 4594
    _globals["_EXECUTORSTATUS"]._serialized_end = 4789
    _globals["_EXECUTORFLAVOR"]._serialized_start = 4791
    _globals["_EXECUTORFLAVOR"]._serialized_end = 4891
    _globals["_TASKOUTCOME"]._serialized_start = 4893
    _globals["_TASKOUTCOME"]._serialized_end = 4984
    _globals["_OUTPUTENCODING"]._serialized_start = 4986
    _globals["_OUTPUTENCODING"]._serialized_end = 5113
    _globals["_GPURESOURCES"]._serialized_start = 54
    _globals["_GPURESOURCES"]._serialized_end = 155
    _globals["_HOSTRESOURCES"]._serialized_start = 158
    _globals["_HOSTRESOURCES"]._serialized_end = 352
    _globals["_ALLOWEDFUNCTION"]._serialized_start = 355
    _globals["_ALLOWEDFUNCTION"]._serialized_end = 542
    _globals["_FUNCTIONEXECUTORDESCRIPTION"]._serialized_start = 545
    _globals["_FUNCTIONEXECUTORDESCRIPTION"]._serialized_end = 978
    _globals["_FUNCTIONEXECUTORSTATE"]._serialized_start = 981
    _globals["_FUNCTIONEXECUTORSTATE"]._serialized_end = 1213
    _globals["_EXECUTORSTATE"]._serialized_start = 1216
    _globals["_EXECUTORSTATE"]._serialized_end = 1887
    _globals["_EXECUTORSTATE_LABELSENTRY"]._serialized_start = 1724
    _globals["_EXECUTORSTATE_LABELSENTRY"]._serialized_end = 1769
    _globals["_REPORTEXECUTORSTATEREQUEST"]._serialized_start = 1889
    _globals["_REPORTEXECUTORSTATEREQUEST"]._serialized_end = 1997
    _globals["_REPORTEXECUTORSTATERESPONSE"]._serialized_start = 1999
    _globals["_REPORTEXECUTORSTATERESPONSE"]._serialized_end = 2028
    _globals["_TASK"]._serialized_start = 2031
    _globals["_TASK"]._serialized_end = 2423
    _globals["_TASKALLOCATION"]._serialized_start = 2425
    _globals["_TASKALLOCATION"]._serialized_end = 2552
    _globals["_GETDESIREDEXECUTORSTATESREQUEST"]._serialized_start = 2554
    _globals["_GETDESIREDEXECUTORSTATESREQUEST"]._serialized_end = 2629
    _globals["_DESIREDEXECUTORSTATE"]._serialized_start = 2632
    _globals["_DESIREDEXECUTORSTATE"]._serialized_end = 2817
    _globals["_DATAPAYLOAD"]._serialized_start = 2819
    _globals["_DATAPAYLOAD"]._serialized_end = 2930
    _globals["_REPORTTASKOUTCOMEREQUEST"]._serialized_start = 2933
    _globals["_REPORTTASKOUTCOMEREQUEST"]._serialized_end = 3708
    _globals["_REPORTTASKOUTCOMERESPONSE"]._serialized_start = 3710
    _globals["_REPORTTASKOUTCOMERESPONSE"]._serialized_end = 3737
    _globals["_EXECUTORAPI"]._serialized_start = 5116
    _globals["_EXECUTORAPI"]._serialized_end = 5483
# @@protoc_insertion_point(module_scope)
