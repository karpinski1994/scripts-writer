import pytest
from sqlalchemy import select

from app.agents.copyright_agent import CopyrightAgent
from app.agents.factcheck_agent import FactCheckAgent
from app.agents.policy_agent import PolicyAgent
from app.agents.readability_agent import ReadabilityAgent, compute_readability_scores
from app.schemas.analysis import (
    CopyrightAgentInput,
    FactCheckAgentInput,
    Finding,
    PolicyAgentInput,
    ReadabilityAgentInput,
)


def test_factcheck_agent_build_prompt():
    agent = FactCheckAgent()
    input_data = FactCheckAgentInput(
        script_content="This product cures everything.", topic="Health", target_format="VSL"
    )
    prompt = agent.build_prompt(input_data)
    assert "This product cures everything." in prompt
    assert "Health" in prompt
    assert "VSL" in prompt


def test_factcheck_agent_cache_key_deterministic():
    agent = FactCheckAgent()
    input_data = FactCheckAgentInput(script_content="Hello", topic="T", target_format="VSL")
    assert agent._compute_cache_key(input_data) == agent._compute_cache_key(input_data)


def test_readability_agent_build_prompt():
    agent = ReadabilityAgent()
    input_data = ReadabilityAgentInput(script_content="The quick brown fox jumps.", target_format="YouTube")
    prompt = agent.build_prompt(input_data)
    assert "The quick brown fox jumps." in prompt
    assert "Flesch-Kincaid" in prompt
    assert "Gunning Fog" in prompt


def test_readability_agent_cache_key_deterministic():
    agent = ReadabilityAgent()
    input_data = ReadabilityAgentInput(script_content="Hello world.", target_format="VSL")
    assert agent._compute_cache_key(input_data) == agent._compute_cache_key(input_data)


def test_copyright_agent_build_prompt():
    agent = CopyrightAgent()
    input_data = CopyrightAgentInput(script_content="Use Coca-Cola everyday.", topic="Drinks", target_format="YouTube")
    prompt = agent.build_prompt(input_data)
    assert "Use Coca-Cola everyday." in prompt
    assert "Drinks" in prompt


def test_copyright_agent_cache_key_deterministic():
    agent = CopyrightAgent()
    input_data = CopyrightAgentInput(script_content="Hello", topic="T", target_format="VSL")
    assert agent._compute_cache_key(input_data) == agent._compute_cache_key(input_data)


def test_policy_agent_build_prompt():
    agent = PolicyAgent()
    input_data = PolicyAgentInput(script_content="Buy now and earn $10,000!", topic="Finance", target_format="YouTube")
    prompt = agent.build_prompt(input_data)
    assert "Buy now and earn $10,000!" in prompt
    assert "YouTube" in prompt


def test_policy_agent_cache_key_deterministic():
    agent = PolicyAgent()
    input_data = PolicyAgentInput(script_content="Hello", topic="T", target_format="VSL")
    assert agent._compute_cache_key(input_data) == agent._compute_cache_key(input_data)


def test_readability_scores_simple_text():
    text = "The cat sat on the mat. The dog ran to the park. It was a nice day."
    fk, gf = compute_readability_scores(text)
    assert isinstance(fk, float)
    assert isinstance(gf, float)
    assert gf > 0


def test_readability_scores_empty_text():
    fk, gf = compute_readability_scores("")
    assert fk == 0.0
    assert gf == 0.0


def test_readability_scores_complex_text():
    text = (
        "Notwithstanding the aforementioned circumstances, the institutionalized "
        "organizational methodology necessitates comprehensive evaluation. "
        "Furthermore, the predetermined conceptualization fundamentally undermines "
        "the aforementioned theoretical framework."
    )
    fk, gf = compute_readability_scores(text)
    assert fk > 10
    assert gf > 14


def test_readability_scores_simple_sentences():
    text = "The cat sat. The dog ran. The bird flew. It was fun."
    fk, gf = compute_readability_scores(text)
    assert fk < 10


@pytest.mark.asyncio
async def test_analysis_service_upsert(db_session):
    from app.db.models import AnalysisResult, Project, ScriptVersion
    from app.services.analysis_service import AnalysisService

    from uuid import uuid4

    project = Project(
        id=str(uuid4()),
        name="Test",
        topic="Test",
        target_format="VSL",
        raw_notes="notes",
    )
    db_session.add(project)
    version = ScriptVersion(
        id=str(uuid4()),
        project_id=project.id,
        version_number=1,
        content="test content",
        format="VSL",
    )
    db_session.add(version)
    await db_session.commit()

    service = AnalysisService(db_session)
    findings = [Finding(type="claim", severity="medium", text="Test finding", suggestion="Fix it", confidence=0.8)]

    result1 = await service.save_result(
        project_id=project.id,
        script_version_id=version.id,
        agent_type="factcheck",
        findings=findings,
    )
    assert result1.agent_type == "factcheck"
    assert len(result1.findings) == 1

    new_findings = [Finding(type="claim", severity="low", text="Updated", suggestion="OK", confidence=0.9)]
    result2 = await service.save_result(
        project_id=project.id,
        script_version_id=version.id,
        agent_type="factcheck",
        findings=new_findings,
    )
    assert len(result2.findings) == 1
    assert result2.findings[0].text == "Updated"

    all_results = await db_session.execute(
        select(AnalysisResult).where(
            AnalysisResult.project_id == project.id,
            AnalysisResult.agent_type == "factcheck",
        )
    )
    rows = all_results.scalars().all()
    assert len(rows) == 1
