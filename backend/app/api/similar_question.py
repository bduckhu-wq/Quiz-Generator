"""
相似题生成 API 路由
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import time
import uuid
import logging
from typing import Optional

from workflows.similar_question_workflow import create_similar_question_workflow
from workflows.similar_question_workflow.state import SimilarQuestionWorkflowState

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/similar-question", tags=["相似题生成"])

# 创建临时目录
TEMP_DIR = Path(__file__).parent.parent.parent / "temp"
TEMP_DIR.mkdir(exist_ok=True)


@router.post("/generate")
async def generate_similar_questions(
    image: UploadFile = File(..., description="原题图片"),
    count: Optional[int] = 3
):
    """
    上传原题图片，生成相似题

    流程：
    1. 保存图片到临时目录
    2. 阿里云 OCR 识别原题
    3. 单次 LLM 调用生成 N 道相似题
    4. 校验题目有效性
    5. 返回相似题列表

    Args:
        image: 原题图片文件 (JPG/PNG)
        count: 生成相似题数量，默认3道，范围1-10

    Returns:
        {
            "ocr_result": {
                "question": "原题内容",
                "confidence": 0.98
            },
            "similar_questions": [
                {
                    "question": "题目内容（含选项）",
                    "answer": "答案",
                    "explanation": "解析"
                },
                ...
            ],
            "validation_results": [
                {
                    "question_index": 1,
                    "valid": true,
                    "errors": []
                },
                ...
            ],
            "generation_time": 54.3,
            "question_count": 3
        }
    """
    start_time = time.time()

    # 参数校验
    if count < 1 or count > 10:
        raise HTTPException(
            status_code=400,
            detail="生成数量必须在 1-10 之间"
        )

    # 验证文件类型
    if not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="只支持图片文件 (JPG/PNG/HEIC)"
        )

    try:
        # 1. 保存图片到临时目录
        file_id = str(uuid.uuid4())
        file_ext = Path(image.filename).suffix
        image_path = TEMP_DIR / f"{file_id}{file_ext}"

        with open(image_path, "wb") as f:
            content = await image.read()
            f.write(content)

        save_time = time.time()
        logger.info(f"[API] 图片已保存：{image_path}，大小：{len(content)} 字节 | 保存耗时: {save_time - start_time:.2f}秒")

        # 2. 创建并执行工作流
        workflow_create_start = time.time()
        workflow = create_similar_question_workflow()
        workflow_create_end = time.time()
        logger.info(f"[API] 工作流创建完成 | 耗时: {workflow_create_end - workflow_create_start:.2f}秒")

        initial_state: SimilarQuestionWorkflowState = {
            "image_path": str(image_path),
            "question_count": count,
            "ocr_result": {},
            "similar_questions": [],
            "validation_results": [],
            "retry_count": 0,
            "error": None
        }

        workflow_start = time.time()
        logger.info(f"[API] 开始执行工作流，生成 {count} 道相似题 | 时间戳: {workflow_start:.2f}")
        final_state = await workflow.ainvoke(initial_state)
        workflow_end = time.time()
        logger.info(f"[API] 工作流执行完成 | 耗时: {workflow_end - workflow_start:.2f}秒")

        # 3. 检查错误
        if final_state.get("error"):
            raise HTTPException(
                status_code=500,
                detail=f"生成失败：{final_state['error']}"
            )

        # 4. 返回结果
        generation_time = time.time() - start_time

        logger.info(f"[API] 生成完成，耗时 {generation_time:.2f} 秒，成功生成 {len(final_state['similar_questions'])} 道题")

        return {
            "ocr_result": final_state["ocr_result"],
            "similar_questions": final_state["similar_questions"],
            "validation_results": final_state["validation_results"],
            "generation_time": round(generation_time, 2),
            "question_count": len(final_state["similar_questions"])
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[API] 生成相似题异常：{e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误：{str(e)}"
        )
    finally:
        # 清理临时文件
        if image_path.exists():
            image_path.unlink()
            logger.info(f"[API] 临时文件已删除：{image_path}")


from pydantic import BaseModel

class RegenerateRequest(BaseModel):
    """重新生成请求"""
    original_question: str
    question_index: int = 1

@router.post("/regenerate")
async def regenerate_single_question(request: RegenerateRequest):
    """
    重新生成单道题目

    用于：
    - 校验失败时重新生成
    - 用户不满意时重新生成

    Args:
        request: 包含 original_question（原题内容）和 question_index（题目序号）

    Returns:
        {
            "question": "新生成的题目",
            "answer": "答案",
            "explanation": "解析",
            "valid": true
        }
    """
    try:
        from services.llm_service import LLMService
        from pathlib import Path
        import json
        import re

        # 加载 Skill
        skill_path = Path(__file__).parent.parent.parent / "skills" / "similar-question-generation" / "SKILL.md"
        skill_content = skill_path.read_text(encoding="utf-8")

        # 构建 Prompt
        system_prompt = f"""你是数学题目生成助手，严格按照以下规则生成相似题。

{skill_content}

输出JSON：{{"question":"题目","answer":"答案","explanation":"解析"}}"""

        user_message = f"""原题：
{request.original_question}

生成1道相似题（70%相似度）。"""

        # 调用 LLM（使用 .env 中配置的默认 provider）
        llm = LLMService()
        response = await llm.chat(
            messages=[{"role": "user", "content": user_message}],
            system_prompt=system_prompt,
            stream=False
        )

        # 解析 JSON
        content = response.content.strip()
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if not json_match:
            raise ValueError("LLM 输出不包含有效 JSON")

        question = json.loads(json_match.group(0))

        # 基础校验
        is_valid = bool(question.get("question") and question.get("answer") and question.get("explanation"))

        logger.info(f"[API] 重新生成题目 {request.question_index} 成功，校验：{'通过' if is_valid else '失败'}")

        return {
            **question,
            "valid": is_valid
        }

    except Exception as e:
        logger.error(f"[API] 重新生成题目失败：{e}")
        raise HTTPException(
            status_code=500,
            detail=f"重新生成失败：{str(e)}"
        )
