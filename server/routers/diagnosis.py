from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

try:
    from server.auth import require_bearer_token
    from server.models.irt_model import estimate_mastery_by_average
    from server.models.ncdm_model import estimate_mastery_multidim
except ModuleNotFoundError:  # pragma: no cover - for `cd server && uvicorn app:app`
    from auth import require_bearer_token
    from models.irt_model import estimate_mastery_by_average
    from models.ncdm_model import estimate_mastery_multidim


router = APIRouter(prefix="/api", tags=["diagnosis"])


class DiagnosisRequest(BaseModel):
    responses: list[dict]
    knowledge_points: list[dict]
    question_knowledge_map: dict[str, list[str]] = Field(default_factory=dict)
    model: str = "irt"


class DiagnosisResponse(BaseModel):
    mastery: list[dict]


@router.post("/diagnosis", response_model=DiagnosisResponse, dependencies=[Depends(require_bearer_token)])
def diagnose_learning(payload: DiagnosisRequest) -> DiagnosisResponse:
    knowledge_ids = [item["id"] for item in payload.knowledge_points if "id" in item]
    if payload.model == "ncdm":
        mastery = estimate_mastery_multidim(
            responses=payload.responses,
            knowledge_ids=knowledge_ids,
            question_knowledge_map=payload.question_knowledge_map,
        )
    else:
        mastery = estimate_mastery_by_average(
            responses=payload.responses,
            knowledge_ids=knowledge_ids,
            question_knowledge_map=payload.question_knowledge_map,
        )
    return DiagnosisResponse(mastery=mastery)
