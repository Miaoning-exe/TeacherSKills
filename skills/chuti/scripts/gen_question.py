from __future__ import annotations

import argparse
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import TypeVar

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pydantic import TypeAdapter

from shared.schemas.question import DifficultyLevel, Question, QuestionType


SUPPORTED_SUBJECTS = {"数学", "语文", "英语"}
EnumT = TypeVar("EnumT", QuestionType, DifficultyLevel)


@dataclass(frozen=True)
class QuestionRequest:
    subject: str
    knowledge_points: list[str]
    question_type: QuestionType
    difficulty: DifficultyLevel
    count: int = 1
    grade: str | None = None
    score: float = 1.0


def parse_enum_value(
    enum_type: type[EnumT],
    raw_value: str,
) -> EnumT:
    for member in enum_type:
        if raw_value in {member.value, member.name, member.name.lower()}:
            return member
    allowed = "、".join(member.value for member in enum_type)
    raise ValueError(f"不支持的取值: {raw_value}，可选: {allowed}")


def parse_knowledge_points(raw_value: str) -> list[str]:
    points = [item.strip() for item in raw_value.replace("，", ",").split(",")]
    return [point for point in points if point]


def generate_questions(request: QuestionRequest) -> list[Question]:
    if request.subject not in SUPPORTED_SUBJECTS:
        allowed = "、".join(sorted(SUPPORTED_SUBJECTS))
        raise ValueError(f"不支持的学科: {request.subject}，可选: {allowed}")
    if request.count < 1:
        raise ValueError("count 必须大于等于 1")
    if request.score <= 0:
        raise ValueError("score 必须大于 0")
    if not request.knowledge_points:
        raise ValueError("knowledge_points 不能为空")

    return [_build_question(request, index + 1) for index in range(request.count)]


def questions_to_json(questions: list[Question]) -> str:
    return TypeAdapter(list[Question]).dump_json(questions, indent=2).decode("utf-8")


def _build_question(request: QuestionRequest, number: int) -> Question:
    builder = _subject_builder(request.subject)
    fields = builder(request, number)
    return Question(
        id=f"q_{uuid.uuid4().hex[:12]}",
        subject=request.subject,
        question_type=request.question_type,
        difficulty=request.difficulty,
        knowledge_points=request.knowledge_points,
        score=request.score,
        **fields,
    )


def _subject_builder(subject: str):
    if subject == "数学":
        return _build_math_question
    if subject == "语文":
        return _build_chinese_question
    if subject == "英语":
        return _build_english_question
    raise ValueError(f"不支持的学科: {subject}")


def _build_math_question(request: QuestionRequest, number: int) -> dict[str, object]:
    topic = request.knowledge_points[0]
    grade_hint = f"{request.grade} " if request.grade else ""
    if request.question_type == QuestionType.CHOICE:
        return {
            "content": f"{grade_hint}围绕“{topic}”，判断函数 $y=x^2+{number}x+{number}$ 的图像性质，下列说法正确的是哪一项？",
            "options": [
                "A. 开口向上",
                "B. 开口向下",
                "C. 与 $y$ 轴没有交点",
                "D. 顶点一定在原点",
            ],
            "answer": "A",
            "explanation": "二次项系数为 1，大于 0，因此抛物线开口向上。",
        }
    if request.question_type == QuestionType.COMPUTATION:
        return {
            "content": f"{grade_hint}计算并化简：$({number}x+2)^2-({number}x-2)^2$。",
            "answer": f"{8 * number}x",
            "explanation": "利用平方差公式或完全平方公式展开后合并同类项。",
        }
    if request.question_type == QuestionType.PROOF:
        return {
            "content": f"{grade_hint}请证明：若关于“{topic}”的二次函数 $y=x^2+2x+{number}$，其对称轴为 $x=-1$。",
            "answer": "由二次函数对称轴公式 $x=-\\frac{b}{2a}$，代入 $a=1,b=2$ 得 $x=-1$。",
            "explanation": "证明题应写出公式、代入过程和结论。",
        }
    if request.question_type == QuestionType.APPLICATION:
        return {
            "content": f"{grade_hint}某问题可建模为二次函数 $y=-x^2+{number + 4}x$。请结合“{topic}”求最大值并说明实际意义。",
            "answer": f"当 $x={(number + 4) / 2:g}$ 时取得最大值 ${((number + 4) ** 2) / 4:g}$。",
            "explanation": "将二次函数配方或使用顶点公式求最大值。",
        }
    return {
        "content": f"{grade_hint}围绕“{topic}”完成一道{request.question_type.value}。",
        "answer": "参考答案需结合题干推导得出。",
        "explanation": "按数学解题步骤写出已知、求解和结论。",
    }


def _build_chinese_question(request: QuestionRequest, number: int) -> dict[str, object]:
    topic = request.knowledge_points[0]
    grade_hint = f"{request.grade} " if request.grade else ""
    material = f"材料：春风拂过校园，树影在窗前轻轻摇动。学生们围绕“{topic}”展开讨论。"
    if request.question_type == QuestionType.READING_COMP:
        return {
            "material": material,
            "content": f"{grade_hint}阅读材料，概括第 {number} 题所体现的中心意思，并结合文本说明理由。",
            "answer": "中心意思应围绕文本主题概括，并引用材料中的关键词句说明。",
            "explanation": "阅读理解题需先概括内容，再结合文本依据作答。",
        }
    if request.question_type == QuestionType.POETRY:
        return {
            "content": f"{grade_hint}围绕“{topic}”，赏析诗句中意象的表达效果。",
            "answer": "应指出意象特点、情感指向和表达效果。",
            "explanation": "古诗词赏析通常从意象、情感、手法三个角度作答。",
        }
    if request.question_type == QuestionType.CLASSICAL_CHINESE:
        return {
            "material": "材料：学而时习之，不亦说乎？",
            "content": f"{grade_hint}解释材料中关键词语，并说明其与“{topic}”的关联。",
            "answer": "“说”通“悦”，意为愉快。关联说明应结合语境作答。",
            "explanation": "文言文题需关注实词、虚词、通假字和句意。",
        }
    if request.question_type == QuestionType.ESSAY:
        return {
            "content": f"{grade_hint}请以“{topic}”为核心，自拟题目写一篇不少于 600 字的作文。",
            "answer": "评分参考：立意明确，结构完整，语言通顺，有具体事例。",
            "explanation": "作文题答案以评分标准形式给出。",
        }
    if request.question_type == QuestionType.CHOICE:
        return {
            "content": f"{grade_hint}下列关于“{topic}”的表述，最恰当的一项是？",
            "options": ["A. 表述准确且有文本依据", "B. 脱离文本主旨", "C. 偷换概念", "D. 以偏概全"],
            "answer": "A",
            "explanation": "选择题应排除与文本主旨不一致或逻辑不严密的选项。",
        }
    return {
        "content": f"{grade_hint}围绕“{topic}”完成一道{request.question_type.value}。",
        "answer": "参考答案需紧扣文本和语文核心素养要求。",
        "explanation": "答题时注意文本依据、表达方式和语言规范。",
    }


def _build_english_question(request: QuestionRequest, number: int) -> dict[str, object]:
    topic = request.knowledge_points[0]
    grade_hint = f"{request.grade} " if request.grade else ""
    material = (
        f"Tom is preparing a short presentation about {topic}. "
        "He wants to make his ideas clear and useful for his classmates."
    )
    if request.question_type == QuestionType.CLOZE:
        return {
            "material": material,
            "content": f"{grade_hint}Choose the best word for blank {number}: Tom ____ his notes before class.",
            "options": ["A. reviews", "B. reviewed", "C. reviewing", "D. review"],
            "answer": "A",
            "explanation": "The sentence describes a habitual action, so the simple present tense is appropriate.",
        }
    if request.question_type == QuestionType.READING_COMP:
        return {
            "material": material,
            "content": f"{grade_hint}According to the passage, why does Tom prepare the presentation?",
            "answer": "He wants to make his ideas clear and useful for his classmates.",
            "explanation": "The answer can be found directly in the second sentence of the passage.",
        }
    if request.question_type == QuestionType.GRAMMAR:
        return {
            "content": f"{grade_hint}Fill in the blank with the correct form: She enjoys ____ (learn) about {topic}.",
            "answer": "learning",
            "explanation": "The verb enjoy is followed by a gerund.",
        }
    if request.question_type == QuestionType.WRITING:
        return {
            "content": f"{grade_hint}Write an 80-word passage about {topic}. Include at least two reasons and one example.",
            "answer": "Scoring guide: clear topic, logical reasons, correct grammar, and one concrete example.",
            "explanation": "Writing tasks use a scoring guide instead of a single fixed answer.",
        }
    if request.question_type == QuestionType.TRANSLATION:
        return {
            "content": f"{grade_hint}Translate the sentence into English: 我们应该认真学习{topic}。",
            "answer": f"We should study {topic} carefully.",
            "explanation": "Use should to express obligation and carefully as an adverbial modifier.",
        }
    if request.question_type == QuestionType.CHOICE:
        return {
            "content": f"{grade_hint}Which sentence is grammatically correct about {topic}?",
            "options": [
                f"A. I am interested in {topic}.",
                f"B. I interested in {topic}.",
                f"C. I am interest in {topic}.",
                f"D. I interesting in {topic}.",
            ],
            "answer": "A",
            "explanation": "Be interested in is the correct expression.",
        }
    return {
        "content": f"{grade_hint}Create a {request.question_type.value} question about {topic}.",
        "answer": "Reference answer should match the language focus and context.",
        "explanation": "Keep the context natural and appropriate for the target grade.",
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="生成符合 Question schema 的本地模板题。")
    parser.add_argument("--subject", required=True, help="学科：数学、语文、英语")
    parser.add_argument("--knowledge-points", required=True, help="逗号分隔的知识点 ID 或名称")
    parser.add_argument("--question-type", required=True, help="题型，如：选择题、阅读理解、计算题")
    parser.add_argument("--difficulty", required=True, help="难度：易、中、难")
    parser.add_argument("--count", type=int, default=1, help="生成数量，默认 1")
    parser.add_argument("--grade", default=None, help="年级，可选")
    parser.add_argument("--score", type=float, default=1.0, help="每题分值，默认 1")
    parser.add_argument("--output", type=Path, default=None, help="输出 JSON 文件路径；不传则写到 stdout")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    try:
        request = QuestionRequest(
            subject=args.subject,
            knowledge_points=parse_knowledge_points(args.knowledge_points),
            question_type=parse_enum_value(QuestionType, args.question_type),
            difficulty=parse_enum_value(DifficultyLevel, args.difficulty),
            count=args.count,
            grade=args.grade,
            score=args.score,
        )
        output = questions_to_json(generate_questions(request))
    except ValueError as exc:
        sys.stderr.write(f"{exc}\n")
        return 2

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + "\n", encoding="utf-8")
    else:
        sys.stdout.write(output + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
