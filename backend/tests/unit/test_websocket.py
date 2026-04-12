import pytest
import pytest_asyncio

from app.ws.handlers import ConnectionManager


class FakeWebSocket:
    def __init__(self):
        self.sent: list[str] = []
        self.accepted = False
        self._closed = False

    async def accept(self):
        self.accepted = True

    async def send_text(self, data: str):
        if self._closed:
            raise RuntimeError("WebSocket closed")
        self.sent.append(data)

    async def receive_text(self):
        raise Exception("disconnect")


@pytest.mark.asyncio
async def test_connect_adds_connection():
    manager = ConnectionManager()
    ws = FakeWebSocket()
    await manager.connect(ws, "proj-1")
    assert "proj-1" in manager._connections
    assert ws in manager._connections["proj-1"]


@pytest.mark.asyncio
async def test_disconnect_removes_connection():
    manager = ConnectionManager()
    ws = FakeWebSocket()
    await manager.connect(ws, "proj-1")
    manager.disconnect(ws, "proj-1")
    assert "proj-1" not in manager._connections


@pytest.mark.asyncio
async def test_broadcast_sends_to_all():
    manager = ConnectionManager()
    ws1 = FakeWebSocket()
    ws2 = FakeWebSocket()
    await manager.connect(ws1, "proj-1")
    await manager.connect(ws2, "proj-1")
    await manager.broadcast("proj-1", {"event": "agent_start", "step_type": "icp"})
    assert len(ws1.sent) == 1
    assert len(ws2.sent) == 1


@pytest.mark.asyncio
async def test_broadcast_no_connections_no_error():
    manager = ConnectionManager()
    await manager.broadcast("proj-1", {"event": "test"})


@pytest.mark.asyncio
async def test_broadcast_removes_failed_connection():
    manager = ConnectionManager()
    ws_ok = FakeWebSocket()
    ws_bad = FakeWebSocket()
    ws_bad._closed = True
    await manager.connect(ws_ok, "proj-1")
    await manager.connect(ws_bad, "proj-1")
    await manager.broadcast("proj-1", {"event": "test"})
    assert ws_bad not in manager._connections["proj-1"]
    assert ws_ok in manager._connections["proj-1"]
