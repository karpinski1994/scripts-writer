import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Project
from app.integrations.errors import NotebookLMAPIError
from app.integrations.notebooklm import NotebookLMClientWrapper
from app.pipeline.state import StepType
from app.schemas.notebooklm import ConnectNotebookResponse, NotebookSummary

logger = logging.getLogger(__name__)

STEP_QUERIES: dict[str, str] = {
    StepType.icp.value: {
        "demographics": "What are the demographics (age, job title, industry, company size) of the ideal customer for {topic}?",
        "psychographics": "What are their values, interests, and lifestyle? What do they care about most?",
        "pains": "What problems, frustrations, or challenges do they face daily related to {topic}?",
        "desires": "What do they want to achieve? What would their ideal outcome be?",
        "objections": "What objections might they have when considering {topic} solutions?",
        "language": "What words, phrases, or language do they use? Give examples of how they talk about their problems.",
    },
    StepType.hook.value: {
        "techniques": "What attention-grabbing approaches or opening strategies work best for this audience?",
        "emotions": "What emotional triggers or feelings resonate with them?",
        "curiosity": "What surprising facts or claims would make them stop and pay attention?",
    },
    StepType.narrative.value: {
        "patterns": "What storytelling patterns or narrative frameworks work best for {topic}?",
        "arcs": "What story structures keep them engaged from start to finish?",
    },
    StepType.retention.value: {
        "techniques": "What techniques keep audiences engaged throughout content about {topic}?",
        "pattern_interrupts": "What pattern interrupts or surprising moments work best?",
    },
    StepType.cta.value: {
        "strategies": "What calls to action or conversion techniques work best for {topic}?",
        "urgency": "What creates urgency or motivates action?",
    },
    StepType.writer.value: {
        "insights": "Summarize the top key insights, evidence, and recommendations from this notebook for {topic}.",
    },
}


class NotebookLMService:
    def __init__(self, db: AsyncSession, client: NotebookLMClientWrapper):
        self.db = db
        self.client = client

    async def list_notebooks(self, project_id: str) -> list[NotebookSummary]:
        return await self.client.list_notebooks()

    async def connect_notebook(self, project_id: str, notebook_id: str) -> ConnectNotebookResponse:
        project = await self.db.get(Project, project_id)
        if project is None:
            raise ValueError(f"Project {project_id} not found")
        notebooks = await self.client.list_notebooks()
        notebook = next((n for n in notebooks if n.id == notebook_id), None)
        title = notebook.title if notebook else ""
        project.notebooklm_notebook_id = notebook_id
        await self.db.commit()
        await self.db.refresh(project)
        return ConnectNotebookResponse(
            project_id=project_id,
            notebook_id=notebook_id,
            notebook_title=title,
            connected=True,
        )

    async def disconnect_notebook(self, project_id: str) -> None:
        project = await self.db.get(Project, project_id)
        if project is None:
            raise ValueError(f"Project {project_id} not found")
        project.notebooklm_notebook_id = None
        await self.db.commit()

    async def query_notebook(self, project_id: str, query: str) -> str | None:
        project = await self.db.get(Project, project_id)
        if project is None or not project.notebooklm_notebook_id:
            return None
        try:
            return await self.client.query_notebook(project.notebooklm_notebook_id, query)
        except NotebookLMAPIError:
            logger.warning("NotebookLM query failed for project %s", project_id)
            return None

    async def get_step_context(self, project_id: str, step_type: str) -> str | None:
        project = await self.db.get(Project, project_id)
        if project is None or not project.notebooklm_notebook_id:
            return None
        queries = STEP_QUERIES.get(step_type)
        if not queries:
            return None
        if isinstance(queries, dict):
            context_parts = []
            for aspect, query_template in queries.items():
                if "{" in query_template:
                    query = query_template.format(topic=project.topic, format=project.target_format)
                else:
                    query = query_template
                try:
                    result = await self.client.query_notebook(project.notebooklm_notebook_id, query)
                    if result:
                        context_parts.append(f"## {aspect.upper()}\n{result}")
                except Exception as e:
                    logger.warning(f"Failed to query {aspect}: {e}")
            return "\n\n".join(context_parts) if context_parts else None
        else:
            query = queries.format(topic=project.topic, format=project.target_format)
            try:
                return await self.client.query_notebook(project.notebooklm_notebook_id, query)
            except NotebookLMAPIError:
                logger.warning("NotebookLM get_step_context failed for project %s step %s", project_id, step_type)
                return None
