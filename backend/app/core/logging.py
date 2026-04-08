import json
import logging
from datetime import datetime, timezone


def setup_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")


class JsonLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def info(self, event: str, **kwargs) -> None:
        payload = {"ts": datetime.now(timezone.utc).isoformat(), "event": event, **kwargs}
        self.logger.info(json.dumps(payload, default=str))

    def error(self, event: str, **kwargs) -> None:
        payload = {"ts": datetime.now(timezone.utc).isoformat(), "event": event, **kwargs}
        self.logger.error(json.dumps(payload, default=str))
