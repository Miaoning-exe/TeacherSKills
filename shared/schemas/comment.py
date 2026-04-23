from pydantic import BaseModel, Field


class TeacherObservation(BaseModel):
    student_id: str
    student_name: str | None = None
    strengths: list[str] = Field(default_factory=list)
    habits: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)
    notes: str | None = None


class StudentComment(BaseModel):
    student_id: str
    student_name: str | None = None
    term: str = "期末"
    comment: str
    highlights: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
