# 贡献指南

## 环境准备

```bash
pip install -e ".[dev]"
```

如需验证 DOCX 导出或 MCP：

```bash
pip install -e ".[export]"
python3 -m mcp_server.stdio_server
```

## 代码规范

- Python >= 3.10，类型标注必须完整
- 数据模型使用 Pydantic v2
- 命名规范见 [wiki/06-conventions.md](wiki/06-conventions.md)
- 改代码必须同步更新 wiki，遵循 `CLUADE.md`

## 目录约定

- `skills/<skill_name>/SKILL.md`：Skill 定义与使用说明
- `skills/<skill_name>/scripts/`：核心逻辑脚本
- `skills/<skill_name>/references/` 或 `assets/`：本地参考资料或模板
- `shared/schemas/`：跨 Skill 共享的 Pydantic 模型
- `examples/`：样例输入/输出与演示文档
- `tests/`：对应测试

## 新增 Skill

推荐从 `community/skill_template/` 复制最小模板，再按实际场景补全。

新增 Skill 至少需要：

- `SKILL.md`
- `scripts/` 中的可执行脚本
- 必要的 `references/` 或 `assets/`
- 最小样例数据或 demo 文档
- 对应测试
- wiki 同步更新

若新增结构化数据：

- 优先复用 `shared/schemas/` 现有模型
- 若必须新增 schema，请同步补：
  - 模型文件
  - `tests/test_schemas.py`
  - 样例 JSON

## 测试要求

提交前至少执行：

```bash
python3 -m pytest tests
```

仓库已提供 GitHub Actions CI，会在 PR 中自动执行：

- `pip install -e ".[dev]"`
- `python3 -m pytest tests`
- MCP stdio 初始化冒烟

若改动 MCP server，额外确认：

```bash
python3 -m pytest tests/test_mcp_server.py
printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python3 -m mcp_server.stdio_server
```

## 文档要求

- 任何功能性改动都要同步更新对应 wiki
- 新增 Stage/模块时，优先补对应 `wiki/*.md`
- README 只保留高层入口，用法细节放到 wiki/开发指南
- 若新增社区入口、模板或样例，也要写入 `CONTRIBUTING.md`

## 提交 PR

1. Fork 仓库，基于 `main` 创建功能分支
2. 确保 `python3 -m pytest tests` 全部通过
3. 若改动文档导出或 MCP，请写清额外验证方式
4. PR 描述说明改动原因、测试方式和受影响的 wiki

## PR 自检

提交前建议逐项核对 `community/skill_review_checklist.md`。
