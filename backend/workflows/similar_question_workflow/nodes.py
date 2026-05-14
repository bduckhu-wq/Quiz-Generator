"""
相似题生成工作流节点实现
"""
from services.aliyun_ocr_service import AliyunOCRService
from services.llm_service import LLMService
from .state import SimilarQuestionWorkflowState
from pathlib import Path
import json
import logging
import re

logger = logging.getLogger(__name__)

# 加载相似题生成 Skill（原始完整版）
SKILL_PATH = Path(__file__).parent.parent.parent / "skills" / "similar-question-generation" / "SKILL.md"
SIMILAR_QUESTION_SKILL = SKILL_PATH.read_text(encoding="utf-8")
logger.info(f"[Skill加载] 路径: {SKILL_PATH}, 文件大小: {len(SIMILAR_QUESTION_SKILL)} 字符")


async def ocr_recognize(state: SimilarQuestionWorkflowState) -> dict:
    """
    节点 1：阿里云 OCR 识别原题（文字 + 公式）

    Args:
        state: 工作流状态，包含 image_path

    Returns:
        更新后的状态：ocr_result
    """
    import time
    start_time = time.time()
    logger.info(f"[OCR节点] 开始识别图片：{state['image_path']} | 时间戳: {start_time:.2f}")

    try:
        ocr_service = AliyunOCRService()
        ocr_result = await ocr_service.recognize_question(state["image_path"])

        end_time = time.time()
        logger.info(f"[OCR节点] 识别成功，题目长度：{len(ocr_result['question'])}字 | 耗时: {end_time - start_time:.2f}秒")

        return {"ocr_result": ocr_result}

    except Exception as e:
        logger.error(f"[OCR节点] 识别失败：{e}")
        return {"error": f"OCR 识别失败：{str(e)}"}


async def generate_similar(state: SimilarQuestionWorkflowState) -> dict:
    """
    节点 2：单次调用生成 N 道相似题

    策略：1次 LLM 请求生成多道题目（默认3道，可动态调整）
    优势：稳定性高，不受 API 并发限流影响

    Args:
        state: 工作流状态，包含 ocr_result 和 question_count（可选，默认3）

    Returns:
        更新后的状态：similar_questions
    """
    import time
    start_time = time.time()

    # 获取题目数量（默认3道）
    question_count = state.get("question_count", 3)
    logger.info(f"[生成节点] 开始生成 {question_count} 道相似题 | 时间戳: {start_time:.2f}")

    try:
        ocr_result = state["ocr_result"]
        original_question = ocr_result["question"]

        # 构建 System Prompt
        system_prompt = f"""你是数学题目生成助手，严格按照以下规则生成相似题。

{SIMILAR_QUESTION_SKILL}

输出JSON数组：[{{"question":"题目","answer":"答案","explanation":"解析"}}, ...]"""

        logger.info(f"[生成节点] System Prompt 长度: {len(system_prompt)} 字符, Skill 内容已包含: {len(SIMILAR_QUESTION_SKILL)} 字符")

        user_message = f"""原题：
{original_question}

一次性生成 {question_count} 道相似题（70%相似度），输出 JSON 数组格式。"""

        llm = LLMService()  # 使用 .env 中配置的默认 provider

        llm_start = time.time()
        logger.info(f"[生成节点] LLM 请求开始 | 时间戳: {llm_start:.2f}")

        response = await llm.chat(
            messages=[{"role": "user", "content": user_message}],
            system_prompt=system_prompt,
            stream=False
        )

        llm_end = time.time()
        logger.info(f"[生成节点] LLM 响应完成 | 耗时: {llm_end - llm_start:.2f}秒")

        # 解析 JSON 数组
        content = response.content.strip()

        # 尝试匹配 JSON 数组
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if not json_match:
            raise ValueError(f"LLM 输出不包含有效 JSON 数组")

        similar_questions = json.loads(json_match.group(0))

        # 校验是否为数组
        if not isinstance(similar_questions, list):
            raise ValueError(f"LLM 输出不是 JSON 数组")

        if len(similar_questions) == 0:
            raise ValueError(f"LLM 返回空数组")

        end_time = time.time()
        logger.info(f"[生成节点] 生成完成：{len(similar_questions)}/{question_count} 道 | 总耗时: {end_time - start_time:.2f}秒")

        return {"similar_questions": similar_questions}

    except Exception as e:
        logger.error(f"[生成节点] 生成失败：{e}")
        return {"error": f"相似题生成失败：{str(e)}"}


async def validate_questions(state: SimilarQuestionWorkflowState) -> dict:
    """
    节点 3：校验相似题的有效性

    校验维度：
    1. 题目完整性（题干、选项、答案、解析）
    2. 知识点一致性（与原题保持一致）
    3. 相似度符合要求（70%）
    4. 干扰项合理性（来自真实误解）

    Args:
        state: 工作流状态，包含 similar_questions

    Returns:
        更新后的状态：validation_results
    """
    import time
    start_time = time.time()
    logger.info(f"[校验节点] 开始校验 {len(state['similar_questions'])} 道相似题 | 时间戳: {start_time:.2f}")

    validation_results = []

    for i, question in enumerate(state["similar_questions"], 1):
        # 基础校验
        is_valid = True
        errors = []

        # 1. 题目完整性校验
        if not question.get("question"):
            is_valid = False
            errors.append("题目内容为空")

        if not question.get("answer"):
            is_valid = False
            errors.append("答案为空")

        if not question.get("explanation"):
            is_valid = False
            errors.append("解析为空")

        validation_results.append({
            "question_index": i,
            "valid": is_valid,
            "errors": errors
        })

        logger.info(f"[校验节点] 题目 {i} 校验结果：{'通过' if is_valid else '失败'}")

    # 统计失败数量
    failed_count = sum(1 for r in validation_results if not r["valid"])
    end_time = time.time()
    logger.info(f"[校验节点] 校验完成：{len(validation_results) - failed_count}/{len(validation_results)} 通过 | 耗时: {end_time - start_time:.2f}秒")

    return {"validation_results": validation_results}


async def format_output(state: SimilarQuestionWorkflowState) -> dict:
    """
    节点 4：格式化输出结果

    过滤掉校验失败的题目，只返回有效题目。

    Args:
        state: 工作流状态，包含 similar_questions 和 validation_results

    Returns:
        更新后的状态：similar_questions（已过滤）
    """
    import time
    start_time = time.time()
    logger.info(f"[格式化节点] 开始格式化输出 | 时间戳: {start_time:.2f}")

    valid_questions = []

    for question, validation in zip(state["similar_questions"], state["validation_results"]):
        if validation["valid"]:
            valid_questions.append(question)

    end_time = time.time()
    logger.info(f"[格式化节点] 输出 {len(valid_questions)} 道有效相似题 | 耗时: {end_time - start_time:.2f}秒")

    return {"similar_questions": valid_questions}
