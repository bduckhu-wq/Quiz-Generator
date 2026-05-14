'use client';

import { useEffect, useState } from 'react';
import { useChat } from '@/hooks/useChat';
import { useSession } from '@/hooks/useSession';

export default function CyberChatPage() {
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
      <div className="h-screen bg-cyber-black flex items-center justify-center">
        <div className="cyber-loader" />
      </div>
    );
  }

  return (
    <div className="h-screen bg-cyber-black flex flex-col md:flex-row overflow-hidden">
      {/* 左侧：终端对话区 */}
      <div className="w-full md:w-1/2 flex flex-col border-r-2 border-cyber-cyan/30 relative">
        {/* 数据流装饰线 */}
        <div className="absolute top-0 left-0 w-full h-full pointer-events-none overflow-hidden opacity-20">
          {[...Array(10)].map((_, i) => (
            <div
              key={i}
              className="absolute w-full h-px bg-gradient-to-r from-transparent via-cyber-cyan to-transparent"
              style={{
                top: `${i * 10}%`,
                animation: `scan-horizontal ${3 + i * 0.5}s linear infinite`,
                animationDelay: `${i * 0.2}s`
              }}
            />
          ))}
        </div>

        {/* 顶部状态栏 */}
        <div className="holo-panel border-b-2 border-cyber-cyan p-4 relative z-10">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="font-display text-xl text-cyber-cyan neon-text-cyan">
                TERMINAL_CHAT
              </h1>
              <p className="font-mono text-xs text-gray-500 mt-1">
                SESSION_ID: {sessionId.slice(0, 12)}...
              </p>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-cyber-lime animate-pulse" />
              <span className="font-mono text-xs text-cyber-lime">ACTIVE</span>
            </div>
          </div>
        </div>

        {/* 消息区域 */}
        <div className="flex-1 overflow-y-auto px-6 py-8 relative z-10 cyber-grid">
          {messages.length === 0 && (
            <div className="h-full flex items-center justify-center">
              <div className="text-center max-w-md">
                <div className="holo-panel p-8">
                  <div className="text-6xl mb-6">🖥️</div>
                  <h2 className="font-display text-2xl text-cyber-cyan mb-4">
                    AWAITING INPUT
                  </h2>
                  <p className="font-body text-gray-400 mb-6 leading-relaxed">
                    输入出题需求参数，AI系统将启动多轮语义解析流程
                  </p>

                  {/* 命令示例 */}
                  <div className="text-left space-y-3">
                    <div className="font-mono text-xs text-cyber-cyan mb-2">
                      &gt; SAMPLE_COMMANDS:
                    </div>
                    {[
                      '三年级数学第三章第二节5题',
                      '初二数学一元二次方程单元测验'
                    ].map((cmd, i) => (
                      <button
                        key={i}
                        onClick={() => sendMessage(cmd)}
                        className="w-full text-left terminal-input p-3 hover:border-cyber-lime transition-colors text-sm"
                      >
                        <span className="text-cyber-lime">$</span> {cmd}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}
          )}

          {/* 消息列表 */}
          <div className="space-y-4">
            {messages.map((message, idx) => (
              <div
                key={message.id}
                className="animate-data-stream"
                style={{ animationDelay: `${idx * 0.05}s` }}
              >
                {message.role === 'system' ? (
                  /* 系统消息 */
                  <div className="flex items-center gap-3 px-4 py-2 border-l-4 border-cyber-lime bg-cyber-lime/5">
                    <div className="text-cyber-lime font-mono text-xs">SYS</div>
                    <div className="font-mono text-sm text-gray-400">
                      {message.content}
                    </div>
                  </div>
                ) : (
                  /* 用户/AI消息 */
                  <div className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[80%] ${message.role === 'user' ? 'ml-auto' : 'mr-auto'}`}>
                      {/* 消息头 */}
                      <div className={`flex items-center gap-2 mb-2 ${
                        message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                      }`}>
                        <div className={`px-2 py-1 font-mono text-xs ${
                          message.role === 'user'
                            ? 'bg-cyber-cyan text-cyber-black'
                            : 'bg-cyber-magenta text-white'
                        }`}>
                          {message.role === 'user' ? 'USER' : 'AI_BOT'}
                        </div>
                        <span className="font-mono text-xs text-gray-600">
                          {new Date(message.timestamp).toLocaleTimeString('en-US', {
                            hour12: false,
                            hour: '2-digit',
                            minute: '2-digit',
                            second: '2-digit'
                          })}
                        </span>
                      </div>

                      {/* 消息体 */}
                      <div className={`data-card ${
                        message.role === 'user'
                          ? 'border-cyber-cyan'
                          : 'border-cyber-magenta'
                      }`}>
                        <div className="font-body text-sm text-gray-300 leading-relaxed whitespace-pre-wrap">
                          {message.content}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}

            {/* AI思考指示器 */}
            {isLoading && (
              <div className="flex justify-start">
                <div className="data-card border-cyber-magenta max-w-xs">
                  <div className="flex items-center gap-3">
                    <div className="cyber-loader w-6 h-6" />
                    <span className="font-mono text-sm text-cyber-magenta">
                      PROCESSING...
                    </span>
                  </div>
                  <div className="progress-bar mt-3" />
                </div>
              </div>
            )}
          </div>
        </div>

        {/* 输入区 */}
        <div className="border-t-2 border-cyber-cyan/30 bg-cyber-dark p-4 relative z-10">
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <div className="absolute left-3 top-1/2 -translate-y-1/2 font-mono text-cyber-lime">
                $
              </div>
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
                placeholder="ENTER_COMMAND..."
                className="terminal-input w-full pl-8 disabled:opacity-50"
              />
            </div>

            <button
              onClick={handleSend}
              disabled={isLoading || !input.trim()}
              className="cyber-btn px-6 disabled:opacity-30 disabled:cursor-not-allowed"
            >
              SEND
            </button>
          </div>

          <p className="font-mono text-xs text-gray-600 mt-2 text-center">
            ENTER → EXECUTE · SHIFT+ENTER → NEWLINE
          </p>
        </div>
      </div>

      {/* 右侧：数据面板 */}
      <div className="w-full md:w-1/2 overflow-y-auto bg-cyber-dark/50 p-6 cyber-grid">
        {currentExam ? (
          <div className="animate-hologram">
            {/* 试卷头部 */}
            <div className="holo-panel p-6 mb-6">
              <div className="text-center mb-4">
                <div className="font-mono text-xs text-cyber-cyan mb-2 tracking-wider">
                  EXAMINATION_DATA_PACKET
                </div>
                <h1 className="font-display text-3xl neon-text-cyan mb-3">
                  {currentExam.subject}
                </h1>

                <div className="flex justify-center gap-4 text-sm flex-wrap">
                  <div className="data-tag">
                    GRADE: {currentExam.grade}
                  </div>
                  <div className="data-tag magenta">
                    SCOPE: {currentExam.knowledge_points.join('、')}
                  </div>
                  <div className="data-tag lime">
                    SCORE: {currentExam.total_score}
                  </div>
                </div>
              </div>

              <div className="flex justify-center gap-6 font-mono text-xs pt-4 border-t border-cyber-cyan/20">
                <span className="text-cyber-cyan">
                  DB: {currentExam.source_stats.database}
                </span>
                <span className="text-cyber-magenta">
                  AI: {currentExam.source_stats.ai_generated}
                </span>
              </div>
            </div>

            {/* 题目列表 */}
            <div className="space-y-4">
              {currentExam.questions.map((q, idx) => (
                <div
                  key={q.id}
                  className="data-card hex-pattern animate-data-stream"
                  data-hex={`0x${(idx + 1).toString(16).toUpperCase().padStart(2, '0')}`}
                  style={{ animationDelay: `${idx * 0.08}s` }}
                >
                  {/* 题目头部 */}
                  <div className="flex items-start justify-between mb-4 pb-3 border-b border-cyber-cyan/20">
                    <div className="flex items-center gap-3 flex-wrap">
                      <div className="w-8 h-8 flex items-center justify-center border-2 border-cyber-cyan font-display text-sm text-cyber-cyan">
                        {q.index}
                      </div>
                      <span className="font-mono text-xs text-gray-400">
                        [{q.question_type}]
                      </span>
                      <span className="font-mono text-xs text-gray-500 uppercase">
                        {q.difficulty}
                      </span>
                      <span className="font-display text-sm text-cyber-lime">
                        {q.score}PTS
                      </span>
                    </div>

                    {/* 来源标签 */}
                    {q.source && (
                      <div className={`data-tag text-xs ${
                        q.source === '题库' ? '' : 'magenta'
                      }`}>
                        {q.source === '题库' ? 'DB' : 'AI'}
                      </div>
                    )}
                  </div>

                  {/* 题目内容 */}
                  <div className="font-body text-gray-300 leading-relaxed mb-3">
                    {q.content}
                  </div>

                  {/* 选项 */}
                  {q.options && (
                    <div className="space-y-2 mb-3 pl-4 border-l border-cyber-cyan/20">
                      {(typeof q.options === 'string'
                        ? JSON.parse(q.options)
                        : q.options
                      ).map((opt: string, i: number) => (
                        <div
                          key={i}
                          className="font-mono text-sm text-gray-400 flex items-start"
                        >
                          <span className="text-cyber-cyan mr-2">›</span>
                          {opt}
                        </div>
                      ))}
                    </div>
                  )}

                  {/* 答案解析 */}
                  <details className="mt-4 group">
                    <summary className="cursor-pointer font-mono text-xs text-cyber-cyan hover:text-cyber-lime transition-colors uppercase tracking-wider">
                      &gt; VIEW_ANSWER
                    </summary>
                    <div className="mt-3 p-4 bg-cyber-black/50 border-l-2 border-cyber-lime">
                      <div className="mb-3">
                        <span className="font-mono text-xs text-cyber-lime">ANS:</span>
                        <span className="font-mono text-sm text-gray-300 ml-2">
                          {q.answer}
                        </span>
                      </div>
                      {q.analysis && (
                        <div>
                          <span className="font-mono text-xs text-cyber-magenta">EXP:</span>
                          <p className="font-body text-sm text-gray-400 leading-relaxed mt-2">
                            {q.analysis}
                          </p>
                        </div>
                      )}
                    </div>
                  </details>
                </div>
              ))}
            </div>

            {/* 底部签名 */}
            <div className="holo-panel p-6 mt-6 flex justify-between items-center">
              <div className="font-mono text-xs text-gray-500">
                <div>GENERATED:</div>
                <div className="text-cyber-cyan mt-1">
                  {new Date().toLocaleString('en-US', {
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit',
                    hour12: false
                  })}
                </div>
              </div>
              <div className="text-right">
                <div className="font-mono text-xs text-gray-500 mb-1">
                  VERIFIED_BY
                </div>
                <div className="w-32 h-px bg-cyber-cyan" />
              </div>
            </div>
          </div>
        ) : (
          /* 空状态 */
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <div className="holo-panel p-8 inline-block">
                <svg
                  className="w-24 h-24 mx-auto mb-6 text-cyber-cyan/30"
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
                <h3 className="font-display text-xl text-cyber-cyan mb-2">
                  NO_DATA
                </h3>
                <p className="font-mono text-sm text-gray-500">
                  AWAITING EXAM GENERATION
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
