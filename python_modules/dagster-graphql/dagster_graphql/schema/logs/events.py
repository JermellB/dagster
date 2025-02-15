import graphene
from dagster import check
from dagster.core.events import AssetLineageInfo, DagsterEventType
from dagster.core.execution.plan.objects import ErrorSource
from dagster.core.execution.stats import RunStepKeyStatsSnapshot

from ...implementation.fetch_runs import get_step_stats
from ..asset_key import GrapheneAssetKey, GrapheneAssetLineageInfo
from ..errors import GraphenePythonError
from ..runs import GrapheneStepEventStatus
from ..util import non_null_list
from .log_level import GrapheneLogLevel


class GrapheneMessageEvent(graphene.Interface):
    runId = graphene.NonNull(graphene.String)
    message = graphene.NonNull(graphene.String)
    timestamp = graphene.NonNull(graphene.String)
    level = graphene.NonNull(GrapheneLogLevel)
    stepKey = graphene.Field(graphene.String)
    solidHandleID = graphene.Field(graphene.String)
    eventType = graphene.Field(graphene.Enum.from_enum(DagsterEventType))

    class Meta:
        name = "MessageEvent"


class GrapheneEventMetadataEntry(graphene.Interface):
    label = graphene.NonNull(graphene.String)
    description = graphene.String()

    class Meta:
        name = "EventMetadataEntry"


class GrapheneDisplayableEvent(graphene.Interface):
    label = graphene.NonNull(graphene.String)
    description = graphene.String()
    metadataEntries = non_null_list(GrapheneEventMetadataEntry)

    class Meta:
        name = "DisplayableEvent"


class GrapheneMissingRunIdErrorEvent(graphene.ObjectType):
    invalidRunId = graphene.NonNull(graphene.String)

    class Meta:
        name = "MissingRunIdErrorEvent"


class GrapheneLogMessageEvent(graphene.ObjectType):
    class Meta:
        interfaces = (GrapheneMessageEvent,)
        name = "LogMessageEvent"


class GrapheneRunEvent(graphene.Interface):
    pipelineName = graphene.NonNull(graphene.String)

    class Meta:
        name = "RunEvent"


class GrapheneRunEnqueuedEvent(graphene.ObjectType):
    class Meta:
        interfaces = (GrapheneMessageEvent, GrapheneRunEvent)
        name = "RunEnqueuedEvent"


class GrapheneRunDequeuedEvent(graphene.ObjectType):
    class Meta:
        interfaces = (GrapheneMessageEvent, GrapheneRunEvent)
        name = "RunDequeuedEvent"


class GrapheneRunStartingEvent(graphene.ObjectType):
    class Meta:
        interfaces = (GrapheneMessageEvent, GrapheneRunEvent)
        name = "RunStartingEvent"


class GrapheneRunCancelingEvent(graphene.ObjectType):
    class Meta:
        interfaces = (GrapheneMessageEvent, GrapheneRunEvent)
        name = "RunCancelingEvent"


class GrapheneRunCanceledEvent(graphene.ObjectType):
    class Meta:
        interfaces = (GrapheneMessageEvent, GrapheneRunEvent)
        name = "RunCanceledEvent"


class GrapheneRunStartEvent(graphene.ObjectType):
    class Meta:
        interfaces = (GrapheneMessageEvent, GrapheneRunEvent)
        name = "RunStartEvent"


class GrapheneRunSuccessEvent(graphene.ObjectType):
    class Meta:
        interfaces = (GrapheneMessageEvent, GrapheneRunEvent)
        name = "RunSuccessEvent"


class GrapheneRunFailureEvent(graphene.ObjectType):
    error = graphene.Field(GraphenePythonError)

    class Meta:
        interfaces = (GrapheneMessageEvent, GrapheneRunEvent)
        name = "RunFailureEvent"


class GrapheneAlertStartEvent(graphene.ObjectType):
    class Meta:
        interfaces = (GrapheneMessageEvent, GrapheneRunEvent)
        name = "AlertStartEvent"


class GrapheneAlertSuccessEvent(graphene.ObjectType):
    class Meta:
        interfaces = (GrapheneMessageEvent, GrapheneRunEvent)
        name = "AlertSuccessEvent"


class GrapheneStepEvent(graphene.Interface):
    stepKey = graphene.Field(graphene.String)
    solidHandleID = graphene.Field(graphene.String)

    class Meta:
        name = "StepEvent"


class GrapheneExecutionStepStartEvent(graphene.ObjectType):
    class Meta:
        interfaces = (GrapheneMessageEvent, GrapheneStepEvent)
        name = "ExecutionStepStartEvent"


class GrapheneExecutionStepRestartEvent(graphene.ObjectType):
    class Meta:
        interfaces = (GrapheneMessageEvent, GrapheneStepEvent)
        name = "ExecutionStepRestartEvent"


class GrapheneExecutionStepUpForRetryEvent(graphene.ObjectType):
    error = graphene.Field(GraphenePythonError)
    secondsToWait = graphene.Field(graphene.Int)

    class Meta:
        interfaces = (GrapheneMessageEvent, GrapheneStepEvent)
        name = "ExecutionStepUpForRetryEvent"


class GrapheneExecutionStepSkippedEvent(graphene.ObjectType):
    class Meta:
        interfaces = (GrapheneMessageEvent, GrapheneStepEvent)
        name = "ExecutionStepSkippedEvent"


class GrapheneEventPathMetadataEntry(graphene.ObjectType):
    path = graphene.NonNull(graphene.String)

    class Meta:
        interfaces = (GrapheneEventMetadataEntry,)
        name = "EventPathMetadataEntry"


class GrapheneEventJsonMetadataEntry(graphene.ObjectType):
    jsonString = graphene.NonNull(graphene.String)

    class Meta:
        interfaces = (GrapheneEventMetadataEntry,)
        name = "EventJsonMetadataEntry"


class GrapheneEventTextMetadataEntry(graphene.ObjectType):
    text = graphene.NonNull(graphene.String)

    class Meta:
        interfaces = (GrapheneEventMetadataEntry,)
        name = "EventTextMetadataEntry"


class GrapheneEventUrlMetadataEntry(graphene.ObjectType):
    url = graphene.NonNull(graphene.String)

    class Meta:
        interfaces = (GrapheneEventMetadataEntry,)
        name = "EventUrlMetadataEntry"


class GrapheneEventMarkdownMetadataEntry(graphene.ObjectType):
    md_str = graphene.NonNull(graphene.String)

    class Meta:
        interfaces = (GrapheneEventMetadataEntry,)
        name = "EventMarkdownMetadataEntry"


class GrapheneEventPythonArtifactMetadataEntry(graphene.ObjectType):
    module = graphene.NonNull(graphene.String)
    name = graphene.NonNull(graphene.String)

    class Meta:
        interfaces = (GrapheneEventMetadataEntry,)
        name = "EventPythonArtifactMetadataEntry"


class GrapheneEventFloatMetadataEntry(graphene.ObjectType):
    floatValue = graphene.Field(graphene.Float)

    class Meta:
        interfaces = (GrapheneEventMetadataEntry,)
        name = "EventFloatMetadataEntry"


class GrapheneEventIntMetadataEntry(graphene.ObjectType):
    intValue = graphene.Field(
        graphene.Int, description="Nullable to allow graceful degrade on > 32 bit numbers"
    )
    intRepr = graphene.NonNull(
        graphene.String,
        description="String representation of the int to support greater than 32 bit",
    )

    class Meta:
        interfaces = (GrapheneEventMetadataEntry,)
        name = "EventIntMetadataEntry"


class GrapheneEventPipelineRunMetadataEntry(graphene.ObjectType):
    runId = graphene.NonNull(graphene.String)

    class Meta:
        interfaces = (GrapheneEventMetadataEntry,)
        name = "EventPipelineRunMetadataEntry"


class GrapheneEventAssetMetadataEntry(graphene.ObjectType):
    assetKey = graphene.NonNull(GrapheneAssetKey)

    class Meta:
        interfaces = (GrapheneEventMetadataEntry,)
        name = "EventAssetMetadataEntry"


class GrapheneObjectStoreOperationType(graphene.Enum):
    SET_OBJECT = "SET_OBJECT"
    GET_OBJECT = "GET_OBJECT"
    RM_OBJECT = "RM_OBJECT"
    CP_OBJECT = "CP_OBJECT"

    class Meta:
        name = "ObjectStoreOperationType"


class GrapheneObjectStoreOperationResult(graphene.ObjectType):
    op = graphene.NonNull(GrapheneObjectStoreOperationType)

    class Meta:
        interfaces = (GrapheneDisplayableEvent,)
        name = "ObjectStoreOperationResult"

    def resolve_metadataEntries(self, _graphene_info):
        from ...implementation.events import _to_metadata_entries

        return _to_metadata_entries(self.metadata_entries)  # pylint: disable=no-member


class GrapheneMaterialization(graphene.ObjectType):
    assetKey = graphene.Field(GrapheneAssetKey)

    class Meta:
        interfaces = (GrapheneDisplayableEvent,)
        name = "Materialization"

    def resolve_metadataEntries(self, _graphene_info):
        from ...implementation.events import _to_metadata_entries

        return _to_metadata_entries(self.metadata_entries)  # pylint: disable=no-member

    def resolve_assetKey(self, _graphene_info):
        asset_key = self.asset_key  # pylint: disable=no-member

        if not asset_key:
            return None

        return GrapheneAssetKey(path=asset_key.path)


class GrapheneExpectationResult(graphene.ObjectType):
    success = graphene.NonNull(graphene.Boolean)

    class Meta:
        interfaces = (GrapheneDisplayableEvent,)
        name = "ExpectationResult"

    def resolve_metadataEntries(self, _graphene_info):
        from ...implementation.events import _to_metadata_entries

        return _to_metadata_entries(self.metadata_entries)  # pylint: disable=no-member


class GrapheneTypeCheck(graphene.ObjectType):
    success = graphene.NonNull(graphene.Boolean)

    class Meta:
        interfaces = (GrapheneDisplayableEvent,)
        name = "TypeCheck"

    def resolve_metadataEntries(self, _graphene_info):
        from ...implementation.events import _to_metadata_entries

        return _to_metadata_entries(self.metadata_entries)  # pylint: disable=no-member


class GrapheneFailureMetadata(graphene.ObjectType):
    class Meta:
        interfaces = (GrapheneDisplayableEvent,)
        name = "FailureMetadata"

    def resolve_metadataEntries(self, _graphene_info):
        from ...implementation.events import _to_metadata_entries

        return _to_metadata_entries(self.metadata_entries)  # pylint: disable=no-member


class GrapheneExecutionStepInputEvent(graphene.ObjectType):
    class Meta:
        interfaces = (GrapheneMessageEvent, GrapheneStepEvent)
        name = "ExecutionStepInputEvent"

    input_name = graphene.NonNull(graphene.String)
    type_check = graphene.NonNull(GrapheneTypeCheck)


class GrapheneExecutionStepOutputEvent(graphene.ObjectType):
    class Meta:
        interfaces = (GrapheneMessageEvent, GrapheneStepEvent, GrapheneDisplayableEvent)
        name = "ExecutionStepOutputEvent"

    output_name = graphene.NonNull(graphene.String)
    type_check = graphene.NonNull(GrapheneTypeCheck)


class GrapheneExecutionStepSuccessEvent(graphene.ObjectType):
    class Meta:
        interfaces = (GrapheneMessageEvent, GrapheneStepEvent)
        name = "ExecutionStepSuccessEvent"


class GrapheneExecutionStepFailureEvent(graphene.ObjectType):
    class Meta:
        interfaces = (GrapheneMessageEvent, GrapheneStepEvent)
        name = "ExecutionStepFailureEvent"

    error = graphene.Field(GraphenePythonError)
    errorSource = graphene.Field(graphene.Enum.from_enum(ErrorSource))
    failureMetadata = graphene.Field(GrapheneFailureMetadata)


class GrapheneHookCompletedEvent(graphene.ObjectType):
    class Meta:
        interfaces = (GrapheneMessageEvent, GrapheneStepEvent)
        name = "HookCompletedEvent"


class GrapheneHookSkippedEvent(graphene.ObjectType):
    class Meta:
        interfaces = (GrapheneMessageEvent, GrapheneStepEvent)
        name = "HookSkippedEvent"


class GrapheneHookErroredEvent(graphene.ObjectType):
    class Meta:
        interfaces = (GrapheneMessageEvent, GrapheneStepEvent)
        name = "HookErroredEvent"

    error = graphene.Field(GraphenePythonError)


class GrapheneLogsCapturedEvent(graphene.ObjectType):
    class Meta:
        interfaces = (GrapheneMessageEvent,)
        name = "LogsCapturedEvent"

    logKey = graphene.NonNull(graphene.String)
    stepKeys = graphene.List(graphene.NonNull(graphene.String))
    pid = graphene.Int()


class GrapheneStepMaterializationEvent(graphene.ObjectType):
    class Meta:
        interfaces = (GrapheneMessageEvent, GrapheneStepEvent)
        name = "StepMaterializationEvent"

    materialization = graphene.NonNull(GrapheneMaterialization)
    stepStats = graphene.NonNull(lambda: GrapheneRunStepStats)
    assetLineage = non_null_list(GrapheneAssetLineageInfo)

    def __init__(self, materialization, assetLineage, **basic_params):
        self._asset_lineage = check.opt_list_param(assetLineage, "assetLineage", AssetLineageInfo)
        super().__init__(materialization=materialization, **basic_params)

    def resolve_stepStats(self, graphene_info):
        run_id = self.runId  # pylint: disable=no-member
        step_key = self.stepKey  # pylint: disable=no-member
        stats = get_step_stats(graphene_info, run_id, step_keys=[step_key])
        return stats[0]

    def resolve_assetLineage(self, _graphene_info):
        return [
            GrapheneAssetLineageInfo(
                assetKey=lineage_info.asset_key,
                partitions=lineage_info.partitions,
            )
            for lineage_info in self._asset_lineage
        ]


class GrapheneHandledOutputEvent(graphene.ObjectType):
    class Meta:
        interfaces = (GrapheneMessageEvent, GrapheneStepEvent, GrapheneDisplayableEvent)
        name = "HandledOutputEvent"

    output_name = graphene.NonNull(graphene.String)
    manager_key = graphene.NonNull(graphene.String)


class GrapheneLoadedInputEvent(graphene.ObjectType):
    class Meta:
        interfaces = (GrapheneMessageEvent, GrapheneStepEvent)
        name = "LoadedInputEvent"

    input_name = graphene.NonNull(graphene.String)
    manager_key = graphene.NonNull(graphene.String)
    upstream_output_name = graphene.Field(graphene.String)
    upstream_step_key = graphene.Field(graphene.String)


class GrapheneObjectStoreOperationEvent(graphene.ObjectType):
    class Meta:
        interfaces = (GrapheneMessageEvent, GrapheneStepEvent)
        name = "ObjectStoreOperationEvent"

    operation_result = graphene.NonNull(GrapheneObjectStoreOperationResult)


class GrapheneEngineEvent(graphene.ObjectType):
    class Meta:
        interfaces = (GrapheneMessageEvent, GrapheneDisplayableEvent, GrapheneStepEvent)
        name = "EngineEvent"

    error = graphene.Field(GraphenePythonError)
    marker_start = graphene.Field(graphene.String)
    marker_end = graphene.Field(graphene.String)


class GrapheneStepExpectationResultEvent(graphene.ObjectType):
    class Meta:
        interfaces = (GrapheneMessageEvent, GrapheneStepEvent)
        name = "StepExpectationResultEvent"

    expectation_result = graphene.NonNull(GrapheneExpectationResult)


# Should be a union of all possible events
class GrapheneDagsterRunEvent(graphene.Union):
    class Meta:
        types = (
            GrapheneExecutionStepFailureEvent,
            GrapheneExecutionStepInputEvent,
            GrapheneExecutionStepOutputEvent,
            GrapheneExecutionStepSkippedEvent,
            GrapheneExecutionStepStartEvent,
            GrapheneExecutionStepSuccessEvent,
            GrapheneExecutionStepUpForRetryEvent,
            GrapheneExecutionStepRestartEvent,
            GrapheneLogMessageEvent,
            GrapheneRunFailureEvent,
            GrapheneRunStartEvent,
            GrapheneRunEnqueuedEvent,
            GrapheneRunDequeuedEvent,
            GrapheneRunStartingEvent,
            GrapheneRunCancelingEvent,
            GrapheneRunCanceledEvent,
            GrapheneRunSuccessEvent,
            GrapheneHandledOutputEvent,
            GrapheneLoadedInputEvent,
            GrapheneLogsCapturedEvent,
            GrapheneObjectStoreOperationEvent,
            GrapheneStepExpectationResultEvent,
            GrapheneStepMaterializationEvent,
            GrapheneEngineEvent,
            GrapheneHookCompletedEvent,
            GrapheneHookSkippedEvent,
            GrapheneHookErroredEvent,
            GrapheneAlertStartEvent,
            GrapheneAlertSuccessEvent,
        )
        name = "DagsterRunEvent"


class GraphenePipelineRunStepStats(graphene.Interface):
    runId = graphene.NonNull(graphene.String)
    stepKey = graphene.NonNull(graphene.String)
    status = graphene.Field(GrapheneStepEventStatus)
    startTime = graphene.Field(graphene.Float)
    endTime = graphene.Field(graphene.Float)
    materializations = non_null_list(GrapheneMaterialization)
    expectationResults = non_null_list(GrapheneExpectationResult)

    class Meta:
        name = "PipelineRunStepStats"


class GrapheneRunStepStats(graphene.ObjectType):
    runId = graphene.NonNull(graphene.String)
    stepKey = graphene.NonNull(graphene.String)
    status = graphene.Field(GrapheneStepEventStatus)
    startTime = graphene.Field(graphene.Float)
    endTime = graphene.Field(graphene.Float)
    materializations = non_null_list(GrapheneMaterialization)
    expectationResults = non_null_list(GrapheneExpectationResult)

    class Meta:
        interfaces = (GraphenePipelineRunStepStats,)
        name = "RunStepStats"

    def __init__(self, stats):
        self._stats = check.inst_param(stats, "stats", RunStepKeyStatsSnapshot)
        super().__init__(
            runId=stats.run_id,
            stepKey=stats.step_key,
            status=stats.status,
            startTime=stats.start_time,
            endTime=stats.end_time,
            materializations=stats.materializations,
            expectationResults=stats.expectation_results,
        )
