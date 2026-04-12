from app.agents.icp_agent import ICPAgent
from app.schemas.icp import ICPAgentInput


def test_build_prompt_contains_notes_and_topic():
    agent = ICPAgent()
    input_data = ICPAgentInput(raw_notes="sell Python course", topic="Python", target_format="VSL")
    prompt = agent.build_prompt(input_data)
    assert "sell Python course" in prompt
    assert "Python" in prompt


def test_build_prompt_contains_format_and_goal():
    agent = ICPAgent()
    input_data = ICPAgentInput(raw_notes="notes", topic="T", target_format="VSL", content_goal="Sell")
    prompt = agent.build_prompt(input_data)
    assert "VSL" in prompt
    assert "Sell" in prompt


def test_build_prompt_omits_goal_when_none():
    agent = ICPAgent()
    input_data = ICPAgentInput(raw_notes="notes", topic="T", target_format="VSL")
    prompt = agent.build_prompt(input_data)
    assert "Content Goal" not in prompt


def test_cache_key_is_deterministic():
    agent = ICPAgent()
    input_data = ICPAgentInput(raw_notes="notes", topic="T", target_format="VSL")
    key1 = agent._compute_cache_key(input_data)
    key2 = agent._compute_cache_key(input_data)
    assert key1 == key2


def test_cache_key_differs_for_different_input():
    agent = ICPAgent()
    input_a = ICPAgentInput(raw_notes="a", topic="T", target_format="VSL")
    input_b = ICPAgentInput(raw_notes="b", topic="T", target_format="VSL")
    assert agent._compute_cache_key(input_a) != agent._compute_cache_key(input_b)
