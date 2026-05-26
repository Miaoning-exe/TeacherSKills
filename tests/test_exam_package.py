from pathlib import Path
from zipfile import ZipFile

from shared.schemas.exam import AnswerKey, AnswerSheetSpec, ExamBlueprint, ExamPackage, ScoringRubric
from skills.zujuan.scripts.build_exam_package import main


def test_build_exam_package_outputs_consistent_files(tmp_path: Path) -> None:
    output_dir = tmp_path / "exam_package"

    exit_code = main(
        [
            "--research",
            "examples/sample_data/research_dossier_math_exam.json",
            "--questions",
            "examples/sample_data/sample_questions.json",
            "--profile",
            "skills/zujuan/assets/profiles/math_junior_standard.json",
            "--output-dir",
            str(output_dir),
        ]
    )

    assert exit_code == 0
    expected_files = [
        "试卷.docx",
        "答题卡.docx",
        "参考答案.docx",
        "评分细则.docx",
        "exam.json",
        "blueprint.json",
        "answer_sheet.json",
        "answer_key.json",
        "scoring_rubric.json",
        "package.json",
        "sources.md",
    ]
    assert all((output_dir / filename).exists() for filename in expected_files)

    blueprint = ExamBlueprint.model_validate_json((output_dir / "blueprint.json").read_text(encoding="utf-8"))
    answer_sheet = AnswerSheetSpec.model_validate_json((output_dir / "answer_sheet.json").read_text(encoding="utf-8"))
    answer_key = AnswerKey.model_validate_json((output_dir / "answer_key.json").read_text(encoding="utf-8"))
    scoring_rubric = ScoringRubric.model_validate_json((output_dir / "scoring_rubric.json").read_text(encoding="utf-8"))
    package = ExamPackage.model_validate_json((output_dir / "package.json").read_text(encoding="utf-8"))

    question_numbers = [1, 2, 3]
    assert blueprint.total_score == 17
    assert [item.question_number for item in answer_key.items] == question_numbers
    assert [item.question_number for item in scoring_rubric.items] == question_numbers
    assert [number for section in answer_sheet.sections for number in section.question_numbers] == question_numbers
    assert all(item.answer for item in answer_key.items)
    assert all(package.checks.values())
    assert package.files["package_json"] == "package.json"
    assert "来源清单" in (output_dir / "sources.md").read_text(encoding="utf-8")

    with ZipFile(output_dir / "试卷.docx") as docx:
        styles_xml = docx.read("word/styles.xml").decode("utf-8")
        document_xml = docx.read("word/document.xml").decode("utf-8")
    assert 'w:eastAsia="宋体"' in styles_xml
    assert 'w:eastAsia="宋体"' in document_xml
