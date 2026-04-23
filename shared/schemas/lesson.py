from pydantic import BaseModel


class TeachingStep(BaseModel):
    phase: str
    duration_minutes: int
    content: str
    teacher_activity: str
    student_activity: str
    design_intent: str | None = None


class LessonPlan(BaseModel):
    id: str
    title: str
    subject: str
    grade: str
    duration_minutes: int
    knowledge_points: list[str]
    objectives: list[str]
    key_points: list[str]
    difficult_points: list[str]
    teaching_flow: list[TeachingStep]
    homework: str | None = None
    reflection: str | None = None
