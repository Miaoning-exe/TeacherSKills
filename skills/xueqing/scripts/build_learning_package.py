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

from shared.schemas.research import ResearchDossier
from shared.tools.docx_writer import add_bullets, new_document, save_document
from shared.tools.sources import render_sources_markdown
from skills.xueqing.scripts.analyze_learning import (
    analyze_learning,
    generate_learning_report,
    load_knowledge_points,
    load_questions,
    load_responses,
    mastery_to_json,
)
from skills.xueqing.scripts.visualize_mastery import generate_visualizations


def build_learning_package(
    *,
    responses_json: str,
    knowledge_points_json: str,
    output_dir: Path,
    questions_json: str | None = None,
    research: ResearchDossier | None = None,
    offline: bool = True,
    chart_dir: Path | None = None,
) -> dict[str, object]:
    responses = load_responses(responses_json)
    knowledge_points = load_knowledge_points(knowledge_points_json)
    questions = load_questions(questions_json) if questions_json else None
    mastery = analyze_learning(responses=responses, knowledge_points=knowledge_points, questions=questions, offline=offline)
    report = generate_learning_report(mastery=mastery, knowledge_points=knowledge_points)
    remediation = _build_remediation_plan(mastery, {point.id: point.name for point in knowledge_points})

    output_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "mastery_json": "mastery.json",
        "learning_report_md": "learning_report.md",
        "class_report_docx": "班级学情报告.docx",
        "student_diagnosis_docx": "学生个人诊断报告.docx",
        "remediation_docx": "补救练习建议.docx",
        "remediation_json": "remediation_plan.json",
        "package_json": "package.json",
        "sources_md": "sources.md" if research else None,
    }
    (output_dir / files["mastery_json"]).write_text(mastery_to_json(mastery) + "\n", encoding="utf-8")
    (output_dir / files["learning_report_md"]).write_text(report, encoding="utf-8")
    (output_dir / files["remediation_json"]).write_text(
        TypeAdapter(list[dict[str, object]]).dump_json(remediation, indent=2).decode("utf-8") + "\n",
        encoding="utf-8",
    )
    _write_class_report(report, output_dir / files["class_report_docx"])
    _write_student_diagnosis(mastery, {point.id: point.name for point in knowledge_points}, output_dir / files["student_diagnosis_docx"])
    _write_remediation_docx(remediation, output_dir / files["remediation_docx"])
    chart_paths: list[str] = []
    if chart_dir:
        try:
            chart_paths = [str(path) for path in generate_visualizations(mastery=mastery, knowledge_points=knowledge_points, output_dir=chart_dir)]
        except RuntimeError:
            chart_paths = []
    if research:
        (output_dir / "sources.md").write_text(render_sources_markdown(research), encoding="utf-8")

    package = {
        "id": f"learning_package_{uuid.uuid4().hex[:12]}",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "output_dir": str(output_dir),
        "files": files,
        "charts": chart_paths,
        "checks": {
            "mastery_generated": bool(mastery),
            "remediation_generated": bool(remediation),
            "docx_generated": all((output_dir / files[key]).exists() for key in ["class_report_docx", "student_diagnosis_docx", "remediation_docx"]),
            "sources_generated": bool(not research or (output_dir / "sources.md").exists()),
        },
        "source_ids": [source.id for source in research.sources] if research else [],
    }
    (output_dir / files["package_json"]).write_text(
        TypeAdapter(dict[str, object]).dump_json(package, indent=2).decode("utf-8") + "\n",
        encoding="utf-8",
    )
    return package


def _build_remediation_plan(mastery, knowledge_lookup: dict[str, str]) -> list[dict[str, object]]:
    plan: list[dict[str, object]] = []
    for item in mastery:
        if item.mastery_level < 0.7:
            name = knowledge_lookup.get(item.knowledge_point_id, item.knowledge_point_id)
            plan.append(
                {
                    "student_id": item.student_id,
                    "knowledge_point_id": item.knowledge_point_id,
                    "knowledge_point_name": name,
                    "mastery_level": item.mastery_level,
                    "suggestion": f"补做 {name} 的基础题、变式题各 1 组，并要求学生订正错因。",
                }
            )
    return plan


def _write_class_report(report: str, output_path: Path) -> None:
    document = new_document()
    document.add_heading("班级学情报告", level=1)
    for line in report.splitlines():
        if line.startswith("# "):
            continue
        if line.startswith("## "):
            document.add_heading(line[3:].strip(), level=2)
        elif line.startswith("### "):
            document.add_heading(line[4:].strip(), level=3)
        elif line.startswith("- "):
            document.add_paragraph(line[2:].strip(), style="List Bullet")
        elif line.startswith("|") or not line.strip():
            continue
        else:
            document.add_paragraph(line)
    save_document(document, output_path)


def _write_student_diagnosis(mastery, knowledge_lookup: dict[str, str], output_path: Path) -> None:
    document = new_document()
    document.add_heading("学生个人诊断报告", level=1)
    grouped: dict[str, list[object]] = {}
    for item in mastery:
        grouped.setdefault(item.student_id, []).append(item)
    for student_id in sorted(grouped):
        document.add_heading(f"学生 {student_id}", level=2)
        for item in sorted(grouped[student_id], key=lambda value: value.mastery_level):
            name = knowledge_lookup.get(item.knowledge_point_id, item.knowledge_point_id)
            document.add_paragraph(f"{name}: 掌握度 {item.mastery_level:.2f}，置信度 {item.confidence or 0:.2f}")
    save_document(document, output_path)


def _write_remediation_docx(remediation: list[dict[str, object]], output_path: Path) -> None:
    document = new_document()
    document.add_heading("补救练习建议", level=1)
    add_bullets(document, "建议清单", [f"{item['student_id']} - {item['knowledge_point_name']}: {item['suggestion']}" for item in remediation] or ["暂无明显薄弱项。"])
    save_document(document, output_path)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="生成 Stage E 正式学情包。")
    parser.add_argument("--responses", required=True, type=Path, help="StudentResponse[] JSON 文件")
    parser.add_argument("--knowledge-points", required=True, type=Path, help="KnowledgePoint[] JSON 文件")
    parser.add_argument("--questions", type=Path, default=None, help="可选 Question[] JSON 文件")
    parser.add_argument("--research", type=Path, default=None, help="ResearchDossier JSON 资料包")
    parser.add_argument("--chart-dir", type=Path, default=None, help="可选图表输出目录")
    parser.add_argument("--online", action="store_true", help="允许调用远程诊断")
    parser.add_argument("--output-dir", required=True, type=Path, help="输出学情包目录")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    try:
        research = ResearchDossier.model_validate_json(args.research.read_text(encoding="utf-8")) if args.research else None
        package = build_learning_package(
            responses_json=args.responses.read_text(encoding="utf-8"),
            knowledge_points_json=args.knowledge_points.read_text(encoding="utf-8"),
            questions_json=args.questions.read_text(encoding="utf-8") if args.questions else None,
            output_dir=args.output_dir,
            research=research,
            offline=not args.online,
            chart_dir=args.chart_dir,
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
