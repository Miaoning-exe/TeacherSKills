from __future__ import annotations

from collections import defaultdict


def estimate_mastery_by_average(
    *,
    responses: list[dict],
    knowledge_ids: list[str],
    question_knowledge_map: dict[str, list[str]],
) -> list[dict]:
    grouped_scores: dict[tuple[str, str], list[float]] = defaultdict(list)
    students = sorted({response["student_id"] for response in responses})

    for response in responses:
        if response.get("score") is None or response.get("max_score", 0) <= 0:
            continue
        normalized = max(0.0, min(float(response["score"]) / float(response["max_score"]), 1.0))
        for knowledge_id in question_knowledge_map.get(response["question_id"], []):
            grouped_scores[(response["student_id"], knowledge_id)].append(normalized)

    mastery = []
    for student_id in students:
        for knowledge_id in knowledge_ids:
            values = grouped_scores.get((student_id, knowledge_id), [])
            if values:
                mastery_level = sum(values) / len(values)
                confidence = min(1.0, 0.5 + 0.2 * len(values))
            else:
                mastery_level = 0.5
                confidence = 0.1
            mastery.append(
                {
                    "student_id": student_id,
                    "knowledge_point_id": knowledge_id,
                    "mastery_level": round(mastery_level, 3),
                    "confidence": round(confidence, 3),
                }
            )
    return mastery
