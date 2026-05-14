#!/bin/bash

echo "停止所有服务..."

# 从PID文件读取并停止
if [ -f .backend.pid ]; then
    BACKEND_PID=$(cat .backend.pid)
    kill $BACKEND_PID 2>/dev/null
    echo "✅ 后端服务已停止 (PID: $BACKEND_PID)"
    rm -f .backend.pid
fi

if [ -f .frontend.pid ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ 前端服务已停止 (PID: $FRONTEND_PID)"
    rm -f .frontend.pid
fi

# 确保端口释放
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null

echo "✅ 所有服务已停止"
