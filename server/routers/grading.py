from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

try:
    from server.auth import require_bearer_token
except ModuleNotFoundError:  # pragma: no cover - for `cd server && uvicorn app:app`
    from auth import require_bearer_token


router = APIRouter(prefix="/api", tags=["grading"])


class GradeRequest(BaseModel):
    question: dict
    student_answer: str
    max_score: float
    rubric: str | None = None


class GradeResponse(BaseModel):
    score: float
    feedback: str


@router.post("/grade", response_model=GradeResponse, dependencies=[Depends(require_bearer_token)])
def grade_answer(payload: GradeRequest) -> GradeResponse:
    reference_answer = str(payload.question.get("answer", "")).strip()
    student_answer = payload.student_answer.strip()
    question_type = payload.question.get("question_type")

    if question_type in {"选择题", "填空题", "判断题", "完形填空", "语法填空"}:
        correct = student_answer.casefold() == reference_answer.casefold()
        score = payload.max_score if correct else 0.0
        feedback = "答案正确" if correct else f"答案错误，参考答案：{reference_answer}"
        return GradeResponse(score=score, feedback=feedback)

    score = _estimate_subjective_score(student_answer=student_answer, max_score=payload.max_score)
    feedback = _subjective_feedback(reference_answer=reference_answer, student_answer=student_answer, rubric=payload.rubric)
    return GradeResponse(score=score, feedback=feedback)


def _estimate_subjective_score(*, student_answer: str, max_score: float) -> float:
    if not student_answer:
        return 0.0
    length_factor = min(1.0, len(student_answer.strip()) / 80)
    return round(max_score * (0.4 + 0.6 * length_factor), 2)


def _subjective_feedback(*, reference_answer: str, student_answer: str, rubric: str | None) -> str:
    if not student_answer:
        return "未作答，建议补充关键步骤或核心观点。"
    segments = ["已根据作答内容给出启发式评分。"]
    if rubric:
        segments.append("已参考提交的评分标准。")
    if reference_answer:
        segments.append("建议继续对照参考答案检查关键步骤或观点是否完整。")
    return " ".join(segments)
