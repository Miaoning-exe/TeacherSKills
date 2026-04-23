from __future__ import annotations

import contextlib
import io
from collections import defaultdict
from pathlib import Path

from shared.schemas.knowledge import KnowledgePoint
from shared.schemas.student import KnowledgeMastery


def generate_visualizations(
    *,
    mastery: list[KnowledgeMastery],
    knowledge_points: list[KnowledgePoint],
    output_dir: Path,
) -> list[Path]:
    plt = load_matplotlib_pyplot()

    output_dir.mkdir(parents=True, exist_ok=True)
    knowledge_name_lookup = {point.id: point.name for point in knowledge_points}

    heatmap_path = output_dir / "class_mastery_heatmap.png"
    _render_class_heatmap(
        mastery=mastery,
        knowledge_name_lookup=knowledge_name_lookup,
        output_path=heatmap_path,
        plt=plt,
    )

    chart_paths = [heatmap_path]
    grouped: dict[str, list[KnowledgeMastery]] = defaultdict(list)
    for item in mastery:
        grouped[item.student_id].append(item)
    for student_id, items in grouped.items():
        chart_path = output_dir / f"{student_id}_mastery.png"
        _render_student_bar_chart(
            student_id=student_id,
            mastery=items,
            knowledge_name_lookup=knowledge_name_lookup,
            output_path=chart_path,
            plt=plt,
        )
        chart_paths.append(chart_path)
    return chart_paths


def load_matplotlib_pyplot():
    try:
        stderr_buffer = io.StringIO()
        with contextlib.redirect_stderr(stderr_buffer):
            import matplotlib.pyplot as plt
    except Exception as exc:  # pragma: no cover - exact failure mode depends on local binary stack
        raise RuntimeError('可视化依赖 matplotlib，请执行 pip install -e ".[visualization]"') from exc
    return plt


def _render_class_heatmap(
    *,
    mastery: list[KnowledgeMastery],
    knowledge_name_lookup: dict[str, str],
    output_path: Path,
    plt,
) -> None:
    student_ids = sorted({item.student_id for item in mastery})
    knowledge_ids = sorted({item.knowledge_point_id for item in mastery})
    matrix = []
    for student_id in student_ids:
        row = []
        for knowledge_id in knowledge_ids:
            matched = next(
                (
                    item.mastery_level
                    for item in mastery
                    if item.student_id == student_id and item.knowledge_point_id == knowledge_id
                ),
                0.0,
            )
            row.append(matched)
        matrix.append(row)

    fig, ax = plt.subplots(figsize=(max(6, len(knowledge_ids) * 1.5), max(3, len(student_ids) * 0.8)))
    image = ax.imshow(matrix, cmap="YlGn", vmin=0, vmax=1)
    ax.set_xticks(range(len(knowledge_ids)))
    ax.set_xticklabels([knowledge_name_lookup.get(item, item) for item in knowledge_ids], rotation=25, ha="right")
    ax.set_yticks(range(len(student_ids)))
    ax.set_yticklabels(student_ids)
    ax.set_title("班级知识点掌握热力图")
    fig.colorbar(image, ax=ax)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def _render_student_bar_chart(
    *,
    student_id: str,
    mastery: list[KnowledgeMastery],
    knowledge_name_lookup: dict[str, str],
    output_path: Path,
    plt,
) -> None:
    sorted_items = sorted(mastery, key=lambda item: item.mastery_level)
    labels = [knowledge_name_lookup.get(item.knowledge_point_id, item.knowledge_point_id) for item in sorted_items]
    values = [item.mastery_level for item in sorted_items]

    fig, ax = plt.subplots(figsize=(max(6, len(labels) * 1.4), 4))
    ax.bar(labels, values, color="#4C7A5B")
    ax.set_ylim(0, 1)
    ax.set_title(f"{student_id} 知识点掌握度")
    ax.set_ylabel("掌握度")
    ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
