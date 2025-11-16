# 🌐 生产环境部署指南 (Render + Railway)

## 📋 目录
1. [部署架构概览](#部署架构概览)
2. [为什么选择这个方案](#为什么选择这个方案)
3. [快速部署步骤](#快速部署步骤)
4. [环境变量配置](#环境变量配置)
5. [部署验证](#部署验证)
6. [常见问题](#常见问题)

---

## 🏗️ 部署架构概览

### 系统架构图
```
┌─────────────────────────────────────────────────────────────┐
│                      用户访问                               │
│                         ↓                                   │
│                 Render Web Service                          │
│           (Flask应用 + SocketIO + 自动HTTPS)                │
│                         ↓                                   │
│                  Railway MySQL                              │
│           (数据库服务 + 自动备份)                           │
│                         ↓                                   │
│              163邮箱SMTP服务                                │
│           (邮件验证码 + 通知)                               │
└─────────────────────────────────────────────────────────────┘
```

### 服务配置详情

#### Render Web Service (免费套餐)
| 配置项 | 规格 |
|--------|------|
| 内存 | 512MB |
| CPU | 0.1 vCPU (共享) |
| 存储 | 持久化存储（二维码图片） |
| 流量 | 100GB/月 |
| 构建时间 | ~3分钟 |
| 特性 | 15分钟无活动自动休眠 |
| 域名 | 自动HTTPS证书 |

#### Railway MySQL (免费套餐)
| 配置项 | 规格 |
|--------|------|
| 内存 | 512MB |
| 存储 | 5GB |
| 连接数 | 100 |
| 备份 | 自动每日备份 |
| 流量 | 无限制 |
| 特性 | 高可用，全球CDN |

---

## 💡 为什么选择这个方案

### ✅ 优势

1. **完全免费**
   - Render免费套餐: 750小时/月
   - Railway免费套餐: $5额度/月（足够使用）
   - 总成本: **$0/月**

2. **零运维**
   - 无需管理服务器
   - 自动扩展和负载均衡
   - 自动备份和恢复
   - 24/7监控和告警

3. **开发友好**
   - GitHub自动部署
   - 推送代码即上线
   - 实时日志查看
   - 简单的环境变量管理

4. **生产级别**
   - 自动HTTPS证书
   - 全球CDN加速
   - DDoS防护
   - 99.9%可用性保证

### ❌ 限制

1. **性能限制**
   - 免费套餐CPU和内存有限
   - 15分钟无活动会休眠
   - 首次唤醒需要30秒左右

2. **存储限制**
   - Railway数据库最大5GB
   - Render文件存储有限

3. **流量限制**
   - Render: 100GB/月
   - Railway: 无限制但有CPU时长限制

### 🆚 与其他方案对比

| 方案 | 成本 | 难度 | 性能 | 推荐度 |
|------|------|------|------|--------|
| Render + Railway | 免费 | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Heroku | $7/月起 | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| AWS EC2 | $10/月起 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| 自建服务器 | 硬件成本 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ |

---

## 🚀 快速部署步骤

### 前置准备

1. **GitHub账号** - 用于代码托管和自动部署
2. **163邮箱** - 用于发送验证码和通知
3. **邮箱授权码** - 在163邮箱设置中开启SMTP并获取授权码

### Step 1: 准备Railway数据库

#### 1.1 创建Railway账号
```
1. 访问 https://railway.app
2. 点击 "Start a New Project"
3. 使用GitHub登录
```

#### 1.2 创建MySQL数据库
```
1. 点击 "New Project"
2. 选择 "Provision MySQL"
3. 等待数据库创建完成（约1分钟）
```

#### 1.3 获取数据库连接信息
```
1. 点击MySQL服务
2. 进入 "Connect" 标签
3. 复制以下信息：
   - MYSQL_HOST: xxxxx.railway.app
   - MYSQL_PORT: 6379
   - MYSQL_USER: root
   - MYSQL_PASSWORD: xxxxxxxxxx
   - MYSQL_DATABASE: railway
```

#### 1.4 测试连接（可选）
```bash
# 使用命令行测试
mysql -h your-host.railway.app \
      -P 6379 \
      -u root \
      -p your-password \
      railway

# 或使用Python测试
python test_railway_connection.py
```

---

### Step 2: 部署到Render

#### 2.1 创建Render账号
```
1. 访问 https://render.com
2. 点击 "Get Started"
3. 使用GitHub登录
```

#### 2.2 连接GitHub仓库
```
1. 点击 "New +" → "Web Service"
2. 点击 "Connect a repository"
3. 选择你的项目仓库
4. 点击 "Connect"
```

#### 2.3 配置Web Service
```
Name: qa-education-platform
Environment: Python 3
Region: 选择最近的区域（Singapore推荐）
Branch: zmd（或main）
Build Command: pip install -r requirements.txt
Start Command: gunicorn -k eventlet -w 1 run:app
```

#### 2.4 配置环境变量

点击 "Environment" 标签，添加以下变量：

**Python配置**
```env
PYTHON_VERSION=3.9.16
FLASK_ENV=production
```

**安全配置**
```env
SECRET_KEY=<生成方法见下方>
```

**Railway数据库配置**
```env
MYSQL_HOST=your-host.railway.app
MYSQL_PORT=6379
MYSQL_USER=root
MYSQL_PASSWORD=your-railway-password
MYSQL_DATABASE=railway
```

**邮件配置**
```env
MAIL_SERVER=smtp.163.com
MAIL_PORT=25
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@163.com
MAIL_PASSWORD=your-163-auth-code
MAIL_DEFAULT_SENDER=your-email@163.com
```

**生成SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

#### 2.5 开始部署
```
1. 检查所有环境变量
2. 点击 "Create Web Service"
3. 等待构建完成（约3-5分钟）
4. 查看日志确认部署成功
```

---

### Step 3: 初始化数据库

#### 3.1 自动初始化
Render会在首次部署时自动运行 `init_db.py`，创建：
- 所有数据表
- 默认管理员账号: `admin@example.com` / `admin123`

#### 3.2 手动初始化（如果需要）
```bash
# 1. 在Render Shell中运行
python init_db.py

# 2. 或通过本地连接Railway运行
export MYSQL_HOST=your-host.railway.app
export MYSQL_PORT=6379
export MYSQL_USER=root
export MYSQL_PASSWORD=your-password
export MYSQL_DATABASE=railway

python init_db.py
```

---

## 🔍 部署验证

### 访问你的应用

Render会提供一个域名，例如：
```
https://qa-education-platform-xxxx.onrender.com
```

### 验证清单

#### ✅ 基础功能
- [ ] 首页能正常访问
- [ ] 静态资源（CSS/JS）加载正常
- [ ] 页面样式显示正确

#### ✅ 用户认证
- [ ] 注册页面能打开
- [ ] 能收到验证码邮件
- [ ] 注册成功
- [ ] 登录功能正常
- [ ] 退出登录正常

#### ✅ 课程功能
- [ ] 能创建新课程
- [ ] 能查看课程列表
- [ ] 能选修课程
- [ ] 能查看课程详情

#### ✅ 活动功能
- [ ] 能创建活动（投票/问答/Quiz）
- [ ] 能设置活动时长（时/分/秒）
- [ ] 能生成二维码
- [ ] 能启动活动
- [ ] 倒计时正常工作
- [ ] 能提交答案
- [ ] 提交后有成功反馈

#### ✅ 二维码功能
- [ ] 二维码能正常生成
- [ ] 二维码图片能显示
- [ ] 扫码能打开注册页面
- [ ] 快速注册能成功
- [ ] 临时密码邮件能收到

#### ✅ AI功能
- [ ] 文本生成问题正常
- [ ] 文件上传功能正常
- [ ] PDF/Word/PPT能解析
- [ ] 生成的问题能使用

#### ✅ 实时功能
- [ ] Socket.IO连接正常
- [ ] 活动状态实时更新
- [ ] 倒计时实时显示
- [ ] 按钮状态自动更新

### 检查日志

在Render Dashboard查看日志：
```
1. 进入你的Web Service
2. 点击 "Logs" 标签
3. 查看是否有错误信息
```

常见的成功日志：
```
==> Building...
==> Installing dependencies
==> Starting server
 * Running on http://0.0.0.0:10000
```

---

## ⚙️ 环境变量详解

### 必需的环境变量

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| PYTHON_VERSION | Python版本 | 3.9.16 |
| FLASK_ENV | Flask环境 | production |
| SECRET_KEY | Flask密钥 | 随机64位十六进制 |
| MYSQL_HOST | 数据库主机 | xxx.railway.app |
| MYSQL_PORT | 数据库端口 | 6379 |
| MYSQL_USER | 数据库用户 | root |
| MYSQL_PASSWORD | 数据库密码 | xxxxxx |
| MYSQL_DATABASE | 数据库名 | railway |
| MAIL_USERNAME | 邮箱账号 | your@163.com |
| MAIL_PASSWORD | 邮箱授权码 | xxxxxx |

### 可选的环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| MAIL_SERVER | SMTP服务器 | smtp.163.com |
| MAIL_PORT | SMTP端口 | 25 |
| MAIL_USE_TLS | 使用TLS | True |
| MAIL_DEFAULT_SENDER | 默认发件人 | MAIL_USERNAME |

---

## 🐛 常见问题

### Q1: 部署成功但访问超时

**症状：** 域名可以访问，但页面加载很慢或超时

**原因：**
1. 免费套餐休眠，首次访问需要唤醒
2. 数据库连接配置错误

**解决方案：**
```bash
# 1. 检查Render日志
# 查看是否有数据库连接错误

# 2. 验证Railway数据库
# 确认环境变量正确

# 3. 等待30秒让服务唤醒
# 首次访问需要时间
```

### Q2: 邮件发送失败

**症状：** 注册时无法收到验证码

**原因：**
1. 163邮箱SMTP未开启
2. 授权码错误
3. 邮件被拦截

**解决方案：**
```bash
# 1. 检查163邮箱设置
# 确保SMTP服务已开启

# 2. 重新获取授权码
# 使用授权码而非登录密码

# 3. 测试邮件功能
python diagnose_email.py
```

### Q3: 二维码图片不显示

**症状：** 二维码生成成功但图片显示404

**原因：**
1. 静态文件路径配置错误
2. Render持久化存储未启用

**解决方案：**
```bash
# 1. 检查static/qrcodes目录
# 确保在.gitignore中但在Render中存在

# 2. 启用持久化存储
# Render Dashboard → Storage → Add Disk
# Mount Path: /opt/render/project/src/static/qrcodes
```

### Q4: 数据库连接失败

**症状：** 启动时报错 "Can't connect to MySQL server"

**原因：**
1. Railway数据库环境变量错误
2. 网络连接问题
3. Railway数据库未启动

**解决方案：**
```bash
# 1. 验证Railway连接
python test_railway_connection.py

# 2. 检查环境变量
# 确保MYSQL_HOST, PORT, PASSWORD正确

# 3. 重启Railway数据库
# Railway Dashboard → Restart
```

### Q5: Socket.IO连接失败

**症状：** 实时功能不工作，倒计时不更新

**原因：**
1. WebSocket连接被阻止
2. eventlet未正确配置

**解决方案：**
```bash
# 1. 确认Start Command正确
gunicorn -k eventlet -w 1 run:app

# 2. 检查浏览器控制台
# 查看Socket.IO连接错误

# 3. 使用polling降级
# 修改socket_events.py中的配置
```

### Q6: 应用频繁休眠

**症状：** 每次访问都要等待很久

**原因：** Render免费套餐15分钟无活动自动休眠

**解决方案：**
```bash
# 方案1: 使用定时Ping服务
# 注册 UptimeRobot 定期访问你的域名

# 方案2: 升级到付费套餐
# Render Pro: $7/月，无休眠

# 方案3: 接受休眠
# 首次访问等待30秒
```

---

## 📊 性能优化

### 数据库优化

```python
# 1. 使用连接池
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    pool_recycle=3600,
    pool_pre_ping=True
)

# 2. 优化查询
# 使用索引加速查询
# 避免N+1查询问题
# 使用延迟加载
```

### 静态文件优化

```python
# 1. 启用缓存
# 在Nginx配置中设置缓存头

# 2. 压缩静态文件
# Render自动启用gzip压缩

# 3. 使用CDN
# 考虑使用Cloudflare CDN
```

### 应用性能优化

```python
# 1. 使用缓存
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# 2. 异步处理
# 邮件发送使用后台任务
# AI处理使用队列

# 3. 优化查询
# 减少数据库查询次数
# 使用批量操作
```

---

## 📚 相关文档

- [RENDER_DEPLOYMENT_GUIDE.md](RENDER_DEPLOYMENT_GUIDE.md) - Render详细部署指南
- [RAILWAY_SETUP_GUIDE.md](RAILWAY_SETUP_GUIDE.md) - Railway数据库配置
- [RAILWAY_COMPLETE.md](RAILWAY_COMPLETE.md) - Railway部署完成报告
- [DEPLOYMENT.md](DEPLOYMENT.md) - 通用部署说明

---

## 🎯 总结

使用Render + Railway部署的优势：
- ✅ **免费**: 完全免费的生产环境
- ✅ **简单**: 几分钟即可部署上线
- ✅ **可靠**: 99.9%可用性保证
- ✅ **安全**: 自动HTTPS和DDoS防护
- ✅ **可扩展**: 随时升级到付费套餐

这是教育项目和小型应用的完美选择！

---

**部署日期**: 2025年11月11日  
**部署分支**: zmd  
**文档版本**: 1.0
