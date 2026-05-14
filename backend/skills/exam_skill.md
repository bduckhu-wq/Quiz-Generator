<skill name="exam_skill" trigger="出题|试卷|生成试卷|create exam|generate exam|出卷|组卷|考试|测验">

# 出题 Skill

## Purpose
帮助教师根据教学需求智能生成试卷，通过多轮对话理解需求，从题库检索和 AI 生成相结合，快速组装高质量试卷。

## When to Use
- 用户提到"出题"、"生成试卷"、"create exam"、"组卷"
- 用户提供了学科、年级等信息
- 用户描述了考试场景（作业、测验、考试、复习）

## Strategy

### Phase 1: 参数收集 (Parameter Collection)

**必需参数 (Required)**：
- `subject` (学科)：数学、物理、化学、生物、语文、英语、历史、地理、政治
- `grade` (年级)：初一、初二、初三、高一、高二、高三
- `knowledge_points` (知识点)：具体考点，如"一元二次方程"、"函数"、"几何证明"

**可选参数 (Optional)**：
- `scene` (场景)：homework / unit_test / exam / review
- `total_count` (总题数)：默认根据场景自动确定
- `difficulty_adjustment` (难度调整)：可微调难度分布

**收集策略**：
1. **友好追问**：如果缺失必需参数，用自然语言追问
   - 示例："好的！请问是哪个学科的试卷？（数学/物理/化学/语文等）"
2. **提供选项**：降低用户输入门槛
   - 示例："请问是关于哪个知识点？比如：一元二次方程、函数、几何证明，或者您可以自由输入"
3. **追问上限**：最多追问 3 轮，避免对话冗长

**参数验证**：
- 学科必须在预定义列表中
- 年级必须在初一到高三范围
- 知识点至少 1 个，最多 5 个

---

### Phase 2: 场景策略匹配 (Scene Strategy Matching)

根据用户输入的关键词或明确指定的场景，匹配对应的难度分布、题型分布、题量范围。

#### 场景策略表

| 场景 | 关键词 | 难度分布 | 题型分布 | 题量范围 | 总分 |
|-----|--------|---------|---------|---------|------|
| **课后作业** (homework) | 作业、练习、巩固、课后、预习 | 简单 50%<br>中等 40%<br>困难 10% | 选择 30%<br>填空 40%<br>解答 30% | 8-15 题 | 50-100 |
| **单元测验** (unit_test) | 测验、小测、单元、检测、周测 | 简单 30%<br>中等 50%<br>困难 20% | 选择 40%<br>填空 30%<br>解答 30% | 12-20 题 | 80-120 |
| **期末考试** (exam) | 考试、期中、期末、月考 | 简单 20%<br>中等 50%<br>困难 30% | 选择 35%<br>填空 25%<br>解答 40% | 20-30 题 | 100-150 |
| **考前复习** (review) | 复习、冲刺、备考、总复习 | 简单 20%<br>中等 40%<br>困难 40% | 选择 30%<br>填空 20%<br>解答 50% | 10-20 题 | 80-150 |

**匹配逻辑**：
1. 优先根据用户明确指定的场景
2. 如果未指定，根据关键词自动推断
3. 如果无法推断，默认为"单元测验"

---

### Phase 3: 题目获取 (Question Retrieval)

采用**题库优先，AI 补充**的策略，确保题目质量和多样性。

#### 3.1 从题库搜索 (Priority)

**工具调用**：`search_questions(knowledge_points, subject, grade, difficulty, question_type, count)`

**搜索策略**：
- **精准匹配**：知识点、学科、年级必须匹配
- **语义检索**：使用 Embedding 向量相似度扩展召回
- **质量过滤**：优先选择高质量评分、使用频率适中的题目
- **去重**：避免重复使用已出现的题目

**分配原则**：
- 按题型和难度分组分配题量
- 示例：单元测验 15 题 = 选择题 6 道（简单 2、中等 3、困难 1）+ 填空题 4 道 + 解答题 5 道

#### 3.2 AI 生成补充 (Fallback)

**触发条件**：题库搜索结果不足（< 需求题量）

**工具调用**：`generate_question_ai(knowledge_points, difficulty, question_type, reference_questions)`

**生成原则**：
1. **参考题库风格**：传入 3-5 道题库题目作为风格参考
2. **保持一致性**：生成的题目应与题库题目在语言风格、难度标准上保持一致
3. **完整信息**：生成的题目必须包含：
   - 题干 (content)
   - 选项 (options，如果是选择题)
   - 标准答案 (answer)
   - 详细解析 (analysis)
   - 知识点标签 (knowledge_points)
   - 难度标签 (difficulty)
   - 分值 (score)

**质量保证**：
- AI 生成题目占比不超过 30%（优先使用题库）
- 生成后标注"AI 生成"来源

---

### Phase 4: 试卷组装 (Exam Assembly)

**工具调用**：`assemble_exam(questions, scene_config)`

**组装规则**：
1. **按题型分组**：选择题 → 填空题 → 解答题
2. **组内排序**：每组内按难度排序（简单 → 中等 → 困难）
3. **自动编号**：题号从 1 开始连续编号
4. **分值分配**：
   - 选择题：3-5 分/题
   - 填空题：3-5 分/题
   - 解答题：8-15 分/题
   - 总分自动计算，调整至目标总分（如 100 分）

**输出结构**：
```json
{
  "exam_id": "exam_xyz789",
  "subject": "数学",
  "grade": "初二",
  "knowledge_points": ["一元二次方程"],
  "scene": "unit_test",
  "questions": [
    {
      "id": "q_001",
      "index": 1,
      "type": "choice",
      "difficulty": "easy",
      "content": "题目内容...",
      "options": [...],
      "answer": "A",
      "analysis": "解析...",
      "knowledge_points": ["一元二次方程"],
      "score": 5,
      "source": "database",
      "source_id": "db_q_12345"
    },
    // ... 更多题目
  ],
  "total_score": 100,
  "source_stats": {
    "database": 12,
    "ai_generated": 3
  },
  "created_at": "2026-04-28T10:30:00Z"
}
```

---

## Example Conversations

### Case 1: 完整对话流程

```
User: 帮我出份初二数学试卷
Assistant: 好的！请问是关于哪个知识点？比如一元二次方程、函数、几何证明等？

User: 一元二次方程
Assistant: 明白了！这份试卷是用于：
A. 课后作业（侧重基础巩固）
B. 单元测验（全面考查）
C. 期末考试（综合难度）
D. 考前复习（典型题训练）

User: 单元测验
Assistant: [调用 search_questions 搜题...]
        🔍 正在从题库检索...
        ✓ 找到 12 道"一元二次方程"相关题目
        ⚠️ 解答题仅 2 道，不足 4 道（需 AI 补充 2 道）
        
        [调用 generate_question_ai 补充...]
        🤖 AI 正在生成补充题目...
        ✓ 已生成 2 道中等难度解答题
        
        [调用 assemble_exam 组卷...]
        ✅ 组卷完成！共 15 题（题库 12 题 + AI 生成 3 题）
        
        试卷预览：
        一、选择题（共 6 题，30 分）
        1. [题库] 若 x²-5x+6=0，则 x=___
        ...
        
        二、填空题（共 4 题，20 分）
        ...
        
        三、解答题（共 5 题，50 分）
        ...
```

### Case 2: 参数已完整

```
User: 帮我出份初二数学期末考试，关于一元二次方程和函数，题量 20 题
Assistant: [直接执行，无需追问...]
        ✅ 已生成 20 题期末考试试卷
```

### Case 3: 用户修改参数

```
User: 帮我出份初二数学单元测验
Assistant: [参数收集...]

User: 等等，改成期末考试，难度高一点
Assistant: 好的！已切换为期末考试模式，难度分布调整为：
        简单 20%、中等 50%、困难 30%
        [重新生成...]
```

---

## Tools Available

### 1. search_questions
**描述**：从题库检索题目（Elasticsearch 混合检索）

**参数**：
- `knowledge_points` (list[str]): 知识点列表
- `subject` (str): 学科
- `grade` (str): 年级
- `difficulty` (str): 难度（easy/medium/hard）
- `question_type` (str): 题型（choice/blank/solution）
- `count` (int): 需要的题目数量

**返回**：
```json
{
  "questions": [...],
  "found_count": 12,
  "required_count": 15,
  "gap": 3
}
```

### 2. generate_question_ai
**描述**：使用 AI 生成题目（基于 LLM）

**参数**：
- `knowledge_points` (list[str]): 知识点列表
- `difficulty` (str): 难度
- `question_type` (str): 题型
- `count` (int): 生成数量
- `reference_questions` (list[dict]): 参考题库风格（3-5 道题）

**返回**：
```json
{
  "questions": [...]
}
```

### 3. assemble_exam
**描述**：组装试卷（按题型、难度排序，分配题号和分值）

**参数**：
- `questions` (list[dict]): 题目列表
- `scene_config` (dict): 场景配置

**返回**：
```json
{
  "exam_id": "...",
  "questions": [...],
  "total_score": 100
}
```

---

## Quality Checklist

在返回试卷前，确保：
- [ ] 所有题目知识点与用户需求匹配
- [ ] 难度分布符合场景策略（误差 < 10%）
- [ ] 题型分布符合场景策略（误差 < 10%）
- [ ] 每道题都有完整的答案和解析
- [ ] 题目来源标注清晰（题库 ID 或"AI 生成"）
- [ ] 总分计算正确
- [ ] 题号连续无遗漏

---

## Edge Cases Handling

### 1. 题库完全没有相关题目
→ 100% AI 生成，但提醒用户："题库暂无相关题目，已全部使用 AI 生成，建议人工审核"

### 2. 用户要求的知识点过多（> 5 个）
→ 提醒用户："知识点过多可能导致试卷聚焦度不够，建议控制在 3-5 个。是否继续？"

### 3. 用户要求的题量超出场景推荐范围
→ 提醒用户："期末考试建议题量 20-30 题，您要求 50 题可能超时。是否继续？"

### 4. AI 生成失败或超时
→ 降级策略：只使用题库题目，减少题量，提醒用户："AI 生成暂时不可用，已为您生成 12 题（原计划 15 题）"

---

## Performance Expectations

- **参数收集**：1-3 轮对话，平均 2 轮
- **搜题耗时**：< 2 秒（15 题）
- **AI 生成耗时**：< 10 秒（3 题）
- **总耗时**：< 30 秒（15 题试卷）

---

## Version History

- v1.0 (2026-04-28): 初始版本，支持 4 种场景策略，题库 + AI 混合生成

</skill>
