import os

from fastapi.testclient import TestClient

from server.app import app


def test_health_endpoint_returns_ok() -> None:
    client = TestClient(app)

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_grade_endpoint_requires_token() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/grade",
        json={
            "question": {"answer": "A", "question_type": "选择题"},
            "student_answer": "A",
            "max_score": 3,
        },
    )

    assert response.status_code == 401


def test_grade_endpoint_scores_objective_question() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/grade",
        headers=_auth_headers(),
        json={
            "question": {"answer": "A", "question_type": "选择题"},
            "student_answer": "A",
            "max_score": 3,
        },
    )

    assert response.status_code == 200
    assert response.json()["score"] == 3


def test_diagnosis_endpoint_returns_mastery() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/diagnosis",
        headers=_auth_headers(),
        json={
            "responses": [
                {
                    "student_id": "stu_001",
                    "question_id": "q1",
                    "answer": "A",
                    "score": 3,
                    "max_score": 3,
                }
            ],
            "knowledge_points": [
                {"id": "math_quad_graph", "name": "二次函数的图像与性质"},
                {"id": "math_quad_vertex", "name": "二次函数顶点坐标"},
            ],
            "question_knowledge_map": {"q1": ["math_quad_graph"]},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert "mastery" in payload
    assert len(payload["mastery"]) == 2


def _auth_headers() -> dict[str, str]:
    os.environ["TEACHERSKILLS_API_SERVER_TOKEN"] = "dev-token"
    return {"Authorization": "Bearer dev-token"}
