from __future__ import annotations

import argparse
import sys
import uuid
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pydantic import BaseModel, Field, TypeAdapter, ValidationError

from shared.schemas.exam import ExamPaper, ExamSection
from shared.schemas.question import DifficultyLevel, Question, QuestionType


QUESTION_LIST_ADAPTER = TypeAdapter(list[Question])


class SectionConstraint(BaseModel):
    title: str | None = None
    question_type: QuestionType
    count: int
    score_per_question: float | None = None
    required_knowledge_points: list[str] = Field(default_factory=list)


class ExamConstraints(BaseModel):
    title: str
    subject: str
    grade: str
    duration_minutes: int
    sections: list[SectionConstraint]
    difficulty_distribution: dict[DifficultyLevel, float] = Field(default_factory=dict)
    required_knowledge_points: list[str] = Field(default_factory=list)


def load_questions(raw_json: str) -> list[Question]:
    return QUESTION_LIST_ADAPTER.validate_json(raw_json)


def load_constraints(raw_json: str) -> ExamConstraints:
    return ExamConstraints.model_validate_json(raw_json)


def assemble_exam(questions: list[Question], constraints: ExamConstraints) -> ExamPaper:
    if constraints.duration_minutes <= 0:
        raise ValueError("duration_minutes 必须大于 0")
    if not constraints.sections:
        raise ValueError("sections 不能为空")

    selected_ids: set[str] = set()
    selected_questions: list[Question] = []
    sections: list[ExamSection] = []

    for section_index, section_constraint in enumerate(constraints.sections, start=1):
        if section_constraint.count <= 0:
            raise ValueError(f"{section_constraint.question_type.value}: count 必须大于 0")
        if section_constraint.score_per_question is not None and section_constraint.score_per_question <= 0:
            raise ValueError(f"{section_constraint.question_type.value}: score_per_question 必须大于 0")

        section_questions = _select_section_questions(
            questions=questions,
            constraints=constraints,
            section_constraint=section_constraint,
            already_selected_ids=selected_ids,
            selected_so_far=selected_questions,
        )
        selected_ids.update(question.id for question in section_questions)
        selected_questions.extend(section_questions)

        scored_questions = [
            question.model_copy(update={"score": section_constraint.score_per_question})
            if section_constraint.score_per_question is not None
            else question
            for question in section_questions
        ]
        section_score = sum(question.score for question in scored_questions)
        sections.append(
            ExamSection(
                title=section_constraint.title
                or _default_section_title(section_index, section_constraint.question_type),
                question_type=section_constraint.question_type,
                questions=scored_questions,
                section_score=section_score,
            )
        )

    _validate_required_knowledge_points(selected_questions, constraints.required_knowledge_points)

    return ExamPaper(
        id=f"exam_{uuid.uuid4().hex[:12]}",
        title=constraints.title,
        subject=constraints.subject,
        grade=constraints.grade,
        total_score=sum(section.section_score for section in sections),
        duration_minutes=constraints.duration_minutes,
        sections=sections,
    )


def exam_to_json(exam: ExamPaper) -> str:
    return exam.model_dump_json(indent=2)


def _select_section_questions(
    questions: list[Question],
    constraints: ExamConstraints,
    section_constraint: SectionConstraint,
    already_selected_ids: set[str],
    selected_so_far: list[Question],
) -> list[Question]:
    candidates = [
        question
        for question in questions
        if question.id not in already_selected_ids
        and question.subject == constraints.subject
        and question.question_type == section_constraint.question_type
        and _contains_all(question.knowledge_points, section_constraint.required_knowledge_points)
    ]
    if len(candidates) < section_constraint.count:
        raise ValueError(
            f"{section_constraint.question_type.value} 可用题目不足：需要 {section_constraint.count} 道，"
            f"实际 {len(candidates)} 道"
        )

    selected: list[Question] = []
    while len(selected) < section_constraint.count:
        candidate = min(
            candidates,
            key=lambda question: _candidate_rank(
                question=question,
                selected=selected_so_far + selected,
                constraints=constraints,
            ),
        )
        selected.append(candidate)
        candidates.remove(candidate)
    return selected


def _candidate_rank(
    question: Question,
    selected: list[Question],
    constraints: ExamConstraints,
) -> tuple[float, int, str]:
    difficulty_penalty = _difficulty_penalty(question, selected, constraints.difficulty_distribution)
    knowledge_bonus = _new_required_knowledge_count(question, selected, constraints.required_knowledge_points)
    return (difficulty_penalty, -knowledge_bonus, question.id)


def _difficulty_penalty(
    question: Question,
    selected: list[Question],
    distribution: dict[DifficultyLevel, float],
) -> float:
    if not distribution:
        return 0.0
    total = len(selected) + 1
    counts = {difficulty: 0 for difficulty in distribution}
    for item in selected:
        if item.difficulty in counts:
            counts[item.difficulty] += 1
    if question.difficulty in counts:
        counts[question.difficulty] += 1
    return sum(abs((counts[difficulty] / total) - target) for difficulty, target in distribution.items())


def _new_required_knowledge_count(
    question: Question,
    selected: list[Question],
    required_knowledge_points: list[str],
) -> int:
    if not required_knowledge_points:
        return 0
    covered = {point for selected_question in selected for point in selected_question.knowledge_points}
    return len(set(question.knowledge_points) & (set(required_knowledge_points) - covered))


def _contains_all(values: list[str], required_values: list[str]) -> bool:
    return set(required_values).issubset(values)


def _validate_required_knowledge_points(
    selected_questions: list[Question],
    required_knowledge_points: list[str],
) -> None:
    covered = {point for question in selected_questions for point in question.knowledge_points}
    missing = sorted(set(required_knowledge_points) - covered)
    if missing:
        raise ValueError(f"知识点覆盖不足，缺少: {', '.join(missing)}")


def _default_section_title(section_index: int, question_type: QuestionType) -> str:
    return f"{_chinese_number(section_index)}、{question_type.value}"


def _chinese_number(number: int) -> str:
    numerals = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
    if 0 <= number <= 10:
        return numerals[number]
    return str(number)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="根据 Question[] 和约束 JSON 组装 ExamPaper。")
    parser.add_argument("--questions", required=True, type=Path, help="Question[] JSON 文件")
    parser.add_argument("--constraints", required=True, type=Path, help="组卷约束 JSON 文件")
    parser.add_argument("--output", type=Path, default=None, help="输出 ExamPaper JSON；不传则写到 stdout")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    try:
        questions = load_questions(args.questions.read_text(encoding="utf-8"))
        constraints = load_constraints(args.constraints.read_text(encoding="utf-8"))
        output = exam_to_json(assemble_exam(questions, constraints))
    except FileNotFoundError as exc:
        sys.stderr.write(f"输入文件不存在: {exc.filename}\n")
        return 1
    except (ValidationError, ValueError) as exc:
        sys.stderr.write(f"{exc}\n")
        return 1

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + "\n", encoding="utf-8")
    else:
        sys.stdout.write(output + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
