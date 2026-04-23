import httpx
import pytest

from shared.api_client import APIRequestError, AuthenticationError, TeacherSkillsAPIClient
from shared.schemas.question import DifficultyLevel, Question, QuestionType


def test_grade_subjective_answer_parses_response() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, json={"score": 4.5, "feedback": "步骤完整，结论正确。"})
    )

    with TeacherSkillsAPIClient(token="token", base_url="https://api.example.com", transport=transport) as client:
        result = client.grade_subjective_answer(
            question=_subjective_question(),
            student_answer="写出完整解题过程",
            rubric="按步骤给分",
        )

    assert result.score == 4.5
    assert "步骤完整" in result.feedback


def test_client_raises_authentication_error_for_401() -> None:
    transport = httpx.MockTransport(lambda request: httpx.Response(401, json={"detail": "unauthorized"}))

    with TeacherSkillsAPIClient(token="token", base_url="https://api.example.com", transport=transport) as client:
        with pytest.raises(AuthenticationError, match="Token"):
            client.grade_subjective_answer(
                question=_subjective_question(),
                student_answer="answer",
            )


def test_client_raises_request_error_for_400_detail() -> None:
    transport = httpx.MockTransport(lambda request: httpx.Response(400, json={"detail": "bad request"}))

    with TeacherSkillsAPIClient(token="token", base_url="https://api.example.com", transport=transport) as client:
        with pytest.raises(APIRequestError, match="bad request"):
            client.grade_subjective_answer(
                question=_subjective_question(),
                student_answer="answer",
            )


def test_diagnose_learning_parses_response() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            200,
            json={
                "mastery": [
                    {
                        "student_id": "stu_001",
                        "knowledge_point_id": "math_quad_graph",
                        "mastery_level": 0.81,
                        "confidence": 0.92,
                    }
                ]
            },
        )
    )

    with TeacherSkillsAPIClient(token="token", base_url="https://api.example.com", transport=transport) as client:
        result = client.diagnose_learning(
            responses=[{"student_id": "stu_001", "question_id": "q1", "score": 3, "max_score": 3, "answer": "A"}],
            knowledge_points=[{"id": "math_quad_graph", "name": "二次函数的图像与性质"}],
            question_knowledge_map={"q1": ["math_quad_graph"]},
        )

    assert len(result.mastery) == 1
    assert result.mastery[0].mastery_level == 0.81
def _subjective_question() -> Question:
    return Question(
        id="q_subjective_1",
        content="请写出解题过程。",
        subject="数学",
        question_type=QuestionType.SHORT_ANSWER,
        difficulty=DifficultyLevel.MEDIUM,
        knowledge_points=["math_quad_graph"],
        answer="参考答案",
        score=5,
    )
