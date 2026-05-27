import pytest
from pydantic import TypeAdapter

from shared.schemas.question import DifficultyLevel, Question, QuestionType
from skills.chuti.scripts.gen_question import QuestionRequest, generate_questions, main, questions_to_json
from skills.chuti.scripts.validate_question import validate_questions


def test_generate_math_choice_questions() -> None:
    request = QuestionRequest(
        subject="数学",
        knowledge_points=["二次函数的图像与性质"],
        question_type=QuestionType.CHOICE,
        difficulty=DifficultyLevel.MEDIUM,
        count=2,
        grade="九年级",
        score=3,
    )

    questions = generate_questions(request)

    assert len(questions) == 2
    assert all(question.subject == "数学" for question in questions)
    assert all(question.options for question in questions)
    assert validate_questions(questions) == []


def test_questions_to_json_round_trip() -> None:
    request = QuestionRequest(
        subject="英语",
        knowledge_points=["be interested in"],
        question_type=QuestionType.CHOICE,
        difficulty=DifficultyLevel.EASY,
    )

    raw_json = questions_to_json(generate_questions(request))
    parsed = TypeAdapter(list[Question]).validate_json(raw_json)

    assert len(parsed) == 1
    assert parsed[0].question_type == QuestionType.CHOICE


def test_validate_questions_rejects_choice_without_options() -> None:
    question = Question(
        id="invalid_choice",
        content="下列说法正确的是哪一项？",
        subject="数学",
        question_type=QuestionType.CHOICE,
        difficulty=DifficultyLevel.EASY,
        knowledge_points=["math_quad_graph"],
        answer="A",
        score=3,
    )

    errors = validate_questions([question])

    assert errors == ["invalid_choice: 选择题至少需要 2 个选项"]


def test_generate_questions_rejects_unknown_subject() -> None:
    request = QuestionRequest(
        subject="物理",
        knowledge_points=["力"],
        question_type=QuestionType.CHOICE,
        difficulty=DifficultyLevel.EASY,
    )

    with pytest.raises(ValueError, match="不支持的学科"):
        generate_questions(request)


def test_main_generates_questions_from_research_and_profile(tmp_path) -> None:
    output_dir = tmp_path / "question_package"

    exit_code = main(
        [
            "--research-dossier",
            "examples/sample_data/research_dossier_math_exam.json",
            "--profile",
            "skills/zujuan/assets/profiles/math_junior_standard.json",
            "--output-dir",
            str(output_dir),
        ]
    )

    assert exit_code == 0
    questions = TypeAdapter(list[Question]).validate_json((output_dir / "questions.json").read_text(encoding="utf-8"))
    assert len(questions) == 1
    assert questions[0].subject == "数学"
    assert questions[0].question_type == QuestionType.CHOICE
    assert questions[0].metadata["source_ids"]
    assert questions[0].metadata["exam_style_id"] == "math_junior_standard"
    assert questions[0].metadata["difficulty_reason"]
    assert (output_dir / "sources.md").exists()
    assert (output_dir / "package.json").exists()
