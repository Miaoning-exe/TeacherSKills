<!-- Last verified: 2026-04-18 | Current stage: D -->

# 系统架构

## 技术栈

| 层 | 技术 |
|----|------|
| 语言 | Python >= 3.10 |
| 数据模型 | Pydantic >= 2.0 |
| API 客户端 | httpx (异步 HTTP) |
| 文档导出 | python-docx |
| 交付形式 | Claude Code Skill (.md + .py) |
| 包管理 | pyproject.toml (PEP 621) |

**API 服务端（独立部署，教师不感知）：**

| 层 | 技术 |
|----|------|
| 认知诊断 | PyTorch, NumPy, Pandas, scikit-learn |
| 主观题评分 | LLM API |
| 可视化 | Matplotlib |

## 混合架构

```
┌──────────────────────────────────────────────────────────────┐
│  教师本地 (Claude Code)                                       │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  用户层 Skills（教师直接调用）                              │  │
│  │  chuti │ zujuan │ gaijuan │ xueqing │ beike │ jiaoan │ pingyu │
│  ├────────────────────────────────────────────────────────┤  │
│  │  共享数据模型 (shared/schemas/)                          │  │
│  │  Question │ ExamPaper │ KnowledgePoint │ ...           │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │  MCP Server (mcp_server/)                               │  │
│  │  tools/list │ tools/call │ stdio transport             │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │  API 客户端 (shared/api_client.py)                      │  │
│  │  Token 认证 │ 请求封装 │ 错误处理                         │  │
│  └────────────────────────────────────────────────────────┘  │
│         │                                                    │
└─────────│────────────────────────────────────────────────────┘
          │ HTTPS + API Token
          ▼
┌──────────────────────────────────────────────────────────────┐
│  TeacherSkills API (远程服务)                                  │
│                                                              │
│  POST /api/diagnosis    — 认知诊断 (IRT/NCDM)                 │
│  POST /api/grade        — 主观题评分 (LLM)                     │
│  GET  /api/health       — 健康检查                             │
└──────────────────────────────────────────────────────────────┘
```

**本地 vs 远程划分原则：**

| 运行位置 | 能力 | 原因 |
|---------|------|------|
| 本地 | 出题、组卷、备课、写教案、评语、客观题批改 | 纯文本处理，无需重计算 |
| 远程 API | 认知诊断 (IRT/NCDM)、主观题语义评分 | 需要 GPU / 大模型推理 |

## 目录结构

```
TeacherSkills/
├── README.md
├── LICENSE                            # MIT
├── CONTRIBUTING.md
├── pyproject.toml
├── .gitignore
│
├── skills/                            # Skill 根目录（本地运行）
│   ├── chuti/                         # 出题 — Phase 1
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   ├── gen_question.py
│   │   │   └── validate_question.py
│   │   └── references/
│   │       ├── question_types.md
│   │       ├── math_patterns.md
│   │       ├── chinese_patterns.md
│   │       └── english_patterns.md
│   │
│   ├── zujuan/                        # 组卷 — Phase 1
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   ├── assemble_exam.py
│   │   │   └── export_exam.py
│   │   └── references/
│   │       └── exam_constraints.md
│   │
│   ├── gaijuan/                       # 批改 — Phase 2
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   ├── grade_answers.py       # 客观题本地 + 主观题调 API
│   │   │   └── score_report.py
│   │   └── references/
│   │       └── grading_rubrics.md
│   │
│   ├── xueqing/                       # 学情分析 — Phase 2
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   ├── analyze_learning.py    # 调用远程诊断 API
│   │   │   └── visualize_mastery.py
│   │   └── references/
│   │       └── report_templates.md
│   │
│   ├── beike/                         # 备课 — Phase 3
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   └── analyze_curriculum.py
│   │   └── references/
│   │       ├── curriculum_standards.md
│   │       └── bloom_taxonomy.md
│   │
│   ├── jiaoan/                        # 写教案 — Phase 3
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   └── generate_plan.py
│   │   └── assets/
│   │       ├── template_standard.md
│   │       └── template_5e.md
│   │
│   └── pingyu/                        # 评语 — Phase 3
│       ├── SKILL.md
│       ├── scripts/
│       │   └── generate_comment.py
│       └── references/
│           └── comment_guidelines.md
│
├── shared/                            # 跨 Skill 共享库
│   ├── __init__.py
│   ├── api_client.py                  # TeacherSkills API 客户端
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── question.py
│   │   ├── knowledge.py
│   │   ├── student.py
│   │   ├── comment.py
│   │   ├── lesson.py
│   │   └── exam.py
│   └── tools/
│       ├── __init__.py
│       └── knowledge_tree.py          # 知识点体系（本地工具）
│
├── mcp_server/                        # MCP Server（Phase 4）
│   ├── __init__.py
│   └── stdio_server.py               # stdio transport + tool registry
│
├── server/                            # API 服务端（独立部署）
│   ├── app.py                         # FastAPI 入口
│   ├── routers/
│   │   ├── diagnosis.py               # POST /api/diagnosis
│   │   └── grading.py                 # POST /api/grade
│   ├── models/
│   │   ├── irt_model.py
│   │   └── ncdm_model.py
│   ├── auth.py                        # Token 认证
│   └── requirements.txt
│
├── examples/
│   ├── demo_chuti.md
│   ├── demo_beike.md
│   ├── demo_jiaoan.md
│   ├── demo_pingyu.md
│   ├── mcp_config.json
│   ├── demo_zujuan.md
│   ├── demo_full_workflow.md
│   ├── demo_xueqing.md
│   └── sample_data/
│       ├── math_knowledge_points.json
│       ├── chinese_knowledge_points.json
│       ├── english_knowledge_points.json
│       ├── sample_lesson_plan.json
│       ├── sample_questions.json
│       ├── sample_student_answers.json
│       ├── sample_teacher_observations.json
│       ├── sample_student_comments.json
│       ├── sample_student_responses.json
│       └── sample_knowledge_mastery.json
│
├── community/
│   ├── skill_review_checklist.md
│   └── skill_template/
│       ├── SKILL.md
│       ├── references/
│       │   └── README.md
│       └── scripts/
│           └── README.md
│
├── tests/
│   ├── test_schemas.py
│   ├── test_question_gen.py
│   ├── test_exam_assembly.py
│   ├── test_api_client.py
│   └── test_mcp_server.py
│
└── wiki/
```

**命名规范：** Skill 目录名用拼音（chuti/zujuan/gaijuan/xueqing/beike/jiaoan/pingyu），避免中文路径编码问题。

## 数据流

```
备课 ──> 写教案 ──> 出题 ──> 组卷 ──> 批改 ──> 学情分析 ──> 回馈备课/出题
                                       │          │
                                  [远程 API]  [远程 API]
                                  主观题评分   认知诊断
                                                 │
                                           评语（学期末）
```

Skill 之间通过 JSON 文件交换数据，统一使用 `shared/schemas/` 中的 Pydantic 模型序列化/反序列化。

**典型数据流（Phase 1）— 纯本地：**

1. 教师指定学科+知识点+题型+难度 → `chuti` Skill → `Question[]` JSON
2. `Question[]` + 组卷约束 → `zujuan` Skill → `ExamPaper` JSON / Markdown / DOCX

**扩展数据流（Phase 2）— 涉及远程 API：**

3. `ExamPaper` + 学生作答 → `gaijuan` Skill → 客观题本地批改 + 主观题调用 `POST /api/grade` → `StudentResponse[]`
4. `StudentResponse[]` → `xueqing` Skill → 调用 `POST /api/diagnosis` → 学情报告 + `KnowledgeMastery[]` → 回馈 `chuti` 定向出题

**扩展数据流（Phase 3）— 纯本地：**

5. 教师指定学科+年级+主题 → `beike` Skill → 课标分析报告（Markdown）
6. 备课报告 + 教师补充参数 → `jiaoan` Skill → `LessonPlan` JSON / Markdown / DOCX
7. `StudentResponse[]` + `KnowledgeMastery[]` + 教师观察 → `pingyu` Skill → `StudentComment[]` / Markdown / DOCX

**扩展数据流（Phase 4）— MCP 接入：**

8. MCP 客户端 → `mcp_server` → `tools/list`
9. MCP 客户端 → `mcp_server` → `tools/call` → 对应本地 Skill / 脚本

## 核心类型

```python
# shared/schemas/knowledge.py
class KnowledgeLevel(str, Enum):
    REMEMBER = "识记"       # Bloom L1
    UNDERSTAND = "理解"     # Bloom L2
    APPLY = "应用"          # Bloom L3
    ANALYZE = "分析"        # Bloom L4
    EVALUATE = "评价"       # Bloom L5
    CREATE = "创造"         # Bloom L6

class KnowledgePoint(BaseModel):
    id: str
    name: str                            # "二次函数的图像与性质"
    subject: str                         # "数学" | "语文" | "英语"
    grade: str                           # "九年级"
    chapter: Optional[str] = None
    parent_id: Optional[str] = None      # 层级结构
    cognitive_level: KnowledgeLevel
    curriculum_standard_ref: Optional[str] = None

# shared/schemas/question.py
class QuestionType(str, Enum):
    CHOICE = "选择题"
    FILL_BLANK = "填空题"
    SHORT_ANSWER = "解答题"
    TRUE_FALSE = "判断题"
    COMPUTATION = "计算题"       # 数学
    PROOF = "证明题"            # 数学
    APPLICATION = "应用题"      # 数学
    READING_COMP = "阅读理解"   # 语文/英语
    POETRY = "古诗词"           # 语文
    CLASSICAL_CHINESE = "文言文" # 语文
    ESSAY = "作文"              # 语文
    CLOZE = "完形填空"          # 英语
    GRAMMAR = "语法填空"        # 英语
    WRITING = "书面表达"        # 英语
    TRANSLATION = "翻译"       # 英语

class DifficultyLevel(str, Enum):
    EASY = "易"
    MEDIUM = "中"
    HARD = "难"

class Question(BaseModel):
    id: str
    content: str                         # 题干（数学支持 LaTeX）
    subject: str
    question_type: QuestionType
    difficulty: DifficultyLevel
    knowledge_points: list[str]          # KnowledgePoint IDs
    answer: str
    explanation: Optional[str] = None
    score: float = 1.0
    options: Optional[list[str]] = None  # 选择题选项
    material: Optional[str] = None       # 阅读材料
    sub_questions: Optional[list["Question"]] = None
    source: Optional[str] = None
    metadata: dict = {}

# shared/schemas/exam.py
class ExamSection(BaseModel):
    title: str                           # "一、选择题"
    question_type: QuestionType
    questions: list[Question]
    section_score: float

class ExamPaper(BaseModel):
    id: str
    title: str
    subject: str
    grade: str
    total_score: float
    duration_minutes: int
    sections: list[ExamSection]

# shared/schemas/lesson.py
class TeachingStep(BaseModel):
    phase: str
    duration_minutes: int
    content: str
    teacher_activity: str
    student_activity: str
    design_intent: Optional[str] = None

class LessonPlan(BaseModel):
    id: str
    title: str
    subject: str
    grade: str
    duration_minutes: int
    knowledge_points: list[str]
    objectives: list[str]
    key_points: list[str]
    difficult_points: list[str]
    teaching_flow: list[TeachingStep]
    homework: Optional[str] = None
    reflection: Optional[str] = None

# shared/schemas/comment.py
class TeacherObservation(BaseModel):
    student_id: str
    student_name: Optional[str] = None
    strengths: list[str] = []
    habits: list[str] = []
    improvements: list[str] = []
    notes: Optional[str] = None

class StudentComment(BaseModel):
    student_id: str
    student_name: Optional[str] = None
    term: str = "期末"
    comment: str
    highlights: list[str] = []
    next_steps: list[str] = []
```

## API 路由概览

> 完整的请求/响应细节见 `04-api-reference.md`（Phase 2 交付后创建）。

| 方法 | 路径 | 用途 | 引入阶段 |
|------|------|------|---------|
| POST | `/api/diagnosis` | 认知诊断：输入作答数据，返回知识点掌握度 | Phase 2 |
| POST | `/api/grade` | 主观题评分：输入题目+作答+评分标准，返回分数和反馈 | Phase 2 |
| GET | `/api/health` | 健康检查 | Phase 2 |

## 环境变量

| 变量 | 用途 | 默认值 |
|------|------|--------|
| `TEACHERSKILLS_API_TOKEN` | API 认证 Token（教师注册后获取） | — |
| `TEACHERSKILLS_API_URL` | API 服务地址 | `https://api.teacherskills.dev` |

Phase 1 不调用远程 API，这两个变量 Phase 2 起生效。

## MCP 接入

本项目在 Phase 4 提供本地 stdio MCP server，用于把现有 Skill 能力暴露为 MCP tools。

- 启动方式：`python3 -m mcp_server.stdio_server`
- Tool 范围：覆盖 `chuti`、`zujuan`、`gaijuan`、`xueqing`、`beike`、`jiaoan`、`pingyu`
- 默认策略：MCP 调用优先走本地/离线路径，减少首次接入时的 API 依赖

## 构建命令

```bash
# Skill 端（教师本地）
pip install -e .

# 运行测试
pytest tests/

# 文档导出
pip install -e ".[export]"

# API 服务端（独立部署）
pip install -r server/requirements.txt
python3 -m uvicorn server.app:app --host 0.0.0.0 --port 8000
```
