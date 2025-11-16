# 🚀 数据迁移快速指南

## 📋 三种迁移方案

根据你的需求选择：

### 方案 A：重新开始（推荐用于测试环境）⭐⭐⭐⭐⭐

**适合：** 没有重要数据，或者是测试环境

```bash
# 1. 设置 PlanetScale 环境变量
export MYSQL_HOST=your-db.psdb.cloud
export MYSQL_PORT=3306
export MYSQL_USER=your_username
export MYSQL_PASSWORD=pscale_pw_xxx
export MYSQL_DATABASE=qa-platform

# 2. 初始化数据库（自动创建表）
python init_db.py

# 3. （可选）创建测试数据
python create_test_data.py

# 完成！
```

**用时：** 2分钟

---

### 方案 B：一键迁移（推荐用于有数据）⭐⭐⭐⭐

**适合：** 有重要数据需要保留

```bash
# 1. 设置 PlanetScale 环境变量
export MYSQL_HOST=your-db.psdb.cloud
export MYSQL_USER=your_username
export MYSQL_PASSWORD=pscale_pw_xxx
export MYSQL_DATABASE=qa-platform

# 2. 运行一键迁移
./migrate_database.sh

# 自动完成：导出 → 初始化 → 导入 → 验证
```

**用时：** 5-10分钟（取决于数据量）

---

### 方案 C：手动分步迁移（最灵活）⭐⭐⭐

**适合：** 需要精细控制迁移过程

```bash
# 步骤 1：导出本地数据
python export_local_data.py
# 生成：data_backup_20251110_153000.json

# 步骤 2：设置 PlanetScale 环境变量
export MYSQL_HOST=your-db.psdb.cloud
export MYSQL_USER=your_username
export MYSQL_PASSWORD=pscale_pw_xxx
export MYSQL_DATABASE=qa-platform

# 步骤 3：初始化表结构
python init_db.py

# 步骤 4：导入数据
python import_to_planetscale.py data_backup_20251110_153000.json

# 步骤 5：验证
python verify_migration.py
```

**用时：** 10-15分钟

---

## 🎯 我该选哪个？

| 情况 | 推荐方案 | 原因 |
|------|---------|------|
| 刚开始项目，没有重要数据 | 方案 A | 最简单，2分钟搞定 |
| 有测试数据，但都不重要 | 方案 A | 重新创建更干净 |
| 有重要用户数据需要保留 | 方案 B | 一键自动化 |
| 需要选择性导入某些表 | 方案 C | 最灵活 |
| 不确定选哪个 | 方案 B | 保险，有备份 |

---

## 💡 常见场景

### 场景 1：我是第一次部署

**建议：** 方案 A（重新开始）

```bash
# 在 PlanetScale 创建全新数据库
export MYSQL_HOST=your-db.psdb.cloud
export MYSQL_USER=your_username
export MYSQL_PASSWORD=pscale_pw_xxx
export MYSQL_DATABASE=qa-platform

# 初始化
python init_db.py

# 创建测试数据
python create_test_data.py
```

✅ 优点：
- 超级简单
- 数据干净
- 避免本地旧数据的问题

### 场景 2：我有一些用户注册数据

**建议：** 方案 B（一键迁移）

```bash
# 设置环境变量
export MYSQL_HOST=your-db.psdb.cloud
export MYSQL_USER=your_username
export MYSQL_PASSWORD=pscale_pw_xxx
export MYSQL_DATABASE=qa-platform

# 一键迁移
./migrate_database.sh
```

✅ 优点：
- 保留所有数据
- 自动备份
- 自动验证

### 场景 3：我只想迁移用户表

**建议：** 方案 C（手动迁移）

```bash
# 1. 导出数据时选择表
python export_local_data.py
# 当提示时输入：user

# 2. 初始化 PlanetScale
export MYSQL_HOST=your-db.psdb.cloud
# ...其他环境变量
python init_db.py

# 3. 导入
python import_to_planetscale.py data_backup_xxx.json
```

---

## 📝 迁移后的配置

### 本地开发（继续使用本地 MySQL）

```bash
# .env 文件
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3307
MYSQL_USER=root
MYSQL_PASSWORD=1234
MYSQL_DATABASE=platform
```

### 生产环境（使用 PlanetScale）

**在 Render 环境变量中配置：**

```
MYSQL_HOST=your-db.psdb.cloud
MYSQL_PORT=3306
MYSQL_USER=your_username
MYSQL_PASSWORD=pscale_pw_xxx
MYSQL_DATABASE=qa-platform
FLASK_ENV=production
```

### 切换数据库

```bash
# 测试 PlanetScale（本地）
export MYSQL_HOST=your-db.psdb.cloud
export MYSQL_USER=your_username
export MYSQL_PASSWORD=pscale_pw_xxx
export MYSQL_DATABASE=qa-platform
python run.py

# 恢复本地 MySQL
unset MYSQL_HOST MYSQL_USER MYSQL_PASSWORD MYSQL_DATABASE
python run.py
```

---

## ⚠️ 注意事项

### 1. 数据备份

迁移前自动创建备份：
```
data_backup_20251110_153000.json
```

**保留这个文件！** 万一迁移失败可以重新导入。

### 2. 表结构自动创建

Flask-SQLAlchemy 会根据 `app/models.py` 自动创建表：

```python
# app/models.py 定义了所有表结构
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    # ...

# init_db.py 会执行
db.create_all()  # 根据 models.py 创建所有表
```

所以**不需要手动执行 SQL 建表语句**！

### 3. 唯一性约束

User 表的 email 字段有唯一约束：

```python
email = db.Column(db.String(120), unique=True, nullable=False)
```

PlanetScale 会自动强制执行，确保不会出现重复邮箱。

### 4. PlanetScale 限制

- ❌ 不支持外键约束（但应用层会处理）
- ❌ 不支持存储过程
- ✅ 支持所有常用 MySQL 特性
- ✅ 自动处理字符集（UTF-8）

---

## 🔍 验证迁移成功

运行验证脚本：

```bash
python verify_migration.py
```

你应该看到：

```
✅ 数据库连接正常
✅ users (用户)              10 条
✅ courses (课程)             5 条
✅ activities (活动)          8 条
✅ 用户邮箱唯一性            所有邮箱唯一
✅ 课程-教师关联            所有课程都有有效教师
✅ 验证通过！数据迁移成功！
```

---

## 🆘 遇到问题？

### 问题 1：本地 MySQL 连接失败

```bash
❌ 连接失败: Can't connect to MySQL server on '127.0.0.1:3307'
```

**解决：**
```bash
# 检查 MySQL 是否运行
# 检查端口号是否正确（3306 还是 3307？）

# 或者设置自定义配置
export LOCAL_MYSQL_PORT=3306
python export_local_data.py
```

### 问题 2：PlanetScale 连接失败

```bash
❌ 连接失败: Access denied
```

**解决：**
```bash
# 检查环境变量
echo $MYSQL_HOST
echo $MYSQL_USER
# 确保密码正确（包含 pscale_pw_ 前缀）
```

### 问题 3：导入时出现重复键错误

```bash
⚠️  失败: 5 条记录
错误: Duplicate entry 'test@example.com' for key 'email'
```

**这是正常的！** 使用 `INSERT IGNORE` 会跳过重复记录。

### 问题 4：表不存在

```bash
❌ Table 'qa-platform.user' doesn't exist
```

**解决：**
```bash
# 先初始化表结构
python init_db.py

# 再导入数据
python import_to_planetscale.py data_backup_xxx.json
```

---

## 📚 工具脚本说明

| 脚本 | 功能 | 用法 |
|------|------|------|
| `export_local_data.py` | 导出本地 MySQL 数据 | `python export_local_data.py` |
| `import_to_planetscale.py` | 导入数据到 PlanetScale | `python import_to_planetscale.py <文件>` |
| `verify_migration.py` | 验证迁移结果 | `python verify_migration.py` |
| `migrate_database.sh` | 一键自动迁移 | `./migrate_database.sh` |
| `init_db.py` | 初始化数据库表 | `python init_db.py` |

---

## 🎉 完成后

迁移成功后：

1. **本地测试 PlanetScale 连接**
   ```bash
   # 设置环境变量指向 PlanetScale
   export MYSQL_HOST=your-db.psdb.cloud
   # ...
   python run.py
   # 访问 localhost:5000 测试
   ```

2. **推送代码到 GitHub**
   ```bash
   git add .
   git commit -m "准备部署到 Render"
   git push origin zmd
   ```

3. **在 Render 部署**
   - 按照 `QUICK_START_RENDER.md` 操作
   - 配置相同的 PlanetScale 环境变量
   - 部署应用

---

## 💡 小贴士

1. **备份很重要**
   - 导出的 JSON 文件是完整备份
   - 保留它以防万一

2. **可以重复迁移**
   - 如果失败，删除 PlanetScale 的数据
   - 重新运行脚本即可

3. **本地和云端独立**
   - 本地 MySQL 不受影响
   - 随时可以切换

4. **数据验证**
   - 每次迁移后运行 `verify_migration.py`
   - 确保数据完整

---

**准备好了吗？选择一个方案开始迁移吧！** 🚀

推荐：先用**方案 B（一键迁移）**试试！
