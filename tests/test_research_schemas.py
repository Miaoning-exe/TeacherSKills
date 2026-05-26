from pathlib import Path

from pydantic import TypeAdapter

from shared.schemas.research import CredibilityLevel, ResearchDossier, SourceEvidence, SourceType
from shared.schemas.template import TemplateProfile, TemplateSectionProfile
from shared.tools.sources import render_sources_markdown


def test_research_dossier_round_trip_and_sources_rendering() -> None:
    dossier = ResearchDossier(
        id="research_1",
        task_type="组卷",
        subject="数学",
        grade="九年级",
        topic="二次函数",
        created_at="2026-05-12",
        query_summary="检索课标、样卷和评分要求。",
        sources=[
            SourceEvidence(
                id="src_1",
                title="二次函数课标摘录",
                source_type=SourceType.CURRICULUM_STANDARD,
                summary="确认图像与性质的考查范围。",
                credibility=CredibilityLevel.HIGH,
                citation_locations=["试卷蓝图"],
            )
        ],
        key_findings=["覆盖图像、顶点和最值。"],
        agent_inferences=["建议难度约 7:2:1。"],
        teacher_review_notes=["请复核地区考试说明。"],
    )

    restored = ResearchDossier.model_validate_json(dossier.model_dump_json())
    markdown = render_sources_markdown(restored)

    assert restored.sources[0].source_type == SourceType.CURRICULUM_STANDARD
    assert "# 资料来源" in markdown
    assert "来源事实" in markdown
    assert "Agent 推理" in markdown
    assert "教师待复核" in markdown


def test_template_profile_round_trip() -> None:
    profile = TemplateProfile(
        id="math_junior_standard",
        name="初中数学标准卷",
        subject="数学",
        grade_band="初中",
        exam_type="单元测验",
        total_score=100,
        duration_minutes=90,
        sections=[
            TemplateSectionProfile(
                title="一、选择题",
                question_type="选择题",
                item_count=10,
                score_per_item=3,
                total_score=30,
                difficulty_ratio={"易": 0.7, "中": 0.2, "难": 0.1},
            )
        ],
        required_outputs=["试卷.docx", "答题卡.docx", "参考答案.docx", "评分细则.docx", "sources.md"],
        source_ids=["src_math_sample_exam_structure"],
    )

    restored = TemplateProfile.model_validate_json(profile.model_dump_json())

    assert restored.sections[0].difficulty_ratio["易"] == 0.7
    assert "sources.md" in restored.required_outputs


def test_sample_research_dossiers_can_be_parsed() -> None:
    base = Path("examples/sample_data")
    adapter = TypeAdapter(ResearchDossier)

    exam_dossier = adapter.validate_json((base / "research_dossier_math_exam.json").read_text(encoding="utf-8"))
    beike_dossier = adapter.validate_json((base / "research_dossier_math_beike.json").read_text(encoding="utf-8"))

    assert exam_dossier.task_type == "组卷"
    assert beike_dossier.task_type == "备课"
    assert len(exam_dossier.sources) >= 3
    assert all(source.summary for source in beike_dossier.sources)
