from __future__ import annotations
from dataclasses import dataclass
from typing import Dict

from bucket_logger import BucketLogger
from trace_context import TraceContext

@dataclass(frozen=True)
class GovernanceInput:
    trace: TraceContext
    app_id: str
    proposed_action: str

@dataclass(frozen=True)
class GovernanceDecision:
    trace: TraceContext
    outcome: str
    action: str
    reason: str


class GovernanceLayer:
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    MODIFY = "MODIFY"

    def __init__(self, logger: BucketLogger) -> None:
        self._logger = logger

    def enforce_action(self, input_data: GovernanceInput) -> GovernanceDecision:
        proposed = input_data.proposed_action.strip().lower()
        allowed_actions = {"deploy", "restart", "scale_up", "scale_down", "noop"}
        deterministic_modifications: Dict[str, str] = {
            "scale down": "scale_down",
            "scale up": "scale_up",
            "restart-service": "restart",
            "deploy-app": "deploy",
            "no-op": "noop",
        }

        if not proposed:
            decision = GovernanceDecision(
                trace=input_data.trace,
                outcome=self.BLOCK,
                action="",
                reason="missing_proposed_action",
            )
        elif proposed in allowed_actions:
            decision = GovernanceDecision(
                trace=input_data.trace,
                outcome=self.ALLOW,
                action=proposed,
                reason="allowed_action",
            )
        elif proposed in deterministic_modifications:
            decision = GovernanceDecision(
                trace=input_data.trace,
                outcome=self.MODIFY,
                action=deterministic_modifications[proposed],
                reason="deterministic_modification",
            )
        else:
            decision = GovernanceDecision(
                trace=input_data.trace,
                outcome=self.BLOCK,
                action="",
                reason="unsupported_action",
            )

        self._logger.append(
            "action_proposed",
            input_data.trace,
            {
                "app_id": input_data.app_id,
                "proposed_action": input_data.proposed_action,
            },
        )
        self._logger.append(
            "governance_decision",
            input_data.trace,
            {
                "app_id": input_data.app_id,
                "proposed_action": input_data.proposed_action,
                "outcome": decision.outcome,
                "action": decision.action,
                "reason": decision.reason,
            },
        )
        return decision
