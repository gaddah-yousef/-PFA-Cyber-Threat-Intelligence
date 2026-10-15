import json
import logging
from collections import Counter
from datetime import datetime, timezone
from threading import Lock


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(json_output: bool) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter() if json_output else logging.Formatter("%(levelname)s %(name)s: %(message)s"))
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)


class MetricsRegistry:
    def __init__(self) -> None:
        self._requests: Counter[tuple[str, str, int]] = Counter()
        self._durations: Counter[tuple[str, str]] = Counter()
        self._lock = Lock()

    def observe(self, method: str, path: str, status_code: int, duration: float) -> None:
        with self._lock:
            self._requests[(method, path, status_code)] += 1
            self._durations[(method, path)] += duration

    def render(self) -> str:
        lines = [
            "# HELP sentinel_http_requests_total Nombre total de requêtes HTTP.",
            "# TYPE sentinel_http_requests_total counter",
        ]
        with self._lock:
            for (method, path, status_code), count in sorted(self._requests.items()):
                lines.append(
                    f'sentinel_http_requests_total{{method="{method}",path="{path}",status="{status_code}"}} {count}'
                )
            lines.extend(
                [
                    "# HELP sentinel_http_request_duration_seconds_total Durée HTTP cumulée.",
                    "# TYPE sentinel_http_request_duration_seconds_total counter",
                ]
            )
            for (method, path), duration in sorted(self._durations.items()):
                lines.append(
                    f'sentinel_http_request_duration_seconds_total{{method="{method}",path="{path}"}} {duration:.6f}'
                )
        return "\n".join(lines) + "\n"


metrics = MetricsRegistry()
