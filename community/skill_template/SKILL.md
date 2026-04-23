---
name: your_skill_name
description: 用一句话说明这个 Skill 解决的教师任务、输入和输出。
---

# Skill 标题

## 触发场景

- 教师会怎样提出需求。
- 这个 Skill 应在什么边界内工作。

## 输入

| 参数 | 必填 | 示例 | 说明 |
|------|------|------|------|
| `subject` | 是 | `物理` | 学科 |

## 推荐流程

```bash
python skills/your_skill_name/scripts/your_script.py \
  --subject 物理 \
  --output output.json
```

## 输出约束

- 若输出结构化数据，必须使用 `shared/schemas/` 中已有模型，或在 PR 中补充新的 Pydantic 模型和测试。
- 若输出 Markdown，应说明固定章节结构。

## 限制

- 说明当前不能覆盖的场景。
