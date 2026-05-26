---
name: zujuan
description: 根据 Question[]、资料包和模板 profile 组装 ExamPaper，并生成正式试卷包或单文件导出。
---

# 组卷 Skill

用于把 `chuti` 或其他来源生成的 `Question[]` JSON 组装成结构化试卷。Stage E 起优先输出正式试卷包，包含试卷、答题卡、参考答案、评分细则、结构化 JSON 和 `sources.md`。

## Stage E 资料增强要求

- Agent 在组卷前应先检索或整理课标、考试说明、样卷结构、题型比例、评分细则和模板要求。
- 检索资料必须进入 `ResearchDossier` 兼容的 `research_dossier.json`，并渲染 `sources.md` 供教师复核。
- 组卷脚本负责确定性组装和一致性校验；Agent 负责判断资料是否适配学科、学段和考试类型。
- 无资料包时允许使用本地约束文件降级组卷，但产物必须标记为“本地模板草稿”。

## 触发场景

- 教师要求“组一套试卷”“按难度分布组卷”“把这些题导出成试卷”。
- 已有题目池 JSON，需要按题型、分值、知识点覆盖、总时长组装。
- 需要生成可打印的 Markdown 或 DOCX。

## 推荐流程

1. Agent 先检索课标、样卷、考试说明和评分要求，形成 `research_dossier.json`。
2. 渲染来源清单：

```bash
python -m shared.tools.sources research_dossier.json --output sources.md
```

3. 准备 `Question[]` JSON 文件和模板 profile。
4. 优先生成正式试卷包：

```bash
python skills/zujuan/scripts/build_exam_package.py \
  --research research_dossier.json \
  --questions questions.json \
  --profile skills/zujuan/assets/profiles/math_junior_standard.json \
  --output-dir exam_package
```

输出目录包含：

```text
exam_package/
  试卷.docx
  答题卡.docx
  参考答案.docx
  评分细则.docx
  exam.json
  blueprint.json
  answer_sheet.json
  answer_key.json
  scoring_rubric.json
  package.json
  sources.md
```

5. 若只需要旧版单文件输出，可准备约束 JSON，格式见 `references/exam_constraints.md`，再调用组卷脚本：

```bash
python skills/zujuan/scripts/assemble_exam.py \
  --questions questions.json \
  --constraints constraints.json \
  --output exam.json
```

6. 导出 Markdown：

```bash
python skills/zujuan/scripts/export_exam.py \
  --input exam.json \
  --format markdown \
  --output exam.md \
  --include-answers
```

7. 可选导出 DOCX：

```bash
python skills/zujuan/scripts/export_exam.py \
  --input exam.json \
  --format docx \
  --output exam.docx
```

DOCX 导出依赖 `python-docx`，可通过 `pip install -e ".[export]"` 安装。

## 输出约束

- 组卷输出必须是 `ExamPaper` JSON。
- 正式试卷包必须包含试卷、答题卡、参考答案、评分细则、`exam.json`、`blueprint.json` 和 `sources.md`。
- 试卷、答题卡、答案、评分细则中的题号必须一致。
- 小题分值、分卷分值、试卷总分和蓝图总分必须一致。
- 每个 section 对应一种 `QuestionType`。
- 同一张试卷中不会重复使用同一个 `question.id`。
- 如果约束无法满足，脚本应失败并说明缺少的题型或数量。

## 限制

- 当前组卷算法是确定性贪心，适合 Phase 1 的本地 MVP。
- Stage E 第一版 profile 是初中数学样例版，适配当前样例题库；真实 100/120 分试卷可扩展 profile 题量和分值，不需要改变包生成接口。
- 目前不支持 PDF 导出。
- 题目去重仅按 `question.id` 去重，不做语义去重。
