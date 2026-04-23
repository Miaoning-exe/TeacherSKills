<!-- Last verified: 2026-04-13 | Current stage: A -->

# Stage A — MVP: 出题 + 组卷

## 功能汇总

| # | 功能 | 状态 | 备注 |
|---|------|------|------|
| A0 | 项目基础设施 | ✅ | pyproject.toml, .gitignore, README |
| A1 | 共享数据模型 | ✅ | KnowledgePoint, Question, ExamPaper |
| A2 | 出题 Skill | ✅ | 本地模板生成器 + 校验脚本 |
| A3 | 组卷 Skill | ✅ | 贪心组卷 + Markdown/DOCX 导出 |
| A4 | 示例数据 | ✅ | 三科知识点 + 样例题目 + 演示文档 |
| A5 | 测试 | ✅ | schema、出题、组卷、失败路径测试已补齐 |

---

## A0: 项目基础设施

### 用户场景

开发者 clone 仓库后能快速了解项目并安装依赖。

### 受影响文件

| 文件 | 改动类型 | 说明 |
|------|---------|------|
| `pyproject.toml` | 新增 | PEP 621 项目配置，依赖声明 |
| `.gitignore` | 新增 | Python + IDE 忽略规则 |
| `README.md` | 新增 | 项目简介、安装方式、Skill 列表 |
| `LICENSE` | 新增 | MIT |
| `CONTRIBUTING.md` | 新增 | 贡献指南 |

---

## A1: 共享数据模型

### 用户场景

所有 Skill 需要统一的数据结构来交换题目、知识点、试卷数据。

### 设计决策

| 决策点 | 选择 | 原因 | 放弃的方案 |
|--------|------|------|-----------|
| 数据模型库 | Pydantic v2 | 自带 JSON 序列化、校验、schema 导出 | dataclasses（无校验）、attrs（生态较小） |
| 学科特化方式 | 统一 Schema + 可选字段 | 减少类数量，JSON 结构一致 | 每科独立 Schema（维护成本高） |
| 题型定义 | 单一 Enum 含所有学科题型 | 简单直接，题型数量有限 | 按学科分 Enum（过度设计） |
| 难度分级 | 三级（易/中/难） | 与中国小初高考试实际匹配 | 五级/百分制（粒度过细） |

### 数据模型

见 [02-system-architecture.md](./02-system-architecture.md#核心类型) 的核心类型定义。

### 受影响文件

| 文件 | 改动类型 | 说明 |
|------|---------|------|
| `shared/__init__.py` | 新增 | 包初始化 |
| `shared/schemas/__init__.py` | 新增 | Schema 包导出 |
| `shared/schemas/knowledge.py` | 新增 | KnowledgePoint, KnowledgeLevel |
| `shared/schemas/question.py` | 新增 | Question, QuestionType, DifficultyLevel |
| `shared/schemas/exam.py` | 新增 | ExamPaper, ExamSection |

---

## A2: 出题 Skill

### 用户场景

教师通过 Skill 命令指定学科、知识点、题型、难度、数量，快速生成高质量题目。

### 设计决策

| 决策点 | 选择 | 原因 | 放弃的方案 |
|--------|------|------|-----------|
| 输出格式 | Question Schema JSON | 可被组卷 Skill 直接消费 | 纯文本（无法程序化处理） |
| 三科差异 | 参考模板 (references/*.md) 引导 LLM 出题 | 灵活、易维护、不需训练 | 规则引擎（覆盖面有限） |
| 答案校验 | 独立 validate_question.py | 职责分离，可选执行 | 嵌入出题逻辑（耦合） |

### 三科差异化

| 学科 | 特有题型 | 特殊要求 |
|------|---------|---------|
| 数学 | 计算题、应用题、证明题 | LaTeX 公式支持、自动验算 |
| 语文 | 阅读理解、古诗词、文言文、作文 | 文本素材选择、文化语境 |
| 英语 | 完形填空、阅读理解、语法填空、书面表达 | 语境真实性、词汇难度控制 |

### 受影响文件

| 文件 | 改动类型 | 说明 |
|------|---------|------|
| `skills/chuti/SKILL.md` | 新增 | Skill 定义与触发说明 |
| `skills/chuti/scripts/gen_question.py` | 新增 | 出题核心逻辑 |
| `skills/chuti/scripts/validate_question.py` | 新增 | 答案校验 |
| `skills/chuti/references/question_types.md` | 新增 | 题型定义与示例 |
| `skills/chuti/references/math_patterns.md` | 新增 | 数学出题模板 |
| `skills/chuti/references/chinese_patterns.md` | 新增 | 语文出题模板 |
| `skills/chuti/references/english_patterns.md` | 新增 | 英语出题模板 |

### 当前实现说明

- 已提供本地模板生成器 `gen_question.py`，可按学科、知识点、题型、难度和数量生成 `Question[]` JSON。
- 已提供 `validate_question.py` 做 schema 解析和规则校验，覆盖选择题选项、阅读材料建议字段等基础约束。
- 当前版本适合生成结构化草稿和测试数据；后续若接入更强生成能力，仍应保持输出兼容 `Question` schema。

---

## A3: 组卷 Skill

### 用户场景

教师提供题目集合和约束条件（难度分布、知识覆盖、总分、时长），自动组装完整试卷并导出。

### 设计决策

| 决策点 | 选择 | 原因 | 放弃的方案 |
|--------|------|------|-----------|
| 组卷算法 | 约束满足 + 贪心 | 实现简单，满足实际需求 | 遗传算法（过度工程化） |
| 导出格式 | Markdown + DOCX | Markdown 便于预览，DOCX 便于打印 | PDF（排版复杂度高） |
| 输入来源 | JSON 文件（Question[] 数组） | 与出题 Skill 输出格式一致 | 数据库查询（Phase 1 无数据库） |

### 三科试卷结构差异

| 学科 | 典型结构 | 难度分布 |
|------|---------|---------|
| 数学 | 选择 → 填空 → 解答 | 易:中:难 = 7:2:1 |
| 语文 | 基础知识 → 阅读理解 → 写作 | 阅读材料需完整呈现 |
| 英语 | 听力 → 单选 → 完形 → 阅读 → 写作 | 分值按考试标准 |

### 受影响文件

| 文件 | 改动类型 | 说明 |
|------|---------|------|
| `skills/zujuan/SKILL.md` | 新增 | Skill 定义 |
| `skills/zujuan/scripts/assemble_exam.py` | 新增 | 约束满足组卷算法 |
| `skills/zujuan/scripts/export_exam.py` | 新增 | Markdown/DOCX 导出 |
| `skills/zujuan/references/exam_constraints.md` | 新增 | 组卷约束说明 |

### 当前实现说明

- 已提供 `assemble_exam.py`，从 `Question[]` JSON 和约束 JSON 生成 `ExamPaper`。
- 组卷过程按 section 顺序做确定性贪心选择，优先满足难度分布和知识点覆盖。
- 已提供 `export_exam.py`，支持导出 Markdown，并在安装 `python-docx` 后导出 DOCX。

---

## A4: 示例数据

### 受影响文件

| 文件 | 改动类型 | 说明 |
|------|---------|------|
| `examples/sample_data/math_knowledge_points.json` | 新增 | 数学知识点示例 |
| `examples/sample_data/chinese_knowledge_points.json` | 新增 | 语文知识点示例 |
| `examples/sample_data/english_knowledge_points.json` | 新增 | 英语知识点示例 |
| `examples/sample_data/sample_questions.json` | 新增 | 三科样例题目 |
| `examples/demo_chuti.md` | 新增 | 出题演示 |
| `examples/demo_zujuan.md` | 新增 | 组卷演示 |
| `examples/demo_full_workflow.md` | 新增 | 完整工作流演示 |

### 当前实现说明

- 已提供三科知识点样例 JSON，可直接按 `KnowledgePoint[]` 解析。
- 已提供跨学科 `sample_questions.json`，可直接通过 `validate_question.py` 校验，并被 `zujuan` 读取。
- 已提供出题、组卷、完整工作流三份演示文档，覆盖 Stage A 的典型使用路径。

---

## A5: 测试

### 受影响文件

| 文件 | 改动类型 | 说明 |
|------|---------|------|
| `tests/test_schemas.py` | 新增 | Pydantic Schema 序列化/校验测试 |
| `tests/test_question_gen.py` | 新增 | 出题逻辑测试 |
| `tests/test_exam_assembly.py` | 新增 | 组卷约束满足测试 |

### 当前实现说明

- 已补齐 `KnowledgePoint`、`Question`、`ExamPaper` 的 JSON 往返测试。
- 已覆盖 `Question` 嵌套小题、样例数据 schema 解析、选择题非法结构等失败路径。
- 已覆盖组卷题量不足、知识点覆盖不足等关键报错场景。
- 当前完整测试集为 `python3 -m pytest tests`，共 12 个用例通过。

---

## 遗留项 / Backlog

- 出题 Skill 暂不支持题目去重（需要题库持久化后实现）
- 组卷导出暂不支持 PDF 格式
- 数学验算仅支持基础四则运算，不支持复杂方程
