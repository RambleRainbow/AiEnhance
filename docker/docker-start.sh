#!/bin/bash

# AiEnhance Docker快速启动脚本
set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    log_success "Docker环境检查通过"
}

# 检查环境文件
check_env() {
    if [ ! -f ".env" ]; then
        log_warning ".env文件不存在，正在从.env.example创建..."
        cp .env.example .env
        log_info "请编辑.env文件设置必要的配置（如API密钥）"
    fi
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    mkdir -p logs config data
    log_success "目录创建完成"
}

# 检查本地Ollama服务
check_ollama_service() {
    log_info "检查本地Ollama服务..."
    
    if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        log_error "本地Ollama服务未运行！"
        log_info "请先启动Ollama服务："
        log_info "  macOS: brew install ollama && ollama serve"
        log_info "  Linux: curl -fsSL https://ollama.ai/install.sh | sh && ollama serve"
        log_info "然后安装推荐模型："
        log_info "  ollama pull qwen3:8b"
        log_info "  ollama pull bge-m3"
        exit 1
    fi
    
    log_success "本地Ollama服务运行正常"
    
    # 检查推荐模型
    if ollama list | grep -q "qwen3:8b"; then
        log_success "发现qwen3:8b模型"
    else
        log_warning "未发现qwen3:8b模型，建议运行: ollama pull qwen3:8b"
    fi
    
    if ollama list | grep -q "bge-m3"; then
        log_success "发现bge-m3嵌入模型"
    else
        log_warning "未发现bge-m3嵌入模型，建议运行: ollama pull bge-m3"
    fi
}

# 主启动函数
main() {
    echo "=========================================="
    echo "🚀 AiEnhance 生产模式启动"
    echo "=========================================="
    
    # 检查环境
    check_docker
    check_env
    create_directories
    check_ollama_service
    
    # 解析命令行参数
    CHECK_MODELS=true
    INCLUDE_MANAGEMENT=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --no-check-models)
                CHECK_MODELS=false
                shift
                ;;
            --with-management)
                INCLUDE_MANAGEMENT=true
                shift
                ;;
            --help)
                echo "使用方法: $0 [选项]"
                echo "选项:"
                echo "  --no-check-models  跳过Ollama模型检查"
                echo "  --with-management  启动管理界面(pgAdmin, Redis Commander)"
                echo "  --help            显示此帮助信息"
                exit 0
                ;;
            *)
                log_error "未知选项: $1"
                exit 1
                ;;
        esac
    done
    
    # 构建镜像 (使用完整配置)
    log_info "构建Docker镜像..."
    if $INCLUDE_MANAGEMENT; then
        docker compose -f docker-compose.full.yml --profile management build
    else
        docker compose -f docker-compose.full.yml build
    fi
    
    # 启动完整应用栈
    log_info "启动完整应用栈..."
    if $INCLUDE_MANAGEMENT; then
        docker compose -f docker-compose.full.yml --profile management up -d
    else
        docker compose -f docker-compose.full.yml up -d
    fi
    
    # 等待所有服务启动
    log_info "等待所有服务启动..."
    sleep 10
    
    # 显示服务状态
    echo ""
    echo "=========================================="
    echo "📊 服务状态"
    echo "=========================================="
    docker compose -f docker-compose.full.yml ps
    
    echo ""
    echo "=========================================="
    echo "🌐 访问地址"
    echo "=========================================="
    echo "🎯 AiEnhance主应用: http://localhost:8080"
    echo "📚 API文档: http://localhost:8080/docs"
    echo "🤖 Ollama API (本地): http://localhost:11434"
    
    if $INCLUDE_MANAGEMENT; then
        echo "🗄️  pgAdmin: http://localhost:5050"
        echo "📊 Redis Commander: http://localhost:8081"
    fi
    
    echo ""
    echo "=========================================="
    echo "💡 快速测试"
    echo "=========================================="
    echo "发送测试请求:"
    echo 'curl -X POST "http://localhost:8080/api/query" \'
    echo '     -H "Content-Type: application/json" \'
    echo '     -d '"'"'{"query": "什么是人工智能？", "user_id": "test_user"}'"'"''
    
    echo ""
    echo "=========================================="
    echo "🎉 启动完成！"
    echo "=========================================="
    
    # 可选：跟踪日志
    read -p "是否查看实时日志？(y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker compose -f docker-compose.full.yml logs -f
    fi
}

# 运行主函数
main "$@"