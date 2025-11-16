# Render 部署完整指南

## 📋 目录
1. [部署方案对比](#部署方案对比)
2. [为什么选择这个方案](#为什么选择这个方案)
3. [PlanetScale 数据库设置](#planetscale-数据库设置)
4. [Render 部署步骤](#render-部署步骤)
5. [环境变量配置](#环境变量配置)
6. [常见问题](#常见问题)

---

## 🎯 部署方案对比

### 方案一：Render Web Service（推荐 ⭐⭐⭐⭐⭐）
**不使用 Docker，直接部署 Python 应用**

✅ **优势：**
- 配置简单，Render 自动识别 Python 项目
- 免费套餐足够用（750小时/月）
- 自动 HTTPS 证书
- 自动从 GitHub 部署
- 构建速度快
- 日志查看方便

❌ **劣势：**
- 空闲 15 分钟后休眠（免费套餐）
- 每月 750 小时限制

### 方案二：Render + Docker
**使用 Docker 容器部署**

✅ **优势：**
- 环境一致性（开发和生产环境完全相同）
- 便于本地测试
- 可以精确控制依赖版本

❌ **劣势：**
- 构建时间更长
- 配置相对复杂
- Docker 镜像占用空间大
- 对于简单的 Flask 应用来说有点"杀鸡用牛刀"

### 方案三：本地 Docker + 其他云服务
略...

---

## 💡 为什么选择这个方案

### 推荐方案：**Render Web Service + PlanetScale MySQL**

#### 为什么不用 Docker？

对于你的 Flask 项目，**不需要使用 Docker**，原因如下：

1. **Render 原生支持 Python**
   - Render 会自动检测 `requirements.txt`
   - 自动创建 Python 虚拟环境
   - 自动安装依赖

2. **部署更简单**
   - 不需要维护 Dockerfile
   - 不需要理解 Docker 概念
   - 配置项更少，出错概率低

3. **性能更好**
   - 没有 Docker 层的开销
   - 冷启动更快
   - 构建速度快 2-3 倍

4. **成本更低**
   - Docker 镜像占用更多存储空间
   - 构建时间更长 = 消耗更多资源

#### Docker 什么时候需要？

只有在以下情况才需要 Docker：
- 需要特殊系统依赖（如 C++ 库、特定系统工具）
- 多服务架构（前端 + 后端 + 数据库）
- 需要完全相同的开发和生产环境
- 需要部署到不支持 Python 的平台

**你的项目是简单的 Flask 应用，不需要 Docker！**

---

## 🗄️ PlanetScale 数据库设置

### 什么是 PlanetScale？

PlanetScale 是一个**无服务器 MySQL 数据库**平台：
- ✅ 免费套餐：5GB 存储 + 10 亿行读取/月
- ✅ 自动备份和恢复
- ✅ 全球 CDN 加速
- ✅ 自动扩展
- ✅ 无需管理服务器

### 为什么用 PlanetScale？

1. **统一数据库** ✅
   - 所有用户共享同一个数据库
   - 不会出现"一个邮箱两个用户"的问题
   - 数据持久化，不会丢失

2. **比 Render 自带数据库好**
   - Render 的 PostgreSQL 免费版只有 1GB
   - PlanetScale 免费版有 5GB
   - PlanetScale 专注于数据库，更可靠

3. **与 Render 完美配合**
   - 直接提供连接字符串
   - 支持 SSL 加密连接
   - 低延迟

### PlanetScale 设置步骤

#### 步骤 1：创建账号
1. 访问 https://planetscale.com/
2. 使用 GitHub 账号登录
3. 选择免费套餐（Hobby）

#### 步骤 2：创建数据库
```bash
# 数据库名称建议
Name: qa-education-platform
Region: AWS us-east-1 (或选择离你最近的)
```

#### 步骤 3：获取连接字符串
1. 点击数据库 → "Connect"
2. 选择 "Connect with: Python"
3. 创建密码（New password）
4. 复制连接信息：

```env
MYSQL_HOST=aws.connect.psdb.cloud
MYSQL_USERNAME=xxxxxxxxx
MYSQL_PASSWORD=pscale_pw_xxxxxxxxx
MYSQL_DATABASE=qa-education-platform
```

#### 步骤 4：连接字符串格式
```
mysql://username:password@host/database?sslmode=require
```

---

## 🚀 Render 部署步骤

### 前置准备

1. **确保代码已推送到 GitHub**
   ```bash
   git add .
   git commit -m "准备部署到 Render"
   git push origin zmd
   ```

2. **检查必需文件**
   - ✅ `requirements.txt` - Python 依赖
   - ✅ `run.py` - 应用入口
   - ✅ `.gitignore` - 忽略敏感文件

### 步骤 1：创建 Render 账号

1. 访问 https://render.com/
2. 使用 GitHub 账号登录
3. 授权 Render 访问你的仓库

### 步骤 2：创建 Web Service

1. 点击 "New +" → "Web Service"
2. 选择你的 GitHub 仓库：`groupproject-team_5`
3. 配置服务：

```yaml
Name: qa-education-platform
Region: Oregon (US West) 或离你最近的
Branch: zmd  # 在 zmd 分支测试
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: gunicorn --bind 0.0.0.0:$PORT run:app
```

### 步骤 3：配置环境变量

在 Render 的 "Environment" 标签页添加：

```env
# 必需的环境变量
PYTHON_VERSION=3.9.16

# Flask 配置
SECRET_KEY=你的随机密钥（至少32位）
FLASK_ENV=production

# PlanetScale 数据库配置
MYSQL_HOST=aws.connect.psdb.cloud
MYSQL_PORT=3306
MYSQL_USER=你的PlanetScale用户名
MYSQL_PASSWORD=你的PlanetScale密码
MYSQL_DATABASE=qa-education-platform

# 可选：AI API（如果使用）
ARK_API_KEY=your_ark_api_key
OPENAI_API_KEY=your_openai_api_key

# 邮件配置（如果需要）
MAIL_SERVER=smtp.163.com
MAIL_PORT=465
MAIL_USERNAME=your_email@163.com
MAIL_PASSWORD=your_email_password
```

#### 生成 SECRET_KEY
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 步骤 4：部署

1. 点击 "Create Web Service"
2. Render 会自动：
   - 克隆你的代码
   - 安装依赖
   - 启动应用
3. 等待 3-5 分钟
4. 部署完成后会得到 URL：`https://qa-education-platform.onrender.com`

### 步骤 5：初始化数据库

首次部署后需要创建数据库表：

**方法一：使用 Render Shell**
```bash
# 在 Render Dashboard 点击 "Shell"
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
...     print("数据库表创建成功！")
```

**方法二：添加初始化脚本**
创建 `init_db.py`：
```python
from app import create_app, db

app = create_app()
with app.app_context():
    db.create_all()
    print("数据库初始化完成！")
```

然后在 Render Shell 运行：
```bash
python init_db.py
```

---

## ⚙️ 环境变量配置

### 完整的 `.env.example`

创建一个环境变量模板文件：

```env
# Flask 配置
SECRET_KEY=your-secret-key-change-this
FLASK_ENV=development
DEBUG=True

# 数据库配置
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3307
MYSQL_USER=root
MYSQL_PASSWORD=1234
MYSQL_DATABASE=platform

# 生产环境数据库（PlanetScale）
# MYSQL_HOST=aws.connect.psdb.cloud
# MYSQL_PORT=3306
# MYSQL_USER=your_planetscale_username
# MYSQL_PASSWORD=pscale_pw_xxxxxxxxx
# MYSQL_DATABASE=qa-education-platform

# AI API 密钥（可选）
ARK_API_KEY=your_ark_api_key
OPENAI_API_KEY=your_openai_api_key

# 邮件配置
MAIL_SERVER=smtp.163.com
MAIL_PORT=465
MAIL_USERNAME=your_email@163.com
MAIL_PASSWORD=your_email_password
MAIL_DEFAULT_SENDER=your_email@163.com
```

### 本地开发 vs 生产环境

| 环境 | 数据库 | 配置 |
|------|--------|------|
| 本地开发 | 本地 MySQL (127.0.0.1:3307) | `.env` 文件 |
| 生产环境 | PlanetScale (云端) | Render 环境变量 |

---

## 📝 需要修改的代码

### 1. 修改 `requirements.txt`

添加生产环境需要的包：

```txt
# Core Flask packages
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Login==0.6.3
Flask-Mail==0.9.1
Flask-SocketIO==5.3.6
Flask-WTF==1.2.1

# Database
PyMySQL==1.1.0
cryptography==41.0.7  # PlanetScale SSL 需要

# Forms and validation
WTForms==3.1.1

# Security
Werkzeug==2.3.7

# Socket.IO for real-time features
python-socketio==5.10.0
python-engineio>=4.8.0

# Other utilities
email-validator==2.1.0
requests==2.31.0

# Production server
gunicorn==21.2.0  # 生产环境 WSGI 服务器
```

### 2. 修改 `app/__init__.py`

优化数据库连接配置：

```python
def create_app():
    """Application factory pattern"""
    
    app = Flask(__name__, template_folder=template_dir)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # 数据库配置
    # 优先使用环境变量，否则使用本地配置
    HOSTNAME = os.getenv('MYSQL_HOST', '127.0.0.1')
    PORT = os.getenv('MYSQL_PORT', '3307')
    USERNAME = os.getenv('MYSQL_USER', 'root')
    PASSWORD = os.getenv('MYSQL_PASSWORD', '1234')
    DATABASE = os.getenv('MYSQL_DATABASE', 'platform')
    
    # 构建数据库 URI
    # 生产环境（PlanetScale）需要 SSL
    if 'psdb.cloud' in HOSTNAME or os.getenv('FLASK_ENV') == 'production':
        # PlanetScale 连接
        app.config['SQLALCHEMY_DATABASE_URI'] = (
            f'mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}'
            f'?charset=utf8mb4&ssl_ca=&ssl_verify_cert=false'
        )
    else:
        # 本地开发连接
        app.config['SQLALCHEMY_DATABASE_URI'] = (
            f'mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}'
            f'?charset=utf8mb4'
        )
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_recycle': 280,  # 避免连接超时
        'pool_pre_ping': True,  # 连接前测试
    }
    
    # ... 其余配置
```

### 3. 修改 `run.py`

支持 Render 的端口配置：

```python
def main():
    # 环境变量配置
    if not os.environ.get('SECRET_KEY'):
        os.environ['SECRET_KEY'] = 'dev-secret-key-change-in-production'
    
    # 创建应用
    app = create_app()
    
    # 获取端口（Render 会设置 PORT 环境变量）
    port = int(os.environ.get('PORT', 5000))
    
    # 运行应用
    if os.environ.get('FLASK_ENV') == 'production':
        # 生产环境由 gunicorn 启动，这里不会执行
        pass
    else:
        # 开发环境使用 Flask 开发服务器
        print(f"🚀 Starting development server on port {port}...")
        socketio.run(app, host='0.0.0.0', port=port, debug=True)

if __name__ == '__main__':
    main()
```

---

## 🔍 部署检查清单

### 部署前检查

- [ ] 代码已推送到 GitHub 的 zmd 分支
- [ ] `requirements.txt` 包含所有依赖
- [ ] 已创建 PlanetScale 数据库
- [ ] 已获取 PlanetScale 连接信息
- [ ] 已生成 SECRET_KEY
- [ ] `.gitignore` 排除了 `.env` 文件

### 部署后检查

- [ ] Render 构建成功（没有错误）
- [ ] 应用可以访问（HTTP 200）
- [ ] 数据库连接成功
- [ ] 可以注册新用户
- [ ] 可以登录
- [ ] 邮箱唯一性检查正常

### 测试步骤

1. **访问应用**
   ```
   https://your-app.onrender.com
   ```

2. **注册测试用户**
   - 使用真实邮箱注册
   - 检查是否成功

3. **尝试重复注册**
   - 使用相同邮箱再次注册
   - 应该显示"邮箱已存在"错误

4. **登录测试**
   - 使用刚注册的账号登录
   - 检查是否能正常访问

---

## 🐛 常见问题

### Q1: 为什么应用启动很慢？
**A:** Render 免费套餐在 15 分钟无活动后会休眠，第一次访问需要"唤醒"，大约需要 30-60 秒。

**解决方案：**
- 付费升级到 Starter 计划（$7/月）
- 使用 UptimeRobot 等服务定时 ping 你的应用

### Q2: 数据库连接失败
**A:** 检查 PlanetScale 连接信息是否正确。

**排查步骤：**
```bash
# 在 Render Shell 中测试连接
python
>>> import pymysql
>>> conn = pymysql.connect(
...     host='your-host.psdb.cloud',
...     user='your-username',
...     password='your-password',
...     database='your-database',
...     ssl={'ssl': True}
... )
>>> print("连接成功！")
```

### Q3: 如何查看日志？
**A:** 
1. Render Dashboard → 你的服务
2. 点击 "Logs" 标签
3. 实时查看应用日志

### Q4: 如何回滚到之前的版本？
**A:**
1. Render Dashboard → 你的服务
2. 点击 "Manual Deploy"
3. 选择之前的 commit
4. 点击 "Deploy"

### Q5: 一个邮箱出现两个用户怎么办？
**A:** 这不应该发生，因为：
1. 数据库有唯一约束
2. 注册时会检查邮箱是否存在

如果真的发生了，检查：
```python
# 在 app/models.py 确保有：
class User(UserMixin, db.Model):
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
```

### Q6: 如何更新代码？
**A:** 
```bash
# 本地修改代码
git add .
git commit -m "更新功能"
git push origin zmd

# Render 会自动检测并重新部署
```

---

## 📊 成本估算

### 免费套餐

| 服务 | 免费额度 | 限制 |
|------|---------|------|
| Render Web Service | 750 小时/月 | 15分钟无活动休眠 |
| PlanetScale | 5GB 存储 + 10亿行读取 | 单数据库 |
| 总计 | **$0/月** | 适合学习和测试 |

### 付费升级（可选）

| 服务 | 价格 | 优势 |
|------|------|------|
| Render Starter | $7/月 | 不休眠 + 更多资源 |
| PlanetScale Scaler | $29/月 | 多数据库 + 更多存储 |

**建议：** 开始使用免费套餐，有需要再升级。

---

## 🎉 下一步

1. **完成部署**
   - 按照本指南完成 PlanetScale 和 Render 设置
   - 测试所有功能

2. **监控和维护**
   - 定期检查日志
   - 监控数据库使用量
   - 备份重要数据

3. **准备合并到 main**
   - 在 zmd 分支充分测试
   - 确认没有问题后合并到 main
   - 可以创建另一个 Render 服务指向 main 分支作为生产环境

---

## 📚 相关资源

- [Render 官方文档](https://render.com/docs)
- [PlanetScale 文档](https://planetscale.com/docs)
- [Flask 部署指南](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [Gunicorn 文档](https://docs.gunicorn.org/)

---

**祝部署顺利！** 🚀

如有问题，请参考本指南的"常见问题"部分或查看日志。
