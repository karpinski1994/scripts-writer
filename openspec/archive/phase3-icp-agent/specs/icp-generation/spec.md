## Purpose

Defines the ICP generation agent, ICP API endpoints, ICP schemas, and the abstract BaseAgent that all future agents inherit from.

## ADDED Requirements

### Requirement: Abstract BaseAgent with cache integration
The system SHALL define `BaseAgent(ABC, Generic[InputT, OutputT])` with abstract `build_prompt(input_data) -> str`, concrete `execute(input_data, cache, factory) -> OutputT` (cache check → LLM call via factory → cache write), and `_compute_cache_key(input_data) -> str`. The class SHALL NOT be instantiable directly.

#### Scenario: Cannot instantiate BaseAgent directly
- **WHEN** code attempts `BaseAgent()`
- **THEN** a `TypeError` is raised because the class is abstract

#### Scenario: Execute uses cache on hit
- **WHEN** `execute()` is called with the same input that was previously executed
- **THEN** the cached result is returned without calling the LLM

### Requirement: ICP Agent generates structured profiles
The system SHALL provide `ICPAgent(BaseAgent[ICPAgentInput, ICPAgentOutput])` with a Pydantic AI agent configured for structured ICP generation. `build_prompt()` SHALL include raw notes, topic, target format, and content goal from the input.

#### Scenario: Build prompt contains notes and topic
- **WHEN** `agent.build_prompt(ICPAgentInput(raw_notes="sell Python course", topic="Python", target_format="VSL"))` is called
- **THEN** the returned prompt string contains "sell Python course" and "Python"

#### Scenario: ICP agent generates valid output
- **WHEN** `ICPAgent.execute(valid_input)` is called with a working LLM provider
- **THEN** an `ICPAgentOutput` is returned with a non-empty `icp` field and `confidence` between 0 and 1

### Requirement: ICP Pydantic schemas
The system SHALL define `ICPProfileResponse` (all ICP fields plus source and approved), `ICPUpdateRequest` (all ICP fields optional plus approved flag), matching the LLD ICP model with demographics, psychographics, pain_points, desires, objections, and language_style.

#### Scenario: ICP profile response validates
- **WHEN** an `ICPProfileResponse` is constructed with valid demographics and psychographics
- **THEN** it validates without error

### Requirement: ICP API endpoints
The system SHALL expose 4 endpoints: `POST /api/v1/projects/{id}/icp/generate` (generate ICP via agent), `GET /api/v1/projects/{id}/icp` (get current ICP), `PATCH /api/v1/projects/{id}/icp` (edit ICP fields, set approved), `POST /api/v1/projects/{id}/icp/upload` (upload .json or .txt file as ICP).

#### Scenario: Generate ICP
- **WHEN** `POST /api/v1/projects/{id}/icp/generate` is called
- **THEN** an ICP profile is generated, saved to `icp_profiles` table, and returned with `approved=False`

#### Scenario: Get ICP
- **WHEN** `GET /api/v1/projects/{id}/icp` is called after generating an ICP
- **THEN** the ICP profile is returned

#### Scenario: Approve ICP
- **WHEN** `PATCH /api/v1/projects/{id}/icp` is called with `approved=True`
- **THEN** the ICP profile's `approved` field is set to `True` and the pipeline step's `selected_option` is updated

#### Scenario: Upload ICP from JSON file
- **WHEN** `POST /api/v1/projects/{id}/icp/upload` is called with a valid JSON file
- **THEN** the ICP profile is saved with `source="uploaded"` and `approved=False`
