#!/usr/bin/env python3
"""
从本地 MySQL 导出数据
用于迁移到 PlanetScale 或备份
"""

import pymysql
import json
import os
from datetime import datetime

def export_data():
    """导出本地数据库数据"""
    print("=" * 60)
    print("📦 本地 MySQL 数据导出工具")
    print("=" * 60)
    
    # 本地数据库配置
    config = {
        'host': os.getenv('LOCAL_MYSQL_HOST', '127.0.0.1'),
        'port': int(os.getenv('LOCAL_MYSQL_PORT', 3307)),
        'user': os.getenv('LOCAL_MYSQL_USER', 'root'),
        'password': os.getenv('LOCAL_MYSQL_PASSWORD', '1234'),
        'database': os.getenv('LOCAL_MYSQL_DATABASE', 'platform'),
        'charset': 'utf8mb4'
    }
    
    print(f"\n🔍 连接配置:")
    print(f"   主机: {config['host']}:{config['port']}")
    print(f"   数据库: {config['database']}")
    print(f"   用户: {config['user']}")
    
    try:
        print(f"\n📡 连接到本地 MySQL...")
        conn = pymysql.connect(**config)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        print("✅ 连接成功！")
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print("\n💡 提示:")
        print("   1. 确保本地 MySQL 正在运行")
        print("   2. 检查端口号是否正确 (默认: 3307)")
        print("   3. 检查用户名和密码")
        return None
    
    # 导出的数据
    export_data = {}
    
    # 获取所有表名
    print(f"\n📋 获取表列表...")
    cursor.execute("SHOW TABLES")
    all_tables = [row[f"Tables_in_{config['database']}"] for row in cursor.fetchall()]
    print(f"   找到 {len(all_tables)} 个表")
    
    # 让用户选择要导出的表
    print(f"\n📊 可用的表:")
    for i, table in enumerate(all_tables, 1):
        cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
        count = cursor.fetchone()['count']
        print(f"   {i}. {table} ({count} 条记录)")
    
    choice = input("\n导出所有表？(y/n，默认 y): ").strip().lower()
    
    if choice == 'n':
        tables_input = input("输入要导出的表名（逗号分隔）: ").strip()
        tables = [t.strip() for t in tables_input.split(',')]
    else:
        tables = all_tables
    
    # 导出每个表
    print(f"\n📤 开始导出...")
    total_records = 0
    
    for table in tables:
        if table not in all_tables:
            print(f"   ⚠️  表 {table} 不存在，跳过")
            continue
        
        try:
            print(f"\n📦 导出表: {table}...")
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            
            # 转换特殊类型
            for row in rows:
                for key, value in row.items():
                    if isinstance(value, datetime):
                        row[key] = value.isoformat()
                    elif isinstance(value, bytes):
                        row[key] = value.decode('utf-8', errors='ignore')
            
            export_data[table] = rows
            total_records += len(rows)
            print(f"   ✅ 导出 {len(rows)} 条记录")
            
        except Exception as e:
            print(f"   ❌ 表 {table} 导出失败: {e}")
            export_data[table] = []
    
    # 保存到文件
    filename = f"data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    print(f"\n💾 保存数据...")
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    file_size = os.path.getsize(filename) / 1024  # KB
    
    print("=" * 60)
    print("✅ 导出完成！")
    print("=" * 60)
    print(f"📁 文件: {filename}")
    print(f"📊 大小: {file_size:.2f} KB")
    print(f"📈 表数: {len([t for t in export_data if export_data[t]])}")
    print(f"📝 总记录: {total_records}")
    print("=" * 60)
    
    cursor.close()
    conn.close()
    
    return filename

def main():
    """主函数"""
    print("\n提示: 可以通过环境变量自定义数据库配置:")
    print("  LOCAL_MYSQL_HOST (默认: 127.0.0.1)")
    print("  LOCAL_MYSQL_PORT (默认: 3307)")
    print("  LOCAL_MYSQL_USER (默认: root)")
    print("  LOCAL_MYSQL_PASSWORD (默认: 1234)")
    print("  LOCAL_MYSQL_DATABASE (默认: platform)")
    print("")
    
    filename = export_data()
    
    if filename:
        print(f"\n下一步:")
        print(f"1. 设置 PlanetScale 环境变量")
        print(f"2. 运行: python init_db.py")
        print(f"3. 运行: python import_to_planetscale.py {filename}")

if __name__ == "__main__":
    main()
