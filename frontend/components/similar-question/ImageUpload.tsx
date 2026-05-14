'use client';

import { useState, useRef } from 'react';

interface ImageUploadProps {
  onUpload: (file: File, count?: number) => void;
}

export default function ImageUpload({ onUpload }: ImageUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedCount, setSelectedCount] = useState(3);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      onUpload(file, selectedCount);
    } else {
      alert('请上传图片文件（JPG、PNG、HEIC）');
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onUpload(file, selectedCount);
    }
  };

  return (
    <div className="p-6 h-full flex flex-col">
      <div className="flex-1 flex items-center justify-center">
        <div
          className={`card-clean p-8 text-center w-full border-2 border-dashed transition-all cursor-pointer ${
            isDragging ? 'border-blue-500 bg-blue-50' : ''
          }`}
          style={{ borderColor: isDragging ? '#3b82f6' : 'var(--border-light)' }}
          onDragOver={(e) => {
            e.preventDefault();
            setIsDragging(true);
          }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <span className="text-6xl mb-4 block">📸</span>
          <h3 className="text-lg font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>
            拖拽图片到此处上传
          </h3>
          <p className="text-sm mb-4" style={{ color: 'var(--text-secondary)' }}>
            或点击选择文件
          </p>
          <p className="text-xs" style={{ color: 'var(--text-tertiary)' }}>
            支持 JPG、PNG、HEIC 格式，最大 10MB
          </p>

          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={handleFileSelect}
          />
        </div>
      </div>

      {/* 生成数量选择 */}
      <div className="mt-6 card-clean p-4">
        <label className="text-sm font-medium mb-3 block" style={{ color: 'var(--text-primary)' }}>
          生成数量
        </label>
        <div className="flex gap-3">
          {[1, 3, 5, 10].map((count) => (
            <button
              key={count}
              onClick={(e) => {
                e.stopPropagation();
                setSelectedCount(count);
              }}
              className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-all ${
                selectedCount === count
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {count} 道
            </button>
          ))}
        </div>
        <p className="text-xs mt-3" style={{ color: 'var(--text-tertiary)' }}>
          💡 生成 {selectedCount} 道题预计耗时：
          {selectedCount === 1 ? '~20秒' : selectedCount === 3 ? '~50秒' : selectedCount === 5 ? '~80秒' : '~150秒'}
        </p>
      </div>
    </div>
  );
}
