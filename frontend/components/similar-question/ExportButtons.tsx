'use client';

interface ExportButtonsProps {
  onExport: (type: 'word' | 'add') => void;
  questionCount: number;
}

export default function ExportButtons({ onExport, questionCount }: ExportButtonsProps) {
  return (
    <div className="flex gap-2">
      <button
        onClick={() => onExport('word')}
        className="btn-primary text-sm px-4 py-2 flex items-center gap-2"
      >
        <span>📄</span>
        <span>导出 Word</span>
      </button>
      <button
        onClick={() => onExport('add')}
        className="btn-secondary text-sm px-4 py-2 flex items-center gap-2"
      >
        <span>➕</span>
        <span>加入试卷</span>
      </button>
      <span className="text-sm px-3 py-2 rounded" style={{ background: 'var(--bg-tertiary)', color: 'var(--text-secondary)' }}>
        共 {questionCount} 道题
      </span>
    </div>
  );
}
