from enum import Enum


class StepType(str, Enum):
    ICP = "icp"
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
    StepType.HOOK: "hooks",
    StepType.NARRATIVE: "narratives",
    StepType.RETENTION: "retention",
    StepType.CTA: "cta",
    StepType.FACTCHECK: "fact_checks",
    StepType.READABILITY: "fact_checks",
    StepType.COPYRIGHT: "fact_checks",
    StepType.POLICY: "policies",
}

PIRAGI_PERSIST_DIR = ".piragi"
PIRAGI_DEFAULT_TOP_K = 3
PIRAGI_EMBEDDING_MODEL = "all-mpnet-base-v2"
PIRAGI_CHUNK_STRATEGY = "semantic"
