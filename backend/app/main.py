"""
FastAPI 主应用
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import exam, session, similar_question

# 创建 FastAPI 应用
app = FastAPI(
    title="AI 出题助手 API",
    description="基于 LLM + Workflow 的智能出题系统",
    version="1.0.0"
)

# CORS 配置（允许前端跨域）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # 本地开发
        "https://quiz-generator-3qks.vercel.app",  # Vercel 生产环境
        "https://*.vercel.app",  # Vercel 预览环境
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(exam.router, prefix="/api/exam", tags=["出题"])
app.include_router(session.router, prefix="/api/session", tags=["会话管理"])
app.include_router(similar_question.router, tags=["相似题生成"])


@app.get("/")
async def root():
    """健康检查"""
    return {
        "status": "ok",
        "service": "AI 出题助手",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
