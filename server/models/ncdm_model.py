from __future__ import annotations


def estimate_mastery_multidim(
    *,
    responses: list[dict],
    knowledge_ids: list[str],
    question_knowledge_map: dict[str, list[str]],
) -> list[dict]:
    # Phase 2 MVP: 先复用平均得分估计，保留 NCDM 接口位置，后续再替换为真实模型。
    try:
        from server.models.irt_model import estimate_mastery_by_average
    except ModuleNotFoundError:  # pragma: no cover - for `cd server && uvicorn app:app`
        from models.irt_model import estimate_mastery_by_average

    return estimate_mastery_by_average(
        responses=responses,
        knowledge_ids=knowledge_ids,
        question_knowledge_map=question_knowledge_map,
    )
