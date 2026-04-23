import httpx

from shared.api_client import TeacherSkillsAPIClient
from shared.schemas.exam import ExamPaper, ExamSection
from shared.schemas.question import DifficultyLevel, Question, QuestionType
from skills.gaijuan.scripts.grade_answers import AnswerSubmission, grade_submissions
from skills.gaijuan.scripts.score_report import generate_score_report


def test_grade_submissions_scores_objective_questions_locally() -> None:
    exam = _build_exam([_choice_question()])
    submissions = [AnswerSubmission(student_id="stu_001", question_id="q_choice", answer="A")]

    responses = grade_submissions(exam=exam, submissions=submissions, offline=True)

    assert responses[0].score == 3
    assert responses[0].feedback == "答案正确"


def test_grade_submissions_marks_subjective_as_pending_when_offline() -> None:
    exam = _build_exam([_subjective_question()])
    submissions = [AnswerSubmission(student_id="stu_001", question_id="q_subjective", answer="我的解答")]

    responses = grade_submissions(exam=exam, submissions=submissions, offline=True)

    assert responses[0].score is None
    assert "待评分" in (responses[0].feedback or "")


def test_grade_submissions_uses_remote_api_for_subjective_questions() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, json={"score": 4.0, "feedback": "过程较完整。"})
    )
    exam = _build_exam([_subjective_question()])
    submissions = [AnswerSubmission(student_id="stu_001", question_id="q_subjective", answer="我的解答")]

    with TeacherSkillsAPIClient(token="token", base_url="https://api.example.com", transport=transport) as client:
        responses = grade_submissions(
            exam=exam,
            submissions=submissions,
            rubric="按步骤给分",
            api_client=client,
        )

    assert responses[0].score == 4.0
    assert responses[0].feedback == "过程较完整。"


def test_generate_score_report_includes_pending_count() -> None:
    exam = _build_exam([_choice_question(), _subjective_question()])
    responses = grade_submissions(
        exam=exam,
        submissions=[
            AnswerSubmission(student_id="stu_001", question_id="q_choice", answer="A"),
            AnswerSubmission(student_id="stu_001", question_id="q_subjective", answer="我的解答"),
        ],
        offline=True,
    )

    report = generate_score_report(exam, responses)

    assert "# 数学单元测验 批改报告" in report
    assert "- 待评分题数：1" in report
    assert "| q_subjective | 解答题 | 待评分 | 8 |" in report


def _build_exam(questions: list[Question]) -> ExamPaper:
    return ExamPaper(
        id="exam_1",
        title="数学单元测验",
        subject="数学",
        grade="九年级",
        total_score=sum(question.score for question in questions),
        duration_minutes=45,
        sections=[
            ExamSection(
                title="一、试题",
                question_type=questions[0].question_type,
                questions=questions,
                section_score=sum(question.score for question in questions),
            )
        ],
    )


def _choice_question() -> Question:
    return Question(
        id="q_choice",
        content="下列说法正确的是哪一项？",
        subject="数学",
        question_type=QuestionType.CHOICE,
        difficulty=DifficultyLevel.EASY,
        knowledge_points=["math_quad_graph"],
        answer="A",
        options=["A. 正确", "B. 错误"],
        score=3,
    )


def _subjective_question() -> Question:
    return Question(
        id="q_subjective",
        content="请写出解题过程。",
        subject="数学",
        question_type=QuestionType.SHORT_ANSWER,
        difficulty=DifficultyLevel.MEDIUM,
        knowledge_points=["math_quad_graph"],
        answer="参考答案",
        score=8,
    )
