import json
import logging
import subprocess

from app.integrations.errors import NotebookLMAPIError

logger = logging.getLogger(__name__)


class NotebookSummary:
    def __init__(self, id: str, title: str):
        self.id = id
        self.title = title


class NotebookLMClientWrapper:
    """Wrapper for NotebookLM using nlm CLI.

    Requires: nlm login (run manually)
    """

    def __init__(self, storage_path: str | None = None):
        self._storage_path = storage_path

    async def list_notebooks(self) -> list[NotebookSummary]:
        try:
            result = subprocess.run(
                ["nlm", "notebook", "list", "--json"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                error_msg = result.stderr.strip() or result.stdout.strip()
                if "not found" in error_msg.lower() or "login" in error_msg.lower():
                    logger.info("NotebookLM not configured - return empty list")
                    return []
                raise NotebookLMAPIError(500, error_msg)
            if not result.stdout.strip():
                return []
            data = json.loads(result.stdout)
            notebooks = data.get("notebooks", [])
            return [NotebookSummary(id=nb.get("id", ""), title=nb.get("name", "")) for nb in notebooks]
        except FileNotFoundError:
            logger.info("nlm CLI not found - return empty list")
            return []
        except subprocess.TimeoutExpired:
            logger.warning("NotebookLM request timed out")
            return []
        except json.JSONDecodeError:
            logger.warning("Failed to parse nlm response")
            return []
        except Exception as e:
            logger.warning(f"NotebookLM error: {e}")
            return []

    async def query_notebook(self, notebook_id: str, query: str) -> str:
        try:
            result = subprocess.run(
                ["nlm", "notebook", "query", notebook_id, query, "--json"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode != 0:
                error_msg = result.stderr.strip() or result.stdout.strip()
                if "not found" in error_msg.lower() or "login" in error_msg.lower():
                    return ""
                logger.warning(f"Query error: {error_msg}")
                return ""
            if not result.stdout.strip():
                return ""
            data = json.loads(result.stdout)
            return data.get("answer", "")
        except FileNotFoundError:
            return ""
        except subprocess.TimeoutExpired:
            logger.warning("NotebookLM query timed out")
            return ""
        except json.JSONDecodeError:
            return ""
        except Exception as e:
            logger.warning(f"Query failed: {e}")
            return ""
