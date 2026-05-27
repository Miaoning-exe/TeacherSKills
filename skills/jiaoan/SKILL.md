---
name: jiaoan
description: 根据备课结果或教师输入生成标准模板或 5E 模板教案，并导出为 LessonPlan JSON、Markdown 或 DOCX。
---

# 写教案 Skill

用于将备课结论转成可提交、可继续编辑的正式教案。默认生成 Markdown，也可同时导出 `LessonPlan` JSON 和 DOCX。

## 输入

| 参数 | 必填 | 示例 | 说明 |
|------|------|------|------|
| `title` | 条件必填 | `二次函数的图像与性质` | 教案标题；提供 `lesson-context` 时可省略 |
| `subject` | 条件必填 | `数学` | 学科；提供 `lesson-context` 时可省略 |
| `grade` | 条件必填 | `九年级` | 年级；提供 `lesson-context` 时可省略 |
| `template` | 否 | `standard` | 支持 `standard` 和 `5e`，默认 `standard` |
| `duration-minutes` | 否 | `45` | 课时长度，默认 45 |
| `beike-report` | 否 | `beike_report.md` | 备课报告 Markdown |
| `lesson-context` | 否 | `lesson_context.json` | Stage E 备课包生成的结构化上下文，优先级高于 `beike-report` |
| `knowledge-points` | 否 | `图像,顶点,最值` | 逗号分隔 |
| `objectives` | 否 | `理解图像性质,会求顶点` | 逗号分隔，优先级高于自动推断 |

## 推荐流程

```bash
python skills/jiaoan/scripts/generate_plan.py \
  --lesson-context lesson_package/lesson_context.json \
  --template standard \
  --duration-minutes 45 \
  --output-json lesson_plan.json \
  --output-markdown lesson_plan.md
```

若需导出 DOCX：

```bash
pip install -e ".[export]"
python skills/jiaoan/scripts/generate_plan.py \
  --title 二次函数的图像与性质 \
  --subject 数学 \
  --grade 九年级 \
  --beike-report examples/demo_beike.md \
  --output-docx lesson_plan.docx
```

## 行为规则

- 若提供 `lesson-context`，脚本会优先读取结构化的知识点、重难点、策略、活动、评价和来源上下文。
- 若提供 `beike` 报告，脚本会提取其中的知识点、重难点、策略和活动建议。
- `standard` 模板生成“导入 / 新授 / 练习 / 小结”四段式教学过程。
- `5e` 模板生成“Engage / Explore / Explain / Elaborate / Evaluate”五段式教学过程。
- 若未提供备课报告，脚本会使用 `title`、`knowledge-points` 和通用教学启发式生成可编辑草稿。
