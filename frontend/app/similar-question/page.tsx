'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useSimilarQuestion } from '@/hooks/useSimilarQuestion';
import ImageUpload from '@/components/similar-question/ImageUpload';
import OriginalQuestion from '@/components/similar-question/OriginalQuestion';
import SimilarQuestionCard from '@/components/similar-question/SimilarQuestionCard';
import LoadingState from '@/components/similar-question/LoadingState';
import ExportButtons from '@/components/similar-question/ExportButtons';

export default function SimilarQuestionPage() {
  const router = useRouter();
  const {
    originalImage,
    ocrResult,
    similarQuestions,
    isLoading,
    progress,
    handleUpload,
    handleRegenerate,
    handleEdit,
    handleDelete,
    handleExport,
    setOriginalImage,
  } = useSimilarQuestion();

  return (
    <div className="min-h-screen" style={{ background: 'var(--bg-secondary)' }}>
      {/* 顶部导航栏 */}
      <header className="border-b" style={{ background: 'var(--bg-primary)', borderColor: 'var(--border-light)' }}>
        <div className="px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.push('/')}
              className="text-sm hover:underline"
              style={{ color: 'var(--text-secondary)' }}
            >
              ← 返回首页
            </button>
            <h1 className="text-xl font-semibold" style={{ color: 'var(--text-primary)' }}>
              📸 相似题生成
            </h1>
          </div>

          {similarQuestions.length > 0 && (
            <ExportButtons onExport={handleExport} questionCount={similarQuestions.length} />
          )}
        </div>
      </header>

      {/* 主内容区 */}
      <div className="flex flex-col md:flex-row h-[calc(100vh-73px)]">
        {/* 左侧：原题区 */}
        <div
          className="w-full md:w-[30%] border-r overflow-y-auto"
          style={{ background: 'var(--bg-primary)', borderColor: 'var(--border-light)' }}
        >
          {!originalImage ? (
            <ImageUpload onUpload={handleUpload} />
          ) : (
            <OriginalQuestion
              image={originalImage}
              ocrResult={ocrResult}
              onReupload={() => {
                setOriginalImage(null);
              }}
              onRegenerateAll={() => handleUpload(originalImage, 3)}
            />
          )}
        </div>

        {/* 右侧：相似题列表 */}
        <div className="w-full md:w-[70%] overflow-y-auto p-6" style={{ background: 'var(--bg-secondary)' }}>
          {isLoading ? (
            <LoadingState progress={progress} />
          ) : similarQuestions.length > 0 ? (
            <div className="space-y-4">
              {similarQuestions.map((question, index) => (
                <SimilarQuestionCard
                  key={index}
                  question={question}
                  index={index + 1}
                  onEdit={(data) => handleEdit(index, data)}
                  onRegenerate={() => handleRegenerate(index)}
                  onDelete={() => handleDelete(index)}
                />
              ))}
            </div>
          ) : (
            <div className="flex items-center justify-center h-full text-center">
              <div>
                <span className="text-6xl mb-4 block">📝</span>
                <p className="text-lg mb-2" style={{ color: 'var(--text-primary)' }}>
                  上传原题图片，开始生成相似题
                </p>
                <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                  支持 JPG、PNG、HEIC 格式
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
