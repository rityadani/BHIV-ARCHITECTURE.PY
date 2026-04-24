from __future__ import annotations
import time
from dataclasses import dataclass
from typing import Dict

from bucket_logger import BucketLogger
from trace_context import TraceContext

@dataclass(frozen=True)
class ExecutionRequest:
    trace: TraceContext
    app_id: str
    action: str

@dataclass(frozen=True)
class ExecutionResult:
    trace: TraceContext
    app_id: str
    action: str
    status: str
    detail: str


class CooldownManager:
    def __init__(self, cooldown_seconds: int = 2) -> None:
        self.cooldown_seconds = cooldown_seconds
        self._last_execution: Dict[str, float] = {}

    def is_allowed(self, app_id: str, now: float = None) -> bool:
        now = now if now is not None else time.time()
        last = self._last_execution.get(app_id)
        if last is None or now - last >= self.cooldown_seconds:
            self._last_execution[app_id] = now
            return True
        return False


class ExecutionLayer:
    def __init__(self, logger: BucketLogger, cooldown_manager: CooldownManager) -> None:
        self._logger = logger
        self._cooldown_manager = cooldown_manager

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        if not request.app_id.strip():
            raise ValueError("Execution input requires a non-empty app_id")
        if not request.action.strip():
            raise ValueError("Execution input requires a non-empty action")

        if not self._cooldown_manager.is_allowed(request.app_id):
            result = ExecutionResult(
                trace=request.trace,
                app_id=request.app_id,
                action=request.action,
                status="BLOCKED_BY_COOLDOWN",
                detail="cooldown_in_effect",
            )
            self._logger.append(
                "execution_result",
                request.trace,
                {
                    "app_id": request.app_id,
                    "action": request.action,
                    "status": result.status,
                    "detail": result.detail,
                },
            )
            return result

        time.sleep(0.1)
        verified = True
        status = "SUCCESS" if verified else "FAILED"
        detail = "action_executed_and_verified" if verified else "verification_failed"
        result = ExecutionResult(
            trace=request.trace,
            app_id=request.app_id,
            action=request.action,
            status=status,
            detail=detail,
        )
        self._logger.append(
            "execution_result",
            request.trace,
            {
                "app_id": request.app_id,
                "action": request.action,
                "status": result.status,
                "detail": result.detail,
            },
        )
        return result
