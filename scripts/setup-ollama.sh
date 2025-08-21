#!/bin/bash

# Ollama模型安装脚本
# 为AiEnhance系统安装推荐的Ollama模型

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

# 检查Ollama是否安装
check_ollama_installed() {
    if ! command -v ollama &> /dev/null; then
        log_error "Ollama未安装！"
        log_info "请先安装Ollama："
        log_info "  macOS: brew install ollama"
        log_info "  Linux: curl -fsSL https://ollama.ai/install.sh | sh"
        log_info "  Windows: 下载 https://ollama.ai/download/windows"
        exit 1
    fi
    log_success "Ollama已安装"
}

# 检查Ollama服务是否运行
check_ollama_running() {
    if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        log_error "Ollama服务未运行！"
        log_info "请在另一个终端启动Ollama服务："
        log_info "  ollama serve"
        exit 1
    fi
    log_success "Ollama服务运行正常"
}

# 拉取模型
pull_model() {
    local model_name=$1
    local description=$2
    
    log_info "正在拉取 $model_name ($description)..."
    
    if ollama list | grep -q "$model_name"; then
        log_warning "$model_name 已存在，跳过下载"
        return 0
    fi
    
    if ollama pull "$model_name"; then
        log_success "$model_name 拉取成功"
    else
        log_error "$model_name 拉取失败"
        return 1
    fi
}

# 验证模型
verify_model() {
    local model_name=$1
    
    log_info "验证模型 $model_name..."
    
    if ollama list | grep -q "$model_name"; then
        log_success "$model_name 验证成功"
        return 0
    else
        log_error "$model_name 验证失败"
        return 1
    fi
}

# 主函数
main() {
    echo "=========================================="
    echo "🚀 AiEnhance Ollama模型安装器"
    echo "=========================================="
    
    # 检查环境
    check_ollama_installed
    check_ollama_running
    
    # 推荐模型列表
    declare -A models=(
        ["qwen3:8b"]="通义千问3.0，最新一代中文大语言模型，8B参数"
        ["bge-m3"]="多语言嵌入模型，支持中英文，多功能多粒度"
    )
    
    # 拉取模型
    failed_models=()
    
    for model in "${!models[@]}"; do
        if ! pull_model "$model" "${models[$model]}"; then
            failed_models+=("$model")
        fi
    done
    
    echo ""
    echo "=========================================="
    echo "📊 安装结果"
    echo "=========================================="
    
    # 验证已安装的模型
    log_info "已安装的模型："
    ollama list
    
    echo ""
    
    # 验证核心模型
    success_count=0
    total_count=${#models[@]}
    
    for model in "${!models[@]}"; do
        if verify_model "$model"; then
            ((success_count++))
        fi
    done
    
    echo ""
    echo "=========================================="
    echo "🎯 总结"
    echo "=========================================="
    
    if [ $success_count -eq $total_count ]; then
        log_success "所有推荐模型安装成功！($success_count/$total_count)"
        echo ""
        log_info "现在可以启动AiEnhance系统："
        log_info "  ./docker-start.sh"
    else
        log_warning "部分模型安装失败 ($success_count/$total_count)"
        if [ ${#failed_models[@]} -gt 0 ]; then
            log_info "失败的模型："
            for model in "${failed_models[@]}"; do
                log_info "  - $model"
            done
        fi
        echo ""
        log_info "你仍然可以启动系统，但某些功能可能受限"
    fi
    
    echo ""
    log_info "模型存储位置："
    log_info "  macOS: ~/.ollama/models"
    log_info "  Linux: /usr/share/ollama/.ollama/models"
    log_info "  Windows: %USERPROFILE%\\.ollama\\models"
}

# 运行主函数
main "$@"