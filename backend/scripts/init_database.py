"""
数据库初始化脚本

用法：
python scripts/init_database.py
"""

import sys
import os

# 添加 backend 到 path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.base import init_db, engine
from models import Base


def main():
    """初始化数据库"""
    print("\n" + "="*60)
    print("初始化数据库")
    print("="*60 + "\n")

    try:
        # 创建所有表
        print("正在创建数据库表...")
        Base.metadata.create_all(bind=engine)
        print("✓ 数据库表创建成功\n")

        # 显示已创建的表
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        print(f"已创建 {len(tables)} 个表:")
        for table in tables:
            print(f"  • {table}")

        print("\n" + "="*60)
        print("✅ 数据库初始化完成！")
        print("="*60 + "\n")

        return True

    except Exception as e:
        print(f"\n❌ 数据库初始化失败: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
