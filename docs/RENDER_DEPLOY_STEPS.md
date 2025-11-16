# 🚀 Render 部署详细步骤（图文版）

## 📋 前提条件

✅ Railway 数据库已创建并迁移完成  
✅ 代码已推送到 GitHub `zmd` 分支  
✅ 准备好部署了！

---

## 🎯 Render 部署步骤

### 步骤 1: 访问 Render 并登录

1. 打开浏览器访问：https://render.com/
2. 点击右上角 **Sign In**
3. 选择 **Sign in with GitHub**（推荐）
4. 授权 Render 访问你的 GitHub

---

### 步骤 2: 创建新的 Web Service

1. 登录后，点击右上角 **New +** 按钮
2. 在下拉菜单中选择 **Web Service**

```
┌─────────────────────────────┐
│  Dashboard                  │
│                             │
│  New + ▼                    │
│    ├─ Web Service      ←─── 点这里
│    ├─ Static Site           │
│    ├─ PostgreSQL            │
│    └─ Redis                 │
└─────────────────────────────┘
```

---

### 步骤 3: 连接 GitHub 仓库

#### 选项 A: 如果是第一次使用 Render

1. 看到 "Connect a repository" 页面
2. 点击 **Connect GitHub**
3. 在弹出窗口中，找到并选择：
   ```
   COMP5241-2526Sem1/groupproject-team_5
   ```
4. 点击 **Install** 或 **Authorize**

#### 选项 B: 如果之前已经连接过 GitHub

1. 在仓库列表中找到：
   ```
   COMP5241-2526Sem1/groupproject-team_5
   ```
2. 点击右侧的 **Connect** 按钮

#### 看不到你的仓库？

点击 **Configure GitHub App** → 选择组织 `COMP5241-2526Sem1` → 授权该仓库

---

### 步骤 4: 配置 Web Service

#### 4.1 基本设置

填写以下信息：

```yaml
Name: qa-platform-zmd
  说明：这是你的应用名称，会成为 URL 的一部分
  示例 URL：https://qa-platform-zmd.onrender.com

Branch: zmd
  说明：选择 zmd 分支（重要！）
  
Region: Singapore
  说明：选择离你最近的区域（亚洲选 Singapore）

Root Directory: (留空)
  说明：项目在仓库根目录，不需要填
```

#### 4.2 运行时设置

```yaml
Runtime: Python 3
  说明：选择 Python 3（不要选 Docker！）
  
Build Command:
  pip install -r requirements.txt
  
  说明：Render 会自动运行这个命令安装依赖
  
Start Command:
  gunicorn --bind 0.0.0.0:$PORT run:app
  
  说明：使用 gunicorn 启动 Flask 应用
```

#### 4.3 实例类型

```yaml
Instance Type: Free
  说明：选择免费版（750小时/月）
  
  免费版特点：
  - ✅ 完全免费
  - ⚠️ 15分钟无访问会休眠
  - ⚠️ 冷启动需要 30-60 秒
```

---

### 步骤 5: 配置环境变量（重要！🔥）

向下滚动到 **Environment Variables** 部分

#### 点击 **Add Environment Variable** 添加以下变量：

##### 变量 1: Python 版本
```
Key:   PYTHON_VERSION
Value: 3.9.16
```

##### 变量 2: Flask 环境
```
Key:   FLASK_ENV
Value: production
```

##### 变量 3: 密钥（需要生成）
```
Key:   SECRET_KEY
Value: <运行下面命令生成>
```

生成密钥：
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```
复制输出的长字符串

##### 变量 4-8: Railway 数据库配置

```
Key:   MYSQL_HOST
Value: trolley.proxy.rlwy.net

Key:   MYSQL_PORT
Value: 53176

Key:   MYSQL_USER
Value: root

Key:   MYSQL_PASSWORD
Value: HGbKlRAozMzZiIbvMcEXeiZUKgHoJxXr

Key:   MYSQL_DATABASE
Value: railway
```

#### 环境变量检查清单

- [ ] PYTHON_VERSION = 3.9.16
- [ ] FLASK_ENV = production
- [ ] SECRET_KEY = (已生成的密钥)
- [ ] MYSQL_HOST = trolley.proxy.rlwy.net
- [ ] MYSQL_PORT = 53176
- [ ] MYSQL_USER = root
- [ ] MYSQL_PASSWORD = HGbKlRAozMzZiIbvMcEXeiZUKgHoJxXr
- [ ] MYSQL_DATABASE = railway

总共 **8 个环境变量**

---

### 步骤 6: 创建 Web Service

1. 检查所有配置
2. 点击页面底部的 **Create Web Service** 按钮
3. Render 开始构建和部署

---

### 步骤 7: 等待部署完成

#### 部署过程（约 2-5 分钟）

你会看到实时日志：

```
==> Cloning from GitHub...
✓ Cloned repository

==> Downloading cache...
✓ Cache downloaded

==> Installing dependencies...
Collecting Flask...
Collecting SQLAlchemy...
... (更多依赖)
✓ Dependencies installed

==> Starting service...
[2024-11-10 10:00:00] [1] [INFO] Starting gunicorn 21.2.0
[2024-11-10 10:00:00] [1] [INFO] Listening at: http://0.0.0.0:10000
✓ Service started

==> Your service is live 🎉
```

#### 常见日志

✅ **成功标志：**
```
Your service is live 🎉
```

⚠️ **可能的警告（可忽略）：**
```
Warning: This is a development server. Do not use it in production
```
（这个警告是针对 Flask 自带服务器的，我们用的是 gunicorn，所以没问题）

❌ **错误标志：**
```
Error: Failed to bind to $PORT
ModuleNotFoundError: No module named 'xxx'
```
（如果看到这些，检查配置是否正确）

---

### 步骤 8: 测试部署的应用

#### 8.1 获取应用 URL

部署成功后，在页面顶部会看到：
```
https://qa-platform-zmd.onrender.com
```

#### 8.2 访问应用

1. 点击 URL 或复制到浏览器
2. **首次访问**可能需要等待 30-60 秒（冷启动）
3. 看到登录页面 = 部署成功！🎉

#### 8.3 测试功能

##### 测试 1: 登录测试
```
使用迁移的账号登录
或使用默认管理员：
  邮箱: admin@example.com
  密码: admin123
```

##### 测试 2: 注册测试
```
注册一个新账号
检查是否能成功创建
```

##### 测试 3: 数据一致性测试
```
1. 在 Render 注册账号 test@example.com
2. 在本地尝试注册相同邮箱（连接 Railway）
3. 应该提示"该邮箱已被注册"
   ✅ 证明共享同一个 Railway 数据库！
```

---

## 🔧 部署后管理

### 查看日志

1. 在 Render Dashboard 点击你的服务
2. 点击左侧 **Logs** 标签
3. 可以看到实时日志和历史日志

### 手动重新部署

1. 点击右上角 **Manual Deploy**
2. 选择 **Deploy latest commit**
3. 或选择特定的 commit 进行部署

### Shell 访问

1. 点击右上角 **Shell** 按钮
2. 可以在线运行命令，例如：
   ```bash
   python init_db.py
   python -c "from app.models import User; print(User.query.count())"
   ```

### 更新环境变量

1. 点击左侧 **Environment** 标签
2. 修改或添加变量
3. 点击 **Save Changes**
4. Render 会自动重新部署

---

## 🎯 完整配置总结

### Render 配置清单

```yaml
# 基本信息
Name: qa-platform-zmd
Repository: COMP5241-2526Sem1/groupproject-team_5
Branch: zmd
Region: Singapore

# 构建配置
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: gunicorn --bind 0.0.0.0:$PORT run:app

# 实例配置
Instance Type: Free

# 环境变量（8个）
PYTHON_VERSION=3.9.16
FLASK_ENV=production
SECRET_KEY=0fc6588d7a2c5e2877f75a0208a8256a7211635164b025e46ee6e565ec192cd3
ARK_API_KEY=
MYSQL_HOST=trolley.proxy.rlwy.net
MYSQL_PORT=53176
MYSQL_USER=root
MYSQL_PASSWORD=HGbKlRAozMzZiIbvMcEXeiZUKgHoJxXr
MYSQL_DATABASE=railway
```

---

## ⚠️ 常见问题

### Q1: 部署失败，提示找不到模块

**原因：** `requirements.txt` 可能不完整

**解决：**
```bash
# 确保 requirements.txt 包含所有依赖
pip freeze > requirements.txt
git add requirements.txt
git commit -m "更新依赖"
git push origin zmd
```

### Q2: 应用启动失败

**检查：**
1. 环境变量是否都配置正确
2. Start Command 是否正确：`gunicorn --bind 0.0.0.0:$PORT run:app`
3. `run.py` 是否在仓库根目录

### Q3: 无法连接数据库

**检查：**
1. Railway 数据库是否正在运行
2. MYSQL_* 环境变量是否正确
3. 在 Render Shell 中测试：
   ```bash
   python3 test_railway_connection.py
   ```

### Q4: 应用很慢或经常超时

**原因：** 免费版会休眠

**解决方案：**
1. 接受免费版限制（适合学习/测试）
2. 升级到 Starter 计划（$7/月，不休眠）
3. 使用 UptimeRobot 定期 ping（保持唤醒）

### Q5: 想切换到其他分支

1. 在 Render Dashboard → Settings
2. 找到 **Branch** 设置
3. 改为 `main` 或其他分支
4. 点击 **Save** → 自动重新部署

---

## 🎉 部署成功！

### 你现在拥有：

- ✅ 运行在 Render 的 Flask 应用
- ✅ 托管在 Railway 的 MySQL 数据库
- ✅ 自动 HTTPS 加密
- ✅ 公网可访问的 URL
- ✅ 完全免费的部署方案

### 下一步：

1. **测试所有功能** - 确保一切正常
2. **分享 URL** - 给团队成员测试
3. **监控使用情况** - 查看 Railway 和 Render 用量
4. **合并到 main** - 测试通过后合并分支
5. **设置自动部署** - main 分支自动部署到生产环境

---

## 📚 相关文档

- `RAILWAY_COMPLETE.md` - Railway 数据库配置
- `DATABASE_MIGRATION_FAQ.md` - 数据库迁移常见问题
- `DEPLOYMENT_SUMMARY.md` - 部署方案总结

---

**祝部署顺利！** 🚀

有任何问题随时查看文档或询问。
