from enum import StrEnum


class StepType(StrEnum):
    ICP = "icp"
    SUBJECT = "subject"
    HOOK = "hook"
    NARRATIVE = "narrative"
    RETENTION = "retention"
    CTA = "cta"
    WRITER = "writer"
    FACTCHECK = "factcheck"
    READABILITY = "readability"
    COPYRIGHT = "copyright"
    POLICY = "policy"


STEP_CATEGORY_MAP: dict[StepType, str] = {
    StepType.ICP: "icp",
    StepType.SUBJECT: "subject",
    StepType.HOOK: "hooks",
    StepType.NARRATIVE: "narratives",
    StepType.RETENTION: "retention",
    StepType.CTA: "cta",
    StepType.FACTCHECK: "fact_checks",
    StepType.READABILITY: "fact_checks",
    StepType.COPYRIGHT: "fact_checks",
    StepType.POLICY: "policies",
}

STEP_DEPENDENCIES: dict[StepType, list[StepType]] = {
    StepType.ICP: [StepType.ICP],
    StepType.SUBJECT: [StepType.ICP],
    StepType.HOOK: [StepType.ICP, StepType.SUBJECT],
    StepType.NARRATIVE: [StepType.ICP, StepType.SUBJECT, StepType.HOOK],
    StepType.RETENTION: [StepType.ICP, StepType.SUBJECT, StepType.HOOK],
    StepType.CTA: [StepType.ICP, StepType.SUBJECT, StepType.HOOK],
    StepType.WRITER: [StepType.ICP, StepType.SUBJECT, StepType.NARRATIVE, StepType.RETENTION, StepType.CTA],
}

DEV_PROVIDED_CATEGORIES: dict[StepType, list[str]] = {
    StepType.NARRATIVE: ["narrative_patterns"],
    StepType.RETENTION: ["retention_tactics"],
}

PIRAGI_PERSIST_DIR = ".piragi"
PIRAGI_DEFAULT_TOP_K = 3
PIRAGI_EMBEDDING_MODEL = "all-mpnet-base-v2"
PIRAGI_CHUNK_STRATEGY = "semantic"
