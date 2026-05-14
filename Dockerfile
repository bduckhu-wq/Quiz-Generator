# 使用官方 Python 镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制后端代码
COPY backend/ /app/backend/

# 安装依赖
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# 暴露端口（Railway 会自动设置 $PORT）
EXPOSE 8000

# 启动命令
CMD cd /app/backend && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
