from enum import StrEnum

from app.pipeline.errors import DependencyNotMetError, InvalidStateTransitionError


class StepType(StrEnum):
    subject = "subject"
    icp = "icp"
    hook = "hook"
    narrative = "narrative"
    retention = "retention"
    cta = "cta"
    writer = "writer"
    analysis = "analysis"
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
    StepType.subject,
    StepType.hook,
    StepType.narrative,
    StepType.retention,
    StepType.cta,
    StepType.writer,
    StepType.analysis,
]

TRANSITIONS: dict[StepStatus, list[StepStatus]] = {
    StepStatus.pending: [StepStatus.running],
    StepStatus.running: [StepStatus.completed, StepStatus.failed],
    StepStatus.failed: [StepStatus.running],
    StepStatus.completed: [],
}

VIDEO_FORMATS = {"short_video", "long_video", "vsl", "Short-form Video", "Long-form Video", "VSL"}


def has_retention(target_format: str | None) -> bool:
    return target_format in VIDEO_FORMATS


DEPENDENCY_MAP: dict[StepType, list[StepType]] = {
    StepType.icp: [],
    StepType.subject: [StepType.icp],
    StepType.hook: [StepType.icp, StepType.subject],
    StepType.narrative: [StepType.icp, StepType.subject, StepType.hook],
    StepType.retention: [StepType.icp, StepType.subject, StepType.narrative],
    StepType.cta: [StepType.icp, StepType.subject, StepType.narrative, StepType.retention],
    StepType.writer: [StepType.icp, StepType.subject, StepType.narrative, StepType.retention, StepType.cta],
    StepType.analysis: [StepType.writer],
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


def validate_step_ready(
    step_type: StepType,
    completed_steps: set[StepType],
    target_format: str | None = None,
) -> None:
    if step_type == StepType.retention:
        if not has_retention(target_format):
            return

    required = DEPENDENCY_MAP.get(step_type, [])

    if step_type in (StepType.cta, StepType.writer) and not has_retention(target_format):
        deps = {StepType.icp, StepType.subject, StepType.narrative}
    else:
        deps = set(required)

    missing = [dep.value for dep in deps if dep not in completed_steps]
    if missing:
        raise DependencyNotMetError(step_type.value, missing)
