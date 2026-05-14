'use client';

import { useState } from 'react';

export default function TestAPIPage() {
  const [result, setResult] = useState<string>('');
  const [loading, setLoading] = useState(false);

  const testAPI = async () => {
    setLoading(true);
    setResult('正在测试...');

    try {
      // 测试健康检查
      const healthRes = await fetch('http://localhost:8000/health');
      const healthData = await healthRes.json();
      setResult(`✅ 健康检查成功: ${JSON.stringify(healthData)}\n\n`);

      // 测试图片上传
      const fileInput = document.getElementById('testFile') as HTMLInputElement;
      if (!fileInput.files || !fileInput.files[0]) {
        setResult((prev) => prev + '❌ 请先选择图片');
        return;
      }

      const formData = new FormData();
      formData.append('image', fileInput.files[0]);

      setResult((prev) => prev + '正在上传图片并生成...\n');

      const uploadRes = await fetch('http://localhost:8000/api/similar-question/generate?count=1', {
        method: 'POST',
        body: formData,
      });

      if (!uploadRes.ok) {
        const errorData = await uploadRes.json().catch(() => ({ detail: '未知错误' }));
        throw new Error(`HTTP ${uploadRes.status}: ${JSON.stringify(errorData)}`);
      }

      const uploadData = await uploadRes.json();
      setResult((prev) => prev + `\n✅ 生成成功:\n${JSON.stringify(uploadData, null, 2)}`);
    } catch (error: any) {
      setResult((prev) => prev + `\n\n❌ 错误: ${error.message}\n${error.stack}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '40px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>API 测试页面</h1>

      <div style={{ marginTop: '20px' }}>
        <input type="file" id="testFile" accept="image/*" />
        <br /><br />
        <button
          onClick={testAPI}
          disabled={loading}
          style={{
            padding: '10px 20px',
            background: loading ? '#ccc' : '#4CAF50',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer',
          }}
        >
          {loading ? '测试中...' : '开始测试'}
        </button>
      </div>

      <div
        style={{
          marginTop: '20px',
          padding: '20px',
          background: '#f5f5f5',
          borderRadius: '4px',
          whiteSpace: 'pre-wrap',
          maxHeight: '400px',
          overflow: 'auto',
          fontFamily: 'monospace',
          fontSize: '12px',
        }}
      >
        {result || '点击"开始测试"按钮'}
      </div>
    </div>
  );
}
