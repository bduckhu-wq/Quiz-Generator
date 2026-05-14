'use client';

import { useEffect, useRef } from 'react';
import katex from 'katex';
import 'katex/dist/katex.min.css';

interface MathRendererProps {
  content: string;
  className?: string;
  style?: React.CSSProperties;
}

/**
 * 数学公式渲染组件
 * 支持 LaTeX 公式渲染（行内和独立）
 */
export default function MathRenderer({ content, className = '', style }: MathRendererProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    try {
      // 渲染数学公式
      const rendered = renderMath(content);
      containerRef.current.innerHTML = rendered;
    } catch (error) {
      console.error('数学公式渲染失败:', error);
      // 失败时显示原始内容
      containerRef.current.textContent = content;
    }
  }, [content]);

  return (
    <div
      ref={containerRef}
      className={`math-content ${className}`}
      style={style}
    />
  );
}

/**
 * 渲染数学公式
 * 支持以下格式：
 * - \(...\) 或 $...$ : 行内公式
 * - \[...\] 或 $$...$$ : 独立公式
 * - \\(...\\) : 转义的 LaTeX
 */
function renderMath(text: string): string {
  if (!text) return '';

  let result = text;

  // 1. 处理独立公式 \[...\] 或 $$...$$
  result = result.replace(/\\\[(.*?)\\\]/gs, (match, latex) => {
    try {
      return `<div class="math-block">${katex.renderToString(latex.trim(), { displayMode: true, throwOnError: false })}</div>`;
    } catch (e) {
      return match;
    }
  });

  result = result.replace(/\$\$(.*?)\$\$/gs, (match, latex) => {
    try {
      return `<div class="math-block">${katex.renderToString(latex.trim(), { displayMode: true, throwOnError: false })}</div>`;
    } catch (e) {
      return match;
    }
  });

  // 2. 处理行内公式 \(...\) 或 $...$
  result = result.replace(/\\\((.*?)\\\)/g, (match, latex) => {
    try {
      return katex.renderToString(latex.trim(), { displayMode: false, throwOnError: false });
    } catch (e) {
      return match;
    }
  });

  result = result.replace(/\$(.*?)\$/g, (match, latex) => {
    try {
      return katex.renderToString(latex.trim(), { displayMode: false, throwOnError: false });
    } catch (e) {
      return match;
    }
  });

  // 3. 处理 Markdown 风格的数学公式（豆包输出的格式）
  // 如：x^2/a^2 + y^2/b^2 = 1 (a>b>0)
  // 尝试识别常见数学表达式并转换

  return result;
}
