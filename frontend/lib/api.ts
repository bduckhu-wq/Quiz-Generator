import axios from 'axios';
import { Exam } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = {
  // 创建会话
  createSession: async () => {
    const response = await axios.post(`${API_BASE}/api/session/create`);
    return response.data;
  },

  // 获取会话
  getSession: async (sessionId: string) => {
    const response = await axios.get(`${API_BASE}/api/session/${sessionId}`);
    return response.data;
  },

  // 删除会话
  deleteSession: async (sessionId: string) => {
    const response = await axios.delete(`${API_BASE}/api/session/${sessionId}`);
    return response.data;
  },

  // 生成试卷（非流式）
  generateExam: async (userInput: string, sessionId?: string) => {
    const response = await axios.post(`${API_BASE}/api/exam/generate`, {
      user_input: userInput,
      session_id: sessionId
    });
    return response.data;
  },

  // 健康检查
  healthCheck: async () => {
    const response = await axios.get(`${API_BASE}/health`);
    return response.data;
  }
};
