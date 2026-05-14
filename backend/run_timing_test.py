"""
专门用于性能分析的运行脚本
添加详细的日志输出
"""
import logging
import sys

# 配置详细日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d [%(name)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/backend_timing_detailed.log', mode='w')
    ]
)

# 设置关键模块的日志级别
logging.getLogger('workflows').setLevel(logging.INFO)
logging.getLogger('services').setLevel(logging.INFO)
logging.getLogger('app').setLevel(logging.INFO)

if __name__ == "__main__":
    import uvicorn
    print("="*80)
    print("启动性能分析版后端服务")
    print("日志输出到: /tmp/backend_timing_detailed.log")
    print("="*80)
    print()

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # 禁用热重载以获得稳定性能
        log_level="info"
    )
