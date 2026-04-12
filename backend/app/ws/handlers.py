import json
import logging

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self._connections: dict[str, list[WebSocket]] = {}

    async def connect(self, ws: WebSocket, project_id: str) -> None:
        await ws.accept()
        if project_id not in self._connections:
            self._connections[project_id] = []
        self._connections[project_id].append(ws)
        logger.info(f"WebSocket connected for project {project_id}")

    def disconnect(self, ws: WebSocket, project_id: str) -> None:
        if project_id in self._connections:
            self._connections[project_id] = [c for c in self._connections[project_id] if c is not ws]
            if not self._connections[project_id]:
                del self._connections[project_id]
        logger.info(f"WebSocket disconnected for project {project_id}")

    async def broadcast(self, project_id: str, message: dict) -> None:
        connections = self._connections.get(project_id, [])
        if not connections:
            return
        payload = json.dumps(message)
        failed: list[WebSocket] = []
        for ws in connections:
            try:
                await ws.send_text(payload)
            except Exception:
                failed.append(ws)
        for ws in failed:
            self.disconnect(ws, project_id)


async def websocket_endpoint(websocket: WebSocket, project_id: str, manager: ConnectionManager) -> None:
    await manager.connect(websocket, project_id)
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        pass
    finally:
        manager.disconnect(websocket, project_id)
