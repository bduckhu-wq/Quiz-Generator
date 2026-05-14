"""
重试装饰器和错误处理工具
"""

import asyncio
import functools
import time
from typing import Callable, Type, Tuple


def retry_async(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    异步函数重试装饰器

    Args:
        max_retries: 最大重试次数
        delay: 初始延迟（秒）
        backoff: 指数退避因子
        exceptions: 需要重试的异常类型

    Usage:
        @retry_async(max_retries=3, delay=1.0)
        async def risky_operation():
            ...
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            current_delay = delay

            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)

                except exceptions as e:
                    if attempt == max_retries - 1:
                        # 最后一次尝试失败，抛出异常
                        raise

                    print(f"⚠️  {func.__name__} 失败（第 {attempt + 1}/{max_retries} 次）: {e}")
                    print(f"   等待 {current_delay:.1f}s 后重试...")

                    await asyncio.sleep(current_delay)
                    current_delay *= backoff

            return None

        return wrapper
    return decorator


class WorkflowError(Exception):
    """Workflow 执行错误基类"""
    pass


class ParameterError(WorkflowError):
    """参数错误"""
    pass


class LLMError(WorkflowError):
    """LLM 调用错误"""
    pass


class DatabaseError(WorkflowError):
    """数据库错误"""
    pass


class GenerationError(WorkflowError):
    """题目生成错误"""
    pass


def handle_workflow_error(error: Exception, context: str = "") -> dict:
    """
    统一的 Workflow 错误处理

    Args:
        error: 异常对象
        context: 上下文信息

    Returns:
        错误响应字典
    """
    error_type = type(error).__name__
    error_message = str(error)

    # 构建错误响应
    error_response = {
        "error": True,
        "error_type": error_type,
        "error_message": error_message,
        "context": context,
        "timestamp": time.time()
    }

    # 根据错误类型添加用户友好提示
    if isinstance(error, ParameterError):
        error_response["user_message"] = "参数不正确，请检查输入"
    elif isinstance(error, LLMError):
        error_response["user_message"] = "AI 服务暂时不可用，请稍后重试"
    elif isinstance(error, DatabaseError):
        error_response["user_message"] = "题库服务异常，请稍后重试"
    elif isinstance(error, GenerationError):
        error_response["user_message"] = "题目生成失败，请重试"
    else:
        error_response["user_message"] = "服务异常，请稍后重试"

    return error_response
