---
name: gaijuan
description: 批改学生作答。客观题本地评分，主观题通过 TeacherSkills API 评分，离线时标记待评分。
---

# 批改 Skill

用于根据 `ExamPaper` 和学生作答数据生成 `StudentResponse[]` 结果。Stage E 起优先输出正式批改包，包含结构化批改结果、批改报告、主观题待复核清单和 `sources.md`。

## Stage E 资料增强要求

- 评分依据、考试要求和复核提示应来自 `ResearchDossier` 兼容资料包。
- 批改脚本不做 web search，只消费结构化资料包、试卷和学生作答。
- 主观题离线时必须进入待复核清单，不应伪装成已完成评分。

## 输入

- `ExamPaper` JSON
- 学生作答 JSON（`student_id`、`question_id`、`answer`）
- 可选评分标准文件（主观题随请求发送给远程 API）
- 可选 `ResearchDossier` JSON，用于生成 `sources.md` 和复核依据

## 推荐流程

1. 优先生成正式批改包。下面命令假设已先运行 E2 生成 `examples_output\exam_package\exam.json`：

```powershell
.\.venv\Scripts\python.exe skills\gaijuan\scripts\build_grading_package.py `
  --exam examples_output\exam_package\exam.json `
  --answers examples\sample_data\sample_math_student_answers.json `
  --research examples\sample_data\research_dossier_math_exam.json `
  --output-dir examples_output\grading_package
```

输出目录包含：

```text
grading_package/
  批改报告.docx
  graded_responses.json
  score_report.md
  主观题待复核清单.json
  package.json
  sources.md
```

2. 保留旧的单步批改：

```powershell
.\.venv\Scripts\python.exe skills\gaijuan\scripts\grade_answers.py `
  --exam examples_output\exam_package\exam.json `
  --answers examples\sample_data\sample_math_student_answers.json `
  --offline `
  --output examples_output\graded_responses.json
```

3. 保留旧的成绩报告：

```powershell
.\.venv\Scripts\python.exe skills\gaijuan\scripts\score_report.py `
  --exam examples_output\exam_package\exam.json `
  --responses examples_output\graded_responses.json `
  --output examples_output\score_report.md
```

## 行为规则

- 客观题：本地精确匹配，正确得满分，错误得 0 分。
- 主观题：调用 `shared/api_client.py` 请求 `POST /api/grade`。
- API 不可用、Token 缺失或显式 `--offline` 时：主观题保留 `score=null`，`feedback` 写明“待评分”。
- 正式批改包必须包含主观题待复核清单，便于教师二次确认。

## 当前支持的作答输入格式

```json
[
  {
    "student_id": "stu_001",
    "question_id": "sample_math_choice_01",
    "answer": "A"
  }
]
```
