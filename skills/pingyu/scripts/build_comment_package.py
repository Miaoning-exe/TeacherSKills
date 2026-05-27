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
from shared.tools.sources import render_sources_markdown
from skills.pingyu.scripts.generate_comment import (
    comments_to_json,
    export_docx,
    generate_student_comments,
    load_knowledge_points,
    load_mastery,
    load_observations,
    load_responses,
    render_markdown,
)


def build_comment_package(
    *,
    responses_json: str,
    mastery_json: str,
    knowledge_points_json: str,
    output_dir: Path,
    observations_json: str | None = None,
    research: ResearchDossier | None = None,
    term: str = "期末",
) -> dict[str, object]:
    responses = load_responses(responses_json)
    mastery = load_mastery(mastery_json)
    knowledge_points = load_knowledge_points(knowledge_points_json)
    observations = load_observations(observations_json) if observations_json else None
    comments = generate_student_comments(
        responses=responses,
        mastery=mastery,
        knowledge_points=knowledge_points,
        observations=observations,
        term=term,
    )
    markdown = render_markdown(comments, term=term)
    review_notes = _build_review_notes(comments, research)

    output_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "comments_json": "student_comments.json",
        "comments_md": "student_comments.md",
        "comments_docx": "学生评语.docx",
        "review_notes_json": "评语复核清单.json",
        "package_json": "package.json",
        "sources_md": "sources.md" if research else None,
    }
    (output_dir / files["comments_json"]).write_text(comments_to_json(comments) + "\n", encoding="utf-8")
    (output_dir / files["comments_md"]).write_text(markdown, encoding="utf-8")
    (output_dir / files["review_notes_json"]).write_text(
        TypeAdapter(list[dict[str, object]]).dump_json(review_notes, indent=2).decode("utf-8") + "\n",
        encoding="utf-8",
    )
    export_docx(comments, output_dir / files["comments_docx"], term=term)
    if research:
        (output_dir / "sources.md").write_text(render_sources_markdown(research), encoding="utf-8")

    package = {
        "id": f"comment_package_{uuid.uuid4().hex[:12]}",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "output_dir": str(output_dir),
        "files": files,
        "checks": {
            "comments_generated": bool(comments),
            "review_notes_generated": (output_dir / files["review_notes_json"]).exists(),
            "docx_generated": (output_dir / files["comments_docx"]).exists(),
            "sources_generated": bool(not research or (output_dir / "sources.md").exists()),
        },
        "source_ids": [source.id for source in research.sources] if research else [],
    }
    (output_dir / files["package_json"]).write_text(
        TypeAdapter(dict[str, object]).dump_json(package, indent=2).decode("utf-8") + "\n",
        encoding="utf-8",
    )
    return package


def _build_review_notes(comments, research: ResearchDossier | None) -> list[dict[str, object]]:
    shared_notes = list(research.teacher_review_notes) if research else []
    return [
        {
            "student_id": comment.student_id,
            "student_name": comment.student_name,
            "review_points": shared_notes
            + [
                "请教师核对评语是否符合学生真实课堂表现。",
                "涉及学情数据的表述应与最新批改和观察记录一致。",
            ],
        }
        for comment in comments
    ]


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="生成 Stage E 正式评语包。")
    parser.add_argument("--responses", required=True, type=Path, help="StudentResponse[] JSON 文件")
    parser.add_argument("--mastery", required=True, type=Path, help="KnowledgeMastery[] JSON 文件")
    parser.add_argument("--knowledge-points", required=True, type=Path, help="KnowledgePoint[] JSON 文件")
    parser.add_argument("--observations", type=Path, default=None, help="TeacherObservation[] JSON 文件")
    parser.add_argument("--research", type=Path, default=None, help="ResearchDossier JSON 资料包")
    parser.add_argument("--term", default="期末", help="评语场景")
    parser.add_argument("--output-dir", required=True, type=Path, help="输出评语包目录")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    try:
        research = ResearchDossier.model_validate_json(args.research.read_text(encoding="utf-8")) if args.research else None
        package = build_comment_package(
            responses_json=args.responses.read_text(encoding="utf-8"),
            mastery_json=args.mastery.read_text(encoding="utf-8"),
            knowledge_points_json=args.knowledge_points.read_text(encoding="utf-8"),
            observations_json=args.observations.read_text(encoding="utf-8") if args.observations else None,
            output_dir=args.output_dir,
            research=research,
            term=args.term,
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
