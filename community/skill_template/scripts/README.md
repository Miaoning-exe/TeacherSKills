# scripts/

放置 Skill 的可执行 Python 脚本。

要求：

- Python >= 3.10
- 使用类型标注
- CLI 参数必须有 `--help`
- 读取和输出 JSON 时必须经 Pydantic schema 校验
- 新增脚本必须在 `tests/` 中覆盖成功路径和失败路径
