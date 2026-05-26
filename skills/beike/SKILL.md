---
name: beike
description: 根据学科、年级和主题分析课标要求、知识点层次与教学策略，生成可直接用于写教案的备课报告。
---

# 备课 Skill

用于在本地完成课标对齐、知识点梳理和教学策略建议，输出教师可直接阅读和二次编辑的 Markdown 备课报告。

## Stage E 资料增强要求

- Agent 在生成备课报告前应先检索并筛选课标、教材、课例、常见误区和课堂活动资料。
- 检索结论必须整理为 `ResearchDossier` 兼容的 `research_dossier.json`，来源字段见 `shared.schemas.research`。
- 资料增强产物必须同步生成 `sources.md`，可用：

```bash
python -m shared.tools.sources research_dossier.json --output sources.md
```

- 若无法联网或没有资料包，允许退化为本地参考生成，但报告和来源文件必须标记为“本地模板草稿”。

## 输入

| 参数 | 必填 | 示例 | 说明 |
|------|------|------|------|
| `subject` | 是 | `数学` | 学科名称 |
| `grade` | 是 | `九年级` | 年级 |
| `topic` | 是 | `二次函数` | 备课主题 |
| `keywords` | 否 | `图像,顶点,性质` | 辅助匹配的知识点关键词 |
| `research-dossier` | 否 | `research_dossier.json` | Agent 检索后生成的资料包，当前脚本尚未直接消费时应作为人工复核依据 |
| `output-report` | 否 | `beike_report.md` | 输出 Markdown 报告路径 |

## 推荐流程

1. Agent 先检索并整理资料包。
2. 渲染来源清单：

```bash
python -m shared.tools.sources research_dossier.json --output sources.md
```

3. 调用本地备课脚本生成结构化草稿：

```bash
python skills/beike/scripts/analyze_curriculum.py \
  --subject 数学 \
  --grade 九年级 \
  --topic 二次函数 \
  --keywords 图像,顶点,性质 \
  --output-report beike_report.md
```

## 行为规则

- 优先使用 Agent 检索形成的 `ResearchDossier` 作为备课依据，并保留 `sources.md` 供教师复核。
- 本地 `references/curriculum_standards.md` 是无网络或无资料包时的降级来源，不应伪装成实时检索结果。
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
