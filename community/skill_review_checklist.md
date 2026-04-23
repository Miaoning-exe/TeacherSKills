# Skill 贡献检查清单

提交新 Skill 前，请确认：

- 已阅读 `CLUADE.md`，并同步更新相关 wiki。
- Skill 目录名使用小写拼音或英文，不使用中文路径。
- `SKILL.md` 包含触发场景、输入、推荐流程、输出约束和限制。
- 核心逻辑放在 `scripts/`，参考资料放在 `references/` 或 `assets/`。
- 新增结构化数据时，使用 Pydantic v2 模型。
- 新增或修改脚本时，添加对应 `tests/test_*.py`。
- 提供最小样例数据或演示文档。
- `python3 -m pytest tests` 通过。
- 不提交学生隐私数据、API Token、学校内部敏感资料或受版权限制的教材全文。
