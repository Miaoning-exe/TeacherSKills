---
name: pingyu
description: 根据批改结果、学情掌握度和教师观察批量生成个性化学生评语，并导出为 JSON、Markdown 或 DOCX。
---

# 评语 Skill

用于学期末或阶段性评价时批量生成学生评语。输入以 `StudentResponse[]`、`KnowledgeMastery[]` 为主，可叠加教师观察信息，让评语既有数据依据，也保留教师口吻。

## 输入

| 参数 | 必填 | 示例 | 说明 |
|------|------|------|------|
| `responses` | 是 | `sample_student_responses.json` | 批改结果 |
| `mastery` | 是 | `sample_knowledge_mastery.json` | 学情掌握度 |
| `knowledge-points` | 是 | `math_knowledge_points.json` | 用于把知识点 ID 转成教师可读名称 |
| `observations` | 否 | `sample_teacher_observations.json` | 教师补充观察 |
| `term` | 否 | `期末` | 评语场景，可写 `阶段性` |

## 推荐流程

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

若需要 DOCX 导出：

```bash
pip install -e ".[export]"
python skills/pingyu/scripts/generate_comment.py \
  --responses examples/sample_data/sample_student_responses.json \
  --mastery examples/sample_data/sample_knowledge_mastery.json \
  --knowledge-points examples/sample_data/math_knowledge_points.json \
  --observations examples/sample_data/sample_teacher_observations.json \
  --output-docx student_comments.docx
```

## 行为规则

- 评语默认遵循“积极鼓励为主 + 委婉指出不足 + 给出成长期待”。
- 若有教师观察，会优先使用学生姓名、习惯表现、教师主观印象等信息。
- 若缺少教师观察，脚本仍可基于得分率和掌握度生成可编辑草稿。
- 输出支持：
  - `StudentComment[]` JSON
  - 批量 Markdown
  - DOCX
