from pydantic import TypeAdapter

from shared.schemas.comment import StudentComment, TeacherObservation
from shared.schemas.exam import ExamPaper, ExamSection
from shared.schemas.knowledge import KnowledgeLevel, KnowledgePoint
from shared.schemas.lesson import LessonPlan, TeachingStep
from shared.schemas.question import DifficultyLevel, Question, QuestionType
from shared.schemas.student import KnowledgeMastery, StudentResponse


def test_knowledge_point_json_round_trip() -> None:
    knowledge_point = KnowledgePoint(
        id="math_quad_graph",
        name="二次函数的图像与性质",
        subject="数学",
        grade="九年级",
        chapter="二次函数",
        cognitive_level=KnowledgeLevel.UNDERSTAND,
        curriculum_standard_ref="M-9-ALG-02",
    )

    restored = KnowledgePoint.model_validate_json(knowledge_point.model_dump_json())

    assert restored == knowledge_point


def test_question_with_sub_questions_round_trip() -> None:
    sub_question = Question(
        id="sub_1",
        content="根据材料回答第 1 小题。",
        subject="语文",
        question_type=QuestionType.SHORT_ANSWER,
        difficulty=DifficultyLevel.MEDIUM,
        knowledge_points=["cn_reading_theme"],
        answer="围绕主旨概括即可。",
        score=3,
    )
    question = Question(
        id="main_1",
        content="阅读材料并回答问题。",
        subject="语文",
        question_type=QuestionType.READING_COMP,
        difficulty=DifficultyLevel.MEDIUM,
        knowledge_points=["cn_reading_theme"],
        answer="见各小题答案。",
        material="材料：雨后的操场格外安静。",
        sub_questions=[sub_question],
        score=6,
    )

    restored = Question.model_validate_json(question.model_dump_json())

    assert restored.sub_questions is not None
    assert restored.sub_questions[0].id == "sub_1"
    assert restored.sub_questions[0].question_type == QuestionType.SHORT_ANSWER


def test_exam_paper_json_round_trip() -> None:
    question = Question(
        id="math_choice_1",
        content="下列说法正确的是哪一项？",
        subject="数学",
        question_type=QuestionType.CHOICE,
        difficulty=DifficultyLevel.EASY,
        knowledge_points=["math_quad_graph"],
        answer="A",
        options=["A. 开口向上", "B. 开口向下"],
        score=3,
    )
    exam = ExamPaper(
        id="exam_1",
        title="数学小测",
        subject="数学",
        grade="九年级",
        total_score=3,
        duration_minutes=20,
        sections=[
            ExamSection(
                title="一、选择题",
                question_type=QuestionType.CHOICE,
                questions=[question],
                section_score=3,
            )
        ],
    )

    restored = ExamPaper.model_validate_json(exam.model_dump_json())

    assert restored.title == "数学小测"
    assert restored.sections[0].questions[0].options == ["A. 开口向上", "B. 开口向下"]


def test_lesson_plan_json_round_trip() -> None:
    lesson_plan = LessonPlan(
        id="lesson_1",
        title="二次函数的图像与性质",
        subject="数学",
        grade="九年级",
        duration_minutes=45,
        knowledge_points=["math_quad_graph"],
        objectives=["理解二次函数图像特征"],
        key_points=["图像的开口方向"],
        difficult_points=["顶点坐标与对称轴关系"],
        teaching_flow=[
            TeachingStep(
                phase="导入",
                duration_minutes=5,
                content="通过生活情境导入。",
                teacher_activity="展示情境图。",
                student_activity="观察并回答问题。",
                design_intent="激活旧知。",
            )
        ],
        homework="完成配套练习。",
        reflection="关注学生图像识别能力。",
    )

    restored = LessonPlan.model_validate_json(lesson_plan.model_dump_json())

    assert restored == lesson_plan
    assert restored.teaching_flow[0].phase == "导入"


def test_comment_models_round_trip() -> None:
    observation = TeacherObservation(
        student_id="stu_001",
        student_name="林然",
        strengths=["表达主动"],
        habits=["上课专注"],
        improvements=["审题更细致"],
        notes="更愿意分享思路",
    )
    comment = StudentComment(
        student_id="stu_001",
        student_name="林然",
        term="期末",
        comment="表现稳健，继续努力。",
        highlights=["表达主动"],
        next_steps=["审题更细致"],
    )

    restored_observation = TeacherObservation.model_validate_json(observation.model_dump_json())
    restored_comment = StudentComment.model_validate_json(comment.model_dump_json())

    assert restored_observation == observation
    assert restored_comment == comment


def test_sample_data_can_be_parsed_by_schema() -> None:
    from pathlib import Path

    base = Path("examples/sample_data")
    knowledge_adapter = TypeAdapter(list[KnowledgePoint])
    question_adapter = TypeAdapter(list[Question])
    response_adapter = TypeAdapter(list[StudentResponse])
    mastery_adapter = TypeAdapter(list[KnowledgeMastery])
    lesson_adapter = TypeAdapter(LessonPlan)
    observation_adapter = TypeAdapter(list[TeacherObservation])
    comment_adapter = TypeAdapter(list[StudentComment])

    math_points = knowledge_adapter.validate_json((base / "math_knowledge_points.json").read_text(encoding="utf-8"))
    chinese_points = knowledge_adapter.validate_json(
        (base / "chinese_knowledge_points.json").read_text(encoding="utf-8")
    )
    english_points = knowledge_adapter.validate_json(
        (base / "english_knowledge_points.json").read_text(encoding="utf-8")
    )
    questions = question_adapter.validate_json((base / "sample_questions.json").read_text(encoding="utf-8"))
    responses = response_adapter.validate_json((base / "sample_student_responses.json").read_text(encoding="utf-8"))
    mastery = mastery_adapter.validate_json((base / "sample_knowledge_mastery.json").read_text(encoding="utf-8"))
    lesson_plan = lesson_adapter.validate_json((base / "sample_lesson_plan.json").read_text(encoding="utf-8"))
    observations = observation_adapter.validate_json(
        (base / "sample_teacher_observations.json").read_text(encoding="utf-8")
    )
    comments = comment_adapter.validate_json((base / "sample_student_comments.json").read_text(encoding="utf-8"))

    assert len(math_points) >= 1
    assert len(chinese_points) >= 1
    assert len(english_points) >= 1
    assert len(questions) >= 1
    assert len(responses) >= 1
    assert len(mastery) >= 1
    assert lesson_plan.duration_minutes >= 1
    assert len(observations) >= 1
    assert len(comments) >= 1


def test_student_models_round_trip() -> None:
    response = StudentResponse(
        student_id="stu_001",
        question_id="q_001",
        answer="A",
        score=3,
        max_score=3,
        feedback="答案正确",
    )
    mastery = KnowledgeMastery(
        student_id="stu_001",
        knowledge_point_id="math_quad_graph",
        mastery_level=0.82,
        confidence=0.9,
    )

    restored_response = StudentResponse.model_validate_json(response.model_dump_json())
    restored_mastery = KnowledgeMastery.model_validate_json(mastery.model_dump_json())

    assert restored_response == response
    assert restored_mastery == mastery
