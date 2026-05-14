# Skill 架构设计 - 完整版

## 核心理念

**Skill = 独立的 Agent 能力模块**
- 每个 Skill 是一个完整的 LangGraph 子图
- 有明确的输入、输出定义
- 包含完整的决策流程
- 可独立测试和迭代
- 可被主 Agent 或其他 Skill 调用

---

## 目录结构

```
backend/
├── skills/                              # 🎯 Skill 模块（核心）
│   ├── __init__.py
│   ├── base_skill.py                    # Skill 基类
│   │   # class BaseSkill(ABC):
│   │   #     @abstractmethod
│   │   #     def get_input_schema() -> dict
│   │   #     def get_output_schema() -> dict
│   │   #     def create_graph() -> CompiledGraph
│   │   #     async def execute(input_data) -> output_data
│   │   #     async def execute_with_trace(input_data) -> (output, trace)
│   │
│   ├── registry.py                      # Skill 注册中心
│   │   # SKILL_REGISTRY = {
│   │   #     "exam": ExamSkill,
│   │   #     "adapt": AdaptSkill,
│   │   #     "search": SearchSkill
│   │   # }
│   │
│   ├── exam_skill/                      # 📋 出题 Skill
│   │   ├── __init__.py
│   │   ├── skill.py                     # Skill 主入口
│   │   │   # class ExamSkill(BaseSkill):
│   │   │   #     """
│   │   │   #     出题 Skill
│   │   │   #     
│   │   │   #     输入：
│   │   │   #     {
│   │   │   #         "messages": [...],           # 对话历史
│   │   │   #         "initial_params": {...}      # 初始参数（可选）
│   │   │   #     }
│   │   │   #     
│   │   │   #     输出：
│   │   │   #     {
│   │   │   #         "exam_id": "...",
│   │   │   #         "questions": [...],
│   │   │   #         "total_score": 100,
│   │   │   #         "source_stats": {...}
│   │   │   #     }
│   │   │   #     """
│   │   │   #     def get_input_schema() -> dict
│   │   │   #     def get_output_schema() -> dict
│   │   │   #     def create_graph() -> CompiledGraph
│   │   │
│   │   ├── graph.py                     # Skill 的 LangGraph 子图
│   │   │   # def create_exam_graph(config: ExamSkillConfig) -> StateGraph:
│   │   │   #     """
│   │   │   #     构建出题流程图：
│   │   │   #     
│   │   │   #     开始 → 解析输入
│   │   │   #         ↓
│   │   │   #     提取参数 → 检查完整性
│   │   │   #         ├─ 不完整 → 生成追问 → 结束（等待用户）
│   │   │   #         └─ 完整 ↓
│   │   │   #     匹配场景策略
│   │   │   #         ↓
│   │   │   #     调用 SearchSkill（搜题）
│   │   │   #         ↓
│   │   │   #     分析缺口
│   │   │   #         ├─ 有缺口 → 调用 AI 生成 → 合并
│   │   │   #         └─ 无缺口 ↓
│   │   │   #     组装试卷
│   │   │   #         ↓
│   │   │   #     验证输出 → 结束
│   │   │   #     """
│   │   │   #     workflow = StateGraph(ExamSkillState)
│   │   │   #     workflow.add_node("parse_input", nodes.parse_input)
│   │   │   #     workflow.add_node("extract_params", nodes.extract_parameters)
│   │   │   #     ...
│   │   │   #     return workflow.compile()
│   │   │
│   │   ├── nodes.py                     # Skill 的节点函数
│   │   │   # async def parse_input(state: ExamSkillState) -> ExamSkillState:
│   │   │   #     """解析输入数据"""
│   │   │   #     ...
│   │   │   #
│   │   │   # async def extract_parameters(state: ExamSkillState) -> ExamSkillState:
│   │   │   #     """从对话中提取参数"""
│   │   │   #     ...
│   │   │   #
│   │   │   # async def match_scene_strategy(state: ExamSkillState) -> ExamSkillState:
│   │   │   #     """匹配场景策略"""
│   │   │   #     ...
│   │   │   #
│   │   │   # async def call_search_skill(state: ExamSkillState) -> ExamSkillState:
│   │   │   #     """调用搜题 Skill"""
│   │   │   #     from skills.search_skill.skill import SearchSkill
│   │   │   #     search_skill = SearchSkill()
│   │   │   #     result = await search_skill.execute({
│   │   │   #         "knowledge_points": state["extracted_params"]["knowledge_points"],
│   │   │   #         "allocation": state["allocation"]
│   │   │   #     })
│   │   │   #     state["search_results"] = result["questions"]
│   │   │   #     return state
│   │   │
│   │   ├── state.py                     # Skill 的状态定义
│   │   │   # class ExamSkillState(TypedDict):
│   │   │   #     """出题 Skill 的状态"""
│   │   │   #     # 输入
│   │   │   #     messages: List[Dict[str, str]]
│   │   │   #     initial_params: Optional[Dict]
│   │   │   #     
│   │   │   #     # 中间状态
│   │   │   #     current_step: str
│   │   │   #     extracted_params: Dict
│   │   │   #     is_complete: bool
│   │   │   #     scene_config: Optional[Dict]
│   │   │   #     allocation: Optional[Dict]
│   │   │   #     search_results: List[Question]
│   │   │   #     generated_questions: List[Question]
│   │   │   #     
│   │   │   #     # 输出
│   │   │   #     final_exam: Optional[Exam]
│   │   │   #     needs_followup: bool
│   │   │   #     followup_message: Optional[str]
│   │   │
│   │   ├── config.yaml                  # Skill 配置规则
│   │   │   # metadata:
│   │   │   #   name: "exam_skill"
│   │   │   #   version: "1.0"
│   │   │   #   description: "智能出题 Skill"
│   │   │   #
│   │   │   # input_schema:
│   │   │   #   messages:
│   │   │   #     type: array
│   │   │   #     required: true
│   │   │   #   initial_params:
│   │   │   #     type: object
│   │   │   #     required: false
│   │   │   #
│   │   │   # output_schema:
│   │   │   #   exam_id:
│   │   │   #     type: string
│   │   │   #     required: true
│   │   │   #   questions:
│   │   │   #     type: array
│   │   │   #     required: true
│   │   │   #
│   │   │   # parameter_extraction_rules:
│   │   │   #   required_fields: [...]
│   │   │   #   optional_fields: [...]
│   │   │   #
│   │   │   # scene_strategies:
│   │   │   #   homework: {...}
│   │   │   #   unit_test: {...}
│   │   │   #
│   │   │   # prompts:
│   │   │   #   system_prompt: |
│   │   │   #     你是专业的出题助手...
│   │   │
│   │   ├── prompts.py                   # Skill 的 Prompt 模板
│   │   │   # SYSTEM_PROMPT = """你是专业的 K12 出题助手..."""
│   │   │   #
│   │   │   # PARAMETER_EXTRACTION_PROMPT = """
│   │   │   # 从以下对话中提取参数：
│   │   │   # {conversation_history}
│   │   │   # """
│   │   │   #
│   │   │   # FOLLOWUP_PROMPT = """
│   │   │   # 已提取：{extracted_params}
│   │   │   # 缺失：{missing_params}
│   │   │   # 请生成追问...
│   │   │   # """
│   │   │
│   │   ├── tools.py                     # Skill 专属工具
│   │   │   # @tool
│   │   │   # def validate_parameters(params: dict, rules: dict) -> tuple[bool, list]:
│   │   │   #     """验证参数完整性"""
│   │   │   #     ...
│   │   │   #
│   │   │   # @tool
│   │   │   # def allocate_questions(scene_config: dict) -> dict:
│   │   │   #     """计算题目分配方案"""
│   │   │   #     ...
│   │   │
│   │   └── tests/                       # Skill 单元测试
│   │       ├── test_graph.py            # 测试流程图
│   │       ├── test_nodes.py            # 测试节点函数
│   │       └── test_integration.py      # 集成测试
│   │
│   ├── search_skill/                    # 🔍 搜题 Skill
│   │   ├── skill.py
│   │   │   # class SearchSkill(BaseSkill):
│   │   │   #     """
│   │   │   #     搜题 Skill
│   │   │   #     
│   │   │   #     输入：
│   │   │   #     {
│   │   │   #         "knowledge_points": [...],
│   │   │   #         "subject": "数学",
│   │   │   #         "grade": "初二",
│   │   │   #         "allocation": {
│   │   │   #             "choice": {"easy": 2, "medium": 3},
│   │   │   #             "blank": {...}
│   │   │   #         }
│   │   │   #     }
│   │   │   #     
│   │   │   #     输出：
│   │   │   #     {
│   │   │   #         "questions": [...],
│   │   │   #         "found_count": 12,
│   │   │   #         "required_count": 15,
│   │   │   #         "gap": 3,
│   │   │   #         "gap_breakdown": {...}
│   │   │   #     }
│   │   │   #     """
│   │   │
│   │   ├── graph.py
│   │   │   # def create_search_graph() -> StateGraph:
│   │   │   #     """
│   │   │   #     搜题流程图：
│   │   │   #     
│   │   │   #     开始 → 解析检索条件
│   │   │   #         ↓
│   │   │   #     ES 混合检索（语义 + 精准）
│   │   │   #         ↓
│   │   │   #     质量过滤（考频、评分）
│   │   │   #         ↓
│   │   │   #     按题型/难度分组
│   │   │   #         ↓
│   │   │   #     计算缺口
│   │   │   #         ↓
│   │   │   #     结束
│   │   │   #     """
│   │   │
│   │   ├── nodes.py
│   │   │   # async def es_search(state: SearchSkillState) -> SearchSkillState:
│   │   │   #     """执行 Elasticsearch 检索"""
│   │   │   #     ...
│   │   │   #
│   │   │   # async def quality_filter(state: SearchSkillState) -> SearchSkillState:
│   │   │   #     """质量过滤"""
│   │   │   #     ...
│   │   │
│   │   ├── state.py
│   │   ├── config.yaml
│   │   └── tests/
│   │
│   ├── adapt_skill/                     # ✏️ 改编 Skill
│   │   ├── skill.py
│   │   │   # class AdaptSkill(BaseSkill):
│   │   │   #     """
│   │   │   #     题目改编 Skill
│   │   │   #     
│   │   │   #     输入：
│   │   │   #     {
│   │   │   #         "original_question": {...},
│   │   │   #         "adapt_type": "increase_difficulty",  # 或 "change_type"
│   │   │   #         "target_difficulty": "hard",
│   │   │   #         "target_type": "blank"
│   │   │   #     }
│   │   │   #     
│   │   │   #     输出：
│   │   │   #     {
│   │   │   #         "adapted_question": {...},
│   │   │   #         "changes": ["难度提升", "题型改变"]
│   │   │   #     }
│   │   │   #     """
│   │   │
│   │   ├── graph.py
│   │   │   # def create_adapt_graph() -> StateGraph:
│   │   │   #     """
│   │   │   #     改编流程图：
│   │   │   #     
│   │   │   #     开始 → 分析原题（知识点、难度、题型）
│   │   │   #         ↓
│   │   │   #     确定改编策略
│   │   │   #         ↓
│   │   │   #     生成改编题目（LLM）
│   │   │   #         ↓
│   │   │   #     验证知识点一致性
│   │   │   #         ↓
│   │   │   #     验证难度/题型是否符合要求
│   │   │   #         ↓
│   │   │   #     结束
│   │   │   #     """
│   │   │
│   │   ├── nodes.py
│   │   ├── state.py
│   │   ├── config.yaml
│   │   └── tests/
│   │
│   └── generate_skill/                  # 🤖 AI生成 Skill
│       ├── skill.py
│       │   # class GenerateSkill(BaseSkill):
│       │   #     """
│       │   #     AI 生成题目 Skill
│       │   #     
│       │   #     输入：
│       │   #     {
│       │   #         "knowledge_points": [...],
│       │   #         "difficulty": "medium",
│       │   #         "question_type": "choice",
│       │   #         "count": 3,
│       │   #         "reference_questions": [...]  # 参考题库风格
│       │   #     }
│       │   #     
│       │   #     输出：
│       │   #     {
│       │   #         "questions": [...]
│       │   #     }
│       │   #     """
│       │
│       ├── graph.py
│       │   # def create_generate_graph() -> StateGraph:
│       │   #     """
│       │   #     生成流程图：
│       │   #     
│       │   #     开始 → 分析参考题目风格
│       │   #         ↓
│       │   #     构建生成 Prompt
│       │   #         ↓
│       │   #     调用 LLM 生成
│       │   #         ↓
│       │   #     解析和验证
│       │   #         ↓
│       │   #     质量检查（知识点、难度）
│       │   #         ├─ 不合格 → 重新生成（最多3次）
│       │   #         └─ 合格 ↓
│       │   #     结束
│       │   #     """
│       │
│       ├── nodes.py
│       ├── state.py
│       ├── config.yaml
│       └── tests/
│
├── agents/                              # 主 Agent（编排层）
│   ├── __init__.py
│   ├── main_agent.py                    # 主 Agent（调用 Skill）
│   │   # class MainAgent:
│   │   #     """
│   │   #     主 Agent，负责 Skill 编排
│   │   #     
│   │   #     根据用户请求决定调用哪个 Skill：
│   │   #     - "/exam generate" → ExamSkill
│   │   #     - "/question adapt" → AdaptSkill
│   │   #     - "/question search" → SearchSkill
│   │   #     """
│   │   #     def __init__(self):
│   │   #         self.skills = {
│   │   #             "exam": ExamSkill(),
│   │   #             "adapt": AdaptSkill(),
│   │   #             "search": SearchSkill()
│   │   #         }
│   │   #     
│   │   #     async def route_to_skill(self, request) -> str:
│   │   #         """路由到具体 Skill"""
│   │   #         ...
│   │   #     
│   │   #     async def execute(self, request):
│   │   #         skill_name = self.route_to_skill(request)
│   │   #         skill = self.skills[skill_name]
│   │   #         return await skill.execute(request)
│   │
│   └── router.py                        # Agent 路由逻辑
│
├── skill_debug/                         # 🧪 Skill 调试平台
│   ├── __init__.py
│   ├── api/
│   │   ├── playground.py                # Skill 单次测试
│   │   │   # @router.post("/skill-debug/playground")
│   │   │   # async def test_skill(
│   │   │   #     skill_name: str,       # "exam_skill"
│   │   │   #     version: str,          # "1.0"
│   │   │   #     input_data: dict,
│   │   │   #     enable_trace: bool = True
│   │   │   # ):
│   │   │   #     """单次测试 Skill"""
│   │   │   #     skill = load_skill(skill_name, version)
│   │   │   #     result, trace = await skill.execute_with_trace(input_data)
│   │   │   #     return {"result": result, "trace": trace}
│   │   │
│   │   ├── batch_test.py                # Skill 批量测试
│   │   │   # @router.post("/skill-debug/batch-test")
│   │   │   # async def batch_test_skill(
│   │   │   #     skill_name: str,
│   │   │   #     version: str,
│   │   │   #     test_cases: list
│   │   │   # ):
│   │   │   #     """批量测试 Skill，返回评估报告"""
│   │   │   #     ...
│   │   │
│   │   ├── ab_test.py                   # Skill A/B 测试
│   │   │   # @router.post("/skill-debug/ab-test")
│   │   │   # async def ab_test_skills(
│   │   │   #     skill_name: str,
│   │   │   #     version_a: str,
│   │   │   #     version_b: str,
│   │   │   #     test_cases: list
│   │   │   # ):
│   │   │   #     """对比两个版本的 Skill 效果"""
│   │   │   #     ...
│   │   │
│   │   └── graph_viz.py                 # Skill 流程图可视化
│   │       # @router.get("/skill-debug/visualize/{skill_name}")
│   │       # async def visualize_skill_graph(skill_name: str):
│   │       #     """生成 Skill 流程图（Mermaid/Graphviz）"""
│   │       #     ...
│   │
│   ├── evaluators/                      # Skill 效果评估器
│   │   ├── __init__.py
│   │   ├── base_evaluator.py           # 评估器基类
│   │   ├── exam_evaluator.py           # ExamSkill 评估器
│   │   │   # class ExamSkillEvaluator:
│   │   │   #     def evaluate_parameter_extraction(extracted, expected) -> dict
│   │   │   #     def evaluate_scene_matching(scene, expected) -> dict
│   │   │   #     def evaluate_question_quality(questions) -> dict
│   │   │
│   │   ├── search_evaluator.py         # SearchSkill 评估器
│   │   │   # class SearchSkillEvaluator:
│   │   │   #     def evaluate_recall(found, expected) -> float
│   │   │   #     def evaluate_relevance(questions, kps) -> float
│   │   │
│   │   └── adapt_evaluator.py          # AdaptSkill 评估器
│   │
│   ├── test_cases/                      # Skill 测试用例库
│   │   ├── exam_skill/
│   │   │   ├── parameter_extraction.json
│   │   │   │   # [
│   │   │   │   #   {
│   │   │   │   #     "id": "case_001",
│   │   │   │   #     "input": {
│   │   │   │   #       "messages": [{"role": "user", "content": "帮我出份初二数学单元测验"}]
│   │   │   │   #     },
│   │   │   │   #     "expected_output": {
│   │   │   │   #       "needs_followup": true,
│   │   │   │   #       "followup_message": "请问是关于哪个知识点？"
│   │   │   │   #     }
│   │   │   │   #   }
│   │   │   │   # ]
│   │   │   ├── scene_matching.json
│   │   │   └── end_to_end.json          # 端到端测试用例
│   │   │
│   │   ├── search_skill/
│   │   │   └── recall_test.json
│   │   │
│   │   └── adapt_skill/
│   │       └── difficulty_test.json
│   │
│   └── reports/                         # 测试报告存储
│       └── {timestamp}_{skill_name}_v{version}_report.json
│
├── app/                                 # FastAPI 应用层
│   ├── api/v1/
│   │   ├── chat.py                      # 对话接口（调用 MainAgent）
│   │   │   # @router.post("/sessions/{session_id}/chat")
│   │   │   # async def chat(session_id: str, message: str):
│   │   │   #     main_agent = MainAgent()
│   │   │   #     result = await main_agent.execute({
│   │   │   #         "session_id": session_id,
│   │   │   #         "message": message
│   │   │   #     })
│   │   │   #     return result
│   │   │
│   │   ├── exams.py                     # 试卷管理接口
│   │   │   # @router.post("/exams/generate")
│   │   │   # async def generate_exam(params: ExamParams):
│   │   │   #     exam_skill = ExamSkill()
│   │   │   #     result = await exam_skill.execute({
│   │   │   #         "messages": [],
│   │   │   #         "initial_params": params.dict()
│   │   │   #     })
│   │   │   #     return result
│   │   │
│   │   ├── questions.py                 # 题目操作接口
│   │   │   # @router.post("/questions/search")
│   │   │   # async def search_questions(params: SearchParams):
│   │   │   #     search_skill = SearchSkill()
│   │   │   #     result = await search_skill.execute(params.dict())
│   │   │   #     return result
│   │   │   #
│   │   │   # @router.post("/questions/{qid}/adapt")
│   │   │   # async def adapt_question(qid: str, adapt_type: str):
│   │   │   #     adapt_skill = AdaptSkill()
│   │   │   #     result = await adapt_skill.execute({
│   │   │   #         "original_question": get_question(qid),
│   │   │   #         "adapt_type": adapt_type
│   │   │   #     })
│   │   │   #     return result
│   │   │
│   │   └── skill_debug.py               # Skill 调试接口（挂载 skill_debug/api）
│   │
│   └── main.py                          # FastAPI 入口
│
└── services/                            # 业务服务层（被 Skill 调用）
    ├── llm_service.py                   # LLM 调用服务
    ├── es_service.py                    # Elasticsearch 服务
    ├── question_service.py              # 题库数据服务
    └── embedding_service.py             # Embedding 服务
```

---

## 核心概念解释

### 1. Skill 的完整性

每个 Skill 是一个**独立的 Agent 子任务**，包含：

#### a) 明确的输入输出（`skill.py`）
```python
class ExamSkill(BaseSkill):
    def get_input_schema(self) -> dict:
        return {
            "messages": {"type": "array", "required": True},
            "initial_params": {"type": "object", "required": False}
        }
    
    def get_output_schema(self) -> dict:
        return {
            "exam_id": {"type": "string"},
            "questions": {"type": "array"},
            "needs_followup": {"type": "boolean"},
            "followup_message": {"type": "string"}
        }
```

#### b) 完整的决策流程（`graph.py`）
```python
def create_exam_graph(config) -> StateGraph:
    workflow = StateGraph(ExamSkillState)
    
    # 添加节点（每个节点是一个决策步骤）
    workflow.add_node("extract_params", extract_parameters)
    workflow.add_node("check_completeness", check_completeness)
    workflow.add_node("generate_followup", generate_followup)
    workflow.add_node("match_scene", match_scene_strategy)
    workflow.add_node("search", call_search_skill)  # 调用其他 Skill
    workflow.add_node("generate", call_generate_skill)
    workflow.add_node("assemble", assemble_exam)
    
    # 定义流程（决策逻辑）
    workflow.set_entry_point("extract_params")
    workflow.add_edge("extract_params", "check_completeness")
    
    # 条件分支（决策点）
    workflow.add_conditional_edges(
        "check_completeness",
        lambda state: "complete" if state["is_complete"] else "incomplete",
        {
            "incomplete": "generate_followup",
            "complete": "match_scene"
        }
    )
    
    workflow.add_edge("generate_followup", END)
    workflow.add_edge("match_scene", "search")
    
    # 另一个决策点
    workflow.add_conditional_edges(
        "search",
        lambda state: "has_gap" if state["gap"] > 0 else "no_gap",
        {
            "has_gap": "generate",
            "no_gap": "assemble"
        }
    )
    
    workflow.add_edge("generate", "assemble")
    workflow.add_edge("assemble", END)
    
    return workflow.compile()
```

#### c) 配置规则（`config.yaml`）
```yaml
# Skill 的参数化配置
parameter_extraction_rules:
  required_fields:
    - name: "subject"
      validation: {enum: ["数学", "物理", ...]}
    - name: "grade"
      validation: {enum: ["初一", "初二", ...]}

scene_strategies:
  homework:
    difficulty_distribution: {easy: 0.5, medium: 0.4, hard: 0.1}
    question_type_distribution: {choice: 0.3, blank: 0.4, solution: 0.3}
```

#### d) 状态管理（`state.py`）
```python
class ExamSkillState(TypedDict):
    # 输入
    messages: List[Dict]
    initial_params: Optional[Dict]
    
    # 中间状态
    extracted_params: Dict
    is_complete: bool
    scene_config: Dict
    search_results: List[Question]
    gap: int
    
    # 输出
    final_exam: Optional[Exam]
    needs_followup: bool
    followup_message: Optional[str]
```

---

### 2. Skill 之间的调用

**ExamSkill 调用 SearchSkill**：

```python
# skills/exam_skill/nodes.py

async def call_search_skill(state: ExamSkillState) -> ExamSkillState:
    """调用搜题 Skill"""
    from skills.search_skill.skill import SearchSkill
    
    # 构建 SearchSkill 的输入
    search_input = {
        "knowledge_points": state["extracted_params"]["knowledge_points"],
        "subject": state["extracted_params"]["subject"],
        "grade": state["extracted_params"]["grade"],
        "allocation": state["allocation"]  # 题目分配方案
    }
    
    # 调用 SearchSkill
    search_skill = SearchSkill()
    search_result = await search_skill.execute(search_input)
    
    # 更新状态
    state["search_results"] = search_result["questions"]
    state["gap"] = search_result["gap"]
    
    return state
```

---

### 3. Skill 的版本管理

每个 Skill 可以有多个版本：

```
skills/exam_skill/
├── versions/
│   ├── v1.0/
│   │   ├── config.yaml
│   │   ├── prompts.py
│   │   └── graph.py
│   ├── v1.1/
│   │   └── config.yaml  # 只修改配置，复用 v1.0 的代码
│   └── v2.0/
│       └── graph.py     # 修改流程图
└── skill.py             # 主入口，支持加载不同版本
```

```python
class ExamSkill(BaseSkill):
    def __init__(self, version: str = "latest"):
        self.version = version
        self.config = self._load_config(version)
        self.graph = self._load_graph(version)
    
    def _load_config(self, version):
        if version == "latest":
            version = self._get_latest_version()
        config_path = f"skills/exam_skill/versions/v{version}/config.yaml"
        return yaml.safe_load(open(config_path))
```

---

### 4. Skill 的调试流程

教研人员迭代 Skill 的完整流程：

#### 步骤 1：修改 Skill
- 调整 `config.yaml`（修改场景策略）
- 或修改 `graph.py`（改变决策流程）
- 或修改 `prompts.py`（优化 Prompt）

#### 步骤 2：单次测试
```bash
POST /skill-debug/playground
{
  "skill_name": "exam_skill",
  "version": "1.1",
  "input_data": {
    "messages": [{"role": "user", "content": "帮我出份初二数学单元测验"}]
  },
  "enable_trace": true
}
```

查看：
- 提取的参数是否正确
- 流程图执行路径
- 每个节点的耗时
- LLM 调用次数和 token 消耗

#### 步骤 3：批量测试
```bash
POST /skill-debug/batch-test
{
  "skill_name": "exam_skill",
  "version": "1.1",
  "test_cases": "exam_skill/parameter_extraction.json"
}
```

查看：
- 准确率、召回率、F1
- 失败的用例列表

#### 步骤 4：A/B 测试
```bash
POST /skill-debug/ab-test
{
  "skill_name": "exam_skill",
  "version_a": "1.0",
  "version_b": "1.1",
  "test_cases": "exam_skill/end_to_end.json"
}
```

对比：
- 准确率提升 +5%
- F1 提升 +3%
- 推荐版本：1.1

#### 步骤 5：发布新版本
```python
# 主 Agent 自动加载最新版本
exam_skill = ExamSkill(version="latest")
```

---

## 总结：Skill 的核心价值

### 1. **完整性**
- 每个 Skill 是独立的 Agent 子任务
- 有明确的输入、输出、决策流程
- 可独立运行和测试

### 2. **可复用性**
- Skill 可被主 Agent 调用
- Skill 之间可以互相调用
- 一次实现，多处使用

### 3. **可迭代性**
- 教研人员可修改配置（YAML）
- 可修改流程图（graph.py）
- 可修改 Prompt（prompts.py）
- 版本管理，随时回滚

### 4. **可测试性**
- 单元测试（节点函数）
- 集成测试（完整流程）
- 批量测试（测试用例库）
- A/B 测试（版本对比）

### 5. **可观测性**
- 执行追踪（Trace）
- 流程图可视化
- 效果指标统计
- 失败用例分析

---

## 下一步

现在架构清晰了，我可以：

**A. 创建完整的目录结构**（所有 Skill 目录 + 核心文件）

**B. 实现第一个 Skill**（ExamSkill 完整实现）

**C. 实现 Skill 调试平台**（Playground + 批量测试 + A/B 测试）

**D. 编写开发文档**（如何创建新 Skill、如何调试 Skill）

你想从哪个开始？或者还有哪里需要调整的？
