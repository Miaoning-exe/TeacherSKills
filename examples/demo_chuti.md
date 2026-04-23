# 出题演示

本示例展示如何使用 `chuti` 生成结构化题目，并校验输出是否符合 `Question[]` schema。

## 目标

- 学科：数学
- 年级：九年级
- 知识点：二次函数的图像与性质
- 题型：选择题
- 难度：中
- 数量：3

## 命令

```bash
python skills/chuti/scripts/gen_question.py \
  --subject 数学 \
  --knowledge-points "二次函数的图像与性质" \
  --question-type 选择题 \
  --difficulty 中 \
  --count 3 \
  --output examples_output/demo_chuti_questions.json
```

```bash
python skills/chuti/scripts/validate_question.py \
  examples_output/demo_chuti_questions.json
```

## 预期结果

- 输出文件为 `Question[]` JSON。
- 每道题都带有 `id`、`answer`、`explanation`、`score`。
- 选择题包含 `options` 字段。

## 可直接使用的示例数据

- 知识点样例：`examples/sample_data/math_knowledge_points.json`
- 跨学科题目池：`examples/sample_data/sample_questions.json`
