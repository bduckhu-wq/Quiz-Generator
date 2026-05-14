# 相似题生成 - 前端开发计划

> **版本**：v1.0  
> **日期**：2026-05-13  
> **状态**：📋 待确认  
> **预计周期**：2-3 天

---

## 📋 开发目标

**交付物**：
- ✅ 相似题生成页面（`/similar-question`）
- ✅ 原题+相似题左右分栏布局
- ✅ 图片上传组件（支持拖拽）
- ✅ 生成进度展示（加载动画）
- ✅ 相似题卡片组件（题目、答案、解析）
- ✅ 单题操作（编辑、重新生成、删除）
- ✅ 导出功能（导出 Word、加入试卷）
- ✅ 响应式布局（移动端适配）

**验收标准**：
- 上传图片 → 显示加载状态 → 展示3道相似题
- 单题编辑功能正常（修改题目、答案、解析）
- 单题重新生成功能正常（调用 `/regenerate` 接口）
- 导出 Word 功能正常（下载 .docx 文件）
- 移动端布局正常（上下布局而非左右分栏）
- UI 风格与现有页面一致（Lab 风格）

---

## 🎨 页面设计方案

### 整体布局

```
┌───────────────────────────────────────────────────────────┐
│  顶部导航栏                                                  │
│  [< 返回首页]    相似题生成    [导出 Word] [加入试卷]          │
├──────────────────┬──────────────────────────────────────────┤
│  原题区（30%）     │  相似题列表（70%）                         │
│                  │                                          │
│  ┌─────────────┐│  ┌────────────────────────────────────┐  │
│  │             ││  │ 相似题 1                            │  │
│  │  原题截图    ││  │ 题目：一个分数的分子扩大到原来的...     │  │
│  │  显示        ││  │ A. 选项1  B. 选项2                  │  │
│  │             ││  │ C. 选项3  D. 选项4                  │  │
│  └─────────────┘│  │                                     │  │
│                  │  │ 答案：A                             │  │
│  原题内容：       │  │ 解析：解题步骤...                    │  │
│  一个分数的分子   │  │                                     │  │
│  扩大到原来的3倍  │  │ [✏️ 编辑] [🔄 重新生成] [🗑️ 删除]    │  │
│  ...             │  └────────────────────────────────────┘  │
│                  │                                          │
│                  │  ┌────────────────────────────────────┐  │
│  生成数量：       │  │ 相似题 2                            │  │
│  [1] [3] [5]     │  │ ...                                 │  │
│                  │  └────────────────────────────────────┘  │
│  [🔄 全部重新生成]│                                          │
│                  │  ┌────────────────────────────────────┐  │
│                  │  │ 相似题 3                            │  │
│                  │  │ ...                                 │  │
│                  │  └────────────────────────────────────┘  │
└──────────────────┴──────────────────────────────────────────┘
```

### 页面状态

**1. 初始状态（未上传图片）**
```
┌────────────────────────────────────┐
│                                    │
│        📸                          │
│                                    │
│   拖拽图片到此处上传                 │
│   或点击选择文件                     │
│                                    │
│   支持 JPG、PNG、HEIC 格式          │
│   最大 10MB                        │
│                                    │
└────────────────────────────────────┘
```

**2. 加载状态（生成中）**
```
┌────────────────────────────────────┐
│  原题截图                           │
│  [显示上传的图片]                   │
│                                    │
│  原题内容：                         │
│  一个分数的分子扩大...              │
│                                    │
├────────────────────────────────────┤
│                                    │
│        ⏳                          │
│                                    │
│   正在生成相似题...                 │
│                                    │
│   已完成 OCR 识别                   │
│   正在生成 3 道相似题 (预计 50 秒)   │
│                                    │
│   [████████░░░░░░░░░░] 40%        │
│                                    │
└────────────────────────────────────┘
```

**3. 完成状态（显示结果）**
```
[如上面整体布局所示]
```

---

## 📁 文件结构

```
frontend/
├── app/
│   └── similar-question/
│       └── page.tsx              # 相似题生成页面（新增）
│
├── components/
│   └── similar-question/        # 相似题组件目录（新增）
│       ├── ImageUpload.tsx      # 图片上传组件
│       ├── OriginalQuestion.tsx # 原题展示组件
│       ├── SimilarQuestionCard.tsx # 相似题卡片组件
│       ├── LoadingState.tsx     # 加载状态组件
│       ├── EditModal.tsx        # 编辑弹窗组件
│       └── ExportButtons.tsx    # 导出按钮组件
│
├── hooks/
│   └── useSimilarQuestion.ts    # 相似题逻辑 Hook（新增）
│
└── lib/
    └── api/
        └── similarQuestion.ts   # 相似题 API 封装（新增）
```

---

## 💻 核心代码设计

### 1. 页面主组件

**文件**：`app/similar-question/page.tsx`

```tsx
'use client';

import { useState } from 'react';
import { useSimilarQuestion } from '@/hooks/useSimilarQuestion';
import ImageUpload from '@/components/similar-question/ImageUpload';
import OriginalQuestion from '@/components/similar-question/OriginalQuestion';
import SimilarQuestionCard from '@/components/similar-question/SimilarQuestionCard';
import LoadingState from '@/components/similar-question/LoadingState';
import ExportButtons from '@/components/similar-question/ExportButtons';

export default function SimilarQuestionPage() {
  const {
    originalImage,
    ocrResult,
    similarQuestions,
    isLoading,
    progress,
    handleUpload,
    handleRegenerate,
    handleEdit,
    handleDelete,
    handleExport
  } = useSimilarQuestion();

  return (
    <div className="min-h-screen" style={{ background: 'var(--bg-secondary)' }}>
      {/* 顶部导航栏 */}
      <header className="border-b" style={{ background: 'var(--bg-primary)', borderColor: 'var(--border-light)' }}>
        <div className="px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button onClick={() => router.back()} className="text-sm hover:underline">
              ← 返回首页
            </button>
            <h1 className="text-xl font-semibold">相似题生成</h1>
          </div>

          {similarQuestions.length > 0 && (
            <ExportButtons onExport={handleExport} />
          )}
        </div>
      </header>

      {/* 主内容区 */}
      <div className="flex flex-col md:flex-row h-[calc(100vh-73px)]">
        {/* 左侧：原题区 */}
        <div className="w-full md:w-[30%] border-r overflow-y-auto" style={{ background: 'var(--bg-primary)', borderColor: 'var(--border-light)' }}>
          {!originalImage ? (
            <ImageUpload onUpload={handleUpload} />
          ) : (
            <OriginalQuestion
              image={originalImage}
              ocrResult={ocrResult}
              onReupload={() => setOriginalImage(null)}
              onRegenerateAll={() => handleUpload(originalImage)}
            />
          )}
        </div>

        {/* 右侧：相似题列表 */}
        <div className="w-full md:w-[70%] overflow-y-auto p-6" style={{ background: 'var(--bg-secondary)' }}>
          {isLoading ? (
            <LoadingState progress={progress} />
          ) : similarQuestions.length > 0 ? (
            <div className="space-y-4">
              {similarQuestions.map((question, index) => (
                <SimilarQuestionCard
                  key={question.id || index}
                  question={question}
                  index={index + 1}
                  onEdit={(data) => handleEdit(index, data)}
                  onRegenerate={() => handleRegenerate(index)}
                  onDelete={() => handleDelete(index)}
                />
              ))}
            </div>
          ) : (
            <div className="flex items-center justify-center h-full text-center">
              <div>
                <span className="text-6xl mb-4 block">📝</span>
                <p className="text-lg" style={{ color: 'var(--text-secondary)' }}>
                  上传原题图片，开始生成相似题
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
```

---

### 2. 图片上传组件

**文件**：`components/similar-question/ImageUpload.tsx`

```tsx
'use client';

import { useState, useRef } from 'react';

interface ImageUploadProps {
  onUpload: (file: File) => void;
}

export default function ImageUpload({ onUpload }: ImageUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      onUpload(file);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onUpload(file);
    }
  };

  return (
    <div className="p-6 h-full flex items-center justify-center">
      <div
        className={`card-clean p-8 text-center w-full border-2 border-dashed transition-all cursor-pointer ${
          isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
        }`}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <span className="text-6xl mb-4 block">📸</span>
        <h3 className="text-lg font-semibold mb-2">拖拽图片到此处上传</h3>
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
  );
}
```

---

### 3. 相似题卡片组件

**文件**：`components/similar-question/SimilarQuestionCard.tsx`

```tsx
'use client';

import { useState } from 'react';
import EditModal from './EditModal';

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
  onDelete
}: SimilarQuestionCardProps) {
  const [showEditModal, setShowEditModal] = useState(false);
  const [showAnswer, setShowAnswer] = useState(true);

  return (
    <>
      <div className="card-clean p-6">
        {/* 标题 */}
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">相似题 {index}</h3>
          <div className="flex gap-2">
            <button
              onClick={() => setShowEditModal(true)}
              className="btn-secondary text-sm px-3 py-1"
              title="编辑"
            >
              ✏️ 编辑
            </button>
            <button
              onClick={onRegenerate}
              className="btn-secondary text-sm px-3 py-1"
              title="重新生成"
            >
              🔄 重新生成
            </button>
            <button
              onClick={onDelete}
              className="btn-secondary text-sm px-3 py-1 text-red-600"
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
          <div className="whitespace-pre-wrap" style={{ color: 'var(--text-primary)' }}>
            {question.question}
          </div>
        </div>

        {/* 答案 */}
        <div className="mb-4">
          <button
            onClick={() => setShowAnswer(!showAnswer)}
            className="text-sm font-medium mb-2 hover:underline"
            style={{ color: 'var(--text-secondary)' }}
          >
            答案：{showAnswer ? '隐藏' : '显示'}
          </button>
          {showAnswer && (
            <div className="mt-2 p-3 rounded" style={{ background: 'var(--bg-tertiary)' }}>
              {question.answer}
            </div>
          )}
        </div>

        {/* 解析 */}
        <div>
          <div className="text-sm font-medium mb-2" style={{ color: 'var(--text-secondary)' }}>
            解析：
          </div>
          <div className="whitespace-pre-wrap text-sm" style={{ color: 'var(--text-primary)' }}>
            {question.explanation}
          </div>
        </div>
      </div>

      {/* 编辑弹窗 */}
      {showEditModal && (
        <EditModal
          question={question}
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
```

---

### 4. 自定义 Hook

**文件**：`hooks/useSimilarQuestion.ts`

```ts
import { useState } from 'react';
import { generateSimilarQuestions, regenerateSingleQuestion } from '@/lib/api/similarQuestion';

export function useSimilarQuestion() {
  const [originalImage, setOriginalImage] = useState<File | null>(null);
  const [ocrResult, setOcrResult] = useState<any>(null);
  const [similarQuestions, setSimilarQuestions] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleUpload = async (file: File, count: number = 3) => {
    setOriginalImage(file);
    setIsLoading(true);
    setProgress(10);

    try {
      // 模拟进度更新
      const progressInterval = setInterval(() => {
        setProgress((prev) => Math.min(prev + 5, 90));
      }, 2000);

      const result = await generateSimilarQuestions(file, count);

      clearInterval(progressInterval);
      setProgress(100);

      setOcrResult(result.ocr_result);
      setSimilarQuestions(result.similar_questions);
    } catch (error) {
      console.error('生成失败:', error);
      alert('生成失败，请重试');
    } finally {
      setIsLoading(false);
      setProgress(0);
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
    } catch (error) {
      console.error('重新生成失败:', error);
      alert('重新生成失败，请重试');
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
    setSimilarQuestions((prev) => prev.filter((_, i) => i !== index));
  };

  const handleExport = async (format: 'word' | 'add') => {
    // TODO: 实现导出逻辑
    console.log('导出格式:', format);
  };

  return {
    originalImage,
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
```

---

### 5. API 封装

**文件**：`lib/api/similarQuestion.ts`

```ts
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
    throw new Error('生成失败');
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
    throw new Error('重新生成失败');
  }

  return response.json();
}
```

---

## 📅 开发任务清单

### Day 1：基础页面 + 组件

- [ ] 创建页面路由 `app/similar-question/page.tsx`
- [ ] 实现 ImageUpload 组件（拖拽上传）
- [ ] 实现 OriginalQuestion 组件（原题展示）
- [ ] 实现 LoadingState 组件（加载状态）
- [ ] 测试图片上传流程

### Day 2：相似题展示 + 交互

- [ ] 实现 SimilarQuestionCard 组件（题目卡片）
- [ ] 实现 EditModal 组件（编辑弹窗）
- [ ] 实现 useSimilarQuestion Hook（核心逻辑）
- [ ] 实现 API 封装（`lib/api/similarQuestion.ts`）
- [ ] 测试完整流程（上传 → 生成 → 编辑）

### Day 3：导出功能 + 优化

- [ ] 实现 ExportButtons 组件（导出按钮）
- [ ] 实现导出 Word 功能（调用后端接口或前端生成）
- [ ] 实现"加入试卷"功能（与现有试卷集成）
- [ ] 响应式布局优化（移动端适配）
- [ ] 错误处理优化（网络错误、超时等）
- [ ] 测试完整功能

---

## ✅ 验收标准

### 功能验收
- [ ] 图片上传功能正常（拖拽 + 点击）
- [ ] 上传后显示加载状态（进度条）
- [ ] 生成成功后展示 3 道相似题
- [ ] 单题编辑功能正常（弹窗编辑）
- [ ] 单题重新生成功能正常
- [ ] 单题删除功能正常
- [ ] 导出 Word 功能正常
- [ ] 加入试卷功能正常（与现有功能集成）

### UI/UX 验收
- [ ] 页面风格与现有页面一致（Lab 风格）
- [ ] 加载状态清晰（进度提示）
- [ ] 响应式布局正常（PC + 移动端）
- [ ] 交互流畅（按钮反馈、动画过渡）
- [ ] 错误提示友好

### 技术验收
- [ ] 代码结构清晰（组件拆分合理）
- [ ] TypeScript 类型完整
- [ ] 无 console 警告/错误
- [ ] API 调用正确（正确处理成功/失败）

---

## 🚀 启动命令

```bash
# 1. 启动后端服务
cd backend
uvicorn app.main:app --reload

# 2. 启动前端服务
cd frontend
npm run dev

# 3. 访问页面
http://localhost:3000/similar-question
```

---

## 📝 注意事项

### 1. 与现有代码集成

- **样式复用**：使用现有的 CSS 变量（`var(--text-primary)` 等）
- **组件复用**：复用 `InputBox`、`ThinkingIndicator` 等组件
- **路由导航**：在首页添加"相似题生成"入口

### 2. 性能优化

- 图片上传前压缩（前端压缩至 <2MB）
- 加载状态使用骨架屏或进度条
- 列表渲染使用虚拟滚动（如题目数量 >10）

### 3. 错误处理

- 网络错误：显示重试按钮
- 超时错误：提示"生成时间较长，请稍候"
- 文件格式错误：上传前校验
- API 错误：显示具体错误信息

### 4. 移动端适配

- 小屏设备：左右分栏改为上下布局
- 触摸交互：按钮区域足够大（≥44px）
- 图片上传：支持相机拍照

---

## 🔗 相关文档

- **PRD**：`docs/product/similar-question-prd.md`
- **API 文档**：`docs/reference/similar-question-api.md`
- **后端完成总结**：`backend/workflows/similar_question_workflow/COMPLETE.md`

---

**维护者**：前端团队  
**最后更新**：2026-05-13
