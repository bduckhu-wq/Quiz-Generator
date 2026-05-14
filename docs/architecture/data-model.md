# AI 出题助手 - 数据模型定义

> **版本**：v1.0 | **日期**：2026-04-28

---

## 1. Question（题目）

```typescript
interface Question {
  id: string;
  index: number;
  type: QuestionType;
  difficulty: Difficulty;
  score: number;
  content: string;
  options?: Option[];
  answer: string;
  analysis?: string;
  knowledgePoints: string[];
  source: "database" | "ai_generated";
}
```

---

## 2. Exam（试卷）

```typescript
interface Exam {
  id: string;
  title: string;
  subject: string;
  grade: string;
  scene: ExamScene;
  questions: Question[];
  metadata: ExamMetadata;
  createdAt: string;
}
```

---

## 3. Session（会话）

```typescript
interface Session {
  id: string;
  messages: Message[];
  extractedParams: Record<string, any>;
  currentExam?: Exam;
  createdAt: string;
  updatedAt: string;
}
```

---

详细数据模型待补充。

**文档维护者**：数据团队  
**最后更新**：2026-04-28
