'use client';

import { useRouter } from 'next/navigation';

export default function HomePage() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-paper relative overflow-hidden">
      {/* 笔记本孔洞装饰 */}
      <div className="absolute left-12 top-0 bottom-0 flex flex-col justify-around py-8">
        {[...Array(12)].map((_, i) => (
          <div
            key={i}
            className="w-4 h-4 rounded-full bg-paper-dark border border-grid-line shadow-inner"
          />
        ))}
      </div>

      {/* 主内容区 */}
      <div className="max-w-5xl mx-auto px-8 md:px-16 py-12 relative z-10">
        {/* 页眉 - 手写标题 */}
        <div className="mb-16 paper-sheet p-8 animate-paper-flip">
          <div className="flex items-start justify-between mb-8">
            <div>
              <div className="font-handwrite text-pencil text-sm mb-2">
                Research Notes · Vol. 2026
              </div>
              <h1 className="font-display text-6xl md:text-7xl text-ink-primary mb-4 leading-tight">
                AI 出题<br />助手系统
              </h1>
              <div className="font-handwrite text-2xl text-ink-secondary mb-6">
                Intelligent Question Generation Laboratory
              </div>
            </div>

            {/* 日期戳章 */}
            <div className="sticky-label text-lg px-6 py-3">
              {new Date().toLocaleDateString('zh-CN', {
                month: 'short',
                day: 'numeric'
              })}
            </div>
          </div>

          {/* 研究摘要 */}
          <div className="border-l-4 border-blue-note pl-6 mb-8">
            <p className="text-lg text-ink-secondary leading-relaxed">
              基于自然语言处理的智能对话式试卷生成系统。通过多轮语义理解，
              <span className="highlight-text">精准匹配题库资源</span>，
              结合AI动态生成，为K12教师提供高效的出题解决方案。
            </p>
          </div>

          {/* CTA按钮 */}
          <button
            onClick={() => router.push('/chat')}
            className="btn-stamp group relative overflow-hidden"
          >
            <span className="relative z-10">开始实验 →</span>

            {/* 墨水扩散效果 */}
            <div className="absolute inset-0 bg-ink-primary transform scale-x-0 transition-transform duration-300 group-hover:scale-x-100 origin-left" />
          </button>
        </div>

        {/* 功能特性 - 索引卡片网格 */}
        <div className="mb-16">
          <h2 className="font-display text-3xl text-ink-primary mb-8 flex items-center">
            <span className="handwritten-note mr-4">核心特性</span>
            <svg className="w-24 h-2" viewBox="0 0 100 2">
              <line
                x1="0"
                y1="1"
                x2="100"
                y2="1"
                className="annotation-line"
                style={{ animationDelay: '0.5s' }}
              />
            </svg>
          </h2>

          <div className="grid md:grid-cols-3 gap-6">
            {/* 特性卡片 1 */}
            <div
              className="index-card animate-ink-spread"
              style={{ animationDelay: '0.1s' }}
            >
              <div className="absolute top-4 right-4 text-4xl opacity-20">
                📊
              </div>
              <div className="relative z-10">
                <h3 className="font-display text-xl text-ink-primary mb-3">
                  语义理解引擎
                </h3>
                <p className="text-ink-secondary leading-relaxed mb-4">
                  自然语言输入，系统自动识别年级、学科、章节、难度等多维度参数
                </p>
                <div className="font-mono text-xs text-pencil">
                  Semantic Parsing
                </div>
              </div>

              {/* 便签标记 */}
              <div className="absolute -right-2 -top-2 sticky-label text-xs px-3 py-1">
                NLP
              </div>
            </div>

            {/* 特性卡片 2 */}
            <div
              className="index-card animate-ink-spread"
              style={{ animationDelay: '0.2s' }}
            >
              <div className="absolute top-4 right-4 text-4xl opacity-20">
                🎯
              </div>
              <div className="relative z-10">
                <h3 className="font-display text-xl text-ink-primary mb-3">
                  混合生成策略
                </h3>
                <p className="text-ink-secondary leading-relaxed mb-4">
                  题库检索 + AI智能生成，确保题目质量与教学相关性
                </p>
                <div className="font-mono text-xs text-pencil">
                  Hybrid Approach
                </div>
              </div>

              {/* 批改标记 */}
              <div className="absolute bottom-4 right-4">
                <div className="circle-mark text-red-mark text-xs">
                  ✓
                </div>
              </div>
            </div>

            {/* 特性卡片 3 */}
            <div
              className="index-card animate-ink-spread"
              style={{ animationDelay: '0.3s' }}
            >
              <div className="absolute top-4 right-4 text-4xl opacity-20">
                📝
              </div>
              <div className="relative z-10">
                <h3 className="font-display text-xl text-ink-primary mb-3">
                  实时试卷预览
                </h3>
                <p className="text-ink-secondary leading-relaxed mb-4">
                  流式输出生成过程，双栏布局即时展示试卷结构与内容
                </p>
                <div className="font-mono text-xs text-pencil">
                  Real-time Preview
                </div>
              </div>

              {/* 荧光标记 */}
              <div className="absolute -left-2 top-1/2 transform -translate-y-1/2 w-1 h-16 bg-highlight-yellow opacity-60" />
            </div>
          </div>
        </div>

        {/* 技术规格 */}
        <div className="paper-sheet p-8 grid-paper animate-paper-flip" style={{ animationDelay: '0.4s' }}>
          <h2 className="font-display text-2xl text-ink-primary mb-6">
            技术规格说明
          </h2>

          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <h3 className="font-mono text-sm text-pencil uppercase tracking-wider mb-3">
                前端技术栈
              </h3>
              <ul className="space-y-2">
                {[
                  'Next.js 14 (App Router)',
                  'TypeScript + React Hooks',
                  'SSE 流式数据接收',
                  'Tailwind CSS 样式系统'
                ].map((item, i) => (
                  <li key={i} className="flex items-center text-ink-secondary">
                    <span className="text-red-mark mr-2">→</span>
                    {item}
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h3 className="font-mono text-sm text-pencil uppercase tracking-wider mb-3">
                后端架构
              </h3>
              <ul className="space-y-2">
                {[
                  'FastAPI + Python 3.9',
                  'LangGraph Workflow Engine',
                  'OpenClaw Skills System',
                  'SQLite 题库 (160+ 题目)'
                ].map((item, i) => (
                  <li key={i} className="flex items-center text-ink-secondary">
                    <span className="text-blue-note mr-2">▪</span>
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* 底部注释 */}
          <div className="mt-8 pt-6 border-t border-grid-line">
            <p className="font-handwrite text-lg text-pencil text-center">
              Designed for K12 educators · Built with precision
            </p>
          </div>
        </div>

        {/* 页脚元数据 */}
        <div className="mt-12 flex justify-between items-center text-sm text-pencil">
          <div className="font-mono">
            Version 2.0 · 2026-04-28
          </div>
          <div className="font-handwrite text-base">
            Claude × AI Research Lab
          </div>
        </div>
      </div>

      {/* 书签装饰 */}
      <div className="bookmark-tab">
        Start
      </div>
    </div>
  );
}
