<!-- Last verified: 2026-04-17 | Current stage: C -->

# Stage C — 备课 + 写教案 + 评语

## 功能汇总

| # | 功能 | 状态 | 备注 |
|---|------|------|------|
| C1 | 备课 Skill (beike) | ✅ | 本地课标分析、Bloom 层次梳理、Markdown 报告 |
| C2 | 写教案 Skill (jiaoan) | ✅ | 标准模板 + 5E 模板 + Markdown/DOCX 导出 |
| C3 | 评语 Skill (pingyu) | ✅ | 批量评语生成 + 教师观察融合 + Markdown/DOCX 导出 |
| C4 | 教案数据模型 | ✅ | LessonPlan, TeachingStep |

---

## C1: 备课 Skill (beike)

### 用户场景

教师为某个主题备课时，获得课标分析、知识点梳理、教学策略建议，为后续写教案和出题提供基础。

### 设计决策

| 决策点 | 选择 | 原因 | 放弃的方案 |
|--------|------|------|-----------|
| 课标来源 | references/curriculum_standards.md 结构化数据 | 离线可用、版本可控 | 在线爬取（不稳定） |
| 认知层次框架 | Bloom 分类法 | 国际通用、与课标对齐 | SOLO 分类（教师不熟悉） |
| 输出 | 结构化分析报告（Markdown） | 可直接用于教案输入 | JSON（教师不友好） |

### 受影响文件

| 文件 | 改动类型 | 说明 |
|------|---------|------|
| `skills/beike/SKILL.md` | 新增 | Skill 定义 |
| `skills/beike/scripts/analyze_curriculum.py` | 新增 | 课标分析逻辑 |
| `skills/beike/references/curriculum_standards.md` | 新增 | 课标结构化数据 |
| `skills/beike/references/bloom_taxonomy.md` | 新增 | Bloom 分类法参考 |
| `tests/test_beike.py` | 新增 | 解析、匹配、报告与 CLI 测试 |
| `examples/demo_beike.md` | 新增 | 备课报告样例 |

### 当前实现

- 输入：`subject`、`grade`、`topic`，可选 `keywords`
- 输出：教师可直接使用的 Markdown 备课分析报告
- 报告结构：
  - 主题信息
  - 课标对齐
  - 知识点梳理
  - 认知层次分析
  - 教学重点与难点
  - 核心素养目标
  - 常见误区
  - 教学策略建议
  - 课堂活动建议
  - 形成性评价建议
  - 后续衔接

### 当前覆盖范围

- 已内置语文、数学、英语三科的代表性课标摘录条目
- 当主题无法完全匹配时，脚本会回退到同学科同年级的相近条目，并在报告中标注

### 推荐命令

```bash
python skills/beike/scripts/analyze_curriculum.py \
  --subject 数学 \
  --grade 九年级 \
  --topic 二次函数 \
  --keywords 图像,顶点,性质 \
  --output-report beike_report.md
```

---

## C2: 写教案 Skill (jiaoan)

### 用户场景

教师基于备课分析结果，生成符合学校要求的标准化教案文档，包含教学目标、重难点、教学过程、作业设计和教学反思。

### 设计决策

| 决策点 | 选择 | 原因 | 放弃的方案 |
|--------|------|------|-----------|
| 教案模板 | 标准模板 + 5E 模板 | 覆盖传统与探究式两种主流教学设计 | 单一模板（不够灵活） |
| 教学过程 | 分阶段（导入/新授/练习/小结） | 与中国课堂实际结构一致 | 自由格式（不规范） |
| 输出格式 | Markdown + DOCX | Markdown 便于编辑，DOCX 便于上交 | 纯文本（格式差） |

### 数据模型

```python
# shared/schemas/lesson.py
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
    reflection: Optional[str] = None
```

### 受影响文件

| 文件 | 改动类型 | 说明 |
|------|---------|------|
| `skills/jiaoan/SKILL.md` | 新增 | Skill 定义 |
| `skills/jiaoan/scripts/generate_plan.py` | 新增 | 教案生成逻辑 |
| `skills/jiaoan/assets/template_standard.md` | 新增 | 标准教案模板 |
| `skills/jiaoan/assets/template_5e.md` | 新增 | 5E 教学模型模板 |
| `shared/schemas/lesson.py` | 新增 | LessonPlan, TeachingStep |
| `tests/test_jiaoan.py` | 新增 | 模板渲染、上下文提取和 CLI 测试 |
| `examples/sample_data/sample_lesson_plan.json` | 新增 | LessonPlan 样例 |
| `examples/demo_jiaoan.md` | 新增 | 教案演示文档 |

### 当前实现

- 新增 `shared.schemas.lesson`：
  - `TeachingStep`
  - `LessonPlan`
- `jiaoan` 支持两种输入模式：
  - 读取 `beike` 报告自动提取知识点、重难点、策略和评价建议
  - 仅基于标题/知识点/目标生成可编辑草稿
- 支持两种模板：
  - `standard`：导入 / 新授 / 练习 / 小结
  - `5e`：Engage / Explore / Explain / Elaborate / Evaluate
- 支持三种输出：
  - `LessonPlan` JSON
  - Markdown
  - DOCX

### 推荐命令

```bash
python skills/jiaoan/scripts/generate_plan.py \
  --title 二次函数的图像与性质 \
  --subject 数学 \
  --grade 九年级 \
  --template standard \
  --beike-report examples/demo_beike.md \
  --output-json lesson_plan.json \
  --output-markdown lesson_plan.md
```

---

## C3: 评语 Skill (pingyu)

### 用户场景

学期末，教师需要为 40-50 个学生各写一段个性化评语。这是教师公认最耗时的任务之一——需要对每个学生的学业表现、行为习惯、成长变化做总结性描述，还要避免千篇一律。

教师说"帮我写期末评语"，输入学生的成绩数据、课堂表现记录、学情分析结果，获得个性化评语。

### 设计决策

| 决策点 | 选择 | 原因 | 放弃的方案 |
|--------|------|------|-----------|
| 输入来源 | 学情数据 + 教师补充的定性描述 | 数据驱动 + 人情味 | 纯模板填充（千篇一律） |
| 评语风格 | 积极鼓励为主 + 委婉指出不足 | 符合中国基础教育评语规范 | 纯客观描述（缺温度） |
| 输出格式 | 批量 Markdown / DOCX | 一次生成全班，教师逐条修改 | 逐个生成（效率太低） |
| 长度 | 每生 150-300 字 | 与学校实际要求匹配 | 过长（浪费空间）或过短（显敷衍） |

### 受影响文件

| 文件 | 改动类型 | 说明 |
|------|---------|------|
| `skills/pingyu/SKILL.md` | 新增 | Skill 定义 |
| `skills/pingyu/scripts/generate_comment.py` | 新增 | 评语生成逻辑 |
| `skills/pingyu/references/comment_guidelines.md` | 新增 | 评语写作规范与示例 |
| `shared/schemas/comment.py` | 新增 | TeacherObservation, StudentComment |
| `tests/test_pingyu.py` | 新增 | 评语生成与 CLI 测试 |
| `examples/sample_data/sample_teacher_observations.json` | 新增 | 教师观察样例 |
| `examples/sample_data/sample_student_comments.json` | 新增 | 评语输出样例 |
| `examples/demo_pingyu.md` | 新增 | 评语演示文档 |

### 当前实现

- 新增 `shared.schemas.comment`：
  - `TeacherObservation`
  - `StudentComment`
- `pingyu` 主输入：
  - `StudentResponse[]`
  - `KnowledgeMastery[]`
  - `KnowledgePoint[]`
  - 可选 `TeacherObservation[]`
- 支持批量输出：
  - `StudentComment[]` JSON
  - Markdown
  - DOCX
- 生成逻辑：
  - 结合得分覆盖度、高置信度掌握度和教师观察
  - 采用“先肯定、再建议、后鼓励”的固定语气框架
  - 通过句式轮换降低同班评语重复度

### 推荐命令

```bash
python skills/pingyu/scripts/generate_comment.py \
  --responses examples/sample_data/sample_student_responses.json \
  --mastery examples/sample_data/sample_knowledge_mastery.json \
  --knowledge-points examples/sample_data/math_knowledge_points.json \
  --observations examples/sample_data/sample_teacher_observations.json \
  --term 期末 \
  --output-json student_comments.json \
  --output-markdown student_comments.md
```

---

## 遗留项 / Backlog

- 课标数据需覆盖语数英三科各年级
- 教案模板格式需与实际学校要求对齐验证
- 5E 模板适用场景需限定（主要用于理科探究课）
- 评语需验证个性化程度——同班学生评语不应重复率过高
- 评语的"教师补充输入"格式需设计（结构化 vs 自由文本）
