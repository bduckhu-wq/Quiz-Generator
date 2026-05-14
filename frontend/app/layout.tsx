import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'AI 出题助手',
  description: '智能对话生成试卷',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  )
}
