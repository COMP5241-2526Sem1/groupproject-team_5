#!/bin/bash
# Render.com 启动脚本 - 优化版
# 确保环境变量正确加载和Web服务正常启动

echo "🚀 Starting Classroom Interaction Platform on Render..."
echo "=========================================================="
echo "📍 Working directory: $(pwd)"
echo "🐍 Python version: $(python3 --version)"
echo ""

# 检查关键环境变量
echo "🔍 Environment Variables Check:"
if [ -n "$ARK_API_KEY" ]; then
    echo "✅ ARK_API_KEY is set (${ARK_API_KEY:0:10}...)"
else
    echo "❌ ARK_API_KEY is NOT set!"
fi

if [ -n "$DATABASE_URL" ]; then
    echo "✅ DATABASE_URL is set"
else
    echo "⚠️  DATABASE_URL is NOT set (will use SQLite)"
fi

if [ -n "$SECRET_KEY" ]; then
    echo "✅ SECRET_KEY is set"
else
    echo "⚠️  SECRET_KEY is NOT set (will use default)"
fi

echo ""

# 检查SDK是否安装
echo "🔍 Checking volcengine SDK..."
python3 -c "from volcenginesdkarkruntime import Ark; print('✅ volcenginesdkarkruntime is installed')" 2>/dev/null || echo "❌ volcenginesdkarkruntime NOT installed"

echo ""

# 数据库迁移（如果需要）
if [ -n "$DATABASE_URL" ]; then
    echo "🗄️  Running database migrations..."
    python3 -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print('✅ Database tables created')" || echo "⚠️  Database migration skipped"
    echo ""
fi

# 启动Gunicorn
echo "🌐 Starting Gunicorn web server..."
echo "   Workers: 2"
echo "   Timeout: 120 seconds"
echo "   Worker class: eventlet"
echo "   Port: $PORT"
echo ""

exec gunicorn \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 2 \
    --timeout 120 \
    --graceful-timeout 30 \
    --worker-class eventlet \
    --worker-connections 1000 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    --enable-stdio-inheritance \
    'run:app'
