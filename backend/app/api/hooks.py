from pathlib import Path

import aiofiles
from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db

router = APIRouter(prefix="/projects/{project_id}/hooks", tags=["hooks"])

DOCUMENTS_DIR = Path("/Users/karpinski94/projects/scripts-writer/documents/hooks")


@router.post("/upload", status_code=200)
async def upload_hook(project_id: str, file: UploadFile, db: AsyncSession = Depends(get_db)):
    content = await file.read()

    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
    file_path = DOCUMENTS_DIR / file.filename
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    return {"filename": file.filename, "path": str(file_path)}
