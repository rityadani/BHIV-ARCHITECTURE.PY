from trace_context import create_trace_context
from telemetry_layer import TelemetryLayer
from governance_layer import GovernanceLayer, GovernanceInput
from execution_layer import ExecutionLayer, ExecutionRequest, CooldownManager
from bucket_logger import BucketLogger


def run_cycle(logger: BucketLogger, app_id: str, proposed_action: str, metrics: dict):
    trace = create_trace_context()
    telemetry = TelemetryLayer(logger)
    governance = GovernanceLayer(logger)
    execution = ExecutionLayer(logger, CooldownManager(cooldown_seconds=1))

    telemetry_output = telemetry.receive_metrics(trace, metrics)
    decision_input = GovernanceInput(trace=telemetry_output.trace, app_id=app_id, proposed_action=proposed_action)
    decision = governance.enforce_action(decision_input)

    if decision.outcome == GovernanceLayer.BLOCK:
        return trace, decision, None

    execution_request = ExecutionRequest(trace=decision.trace, app_id=app_id, action=decision.action)
    result = execution.execute(execution_request)
    return trace, decision, result


def main() -> None:
    logger = BucketLogger()
    cycles = [
        {
            "app_id": "payment-service",
            "proposed_action": "scale down",
            "metrics": {"cpu_usage": 72, "memory_mb": 420, "request_rate": 180},
        },
        {
            "app_id": "analytics-engine",
            "proposed_action": "shutdown",
            "metrics": {"cpu_usage": 22, "memory_mb": 180, "request_rate": 12},
        },
    ]

    for item in cycles:
        trace, decision, result = run_cycle(
            logger,
            app_id=item["app_id"],
            proposed_action=item["proposed_action"],
            metrics=item["metrics"],
        )
        print(f"Trace={trace.trace_id} Execution={trace.execution_id}")
        print(f"Governance decision: outcome={decision.outcome}, action={decision.action}, reason={decision.reason}")
        if result:
            print(f"Execution result: status={result.status}, detail={result.detail}")
        print("---")

    print("\nBucket log entries:")
    for entry in logger.entries:
        print(entry)


if __name__ == "__main__":
    main()
