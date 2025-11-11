#!/bin/bash

# 一键数据迁移脚本
# 从本地 MySQL 迁移到 PlanetScale

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║       🚀 数据库一键迁移工具                                    ║"
echo "║       本地 MySQL → PlanetScale                                ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 未找到 Python 3${NC}"
    exit 1
fi

# 检查环境变量
echo "🔍 检查环境变量..."
REQUIRED_VARS=("MYSQL_HOST" "MYSQL_USER" "MYSQL_PASSWORD" "MYSQL_DATABASE")
MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo -e "${RED}❌ 缺少以下环境变量:${NC}"
    for var in "${MISSING_VARS[@]}"; do
        echo "   - $var"
    done
    echo ""
    echo "请设置 PlanetScale 环境变量:"
    echo "  export MYSQL_HOST=your-db.psdb.cloud"
    echo "  export MYSQL_USER=your_username"
    echo "  export MYSQL_PASSWORD=pscale_pw_xxx"
    echo "  export MYSQL_DATABASE=qa-platform"
    exit 1
fi

echo -e "${GREEN}✅ 环境变量配置完整${NC}"
echo ""

# 显示配置
echo "📊 迁移配置:"
echo "   源数据库: 本地 MySQL (127.0.0.1:3307)"
echo "   目标数据库: PlanetScale ($MYSQL_HOST)"
echo "   目标库名: $MYSQL_DATABASE"
echo ""

# 确认
read -p "是否继续迁移？(y/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 已取消"
    exit 0
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 第1步：导出本地数据
echo ""
echo "📤 第1步：导出本地数据..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 export_local_data.py
EXPORT_STATUS=$?

if [ $EXPORT_STATUS -ne 0 ]; then
    echo -e "${RED}❌ 导出失败！${NC}"
    exit 1
fi

# 获取最新的备份文件
BACKUP_FILE=$(ls -t data_backup_*.json 2>/dev/null | head -1)

if [ -z "$BACKUP_FILE" ]; then
    echo -e "${RED}❌ 未找到备份文件${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 数据已导出到: $BACKUP_FILE${NC}"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 第2步：初始化 PlanetScale 表结构
echo ""
echo "🏗️  第2步：初始化 PlanetScale 表结构..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 init_db.py
INIT_STATUS=$?

if [ $INIT_STATUS -ne 0 ]; then
    echo -e "${YELLOW}⚠️  初始化可能失败，但继续尝试导入数据...${NC}"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 第3步：导入数据
echo ""
echo "📥 第3步：导入数据到 PlanetScale..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 import_to_planetscale.py "$BACKUP_FILE"
IMPORT_STATUS=$?

if [ $IMPORT_STATUS -ne 0 ]; then
    echo -e "${RED}❌ 导入失败！${NC}"
    echo ""
    echo "💡 可能的原因:"
    echo "   1. PlanetScale 连接失败"
    echo "   2. 表结构不匹配"
    echo "   3. 数据格式问题"
    echo ""
    echo "🔧 解决方法:"
    echo "   1. 检查环境变量是否正确"
    echo "   2. 确认 PlanetScale 数据库已创建"
    echo "   3. 查看错误信息进行调试"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 第4步：验证
echo ""
echo "🔍 第4步：验证数据..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 verify_migration.py
VERIFY_STATUS=$?

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ $VERIFY_STATUS -eq 0 ]; then
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║                                                               ║"
    echo "║       🎉 数据迁移成功！                                        ║"
    echo "║                                                               ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "📊 备份文件已保存: $BACKUP_FILE"
    echo "🗄️  数据已导入到: $MYSQL_HOST/$MYSQL_DATABASE"
    echo ""
    echo "下一步："
    echo "  1. 在本地测试 PlanetScale 连接"
    echo "  2. 推送代码到 GitHub: git push origin zmd"
    echo "  3. 在 Render 部署应用"
else
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║                                                               ║"
    echo "║       ⚠️  迁移完成但发现问题                                   ║"
    echo "║                                                               ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "请检查上述验证结果，解决问题后可以重新导入数据。"
fi

echo ""
