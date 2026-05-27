---
name: chuti
description: 按学科、知识点、题型、难度和数量生成符合 TeacherSkills Question schema 的练习题。
---

# 出题 Skill

用于语文、数学、英语三科的本地出题。输出必须是 `shared.schemas.Question` 兼容的 JSON，便于后续交给 `zujuan` 组卷 Skill。

## Stage E 资料增强要求

- Agent 在出题前应先检索或整理课标、教材、样题、题型要求和评分标准。
- 检索资料必须进入 `ResearchDossier` 兼容的 `research_dossier.json`，并用 `sources.md` 记录来源。
- 出题脚本仍负责确定性生成和 schema 校验；Agent 负责判断资料是否可信、是否适配学段和考试类型。
- 若使用本地模板降级生成，题目应标记为草稿，并提示教师复核题源依据和难度。

## 触发场景

- 教师要求“出几道题”“生成练习题”“按知识点出题”。
- 教师指定学科、年级、知识点、题型、难度、数量。
- 需要把题目导出为结构化 JSON。

## 输入参数

| 参数 | 必填 | 示例 | 说明 |
|------|------|------|------|
| `subject` | 条件必填 | `数学` | 支持 `数学`、`语文`、`英语`；提供 `research-dossier` 或 `profile` 时可推断 |
| `knowledge-points` | 条件必填 | `二次函数,图像性质` | 逗号分隔的知识点 ID 或名称；提供 `research-dossier` 时可推断 |
| `question-type` | 条件必填 | `选择题` | 见 `references/question_types.md`；提供 `profile` 时可推断 |
| `difficulty` | 条件必填 | `中` | 支持 `易`、`中`、`难`；提供 `profile` 时可推断 |
| `count` | 否 | `5` | 可由 `profile.sections[].item_count` 推断 |
| `grade` | 否 | `九年级` | 默认不写入题目字段，仅用于内容提示 |
| `score` | 否 | `5` | 可由 `profile.sections[].score_per_item` 推断 |
| `research-dossier` | 否 | `examples\sample_data\research_dossier_math_exam.json` | Agent 检索后生成的资料包，作为出题依据和复核材料 |
| `profile` | 否 | `skills\zujuan\assets\profiles\math_junior_standard.json` | 考试样式文件，即 `TemplateProfile`，提供题型、数量、分值和难度结构 |
| `output-dir` | 否 | `examples_output\question_package` | 输出题目包目录，包含 `questions.json`、`sources.md`、`package.json` |

## 推荐流程

1. Agent 先检索课标、教材、样题、题型和评分要求，形成 `research_dossier.json`。
2. 渲染来源清单：

```powershell
.\.venv\Scripts\python.exe -m shared.tools.sources `
  examples\sample_data\research_dossier_math_exam.json `
  --output examples_output\sources.md
```

3. 读取 `references/question_types.md` 确认题型定义。
4. 按学科读取对应参考模板：
   - 数学：`references/math_patterns.md`
   - 语文：`references/chinese_patterns.md`
   - 英语：`references/english_patterns.md`
5. 调用脚本生成结构化题目包：

```powershell
.\.venv\Scripts\python.exe skills\chuti\scripts\gen_question.py `
  --research-dossier examples\sample_data\research_dossier_math_exam.json `
  --profile skills\zujuan\assets\profiles\math_junior_standard.json `
  --output-dir examples_output\question_package
```

6. 校验输出：

```powershell
.\.venv\Scripts\python.exe skills\chuti\scripts\validate_question.py `
  examples_output\question_package\questions.json
```

## 输出约束

- 输出是 `Question[]` JSON 数组。
- 每道题必须包含 `id`、`content`、`subject`、`question_type`、`difficulty`、`knowledge_points`、`answer`、`score`。
- 选择题必须包含 `options`。
- 阅读理解、完形填空、文言文题建议包含 `material`。
- 数学公式使用 LaTeX，行内公式写作 `$...$`。
- Stage E 生成的题目应在 `metadata` 中记录 `source_ids`、`source_basis`、`difficulty_reason`、`exam_style_id`、`teacher_review_notes`。

## 限制

当前脚本是本地模板生成器，适合生成结构化草稿和测试数据。需要高质量原创题目时，Agent 应结合 `ResearchDossier`、参考模板和教师要求进一步润色，并继续使用 `validate_question.py` 校验输出。
