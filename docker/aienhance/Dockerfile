# AiEnhance主应用Dockerfile
FROM python:3.12-slim

LABEL maintainer="AiEnhance Team"
LABEL description="AiEnhance Memory-Cognitive System"

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 创建必要的目录
RUN mkdir -p /app/config /app/logs /app/data

# 复制项目文件
COPY pyproject.toml /app/
COPY README.md /app/
COPY aienhance/ /app/aienhance/
COPY examples/ /app/examples/
COPY docker/aienhance/requirements.txt /app/
COPY docker/aienhance/app.py /app/
COPY docker/aienhance/start.sh /app/

# 安装Python依赖
RUN pip install --no-cache-dir -e .
RUN pip install --no-cache-dir -r requirements.txt

# 设置权限
RUN chmod +x /app/start.sh

# 暴露端口
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# 启动服务
CMD ["/app/start.sh"]