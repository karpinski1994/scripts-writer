class InvalidStateTransitionError(Exception):
    def __init__(self, step_type: str, from_status: str, to_status: str):
        self.step_type = step_type
        self.from_status = from_status
        self.to_status = to_status
        super().__init__(f"Invalid transition for {step_type}: {from_status} → {to_status}")


class DependencyNotMetError(Exception):
    def __init__(self, step_type: str, missing: list[str]):
        self.step_type = step_type
        self.missing = missing
        super().__init__(f"Dependencies not met for {step_type}: {', '.join(missing)}")


class AgentExecutionError(Exception):
    def __init__(self, step_type: str, detail: str):
        self.step_type = step_type
        self.detail = detail
        super().__init__(f"Agent execution failed for {step_type}: {detail}")
