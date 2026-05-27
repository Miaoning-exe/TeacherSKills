# Stage E 专业批改包演示

先运行 E2 生成 `examples_output\exam_package\exam.json`，再运行：

```powershell
.\.venv\Scripts\python.exe skills\gaijuan\scripts\build_grading_package.py `
  --exam examples_output\exam_package\exam.json `
  --answers examples\sample_data\sample_math_student_answers.json `
  --research examples\sample_data\research_dossier_math_exam.json `
  --output-dir examples_output\grading_package
```

输出：

```text
grading_package/
  批改报告.docx
  graded_responses.json
  score_report.md
  主观题待复核清单.json
  package.json
  sources.md
```
