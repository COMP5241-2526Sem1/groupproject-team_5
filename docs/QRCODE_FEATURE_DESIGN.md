# 🔗 二维码快速参与活动功能设计

## 功能概述

通过扫描二维码，学生可以：
1. 快速注册（如果未注册）
2. 自动加入课程（如果未加入）
3. 直接参与活动

## 数据库改动

### 1. Activity 表添加字段

```python
class Activity(db.Model):
    # ... 现有字段 ...
    
    # 新增字段
    join_token = db.Column(db.String(32), unique=True, nullable=True)  # 参与令牌
    allow_quick_join = db.Column(db.Boolean, default=True)  # 是否允许快速加入
    token_expires_at = db.Column(db.DateTime, nullable=True)  # 令牌过期时间
    
    def generate_join_token(self):
        """生成参与令牌"""
        import secrets
        self.join_token = secrets.token_urlsafe(16)
        return self.join_token
    
    def get_join_url(self, base_url):
        """获取参与链接"""
        if not self.join_token:
            self.generate_join_token()
        return f"{base_url}/activity/join/{self.join_token}"
    
    def is_token_valid(self):
        """检查令牌是否有效"""
        if not self.allow_quick_join:
            return False
        if self.token_expires_at:
            from datetime import datetime
            return datetime.utcnow() < self.token_expires_at
        return True
```

## 实现步骤

### 步骤 1: 安装二维码生成库

```bash
pip install qrcode[pil]
```

添加到 requirements.txt:
```
qrcode[pil]==7.4.2
Pillow==10.1.0
```

### 步骤 2: 创建数据库迁移

```python
# add_activity_join_token.py
from app import create_app, db
from app.models import Activity

app = create_app()

with app.app_context():
    # 添加新列
    from sqlalchemy import text
    
    # 添加 join_token 列
    db.session.execute(text("""
        ALTER TABLE activity 
        ADD COLUMN join_token VARCHAR(32) UNIQUE
    """))
    
    # 添加 allow_quick_join 列
    db.session.execute(text("""
        ALTER TABLE activity 
        ADD COLUMN allow_quick_join BOOLEAN DEFAULT TRUE
    """))
    
    # 添加 token_expires_at 列
    db.session.execute(text("""
        ALTER TABLE activity 
        ADD COLUMN token_expires_at DATETIME
    """))
    
    db.session.commit()
    
    print("✅ 数据库迁移完成！")
    print("为现有活动生成令牌...")
    
    # 为现有活动生成令牌
    activities = Activity.query.all()
    for activity in activities:
        activity.generate_join_token()
    
    db.session.commit()
    print(f"✅ 已为 {len(activities)} 个活动生成令牌")
```

### 步骤 3: 创建二维码生成工具

```python
# app/qr_utils.py
import qrcode
from io import BytesIO
import base64

def generate_qr_code(data: str, size: int = 10) -> str:
    """
    生成二维码并返回 base64 编码的图片
    
    Args:
        data: 二维码包含的数据（通常是 URL）
        size: 二维码大小（1-40）
        
    Returns:
        base64 编码的 PNG 图片字符串
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=size,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # 转换为 base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"

def generate_activity_qr_code(activity, base_url: str) -> str:
    """
    为活动生成二维码
    
    Args:
        activity: Activity 对象
        base_url: 应用的基础 URL（如 https://your-app.com）
        
    Returns:
        base64 编码的二维码图片
    """
    if not activity.join_token:
        activity.generate_join_token()
        from app import db
        db.session.commit()
    
    join_url = activity.get_join_url(base_url)
    return generate_qr_code(join_url)
```

### 步骤 4: 修改创建活动页面

```python
# app/routes/activities.py

@activities_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    # ... 现有创建逻辑 ...
    
    if form.validate_on_submit():
        activity = Activity(
            title=form.title.data,
            # ... 其他字段 ...
        )
        
        # 生成参与令牌
        activity.generate_join_token()
        
        db.session.add(activity)
        db.session.commit()
        
        flash('活动创建成功！', 'success')
        return redirect(url_for('activities.detail', activity_id=activity.id))
    
    return render_template('activities/create_activity.html', form=form)
```

### 步骤 5: 活动详情页显示二维码

```python
# app/routes/activities.py

@activities_bp.route('/<int:activity_id>')
@login_required
def detail(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    
    # 生成二维码（仅老师可见）
    qr_code = None
    if current_user.role == 'instructor' and activity.course.instructor_id == current_user.id:
        from flask import request
        base_url = request.url_root.rstrip('/')
        from app.qr_utils import generate_activity_qr_code
        qr_code = generate_activity_qr_code(activity, base_url)
    
    return render_template('activities/activity_detail.html', 
                         activity=activity, 
                         qr_code=qr_code)
```

### 步骤 6: 创建快速加入路由

```python
# app/routes/activities.py

@activities_bp.route('/join/<token>')
def quick_join(token):
    """
    通过令牌快速加入活动
    """
    from flask import session
    
    # 查找活动
    activity = Activity.query.filter_by(join_token=token).first_or_404()
    
    # 检查令牌是否有效
    if not activity.is_token_valid():
        flash('该活动链接已失效或不允许快速加入', 'error')
        return redirect(url_for('main.index'))
    
    # 检查用户登录状态
    if current_user.is_authenticated:
        # 用户已登录，检查是否已加入课程
        enrollment = Enrollment.query.filter_by(
            student_id=current_user.id,
            course_id=activity.course_id
        ).first()
        
        if not enrollment:
            # 自动加入课程
            enrollment = Enrollment(
                student_id=current_user.id,
                course_id=activity.course_id,
                enrolled_at=datetime.utcnow()
            )
            db.session.add(enrollment)
            db.session.commit()
            flash(f'已自动加入课程：{activity.course.name}', 'success')
        
        # 跳转到活动页面
        return redirect(url_for('activities.detail', activity_id=activity.id))
    
    else:
        # 用户未登录，保存令牌到 session，跳转到快速注册页面
        session['join_token'] = token
        session['redirect_activity'] = activity.id
        return redirect(url_for('activities.quick_register'))


@activities_bp.route('/quick-register', methods=['GET', 'POST'])
def quick_register():
    """
    快速注册并加入活动
    """
    from flask import session, request
    
    # 检查是否有待加入的活动
    token = session.get('join_token')
    if not token:
        flash('无效的访问', 'error')
        return redirect(url_for('main.index'))
    
    activity = Activity.query.filter_by(join_token=token).first_or_404()
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        student_id = request.form.get('student_id')
        password = request.form.get('password')
        
        # 验证
        if not all([username, email, student_id, password]):
            flash('请填写所有字段', 'error')
            return render_template('activities/quick_register.html', activity=activity)
        
        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            flash('该邮箱已被注册，请直接登录', 'error')
            return redirect(url_for('auth.login'))
        
        # 创建用户
        user = User(
            username=username,
            email=email,
            student_id=student_id,
            role='student'
        )
        user.set_password(password)
        db.session.add(user)
        
        # 自动加入课程
        enrollment = Enrollment(
            student_id=user.id,
            course_id=activity.course_id,
            enrolled_at=datetime.utcnow()
        )
        db.session.add(enrollment)
        
        db.session.commit()
        
        # 登录用户
        login_user(user)
        
        # 清除 session
        session.pop('join_token', None)
        activity_id = session.pop('redirect_activity', None)
        
        flash(f'注册成功！已自动加入课程：{activity.course.name}', 'success')
        return redirect(url_for('activities.detail', activity_id=activity_id))
    
    return render_template('activities/quick_register.html', activity=activity)
```

### 步骤 7: 创建快速注册模板

```html
<!-- templates/activities/quick_register.html -->
{% extends "base.html" %}

{% block content %}
<div class="container mt-5">
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="card">
                <div class="card-header bg-primary text-white">
                    <h4 class="mb-0">快速注册参与活动</h4>
                </div>
                <div class="card-body">
                    <div class="alert alert-info">
                        <strong>活动信息：</strong><br>
                        课程：{{ activity.course.name }}<br>
                        活动：{{ activity.title }}<br>
                        老师：{{ activity.course.instructor.username }}
                    </div>
                    
                    <p class="text-muted">
                        快速注册后，您将自动加入该课程并可以参与活动。
                    </p>
                    
                    <form method="POST">
                        <div class="mb-3">
                            <label for="username" class="form-label">姓名 *</label>
                            <input type="text" class="form-control" id="username" 
                                   name="username" required>
                        </div>
                        
                        <div class="mb-3">
                            <label for="student_id" class="form-label">学号 *</label>
                            <input type="text" class="form-control" id="student_id" 
                                   name="student_id" required>
                        </div>
                        
                        <div class="mb-3">
                            <label for="email" class="form-label">邮箱 *</label>
                            <input type="email" class="form-control" id="email" 
                                   name="email" required>
                            <small class="form-text text-muted">
                                用于登录和接收通知
                            </small>
                        </div>
                        
                        <div class="mb-3">
                            <label for="password" class="form-label">密码 *</label>
                            <input type="password" class="form-control" id="password" 
                                   name="password" required minlength="6">
                            <small class="form-text text-muted">
                                至少6个字符
                            </small>
                        </div>
                        
                        <div class="d-grid gap-2">
                            <button type="submit" class="btn btn-primary btn-lg">
                                注册并加入活动
                            </button>
                        </div>
                    </form>
                    
                    <hr>
                    
                    <p class="text-center mb-0">
                        已有账号？
                        <a href="{{ url_for('auth.login') }}">直接登录</a>
                    </p>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### 步骤 8: 在活动详情页显示二维码

```html
<!-- templates/activities/activity_detail.html -->

{% if qr_code %}
<div class="card mb-4">
    <div class="card-header">
        <h5 class="mb-0">📱 学生参与二维码</h5>
    </div>
    <div class="card-body text-center">
        <img src="{{ qr_code }}" alt="活动二维码" class="img-fluid mb-3" style="max-width: 300px;">
        
        <p class="text-muted">
            学生扫描此二维码可直接参与活动<br>
            <small>即使未注册也可以快速加入</small>
        </p>
        
        <div class="btn-group" role="group">
            <button class="btn btn-outline-primary" onclick="downloadQRCode()">
                <i class="bi bi-download"></i> 下载二维码
            </button>
            <button class="btn btn-outline-secondary" onclick="copyJoinLink()">
                <i class="bi bi-link"></i> 复制链接
            </button>
        </div>
        
        <input type="hidden" id="joinLink" value="{{ activity.get_join_url(request.url_root.rstrip('/')) }}">
    </div>
</div>

<script>
function downloadQRCode() {
    const img = document.querySelector('img[alt="活动二维码"]');
    const link = document.createElement('a');
    link.download = 'activity_qr_{{ activity.id }}.png';
    link.href = img.src;
    link.click();
}

function copyJoinLink() {
    const link = document.getElementById('joinLink').value;
    navigator.clipboard.writeText(link).then(() => {
        alert('链接已复制到剪贴板！');
    });
}
</script>
{% endif %}
```

## 部署步骤

### 1. 更新 requirements.txt

```bash
# 添加二维码生成库
qrcode[pil]==7.4.2
Pillow==10.1.0
```

### 2. 运行数据库迁移

```bash
python add_activity_join_token.py
```

### 3. 重启应用

```bash
# 本地
python run.py

# Render 会自动重新部署
```

## 使用流程

### 老师端

1. 创建活动
2. 在活动详情页看到二维码
3. 课堂上展示二维码或分享链接

### 学生端

#### 情况 1：未注册用户
1. 扫描二维码
2. 看到快速注册页面
3. 填写姓名、学号、邮箱、密码
4. 自动注册 → 自动加入课程 → 进入活动页面

#### 情况 2：已注册但未选课
1. 扫描二维码
2. 自动加入课程
3. 进入活动页面

#### 情况 3：已选课
1. 扫描二维码
2. 直接进入活动页面

## 安全性考虑

1. **令牌唯一性**: 每个活动有唯一的令牌
2. **可选过期时间**: 可以设置令牌过期时间
3. **可关闭功能**: `allow_quick_join` 可以关闭快速加入
4. **防止滥用**: 可以添加 IP 限制或验证码

## 优化建议

### 1. 添加令牌有效期设置

在创建活动时，让老师选择：
- 永久有效
- 活动开始后1小时内有效
- 活动期间有效
- 自定义时间

### 2. 添加参与统计

记录通过二维码加入的学生数量和时间

### 3. 支持多次使用

同一个二维码可以被多个学生扫描使用

---

**这个方案完美解决了你的问题！** 🎉

学生扫描二维码后：
- ✅ 自动完成注册（如果需要）
- ✅ 自动加入课程（如果需要）
- ✅ 直接参与活动
- ✅ 老师无需手动添加学生

需要我帮你实现吗？
