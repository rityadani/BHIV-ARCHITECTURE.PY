from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any

from bucket_logger import BucketLogger
from trace_context import TraceContext

@dataclass(frozen=True)
class TelemetryOutput:
    trace: TraceContext
    metrics: Dict[str, Any]


class TelemetryLayer:
    def __init__(self, logger: BucketLogger) -> None:
        self._logger = logger

    def receive_metrics(self, trace: TraceContext, raw_metrics: Dict[str, Any]) -> TelemetryOutput:
        self._logger.append("telemetry_received", trace, {"metrics": raw_metrics})
        metrics = {k: v for k, v in raw_metrics.items() if isinstance(v, (int, float, str, bool))}
        return TelemetryOutput(trace=trace, metrics=metrics)
