# AI 出题助手 - Demo 版 PRD

> **版本**：v0.5 Demo  
> **日期**：2026-04-28  
> **目标**：向教师演示「智能追问 + 题库检索 + AI 补充」核心能力  
> **范围**：聚焦后端实现，前端已有基础

---

## 📋 目录

1. [核心目标](#核心目标)
2. [产品流程](#产品流程)
3. [后端架构设计](#后端架构设计)
4. [数据库 Schema](#数据库-schema)
5. [API 接口设计](#api-接口设计)
6. [核心算法](#核心算法)
7. [技术选型](#技术选型)
8. [开发计划](#开发计划)

---

## 核心目标

### Demo 需要展示的能力

| 能力模块 | 具体表现 | 技术实现 |
|---------|---------|---------|
| **智能追问** | 用户输入模糊需求，Agent 3 轮对话内补全参数 | ExamAgent + Claude Agent SDK |
| **场景策略** | 自动匹配 4 种场景（作业/测验/考试/复习）的难度/题型分布 | Skill 规则引擎 |
| **智能搜题** | 从 10w+ 题库中语义检索 + 精准过滤，实时展示进度 | Elasticsearch + Embedding |
| **AI 补充** | 题库不足时，AI 生成题目补充，风格与题库一致 | LLM Tool Calling |
| **试卷预览** | 分栏展示题目（带来源标签：题库/AI），支持单题操作 | 前端已实现 |

### 成功标准

- [ ] Agent 参数提取准确率 > 90%（人工评估 20 个对话）
- [ ] 题库检索召回率 > 80%（有相关题目时能找到）
- [ ] AI 生成题目质量可用（教师主观评分 > 3/5 分）
- [ ] 单次出题耗时 < 30 秒（15 题试卷）

---

## 产品流程

### 完整用户旅程

```mermaid
sequenceDiagram
    participant U as 用户（教师）
    participant F as 前端
    participant A as ExamAgent
    participant S as 搜题引擎
    participant G as AI 生成器
    
    U->>F: 输入"帮我出份初二数学单元测验"
    F->>A: POST /api/chat
    A->>A: 识别参数：学科=数学，年级=初二
    A->>F: 追问"请问是关于哪个知识点？"
    U->>F: "一元二次方程"
    F->>A: POST /api/chat
    A->>A: 参数补全，推断场景=单元测验
    A->>F: 返回参数面板 JSON
    
    U->>F: 确认参数并调整题量
    F->>S: POST /api/exam/generate
    S->>S: ES 语义检索 + 精准过滤
    S->>F: 返回检索结果（12/15 题）
    
    S->>G: 请求补充 3 道题
    G->>G: 基于知识点和题库风格生成
    G->>F: 返回 AI 生成题目
    
    F->>U: 展示试卷预览（题库 12 + AI 3）
    U->>F: 对单题"重新搜题"
    F->>S: POST /api/question/replace
    S->>F: 返回新题目
```

### 关键交互点

#### 1. 多轮对话追问
```
用户：帮我出份数学试卷
Agent：好的！请问是哪个年级的数学？（初一/初二/初三/高一...）

用户：初二
Agent：明白了。请问是关于哪个知识点或章节？比如：
       - 一元二次方程
       - 函数（一次函数/二次函数/反比例函数）
       - 几何证明
       或者您可以自由输入知识点

用户：一元二次方程的应用题
Agent：收到！这份试卷是用于：
       A. 课后作业（侧重基础巩固）
       B. 单元测验（全面考查）
       C. 期末考试（综合难度）
       D. 考前复习（典型题训练）
       
用户：单元测验
Agent：【展示参数确认面板】
```

#### 2. 参数确认面板
```json
{
  "subject": "数学",
  "grade": "初二",
  "knowledge_points": ["一元二次方程", "应用题"],
  "scene": "unit_test",
  "scene_config": {
    "difficulty_distribution": {
      "easy": 0.3,
      "medium": 0.5,
      "hard": 0.2
    },
    "question_type_distribution": {
      "choice": 0.4,
      "blank": 0.3,
      "solution": 0.3
    },
    "total_count": 15,
    "total_score": 100
  },
  "editable_fields": ["total_count", "difficulty_distribution"]
}
```

#### 3. 搜题进度实时展示（SSE 流式输出）
```
🔍 正在从题库检索...
  [████████░░] 80% - 已找到 12 道题
  
  📊 检索结果分析：
  ├─ 选择题：5/6 道 ✓
  ├─ 填空题：4/4 道 ✓
  └─ 解答题：3/5 道 ⚠️ 缺 2 道

🤖 AI 正在生成补充题目...
  [██████████] 100% - 已生成 3 道题
  ├─ 中等难度解答题 ✓
  ├─ 困难解答题 ✓
  └─ 中等难度选择题 ✓

✅ 组卷完成！共 15 题
  ├─ 题库题目：12 道（80%）
  └─ AI 生成：3 道（20%）
```

---

## 🏗️ 架构设计理念

### 融合架构：OpenClaw Skill + LangGraph Workflow

本项目采用**分层融合架构**，结合两种主流 Agent 设计模式的优势：

#### 1. **OpenClaw Skill 模式（策略层）**
- **定义**：Skill = Markdown 策略文档，注入到 System Prompt
- **作用**：高层策略指导，告诉 LLM "应该做什么"和"怎么做"
- **特点**：
  - ✅ 教研人员可编辑（无需写代码）
  - ✅ 渐进式加载（按需加载，不占满 Context）
  - ✅ 灵活应变（LLM 可根据实际情况调整）
- **适用场景**：定义业务规则、场景策略、追问逻辑

#### 2. **LangGraph Workflow 模式（执行层）**
- **定义**：Workflow = 可执行的流程图，节点 + 边
- **作用**：确定性执行，保证流程的可控性和可测试性
- **特点**：
  - ✅ 流程可视化（图结构清晰）
  - ✅ 确定性执行（不依赖 LLM 理解）
  - ✅ 可测试、可调试（每个节点独立测试）
- **适用场景**：多步决策流程、状态管理、工具调用编排

#### 3. **融合优势**

| 维度 | OpenClaw Skill | LangGraph Workflow | 融合方案 |
|-----|----------------|-------------------|---------|
| **灵活性** | ✅ 高 | ⚠️ 低 | ✅ 策略灵活 + 流程确定 |
| **可控性** | ⚠️ 低（依赖 LLM） | ✅ 高 | ✅ 关键环节确定性执行 |
| **可维护性** | ✅ 易于修改规则 | ⚠️ 需改代码 | ✅ 策略和代码分离 |
| **可测试性** | ⚠️ 难以量化 | ✅ 单元测试 | ✅ 规则验证 + 流程测试 |
| **开发成本** | 低（写文档） | 高（写代码） | ⚖️ 适中 |

#### 4. **分工明确**
```
教研人员修改 Skill 策略（改规则）
    ↓
Skills/exam_skill.md
    ↓
    【场景策略、参数规则、追问逻辑】
    ↓
开发人员维护 Workflow 逻辑（改流程）
    ↓
Workflows/exam_workflow/graph.py
    ↓
    【节点编排、状态管理、工具调用】
```

---

## 后端架构设计

### 总体架构（融合模式）

```
┌─────────────────────────────────────────────────┐
│              FastAPI API 层                     │
│   (接收请求，返回 SSE 流式输出)                  │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│             MainAgent（路由层）                  │
│  • 渐进式加载 Skill 文档                         │
│  • 路由到对应的 Workflow                        │
└─────────────────┬───────────────────────────────┘
                  │
          ┌───────┴──────────┐
          ▼                  ▼
┌──────────────────┐  ┌──────────────────┐
│ Skill 层         │  │ Workflow 层      │
│ (OpenClaw 模式)  │  │ (LangGraph)      │
│                  │  │                  │
│ • exam_skill.md  │  │ • ExamWorkflow   │
│ • search_skill.md│  │   ├─ graph.py    │
│ • adapt_skill.md │  │   ├─ nodes.py    │
│                  │  │   └─ state.py    │
│ 策略文档         │  │ 流程图编排       │
│ 教研可编辑       │  │ 开发人员维护     │
└──────────────────┘  └────────┬─────────┘
                               │
                               ▼
                    ┌──────────────────┐
                    │   Tool / Service  │
                    │   • ES 检索       │
                    │   • LLM 生成      │
                    │   • 数据库查询    │
                    └──────────────────┘
```

### 总体架构（详细版）

```
┌─────────────────────────────────────────────────┐
│                   FastAPI 服务                   │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────┐      ┌──────────────┐       │
│  │  ExamAgent   │      │  AdaptAgent  │       │
│  │ (出题调度)    │      │ (单题改编)    │       │
│  └──────┬───────┘      └──────┬───────┘       │
│         │                     │                │
│         ├─────────┬───────────┤                │
│         ▼         ▼           ▼                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │ 参数提取  │ │ 搜题引擎  │ │ AI 生成器 │      │
│  │  工具     │ │          │ │          │      │
│  └──────────┘ └─────┬────┘ └─────┬────┘      │
│                     │             │           │
└─────────────────────┼─────────────┼───────────┘
                      ▼             ▼
              ┌──────────────┐ ┌──────────┐
              │ Elasticsearch│ │   LLM    │
              │   题库索引   │ │  API     │
              └──────┬───────┘ └──────────┘
                     ▼
              ┌──────────────┐
              │  PostgreSQL  │
              │  题库数据    │
              └──────────────┘
```

### 核心模块

#### 1. ExamAgent（出题调度 Agent）

**职责**：
- 多轮对话参数提取
- 场景策略匹配
- 调用搜题引擎和 AI 生成器
- 组卷逻辑

**System Prompt 要点**：
```markdown
你是一个专业的 K12 出题助手，负责通过对话理解教师需求并生成试卷。

# 参数提取规则
必须提取的参数：
- subject（学科）：数学/物理/化学/语文等
- grade（年级）：初一到高三
- knowledge_points（知识点）：具体到章节或考点

可选参数：
- scene（场景）：如未明确，根据关键词推断
  - "作业" → homework
  - "测验/小测" → unit_test
  - "期中/期末" → exam
  - "复习/冲刺" → review

# 追问策略
- 第 1 轮缺失学科/年级 → 直接询问
- 第 2 轮缺失知识点 → 提供常见选项 + 自由输入
- 第 3 轮缺失场景 → 展示 4 种场景说明

# 工具调用
当参数满足【学科 + 年级 + 知识点】时，调用：
- extract_parameters() → 返回结构化参数 JSON
- match_scene_strategy() → 匹配场景策略（难度/题型分布）
```

**可用工具**：
```python
def extract_parameters(
    conversation_history: list[Message]
) -> ExamParameters:
    """从对话历史中提取结构化参数"""
    pass

def match_scene_strategy(
    scene: ExamScene,
    custom_adjustments: dict = None
) -> SceneConfig:
    """匹配场景策略，返回难度/题型分布"""
    pass

def generate_exam(
    params: ExamParameters,
    scene_config: SceneConfig
) -> ExamPlan:
    """
    核心出题工具，内部流程：
    1. 调用搜题引擎
    2. 计算缺口
    3. 调用 AI 生成器补充
    4. 组装试卷
    """
    pass
```

#### 2. 搜题引擎（QuestionSearchEngine）

**检索策略**：

```python
class QuestionSearchEngine:
    def __init__(self, es_client, embedding_model):
        self.es = es_client
        self.embedder = embedding_model  # 用于语义检索
    
    async def search(
        self,
        knowledge_points: list[str],
        difficulty: Difficulty,
        question_type: QuestionType,
        count: int,
        exclude_ids: list[str] = []  # 避免重复
    ) -> SearchResult:
        """
        混合检索策略：
        1. 精准过滤（must 条件）
        2. 语义检索（should 条件，加权）
        3. 结果排序（考频、质量分）
        """
        # 1. 构建 ES Query
        query = {
            "bool": {
                "must": [
                    {"term": {"difficulty": difficulty.value}},
                    {"term": {"question_type": question_type.value}},
                    {"terms": {"grade": self._expand_grades(grade)}}
                ],
                "should": [
                    # 精确匹配知识点
                    {"terms": {"knowledge_points": knowledge_points, "boost": 3.0}},
                    # 语义相似度
                    {"knn": {
                        "field": "content_vector",
                        "query_vector": self._embed_query(knowledge_points),
                        "k": 50,
                        "num_candidates": 100
                    }}
                ],
                "must_not": [
                    {"ids": {"values": exclude_ids}}
                ]
            }
        }
        
        # 2. 执行检索
        results = await self.es.search(index="questions", body=query, size=count * 2)
        
        # 3. 后处理（去重、质量过滤）
        questions = self._post_process(results, count)
        
        return SearchResult(
            questions=questions,
            found_count=len(questions),
            required_count=count,
            gap=max(0, count - len(questions))
        )
    
    def _expand_grades(self, grade: str) -> list[str]:
        """
        年级扩展策略：
        初二 → ["初二", "初一"]（可降级取题）
        高一 → ["高一", "初三"]（可跨学段取难题）
        """
        pass
```

**Elasticsearch Index Mapping**：

```json
{
  "mappings": {
    "properties": {
      "question_id": {"type": "keyword"},
      "subject": {"type": "keyword"},
      "grade": {"type": "keyword"},
      "knowledge_points": {"type": "keyword"},
      "question_type": {"type": "keyword"},
      "difficulty": {"type": "keyword"},
      "content": {
        "type": "text",
        "analyzer": "ik_max_word"
      },
      "content_vector": {
        "type": "dense_vector",
        "dims": 768,
        "index": true,
        "similarity": "cosine"
      },
      "answer": {"type": "text"},
      "analysis": {"type": "text"},
      "score": {"type": "integer"},
      "source": {"type": "keyword"},
      "usage_frequency": {"type": "integer"},
      "quality_score": {"type": "float"},
      "created_at": {"type": "date"}
    }
  }
}
```

#### 3. AI 生成器（QuestionGenerator）

**职责**：
- 基于知识点和参考风格生成题目
- 保持与题库题目风格一致
- 自动标注知识点和难度

**核心 Prompt**：

```python
def build_generation_prompt(
    knowledge_points: list[str],
    difficulty: Difficulty,
    question_type: QuestionType,
    reference_questions: list[Question]  # 题库中的参考题
) -> str:
    """
    构建 AI 生成题目的 Prompt
    """
    return f"""
你是一个专业的 K12 数学出题专家。请根据以下要求生成题目：

# 知识点要求
{', '.join(knowledge_points)}

# 题型和难度
- 题型：{question_type.name}
- 难度：{difficulty.name}

# 参考题库风格
以下是题库中的典型题目，请参考其语言风格和结构：

{self._format_reference_questions(reference_questions)}

# 生成要求
1. 题目内容贴近生活场景（如工程问题、商品定价、几何测量）
2. 避免过于抽象，优先用具体数字
3. 选择题选项需有迷惑性（常见错误答案）
4. 必须提供详细解析（步骤清晰）
5. 标注涉及的知识点（可多个）

# 输出格式（JSON）
{{
  "question_type": "{question_type.value}",
  "difficulty": "{difficulty.value}",
  "content": "题目内容...",
  "options": [  // 仅选择题需要
    {{"label": "A", "content": "选项 A"}},
    ...
  ],
  "answer": "标准答案",
  "analysis": "详细解析...",
  "knowledge_points": ["一元二次方程", "应用题"],
  "score": 5
}}
"""
```

#### 4. 组卷策略（ExamAssembler）

```python
class ExamAssembler:
    """
    组卷逻辑：
    1. 按题型分组（选择题 → 填空题 → 解答题）
    2. 按难度排序（先易后难）
    3. 自动计算题号和总分
    """
    
    def assemble(
        self,
        search_results: dict[QuestionType, list[Question]],
        generated_questions: list[Question],
        scene_config: SceneConfig
    ) -> Exam:
        # 1. 合并题库题目和 AI 生成题目
        all_questions = self._merge_questions(search_results, generated_questions)
        
        # 2. 按题型分组
        grouped = self._group_by_type(all_questions)
        
        # 3. 每组内按难度排序
        for qtype, questions in grouped.items():
            grouped[qtype] = sorted(questions, key=lambda q: q.difficulty.value)
        
        # 4. 展平并分配题号
        final_questions = []
        index = 1
        for qtype in [QuestionType.CHOICE, QuestionType.BLANK, QuestionType.SOLUTION]:
            for q in grouped.get(qtype, []):
                q.index = index
                index += 1
                final_questions.append(q)
        
        # 5. 计算总分
        total_score = sum(q.score for q in final_questions)
        
        return Exam(
            exam_id=str(uuid.uuid4()),
            subject=scene_config.subject,
            grade=scene_config.grade,
            knowledge_points=scene_config.knowledge_points,
            scene=scene_config.scene,
            questions=final_questions,
            total_score=total_score,
            source_stats={
                "database": len([q for q in final_questions if q.source == "database"]),
                "ai_generated": len([q for q in final_questions if q.source == "ai"])
            },
            created_at=datetime.now()
        )
```

---

## 数据库 Schema

### PostgreSQL 题库表结构

```sql
-- 题目主表
CREATE TABLE questions (
    question_id VARCHAR(50) PRIMARY KEY,
    subject VARCHAR(20) NOT NULL,
    grade VARCHAR(10) NOT NULL,
    knowledge_points TEXT[] NOT NULL,  -- 数组类型
    question_type VARCHAR(20) NOT NULL,  -- choice/blank/solution/...
    difficulty VARCHAR(10) NOT NULL,  -- easy/medium/hard
    content TEXT NOT NULL,
    options JSONB,  -- 选择题选项，JSON 格式
    answer TEXT NOT NULL,
    analysis TEXT,
    score INTEGER DEFAULT 5,
    source VARCHAR(50),  -- 来源（真题/模拟题/出版社）
    usage_frequency INTEGER DEFAULT 0,  -- 使用次数
    quality_score FLOAT DEFAULT 0.0,  -- 质量评分（教师反馈）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_subject_grade ON questions(subject, grade);
CREATE INDEX idx_knowledge_points ON questions USING GIN(knowledge_points);
CREATE INDEX idx_difficulty_type ON questions(difficulty, question_type);
CREATE INDEX idx_quality ON questions(quality_score DESC);

-- 知识点表（可选，用于知识图谱）
CREATE TABLE knowledge_graph (
    kp_id VARCHAR(50) PRIMARY KEY,
    kp_name VARCHAR(100) NOT NULL,
    parent_id VARCHAR(50),  -- 父知识点
    subject VARCHAR(20) NOT NULL,
    grade_range TEXT[],  -- 适用年级
    description TEXT,
    FOREIGN KEY (parent_id) REFERENCES knowledge_graph(kp_id)
);

-- 试卷历史表（记录生成的试卷）
CREATE TABLE exam_history (
    exam_id VARCHAR(50) PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    subject VARCHAR(20) NOT NULL,
    grade VARCHAR(10) NOT NULL,
    knowledge_points TEXT[] NOT NULL,
    scene VARCHAR(20) NOT NULL,
    question_ids TEXT[] NOT NULL,  -- 题目 ID 列表
    total_score INTEGER NOT NULL,
    source_stats JSONB,  -- {"database": 12, "ai": 3}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 会话管理（Session）

```python
# 使用 Redis 或 JSON 文件存储会话
{
  "session_id": "sess_abc123",
  "user_id": "teacher_001",
  "conversation_history": [
    {"role": "user", "content": "帮我出份初二数学试卷"},
    {"role": "assistant", "content": "好的！请问是哪个知识点？"}
  ],
  "extracted_params": {
    "subject": "数学",
    "grade": "初二",
    "knowledge_points": ["一元二次方程"],
    "scene": "unit_test"
  },
  "current_exam": {
    "exam_id": "exam_xyz789",
    "questions": [...],
    "status": "previewing"
  },
  "created_at": "2026-04-28T10:30:00",
  "updated_at": "2026-04-28T10:35:00"
}
```

---

## API 接口设计

### 基础约定

- **Base URL**: `http://localhost:8000/api`
- **认证**: 暂不实现（Demo 版）
- **响应格式**: 统一 JSON

```typescript
interface APIResponse<T> {
  code: number;  // 200 成功，4xx 客户端错误，5xx 服务器错误
  message: string;
  data: T;
  timestamp: string;
}
```

### 接口列表

#### 1. 创建会话

```http
POST /sessions
```

**请求**：
```json
{
  "user_id": "teacher_001"  // 可选
}
```

**响应**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "session_id": "sess_abc123",
    "created_at": "2026-04-28T10:30:00Z"
  }
}
```

#### 2. 对话接口（多轮）

```http
POST /sessions/{session_id}/chat
```

**请求**：
```json
{
  "message": "帮我出份初二数学单元测验"
}
```

**响应（流式 SSE）**：
```
data: {"type": "thinking", "content": "正在分析您的需求..."}

data: {"type": "param_extracted", "params": {"subject": "数学", "grade": "初二"}}

data: {"type": "question", "content": "请问是关于哪个知识点？比如一元二次方程、函数、几何证明？"}

data: {"type": "done"}
```

**响应（非流式，返回参数面板）**：
```json
{
  "code": 200,
  "data": {
    "need_more_info": false,
    "params": {
      "subject": "数学",
      "grade": "初二",
      "knowledge_points": ["一元二次方程"],
      "scene": "unit_test",
      "scene_config": {
        "difficulty_distribution": {"easy": 0.3, "medium": 0.5, "hard": 0.2},
        "question_type_distribution": {"choice": 0.4, "blank": 0.3, "solution": 0.3},
        "total_count": 15,
        "total_score": 100
      }
    },
    "editable_fields": ["total_count", "difficulty_distribution", "question_type_distribution"]
  }
}
```

#### 3. 生成试卷

```http
POST /sessions/{session_id}/exams/generate
```

**请求**：
```json
{
  "params": {
    "subject": "数学",
    "grade": "初二",
    "knowledge_points": ["一元二次方程"],
    "scene": "unit_test",
    "scene_config": {
      "difficulty_distribution": {"easy": 0.3, "medium": 0.5, "hard": 0.2},
      "question_type_distribution": {"choice": 0.4, "blank": 0.3, "solution": 0.3},
      "total_count": 15
    }
  }
}
```

**响应（流式 SSE）**：
```
data: {"type": "search_start", "content": "正在从题库检索..."}

data: {"type": "search_progress", "progress": 0.5, "found": 8, "required": 15}

data: {"type": "search_result", "data": {"found": 12, "gap": 3, "breakdown": {"choice": {"found": 5, "required": 6}, ...}}}

data: {"type": "generate_start", "content": "AI 正在生成补充题目..."}

data: {"type": "generate_progress", "progress": 0.66, "generated": 2, "required": 3}

data: {"type": "assemble_complete", "data": {"exam_id": "exam_xyz789", "total_questions": 15, "source_stats": {"database": 12, "ai": 3}}}

data: {"type": "done"}
```

**最终响应**：
```json
{
  "code": 200,
  "data": {
    "exam_id": "exam_xyz789",
    "subject": "数学",
    "grade": "初二",
    "knowledge_points": ["一元二次方程"],
    "scene": "unit_test",
    "questions": [
      {
        "id": "q_001",
        "index": 1,
        "type": "choice",
        "difficulty": "easy",
        "content": "若 x²-5x+6=0，则 x 的值为（ ）",
        "options": [
          {"label": "A", "content": "2 或 3"},
          {"label": "B", "content": "1 或 6"},
          {"label": "C", "content": "-2 或 -3"},
          {"label": "D", "content": "无解"}
        ],
        "answer": "A",
        "analysis": "因式分解：(x-2)(x-3)=0，得 x=2 或 x=3",
        "knowledge_points": ["一元二次方程", "因式分解"],
        "score": 5,
        "source": "database",
        "source_id": "db_q_12345"
      },
      {
        "id": "q_015",
        "index": 15,
        "type": "solution",
        "difficulty": "hard",
        "content": "某工厂生产一批零件，原计划每天生产 120 个...",
        "answer": "设实际每天生产 x 个...",
        "analysis": "...",
        "knowledge_points": ["一元二次方程", "应用题"],
        "score": 12,
        "source": "ai",
        "source_id": null
      }
    ],
    "total_score": 100,
    "source_stats": {
      "database": 12,
      "ai": 3
    },
    "created_at": "2026-04-28T10:35:00Z"
  }
}
```

#### 4. 单题替换（重新搜题）

```http
POST /exams/{exam_id}/questions/{question_id}/replace
```

**请求**：
```json
{
  "strategy": "search_similar"  // 或 "regenerate"
}
```

**响应**：
```json
{
  "code": 200,
  "data": {
    "new_question": {
      "id": "q_new_001",
      "index": 3,
      "type": "choice",
      ...
    }
  }
}
```

#### 5. 单题改编（AI）

```http
POST /exams/{exam_id}/questions/{question_id}/adapt
```

**请求**：
```json
{
  "adaptation_type": "increase_difficulty",  // 或 "decrease_difficulty", "change_type"
  "target_difficulty": "hard",  // 可选
  "target_type": "blank"  // 可选
}
```

**响应**：
```json
{
  "code": 200,
  "data": {
    "adapted_question": {
      "id": "q_adapted_001",
      "index": 3,
      "type": "blank",
      "difficulty": "hard",
      ...
    }
  }
}
```

#### 6. 导出试卷

```http
POST /exams/{exam_id}/export
```

**请求**：
```json
{
  "format": "word",  // 或 "pdf", "markdown"
  "include_answer": true,
  "include_analysis": false
}
```

**响应**：
```json
{
  "code": 200,
  "data": {
    "download_url": "/downloads/exam_xyz789.docx",
    "expires_at": "2026-04-28T11:00:00Z"
  }
}
```

---

## 核心算法

### 1. 场景策略匹配

```python
SCENE_STRATEGIES = {
    ExamScene.HOMEWORK: {
        "difficulty_distribution": {
            Difficulty.EASY: 0.5,
            Difficulty.MEDIUM: 0.4,
            Difficulty.HARD: 0.1
        },
        "question_type_distribution": {
            QuestionType.CHOICE: 0.3,
            QuestionType.BLANK: 0.4,
            QuestionType.SOLUTION: 0.3
        },
        "total_count_range": (8, 15),
        "total_score_range": (50, 100),
        "description": "课后作业：侧重基础巩固，难度偏低"
    },
    ExamScene.UNIT_TEST: {
        "difficulty_distribution": {
            Difficulty.EASY: 0.3,
            Difficulty.MEDIUM: 0.5,
            Difficulty.HARD: 0.2
        },
        "question_type_distribution": {
            QuestionType.CHOICE: 0.4,
            QuestionType.BLANK: 0.3,
            QuestionType.SOLUTION: 0.3
        },
        "total_count_range": (12, 20),
        "total_score_range": (80, 120),
        "description": "单元测验：全面考查，难度中等"
    },
    ExamScene.EXAM: {
        "difficulty_distribution": {
            Difficulty.EASY: 0.2,
            Difficulty.MEDIUM: 0.5,
            Difficulty.HARD: 0.3
        },
        "question_type_distribution": {
            QuestionType.CHOICE: 0.35,
            QuestionType.BLANK: 0.25,
            QuestionType.SOLUTION: 0.4
        },
        "total_count_range": (20, 30),
        "total_score_range": (100, 150),
        "description": "期末考试：综合难度，区分度高"
    },
    ExamScene.REVIEW: {
        "difficulty_distribution": {
            Difficulty.EASY: 0.2,
            Difficulty.MEDIUM: 0.4,
            Difficulty.HARD: 0.4
        },
        "question_type_distribution": {
            QuestionType.CHOICE: 0.3,
            QuestionType.BLANK: 0.2,
            QuestionType.SOLUTION: 0.5
        },
        "total_count_range": (10, 20),
        "total_score_range": (80, 150),
        "description": "考前复习：典型题训练，难题占比高"
    }
}

def match_scene(user_input: str, params: dict) -> ExamScene:
    """
    根据用户输入和参数推断场景
    """
    keywords = {
        ExamScene.HOMEWORK: ["作业", "练习", "巩固"],
        ExamScene.UNIT_TEST: ["测验", "小测", "单元"],
        ExamScene.EXAM: ["考试", "期中", "期末"],
        ExamScene.REVIEW: ["复习", "冲刺", "备考"]
    }
    
    for scene, kws in keywords.items():
        if any(kw in user_input for kw in kws):
            return scene
    
    # 默认返回单元测验
    return ExamScene.UNIT_TEST
```

### 2. 题目分配算法

```python
def allocate_questions(
    scene_config: SceneConfig,
    search_results: dict[QuestionType, list[Question]]
) -> dict[QuestionType, dict[Difficulty, int]]:
    """
    根据场景配置和检索结果，计算每种（题型 + 难度）的题目数量
    
    输入示例：
    - total_count = 15
    - difficulty_distribution = {"easy": 0.3, "medium": 0.5, "hard": 0.2}
    - question_type_distribution = {"choice": 0.4, "blank": 0.3, "solution": 0.3}
    
    输出示例：
    {
      "choice": {"easy": 2, "medium": 3, "hard": 1},  # 共 6 题
      "blank": {"easy": 1, "medium": 2, "hard": 1},   # 共 4 题
      "solution": {"easy": 1, "medium": 2, "hard": 2}  # 共 5 题
    }
    """
    total = scene_config.total_count
    type_dist = scene_config.question_type_distribution
    diff_dist = scene_config.difficulty_distribution
    
    allocation = {}
    
    for qtype, type_ratio in type_dist.items():
        type_count = round(total * type_ratio)
        allocation[qtype] = {}
        
        for difficulty, diff_ratio in diff_dist.items():
            count = round(type_count * diff_ratio)
            allocation[qtype][difficulty] = max(1, count)  # 至少 1 题
    
    # 调整总数（四舍五入可能导致偏差）
    current_total = sum(sum(d.values()) for d in allocation.values())
    diff = total - current_total
    
    if diff != 0:
        # 优先调整中等难度的题目
        for qtype in allocation:
            if Difficulty.MEDIUM in allocation[qtype]:
                allocation[qtype][Difficulty.MEDIUM] += diff
                break
    
    return allocation
```

### 3. 语义检索 Embedding

```python
from sentence_transformers import SentenceTransformer

class EmbeddingService:
    def __init__(self):
        # 使用中文优化的模型
        self.model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
    
    def embed_question(self, content: str, knowledge_points: list[str]) -> list[float]:
        """
        对题目内容 + 知识点生成 Embedding
        """
        text = f"{content} {' '.join(knowledge_points)}"
        vector = self.model.encode(text, normalize_embeddings=True)
        return vector.tolist()
    
    def embed_query(self, knowledge_points: list[str]) -> list[float]:
        """
        对查询知识点生成 Embedding
        """
        text = ' '.join(knowledge_points)
        vector = self.model.encode(text, normalize_embeddings=True)
        return vector.tolist()
```

**数据预处理**（题库导入时）：
```python
async def index_questions_to_es():
    """
    将 PostgreSQL 题库数据导入 Elasticsearch，并生成 Embedding
    """
    embedding_service = EmbeddingService()
    
    async for question in fetch_questions_from_db():
        # 生成 Embedding
        vector = embedding_service.embed_question(
            question.content,
            question.knowledge_points
        )
        
        # 插入 ES
        await es_client.index(
            index="questions",
            id=question.question_id,
            document={
                **question.dict(),
                "content_vector": vector
            }
        )
```

---

## 技术选型

### 后端技术栈

| 模块 | 技术选型 | 版本 | 说明 |
|-----|---------|------|------|
| **Web 框架** | FastAPI | 0.115+ | 异步支持，自动 API 文档 |
| **Agent SDK** | Claude Agent SDK | Latest | Claude 官方 SDK |
| **LLM 提供商** | DeepSeek / Kimi | - | 选一个性价比高的 |
| **数据库** | PostgreSQL | 15+ | 题库存储 |
| **检索引擎** | Elasticsearch | 8.x | 混合检索（BM25 + KNN） |
| **Embedding 模型** | sentence-transformers | - | `paraphrase-multilingual-mpnet-base-v2` |
| **会话存储** | Redis | 7+ | 会话状态管理 |
| **异步任务** | Celery + Redis | - | 异步生成题目（可选） |
| **Word 导出** | python-docx | - | 试卷导出 |

### 前端技术栈（参考）

| 模块 | 技术选型 | 说明 |
|-----|---------|------|
| **框架** | Next.js 14 | App Router，SSR |
| **状态管理** | Zustand | 轻量级 |
| **UI 组件** | Ant Design / shadcn/ui | 成熟组件库 |
| **SSE 处理** | EventSource API | 原生支持 |
| **数学公式** | KaTeX | 快速渲染 |
| **拖拽排序** | @dnd-kit/core | 题目顺序调整 |

### 部署架构（Demo 版）

```
┌─────────────────────────────────────────┐
│          Nginx (反向代理)                │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────┐    ┌──────────────┐  │
│  │   Next.js    │    │   FastAPI    │  │
│  │  (前端服务)   │    │  (后端服务)   │  │
│  │  :3000       │    │  :8000       │  │
│  └──────────────┘    └───────┬──────┘  │
│                              │         │
│  ┌──────────────┐    ┌───────▼──────┐  │
│  │  PostgreSQL  │    │ Elasticsearch│  │
│  │  :5432       │    │  :9200       │  │
│  └──────────────┘    └──────────────┘  │
│                                         │
│  ┌──────────────┐                      │
│  │    Redis     │                      │
│  │    :6379     │                      │
│  └──────────────┘                      │
└─────────────────────────────────────────┘
```

---

## 开发计划

### 第 1 阶段：基础架构搭建（2-3 天）

**目标**：跑通基本流程（对话 → 参数提取 → 返回 JSON）

- [ ] FastAPI 项目初始化
  - 目录结构：`backend/app/`, `backend/agents/`, `backend/tools/`
  - 环境变量配置：`.env` 文件（LLM API Key、数据库连接）
  - 日志配置：`logging.conf`

- [ ] 数据库初始化
  - PostgreSQL 建表（`questions`, `exam_history`）
  - 导入测试数据（100 道题，覆盖初二数学）
  - 数据库连接池（SQLAlchemy）

- [ ] ExamAgent 基础实现
  - System Prompt 编写（基于 `smart-question-generator/SKILL.md`）
  - 参数提取工具（`extract_parameters`）
  - 场景策略匹配（`match_scene_strategy`）

- [ ] API 基础接口
  - `POST /sessions` - 创建会话
  - `POST /sessions/{id}/chat` - 对话接口（非流式）
  - 返回参数面板 JSON

**验收标准**：
- 用户输入 → Agent 追问 → 返回结构化参数 JSON
- 日志完整记录对话过程

---

### 第 2 阶段：题库检索（3-4 天）

**目标**：实现 Elasticsearch 混合检索，返回题目列表

- [ ] Elasticsearch 部署
  - Docker Compose 配置
  - Index 创建（`questions` 索引）
  - Mapping 定义（包含 `content_vector` 字段）

- [ ] Embedding 服务
  - `sentence-transformers` 模型加载
  - 题库 Embedding 预计算（批量处理）
  - 查询 Embedding 实时生成

- [ ] 搜题引擎实现
  - 混合检索策略（BM25 + KNN）
  - 精准过滤（学科、年级、难度、题型）
  - 年级扩展逻辑（初二 → 初二/初一）
  - 结果排序（质量分、考频）

- [ ] API 接口
  - `POST /sessions/{id}/exams/generate` - 生成试卷（仅检索，暂不 AI 生成）
  - 流式输出搜题进度（SSE）

**验收标准**：
- 输入参数 → 检索到匹配题目（召回率 > 80%）
- 前端实时显示搜题进度
- 检索耗时 < 2 秒（15 题）

---

### 第 3 阶段：AI 补充生成（2-3 天）

**目标**：题库不足时，AI 生成题目补充

- [ ] QuestionGenerator 实现
  - 构建生成 Prompt（含参考题目风格）
  - LLM API 调用（DeepSeek/Kimi）
  - 结果解析和校验（JSON Schema）

- [ ] 组卷逻辑
  - 计算缺口（按题型、难度）
  - 调用 AI 生成器补充
  - 合并题库题目和 AI 题目
  - 按题型、难度排序

- [ ] API 接口完善
  - 流式输出 AI 生成进度
  - 返回完整试卷 JSON（含来源标签）

**验收标准**：
- 题库不足时，AI 自动补充
- AI 生成题目质量可用（教师主观评分 > 3/5）
- 生成耗时 < 10 秒（3 道题）

---

### 第 4 阶段：单题操作（1-2 天）

**目标**：支持单题替换和改编

- [ ] 单题替换
  - 重新搜题（排除已用题目）
  - 返回新题目，前端局部更新

- [ ] 单题改编（AdaptAgent）
  - 提难度/降难度
  - 换题型（选择题 → 填空题）
  - 换场景（保持知识点不变）

- [ ] API 接口
  - `POST /exams/{id}/questions/{qid}/replace`
  - `POST /exams/{id}/questions/{qid}/adapt`

**验收标准**：
- 单题替换响应时间 < 1 秒
- AI 改编保持知识点一致性

---

### 第 5 阶段：导出和优化（1-2 天）

**目标**：支持 Word 导出，优化性能

- [ ] Word 导出
  - 使用 `python-docx` 生成 .docx
  - 支持"含答案"和"不含答案"两种模式
  - 题目排版（题号、分值、答题区域）

- [ ] 性能优化
  - ES 查询缓存
  - LLM 调用并发控制
  - 会话过期清理

- [ ] 监控和日志
  - 关键操作埋点（搜题、生成、导出）
  - 错误日志记录
  - 性能指标统计

**验收标准**：
- 导出 Word 文件格式正确
- 单次出题总耗时 < 30 秒

---

### 总时间估算：10-14 天

**并行开发建议**：
- 阶段 1-2 可以并行（一人做 Agent，一人做 ES）
- 阶段 3-4 依赖阶段 2 完成
- 阶段 5 可以最后补充

---

## 风险与应对

### 风险 1：Elasticsearch 部署复杂度

**风险**：ES 配置复杂，Embedding 预计算耗时长

**应对**：
- 使用 Docker Compose 一键部署
- Embedding 计算使用异步任务（Celery），不阻塞主流程
- 提供 SQL 全文检索降级方案（功能受限但可用）

### 风险 2：LLM API 调用不稳定

**风险**：超时、限流、返回格式错误

**应对**：
- 设置 timeout 和重试机制（最多 3 次）
- 多 LLM 提供商备份（DeepSeek 主，Kimi 备）
- 返回格式校验，无效结果自动重试

### 风险 3：AI 生成题目质量不稳定

**风险**：生成的题目知识点偏离、答案错误

**应对**：
- Prompt 优化（提供详细示例）
- 参考题库风格生成（Few-shot Learning）
- 人工审核机制（教师标记低质量题目）

### 风险 4：题库数据质量问题

**风险**：知识点标注不准、难度分级不合理

**应对**：
- 数据预处理清洗（去重、格式统一）
- 人工抽查标注质量（抽查 5%）
- 提供反馈机制（教师标记错误题目）

---

## 附录

### 附录 A：18 种题型定义

详见 `smart-question-generator/SKILL.md` 第 3 节。

Demo 版重点支持：
- 选择题（单选）
- 填空题
- 解答题

### 附录 B：知识点库示例（初二数学）

```json
[
  {
    "kp_id": "kp_001",
    "kp_name": "一元二次方程",
    "parent_id": null,
    "children": [
      {"kp_id": "kp_001_01", "kp_name": "一元二次方程的定义"},
      {"kp_id": "kp_001_02", "kp_name": "解一元二次方程（因式分解法）"},
      {"kp_id": "kp_001_03", "kp_name": "解一元二次方程（配方法）"},
      {"kp_id": "kp_001_04", "kp_name": "解一元二次方程（求根公式）"},
      {"kp_id": "kp_001_05", "kp_name": "一元二次方程的应用"}
    ]
  },
  {
    "kp_id": "kp_002",
    "kp_name": "函数",
    "children": [
      {"kp_id": "kp_002_01", "kp_name": "函数的概念"},
      {"kp_id": "kp_002_02", "kp_name": "一次函数"},
      {"kp_id": "kp_002_03", "kp_name": "反比例函数"},
      {"kp_id": "kp_002_04", "kp_name": "二次函数"}
    ]
  }
]
```

### 附录 C：环境变量配置示例

```bash
# .env

# LLM API
LLM_PROVIDER=deepseek  # 或 kimi
DEEPSEEK_API_KEY=sk-xxxxx
KIMI_API_KEY=sk-xxxxx

# 数据库
DATABASE_URL=postgresql://user:password@localhost:5432/question_db

# Elasticsearch
ES_HOST=localhost
ES_PORT=9200
ES_INDEX=questions

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# 应用配置
DEBUG=true
LOG_LEVEL=INFO
SESSION_EXPIRE_SECONDS=3600
```

---

## 📁 项目目录结构（已创建）

```
AI_quiz_new/
├── backend/                              # 后端项目
│   ├── skills/                           # 🦞 Skill 层（OpenClaw 模式）
│   │   ├── __init__.py
│   │   ├── exam_skill.md                 # 出题 Skill 策略文档
│   │   ├── search_skill.md               # 搜题 Skill 策略文档
│   │   ├── adapt_skill.md                # 改编 Skill 策略文档（待创建）
│   │   ├── loader.py                     # Skill 加载器（渐进式加载）
│   │   └── base_skill.py                 # Skill 基类（待实现）
│   │
│   ├── workflows/                        # 🔧 Workflow 层（LangGraph）
│   │   ├── __init__.py
│   │   ├── base_workflow.py              # Workflow 基类（待实现）
│   │   ├── exam_workflow/                # 出题 Workflow
│   │   │   ├── __init__.py
│   │   │   ├── graph.py                  # 流程图定义（已创建）
│   │   │   ├── nodes.py                  # 节点函数（已创建）
│   │   │   ├── state.py                  # 状态定义（已创建）
│   │   │   └── config.yaml               # 配置文件（待创建）
│   │   ├── search_workflow/              # 搜题 Workflow（待创建）
│   │   ├── adapt_workflow/               # 改编 Workflow（待创建）
│   │   └── generate_workflow/            # 生成 Workflow（待创建）
│   │
│   ├── agents/                           # Agent 层（路由编排）
│   │   ├── __init__.py
│   │   └── main_agent.py                 # 主 Agent（已创建）
│   │
│   ├── tools/                            # 工具层（原子工具）
│   │   ├── __init__.py
│   │   ├── es_search_tool.py             # ES 检索工具（待实现）
│   │   ├── llm_generate_tool.py          # LLM 生成工具（待实现）
│   │   └── db_query_tool.py              # 数据库查询工具（待实现）
│   │
│   ├── services/                         # 业务服务层
│   │   ├── __init__.py
│   │   ├── llm_service.py                # LLM 调用服务（已创建）
│   │   ├── question_service.py           # 题库服务（待实现）
│   │   ├── es_service.py                 # ES 服务（待实现）
│   │   ├── exam_service.py               # 试卷服务（待实现）
│   │   └── embedding_service.py          # Embedding 服务（待实现）
│   │
│   ├── db/                               # 数据库层
│   │   ├── __init__.py
│   │   ├── connection.py                 # 数据库连接（待实现）
│   │   └── models.py                     # ORM 模型（待实现）
│   │
│   ├── skill_debug/                      # 🧪 Skill 调试平台
│   │   ├── __init__.py
│   │   ├── api/                          # 调试 API
│   │   │   ├── __init__.py
│   │   │   ├── playground.py             # 单次测试（待实现）
│   │   │   ├── batch_test.py             # 批量测试（待实现）
│   │   │   └── ab_test.py                # A/B 测试（待实现）
│   │   ├── evaluators/                   # 效果评估器
│   │   │   ├── __init__.py
│   │   │   ├── parameter_evaluator.py    # 参数提取评估（待实现）
│   │   │   └── question_evaluator.py     # 题目质量评估（待实现）
│   │   ├── test_cases/                   # 测试用例库
│   │   │   ├── exam_skill/
│   │   │   ├── search_skill/
│   │   │   └── adapt_skill/
│   │   ├── reports/                      # 测试报告
│   │   └── traces/                       # 执行追踪
│   │
│   ├── app/                              # FastAPI 应用层
│   │   ├── __init__.py
│   │   ├── main.py                       # FastAPI 入口（已创建）
│   │   ├── api/                          # API 路由
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── chat.py               # 对话接口（待实现）
│   │   │       ├── exams.py              # 试卷接口（待实现）
│   │   │       ├── questions.py          # 题目接口（待实现）
│   │   │       └── skill_debug.py        # Skill 调试接口（待实现）
│   │   ├── models/                       # Pydantic 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── request.py                # 请求模型（待实现）
│   │   │   └── response.py               # 响应模型（待实现）
│   │   ├── config/                       # 配置管理
│   │   │   ├── __init__.py
│   │   │   └── settings.py               # 环境变量配置（待实现）
│   │   └── middleware/                   # 中间件
│   │       ├── __init__.py
│   │       └── error_handler.py          # 错误处理（待实现）
│   │
│   ├── core/                             # 核心模块
│   │   ├── __init__.py
│   │   ├── enums.py                      # 枚举定义（待实现）
│   │   └── constants.py                  # 常量定义（待实现）
│   │
│   ├── utils/                            # 工具函数
│   │   ├── __init__.py
│   │   └── logger.py                     # 日志工具（待实现）
│   │
│   ├── tests/                            # 测试代码
│   │   ├── __init__.py
│   │   ├── conftest.py                   # Pytest 配置（待实现）
│   │   ├── unit/                         # 单元测试
│   │   ├── integration/                  # 集成测试
│   │   └── fixtures/                     # 测试数据
│   │
│   ├── scripts/                          # 脚本工具
│   │   ├── init_db.py                    # 初始化数据库（待实现）
│   │   ├── import_questions.py           # 题库导入（待实现）
│   │   └── build_es_index.py             # 构建 ES 索引（待实现）
│   │
│   ├── requirements.txt                  # Python 依赖（已创建）
│   ├── .env.example                      # 环境变量示例（待创建）
│   └── README.md                         # 项目说明（待创建）
│
├── frontend/                             # 前端项目（已有基础）
│   └── ...
│
├── docs/                                 # 项目文档
│   ├── DEVELOPMENT.md                    # 开发指南（待创建）
│   └── SKILL_GUIDE.md                    # Skill 编写指南（待创建）
│
├── PRD.md                                # 完整产品需求文档
├── PRD_demo.md                           # Demo 版需求文档（本文档）
├── CLAUDE.md                             # 项目指南
└── PROJECT_STRUCTURE.md                  # 项目结构说明
```

### 目录说明

#### 1. **Skills 层**（OpenClaw 模式）
- **文件格式**：Markdown 文档（`<skill>` 标签）
- **作用**：定义业务策略、参数规则、场景配置
- **编辑者**：教研人员（无需写代码）
- **加载方式**：渐进式加载到 System Prompt

#### 2. **Workflows 层**（LangGraph）
- **文件组成**：
  - `graph.py`：流程图定义（节点 + 边）
  - `nodes.py`：节点函数实现
  - `state.py`：状态 Schema 定义
  - `config.yaml`：可配置参数
- **作用**：确定性执行多步流程
- **维护者**：开发人员

#### 3. **Agents 层**
- **MainAgent**：主 Agent，负责：
  - 加载相关 Skill
  - 路由到对应 Workflow
  - 执行 Workflow 并返回结果

#### 4. **Services 层**
- **业务服务**：封装具体业务逻辑
  - `llm_service.py`：LLM 调用（支持多提供商）
  - `question_service.py`：题库查询
  - `es_service.py`：Elasticsearch 检索
  - `exam_service.py`：试卷组装

#### 5. **Skill Debug 平台**
- **作用**：教研人员迭代 Skill 的调试工具
- **功能**：
  - Playground：单次测试
  - Batch Test：批量测试
  - A/B Test：版本对比
  - Evaluators：效果评估（准确率、召回率）

---

## 总结

本 Demo 版 PRD 聚焦核心能力验证：
1. ✅ **智能追问**：ExamAgent 多轮对话提取参数
2. ✅ **场景策略**：4 种场景的难度/题型分布自动匹配
3. ✅ **智能搜题**：Elasticsearch 混合检索（语义 + 精准）
4. ✅ **AI 补充**：题库不足时，AI 生成题目（保持风格一致）
5. ✅ **试卷预览**：前端展示（题库题目 + AI 题目，带来源标签）

**开发时间**：10-14 天（2 人并行）

**下一步行动**：
1. 确认技术选型（LLM 提供商选哪个？）
2. 准备测试数据（100 道初二数学题）
3. 开始阶段 1 开发（FastAPI + ExamAgent）

有任何问题随时讨论！🚀
