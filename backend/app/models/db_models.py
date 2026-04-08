from datetime import datetime, timezone
from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    user_input: str
    status: str = "pending"
    plan: str = ""
    result: str = ""
    model_tier: str = "cheap_fast"
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class StepLog(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    task_id: int
    step_type: str
    message: str
    metadata_json: str = "{}"
    created_at: datetime = Field(default_factory=utcnow)


class MemoryEntry(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    task_id: int | None = None
    memory_type: str  # conversational, summary, factual, task, tool
    key: str = ""
    content: str
    embedding_json: str = "[]"
    created_at: datetime = Field(default_factory=utcnow)


class RequestCounter(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    window_type: str  # minute/day
    window_key: str
    count: int = 0
    updated_at: datetime = Field(default_factory=utcnow)


class UsageRecord(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    task_id: int | None = None
    provider: str
    model: str
    status: str
    attempts: int = 1
    latency_ms: int = 0
    request_fingerprint: str = ""
    error_code: str = ""
    created_at: datetime = Field(default_factory=utcnow)
