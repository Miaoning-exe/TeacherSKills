# Stage E 专业评语包演示

```powershell
.\.venv\Scripts\python.exe skills\pingyu\scripts\build_comment_package.py `
  --responses examples\sample_data\sample_student_responses.json `
  --mastery examples\sample_data\sample_knowledge_mastery.json `
  --knowledge-points examples\sample_data\math_knowledge_points.json `
  --observations examples\sample_data\sample_teacher_observations.json `
  --research examples\sample_data\research_dossier_math_beike.json `
  --term 期末 `
  --output-dir examples_output\comment_package
```

输出：

```text
comment_package/
  学生评语.docx
  student_comments.json
  student_comments.md
  评语复核清单.json
  package.json
  sources.md
```
