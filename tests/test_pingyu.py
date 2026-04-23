import json
from pathlib import Path

from shared.schemas.comment import StudentComment
from skills.pingyu.scripts.generate_comment import (
    build_student_profile,
    generate_student_comments,
    load_observations,
    main,
    render_markdown,
)


def test_build_student_profile_merges_mastery_and_observation() -> None:
    from shared.schemas.knowledge import KnowledgeLevel, KnowledgePoint
    from shared.schemas.student import KnowledgeMastery, StudentResponse

    observation = load_observations(Path("examples/sample_data/sample_teacher_observations.json").read_text(encoding="utf-8"))[0]
    profile = build_student_profile(
        student_id="stu_001",
        responses=[
            StudentResponse(student_id="stu_001", question_id="q1", answer="A", score=4, max_score=5, feedback=""),
        ],
        mastery=[
            KnowledgeMastery(student_id="stu_001", knowledge_point_id="kp1", mastery_level=0.9, confidence=0.8),
            KnowledgeMastery(student_id="stu_001", knowledge_point_id="kp2", mastery_level=0.4, confidence=0.8),
        ],
        knowledge_lookup={"kp1": "图像性质", "kp2": "最值应用"},
        observation=observation,
    )

    assert profile.student_name == "林然"
    assert "图像性质" in profile.strengths
    assert profile.improvements


def test_generate_student_comments_returns_distinct_comments() -> None:
    comments = generate_student_comments(
        responses=_responses(),
        mastery=_mastery(),
        knowledge_points=_knowledge_points(),
        observations=_observations(),
        term="期末",
    )

    assert len(comments) == 2
    assert comments[0].comment != comments[1].comment
    assert any(comment.student_name for comment in comments)


def test_render_markdown_contains_student_sections() -> None:
    comments = generate_student_comments(
        responses=_responses(),
        mastery=_mastery(),
        knowledge_points=_knowledge_points(),
        observations=_observations(),
    )

    markdown = render_markdown(comments, term="期末")

    assert "# 期末学生评语" in markdown
    assert "## 林然（stu_001）" in markdown
    assert "## 周宁（stu_002）" in markdown


def test_main_writes_json_and_markdown(tmp_path: Path) -> None:
    json_path = tmp_path / "comments.json"
    markdown_path = tmp_path / "comments.md"

    exit_code = main(
        [
            "--responses",
            "examples/sample_data/sample_student_responses.json",
            "--mastery",
            "examples/sample_data/sample_knowledge_mastery.json",
            "--knowledge-points",
            "examples/sample_data/math_knowledge_points.json",
            "--observations",
            "examples/sample_data/sample_teacher_observations.json",
            "--output-json",
            str(json_path),
            "--output-markdown",
            str(markdown_path),
        ]
    )

    assert exit_code == 0
    comments = [StudentComment.model_validate(item) for item in json.loads(json_path.read_text(encoding="utf-8"))]
    markdown = markdown_path.read_text(encoding="utf-8")

    assert len(comments) >= 2
    assert "学生评语" in markdown


def _responses():
    from shared.schemas.student import StudentResponse

    return [
        StudentResponse(student_id="stu_001", question_id="q1", answer="A", score=5, max_score=5, feedback=""),
        StudentResponse(student_id="stu_001", question_id="q2", answer="B", score=4, max_score=5, feedback=""),
        StudentResponse(student_id="stu_002", question_id="q1", answer="A", score=2, max_score=5, feedback=""),
    ]


def _mastery():
    from shared.schemas.student import KnowledgeMastery

    return [
        KnowledgeMastery(student_id="stu_001", knowledge_point_id="kp1", mastery_level=0.92, confidence=0.8),
        KnowledgeMastery(student_id="stu_001", knowledge_point_id="kp2", mastery_level=0.58, confidence=0.8),
        KnowledgeMastery(student_id="stu_002", knowledge_point_id="kp1", mastery_level=0.55, confidence=0.8),
        KnowledgeMastery(student_id="stu_002", knowledge_point_id="kp2", mastery_level=0.48, confidence=0.8),
    ]


def _knowledge_points():
    from shared.schemas.knowledge import KnowledgeLevel, KnowledgePoint

    return [
        KnowledgePoint(id="kp1", name="图像性质", subject="数学", grade="九年级", cognitive_level=KnowledgeLevel.UNDERSTAND),
        KnowledgePoint(id="kp2", name="最值应用", subject="数学", grade="九年级", cognitive_level=KnowledgeLevel.APPLY),
    ]


def _observations():
    return load_observations(Path("examples/sample_data/sample_teacher_observations.json").read_text(encoding="utf-8"))
