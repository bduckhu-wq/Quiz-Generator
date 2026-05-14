// 题目类型
export interface Question {
  id: string;
  index: number;
  question_type: string;
  difficulty: string;
  content: string;
  options?: string | string[];
  answer: string;
  analysis?: string;
  score: number;
  knowledge_points: string[];
  subject?: string;
  grade?: string;
  source?: string;  // 来源标记：'题库' 或 'AI生成'
}

// 试卷类型
export interface Exam {
  exam_id: string;
  subject: string;
  grade: string;
  knowledge_points: string[];
  scene: string;
  questions: Question[];
  question_count: number;
  total_score: number;
  source_stats: {
    database: number;
    ai_generated: number;
  };
  created_at: number;
}

// 提取的参数
export interface ExtractedParams {
  subject?: string;
  grade?: string;
  knowledge_points?: string[];
  scene?: string;
  question_count?: number;
  chapter?: string;
}

// SSE事件类型
export type SSEEvent =
  | { type: 'session'; session_id: string }
  | { type: 'progress'; step: string; message: string }
  | { type: 'followup'; message: string }
  | { type: 'exam'; exam: Exam }
  | { type: 'done' };

// 消息类型
export type MessageRole = 'user' | 'assistant' | 'system';

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: number;
  type?: 'text' | 'exam' | 'followup' | 'thinking';
  exam?: Exam;
  metadata?: {
    step?: string;
    progress?: string;
  };
}

// 会话类型
export interface ChatSession {
  sessionId: string;
  messages: Message[];
  currentExam?: Exam;
  createdAt: number;
  updatedAt: number;
}
