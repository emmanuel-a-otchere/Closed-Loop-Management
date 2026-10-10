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
    DAISY_CHAIN = "DAISY_CHAIN"
    HIERARCHICAL = "HIERARCHICAL"
    FEEDBACK = "FEEDBACK"


class DecisionModelKind(StrEnum):
    OODA = "OODA"
    MAPE = "MAPE"
    CUSTOM = "CUSTOM"


class ActivityRef(BaseModel):
    """Lightweight projection of an Activity used inside other entities."""

    model_config = ConfigDict(extra="forbid")

    id: UUID
    name: str | None = None


class DecisionModelRef(BaseModel):
    """Lightweight reference to a DecisionModel."""

    model_config = ConfigDict(extra="forbid")

    id: UUID
    kind: DecisionModelKind


class GoalTarget(BaseModel):
    metric: str = Field(..., description="The metric being targeted (e.g. 'cpu_temp_c').")
    value: float = Field(..., description="The numeric value of the target.")
    unit: str | None = None
    direction: GoalDirection = GoalDirection.AT_LEAST


class Goal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID = Field(default_factory=uuid4)
    name: str
    description: str | None = None
    target: GoalTarget
    scope: GoalScope = GoalScope.CLOSED_LOOP
    scopeRef: UUID | None = None


class WorkflowRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    name: str


class Activity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID = Field(default_factory=uuid4)
    name: str
    description: str | None = None
    action: str = Field(..., description="Underlying implementation reference.")
    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)


class Workflow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID = Field(default_factory=uuid4)
    name: str
    path: WorkflowPath
    activities: list[ActivityRef] = Field(default_factory=list)


class ClosedLoopLink(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID = Field(default_factory=uuid4)
    source: DecisionModelRef  # reuse as a placeholder; full ClosedLoopRef lands in Slice 3
    target: DecisionModelRef
    kind: LinkKind
    condition: str | None = None


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


class Page(BaseModel):
    """Generic pagination envelope."""

    model_config = ConfigDict(extra="forbid")

    items: list[object]
    total: int
    page: int
    pageSize: int


__all__ = [
    "Activity",
    "ActivityRef",
    "ClosedLoop",
    "ClosedLoopCreate",
    "ClosedLoopLink",
    "ClosedLoopState",
    "ClosedLoopUpdate",
    "CustomDecisionModel",
    "CustomDecisionModelStep",
    "DecisionModel",
    "DecisionModelKind",
    "DecisionModelRef",
    "ErrorEnvelope",
    "Goal",
    "GoalDirection",
    "GoalScope",
    "GoalTarget",
    "LinkKind",
    "MapeDecisionModel",
    "OodaDecisionModel",
    "OodaStep",
    "Page",
    "StateResponse",
    "StateTransitionRequest",
    "Workflow",
    "WorkflowPath",
    "WorkflowRef",
]


# Re-export HttpUrl so callers depending on this module don't need to import
# pydantic directly when constructing links in tests.
__all__ += ["HttpUrl"]