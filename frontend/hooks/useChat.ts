'use client';

import { useState, useCallback } from 'react';
import { Message, Exam } from '@/lib/types';
import { streamGenerate } from '@/lib/sseClient';
import { v4 as uuidv4 } from 'uuid';

export function useChat(initialSessionId?: string) {
  const [sessionId, setSessionId] = useState<string>(initialSessionId || '');
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentExam, setCurrentExam] = useState<Exam | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // 添加消息
  const addMessage = useCallback((message: Omit<Message, 'id' | 'timestamp'>) => {
    const newMessage: Message = {
      ...message,
      id: uuidv4(),
      timestamp: Date.now()
    };
    setMessages(prev => [...prev, newMessage]);
    return newMessage;
  }, []);

  // 添加系统消息
  const addSystemMessage = useCallback((content: string) => {
    addMessage({
      role: 'system',
      content,
      type: 'thinking'
    });
  }, [addMessage]);

  // 发送消息
  const sendMessage = useCallback(async (content: string) => {
    // 添加用户消息
    addMessage({
      role: 'user',
      content,
      type: 'text'
    });

    setIsLoading(true);

    try {
      await streamGenerate(content, sessionId, (event) => {
        switch (event.type) {
          case 'session':
            setSessionId(event.session_id);
            // 保存到localStorage
            localStorage.setItem('current_session_id', event.session_id);
            break;

          case 'progress':
            addSystemMessage(event.message);
            break;

          case 'followup':
            addMessage({
              role: 'assistant',
              content: event.message,
              type: 'followup'
            });
            break;

          case 'exam':
            setCurrentExam(event.exam);
            addMessage({
              role: 'assistant',
              content: '✅ 试卷已生成完成！请在右侧查看详情。',
              type: 'exam',
              exam: event.exam
            });
            break;

          case 'done':
            break;
        }
      });
    } catch (error) {
      console.error('发送消息失败:', error);
      addMessage({
        role: 'assistant',
        content: '抱歉，生成失败了，请重试。' + (error instanceof Error ? error.message : ''),
        type: 'text'
      });
    } finally {
      setIsLoading(false);
    }
  }, [sessionId, addMessage, addSystemMessage]);

  // 清空对话
  const clearChat = useCallback(() => {
    setMessages([]);
    setCurrentExam(null);
  }, []);

  return {
    sessionId,
    messages,
    currentExam,
    isLoading,
    sendMessage,
    clearChat
  };
}
