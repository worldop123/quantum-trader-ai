#!/bin/bash

# QuantumTrader 启动脚本
# 用法: ./start.sh [backend|frontend|all]

set -e

echo "========================================="
echo "  QuantumTrader AI量化交易系统"
echo "========================================="
echo ""

# 获取项目根目录
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR"

start_backend() {
    echo "🚀 启动后端服务..."
    echo "   后端地址: http://localhost:8000"
    echo "   API文档: http://localhost:8000/docs"
    echo ""
    
    cd "$BACKEND_DIR"
    
    # 检查是否安装了依赖
    if [ ! -d "venv" ] && [ -z "$VIRTUAL_ENV" ]; then
        echo "📦 创建虚拟环境..."
        python3 -m venv venv
        source venv/bin/activate
        echo "📦 安装依赖..."
        pip install -r requirements.txt
    else
        if [ -d "venv" ]; then
            source venv/bin/activate
        fi
    fi
    
    # 启动后端
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
}

start_frontend() {
    echo "🎨 启动前端服务..."
    echo "   前端地址: http://localhost:5173"
    echo ""
    
    cd "$FRONTEND_DIR"
    
    # 检查是否安装了依赖
    if [ ! -d "node_modules" ]; then
        echo "📦 安装依赖..."
        npm install
    fi
    
    # 启动前端
    npm run dev
}

start_all() {
    echo "🚀 启动全部服务..."
    echo ""
    
    # 启动后端（后台运行）
    echo "📡 启动后端服务..."
    cd "$BACKEND_DIR"
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/quantumtrader-backend.log 2>&1 &
    BACKEND_PID=$!
    echo "   后端PID: $BACKEND_PID"
    echo "   后端日志: /tmp/quantumtrader-backend.log"
    
    # 等待后端启动
    sleep 3
    
    # 启动前端
    echo ""
    echo "🎨 启动前端服务..."
    cd "$FRONTEND_DIR"
    
    # 捕获退出信号，关闭后端
    trap "kill $BACKEND_PID 2>/dev/null; echo ''; echo '🛑 停止后端服务...'; exit" INT TERM
    
    npm run dev
}

# 主逻辑
case "${1:-all}" in
    backend)
        start_backend
        ;;
    frontend)
        start_frontend
        ;;
    all)
        start_all
        ;;
    *)
        echo "用法: $0 [backend|frontend|all]"
        echo ""
        echo "  backend  - 仅启动后端"
        echo "  frontend - 仅启动前端"
        echo "  all      - 启动前后端（默认）"
        echo ""
        exit 1
        ;;
esac
