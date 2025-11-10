#!/bin/bash

# 清理旧项目文件的脚本

echo "🧹 开始清理旧项目文件..."

BASE_DIR="/Users/dududu/Desktop/文件/python_code/Q&A platform demo"

# 进入项目目录
cd "$BASE_DIR"

echo "📂 当前清理目录: $BASE_DIR"

# 删除缓存文件
echo "🗑️  删除Python缓存文件..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true

# 删除IDE配置文件
echo "🗑️  删除IDE配置文件..."
rm -rf .vscode .idea 2>/dev/null || true

# 删除数据库文件
echo "🗑️  删除SQLite数据库文件..."
find . -name "*.db" -delete 2>/dev/null || true
rm -rf instance 2>/dev/null || true

# 删除日志文件
echo "🗑️  删除日志文件..."
find . -name "*.log" -delete 2>/dev/null || true

# 询问是否删除integrated_platform目录
echo ""
echo "❓ 是否删除 integrated_platform 目录？(功能已整合到final_integrated_platform)"
echo "   输入 'yes' 确认删除，其他任意键跳过："
read -r response

if [ "$response" = "yes" ]; then
    echo "🗑️  删除 integrated_platform 目录..."
    rm -rf integrated_platform 2>/dev/null || true
    echo "✅ integrated_platform 目录已删除"
else
    echo "⏭️  跳过删除 integrated_platform 目录"
fi

# 询问是否删除旧的虚拟环境
echo ""
echo "❓ 是否删除旧的虚拟环境 .venv？"
echo "   输入 'yes' 确认删除，其他任意键跳过："
read -r response

if [ "$response" = "yes" ]; then
    echo "🗑️  删除 .venv 目录..."
    rm -rf .venv 2>/dev/null || true
    echo "✅ .venv 目录已删除"
else
    echo "⏭️  跳过删除 .venv 目录"
fi

echo ""
echo "✅ 清理完成！"
echo ""
echo "📁 推荐的项目结构:"
echo "   ✅ final_integrated_platform/  (主要项目)"
echo "   📄 config.py  (参考配置)"
echo "   📄 exts.py   (参考配置)"
echo "   📄 decorators.py  (参考工具)"
echo ""
echo "🚀 使用最终版本:"
echo "   cd final_integrated_platform"
echo "   python -m venv venv"
echo "   source venv/bin/activate"
echo "   pip install -r requirements.txt"
echo "   python run.py"
