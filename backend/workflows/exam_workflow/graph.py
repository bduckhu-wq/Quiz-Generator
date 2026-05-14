"""
ExamWorkflow 流程图定义 - LangGraph
"""

from langgraph.graph import StateGraph, END
from .state import ExamWorkflowState
from . import nodes


def create_exam_workflow() -> StateGraph:
    """
    创建出题 Workflow 流程图

    流程：
    1. 解析输入 → 提取参数
    2. 检查参数完整性
        ├─ 不完整 → 生成追问 → END（等待用户回复）
        └─ 完整 ↓
    3. 匹配场景策略
    4. 计算题目分配
    5. 调用搜题 Workflow
    6. 分析缺口
        ├─ 有缺口 → 调用 AI 生成
        └─ 无缺口 ↓
    7. 组装试卷
    8. END
    """

    # 创建流程图
    workflow = StateGraph(ExamWorkflowState)

    # ========== 添加节点 ==========
    workflow.add_node("extract_parameters", nodes.extract_parameters)
    workflow.add_node("check_completeness", nodes.check_completeness)
    workflow.add_node("generate_followup", nodes.generate_followup)
    workflow.add_node("match_scene_strategy", nodes.match_scene_strategy)
    workflow.add_node("calculate_allocation", nodes.calculate_allocation)
    workflow.add_node("search_questions", nodes.search_questions)
    workflow.add_node("analyze_gap", nodes.analyze_gap)
    workflow.add_node("generate_questions", nodes.generate_questions)
    workflow.add_node("assemble_exam", nodes.assemble_exam)

    # ========== 设置入口 ==========
    workflow.set_entry_point("extract_parameters")

    # ========== 定义边（流程控制）==========

    # 1. 提取参数 → 检查完整性
    workflow.add_edge("extract_parameters", "check_completeness")

    # 2. 检查完整性 → 条件分支
    workflow.add_conditional_edges(
        "check_completeness",
        should_continue_or_followup,  # 决策函数
        {
            "followup": "generate_followup",  # 参数不完整 → 生成追问
            "continue": "match_scene_strategy"  # 参数完整 → 继续流程
        }
    )

    # 3. 生成追问 → END（等待用户回复）
    workflow.add_edge("generate_followup", END)

    # 4. 匹配场景策略 → 计算题目分配
    workflow.add_edge("match_scene_strategy", "calculate_allocation")

    # 5. 计算分配 → 搜题
    workflow.add_edge("calculate_allocation", "search_questions")

    # 6. 搜题 → 分析缺口
    workflow.add_edge("search_questions", "analyze_gap")

    # 7. 分析缺口 → 条件分支
    workflow.add_conditional_edges(
        "analyze_gap",
        need_ai_generation,  # 决策函数
        {
            "generate": "generate_questions",  # 有缺口 → AI 生成
            "assemble": "assemble_exam"  # 无缺口 → 直接组卷
        }
    )

    # 8. AI 生成 → 组卷
    workflow.add_edge("generate_questions", "assemble_exam")

    # 9. 组卷 → END
    workflow.add_edge("assemble_exam", END)

    return workflow.compile()


# ========== 决策函数 ==========

def should_continue_or_followup(state: ExamWorkflowState) -> str:
    """
    决策：是否需要继续追问

    Args:
        state: 当前状态

    Returns:
        "followup": 参数不完整，需要追问
        "continue": 参数完整，继续流程
    """
    if state["is_params_complete"]:
        return "continue"
    else:
        return "followup"


def need_ai_generation(state: ExamWorkflowState) -> str:
    """
    决策：是否需要 AI 生成补充题目

    Args:
        state: 当前状态

    Returns:
        "generate": 有缺口，需要 AI 生成
        "assemble": 无缺口，直接组卷
    """
    gap = state.get("gap", 0)

    if gap > 0:
        return "generate"
    else:
        return "assemble"


# ========== 导出 ==========

def get_workflow():
    """获取编译后的 Workflow（供外部调用）"""
    return create_exam_workflow()


# ========== 流程图可视化（开发用）==========

def visualize_workflow():
    """
    生成流程图的 Mermaid 代码

    用于文档或调试界面展示
    """
    mermaid = """
graph TD
    Start([开始]) --> ExtractParams[提取参数]
    ExtractParams --> CheckComplete{参数完整?}
    CheckComplete -->|否| GenFollowup[生成追问]
    GenFollowup --> End([结束 - 等待用户])
    CheckComplete -->|是| MatchScene[匹配场景策略]
    MatchScene --> CalcAlloc[计算题目分配]
    CalcAlloc --> Search[搜题]
    Search --> AnalyzeGap[分析缺口]
    AnalyzeGap --> HasGap{有缺口?}
    HasGap -->|是| Generate[AI生成]
    HasGap -->|否| Assemble[组装试卷]
    Generate --> Assemble
    Assemble --> End2([结束 - 返回试卷])
    """
    return mermaid


if __name__ == "__main__":
    # 测试：打印流程图
    print("ExamWorkflow 流程图 (Mermaid):")
    print(visualize_workflow())

    # 测试：编译 Workflow
    workflow = get_workflow()
    print("\nWorkflow 编译成功!")
    print(f"节点数: {len(workflow.nodes)}")
