import pytest

from app.schemas.project import ContentGoal, ProjectCreateRequest, ProjectUpdateRequest, TargetFormat
from app.services.project_service import ProjectService


@pytest.mark.asyncio
async def test_create_project(db_session):
    service = ProjectService(db_session)
    data = ProjectCreateRequest(name="Test", topic="Python", target_format=TargetFormat.VSL, raw_notes="some notes")
    project = await service.create(data)
    assert project.id is not None
    assert project.name == "Test"
    assert project.topic == "Python"
    assert project.target_format == "VSL"
    assert project.status == "draft"


@pytest.mark.asyncio
async def test_list_projects(db_session):
    service = ProjectService(db_session)
    await service.create(ProjectCreateRequest(name="A", topic="T1", target_format=TargetFormat.VSL, raw_notes="n1"))
    await service.create(ProjectCreateRequest(name="B", topic="T2", target_format=TargetFormat.Blog, raw_notes="n2"))
    projects = await service.list_all()
    assert len(projects) == 2


@pytest.mark.asyncio
async def test_get_by_id(db_session):
    service = ProjectService(db_session)
    created = await service.create(
        ProjectCreateRequest(name="X", topic="T", target_format=TargetFormat.YouTube, raw_notes="n")
    )
    found = await service.get_by_id(created.id)
    assert found.name == "X"


@pytest.mark.asyncio
async def test_get_by_id_not_found(db_session):
    service = ProjectService(db_session)
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        await service.get_by_id("nonexistent-id")
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_update_project(db_session):
    service = ProjectService(db_session)
    created = await service.create(
        ProjectCreateRequest(name="Old", topic="T", target_format=TargetFormat.VSL, raw_notes="n")
    )
    updated = await service.update(created.id, ProjectUpdateRequest(name="New"))
    assert updated.name == "New"


@pytest.mark.asyncio
async def test_delete_project(db_session):
    service = ProjectService(db_session)
    created = await service.create(
        ProjectCreateRequest(name="Del", topic="T", target_format=TargetFormat.VSL, raw_notes="n")
    )
    await service.delete(created.id)
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        await service.get_by_id(created.id)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_create_project_with_content_goal(db_session):
    service = ProjectService(db_session)
    data = ProjectCreateRequest(
        name="CG", topic="T", target_format=TargetFormat.VSL, content_goal=ContentGoal.Sell, raw_notes="n"
    )
    project = await service.create(data)
    assert project.content_goal == "Sell"
