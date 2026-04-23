---
name: chuti
description: 按学科、知识点、题型、难度和数量生成符合 TeacherSkills Question schema 的练习题。
---

# 出题 Skill

用于语文、数学、英语三科的本地出题。输出必须是 `shared.schemas.Question` 兼容的 JSON，便于后续交给 `zujuan` 组卷 Skill。

## 触发场景

- 教师要求“出几道题”“生成练习题”“按知识点出题”。
- 教师指定学科、年级、知识点、题型、难度、数量。
- 需要把题目导出为结构化 JSON。

## 输入参数

| 参数 | 必填 | 示例 | 说明 |
|------|------|------|------|
| `subject` | 是 | `数学` | 支持 `数学`、`语文`、`英语` |
| `knowledge-points` | 是 | `二次函数,图像性质` | 逗号分隔的知识点 ID 或名称 |
| `question-type` | 是 | `选择题` | 见 `references/question_types.md` |
| `difficulty` | 是 | `中` | 支持 `易`、`中`、`难` |
| `count` | 否 | `5` | 默认 1 |
| `grade` | 否 | `九年级` | 默认不写入题目字段，仅用于内容提示 |
| `score` | 否 | `5` | 默认 1 |

## 推荐流程

1. 读取 `references/question_types.md` 确认题型定义。
2. 按学科读取对应参考模板：
   - 数学：`references/math_patterns.md`
   - 语文：`references/chinese_patterns.md`
   - 英语：`references/english_patterns.md`
3. 调用脚本生成结构化 JSON：

```bash
python skills/chuti/scripts/gen_question.py \
  --subject 数学 \
  --knowledge-points "二次函数的图像与性质" \
  --question-type 选择题 \
  --difficulty 中 \
  --count 3 \
  --output questions.json
```

4. 校验输出：

```bash
python skills/chuti/scripts/validate_question.py questions.json
```

## 输出约束

- 输出是 `Question[]` JSON 数组。
- 每道题必须包含 `id`、`content`、`subject`、`question_type`、`difficulty`、`knowledge_points`、`answer`、`score`。
- 选择题必须包含 `options`。
- 阅读理解、完形填空、文言文题建议包含 `material`。
- 数学公式使用 LaTeX，行内公式写作 `$...$`。

## 限制

当前脚本是本地模板生成器，适合生成结构化草稿和测试数据。需要高质量原创题目时，Agent 应结合参考模板进一步润色，并继续使用 `validate_question.py` 校验输出。
