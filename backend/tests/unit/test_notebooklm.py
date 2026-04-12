from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.integrations.errors import NotebookLMAPIError
from app.integrations.notebooklm import NotebookLMClient, NotebookSummary
from app.pipeline.state import StepType
from app.schemas.notebooklm import ConnectNotebookResponse
from app.services.notebooklm_service import STEP_QUERIES, NotebookLMService


@pytest.fixture
def mock_client():
    client = MagicMock(spec=NotebookLMClient)
    client.list_notebooks = AsyncMock()
    client.query_notebook = AsyncMock()
    return client


@pytest.fixture
def mock_db():
    db = AsyncMock()
    return db


class TestNotebookLMAPIError:
    def test_error_attributes(self):
        err = NotebookLMAPIError(404, "not found")
        assert err.status_code == 404
        assert err.message == "not found"
        assert "404" in str(err)


class TestNotebookLMService:
    @pytest.mark.asyncio
    async def test_list_notebooks(self, mock_db, mock_client):
        mock_client.list_notebooks.return_value = [NotebookSummary(id="nb1", title="Test Notebook")]
        service = NotebookLMService(mock_db, mock_client)
        result = await service.list_notebooks("proj-1")
        assert len(result) == 1
        assert result[0].id == "nb1"

    @pytest.mark.asyncio
    async def test_connect_notebook(self, mock_db, mock_client):
        project = MagicMock()
        project.notebooklm_notebook_id = None
        mock_db.get = AsyncMock(return_value=project)
        mock_client.list_notebooks.return_value = [NotebookSummary(id="nb1", title="My Notebook")]
        service = NotebookLMService(mock_db, mock_client)
        result = await service.connect_notebook("proj-1", "nb1")
        assert result.connected is True
        assert result.notebook_id == "nb1"
        assert result.notebook_title == "My Notebook"

    @pytest.mark.asyncio
    async def test_connect_notebook_project_not_found(self, mock_db, mock_client):
        mock_db.get = AsyncMock(return_value=None)
        service = NotebookLMService(mock_db, mock_client)
        with pytest.raises(ValueError, match="not found"):
            await service.connect_notebook("proj-1", "nb1")

    @pytest.mark.asyncio
    async def test_disconnect_notebook(self, mock_db, mock_client):
        project = MagicMock()
        project.notebooklm_notebook_id = "nb1"
        mock_db.get = AsyncMock(return_value=project)
        service = NotebookLMService(mock_db, mock_client)
        await service.disconnect_notebook("proj-1")
        assert project.notebooklm_notebook_id is None

    @pytest.mark.asyncio
    async def test_query_notebook_no_notebook(self, mock_db, mock_client):
        project = MagicMock()
        project.notebooklm_notebook_id = None
        mock_db.get = AsyncMock(return_value=project)
        service = NotebookLMService(mock_db, mock_client)
        result = await service.query_notebook("proj-1", "test query")
        assert result is None

    @pytest.mark.asyncio
    async def test_query_notebook_success(self, mock_db, mock_client):
        project = MagicMock()
        project.notebooklm_notebook_id = "nb1"
        mock_db.get = AsyncMock(return_value=project)
        mock_client.query_notebook.return_value = "Answer from notebook"
        service = NotebookLMService(mock_db, mock_client)
        result = await service.query_notebook("proj-1", "test query")
        assert result == "Answer from notebook"

    @pytest.mark.asyncio
    async def test_query_notebook_api_error_graceful(self, mock_db, mock_client):
        project = MagicMock()
        project.notebooklm_notebook_id = "nb1"
        mock_db.get = AsyncMock(return_value=project)
        mock_client.query_notebook.side_effect = NotebookLMAPIError(500, "internal error")
        service = NotebookLMService(mock_db, mock_client)
        result = await service.query_notebook("proj-1", "test query")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_step_context_no_notebook(self, mock_db, mock_client):
        project = MagicMock()
        project.notebooklm_notebook_id = None
        mock_db.get = AsyncMock(return_value=project)
        service = NotebookLMService(mock_db, mock_client)
        result = await service.get_step_context("proj-1", StepType.icp.value)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_step_context_generates_correct_query(self, mock_db, mock_client):
        project = MagicMock()
        project.notebooklm_notebook_id = "nb1"
        project.topic = "AI Tools"
        project.target_format = "YouTube"
        mock_db.get = AsyncMock(return_value=project)
        mock_client.query_notebook.return_value = "Audience insights"

        service = NotebookLMService(mock_db, mock_client)
        result = await service.get_step_context("proj-1", StepType.icp.value)
        assert result == "Audience insights"
        call_args = mock_client.query_notebook.call_args
        query = call_args[0][1]
        assert "AI Tools" in query
        assert "YouTube" in query

    @pytest.mark.asyncio
    async def test_get_step_context_api_error_graceful(self, mock_db, mock_client):
        project = MagicMock()
        project.notebooklm_notebook_id = "nb1"
        project.topic = "AI Tools"
        project.target_format = "YouTube"
        mock_db.get = AsyncMock(return_value=project)
        mock_client.query_notebook.side_effect = NotebookLMAPIError(500, "error")
        service = NotebookLMService(mock_db, mock_client)
        result = await service.get_step_context("proj-1", StepType.icp.value)
        assert result is None


class TestStepQueries:
    def test_all_creative_steps_have_queries(self):
        creative_steps = [
            StepType.icp.value,
            StepType.hook.value,
            StepType.narrative.value,
            StepType.retention.value,
            StepType.cta.value,
            StepType.writer.value,
        ]
        for step in creative_steps:
            assert step in STEP_QUERIES, f"Missing query template for step: {step}"

    def test_query_templates_contain_placeholders(self):
        steps_with_placeholders = [
            s for s in STEP_QUERIES if "{topic}" in STEP_QUERIES[s] or "{format}" in STEP_QUERIES[s]
        ]
        assert len(steps_with_placeholders) >= 5, "Most steps should have topic/format placeholders"
