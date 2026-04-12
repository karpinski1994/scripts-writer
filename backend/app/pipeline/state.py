from enum import StrEnum

from app.pipeline.errors import DependencyNotMetError, InvalidStateTransitionError


class StepType(StrEnum):
    icp = "icp"
    hook = "hook"
    narrative = "narrative"
    retention = "retention"
    cta = "cta"
    writer = "writer"
    factcheck = "factcheck"
    readability = "readability"
    copyright = "copyright"
    policy = "policy"


class StepStatus(StrEnum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


STEP_ORDER: list[StepType] = [
    StepType.icp,
    StepType.hook,
    StepType.narrative,
    StepType.retention,
    StepType.cta,
    StepType.writer,
    StepType.factcheck,
    StepType.readability,
    StepType.copyright,
    StepType.policy,
]

TRANSITIONS: dict[StepStatus, list[StepStatus]] = {
    StepStatus.pending: [StepStatus.running],
    StepStatus.running: [StepStatus.completed, StepStatus.failed],
    StepStatus.failed: [StepStatus.running],
    StepStatus.completed: [],
}

DEPENDENCY_MAP: dict[StepType, list[StepType]] = {
    StepType.icp: [],
    StepType.hook: [StepType.icp],
    StepType.narrative: [StepType.hook],
    StepType.retention: [StepType.narrative],
    StepType.cta: [StepType.retention],
    StepType.writer: [StepType.cta],
    StepType.factcheck: [StepType.writer],
    StepType.readability: [StepType.writer],
    StepType.copyright: [StepType.writer],
    StepType.policy: [StepType.writer],
}


def can_transition(from_status: StepStatus, to_status: StepStatus) -> bool:
    return to_status in TRANSITIONS.get(from_status, [])


def validate_transition(step_type: str, from_status: StepStatus, to_status: StepStatus) -> None:
    if not can_transition(from_status, to_status):
        raise InvalidStateTransitionError(step_type, from_status.value, to_status.value)


def validate_step_ready(step_type: StepType, completed_steps: set[StepType]) -> None:
    required = DEPENDENCY_MAP.get(step_type, [])
    missing = [dep.value for dep in required if dep not in completed_steps]
    if missing:
        raise DependencyNotMetError(step_type.value, missing)
