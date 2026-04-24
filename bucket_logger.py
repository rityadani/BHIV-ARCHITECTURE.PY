from __future__ import annotations
from typing import Any, Dict, List

from trace_context import TraceContext

class BucketLogger:
    def __init__(self) -> None:
        self._entries: List[Dict[str, Any]] = []

    def append(self, stage: str, trace: TraceContext, details: Dict[str, Any] = None) -> None:
        entry = {
            "stage": stage,
            "trace_id": trace.trace_id,
            "execution_id": trace.execution_id,
            "details": details or {},
        }
        self._entries.append(entry)

    @property
    def entries(self):
        return tuple(self._entries)
