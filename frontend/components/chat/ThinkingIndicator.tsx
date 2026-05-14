export function ThinkingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="max-w-[75%]">
        <div className="flex items-center gap-2 mb-2">
          <div
            className="avatar-circle"
            style={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white'
            }}
          >
            AI
          </div>
        </div>

        <div className="message-bubble-ai flex items-center gap-3">
          <div className="loading-dots">
            <div className="loading-dot" />
            <div className="loading-dot" />
            <div className="loading-dot" />
          </div>
          <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>
            AI正在思考...
          </span>
        </div>
      </div>
    </div>
  );
}
