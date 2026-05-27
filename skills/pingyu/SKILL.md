---
name: pingyu
description: 根据批改结果、学情掌握度和教师观察批量生成个性化学生评语，并导出为 JSON、Markdown 或 DOCX。
---

# 评语 Skill

用于学期末或阶段性评价时批量生成学生评语。输入以 `StudentResponse[]`、`KnowledgeMastery[]` 为主，可叠加教师观察信息，让评语既有数据依据，也保留教师口吻。Stage E 起优先输出正式评语包。

## Stage E 资料增强要求

- 评语包应保留资料来源、学情依据和教师复核清单。
- 评语脚本不做 web search，只消费结构化批改结果、掌握度、教师观察和资料包。
- 生成内容必须保留教师复核环节，避免把数据推断直接当成最终评价。

## 输入

| 参数 | 必填 | 示例 | 说明 |
|------|------|------|------|
| `responses` | 是 | `sample_student_responses.json` | 批改结果 |
| `mastery` | 是 | `sample_knowledge_mastery.json` | 学情掌握度 |
| `knowledge-points` | 是 | `math_knowledge_points.json` | 用于把知识点 ID 转成教师可读名称 |
| `observations` | 否 | `sample_teacher_observations.json` | 教师补充观察 |
| `research` | 否 | `research_dossier_math_beike.json` | 资料包，用于生成来源清单和复核提示 |
| `term` | 否 | `期末` | 评语场景，可写 `阶段性` |

## 推荐流程

```powershell
.\.venv\Scripts\python.exe skills\pingyu\scripts\build_comment_package.py `
  --responses examples\sample_data\sample_student_responses.json `
  --mastery examples\sample_data\sample_knowledge_mastery.json `
  --knowledge-points examples\sample_data\math_knowledge_points.json `
  --observations examples\sample_data\sample_teacher_observations.json `
  --research examples\sample_data\research_dossier_math_beike.json `
  --term 期末 `
  --output-dir examples_output\comment_package
```

输出目录包含：

```text
comment_package/
  学生评语.docx
  student_comments.json
  student_comments.md
  评语复核清单.json
  package.json
  sources.md
```

## 行为规则

- 评语默认遵循“积极鼓励为主 + 委婉指出不足 + 给出成长期待”。
- 若有教师观察，会优先使用学生姓名、习惯表现、教师主观印象等信息。
- 若缺少教师观察，脚本仍可基于得分率和掌握度生成可编辑草稿。
- 输出支持：
  - `StudentComment[]` JSON
  - 批量 Markdown
  - DOCX
- 正式评语包会额外输出 `评语复核清单.json`，提醒教师核对数据表述与学生真实表现。
