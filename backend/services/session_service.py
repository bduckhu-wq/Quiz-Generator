"""
Session 管理服务
"""

import json
import os
import time
import uuid
from pathlib import Path
from typing import Dict, Optional, List


class SessionService:
    """
    会话管理服务

    功能：
    1. 创建会话
    2. 保存对话历史
    3. 保存 Workflow 状态
    4. 加载会话
    5. 清理过期会话
    """

    def __init__(self, sessions_dir: str = "sessions"):
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(exist_ok=True)

    def create_session(self, user_id: Optional[str] = None) -> str:
        """
        创建新会话

        Args:
            user_id: 用户 ID（可选）

        Returns:
            session_id
        """
        session_id = str(uuid.uuid4())

        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": time.time(),
            "updated_at": time.time(),
            "messages": [],
            "workflow_state": None,
            "metadata": {}
        }

        self._save_session(session_id, session_data)

        return session_id

    def get_session(self, session_id: str) -> Optional[Dict]:
        """
        获取会话数据

        Args:
            session_id: 会话 ID

        Returns:
            会话数据字典，如果不存在返回 None
        """
        session_file = self.sessions_dir / f"{session_id}.json"

        if not session_file.exists():
            return None

        try:
            with open(session_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  加载会话失败（{session_id}）: {e}")
            return None

    def update_session(
        self,
        session_id: str,
        messages: Optional[List[Dict]] = None,
        workflow_state: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ):
        """
        更新会话数据

        Args:
            session_id: 会话 ID
            messages: 对话历史（可选）
            workflow_state: Workflow 状态（可选）
            metadata: 元数据（可选）
        """
        session_data = self.get_session(session_id)

        if not session_data:
            raise ValueError(f"会话不存在: {session_id}")

        # 更新字段
        if messages is not None:
            session_data["messages"] = messages

        if workflow_state is not None:
            session_data["workflow_state"] = workflow_state

        if metadata is not None:
            session_data["metadata"].update(metadata)

        session_data["updated_at"] = time.time()

        self._save_session(session_id, session_data)

    def add_message(self, session_id: str, role: str, content: str):
        """
        添加对话消息

        Args:
            session_id: 会话 ID
            role: 角色（user/assistant）
            content: 消息内容
        """
        session_data = self.get_session(session_id)

        if not session_data:
            raise ValueError(f"会话不存在: {session_id}")

        session_data["messages"].append({
            "role": role,
            "content": content,
            "timestamp": time.time()
        })

        session_data["updated_at"] = time.time()

        self._save_session(session_id, session_data)

    def get_messages(self, session_id: str) -> List[Dict]:
        """
        获取对话历史

        Args:
            session_id: 会话 ID

        Returns:
            消息列表
        """
        session_data = self.get_session(session_id)

        if not session_data:
            return []

        return session_data.get("messages", [])

    def delete_session(self, session_id: str) -> bool:
        """
        删除会话

        Args:
            session_id: 会话 ID

        Returns:
            是否删除成功
        """
        session_file = self.sessions_dir / f"{session_id}.json"

        if not session_file.exists():
            return False

        try:
            session_file.unlink()
            return True
        except Exception as e:
            print(f"⚠️  删除会话失败（{session_id}）: {e}")
            return False

    def cleanup_expired_sessions(self, max_age_hours: int = 24):
        """
        清理过期会话

        Args:
            max_age_hours: 最大保存时长（小时）
        """
        now = time.time()
        max_age_seconds = max_age_hours * 3600

        deleted_count = 0

        for session_file in self.sessions_dir.glob("*.json"):
            try:
                with open(session_file, "r", encoding="utf-8") as f:
                    session_data = json.load(f)

                updated_at = session_data.get("updated_at", 0)

                if now - updated_at > max_age_seconds:
                    session_file.unlink()
                    deleted_count += 1

            except Exception as e:
                print(f"⚠️  清理会话失败（{session_file.name}）: {e}")

        print(f"✓ 清理了 {deleted_count} 个过期会话")

    def _save_session(self, session_id: str, session_data: Dict):
        """内部方法：保存会话到文件"""
        session_file = self.sessions_dir / f"{session_id}.json"

        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)

    def list_sessions(self, limit: int = 100) -> List[Dict]:
        """
        列出所有会话（按更新时间倒序）

        Args:
            limit: 返回数量

        Returns:
            会话列表
        """
        sessions = []

        for session_file in self.sessions_dir.glob("*.json"):
            try:
                with open(session_file, "r", encoding="utf-8") as f:
                    session_data = json.load(f)
                    sessions.append({
                        "session_id": session_data["session_id"],
                        "created_at": session_data["created_at"],
                        "updated_at": session_data["updated_at"],
                        "message_count": len(session_data.get("messages", []))
                    })
            except Exception:
                pass

        # 按更新时间倒序
        sessions.sort(key=lambda x: x["updated_at"], reverse=True)

        return sessions[:limit]
