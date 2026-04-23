import pytest
from pydantic import TypeAdapter

from shared.schemas.question import DifficultyLevel, Question, QuestionType
from skills.chuti.scripts.gen_question import QuestionRequest, generate_questions, questions_to_json
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
