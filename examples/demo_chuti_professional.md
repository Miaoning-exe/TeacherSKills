# Stage E 专业出题演示

本演示使用两个结构化输入：

- 资料包：`examples\sample_data\research_dossier_math_exam.json`
- 考试样式：`skills\zujuan\assets\profiles\math_junior_standard.json`

运行：

```powershell
.\.venv\Scripts\python.exe skills\chuti\scripts\gen_question.py `
  --research-dossier examples\sample_data\research_dossier_math_exam.json `
  --profile skills\zujuan\assets\profiles\math_junior_standard.json `
  --output-dir examples_output\question_package
```

校验：

```powershell
.\.venv\Scripts\python.exe skills\chuti\scripts\validate_question.py `
  examples_output\question_package\questions.json
```

输出：

```text
question_package/
  questions.json
  sources.md
  package.json
```

`questions.json` 中每道题的 `metadata` 会记录来源 ID、来源依据、难度理由、考试样式 ID 和教师复核提示。
