<!-- Last verified: 2026-04-18 | Current stage: D -->

# 项目路线图

## 阶段总览

| 阶段 | 主题 | 状态 | 文件 |
|------|------|------|------|
| A | MVP: 出题 + 组卷 | ✅ Completed | [stage-a](./10-stage-a.md) |
| B | 批改 + 学情分析 | ✅ Completed | [stage-b](./11-stage-b.md) |
| C | 备课 + 写教案 + 评语 | ✅ Completed | [stage-c](./12-stage-c.md) |
| D | MCP Server + 社区化 | ✅ Completed | [stage-d](./13-stage-d.md) |

## 功能索引

### Stage A — MVP: 出题 + 组卷

| # | 功能 | 状态 | 备注 |
|---|------|------|------|
| A0 | 项目基础设施 (pyproject.toml, .gitignore, README) | ✅ | |
| A1 | 共享数据模型 (schemas) | ✅ | KnowledgePoint, Question, ExamPaper |
| A2 | 出题 Skill (chuti) | ✅ | 本地模板生成 + schema 校验 |
| A3 | 组卷 Skill (zujuan) | ✅ | 贪心组卷 + Markdown/DOCX 导出 |
| A4 | 示例数据 | ✅ | 三科知识点 + 样例题目 + 演示文档 |
| A5 | 测试 | ✅ | 已覆盖 schema、出题、组卷与失败路径 |

### Stage B — 批改 + 学情分析

| # | 功能 | 状态 | 备注 |
|---|------|------|------|
| B1 | 批改 Skill (gaijuan) | ✅ | 客观题本地 + 主观题远程/离线降级 |
| B2 | 学情分析 Skill (xueqing) | ✅ | 诊断结果 + Markdown 报告 + 可选图表 |
| B3 | API 客户端 | ✅ | Token 认证 + `/api/grade` 封装 |
| B4 | API 服务端 | ✅ | FastAPI + 认证 + `/api/grade` `/api/diagnosis` |
| B5 | 学生数据模型 | ✅ | StudentResponse, KnowledgeMastery |

### Stage C — 备课 + 写教案 + 评语

| # | 功能 | 状态 | 备注 |
|---|------|------|------|
| C1 | 备课 Skill (beike) | ✅ | 本地课标分析、Bloom 层次梳理、Markdown 报告 |
| C2 | 写教案 Skill (jiaoan) | ✅ | 标准模板 + 5E 模板 + Markdown/DOCX 导出 |
| C3 | 评语 Skill (pingyu) | ✅ | 批量评语生成 + 教师观察融合 + Markdown/DOCX 导出 |
| C4 | 教案数据模型 | ✅ | LessonPlan, TeachingStep |

### Stage D — MCP Server + 社区化

| # | 功能 | 状态 | 备注 |
|---|------|------|------|
| D1 | MCP Server 封装 | ✅ | stdio MCP server + 7 个核心 tools |
| D2 | 社区贡献规范 | ✅ | 模板目录 + 检查清单 + 扩展贡献指南 |

## 里程碑

| 日期 | 里程碑 | 状态 |
|------|--------|------|
| <!-- TBD --> | Phase 1 MVP 交付 | 📋 |
| <!-- TBD --> | Phase 2 批改+学情分析交付 | 📋 |
| <!-- TBD --> | Phase 3 备课+教案+评语交付 | ✅ |
| <!-- TBD --> | Phase 4 MCP Server 上线 | ✅ |
