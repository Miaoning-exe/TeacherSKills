# 完整工作流演示

本示例串联 Stage A 的两个核心能力：先出题，再组卷。

## 1. 生成题目池

```bash
python skills/chuti/scripts/gen_question.py \
  --subject 数学 \
  --knowledge-points "二次函数的图像与性质" \
  --question-type 选择题 \
  --difficulty 中 \
  --count 2 \
  --output examples_output/workflow_choice.json
```

```bash
python skills/chuti/scripts/gen_question.py \
  --subject 数学 \
  --knowledge-points "二次函数顶点坐标" \
  --question-type 填空题 \
  --difficulty 中 \
  --count 1 \
  --output examples_output/workflow_fill.json
```

```bash
python skills/chuti/scripts/gen_question.py \
  --subject 数学 \
  --knowledge-points "二次函数的图像与性质" \
  --question-type 应用题 \
  --difficulty 难 \
  --count 1 \
  --output examples_output/workflow_application.json
```

将三个 JSON 文件合并为一个 `Question[]` 数组后，再执行组卷。当前仓库尚未提供专门的合并脚本，最简单的方式是手动整理，或直接使用 `examples/sample_data/sample_questions.json` 里的数学题作为现成题目池。

## 2. 准备约束

```json
{
  "title": "九年级数学综合练习",
  "subject": "数学",
  "grade": "九年级",
  "duration_minutes": 45,
  "sections": [
    {
      "question_type": "选择题",
      "count": 2,
      "score_per_question": 3
    },
    {
      "question_type": "填空题",
      "count": 1,
      "score_per_question": 4
    },
    {
      "question_type": "应用题",
      "count": 1,
      "score_per_question": 10
    }
  ],
  "required_knowledge_points": [
    "math_quad_graph",
    "math_quad_vertex"
  ]
}
```

## 3. 组卷并导出

```bash
python skills/zujuan/scripts/assemble_exam.py \
  --questions examples/sample_data/sample_questions.json \
  --constraints constraints.json \
  --output examples_output/workflow_exam.json
```

```bash
python skills/zujuan/scripts/export_exam.py \
  --input examples_output/workflow_exam.json \
  --format markdown \
  --output examples_output/workflow_exam.md \
  --include-answers
```

## 4. 结果检查

- `workflow_exam.json` 应符合 `ExamPaper` schema。
- `workflow_exam.md` 应包含试卷头部、分卷标题、题干和参考答案。
- 如需 DOCX，安装 `python-docx` 后将 `--format markdown` 改为 `--format docx`。
