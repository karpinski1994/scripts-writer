from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router
from app.config import get_settings
from app.db.database import engine
from app.db.models import Base
from app.ws.connection import connection_manager
from app.ws.handlers import websocket_endpoint


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    print(f"Scripts Writer backend starting | log_level={settings.log_level} | db={settings.database_url}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    print("Scripts Writer backend shutting down")


app = FastAPI(
    title="Scripts Writer",
    description="Agentic AI pipeline for generating high-converting video scripts and marketing posts",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.websocket("/ws/pipeline/{project_id}")
async def ws_pipeline(websocket: WebSocket, project_id: str):
    await websocket_endpoint(websocket, project_id, connection_manager)


@app.get("/health")
async def health():
    return {"status": "ok"}
