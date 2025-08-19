# MIRIX后端服务Dockerfile
FROM python:3.11-slim

LABEL maintainer="AiEnhance Team"
LABEL description="MIRIX Memory Backend Service for AiEnhance"

# 设置工作目录
WORKDIR /app

# 配置中国镜像源以加速下载
# 使用阿里云镜像源 (推荐)
RUN echo "deb https://mirrors.aliyun.com/debian/ bookworm main non-free non-free-firmware contrib" > /etc/apt/sources.list && \
    echo "deb-src https://mirrors.aliyun.com/debian/ bookworm main non-free non-free-firmware contrib" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.aliyun.com/debian-security/ bookworm-security main" >> /etc/apt/sources.list && \
    echo "deb-src https://mirrors.aliyun.com/debian-security/ bookworm-security main" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.aliyun.com/debian/ bookworm-updates main non-free non-free-firmware contrib" >> /etc/apt/sources.list && \
    echo "deb-src https://mirrors.aliyun.com/debian/ bookworm-updates main non-free non-free-firmware contrib" >> /etc/apt/sources.list

# 如果需要使用清华源，请将上面的阿里云源注释，并取消下面的注释：
# RUN echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm main contrib non-free non-free-firmware" > /etc/apt/sources.list && \
#     echo "deb-src https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm main contrib non-free non-free-firmware" >> /etc/apt/sources.list && \
#     echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian-security/ bookworm-security main contrib non-free non-free-firmware" >> /etc/apt/sources.list && \
#     echo "deb-src https://mirrors.tuna.tsinghua.edu.cn/debian-security/ bookworm-security main contrib non-free non-free-firmware" >> /etc/apt/sources.list && \
#     echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm-updates main contrib non-free non-free-firmware" >> /etc/apt/sources.list && \
#     echo "deb-src https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm-updates main contrib non-free non-free-firmware" >> /etc/apt/sources.list

# 配置pip镜像源为阿里云
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
    pip config set install.trusted-host mirrors.aliyun.com

# 如果需要使用清华PyPI源，请将上面注释，并取消下面的注释：
# RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/ && \
#     pip config set install.trusted-host pypi.tuna.tsinghua.edu.cn

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    ffmpeg \
    postgresql-client \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

# 创建必要的目录
RUN mkdir -p /app/config /app/logs /data/mirix

# 安装MIRIX
RUN pip install --no-cache-dir git+https://github.com/Mirix-AI/MIRIX.git

# 复制配置文件
COPY docker/mirix/requirements.txt /app/
COPY docker/mirix/mirix_config.yml /app/config/mirix.yml
COPY docker/mirix/start_simple.sh /app/start.sh
COPY docker/mirix/wait_for_services.py /app/

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