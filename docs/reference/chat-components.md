# 多轮对话组件完整实现

> **核心功能**: 支持多轮对话、参数追问、历史记录、Session持久化

---

## 🎯 对话功能需求

### 核心场景
1. **初始对话**：用户输入模糊需求 → AI追问补充参数
2. **参数补充**：用户回答追问 → AI继续追问或生成试卷
3. **历史回溯**：查看完整对话历史
4. **会话恢复**：刷新页面后恢复对话状态

### 交互流程
```
用户: "帮我出份数学试卷"
  ↓
AI: "好的！请问是针对哪个年级出题呢？（如：初二、高一、高三）"
  ↓
用户: "三年级"
  ↓
AI: "明白了！请问是关于哪个知识点或章节？"
  ↓
用户: "第三章第二节"
  ↓
AI: [生成试卷并展示在右侧]
```

---

## 📊 数据结构设计

### 1. 消息类型定义

```typescript
// src/lib/types.ts

export type MessageRole = 'user' | 'assistant' | 'system';

export interface Message {
  id: string;                    // 消息唯一ID
  role: MessageRole;             // 角色
  content: string;               // 消息内容
  timestamp: number;             // 时间戳
  type?: 'text' | 'exam' | 'followup' | 'thinking'; // 消息类型
  exam?: Exam;                   // 关联的试卷数据
  metadata?: {
    step?: string;               // 当前执行步骤
    progress?: string;           // 进度信息
  };
}

export interface ChatSession {
  sessionId: string;             // 会话ID
  messages: Message[];           // 消息列表
  currentExam?: Exam;           // 当前生成的试卷
  createdAt: number;
  updatedAt: number;
}
```

---

## 🎨 核心组件实现

### 1. ChatPage - 对话页主组件

```tsx
// src/app/chat/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { MessageList } from '@/components/chat/MessageList';
import { InputBox } from '@/components/chat/InputBox';
import { ExamPreview } from '@/components/exam/ExamPreview';
import { useChat } from '@/hooks/useChat';
import { useSession } from '@/hooks/useSession';

export default function ChatPage() {
  const { 
    messages, 
    currentExam, 
    isLoading, 
    sendMessage 
  } = useChat();
  
  const { sessionId, initSession } = useSession();

  useEffect(() => {
    // 初始化或恢复会话
    initSession();
  }, []);

  return (
    <div className="flex h-screen bg-gray-50">
      {/* 左侧：对话区 */}
      <div className="w-1/2 flex flex-col border-r bg-white">
        {/* 顶部标题栏 */}
        <div className="px-6 py-4 border-b bg-blue-600 text-white">
          <h1 className="text-xl font-bold">AI 出题助手</h1>
          <p className="text-sm text-blue-100 mt-1">
            智能对话生成试卷
          </p>
        </div>

        {/* 消息列表区 */}
        <div className="flex-1 overflow-hidden">
          <MessageList 
            messages={messages} 
            isLoading={isLoading}
          />
        </div>

        {/* 输入框 */}
        <div className="border-t bg-white">
          <InputBox 
            onSend={sendMessage}
            disabled={isLoading}
            placeholder={
              messages.length === 0 
                ? "输入出题需求，如：三年级数学第三章第二节课后练习5题" 
                : "继续对话..."
            }
          />
        </div>
      </div>

      {/* 右侧：试卷预览区 */}
      <div className="w-1/2 overflow-y-auto bg-gray-50">
        {currentExam ? (
          <ExamPreview exam={currentExam} />
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-gray-400">
            <svg className="w-24 h-24 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} 
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p className="text-lg">试卷将在这里展示</p>
            <p className="text-sm mt-2">在左侧输入出题需求开始</p>
          </div>
        )}
      </div>
    </div>
  );
}
```

---

### 2. MessageList - 消息列表组件

```tsx
// src/components/chat/MessageList.tsx
'use client';

import { useEffect, useRef } from 'react';
import { Message } from '@/lib/types';
import { MessageBubble } from './MessageBubble';
import { ThinkingIndicator } from './ThinkingIndicator';

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
}

export function MessageList({ messages, isLoading }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  // 自动滚动到底部
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="h-full overflow-y-auto px-6 py-4">
      {/* 欢迎消息 */}
      {messages.length === 0 && (
        <div className="text-center text-gray-500 mt-12">
          <div className="mb-4">
            <span className="text-4xl">👋</span>
          </div>
          <h2 className="text-xl font-semibold mb-2">欢迎使用 AI 出题助手</h2>
          <p className="text-sm">告诉我您的出题需求，我会帮您生成试卷</p>
          
          {/* 示例提示 */}
          <div className="mt-8 space-y-2">
            <p className="text-xs text-gray-400 mb-3">💡 试试这些示例：</p>
            <div className="flex flex-col gap-2 items-center">
              <button className="px-4 py-2 bg-blue-50 hover:bg-blue-100 rounded-lg text-sm text-blue-700 transition">
                三年级数学第三章第二节课后练习5题
              </button>
              <button className="px-4 py-2 bg-blue-50 hover:bg-blue-100 rounded-lg text-sm text-blue-700 transition">
                初二数学一元二次方程单元测验
              </button>
              <button className="px-4 py-2 bg-blue-50 hover:bg-blue-100 rounded-lg text-sm text-blue-700 transition">
                高一物理力学期中考试试卷
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 消息列表 */}
      <div className="space-y-4">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}

        {/* 加载中的思考动画 */}
        {isLoading && <ThinkingIndicator />}

        {/* 滚动锚点 */}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
```

---

### 3. MessageBubble - 单条消息气泡

```tsx
// src/components/chat/MessageBubble.tsx
import { Message } from '@/lib/types';
import { formatTime } from '@/lib/utils';
import { ExamSummary } from './ExamSummary';

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';

  // 系统消息（进度提示）
  if (isSystem) {
    return (
      <div className="flex justify-center">
        <div className="px-4 py-2 bg-gray-100 text-gray-600 text-xs rounded-full">
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[70%] ${isUser ? 'order-2' : 'order-1'}`}>
        {/* 头像和名称 */}
        <div className={`flex items-center gap-2 mb-1 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
            isUser ? 'bg-blue-600 text-white' : 'bg-green-600 text-white'
          }`}>
            {isUser ? '我' : 'AI'}
          </div>
          <span className="text-xs text-gray-500">
            {formatTime(message.timestamp)}
          </span>
        </div>

        {/* 消息内容 */}
        <div className={`px-4 py-3 rounded-lg ${
          isUser 
            ? 'bg-blue-600 text-white' 
            : 'bg-gray-100 text-gray-800'
        }`}>
          {/* 文本内容 */}
          <div className="whitespace-pre-wrap break-words">
            {message.content}
          </div>

          {/* 如果是试卷消息，显示试卷摘要 */}
          {message.exam && (
            <ExamSummary exam={message.exam} className="mt-3" />
          )}

          {/* 进度信息 */}
          {message.metadata?.progress && (
            <div className="mt-2 text-xs opacity-75">
              {message.metadata.progress}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
```

---

### 4. InputBox - 输入框组件

```tsx
// src/components/chat/InputBox.tsx
'use client';

import { useState, useRef, KeyboardEvent } from 'react';

interface InputBoxProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export function InputBox({ onSend, disabled, placeholder }: InputBoxProps) {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    const trimmed = input.trim();
    if (!trimmed || disabled) return;

    onSend(trimmed);
    setInput('');
    
    // 重置textarea高度
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Enter发送，Shift+Enter换行
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    
    // 自动调整高度
    e.target.style.height = 'auto';
    e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`;
  };

  return (
    <div className="px-6 py-4">
      <div className="flex gap-3 items-end">
        {/* 多行输入框 */}
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={handleInput}
            onKeyDown={handleKeyDown}
            disabled={disabled}
            placeholder={placeholder}
            rows={1}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
            style={{ minHeight: '48px', maxHeight: '120px' }}
          />
          
          {/* 提示文字 */}
          <div className="absolute right-3 bottom-2 text-xs text-gray-400">
            Enter 发送 / Shift+Enter 换行
          </div>
        </div>

        {/* 发送按钮 */}
        <button
          onClick={handleSend}
          disabled={disabled || !input.trim()}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition flex items-center gap-2"
        >
          {disabled ? (
            <>
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              <span>生成中</span>
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
              <span>发送</span>
            </>
          )}
        </button>
      </div>

      {/* 快捷操作按钮（可选） */}
      <div className="flex gap-2 mt-3">
        <button className="text-xs text-gray-500 hover:text-gray-700 px-2 py-1 rounded hover:bg-gray-100">
          📎 上传参考资料
        </button>
        <button className="text-xs text-gray-500 hover:text-gray-700 px-2 py-1 rounded hover:bg-gray-100">
          📋 查看历史会话
        </button>
      </div>
    </div>
  );
}
```

---

### 5. ThinkingIndicator - AI思考动画

```tsx
// src/components/chat/ThinkingIndicator.tsx
export function ThinkingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="max-w-[70%]">
        {/* 头像 */}
        <div className="flex items-center gap-2 mb-1">
          <div className="w-8 h-8 rounded-full bg-green-600 text-white flex items-center justify-center text-sm font-medium">
            AI
          </div>
          <span className="text-xs text-gray-500">正在思考...</span>
        </div>

        {/* 动画气泡 */}
        <div className="px-4 py-3 bg-gray-100 rounded-lg">
          <div className="flex gap-1.5">
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
        </div>
      </div>
    </div>
  );
}
```

---

### 6. ExamSummary - 试卷摘要卡片

```tsx
// src/components/chat/ExamSummary.tsx
import { Exam } from '@/lib/types';

interface ExamSummaryProps {
  exam: Exam;
  className?: string;
}

export function ExamSummary({ exam, className = '' }: ExamSummaryProps) {
  return (
    <div className={`border border-white/20 rounded-lg p-3 bg-white/10 ${className}`}>
      <div className="flex items-center gap-2 mb-2">
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <span className="font-semibold">试卷已生成</span>
      </div>
      
      <div className="text-sm space-y-1">
        <div className="flex justify-between">
          <span className="opacity-75">学科年级：</span>
          <span>{exam.subject} · {exam.grade}</span>
        </div>
        <div className="flex justify-between">
          <span className="opacity-75">题目数量：</span>
          <span>{exam.question_count} 道</span>
        </div>
        <div className="flex justify-between">
          <span className="opacity-75">总分：</span>
          <span>{exam.total_score} 分</span>
        </div>
        <div className="flex justify-between">
          <span className="opacity-75">来源：</span>
          <span>
            题库 {exam.source_stats.database} 道 + 
            AI {exam.source_stats.ai_generated} 道
          </span>
        </div>
      </div>

      <div className="mt-3 text-xs opacity-75">
        👉 完整试卷请查看右侧预览区
      </div>
    </div>
  );
}
```

---

## 🔗 自定义Hooks实现

### 1. useChat - 对话管理Hook

```typescript
// src/hooks/useChat.ts
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

  // 添加系统消息（进度提示）
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
      // SSE流式接收
      await streamGenerate(content, sessionId, (event) => {
        switch (event.type) {
          case 'session':
            // 保存会话ID
            setSessionId(event.session_id);
            break;

          case 'progress':
            // 显示进度
            addSystemMessage(event.message);
            break;

          case 'followup':
            // AI追问
            addMessage({
              role: 'assistant',
              content: event.message,
              type: 'followup'
            });
            break;

          case 'exam':
            // 试卷生成完成
            setCurrentExam(event.exam);
            addMessage({
              role: 'assistant',
              content: '✅ 试卷已生成完成！请在右侧查看详情。',
              type: 'exam',
              exam: event.exam
            });
            break;

          case 'done':
            // 流程结束
            break;
        }
      });
    } catch (error) {
      console.error('发送消息失败:', error);
      addMessage({
        role: 'assistant',
        content: '抱歉，生成失败了，请重试。',
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
```

---

### 2. useSession - 会话持久化Hook

```typescript
// src/hooks/useSession.ts
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
      // 验证会话是否仍然有效
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
    const newSessionId = response.data.session_id;
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
```

---

## 🎨 样式优化

### Tailwind配置扩展

```typescript
// tailwind.config.ts
import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      animation: {
        'bounce': 'bounce 1s infinite',
      },
      keyframes: {
        bounce: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-25%)' },
        }
      }
    },
  },
  plugins: [],
}
export default config
```

---

## 🔄 完整对话流程示例

### 场景1: 参数完整，直接生成

```
用户: "三年级数学第三章第二节课后练习5题"
  ↓
系统: [正在加载Skill...]
系统: [正在执行: extract_parameters]
系统: [正在执行: search_questions]
系统: [正在执行: generate_questions]
  ↓
AI: "✅ 试卷已生成完成！请在右侧查看详情。"
    [试卷摘要卡片]
    - 学科年级：数学 · 三年级
    - 题目数量：5 道
    - 总分：40 分
    - 来源：题库 3 道 + AI 2 道
```

### 场景2: 参数不完整，触发追问

```
用户: "帮我出份数学试卷"
  ↓
系统: [正在加载Skill...]
系统: [正在执行: extract_parameters]
系统: [正在执行: check_completeness]
  ↓
AI: "好的！请问是针对哪个年级出题呢？（如：初二、高一、高三）"
  ↓
用户: "三年级"
  ↓
系统: [正在执行: extract_parameters]
系统: [正在执行: check_completeness]
  ↓
AI: "明白了！请问是关于哪个知识点或章节？"
  ↓
用户: "第三章第二节"
  ↓
系统: [正在执行: extract_parameters]
系统: [正在执行: search_questions]
系统: [正在执行: generate_questions]
  ↓
AI: "✅ 试卷已生成完成！"
    [试卷摘要卡片]
```

---

## 🔧 工具函数

### 时间格式化

```typescript
// src/lib/utils.ts
export function formatTime(timestamp: number): string {
  const date = new Date(timestamp);
  const now = new Date();
  
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  
  if (diffMins < 1) return '刚刚';
  if (diffMins < 60) return `${diffMins}分钟前`;
  if (diffHours < 24) return `${diffHours}小时前`;
  
  return date.toLocaleString('zh-CN', {
    month: 'numeric',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}
```

---

## 📱 响应式适配

### 移动端布局调整

```tsx
// src/app/chat/page.tsx (响应式版本)
export default function ChatPage() {
  const [showExam, setShowExam] = useState(false);
  
  return (
    <div className="flex flex-col md:flex-row h-screen">
      {/* 移动端：Tab切换 */}
      <div className="md:hidden flex border-b">
        <button 
          onClick={() => setShowExam(false)}
          className={`flex-1 py-3 ${!showExam ? 'border-b-2 border-blue-600' : ''}`}
        >
          对话
        </button>
        <button 
          onClick={() => setShowExam(true)}
          className={`flex-1 py-3 ${showExam ? 'border-b-2 border-blue-600' : ''}`}
        >
          试卷
        </button>
      </div>

      {/* 对话区 */}
      <div className={`
        ${showExam ? 'hidden md:flex' : 'flex'} 
        w-full md:w-1/2 flex-col
      `}>
        {/* ... */}
      </div>

      {/* 试卷区 */}
      <div className={`
        ${!showExam ? 'hidden md:block' : 'block'}
        w-full md:w-1/2
      `}>
        {/* ... */}
      </div>
    </div>
  );
}
```

---

## ✅ 开发清单

### Phase 1: 基础对话（2天）
- [ ] 创建ChatPage主页面
- [ ] 实现MessageList组件
- [ ] 实现MessageBubble组件
- [ ] 实现InputBox组件
- [ ] 实现ThinkingIndicator组件

### Phase 2: 对话逻辑（2天）
- [ ] 实现useChat Hook
- [ ] 集成SSE流式接收
- [ ] 实现消息状态管理
- [ ] 实现自动滚动

### Phase 3: 会话管理（1天）
- [ ] 实现useSession Hook
- [ ] 实现localStorage持久化
- [ ] 实现会话恢复功能
- [ ] 实现会话清空功能

### Phase 4: UI优化（1天）
- [ ] 优化消息气泡样式
- [ ] 添加加载动画
- [ ] 实现响应式布局
- [ ] 优化交互体验

---

## 🎯 关键特性总结

| 特性 | 实现方式 |
|------|----------|
| **多轮对话** | 消息数组 + 追加新消息 |
| **参数追问** | SSE接收followup事件 |
| **实时反馈** | SSE进度事件 + 系统消息 |
| **会话持久化** | localStorage + Session API |
| **自动滚动** | useRef + scrollIntoView |
| **输入优化** | 自动高度 + Enter发送 |
| **加载状态** | isLoading + 思考动画 |
| **试卷联动** | currentExam状态 + 右侧预览 |

---

**现在多轮对话组件已经完整设计好了！可以开始实现。** 🎉
