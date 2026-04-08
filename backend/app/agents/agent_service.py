from datetime import datetime, timezone

from app.agents.executor import Executor
from app.agents.planner import Planner
from app.memory.memory_manager import MemoryManager
from app.models.db_models import StepLog, Task
from app.models.schemas import ChatRequest, ChatResponse
from app.providers.base import ProviderError
from app.providers.openrouter_client import OpenRouterClient
from app.services.model_policy import ModelPolicyManager
from app.services.rate_limit_manager import RateLimitError, RateLimitManager
from app.services.usage_tracker import UsageTracker
from app.tools.default_tools import (
    http_request,
    list_files,
    read_file,
    run_command,
    search_local_data,
    write_file,
)
from app.tools.tool_registry import ToolRegistry


class AgentService:
    def __init__(self, session):
        self.session = session
        self.memory = MemoryManager(session)
        self.planner = Planner()
        self.policy = ModelPolicyManager()
        self.provider = OpenRouterClient()
        self.usage = UsageTracker(session)
        self.rate_limit = RateLimitManager(self.usage)

        self.tools = ToolRegistry()
        self.tools.register("read_file", read_file)
        self.tools.register("write_file", write_file)
        self.tools.register("list_files", list_files)
        self.tools.register("http_request", http_request)
        self.tools.register("run_command", run_command)
        self.tools.register("search_local_data", search_local_data)
        self.tools.register("retrieve_memory", lambda query: self._tool_retrieve_memory(query))
        self.executor = Executor(self.tools)

    def _log(self, task_id: int, step_type: str, message: str, metadata: str = "{}") -> None:
        self.session.add(StepLog(task_id=task_id, step_type=step_type, message=message, metadata_json=metadata))
        self.session.commit()

    def _tool_retrieve_memory(self, query: str):
        hits = self.memory.retrieve_relevant(query)
        output = "\n".join([h.content for h in hits])
        from app.tools.tool_registry import ToolResult

        return ToolResult(True, output, {"hits": len(hits)})

    async def handle_chat(self, req: ChatRequest) -> ChatResponse:
        task = Task(title=req.task_title, user_input=req.message, status="running")
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        self.memory.add("conversational", f"user: {req.message}", task_id=task.id)
        plan = self.planner.classify(req.message)
        task.model_tier = self.policy.for_task(plan.task_type).tier
        task.plan = " | ".join(plan.steps)
        self.session.add(task)
        self.session.commit()

        self._log(task.id, "plan", f"classified={plan.task_type}, planning={plan.needs_planning}")

        try:
            self.rate_limit.assert_within_limits()
            self.rate_limit.consume()
        except RateLimitError as exc:
            task.status = "blocked"
            task.result = str(exc)
            self.session.add(task)
            self.session.commit()
            return ChatResponse(task_id=task.id, status=task.status, response=task.result, model_used="none", fallback_used=False)

        tool_call = self.executor.maybe_tool_call(req.message)
        if tool_call:
            tr = self.tools.run(tool_call.name, tool_call.args)
            content = f"Tool {tool_call.name} => {tr.output}"
            self.memory.add("tool", content, task_id=task.id, key=tool_call.name)
            self._log(task.id, "tool", content)
            final = content
            model_used = "tool-only"
            fallback_used = False
        else:
            relevant = self.memory.retrieve_relevant(req.message, limit=4)
            context = "\n".join([m.content for m in relevant])
            summary = self.memory.rolling_summary(10)
            messages = [
                {"role": "system", "content": "You are JARVIS, concise, practical, and tool-first."},
                {"role": "system", "content": f"Memory context:\n{context}\nRolling summary:\n{summary}"},
                {"role": "user", "content": req.message},
            ]
            models = self.policy.for_task(plan.task_type).models
            try:
                result = await self.provider.chat(messages, models)
                final = result.content
                model_used = result.model
                fallback_used = result.fallback_used
                self.usage.record_usage(
                    task_id=task.id,
                    provider="openrouter",
                    model=model_used,
                    status="ok",
                    attempts=result.attempts,
                    latency_ms=0,
                    request_fingerprint=req.message[:120],
                )
            except ProviderError as exc:
                final = f"Provider failure: {exc}"
                model_used = "none"
                fallback_used = False
                self.usage.record_usage(
                    task_id=task.id,
                    provider="openrouter",
                    model=models[0],
                    status="failed",
                    attempts=1,
                    latency_ms=0,
                    request_fingerprint=req.message[:120],
                    error_code=str(exc.code or "unknown"),
                )
                self._log(task.id, "provider_error", str(exc))

        self.memory.add("conversational", f"assistant: {final}", task_id=task.id)
        self.memory.add("task", f"task#{task.id} {req.message} => {final[:200]}", task_id=task.id)
        task.status = "done"
        task.result = final
        task.updated_at = datetime.now(timezone.utc)
        self.session.add(task)
        self.session.commit()

        return ChatResponse(task_id=task.id, status=task.status, response=final, model_used=model_used, fallback_used=fallback_used)
