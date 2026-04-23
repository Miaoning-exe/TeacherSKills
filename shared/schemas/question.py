from enum import Enum
from pydantic import BaseModel, Field


class QuestionType(str, Enum):
    CHOICE = "选择题"
    FILL_BLANK = "填空题"
    SHORT_ANSWER = "解答题"
    TRUE_FALSE = "判断题"
    COMPUTATION = "计算题"
    PROOF = "证明题"
    APPLICATION = "应用题"
    READING_COMP = "阅读理解"
    POETRY = "古诗词"
    CLASSICAL_CHINESE = "文言文"
    ESSAY = "作文"
    CLOZE = "完形填空"
    GRAMMAR = "语法填空"
    WRITING = "书面表达"
    TRANSLATION = "翻译"


class DifficultyLevel(str, Enum):
    EASY = "易"
    MEDIUM = "中"
    HARD = "难"


class Question(BaseModel):
    id: str
    content: str
    subject: str
    question_type: QuestionType
    difficulty: DifficultyLevel
    knowledge_points: list[str]
    answer: str
    explanation: str | None = None
    score: float = 1.0
    options: list[str] | None = None
    material: str | None = None
    sub_questions: list["Question"] | None = None
    source: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)
