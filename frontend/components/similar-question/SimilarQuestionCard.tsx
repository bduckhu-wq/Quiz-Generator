'use client';

import { useState } from 'react';
import EditModal from './EditModal';
import MathRenderer from '../MathRenderer';

interface SimilarQuestionCardProps {
  question: {
    question: string;
    answer: string;
    explanation: string;
  };
  index: number;
  onEdit: (data: any) => void;
  onRegenerate: () => void;
  onDelete: () => void;
}

export default function SimilarQuestionCard({
  question,
  index,
  onEdit,
  onRegenerate,
  onDelete,
}: SimilarQuestionCardProps) {
  const [showEditModal, setShowEditModal] = useState(false);
  const [showAnswer, setShowAnswer] = useState(true);
  const [isRegenerating, setIsRegenerating] = useState(false);

  const handleRegenerate = async () => {
    setIsRegenerating(true);
    try {
      await onRegenerate();
    } finally {
      setIsRegenerating(false);
    }
  };

  return (
    <>
      <div className="card-clean p-6">
        {/* 标题 */}
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
            相似题 {index}
          </h3>
          <div className="flex gap-2">
            <button
              onClick={() => setShowEditModal(true)}
              className="btn-secondary text-sm px-3 py-1.5"
              title="编辑"
            >
              ✏️ 编辑
            </button>
            <button
              onClick={handleRegenerate}
              disabled={isRegenerating}
              className="btn-secondary text-sm px-3 py-1.5"
              title="重新生成"
            >
              {isRegenerating ? '⏳ 生成中...' : '🔄 重新生成'}
            </button>
            <button
              onClick={() => {
                if (confirm('确定删除这道题目？')) {
                  onDelete();
                }
              }}
              className="btn-secondary text-sm px-3 py-1.5 text-red-600 hover:bg-red-50"
              title="删除"
            >
              🗑️ 删除
            </button>
          </div>
        </div>

        {/* 题目内容 */}
        <div className="mb-4">
          <div className="text-sm font-medium mb-2" style={{ color: 'var(--text-secondary)' }}>
            题目：
          </div>
          <MathRenderer
            content={question.question}
            className="whitespace-pre-wrap leading-relaxed"
            style={{ color: 'var(--text-primary)' }}
          />
        </div>

        {/* 答案 */}
        <div className="mb-4">
          <button
            onClick={() => setShowAnswer(!showAnswer)}
            className="text-sm font-medium mb-2 hover:underline flex items-center gap-1"
            style={{ color: 'var(--text-secondary)' }}
          >
            <span>答案：</span>
            <span className="text-xs">{showAnswer ? '👁️ 隐藏' : '👁️‍🗨️ 显示'}</span>
          </button>
          {showAnswer && (
            <div className="mt-2 p-3 rounded" style={{ background: 'var(--bg-tertiary)' }}>
              <MathRenderer
                content={question.answer}
                className="leading-relaxed"
                style={{ color: 'var(--text-primary)' }}
              />
            </div>
          )}
        </div>

        {/* 解析 */}
        <div>
          <div className="text-sm font-medium mb-2" style={{ color: 'var(--text-secondary)' }}>
            解析：
          </div>
          <MathRenderer
            content={question.explanation}
            className="whitespace-pre-wrap text-sm leading-relaxed"
            style={{ color: 'var(--text-primary)' }}
          />
        </div>
      </div>

      {/* 编辑弹窗 */}
      {showEditModal && (
        <EditModal
          question={question}
          index={index}
          onSave={(data) => {
            onEdit(data);
            setShowEditModal(false);
          }}
          onCancel={() => setShowEditModal(false)}
        />
      )}
    </>
  );
}
