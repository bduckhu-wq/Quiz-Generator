'use client';

import { useRouter } from 'next/navigation';

export default function HomePage() {
  const router = useRouter();

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6" style={{ background: 'var(--bg-secondary)' }}>
      <div className="text-center max-w-3xl w-full">
        {/* Logo */}
        <div className="mb-8">
          <span className="text-7xl">🎓</span>
        </div>

        {/* 标题 */}
        <h1 className="text-5xl md:text-6xl font-bold mb-4" style={{ color: 'var(--text-primary)' }}>
          AI 出题助手
        </h1>

        <p className="text-lg md:text-xl mb-10" style={{ color: 'var(--text-secondary)' }}>
          通过智能对话，快速生成高质量试卷
        </p>

        {/* CTA按钮 */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={() => router.push('/chat')}
            className="btn-primary text-base inline-flex items-center gap-2 justify-center"
          >
            <span>💬 对话出题</span>
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
          <button
            onClick={() => router.push('/similar-question')}
            className="btn-secondary text-base inline-flex items-center gap-2 justify-center"
          >
            <span>📸 相似题生成</span>
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>

        {/* 特性卡片 */}
        <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-5">
          <div className="card-clean p-6 text-left">
            <div className="w-12 h-12 rounded-full flex items-center justify-center mb-4" style={{ background: '#eef3ff' }}>
              <span className="text-2xl">⚡</span>
            </div>
            <h3 className="font-semibold text-base mb-2" style={{ color: 'var(--text-primary)' }}>
              智能理解
            </h3>
            <p className="text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
              自然语言输入，AI自动识别年级、学科、章节等参数
            </p>
          </div>

          <div className="card-clean p-6 text-left">
            <div className="w-12 h-12 rounded-full flex items-center justify-center mb-4" style={{ background: '#e8faf3' }}>
              <span className="text-2xl">🎯</span>
            </div>
            <h3 className="font-semibold text-base mb-2" style={{ color: 'var(--text-primary)' }}>
              精准匹配
            </h3>
            <p className="text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
              题库检索+AI生成，双重保障题目质量
            </p>
          </div>

          <div className="card-clean p-6 text-left">
            <div className="w-12 h-12 rounded-full flex items-center justify-center mb-4" style={{ background: '#fff3e8' }}>
              <span className="text-2xl">📝</span>
            </div>
            <h3 className="font-semibold text-base mb-2" style={{ color: 'var(--text-primary)' }}>
              即时预览
            </h3>
            <p className="text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
              实时查看试卷，双栏布局即时展示
            </p>
          </div>
        </div>

        {/* 底部信息 */}
        <div className="mt-16 text-sm" style={{ color: 'var(--text-secondary)' }}>
          基于 FastAPI + LangGraph + DeepSeek LLM 构建
        </div>
      </div>
    </div>
  );
}
