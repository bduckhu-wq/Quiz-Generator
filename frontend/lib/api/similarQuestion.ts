const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function generateSimilarQuestions(file: File, count: number = 3) {
  const formData = new FormData();
  formData.append('image', file);

  const response = await fetch(
    `${API_BASE_URL}/api/similar-question/generate?count=${count}`,
    {
      method: 'POST',
      body: formData,
    }
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '生成失败' }));
    throw new Error(error.detail || '生成失败');
  }

  return response.json();
}

export async function regenerateSingleQuestion(
  originalQuestion: string,
  questionIndex: number
) {
  const response = await fetch(
    `${API_BASE_URL}/api/similar-question/regenerate`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        original_question: originalQuestion,
        question_index: questionIndex,
      }),
    }
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '重新生成失败' }));
    throw new Error(error.detail || '重新生成失败');
  }

  return response.json();
}
