<!-- Last verified: 2026-05-12 | Current stage: E -->

# Stage E — 资料增强与专业化交付

## 背景判断

当前 TeacherSkills 已经完成 7 个核心 Skill、共享 Schema、示例数据、测试和 MCP Server，但整体能力仍偏 demo 化。主要问题不是 Skill 数量不足，而是缺少真实教师工作流中最关键的三层能力：

- 资料来源：备课、出题、组卷不能只依赖本地静态模板，应先检索课标、教材、样卷、考试要求和主流模板。
- 规范模板：组卷、备课、教案、学情等产物需要固定结构和学科/学段/考试类型 profile，而不是临时 Markdown。
- 正式交付件：教师真正需要的是可编辑、可打印、可归档的 Office 文档包，包括试卷、答题卡、答案、评分细则等。

Stage E 的目标是把项目从“本地模板生成器”升级为“资料增强 + 标准模板渲染 + 正式文档包”的教师工作流系统。

## 总体原则

| 原则 | 说明 |
|------|------|
| Agent 先检索，脚本后生成 | Agent 负责 web search、资料筛选、判断适配性；Python 脚本负责确定性数据校验和文档生成。 |
| 中间数据结构化 | 检索结果、模板 profile、试卷蓝图、输出清单都必须进入 Pydantic Schema，避免只靠自由文本传递。 |
| 每个 Skill 都有正式产物 | 不再只交付 JSON/Markdown，关键 Skill 必须输出 DOCX 文档包。 |
| 来源可追溯 | 所有资料增强产物必须附 `sources.md` 或等价字段，区分来源事实、Agent 推理和教师待复核内容。 |
| 先做组卷标杆 | `zujuan` 最容易体现专业化价值，应先完成闭环，再复用同一套规范升级其他 Skill。 |

## 目标架构

```text
用户需求
  ↓
Agent web search
  ↓
research_dossier.json
  ↓
Skill 结构化处理
  ↓
blueprint / profile / package schema
  ↓
模板渲染
  ↓
DOCX 文档包 + JSON + sources.md
```

建议新增共享模型：

| Schema | 用途 |
|--------|------|
| `SourceEvidence` | 记录资料标题、URL、来源类型、发布时间、可信等级、摘要和引用位置。 |
| `ResearchDossier` | 一次任务的资料包，包含课标、教材、样卷、模板、评分标准等检索结果。 |
| `CurriculumContext` | 面向备课/出题/组卷的课标、教材、知识点和考试要求上下文。 |
| `TemplateProfile` | 描述不同学科、学段、考试类型的模板结构和格式规则。 |
| `GenerationPackage` | 描述一次正式输出包含哪些文件、生成时间、输入数据和来源清单。 |

## E1: 资料增强层

### 用户场景

教师要求“围绕某个主题备课”“出一套单元卷”“按中考风格组卷”时，Agent 应先检索并整理资料，而不是直接调用本地模板。

### 设计决策

| 决策点 | 选择 | 原因 |
|--------|------|------|
| web search 位置 | Agent 工作流层 | 搜索质量需要判断、比较和取舍，不适合放进纯脚本。 |
| 脚本输入 | `research_dossier.json` | 让脚本保持可测试、可复现。 |
| 来源记录 | 强制输出 `sources.md` | 教师可复核资料来源，降低幻觉风险。 |
| 资料分类 | 课标、教材、样卷、题型、评分、模板 | 覆盖备课、出题、组卷的核心依据。 |

### 任务拆分

| # | 任务 | 状态 | 备注 |
|---|------|------|------|
| E1.1 | 新增 `shared/schemas/research.py` | ✅ | 定义 `SourceEvidence`、`ResearchDossier`，覆盖来源类型、可信等级、引用位置和复核提示。 |
| E1.2 | 新增 `shared/schemas/template.py` | ✅ | 定义 `TemplateProfile`、模板 section 和格式元数据。 |
| E1.3 | 新增资料包样例 | ✅ | 已覆盖数学组卷、备课两个场景：`research_dossier_math_exam.json`、`research_dossier_math_beike.json`。 |
| E1.4 | 更新 Skill 行为规则 | ✅ | `beike`、`chuti`、`zujuan` 已明确要求先检索、生成资料包和 `sources.md`，无资料时标记本地模板草稿。 |
| E1.5 | 新增来源渲染工具 | ✅ | `python -m shared.tools.sources research_dossier.json --output sources.md` 可从 `ResearchDossier` 生成 `sources.md`。 |

### E1 交付说明

E1 当前只实现资料增强层的数据边界和确定性渲染能力，不把 web search 写入脚本。Agent 仍负责检索、比较和筛选资料；脚本只消费 `research_dossier.json` 并输出可复核的 `sources.md`。这保持了 Stage E “Agent 先检索，脚本后生成”的边界。

## E2: 组卷专业化标杆

### 用户场景

教师需要一套可直接打印和发给学生的正式试卷包，而不是只有 `exam.json` 或简单 DOCX。

### 目标输出

`zujuan` 应输出一个完整目录：

```text
exam_package/
  试卷.docx
  答题卡.docx
  参考答案.docx
  评分细则.docx
  exam.json
  blueprint.json
  sources.md
```

### 新增概念

| 概念 | 说明 |
|------|------|
| `ExamBlueprint` | 试卷蓝图，描述考试类型、总分、时长、题型结构、分值、难度比例和知识点覆盖。 |
| `AnswerSheetSpec` | 答题卡规格，描述选择题涂卡区、填空区、解答题书写区、作文/写作区。 |
| `AnswerKey` | 参考答案结构，按题号对齐试卷。 |
| `ScoringRubric` | 评分细则结构，支持主观题分步给分。 |
| `ExamPackage` | 试卷包清单，记录所有输出文件和一致性校验结果。 |

### 主流模板要求

第一版先覆盖初中数学标准卷，后续扩展语文和英语。

| 学科 | 第一版模板结构 |
|------|----------------|
| 数学 | 选择题、填空题、解答题；100/120 分；90/120 分钟；难度约 7:2:1。 |
| 语文 | 积累运用、阅读理解、古诗文、写作；含作文格或写作答题区。 |
| 英语 | 听力、单选/语法、完形、阅读、任务型阅读、书面表达。 |

### 任务拆分

| # | 任务 | 状态 | 备注 |
|---|------|------|------|
| E2.1 | 扩展 `shared/schemas/exam.py` | ✅ | 增加 `ExamBlueprint`、`AnswerSheetSpec`、`AnswerKey`、`ScoringRubric`、`ExamPackage`。 |
| E2.2 | 新增模板 profile | ✅ | `skills/zujuan/assets/profiles/math_junior_standard.json`，第一版为适配样例题库的初中数学标准卷样例版。 |
| E2.3 | 新增 DOCX 模板资产 | ✅ | `skills/zujuan/assets/templates/README.md` 记录四类 DOCX 模板资产约定；第一版由脚本确定性生成四类 DOCX。 |
| E2.4 | 新增 `build_exam_package.py` | ✅ | 一次性生成正式试卷包。 |
| E2.5 | 改造 `export_exam.py` | ✅ | 保留单文件导出，并在 CLI 说明中推荐正式试卷包命令。 |
| E2.6 | 更新 `skills/zujuan/SKILL.md` | ✅ | 写入资料增强、模板 profile、正式文档包流程和一致性约束。 |
| E2.7 | 新增测试 | ✅ | `tests/test_exam_package.py` 校验分值一致、题号一致、答案完整、输出文件存在。 |
| E2.8 | 新增 demo | ✅ | `examples/demo_zujuan_professional.md` 说明专业组卷输入、命令和输出目录。 |

### E2 交付说明

E2 第一版以 `math_junior_standard` 作为初中数学标准卷样例 profile。为保证当前仓库样例可直接运行，该 profile 的题量与 `examples/sample_data/sample_questions.json` 中的数学题保持一致，总分为 17 分、时长 45 分。真实 100/120 分试卷可通过扩展 profile 的 `item_count`、`score_per_item` 和题库规模实现，包生成接口保持不变。

`build_exam_package.py` 当前会生成：

```text
exam_package/
  试卷.docx
  答题卡.docx
  参考答案.docx
  评分细则.docx
  exam.json
  blueprint.json
  answer_sheet.json
  answer_key.json
  scoring_rubric.json
  package.json
  sources.md
```

一致性校验覆盖总分、分卷分值、答题卡题号、答案题号、评分细则题号、答案完整性和输出文件存在性。

### 推荐命令形态

```bash
python skills/zujuan/scripts/build_exam_package.py \
  --research research_dossier.json \
  --questions questions.json \
  --profile skills/zujuan/assets/profiles/math_junior_standard.json \
  --output-dir output/exam_package
```

## E3: 备课专业化

### 用户场景

教师需要基于课标、教材和优秀课例完成备课，并进一步生成教案、课堂活动单和配套练习。

### 目标输出

```text
lesson_package/
  备课分析.docx
  教学设计.docx
  课堂活动单.docx
  配套练习.docx
  lesson_context.json
  sources.md
```

### 任务拆分

| # | 任务 | 状态 | 备注 |
|---|------|------|------|
| E3.1 | 改造 `beike` 输入 | 📋 | 支持 `research_dossier.json`，保留本地参考降级。 |
| E3.2 | 新增 `LessonContext` | 📋 | 统一课标、教材、学情、教学目标和活动建议。 |
| E3.3 | 新增备课 DOCX 模板 | 📋 | 备课分析、课堂活动单、配套练习。 |
| E3.4 | 更新 `jiaoan` | 📋 | 从 `LessonContext` 生成更正式的教案文档。 |
| E3.5 | 新增来源与复核区 | 📋 | 明确哪些内容来自资料，哪些是生成建议。 |

## E4: 其他 Skill 规范化

| Skill | 升级方向 |
|-------|----------|
| `chuti` | 基于资料包和考试样式生成题目，记录题目来源依据、考查点、难度理由和答案解析。 |
| `gaijuan` | 输出评分细则、批改报告、错因标签和主观题待复核清单。 |
| `xueqing` | 输出班级学情报告、学生个人诊断报告、补救练习建议和知识点热力图。 |
| `pingyu` | 区分班主任评语、学科评语、阶段性反馈，降低同质化重复。 |
| `mcp_server` | 暴露资料包、模板 profile、文档包生成等新工具。 |

## E5: 验收标准

Stage E 不以“脚本能跑”为完成标准，而以教师可用性为标准。

| 维度 | 验收标准 |
|------|----------|
| 资料可信 | 每个资料增强任务都有 `sources.md`，来源类型和摘要完整。 |
| 文档完整 | 组卷至少生成试卷、答题卡、答案、评分细则。 |
| 结构一致 | 试卷题号、答题卡题号、答案题号、评分细则题号一致。 |
| 分值一致 | 小题分值、分卷分值、总分一致。 |
| 模板可复用 | 模板 profile 能被不同题库复用，不依赖某一次样例。 |
| 可测试 | 核心 schema、包生成、文档存在性和一致性都有自动化测试。 |
| 可降级 | 无网络或无资料包时能使用本地参考，但产物必须标记为“本地模板草稿”。 |

## 推荐实施顺序

1. 先定义 `ResearchDossier` 和 `ExamBlueprint`，把资料增强和试卷蓝图边界稳定下来。
2. 先做初中数学标准组卷包，完成 `试卷.docx`、`答题卡.docx`、`参考答案.docx`、`评分细则.docx`。
3. 给 `zujuan` 补完整测试和 demo，让它成为专业化改造样板。
4. 用同样的资料包和模板 profile 思路改造 `beike` 与 `jiaoan`。
5. 最后把 `chuti`、`gaijuan`、`xueqing`、`pingyu` 的输出规范统一到“资料依据 + 结构化数据 + 正式文档包”。

## 第一批具体文件计划

| 文件 | 改动类型 | 说明 |
|------|----------|------|
| `shared/schemas/research.py` | 新增 | 资料增强层 Schema。 |
| `shared/schemas/template.py` | 新增 | 模板 profile Schema。 |
| `shared/schemas/exam.py` | 修改 | 扩展正式试卷包相关 Schema。 |
| `skills/zujuan/assets/profiles/math_junior_standard.json` | 新增 | 初中数学标准卷 profile。 |
| `skills/zujuan/scripts/build_exam_package.py` | 新增 | 正式试卷包生成入口。 |
| `skills/zujuan/SKILL.md` | 修改 | 更新为资料增强 + 正式文档包流程。 |
| `tests/test_exam_package.py` | 新增 | 试卷包一致性测试。 |
| `examples/demo_zujuan_professional.md` | 新增 | 专业组卷演示。 |

## 风险与注意事项

- web search 结果具有时效性，必须记录检索日期和来源，不应把检索内容静默写死到代码里。
- DOCX 模板不要追求复杂排版优先，第一版先保证结构、题号、分值、分页和可编辑性。
- 答题卡生成需要先支持常见纸面结构，再考虑机读卡识别或扫描场景。
- 学科模板差异很大，先做一个标杆学科，不要同时铺开三科。
- 需要避免把 Agent 自由生成内容伪装成官方依据，所有推理建议都应明确标记。
