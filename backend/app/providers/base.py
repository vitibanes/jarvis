from dataclasses import dataclass


@dataclass
class ProviderResult:
    content: str
    model: str
    attempts: int
    fallback_used: bool


class ProviderError(Exception):
    def __init__(self, message: str, code: int | None = None):
        super().__init__(message)
        self.code = code
