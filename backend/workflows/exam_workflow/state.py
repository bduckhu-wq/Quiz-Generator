"""
ExamWorkflow 状态定义
"""

from typing import TypedDict, List, Dict, Optional, Annotated
from operator import add


class ExamWorkflowState(TypedDict):
    """
    出题 Workflow 的状态

    LangGraph 会在节点之间传递这个状态对象，
    每个节点读取状态、执行逻辑、更新状态
    """

    # ========== 输入 ==========
    messages: List[Dict[str, str]]
    """对话历史，格式: [{"role": "user", "content": "..."}]
    注意：不使用 add operator，避免重复累加"""

    user_input: str
    """用户当前输入"""

    session_id: str
    """会话 ID"""

    skill_context: Optional[str]
    """Skill 策略文档内容（从 SkillLoader 加载）"""

    initial_params: Optional[Dict]
    """初始参数（如果用户直接提供）"""

    # ========== 中间状态 ==========
    current_step: str
    """当前执行步骤，用于追踪流程"""

    extracted_params: Dict
    """
    提取的参数，格式:
    {
        "subject": "数学",
        "grade": "初二",
        "knowledge_points": ["一元二次方程"],
        "scene": "unit_test"
    }
    """

    is_params_complete: bool
    """参数是否完整（学科 + 年级 + 知识点齐全）"""

    missing_params: List[str]
    """缺失的参数列表，用于生成追问"""

    scene_config: Optional[Dict]
    """
    场景策略配置，格式:
    {
        "scene": "unit_test",
        "difficulty_distribution": {"easy": 0.3, "medium": 0.5, "hard": 0.2},
        "question_type_distribution": {"choice": 0.4, "blank": 0.3, "solution": 0.3},
        "total_count": 15,
        "total_score": 100
    }
    """

    allocation: Optional[Dict]
    """
    题目分配方案，格式:
    {
        "choice": {"easy": 2, "medium": 3, "hard": 1},
        "blank": {"easy": 1, "medium": 2, "hard": 1},
        "solution": {"easy": 1, "medium": 2, "hard": 2}
    }
    """

    search_results: List[Dict]
    """从题库搜索到的题目列表"""

    gap: int
    """题目缺口（需要 AI 生成的题目数量）"""

    gap_breakdown: Optional[Dict]
    """
    缺口明细，格式:
    {
        "choice": {"easy": 0, "medium": 0, "hard": 0},
        "solution": {"easy": 0, "medium": 1, "hard": 2}
    }
    """

    generated_questions: List[Dict]
    """AI 生成的题目列表"""

    # ========== 输出 ==========
    final_exam: Optional[Dict]
    """
    最终试卷，格式:
    {
        "exam_id": "...",
        "questions": [...],
        "total_score": 100,
        "source_stats": {"database": 12, "ai": 3}
    }
    """

    needs_followup: bool
    """是否需要追问用户"""

    followup_message: Optional[str]
    """追问的消息内容"""

    error: Optional[str]
    """错误信息（如果执行失败）"""

    # ========== 元数据 ==========
    execution_trace: List[Dict]
    """
    执行追踪记录（用于调试），格式:
    [
        {"step": "extract_params", "timestamp": "...", "duration": 0.5},
        ...
    ]
    注意：不使用 add operator，避免重复累加
    """


# 状态初始化函数
def create_initial_state(
    user_input: str,
    session_id: str,
    skill_context: str = "",
    messages: List[Dict[str, str]] = None
) -> ExamWorkflowState:
    """
    创建初始状态

    Args:
        user_input: 用户输入
        session_id: 会话 ID
        skill_context: Skill 策略文档
        messages: 对话历史（可选）

    Returns:
        ExamWorkflowState 初始状态
    """
    return ExamWorkflowState(
        # 输入
        messages=messages or [],
        user_input=user_input,
        session_id=session_id,
        skill_context=skill_context,
        initial_params=None,

        # 中间状态
        current_step="start",
        extracted_params={},
        is_params_complete=False,
        missing_params=[],
        scene_config=None,
        allocation=None,
        search_results=[],
        gap=0,
        gap_breakdown=None,
        generated_questions=[],

        # 输出
        final_exam=None,
        needs_followup=False,
        followup_message=None,
        error=None,

        # 元数据
        execution_trace=[]
    )
