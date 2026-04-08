from app.models.schemas import ToolCall
from app.tools.tool_registry import ToolRegistry


class Executor:
    def __init__(self, tools: ToolRegistry):
        self.tools = tools

    def maybe_tool_call(self, user_input: str) -> ToolCall | None:
        text = user_input.lower()
        if text.startswith("read "):
            return ToolCall(name="read_file", args={"path": user_input[5:].strip()})
        if text.startswith("write "):
            return ToolCall(name="write_file", args={"path": "note.txt", "content": user_input[6:]})
        if text.startswith("list"):
            return ToolCall(name="list_files", args={"path": "."})
        if text.startswith("http "):
            return ToolCall(name="http_request", args={"url": user_input[5:].strip()})
        if text.startswith("run "):
            return ToolCall(name="run_command", args={"command": user_input[4:].strip()})
        return None
