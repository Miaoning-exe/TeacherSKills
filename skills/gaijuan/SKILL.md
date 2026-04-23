---
name: gaijuan
description: 批改学生作答。客观题本地评分，主观题通过 TeacherSkills API 评分，离线时标记待评分。
---

# 批改 Skill

用于根据 `ExamPaper` 和学生作答数据生成 `StudentResponse[]` 结果，并可进一步导出成绩报告。

## 输入

- `ExamPaper` JSON
- 学生作答 JSON（`student_id`、`question_id`、`answer`）
- 可选评分标准文件（主观题随请求发送给远程 API）

## 推荐流程

1. 本地批改：

```bash
python skills/gaijuan/scripts/grade_answers.py \
  --exam exam.json \
  --answers student_answers.json \
  --output graded_responses.json
```

2. 强制离线模式：

```bash
python skills/gaijuan/scripts/grade_answers.py \
  --exam exam.json \
  --answers student_answers.json \
  --offline \
  --output graded_responses.json
```

3. 生成成绩报告：

```bash
python skills/gaijuan/scripts/score_report.py \
  --exam exam.json \
  --responses graded_responses.json \
  --output score_report.md
```

## 行为规则

- 客观题：本地精确匹配，正确得满分，错误得 0 分。
- 主观题：调用 `shared/api_client.py` 请求 `POST /api/grade`。
- API 不可用、Token 缺失或显式 `--offline` 时：主观题保留 `score=null`，`feedback` 写明“待评分”。

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
