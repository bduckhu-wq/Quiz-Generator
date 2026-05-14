"""
会话管理 API
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional

from services.session_service import SessionService

router = APIRouter()

# 初始化服务
session_service = SessionService()


class CreateSessionResponse(BaseModel):
    """创建会话响应"""
    session_id: str


class SessionInfo(BaseModel):
    """会话信息"""
    session_id: str
    created_at: float
    updated_at: float
    message_count: int


@router.post("/create", response_model=CreateSessionResponse)
async def create_session(user_id: Optional[str] = None):
    """创建新会话"""
    session_id = session_service.create_session(user_id=user_id)
    return CreateSessionResponse(session_id=session_id)


@router.get("/{session_id}")
async def get_session(session_id: str):
    """获取会话详情"""
    session_data = session_service.get_session(session_id)

    if not session_data:
        raise HTTPException(status_code=404, detail="会话不存在")

    return session_data


@router.get("/{session_id}/messages")
async def get_messages(session_id: str):
    """获取会话对话历史"""
    messages = session_service.get_messages(session_id)

    if messages is None:
        raise HTTPException(status_code=404, detail="会话不存在")

    return {"messages": messages}


@router.delete("/{session_id}")
async def delete_session(session_id: str):
    """删除会话"""
    success = session_service.delete_session(session_id)

    if not success:
        raise HTTPException(status_code=404, detail="会话不存在")

    return {"success": True}


@router.get("/", response_model=List[SessionInfo])
async def list_sessions(limit: int = 100):
    """列出所有会话"""
    sessions = session_service.list_sessions(limit=limit)
    return sessions


@router.post("/cleanup")
async def cleanup_sessions(max_age_hours: int = 24):
    """清理过期会话"""
    session_service.cleanup_expired_sessions(max_age_hours=max_age_hours)
    return {"success": True}
