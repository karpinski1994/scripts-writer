from pathlib import Path

import aiofiles
from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects/{project_id}/hooks", tags=["hooks"])


@router.post("/upload", status_code=200)
async def upload_hook(project_id: str, file: UploadFile, db: AsyncSession = Depends(get_db)):
    project_service = ProjectService(db)
    project = await project_service.get_by_id(project_id)
    project_slug = project.name.lower().replace(" ", "-")

    docs_dir = Path(f"/Users/karpinski94/projects/scripts-writer/documents/{project_slug}/hooks")
    docs_dir.mkdir(parents=True, exist_ok=True)

    file_path = docs_dir / file.filename
    content = await file.read()
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    return {"filename": file.filename, "path": str(file_path)}
