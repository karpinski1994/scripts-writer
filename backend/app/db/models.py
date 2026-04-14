import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def _uuid_str() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    topic: Mapped[str] = mapped_column(String(200), nullable=False)
    target_format: Mapped[str] = mapped_column(String(20), nullable=False)
    content_goal: Mapped[str | None] = mapped_column(String(20), nullable=True)
    cta_purpose: Mapped[str | None] = mapped_column(String(100), nullable=True)
    raw_notes: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    current_step: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    notebooklm_notebook_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    piragi_document_paths: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=_now)
    updated_at: Mapped[datetime] = mapped_column(nullable=False, default=_now, onupdate=_now)

    __table_args__ = (
        CheckConstraint(
            "target_format IN ('VSL','YouTube','Tutorial','Facebook','LinkedIn','Blog')",
            name="ck_projects_target_format",
        ),
        CheckConstraint(
            "content_goal IN ('Sell','Educate','Entertain','Build Authority') OR content_goal IS NULL",
            name="ck_projects_content_goal",
        ),
        CheckConstraint(
            "status IN ('draft','in_progress','completed')",
            name="ck_projects_status",
        ),
        Index("idx_projects_status", "status"),
        Index("idx_projects_updated_at", updated_at.desc()),
    )

    icp_profile: Mapped["ICPProfile | None"] = relationship(
        back_populates="project", uselist=False, cascade="all, delete-orphan"
    )
    pipeline_steps: Mapped[list["PipelineStep"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    script_versions: Mapped[list["ScriptVersion"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    analysis_results: Mapped[list["AnalysisResult"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class ICPProfile(Base):
    __tablename__ = "icp_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    demographics: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    psychographics: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    pain_points: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    desires: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    objections: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    language_style: Mapped[str] = mapped_column(String(50), nullable=False, default="professional")
    source: Mapped[str] = mapped_column(String(20), nullable=False, default="generated")
    approved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=_now)
    updated_at: Mapped[datetime] = mapped_column(nullable=False, default=_now, onupdate=_now)

    __table_args__ = (CheckConstraint("source IN ('generated','uploaded','piragi')", name="ck_icp_profiles_source"),)

    project: Mapped["Project"] = relationship(back_populates="icp_profile")


class PipelineStep(Base):
    __tablename__ = "pipeline_steps"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    step_type: Mapped[str] = mapped_column(String(30), nullable=False)
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    input_data: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    output_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    selected_option: Mapped[str | None] = mapped_column(Text, nullable=True)
    llm_provider: Mapped[str | None] = mapped_column(String(20), nullable=True)
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)

    __table_args__ = (
        CheckConstraint(
            "step_type IN ("
            "'icp','hook','narrative','retention','cta',"
            "'writer','factcheck','readability','copyright','policy'"
            ")",
            name="ck_pipeline_steps_step_type",
        ),
        CheckConstraint(
            "status IN ('pending','running','completed','failed')",
            name="ck_pipeline_steps_status",
        ),
        UniqueConstraint("project_id", "step_type", "step_order", name="uq_project_step_type"),
        Index("idx_pipeline_steps_project_order", "project_id", "step_order"),
        Index("idx_pipeline_steps_status", "project_id", "status"),
    )

    project: Mapped["Project"] = relationship(back_populates="pipeline_steps")


class ScriptVersion(Base):
    __tablename__ = "script_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    format: Mapped[str] = mapped_column(String(20), nullable=False)
    hook_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    narrative_pattern: Mapped[str | None] = mapped_column(String(50), nullable=True)
    retention_techniques: Mapped[str | None] = mapped_column(Text, nullable=True)
    cta_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=_now)

    __table_args__ = (
        UniqueConstraint("project_id", "version_number", name="uq_project_version"),
        Index("idx_script_versions_project", "project_id", version_number.desc()),
    )

    project: Mapped["Project"] = relationship(back_populates="script_versions")
    analysis_results: Mapped[list["AnalysisResult"]] = relationship(
        back_populates="script_version", cascade="all, delete-orphan"
    )


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    script_version_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("script_versions.id", ondelete="CASCADE"), nullable=False
    )
    agent_type: Mapped[str] = mapped_column(String(20), nullable=False)
    findings: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=_now)

    __table_args__ = (
        CheckConstraint(
            "agent_type IN ('factcheck','readability','copyright','policy')",
            name="ck_analysis_results_agent_type",
        ),
        UniqueConstraint("project_id", "script_version_id", "agent_type", name="uq_analysis_version_agent"),
        Index("idx_analysis_results_project", "project_id"),
        Index("idx_analysis_results_version", "script_version_id"),
    )

    project: Mapped["Project"] = relationship(back_populates="analysis_results")
    script_version: Mapped["ScriptVersion"] = relationship(back_populates="analysis_results")
