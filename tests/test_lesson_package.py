from pathlib import Path
from zipfile import ZipFile

from shared.schemas.lesson import LessonContext, LessonPackage, LessonPlan
from skills.beike.scripts.build_lesson_package import main


def test_build_lesson_package_outputs_professional_files(tmp_path: Path) -> None:
    output_dir = tmp_path / "lesson_package"

    exit_code = main(
        [
            "--research",
            "examples/sample_data/research_dossier_math_beike.json",
            "--output-dir",
            str(output_dir),
        ]
    )

    assert exit_code == 0
    expected_files = [
        "备课分析.docx",
        "教学设计.docx",
        "课堂活动单.docx",
        "配套练习.docx",
        "lesson_context.json",
        "lesson_plan.json",
        "package.json",
        "sources.md",
    ]
    assert all((output_dir / filename).exists() for filename in expected_files)

    context = LessonContext.model_validate_json((output_dir / "lesson_context.json").read_text(encoding="utf-8"))
    plan = LessonPlan.model_validate_json((output_dir / "lesson_plan.json").read_text(encoding="utf-8"))
    package = LessonPackage.model_validate_json((output_dir / "package.json").read_text(encoding="utf-8"))

    assert context.title == "二次函数的图像与性质"
    assert context.source_ids
    assert context.teacher_review_notes
    assert plan.title == context.title
    assert all(package.checks.values())
    assert "来源清单" in (output_dir / "sources.md").read_text(encoding="utf-8")

    with ZipFile(output_dir / "教学设计.docx") as docx:
        styles_xml = docx.read("word/styles.xml").decode("utf-8")
        document_xml = docx.read("word/document.xml").decode("utf-8")
    assert 'w:eastAsia="宋体"' in styles_xml
    assert 'w:eastAsia="宋体"' in document_xml
