from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pydantic import BaseModel, ValidationError


class CurriculumEntry(BaseModel):
    title: str
    subject: str
    grade: str
    topic: str
    standard_id: str
    standard_summary: str
    knowledge_points: list[str]
    core_competencies: list[str]
    misconceptions: list[str]
    teaching_strategies: list[str]
    activity_suggestions: list[str]
    assessment_suggestions: list[str]
    bloom_levels: list[str]


class CurriculumAnalysis(BaseModel):
    subject: str
    grade: str
    topic: str
    keywords: list[str]
    match_note: str
    matched_entries: list[CurriculumEntry]
    key_points: list[str]
    difficult_points: list[str]


REFERENCE_DIR = Path(__file__).resolve().parent.parent / "references"
DEFAULT_CURRICULUM_PATH = REFERENCE_DIR / "curriculum_standards.md"
DEFAULT_BLOOM_PATH = REFERENCE_DIR / "bloom_taxonomy.md"


def load_curriculum_entries(markdown_text: str) -> list[CurriculumEntry]:
    entries: list[CurriculumEntry] = []
    current_title: str | None = None
    current_data: dict[str, object] | None = None
    current_list_key: str | None = None

    for raw_line in markdown_text.splitlines():
        line = raw_line.rstrip()
        if line.startswith("## "):
            if current_title and current_data:
                entries.append(CurriculumEntry(title=current_title, **current_data))
            current_title = line[3:].strip()
            current_data = {}
            current_list_key = None
            continue
        if current_data is None:
            continue
        if not line.strip():
            current_list_key = None
            continue
        if line.startswith("- "):
            content = line[2:]
            if ":" not in content:
                continue
            key, value = content.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value:
                current_data[key] = value
                current_list_key = None
            else:
                current_data[key] = []
                current_list_key = key
            continue
        if line.startswith("  - ") and current_list_key:
            items = current_data.setdefault(current_list_key, [])
            if isinstance(items, list):
                items.append(line[4:].strip())

    if current_title and current_data:
        entries.append(CurriculumEntry(title=current_title, **current_data))
    return entries


def load_bloom_descriptions(markdown_text: str) -> dict[str, str]:
    descriptions: dict[str, str] = {}
    for line in markdown_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or "层级" in stripped or "---" in stripped:
            continue
        columns = [column.strip() for column in stripped.strip("|").split("|")]
        if len(columns) >= 2:
            descriptions[columns[0]] = columns[1]
    return descriptions


def analyze_curriculum(
    *,
    subject: str,
    grade: str,
    topic: str,
    keywords: list[str],
    entries: list[CurriculumEntry],
) -> CurriculumAnalysis:
    subject_matches = [entry for entry in entries if entry.subject == subject]
    if not subject_matches:
        raise ValueError(f"未找到学科 {subject} 的课标条目")

    grade_matches = [entry for entry in subject_matches if entry.grade == grade]
    candidates = grade_matches or subject_matches
    ranked = sorted(
        candidates,
        key=lambda entry: _entry_match_score(entry=entry, topic=topic, keywords=keywords),
        reverse=True,
    )
    matched = ranked[:2]
    exact_match = any(_topic_exact_or_contains(entry.topic, topic) for entry in matched)
    match_note = (
        "已命中同年级主题课标条目，可直接据此展开备课。"
        if exact_match and grade_matches
        else "未找到完全匹配主题，已回退到相近课标条目，请教师结合教材目录复核。"
    )

    knowledge_points = _deduplicate(item for entry in matched for item in entry.knowledge_points)
    misconceptions = _deduplicate(item for entry in matched for item in entry.misconceptions)
    key_points = knowledge_points[: min(3, len(knowledge_points))]
    difficult_points = misconceptions[: min(3, len(misconceptions))]
    return CurriculumAnalysis(
        subject=subject,
        grade=grade,
        topic=topic,
        keywords=keywords,
        match_note=match_note,
        matched_entries=matched,
        key_points=key_points,
        difficult_points=difficult_points,
    )


def generate_analysis_report(
    *,
    analysis: CurriculumAnalysis,
    bloom_descriptions: dict[str, str],
) -> str:
    primary_entry = analysis.matched_entries[0]
    knowledge_points = _deduplicate(item for entry in analysis.matched_entries for item in entry.knowledge_points)
    competencies = _deduplicate(item for entry in analysis.matched_entries for item in entry.core_competencies)
    misconceptions = _deduplicate(item for entry in analysis.matched_entries for item in entry.misconceptions)
    strategies = _deduplicate(item for entry in analysis.matched_entries for item in entry.teaching_strategies)
    activities = _deduplicate(item for entry in analysis.matched_entries for item in entry.activity_suggestions)
    assessments = _deduplicate(item for entry in analysis.matched_entries for item in entry.assessment_suggestions)
    bloom_levels = _deduplicate(item for entry in analysis.matched_entries for item in entry.bloom_levels)

    lines = [
        "# 备课分析报告",
        "",
        "## 主题信息",
        "",
        f"- 学科：{analysis.subject}",
        f"- 年级：{analysis.grade}",
        f"- 主题：{analysis.topic}",
        f"- 辅助关键词：{', '.join(analysis.keywords) if analysis.keywords else '无'}",
        f"- 匹配说明：{analysis.match_note}",
        "",
        "## 课标对齐",
        "",
        f"- 主要课标条目：{primary_entry.standard_id}（{primary_entry.topic}）",
        f"- 课标摘要：{primary_entry.standard_summary}",
    ]
    if len(analysis.matched_entries) > 1:
        lines.append(
            "- 补充参考条目："
            + "；".join(f"{entry.standard_id}（{entry.topic}）" for entry in analysis.matched_entries[1:])
        )

    lines.extend(["", "## 知识点梳理", ""])
    for item in knowledge_points:
        lines.append(f"- {item}")

    lines.extend(["", "## 认知层次分析", "", "| Bloom 层级 | 说明 | 备课提示 |", "|------------|------|----------|"])
    for level in bloom_levels:
        description = bloom_descriptions.get(level, "建议教师结合学情补充说明。")
        lines.append(f"| {level} | {description} | {_bloom_teaching_hint(level)} |")

    lines.extend(["", "## 教学重点与难点", ""])
    for item in analysis.key_points:
        lines.append(f"- 教学重点：{item}")
    for item in analysis.difficult_points:
        lines.append(f"- 教学难点：{item}")

    lines.extend(["", "## 核心素养目标", ""])
    for item in competencies:
        lines.append(f"- {item}")

    lines.extend(["", "## 常见误区", ""])
    for item in misconceptions:
        lines.append(f"- {item}")

    lines.extend(["", "## 教学策略建议", ""])
    for item in strategies:
        lines.append(f"- {item}")

    lines.extend(["", "## 课堂活动建议", ""])
    for item in activities:
        lines.append(f"- {item}")

    lines.extend(["", "## 形成性评价建议", ""])
    for item in assessments:
        lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "## 后续衔接",
            "",
            "- 可将“知识点梳理”和“教学重点与难点”直接作为 `jiaoan` 的输入基础。",
            "- 可将薄弱认知层级转换为分层练习要求，交给 `chuti` 和 `zujuan` 继续生成题目。",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="根据本地课标摘录生成备课分析报告。")
    parser.add_argument("--subject", required=True, help="学科名称")
    parser.add_argument("--grade", required=True, help="年级")
    parser.add_argument("--topic", required=True, help="备课主题")
    parser.add_argument("--keywords", default="", help="逗号分隔的辅助关键词")
    parser.add_argument("--curriculum-file", type=Path, default=DEFAULT_CURRICULUM_PATH, help="课标参考文件")
    parser.add_argument("--bloom-file", type=Path, default=DEFAULT_BLOOM_PATH, help="Bloom 分类参考文件")
    parser.add_argument("--output-report", type=Path, default=None, help="输出 Markdown 报告路径")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    try:
        curriculum_text = args.curriculum_file.read_text(encoding="utf-8")
        bloom_text = args.bloom_file.read_text(encoding="utf-8")
        entries = load_curriculum_entries(curriculum_text)
        keywords = [item.strip() for item in args.keywords.split(",") if item.strip()]
        analysis = analyze_curriculum(
            subject=args.subject,
            grade=args.grade,
            topic=args.topic,
            keywords=keywords,
            entries=entries,
        )
        report = generate_analysis_report(
            analysis=analysis,
            bloom_descriptions=load_bloom_descriptions(bloom_text),
        )
    except FileNotFoundError as exc:
        sys.stderr.write(f"输入文件不存在: {exc.filename}\n")
        return 1
    except (ValidationError, ValueError) as exc:
        sys.stderr.write(f"{exc}\n")
        return 1

    if args.output_report:
        args.output_report.parent.mkdir(parents=True, exist_ok=True)
        args.output_report.write_text(report, encoding="utf-8")
    else:
        sys.stdout.write(report)
    return 0


def _entry_match_score(*, entry: CurriculumEntry, topic: str, keywords: list[str]) -> int:
    score = 0
    if entry.grade:
        score += 5
    if entry.topic == topic:
        score += 100
    elif _topic_exact_or_contains(entry.topic, topic):
        score += 60
    normalized_keywords = [keyword.casefold() for keyword in keywords]
    haystacks = [
        entry.topic.casefold(),
        entry.standard_summary.casefold(),
        " ".join(entry.knowledge_points).casefold(),
    ]
    for keyword in normalized_keywords:
        if any(keyword in haystack for haystack in haystacks):
            score += 15
    return score


def _topic_exact_or_contains(entry_topic: str, target_topic: str) -> bool:
    return entry_topic == target_topic or entry_topic in target_topic or target_topic in entry_topic


def _deduplicate(items) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def _bloom_teaching_hint(level: str) -> str:
    hints = {
        "识记": "先确保定义、规则与关键词能被准确回忆。",
        "理解": "用对比、解释和例子确认学生真正懂了。",
        "应用": "安排典型题和情境任务，检验方法迁移。",
        "分析": "引导学生说明依据、比较变化和拆解结构。",
        "评价": "要求学生基于标准给出判断并说明理由。",
        "创造": "设计开放任务，鼓励学生综合迁移与生成。",
    }
    return hints.get(level, "结合教材和学情补充具体活动。")


if __name__ == "__main__":
    raise SystemExit(main())
