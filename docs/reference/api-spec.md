# AI 出题助手 - API 接口规范

> **版本**：v1.0 | **日期**：2026-04-28  
> **API 版本**：v1  
> **Base URL**：`/api/v1`

---

## 1. 会话管理

### POST /sessions
创建新会话

**Request**:
```json
{}
```

**Response**:
```json
{
  "session_id": "uuid",
  "created_at": "2026-04-28T10:00:00Z"
}
```

---

## 2. 对话接口

### POST /chat/{session_id}/message
发送消息

**Request**:
```json
{
  "message": "帮我出一份初二数学期末试卷"
}
```

**Response (SSE)**:
```
event: text
data: {"type": "text", "content": "收到！还需要确认..."}

event: params_extracted
data: {"type": "params", "params": {...}}

event: done
data: {"type": "done"}
```

---

## 3. 试卷生成

### POST /exams/generate
生成试卷

**Request**:
```json
{
  "session_id": "uuid",
  "params": {
    "subject": "数学",
    "grade": "初二",
    "textbook": "人教版",
    "chapter": "第16-18章",
    "scene": "exam"
  }
}
```

**Response**:
```json
{
  "exam_id": "uuid",
  "questions": [...],
  "metadata": {...}
}
```

---

详细接口规范待补充（OpenAPI 格式）。

**文档维护者**：API 团队  
**最后更新**：2026-04-28
