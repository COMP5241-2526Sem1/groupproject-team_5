# 🚂 Railway MySQL 配置指南

## ✅ 你的 Railway 数据库信息

### 连接信息
```
主机: trolley.proxy.rlwy.net
端口: 53176
用户: root
密码: HGbKlRAozMzZiIbvMcEXeiZUKgHoJxXr
数据库: railway
```

### 连接 URL
```
mysql://root:HGbKlRAozMzZiIbvMcEXeiZUKgHoJxXr@trolley.proxy.rlwy.net:53176/railway
```

## 🎯 下一步操作

### 1. 本地测试 Railway 连接

#### 方法一：使用环境变量
```bash
# 设置 Railway 环境变量
export MYSQL_HOST=trolley.proxy.rlwy.net
export MYSQL_PORT=53176
export MYSQL_USER=root
export MYSQL_PASSWORD=HGbKlRAozMzZiIbvMcEXeiZUKgHoJxXr
export MYSQL_DATABASE=railway

# 运行应用
python run.py
```

#### 方法二：使用 .env 文件
```bash
# 复制 Railway 环境配置
cp .env.railway .env

# 运行应用
python run.py
```

### 2. 初始化 Railway 数据库

```bash
# 运行初始化脚本
python init_db.py
```

这会在 Railway 数据库中创建所有表并创建默认管理员账号：
- 邮箱: admin@example.com
- 密码: admin123

### 3. 迁移本地数据到 Railway（可选）

如果你有本地数据需要迁移：

```bash
# 方法一：使用一键迁移脚本
./migrate_database.sh

# 方法二：手动迁移
# 1. 导出本地数据
python export_local_data.py

# 2. 导入到 Railway
python import_to_railway.py

# 3. 验证迁移
python verify_migration.py
```

### 4. 在 Render 配置环境变量

访问 Render Dashboard，添加以下环境变量：

```env
PYTHON_VERSION=3.9.16
FLASK_ENV=production
SECRET_KEY=生成一个强密钥
MYSQL_HOST=trolley.proxy.rlwy.net
MYSQL_PORT=53176
MYSQL_USER=root
MYSQL_PASSWORD=HGbKlRAozMzZiIbvMcEXeiZUKgHoJxXr
MYSQL_DATABASE=railway
```

#### 生成强密钥：
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## 🔍 测试连接

### 使用 MySQL 命令行
```bash
mysql -h trolley.proxy.rlwy.net \
      -u root \
      -pHGbKlRAozMzZiIbvMcEXeiZUKgHoJxXr \
      --port 53176 \
      --protocol=TCP \
      railway
```

### 使用 Python 测试
```python
# test_railway_connection.py
import pymysql
import os

try:
    connection = pymysql.connect(
        host='trolley.proxy.rlwy.net',
        port=53176,
        user='root',
        password='HGbKlRAozMzZiIbvMcEXeiZUKgHoJxXr',
        database='railway',
        ssl_ca='',
        ssl_verify_cert=False,
        ssl_verify_identity=False
    )
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"✅ 成功连接到 Railway MySQL!")
        print(f"   数据库版本: {version[0]}")
        
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"   数据库表数量: {len(tables)}")
        
    connection.close()
    print("✅ 连接测试成功!")
    
except Exception as e:
    print(f"❌ 连接失败: {e}")
```

运行测试：
```bash
python test_railway_connection.py
```

## 📊 Railway 使用情况

### 免费额度
- **每月**: $5 免费额度
- **存储**: 最多 500MB
- **流量**: 约 100GB/月

### 监控使用量
访问 Railway Dashboard 查看：
- 存储使用量
- 流量使用量
- 连接数
- 查询性能

## ⚠️ 注意事项

### 1. 密码安全
- ✅ 已包含在 `.gitignore` 中（.env.railway）
- ❌ 不要将密码提交到 Git
- ✅ 使用环境变量管理敏感信息

### 2. 连接池配置
应用已配置连接池优化：
```python
'pool_recycle': 280,      # 4分40秒回收连接
'pool_pre_ping': True,    # 连接前测试
'pool_size': 10,          # 连接池大小
'max_overflow': 20        # 最大溢出连接
```

### 3. SSL 配置
代码已自动检测 Railway 并启用 SSL：
```python
if 'railway' in HOSTNAME or 'rlwy.net' in HOSTNAME:
    # 自动使用 SSL 连接
```

## 🚀 部署到 Render

### 1. 推送代码
```bash
git add .
git commit -m "配置 Railway MySQL 数据库"
git push origin zmd
```

### 2. 在 Render 创建 Web Service

#### 基本设置
- **Name**: qa-platform
- **Branch**: zmd
- **Runtime**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn --bind 0.0.0.0:$PORT run:app`

#### 环境变量
使用 `.env.railway` 文件中的所有变量

### 3. 部署后初始化
```bash
# 在 Render Shell 中运行
python init_db.py
```

## ✅ 验证部署

### 1. 检查应用状态
访问: `https://your-app.onrender.com`

### 2. 测试功能
- 注册新用户
- 登录系统
- 创建课程
- 发布问题

### 3. 检查数据统一性
- 在不同设备注册相同邮箱
- 应该提示"该邮箱已被注册"

## 📚 相关文档

- `DEPLOYMENT_SUMMARY.md` - 部署方案总结
- `QUICK_START_RENDER.md` - 快速开始指南
- `DATABASE_MIGRATION_GUIDE.md` - 数据迁移指南

## 💡 常见问题

### Q: Railway 会自动休眠吗？
A: 不会，Railway 数据库持续运行。

### Q: 如何备份数据？
A: 
```bash
# 导出数据库
mysqldump -h trolley.proxy.rlwy.net \
          -u root \
          -pHGbKlRAozMzZiIbvMcEXeiZUKgHoJxXr \
          --port 53176 \
          railway > backup.sql

# 导入数据库
mysql -h trolley.proxy.rlwy.net \
      -u root \
      -pHGbKlRAozMzZiIbvMcEXeiZUKgHoJxXr \
      --port 53176 \
      railway < backup.sql
```

### Q: 超过免费额度怎么办？
A: Railway 会提示你升级，可以选择：
1. 优化查询减少资源使用
2. 升级到付费计划（$5/月）
3. 切换到其他免费数据库

### Q: 如何查看数据库日志？
A: 在 Railway Dashboard → 你的项目 → MySQL → Logs

---

**准备好了吗？开始部署吧！** 🎉
