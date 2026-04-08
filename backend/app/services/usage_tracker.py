from datetime import datetime, timezone
from sqlmodel import select

from app.models.db_models import RequestCounter, UsageRecord


class UsageTracker:
    def __init__(self, session):
        self.session = session

    def _window_key(self, kind: str) -> str:
        now = datetime.now(timezone.utc)
        return now.strftime("%Y-%m-%d-%H-%M") if kind == "minute" else now.strftime("%Y-%m-%d")

    def increment(self, kind: str) -> int:
        key = self._window_key(kind)
        stmt = select(RequestCounter).where(RequestCounter.window_type == kind, RequestCounter.window_key == key)
        counter = self.session.exec(stmt).first()
        if not counter:
            counter = RequestCounter(window_type=kind, window_key=key, count=0)
            self.session.add(counter)
        counter.count += 1
        self.session.commit()
        return counter.count

    def current_count(self, kind: str) -> int:
        key = self._window_key(kind)
        stmt = select(RequestCounter).where(RequestCounter.window_type == kind, RequestCounter.window_key == key)
        counter = self.session.exec(stmt).first()
        return counter.count if counter else 0

    def record_usage(self, **kwargs) -> None:
        self.session.add(UsageRecord(**kwargs))
        self.session.commit()
