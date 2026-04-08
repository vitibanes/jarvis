from dataclasses import dataclass
from typing import Callable


@dataclass
class ToolResult:
    ok: bool
    output: str
    metadata: dict


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Callable] = {}

    def register(self, name: str, fn: Callable) -> None:
        self._tools[name] = fn

    def list_tools(self) -> list[str]:
        return sorted(self._tools.keys())

    def run(self, name: str, args: dict) -> ToolResult:
        if name not in self._tools:
            return ToolResult(ok=False, output=f"Unknown tool: {name}", metadata={})
        try:
            return self._tools[name](**args)
        except Exception as exc:
            return ToolResult(ok=False, output=str(exc), metadata={"error": True})
