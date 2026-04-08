from app.core.config import get_settings
from app.services.usage_tracker import UsageTracker


class RateLimitError(Exception):
    pass


class RateLimitManager:
    def __init__(self, tracker: UsageTracker):
        self.tracker = tracker
        self.settings = get_settings()

    def assert_within_limits(self) -> None:
        minute = self.tracker.current_count("minute")
        day = self.tracker.current_count("day")
        if minute >= self.settings.max_requests_per_minute:
            raise RateLimitError("Per-minute request limit reached")
        if day >= self.settings.max_requests_per_day:
            raise RateLimitError("Per-day request limit reached")

    def consume(self) -> None:
        self.tracker.increment("minute")
        self.tracker.increment("day")
