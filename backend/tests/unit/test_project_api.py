import pytest


@pytest.mark.asyncio
async def test_create_project(async_client):
    response = await async_client.post(
        "/api/v1/projects",
        json={"name": "Test", "topic": "Python", "target_format": "VSL", "raw_notes": "test notes"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test"
    assert data["target_format"] == "VSL"
    assert data["id"] is not None


@pytest.mark.asyncio
async def test_list_projects(async_client):
    await async_client.post(
        "/api/v1/projects",
        json={"name": "A", "topic": "T1", "target_format": "VSL", "raw_notes": "n1"},
    )
    await async_client.post(
        "/api/v1/projects",
        json={"name": "B", "topic": "T2", "target_format": "Blog", "raw_notes": "n2"},
    )
    response = await async_client.get("/api/v1/projects")
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_get_project(async_client):
    create_resp = await async_client.post(
        "/api/v1/projects",
        json={"name": "Detail", "topic": "T", "target_format": "YouTube", "raw_notes": "notes"},
    )
    project_id = create_resp.json()["id"]
    response = await async_client.get(f"/api/v1/projects/{project_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Detail"


@pytest.mark.asyncio
async def test_get_project_not_found(async_client):
    response = await async_client.get("/api/v1/projects/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_project(async_client):
    create_resp = await async_client.post(
        "/api/v1/projects",
        json={"name": "Old", "topic": "T", "target_format": "VSL", "raw_notes": "n"},
    )
    project_id = create_resp.json()["id"]
    response = await async_client.patch(f"/api/v1/projects/{project_id}", json={"name": "New"})
    assert response.status_code == 200
    assert response.json()["name"] == "New"


@pytest.mark.asyncio
async def test_delete_project(async_client):
    create_resp = await async_client.post(
        "/api/v1/projects",
        json={"name": "Del", "topic": "T", "target_format": "VSL", "raw_notes": "n"},
    )
    project_id = create_resp.json()["id"]
    response = await async_client.delete(f"/api/v1/projects/{project_id}")
    assert response.status_code == 204
    get_resp = await async_client.get(f"/api/v1/projects/{project_id}")
    assert get_resp.status_code == 404
