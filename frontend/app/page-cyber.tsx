'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

export default function CyberHomePage() {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  return (
    <div className="min-h-screen bg-cyber-black relative overflow-hidden cyber-grid">
      {/* 背景动态网格 */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {/* 移动光束 */}
        <div className="absolute top-0 left-1/4 w-px h-full bg-gradient-to-b from-transparent via-cyber-cyan to-transparent opacity-30 animate-pulse" />
        <div className="absolute top-0 right-1/3 w-px h-full bg-gradient-to-b from-transparent via-cyber-magenta to-transparent opacity-20 animate-pulse" style={{ animationDelay: '1s' }} />

        {/* 六边形装饰 */}
        <svg className="absolute top-20 right-20 w-40 h-40 opacity-10" viewBox="0 0 100 100">
          <polygon
            points="50,10 90,30 90,70 50,90 10,70 10,30"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            className="text-cyber-cyan animate-pulse-glow"
          />
        </svg>
        <svg className="absolute bottom-40 left-32 w-32 h-32 opacity-10" viewBox="0 0 100 100">
          <polygon
            points="50,10 90,30 90,70 50,90 10,70 10,30"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            className="text-cyber-magenta"
          />
        </svg>
      </div>

      {/* 主内容 */}
      <div className="relative z-10 max-w-7xl mx-auto px-8 py-20">
        {/* 顶部系统信息栏 */}
        <div className="font-mono text-xs text-cyber-cyan mb-16 flex justify-between items-center">
          <div className="flex gap-6">
            <span className="opacity-50">SYS://EDU_TERMINAL_v2.0</span>
            <span className="opacity-50">LOC://NODE_CN_BJ</span>
            <span className="opacity-50">TIME://{new Date().toLocaleTimeString('en-US', { hour12: false })}</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-cyber-lime animate-pulse" />
            <span className="text-cyber-lime">ONLINE</span>
          </div>
        </div>

        {/* 主标题区 */}
        <div className="holo-panel p-12 mb-16 animate-hologram">
          <div className="text-center">
            {/* 故障标题 */}
            <div className="mb-6">
              <h1
                className="font-display text-7xl md:text-8xl neon-text-cyan glitch mb-4"
                data-text="AI 出题助手"
              >
                AI 出题助手
              </h1>
              <div className="h-1 w-64 mx-auto bg-gradient-to-r from-transparent via-cyber-cyan to-transparent" />
            </div>

            {/* 英文副标题 */}
            <p className="font-mono text-xl text-cyber-magenta mb-8 tracking-widest">
              &lt; INTELLIGENT QUESTION GENERATION SYSTEM /&gt;
            </p>

            {/* 描述文字 */}
            <div className="max-w-2xl mx-auto mb-10">
              <p className="font-body text-lg text-cyan-200 leading-relaxed">
                基于神经网络的<span className="neon-text-lime">自然语言处理引擎</span>，
                通过多轮语义解析，动态生成<span className="neon-text-magenta">高质量试卷</span>。
                混合策略检索 + AI生成，为K12教育提供智能化解决方案。
              </p>
            </div>

            {/* CTA按钮 */}
            <button
              onClick={() => router.push('/chat')}
              className="cyber-btn text-lg px-12 py-4 group"
            >
              <span className="relative z-10 flex items-center gap-3">
                INITIALIZE SESSION
                <svg className="w-6 h-6 transition-transform group-hover:translate-x-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </span>
            </button>

            {/* 系统状态指示器 */}
            <div className="mt-8 flex justify-center gap-8 font-mono text-xs text-cyber-cyan/50">
              <div className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-cyber-lime animate-pulse" />
                <span>NLP ENGINE</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-cyber-cyan animate-pulse" />
                <span>DB ONLINE</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-cyber-magenta animate-pulse" />
                <span>AI READY</span>
              </div>
            </div>
          </div>
        </div>

        {/* 功能模块 - 三栏数据卡 */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          {/* 模块 1 */}
          <div
            className="data-card hex-pattern animate-data-stream"
            data-hex="0xA1"
            style={{ animationDelay: '0.2s' }}
          >
            <div className="flex items-start gap-4">
              <div className="text-4xl neon-text-cyan">⚡</div>
              <div className="flex-1">
                <h3 className="font-display text-xl text-cyber-cyan mb-3">
                  SEMANTIC PARSE
                </h3>
                <p className="font-body text-sm text-gray-400 leading-relaxed mb-4">
                  深度学习语义解析器，自动识别年级、学科、章节、难度等多维度参数向量
                </p>
                <div className="data-tag">NLP CORE</div>
              </div>
            </div>
          </div>

          {/* 模块 2 */}
          <div
            className="data-card hex-pattern animate-data-stream"
            data-hex="0xB2"
            style={{ animationDelay: '0.4s' }}
          >
            <div className="flex items-start gap-4">
              <div className="text-4xl neon-text-magenta">🎯</div>
              <div className="flex-1">
                <h3 className="font-display text-xl text-cyber-magenta mb-3">
                  HYBRID STRATEGY
                </h3>
                <p className="font-body text-sm text-gray-400 leading-relaxed mb-4">
                  数据库检索 + AI神经网络生成，双路径混合策略保障内容质量
                </p>
                <div className="data-tag magenta">DB × AI</div>
              </div>
            </div>
          </div>

          {/* 模块 3 */}
          <div
            className="data-card hex-pattern animate-data-stream"
            data-hex="0xC3"
            style={{ animationDelay: '0.6s' }}
          >
            <div className="flex items-start gap-4">
              <div className="text-4xl neon-text-lime">📊</div>
              <div className="flex-1">
                <h3 className="font-display text-xl text-cyber-lime mb-3">
                  REALTIME STREAM
                </h3>
                <p className="font-body text-sm text-gray-400 leading-relaxed mb-4">
                  SSE实时数据流，全息投影式试卷预览，零延迟响应体验
                </p>
                <div className="data-tag lime">SSE FLOW</div>
              </div>
            </div>
          </div>
        </div>

        {/* 技术栈展示 */}
        <div className="holo-panel p-8 animate-hologram" style={{ animationDelay: '0.8s' }}>
          <div className="font-display text-2xl text-cyber-cyan mb-6 flex items-center gap-3">
            <div className="w-1 h-6 bg-cyber-cyan" />
            TECH_STACK
          </div>

          <div className="grid md:grid-cols-2 gap-12">
            {/* 前端 */}
            <div>
              <div className="font-mono text-sm text-cyber-magenta uppercase mb-4 tracking-wider">
                &gt; FRONTEND_LAYER
              </div>
              <div className="space-y-3">
                {[
                  { name: 'Next.js 14', desc: 'React Meta Framework' },
                  { name: 'TypeScript', desc: 'Type-safe JavaScript' },
                  { name: 'SSE Client', desc: 'Server-Sent Events' },
                  { name: 'Tailwind CSS', desc: 'Utility-first Styling' }
                ].map((item, i) => (
                  <div key={i} className="flex items-center gap-3 group">
                    <div className="w-2 h-2 bg-cyber-cyan group-hover:bg-cyber-lime transition-colors" />
                    <span className="font-body text-cyber-cyan group-hover:text-cyber-lime transition-colors">
                      {item.name}
                    </span>
                    <span className="font-mono text-xs text-gray-500 ml-auto">
                      //{item.desc}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* 后端 */}
            <div>
              <div className="font-mono text-sm text-cyber-lime uppercase mb-4 tracking-wider">
                &gt; BACKEND_LAYER
              </div>
              <div className="space-y-3">
                {[
                  { name: 'FastAPI', desc: 'Async Python Framework' },
                  { name: 'LangGraph', desc: 'Workflow Engine' },
                  { name: 'OpenClaw Skills', desc: 'Agent System' },
                  { name: 'SQLite', desc: 'Question Database' }
                ].map((item, i) => (
                  <div key={i} className="flex items-center gap-3 group">
                    <div className="w-2 h-2 bg-cyber-lime group-hover:bg-cyber-magenta transition-colors" />
                    <span className="font-body text-cyber-lime group-hover:text-cyber-magenta transition-colors">
                      {item.name}
                    </span>
                    <span className="font-mono text-xs text-gray-500 ml-auto">
                      //{item.desc}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* 系统信息 */}
          <div className="mt-8 pt-6 border-t border-cyber-cyan/20 font-mono text-xs text-gray-500 flex justify-between">
            <span>BUILD: #2077.04.28</span>
            <span>ARCH: x64_neural</span>
            <span>PROTOCOL: HTTP/2.0</span>
          </div>
        </div>

        {/* 底部元信息 */}
        <div className="mt-16 font-mono text-xs text-cyber-cyan/30 text-center">
          <div className="mb-2">
            &lt;/&gt; DEVELOPED BY CLAUDE AI · POWERED BY DEEPSEEK LLM
          </div>
          <div>
            VERSION 2.0.2077 · NEURAL NETWORK INTERFACE
          </div>
        </div>
      </div>

      {/* 右下角系统监控 */}
      <div className="fixed bottom-6 right-6 font-mono text-xs text-cyber-cyan/50 text-right">
        <div>MEM: 2.4GB / 8GB</div>
        <div>CPU: 34%</div>
        <div>NET: 124MB/s</div>
      </div>
    </div>
  );
}
