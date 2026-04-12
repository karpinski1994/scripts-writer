import pytest

from app.pipeline.errors import DependencyNotMetError, InvalidStateTransitionError
from app.pipeline.state import (
    DEPENDENCY_MAP,
    STEP_ORDER,
    StepStatus,
    StepType,
    can_transition,
    validate_step_ready,
)


def test_step_type_has_10_values():
    assert len(StepType) == 10


def test_step_status_has_4_values():
    assert len(StepStatus) == 4


def test_step_order_matches_enum():
    assert STEP_ORDER == list(StepType)


def test_valid_transitions():
    assert can_transition(StepStatus.pending, StepStatus.running) is True
    assert can_transition(StepStatus.running, StepStatus.completed) is True
    assert can_transition(StepStatus.running, StepStatus.failed) is True
    assert can_transition(StepStatus.failed, StepStatus.running) is True


def test_invalid_transitions():
    assert can_transition(StepStatus.pending, StepStatus.completed) is False
    assert can_transition(StepStatus.pending, StepStatus.failed) is False
    assert can_transition(StepStatus.completed, StepStatus.running) is False
    assert can_transition(StepStatus.completed, StepStatus.pending) is False
    assert can_transition(StepStatus.failed, StepStatus.completed) is False


def test_invalid_transition_raises_error():
    from app.pipeline.state import validate_transition

    with pytest.raises(InvalidStateTransitionError):
        validate_transition("icp", StepStatus.pending, StepStatus.completed)


def test_dependency_map_icp_has_no_deps():
    assert DEPENDENCY_MAP[StepType.icp] == []


def test_dependency_map_hook_requires_icp():
    assert StepType.icp in DEPENDENCY_MAP[StepType.hook]


def test_dependency_map_analysis_requires_writer():
    for step in [StepType.factcheck, StepType.readability, StepType.copyright, StepType.policy]:
        assert StepType.writer in DEPENDENCY_MAP[step]


def test_validate_step_ready_icp_no_deps():
    validate_step_ready(StepType.icp, set())


def test_validate_step_ready_hook_requires_icp():
    with pytest.raises(DependencyNotMetError):
        validate_step_ready(StepType.hook, set())


def test_validate_step_ready_hook_passes_when_icp_completed():
    validate_step_ready(StepType.hook, {StepType.icp})


def test_validate_step_ready_writer_requires_cta():
    with pytest.raises(DependencyNotMetError):
        validate_step_ready(StepType.writer, {StepType.icp, StepType.hook})
