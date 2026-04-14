from app.agents.cta_agent import CTAAgent
from app.agents.hook_agent import HookAgent
from app.agents.narrative_agent import NarrativeAgent
from app.agents.retention_agent import RetentionAgent
from app.agents.writer_agent import WriterAgent
from app.schemas.agents import (
    CTAAgentInput,
    HookAgentInput,
    HookSuggestion,
    NarrativeAgentInput,
    NarrativePattern,
    RetentionAgentInput,
    RetentionTechnique,
    WriterAgentInput,
)
from app.schemas.icp import ICPProfile


def _icp():
    return ICPProfile(language_style="casual")


def _hook():
    return HookSuggestion(hook_type="question", text="Ever wondered why?", reasoning="test")


def _narrative():
    return NarrativePattern(
        pattern_name="Hero's Journey", description="Classic", structure=["call", "struggle", "return"]
    )


def _retention():
    return RetentionTechnique(technique_name="open loop", description="Tease then reveal", placement_hint="middle")


def _cta():
    from app.schemas.agents import CTASuggestion

    return CTASuggestion(cta_type="direct", text="Buy now", reasoning="test")


def test_hook_agent_build_prompt_contains_icp_and_topic():
    agent = HookAgent()
    input_data = HookAgentInput(icp=_icp(), topic="Python", target_format="VSL", content_goal="Sell")
    prompt = agent.build_prompt(input_data)
    assert "Python" in prompt
    assert "ICP Summary" in prompt
    assert "VSL" in prompt
    assert "Sell" in prompt


def test_hook_agent_cache_key_deterministic():
    agent = HookAgent()
    input_data = HookAgentInput(icp=_icp(), topic="T", target_format="VSL")
    assert agent._compute_cache_key(input_data) == agent._compute_cache_key(input_data)


def test_narrative_agent_build_prompt_contains_hook():
    agent = NarrativeAgent()
    input_data = NarrativeAgentInput(icp=_icp(), selected_hook=_hook(), topic="T", target_format="VSL")
    prompt = agent.build_prompt(input_data)
    assert "Selected Hook" in prompt
    assert "Ever wondered why?" in prompt


def test_narrative_agent_cache_key_deterministic():
    agent = NarrativeAgent()
    input_data = NarrativeAgentInput(icp=_icp(), selected_hook=_hook(), topic="T", target_format="VSL")
    assert agent._compute_cache_key(input_data) == agent._compute_cache_key(input_data)


def test_retention_agent_build_prompt_contains_narrative():
    agent = RetentionAgent()
    input_data = RetentionAgentInput(
        icp=_icp(), selected_hook=_hook(), selected_narrative=_narrative(), target_format="VSL"
    )
    prompt = agent.build_prompt(input_data)
    assert "Selected Narrative" in prompt
    assert "Hero's Journey" in prompt


def test_retention_agent_cache_key_deterministic():
    agent = RetentionAgent()
    input_data = RetentionAgentInput(
        icp=_icp(), selected_hook=_hook(), selected_narrative=_narrative(), target_format="VSL"
    )
    assert agent._compute_cache_key(input_data) == agent._compute_cache_key(input_data)


def test_cta_agent_build_prompt_contains_hook_and_narrative():
    agent = CTAAgent()
    input_data = CTAAgentInput(
        icp=_icp(),
        selected_hook=_hook(),
        selected_narrative=_narrative(),
        cta_purpose="Go to the course",
        content_goal="Sell",
    )
    prompt = agent.build_prompt(input_data)
    assert "Primary CTA Goal (most important instruction)" in prompt
    assert "Go to the course" in prompt
    assert "Selected Hook" in prompt
    assert "Selected Narrative" in prompt
    assert "Content Goal (secondary context): Sell" in prompt
    assert prompt.index("Primary CTA Goal (most important instruction)") < prompt.index("ICP Summary")


def test_cta_agent_cache_key_deterministic():
    agent = CTAAgent()
    input_data = CTAAgentInput(icp=_icp(), selected_hook=_hook(), selected_narrative=_narrative())
    assert agent._compute_cache_key(input_data) == agent._compute_cache_key(input_data)


def test_writer_agent_build_prompt_contains_all_upstream():
    agent = WriterAgent()
    input_data = WriterAgentInput(
        icp=_icp(),
        selected_hook=_hook(),
        selected_narrative=_narrative(),
        selected_retention=_retention(),
        selected_cta=_cta(),
        topic="Python",
        target_format="VSL",
        content_goal="Sell",
        raw_notes="some notes",
    )
    prompt = agent.build_prompt(input_data)
    assert "Selected Hook" in prompt
    assert "Selected Narrative" in prompt
    assert "Selected Retention" in prompt
    assert "Selected CTA" in prompt
    assert "Python" in prompt
    assert "some notes" in prompt


def test_writer_agent_cache_key_deterministic():
    agent = WriterAgent()
    input_data = WriterAgentInput(
        icp=_icp(),
        selected_hook=_hook(),
        selected_narrative=_narrative(),
        selected_retention=_retention(),
        selected_cta=_cta(),
        topic="T",
        target_format="VSL",
    )
    assert agent._compute_cache_key(input_data) == agent._compute_cache_key(input_data)


def test_writer_agent_cache_key_differs_for_different_input():
    agent = WriterAgent()
    base = WriterAgentInput(
        icp=_icp(),
        selected_hook=_hook(),
        selected_narrative=_narrative(),
        selected_retention=_retention(),
        selected_cta=_cta(),
        topic="A",
        target_format="VSL",
    )
    different = WriterAgentInput(
        icp=_icp(),
        selected_hook=_hook(),
        selected_narrative=_narrative(),
        selected_retention=_retention(),
        selected_cta=_cta(),
        topic="B",
        target_format="VSL",
    )
    assert agent._compute_cache_key(base) != agent._compute_cache_key(different)
