# Teacher Skill Hub - 教师技能中心方案

## Context

构建一个开源的 **Teacher Skill Hub**，为中国 K-12 教师提供 AI 驱动的日常工作技能集。以 **Claude Code Skill** 格式为主要交付形式，每个 Skill 独立可用，同时支持组合使用形成完整教学工作流。语数英三科各有专门设计，后续可扩展其他学科。

---

## 项目结构

```
TeacherSkills/
├── README.md
├── LICENSE                            # MIT
├── CONTRIBUTING.md
├── pyproject.toml
├── .gitignore
│
├── skills/                            # Skill 根目录
│   ├── chuti/                         # 出题 (Question Generation)
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   ├── gen_question.py        # 出题核心逻辑
│   │   │   └── validate_question.py   # 答案校验
│   │   └── references/
│   │       ├── question_types.md      # 题型定义
│   │       ├── math_patterns.md       # 数学出题模板
│   │       ├── chinese_patterns.md    # 语文出题模板
│   │       └── english_patterns.md    # 英语出题模板
│   │
│   ├── zujuan/                        # 组卷 (Exam Assembly)
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   ├── assemble_exam.py       # 约束满足组卷
│   │   │   └── export_exam.py         # 导出为 Markdown/DOCX
│   │   └── references/
│   │       └── exam_constraints.md    # 组卷约束说明
│   │
│   ├── gaijuan/                       # 改卷 (Grading)
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   ├── grade_answers.py
│   │   │   └── score_report.py
│   │   └── references/
│   │       └── grading_rubrics.md
│   │
│   ├── renzhi/                        # 认知诊断 (Cognitive Diagnosis)
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   ├── run_diagnosis.py
│   │   │   ├── visualize_mastery.py
│   │   │   └── models/
│   │   │       ├── irt_model.py
│   │   │       └── ncdm_model.py
│   │   └── references/
│   │       └── cd_models.md
│   │
│   ├── beike/                         # 备课 (Lesson Preparation)
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   └── analyze_curriculum.py
│   │   └── references/
│   │       ├── curriculum_standards.md
│   │       └── bloom_taxonomy.md
│   │
│   └── jiaoan/                        # 写教案 (Lesson Plan Writing)
│       ├── SKILL.md
│       ├── scripts/
│       │   └── generate_plan.py
│       └── assets/
│           ├── template_standard.md
│           └── template_5e.md
│
├── shared/                            # 跨 Skill 共享库
│   ├── __init__.py
│   └── schemas/
│       ├── __init__.py
│       ├── question.py                # 题目模型 (含学科特化字段)
│       ├── knowledge.py               # 知识点分类
│       ├── student.py                 # 学生作答/画像
│       ├── lesson.py                  # 教案结构
│       └── exam.py                    # 试卷结构
│
├── examples/
│   ├── demo_chuti.md                  # 出题演示
│   ├── demo_zujuan.md                 # 组卷演示
│   ├── demo_full_workflow.md          # 完整工作流
│   └── sample_data/
│       ├── math_knowledge_points.json
│       ├── chinese_knowledge_points.json
│       ├── english_knowledge_points.json
│       ├── sample_questions.json
│       └── sample_student_responses.json
│
└── tests/
    ├── test_schemas.py
    ├── test_question_gen.py
    └── test_exam_assembly.py
```

**命名说明**: 目录名用拼音（chuti/zujuan/gaijuan/renzhi/beike/jiaoan），避免中文路径编码问题，同时对中文用户一目了然。

---

## 6 个核心 Skill

### 1. 出题 (chuti) - MVP

- **触发**: 教师需要生成练习题或测试题
- **输入**: 学科、知识点、题型、难度、数量
- **输出**: Question schema JSON
- **三科差异化**:
  - **数学**: 计算题、应用题、证明题，支持 LaTeX 公式，自动验算
  - **语文**: 阅读理解、古诗词填空、作文题、文言文翻译，注重文本素材选择
  - **英语**: 完形填空、阅读理解、语法选择、书面表达，注重语境真实性

### 2. 组卷 (zujuan) - MVP

- **触发**: 教师需要组装完整试卷
- **输入**: 题库 + 约束（难度分布、知识覆盖、总分、时长）
- **输出**: 结构化试卷 + 答案
- **三科差异化**:
  - **数学**: 典型结构（选择→填空→解答），难度 7:2:1
  - **语文**: 基础知识→阅读理解→写作，阅读材料需完整
  - **英语**: 听力→单选→完形→阅读→写作，分值按考试标准

### 3. 改卷 (gaijuan) - Phase 2

- **触发**: 教师批改学生作答
- **能力**: 客观题精确匹配 + 主观题 LLM 语义评分
- **三科特殊处理**: 数学关注解题步骤，语文/英语关注语言表达

### 4. 认知诊断 (renzhi) - Phase 2

- **触发**: 了解学生知识掌握情况
- **输出**: 知识掌握画像、班级分析报告
- **模型**: IRT（简单场景）+ NCDM（多维诊断）

### 5. 备课 (beike) - Phase 3

- **触发**: 为某主题备课
- **输出**: 课标分析、知识点梳理、教学策略建议

### 6. 写教案 (jiaoan) - Phase 3

- **触发**: 撰写正式教案
- **输出**: 教学目标/重难点/教学过程/作业/反思

---

## Skill 工作流

```
备课 ──> 写教案 ──> 出题 ──> 组卷 ──> 改卷 ──> 认知诊断
                                                    │
                                                    └──> (回馈出题，针对薄弱点定向出题)
```

**组合机制**: 各 Skill 通过 JSON 文件交换数据，统一使用 `shared/schemas/` 中的 Pydantic 模型。

---

## 核心数据模型

### KnowledgePoint (知识点)

```python
from pydantic import BaseModel
from typing import Optional
from enum import Enum

class KnowledgeLevel(str, Enum):
    REMEMBER = "识记"      # Bloom L1
    UNDERSTAND = "理解"    # Bloom L2
    APPLY = "应用"         # Bloom L3
    ANALYZE = "分析"       # Bloom L4
    EVALUATE = "评价"      # Bloom L5
    CREATE = "创造"        # Bloom L6

class KnowledgePoint(BaseModel):
    id: str
    name: str                            # "二次函数的图像与性质"
    subject: str                         # "数学" | "语文" | "英语"
    grade: str                           # "九年级"
    chapter: Optional[str] = None
    parent_id: Optional[str] = None      # 层级结构
    cognitive_level: KnowledgeLevel = KnowledgeLevel.UNDERSTAND
    curriculum_standard_ref: Optional[str] = None  # 课标编号
```

### Question (题目) - 含学科特化

```python
class QuestionType(str, Enum):
    # 通用
    CHOICE = "选择题"
    FILL_BLANK = "填空题"
    SHORT_ANSWER = "解答题"
    TRUE_FALSE = "判断题"
    # 数学
    COMPUTATION = "计算题"
    PROOF = "证明题"
    APPLICATION = "应用题"
    # 语文
    READING_COMP = "阅读理解"
    POETRY = "古诗词"
    CLASSICAL_CHINESE = "文言文"
    ESSAY = "作文"
    # 英语
    CLOZE = "完形填空"
    GRAMMAR = "语法填空"
    WRITING = "书面表达"
    TRANSLATION = "翻译"

class DifficultyLevel(str, Enum):
    EASY = "易"
    MEDIUM = "中"
    HARD = "难"

class Question(BaseModel):
    id: str
    content: str                         # 题干 (数学支持 LaTeX)
    subject: str
    question_type: QuestionType
    difficulty: DifficultyLevel
    knowledge_points: list[str]          # KnowledgePoint IDs
    answer: str                          # 参考答案
    explanation: Optional[str] = None    # 解题过程/解析
    score: float = 1.0
    options: Optional[list[str]] = None  # 选择题选项
    material: Optional[str] = None       # 阅读材料 (语文/英语)
    sub_questions: Optional[list["Question"]] = None  # 小题 (阅读理解)
    source: Optional[str] = None         # 来源
    metadata: dict = {}                  # 可扩展字段
```

### ExamPaper (试卷)

```python
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
```

### StudentResponse / KnowledgeMastery (Phase 2)

```python
class StudentResponse(BaseModel):
    student_id: str
    question_id: str
    answer: str
    score: Optional[float] = None
    max_score: float
    feedback: Optional[str] = None

class KnowledgeMastery(BaseModel):
    student_id: str
    knowledge_point_id: str
    mastery_level: float                 # 0.0 ~ 1.0
    confidence: Optional[float] = None
```

### LessonPlan (教案, Phase 3)

```python
class TeachingStep(BaseModel):
    phase: str                           # "导入" / "新授" / "练习" / "小结"
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
    objectives: list[str]                # 教学目标
    key_points: list[str]                # 教学重点
    difficult_points: list[str]          # 教学难点
    teaching_flow: list[TeachingStep]
    homework: Optional[str] = None
    reflection: Optional[str] = None     # 教学反思
```

---

## 实施计划

### Phase 1 - MVP: 出题 + 组卷（首批实施）

| Step | 内容 | 关键文件 |
|------|------|---------|
| 1 | 项目基础设施 | `pyproject.toml`, `.gitignore`, `README.md`, `git init` |
| 2 | 共享数据模型 | `shared/schemas/{knowledge,question,exam}.py` |
| 3 | 出题 Skill | `skills/chuti/SKILL.md` + scripts + references (三科模板) |
| 4 | 组卷 Skill | `skills/zujuan/SKILL.md` + scripts + references |
| 5 | 示例数据 | `examples/sample_data/` (语数英三科知识点+样例题目) |
| 6 | 测试 | `tests/test_schemas.py`, `tests/test_question_gen.py` |

### Phase 2: 改卷 + 认知诊断

### Phase 3: 备课 + 写教案

### Phase 4: MCP Server + 社区化

---

## 依赖

```toml
[project]
name = "teacher-skill-hub"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = ["pydantic>=2.0"]

[project.optional-dependencies]
diagnosis = ["torch", "numpy", "pandas", "scikit-learn"]
visualization = ["matplotlib"]
export = ["python-docx"]
```

---

## 验证方式

1. `pytest tests/` - Schema 和脚本测试
2. 在 Claude Code 中 symlink `skills/` 到 `~/.claude/skills/`，调用出题和组卷 Skill
3. 用 `examples/sample_data/` 跑完整出题→组卷流程
4. 检查三科（语数英）的出题质量和格式正确性
