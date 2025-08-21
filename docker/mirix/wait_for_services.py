#!/usr/bin/env python3
"""
等待外部服务就绪的Python脚本
替代需要外部客户端工具的shell命令
"""

import asyncio
import os
import sys
from datetime import datetime

import asyncpg
import redis.asyncio as redis


async def wait_for_postgres():
    """等待PostgreSQL准备就绪"""
    host = os.getenv('POSTGRES_HOST', 'postgres')
    port = int(os.getenv('POSTGRES_PORT', '5432'))
    user = os.getenv('POSTGRES_USER', 'mirix')
    password = os.getenv('POSTGRES_PASSWORD', 'mirix_password')
    database = os.getenv('POSTGRES_DB', 'mirix_memory')

    max_attempts = 30
    attempt = 0

    print(f"Waiting for PostgreSQL at {host}:{port}...")

    while attempt < max_attempts:
        try:
            conn = await asyncpg.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                command_timeout=5
            )
            await conn.close()
            print("✅ PostgreSQL is ready!")
            return True
        except Exception as e:
            attempt += 1
            print(f"PostgreSQL is unavailable (attempt {attempt}/{max_attempts}): {e}")
            await asyncio.sleep(2)

    print("❌ PostgreSQL failed to become ready")
    return False


async def wait_for_redis():
    """等待Redis准备就绪"""
    host = os.getenv('REDIS_HOST', 'redis')
    port = int(os.getenv('REDIS_PORT', '6379'))

    max_attempts = 30
    attempt = 0

    print(f"Waiting for Redis at {host}:{port}...")

    while attempt < max_attempts:
        try:
            client = redis.Redis(host=host, port=port, socket_connect_timeout=5)
            result = await client.ping()
            await client.aclose()
            if result:
                print("✅ Redis is ready!")
                return True
        except Exception as e:
            attempt += 1
            print(f"Redis is unavailable (attempt {attempt}/{max_attempts}): {e}")
            await asyncio.sleep(2)

    print("❌ Redis failed to become ready")
    return False


async def setup_database():
    """设置数据库扩展和表结构"""
    host = os.getenv('POSTGRES_HOST', 'postgres')
    port = int(os.getenv('POSTGRES_PORT', '5432'))
    user = os.getenv('POSTGRES_USER', 'mirix')
    password = os.getenv('POSTGRES_PASSWORD', 'mirix_password')
    database = os.getenv('POSTGRES_DB', 'mirix_memory')

    print("Setting up database...")

    try:
        conn = await asyncpg.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )

        # 创建vector扩展
        try:
            await conn.execute('CREATE EXTENSION IF NOT EXISTS vector;')
            print("✅ Vector extension created successfully")
        except Exception as e:
            print(f"⚠️  Vector extension setup: {e}")

        # 这里可以添加更多的数据库初始化逻辑
        # 例如创建MIRIX需要的表结构

        await conn.close()
        print("✅ Database setup completed")
        return True

    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False


async def main():
    """主函数"""
    print("=" * 50)
    print(f"🔄 Service readiness check started at {datetime.now()}")
    print("=" * 50)

    # 等待PostgreSQL
    if not await wait_for_postgres():
        sys.exit(1)

    # 等待Redis
    if not await wait_for_redis():
        sys.exit(1)

    # 设置数据库
    if not await setup_database():
        sys.exit(1)

    print("=" * 50)
    print("🎉 All services are ready!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
