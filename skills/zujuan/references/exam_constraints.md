# 组卷约束说明

`assemble_exam.py` 接收一个约束 JSON 文件，用于描述试卷结构、题型数量、分值、难度分布和知识点覆盖。

## 最小示例

```json
{
  "title": "九年级数学单元练习",
  "subject": "数学",
  "grade": "九年级",
  "duration_minutes": 45,
  "sections": [
    {
      "title": "一、选择题",
      "question_type": "选择题",
      "count": 5,
      "score_per_question": 3
    },
    {
      "title": "二、解答题",
      "question_type": "解答题",
      "count": 2,
      "score_per_question": 10
    }
  ],
  "difficulty_distribution": {
    "易": 0.7,
    "中": 0.2,
    "难": 0.1
  },
  "required_knowledge_points": [
    "二次函数的图像与性质"
  ]
}
```

## 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| `title` | 是 | 试卷标题 |
| `subject` | 是 | 学科，必须与题目 `subject` 一致 |
| `grade` | 是 | 年级 |
| `duration_minutes` | 是 | 考试时长，必须大于 0 |
| `sections` | 是 | 试卷分卷结构，每个 section 对应一种题型 |
| `difficulty_distribution` | 否 | 目标难度比例，键为 `易`、`中`、`难` |
| `required_knowledge_points` | 否 | 整张试卷必须覆盖的知识点 |

## Section 字段

| 字段 | 必填 | 说明 |
|------|------|------|
| `title` | 否 | 分卷标题，不填时自动生成，如 `一、选择题` |
| `question_type` | 是 | 题型，必须匹配 `QuestionType` |
| `count` | 是 | 需要抽取的题目数量 |
| `score_per_question` | 否 | 每题分值，不填则保留原题分值 |
| `required_knowledge_points` | 否 | 本 section 中每道候选题都必须包含的知识点 |

## 贪心选择策略

脚本会按 section 顺序选题，并确保同一张试卷不重复使用同一个 `question.id`。候选题排序优先考虑：

1. 选择后整体难度分布更接近 `difficulty_distribution`。
2. 优先覆盖尚未覆盖的 `required_knowledge_points`。
3. 使用 `question.id` 做稳定排序，保证结果可复现。

## 失败条件

- 某个 section 的候选题数量不足。
- `duration_minutes`、`count` 或 `score_per_question` 非正数。
- 整张试卷没有覆盖必需知识点。
- 输入 JSON 不符合 `Question[]` 或约束 schema。
