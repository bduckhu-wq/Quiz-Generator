# 项目目录结构 - 基于 LangGraph

```
AI_quiz_new/
├── backend/                              # 后端项目根目录
│   ├── app/                              # FastAPI 应用
│   │   ├── __init__.py
│   │   ├── main.py                       # FastAPI 入口，定义所有路由
│   │   ├── api/                          # API 路由层
│   │   │   ├── __init__.py
│   │   │   ├── v1/                       # API v1 版本
│   │   │   │   ├── __init__.py
│   │   │   │   ├── sessions.py           # 会话管理接口
│   │   │   │   ├── chat.py               # 对话接口（SSE 流式）
│   │   │   │   ├── exams.py              # 试卷生成/管理接口
│   │   │   │   ├── questions.py          # 单题操作接口
│   │   │   │   └── export.py             # 导出接口
│   │   │   └── deps.py                   # 依赖注入（数据库、服务等）
│   │   ├── models/                       # Pydantic 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── request.py                # 请求模型
│   │   │   ├── response.py               # 响应模型
│   │   │   ├── question.py               # 题目模型
│   │   │   ├── exam.py                   # 试卷模型
│   │   │   └── session.py                # 会话模型
│   │   ├── config/                       # 配置管理
│   │   │   ├── __init__.py
│   │   │   ├── settings.py               # 环境变量配置
│   │   │   └── logging.py                # 日志配置
│   │   └── middleware/                   # 中间件
│   │       ├── __init__.py
│   │       ├── cors.py                   # CORS 配置
│   │       └── error_handler.py          # 统一错误处理
│   │
│   ├── agents/                           # LangGraph Agent 核心
│   │   ├── __init__.py
│   │   ├── graphs/                       # 图定义（核心流程编排）
│   │   │   ├── __init__.py
│   │   │   ├── exam_graph.py             # 出题流程图
│   │   │   │   # 流程：对话 → 参数提取 → 场景匹配 → 搜题 → AI生成 → 组卷
│   │   │   └── adapt_graph.py            # 单题改编流程图
│   │   │       # 流程：分析原题 → 确定改编策略 → 生成新题 → 验证
│   │   ├── nodes/                        # 节点函数（每个节点是一个处理步骤）
│   │   │   ├── __init__.py
│   │   │   ├── chat_nodes.py             # 对话相关节点
│   │   │   │   # - parse_user_input: 解析用户输入
│   │   │   │   # - extract_parameters: 参数提取
│   │   │   │   # - generate_followup: 生成追问
│   │   │   │   # - check_completeness: 检查参数完整性
│   │   │   ├── search_nodes.py           # 搜题相关节点
│   │   │   │   # - search_questions: 从题库检索
│   │   │   │   # - analyze_gap: 分析缺口
│   │   │   ├── generate_nodes.py         # 生成相关节点
│   │   │   │   # - generate_questions: AI 生成题目
│   │   │   │   # - validate_questions: 验证题目质量
│   │   │   ├── assemble_nodes.py         # 组卷相关节点
│   │   │   │   # - assemble_exam: 组装试卷
│   │   │   │   # - calculate_scores: 计算分值
│   │   │   └── adapt_nodes.py            # 改编相关节点
│   │   │       # - analyze_question: 分析原题
│   │   │       # - adapt_difficulty: 调整难度
│   │   │       # - adapt_type: 改题型
│   │   ├── states/                       # 状态定义（LangGraph State）
│   │   │   ├── __init__.py
│   │   │   ├── exam_state.py             # 出题流程状态
│   │   │   │   # class ExamState(TypedDict):
│   │   │   │   #     messages: List[Message]
│   │   │   │   #     extracted_params: Dict
│   │   │   │   #     scene_config: Dict
│   │   │   │   #     search_results: List[Question]
│   │   │   │   #     generated_questions: List[Question]
│   │   │   │   #     final_exam: Exam
│   │   │   │   #     current_step: str
│   │   │   └── adapt_state.py            # 改编流程状态
│   │   ├── prompts/                      # Prompt 模板
│   │   │   ├── __init__.py
│   │   │   ├── exam_prompts.py           # 出题相关 Prompt
│   │   │   │   # - PARAMETER_EXTRACTION_PROMPT
│   │   │   │   # - FOLLOWUP_GENERATION_PROMPT
│   │   │   │   # - QUESTION_GENERATION_PROMPT
│   │   │   └── adapt_prompts.py          # 改编相关 Prompt
│   │   └── utils/                        # Agent 工具函数
│   │       ├── __init__.py
│   │       ├── state_helpers.py          # 状态操作辅助函数
│   │       └── routing.py                # 路由逻辑（条件判断）
│   │
│   ├── tools/                            # LangGraph Tools（可被 Agent 调用）
│   │   ├── __init__.py
│   │   ├── exam_tools.py                 # 出题工具
│   │   │   # @tool
│   │   │   # def extract_parameters(conversation: str) -> dict:
│   │   │   #     """从对话中提取结构化参数"""
│   │   │   #     ...
│   │   │   #
│   │   │   # @tool
│   │   │   # def match_scene_strategy(scene: str) -> dict:
│   │   │   #     """匹配场景策略"""
│   │   │   #     ...
│   │   ├── search_tools.py               # 搜题工具
│   │   │   # @tool
│   │   │   # def search_questions_from_db(params: dict) -> list:
│   │   │   #     """从题库检索题目"""
│   │   │   #     ...
│   │   └── generate_tools.py             # 生成工具
│   │       # @tool
│   │       # def generate_question_by_ai(
│   │       #     knowledge_points: list,
│   │       #     difficulty: str,
│   │       #     question_type: str,
│   │       #     reference_questions: list
│   │       # ) -> dict:
│   │       #     """AI 生成题目"""
│   │       #     ...
│   │
│   ├── services/                         # 业务服务层
│   │   ├── __init__.py
│   │   ├── llm_service.py                # LLM 调用封装
│   │   │   # class LLMService:
│   │   │   #     def __init__(self, provider: str)
│   │   │   #     async def chat(self, messages, tools, stream)
│   │   │   #     async def embed(self, text)
│   │   ├── question_service.py           # 题库业务逻辑
│   │   │   # class QuestionService:
│   │   │   #     async def search(self, params) -> list
│   │   │   #     async def get_by_id(self, qid) -> Question
│   │   │   #     async def get_similar(self, qid, count) -> list
│   │   ├── elasticsearch_service.py      # ES 检索服务
│   │   │   # class ESService:
│   │   │   #     async def hybrid_search(...)
│   │   │   #     async def index_question(...)
│   │   ├── exam_service.py               # 试卷业务逻辑
│   │   │   # class ExamService:
│   │   │   #     async def save_exam(self, exam)
│   │   │   #     async def get_exam(self, exam_id)
│   │   │   #     async def export_word(self, exam_id)
│   │   ├── session_service.py            # 会话管理
│   │   │   # class SessionService:
│   │   │   #     async def create_session() -> str
│   │   │   #     async def get_session(session_id) -> dict
│   │   │   #     async def update_session(session_id, data)
│   │   └── embedding_service.py          # Embedding 服务
│   │       # class EmbeddingService:
│   │       #     def embed_text(self, text) -> list[float]
│   │       #     def embed_batch(self, texts) -> list[list[float]]
│   │
│   ├── db/                               # 数据库层
│   │   ├── __init__.py
│   │   ├── connection.py                 # 数据库连接
│   │   │   # async_engine = create_async_engine(...)
│   │   │   # AsyncSessionLocal = sessionmaker(...)
│   │   ├── models.py                     # SQLAlchemy ORM 模型
│   │   │   # class Question(Base):
│   │   │   #     __tablename__ = "questions"
│   │   │   #     question_id = Column(String, primary_key=True)
│   │   │   #     subject = Column(String)
│   │   │   #     ...
│   │   │   #
│   │   │   # class ExamHistory(Base):
│   │   │   #     __tablename__ = "exam_history"
│   │   │   #     ...
│   │   ├── repositories.py               # 数据访问层（Repository 模式）
│   │   │   # class QuestionRepository:
│   │   │   #     async def find_by_filters(self, filters) -> list
│   │   │   #     async def find_by_id(self, qid) -> Question
│   │   │   #     ...
│   │   │   #
│   │   │   # class ExamRepository:
│   │   │   #     async def save(self, exam) -> str
│   │   │   #     async def find_by_id(self, exam_id) -> Exam
│   │   └── migrations/                   # Alembic 数据库迁移
│   │       ├── versions/
│   │       └── env.py
│   │
│   ├── core/                             # 核心模块
│   │   ├── __init__.py
│   │   ├── enums.py                      # 枚举定义
│   │   │   # class QuestionType(str, Enum):
│   │   │   #     CHOICE = "choice"
│   │   │   #     BLANK = "blank"
│   │   │   #     ...
│   │   │   #
│   │   │   # class Difficulty(str, Enum):
│   │   │   #     EASY = "easy"
│   │   │   #     MEDIUM = "medium"
│   │   │   #     HARD = "hard"
│   │   │   #
│   │   │   # class ExamScene(str, Enum):
│   │   │   #     HOMEWORK = "homework"
│   │   │   #     UNIT_TEST = "unit_test"
│   │   │   #     EXAM = "exam"
│   │   │   #     REVIEW = "review"
│   │   ├── constants.py                  # 常量定义
│   │   │   # SCENE_STRATEGIES = {...}
│   │   │   # QUESTION_TYPE_SCORES = {...}
│   │   ├── exceptions.py                 # 自定义异常
│   │   │   # class QuestionNotFoundError(Exception)
│   │   │   # class ESSearchError(Exception)
│   │   │   # class LLMAPIError(Exception)
│   │   └── security.py                   # 安全相关（API Key 验证等）
│   │
│   ├── utils/                            # 通用工具函数
│   │   ├── __init__.py
│   │   ├── logger.py                     # 日志工具
│   │   ├── redis_client.py               # Redis 客户端
│   │   ├── json_helper.py                # JSON 序列化工具
│   │   ├── time_helper.py                # 时间处理工具
│   │   └── word_exporter.py              # Word 导出工具
│   │       # class WordExporter:
│   │       #     def export(self, exam, include_answer) -> bytes
│   │
│   ├── tests/                            # 测试代码
│   │   ├── __init__.py
│   │   ├── conftest.py                   # Pytest 配置
│   │   ├── unit/                         # 单元测试
│   │   │   ├── test_agents/
│   │   │   ├── test_services/
│   │   │   └── test_tools/
│   │   ├── integration/                  # 集成测试
│   │   │   ├── test_api/
│   │   │   └── test_graph_flow/
│   │   └── fixtures/                     # 测试数据
│   │       ├── sample_questions.json
│   │       └── sample_conversations.json
│   │
│   ├── scripts/                          # 脚本工具
│   │   ├── init_db.py                    # 初始化数据库
│   │   ├── import_questions.py           # 题库导入
│   │   │   # 从 Excel/JSON 导入题目到 PostgreSQL
│   │   ├── build_es_index.py             # 构建 ES 索引
│   │   │   # 从 PostgreSQL 同步到 Elasticsearch
│   │   ├── compute_embeddings.py         # 批量计算 Embedding
│   │   │   # 为所有题目生成向量并存入 ES
│   │   └── test_llm_connection.py        # 测试 LLM 连接
│   │
│   ├── requirements.txt                  # Python 依赖
│   ├── requirements-dev.txt              # 开发依赖
│   ├── pyproject.toml                    # 项目配置（Poetry）
│   ├── .env.example                      # 环境变量示例
│   ├── .gitignore
│   └── README.md
│
├── frontend/                             # 前端项目（已有）
│   ├── src/
│   │   ├── app/                          # Next.js App Router
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx                  # 首页
│   │   │   ├── chat/
│   │   │   │   └── [sessionId]/
│   │   │   │       └── page.tsx          # 对话页面
│   │   │   └── exam/
│   │   │       └── [examId]/
│   │   │           └── page.tsx          # 试卷预览页
│   │   ├── components/                   # 组件
│   │   │   ├── chat/
│   │   │   │   ├── ChatWindow.tsx        # 对话窗口
│   │   │   │   ├── MessageList.tsx
│   │   │   │   └── InputBox.tsx
│   │   │   ├── exam/
│   │   │   │   ├── ParameterPanel.tsx    # 参数确认面板
│   │   │   │   ├── ExamPreview.tsx       # 试卷预览
│   │   │   │   ├── QuestionCard.tsx      # 单题卡片
│   │   │   │   └── ProgressIndicator.tsx # 搜题进度
│   │   │   └── ui/                       # 基础 UI 组件
│   │   ├── hooks/
│   │   │   ├── useSSE.ts                 # SSE 流式消费
│   │   │   ├── useChat.ts                # 对话逻辑
│   │   │   └── useExam.ts                # 试卷操作
│   │   ├── lib/
│   │   │   ├── api.ts                    # API 客户端
│   │   │   └── utils.ts
│   │   └── types/
│   │       ├── question.ts
│   │       ├── exam.ts
│   │       └── api.ts
│   ├── package.json
│   └── tsconfig.json
│
├── docs/                                 # 项目文档
│   ├── architecture.md                   # 架构设计
│   ├── api_spec.md                       # API 接口规范
│   ├── langgraph_flow.md                 # LangGraph 流程说明
│   └── deployment.md                     # 部署指南
│
├── docker/                               # Docker 配置
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   └── nginx.conf
│
├── docker-compose.yml                    # Docker Compose 配置
│   # 服务：
│   #   - backend: FastAPI + LangGraph
│   #   - frontend: Next.js
│   #   - postgres: PostgreSQL
│   #   - elasticsearch: Elasticsearch
│   #   - redis: Redis
│   #   - nginx: 反向代理
│
├── PRD.md                                # 完整产品需求文档
├── PRD_demo.md                           # Demo 版需求文档
├── CLAUDE.md                             # 项目指南（当前文档）
└── .claude/                              # Claude Code 配置
    ├── settings.json
    └── rules/
        └── code-style.md
```

---

## 核心目录说明

### 1. `agents/graphs/` - LangGraph 流程编排

这是 LangGraph 的核心，定义了整个 Agent 的执行流程。

**示例：`exam_graph.py`**
```python
from langgraph.graph import StateGraph, END
from agents.states.exam_state import ExamState
from agents.nodes import chat_nodes, search_nodes, generate_nodes, assemble_nodes

def create_exam_graph():
    """
    创建出题流程图
    
    流程：
    1. 解析用户输入
    2. 提取参数
    3. 检查完整性
       - 不完整 → 生成追问 → 回到步骤 1
       - 完整 → 进入步骤 4
    4. 匹配场景策略
    5. 从题库搜题
    6. 分析缺口
    7. AI 生成补充（如果需要）
    8. 组装试卷
    9. 结束
    """
    workflow = StateGraph(ExamState)
    
    # 添加节点
    workflow.add_node("parse_input", chat_nodes.parse_user_input)
    workflow.add_node("extract_params", chat_nodes.extract_parameters)
    workflow.add_node("generate_followup", chat_nodes.generate_followup)
    workflow.add_node("match_scene", chat_nodes.match_scene_strategy)
    workflow.add_node("search", search_nodes.search_questions)
    workflow.add_node("analyze_gap", search_nodes.analyze_gap)
    workflow.add_node("generate", generate_nodes.generate_questions)
    workflow.add_node("assemble", assemble_nodes.assemble_exam)
    
    # 设置入口
    workflow.set_entry_point("parse_input")
    
    # 添加边（流程控制）
    workflow.add_edge("parse_input", "extract_params")
    
    # 条件边：检查参数完整性
    workflow.add_conditional_edges(
        "extract_params",
        should_continue_chat,  # 判断函数
        {
            "continue": "generate_followup",  # 参数不完整，继续追问
            "done": "match_scene"              # 参数完整，进入出题
        }
    )
    
    workflow.add_edge("generate_followup", END)  # 返回追问，等待用户回复
    workflow.add_edge("match_scene", "search")
    workflow.add_edge("search", "analyze_gap")
    
    # 条件边：是否需要 AI 生成
    workflow.add_conditional_edges(
        "analyze_gap",
        need_ai_generation,  # 判断函数
        {
            "yes": "generate",
            "no": "assemble"
        }
    )
    
    workflow.add_edge("generate", "assemble")
    workflow.add_edge("assemble", END)
    
    return workflow.compile()


def should_continue_chat(state: ExamState) -> str:
    """判断是否需要继续追问"""
    params = state["extracted_params"]
    
    # 检查必需参数
    required = ["subject", "grade", "knowledge_points"]
    if all(params.get(k) for k in required):
        return "done"
    return "continue"


def need_ai_generation(state: ExamState) -> str:
    """判断是否需要 AI 生成"""
    gap = state["gap_analysis"]
    return "yes" if gap["total_gap"] > 0 else "no"
```

### 2. `agents/nodes/` - 节点函数

每个节点是一个独立的处理函数，接收 State，返回更新后的 State。

**示例：`chat_nodes.py`**
```python
from agents.states.exam_state import ExamState
from services.llm_service import LLMService

llm = LLMService(provider="deepseek")

async def extract_parameters(state: ExamState) -> ExamState:
    """
    从对话历史中提取结构化参数
    """
    messages = state["messages"]
    
    # 调用 LLM 提取参数
    result = await llm.chat(
        messages=[
            {"role": "system", "content": PARAMETER_EXTRACTION_PROMPT},
            *messages
        ],
        tools=[extract_parameters_tool],  # 工具调用
        stream=False
    )
    
    # 更新状态
    extracted = result["tool_calls"][0]["arguments"]
    state["extracted_params"].update(extracted)
    state["current_step"] = "parameter_extraction"
    
    return state
```

### 3. `agents/states/` - 状态定义

定义 LangGraph 的 State Schema。

**示例：`exam_state.py`**
```python
from typing import TypedDict, List, Dict, Optional
from app.models.question import Question
from app.models.exam import Exam

class ExamState(TypedDict):
    """出题流程的状态"""
    
    # 对话相关
    messages: List[Dict[str, str]]          # 对话历史
    current_step: str                       # 当前步骤
    
    # 参数提取
    extracted_params: Dict                   # 提取的参数
    is_params_complete: bool                 # 参数是否完整
    
    # 场景策略
    scene_config: Optional[Dict]             # 场景配置
    
    # 搜题结果
    search_results: List[Question]           # 题库搜索结果
    gap_analysis: Optional[Dict]             # 缺口分析
    
    # AI 生成
    generated_questions: List[Question]      # AI 生成的题目
    
    # 最终试卷
    final_exam: Optional[Exam]               # 组装后的试卷
    
    # 元数据
    session_id: str                          # 会话 ID
    user_id: Optional[str]                   # 用户 ID
    created_at: str                          # 创建时间
```

### 4. `services/` - 业务逻辑层

封装具体的业务逻辑，被 nodes 和 tools 调用。

**示例：`llm_service.py`**
```python
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

class LLMService:
    """
    LLM 调用服务，支持多提供商
    """
    def __init__(self, provider: str):
        self.provider = provider
        self.client = self._init_client(provider)
    
    def _init_client(self, provider: str):
        if provider == "deepseek":
            return ChatOpenAI(
                base_url="https://api.deepseek.com",
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                model="deepseek-v4-pro",
                streaming=True
            )
        elif provider == "claude":
            return ChatAnthropic(
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                model="claude-3-5-sonnet-20241022",
                streaming=True
            )
        # ... 其他提供商
    
    async def chat(self, messages, tools=None, stream=True):
        if stream:
            return self.client.astream(messages, tools=tools)
        else:
            return await self.client.ainvoke(messages, tools=tools)
```

---

## LangGraph 核心优势（对比自己实现）

| 功能 | 自己实现 | LangGraph |
|-----|---------|-----------|
| **状态管理** | 手动维护 State 字典 | 自动管理，类型安全 |
| **流程编排** | 手动 if-else 控制 | 图结构，清晰可视化 |
| **流式输出** | 手动处理 SSE | `astream_events()` 原生支持 |
| **工具调用** | 手动解析和执行 | 自动处理 Tool Calling |
| **可视化调试** | 日志查看 | LangSmith 可视化追踪 |
| **状态持久化** | 手动存储 | Checkpointer 自动持久化 |
| **并发控制** | 手动处理 | 内置并发节点支持 |

---

## 关键文件依赖关系

```
FastAPI main.py
    ↓
API Routes (chat.py)
    ↓
LangGraph (exam_graph.py)
    ↓
Nodes (chat_nodes.py, search_nodes.py, ...)
    ↓
Services (llm_service.py, question_service.py, ...)
    ↓
Repositories (db/repositories.py)
    ↓
Database / Elasticsearch
```

---

## 下一步

这个目录结构确认后，我可以：

1. **创建完整的目录结构**（用 `mkdir` 和 `touch` 命令）
2. **实现第一个 LangGraph 流程**（`exam_graph.py`）
3. **编写核心节点函数**（参数提取节点）
4. **配置 FastAPI SSE 接口**（对接 LangGraph 的流式输出）

你觉得这个结构如何？有需要调整的地方吗？
