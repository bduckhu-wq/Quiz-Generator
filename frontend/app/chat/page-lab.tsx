'use client';

import { useEffect, useState } from 'react';
import { useChat } from '@/hooks/useChat';
import { useSession } from '@/hooks/useSession';

export default function ChatPageLab() {
  const { sessionId, initSession } = useSession();
  const { messages, currentExam, isLoading, sendMessage } = useChat(sessionId);
  const [mounted, setMounted] = useState(false);
  const [input, setInput] = useState('');

  useEffect(() => {
    setMounted(true);
    initSession();
  }, []);

  const handleSend = () => {
    if (!input.trim() || isLoading) return;
    sendMessage(input.trim());
    setInput('');
  };

  if (!mounted) {
    return (
      <div className="min-h-screen bg-paper flex items-center justify-center">
        <div className="font-handwrite text-2xl text-ink-secondary">
          Loading research notes...
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen bg-paper flex flex-col md:flex-row overflow-hidden">
      {/* 左侧：对话区 - 活页笔记本风格 */}
      <div className="w-full md:w-1/2 flex flex-col border-r-2 border-grid-line relative">
        {/* 笔记本孔洞 */}
        <div className="absolute left-8 top-0 bottom-0 flex flex-col justify-around py-4 z-0">
          {[...Array(20)].map((_, i) => (
            <div
              key={i}
              className="w-3 h-3 rounded-full bg-paper-dark border border-pencil-gray/30"
            />
          ))}
        </div>

        {/* 顶部标题栏 - 印章风格 */}
        <div className="paper-sheet border-b-2 border-ink-primary p-6 relative z-10">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="font-display text-2xl text-ink-primary mb-1">
                对话实验记录
              </h1>
              <p className="font-mono text-xs text-pencil uppercase">
                Session · {sessionId.slice(0, 8)}...
              </p>
            </div>
            <div className="sticky-label text-sm px-4 py-2">
              Lab Mode
            </div>
          </div>
        </div>

        {/* 消息区域 */}
        <div className="flex-1 overflow-y-auto px-8 md:px-12 py-8 relative z-10">
          {messages.length === 0 && (
            <div className="h-full flex flex-col items-center justify-center text-center">
              <div className="index-card max-w-md">
                <div className="text-5xl mb-6">📓</div>
                <h2 className="font-display text-2xl text-ink-primary mb-4">
                  实验记录簿
                </h2>
                <p className="text-ink-secondary leading-relaxed mb-6">
                  输入您的出题需求，系统将通过智能对话逐步明确参数，
                  最终生成完整试卷。
                </p>

                {/* 示例按钮 */}
                <div className="space-y-3">
                  <p className="font-handwrite text-sm text-pencil mb-3">
                    尝试这些示例：
                  </p>
                  {[
                    '三年级数学第三章第二节5题',
                    '初二数学一元二次方程单元测验'
                  ].map((example, i) => (
                    <button
                      key={i}
                      onClick={() => sendMessage(example)}
                      className="w-full text-left p-3 border border-grid-line hover:border-ink-secondary transition-colors bg-white/50 hover:bg-white text-sm text-ink-secondary"
                    >
                      → {example}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* 消息列表 */}
          <div className="space-y-6">
            {messages.map((message, idx) => (
              <div
                key={message.id}
                className={`animate-ink-spread ${
                  message.role === 'system' ? 'flex justify-center' : ''
                }`}
                style={{ animationDelay: `${idx * 0.05}s` }}
              >
                {message.role === 'system' ? (
                  /* 系统消息 - 荧光标记风格 */
                  <div className="inline-block px-4 py-2 bg-highlight-yellow/30 border-l-4 border-highlight-yellow font-handwrite text-sm text-ink-secondary">
                    💭 {message.content}
                  </div>
                ) : (
                  /* 用户/AI消息 - 便签风格 */
                  <div
                    className={`flex ${
                      message.role === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                  >
                    <div className={`max-w-[75%] ${
                      message.role === 'user' ? 'ml-auto' : 'mr-auto'
                    }`}>
                      {/* 标签头 */}
                      <div
                        className={`flex items-center gap-2 mb-2 ${
                          message.role === 'user'
                            ? 'flex-row-reverse'
                            : 'flex-row'
                        }`}
                      >
                        <div
                          className={`w-8 h-8 rounded-sm flex items-center justify-center font-display text-xs font-bold ${
                            message.role === 'user'
                              ? 'bg-blue-note text-white'
                              : 'bg-red-mark text-white'
                          }`}
                        >
                          {message.role === 'user' ? 'U' : 'AI'}
                        </div>
                        <span className="font-mono text-xs text-pencil uppercase">
                          {new Date(message.timestamp).toLocaleTimeString('zh-CN', {
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </span>
                      </div>

                      {/* 消息内容 */}
                      <div
                        className={`paper-sheet p-4 relative ${
                          message.role === 'user'
                            ? 'bg-blue-note/5 border-l-4 border-blue-note'
                            : 'bg-white border-l-4 border-red-mark'
                        }`}
                      >
                        <div className="text-ink-primary leading-relaxed whitespace-pre-wrap">
                          {message.content}
                        </div>

                        {/* 便签折角 */}
                        {message.role === 'assistant' && (
                          <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-red-mark/10 border-t border-l border-red-mark/20" />
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}

            {/* AI思考动画 */}
            {isLoading && (
              <div className="flex justify-start animate-ink-spread">
                <div className="index-card max-w-xs">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-sm bg-red-mark text-white flex items-center justify-center font-display text-xs font-bold animate-pulse">
                      AI
                    </div>
                    <div className="flex gap-1.5">
                      {[0, 1, 2].map((i) => (
                        <div
                          key={i}
                          className="w-2 h-2 rounded-full bg-red-mark animate-bounce"
                          style={{ animationDelay: `${i * 0.15}s` }}
                        />
                      ))}
                    </div>
                    <span className="font-handwrite text-ink-secondary">
                      思考中...
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* 输入区 - 手写输入框风格 */}
        <div className="border-t-2 border-grid-line bg-paper-dark p-6 relative z-10">
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                disabled={isLoading}
                placeholder="输入出题需求..."
                className="input-underline w-full text-lg disabled:opacity-50"
              />
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-ink-primary/20 to-transparent" />
            </div>

            <button
              onClick={handleSend}
              disabled={isLoading || !input.trim()}
              className="btn-stamp px-6 disabled:opacity-30 disabled:cursor-not-allowed"
            >
              发送
            </button>
          </div>

          <p className="font-mono text-xs text-pencil mt-3 text-center">
            Enter 发送 · Shift+Enter 换行
          </p>
        </div>
      </div>

      {/* 右侧：试卷预览区 - 打印稿风格 */}
      <div className="w-full md:w-1/2 overflow-y-auto bg-paper-dark p-8">
        {currentExam ? (
          <div className="max-w-3xl mx-auto animate-paper-flip">
            {/* 试卷头部 - 官方文件风格 */}
            <div className="paper-sheet p-8 mb-8 text-center relative">
              {/* 密封条 */}
              <div className="absolute top-0 left-0 right-0 h-12 bg-gradient-to-b from-red-mark/10 to-transparent border-b-2 border-dashed border-red-mark/30" />

              <div className="mt-6">
                <div className="font-mono text-xs text-pencil uppercase tracking-wider mb-2">
                  Official Examination Paper
                </div>
                <h1 className="font-display text-4xl text-ink-primary mb-3">
                  {currentExam.subject} 试卷
                </h1>

                <div className="flex justify-center items-center gap-4 text-sm mb-4 flex-wrap">
                  <span className="font-mono text-ink-secondary">
                    年级：{currentExam.grade}
                  </span>
                  <span className="text-pencil">|</span>
                  <span className="font-mono text-ink-secondary">
                    范围：{currentExam.knowledge_points.join('、')}
                  </span>
                  <span className="text-pencil">|</span>
                  <span className="font-mono text-ink-secondary">
                    总分：{currentExam.total_score}分
                  </span>
                </div>

                <div className="inline-flex gap-4 text-xs border-t border-b border-grid-line py-2 px-6">
                  <span className="text-blue-note">
                    📚 题库: {currentExam.source_stats.database}题
                  </span>
                  <span className="text-red-mark">
                    🤖 AI: {currentExam.source_stats.ai_generated}题
                  </span>
                </div>
              </div>
            </div>

            {/* 题目列表 */}
            <div className="space-y-6">
              {currentExam.questions.map((q, idx) => (
                <div
                  key={q.id}
                  className="paper-sheet p-6 animate-ink-spread hover:shadow-lifted transition-shadow"
                  style={{ animationDelay: `${idx * 0.08}s` }}
                >
                  {/* 题目头部 */}
                  <div className="flex items-start justify-between mb-4 border-b border-grid-line pb-3">
                    <div className="flex items-center gap-3">
                      <div className="circle-mark text-ink-primary px-3 py-1">
                        {q.index}
                      </div>
                      <div className="font-mono text-sm text-ink-secondary">
                        [{q.question_type}]
                      </div>
                      <div className="font-mono text-xs text-pencil uppercase">
                        {q.difficulty}
                      </div>
                      <div className="font-display text-sm text-ink-primary">
                        {q.score}分
                      </div>
                    </div>

                    {/* 来源标记 */}
                    {q.source && (
                      <div
                        className={`sticky-label text-xs px-3 py-1 ${
                          q.source === '题库'
                            ? 'bg-blue-note/20 border border-blue-note/30'
                            : 'bg-red-mark/20 border border-red-mark/30'
                        }`}
                      >
                        {q.source === '题库' ? '📚 题库' : '🤖 AI'}
                      </div>
                    )}
                  </div>

                  {/* 题目内容 */}
                  <div className="text-ink-primary leading-relaxed mb-4">
                    {q.content}
                  </div>

                  {/* 选项 */}
                  {q.options && (
                    <div className="space-y-2 mb-4 pl-4">
                      {(typeof q.options === 'string'
                        ? JSON.parse(q.options)
                        : q.options
                      ).map((opt: string, i: number) => (
                        <div
                          key={i}
                          className="text-ink-secondary flex items-start"
                        >
                          <span className="text-pencil mr-2">→</span>
                          {opt}
                        </div>
                      ))}
                    </div>
                  )}

                  {/* 答案解析 */}
                  <details className="mt-4 group">
                    <summary className="cursor-pointer font-handwrite text-base text-blue-note hover:text-ink-primary transition-colors flex items-center gap-2">
                      <span className="group-open:rotate-90 transition-transform text-sm">
                        ▶
                      </span>
                      查看答案与解析
                    </summary>
                    <div className="mt-4 p-4 bg-highlight-yellow/10 border-l-4 border-highlight-yellow">
                      <div className="mb-3">
                        <span className="font-display text-sm text-ink-primary">
                          答案：
                        </span>
                        <span className="font-mono text-ink-primary ml-2">
                          {q.answer}
                        </span>
                      </div>
                      {q.analysis && (
                        <div>
                          <span className="font-display text-sm text-ink-secondary">
                            解析：
                          </span>
                          <p className="text-ink-secondary leading-relaxed mt-2">
                            {q.analysis}
                          </p>
                        </div>
                      )}
                    </div>
                  </details>
                </div>
              ))}
            </div>

            {/* 底部签名区 */}
            <div className="paper-sheet p-8 mt-8 flex justify-between items-end">
              <div>
                <div className="font-mono text-xs text-pencil mb-2">
                  Generated on
                </div>
                <div className="font-handwrite text-lg text-ink-secondary">
                  {new Date().toLocaleDateString('zh-CN', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </div>
              </div>
              <div className="text-right">
                <div className="pencil-underline font-mono text-sm text-ink-primary pb-1 w-32 text-center mb-2">
                  教师签名
                </div>
                <div className="font-mono text-xs text-pencil">
                  Signature
                </div>
              </div>
            </div>
          </div>
        ) : (
          /* 空状态 - 草稿纸风格 */
          <div className="h-full flex items-center justify-center">
            <div className="text-center max-w-md">
              <div className="index-card grid-paper p-8">
                <svg
                  className="w-24 h-24 mx-auto mb-6 text-pencil opacity-30"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
                <h3 className="font-display text-xl text-ink-primary mb-2">
                  等待生成试卷
                </h3>
                <p className="font-handwrite text-lg text-pencil">
                  在左侧输入出题需求后，试卷将在此处展示
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
