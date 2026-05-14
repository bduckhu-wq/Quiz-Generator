# 部署指南

本项目采用前后端分离部署方式。

## 一、前端部署（Vercel）

### 1. 连接 GitHub 仓库

1. 访问 [Vercel](https://vercel.com)
2. 使用 GitHub 账号登录
3. 点击 "New Project"
4. 选择 `Quiz-Generator` 仓库
5. 点击 "Import"

### 2. 配置构建设置

Vercel 会自动检测到 Next.js 项目，但需要调整配置：

**Root Directory（根目录）：**
```
frontend
```

**Build Command（构建命令）：**
```
npm run build
```

**Output Directory（输出目录）：**
```
.next
```

**Install Command（安装命令）：**
```
npm install
```

### 3. 配置环境变量

在 Vercel 项目设置中添加环境变量：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `NEXT_PUBLIC_API_BASE_URL` | `https://你的后端地址` | 后端 API 地址（先留空，后端部署后填入） |

### 4. 部署

点击 "Deploy"，等待部署完成。

部署完成后会得到前端地址，例如：
```
https://quiz-generator.vercel.app
```

---

## 二、后端部署（Railway / Render）

### 方案 A：Railway（推荐）

#### 1. 创建项目

1. 访问 [Railway](https://railway.app)
2. 使用 GitHub 账号登录
3. 点击 "New Project" → "Deploy from GitHub repo"
4. 选择 `Quiz-Generator` 仓库

#### 2. 配置服务

**Root Directory（根目录）：**
```
backend
```

**Start Command（启动命令）：**
```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

#### 3. 配置环境变量

在 Railway 项目的 Variables 中添加：

```bash
# LLM API Keys
DEEPSEEK_API_KEY=你的deepseek_api_key
DEEPSEEK_API_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-pro

DOUBAO_API_KEY=你的doubao_api_key
DOUBAO_API_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
DOUBAO_MODEL=doubao-seed-2-0-mini-260428

# 默认 LLM 提供商
LLM_PROVIDER=deepseek
LLM_TEMPERATURE=0.3

# 阿里云 OCR
ALIYUN_ACCESS_KEY_ID=你的aliyun_access_key_id
ALIYUN_ACCESS_KEY_SECRET=你的aliyun_access_key_secret
ALIYUN_REGION=cn-hangzhou

# 数据库
DATABASE_URL=sqlite:///./question_bank.db

# 应用配置
DEBUG=false
LOG_LEVEL=INFO
SESSION_EXPIRE_SECONDS=3600
```

#### 4. 部署

Railway 会自动部署，部署完成后会得到后端地址，例如：
```
https://quiz-generator-backend.railway.app
```

#### 5. 更新前端环境变量

回到 Vercel，在环境变量中更新 `NEXT_PUBLIC_API_BASE_URL` 为后端地址，然后重新部署前端。

---

### 方案 B：Render

#### 1. 创建 Web Service

1. 访问 [Render](https://render.com)
2. 使用 GitHub 账号登录
3. 点击 "New +" → "Web Service"
4. 选择 `Quiz-Generator` 仓库

#### 2. 配置服务

**Name：** `quiz-generator-backend`

**Root Directory：** `backend`

**Runtime：** `Python 3`

**Build Command：**
```bash
pip install -r requirements.txt
```

**Start Command：**
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Plan：** Free（免费）

#### 3. 环境变量

添加与 Railway 相同的环境变量。

#### 4. 部署

点击 "Create Web Service"，等待部署完成。

---

## 三、跨域配置（重要）

后端需要配置 CORS 允许前端域名访问。

编辑 `backend/app/main.py`，确保 CORS 配置包含你的 Vercel 域名：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://quiz-generator.vercel.app",  # 添加你的 Vercel 域名
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

修改后提交并推送到 GitHub，后端会自动重新部署。

---

## 四、验证部署

### 1. 测试后端 API

访问后端健康检查接口：
```
https://你的后端地址/health
```

应该返回：
```json
{"status": "ok"}
```

### 2. 测试前端

访问前端地址：
```
https://quiz-generator.vercel.app
```

测试相似题生成功能：
1. 进入"相似题生成"页面
2. 上传题目图片
3. 等待 OCR 识别
4. 生成相似题

---

## 五、常见问题

### 1. 前端无法连接后端

**原因：** CORS 配置问题或环境变量未设置

**解决：**
- 检查后端 CORS 配置是否包含前端域名
- 检查 Vercel 环境变量 `NEXT_PUBLIC_API_BASE_URL` 是否正确

### 2. 后端部署失败

**原因：** 依赖安装失败或环境变量缺失

**解决：**
- 检查 `requirements.txt` 是否完整
- 检查环境变量是否都已设置

### 3. OCR 识别失败

**原因：** 阿里云 OCR API Key 未配置

**解决：**
- 在后端环境变量中配置 `ALIYUN_ACCESS_KEY_ID` 和 `ALIYUN_ACCESS_KEY_SECRET`

### 4. LLM 生成失败

**原因：** LLM API Key 未配置或余额不足

**解决：**
- 检查 `DEEPSEEK_API_KEY` 或 `DOUBAO_API_KEY` 是否正确
- 检查 API Key 余额

---

## 六、成本估算

### 免费额度

- **Vercel：** 每月免费额度足够个人项目使用
- **Railway：** $5 免费额度/月，约可运行 500 小时
- **Render：** 免费计划（有休眠限制，15 分钟无活动会休眠）

### LLM API 成本

- **DeepSeek：** 约 ¥0.001/次生成（1道相似题）
- **豆包：** 约 ¥0.0005/次生成

### 阿里云 OCR 成本

- 前 1000 次/月免费
- 超出后约 ¥0.01/次

---

## 七、下一步优化

- [ ] 配置自定义域名
- [ ] 添加 CDN 加速
- [ ] 配置数据库持久化（PostgreSQL）
- [ ] 添加用户认证
- [ ] 配置监控和日志

---

**需要帮助？** 查看项目文档或提交 Issue：https://github.com/bduckhu-wq/Quiz-Generator/issues
