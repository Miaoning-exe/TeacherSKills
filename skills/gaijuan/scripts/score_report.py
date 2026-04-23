from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pydantic import TypeAdapter, ValidationError

from shared.schemas.exam import ExamPaper
from shared.schemas.student import StudentResponse


STUDENT_RESPONSE_ADAPTER = TypeAdapter(list[StudentResponse])


def load_exam(raw_json: str) -> ExamPaper:
    return ExamPaper.model_validate_json(raw_json)


def load_responses(raw_json: str) -> list[StudentResponse]:
    return STUDENT_RESPONSE_ADAPTER.validate_json(raw_json)


def generate_score_report(exam: ExamPaper, responses: list[StudentResponse]) -> str:
    question_lookup = {
        question.id: question
        for section in exam.sections
        for question in section.questions
    }
    grouped: dict[str, list[StudentResponse]] = defaultdict(list)
    for response in responses:
        grouped[response.student_id].append(response)

    lines = [
        f"# {exam.title} 批改报告",
        "",
        f"- 学科：{exam.subject}",
        f"- 年级：{exam.grade}",
        f"- 试卷满分：{exam.total_score:g}",
        f"- 统计学生数：{len(grouped)}",
        "",
    ]
    for student_id in sorted(grouped):
        student_responses = grouped[student_id]
        graded_score = sum(response.score or 0.0 for response in student_responses)
        pending_count = sum(1 for response in student_responses if response.score is None)
        lines.extend(
            [
                f"## 学生 {student_id}",
                "",
                f"- 已得分：{graded_score:g}",
                f"- 待评分题数：{pending_count}",
                "",
                "| 题号 | 题型 | 得分 | 满分 | 反馈 |",
                "|------|------|------|------|------|",
            ]
        )
        for response in student_responses:
            question = question_lookup.get(response.question_id)
            question_type = question.question_type.value if question else "未知"
            score_text = "待评分" if response.score is None else f"{response.score:g}"
            feedback = (response.feedback or "").replace("\n", " ")
            lines.append(
                f"| {response.question_id} | {question_type} | {score_text} | {response.max_score:g} | {feedback} |"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="根据 StudentResponse[] 生成 Markdown 成绩报告。")
    parser.add_argument("--exam", required=True, type=Path, help="ExamPaper JSON 文件")
    parser.add_argument("--responses", required=True, type=Path, help="StudentResponse[] JSON 文件")
    parser.add_argument("--output", required=True, type=Path, help="输出 Markdown 文件路径")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    try:
        exam = load_exam(args.exam.read_text(encoding="utf-8"))
        responses = load_responses(args.responses.read_text(encoding="utf-8"))
        report = generate_score_report(exam, responses)
    except FileNotFoundError as exc:
        sys.stderr.write(f"输入文件不存在: {exc.filename}\n")
        return 1
    except ValidationError as exc:
        sys.stderr.write(f"{exc}\n")
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
