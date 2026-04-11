from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    print(f"Scripts Writer backend starting | log_level={settings.log_level} | db={settings.database_url}")
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


@app.get("/health")
async def health():
    return {"status": "ok"}
