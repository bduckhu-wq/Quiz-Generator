'use client';

interface LoadingStateProps {
  progress: number;
}

export default function LoadingState({ progress }: LoadingStateProps) {
  // 根据进度显示不同状态
  const getStatusText = () => {
    if (progress < 20) return '正在识别原题...';
    if (progress < 40) return '✅ OCR 识别完成';
    if (progress < 90) return '正在生成相似题...';
    return '正在校验题目...';
  };

  const getStatusIcon = () => {
    if (progress < 20) return '📸';
    if (progress < 40) return '✅';
    if (progress < 90) return '✨';
    return '🔍';
  };

  return (
    <div className="flex items-center justify-center h-full">
      <div className="text-center max-w-md">
        {/* 图标 */}
        <div className="mb-6">
          <span className="text-6xl animate-pulse">{getStatusIcon()}</span>
        </div>

        {/* 状态文字 */}
        <h3 className="text-xl font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>
          {getStatusText()}
        </h3>

        {/* 进度条 */}
        <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden mb-4">
          <div
            className="h-full bg-blue-500 transition-all duration-500 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>

        {/* 进度百分比 */}
        <p className="text-sm mb-6" style={{ color: 'var(--text-secondary)' }}>
          {progress}%
        </p>

        {/* 详细状态 */}
        <div className="card-clean p-4 text-left">
          <div className="space-y-2 text-sm">
            <div className="flex items-center gap-2">
              <span>{progress >= 20 ? '✅' : '⏳'}</span>
              <span style={{ color: progress >= 20 ? 'var(--text-primary)' : 'var(--text-secondary)' }}>
                OCR 识别原题
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span>{progress >= 40 ? '✅' : progress >= 20 ? '⏳' : '⬜'}</span>
              <span style={{ color: progress >= 40 ? 'var(--text-primary)' : 'var(--text-secondary)' }}>
                生成相似题
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span>{progress >= 90 ? '✅' : progress >= 40 ? '⏳' : '⬜'}</span>
              <span style={{ color: progress >= 90 ? 'var(--text-primary)' : 'var(--text-secondary)' }}>
                校验题目质量
              </span>
            </div>
          </div>
        </div>

        {/* 温馨提示 */}
        <p className="text-xs mt-4" style={{ color: 'var(--text-tertiary)' }}>
          💡 生成时间约 50-80 秒，请耐心等待
        </p>
      </div>
    </div>
  );
}
