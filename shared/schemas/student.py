from pydantic import BaseModel


class StudentResponse(BaseModel):
    student_id: str
    question_id: str
    answer: str
    score: float | None = None
    max_score: float
    feedback: str | None = None


class KnowledgeMastery(BaseModel):
    student_id: str
    knowledge_point_id: str
    mastery_level: float
    confidence: float | None = None
