# 专业组卷演示

本示例演示 Stage E 的资料增强组卷流程：使用资料包、题库和模板 profile 生成正式试卷包。

## 输入

- 资料包：`examples/sample_data/research_dossier_math_exam.json`
- 题库：`examples/sample_data/sample_questions.json`
- 模板 profile：`skills/zujuan/assets/profiles/math_junior_standard.json`

## 命令

```bash
python skills/zujuan/scripts/build_exam_package.py \
  --research examples/sample_data/research_dossier_math_exam.json \
  --questions examples/sample_data/sample_questions.json \
  --profile skills/zujuan/assets/profiles/math_junior_standard.json \
  --output-dir examples_output/exam_package
```

## 输出目录

```text
examples_output/exam_package/
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

## 说明

当前 `math_junior_standard` profile 是样例版，题量与 `sample_questions.json` 中的数学题保持一致，便于本地测试和演示。真实 100/120 分试卷可以沿用相同结构，扩展 profile 中的题量、分值和题库即可。
