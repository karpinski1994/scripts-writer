## Purpose

Defines the frontend WebSocket hooks and streaming text component.

## ADDED Requirements

### Requirement: WebSocket hook with auto-reconnect
The system SHALL provide `use-websocket.ts` hook that connects to `ws://localhost:8000/ws/pipeline/{projectId}`, tracks connection status (`"connecting" | "open" | "closed"`), receives JSON messages and exposes them as `lastEvent`, and auto-reconnects with exponential backoff (1s, 2s, 4s, 8s, max 30s). The hook SHALL clean up the connection on unmount or projectId change. WebSocket base URL SHALL use `NEXT_PUBLIC_API_URL` env var (same as API client) with `http` replaced by `ws`.

#### Scenario: Hook connects on mount
- **WHEN** `useWebSocket("project-123")` is called
- **THEN** a WebSocket connection is opened to `ws://localhost:8000/ws/pipeline/project-123` and status becomes "open"

#### Scenario: Auto-reconnect on disconnect
- **WHEN** the WebSocket connection drops
- **THEN** status becomes "closed", and a reconnection is attempted with exponential backoff

#### Scenario: Cleanup on unmount
- **WHEN** the component using the hook unmounts
- **THEN** the WebSocket connection is closed cleanly

### Requirement: Agent stream hook processes WS events
The system SHALL provide `use-agent-stream.ts` hook that takes `projectId` and uses `useWebSocket(projectId)` to receive events. On `agent_start`: sets step status to running in pipeline store. On `agent_complete`: updates step output and status in pipeline store, refetches pipeline query. The `agent_progress` event is reserved for future token streaming but currently not processed.

#### Scenario: Agent start event updates store
- **WHEN** an `agent_start` event is received with `step_type: "hook"`
- **THEN** the pipeline store marks the hook step as running and `isRunning` becomes true

#### Scenario: Agent complete event updates store and refetches
- **WHEN** an `agent_complete` event is received with `step_type: "hook"` and `status: "completed"`
- **THEN** the pipeline store updates the hook step status and output_data, and the TanStack Query pipeline data is invalidated/refetched

### Requirement: Streaming text component
The system SHALL provide `streaming-text.tsx` component that renders `streamingOutput[stepType]` from the pipeline store as text. When streaming is active (text is growing), a blinking cursor SHALL appear at the end. When streaming is complete, the full text is shown without cursor.

#### Scenario: Streaming text with cursor
- **WHEN** `streamingOutput["hook"]` is non-empty and the hook step is running
- **THEN** the text is rendered with a blinking cursor at the end

#### Scenario: Complete text without cursor
- **WHEN** the hook step is completed
- **THEN** the full text is rendered without a cursor
