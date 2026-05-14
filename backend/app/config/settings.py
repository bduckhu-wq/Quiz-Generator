"""
应用配置管理
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""

    # LLM 配置
    llm_provider: str = "deepseek"
    deepseek_api_key: Optional[str] = None
    deepseek_api_base_url: Optional[str] = "https://api.deepseek.com"
    deepseek_model: Optional[str] = "deepseek-v4-flash"
    kimi_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    qwen_api_key: Optional[str] = None

    # 阿里云 OCR 配置
    aliyun_access_key_id: Optional[str] = None
    aliyun_access_key_secret: Optional[str] = None
    aliyun_region: str = "cn-hangzhou"

    # 数据库配置
    database_url: Optional[str] = None

    # Elasticsearch 配置
    es_host: str = "localhost"
    es_port: int = 9200
    es_index: str = "questions"

    # Redis 配置
    redis_host: str = "localhost"
    redis_port: int = 6379

    # 应用配置
    debug: bool = True
    log_level: str = "INFO"
    session_expire_seconds: int = 3600

    class Config:
        env_file = ".env"
        case_sensitive = False


# 全局配置实例
settings = Settings()


# 导出常用配置
def get_llm_api_key(provider: str) -> Optional[str]:
    """获取 LLM API Key"""
    key_map = {
        "deepseek": settings.deepseek_api_key,
        "kimi": settings.kimi_api_key,
        "claude": settings.anthropic_api_key,
        "qwen": settings.qwen_api_key
    }
    return key_map.get(provider)
