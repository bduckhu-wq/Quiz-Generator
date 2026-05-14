#!/bin/bash

echo "================================"
echo "AI出题助手 - 快速启动脚本"
echo "================================"
echo ""

# 检查是否在项目根目录
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

# 启动后端
echo "📦 启动后端服务..."
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "✅ 后端已启动 (PID: $BACKEND_PID)"
echo "   访问: http://localhost:8000"
echo ""

# 等待后端启动
sleep 3

# 检查后端是否启动成功
curl -s http://localhost:8000/health > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ 后端健康检查通过"
else
    echo "⚠️  后端可能未完全启动，请稍等..."
fi

echo ""

# 启动前端
echo "🎨 启动前端服务..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!
echo "✅ 前端已启动 (PID: $FRONTEND_PID)"
echo "   访问: http://localhost:3000"
echo ""

echo "================================"
echo "🎉 所有服务已启动！"
echo "================================"
echo ""
echo "📝 使用说明:"
echo "  1. 打开浏览器访问: http://localhost:3000"
echo "  2. 点击"开始使用"进入对话页"
echo "  3. 输入出题需求，如: 三年级数学第三章第二节课后练习5题"
echo ""
echo "⚠️  停止服务:"
echo "  按 Ctrl+C 停止本脚本"
echo "  或运行: ./stop.sh"
echo ""

# 保存PID到文件
echo "$BACKEND_PID" > .backend.pid
echo "$FRONTEND_PID" > .frontend.pid

# 等待用户中断
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; rm -f .backend.pid .frontend.pid; echo ''; echo '✅ 所有服务已停止'; exit" INT

wait
