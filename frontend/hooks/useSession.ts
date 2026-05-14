'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';

export function useSession() {
  const [sessionId, setSessionId] = useState<string>('');
  const [isRestoring, setIsRestoring] = useState(false);

  // 初始化会话
  const initSession = async () => {
    // 尝试从localStorage恢复
    const savedSessionId = localStorage.getItem('current_session_id');

    if (savedSessionId) {
      try {
        setIsRestoring(true);
        const session = await api.getSession(savedSessionId);
        if (session) {
          setSessionId(savedSessionId);
          return savedSessionId;
        }
      } catch (error) {
        console.log('会话已过期，创建新会话');
      } finally {
        setIsRestoring(false);
      }
    }

    // 创建新会话
    const response = await api.createSession();
    const newSessionId = response.session_id;
    setSessionId(newSessionId);
    localStorage.setItem('current_session_id', newSessionId);
    return newSessionId;
  };

  // 删除会话
  const deleteSession = async () => {
    if (!sessionId) return;

    await api.deleteSession(sessionId);
    localStorage.removeItem('current_session_id');
    setSessionId('');
  };

  return {
    sessionId,
    isRestoring,
    initSession,
    deleteSession
  };
}
