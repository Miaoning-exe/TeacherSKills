from __future__ import annotations

import argparse
import sys
from pathlib import Path

from shared.schemas.research import ResearchDossier, SourceEvidence


def render_sources_markdown(dossier: ResearchDossier) -> str:
    lines = [
        "# 资料来源",
        "",
        f"- 任务：{dossier.task_type}",
        f"- 学科：{dossier.subject}",
        f"- 年级：{dossier.grade}",
        f"- 主题：{dossier.topic}",
        f"- 生成时间：{dossier.created_at}",
        f"- 检索摘要：{dossier.query_summary}",
        f"- 资料模式：{'本地模板草稿' if dossier.local_fallback else '资料增强'}",
        "",
        "## 来源清单",
        "",
    ]
    for index, source in enumerate(dossier.sources, start=1):
        lines.extend(_render_source(index, source))

    if dossier.key_findings:
        lines.extend(["", "## 来源事实", ""])
        lines.extend(f"- {item}" for item in dossier.key_findings)

    if dossier.agent_inferences:
        lines.extend(["", "## Agent 推理", ""])
        lines.extend(f"- {item}" for item in dossier.agent_inferences)

    if dossier.teacher_review_notes:
        lines.extend(["", "## 教师待复核", ""])
        lines.extend(f"- {item}" for item in dossier.teacher_review_notes)

    return "\n".join(lines).rstrip() + "\n"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="将 ResearchDossier JSON 渲染为 sources.md。")
    parser.add_argument("input", type=Path, help="ResearchDossier JSON 文件")
    parser.add_argument("--output", type=Path, default=None, help="输出 sources.md 路径，默认打印到 stdout")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    dossier = ResearchDossier.model_validate_json(args.input.read_text(encoding="utf-8"))
    markdown = render_sources_markdown(dossier)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(markdown, encoding="utf-8")
    else:
        sys.stdout.write(markdown)
    return 0


def _render_source(index: int, source: SourceEvidence) -> list[str]:
    lines = [
        f"### {index}. {source.title}",
        "",
        f"- 来源 ID：{source.id}",
        f"- 类型：{source.source_type.value}",
        f"- 可信等级：{source.credibility.value}",
        f"- 摘要：{source.summary}",
    ]
    if source.publisher:
        lines.append(f"- 发布方：{source.publisher}")
    if source.published_at:
        lines.append(f"- 发布时间：{source.published_at}")
    if source.retrieved_at:
        lines.append(f"- 检索时间：{source.retrieved_at}")
    if source.url:
        lines.append(f"- 链接：{source.url}")
    if source.citation_locations:
        lines.append("- 引用位置：" + "；".join(source.citation_locations))
    if source.review_note:
        lines.append(f"- 复核提示：{source.review_note}")
    lines.append("")
    return lines


if __name__ == "__main__":
    raise SystemExit(main())
