import logging

import google.auth
import google.auth.transport.requests
import httpx

from app.integrations.errors import NotebookLMAPIError

logger = logging.getLogger(__name__)


class NotebookSummary:
    def __init__(self, id: str, title: str):
        self.id = id
        self.title = title


class NotebookLMClient:
    def __init__(self, cloud_project: str, location: str = "us", credentials_path: str = ""):
        self._cloud_project = cloud_project
        self._location = location
        self._credentials_path = credentials_path
        self._credentials = None

    def _get_credentials(self):
        if self._credentials is not None:
            return self._credentials
        import google.oauth2.service_account

        if self._credentials_path:
            self._credentials = google.oauth2.service_account.Credentials.from_service_account_file(
                self._credentials_path,
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )
        else:
            self._credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        return self._credentials

    def _get_base_url(self) -> str:
        return (
            f"https://{self._location}-discoveryengine.googleapis.com/v1alpha"
            f"/projects/{self._cloud_project}/locations/{self._location}/notebooks"
        )

    def _get_token(self) -> str:
        creds = self._get_credentials()
        if not creds.valid:
            request = google.auth.transport.requests.Request()
            creds.refresh(request)
        return creds.token

    async def list_notebooks(self) -> list[NotebookSummary]:
        base_url = self._get_base_url()
        token = self._get_token()
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                base_url,
                headers={"Authorization": f"Bearer {token}"},
            )
        if resp.status_code != 200:
            raise NotebookLMAPIError(resp.status_code, resp.text)
        notebooks = resp.json().get("notebooks", [])
        return [NotebookSummary(id=n["name"].split("/")[-1], title=n.get("displayName", "")) for n in notebooks]

    async def query_notebook(self, notebook_id: str, query: str) -> str:
        base_url = self._get_base_url()
        token = self._get_token()
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{base_url}/{notebook_id}:converse",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={"query": {"text": query}},
            )
        if resp.status_code != 200:
            raise NotebookLMAPIError(resp.status_code, resp.text)
        data = resp.json()
        return data.get("answer", {}).get("text", "")
