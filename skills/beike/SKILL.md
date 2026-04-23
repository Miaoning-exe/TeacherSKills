---
name: beike
description: 根据学科、年级和主题分析课标要求、知识点层次与教学策略，生成可直接用于写教案的备课报告。
---

# 备课 Skill

用于在本地完成课标对齐、知识点梳理和教学策略建议，输出教师可直接阅读和二次编辑的 Markdown 备课报告。

## 输入

| 参数 | 必填 | 示例 | 说明 |
|------|------|------|------|
| `subject` | 是 | `数学` | 学科名称 |
| `grade` | 是 | `九年级` | 年级 |
| `topic` | 是 | `二次函数` | 备课主题 |
| `keywords` | 否 | `图像,顶点,性质` | 辅助匹配的知识点关键词 |
| `output-report` | 否 | `beike_report.md` | 输出 Markdown 报告路径 |

## 推荐流程

```bash
python skills/beike/scripts/analyze_curriculum.py \
  --subject 数学 \
  --grade 九年级 \
  --topic 二次函数 \
  --keywords 图像,顶点,性质 \
  --output-report beike_report.md
```

## 行为规则

- 仅使用本地 `references/curriculum_standards.md` 进行课标匹配，不依赖联网数据。
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
