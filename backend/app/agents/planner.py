from dataclasses import dataclass


@dataclass
class Plan:
    task_type: str
    needs_planning: bool
    steps: list[str]


class Planner:
    def classify(self, user_goal: str) -> Plan:
        text = user_goal.lower()
        if any(x in text for x in ["remember", "recall", "what did i say"]):
            return Plan("memory", False, ["Retrieve relevant memory", "Return concise answer"])
        if any(x in text for x in ["file", "http", "command", "list", "write", "read"]):
            return Plan("tool", True, ["Map to tool", "Execute tool", "Summarize result"])
        if any(x in text for x in ["plan", "roadmap", "steps", "multi"]):
            return Plan("multi_step", True, ["Create concise plan", "Execute steps", "Return result"])
        return Plan("direct", False, ["Respond directly"])
