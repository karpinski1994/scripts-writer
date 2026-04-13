from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.database import get_db
from app.integrations.notebooklm import NotebookLMClientWrapper
from app.schemas.notebooklm import (
    ConnectNotebookRequest,
    ConnectNotebookResponse,
    NotebookQueryRequest,
    NotebookQueryResponse,
    NotebookSummary,
)
from app.services.notebooklm_service import NotebookLMService
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects/{project_id}/notebooklm", tags=["notebooklm"])


def _build_client() -> NotebookLMClientWrapper:
    settings = get_settings()
    storage_path = settings.notebooklm_storage_path or None
    return NotebookLMClientWrapper(storage_path=storage_path)


@router.get("/notebooks", response_model=list[NotebookSummary])
async def list_notebooks(project_id: str, db: AsyncSession = Depends(get_db)):
    project_service = ProjectService(db)
    await project_service.get_by_id(project_id)
    client = _build_client()
    service = NotebookLMService(db, client)
    return await service.list_notebooks(project_id)


@router.post("/connect", response_model=ConnectNotebookResponse)
async def connect_notebook(project_id: str, body: ConnectNotebookRequest, db: AsyncSession = Depends(get_db)):
    project_service = ProjectService(db)
    await project_service.get_by_id(project_id)
    client = _build_client()
    service = NotebookLMService(db, client)
    try:
        return await service.connect_notebook(project_id, body.notebook_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/connect", status_code=204)
async def disconnect_notebook(project_id: str, db: AsyncSession = Depends(get_db)):
    project_service = ProjectService(db)
    await project_service.get_by_id(project_id)
    client = _build_client()
    service = NotebookLMService(db, client)
    await service.disconnect_notebook(project_id)


@router.post("/query", response_model=NotebookQueryResponse)
async def query_notebook(project_id: str, body: NotebookQueryRequest, db: AsyncSession = Depends(get_db)):
    project_service = ProjectService(db)
    await project_service.get_by_id(project_id)
    client = _build_client()
    service = NotebookLMService(db, client)
    answer = await service.query_notebook(project_id, body.query)
    if answer is None:
        raise HTTPException(status_code=404, detail="No notebook connected or query failed")
    return NotebookQueryResponse(answer=answer)
