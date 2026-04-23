# TeacherSkills

面向中国小初高教师的 AI 工具集，以 [Claude Code Skill](https://docs.anthropic.com/claude-code) 格式交付。

## Skills

| Skill | 功能 | 阶段 |
|-------|------|------|
| `chuti` | 出题：按学科/知识点/题型/难度生成题目 | Phase 1 |
| `zujuan` | 组卷：按约束组装完整试卷并导出 | Phase 1 |
| `gaijuan` | 批改：客观题本地批改 + 主观题 API 评分 | Phase 2 |
| `xueqing` | 学情分析：知识点掌握度诊断 + 补救建议 | Phase 2 |
| `beike` | 备课：课标分析 + 教学策略 | Phase 3 |
| `jiaoan` | 写教案：生成标准化教案文档 | Phase 3 |
| `pingyu` | 评语：生成个性化学生评语 | Phase 3 |

## 安装

```bash
git clone <repo-url>
cd TeacherSkills
pip install -e .
```

安装 Skill（symlink 到 Claude Code Skill 目录）：

```bash
ln -s $(pwd)/skills/* ~/.claude/skills/
```

## 架构

本地 Skill（出题、组卷等轻量操作）+ 远程 TeacherSkills API（认知诊断、主观题评分）混合架构。Phase 2 起需要 API Token：

```bash
export TEACHERSKILLS_API_TOKEN="your-token"
```

详见 [wiki/02-system-architecture.md](wiki/02-system-architecture.md)。

## 开发

```bash
pip install -e ".[dev]"
pytest tests/
```

## Phase 1 工作流

```bash
python skills/chuti/scripts/gen_question.py \
  --subject 数学 \
  --knowledge-points "二次函数的图像与性质" \
  --question-type 选择题 \
  --difficulty 中 \
  --count 6 \
  --output questions.json

python skills/zujuan/scripts/assemble_exam.py \
  --questions questions.json \
  --constraints constraints.json \
  --output exam.json

python skills/zujuan/scripts/export_exam.py \
  --input exam.json \
  --format markdown \
  --output exam.md \
  --include-answers
```

## 示例数据

- 知识点样例：`examples/sample_data/math_knowledge_points.json`、`examples/sample_data/chinese_knowledge_points.json`、`examples/sample_data/english_knowledge_points.json`
- 跨学科题目池：`examples/sample_data/sample_questions.json`
- 学生作答样例：`examples/sample_data/sample_student_answers.json`
- 批改结果样例：`examples/sample_data/sample_student_responses.json`
- 掌握度样例：`examples/sample_data/sample_knowledge_mastery.json`
- 教师观察样例：`examples/sample_data/sample_teacher_observations.json`
- 教案样例：`examples/sample_data/sample_lesson_plan.json`
- 评语样例：`examples/sample_data/sample_student_comments.json`
- 演示文档：`examples/demo_chuti.md`、`examples/demo_zujuan.md`、`examples/demo_full_workflow.md`、`examples/demo_xueqing.md`、`examples/demo_beike.md`、`examples/demo_jiaoan.md`、`examples/demo_pingyu.md`

## Phase 2 批改工作流

```bash
python skills/gaijuan/scripts/grade_answers.py \
  --exam exam.json \
  --answers examples/sample_data/sample_student_answers.json \
  --offline \
  --output graded_responses.json

python skills/gaijuan/scripts/score_report.py \
  --exam exam.json \
  --responses graded_responses.json \
  --output score_report.md
```

## Phase 2 学情分析工作流

```bash
python skills/xueqing/scripts/analyze_learning.py \
  --responses examples/sample_data/sample_student_responses.json \
  --knowledge-points examples/sample_data/math_knowledge_points.json \
  --questions examples/sample_data/sample_questions.json \
  --output-mastery mastery.json \
  --output-report learning_report.md \
  --offline
```

## Phase 3 备课工作流

```bash
python skills/beike/scripts/analyze_curriculum.py \
  --subject 数学 \
  --grade 九年级 \
  --topic 二次函数 \
  --keywords 图像,顶点,性质 \
  --output-report beike_report.md
```

## Phase 3 教案生成工作流

```bash
python skills/jiaoan/scripts/generate_plan.py \
  --title 二次函数的图像与性质 \
  --subject 数学 \
  --grade 九年级 \
  --template standard \
  --beike-report examples/demo_beike.md \
  --output-json lesson_plan.json \
  --output-markdown lesson_plan.md
```

若需要 DOCX 导出：

```bash
pip install -e ".[export]"
python skills/jiaoan/scripts/generate_plan.py \
  --title 二次函数的图像与性质 \
  --subject 数学 \
  --grade 九年级 \
  --beike-report examples/demo_beike.md \
  --output-docx lesson_plan.docx
```

## Phase 3 评语生成工作流

```bash
python skills/pingyu/scripts/generate_comment.py \
  --responses examples/sample_data/sample_student_responses.json \
  --mastery examples/sample_data/sample_knowledge_mastery.json \
  --knowledge-points examples/sample_data/math_knowledge_points.json \
  --observations examples/sample_data/sample_teacher_observations.json \
  --term 期末 \
  --output-json student_comments.json \
  --output-markdown student_comments.md
```

## Phase 2 API 服务端

```bash
pip install -r server/requirements.txt
python3 -m uvicorn server.app:app --host 0.0.0.0 --port 8000
```

## Phase 4 MCP Server

```bash
python3 -m mcp_server.stdio_server
```

或：

```bash
teacherskills-mcp
```

MCP 客户端配置样例见 `examples/mcp_config.json`。
