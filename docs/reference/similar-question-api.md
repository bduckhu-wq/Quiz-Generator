# 相似题生成 API 文档

> **版本**：v1.0  
> **基础路径**：`/api/similar-question`  
> **日期**：2026-05-13

---

## 📋 接口概览

| 接口 | 方法 | 功能 | 耗时 |
|-----|------|------|------|
| `/generate` | POST | 上传原题图片，生成N道相似题 | ~50-80秒 |
| `/regenerate` | POST | 重新生成单道题 | ~20秒 |

---

## 1. 生成相似题

### 基本信息

```
POST /api/similar-question/generate
```

**功能描述**：上传原题图片，自动识别后生成指定数量的相似题

**流程**：
```
上传图片 → 阿里云OCR识别 → 单次LLM调用生成N道题 → 校验有效性 → 返回结果
```

### 请求参数

**Query Parameters**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `count` | int | ❌ | 3 | 生成相似题数量，范围 1-10 |

**Body (multipart/form-data)**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `image` | File | ✅ | 原题图片文件（JPG/PNG/HEIC），最大10MB |

### 请求示例

**cURL**：
```bash
curl -X POST "http://localhost:8000/api/similar-question/generate?count=3" \
  -H "Content-Type: multipart/form-data" \
  -F "image=@/path/to/question.png"
```

**Python (requests)**：
```python
import requests

with open("question.png", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/similar-question/generate",
        params={"count": 3},
        files={"image": f}
    )

result = response.json()
print(f"生成 {result['question_count']} 道题，耗时 {result['generation_time']} 秒")
```

**JavaScript (fetch)**：
```javascript
const formData = new FormData();
formData.append('image', fileInput.files[0]);

const response = await fetch('/api/similar-question/generate?count=3', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log(`生成 ${result.question_count} 道题`);
```

### 响应格式

**成功响应 (200 OK)**：

```json
{
  "ocr_result": {
    "question": "原题内容（含LaTeX公式）",
    "confidence": 0.98
  },
  "similar_questions": [
    {
      "question": "题目内容（含选项A/B/C/D）",
      "answer": "A",
      "explanation": "解题步骤和思路"
    },
    {
      "question": "题目内容2...",
      "answer": "C",
      "explanation": "解析2..."
    },
    {
      "question": "题目内容3...",
      "answer": "B",
      "explanation": "解析3..."
    }
  ],
  "validation_results": [
    {
      "question_index": 1,
      "valid": true,
      "errors": []
    },
    {
      "question_index": 2,
      "valid": true,
      "errors": []
    },
    {
      "question_index": 3,
      "valid": true,
      "errors": []
    }
  ],
  "generation_time": 54.32,
  "question_count": 3
}
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `ocr_result.question` | string | OCR识别的原题内容 |
| `ocr_result.confidence` | float | OCR识别置信度（0-1） |
| `similar_questions` | array | 生成的相似题列表 |
| `similar_questions[].question` | string | 题目内容（含选项） |
| `similar_questions[].answer` | string | 答案 |
| `similar_questions[].explanation` | string | 解析 |
| `validation_results` | array | 校验结果列表 |
| `validation_results[].valid` | boolean | 是否通过校验 |
| `validation_results[].errors` | array | 错误信息列表 |
| `generation_time` | float | 总耗时（秒） |
| `question_count` | int | 实际生成题目数量 |

**错误响应**：

```json
// 400 Bad Request - 参数错误
{
  "detail": "生成数量必须在 1-10 之间"
}

// 400 Bad Request - 文件类型错误
{
  "detail": "只支持图片文件 (JPG/PNG/HEIC)"
}

// 500 Internal Server Error - 生成失败
{
  "detail": "生成失败：OCR 识别失败"
}
```

### 性能指标

| 生成数量 | 平均耗时 | P95耗时 | Token消耗 |
|---------|---------|---------|-----------|
| 1道     | 20秒    | 25秒    | ~1,000    |
| 3道     | 50秒    | 60秒    | ~3,000    |
| 5道     | 80秒    | 95秒    | ~5,000    |
| 10道    | 150秒   | 180秒   | ~10,000   |

**说明**：
- 耗时主要受 DeepSeek v4-flash 生成速度限制（46 tokens/秒）
- OCR 识别耗时约 1-2 秒
- 校验耗时可忽略（<1秒）

---

## 2. 重新生成单道题

### 基本信息

```
POST /api/similar-question/regenerate
```

**功能描述**：基于原题重新生成单道相似题

**使用场景**：
- 校验失败时自动重试
- 用户不满意时手动重新生成

### 请求参数

**Body (application/json)**：

```json
{
  "original_question": "原题内容（含选项）",
  "question_index": 1
}
```

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `original_question` | string | ✅ | - | 原题内容 |
| `question_index` | int | ❌ | 1 | 题目序号（用于日志） |

### 请求示例

**cURL**：
```bash
curl -X POST "http://localhost:8000/api/similar-question/regenerate" \
  -H "Content-Type: application/json" \
  -d '{
    "original_question": "一个分数的分子扩大到原来的3倍...",
    "question_index": 1
  }'
```

**Python (requests)**：
```python
response = requests.post(
    "http://localhost:8000/api/similar-question/regenerate",
    json={
        "original_question": "一个分数的分子扩大到原来的3倍...",
        "question_index": 1
    }
)

result = response.json()
print(f"新题目：{result['question']}")
```

### 响应格式

**成功响应 (200 OK)**：

```json
{
  "question": "新生成的题目内容（含选项A/B/C/D）",
  "answer": "B",
  "explanation": "解题步骤和思路",
  "valid": true
}
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `question` | string | 题目内容 |
| `answer` | string | 答案 |
| `explanation` | string | 解析 |
| `valid` | boolean | 是否通过基础校验 |

**错误响应**：

```json
// 500 Internal Server Error
{
  "detail": "重新生成失败：LLM 调用超时"
}
```

---

## 📊 通用说明

### 鉴权

当前版本无需鉴权，后续可添加 API Key 或 JWT Token。

### 限流

建议限制：
- 单用户：10 次/分钟
- 全局：100 次/分钟

### 错误码

| 状态码 | 说明 | 处理建议 |
|--------|------|----------|
| 200 | 成功 | - |
| 400 | 参数错误 | 检查请求参数 |
| 422 | 验证错误 | 检查请求格式 |
| 500 | 服务器错误 | 重试或联系技术支持 |
| 504 | 超时 | 重试（LLM 响应慢） |

### 最佳实践

1. **文件大小控制**：上传前压缩图片至 <2MB
2. **超时处理**：设置客户端超时时间 ≥120秒
3. **重试机制**：失败后最多重试 2 次，间隔 5 秒
4. **并发控制**：避免同时发起多个生成请求

---

## 🧪 测试

### Swagger UI

访问 `http://localhost:8000/docs` 查看交互式 API 文档。

### 测试脚本

```bash
# 运行测试脚本
cd backend
python3 scripts/test_api.py
```

### Postman Collection

导入 `docs/postman/similar-question-api.postman_collection.json`

---

## 📝 更新记录

### v1.0 (2026-05-13)

- ✅ 生成相似题接口（支持动态数量 1-10 道）
- ✅ 重新生成单道题接口
- ✅ 单次 LLM 调用策略（稳定性优先）
- ✅ 完整的错误处理和日志记录

---

**维护者**：后端团队  
**联系方式**：support@example.com
