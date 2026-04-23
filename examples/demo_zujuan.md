# 组卷演示

本示例展示如何从样例题目池中挑选数学题，组装成一份简单试卷并导出 Markdown。

## 题目池

使用仓库内样例题目：

`examples/sample_data/sample_questions.json`

组卷脚本会根据 `subject` 自动忽略语文、英语题目，只选择数学题目。

## 约束示例

将以下内容保存为 `constraints.json`：

```json
{
  "title": "九年级数学二次函数练习",
  "subject": "数学",
  "grade": "九年级",
  "duration_minutes": 40,
  "sections": [
    {
      "title": "一、选择题",
      "question_type": "选择题",
      "count": 1,
      "score_per_question": 3
    },
    {
      "title": "二、填空题",
      "question_type": "填空题",
      "count": 1,
      "score_per_question": 4
    },
    {
      "title": "三、应用题",
      "question_type": "应用题",
      "count": 1,
      "score_per_question": 10
    }
  ],
  "difficulty_distribution": {
    "易": 0.34,
    "中": 0.33,
    "难": 0.33
  },
  "required_knowledge_points": [
    "math_quad_graph",
    "math_quad_vertex"
  ]
}
```

## 命令

```bash
python skills/zujuan/scripts/assemble_exam.py \
  --questions examples/sample_data/sample_questions.json \
  --constraints constraints.json \
  --output examples_output/demo_exam.json
```

```bash
python skills/zujuan/scripts/export_exam.py \
  --input examples_output/demo_exam.json \
  --format markdown \
  --output examples_output/demo_exam.md \
  --include-answers
```

## 预期结果

- 输出 `ExamPaper` JSON。
- Markdown 中按分卷列题，并附带参考答案。
- 不会重复使用同一个 `question.id`。
