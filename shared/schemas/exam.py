from pydantic import BaseModel, Field
from shared.schemas.question import Question, QuestionType


class ExamSection(BaseModel):
    title: str
    question_type: QuestionType
    questions: list[Question]
    section_score: float


class ExamPaper(BaseModel):
    id: str
    title: str
    subject: str
    grade: str
    total_score: float
    duration_minutes: int
    sections: list[ExamSection]


class ExamBlueprintSection(BaseModel):
    title: str
    question_type: QuestionType
    item_count: int
    score_per_item: float
    section_score: float
    difficulty_ratio: dict[str, float] = Field(default_factory=dict)
    required_knowledge_points: list[str] = Field(default_factory=list)


class ExamBlueprint(BaseModel):
    id: str
    title: str
    subject: str
    grade: str
    exam_type: str
    total_score: float
    duration_minutes: int
    sections: list[ExamBlueprintSection]
    knowledge_points: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    profile_id: str | None = None


class AnswerSheetSectionSpec(BaseModel):
    title: str
    question_type: QuestionType
    question_numbers: list[int]
    response_area: str
    notes: list[str] = Field(default_factory=list)


class AnswerSheetSpec(BaseModel):
    exam_id: str
    title: str
    student_fields: list[str] = Field(default_factory=lambda: ["姓名", "班级", "学号"])
    sections: list[AnswerSheetSectionSpec]


class AnswerKeyItem(BaseModel):
    question_number: int
    question_id: str
    answer: str
    score: float
    explanation: str | None = None


class AnswerKey(BaseModel):
    exam_id: str
    items: list[AnswerKeyItem]


class ScoringRubricItem(BaseModel):
    question_number: int
    question_id: str
    max_score: float
    scoring_points: list[str]
    review_required: bool = False


class ScoringRubric(BaseModel):
    exam_id: str
    items: list[ScoringRubricItem]


class ExamPackage(BaseModel):
    id: str
    exam_id: str
    created_at: str
    output_dir: str
    files: dict[str, str]
    checks: dict[str, bool]
    profile_id: str | None = None
    source_ids: list[str] = Field(default_factory=list)
