'use client';

import { useEffect, useState } from 'react';
import { useChat } from '@/hooks/useChat';
import { useSession } from '@/hooks/useSession';
import { InputBox } from '@/components/chat/InputBox';
import { ThinkingIndicator } from '@/components/chat/ThinkingIndicator';

export default function ChatPage() {
  const { sessionId, initSession } = useSession();
  const { messages, currentExam, isLoading, sendMessage } = useChat(sessionId);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    initSession();
  }, []);

  if (!mounted) {
    return <div className="flex h-screen items-center justify-center">加载中...</div>;
  }

  return (
    <div className="flex flex-col md:flex-row h-screen" style={{ background: 'var(--bg-secondary)' }}>
      {/* 左侧：对话区 */}
      <div className="w-full md:w-1/2 flex flex-col" style={{ background: 'var(--bg-primary)', borderRight: '1px solid var(--border-light)' }}>
        {/* 顶部标题栏 */}
        <div className="px-6 py-4" style={{ borderBottom: '1px solid var(--border-light)' }}>
          <h1 className="text-xl font-semibold flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
            <span>🎓</span>
            AI 出题助手
          </h1>
          <p className="text-sm mt-1" style={{ color: 'var(--text-secondary)' }}>智能对话生成试卷</p>
        </div>

        {/* 消息列表区 */}
        <div className="flex-1 overflow-y-auto px-6 py-6">
          {messages.length === 0 && (
            <div className="text-center mt-20">
              <div className="mb-6">
                <span className="text-5xl">👋</span>
              </div>
              <h2 className="text-xl font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>
                你好，我是 AI 出题助手
              </h2>
              <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                告诉我您的出题需求，我会帮您生成试卷
              </p>

              <div className="mt-10 space-y-3 max-w-md mx-auto">
                <p className="text-xs text-left mb-4" style={{ color: 'var(--text-tertiary)' }}>
                  💡 试试这些示例
                </p>
                <button
                  onClick={() => sendMessage('三年级数学第三章第二节课后练习5题')}
                  className="card-clean w-full p-4 text-left text-sm hover:shadow-md transition-all"
                  style={{ color: 'var(--text-primary)' }}
                >
                  三年级数学第三章第二节课后练习5题
                </button>
                <button
                  onClick={() => sendMessage('初二数学一元二次方程单元测验')}
                  className="card-clean w-full p-4 text-left text-sm hover:shadow-md transition-all"
                  style={{ color: 'var(--text-primary)' }}
                >
                  初二数学一元二次方程单元测验
                </button>
              </div>
            </div>
          )}

          {/* 消息列表 */}
          <div className="space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                {message.role === 'system' ? (
                  <div className="px-4 py-2 text-xs rounded-full text-center mx-auto max-w-fit" style={{ background: 'var(--bg-tertiary)', color: 'var(--text-secondary)' }}>
                    {message.content}
                  </div>
                ) : (
                  <div className={`max-w-[75%] ${
                    message.role === 'user' ? 'ml-auto' : 'mr-auto'
                  }`}>
                    <div
                      className={`flex items-center gap-2 mb-2 ${
                        message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                      }`}
                    >
                      <div
                        className="avatar-circle"
                        style={{
                          background: message.role === 'user' ? 'var(--brand-primary)' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                          color: 'white'
                        }}
                      >
                        {message.role === 'user' ? '我' : 'AI'}
                      </div>
                    </div>

                    <div
                      className={message.role === 'user' ? 'message-bubble-user' : 'message-bubble-ai'}
                    >
                      {message.content}

                      {message.exam && (
                        <div className="mt-3 border-t border-white/20 pt-3 text-sm">
                          <div>📊 {message.exam.question_count} 道题</div>
                          <div>💯 {message.exam.total_score} 分</div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}

            {isLoading && <ThinkingIndicator />}
          </div>
        </div>

        {/* 输入框 */}
        <div className="border-t bg-white">
          <InputBox
            onSend={sendMessage}
            disabled={isLoading}
            placeholder={
              messages.length === 0
                ? '输入出题需求，如：三年级数学第三章第二节课后练习5题'
                : '继续对话...'
            }
          />
        </div>
      </div>

      {/* 右侧：试卷预览区 */}
      <div className="w-full md:w-1/2 overflow-y-auto" style={{ background: 'var(--bg-secondary)' }}>
        {currentExam ? (
          <div className="p-6">
            {/* 试卷头部 */}
            <div className="card-clean p-6 mb-6 text-center">
              <h1 className="text-2xl font-bold mb-3" style={{ color: 'var(--text-primary)' }}>
                {currentExam.subject} 试卷
              </h1>
              <div className="flex justify-center items-center gap-3 text-sm flex-wrap">
                <span className="tag tag-blue">
                  {currentExam.grade}
                </span>
                <span className="tag tag-gray">
                  {currentExam.knowledge_points.join('、')}
                </span>
                <span className="tag tag-green">
                  总分 {currentExam.total_score}
                </span>
              </div>
              <div className="mt-3 flex justify-center gap-4 text-xs" style={{ color: 'var(--text-secondary)' }}>
                <span>📚 题库 {currentExam.source_stats.database}</span>
                <span>🤖 AI {currentExam.source_stats.ai_generated}</span>
              </div>
            </div>

            {/* 题目列表 */}
            <div className="space-y-4">
              {currentExam.questions.map((q, idx) => (
                <div
                  key={q.id}
                  className="question-card"
                >
                  {/* 题目头部 */}
                  <div className="flex justify-between items-start mb-4 pb-3" style={{ borderBottom: '1px solid var(--border-light)' }}>
                    <div className="flex items-center flex-wrap gap-2">
                      <div className="question-number">
                        {q.index}
                      </div>
                      <span className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
                        [{q.question_type}]
                      </span>
                      <span className="tag tag-gray text-xs">
                        {q.difficulty}
                      </span>
                      <span className="tag tag-green text-xs">
                        {q.score}分
                      </span>
                      {q.source && (
                        <span className={`tag text-xs ${
                          q.source === '题库' ? 'tag-blue' : 'tag-orange'
                        }`}>
                          {q.source === '题库' ? '📚 题库' : '🤖 AI'}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* 题目内容 */}
                  <div className="mb-4 leading-relaxed" style={{ color: 'var(--text-primary)' }}>
                    {q.content}
                  </div>

                  {/* 选项 */}
                  {q.options && (
                    <div className="mb-4 space-y-2">
                      {(typeof q.options === 'string'
                        ? JSON.parse(q.options)
                        : q.options
                      ).map((opt: string, idx: number) => (
                        <div key={idx} className="pl-4 py-1 text-gray-700 hover:bg-gray-50 rounded transition">
                          {opt}
                        </div>
                      ))}
                    </div>
                  )}

                  {/* 答案解析 */}
                  <details className="mt-4 group">
                    <summary className="cursor-pointer text-sm font-medium flex items-center gap-2 transition" style={{ color: 'var(--brand-primary)' }}>
                      <span className="group-open:rotate-90 transition-transform">▶</span>
                      查看答案和解析
                    </summary>
                    <div className="mt-3 p-4 rounded-lg" style={{ background: 'var(--bg-tertiary)' }}>
                      <p className="mb-3 flex items-start gap-2">
                        <strong className="flex-shrink-0" style={{ color: 'var(--text-primary)' }}>
                          答案：
                        </strong>
                        <span style={{ color: 'var(--text-primary)' }}>{q.answer}</span>
                      </p>
                      {q.analysis && (
                        <p className="flex items-start gap-2">
                          <strong className="flex-shrink-0" style={{ color: 'var(--text-primary)' }}>
                            解析：
                          </strong>
                          <span className="leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
                            {q.analysis}
                          </span>
                        </p>
                      )}
                    </div>
                  </details>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-gray-400">
            <svg
              className="w-24 h-24 mb-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <p className="text-lg">试卷将在这里展示</p>
            <p className="text-sm mt-2">在左侧输入出题需求开始</p>
          </div>
        )}
      </div>
    </div>
  );
}
