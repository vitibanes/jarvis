from fastapi import APIRouter
from sqlmodel import select

from app.agents.agent_service import AgentService
from app.core.config import get_settings
from app.models.db_models import MemoryEntry, StepLog, Task
from app.models.schemas import ChatRequest, ChatResponse, StatusResponse
from app.services.usage_tracker import UsageTracker
from app.storage.db import get_session

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    with get_session() as session:
        service = AgentService(session)
        return await service.handle_chat(req)


@router.get("/tasks")
def tasks():
    with get_session() as session:
        return session.exec(select(Task).order_by(Task.id.desc()).limit(30)).all()


@router.get("/logs")
def logs():
    with get_session() as session:
        return session.exec(select(StepLog).order_by(StepLog.id.desc()).limit(80)).all()


@router.get("/memory")
def memory():
    with get_session() as session:
        return session.exec(select(MemoryEntry).order_by(MemoryEntry.id.desc()).limit(80)).all()


@router.get("/status", response_model=StatusResponse)
def status():
    with get_session() as session:
        tracker = UsageTracker(session)
        s = get_settings()
        return StatusResponse(
            minute_usage=tracker.current_count("minute"),
            day_usage=tracker.current_count("day"),
            minute_limit=s.max_requests_per_minute,
            day_limit=s.max_requests_per_day,
            provider_status="configured" if bool(s.openrouter_api_key) else "missing_api_key",
        )
