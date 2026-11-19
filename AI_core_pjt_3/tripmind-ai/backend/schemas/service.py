from datetime import date
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, StringConstraints, model_validator


Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=250)]
Clock = Annotated[str, StringConstraints(pattern=r"^(?:[01][0-9]|2[0-3]):[0-5][0-9]$")]


class ChatInput(BaseModel):
    session_id: UUID | None = None
    message: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=4000)]


class Evidence(BaseModel):
    tool: str
    source: str
    fact: str
    reference_url: str | None = None


class PlanItem(BaseModel):
    content_id: str | None = None
    title: Text
    address: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    start_time: Clock | None = None
    end_time: Clock | None = None
    evidence: list[Evidence] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_time(self):
        if (self.start_time is None) != (self.end_time is None):
            raise ValueError("Both item times are required together")
        if self.start_time is not None and self.start_time >= self.end_time:
            raise ValueError("Item end must follow start")
        return self


class PlanInput(BaseModel):
    session_id: UUID | None = None
    title: Text
    region: Text
    visit_date: date
    start_time: Clock
    end_time: Clock
    notes: str | None = None
    items: list[PlanItem] = Field(min_length=1, max_length=100)

    @model_validator(mode="after")
    def validate_window(self):
        if self.start_time >= self.end_time:
            raise ValueError("Plan end must follow start")
        for item in self.items:
            if item.start_time is not None and not (
                self.start_time <= item.start_time < item.end_time <= self.end_time
            ):
                raise ValueError("Item must fit within the plan window")
        return self


class PlanPatch(BaseModel):
    title: Text | None = None
    region: Text | None = None
    visit_date: date | None = None
    start_time: Clock | None = None
    end_time: Clock | None = None
    notes: str | None = None
    items: list[PlanItem] | None = None

    @model_validator(mode="after")
    def validate_changes(self):
        if not self.model_fields_set:
            raise ValueError("Include at least one change")
        if any(getattr(self, field) is None for field in self.model_fields_set - {"notes"}):
            raise ValueError("Only notes can be cleared")
        return self


class PlanSummary(BaseModel):
    id: int
    title: str
    region: str
    visit_date: date
    start_time: Clock
    end_time: Clock
    created_at: str
    updated_at: str
    item_count: int


class SavedItem(PlanItem):
    id: int
    position: int


class SavedPlan(PlanInput):
    id: int
    created_at: str
    updated_at: str
    items: list[SavedItem]


class PlanWrite(BaseModel):
    plan: SavedPlan
    conflicts: list[PlanSummary]


class PlanList(BaseModel):
    items: list[PlanSummary]
    total: int


class Warning(BaseModel):
    code: str
    message: str
    tool: str | None = None


class ExecutionEvent(BaseModel):
    event_id: UUID
    session_id: UUID
    run_id: UUID
    seq: int
    type: str
    node: str
    occurred_at: str
    payload: dict


class ChatResponse(BaseModel):
    session_id: UUID
    run_id: UUID
    status: str
    reply: str
    questions: list[str]
    draft_plan: PlanInput | None
    evidence: list[Evidence]
    warnings: list[Warning]
    events: list[ExecutionEvent]


class LogSummary(BaseModel):
    session_id: UUID
    event_count: int
    run_count: int
    last_event_at: str


class LogList(BaseModel):
    items: list[LogSummary]
    total: int


class LogDetail(BaseModel):
    session_id: UUID
    events: list[ExecutionEvent]
