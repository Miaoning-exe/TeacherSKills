# Stage E 专业学情包演示

```powershell
.\.venv\Scripts\python.exe skills\xueqing\scripts\build_learning_package.py `
  --responses examples\sample_data\sample_student_responses.json `
  --knowledge-points examples\sample_data\math_knowledge_points.json `
  --questions examples\sample_data\sample_questions.json `
  --research examples\sample_data\research_dossier_math_exam.json `
  --output-dir examples_output\learning_package
```

输出：

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
