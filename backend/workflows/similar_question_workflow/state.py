"""
相似题生成工作流状态定义
"""
from typing import TypedDict


class SimilarQuestionWorkflowState(TypedDict):
    """工作流状态"""

    image_path: str                      # 输入：图片本地路径
    question_count: int                  # 输入：生成相似题数量（默认3道）
    ocr_result: dict                     # 阿里云 OCR 识别结果（文字+公式）
    similar_questions: list[dict]        # 生成的相似题列表
    validation_results: list[dict]       # 有效性校验结果
    retry_count: int                     # 重试次数（最多2次）
    error: str | None                    # 错误信息
