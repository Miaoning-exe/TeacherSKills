from pydantic import BaseModel
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
