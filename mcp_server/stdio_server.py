from __future__ import annotations

import json
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TextIO

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pydantic import TypeAdapter, ValidationError

from shared.schemas.comment import StudentComment, TeacherObservation
from shared.schemas.exam import ExamPaper
from shared.schemas.knowledge import KnowledgePoint
from shared.schemas.question import DifficultyLevel, Question, QuestionType
from shared.schemas.student import KnowledgeMastery, StudentResponse
from skills.beike.scripts.analyze_curriculum import (
    DEFAULT_BLOOM_PATH,
    DEFAULT_CURRICULUM_PATH,
    analyze_curriculum,
    generate_analysis_report,
    load_bloom_descriptions,
    load_curriculum_entries,
)
from skills.chuti.scripts.gen_question import (
    QuestionRequest,
    generate_questions,
    parse_enum_value,
    parse_knowledge_points,
    questions_to_json,
)
from skills.gaijuan.scripts.grade_answers import AnswerSubmission, grade_submissions, responses_to_json
from skills.jiaoan.scripts.generate_plan import (
    generate_lesson_plan,
    lesson_plan_to_json,
    parse_beike_report,
    render_markdown as render_lesson_markdown,
)
from skills.pingyu.scripts.generate_comment import (
    comments_to_json,
    generate_student_comments,
    render_markdown as render_comments_markdown,
)
from skills.xueqing.scripts.analyze_learning import (
    analyze_learning,
    generate_learning_report,
    mastery_to_json,
)
from skills.zujuan.scripts.assemble_exam import ExamConstraints, assemble_exam, exam_to_json


JSONRPC_VERSION = "2.0"
MCP_PROTOCOL_VERSION = "2024-11-05"

QUESTION_LIST_ADAPTER = TypeAdapter(list[Question])
ANSWER_SUBMISSION_ADAPTER = TypeAdapter(list[AnswerSubmission])
STUDENT_RESPONSE_ADAPTER = TypeAdapter(list[StudentResponse])
KNOWLEDGE_MASTERY_ADAPTER = TypeAdapter(list[KnowledgeMastery])
KNOWLEDGE_POINT_ADAPTER = TypeAdapter(list[KnowledgePoint])
TEACHER_OBSERVATION_ADAPTER = TypeAdapter(list[TeacherObservation])
STUDENT_COMMENT_ADAPTER = TypeAdapter(list[StudentComment])


@dataclass(frozen=True)
class MCPTool:
    name: str
    description: str
    input_schema: dict[str, Any]
    handler: Callable[[dict[str, Any]], str]


def build_tools() -> dict[str, MCPTool]:
    tools = [
        MCPTool(
            name="teacherskills.chuti.generate_questions",
            description="按学科、知识点、题型、难度生成 Question[] JSON。",
            input_schema={
                "type": "object",
                "required": ["subject", "knowledge_points", "question_type", "difficulty"],
                "properties": {
                    "subject": {"type": "string"},
                    "knowledge_points": {"oneOf": [{"type": "string"}, {"type": "array", "items": {"type": "string"}}]},
                    "question_type": {"type": "string"},
                    "difficulty": {"type": "string"},
                    "count": {"type": "integer", "default": 1},
                    "grade": {"type": "string"},
                    "score": {"type": "number", "default": 1},
                },
            },
            handler=_handle_chuti_generate_questions,
        ),
        MCPTool(
            name="teacherskills.zujuan.assemble_exam",
            description="根据 Question[] 与组卷约束生成 ExamPaper JSON。",
            input_schema={
                "type": "object",
                "required": ["questions", "constraints"],
                "properties": {
                    "questions": {"type": "array", "items": {"type": "object"}},
                    "constraints": {"type": "object"},
                },
            },
            handler=_handle_zujuan_assemble_exam,
        ),
        MCPTool(
            name="teacherskills.gaijuan.grade_answers",
            description="批改学生作答，默认离线处理客观题并将主观题标记为待评分。",
            input_schema={
                "type": "object",
                "required": ["exam", "answers"],
                "properties": {
                    "exam": {"type": "object"},
                    "answers": {"type": "array", "items": {"type": "object"}},
                    "rubric": {"type": "string"},
                    "offline": {"type": "boolean", "default": True},
                },
            },
            handler=_handle_gaijuan_grade_answers,
        ),
        MCPTool(
            name="teacherskills.xueqing.analyze_learning",
            description="根据 StudentResponse[] 生成 KnowledgeMastery[] 和 Markdown 学情报告，默认离线启发式分析。",
            input_schema={
                "type": "object",
                "required": ["responses", "knowledge_points"],
                "properties": {
                    "responses": {"type": "array", "items": {"type": "object"}},
                    "knowledge_points": {"type": "array", "items": {"type": "object"}},
                    "questions": {"type": "array", "items": {"type": "object"}},
                    "offline": {"type": "boolean", "default": True},
                },
            },
            handler=_handle_xueqing_analyze_learning,
        ),
        MCPTool(
            name="teacherskills.beike.analyze_curriculum",
            description="根据学科、年级、主题和关键词生成 Markdown 备课分析报告。",
            input_schema={
                "type": "object",
                "required": ["subject", "grade", "topic"],
                "properties": {
                    "subject": {"type": "string"},
                    "grade": {"type": "string"},
                    "topic": {"type": "string"},
                    "keywords": {"oneOf": [{"type": "string"}, {"type": "array", "items": {"type": "string"}}]},
                },
            },
            handler=_handle_beike_analyze_curriculum,
        ),
        MCPTool(
            name="teacherskills.jiaoan.generate_plan",
            description="根据备课报告或教师输入生成教案，支持 markdown/json 输出。",
            input_schema={
                "type": "object",
                "required": ["title", "subject", "grade"],
                "properties": {
                    "title": {"type": "string"},
                    "subject": {"type": "string"},
                    "grade": {"type": "string"},
                    "template": {"type": "string", "enum": ["standard", "5e"], "default": "standard"},
                    "duration_minutes": {"type": "integer", "default": 45},
                    "beike_report": {"type": "string"},
                    "knowledge_points": {"type": "array", "items": {"type": "string"}},
                    "objectives": {"type": "array", "items": {"type": "string"}},
                    "output_format": {"type": "string", "enum": ["markdown", "json"], "default": "markdown"},
                },
            },
            handler=_handle_jiaoan_generate_plan,
        ),
        MCPTool(
            name="teacherskills.pingyu.generate_comments",
            description="根据批改结果、学情掌握度和教师观察批量生成学生评语。",
            input_schema={
                "type": "object",
                "required": ["responses", "mastery", "knowledge_points"],
                "properties": {
                    "responses": {"type": "array", "items": {"type": "object"}},
                    "mastery": {"type": "array", "items": {"type": "object"}},
                    "knowledge_points": {"type": "array", "items": {"type": "object"}},
                    "observations": {"type": "array", "items": {"type": "object"}},
                    "term": {"type": "string", "default": "期末"},
                    "output_format": {"type": "string", "enum": ["markdown", "json"], "default": "markdown"},
                },
            },
            handler=_handle_pingyu_generate_comments,
        ),
    ]
    return {tool.name: tool for tool in tools}

def handle_jsonrpc_message(message: dict[str, Any]) -> dict[str, Any] | None:
    request_id = message.get("id")
    method = message.get("method")
    params = message.get("params") or {}

    if request_id is None and isinstance(method, str) and method.startswith("notifications/"):
        return None
    if method == "initialize":
        return _response(
            request_id,
            {
                "protocolVersion": MCP_PROTOCOL_VERSION,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "teacherskills", "version": "0.1.0"},
            },
        )
    if method == "tools/list":
        return _response(request_id, {"tools": [_tool_to_protocol(tool) for tool in TOOLS.values()]})
    if method == "tools/call":
        return _response(request_id, _call_tool(params))
    if method == "ping":
        return _response(request_id, {})
    return _error(request_id, code=-32601, message=f"未知方法: {method}")


def serve(input_stream: TextIO = sys.stdin, output_stream: TextIO = sys.stdout) -> None:
    for raw_line in input_stream:
        line = raw_line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
            if not isinstance(message, dict):
                raise ValueError("JSON-RPC message must be an object")
            response = handle_jsonrpc_message(message)
        except json.JSONDecodeError as exc:
            response = _error(None, code=-32700, message=f"JSON 解析失败: {exc}")
        except Exception as exc:  # pragma: no cover - defensive guard for long-running stdio process.
            response = _error(None, code=-32603, message=f"内部错误: {exc}")
        if response is not None:
            output_stream.write(json.dumps(response, ensure_ascii=False) + "\n")
            output_stream.flush()


def main() -> int:
    serve()
    return 0


def _call_tool(params: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(params, dict):
        return _tool_error("tools/call params 必须是对象")
    tool_name = params.get("name")
    arguments = params.get("arguments") or {}
    if not isinstance(tool_name, str):
        return _tool_error("tools/call 缺少 name")
    if not isinstance(arguments, dict):
        return _tool_error("tools/call arguments 必须是对象")
    tool = TOOLS.get(tool_name)
    if tool is None:
        return _tool_error(f"未知工具: {tool_name}")
    try:
        text = tool.handler(arguments)
    except (ValidationError, ValueError, KeyError) as exc:
        return _tool_error(str(exc))
    return {"content": [{"type": "text", "text": text}], "isError": False}


def _handle_chuti_generate_questions(arguments: dict[str, Any]) -> str:
    raw_knowledge_points = arguments["knowledge_points"]
    knowledge_points = (
        parse_knowledge_points(raw_knowledge_points)
        if isinstance(raw_knowledge_points, str)
        else [str(item) for item in raw_knowledge_points]
    )
    request = QuestionRequest(
        subject=str(arguments["subject"]),
        knowledge_points=knowledge_points,
        question_type=parse_enum_value(QuestionType, str(arguments["question_type"])),
        difficulty=parse_enum_value(DifficultyLevel, str(arguments["difficulty"])),
        count=int(arguments.get("count", 1)),
        grade=arguments.get("grade"),
        score=float(arguments.get("score", 1.0)),
    )
    return questions_to_json(generate_questions(request))


def _handle_zujuan_assemble_exam(arguments: dict[str, Any]) -> str:
    questions = QUESTION_LIST_ADAPTER.validate_python(arguments["questions"])
    constraints = ExamConstraints.model_validate(arguments["constraints"])
    return exam_to_json(assemble_exam(questions, constraints))


def _handle_gaijuan_grade_answers(arguments: dict[str, Any]) -> str:
    exam = ExamPaper.model_validate(arguments["exam"])
    answers = ANSWER_SUBMISSION_ADAPTER.validate_python(arguments["answers"])
    responses = grade_submissions(
        exam=exam,
        submissions=answers,
        rubric=arguments.get("rubric"),
        offline=bool(arguments.get("offline", True)),
    )
    return responses_to_json(responses)


def _handle_xueqing_analyze_learning(arguments: dict[str, Any]) -> str:
    responses = STUDENT_RESPONSE_ADAPTER.validate_python(arguments["responses"])
    knowledge_points = KNOWLEDGE_POINT_ADAPTER.validate_python(arguments["knowledge_points"])
    questions = QUESTION_LIST_ADAPTER.validate_python(arguments.get("questions", []))
    mastery = analyze_learning(
        responses=responses,
        knowledge_points=knowledge_points,
        questions=questions,
        offline=bool(arguments.get("offline", True)),
    )
    report = generate_learning_report(mastery=mastery, knowledge_points=knowledge_points)
    return _json_dump({"mastery": json.loads(mastery_to_json(mastery)), "report": report})


def _handle_beike_analyze_curriculum(arguments: dict[str, Any]) -> str:
    raw_keywords = arguments.get("keywords", [])
    keywords = parse_knowledge_points(raw_keywords) if isinstance(raw_keywords, str) else [str(item) for item in raw_keywords]
    entries = load_curriculum_entries(DEFAULT_CURRICULUM_PATH.read_text(encoding="utf-8"))
    bloom = load_bloom_descriptions(DEFAULT_BLOOM_PATH.read_text(encoding="utf-8"))
    analysis = analyze_curriculum(
        subject=str(arguments["subject"]),
        grade=str(arguments["grade"]),
        topic=str(arguments["topic"]),
        keywords=keywords,
        entries=entries,
    )
    return generate_analysis_report(analysis=analysis, bloom_descriptions=bloom)


def _handle_jiaoan_generate_plan(arguments: dict[str, Any]) -> str:
    template = str(arguments.get("template", "standard"))
    beike_context = parse_beike_report(arguments["beike_report"]) if arguments.get("beike_report") else None
    plan = generate_lesson_plan(
        title=str(arguments["title"]),
        subject=str(arguments["subject"]),
        grade=str(arguments["grade"]),
        template=template,
        duration_minutes=int(arguments.get("duration_minutes", 45)),
        beike_context=beike_context,
        knowledge_points=[str(item) for item in arguments.get("knowledge_points", [])] or None,
        objectives=[str(item) for item in arguments.get("objectives", [])] or None,
    )
    if arguments.get("output_format", "markdown") == "json":
        return lesson_plan_to_json(plan)
    assessments = []
    if beike_context:
        raw_assessments = beike_context.get("assessments", [])
        assessments = list(raw_assessments) if isinstance(raw_assessments, list) else []
    return render_lesson_markdown(plan, template=template, assessments=assessments)


def _handle_pingyu_generate_comments(arguments: dict[str, Any]) -> str:
    responses = STUDENT_RESPONSE_ADAPTER.validate_python(arguments["responses"])
    mastery = KNOWLEDGE_MASTERY_ADAPTER.validate_python(arguments["mastery"])
    knowledge_points = KNOWLEDGE_POINT_ADAPTER.validate_python(arguments["knowledge_points"])
    observations = TEACHER_OBSERVATION_ADAPTER.validate_python(arguments.get("observations", []))
    term = str(arguments.get("term", "期末"))
    comments = generate_student_comments(
        responses=responses,
        mastery=mastery,
        knowledge_points=knowledge_points,
        observations=observations,
        term=term,
    )
    if arguments.get("output_format", "markdown") == "json":
        return comments_to_json(comments)
    return render_comments_markdown(comments, term=term)


def _tool_to_protocol(tool: MCPTool) -> dict[str, Any]:
    return {
        "name": tool.name,
        "description": tool.description,
        "inputSchema": tool.input_schema,
    }


def _response(request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": JSONRPC_VERSION, "id": request_id, "result": result}


def _error(request_id: Any, *, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": JSONRPC_VERSION, "id": request_id, "error": {"code": code, "message": message}}


def _tool_error(message: str) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": message}], "isError": True}


def _json_dump(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)


TOOLS = build_tools()


if __name__ == "__main__":
    raise SystemExit(main())
