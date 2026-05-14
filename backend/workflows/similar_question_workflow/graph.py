"""
相似题生成工作流图定义
"""
from langgraph.graph import StateGraph, END
from .state import SimilarQuestionWorkflowState
from . import nodes
import logging

logger = logging.getLogger(__name__)


def create_similar_question_workflow():
    """
    创建相似题生成工作流

    流程：
    1. ocr_recognize：阿里云 OCR 识别原题
    2. generate_similar：调用 Skill 生成 3 道相似题
    3. validate_questions：并行校验相似题有效性
    4. format_output：格式化输出（过滤无效题目）

    重试逻辑：
    - 校验失败时，最多重试 2 次
    - 重试次数达到上限后，直接输出有效题目

    Returns:
        编译后的工作流
    """
    logger.info("创建相似题生成工作流")

    workflow = StateGraph(SimilarQuestionWorkflowState)

    # 添加节点（4 个）
    workflow.add_node("ocr_recognize", nodes.ocr_recognize)
    workflow.add_node("generate_similar", nodes.generate_similar)
    workflow.add_node("validate_questions", nodes.validate_questions)
    workflow.add_node("format_output", nodes.format_output)

    # 设置入口点
    workflow.set_entry_point("ocr_recognize")

    # 设置边（线性流程 + 条件分支）
    workflow.add_edge("ocr_recognize", "generate_similar")
    workflow.add_edge("generate_similar", "validate_questions")

    # 校验失败重试逻辑
    def should_retry(state: SimilarQuestionWorkflowState) -> str:
        """
        判断是否需要重试生成

        重试条件：
        1. 有校验失败的题目
        2. 重试次数 < 2

        Returns:
            "generate_similar"（重试）或 "format_output"（结束）
        """
        failed_count = sum(1 for r in state["validation_results"] if not r["valid"])
        retry_count = state.get("retry_count", 0)

        if failed_count > 0 and retry_count < 2:
            logger.info(f"[工作流] 校验失败 {failed_count} 道，重试第 {retry_count + 1} 次")
            return "generate_similar"
        else:
            logger.info(f"[工作流] 校验完成，进入格式化输出")
            return "format_output"

    workflow.add_conditional_edges(
        "validate_questions",
        should_retry,
        {
            "generate_similar": "generate_similar",
            "format_output": "format_output"
        }
    )

    workflow.add_edge("format_output", END)

    return workflow.compile()
