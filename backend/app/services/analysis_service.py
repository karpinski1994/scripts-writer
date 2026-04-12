import json
import logging
from uuid import uuid4

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AnalysisResult
from app.schemas.analysis import AnalysisResultResponse, Finding

logger = logging.getLogger(__name__)


class AnalysisService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_result(
        self,
        project_id: str,
        script_version_id: str,
        agent_type: str,
        findings: list[Finding],
        overall_score: float | None = None,
    ) -> AnalysisResultResponse:
        await self.db.execute(
            delete(AnalysisResult).where(
                AnalysisResult.project_id == project_id,
                AnalysisResult.script_version_id == script_version_id,
                AnalysisResult.agent_type == agent_type,
            )
        )
        await self.db.flush()

        result = AnalysisResult(
            id=str(uuid4()),
            project_id=project_id,
            script_version_id=script_version_id,
            agent_type=agent_type,
            findings=json.dumps([f.model_dump() for f in findings]),
            overall_score=overall_score,
        )
        self.db.add(result)
        await self.db.commit()
        await self.db.refresh(result)
        return self._to_response(result)

    async def get_results(self, project_id: str) -> list[AnalysisResultResponse]:
        result = await self.db.execute(select(AnalysisResult).where(AnalysisResult.project_id == project_id))
        return [self._to_response(r) for r in result.scalars().all()]

    async def get_result_by_type(self, project_id: str, agent_type: str) -> AnalysisResultResponse | None:
        result = await self.db.execute(
            select(AnalysisResult).where(
                AnalysisResult.project_id == project_id,
                AnalysisResult.agent_type == agent_type,
            )
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return self._to_response(row)

    def _to_response(self, result: AnalysisResult) -> AnalysisResultResponse:
        findings_data = json.loads(result.findings) if result.findings else []
        findings = [Finding.model_validate(f) for f in findings_data]
        return AnalysisResultResponse(
            id=result.id,
            project_id=result.project_id,
            script_version_id=result.script_version_id,
            agent_type=result.agent_type,
            findings=findings,
            overall_score=result.overall_score,
            created_at=result.created_at,
        )
