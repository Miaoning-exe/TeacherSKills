from __future__ import annotations

import argparse
import logging
import sys
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pydantic import TypeAdapter, ValidationError

from shared.api_client import AuthenticationError, TeacherSkillsAPIClient, TeacherSkillsAPIError
from shared.schemas.knowledge import KnowledgePoint
from shared.schemas.question import Question
from shared.schemas.student import KnowledgeMastery, StudentResponse
from skills.xueqing.scripts.visualize_mastery import generate_visualizations


LOGGER = logging.getLogger(__name__)
KNOWLEDGE_POINT_ADAPTER = TypeAdapter(list[KnowledgePoint])
QUESTION_ADAPTER = TypeAdapter(list[Question])
STUDENT_RESPONSE_ADAPTER = TypeAdapter(list[StudentResponse])
KNOWLEDGE_MASTERY_ADAPTER = TypeAdapter(list[KnowledgeMastery])


def load_responses(raw_json: str) -> list[StudentResponse]:
    return STUDENT_RESPONSE_ADAPTER.validate_json(raw_json)


def load_knowledge_points(raw_json: str) -> list[KnowledgePoint]:
    return KNOWLEDGE_POINT_ADAPTER.validate_json(raw_json)


def load_questions(raw_json: str) -> list[Question]:
    return QUESTION_ADAPTER.validate_json(raw_json)


def analyze_learning(
    *,
    responses: list[StudentResponse],
    knowledge_points: list[KnowledgePoint],
    questions: list[Question] | None = None,
    offline: bool = False,
    api_client: TeacherSkillsAPIClient | None = None,
) -> list[KnowledgeMastery]:
    question_knowledge_map = build_question_knowledge_map(questions or [])
    created_client = False
    client = api_client
    if not offline and client is None:
        try:
            client = TeacherSkillsAPIClient()
            created_client = True
        except AuthenticationError as exc:
            LOGGER.info("远程诊断不可用，改用本地启发式分析: %s", exc)
            client = None

    try:
        if client is not None:
            try:
                result = client.diagnose_learning(
                    responses=[response.model_dump(mode="json") for response in responses],
                    knowledge_points=[point.model_dump(mode="json") for point in knowledge_points],
                    question_knowledge_map=question_knowledge_map or None,
                )
                return result.mastery
            except TeacherSkillsAPIError as exc:
                LOGGER.warning("远程诊断失败，改用本地启发式分析: %s", exc)
        return estimate_mastery_locally(
            responses=responses,
            knowledge_points=knowledge_points,
            question_knowledge_map=question_knowledge_map,
        )
    finally:
        if created_client and client is not None:
            client.close()


def estimate_mastery_locally(
    *,
    responses: list[StudentResponse],
    knowledge_points: list[KnowledgePoint],
    question_knowledge_map: dict[str, list[str]] | None = None,
) -> list[KnowledgeMastery]:
    grouped_scores: dict[tuple[str, str], list[float]] = defaultdict(list)
    answered_knowledge_by_student: dict[str, set[str]] = defaultdict(set)

    for response in responses:
        if response.score is None:
            continue
        normalized = 0.0 if response.max_score <= 0 else max(0.0, min(response.score / response.max_score, 1.0))
        question_knowledge_ids = _resolve_question_knowledge_ids(
            question_id=response.question_id,
            knowledge_points=knowledge_points,
            question_knowledge_map=question_knowledge_map or {},
        )
        for knowledge_id in question_knowledge_ids:
            grouped_scores[(response.student_id, knowledge_id)].append(normalized)
            answered_knowledge_by_student[response.student_id].add(knowledge_id)

    all_student_ids = sorted({response.student_id for response in responses})
    all_knowledge_ids = [point.id for point in knowledge_points]
    mastery: list[KnowledgeMastery] = []
    for student_id in all_student_ids:
        for knowledge_id in all_knowledge_ids:
            values = grouped_scores.get((student_id, knowledge_id))
            if values:
                level = sum(values) / len(values)
                confidence = min(1.0, 0.5 + len(values) * 0.2)
            elif knowledge_id in answered_knowledge_by_student[student_id]:
                level = 0.5
                confidence = 0.2
            else:
                level = 0.5
                confidence = 0.1
            mastery.append(
                KnowledgeMastery(
                    student_id=student_id,
                    knowledge_point_id=knowledge_id,
                    mastery_level=round(level, 3),
                    confidence=round(confidence, 3),
                )
            )
    return mastery


def generate_learning_report(
    *,
    mastery: list[KnowledgeMastery],
    knowledge_points: list[KnowledgePoint],
) -> str:
    knowledge_lookup = {point.id: point for point in knowledge_points}
    lines = [
        "# 学情分析报告",
        "",
        "## 班级概览",
        "",
    ]
    class_summary = _build_class_summary(mastery, knowledge_lookup)
    lines.extend(class_summary)
    lines.extend(["", "## 学生个体分析", ""])

    grouped: dict[str, list[KnowledgeMastery]] = defaultdict(list)
    for item in mastery:
        grouped[item.student_id].append(item)
    for student_id in sorted(grouped):
        lines.extend(_render_student_summary(student_id, grouped[student_id], knowledge_lookup))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def mastery_to_json(mastery: list[KnowledgeMastery]) -> str:
    return KNOWLEDGE_MASTERY_ADAPTER.dump_json(mastery, indent=2).decode("utf-8")


def _build_class_summary(
    mastery: list[KnowledgeMastery],
    knowledge_lookup: dict[str, KnowledgePoint],
) -> list[str]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for item in mastery:
        grouped[item.knowledge_point_id].append(item.mastery_level)

    lines = [
        "| 知识点 | 平均掌握度 | 建议 |",
        "|--------|------------|------|",
    ]
    for knowledge_id in sorted(grouped):
        average = sum(grouped[knowledge_id]) / len(grouped[knowledge_id])
        point = knowledge_lookup.get(knowledge_id)
        point_name = point.name if point else knowledge_id
        lines.append(f"| {point_name} | {average:.2f} | {_class_recommendation(average)} |")
    return lines


def _render_student_summary(
    student_id: str,
    mastery: list[KnowledgeMastery],
    knowledge_lookup: dict[str, KnowledgePoint],
) -> list[str]:
    sorted_items = sorted(mastery, key=lambda item: item.mastery_level)
    lines = [f"### 学生 {student_id}", ""]
    if not sorted_items:
        lines.append("- 暂无可分析数据")
        return lines
    weak_items = [item for item in sorted_items if item.mastery_level < 0.7][:3]
    if not weak_items:
        lines.append("- 暂未发现明显薄弱知识点，可继续做综合巩固。")
        return lines
    for item in weak_items:
        point = knowledge_lookup.get(item.knowledge_point_id)
        point_name = point.name if point else item.knowledge_point_id
        lines.append(
            f"- 薄弱知识点：{point_name}（掌握度 {item.mastery_level:.2f}，建议：{_student_recommendation(item.mastery_level, point_name)}）"
        )
    return lines


def _class_recommendation(average: float) -> str:
    if average < 0.4:
        return "建议整班重讲并补充基础练习"
    if average < 0.7:
        return "建议分层复习并增加针对性练习"
    return "整体较稳，可加入综合应用题巩固"


def _student_recommendation(level: float, knowledge_name: str) -> str:
    if level < 0.4:
        return f"优先回顾 {knowledge_name} 的基础概念和例题"
    if level < 0.7:
        return f"建议增加 {knowledge_name} 的变式训练"
    return f"可用 {knowledge_name} 的综合题继续巩固"


def build_question_knowledge_map(questions: list[Question]) -> dict[str, list[str]]:
    return {question.id: question.knowledge_points for question in questions}


def _resolve_question_knowledge_ids(
    *,
    question_id: str,
    knowledge_points: list[KnowledgePoint],
    question_knowledge_map: dict[str, list[str]],
) -> list[str]:
    mapped_ids = question_knowledge_map.get(question_id)
    if mapped_ids:
        return mapped_ids
    # 没有题目映射时退化为保守估计：不臆造知识点关联。
    return []


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="根据 StudentResponse[] 生成学情分析报告和 KnowledgeMastery[]。")
    parser.add_argument("--responses", required=True, type=Path, help="StudentResponse[] JSON 文件")
    parser.add_argument("--knowledge-points", required=True, type=Path, help="KnowledgePoint[] JSON 文件")
    parser.add_argument("--questions", type=Path, default=None, help="可选 Question[] JSON 文件，用于题目到知识点映射")
    parser.add_argument("--output-mastery", required=True, type=Path, help="输出 KnowledgeMastery[] JSON 文件")
    parser.add_argument("--output-report", required=True, type=Path, help="输出 Markdown 学情报告")
    parser.add_argument("--chart-dir", type=Path, default=None, help="可选图表输出目录")
    parser.add_argument("--offline", action="store_true", help="强制离线，使用本地启发式分析")
    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    try:
        responses = load_responses(args.responses.read_text(encoding="utf-8"))
        knowledge_points = load_knowledge_points(args.knowledge_points.read_text(encoding="utf-8"))
        questions = load_questions(args.questions.read_text(encoding="utf-8")) if args.questions else None
        mastery = analyze_learning(
            responses=responses,
            knowledge_points=knowledge_points,
            questions=questions,
            offline=args.offline,
        )
        report = generate_learning_report(mastery=mastery, knowledge_points=knowledge_points)
    except FileNotFoundError as exc:
        sys.stderr.write(f"输入文件不存在: {exc.filename}\n")
        return 1
    except ValidationError as exc:
        sys.stderr.write(f"{exc}\n")
        return 1

    args.output_mastery.parent.mkdir(parents=True, exist_ok=True)
    args.output_report.parent.mkdir(parents=True, exist_ok=True)
    args.output_mastery.write_text(mastery_to_json(mastery) + "\n", encoding="utf-8")
    args.output_report.write_text(report, encoding="utf-8")

    if args.chart_dir is not None:
        try:
            generate_visualizations(
                mastery=mastery,
                knowledge_points=knowledge_points,
                output_dir=args.chart_dir,
            )
        except RuntimeError as exc:
            LOGGER.warning("跳过图表生成: %s", exc)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
