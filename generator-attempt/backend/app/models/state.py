from __future__ import annotations

from typing import Any, Literal, TypedDict

from pydantic import BaseModel, Field


class ScriptVariant(TypedDict):
    id: str
    hook: str
    body: str
    cta: str
    predicted_retention: float
    tone: str


class ThumbnailVariant(TypedDict):
    id: str
    style: str
    prompt: str
    image_url: str
    seed: int


class ABTestVariantMetrics(TypedDict):
    thumbnail_id: str
    style: str
    impressions: int
    clicks: int
    ctr: float
    avg_view_duration: int
    confidence: float


class ABTestState(TypedDict):
    started_at: float
    last_updated: float
    status: str  # running, completed, timeout, manual_override
    variants: list[ABTestVariantMetrics]
    winner_id: str | None
    confidence: float
    total_impressions: int
    check_count: int
    final_stats: dict[str, Any] | None


class ContentWorkflowState(TypedDict):
    workflow_id: str
    user_id: str
    topic: str
    target_platforms: list[str]
    brand_voice: str

    trend_data: dict[str, Any] | None
    script_variants: list[ScriptVariant]
    selected_script_id: str | None
    thumbnail_variants: list[ThumbnailVariant]
    selected_thumbnail_id: str | None
    ab_test: ABTestState | None

    current_step: str
    human_approval_status: dict[str, bool]
    token_usage: dict[str, int]
    errors: list[str]

    created_ts: int
    updated_ts: int


class WorkflowStartRequest(BaseModel):
    topic: str = Field(min_length=1)
    platforms: list[str] = Field(default_factory=lambda: ["youtube"])
    user_id: str = "user_001"
    brand_voice: str = "educational"


class WorkflowApproveRequest(BaseModel):
    selected_script_id: str | None = None
    action: Literal["approve", "reject"] = "approve"


class WorkflowThumbnailSelectRequest(BaseModel):
    selected_thumbnail_id: str = Field(min_length=1)


class DeclareWinnerRequest(BaseModel):
    thumbnail_id: str = Field(min_length=1)


class StopTestRequest(BaseModel):
    reason: str = "manual_stop"


class ABTestStatusResponse(BaseModel):
    workflow_id: str
    status: str
    is_running: bool
    variants: list[dict[str, Any]]
    current_confidence: float
    total_impressions: int
    winner_id: str | None
    elapsed_time_seconds: int
    estimated_time_remaining: int
    checks_completed: int
    can_declare_early: bool


class WorkflowStatusResponse(BaseModel):
    workflow_id: str
    status: str
    current_step: str
    requires_action: str | None = None
    scripts: list[dict[str, Any]] = Field(default_factory=list)
    selected_script_id: str | None = None
    thumbnails: list[dict[str, Any]] = Field(default_factory=list)
    selected_thumbnail_id: str | None = None
    token_usage: dict[str, int] = Field(default_factory=dict)


class WorkflowSummaryResponse(BaseModel):
    workflow_id: str
    topic: str
    status: str
    current_step: str
    created_ts: int
    updated_ts: int
