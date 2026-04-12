import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Project
from app.integrations.errors import NotebookLMAPIError
from app.integrations.notebooklm import NotebookLMClient
from app.pipeline.state import StepType
from app.schemas.notebooklm import ConnectNotebookResponse, NotebookSummary

logger = logging.getLogger(__name__)

STEP_QUERIES: dict[str, str] = {
    StepType.icp.value: (
        "What audience insights and demographic information are relevant for defining"
        " an Ideal Customer Profile about {topic} for a {format}?"
    ),
    StepType.hook.value: (
        "What attention-grabbing approaches, opening strategies, or hook techniques"
        " are mentioned for content about {topic}?"
    ),
    StepType.narrative.value: (
        "What narrative patterns, storytelling approaches, or structural frameworks are discussed for {topic} content?"
    ),
    StepType.retention.value: (
        "What techniques for keeping audiences engaged, pattern interrupts, or retention strategies are mentioned?"
    ),
    StepType.cta.value: (
        "What calls to action, conversion techniques, or action-driving strategies are discussed for {topic}?"
    ),
    StepType.writer.value: (
        "Summarize all key insights, arguments, evidence, and recommendations that"
        " should be incorporated into a {format} script about {topic}."
    ),
}


class NotebookLMService:
    def __init__(self, db: AsyncSession, client: NotebookLMClient):
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
        template = STEP_QUERIES.get(step_type)
        if not template:
            return None
        query = template.format(topic=project.topic, format=project.target_format)
        try:
            return await self.client.query_notebook(project.notebooklm_notebook_id, query)
        except NotebookLMAPIError:
            logger.warning("NotebookLM get_step_context failed for project %s step %s", project_id, step_type)
            return None
