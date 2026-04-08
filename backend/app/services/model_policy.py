from dataclasses import dataclass

from app.core.config import get_settings


@dataclass
class TierPolicy:
    tier: str
    models: list[str]


class ModelPolicyManager:
    def __init__(self):
        s = get_settings()
        self.policies = {
            "cheap_fast": TierPolicy("cheap_fast", [s.primary_model, s.secondary_model, s.tertiary_model]),
            "balanced": TierPolicy("balanced", [s.primary_model, s.secondary_model, s.tertiary_model]),
            "reasoning": TierPolicy("reasoning", [s.secondary_model, s.primary_model, s.tertiary_model]),
            "emergency_free": TierPolicy("emergency_free", [s.tertiary_model, s.secondary_model]),
        }

    def for_task(self, task_type: str) -> TierPolicy:
        mapping = {
            "direct": "cheap_fast",
            "memory": "cheap_fast",
            "tool": "balanced",
            "multi_step": "reasoning",
            "summary": "cheap_fast",
        }
        tier = mapping.get(task_type, "balanced")
        return self.policies[tier]
