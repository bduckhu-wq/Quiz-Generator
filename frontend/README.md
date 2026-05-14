# AI出题助手 - 前端

基于 Next.js 14 + TypeScript + Tailwind CSS 的智能对话出题系统

## 🚀 快速开始

### 1. 安装依赖
```bash
npm install
```

### 2. 启动后端（另一个终端）
```bash
cd ../backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 启动前端开发服务器
```bash
npm run dev
```

### 4. 访问应用
打开浏览器访问：http://localhost:3000

---

## 📁 项目结构

```
frontend/
├── app/                      # Next.js 14 App Router
│   ├── page.tsx             # 首页
│   ├── chat/
│   │   └── page.tsx         # 对话页（核心功能）
│   ├── layout.tsx           # 根布局
│   └── globals.css          # 全局样式
│
├── components/              # React组件
│   ├── chat/
│   │   ├── InputBox.tsx    # 输入框组件
│   │   └── ThinkingIndicator.tsx  # AI思考动画
│   ├── exam/               # 试卷相关组件
│   └── common/             # 通用组件
│
├── hooks/                  # 自定义Hooks
│   ├── useChat.ts          # 对话管理
│   └── useSession.ts       # 会话管理
│
├── lib/                    # 工具函数
│   ├── api.ts             # API封装
│   ├── sseClient.ts       # SSE流式接收
│   ├── types.ts           # TypeScript类型
│   └── utils.ts           # 工具函数
│
├── public/                # 静态资源
├── .env.local            # 环境变量
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

---

## 🎯 核心功能

### 1. 多轮对话
- ✅ 用户输入需求
- ✅ AI智能追问补全参数
- ✅ 实时消息展示
- ✅ 会话持久化

### 2. SSE流式输出
- ✅ 实时接收后端进度
- ✅ 显示AI思考过程
- ✅ 平滑的用户体验

### 3. 试卷预览
- ✅ 双栏布局（对话|试卷）
- ✅ 题目详细展示
- ✅ 答案解析折叠

### 4. 智能功能
- ✅ 会话恢复（刷新页面保持状态）
- ✅ localStorage持久化
- ✅ 自动滚动到最新消息

---

## 🔧 开发命令

```bash
# 开发环境
npm run dev

# 构建生产版本
npm run build

# 启动生产服务器
npm run start

# 代码检查
npm run lint
```

---

## 🌐 API接口

### 后端地址
- 开发环境: `http://localhost:8000`
- 可在 `.env.local` 中配置

### 主要接口
- `POST /api/session/create` - 创建会话
- `POST /api/exam/generate/stream` - SSE流式生成试卷
- `GET /api/session/{id}` - 获取会话

---

## 📝 使用说明

### 基础使用流程

1. **首页** → 点击"开始使用"
2. **对话页** → 输入需求，如：
   ```
   三年级数学第三章第二节课后练习5题
   ```
3. **AI处理** → 自动提取参数或追问补充
4. **试卷生成** → 右侧实时预览试卷

### 示例对话

**场景1: 参数完整，直接生成**
```
用户: "三年级数学第三章第二节课后练习5题"
AI: [思考中...]
AI: "✅ 试卷已生成完成！"
→ 右侧显示完整试卷
```

**场景2: 参数不足，多轮追问**
```
用户: "帮我出份数学试卷"
AI: "好的！请问是针对哪个年级出题呢？"

用户: "三年级"
AI: "明白了！请问是关于哪个知识点或章节？"

用户: "第三章第二节"
AI: "✅ 试卷已生成完成！"
```

---

## 🎨 技术栈

- **框架**: Next.js 14 (App Router)
- **语言**: TypeScript
- **样式**: Tailwind CSS
- **HTTP**: Axios
- **状态管理**: React Hooks
- **实时通信**: SSE (Server-Sent Events)

---

## ⚙️ 环境变量

创建 `.env.local` 文件：

```bash
# 后端API地址
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🐛 常见问题

### Q1: 连接后端失败
**A**: 确保后端服务已启动
```bash
cd ../backend
python3 -m uvicorn app.main:app --reload
# 访问 http://localhost:8000/health 检查
```

### Q2: 依赖安装失败
**A**: 尝试清理缓存重装
```bash
rm -rf node_modules package-lock.json
npm install
```

### Q3: 页面显示空白
**A**: 检查浏览器控制台错误信息
- F12 打开开发者工具
- 查看 Console 和 Network 标签页

---

## 📊 性能优化

- ✅ Next.js 自动代码分割
- ✅ 图片优化（Next/Image）
- ✅ SSE减少轮询开销
- ✅ React.memo优化重渲染

---

## 🚀 部署建议

### Vercel部署（推荐）
```bash
npm install -g vercel
vercel
```

### Docker部署
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

---

## 📚 相关文档

- [Next.js 文档](https://nextjs.org/docs)
- [Tailwind CSS 文档](https://tailwindcss.com/docs)
- [后端API文档](../backend/DELIVERY.md)

---

**当前状态**: ✅ 基础版本已完成，可立即运行测试
