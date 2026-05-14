// 时间格式化
export function formatTime(timestamp: number): string {
  const date = new Date(timestamp);
  const now = new Date();

  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);

  if (diffMins < 1) return '刚刚';
  if (diffMins < 60) return `${diffMins}分钟前`;
  if (diffHours < 24) return `${diffHours}小时前`;

  return date.toLocaleString('zh-CN', {
    month: 'numeric',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

// 解析选项（兼容字符串和数组）
export function parseOptions(options: string | string[] | undefined): string[] {
  if (!options) return [];
  if (Array.isArray(options)) return options;

  try {
    return JSON.parse(options);
  } catch {
    return [];
  }
}
