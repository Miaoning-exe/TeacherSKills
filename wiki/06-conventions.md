<!-- Last verified: 2026-04-12 | Current stage: A -->

# 编码约定

> 项目级编码偏好和约束。Agent 写代码前参考此文件。

## 库选择

| 用途 | 使用 | 不使用 | 原因 |
|------|------|--------|------|
| 数据模型 | Pydantic v2 | dataclasses / attrs | 需要 JSON 序列化、校验、schema 导出 |
| 文档导出 | python-docx | reportlab | DOCX 是教师最常用格式 |
| HTTP 客户端 | httpx | requests | 支持异步、类型友好 |
| API 框架 (服务端) | FastAPI | Flask | 自动文档、类型安全、异步 |
| 认知诊断 (服务端) | PyTorch | TensorFlow | 学术界 CDM 实现多用 PyTorch |
| 数据处理 (服务端) | Pandas | 手写循环 | 学生成绩数据天然适合 DataFrame |

## 命名规范

| 对象 | 规范 | 示例 |
|------|------|------|
| Python 模块 | snake_case | `gen_question.py` |
| Python 类 | PascalCase | `KnowledgePoint`, `ExamPaper` |
| Python 函数/变量 | snake_case | `generate_questions()`, `total_score` |
| Skill 目录 | 拼音小写 | `chuti/`, `zujuan/` |
| Enum 成员 | UPPER_CASE (代码) + 中文值 | `CHOICE = "选择题"` |
| JSON 字段 | snake_case | `knowledge_points`, `question_type` |
| API 路由 | `/api/` 前缀 + 名词 | `/api/diagnosis`, `/api/grade` |
| 环境变量 | `TEACHERSKILLS_` 前缀 | `TEACHERSKILLS_API_TOKEN` |
| 测试函数 | `test_` 前缀 + 描述 | `test_question_schema_validation()` |

## 代码模式

### 类型标注
- 所有公开函数必须有类型标注
- 使用 `list[str]` 而非 `List[str]`（Python 3.10+）
- 使用 `X | None` 而非 `Optional[X]`（Pydantic model 字段除外，因为 `Optional` 在 Pydantic v2 中语义更清晰）

### 数据交换
- Skill 之间通过 JSON 文件交换数据
- 所有 JSON 序列化/反序列化通过 Pydantic 的 `model_dump_json()` / `model_validate_json()`
- 不手写 `json.dumps()` / `json.loads()` 处理 schema 数据

### 远程 API 调用
- 所有远程 API 调用通过 `shared/api_client.py` 统一封装，Skill 脚本不直接构造 HTTP 请求
- Token 从环境变量 `TEACHERSKILLS_API_TOKEN` 读取
- API 调用失败时抛出统一异常，由 Skill 脚本决定降级策略

### 学科特化
- 学科差异通过同一 Schema 的可选字段处理，不为每个学科建独立 Schema
- 学科特有逻辑用 `if subject == "数学":` 分支，不用继承

### LaTeX
- 数学题目中的公式用 LaTeX 语法，存储在 `content` 字段中
- 行内公式用 `$...$`，独立公式用 `$$...$$`

## 禁止项

- 不使用 `print()` 做日志——使用 `logging` 模块
- 不使用 `*` 导入——显式列出导入名
- 不在 Schema 中使用 `dict` / `list` 裸类型——指定泛型参数
- 不硬编码学科名——使用 Enum 或常量
- 不在 Skill 脚本中直接 `import httpx`——通过 `shared/api_client.py` 调用
- 不硬编码 API 地址——从环境变量读取
