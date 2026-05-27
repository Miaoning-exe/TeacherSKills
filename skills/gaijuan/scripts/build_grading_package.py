from __future__ import annotations

import argparse
import sys
import uuid
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pydantic import TypeAdapter, ValidationError

from shared.schemas.exam import ExamPaper
from shared.schemas.research import ResearchDossier
from shared.schemas.student import StudentResponse
from shared.tools.docx_writer import add_bullets, new_document, save_document
from shared.tools.sources import render_sources_markdown
from skills.gaijuan.scripts.grade_answers import grade_submissions, load_submissions, responses_to_json
from skills.gaijuan.scripts.score_report import generate_score_report


def build_grading_package(
    *,
    exam: ExamPaper,
    answers_json: str,
    output_dir: Path,
    research: ResearchDossier | None = None,
    offline: bool = True,
    rubric: str | None = None,
) -> dict[str, object]:
    submissions = load_submissions(answers_json)
    responses = grade_submissions(exam=exam, submissions=submissions, rubric=rubric, offline=offline)
    report = generate_score_report(exam, responses)
    review_items = _review_required_items(responses)

    output_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "responses_json": "graded_responses.json",
        "score_report_md": "score_report.md",
        "grading_report_docx": "批改报告.docx",
        "review_required_json": "主观题待复核清单.json",
        "package_json": "package.json",
        "sources_md": "sources.md" if research else None,
    }
    (output_dir / files["responses_json"]).write_text(responses_to_json(responses) + "\n", encoding="utf-8")
    (output_dir / files["score_report_md"]).write_text(report, encoding="utf-8")
    (output_dir / files["review_required_json"]).write_text(
        TypeAdapter(list[dict[str, object]]).dump_json(review_items, indent=2).decode("utf-8") + "\n",
        encoding="utf-8",
    )
    _write_grading_docx(exam=exam, responses=responses, review_items=review_items, output_path=output_dir / files["grading_report_docx"])
    if research:
        (output_dir / "sources.md").write_text(render_sources_markdown(research), encoding="utf-8")

    package = {
        "id": f"grading_package_{uuid.uuid4().hex[:12]}",
        "exam_id": exam.id,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "output_dir": str(output_dir),
        "files": files,
        "checks": {
            "responses_generated": bool(responses),
            "review_list_generated": (output_dir / files["review_required_json"]).exists(),
            "report_generated": (output_dir / files["grading_report_docx"]).exists(),
            "sources_generated": bool(not research or (output_dir / "sources.md").exists()),
        },
        "source_ids": [source.id for source in research.sources] if research else [],
    }
    (output_dir / files["package_json"]).write_text(
        TypeAdapter(dict[str, object]).dump_json(package, indent=2).decode("utf-8") + "\n",
        encoding="utf-8",
    )
    return package


def _review_required_items(responses: list[StudentResponse]) -> list[dict[str, object]]:
    return [
        {
            "student_id": response.student_id,
            "question_id": response.question_id,
            "answer": response.answer,
            "max_score": response.max_score,
            "reason": response.feedback or "主观题需教师复核",
        }
        for response in responses
        if response.score is None
    ]


def _write_grading_docx(
    *,
    exam: ExamPaper,
    responses: list[StudentResponse],
    review_items: list[dict[str, object]],
    output_path: Path,
) -> None:
    document = new_document()
    document.add_heading(f"{exam.title} 批改报告", level=1)
    document.add_paragraph(f"学科：{exam.subject}    年级：{exam.grade}    满分：{exam.total_score:g}")
    add_bullets(
        document,
        "批改概览",
        [
            f"作答记录数：{len(responses)}",
            f"待教师复核题数：{len(review_items)}",
            "客观题由本地规则确定性评分，主观题离线时进入待复核清单。",
        ],
    )
    document.add_heading("逐题反馈", level=2)
    for response in responses:
        score = "待评分" if response.score is None else f"{response.score:g}"
        document.add_paragraph(
            f"{response.student_id} / {response.question_id}: {score}/{response.max_score:g}；{response.feedback or ''}"
        )
    if review_items:
        add_bullets(document, "主观题待复核", [f"{item['student_id']} - {item['question_id']}: {item['reason']}" for item in review_items])
    save_document(document, output_path)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="生成 Stage E 正式批改包。")
    parser.add_argument("--exam", required=True, type=Path, help="ExamPaper JSON 文件")
    parser.add_argument("--answers", required=True, type=Path, help="学生作答 JSON 文件")
    parser.add_argument("--research", type=Path, default=None, help="ResearchDossier JSON 资料包")
    parser.add_argument("--rubric-file", type=Path, default=None, help="主观题评分标准文件")
    parser.add_argument("--online", action="store_true", help="允许调用远程主观题评分")
    parser.add_argument("--output-dir", required=True, type=Path, help="输出批改包目录")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    try:
        exam = ExamPaper.model_validate_json(args.exam.read_text(encoding="utf-8"))
        research = ResearchDossier.model_validate_json(args.research.read_text(encoding="utf-8")) if args.research else None
        rubric = args.rubric_file.read_text(encoding="utf-8") if args.rubric_file else None
        package = build_grading_package(
            exam=exam,
            answers_json=args.answers.read_text(encoding="utf-8"),
            output_dir=args.output_dir,
            research=research,
            offline=not args.online,
            rubric=rubric,
        )
    except FileNotFoundError as exc:
        sys.stderr.write(f"输入文件不存在: {exc.filename}\n")
        return 1
    except (RuntimeError, ValidationError, ValueError) as exc:
        sys.stderr.write(f"{exc}\n")
        return 1
    sys.stdout.write(TypeAdapter(dict[str, object]).dump_json(package, indent=2).decode("utf-8") + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
