"""Pydantic models for CLAM.

These models are the source-of-truth for the OAS 3.1 document served at
``/openapi.json``. Add a field here, and the schema, the request/response
shapes, the Swagger UI, and the Postman collection all pick it up.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

# --- Enums -------------------------------------------------------------------


class ClosedLoopState(StrEnum):
    """Lifecycle state of a closed loop.

    The transition diagram lives in ``docs/data-model/clam-data-model-1.0.md``
    under "State machine". A transition is requested via
    ``POST /api/v1/closedLoop/{id}/state`` and is validated by the API.
    """

    DESIGNED = "designed"
    VALIDATED = "validated"
    PUBLISHED = "published"
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    RETIRED = "retired"


class GoalDirection(StrEnum):
    AT_LEAST = "AT_LEAST"
    AT_MOST = "AT_MOST"
    EXACTLY = "EXACTLY"


class GoalScope(StrEnum):
    CLOSED_LOOP = "CLOSED_LOOP"
    WORKFLOW = "WORKFLOW"
    ACTIVITY = "ACTIVITY"


class WorkflowPath(StrEnum):
    FEEDFORWARD = "FEEDFORWARD"
    FEEDBACK = "FEEDBACK"


class LinkKind(StrEnum):
    """Topology of a relationship between two closed loops.

    - ``DAISY_CHAIN``: source.target feeds source.source (linear topology).
    - ``HIERARCHICAL``: source is parent of target (parent supervises child).
    - ``FEEDBACK``: target feeds back into source (closes the outer loop).
    - ``SHADOW``: target is a shadow / replica used for failover.
    """

    DAISY_CHAIN = "DAISY_CHAIN"
    HIERARCHICAL = "HIERARCHICAL"
    FEEDBACK = "FEEDBACK"
    SHADOW = "SHADOW"


class LinkDirection(StrEnum):
    FORWARD = "FORWARD"
    BIDIRECTIONAL = "BIDIRECTIONAL"


class DecisionModelKind(StrEnum):
    OODA = "OODA"
    MAPE = "MAPE"
    CUSTOM = "CUSTOM"


class ActivityType(StrEnum):
    """Role of an activity in the closed loop."""

    SENSE = "sense"
    ANALYSE = "analyse"
    DECIDE = "decide"
    ACT = "act"
    FEEDBACK = "feedback"
    FEEDFORWARD = "feedforward"


class ActivityLifecycleState(StrEnum):
    DESIGNED = "designed"
    VALIDATED = "validated"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"
    RETIRED = "retired"


class ActivityExecutor(StrEnum):
    """Where an activity is executed."""

    INTERNAL = "internal"
    EXTERNAL = "external"
    HUMAN = "human"


# --- Lightweight references --------------------------------------------------


class ActivityRef(BaseModel):
    """Lightweight projection of an Activity used inside other entities."""

    model_config = ConfigDict(extra="forbid")

    id: UUID
    name: str | None = None
    activityType: ActivityType | None = None


class DecisionModelRef(BaseModel):
    """Lightweight reference to a DecisionModel."""

    model_config = ConfigDict(extra="forbid")

    id: UUID
    kind: DecisionModelKind


class ClosedLoopRef(BaseModel):
    """Lightweight reference to a ClosedLoop.

    Used inside ``ClosedLoopLink`` and other cross-loop structures so the
    link topology stays decoupled from the full loop payload.
    """

    model_config = ConfigDict(extra="forbid")

    id: UUID
    name: str | None = None


class WorkflowRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    name: str
    path: WorkflowPath | None = None


class GoalRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    name: str


# --- Goals -------------------------------------------------------------------


class GoalTarget(BaseModel):
    metric: str = Field(..., description="The metric being targeted (e.g. 'cpu_temp_c').")
    value: float = Field(..., description="The numeric value of the target.")
    unit: str | None = None
    direction: GoalDirection = GoalDirection.AT_LEAST


class GoalTimeframe(BaseModel):
    """Optional time window during which the goal is measured."""

    model_config = ConfigDict(extra="forbid")

    startsAt: datetime | None = None
    endsAt: datetime | None = None


class GoalBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=120)
    description: str | None = None
    target: GoalTarget
    scope: GoalScope = GoalScope.CLOSED_LOOP
    scopeRef: UUID | None = Field(
        default=None,
        description="ID of the entity this goal is scoped to (a ClosedLoop, Workflow, or Activity).",
    )
    timeframe: GoalTimeframe | None = None
    currentValue: float | None = Field(
        default=None,
        description="Latest observed value for the metric. Used for KPI calculations.",
    )
    metricSource: str | None = Field(
        default=None,
        description="Where the metric is sourced from (e.g. 'sensor:cpu.temp', 'http:api/metrics').",
    )


class GoalCreate(GoalBase):
    pass


class GoalUpdate(BaseModel):
    """Partial-update payload for PATCH on /goal/{id}."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None
    target: GoalTarget | None = None
    scope: GoalScope | None = None
    scopeRef: UUID | None = None
    timeframe: GoalTimeframe | None = None
    currentValue: float | None = None
    metricSource: str | None = None


class Goal(GoalBase):
    id: UUID = Field(default_factory=uuid4)
    achieved: bool | None = None
    createdAt: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(UTC))


# --- Activities --------------------------------------------------------------


class ActivityBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=120)
    description: str | None = None
    activityType: ActivityType = ActivityType.SENSE
    action: str = Field(
        ...,
        description=(
            "Underlying implementation reference. Free-form string. Examples: "
            "'script:sense_cpu_temp', 'http:POST /api/cooling/start', "
            "'agent:thermostat-orchestrator', 'human:oncall-rotation'."
        ),
    )
    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    params: dict[str, object] = Field(
        default_factory=dict,
        description="Activity-specific configuration. Free-form key/value map.",
    )
    executor: ActivityExecutor = ActivityExecutor.INTERNAL
    expectedDurationMs: int | None = Field(
        default=None, ge=0, description="Expected execution time in milliseconds (for SLA)."
    )


class ActivityCreate(ActivityBase):
    pass


class ActivityUpdate(BaseModel):
    """Partial-update payload for PATCH on /activity/{id}."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None
    activityType: ActivityType | None = None
    action: str | None = None
    inputs: list[str] | None = None
    outputs: list[str] | None = None
    params: dict[str, object] | None = None
    executor: ActivityExecutor | None = None
    expectedDurationMs: int | None = None
    lifecycleState: ActivityLifecycleState | None = None


class Activity(ActivityBase):
    id: UUID = Field(default_factory=uuid4)
    lifecycleState: ActivityLifecycleState = ActivityLifecycleState.DESIGNED
    createdAt: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ActivityStateTransitionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    targetState: ActivityLifecycleState


# --- Workflows ---------------------------------------------------------------


class WorkflowBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=120)
    description: str | None = None
    path: WorkflowPath
    activities: list[ActivityRef] = Field(default_factory=list)
    goals: list[GoalRef] = Field(default_factory=list)
    targetCycleTimeMs: int | None = Field(
        default=None, ge=0, description="Target time to run all activities once, in milliseconds."
    )


class WorkflowCreate(WorkflowBase):
    pass


class WorkflowUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None
    path: WorkflowPath | None = None
    activities: list[ActivityRef] | None = None
    goals: list[GoalRef] | None = None
    targetCycleTimeMs: int | None = None
    lifecycleState: ActivityLifecycleState | None = None


class Workflow(WorkflowBase):
    id: UUID = Field(default_factory=uuid4)
    lifecycleState: ActivityLifecycleState = ActivityLifecycleState.DESIGNED
    createdAt: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(UTC))


class WorkflowStateTransitionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    targetState: ActivityLifecycleState


# --- ClosedLoopLink ---------------------------------------------------------


class ClosedLoopLink(BaseModel):
    """Daisy-chain / hierarchical interlink between two closed loops.

    PR1 wires the data model; PR3 adds cycle detection + bulk operations.
    """

    model_config = ConfigDict(extra="forbid")

    id: UUID = Field(default_factory=uuid4)
    source: ClosedLoopRef
    target: ClosedLoopRef
    kind: LinkKind = LinkKind.DAISY_CHAIN
    direction: LinkDirection = LinkDirection.FORWARD
    condition: str | None = Field(
        default=None,
        description="Optional boolean condition expression. Empty/null means always-on.",
    )
    weight: float | None = Field(
        default=None,
        description="Optional relative weight for fan-in / fan-out aggregations.",
    )


# --- Decision models ---------------------------------------------------------


class OodaStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Literal["observe", "orient", "decide", "act"]
    activityRef: ActivityRef


class OodaDecisionModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID = Field(default_factory=uuid4)
    kind: Literal["OODA"] = "OODA"
    name: str
    observe: ActivityRef
    orient: ActivityRef
    decide: ActivityRef
    act: ActivityRef


class MapeDecisionModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID = Field(default_factory=uuid4)
    kind: Literal["MAPE"] = "MAPE"
    name: str
    monitor: ActivityRef
    analyze: ActivityRef
    plan: ActivityRef
    execute: ActivityRef


class CustomDecisionModelStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    activityRef: ActivityRef


class CustomDecisionModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID = Field(default_factory=uuid4)
    kind: Literal["CUSTOM"] = "CUSTOM"
    name: str
    steps: list[CustomDecisionModelStep] = Field(..., min_length=1)


DecisionModel = Annotated[
    OodaDecisionModel | MapeDecisionModel | CustomDecisionModel,
    Field(discriminator="kind"),
]


# --- ClosedLoop ---------------------------------------------------------------


class ClosedLoopBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=120)
    description: str | None = None
    decisionModelRef: DecisionModelRef


class ClosedLoopCreate(ClosedLoopBase):
    pass


class ClosedLoopUpdate(BaseModel):
    """Partial-update payload for PATCH."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None
    decisionModelRef: DecisionModelRef | None = None


class ClosedLoop(ClosedLoopBase):
    id: UUID = Field(default_factory=uuid4)
    goals: list[Goal] = Field(default_factory=list)
    workflows: list[WorkflowRef] = Field(default_factory=list)
    links: list[ClosedLoopLink] = Field(default_factory=list)
    state: ClosedLoopState = ClosedLoopState.DESIGNED
    createdAt: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(UTC))


class StateTransitionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    targetState: ClosedLoopState


class StateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    state: ClosedLoopState


class ErrorEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    message: str
    details: dict[str, object] | None = None


class ClosedLoopGoalRollup(BaseModel):
    """Aggregated goal achievement for a closed loop (PR2 + PR4 nested rollup).

    The rollup computes:
    - ``goalCount``: total goals scoped to the loop (direct + indirect,
      including nested loops reachable via HIERARCHICAL / DAISY_CHAIN
      outgoing edges -- see PR4).
    - ``achievedCount``: goals whose latest ``currentValue`` satisfies the
      target direction.
    - ``achievementPercent``: ``achievedCount / goalCount`` (0..100), or 0
      when ``goalCount`` is 0.
    - ``goals``: the per-goal evaluation rows (latest value vs target).
    - ``nested``: per-child-loop rollup snapshots. Each entry is a
      ``NestedClosedLoopRollup`` carrying the child loop id, depth, and
      its own goalCount / achievedCount / achievementPercent.
    - ``depth``: maximum nested depth traversed (0 = no nested).
    - ``computedAt``: server-side timestamp.
    """

    model_config = ConfigDict(extra="forbid")

    closedLoopId: UUID
    goalCount: int
    achievedCount: int
    achievementPercent: float
    goals: list[Goal]
    nested: list[NestedClosedLoopRollup] = Field(default_factory=list)
    depth: int = 0
    computedAt: datetime = Field(default_factory=lambda: datetime.now(UTC))


class NestedClosedLoopRollup(BaseModel):
    """Per-child-loop rollup snapshot attached to a parent rollup (PR4)."""

    model_config = ConfigDict(extra="forbid")

    closedLoopId: UUID
    depth: int
    goalCount: int
    achievedCount: int
    achievementPercent: float


class ClosedLoopLinkCreateBatch(BaseModel):
    """Batch payload for bulk link creation (PR3).

    The body is a JSON object containing a ``items`` array of links.
    The endpoint validates cycle-freedom across the whole batch plus
    the existing graph; on failure the entire batch is rejected.
    """

    model_config = ConfigDict(extra="forbid")

    items: list[ClosedLoopLink]


class ClosedLoopTopology(BaseModel):
    """Topology snapshot of the closed-loop link graph (PR3)."""

    model_config = ConfigDict(extra="forbid")

    linkCount: int
    nodeCount: int
    links: list[ClosedLoopLink]


class AuthTokenCreate(BaseModel):
    """Request body for issuing a new auth token (Slice 3 PR1)."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=120)
    scopes: list[str] = Field(
        ...,
        min_length=1,
        description=(
            "Scopes to grant. Must contain only valid scope strings "
            "(read / write / admin)."
        ),
    )


class AuthTokenIssued(BaseModel):
    """Response body returned once when a token is issued.

    The plaintext token is returned exactly once and never persisted;
    the server only retains its SHA-256 fingerprint.
    """

    model_config = ConfigDict(extra="forbid")

    tokenId: str
    plaintext: str
    name: str
    scopes: list[str]
    issuedAt: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AuthTokenInfo(BaseModel):
    """Public view of an issued token (no plaintext)."""

    model_config = ConfigDict(extra="forbid")

    tokenId: str
    name: str
    scopes: list[str]
    issuedAt: datetime


class Page(BaseModel):
    """Generic pagination envelope."""

    model_config = ConfigDict(extra="forbid")

    items: list[object]
    total: int
    page: int
    pageSize: int


__all__ = [
    "Activity",
    "ActivityCreate",
    "ActivityExecutor",
    "ActivityLifecycleState",
    "ActivityRef",
    "ActivityStateTransitionRequest",
    "ActivityType",
    "ActivityUpdate",
    "AuthTokenCreate",
    "AuthTokenInfo",
    "AuthTokenIssued",
    "ClosedLoop",
    "ClosedLoopCreate",
    "ClosedLoopGoalRollup",
    "ClosedLoopLink",
    "ClosedLoopLinkCreateBatch",
    "ClosedLoopRef",
    "ClosedLoopState",
    "ClosedLoopTopology",
    "ClosedLoopUpdate",
    "CustomDecisionModel",
    "CustomDecisionModelStep",
    "DecisionModel",
    "DecisionModelKind",
    "DecisionModelRef",
    "ErrorEnvelope",
    "Goal",
    "GoalCreate",
    "GoalDirection",
    "GoalRef",
    "GoalScope",
    "GoalTarget",
    "GoalTimeframe",
    "GoalUpdate",
    "LinkDirection",
    "LinkKind",
    "MapeDecisionModel",
    "OodaDecisionModel",
    "OodaStep",
    "Page",
    "StateResponse",
    "StateTransitionRequest",
    "Workflow",
    "WorkflowCreate",
    "WorkflowPath",
    "WorkflowRef",
    "WorkflowStateTransitionRequest",
    "WorkflowUpdate",
]


# Re-export HttpUrl so callers depending on this module don't need to import
# pydantic directly when constructing links in tests.
__all__ += ["HttpUrl"]