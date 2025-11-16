# Gmail邮箱配置指南

## 1. 准备Gmail账号

### 步骤1：启用两步验证
1. 登录你的Gmail账号
2. 前往 [Google Account Security](https://myaccount.google.com/security)
3. 在"登录Google"部分，启用"两步验证"

### 步骤2：生成应用专用密码
1. 在Google账号安全页面，找到"应用专用密码"
2. 选择"邮件"作为应用类型
3. 选择设备类型（例如"其他"）
4. 点击"生成"
5. **复制生成的16位密码**（格式类似：abcd efgh ijkl mnop）

## 2. 在Render设置环境变量

在Render Dashboard中设置以下环境变量：

```bash
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=你的Gmail地址@gmail.com
MAIL_PASSWORD=应用专用密码（16位）
MAIL_DEFAULT_SENDER=你的Gmail地址@gmail.com
```

### 设置步骤：
1. 登录 [Render Dashboard](https://dashboard.render.com)
2. 选择你的服务（qa-platform-zmd）
3. 点击"Settings"
4. 滚动到"Environment Variables"部分
5. 逐一添加上述环境变量
6. 点击"Save Changes"

## 3. 测试配置

配置完成后，你可以：
1. 访问 `https://qa-platform-zmd.onrender.com/debug/email_config` 查看配置
2. 在注册页面测试发送验证码

## 示例配置

```bash
MAIL_USERNAME=classroom.demo@gmail.com
MAIL_PASSWORD=abcd efgh ijkl mnop  # 应用专用密码
```

## 常见问题

### Q: 提示"Authentication failed"
A: 请确保：
- 已启用两步验证
- 使用的是应用专用密码，不是Gmail登录密码
- 邮箱地址正确

### Q: 仍然超时
A: Gmail服务器通常很稳定。如果仍然超时，可能是网络问题，稍后重试。

### Q: 不想使用个人Gmail
A: 可以创建一个专门的Gmail账号用于发送邮件，比如 `yourproject.noreply@gmail.com`
