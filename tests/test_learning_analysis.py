from pathlib import Path

import httpx
import pytest

from shared.api_client import TeacherSkillsAPIClient
from shared.schemas.knowledge import KnowledgeLevel, KnowledgePoint
from shared.schemas.student import StudentResponse
from skills.xueqing.scripts.analyze_learning import (
    analyze_learning,
    build_question_knowledge_map,
    estimate_mastery_locally,
    generate_learning_report,
)
from skills.xueqing.scripts.visualize_mastery import generate_visualizations, load_matplotlib_pyplot


def test_estimate_mastery_locally_returns_entries_for_each_student_and_knowledge_point() -> None:
    mastery = estimate_mastery_locally(
        responses=_responses(),
        knowledge_points=_knowledge_points(),
        question_knowledge_map=build_question_knowledge_map(_questions()),
    )

    assert len(mastery) == 4
    assert {item.student_id for item in mastery} == {"stu_001", "stu_002"}
    assert {item.knowledge_point_id for item in mastery} == {"math_quad_graph", "math_quad_vertex"}
    assert any(item.mastery_level < 1.0 for item in mastery)


def test_analyze_learning_uses_remote_api_when_client_is_available() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            200,
            json={
                "mastery": [
                    {
                        "student_id": "stu_001",
                        "knowledge_point_id": "math_quad_graph",
                        "mastery_level": 0.9,
                        "confidence": 0.8,
                    }
                ]
            },
        )
    )

    with TeacherSkillsAPIClient(token="token", base_url="https://api.example.com", transport=transport) as client:
        mastery = analyze_learning(
            responses=_responses(),
            knowledge_points=_knowledge_points(),
            questions=_questions(),
            api_client=client,
        )

    assert len(mastery) == 1
    assert mastery[0].mastery_level == 0.9


def test_generate_learning_report_lists_class_summary_and_student_recommendations() -> None:
    mastery = estimate_mastery_locally(
        responses=_responses(),
        knowledge_points=_knowledge_points(),
        question_knowledge_map=build_question_knowledge_map(_questions()),
    )

    report = generate_learning_report(mastery=mastery, knowledge_points=_knowledge_points())

    assert "# 学情分析报告" in report
    assert "## 班级概览" in report
    assert "### 学生 stu_001" in report
    assert "薄弱知识点" in report


def test_generate_visualizations_creates_png_files(tmp_path: Path) -> None:
    try:
        load_matplotlib_pyplot()
    except RuntimeError as exc:
        pytest.skip(str(exc))

    mastery = estimate_mastery_locally(
        responses=_responses(),
        knowledge_points=_knowledge_points(),
        question_knowledge_map=build_question_knowledge_map(_questions()),
    )

    chart_paths = generate_visualizations(
        mastery=mastery,
        knowledge_points=_knowledge_points(),
        output_dir=tmp_path,
    )

    assert len(chart_paths) >= 2
    assert all(path.exists() for path in chart_paths)
    assert all(path.suffix == ".png" for path in chart_paths)


def _responses() -> list[StudentResponse]:
    return [
        StudentResponse(
            student_id="stu_001",
            question_id="sample_math_choice_01",
            answer="A",
            score=3,
            max_score=3,
            feedback="答案正确",
        ),
        StudentResponse(
            student_id="stu_001",
            question_id="sample_math_fill_01",
            answer="3",
            score=2,
            max_score=4,
            feedback="部分正确",
        ),
        StudentResponse(
            student_id="stu_002",
            question_id="sample_math_fill_01",
            answer="2",
            score=0,
            max_score=4,
            feedback="答案错误",
        ),
    ]


def _knowledge_points() -> list[KnowledgePoint]:
    return [
        KnowledgePoint(
            id="math_quad_graph",
            name="二次函数的图像与性质",
            subject="数学",
            grade="九年级",
            cognitive_level=KnowledgeLevel.UNDERSTAND,
        ),
        KnowledgePoint(
            id="math_quad_vertex",
            name="二次函数顶点坐标",
            subject="数学",
            grade="九年级",
            cognitive_level=KnowledgeLevel.APPLY,
        ),
    ]


def _questions():
    from shared.schemas.question import DifficultyLevel, Question, QuestionType

    return [
        Question(
            id="sample_math_choice_01",
            content="选择题",
            subject="数学",
            question_type=QuestionType.CHOICE,
            difficulty=DifficultyLevel.EASY,
            knowledge_points=["math_quad_graph"],
            answer="A",
            options=["A. 正确", "B. 错误"],
            score=3,
        ),
        Question(
            id="sample_math_fill_01",
            content="填空题",
            subject="数学",
            question_type=QuestionType.FILL_BLANK,
            difficulty=DifficultyLevel.MEDIUM,
            knowledge_points=["math_quad_vertex"],
            answer="3",
            score=4,
        ),
    ]
