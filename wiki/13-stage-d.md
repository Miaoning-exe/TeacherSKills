<!-- Last verified: 2026-04-18 | Current stage: D -->

# Stage D — MCP Server + 社区化

## 功能汇总

| # | 功能 | 状态 | 备注 |
|---|------|------|------|
| D1 | MCP Server 封装 | ✅ | stdio MCP server，封装 7 个核心 tools |
| D2 | 社区贡献规范 | ✅ | 模板、检查清单、扩展版贡献指南 |

---

## D1: MCP Server 封装

### 用户场景

开发者希望不直接调用本地脚本，而是通过 MCP 协议把 TeacherSkills 接入 Claude Code、IDE 或其他支持 MCP 的客户端。

### 设计决策

| 决策点 | 选择 | 原因 | 放弃的方案 |
|--------|------|------|-----------|
| 传输方式 | stdio | 与 MCP 客户端最常见接入方式一致，部署最轻 | HTTP transport（实现复杂度更高） |
| 协议范围 | `initialize` + `tools/list` + `tools/call` 最小闭环 | 先满足可用性，后续再扩资源/提示词等能力 | 一次性实现全协议 |
| 工具覆盖 | 封装现有 7 个 Skill | 与现有能力一一对应，便于维护 | 只暴露部分功能 |
| 远程调用默认值 | MCP 内默认走离线/本地路径 | 减少 API Token 和网络依赖 | 默认远程，首次接入即报错 |

### 受影响文件

| 文件 | 改动类型 | 说明 |
|------|---------|------|
| `mcp_server/stdio_server.py` | 新增 | stdio MCP server 与 tool registry |
| `mcp_server/__init__.py` | 新增 | 包入口 |
| `tests/test_mcp_server.py` | 新增 | initialize、tools/list、tools/call 和 stdio 测试 |
| `examples/mcp_config.json` | 新增 | MCP 客户端配置样例 |
| `pyproject.toml` | 修改 | 暴露 `teacherskills-mcp` 启动命令 |

### 当前实现

- 协议：
  - `initialize`
  - `tools/list`
  - `tools/call`
  - `notifications/*` 忽略处理
- 已封装 tools：
  - `teacherskills.chuti.generate_questions`
  - `teacherskills.zujuan.assemble_exam`
  - `teacherskills.gaijuan.grade_answers`
  - `teacherskills.xueqing.analyze_learning`
  - `teacherskills.beike.analyze_curriculum`
  - `teacherskills.jiaoan.generate_plan`
  - `teacherskills.pingyu.generate_comments`
- 返回格式：
  - 成功：`content` 文本数组
  - 失败：`isError: true`

### 推荐启动方式

```bash
python3 -m mcp_server.stdio_server
```

或：

```bash
teacherskills-mcp
```

---

## D2: 社区贡献规范

### 用户场景

外部开发者希望贡献新的学科 Skill、参考资料或测试，但需要明确的目录结构、提交流程和验收标准。

### 设计决策

| 决策点 | 选择 | 原因 | 放弃的方案 |
|--------|------|------|-----------|
| 规范位置 | `CONTRIBUTING.md` + `community/` | 入口清晰，模板与检查清单分离 | 只在 wiki 里写说明 |
| 模板形式 | 最小可复制目录模板 | 外部开发者能直接照着填 | 纯文字说明 |
| 验收标准 | 测试、样例、wiki 同步 | 保持现有仓库工作流一致 | 只要求代码通过 |

### 受影响文件

| 文件 | 改动类型 | 说明 |
|------|---------|------|
| `CONTRIBUTING.md` | 修改 | 扩展社区贡献流程与要求 |
| `community/skill_template/SKILL.md` | 新增 | Skill 模板 |
| `community/skill_template/scripts/README.md` | 新增 | 脚本目录规范 |
| `community/skill_template/references/README.md` | 新增 | 参考资料目录规范 |
| `community/skill_review_checklist.md` | 新增 | PR 自检清单 |

### 当前实现

- 贡献者可直接复制 `community/skill_template/`
- `CONTRIBUTING.md` 现在覆盖：
  - 环境准备
  - 目录约定
  - Skill 贡献要求
  - 测试与样例要求
  - wiki 同步要求
  - PR 检查项
- 已补最小 GitHub Actions CI：
  - 安装开发依赖
  - 运行 `python3 -m pytest tests`
  - 执行 MCP stdio 初始化冒烟

## 遗留项 / Backlog

- MCP 资源（resources）与提示词（prompts）能力尚未实现
- MCP tool 输出当前以文本为主，后续可补更细粒度结构化 content
- 社区贡献流程尚未接入更细粒度 lint / schema / 文档差异检查
