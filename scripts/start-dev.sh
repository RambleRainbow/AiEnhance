#!/bin/bash

# AiEnhance 开发模式启动脚本
# 只启动外部依赖服务，主应用在本地运行
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
        log_info "请编辑.env文件设置必要的配置"
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
        log_info "  ./setup-ollama.sh"
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

# 检查uv环境
check_uv_env() {
    log_info "检查Python开发环境..."
    
    if ! command -v uv &> /dev/null; then
        log_error "uv未安装，请先安装uv包管理器"
        log_info "安装方法: curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
    
    if [ ! -f "pyproject.toml" ]; then
        log_error "pyproject.toml文件不存在"
        exit 1
    fi
    
    # 检查依赖是否已安装
    if ! uv run python -c "import aienhance" &> /dev/null; then
        log_warning "Python依赖未安装，正在安装..."
        uv sync
    fi
    
    log_success "Python开发环境检查通过"
}

# 主启动函数
main() {
    echo "=========================================="
    echo "🚀 AiEnhance 开发模式启动"
    echo "=========================================="
    
    # 解析命令行参数
    SKIP_CHECKS=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-checks)
                SKIP_CHECKS=true
                shift
                ;;
            --help)
                echo "开发模式启动脚本 - 只启动外部依赖服务"
                echo ""
                echo "使用方法: $0 [选项]"
                echo ""
                echo "选项:"
                echo "  --skip-checks     跳过环境检查"
                echo "  --help           显示此帮助信息"
                echo ""
                echo "开发流程:"
                echo "  1. $0                      # 启动外部依赖"
                echo "  2. uv run python main.py   # 本地运行主应用"
                echo "  3. 开发、调试、测试"
                echo "  4. docker compose down     # 停止依赖服务"
                exit 0
                ;;
            *)
                log_error "未知选项: $1"
                exit 1
                ;;
        esac
    done
    
    # 环境检查
    if [ "$SKIP_CHECKS" != "true" ]; then
        check_docker
        check_env
        create_directories
        check_ollama_service
        check_uv_env
    fi
    
    # 构建并启动外部依赖服务
    log_info "构建Docker镜像..."
    docker compose build
    
    log_info "启动外部依赖服务..."
    docker compose up -d
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 15
    
    # 显示服务状态
    echo ""
    echo "=========================================="
    echo "📊 外部依赖服务状态"
    echo "=========================================="
    docker compose ps
    
    echo ""
    echo "=========================================="
    echo "🌐 服务访问地址"
    echo "=========================================="
    echo "🗄️  PostgreSQL: localhost:5432"
    echo "🔴 Redis: localhost:6379"
    echo "🤖 MIRIX后端: http://localhost:8000"
    echo "🤖 Ollama (本地): http://localhost:11434"
    
    echo ""
    echo "=========================================="
    echo "💻 本地开发命令"
    echo "=========================================="
    echo "运行主应用:"
    echo "  uv run python main.py"
    echo ""
    echo "测试协作功能:"
    echo "  uv run python test_collaboration_layer.py"
    echo ""
    echo "代码检查:"
    echo "  uv run ruff check ."
    echo "  uv run ruff format ."
    echo ""
    echo "停止依赖服务:"
    echo "  docker compose down"
    
    echo ""
    echo "=========================================="
    echo "🎉 开发环境启动完成！"
    echo "=========================================="
    echo "✅ 外部依赖服务已启动"
    echo "💡 现在可以运行: uv run python main.py"
    
    # 可选：跟踪日志
    echo ""
    read -p "是否查看依赖服务实时日志？(y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "按 Ctrl+C 停止日志查看"
        docker compose logs -f
    fi
}

# 运行主函数
main "$@"