from pathlib import Path
from typing import Optional
import structlog

from .config import (
    STEP_CATEGORY_MAP,
    PIRAGI_PERSIST_DIR,
    PIRAGI_DEFAULT_TOP_K,
)

logger = structlog.get_logger(__name__)


class PiragiManager:
    def __init__(self, persist_dir: str = PIRAGI_PERSIST_DIR):
        self._ragi_cache: dict[str, "Ragi"] = {}
        self._persist_dir = Path(persist_dir)
        self._documents_base = Path("documents")

    def get_or_create(self, category: str) -> "Ragi":
        if category in self._ragi_cache:
            return self._ragi_cache[category]

        category_path = self._resolve_category_path(category)
        category_path.mkdir(parents=True, exist_ok=True)

        index_path = self._persist_dir / category
        index_path.mkdir(parents=True, exist_ok=True)

        try:
            from piragi import Ragi

            ragi = Ragi(sources=[str(category_path)], persist_dir=str(index_path))
        except ImportError:
            logger.warning("piragi_not_installed", category=category)
            raise ImportError("Piragi package not installed. Run: uv add piragi")

        self._ragi_cache[category] = ragi
        return ragi

    def _resolve_category_path(self, category: str) -> Path:
        return self._documents_base / category

    async def query(self, category: str, query_text: str, top_k: int = PIRAGI_DEFAULT_TOP_K) -> list[str]:
        try:
            ragi = self.get_or_create(category)
            results = ragi.query(query_text, top_k=top_k)
            return [r.chunk for r in results] if results else []
        except Exception as e:
            logger.warning("piragi_query_failed", category=category, error=str(e))
            return []

    async def add_documents(self, category: str, sources: list[str]) -> None:
        ragi = self.get_or_create(category)
        for source in sources:
            ragi.add_documents([source])
        logger.info("documents_added", category=category, count=len(sources))

    async def refresh(self, category: str) -> None:
        if category in self._ragi_cache:
            del self._ragi_cache[category]
        self.get_or_create(category)
        logger.info("piragi_refreshed", category=category)

    def list_categories(self) -> dict[str, int]:
        categories = {}
        for step_type, category in STEP_CATEGORY_MAP.items():
            category_path = self._resolve_category_path(category)
            if category_path.exists():
                files = list(category_path.iterdir())
                categories[category] = len([f for f in files if f.is_file()])
            else:
                categories[category] = 0
        return categories


piragi_manager = PiragiManager()
