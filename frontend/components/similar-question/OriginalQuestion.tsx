'use client';

import Image from 'next/image';
import { useState, useEffect } from 'react';
import MathRenderer from '../MathRenderer';

interface OriginalQuestionProps {
  image: File;
  ocrResult: {
    question: string;
    confidence?: number;
  } | null;
  onReupload: () => void;
  onRegenerateAll: () => void;
}

export default function OriginalQuestion({
  image,
  ocrResult,
  onReupload,
  onRegenerateAll,
}: OriginalQuestionProps) {
  const [imageUrl, setImageUrl] = useState<string>('');

  useEffect(() => {
    if (image) {
      const url = URL.createObjectURL(image);
      setImageUrl(url);
      return () => URL.revokeObjectURL(url);
    }
  }, [image]);

  return (
    <div className="p-6 space-y-4">
      {/* 图片预览 */}
      <div className="card-clean overflow-hidden">
        {imageUrl && (
          <div className="relative w-full aspect-[4/3] bg-gray-100">
            <Image
              src={imageUrl}
              alt="原题图片"
              fill
              className="object-contain"
            />
          </div>
        )}
      </div>

      {/* OCR 识别结果 */}
      {ocrResult && (
        <div className="card-clean p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
              原题内容
            </h3>
            {ocrResult.confidence && (
              <span className="text-xs px-2 py-1 rounded" style={{ background: 'var(--bg-tertiary)', color: 'var(--text-secondary)' }}>
                识别准确度 {Math.round(ocrResult.confidence * 100)}%
              </span>
            )}
          </div>
          <MathRenderer
            content={ocrResult.question}
            className="text-sm whitespace-pre-wrap leading-relaxed"
            style={{ color: 'var(--text-primary)' }}
          />
        </div>
      )}

      {/* 操作按钮 */}
      <div className="space-y-2">
        <button
          onClick={onRegenerateAll}
          className="btn-primary w-full text-sm"
        >
          🔄 全部重新生成
        </button>
        <button
          onClick={onReupload}
          className="btn-secondary w-full text-sm"
        >
          📸 重新上传
        </button>
      </div>

      {/* 提示信息 */}
      <div className="text-xs p-3 rounded" style={{ background: 'var(--bg-tertiary)', color: 'var(--text-secondary)' }}>
        <p className="mb-1">💡 提示：</p>
        <ul className="list-disc list-inside space-y-1">
          <li>相似题保持核心知识点不变</li>
          <li>场景和数值会有变化</li>
          <li>可单独编辑或重新生成</li>
        </ul>
      </div>
    </div>
  );
}
