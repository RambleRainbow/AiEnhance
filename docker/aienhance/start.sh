#!/bin/bash

# AiEnhance应用启动脚本
set -e

echo "=== AiEnhance Application Startup ==="
echo "Starting AiEnhance Memory-Cognitive System..."

# 设置环境变量
export PYTHONPATH="/app:$PYTHONPATH"
export AIENHANCE_ENV="docker"

# 等待依赖服务
echo "Waiting for MIRIX service..."
while ! curl -f $MIRIX_API_URL/health > /dev/null 2>&1; do
  echo "MIRIX is unavailable - sleeping"
  sleep 5
done
echo "MIRIX service is ready!"

echo "Waiting for Ollama service..."
while ! curl -f $OLLAMA_API_URL/api/tags > /dev/null 2>&1; do
  echo "Ollama is unavailable - sleeping"
  sleep 5
done
echo "Ollama service is ready!"

# 创建必要的目录
mkdir -p /app/logs
mkdir -p /app/data

# 设置日志
export LOG_LEVEL="${LOG_LEVEL:-info}"

echo "All services are ready, starting AiEnhance application..."

# 启动应用
python /app/app.py