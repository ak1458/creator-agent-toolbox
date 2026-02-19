from __future__ import annotations

import time
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import get_db_session, get_workflow_engine
from app.models.database import WorkflowRecord
from app.agents.ab_test_orchestrator import ABTestOrchestratorAgent
from app.models.state import (
    ContentWorkflowState,
    DeclareWinnerRequest,
    StopTestRequest,
    WorkflowApproveRequest,
    WorkflowThumbnailSelectRequest,
    WorkflowSummaryResponse,
    WorkflowStartRequest,
    WorkflowStatusResponse,
)
from app.orchestration.workflow import ContentWorkflow

router = APIRouter()


@router.get("", response_model=list[WorkflowSummaryResponse])
async def list_workflows(
    user_id: str | None = Query(default=None),
    session: AsyncSession = Depends(get_db_session),
) -> list[WorkflowSummaryResponse]:
    statement = select(WorkflowRecord)
    if user_id:
        statement = statement.where(WorkflowRecord.user_id == user_id)
    statement = statement.order_by(WorkflowRecord.updated_ts.desc())
    result = await session.exec(statement)
    records = result.all()

    return [
        WorkflowSummaryResponse(
            workflow_id=record.id,
            topic=record.topic,
            status=record.status,
            current_step=record.state_snapshot.get("current_step", "unknown"),
            created_ts=record.created_ts,
            updated_ts=record.updated_ts,
        )
        for record in records
    ]


@router.post("/start", response_model=WorkflowStatusResponse)
async def start_workflow(
    payload: WorkflowStartRequest,
    session: AsyncSession = Depends(get_db_session),
    workflow_engine: ContentWorkflow = Depends(get_workflow_engine),
) -> WorkflowStatusResponse:
    workflow_id = str(uuid.uuid4())
    now = int(time.time())

    initial_state: ContentWorkflowState = {
        "workflow_id": workflow_id,
        "user_id": payload.user_id,
        "topic": payload.topic,
        "target_platforms": payload.platforms,
        "brand_voice": payload.brand_voice,
        "trend_data": None,
        "script_variants": [],
        "selected_script_id": None,
        "thumbnail_variants": [],
        "selected_thumbnail_id": None,
        "ab_test": None,
        "current_step": "init",
        "human_approval_status": {
            "scripts_approved": False,
            "scripts_rejected": False,
            "thumbnails_approved": False,
        },
        "token_usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        },
        "errors": [],
        "created_ts": now,
        "updated_ts": now,
    }

    result = await workflow_engine.run(initial_state, thread_id=workflow_id)

    record = WorkflowRecord(
        id=workflow_id,
        user_id=payload.user_id,
        topic=payload.topic,
        target_platforms=payload.platforms,
        status=_map_status(result["current_step"]),
        state_snapshot=result,
        created_ts=now,
        updated_ts=result["updated_ts"],
    )

    session.add(record)
    await session.commit()

    return _to_response(result)


@router.get("/{workflow_id}/status", response_model=WorkflowStatusResponse)
async def workflow_status(
    workflow_id: str,
    session: AsyncSession = Depends(get_db_session),
) -> WorkflowStatusResponse:
    statement = select(WorkflowRecord).where(WorkflowRecord.id == workflow_id)
    result = await session.exec(statement)
    record = result.one_or_none()

    if not record:
        raise HTTPException(status_code=404, detail="Workflow not found")

    return _to_response(record.state_snapshot)


@router.post("/{workflow_id}/approve", response_model=WorkflowStatusResponse)
async def approve_workflow(
    workflow_id: str,
    payload: WorkflowApproveRequest,
    session: AsyncSession = Depends(get_db_session),
    workflow_engine: ContentWorkflow = Depends(get_workflow_engine),
) -> WorkflowStatusResponse:
    statement = select(WorkflowRecord).where(WorkflowRecord.id == workflow_id)
    result = await session.exec(statement)
    record = result.one_or_none()

    if not record:
        raise HTTPException(status_code=404, detail="Workflow not found")

    state = record.state_snapshot

    if not state.get("script_variants"):
        raise HTTPException(status_code=400, detail="No scripts available for approval")

    if payload.action == "approve":
        selected_id = payload.selected_script_id or state["script_variants"][0]["id"]
        script_ids = {script["id"] for script in state["script_variants"]}
        if selected_id not in script_ids:
            raise HTTPException(status_code=400, detail="Invalid selected_script_id")

        state["selected_script_id"] = selected_id
        state["human_approval_status"]["scripts_approved"] = True
        state["human_approval_status"]["scripts_rejected"] = False
        state["selected_thumbnail_id"] = None
        state["human_approval_status"]["thumbnails_approved"] = False
    else:
        state["selected_script_id"] = None
        state["human_approval_status"]["scripts_approved"] = False
        state["human_approval_status"]["scripts_rejected"] = True
        state["selected_thumbnail_id"] = None
        state["human_approval_status"]["thumbnails_approved"] = False

    state["updated_ts"] = int(time.time())

    updated_state = await workflow_engine.run(state, thread_id=workflow_id)

    record.status = _map_status(updated_state["current_step"])
    record.state_snapshot = updated_state
    record.updated_ts = updated_state["updated_ts"]

    session.add(record)
    await session.commit()

    return _to_response(updated_state)


@router.post("/{workflow_id}/select-thumbnail", response_model=WorkflowStatusResponse)
async def select_thumbnail(
    workflow_id: str,
    payload: WorkflowThumbnailSelectRequest,
    session: AsyncSession = Depends(get_db_session),
    workflow_engine: ContentWorkflow = Depends(get_workflow_engine),
) -> WorkflowStatusResponse:
    statement = select(WorkflowRecord).where(WorkflowRecord.id == workflow_id)
    result = await session.exec(statement)
    record = result.one_or_none()

    if not record:
        raise HTTPException(status_code=404, detail="Workflow not found")

    state = record.state_snapshot
    thumbnails = state.get("thumbnail_variants", [])
    if not thumbnails:
        raise HTTPException(status_code=400, detail="No thumbnails available for selection")

    thumbnail_ids = {thumbnail["id"] for thumbnail in thumbnails}
    if payload.selected_thumbnail_id not in thumbnail_ids:
        raise HTTPException(status_code=400, detail="Invalid selected_thumbnail_id")

    state["selected_thumbnail_id"] = payload.selected_thumbnail_id
    state["human_approval_status"]["thumbnails_approved"] = True
    state["updated_ts"] = int(time.time())

    updated_state = await workflow_engine.run(state, thread_id=workflow_id)

    record.status = _map_status(updated_state["current_step"])
    record.state_snapshot = updated_state
    record.updated_ts = updated_state["updated_ts"]

    session.add(record)
    await session.commit()

    return _to_response(updated_state)


def _map_status(step: str) -> str:
    if step == "completed":
        return "completed"
    if step == "awaiting_approval":
        return "awaiting_approval"
    if step == "awaiting_thumbnail_selection":
        return "awaiting_thumbnail_selection"
    if step in ["ab_testing", "ab_test_complete"]:
        return "ab_testing"
    return "running"


def _to_response(state: dict) -> WorkflowStatusResponse:
    step = state.get("current_step", "unknown")
    if step == "awaiting_approval":
        requires_action = "script_approval"
    elif step == "awaiting_thumbnail_selection":
        requires_action = "thumbnail_selection"
    elif step in ["ab_testing", "ab_test_complete"]:
        requires_action = "ab_test_monitoring"
    else:
        requires_action = None

    return WorkflowStatusResponse(
        workflow_id=state["workflow_id"],
        status=_map_status(step),
        current_step=step,
        requires_action=requires_action,
        scripts=state.get("script_variants", []),
        selected_script_id=state.get("selected_script_id"),
        thumbnails=state.get("thumbnail_variants", []),
        selected_thumbnail_id=state.get("selected_thumbnail_id"),
        token_usage=state.get("token_usage", {}),
    )


@router.get("/{workflow_id}/ab-status")
async def get_ab_test_status(
    workflow_id: str,
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """
    Get current A/B test metrics and statistics.
    Frontend polls this every 5-10 seconds during testing phase.
    """
    statement = select(WorkflowRecord).where(WorkflowRecord.id == workflow_id)
    result = await session.exec(statement)
    record = result.one_or_none()

    if not record:
        raise HTTPException(status_code=404, detail="Workflow not found")

    state = record.state_snapshot

    if "ab_test" not in state or not state["ab_test"]:
        raise HTTPException(status_code=400, detail="A/B test not started yet")

    ab_test = state["ab_test"]

    # Calculate time remaining
    elapsed = time.time() - ab_test["started_at"]
    max_duration = 72 * 3600  # 72 hours in seconds
    time_remaining = max(0, max_duration - elapsed)

    return {
        "workflow_id": workflow_id,
        "status": ab_test["status"],  # running, completed, timeout, manual_override
        "is_running": ab_test["status"] == "running",
        "variants": ab_test["variants"],
        "current_confidence": ab_test["confidence"],
        "total_impressions": ab_test["total_impressions"],
        "winner_id": ab_test.get("winner_id"),
        "elapsed_time_seconds": int(elapsed),
        "estimated_time_remaining": int(time_remaining),
        "checks_completed": ab_test.get("check_count", 0),
        "can_declare_early": ab_test["confidence"] > 0.90 or elapsed > 3600,  # 1 hour minimum
    }


@router.post("/{workflow_id}/declare-winner", response_model=WorkflowStatusResponse)
async def declare_winner_manually(
    workflow_id: str,
    request: DeclareWinnerRequest,
    session: AsyncSession = Depends(get_db_session),
    workflow_engine: ContentWorkflow = Depends(get_workflow_engine),
) -> WorkflowStatusResponse:
    """
    Manual override to declare a winner before statistical significance.
    Human sovereignty over AI decision.
    """
    statement = select(WorkflowRecord).where(WorkflowRecord.id == workflow_id)
    result = await session.exec(statement)
    record = result.one_or_none()

    if not record:
        raise HTTPException(status_code=404, detail="Workflow not found")

    state = record.state_snapshot

    # Validate thumbnail_id exists in variants
    valid_ids = {v["id"] for v in state.get("thumbnail_variants", [])}
    if request.thumbnail_id not in valid_ids:
        raise HTTPException(status_code=400, detail="Invalid thumbnail ID")

    # Force winner
    agent = ABTestOrchestratorAgent()
    new_state = await agent.force_winner(state, request.thumbnail_id)
    new_state["updated_ts"] = int(time.time())

    # Resume workflow to completion
    updated_state = await workflow_engine.run(new_state, thread_id=workflow_id)

    record.status = _map_status(updated_state["current_step"])
    record.state_snapshot = updated_state
    record.updated_ts = updated_state["updated_ts"]

    session.add(record)
    await session.commit()

    return _to_response(updated_state)


@router.post("/{workflow_id}/stop-test", response_model=WorkflowStatusResponse)
async def stop_ab_test(
    workflow_id: str,
    request: StopTestRequest,
    session: AsyncSession = Depends(get_db_session),
    workflow_engine: ContentWorkflow = Depends(get_workflow_engine),
) -> WorkflowStatusResponse:
    """
    Stop A/B test early without declaring winner (inconclusive).
    Picks current best performer.
    """
    statement = select(WorkflowRecord).where(WorkflowRecord.id == workflow_id)
    result = await session.exec(statement)
    record = result.one_or_none()

    if not record:
        raise HTTPException(status_code=404, detail="Workflow not found")

    state = record.state_snapshot
    ab_test = state.get("ab_test", {})

    if ab_test.get("status") != "running":
        raise HTTPException(status_code=400, detail="Test not running")

    # Pick best current performer
    variants = ab_test.get("variants", [])
    if variants:
        best = max(variants, key=lambda x: x["ctr"])

        agent = ABTestOrchestratorAgent()
        new_state = await agent.force_winner(state, best["thumbnail_id"])
        new_state["updated_ts"] = int(time.time())

        updated_state = await workflow_engine.run(new_state, thread_id=workflow_id)

        record.status = _map_status(updated_state["current_step"])
        record.state_snapshot = updated_state
        record.updated_ts = updated_state["updated_ts"]

        session.add(record)
        await session.commit()

        return _to_response(updated_state)

    raise HTTPException(status_code=400, detail="No variants to evaluate")


@router.get("/{workflow_id}/results")
async def get_final_results(
    workflow_id: str,
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """
    Get complete results after workflow completion.
    Includes winning script, winning thumbnail, and A/B test statistics.
    """
    statement = select(WorkflowRecord).where(WorkflowRecord.id == workflow_id)
    result = await session.exec(statement)
    record = result.one_or_none()

    if not record:
        raise HTTPException(status_code=404, detail="Workflow not found")

    state = record.state_snapshot

    if state["current_step"] != "completed":
        raise HTTPException(status_code=400, detail="Workflow not completed yet")

    # Find winning script
    scripts = state.get("script_variants", [])
    winning_script = next(
        (s for s in scripts if s["id"] == state.get("selected_script_id")),
        None,
    )

    # Find winning thumbnail
    thumbnails = state.get("thumbnail_variants", [])
    winning_thumb = next(
        (t for t in thumbnails if t["id"] == state.get("selected_thumbnail_id")),
        None,
    )

    ab_stats = state.get("ab_test", {})
    final_stats = ab_stats.get("final_stats", {})

    return {
        "workflow_id": workflow_id,
        "topic": state["topic"],
        "status": "completed",
        "winning_content": {
            "script": winning_script,
            "thumbnail": winning_thumb,
            "combined_ctr": final_stats.get("treatment_ctr")
            or (
                max(ab_stats.get("variants", []), key=lambda x: x["ctr"], default={}).get("ctr")
                if ab_stats.get("variants")
                else None
            ),
        },
        "ab_test_summary": {
            "duration_hours": (ab_stats.get("last_updated", 0) - ab_stats.get("started_at", 0))
            / 3600,
            "total_impressions": ab_stats.get("total_impressions"),
            "confidence_reached": ab_stats.get("confidence", 0),
            "was_manual_override": ab_stats.get("status") == "manual_override",
        },
        "export_ready": True,
    }
