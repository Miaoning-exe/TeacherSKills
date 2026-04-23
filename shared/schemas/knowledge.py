from enum import Enum
from pydantic import BaseModel


class KnowledgeLevel(str, Enum):
    REMEMBER = "识记"
    UNDERSTAND = "理解"
    APPLY = "应用"
    ANALYZE = "分析"
    EVALUATE = "评价"
    CREATE = "创造"


class KnowledgePoint(BaseModel):
    id: str
    name: str
    subject: str
    grade: str
    chapter: str | None = None
    parent_id: str | None = None
    cognitive_level: KnowledgeLevel
    curriculum_standard_ref: str | None = None
