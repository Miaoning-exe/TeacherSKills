<!-- Last verified: 2026-04-18 | Current stage: D -->

# 变更日志

## Stage D — MCP Server + 社区化

**日期：** 2026-04-18

### 新增
- MCP Server 包 (mcp_server/) — 基于 stdio 的最小 MCP server，实现 `initialize`、`tools/list`、`tools/call`
- MCP 工具封装 — 暴露 `chuti`、`zujuan`、`gaijuan`、`xueqing`、`beike`、`jiaoan`、`pingyu` 七个核心能力
- MCP 测试 (tests/test_mcp_server.py) — 覆盖协议初始化、tool 列表、tool 调用和 line-delimited stdio
- MCP 配置样例 (examples/mcp_config.json)
- 社区模板目录 (community/skill_template/) — Skill、脚本目录和参考资料目录模板
- Skill 自检清单 (community/skill_review_checklist.md)
- Stage D 文档 (wiki/13-stage-d.md)
- GitHub Actions CI (`.github/workflows/ci.yml`) — PR 自动执行测试与 MCP 冒烟

### 调整
- `pyproject.toml` 暴露 `teacherskills-mcp` 启动命令
- Stage D 状态更新为完成，D1、D2 已全部落地
- `CONTRIBUTING.md` 升级为可执行的社区贡献指南
- 社区贡献流程进一步接入最小 CI 闭环

### 关键决策
- MCP 先实现 stdio 最小闭环，不一次性扩展到 resources/prompts
- MCP 默认优先走本地/离线路径，避免外部客户端首次接入时因网络或 Token 失败
- 社区贡献规范使用“模板 + 检查清单 + wiki 同步”组合，降低新贡献者上手成本

## Stage C — 备课 + 写教案 + 评语

**日期：** 2026-04-17

### 新增
- 备课 Skill (skills/beike) — 本地课标匹配、知识点梳理、Bloom 层次分析与教学策略建议
- 课标参考数据 (skills/beike/references/curriculum_standards.md) — 语数英代表性条目，支持离线分析
- Bloom 分类参考 (skills/beike/references/bloom_taxonomy.md)
- 备课演示文档 (examples/demo_beike.md)
- 备课测试 (tests/test_beike.py) — 覆盖参考数据解析、主题匹配、报告生成与 CLI 输出
- 教案数据模型 (shared/schemas/lesson.py) — `LessonPlan` 和 `TeachingStep`
- 写教案 Skill (skills/jiaoan) — 备课报告提取、标准模板/5E 模板生成、Markdown/DOCX 导出
- 教案样例数据 (examples/sample_data/sample_lesson_plan.json)
- 教案演示文档 (examples/demo_jiaoan.md)
- 教案测试 (tests/test_jiaoan.py) — 覆盖备课上下文提取、模板渲染与 CLI 输出
- 评语数据模型 (shared/schemas/comment.py) — `TeacherObservation` 和 `StudentComment`
- 评语 Skill (skills/pingyu) — 批改结果、学情掌握度和教师观察融合生成批量评语
- 评语样例数据 (examples/sample_data/sample_teacher_observations.json, sample_student_comments.json)
- 评语演示文档 (examples/demo_pingyu.md)
- 评语测试 (tests/test_pingyu.py) — 覆盖学生画像、个性化差异和 CLI 输出

### 调整
- Stage C 状态更新为完成，C1-C4 已全部完成
- README 增加 Phase 3 备课、教案与评语工作流示例
- README 服务端启动说明修正为根目录安装 `server/requirements.txt`

### 关键决策
- 课标数据继续采用本地 Markdown 结构化摘录，避免联网依赖
- 备课输出以教师可直接消费的 Markdown 报告为主，不引入新的中间 JSON 格式
- 当主题无法完全匹配时，退化为同学科同年级相近条目并显式提示，避免静默误判
- 教案统一先生成 `LessonPlan` 结构，再派生 Markdown/DOCX，避免多种输出格式各自维护一套逻辑
- `jiaoan` 优先消费 `beike` 报告，保持 Stage C 内部工作流衔接
- 评语生成优先使用高置信度学情数据和教师观察，避免用低置信度诊断结果误导表述
- 教师观察采用轻量结构化 JSON，先满足批量生成，再保留后续扩展自由文本输入的空间

## Stage B — 批改 + 学情分析

**日期：** 2026-04-16

### 新增
- 学生作答模型 (shared/schemas/student.py) — `StudentResponse` 和 `KnowledgeMastery`
- API 客户端 (shared/api_client.py) — Token 认证、`/api/grade`、`/api/diagnosis` 封装
- 批改 Skill (skills/gaijuan) — 本地客观题批改、主观题远程评分、离线降级
- 学情分析 Skill (skills/xueqing) — 诊断调用、Markdown 报告、可选图表
- API 服务端 (server/) — FastAPI 入口、认证、评分与诊断路由
- 成绩报告脚本 (score_report.py) — 按学生汇总 Markdown 报告
- 批改样例数据 (examples/sample_data/sample_student_answers.json)
- 批改结果样例 (examples/sample_data/sample_student_responses.json)
- 掌握度样例 (examples/sample_data/sample_knowledge_mastery.json)
- 学情分析演示文档 (examples/demo_xueqing.md)
- API 客户端测试 (tests/test_api_client.py)
- 批改流程测试 (tests/test_grading.py)
- 学情分析测试 (tests/test_learning_analysis.py)
- 服务端接口测试 (tests/test_server_api.py)

### 调整
- `pyproject.toml` 基础依赖加入 `httpx`
- Stage B 状态更新为完成，B1-B5 已全部落地

### 关键决策
- 客观题继续本地处理，避免不必要的远程请求
- 主观题评分失败时不阻塞流程，统一降级为“待评分”
- 远程 API 调用集中到 `shared/api_client.py`，避免 Skill 层重复处理认证和错误语义

## Stage A — MVP: 出题 + 组卷

**日期：** 2026-04-13

### 新增
- 项目基础设施 (pyproject.toml, README, LICENSE)
- 共享数据模型 (KnowledgePoint, Question, ExamPaper)
- 出题 Skill (chuti) — 本地模板出题、三科参考模板、Question schema 输出
- 组卷 Skill (zujuan) — 约束 JSON 驱动的贪心组卷、ExamPaper 输出
- 试卷导出脚本 (export_exam.py) — Markdown 导出，支持可选 DOCX 导出
- 题目校验脚本 (validate_question.py) — 选择题选项与阅读材料等基础规则校验
- 示例数据 (examples/sample_data) — 三科知识点样例和跨学科题目池
- 演示文档 (examples/demo_*.md) — 出题、组卷、完整工作流示例
- Schema 测试 (tests/test_schemas.py) — 覆盖 JSON 往返、嵌套题目和样例数据解析
- 出题逻辑测试 (tests/test_question_gen.py)
- 组卷逻辑测试 (tests/test_exam_assembly.py)

### 调整
- `Question.metadata` 改为 `Field(default_factory=dict)`，避免共享可变默认值
- Stage A 状态更新为完成，A0-A5 已全部落地

### 关键决策
- 选择 Pydantic v2 作为数据模型库，因其自带 JSON 序列化和校验
- 学科差异通过统一 Schema 可选字段处理，不为每科建独立 Schema
- 目录名用拼音（chuti/zujuan），避免中文路径编码问题
