from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.rag.config import STEP_CATEGORY_MAP
from app.schemas.piragi import (
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

router = APIRouter(prefix="/projects/{project_id}/rag", tags=["rag"])


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


ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf"}
DOCUMENTS_DIR = "documents"

STEP_TO_CATEGORY: dict[str, str] = {s.value: s.value for s in STEP_CATEGORY_MAP.keys()}


@router.post("/upload", response_model=UploadDocumentResponse)
async def upload_document(
    project_id: UUID,
    step_type: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> UploadDocumentResponse:
    from pathlib import Path

    import aiofiles

    category = STEP_TO_CATEGORY.get(step_type)
    if not category:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid step_type. Must be one of: {list(STEP_TO_CATEGORY.keys())}",
        )

    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    category_dir = Path(DOCUMENTS_DIR) / category
    category_dir.mkdir(parents=True, exist_ok=True)

    file_path = category_dir / file.filename

    content = await file.read()
    if file_ext == ".pdf":
        raise HTTPException(status_code=400, detail="PDF support coming soon")

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    service = PiragiService(db)
    await service.index_document(str(file_path), category)

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
