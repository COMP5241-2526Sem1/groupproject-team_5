# 🚀 部署指南 - QA教育平台

本指南提供QA教育平台的完整部署方案，适用于开发、测试和生产环境。

## 📋 系统要求

### 基础环境
- **Python**: 3.8 或更高版本
- **数据库**: MySQL 5.7+ 或 MariaDB 10.2+
- **操作系统**: macOS, Linux, Windows
- **内存**: 最少 512MB，推荐 2GB+
- **存储**: 最少 1GB 可用空间

### 推荐配置
- **CPU**: 2核心以上
- **内存**: 4GB以上
- **存储**: SSD 硬盘，20GB以上

## ⚡ 快速部署 (开发环境)

### 1. 项目准备

```bash
# 进入项目目录
cd /Users/dududu/Desktop/QA_Platform/final_integrated_platform

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows
```

### 2. 安装依赖

```bash
# 升级pip
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt
```

### 3. 数据库配置

```bash
# 启动MySQL服务
# macOS: brew services start mysql
# Linux: sudo systemctl start mysql

# 创建数据库
mysql -u root -p
mysql> CREATE DATABASE classroom CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
mysql> EXIT;

# 初始化数据库
python run.py init-db
```

### 4. 启动应用

```bash
# 启动开发服务器
python run.py

# 应用将在 http://localhost:5001 运行
```

### 5. 验证部署

访问 http://localhost:5001，使用默认管理员账户：
- 邮箱: admin@example.com
- 密码: admin123

## 🏭 生产环境部署

### 服务器准备

#### Ubuntu/Debian 系统

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装必要软件
sudo apt install -y python3 python3-pip python3-venv \
    mysql-server nginx supervisor git \
    build-essential python3-dev libmysqlclient-dev
```

#### CentOS/RHEL 系统

```bash
# 更新系统
sudo yum update -y

# 安装必要软件
sudo yum install -y python3 python3-pip \
    mysql-server nginx supervisor git \
    gcc python3-devel mysql-devel
```

### 应用部署

#### 1. 创建应用用户和目录

```bash
# 创建专用用户
sudo useradd -r -s /bin/false qa_app

# 创建应用目录
sudo mkdir -p /opt/qa_platform
sudo chown qa_app:qa_app /opt/qa_platform
```

#### 2. 部署应用代码

```bash
# 复制代码到服务器
sudo -u qa_app cp -r /path/to/final_integrated_platform/* /opt/qa_platform/

# 或者从Git克隆
sudo -u qa_app git clone <repository-url> /opt/qa_platform

cd /opt/qa_platform
```

#### 3. 安装Python依赖

```bash
# 创建虚拟环境
sudo -u qa_app python3 -m venv venv

# 安装依赖
sudo -u qa_app ./venv/bin/pip install --upgrade pip
sudo -u qa_app ./venv/bin/pip install -r requirements.txt

# 安装生产服务器
sudo -u qa_app ./venv/bin/pip install gunicorn
```

### 数据库配置

#### 1. MySQL安全设置

```bash
# 运行安全初始化
sudo mysql_secure_installation

# 设置强密码和安全选项
```

#### 2. 创建生产数据库

```bash
mysql -u root -p

mysql> CREATE DATABASE classroom CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
mysql> CREATE USER 'qa_prod'@'localhost' IDENTIFIED BY 'STRONG_PASSWORD_HERE';
mysql> GRANT ALL PRIVILEGES ON classroom.* TO 'qa_prod'@'localhost';
mysql> FLUSH PRIVILEGES;
mysql> EXIT;
```

#### 3. 配置数据库连接

编辑应用配置文件，设置生产数据库连接：

```python
# 在 app/__init__.py 中配置
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://qa_prod:STRONG_PASSWORD@localhost/classroom'
```

#### 4. 初始化数据库

```bash
sudo -u qa_app /opt/qa_platform/venv/bin/python run.py init-db
```

### Web服务器配置

#### 1. Nginx配置

创建 `/etc/nginx/sites-available/qa_platform`:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # 静态文件
    location /static {
        alias /opt/qa_platform/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
        
        # 静态文件压缩
        gzip on;
        gzip_types text/css application/javascript image/png image/jpg image/jpeg;
    }
    
    # 应用服务器代理
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # 日志配置
    access_log /var/log/nginx/qa_platform_access.log;
    error_log /var/log/nginx/qa_platform_error.log;
}
```

#### 2. 启用Nginx配置

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/qa_platform /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重载配置
sudo systemctl reload nginx
```

### 进程管理配置

#### 1. Supervisor配置

创建 `/etc/supervisor/conf.d/qa_platform.conf`:

```ini
[program:qa_platform]
command=/opt/qa_platform/venv/bin/gunicorn --bind 127.0.0.1:5001 --workers 4 --timeout 30 --keep-alive 2 --max-requests 1000 "app:create_app()"
directory=/opt/qa_platform
user=qa_app
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/qa_platform.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
environment=FLASK_ENV=production
```

#### 2. 启动服务

```bash
# 重新读取配置
sudo supervisorctl reread
sudo supervisorctl update

# 启动应用
sudo supervisorctl start qa_platform

# 检查状态
sudo supervisorctl status qa_platform
```

## 🔒 安全配置

### 防火墙设置

```bash
# Ubuntu (UFW)
sudo ufw enable
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS

# CentOS (firewalld)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### SSL证书配置

#### 使用 Let's Encrypt

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx  # Ubuntu
sudo yum install certbot python3-certbot-nginx  # CentOS

# 获取SSL证书
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 设置自动续期
sudo crontab -e
# 添加: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 监控与日志

### 日志管理

#### 1. 应用日志

```bash
# 查看应用日志
sudo supervisorctl tail qa_platform stdout

# 查看详细日志
sudo tail -f /var/log/supervisor/qa_platform.log
```

#### 2. Nginx日志

```bash
# 访问日志
sudo tail -f /var/log/nginx/qa_platform_access.log

# 错误日志
sudo tail -f /var/log/nginx/qa_platform_error.log
```

### 性能监控

#### 1. 系统资源监控

```bash
# 安装监控工具
sudo apt install htop iotop nethogs

# 实时监控
htop           # CPU和内存
iotop          # 磁盘I/O
nethogs        # 网络使用
```

## 🔄 备份与恢复

### 自动备份配置

#### 1. 创建备份脚本

创建 `/opt/qa_platform/scripts/backup.sh`:

```bash
#!/bin/bash

# 配置变量
BACKUP_DIR="/opt/backups/qa_platform"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="classroom"
DB_USER="qa_prod"
DB_PASS="STRONG_PASSWORD"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 数据库备份
echo "Starting database backup..."
mysqldump -u $DB_USER -p$DB_PASS $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql

# 压缩备份文件
gzip $BACKUP_DIR/db_backup_$DATE.sql

# 应用文件备份
echo "Starting application backup..."
tar -czf $BACKUP_DIR/app_backup_$DATE.tar.gz -C /opt qa_platform

# 清理旧备份 (保留7天)
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +7 -delete
find $BACKUP_DIR -name "app_backup_*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

#### 2. 设置定时备份

```bash
# 设置执行权限
sudo chmod +x /opt/qa_platform/scripts/backup.sh

# 设置定时任务
sudo crontab -e

# 添加以下行 (每天凌晨2点备份)
0 2 * * * /opt/qa_platform/scripts/backup.sh >> /var/log/backup.log 2>&1
```

## 🚀 性能优化

### 应用层优化

#### 1. Gunicorn优化

```bash
# 优化的Gunicorn配置
/opt/qa_platform/venv/bin/gunicorn \
    --bind 127.0.0.1:5001 \
    --workers 4 \
    --worker-class gevent \
    --worker-connections 1000 \
    --timeout 30 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --preload \
    "app:create_app()"
```

#### 2. 数据库优化

```sql
-- 添加必要索引
CREATE INDEX idx_question_created_at ON Question(created_at);
CREATE INDEX idx_question_course_id ON Question(course_id);
CREATE INDEX idx_answer_question_id ON Answer(question_id);
CREATE INDEX idx_answer_created_at ON Answer(created_at);
CREATE INDEX idx_enrollment_student_course ON Enrollment(student_id, course_id);

-- 分析表统计信息
ANALYZE TABLE Question, Answer, User, Course, Enrollment;
```

## 🔧 故障排除

### 常见问题及解决方案

#### 1. 应用无法启动

```bash
# 检查进程状态
sudo supervisorctl status qa_platform

# 查看错误日志
sudo supervisorctl tail qa_platform stderr

# 检查端口占用
sudo netstat -tlnp | grep :5001

# 手动测试启动
sudo -u qa_app /opt/qa_platform/venv/bin/python /opt/qa_platform/run.py
```

#### 2. 数据库连接失败

```bash
# 检查MySQL服务状态
sudo systemctl status mysql

# 测试数据库连接
mysql -u qa_prod -p -h localhost classroom

# 检查数据库配置
grep -r "DATABASE_URL" /opt/qa_platform/
```

#### 3. 静态文件无法访问

```bash
# 检查文件权限
ls -la /opt/qa_platform/static/

# 检查Nginx配置
sudo nginx -t

# 重载Nginx配置
sudo systemctl reload nginx
```

### 更新流程

#### 1. 准备更新

```bash
# 创建备份
/opt/qa_platform/scripts/backup.sh

# 停止应用
sudo supervisorctl stop qa_platform
```

#### 2. 更新代码

```bash
cd /opt/qa_platform

# 备份当前版本
sudo -u qa_app git stash

# 拉取最新代码
sudo -u qa_app git pull origin main

# 更新依赖
sudo -u qa_app ./venv/bin/pip install -r requirements.txt
```

#### 3. 重启服务

```bash
# 重启应用
sudo supervisorctl start qa_platform

# 检查状态
sudo supervisorctl status qa_platform

# 测试应用
curl -f http://localhost:5001/ || echo "应用启动失败"
```

---

🎉 **恭喜！您已完成QA教育平台的部署！**

如需技术支持，请检查日志文件或联系技术团队。平台现在已准备就绪，可以为用户提供服务。
