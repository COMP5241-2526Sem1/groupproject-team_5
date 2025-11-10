# 📦 数据库迁移指南：本地 MySQL → PlanetScale

## 🎯 目标

将你现有的本地 MySQL 数据库（包括表结构和数据）迁移到 PlanetScale 云端数据库。

---

## 📋 迁移概览

```
本地 MySQL 数据库              PlanetScale 云端数据库
(127.0.0.1:3307)      →       (xxx.psdb.cloud)
  
包含：                         迁移后包含：
✅ 所有表结构                   ✅ 所有表结构
✅ 所有用户数据                 ✅ 所有用户数据
✅ 所有课程数据                 ✅ 所有课程数据
✅ 所有活动数据                 ✅ 所有活动数据
```

---

## 🚀 快速迁移方案（推荐）

### 方案一：使用应用自动创建表 + 手动迁移数据（最简单）

**适合：** 数据量不大，可以重新创建测试数据

#### 步骤 1：在 PlanetScale 创建空数据库

1. 访问 https://planetscale.com/
2. 创建数据库：`qa-platform`
3. 获取连接信息

#### 步骤 2：应用自动创建表结构

```bash
# 设置 PlanetScale 连接信息
export MYSQL_HOST=your-db.psdb.cloud
export MYSQL_PORT=3306
export MYSQL_USER=your_username
export MYSQL_PASSWORD=pscale_pw_xxxx
export MYSQL_DATABASE=qa-platform

# 运行初始化脚本（会自动创建所有表）
python init_db.py
```

这会自动创建：
- ✅ users 表
- ✅ courses 表
- ✅ activities 表
- ✅ questions 表
- ✅ answers 表
- ✅ 等所有表...

#### 步骤 3：迁移重要数据（可选）

如果有重要的用户数据需要保留：

```python
# 创建 migrate_data.py
python migrate_data.py
```

---

### 方案二：导出 SQL 然后导入（完整迁移）

**适合：** 有大量重要数据需要完整迁移

#### 步骤 1：从本地 MySQL 导出数据

```bash
# 导出整个数据库（包括表结构和数据）
mysqldump -h 127.0.0.1 -P 3307 -u root -p1234 \
  --databases platform \
  --add-drop-table \
  --single-transaction \
  > backup_$(date +%Y%m%d).sql

# 或者只导出表结构
mysqldump -h 127.0.0.1 -P 3307 -u root -p1234 \
  --no-data \
  platform > schema_only.sql

# 或者只导出数据
mysqldump -h 127.0.0.1 -P 3307 -u root -p1234 \
  --no-create-info \
  platform > data_only.sql
```

#### 步骤 2：修改导出的 SQL 文件

PlanetScale 有一些限制，需要修改 SQL 文件：

```bash
# 创建兼容 PlanetScale 的 SQL 文件
cat backup_YYYYMMDD.sql | \
  sed 's/ENGINE=InnoDB/ENGINE=InnoDB/g' | \
  grep -v 'SET @@' | \
  grep -v 'SET SQL_MODE' \
  > planetscale_compatible.sql
```

#### 步骤 3：导入到 PlanetScale

**注意：** PlanetScale 不支持直接 `mysql` 命令导入，需要使用 Python 脚本。

---

## 🛠️ 详细迁移脚本

我为你创建了完整的迁移脚本：

### 脚本 1：数据导出脚本 `export_local_data.py`

```python
#!/usr/bin/env python3
"""
从本地 MySQL 导出数据
"""
import pymysql
import json
import os
from datetime import datetime

def export_data():
    """导出本地数据库数据"""
    print("🔍 连接到本地 MySQL...")
    
    # 本地数据库连接
    conn = pymysql.connect(
        host='127.0.0.1',
        port=3307,
        user='root',
        password='1234',
        database='platform',
        charset='utf8mb4'
    )
    
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # 导出的数据
    export_data = {}
    
    # 表列表
    tables = ['user', 'course', 'enrollment', 'activity', 'question', 'answer', 'reply']
    
    for table in tables:
        try:
            print(f"📦 导出表: {table}...")
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            
            # 转换 datetime 对象为字符串
            for row in rows:
                for key, value in row.items():
                    if isinstance(value, datetime):
                        row[key] = value.isoformat()
            
            export_data[table] = rows
            print(f"   ✅ 导出 {len(rows)} 条记录")
        except Exception as e:
            print(f"   ⚠️  表 {table} 导出失败: {e}")
            export_data[table] = []
    
    # 保存到文件
    filename = f"data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 数据已导出到: {filename}")
    
    cursor.close()
    conn.close()
    
    return filename

if __name__ == "__main__":
    export_data()
```

### 脚本 2：数据导入脚本 `import_to_planetscale.py`

```python
#!/usr/bin/env python3
"""
导入数据到 PlanetScale
"""
import pymysql
import json
import os
import sys
from datetime import datetime

def import_data(json_file):
    """导入数据到 PlanetScale"""
    print("🔍 连接到 PlanetScale...")
    
    # PlanetScale 连接
    conn = pymysql.connect(
        host=os.getenv('MYSQL_HOST'),
        port=int(os.getenv('MYSQL_PORT', 3306)),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DATABASE'),
        charset='utf8mb4',
        ssl={'ssl': True}
    )
    
    cursor = conn.cursor()
    
    # 读取数据
    print(f"📖 读取数据文件: {json_file}")
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 导入顺序（考虑外键依赖）
    import_order = ['user', 'course', 'enrollment', 'activity', 'question', 'answer', 'reply']
    
    for table in import_order:
        if table not in data or not data[table]:
            print(f"⚠️  跳过空表: {table}")
            continue
        
        print(f"\n📥 导入表: {table}...")
        rows = data[table]
        
        if not rows:
            print(f"   ℹ️  表为空")
            continue
        
        # 获取列名
        columns = list(rows[0].keys())
        placeholders = ', '.join(['%s'] * len(columns))
        columns_str = ', '.join([f'`{col}`' for col in columns])
        
        # 批量插入
        sql = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"
        
        success_count = 0
        error_count = 0
        
        for row in rows:
            try:
                values = [row[col] for col in columns]
                cursor.execute(sql, values)
                success_count += 1
            except Exception as e:
                error_count += 1
                if error_count <= 3:  # 只显示前3个错误
                    print(f"   ⚠️  插入失败: {e}")
        
        conn.commit()
        print(f"   ✅ 成功: {success_count}, 失败: {error_count}")
    
    cursor.close()
    conn.close()
    
    print("\n🎉 数据导入完成！")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python import_to_planetscale.py <json文件>")
        sys.exit(1)
    
    import_data(sys.argv[1])
```

---

## 📝 完整迁移步骤

### 第一步：导出本地数据

```bash
# 1. 确保本地 MySQL 正在运行
# 2. 运行导出脚本
python export_local_data.py

# 会生成类似：data_backup_20251110_153000.json
```

### 第二步：创建 PlanetScale 数据库

1. 访问 https://planetscale.com/
2. 创建新数据库
3. 获取连接信息

### 第三步：初始化 PlanetScale 表结构

```bash
# 设置 PlanetScale 环境变量
export MYSQL_HOST=your-db.psdb.cloud
export MYSQL_PORT=3306
export MYSQL_USER=your_username
export MYSQL_PASSWORD=pscale_pw_xxxx
export MYSQL_DATABASE=qa-platform

# 创建表结构（使用应用的模型）
python init_db.py
```

### 第四步：导入数据

```bash
# 导入之前导出的数据
python import_to_planetscale.py data_backup_20251110_153000.json
```

### 第五步：验证数据

```bash
# 运行验证脚本
python verify_migration.py
```

---

## 🔍 验证脚本 `verify_migration.py`

```python
#!/usr/bin/env python3
"""
验证数据迁移是否成功
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Course, Activity, Question, Answer

def verify():
    """验证迁移"""
    app = create_app()
    
    with app.app_context():
        print("🔍 验证数据迁移...")
        print("=" * 60)
        
        # 统计数据
        stats = {
            'users': User.query.count(),
            'courses': Course.query.count(),
            'activities': Activity.query.count(),
            'questions': Question.query.count(),
            'answers': Answer.query.count(),
        }
        
        print("\n📊 数据统计:")
        for table, count in stats.items():
            print(f"   {table}: {count} 条记录")
        
        # 检查示例数据
        print("\n👤 示例用户:")
        users = User.query.limit(5).all()
        for user in users:
            print(f"   - {user.email} ({user.role})")
        
        print("\n📚 示例课程:")
        courses = Course.query.limit(5).all()
        for course in courses:
            print(f"   - {course.name}")
        
        print("\n✅ 验证完成！")

if __name__ == "__main__":
    verify()
```

---

## ⚡ 快速迁移命令（一键执行）

创建一个一键迁移脚本 `quick_migrate.sh`：

```bash
#!/bin/bash

echo "🚀 开始数据库迁移..."
echo "================================"

# 第1步：导出本地数据
echo ""
echo "📤 第1步：导出本地数据..."
python export_local_data.py
if [ $? -ne 0 ]; then
    echo "❌ 导出失败！"
    exit 1
fi

# 获取最新的备份文件
BACKUP_FILE=$(ls -t data_backup_*.json | head -1)
echo "✅ 备份文件: $BACKUP_FILE"

# 第2步：初始化 PlanetScale 表结构
echo ""
echo "🏗️  第2步：初始化 PlanetScale 表结构..."
python init_db.py
if [ $? -ne 0 ]; then
    echo "❌ 初始化失败！"
    exit 1
fi

# 第3步：导入数据
echo ""
echo "📥 第3步：导入数据到 PlanetScale..."
python import_to_planetscale.py "$BACKUP_FILE"
if [ $? -ne 0 ]; then
    echo "❌ 导入失败！"
    exit 1
fi

# 第4步：验证
echo ""
echo "🔍 第4步：验证数据..."
python verify_migration.py

echo ""
echo "================================"
echo "🎉 迁移完成！"
```

使用方法：

```bash
# 设置 PlanetScale 环境变量
export MYSQL_HOST=your-db.psdb.cloud
export MYSQL_PORT=3306
export MYSQL_USER=your_username
export MYSQL_PASSWORD=pscale_pw_xxxx
export MYSQL_DATABASE=qa-platform

# 运行一键迁移
chmod +x quick_migrate.sh
./quick_migrate.sh
```

---

## 🤔 常见问题

### Q1: 本地有很多测试数据，要全部迁移吗？

**A:** 不一定。建议：

1. **只迁移重要数据**
   - 保留真实用户账号
   - 保留重要课程数据
   - 丢弃测试数据

2. **或者重新开始**
   - PlanetScale 创建全新数据库
   - 运行 `init_db.py` 创建表
   - 只添加必需的初始数据

### Q2: 迁移会影响本地数据库吗？

**A:** 不会！
- 导出是只读操作
- 不会修改本地数据
- 本地和云端数据库独立

### Q3: 迁移失败怎么办？

**A:** 可以重试：

```bash
# 1. 删除 PlanetScale 的所有数据
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
...     db.drop_all()  # 删除所有表
...     db.create_all()  # 重新创建

# 2. 重新导入
python import_to_planetscale.py data_backup_xxx.json
```

### Q4: 如何只迁移特定表？

**A:** 修改导出脚本：

```python
# 在 export_local_data.py 中
tables = ['user', 'course']  # 只导出这两个表
```

### Q5: 数据太大怎么办？

**A:** 分批迁移：

```python
# 每次只导入部分数据
for i in range(0, len(rows), 1000):  # 每批1000条
    batch = rows[i:i+1000]
    # 插入 batch
```

---

## 📊 迁移对比

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| 方案一：重新创建 | 简单快速 | 丢失旧数据 | ⭐⭐⭐⭐⭐ (测试环境) |
| 方案二：完整迁移 | 保留所有数据 | 需要脚本 | ⭐⭐⭐⭐ (生产环境) |
| 手动 SQL 导出导入 | 通用方法 | PlanetScale 限制多 | ⭐⭐ (不推荐) |

---

## 🎯 推荐方案（根据你的情况）

### 如果是测试/开发环境（推荐）

```bash
# 1. 直接在 PlanetScale 创建新数据库
# 2. 运行初始化
python init_db.py

# 3. 创建测试数据
python create_test_data.py

# 完成！不需要迁移旧数据
```

### 如果有重要用户数据

```bash
# 1. 导出本地数据
python export_local_data.py

# 2. 初始化 PlanetScale
python init_db.py

# 3. 导入数据
python import_to_planetscale.py data_backup_xxx.json

# 4. 验证
python verify_migration.py
```

---

## 📝 总结

### 你需要做的

1. **决定是否需要迁移旧数据**
   - 测试数据 → 不需要，重新创建
   - 重要数据 → 需要，使用迁移脚本

2. **在 PlanetScale 创建数据库**
   - 获取连接信息

3. **初始化表结构**
   - 运行 `python init_db.py`
   - 应用会根据 `app/models.py` 自动创建所有表

4. **（可选）迁移数据**
   - 如果需要，使用提供的迁移脚本

### 关键点

- ✅ **表结构不需要手动创建** - Flask-SQLAlchemy 自动创建
- ✅ **本地和云端独立** - 互不影响
- ✅ **随时可以重新开始** - PlanetScale 数据可以清空重建
- ✅ **测试环境建议不迁移** - 重新创建干净的数据

---

**下一步：** 我来创建这些迁移脚本给你！
