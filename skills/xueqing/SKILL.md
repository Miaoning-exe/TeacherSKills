---
name: xueqing
description: 根据 StudentResponse[] 调用诊断 API，输出 KnowledgeMastery[]、学情报告和可视化图表。
---

# 学情分析 Skill

用于将批改结果转换为教师可读的学情报告，并输出结构化 `KnowledgeMastery[]` 供后续定向出题或教学调整使用。Stage E 起优先输出正式学情包。

## Stage E 资料增强要求

- 学情包应保留 `ResearchDossier` 来源清单，说明本次诊断依据来自哪套试卷、题型或教学目标。
- 学情分析脚本不做 web search，只消费批改结果、知识点、题目映射和资料包。
- 补救建议必须以结构化 `remediation_plan.json` 输出，方便后续交给 `chuti` 或 `beike`。

## 输入

- `StudentResponse[]` JSON
- `KnowledgePoint[]` JSON
- 可选 `Question[]` JSON，用于提供题目到知识点的精确映射，建议传入
- 可选图表输出目录
- 可选 `ResearchDossier` JSON，用于生成 `sources.md`

## 推荐流程

```powershell
.\.venv\Scripts\python.exe skills\xueqing\scripts\build_learning_package.py `
  --responses examples\sample_data\sample_student_responses.json `
  --knowledge-points examples\sample_data\math_knowledge_points.json `
  --questions examples\sample_data\sample_questions.json `
  --research examples\sample_data\research_dossier_math_exam.json `
  --output-dir examples_output\learning_package
```

输出目录包含：

```text
learning_package/
  班级学情报告.docx
  学生个人诊断报告.docx
  补救练习建议.docx
  mastery.json
  learning_report.md
  remediation_plan.json
  package.json
  sources.md
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
- 正式学情包会额外输出班级报告、学生个人诊断和补救练习建议三类 DOCX。
