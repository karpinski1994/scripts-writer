## Purpose

Defines the backend WebSocket endpoint, ConnectionManager, and orchestrator integration for broadcasting agent events to connected clients.

## ADDED Requirements

### Requirement: WebSocket endpoint for pipeline events
The system SHALL provide a WebSocket endpoint at `/ws/pipeline/{project_id}` that accepts connections, tracks them per project_id, and broadcasts JSON events to all connections for a given project_id. The endpoint SHALL handle connection/disconnection gracefully.

#### Scenario: Client connects to WebSocket
- **WHEN** a client connects to `ws://localhost:8000/ws/pipeline/{project_id}`
- **THEN** the connection is accepted and tracked in ConnectionManager

#### Scenario: Client disconnects from WebSocket
- **WHEN** a client disconnects (close or error)
- **THEN** the connection is removed from ConnectionManager without errors

### Requirement: ConnectionManager tracks connections per project
The system SHALL provide `ConnectionManager` with `connect(websocket, project_id)`, `disconnect(websocket, project_id)`, and `broadcast(project_id, message: dict)` methods. `broadcast` SHALL serialize the message dict to JSON and send it to all active connections for the given project_id. Failed sends SHALL silently remove the connection.

#### Scenario: Broadcast to multiple connections
- **WHEN** `broadcast(project_id, {"event": "agent_start", "step_type": "icp"})` is called
- **THEN** all connected clients for that project_id receive the JSON message

#### Scenario: Broadcast with no connections
- **WHEN** `broadcast(project_id, message)` is called and no clients are connected
- **THEN** no error is raised

### Requirement: Orchestrator emits WebSocket events during agent execution
The system SHALL extend `PipelineOrchestrator.run_step()` to emit WebSocket events when a `ws_manager` is provided. Events: `agent_start` (when step status becomes RUNNING), `agent_complete` (when step status becomes COMPLETED, includes output_data). The orchestrator constructor SHALL accept an optional `ws_manager: ConnectionManager | None = None` parameter.

#### Scenario: Agent start event emitted
- **WHEN** `run_step(project_id, StepType.ICP)` is called with a ws_manager
- **THEN** an `agent_start` event with `step_type: "icp"` is broadcast before agent execution

#### Scenario: Agent complete event emitted
- **WHEN** an agent completes successfully
- **THEN** an `agent_complete` event with `step_type`, `status: "completed"`, and `output` (the agent output dict) is broadcast

#### Scenario: Orchestrator works without ws_manager
- **WHEN** `PipelineOrchestrator(db)` is constructed without ws_manager
- **THEN** `run_step()` works exactly as before, no events broadcast

### Requirement: WebSocket route registered in FastAPI app
The system SHALL register the WebSocket endpoint in the FastAPI app via the router or directly in main.py.

#### Scenario: WebSocket endpoint accessible
- **WHEN** the backend is running
- **THEN** `ws://localhost:8000/ws/pipeline/{id}` accepts WebSocket connections
