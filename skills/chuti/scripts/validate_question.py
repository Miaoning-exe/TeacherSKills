from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pydantic import TypeAdapter, ValidationError

from shared.schemas.question import Question, QuestionType


QUESTION_LIST_ADAPTER = TypeAdapter(list[Question])
QUESTION_ADAPTER = TypeAdapter(Question)


def load_questions_json(raw_json: str) -> list[Question]:
    try:
        return QUESTION_LIST_ADAPTER.validate_json(raw_json)
    except ValidationError as list_error:
        try:
            return [QUESTION_ADAPTER.validate_json(raw_json)]
        except ValidationError as single_error:
            raise ValueError(f"Question JSON 校验失败: {single_error}") from list_error


def validate_question(question: Question) -> list[str]:
    errors: list[str] = []
    if question.score <= 0:
        errors.append(f"{question.id}: score 必须大于 0")
    if not question.knowledge_points:
        errors.append(f"{question.id}: knowledge_points 不能为空")
    if question.question_type == QuestionType.CHOICE:
        if not question.options or len(question.options) < 2:
            errors.append(f"{question.id}: 选择题至少需要 2 个选项")
        elif not _answer_matches_options(question.answer, question.options):
            errors.append(f"{question.id}: 选择题答案需要匹配选项编号或选项内容")
    if question.question_type in {
        QuestionType.READING_COMP,
        QuestionType.CLOZE,
        QuestionType.CLASSICAL_CHINESE,
    } and not question.material:
        errors.append(f"{question.id}: {question.question_type.value}建议提供 material")
    return errors


def validate_questions(questions: list[Question]) -> list[str]:
    errors: list[str] = []
    for question in questions:
        errors.extend(validate_question(question))
    return errors


def _answer_matches_options(answer: str, options: list[str]) -> bool:
    normalized_answer = answer.strip()
    if normalized_answer in options:
        return True
    prefixes = [option.split(".", 1)[0].strip() for option in options if "." in option]
    return normalized_answer in prefixes


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="校验 Question 或 Question[] JSON。")
    parser.add_argument("input", nargs="?", type=Path, help="输入 JSON 文件；不传则从 stdin 读取")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    try:
        raw_json = args.input.read_text(encoding="utf-8") if args.input else sys.stdin.read()
    except FileNotFoundError:
        missing_path = args.input if args.input else "<stdin>"
        sys.stderr.write(f"输入文件不存在: {missing_path}\n")
        return 1
    try:
        questions = load_questions_json(raw_json)
    except ValueError as exc:
        sys.stderr.write(f"{exc}\n")
        return 1

    errors = validate_questions(questions)
    if errors:
        sys.stderr.write("\n".join(errors) + "\n")
        return 1

    sys.stdout.write(f"校验通过：{len(questions)} 道题\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
