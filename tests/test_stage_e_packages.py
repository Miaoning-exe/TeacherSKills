from pathlib import Path
from zipfile import ZipFile

from shared.schemas.exam import ExamPaper, ExamSection
from shared.schemas.question import DifficultyLevel, Question, QuestionType
from skills.gaijuan.scripts.build_grading_package import main as grading_main
from skills.pingyu.scripts.build_comment_package import main as comment_main
from skills.xueqing.scripts.build_learning_package import main as learning_main


def test_build_grading_package_outputs_sources_and_docx(tmp_path: Path) -> None:
    exam_path = tmp_path / "exam.json"
    answers_path = tmp_path / "answers.json"
    output_dir = tmp_path / "grading_package"
    exam = _exam()
    exam_path.write_text(exam.model_dump_json(indent=2), encoding="utf-8")
    answers_path.write_text(
        '[{"student_id":"stu_001","question_id":"q_choice","answer":"A"},'
        '{"student_id":"stu_001","question_id":"q_subjective","answer":"过程说明"}]',
        encoding="utf-8",
    )

    exit_code = grading_main(
        [
            "--exam",
            str(exam_path),
            "--answers",
            str(answers_path),
            "--research",
            "examples/sample_data/research_dossier_math_exam.json",
            "--output-dir",
            str(output_dir),
        ]
    )

    assert exit_code == 0
    assert (output_dir / "graded_responses.json").exists()
    assert (output_dir / "批改报告.docx").exists()
    assert (output_dir / "主观题待复核清单.json").exists()
    assert "来源清单" in (output_dir / "sources.md").read_text(encoding="utf-8")


def test_build_learning_package_outputs_structured_reports(tmp_path: Path) -> None:
    output_dir = tmp_path / "learning_package"

    exit_code = learning_main(
        [
            "--responses",
            "examples/sample_data/sample_student_responses.json",
            "--knowledge-points",
            "examples/sample_data/math_knowledge_points.json",
            "--questions",
            "examples/sample_data/sample_questions.json",
            "--research",
            "examples/sample_data/research_dossier_math_exam.json",
            "--output-dir",
            str(output_dir),
        ]
    )

    assert exit_code == 0
    assert (output_dir / "mastery.json").exists()
    assert (output_dir / "班级学情报告.docx").exists()
    assert (output_dir / "学生个人诊断报告.docx").exists()
    assert (output_dir / "补救练习建议.docx").exists()
    assert (output_dir / "remediation_plan.json").exists()
    assert "来源清单" in (output_dir / "sources.md").read_text(encoding="utf-8")


def test_build_comment_package_outputs_review_notes_and_docx(tmp_path: Path) -> None:
    output_dir = tmp_path / "comment_package"

    exit_code = comment_main(
        [
            "--responses",
            "examples/sample_data/sample_student_responses.json",
            "--mastery",
            "examples/sample_data/sample_knowledge_mastery.json",
            "--knowledge-points",
            "examples/sample_data/math_knowledge_points.json",
            "--observations",
            "examples/sample_data/sample_teacher_observations.json",
            "--research",
            "examples/sample_data/research_dossier_math_beike.json",
            "--output-dir",
            str(output_dir),
        ]
    )

    assert exit_code == 0
    assert (output_dir / "student_comments.json").exists()
    assert (output_dir / "学生评语.docx").exists()
    assert (output_dir / "评语复核清单.json").exists()
    assert "来源清单" in (output_dir / "sources.md").read_text(encoding="utf-8")
    with ZipFile(output_dir / "学生评语.docx") as docx:
        assert 'w:eastAsia="宋体"' in docx.read("word/styles.xml").decode("utf-8")


def _exam() -> ExamPaper:
    questions = [
        Question(
            id="q_choice",
            content="选择正确说法。",
            subject="数学",
            question_type=QuestionType.CHOICE,
            difficulty=DifficultyLevel.EASY,
            knowledge_points=["math_quad_graph"],
            answer="A",
            options=["A. 正确", "B. 错误"],
            score=3,
        ),
        Question(
            id="q_subjective",
            content="请写出解题过程。",
            subject="数学",
            question_type=QuestionType.SHORT_ANSWER,
            difficulty=DifficultyLevel.MEDIUM,
            knowledge_points=["math_quad_vertex"],
            answer="参考答案",
            score=8,
        ),
    ]
    return ExamPaper(
        id="exam_stage_e",
        title="数学单元测验",
        subject="数学",
        grade="九年级",
        total_score=11,
        duration_minutes=45,
        sections=[
            ExamSection(
                title="一、试题",
                question_type=QuestionType.CHOICE,
                questions=questions,
                section_score=11,
            )
        ],
    )
