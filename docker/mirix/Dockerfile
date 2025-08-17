# MIRIX后端服务Dockerfile
FROM python:3.11-slim

LABEL maintainer="AiEnhance Team"
LABEL description="MIRIX Memory Backend Service for AiEnhance"

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 创建必要的目录
RUN mkdir -p /app/config /app/logs /data/mirix

# 安装MIRIX
RUN pip install --no-cache-dir git+https://github.com/Mirix-AI/MIRIX.git

# 复制配置文件
COPY docker/mirix/requirements.txt /app/
COPY docker/mirix/mirix_config.yml /app/config/mirix.yml
COPY docker/mirix/start.sh /app/

# 安装额外依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置权限
RUN chmod +x /app/start.sh

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动服务
CMD ["/app/start.sh"]