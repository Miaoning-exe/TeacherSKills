import pytest

from shared.schemas.question import DifficultyLevel, Question, QuestionType
from skills.zujuan.scripts.assemble_exam import ExamConstraints, SectionConstraint, assemble_exam
from skills.zujuan.scripts.export_exam import export_markdown


def test_assemble_exam_groups_questions_by_section() -> None:
    questions = [
        _question("q1", QuestionType.CHOICE, DifficultyLevel.EASY, ["kp1"]),
        _question("q2", QuestionType.CHOICE, DifficultyLevel.MEDIUM, ["kp2"]),
        _question("q3", QuestionType.FILL_BLANK, DifficultyLevel.EASY, ["kp1"]),
    ]
    constraints = ExamConstraints(
        title="数学单元练习",
        subject="数学",
        grade="九年级",
        duration_minutes=45,
        sections=[
            SectionConstraint(question_type=QuestionType.CHOICE, count=2, score_per_question=3),
            SectionConstraint(question_type=QuestionType.FILL_BLANK, count=1, score_per_question=2),
        ],
        required_knowledge_points=["kp1", "kp2"],
        difficulty_distribution={DifficultyLevel.EASY: 0.7, DifficultyLevel.MEDIUM: 0.3},
    )

    exam = assemble_exam(questions, constraints)

    assert exam.total_score == 8
    assert [section.question_type for section in exam.sections] == [
        QuestionType.CHOICE,
        QuestionType.FILL_BLANK,
    ]
    assert [question.score for section in exam.sections for question in section.questions] == [3, 3, 2]


def test_export_markdown_includes_answers_when_requested() -> None:
    questions = [_question("q1", QuestionType.CHOICE, DifficultyLevel.EASY, ["kp1"])]
    constraints = ExamConstraints(
        title="数学小测",
        subject="数学",
        grade="七年级",
        duration_minutes=20,
        sections=[SectionConstraint(question_type=QuestionType.CHOICE, count=1)],
    )

    markdown = export_markdown(assemble_exam(questions, constraints), include_answers=True)

    assert "# 数学小测" in markdown
    assert "## 参考答案" in markdown
    assert "A. 正确选项" in markdown


def test_assemble_exam_raises_when_questions_are_insufficient() -> None:
    questions = [_question("q1", QuestionType.CHOICE, DifficultyLevel.EASY, ["kp1"])]
    constraints = ExamConstraints(
        title="数学小测",
        subject="数学",
        grade="七年级",
        duration_minutes=20,
        sections=[SectionConstraint(question_type=QuestionType.CHOICE, count=2)],
    )

    with pytest.raises(ValueError, match="可用题目不足"):
        assemble_exam(questions, constraints)


def test_assemble_exam_raises_when_required_knowledge_point_is_missing() -> None:
    questions = [_question("q1", QuestionType.CHOICE, DifficultyLevel.EASY, ["kp1"])]
    constraints = ExamConstraints(
        title="数学小测",
        subject="数学",
        grade="七年级",
        duration_minutes=20,
        sections=[SectionConstraint(question_type=QuestionType.CHOICE, count=1)],
        required_knowledge_points=["kp2"],
    )

    with pytest.raises(ValueError, match="知识点覆盖不足"):
        assemble_exam(questions, constraints)


def _question(
    question_id: str,
    question_type: QuestionType,
    difficulty: DifficultyLevel,
    knowledge_points: list[str],
) -> Question:
    return Question(
        id=question_id,
        content=f"{question_id} 题干",
        subject="数学",
        question_type=question_type,
        difficulty=difficulty,
        knowledge_points=knowledge_points,
        answer="A",
        explanation="解析",
        options=["A. 正确选项", "B. 干扰项"] if question_type == QuestionType.CHOICE else None,
        score=1,
    )
