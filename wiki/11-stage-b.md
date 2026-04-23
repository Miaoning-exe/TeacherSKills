<!-- Last verified: 2026-04-16 | Current stage: B -->

# Stage B — 批改 + 学情分析

## 功能汇总

| # | 功能 | 状态 | 备注 |
|---|------|------|------|
| B1 | 批改 Skill (gaijuan) | ✅ | 客观题本地 + 主观题远程 API |
| B2 | 学情分析 Skill (xueqing) | ✅ | 远程调用认知诊断 API |
| B3 | API 客户端 | ✅ | Token 认证 + 请求封装 |
| B4 | API 服务端 | ✅ | 认知诊断 + 主观题评分 |
| B5 | 学生数据模型 | ✅ | StudentResponse, KnowledgeMastery |

---

## B1: 批改 Skill (gaijuan)

### 用户场景

教师将学生作答导入后，自动完成客观题精确批改和主观题语义评分，输出分数和反馈。

### 设计决策

| 决策点 | 选择 | 原因 | 放弃的方案 |
|--------|------|------|-----------|
| 客观题批改 | 本地精确字符串匹配 | 答案确定，无需网络 | 远程（浪费带宽） |
| 主观题评分 | 远程 API (`POST /api/grade`) | 需要 LLM 推理，教师本地无 GPU | 本地运行（需装 PyTorch） |
| 评分标准 | 参考 grading_rubrics.md，随请求发送给 API | 教师可自定义标准 | 硬编码在服务端（不灵活） |
| 离线降级 | 客观题正常批改，主观题标记"待评分" | 网络不可用时仍有部分价值 | 全部阻塞（体验差） |

### 三科特殊处理

| 学科 | 重点关注 | 评分特点 |
|------|---------|---------|
| 数学 | 解题步骤的正确性和完整性 | 步骤分、过程分 |
| 语文 | 阅读理解的概括能力、作文的语言表达 | 分维度评分（内容/结构/语言） |
| 英语 | 语法正确性、表达地道性 | 语言准确度 + 内容完整度 |

### 数据模型

```python
# shared/schemas/student.py
class StudentResponse(BaseModel):
    student_id: str
    question_id: str
    answer: str
    score: Optional[float] = None
    max_score: float
    feedback: Optional[str] = None
```

### 受影响文件

| 文件 | 改动类型 | 说明 |
|------|---------|------|
| `skills/gaijuan/SKILL.md` | 新增 | Skill 定义 |
| `skills/gaijuan/scripts/grade_answers.py` | 新增 | 客观题本地 + 主观题调 API |
| `skills/gaijuan/scripts/score_report.py` | 新增 | 成绩报告生成 |
| `skills/gaijuan/references/grading_rubrics.md` | 新增 | 评分标准 |
| `shared/schemas/student.py` | 新增 | StudentResponse 模型 |

### 当前实现说明

- 已提供 `grade_answers.py`，支持读取 `ExamPaper` 和学生作答 JSON，输出 `StudentResponse[]`。
- 客观题在本地按精确匹配评分；主观题通过 `shared/api_client.py` 调用 `/api/grade`。
- 当 Token 缺失、网络异常或显式 `--offline` 时，主观题不会阻塞流程，而是标记为“待评分”。
- 已提供 `score_report.py` 生成按学生汇总的 Markdown 成绩报告。

---

## B2: 学情分析 Skill (xueqing)

### 用户场景

教师说"帮我看看这次考试学生掌握情况怎么样"，获得：
- 班级整体知识点掌握热力图
- 每个学生的薄弱知识点雷达图
- 定向补救建议（哪些知识点需要重点复习、建议出哪类题目练习）

### 设计决策

| 决策点 | 选择 | 原因 | 放弃的方案 |
|--------|------|------|-----------|
| 对教师的呈现 | "学情分析"（教师语言） | 教师不关心算法名称 | "认知诊断"（技术语言） |
| 诊断计算 | 远程 API (`POST /api/diagnosis`) | IRT/NCDM 需要 PyTorch + GPU | 本地运行（教师需装重依赖） |
| 可视化 | 本地 Matplotlib 生成图表 | 诊断结果返回后本地画图即可 | 服务端生成图片（增加传输量） |
| 输出 | 学情报告(Markdown) + KnowledgeMastery[] | 报告给教师看，数据给出题 Skill 消费 | 纯数据（教师无法直接使用） |

### 调用流程

```
教师 → xueqing Skill
  1. 收集 StudentResponse[] 数据
  2. 调用 POST /api/diagnosis (发送作答数据 + 知识点映射)
  3. 接收 KnowledgeMastery[] 结果
  4. 本地生成可视化图表 (Matplotlib)
  5. 本地生成学情报告 (Markdown)
  6. 输出报告 + 图表 + KnowledgeMastery[] JSON
```

### 数据模型

```python
# shared/schemas/student.py
class KnowledgeMastery(BaseModel):
    student_id: str
    knowledge_point_id: str
    mastery_level: float                 # 0.0 ~ 1.0
    confidence: Optional[float] = None
```

### 受影响文件

| 文件 | 改动类型 | 说明 |
|------|---------|------|
| `skills/xueqing/SKILL.md` | 新增 | Skill 定义 |
| `skills/xueqing/scripts/analyze_learning.py` | 新增 | 调用 API + 生成报告 |
| `skills/xueqing/scripts/visualize_mastery.py` | 新增 | 本地生成雷达图/热力图 |
| `skills/xueqing/references/report_templates.md` | 新增 | 报告模板 |
| `shared/schemas/student.py` | 修改 | 追加 KnowledgeMastery |

### 当前实现说明

- 已提供 `analyze_learning.py`，支持读取 `StudentResponse[]`、`KnowledgePoint[]` 和可选 `Question[]`，输出 `KnowledgeMastery[]` 与 Markdown 学情报告。
- 优先调用 `/api/diagnosis`；当 Token 缺失、网络异常或显式 `--offline` 时，会退化为本地启发式估计。
- 已提供 `visualize_mastery.py` 生成班级热力图和按学生图表；若 `matplotlib` 不可用或与本地环境不兼容，会跳过图表生成但保留报告和数据输出。
- 已补充样例 `sample_knowledge_mastery.json` 和 `demo_xueqing.md` 供本地演示。

---

## B3: API 客户端

### 设计决策

| 决策点 | 选择 | 原因 | 放弃的方案 |
|--------|------|------|-----------|
| HTTP 库 | httpx | 支持异步、类型友好 | requests（无异步支持） |
| 认证 | Bearer Token (环境变量 `TEACHERSKILLS_API_TOKEN`) | 简单、教师易理解 | OAuth（过度复杂） |
| 错误处理 | 统一异常类 + 重试 | 网络不稳定时自动重试 | 裸异常（调用方需自行处理） |

### 受影响文件

| 文件 | 改动类型 | 说明 |
|------|---------|------|
| `shared/api_client.py` | 新增 | 统一 API 客户端 |
| `tests/test_api_client.py` | 新增 | 客户端测试 |

### 当前实现说明

- 已提供 `TeacherSkillsAPIClient`，统一管理 `TEACHERSKILLS_API_URL` 和 `TEACHERSKILLS_API_TOKEN`。
- 已封装 `grade_subjective_answer()` 与 `diagnose_learning()` 两个入口，其中 `/api/grade` 已被 `gaijuan` 使用。
- 已统一认证异常、请求异常和超时异常，便于 Skill 脚本做离线降级。

---

## B5: 学生数据模型

### 当前实现说明

- 已新增 `shared/schemas/student.py`，包含 `StudentResponse` 和 `KnowledgeMastery`。
- `StudentResponse` 已被 `gaijuan` 使用，`KnowledgeMastery` 已为 `xueqing` 预留。

---

## B4: API 服务端

### 设计决策

| 决策点 | 选择 | 原因 | 放弃的方案 |
|--------|------|------|-----------|
| 框架 | FastAPI | 自动文档、类型安全、异步 | Flask（手动序列化） |
| 认知诊断模型 | IRT (简单) + NCDM (多维) | 覆盖不同复杂度场景 | 仅 IRT（多维诊断能力不足） |
| 部署 | 容器化 | 环境隔离、易扩展 | 裸机（环境管理复杂） |

### 受影响文件

| 文件 | 改动类型 | 说明 |
|------|---------|------|
| `server/app.py` | 新增 | FastAPI 入口 |
| `server/routers/diagnosis.py` | 新增 | 认知诊断路由 |
| `server/routers/grading.py` | 新增 | 主观题评分路由 |
| `server/models/irt_model.py` | 新增 | IRT 实现 |
| `server/models/ncdm_model.py` | 新增 | NCDM 实现 |
| `server/auth.py` | 新增 | Token 认证中间件 |
| `server/requirements.txt` | 新增 | 服务端依赖 |

### 当前实现说明

- 已提供 `server/app.py`，包含 `/api/health`、`/api/grade`、`/api/diagnosis` 三个入口。
- 已提供 Bearer Token 认证，默认读取 `TEACHERSKILLS_API_SERVER_TOKEN`，未设置时使用开发默认值。
- `/api/grade` 当前提供 MVP 级启发式评分逻辑，接口字段已与客户端对齐。
- `/api/diagnosis` 当前提供基于得分均值的启发式掌握度估计，并保留 IRT/NCDM 模型替换位置。
- 已补充 `tests/test_server_api.py` 验证健康检查、认证、评分和诊断接口。

---

## 遗留项 / Backlog

- 主观题评分需验证与教师评分的相关性
- NCDM 模型需要足够的训练数据
- 可视化报告格式待与教师确认
- 学情分析报告的补救建议质量需迭代优化
- API 限流策略待定
- 离线模式下主观题"待评分"的后续同步机制
