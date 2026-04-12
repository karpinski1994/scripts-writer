from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import ScriptVersion
from app.services.export_service import ExportService

router = APIRouter(prefix="/projects", tags=["export"])


@router.get("/{project_id}/export")
async def export_script(
    project_id: str,
    format: str = "txt",
    db: AsyncSession = Depends(get_db),
):
    if format not in ("txt", "md"):
        raise HTTPException(status_code=400, detail="Format must be 'txt' or 'md'")

    result = await db.execute(
        select(ScriptVersion)
        .where(ScriptVersion.project_id == project_id)
        .order_by(ScriptVersion.version_number.desc())
    )
    version = result.scalars().first()
    if version is None:
        raise HTTPException(status_code=404, detail="No script versions found for project")

    from app.config import get_settings

    service = ExportService(db, get_settings().export_dir)
    if format == "txt":
        filepath = await service.export_txt(project_id, version.id)
    else:
        filepath = await service.export_md(project_id, version.id)

    return FileResponse(
        path=filepath, filename=filepath.name, media_type="text/plain" if format == "txt" else "text/markdown"
    )
