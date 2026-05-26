# 组卷 DOCX 模板资产

Stage E 第一版使用 `build_exam_package.py` 根据 `TemplateProfile` 确定性生成四类 DOCX：

- `试卷.docx`
- `答题卡.docx`
- `参考答案.docx`
- `评分细则.docx`

当前目录记录模板资产约定。后续若引入可编辑 `.docx` 模板，应保持文件名与 `TemplateProfile.required_outputs` 对齐，并继续由脚本负责题号、分值和来源一致性校验。
