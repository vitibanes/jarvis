from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str
    task_title: str = "User request"


class ChatResponse(BaseModel):
    task_id: int
    status: str
    response: str
    model_used: str
    fallback_used: bool


class StatusResponse(BaseModel):
    minute_usage: int
    day_usage: int
    minute_limit: int
    day_limit: int
    provider_status: str


class ToolCall(BaseModel):
    name: str
    args: dict = Field(default_factory=dict)
