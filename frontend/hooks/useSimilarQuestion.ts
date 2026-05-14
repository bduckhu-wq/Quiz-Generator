import { useState } from 'react';
import { generateSimilarQuestions, regenerateSingleQuestion } from '@/lib/api/similarQuestion';

export function useSimilarQuestion() {
  const [originalImage, setOriginalImage] = useState<File | null>(null);
  const [ocrResult, setOcrResult] = useState<any>(null);
  const [similarQuestions, setSimilarQuestions] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleUpload = async (file: File, count: number = 3) => {
    console.log('[useSimilarQuestion] 开始上传', { fileName: file.name, size: file.size, count });

    setOriginalImage(file);
    setIsLoading(true);
    setProgress(10);
    setSimilarQuestions([]); // 清空之前的结果

    try {
      // 模拟进度更新
      const progressInterval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 90) return prev;
          return prev + Math.random() * 10;
        });
      }, 2000);

      console.log('[useSimilarQuestion] 调用 API...');
      const result = await generateSimilarQuestions(file, count);
      console.log('[useSimilarQuestion] API 返回结果', result);

      clearInterval(progressInterval);
      setProgress(100);

      setOcrResult(result.ocr_result);
      setSimilarQuestions(result.similar_questions);

      console.log('[useSimilarQuestion] 状态更新完成', {
        ocrResult: result.ocr_result,
        questionCount: result.similar_questions.length
      });

      // 完成后重置进度
      setTimeout(() => setProgress(0), 500);
    } catch (error: any) {
      console.error('[useSimilarQuestion] 生成失败:', error);
      alert(error.message || '生成失败，请重试');
      setOriginalImage(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegenerate = async (index: number) => {
    if (!ocrResult) return;

    try {
      const newQuestion = await regenerateSingleQuestion(
        ocrResult.question,
        index + 1
      );

      setSimilarQuestions((prev) => {
        const updated = [...prev];
        updated[index] = newQuestion;
        return updated;
      });
    } catch (error: any) {
      console.error('重新生成失败:', error);
      alert(error.message || '重新生成失败，请重试');
    }
  };

  const handleEdit = (index: number, data: any) => {
    setSimilarQuestions((prev) => {
      const updated = [...prev];
      updated[index] = { ...updated[index], ...data };
      return updated;
    });
  };

  const handleDelete = (index: number) => {
    if (similarQuestions.length === 1) {
      alert('至少保留一道题目');
      return;
    }
    setSimilarQuestions((prev) => prev.filter((_, i) => i !== index));
  };

  const handleExport = async (type: 'word' | 'add') => {
    if (type === 'word') {
      // TODO: 实现 Word 导出
      alert('Word 导出功能开发中...');
    } else {
      // TODO: 实现加入试卷
      alert('加入试卷功能开发中...');
    }
  };

  return {
    originalImage,
    setOriginalImage,
    ocrResult,
    similarQuestions,
    isLoading,
    progress,
    handleUpload,
    handleRegenerate,
    handleEdit,
    handleDelete,
    handleExport,
  };
}
