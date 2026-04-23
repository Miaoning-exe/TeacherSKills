from pathlib import Path

from skills.beike.scripts.analyze_curriculum import (
    analyze_curriculum,
    generate_analysis_report,
    load_bloom_descriptions,
    load_curriculum_entries,
    main,
)


def test_load_curriculum_entries_parses_reference_file() -> None:
    entries = load_curriculum_entries(
        Path("skills/beike/references/curriculum_standards.md").read_text(encoding="utf-8")
    )

    assert len(entries) >= 6
    assert entries[0].subject == "数学"
    assert "图像的开口方向、对称轴与顶点" in entries[0].knowledge_points


def test_analyze_curriculum_prefers_exact_topic_match() -> None:
    entries = load_curriculum_entries(
        Path("skills/beike/references/curriculum_standards.md").read_text(encoding="utf-8")
    )

    analysis = analyze_curriculum(
        subject="数学",
        grade="九年级",
        topic="二次函数",
        keywords=["顶点", "图像"],
        entries=entries,
    )

    assert analysis.matched_entries[0].topic == "二次函数"
    assert any("顶点" in item for item in analysis.key_points)
    assert "已命中同年级主题课标条目" in analysis.match_note


def test_generate_analysis_report_contains_expected_sections() -> None:
    curriculum_text = Path("skills/beike/references/curriculum_standards.md").read_text(encoding="utf-8")
    bloom_text = Path("skills/beike/references/bloom_taxonomy.md").read_text(encoding="utf-8")
    entries = load_curriculum_entries(curriculum_text)

    analysis = analyze_curriculum(
        subject="英语",
        grade="七年级",
        topic="一般现在时",
        keywords=["第三人称", "频率副词"],
        entries=entries,
    )
    report = generate_analysis_report(
        analysis=analysis,
        bloom_descriptions=load_bloom_descriptions(bloom_text),
    )

    assert "# 备课分析报告" in report
    assert "## 课标对齐" in report
    assert "## 认知层次分析" in report
    assert "第三人称单数变化" in report
    assert "课堂活动建议" in report


def test_main_writes_report_file(tmp_path: Path) -> None:
    output_path = tmp_path / "beike_report.md"

    exit_code = main(
        [
            "--subject",
            "语文",
            "--grade",
            "七年级",
            "--topic",
            "记叙文阅读",
            "--keywords",
            "人物,线索",
            "--output-report",
            str(output_path),
        ]
    )

    assert exit_code == 0
    assert output_path.exists()
    report = output_path.read_text(encoding="utf-8")
    assert "记叙文阅读" in report
    assert "人物证据卡分享" in report
