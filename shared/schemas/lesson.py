from pydantic import BaseModel, Field


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


class LessonContext(BaseModel):
    id: str
    title: str
    subject: str
    grade: str
    topic: str
    duration_minutes: int = 45
    curriculum_alignment: list[str] = Field(default_factory=list)
    knowledge_points: list[str] = Field(default_factory=list)
    core_competencies: list[str] = Field(default_factory=list)
    key_points: list[str] = Field(default_factory=list)
    difficult_points: list[str] = Field(default_factory=list)
    misconceptions: list[str] = Field(default_factory=list)
    teaching_strategies: list[str] = Field(default_factory=list)
    activity_suggestions: list[str] = Field(default_factory=list)
    assessment_suggestions: list[str] = Field(default_factory=list)
    teacher_review_notes: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    local_fallback: bool = False


class LessonPackage(BaseModel):
    id: str
    lesson_context_id: str
    lesson_plan_id: str
    created_at: str
    output_dir: str
    files: dict[str, str]
    checks: dict[str, bool]
    source_ids: list[str] = Field(default_factory=list)
