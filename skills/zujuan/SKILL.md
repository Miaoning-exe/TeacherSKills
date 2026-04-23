---
name: zujuan
description: 根据 Question[] 题目池和约束条件自动组装 ExamPaper，并导出 Markdown 或 DOCX。
---

# 组卷 Skill

用于把 `chuti` 或其他来源生成的 `Question[]` JSON 组装成结构化试卷。输出为 `shared.schemas.ExamPaper` 兼容 JSON，可继续导出 Markdown 或 DOCX。

## 触发场景

- 教师要求“组一套试卷”“按难度分布组卷”“把这些题导出成试卷”。
- 已有题目池 JSON，需要按题型、分值、知识点覆盖、总时长组装。
- 需要生成可打印的 Markdown 或 DOCX。

## 推荐流程

1. 准备 `Question[]` JSON 文件。
2. 准备约束 JSON，格式见 `references/exam_constraints.md`。
3. 调用组卷脚本：

```bash
python skills/zujuan/scripts/assemble_exam.py \
  --questions questions.json \
  --constraints constraints.json \
  --output exam.json
```

4. 导出 Markdown：

```bash
python skills/zujuan/scripts/export_exam.py \
  --input exam.json \
  --format markdown \
  --output exam.md \
  --include-answers
```

5. 可选导出 DOCX：

```bash
python skills/zujuan/scripts/export_exam.py \
  --input exam.json \
  --format docx \
  --output exam.docx
```

DOCX 导出依赖 `python-docx`，可通过 `pip install -e ".[export]"` 安装。

## 输出约束

- 组卷输出必须是 `ExamPaper` JSON。
- 每个 section 对应一种 `QuestionType`。
- 同一张试卷中不会重复使用同一个 `question.id`。
- 如果约束无法满足，脚本应失败并说明缺少的题型或数量。

## 限制

- 当前组卷算法是确定性贪心，适合 Phase 1 的本地 MVP。
- 目前不支持 PDF 导出。
- 题目去重仅按 `question.id` 去重，不做语义去重。
