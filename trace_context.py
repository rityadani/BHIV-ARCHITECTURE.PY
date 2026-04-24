import uuid
from dataclasses import dataclass

@dataclass(frozen=True)
class TraceContext:
    trace_id: str
    execution_id: str


def create_trace_context() -> TraceContext:
    return TraceContext(trace_id=str(uuid.uuid4()), execution_id=str(uuid.uuid4()))
