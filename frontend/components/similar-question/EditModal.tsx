'use client';

import { useState } from 'react';

interface EditModalProps {
  question: {
    question: string;
    answer: string;
    explanation: string;
  };
  index: number;
  onSave: (data: { question: string; answer: string; explanation: string }) => void;
  onCancel: () => void;
}

export default function EditModal({ question, index, onSave, onCancel }: EditModalProps) {
  const [formData, setFormData] = useState({
    question: question.question,
    answer: question.answer,
    explanation: question.explanation,
  });

  const handleSave = () => {
    if (!formData.question.trim() || !formData.answer.trim() || !formData.explanation.trim()) {
      alert('请填写完整的题目、答案和解析');
      return;
    }
    onSave(formData);
  };

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={onCancel}
    >
      <div
        className="card-clean max-w-3xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* 标题 */}
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
          <h2 className="text-xl font-semibold" style={{ color: 'var(--text-primary)' }}>
            编辑相似题 {index}
          </h2>
          <button
            onClick={onCancel}
            className="text-2xl text-gray-400 hover:text-gray-600"
          >
            ×
          </button>
        </div>

        {/* 表单 */}
        <div className="p-6 space-y-6">
          {/* 题目 */}
          <div>
            <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
              题目内容
            </label>
            <textarea
              value={formData.question}
              onChange={(e) => setFormData({ ...formData, question: e.target.value })}
              className="w-full h-40 p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              style={{ borderColor: 'var(--border-light)' }}
              placeholder="输入题目内容（包含选项）"
            />
          </div>

          {/* 答案 */}
          <div>
            <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
              答案
            </label>
            <input
              type="text"
              value={formData.answer}
              onChange={(e) => setFormData({ ...formData, answer: e.target.value })}
              className="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              style={{ borderColor: 'var(--border-light)' }}
              placeholder="输入答案（如：A 或 具体答案）"
            />
          </div>

          {/* 解析 */}
          <div>
            <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
              解析
            </label>
            <textarea
              value={formData.explanation}
              onChange={(e) => setFormData({ ...formData, explanation: e.target.value })}
              className="w-full h-32 p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              style={{ borderColor: 'var(--border-light)' }}
              placeholder="输入解题步骤和思路"
            />
          </div>
        </div>

        {/* 底部按钮 */}
        <div className="sticky bottom-0 bg-white border-t px-6 py-4 flex gap-3 justify-end">
          <button onClick={onCancel} className="btn-secondary px-6">
            取消
          </button>
          <button onClick={handleSave} className="btn-primary px-6">
            保存
          </button>
        </div>
      </div>
    </div>
  );
}
