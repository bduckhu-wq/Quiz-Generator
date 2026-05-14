# 前端搭建指南

> **版本**: v1.0  
> **日期**: 2026-04-28  
> **后端状态**: ✅ 生产就绪（160道题库 + 完整API）

---

## ✅ 后端已完成清单

### 核心功能
- [x] LLM智能路由（语义理解用户意图）
- [x] 参数自动提取（学科/年级/章节/知识点/题量）
- [x] 智能追问（参数不完整时）
- [x] 场景自适应（课后作业/单元测验/期中期末/考前复习）
- [x] 混合出题（题库搜索 + AI生成补充）
- [x] 知识点模糊匹配
- [x] 试卷智能组装
- [x] Session管理（会话持久化）

### 数据规模
- 总题目：160道
  - 三年级数学：60道（8章节 × 20知识点）
  - 初二数学：50道
  - 初二物理：50道
- 支持年级：小学1-6年级 + 初中1-3年级 + 高中1-3年级
- 题型：18种（单选、填空、计算、应用、证明等）

### API接口（已测试通过）
```bash
# 1. 健康检查
GET http://localhost:8000/health

# 2. 创建会话
POST http://localhost:8000/api/session/create

# 3. 生成试卷（非流式）
POST http://localhost:8000/api/exam/generate
{
  "user_input": "三年级数学第三章第二节课后练习5题",
  "session_id": "xxx" // 可选
}

# 4. 生成试卷（SSE流式）
POST http://localhost:8000/api/exam/generate/stream
{
  "user_input": "帮我出份初二数学关于一元二次方程的试卷",
  "session_id": "xxx" // 可选
}

# 5. 获取会话
GET http://localhost:8000/api/session/{session_id}

# 6. 删除会话
DELETE http://localhost:8000/api/session/{session_id}
```

---

## 🎨 前端技术栈建议

### 推荐方案：Next.js + TypeScript + Tailwind CSS

**理由：**
- ✅ 符合PRD中的技术预期
- ✅ TypeScript提供类型安全
- ✅ Tailwind CSS快速开发UI
- ✅ 支持SSR（如需SEO优化）
- ✅ 良好的开发体验

### 核心依赖
```json
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.0",              // HTTP请求
    "eventsource": "^2.0.2",        // SSE流式输出
    "@dnd-kit/core": "^6.1.0",      // 拖拽排序
    "katex": "^0.16.9",             // 数学公式渲染
    "react-katex": "^3.0.1",
    "docx": "^8.5.0"                // Word导出
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "@types/react": "^18.2.0",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32"
  }
}
```

---

## 📂 前端目录结构建议

```
frontend/
├── public/
│   └── favicon.ico
├── src/
│   ├── app/                          # Next.js 14 App Router
│   │   ├── page.tsx                  # 首页（欢迎页）
│   │   ├── chat/
│   │   │   └── page.tsx              # 对话页（核心功能）
│   │   ├── layout.tsx                # 根布局
│   │   └── globals.css               # 全局样式
│   │
│   ├── components/                   # 组件目录
│   │   ├── chat/
│   │   │   ├── MessageList.tsx       # 对话历史列表
│   │   │   ├── InputBox.tsx          # 输入框
│   │   │   └── ThinkingIndicator.tsx # AI思考动画
│   │   │
│   │   ├── exam/
│   │   │   ├── ParameterPanel.tsx    # 参数确认面板
│   │   │   ├── ExamPreview.tsx       # 试卷预览
│   │   │   ├── QuestionCard.tsx      # 单题卡片
│   │   │   ├── QuestionEditor.tsx    # 题目编辑器
│   │   │   └── ExportButton.tsx      # 导出按钮
│   │   │
│   │   └── common/
│   │       ├── Header.tsx            # 页头
│   │       └── Loading.tsx           # 加载动画
│   │
│   ├── lib/                          # 工具函数
│   │   ├── api.ts                    # API封装
│   │   ├── types.ts                  # TypeScript类型定义
│   │   ├── sseClient.ts              # SSE客户端
│   │   └── exportExam.ts             # 导出功能
│   │
│   ├── hooks/                        # 自定义Hooks
│   │   ├── useChat.ts                # 对话管理
│   │   ├── useExam.ts                # 试卷管理
│   │   └── useSession.ts             # 会话管理
│   │
│   └── styles/
│       └── exam.module.css           # 试卷样式
│
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

---

## 🔧 核心功能实现指引

### 1. 对话页布局（双栏）

```tsx
// src/app/chat/page.tsx
export default function ChatPage() {
  return (
    <div className="flex h-screen">
      {/* 左侧：对话区 */}
      <div className="w-1/2 flex flex-col border-r">
        <MessageList messages={messages} />
        <InputBox onSend={handleSend} />
      </div>

      {/* 右侧：试卷预览区 */}
      <div className="w-1/2 overflow-y-auto">
        {exam ? (
          <ExamPreview exam={exam} onEdit={handleEdit} />
        ) : (
          <div className="flex items-center justify-center h-full text-gray-400">
            发送出题需求开始生成试卷
          </div>
        )}
      </div>
    </div>
  );
}
```

---

### 2. SSE流式输出接收

```typescript
// src/lib/sseClient.ts
export async function streamGenerate(
  userInput: string,
  sessionId: string,
  onProgress: (event: SSEEvent) => void
) {
  const response = await fetch('http://localhost:8000/api/exam/generate/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_input: userInput, session_id: sessionId })
  });

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader!.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split('\n');

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = JSON.parse(line.slice(6));
        onProgress(data);

        if (data.type === 'done') {
          return;
        }
      }
    }
  }
}

// 使用示例
streamGenerate(userInput, sessionId, (event) => {
  switch (event.type) {
    case 'session':
      setSessionId(event.session_id);
      break;
    case 'progress':
      setProgress(event.message);
      break;
    case 'followup':
      addMessage({ role: 'assistant', content: event.message });
      break;
    case 'exam':
      setExam(event.exam);
      break;
  }
});
```

---

### 3. 参数面板组件

```tsx
// src/components/exam/ParameterPanel.tsx
interface ParameterPanelProps {
  params: ExtractedParams;
  onChange: (params: ExtractedParams) => void;
  onConfirm: () => void;
}

export function ParameterPanel({ params, onChange, onConfirm }: ParameterPanelProps) {
  return (
    <div className="p-4 bg-blue-50 rounded-lg">
      <h3 className="font-bold mb-4">📝 参数确认</h3>

      {/* 学科选择 */}
      <div className="mb-3">
        <label className="block text-sm font-medium mb-1">学科</label>
        <select 
          value={params.subject}
          onChange={(e) => onChange({ ...params, subject: e.target.value })}
          className="w-full border rounded px-3 py-2"
        >
          <option value="数学">数学</option>
          <option value="物理">物理</option>
          <option value="化学">化学</option>
        </select>
      </div>

      {/* 年级选择 */}
      <div className="mb-3">
        <label className="block text-sm font-medium mb-1">年级</label>
        <select 
          value={params.grade}
          onChange={(e) => onChange({ ...params, grade: e.target.value })}
          className="w-full border rounded px-3 py-2"
        >
          <option value="三年级">三年级</option>
          <option value="初二">初二</option>
          <option value="高一">高一</option>
        </select>
      </div>

      {/* 知识点输入 */}
      <div className="mb-3">
        <label className="block text-sm font-medium mb-1">知识点</label>
        <input
          type="text"
          value={params.knowledge_points?.join(', ')}
          onChange={(e) => onChange({ 
            ...params, 
            knowledge_points: e.target.value.split(',').map(s => s.trim())
          })}
          className="w-full border rounded px-3 py-2"
          placeholder="如：一元二次方程, 函数"
        />
      </div>

      {/* 难度滑块 */}
      <div className="mb-3">
        <label className="block text-sm font-medium mb-1">
          难度分布（简单 / 中等 / 困难）
        </label>
        <div className="flex gap-2">
          <input type="range" min="0" max="10" className="flex-1" />
          <input type="range" min="0" max="10" className="flex-1" />
          <input type="range" min="0" max="10" className="flex-1" />
        </div>
      </div>

      {/* 题量 */}
      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">题目数量</label>
        <input
          type="number"
          value={params.question_count || 12}
          onChange={(e) => onChange({ ...params, question_count: parseInt(e.target.value) })}
          className="w-full border rounded px-3 py-2"
        />
      </div>

      <button
        onClick={onConfirm}
        className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
      >
        确认并生成
      </button>
    </div>
  );
}
```

---

### 4. 试卷预览组件

```tsx
// src/components/exam/ExamPreview.tsx
interface ExamPreviewProps {
  exam: Exam;
  onEdit?: (questionId: string) => void;
}

export function ExamPreview({ exam, onEdit }: ExamPreviewProps) {
  return (
    <div className="p-6">
      {/* 试卷头 */}
      <div className="mb-6 text-center border-b pb-4">
        <h1 className="text-2xl font-bold">{exam.subject} 试卷</h1>
        <p className="text-gray-600 mt-2">
          {exam.grade} | {exam.knowledge_points.join('、')} | 总分 {exam.total_score}分
        </p>
      </div>

      {/* 题目列表 */}
      <div className="space-y-6">
        {exam.questions.map((q) => (
          <QuestionCard 
            key={q.id} 
            question={q}
            onEdit={() => onEdit?.(q.id)}
          />
        ))}
      </div>

      {/* 导出按钮 */}
      <div className="mt-8 flex gap-4 justify-center">
        <ExportButton exam={exam} withAnswer={true} />
        <ExportButton exam={exam} withAnswer={false} />
      </div>
    </div>
  );
}
```

---

### 5. 单题卡片组件

```tsx
// src/components/exam/QuestionCard.tsx
interface QuestionCardProps {
  question: Question;
  onEdit?: () => void;
}

export function QuestionCard({ question, onEdit }: QuestionCardProps) {
  return (
    <div className="border rounded-lg p-4 hover:shadow-md transition">
      {/* 题目头部 */}
      <div className="flex justify-between items-start mb-3">
        <div>
          <span className="font-bold text-lg">第{question.index}题</span>
          <span className="ml-3 text-gray-600">
            [{question.question_type}] {question.difficulty} | {question.score}分
          </span>
        </div>
        {onEdit && (
          <button onClick={onEdit} className="text-blue-600 text-sm">
            编辑
          </button>
        )}
      </div>

      {/* 题目内容（支持LaTeX） */}
      <div className="mb-3">
        <MathContent content={question.content} />
      </div>

      {/* 选项（如果有） */}
      {question.options && (
        <div className="mb-3 space-y-1">
          {JSON.parse(question.options).map((opt: string, idx: number) => (
            <div key={idx} className="pl-4">{opt}</div>
          ))}
        </div>
      )}

      {/* 答案和解析（可折叠） */}
      <details className="mt-3">
        <summary className="cursor-pointer text-sm text-gray-600">
          查看答案和解析
        </summary>
        <div className="mt-2 p-3 bg-gray-50 rounded">
          <p className="mb-2"><strong>答案：</strong>{question.answer}</p>
          {question.analysis && (
            <p><strong>解析：</strong>{question.analysis}</p>
          )}
        </div>
      </details>

      {/* 知识点标签 */}
      <div className="mt-3 flex flex-wrap gap-2">
        {question.knowledge_points?.map((kp, idx) => (
          <span key={idx} className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">
            {kp}
          </span>
        ))}
      </div>
    </div>
  );
}
```

---

### 6. 数学公式渲染

```tsx
// src/components/common/MathContent.tsx
import 'katex/dist/katex.min.css';
import { InlineMath, BlockMath } from 'react-katex';

interface MathContentProps {
  content: string;
}

export function MathContent({ content }: MathContentProps) {
  // 识别LaTeX公式：$...$（行内） 或 $$...$$（块级）
  const parts = content.split(/(\$\$[\s\S]+?\$\$|\$[^\$]+?\$)/g);

  return (
    <div>
      {parts.map((part, idx) => {
        if (part.startsWith('$$') && part.endsWith('$$')) {
          return <BlockMath key={idx} math={part.slice(2, -2)} />;
        } else if (part.startsWith('$') && part.endsWith('$')) {
          return <InlineMath key={idx} math={part.slice(1, -1)} />;
        }
        return <span key={idx}>{part}</span>;
      })}
    </div>
  );
}
```

---

### 7. Word导出功能

```typescript
// src/lib/exportExam.ts
import { Document, Packer, Paragraph, TextRun } from 'docx';

export async function exportToWord(exam: Exam, withAnswer: boolean) {
  const doc = new Document({
    sections: [{
      children: [
        // 标题
        new Paragraph({
          children: [
            new TextRun({
              text: `${exam.subject} 试卷`,
              bold: true,
              size: 32
            })
          ],
          alignment: 'center'
        }),

        // 题目
        ...exam.questions.flatMap(q => [
          new Paragraph({
            children: [
              new TextRun({
                text: `第${q.index}题 [${q.question_type}] ${q.score}分`,
                bold: true
              })
            ]
          }),
          new Paragraph({ text: q.content }),

          // 选项
          ...(q.options ? JSON.parse(q.options).map((opt: string) =>
            new Paragraph({ text: opt })
          ) : []),

          // 答案（如果需要）
          ...(withAnswer ? [
            new Paragraph({ text: '' }),
            new Paragraph({ text: `答案：${q.answer}` }),
            new Paragraph({ text: `解析：${q.analysis || ''}` })
          ] : []),

          new Paragraph({ text: '' }) // 空行
        ])
      ]
    }]
  });

  const blob = await Packer.toBlob(doc);
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${exam.subject}_${exam.grade}_试卷.docx`;
  a.click();
}
```

---

## 🎯 开发步骤建议

### Phase 1: 基础搭建（1天）
1. ✅ 创建Next.js项目
2. ✅ 配置TypeScript + Tailwind CSS
3. ✅ 创建基础页面结构（首页 + 对话页）
4. ✅ 封装API请求函数

```bash
npx create-next-app@latest frontend --typescript --tailwind --app
cd frontend
npm install axios eventsource katex react-katex docx
```

### Phase 2: 对话功能（2天）
1. ✅ 实现对话框组件（MessageList + InputBox）
2. ✅ 集成SSE流式输出
3. ✅ 实现Session管理
4. ✅ 添加加载动画和错误处理

### Phase 3: 参数面板（1天）
1. ✅ 实现参数确认面板
2. ✅ 支持用户修改参数
3. ✅ 参数验证和默认值处理

### Phase 4: 试卷预览（2天）
1. ✅ 实现试卷预览布局
2. ✅ 实现单题卡片组件
3. ✅ 集成LaTeX数学公式渲染
4. ✅ 实现题目编辑功能

### Phase 5: 高级功能（2天）
1. ✅ 实现题目拖拽排序（@dnd-kit）
2. ✅ 实现Word导出功能
3. ✅ 实现单题改编（调用后端API）
4. ✅ 优化UI交互体验

### Phase 6: 测试与优化（1天）
1. ✅ 端到端测试
2. ✅ 性能优化
3. ✅ 响应式适配
4. ✅ 错误边界处理

**总预计时间：9天**

---

## 🔍 前后端联调要点

### 1. 跨域配置（开发环境）

后端已配置CORS：
```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. 环境变量配置

```bash
# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. API Base URL封装

```typescript
// src/lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = {
  createSession: () => 
    axios.post(`${API_BASE}/api/session/create`),

  generateExam: (userInput: string, sessionId?: string) =>
    axios.post(`${API_BASE}/api/exam/generate`, { 
      user_input: userInput, 
      session_id: sessionId 
    }),

  streamGenerate: (userInput: string, sessionId: string, onProgress: Function) =>
    streamSSE(`${API_BASE}/api/exam/generate/stream`, { 
      user_input: userInput, 
      session_id: sessionId 
    }, onProgress)
};
```

---

## 📊 TypeScript类型定义

```typescript
// src/lib/types.ts

// 题目类型
export interface Question {
  id: string;
  index: number;
  question_type: string;
  difficulty: string;
  content: string;
  options?: string[];
  answer: string;
  analysis?: string;
  score: number;
  knowledge_points: string[];
}

// 试卷类型
export interface Exam {
  exam_id: string;
  subject: string;
  grade: string;
  knowledge_points: string[];
  scene: string;
  questions: Question[];
  question_count: number;
  total_score: number;
  source_stats: {
    database: number;
    ai_generated: number;
  };
  created_at: number;
}

// 提取的参数
export interface ExtractedParams {
  subject?: string;
  grade?: string;
  knowledge_points?: string[];
  scene?: string;
  question_count?: number;
}

// SSE事件类型
export type SSEEvent = 
  | { type: 'session'; session_id: string }
  | { type: 'progress'; step: string; message: string }
  | { type: 'followup'; message: string }
  | { type: 'exam'; exam: Exam }
  | { type: 'done' };

// 消息类型
export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
  exam?: Exam;
}
```

---

## ✅ 启动清单

### 启动后端
```bash
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 启动前端（创建后）
```bash
cd frontend
npm run dev
# 访问 http://localhost:3000
```

---

## 🎨 UI/UX建议

### 色彩方案
- 主色：蓝色系（#3B82F6）- 教育、专业
- 辅助色：绿色（成功）、黄色（警告）、红色（错误）
- 背景：白色 + 浅灰（#F9FAFB）

### 交互细节
- ✅ 输入时显示思考动画（"AI正在分析需求..."）
- ✅ 参数面板平滑展开/收起动画
- ✅ 题目卡片hover时轻微上浮效果
- ✅ 拖拽时显示占位符
- ✅ 导出时显示进度提示

### 响应式适配
- 桌面端（≥1024px）：双栏布局
- 平板端（768-1023px）：Tab切换
- 移动端（<768px）：单栏堆叠

---

## 📝 下一步行动

1. **立即可做**：
   ```bash
   cd /Users/pinya_hu/Desktop/tare/AI_quiz_new
   npx create-next-app@latest frontend --typescript --tailwind --app
   ```

2. **参考文档**：
   - 后端API：`DELIVERY.md`（完整API文档）
   - 工作流程：`WORKFLOW_DIAGRAM.md`（业务逻辑）
   - 产品需求：`PRD.md`（用户流程）

3. **测试接口**：
   ```bash
   # 启动后端
   cd backend
   python3 -m uvicorn app.main:app --reload
   
   # 测试接口
   curl http://localhost:8000/health
   ```

---

**状态：✅ 后端完全就绪，前端可以开始开发！**
