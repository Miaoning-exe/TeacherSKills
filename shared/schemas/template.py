from pydantic import BaseModel, Field


class TemplateSectionProfile(BaseModel):
    title: str
    question_type: str | None = None
    item_count: int | None = None
    score_per_item: float | None = None
    total_score: float | None = None
    difficulty_ratio: dict[str, float] = Field(default_factory=dict)
    notes: list[str] = Field(default_factory=list)


class TemplateFormattingProfile(BaseModel):
    page_size: str = "A4"
    orientation: str = "portrait"
    font_family: str = "宋体"
    font_size_pt: float = 10.5
    line_spacing: float = 1.2
    include_header: bool = True
    include_score_table: bool = True


class TemplateProfile(BaseModel):
    id: str
    name: str
    subject: str
    grade_band: str
    exam_type: str
    total_score: float | None = None
    duration_minutes: int | None = None
    sections: list[TemplateSectionProfile]
    formatting: TemplateFormattingProfile = Field(default_factory=TemplateFormattingProfile)
    required_outputs: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    review_notes: list[str] = Field(default_factory=list)
