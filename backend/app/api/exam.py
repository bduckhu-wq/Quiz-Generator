"""
出题相关 API
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import json
import asyncio

from workflows.exam_workflow.graph import get_workflow
from workflows.exam_workflow.state import create_initial_state
from skills.loader import SkillLoader
from services.llm_service import LLMService
from services.session_service import SessionService
from utils.retry import handle_workflow_error

router = APIRouter()

# 初始化服务
skill_loader = SkillLoader()
session_service = SessionService()


class GenerateExamRequest(BaseModel):
    """生成试卷请求"""
    user_input: str
    session_id: Optional[str] = None


class GenerateExamResponse(BaseModel):
    """生成试卷响应"""
    session_id: str
    needs_followup: bool
    followup_message: Optional[str] = None
    exam: Optional[Dict] = None
    error: Optional[str] = None


@router.post("/generate", response_model=GenerateExamResponse)
async def generate_exam(request: GenerateExamRequest):
    """
    生成试卷（非流式）

    流程：
    1. 创建/获取 Session
    2. 加载 Skill
    3. 执行 Workflow
    4. 返回结果
    """
    try:
        # 1. 创建或获取 Session
        if request.session_id:
            session_id = request.session_id
            session_data = session_service.get_session(session_id)
            if not session_data:
                raise HTTPException(status_code=404, detail="会话不存在")
            messages = session_data["messages"]
        else:
            session_id = session_service.create_session()
            messages = []

        # 2. 保存用户消息
        session_service.add_message(session_id, "user", request.user_input)

        # 3. 加载 Skill
        llm = LLMService(provider="deepseek")
        skill_context = await skill_loader.route_to_skill(request.user_input, llm)

        # 4. 执行 Workflow
        workflow = get_workflow()
        initial_state = create_initial_state(
            user_input=request.user_input,
            session_id=session_id,
            skill_context=skill_context,
            messages=messages
        )

        result = await workflow.ainvoke(initial_state)

        # 5. 保存 Workflow 状态
        session_service.update_session(
            session_id=session_id,
            workflow_state=result
        )

        # 6. 构建响应
        if result.get("needs_followup"):
            # 需要追问
            followup_message = result["followup_message"]
            session_service.add_message(session_id, "assistant", followup_message)

            return GenerateExamResponse(
                session_id=session_id,
                needs_followup=True,
                followup_message=followup_message,
                exam=None
            )
        else:
            # 生成成功
            final_exam = result.get("final_exam")

            return GenerateExamResponse(
                session_id=session_id,
                needs_followup=False,
                followup_message=None,
                exam=final_exam
            )

    except Exception as e:
        error_info = handle_workflow_error(e, context="generate_exam")
        raise HTTPException(status_code=500, detail=error_info)


@router.post("/generate/stream")
async def generate_exam_stream(request: GenerateExamRequest):
    """
    生成试卷（SSE 流式输出）

    流程：
    1. 创建/获取 Session
    2. 加载 Skill
    3. 流式执行 Workflow
    4. 实时推送进度
    """

    async def event_generator():
        try:
            # 1. 创建或获取 Session
            if request.session_id:
                session_id = request.session_id
                session_data = session_service.get_session(session_id)
                if not session_data:
                    yield f"data: {json.dumps({'error': '会话不存在'})}\n\n"
                    return
                messages = session_data["messages"]
            else:
                session_id = session_service.create_session()
                messages = []

            # 发送 session_id
            yield f"data: {json.dumps({'type': 'session', 'session_id': session_id})}\n\n"

            # 2. 保存用户消息
            session_service.add_message(session_id, "user", request.user_input)

            # 3. 加载 Skill
            yield f"data: {json.dumps({'type': 'progress', 'step': 'load_skill', 'message': '🤔 AI正在理解你的需求...'}, ensure_ascii=False)}\n\n"

            llm = LLMService(provider="deepseek")
            skill_context = await skill_loader.route_to_skill(request.user_input, llm)

            yield f"data: {json.dumps({'type': 'progress', 'step': 'skill_loaded', 'message': '✅ 需求理解完成'}, ensure_ascii=False)}\n\n"

            # 4. 执行 Workflow（流式）
            workflow = get_workflow()
            initial_state = create_initial_state(
                user_input=request.user_input,
                session_id=session_id,
                skill_context=skill_context,
                messages=messages
            )

            # 步骤中文映射
            step_messages = {
                'extract_parameters': '📝 正在提取出题参数...',
                'check_completeness': '🔍 正在检查参数完整性...',
                'match_scene_strategy': '🎯 正在匹配出题场景...',
                'calculate_allocation': '📊 正在计算题目分配方案...',
                'search_database': '🔎 正在搜索题库...',
                'analyze_gap': '🧮 正在分析题目缺口...',
                'generate_questions': '🤖 AI正在生成题目...',
                'assemble_exam': '📦 正在组装试卷...'
            }

            # 逐步推送进度
            async for chunk in workflow.astream(initial_state):
                # chunk 格式: {node_name: node_output}
                for node_name, node_output in chunk.items():
                    current_step = node_output.get("current_step", node_name)
                    message = step_messages.get(current_step, f'正在执行: {current_step}')

                    yield f"data: {json.dumps({
                        'type': 'progress',
                        'step': current_step,
                        'message': message
                    }, ensure_ascii=False)}\n\n"

                    # 如果是追问，立即返回
                    if node_output.get("needs_followup"):
                        followup_message = node_output["followup_message"]
                        session_service.add_message(session_id, "assistant", followup_message)

                        yield f"data: {json.dumps({
                            'type': 'followup',
                            'message': followup_message
                        }, ensure_ascii=False)}\n\n"

                        yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"
                        return

                    # 如果生成完成，返回试卷
                    if node_output.get("final_exam"):
                        final_exam = node_output["final_exam"]

                        # 保存状态
                        session_service.update_session(
                            session_id=session_id,
                            workflow_state=node_output
                        )

                        yield f"data: {json.dumps({
                            'type': 'exam',
                            'exam': final_exam
                        }, ensure_ascii=False)}\n\n"

                        yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"
                        return

        except Exception as e:
            error_info = handle_workflow_error(e, context="generate_exam_stream")
            yield f"data: {json.dumps({'type': 'error', 'error': error_info})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/history/{session_id}")
async def get_exam_history(session_id: str):
    """获取会话的试卷历史"""
    session_data = session_service.get_session(session_id)

    if not session_data:
        raise HTTPException(status_code=404, detail="会话不存在")

    workflow_state = session_data.get("workflow_state")

    if not workflow_state or not workflow_state.get("final_exam"):
        return {"exam": None}

    return {"exam": workflow_state["final_exam"]}
