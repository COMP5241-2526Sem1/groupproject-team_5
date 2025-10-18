# 🚀 Quick Start Guide - QA教育平台

欢迎使用QA教育平台！本指南将帮助您快速部署和运行平台。

## 📋 系统要求

- **Python**: 3.8 或更高版本
- **数据库**: MySQL 5.7+ 或 MariaDB 10.2+
- **系统**: macOS, Linux, Windows
- **内存**: 至少 512MB RAM
- **存储**: 至少 1GB 可用空间

## ⚡ 5分钟快速部署

### 步骤 1: 克隆项目

```bash
# 如果从Git仓库克隆
git clone <repository-url>
cd final_integrated_platform

# 或者直接使用现有项目目录
cd /path/to/final_integrated_platform
```

### 步骤 2: 创建虚拟环境

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 步骤 3: 安装依赖

```bash
# 安装所有必需的包
pip install -r requirements.txt
```

### 步骤 4: 配置数据库

```bash
# 方法1: 使用现有数据库
# 确保MySQL服务运行，并已有classroom数据库

# 方法2: 初始化新数据库
python run.py init-db
```

### 步骤 5: 启动应用

```bash
# 启动开发服务器
python run.py

# 应用将在 http://localhost:5001 启动
```

## 🎯 首次使用

### 默认管理员账户

```
邮箱: admin@example.com
密码: admin123
角色: 管理员
```

### 创建测试用户

1. **访问注册页面**: http://localhost:5001/register
2. **注册学生账户**:
   - 用户名: student1
   - 邮箱: student1@example.com
   - 密码: student123
   - 角色: 学生

3. **注册教师账户**:
   - 用户名: teacher1
   - 邮箱: teacher1@example.com
   - 密码: teacher123
   - 角色: 教师

## 🏠 功能导览

### 管理员功能
- **Dashboard**: http://localhost:5001/dashboard
- **用户管理**: 查看所有用户统计
- **课程管理**: 监控所有课程
- **系统统计**: 查看平台使用数据

### 教师功能
- **创建课程**: 在Dashboard中创建新课程
- **管理问答**: 回答学生问题，标记最佳答案
- **查看统计**: 监控课程活跃度

### 学生功能
- **选修课程**: 浏览并选修感兴趣的课程
- **提问交流**: 在课程中提问和回答
- **查看回复**: 查看别人对我问题的回复
- **投票互动**: 对回答进行👍👎投票

## 📱 界面预览

### 学生Dashboard
- **我的课程**: 显示前4门课程，点击"查看所有课程"查看完整列表
- **Recent Replies**: 显示最新4条回复，点击"查看所有回复"查看全部
- **统计信息**: 选修课程数、活动数、回复数等

### 问答系统
- **问题列表**: 分页显示课程问题
- **问题详情**: 查看问题和所有回答
- **投票系统**: 支持点赞/点踩
- **分页导航**: 智能页码显示

## 🔧 配置选项

### 数据库配置

在 `app/__init__.py` 中修改数据库连接：

```python
# MySQL配置示例
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://username:password@localhost/database_name'
```

### 端口配置

在 `run.py` 中修改端口：

```python
# 默认端口5001，可修改为其他端口
socketio.run(app, host='0.0.0.0', port=5002, debug=True)
```

### AI功能配置

在 `app/ai_utils.py` 中配置AI服务：

```python
# 配置AI API密钥和端点
ARK_API_KEY = "your-api-key"
ARK_BASE_URL = "your-api-endpoint"
```

## 🐛 常见问题

### Q1: 启动时提示端口被占用
```bash
# 查找并结束占用进程
lsof -ti:5001 | xargs kill -9

# 或者修改端口
python run.py --port 5002
```

### Q2: 数据库连接失败
```bash
# 确保MySQL服务运行
sudo service mysql start  # Linux
brew services start mysql # macOS

# 检查数据库是否存在
mysql -u root -p
mysql> SHOW DATABASES;
mysql> CREATE DATABASE classroom CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Q3: 缺少依赖包
```bash
# 升级pip并重新安装
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Q4: 模板找不到
```bash
# 确保在正确目录启动
cd /path/to/final_integrated_platform
python run.py
```

## 📊 性能优化

### 开发环境优化
```bash
# 启用调试模式
export FLASK_ENV=development
export FLASK_DEBUG=1
python run.py
```

### 生产环境部署
```bash
# 使用生产WSGI服务器
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 "app:create_app()"
```

## 🔐 安全设置

### 密钥配置
```python
# 在生产环境中设置强密钥
SECRET_KEY = 'your-secret-key-here'
```

### 数据库安全
```bash
# 创建专用数据库用户
mysql> CREATE USER 'qa_platform'@'localhost' IDENTIFIED BY 'strong_password';
mysql> GRANT ALL PRIVILEGES ON classroom.* TO 'qa_platform'@'localhost';
mysql> FLUSH PRIVILEGES;
```

## 📚 下一步

1. **阅读完整文档**:
   - [项目结构说明](PROJECT_STRUCTURE.md)
   - [部署指南](DEPLOYMENT.md)
   - [用户手册](USER_MANUAL.md)

2. **探索功能**:
   - 创建课程并邀请学生
   - 尝试AI问题生成功能
   - 测试投票和分页系统

3. **自定义开发**:
   - 修改模板样式
   - 添加新功能模块
   - 集成第三方服务

## 🆘 获取帮助

- **技术问题**: 查看错误日志和控制台输出
- **功能疑问**: 参考用户手册
- **开发指导**: 查看项目结构文档

---

🎉 **恭喜！您已成功启动QA教育平台！**

现在可以访问 http://localhost:5001 开始使用平台功能。
