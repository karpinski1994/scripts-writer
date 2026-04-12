from app.services.export_service import ExportService


class MockVersion:
    def __init__(
        self,
        version_number=1,
        content="Hello world",
        format="VSL",
        hook_text=None,
        narrative_pattern=None,
        cta_text=None,
    ):
        self.version_number = version_number
        self.content = content
        self.format = format
        self.hook_text = hook_text
        self.narrative_pattern = narrative_pattern
        self.cta_text = cta_text


def test_export_txt_creates_file(tmp_path):
    service = ExportService(db=None, export_dir=str(tmp_path))

    async def fake_get_version(version_id, project_id):
        return MockVersion(content="raw script content")

    service._get_version = fake_get_version
    import asyncio

    filepath = asyncio.get_event_loop().run_until_complete(service.export_txt("proj1", "v1"))
    assert filepath.exists()
    assert filepath.read_text() == "raw script content"
    assert filepath.suffix == ".txt"


def test_export_md_creates_file_with_metadata(tmp_path):
    service = ExportService(db=None, export_dir=str(tmp_path))

    async def fake_get_version(version_id, project_id):
        return MockVersion(
            content="script body", format="VSL", hook_text="hook!", narrative_pattern="Hero", cta_text="Buy now"
        )

    service._get_version = fake_get_version
    import asyncio

    filepath = asyncio.get_event_loop().run_until_complete(service.export_md("proj1", "v1"))
    content = filepath.read_text()
    assert "Script v1" in content
    assert "VSL" in content
    assert "hook!" in content
    assert "Hero" in content
    assert "Buy now" in content
    assert "script body" in content
    assert filepath.suffix == ".md"


def test_slugify_sanitizes_filenames():
    assert ExportService._slugify("Hello World!") == "hello-world"
    assert ExportService._slugify("a/b\\c:d*e?f") == "a-b-c-d-e-f"
    assert ExportService._slugify("  spaces  ") == "spaces"
    assert ExportService._slugify("multiple---dashes") == "multiple-dashes"
