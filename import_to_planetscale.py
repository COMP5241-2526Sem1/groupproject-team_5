#!/usr/bin/env python3
"""
导入数据到云端 MySQL 数据库（Railway/PlanetScale等）
从 export_local_data.py 导出的 JSON 文件导入
"""

import pymysql
import json
import os
import sys
from datetime import datetime

def import_data(json_file):
    """导入数据到 PlanetScale"""
    print("=" * 60)
    print("📥 PlanetScale 数据导入工具")
    print("=" * 60)
    
    # 检查文件
    if not os.path.exists(json_file):
        print(f"❌ 文件不存在: {json_file}")
        return False
    
    file_size = os.path.getsize(json_file) / 1024
    print(f"\n📁 数据文件: {json_file}")
    print(f"📊 文件大小: {file_size:.2f} KB")
    
    # PlanetScale 配置
    config = {
        'host': os.getenv('MYSQL_HOST'),
        'port': int(os.getenv('MYSQL_PORT', 3306)),
        'user': os.getenv('MYSQL_USER'),
        'password': os.getenv('MYSQL_PASSWORD'),
        'database': os.getenv('MYSQL_DATABASE'),
        'charset': 'utf8mb4'
    }
    
    # 检查环境变量
    missing = [k for k, v in config.items() if v is None and k != 'port']
    if missing:
        print(f"\n❌ 缺少环境变量: {', '.join(missing)}")
        print("\n请设置以下环境变量:")
        print("  export MYSQL_HOST=your-db.psdb.cloud")
        print("  export MYSQL_USER=your_username")
        print("  export MYSQL_PASSWORD=pscale_pw_xxx")
        print("  export MYSQL_DATABASE=qa-platform")
        return False
    
    print(f"\n🔍 连接配置:")
    print(f"   主机: {config['host']}:{config['port']}")
    print(f"   数据库: {config['database']}")
    print(f"   用户: {config['user']}")
    
    # 检测是否是 PlanetScale
    is_planetscale = 'psdb.cloud' in config['host']
    if is_planetscale:
        print("   ✅ 检测到 PlanetScale 连接")
        config['ssl'] = {'ssl': True}
    
    try:
        print(f"\n📡 连接到数据库...")
        conn = pymysql.connect(**config)
        cursor = conn.cursor()
        print("✅ 连接成功！")
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False
    
    # 读取数据
    print(f"\n📖 读取数据文件...")
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ 读取成功，包含 {len(data)} 个表")
    except Exception as e:
        print(f"❌ 读取失败: {e}")
        return False
    
    # 检查表是否存在
    print(f"\n🔍 检查表结构...")
    cursor.execute("SHOW TABLES")
    existing_tables = [row[0] for row in cursor.fetchall()]
    print(f"   数据库中有 {len(existing_tables)} 个表")
    
    if not existing_tables:
        print("\n⚠️  数据库中没有表！")
        print("   请先运行: python init_db.py")
        return False
    
    # 导入顺序（考虑外键依赖）
    # 根据你的模型调整顺序
    import_order = ['user', 'course', 'enrollment', 'activity', 'question', 'answer', 'reply']
    
    # 添加数据中有但不在顺序列表的表
    for table in data.keys():
        if table not in import_order and table in existing_tables:
            import_order.append(table)
    
    print(f"\n📥 开始导入...")
    print(f"   导入顺序: {' → '.join(import_order)}")
    
    total_success = 0
    total_error = 0
    
    for table in import_order:
        if table not in data:
            continue
        
        rows = data[table]
        
        if not rows:
            print(f"\n⚠️  跳过空表: {table}")
            continue
        
        if table not in existing_tables:
            print(f"\n⚠️  表 {table} 不存在于目标数据库，跳过")
            continue
        
        print(f"\n📦 导入表: {table}")
        print(f"   共 {len(rows)} 条记录")
        
        # 获取列名
        columns = list(rows[0].keys())
        placeholders = ', '.join(['%s'] * len(columns))
        columns_str = ', '.join([f'`{col}`' for col in columns])
        
        # 构建 INSERT 语句
        sql = f"INSERT IGNORE INTO {table} ({columns_str}) VALUES ({placeholders})"
        
        success_count = 0
        error_count = 0
        errors = []
        
        # 批量插入
        batch_size = 100
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i+batch_size]
            
            for row in batch:
                try:
                    values = [row[col] for col in columns]
                    cursor.execute(sql, values)
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    if error_count <= 3:  # 只记录前3个错误
                        errors.append(str(e))
            
            # 每批提交一次
            conn.commit()
            
            # 显示进度
            progress = min(i + batch_size, len(rows))
            percent = (progress / len(rows)) * 100
            print(f"   进度: {progress}/{len(rows)} ({percent:.1f}%)", end='\r')
        
        print()  # 换行
        print(f"   ✅ 成功: {success_count}")
        if error_count > 0:
            print(f"   ⚠️  失败: {error_count}")
            if errors:
                print(f"   错误示例:")
                for err in errors[:3]:
                    print(f"     - {err}")
        
        total_success += success_count
        total_error += error_count
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("🎉 导入完成！")
    print("=" * 60)
    print(f"✅ 成功导入: {total_success} 条记录")
    if total_error > 0:
        print(f"⚠️  失败: {total_error} 条记录")
    print("=" * 60)
    
    print(f"\n下一步:")
    print(f"  运行验证: python verify_migration.py")
    
    return True

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python import_to_planetscale.py <json文件>")
        print("\n示例:")
        print("  python import_to_planetscale.py data_backup_20251110_153000.json")
        print("\n最近的备份文件:")
        
        # 查找备份文件
        import glob
        backups = sorted(glob.glob("data_backup_*.json"), reverse=True)
        if backups:
            for backup in backups[:5]:
                size = os.path.getsize(backup) / 1024
                print(f"  - {backup} ({size:.2f} KB)")
        else:
            print("  未找到备份文件")
        
        sys.exit(1)
    
    json_file = sys.argv[1]
    success = import_data(json_file)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
