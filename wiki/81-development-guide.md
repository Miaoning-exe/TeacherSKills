<!-- Last verified: 2026-04-18 | Current stage: D -->

# 开发指南

## 环境要求

### Skill 端（教师本地 / 开发者）

| 依赖 | 版本 |
|------|------|
| Python | >= 3.10 |
| pip | 最新 |

### API 服务端（独立部署）

| 依赖 | 版本 |
|------|------|
| Python | >= 3.10 |
| PyTorch | >= 2.0 |
| CUDA (可选) | >= 11.8 |

## 快速启动

### Skill 端

```bash
# 克隆仓库
git clone <repo-url>
cd TeacherSkills

# 安装基础依赖（Phase 2 起包含 httpx）
pip install -e .

# 运行测试
pytest tests/

# 配置 API Token（Phase 2 起需要）
export TEACHERSKILLS_API_TOKEN="your-token-here"
export TEACHERSKILLS_API_URL="https://api.teacherskills.dev"  # 可选，有默认值
```

### Phase 1 本地出题

```bash
python skills/chuti/scripts/gen_question.py \
  --subject 数学 \
  --knowledge-points "二次函数的图像与性质" \
  --question-type 选择题 \
  --difficulty 中 \
  --count 3 \
  --output questions.json

python skills/chuti/scripts/validate_question.py questions.json
```

### Phase 1 本地组卷

```bash
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

若需要 DOCX 导出：

```bash
pip install -e ".[export]"
python skills/zujuan/scripts/export_exam.py \
  --input exam.json \
  --format docx \
  --output exam.docx
```

### Phase 2 本地批改

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

如需主观题远程评分，设置：

```bash
export TEACHERSKILLS_API_TOKEN="your-token-here"
export TEACHERSKILLS_API_URL="https://api.teacherskills.dev"
```

### Phase 2 学情分析

```bash
python skills/xueqing/scripts/analyze_learning.py \
  --responses examples/sample_data/sample_student_responses.json \
  --knowledge-points examples/sample_data/math_knowledge_points.json \
  --questions examples/sample_data/sample_questions.json \
  --output-mastery mastery.json \
  --output-report learning_report.md \
  --chart-dir charts \
  --offline
```

### Phase 3 备课

```bash
python skills/beike/scripts/analyze_curriculum.py \
  --subject 数学 \
  --grade 九年级 \
  --topic 二次函数 \
  --keywords 图像,顶点,性质 \
  --output-report beike_report.md
```

### Phase 3 写教案

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

### Phase 3 写评语

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

### Phase 4 MCP Server

```bash
python3 -m mcp_server.stdio_server
```

或：

```bash
teacherskills-mcp
```

MCP 客户端配置可参考 `examples/mcp_config.json`。

## CI

仓库已提供 `.github/workflows/ci.yml`，当前自动执行：

- `pip install -e ".[dev]"`
- `python3 -m pytest tests`
- MCP stdio 初始化冒烟

## 示例文件

- `examples/sample_data/`：知识点样例和跨学科题目池
- `examples/sample_data/sample_student_answers.json`：学生作答样例
- `examples/sample_data/sample_student_responses.json`：批改结果样例
- `examples/sample_data/sample_knowledge_mastery.json`：掌握度样例
- `examples/sample_data/sample_teacher_observations.json`：教师观察样例
- `examples/sample_data/sample_student_comments.json`：评语输出样例
- `examples/sample_data/sample_lesson_plan.json`：教案结构样例
- `examples/mcp_config.json`：MCP 客户端配置样例
- `examples/demo_chuti.md`：只演示出题
- `examples/demo_zujuan.md`：只演示组卷
- `examples/demo_full_workflow.md`：串联出题和组卷
- `examples/demo_xueqing.md`：演示学情分析
- `examples/demo_beike.md`：演示备课分析
- `examples/demo_jiaoan.md`：演示标准教案输出
- `examples/demo_pingyu.md`：演示批量评语输出

## 测试说明

- 运行全部测试：`python3 -m pytest tests`
- 当前已覆盖：
  - `tests/test_schemas.py`：schema 序列化与样例数据解析
  - `tests/test_question_gen.py`：出题逻辑与校验失败路径
  - `tests/test_exam_assembly.py`：组卷成功路径与约束失败路径
  - `tests/test_api_client.py`：API 客户端异常与响应解析
  - `tests/test_grading.py`：批改成功路径与离线降级
  - `tests/test_beike.py`：备课分析解析、匹配、报告与 CLI
  - `tests/test_jiaoan.py`：教案生成、模板渲染与 CLI
  - `tests/test_pingyu.py`：评语生成、个性化差异与 CLI
  - `tests/test_mcp_server.py`：MCP initialize、tools/list、tools/call 与 stdio 交互
  - `tests/test_learning_analysis.py`：学情分析成功路径、报告生成与图表依赖降级
  - `tests/test_server_api.py`：服务端健康检查、认证、评分和诊断接口

### API 服务端

```bash
pip install -r server/requirements.txt
python3 -m uvicorn server.app:app --host 0.0.0.0 --port 8000
```

默认服务端 Token：

```bash
export TEACHERSKILLS_API_SERVER_TOKEN="dev-token"
```

## 可选依赖

```bash
# 文档导出 (DOCX)
pip install -e ".[export]"          # python-docx

# 可视化（学情分析本地画图）
pip install -e ".[visualization]"   # matplotlib
```

## Skill 安装

将 `skills/` 目录 symlink 到 Claude Code 的 Skill 目录：

```bash
ln -s $(pwd)/skills/* ~/.claude/skills/
```

## API Token 获取

1. 访问 TeacherSkills 注册页面
2. 注册账号
3. 在个人设置中生成 API Token
4. 设置环境变量 `TEACHERSKILLS_API_TOKEN`

## 常见问题

### Pydantic v1 vs v2
本项目使用 Pydantic v2。如果环境中有 v1，请升级：`pip install "pydantic>=2.0"`。

### API 调用报 401
检查 `TEACHERSKILLS_API_TOKEN` 环境变量是否正确设置。

### Phase 1 功能不需要 Token
出题和组卷是纯本地功能，不需要 API Token。Token 仅在 Phase 2（批改主观题、学情分析）时需要。

### DOCX 导出失败
若 `jiaoan` 或 `zujuan` 提示缺少 `python-docx`，安装 `pip install -e ".[export]"` 后重试。

### Matplotlib 导入失败
若学情分析提示跳过图表生成，通常是本地 `matplotlib` 与 `NumPy` 二进制版本不兼容。此时报告和 `KnowledgeMastery[]` 仍会正常输出，图表依赖修复后可单独重跑。
