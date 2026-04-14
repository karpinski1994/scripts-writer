import logging
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.rag.config import STEP_CATEGORY_MAP
from app.schemas.piragi import (
    ALLOWED_EXTENSIONS,
    ChunkResult,
    ConnectDocumentsRequest,
    ConnectDocumentsResponse,
    DocumentSummary,
    PiragiDocumentsResponse,
    PiragiQueryRequest,
    PiragiQueryResponse,
    UploadDocumentResponse,
)
from app.services.piragi_service import PiragiService
from app.services.project_service import ProjectService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects/{project_id}/rag", tags=["rag"])

DOCUMENTS_DIR = "/Users/karpinski94/projects/scripts-writer/documents"
PLAYBOOKS_DIR = "playbooks"

STEP_TO_CATEGORY: dict[str, str] = {s.value: s.value for s in STEP_CATEGORY_MAP.keys()}


@router.get("/documents", response_model=PiragiDocumentsResponse)
async def list_documents(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> PiragiDocumentsResponse:
    service = PiragiService(db)

    categories = await service.list_categories()

    docs = []
    for step_type, category in STEP_CATEGORY_MAP.items():
        docs.append(
            DocumentSummary(
                category=category,
                file_count=categories.get(category, 0),
                path=f"documents/{category}",
            )
        )

    return PiragiDocumentsResponse(categories=docs)


@router.post("/connect", response_model=ConnectDocumentsResponse)
async def connect_documents(
    project_id: UUID,
    request: ConnectDocumentsRequest,
    db: AsyncSession = Depends(get_db),
) -> ConnectDocumentsResponse:
    try:
        service = PiragiService(db)
        project = await service.connect_documents(project_id, request.document_paths)
        return ConnectDocumentsResponse(
            project_id=str(project_id),
            document_paths=project.piragi_document_paths or "",
            connected=True,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/connect", status_code=204)
async def disconnect_documents(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    try:
        service = PiragiService(db)
        await service.disconnect_documents(project_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/upload", response_model=UploadDocumentResponse)
async def upload_document(
    project_id: UUID,
    step_type: str,
    is_playbook: bool = False,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> UploadDocumentResponse:
    import aiofiles

    logger.info(
        f"[PIRAGI-UPLOAD] Starting upload - project_id: {project_id}, step_type: {step_type}, filename: {file.filename}, is_playbook: {is_playbook}"
    )

    category = STEP_TO_CATEGORY.get(step_type)
    if not category:
        logger.error(f"[PIRAGI-UPLOAD] Invalid step_type: {step_type}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid step_type. Must be one of: {list(STEP_TO_CATEGORY.keys())}",
        )

    file_ext = Path(file.filename).suffix.lower()
    logger.debug(f"[PIRAGI-UPLOAD] File extension: {file_ext}")

    if file_ext not in ALLOWED_EXTENSIONS:
        logger.error(f"[PIRAGI-UPLOAD] File type not allowed: {file_ext}")
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    if is_playbook:
        base_dir = Path(DOCUMENTS_DIR) / PLAYBOOKS_DIR / category
        logger.debug(f"[PIRAGI-UPLOAD] Using playbook directory: {base_dir}")
    else:
        project_service = ProjectService(db)
        project = await project_service.get_by_id(str(project_id))
        project_slug = project.name.lower().replace(" ", "-")
        base_dir = Path(DOCUMENTS_DIR) / project_slug / category
        logger.debug(f"[PIRAGI-UPLOAD] Using project directory: {base_dir}")

    base_dir.mkdir(parents=True, exist_ok=True)
    logger.debug(f"[PIRAGI-UPLOAD] Directory created/verified")

    file_path = base_dir / file.filename

    content = await file.read()
    logger.debug(f"[PIRAGI-UPLOAD] File content size: {len(content)} bytes")

    if file_ext == ".pdf":
        logger.error("[PIRAGI-UPLOAD] PDF support not available")
        raise HTTPException(status_code=400, detail="PDF support coming soon")

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)
    logger.debug(f"[PIRAGI-UPLOAD] File written to: {file_path}")

    logger.info(f"[PIRAGI-UPLOAD] Indexing document: {file_path}")
    service = PiragiService(db)
    await service.index_document(str(file_path), category)
    logger.info(f"[PIRAGI-UPLOAD] Document indexed successfully")

    return UploadDocumentResponse(
        filename=file.filename,
        category=category,
        path=str(file_path),
        size=len(content),
    )


@router.post("/query", response_model=PiragiQueryResponse)
async def query_documents(
    project_id: UUID,
    request: PiragiQueryRequest,
    db: AsyncSession = Depends(get_db),
) -> PiragiQueryResponse:
    try:
        service = PiragiService(db)
        results = await service.query_documents(project_id, request.query, request.step_type)

        chunk_results = []
        for r in results:
            chunk_results.append(
                ChunkResult(
                    chunk=r["chunk"],
                    source=r["source"],
                    relevance=r["relevance"],
                )
            )

        return PiragiQueryResponse(
            query=request.query,
            results=chunk_results,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
