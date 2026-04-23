import json
from io import StringIO

from mcp_server.stdio_server import handle_jsonrpc_message, serve


def test_initialize_returns_server_capabilities() -> None:
    response = handle_jsonrpc_message(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {},
        }
    )

    assert response is not None
    assert response["result"]["serverInfo"]["name"] == "teacherskills"
    assert "tools" in response["result"]["capabilities"]


def test_tools_list_contains_stage_skills() -> None:
    response = handle_jsonrpc_message(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {},
        }
    )

    tool_names = {tool["name"] for tool in response["result"]["tools"]}

    assert "teacherskills.chuti.generate_questions" in tool_names
    assert "teacherskills.beike.analyze_curriculum" in tool_names
    assert "teacherskills.pingyu.generate_comments" in tool_names


def test_tools_call_generate_questions_returns_json_text() -> None:
    response = handle_jsonrpc_message(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "teacherskills.chuti.generate_questions",
                "arguments": {
                    "subject": "数学",
                    "knowledge_points": ["二次函数的图像与性质"],
                    "question_type": "选择题",
                    "difficulty": "中",
                    "count": 1,
                },
            },
        }
    )

    result = response["result"]
    text = result["content"][0]["text"]
    questions = json.loads(text)

    assert result["isError"] is False
    assert len(questions) == 1
    assert questions[0]["subject"] == "数学"


def test_tools_call_beike_returns_markdown_report() -> None:
    response = handle_jsonrpc_message(
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "teacherskills.beike.analyze_curriculum",
                "arguments": {
                    "subject": "数学",
                    "grade": "九年级",
                    "topic": "二次函数",
                    "keywords": ["图像", "顶点"],
                },
            },
        }
    )

    text = response["result"]["content"][0]["text"]

    assert response["result"]["isError"] is False
    assert "# 备课分析报告" in text
    assert "M-9-ALG-02" in text


def test_unknown_tool_returns_tool_error() -> None:
    response = handle_jsonrpc_message(
        {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {"name": "missing.tool", "arguments": {}},
        }
    )

    assert response["result"]["isError"] is True
    assert "未知工具" in response["result"]["content"][0]["text"]


def test_serve_handles_line_delimited_jsonrpc() -> None:
    input_stream = StringIO(
        json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
        + "\n"
        + json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        + "\n"
    )
    output_stream = StringIO()

    serve(input_stream=input_stream, output_stream=output_stream)
    responses = [json.loads(line) for line in output_stream.getvalue().splitlines()]

    assert len(responses) == 2
    assert responses[0]["id"] == 1
    assert responses[1]["id"] == 2
