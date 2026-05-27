---
name: beike
description: 根据学科、年级和主题分析课标要求、知识点层次与教学策略，生成可直接用于写教案的备课报告。
---

# 备课 Skill

用于在本地完成课标对齐、知识点梳理和教学策略建议，输出教师可直接阅读和二次编辑的正式备课包。

## Stage E 资料增强要求

- Agent 在生成备课报告前应先检索并筛选课标、教材、课例、常见误区和课堂活动资料。
- 检索结论必须整理为 `ResearchDossier` 兼容的 `research_dossier.json`，来源字段见 `shared.schemas.research`。
- 资料增强产物必须同步生成 `sources.md`，可用：

```powershell
.\.venv\Scripts\python.exe -m shared.tools.sources `
  examples\sample_data\research_dossier_math_beike.json `
  --output examples_output\sources_beike.md
```

- 若无法联网或没有资料包，允许退化为本地参考生成，但报告和来源文件必须标记为“本地模板草稿”。

## 输入

| 参数 | 必填 | 示例 | 说明 |
|------|------|------|------|
| `subject` | 是 | `数学` | 学科名称 |
| `grade` | 是 | `九年级` | 年级 |
| `topic` | 是 | `二次函数` | 备课主题 |
| `keywords` | 否 | `图像,顶点,性质` | 辅助匹配的知识点关键词 |
| `research-dossier` | 否 | `research_dossier.json` | Agent 检索后生成的资料包，脚本会直接消费并写入来源事实、Agent 推理和复核提示 |
| `output-report` | 否 | `beike_report.md` | 输出 Markdown 报告路径 |

## 推荐流程

1. Agent 先检索并整理资料包。
2. 渲染来源清单：

```powershell
.\.venv\Scripts\python.exe -m shared.tools.sources `
  examples\sample_data\research_dossier_math_beike.json `
  --output examples_output\sources_beike.md
```

3. 调用本地备课脚本生成结构化草稿：

```powershell
.\.venv\Scripts\python.exe skills\beike\scripts\analyze_curriculum.py `
  --subject 数学 `
  --grade 九年级 `
  --topic 二次函数 `
  --keywords 图像,顶点,性质 `
  --research-dossier examples\sample_data\research_dossier_math_beike.json `
  --output-report examples_output\beike_report.md
```

4. 若需要正式备课包，生成：

```powershell
.\.venv\Scripts\python.exe skills\beike\scripts\build_lesson_package.py `
  --research examples\sample_data\research_dossier_math_beike.json `
  --output-dir examples_output\lesson_package
```

输出目录包含：

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

## 行为规则

- 优先使用 Agent 检索形成的 `ResearchDossier` 作为备课依据，并保留 `sources.md` 供教师复核。
- 本地 `references/curriculum_standards.md` 是无网络或无资料包时的降级来源，不应伪装成实时检索结果。
- `lesson_context.json` 是备课到教案之间的结构化中间数据，后续 `jiaoan` 可直接读取。
- 认知层次按照 `references/bloom_taxonomy.md` 中的 Bloom 分类法组织。
- 输出报告默认包含：
  - 课标对齐结论
  - 知识点梳理
  - 认知层次分析
  - 教学重点与难点
  - 常见误区
  - 教学策略与课堂活动建议
  - 形成性评价建议
- 若主题没有完全命中，脚本会退化为同学科同年级的相近条目，并在报告中明确提示。
- 报告中的来源事实、Agent 推理和教师待复核内容应明确区分。
