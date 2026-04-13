from uuid import UUID
import structlog

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..db.models import Project
from ..rag import piragi_manager
from ..rag.config import STEP_CATEGORY_MAP, StepType

logger = structlog.get_logger(__name__)


class PiragiService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def connect_documents(self, project_id: UUID, document_paths: str) -> Project:
        result = await self.db.execute(select(Project).where(Project.id == str(project_id)))
        project = result.scalar_one_or_none()
        if not project:
            raise ValueError(f"Project {project_id} not found")

        project.piragi_document_paths = document_paths
        await self.db.commit()
        await self.db.refresh(project)
        logger.info("piragi_documents_connected", project_id=str(project_id), paths=document_paths)
        return project

    async def disconnect_documents(self, project_id: UUID) -> None:
        result = await self.db.execute(select(Project).where(Project.id == str(project_id)))
        project = result.scalar_one_or_none()
        if not project:
            raise ValueError(f"Project {project_id} not found")

        project.piragi_document_paths = None
        await self.db.commit()
        logger.info("piragi_documents_disconnected", project_id=str(project_id))

    async def query_documents(self, project_id: UUID, query: str, step_type: str) -> list[dict]:
        project = await self._get_project(project_id)
        if not project.piragi_document_paths:
            return []

        try:
            step_enum = StepType(step_type)
        except ValueError:
            step_enum = StepType.ICP

        category = STEP_CATEGORY_MAP.get(step_enum, "icp")
        chunks = await piragi_manager.query(category, query, top_k=3)

        results = []
        for i, chunk in enumerate(chunks):
            results.append({"chunk": chunk, "source": f"documents/{category}", "relevance": 1.0 - (i * 0.1)})
        return results

    async def get_step_context(self, project_id: UUID, step_type: StepType) -> str | None:
        project = await self._get_project(project_id)
        if not project.piragi_document_paths:
            return None

        category = STEP_CATEGORY_MAP.get(step_type, "icp")

        default_queries = {
            StepType.ICP: "audience insights demographics pain points",
            StepType.HOOK: "effective hooks viral patterns",
            StepType.NARRATIVE: "story templates narrative patterns",
            StepType.RETENTION: "retention techniques engagement",
            StepType.CTA: "call to action urgency conversion",
        }
        query = default_queries.get(step_type, "relevant context")

        try:
            chunks = await piragi_manager.query(category, query, top_k=3)
            if not chunks:
                return None
            return "\n\n".join(chunks)
        except Exception as e:
            logger.warning("piragi_query_failed", project_id=str(project_id), error=str(e))
            return None

    async def list_categories(self) -> dict[str, int]:
        return piragi_manager.list_categories()

    async def index_document(self, file_path: str, category: str) -> None:
        try:
            await piragi_manager.add_documents(category, [file_path])
        except Exception as e:
            logger.warning("piragi_index_failed", file_path=file_path, error=str(e))
            raise

    async def _get_project(self, project_id: UUID) -> Project:
        result = await self.db.execute(select(Project).where(Project.id == str(project_id)))
        project = result.scalar_one_or_none()
        if not project:
            raise ValueError(f"Project {project_id} not found")
        return project
