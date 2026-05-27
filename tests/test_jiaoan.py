import json
from pathlib import Path

from shared.schemas.lesson import LessonContext, LessonPlan
from skills.jiaoan.scripts.generate_plan import generate_lesson_plan, main, parse_beike_report, render_markdown


def test_parse_beike_report_extracts_sections() -> None:
    report = Path("examples/demo_beike.md").read_text(encoding="utf-8")

    context = parse_beike_report(report)

    assert "图像的开口方向、对称轴与顶点" in context["knowledge_points"]
    assert "课堂快测图像识别" in context["assessments"]


def test_generate_lesson_plan_uses_beike_context_for_standard_template() -> None:
    report = Path("examples/demo_beike.md").read_text(encoding="utf-8")
    context = parse_beike_report(report)

    plan = generate_lesson_plan(
        title="二次函数的图像与性质",
        subject="数学",
        grade="九年级",
        template="standard",
        duration_minutes=45,
        beike_context=context,
    )

    assert isinstance(plan, LessonPlan)
    assert plan.key_points
    assert plan.difficult_points
    assert [step.phase for step in plan.teaching_flow] == ["导入", "新授", "练习", "小结"]


def test_render_markdown_supports_five_e_template() -> None:
    plan = generate_lesson_plan(
        title="一般现在时",
        subject="英语",
        grade="七年级",
        template="5e",
        duration_minutes=40,
        knowledge_points=["一般现在时基本结构", "第三人称单数变化"],
    )

    markdown = render_markdown(plan, template="5e", assessments=["句型转换练习", "口头问答"])

    assert "## 四、5E 教学流程" in markdown
    assert "### Engage" in markdown
    assert "### Evaluate" in markdown


def test_main_writes_json_and_markdown_outputs(tmp_path: Path) -> None:
    json_path = tmp_path / "lesson_plan.json"
    markdown_path = tmp_path / "lesson_plan.md"

    exit_code = main(
        [
            "--title",
            "二次函数的图像与性质",
            "--subject",
            "数学",
            "--grade",
            "九年级",
            "--beike-report",
            "examples/demo_beike.md",
            "--output-json",
            str(json_path),
            "--output-markdown",
            str(markdown_path),
        ]
    )

    assert exit_code == 0
    plan = LessonPlan.model_validate(json.loads(json_path.read_text(encoding="utf-8")))
    markdown = markdown_path.read_text(encoding="utf-8")

    assert plan.title == "二次函数的图像与性质"
    assert "## 五、教学过程" in markdown
    assert "教学重点" in markdown


def test_main_accepts_lesson_context(tmp_path: Path) -> None:
    context_path = tmp_path / "lesson_context.json"
    json_path = tmp_path / "lesson_plan.json"
    context = LessonContext(
        id="lesson_context_test",
        title="二次函数的图像与性质",
        subject="数学",
        grade="九年级",
        topic="二次函数的图像与性质",
        knowledge_points=["图像的开口方向、对称轴与顶点"],
        key_points=["图像的开口方向、对称轴与顶点"],
        difficult_points=["混淆顶点坐标与对称轴"],
        activity_suggestions=["观察参数变化并记录图像变化"],
        assessment_suggestions=["课堂快测图像识别"],
        source_ids=["src_test"],
    )
    context_path.write_text(context.model_dump_json(indent=2), encoding="utf-8")

    exit_code = main(
        [
            "--lesson-context",
            str(context_path),
            "--output-json",
            str(json_path),
        ]
    )

    assert exit_code == 0
    plan = LessonPlan.model_validate(json.loads(json_path.read_text(encoding="utf-8")))
    assert plan.title == context.title
    assert plan.knowledge_points == context.knowledge_points
