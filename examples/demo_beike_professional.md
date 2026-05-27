# Stage E 专业备课包演示

输入资料包：

- `examples/sample_data/research_dossier_math_beike.json`

生成命令：

```powershell
.\.venv\Scripts\python.exe skills\beike\scripts\build_lesson_package.py `
  --research examples\sample_data\research_dossier_math_beike.json `
  --output-dir examples_output\lesson_package
```

输出目录：

```text
lesson_package/
  备课分析.docx
  教学设计.docx
  课堂活动单.docx
  配套练习.docx
  lesson_context.json
  lesson_plan.json
  package.json
  sources.md
```

`lesson_context.json` 是备课分析与教案生成之间的结构化中间数据，可继续交给 `jiaoan`：

```powershell
.\.venv\Scripts\python.exe skills\jiaoan\scripts\generate_plan.py `
  --lesson-context examples_output\lesson_package\lesson_context.json `
  --output-markdown examples_output\lesson_plan.md
```
