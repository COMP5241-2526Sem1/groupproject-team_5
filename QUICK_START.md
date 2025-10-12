# 快速启动指南

## 本地运行（5分钟快速体验）

### 1. 环境准备
```bash
# 确保已安装 Python 3.7+
python --version

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 创建测试数据
```bash
python create_test_data.py
```

### 4. 启动应用
```bash
python run.py
```

### 5. 访问应用
打开浏览器访问：http://localhost:5000

## 测试账户

| 角色 | 邮箱 | 密码 | 说明 |
|------|------|------|------|
| 管理员 | admin@example.com | admin123 | 全局管理 |
| 教师 | instructor1@example.com | instructor123 | 创建课程和活动 |
| 学生 | student1@example.com | student123 | 参与活动 |

## 快速体验流程

### 作为教师：
1. 登录 instructor1@example.com
2. 查看已有课程和活动
3. 创建新课程
4. 导入学生（使用示例 CSV）
5. 创建投票或简答题活动
6. 开始活动并查看结果

### 作为学生：
1. 登录 student1@example.com
2. 查看已注册的课程
3. 参与进行中的活动
4. 提交答案

### 作为管理员：
1. 登录 admin@example.com
2. 查看全局统计
3. 查看所有课程和活动
4. 查看学生排行榜

## 功能演示

### AI 生成题目
1. 创建活动时，在"AI 辅助生成题目"区域
2. 粘贴教学文本
3. 点击"生成题目"
4. 选择合适的问题使用

### 实时互动
1. 教师开始活动
2. 学生实时提交答案
3. 教师查看实时参与情况
4. 活动结束后查看详细分析

### 数据分析
1. 投票活动：查看各选项得票数和百分比
2. 简答题：查看所有答案和词频分析
3. 排行榜：查看学生参与度排名

## 部署到云端

### Render 部署
1. 推送代码到 GitHub
2. 在 Render 创建 Web Service
3. 设置环境变量
4. 部署完成

### Heroku 部署
1. 安装 Heroku CLI
2. 创建应用：`heroku create your-app-name`
3. 设置环境变量
4. 推送代码：`git push heroku main`

## 故障排除

### 常见问题
1. **端口被占用**：修改 `start.py` 中的端口号
2. **数据库错误**：删除 `instance/classroom.db` 重新创建
3. **AI 功能不工作**：检查 `OPENAI_API_KEY` 环境变量

### 重置数据
```bash
# 删除数据库
rm instance/classroom.db

# 重新创建测试数据
python create_test_data.py
```

## 下一步

1. 阅读完整 [README.md](README.md)
2. 查看 [用户手册](USER_MANUAL.md)
3. 自定义配置和部署
4. 添加更多功能

## 技术支持

- 查看 [README.md](README.md) 中的详细文档
- 检查 [USER_MANUAL.md](USER_MANUAL.md) 中的常见问题
- 提交 GitHub Issue 获取帮助



