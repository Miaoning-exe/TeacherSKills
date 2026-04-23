from __future__ import annotations

import json
import os
from typing import Any

import httpx
from pydantic import BaseModel

from shared.schemas.question import Question
from shared.schemas.student import KnowledgeMastery


DEFAULT_API_URL = "https://api.teacherskills.dev"


class TeacherSkillsAPIError(RuntimeError):
    pass


class AuthenticationError(TeacherSkillsAPIError):
    pass


class APIRequestError(TeacherSkillsAPIError):
    pass


class APITimeoutError(TeacherSkillsAPIError):
    pass


class GradeResult(BaseModel):
    score: float
    feedback: str


class DiagnosisResult(BaseModel):
    mastery: list[KnowledgeMastery]


class TeacherSkillsAPIClient:
    def __init__(
        self,
        *,
        base_url: str | None = None,
        token: str | None = None,
        timeout: float = 10.0,
        max_retries: int = 2,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.base_url = (base_url or os.getenv("TEACHERSKILLS_API_URL") or DEFAULT_API_URL).rstrip("/")
        self.token = token or os.getenv("TEACHERSKILLS_API_TOKEN")
        if not self.token:
            raise AuthenticationError("缺少 TEACHERSKILLS_API_TOKEN，无法调用远程 API")

        self.max_retries = max(0, max_retries)
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            },
            transport=transport,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "TeacherSkillsAPIClient":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def grade_subjective_answer(
        self,
        *,
        question: Question,
        student_answer: str,
        rubric: str | None = None,
    ) -> GradeResult:
        payload = {
            "question": question.model_dump(mode="json"),
            "student_answer": student_answer,
            "max_score": question.score,
            "rubric": rubric,
        }
        data = self._request_json("POST", "/api/grade", payload)
        return GradeResult.model_validate(data)

    def diagnose_learning(
        self,
        *,
        responses: list[dict[str, Any]],
        knowledge_points: list[dict[str, Any]],
        question_knowledge_map: dict[str, list[str]] | None = None,
    ) -> DiagnosisResult:
        payload = {
            "responses": responses,
            "knowledge_points": knowledge_points,
        }
        if question_knowledge_map is not None:
            payload["question_knowledge_map"] = question_knowledge_map
        data = self._request_json("POST", "/api/diagnosis", payload)
        return DiagnosisResult.model_validate(data)

    def _request_json(self, method: str, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                response = self._client.request(method, path, json=payload)
            except httpx.TimeoutException as exc:
                last_error = exc
                if attempt == self.max_retries:
                    raise APITimeoutError(f"请求超时: {path}") from exc
                continue
            except httpx.HTTPError as exc:
                last_error = exc
                if attempt == self.max_retries:
                    raise APIRequestError(f"网络请求失败: {path}") from exc
                continue

            if response.status_code == 401:
                raise AuthenticationError("API Token 无效或已过期")
            if response.status_code >= 500:
                last_error = APIRequestError(f"服务端错误: HTTP {response.status_code}")
                if attempt == self.max_retries:
                    raise last_error
                continue
            if response.status_code >= 400:
                raise APIRequestError(_extract_error_message(response))

            try:
                return response.json()
            except json.JSONDecodeError as exc:
                raise APIRequestError(f"API 返回了无效 JSON: {path}") from exc

        if last_error is None:
            raise APIRequestError(f"请求失败: {path}")
        if isinstance(last_error, TeacherSkillsAPIError):
            raise last_error
        raise APIRequestError(f"请求失败: {path}") from last_error


def _extract_error_message(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except json.JSONDecodeError:
        return f"请求失败: HTTP {response.status_code}"
    if isinstance(payload, dict) and "detail" in payload:
        return str(payload["detail"])
    return f"请求失败: HTTP {response.status_code}"
