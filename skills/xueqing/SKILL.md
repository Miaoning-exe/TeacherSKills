---
name: xueqing
description: 根据 StudentResponse[] 调用诊断 API，输出 KnowledgeMastery[]、学情报告和可视化图表。
---

# 学情分析 Skill

用于将批改结果转换为教师可读的学情报告，并输出结构化 `KnowledgeMastery[]` 供后续定向出题或教学调整使用。

## 输入

- `StudentResponse[]` JSON
- `KnowledgePoint[]` JSON
- 可选 `Question[]` JSON，用于提供题目到知识点的精确映射，建议传入
- 可选图表输出目录

## 推荐流程

```bash
python skills/xueqing/scripts/analyze_learning.py \
  --responses examples/sample_data/sample_student_responses.json \
  --knowledge-points examples/sample_data/math_knowledge_points.json \
  --questions examples/sample_data/sample_questions.json \
  --output-mastery mastery.json \
  --output-report report.md \
  --chart-dir charts
```

## 行为规则

- 默认尝试调用 `POST /api/diagnosis`。
- 当 Token 缺失、网络失败或显式 `--offline` 时，脚本退化为本地启发式估计，不阻塞输出。
- 离线启发式分析强烈建议传入 `--questions`，否则只能做保守估计。
- 报告会生成：
  - 班级整体知识点掌握概览
  - 每个学生的薄弱知识点
  - 定向补救建议
- 若安装了 `matplotlib` 且传入 `--chart-dir`，会生成热力图与按学生条形图。
