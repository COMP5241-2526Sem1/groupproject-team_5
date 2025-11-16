#!/bin/bash
# Render Shell 命令执行指南

echo "🚀 Render环境AI功能测试指南"
echo "================================"

echo "1️⃣ 首先确认代理设置已生效:"
echo "echo \"no_proxy: \$no_proxy\""
echo ""

echo "2️⃣ 检查API密钥:"
echo "echo \"ARK_API_KEY: \${ARK_API_KEY:0:10}...\""
echo ""

echo "3️⃣ 进入项目目录:"
echo "cd /opt/render/project/src"
echo ""

echo "4️⃣ 运行AI功能测试脚本:"
echo "python3 render_api_debug.py"
echo ""

echo "5️⃣ 如果需要单独测试网络连接:"
echo "curl -v --connect-timeout 10 https://ark.cn-beijing.volces.com/"
echo ""

echo "6️⃣ 查看应用日志:"
echo "tail -f /opt/render/project/src/logs/app.log"
echo ""

echo "💡 提示: 如果遇到语法错误，确保一次只执行一条命令"
