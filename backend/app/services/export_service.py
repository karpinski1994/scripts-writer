import logging
import re
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ScriptVersion

logger = logging.getLogger(__name__)


class ExportService:
    def __init__(self, db: AsyncSession, export_dir: str):
        self.db = db
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    async def export_txt(self, project_id: str, version_id: str) -> Path:
        version = await self._get_version(version_id, project_id)
        filename = self._slugify(f"{project_id}_v{version.version_number}") + ".txt"
        filepath = self.export_dir / filename
        filepath.write_text(version.content, encoding="utf-8")
        return filepath

    async def export_md(self, project_id: str, version_id: str) -> Path:
        version = await self._get_version(version_id, project_id)
        filename = self._slugify(f"{project_id}_v{version.version_number}") + ".md"
        filepath = self.export_dir / filename
        filepath.write_text(self._format_as_markdown(version), encoding="utf-8")
        return filepath

    def _format_as_markdown(self, version: ScriptVersion) -> str:
        lines = [
            f"# Script v{version.version_number}",
            "",
            f"**Format:** {version.format}",
        ]
        if version.hook_text:
            lines.append(f"**Hook:** {version.hook_text}")
        if version.narrative_pattern:
            lines.append(f"**Narrative:** {version.narrative_pattern}")
        if version.cta_text:
            lines.append(f"**CTA:** {version.cta_text}")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(version.content)
        return "\n".join(lines)

    @staticmethod
    def _slugify(text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^a-z0-9]+", "-", text)
        text = re.sub(r"-+", "-", text)
        return text.strip("-")

    async def _get_version(self, version_id: str, project_id: str) -> ScriptVersion:
        result = await self.db.execute(
            select(ScriptVersion).where(
                ScriptVersion.id == version_id,
                ScriptVersion.project_id == project_id,
            )
        )
        version = result.scalar_one_or_none()
        if version is None:
            from fastapi import HTTPException

            raise HTTPException(status_code=404, detail="Script version not found")
        return version
