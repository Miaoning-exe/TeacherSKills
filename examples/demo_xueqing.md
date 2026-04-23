# 学情分析演示

本示例展示如何从 `StudentResponse[]` 生成 `KnowledgeMastery[]` 和 Markdown 学情报告。

## 输入文件

- 批改结果：`examples/sample_data/sample_student_responses.json`
- 知识点：`examples/sample_data/math_knowledge_points.json`
- 题目映射：`examples/sample_data/sample_questions.json`

## 命令

```bash
python skills/xueqing/scripts/analyze_learning.py \
  --responses examples/sample_data/sample_student_responses.json \
  --knowledge-points examples/sample_data/math_knowledge_points.json \
  --questions examples/sample_data/sample_questions.json \
  --output-mastery examples_output/sample_knowledge_mastery.json \
  --output-report examples_output/sample_learning_report.md \
  --chart-dir examples_output/charts \
  --offline
```

## 结果

- `sample_knowledge_mastery.json`：结构化掌握度数据
- `sample_learning_report.md`：教师可直接阅读的学情报告
- `charts/`：若环境中 `matplotlib` 可用，则输出热力图和学生图表

## 注意

- 本地离线模式依赖 `--questions` 提供题目到知识点的映射。
- 若 `matplotlib` 与本地 `NumPy` 环境不兼容，脚本会跳过图表生成，但不会影响报告和数据输出。
