from enum import Enum

from pydantic import BaseModel, Field


class SourceType(str, Enum):
    CURRICULUM_STANDARD = "课标"
    TEXTBOOK = "教材"
    SAMPLE_EXAM = "样卷"
    QUESTION_PATTERN = "题型"
    SCORING_RUBRIC = "评分"
    TEMPLATE = "模板"
    LOCAL_REFERENCE = "本地参考"
    OTHER = "其他"


class CredibilityLevel(str, Enum):
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"


class SourceEvidence(BaseModel):
    id: str
    title: str
    source_type: SourceType
    summary: str
    url: str | None = None
    publisher: str | None = None
    published_at: str | None = None
    retrieved_at: str | None = None
    credibility: CredibilityLevel = CredibilityLevel.MEDIUM
    citation_locations: list[str] = Field(default_factory=list)
    review_note: str | None = None


class ResearchDossier(BaseModel):
    id: str
    task_type: str
    subject: str
    grade: str
    topic: str
    created_at: str
    query_summary: str
    sources: list[SourceEvidence]
    key_findings: list[str] = Field(default_factory=list)
    agent_inferences: list[str] = Field(default_factory=list)
    teacher_review_notes: list[str] = Field(default_factory=list)
    local_fallback: bool = False
