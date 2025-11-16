"""
测试 Railway MySQL 连接

用途：验证能否成功连接到 Railway 数据库
"""

import pymysql
import os

def test_railway_connection():
    """测试 Railway MySQL 连接"""
    
    print("🔍 测试 Railway MySQL 连接...\n")
    
    # Railway 连接信息
    config = {
        'host': 'trolley.proxy.rlwy.net',
        'port': 53176,
        'user': 'root',
        'password': 'HGbKlRAozMzZiIbvMcEXeiZUKgHoJxXr',
        'database': 'railway',
        'ssl_ca': '',
        'ssl_verify_cert': False,
        'ssl_verify_identity': False
    }
    
    print(f"连接配置:")
    print(f"  主机: {config['host']}")
    print(f"  端口: {config['port']}")
    print(f"  用户: {config['user']}")
    print(f"  数据库: {config['database']}")
    print()
    
    try:
        # 尝试连接
        print("正在连接...")
        connection = pymysql.connect(**config)
        
        print("✅ 成功连接到 Railway MySQL!\n")
        
        # 获取数据库版本
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"📊 数据库信息:")
            print(f"  版本: {version[0]}")
            
            # 查看现有表
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"  表数量: {len(tables)}")
            
            if tables:
                print(f"  表列表:")
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                    count = cursor.fetchone()[0]
                    print(f"    - {table[0]}: {count} 条记录")
            else:
                print(f"  ⚠️  数据库为空，需要运行 init_db.py 初始化")
        
        connection.close()
        print("\n✅ 连接测试成功!")
        print("\n📝 下一步:")
        print("  1. 如果数据库为空，运行: python init_db.py")
        print("  2. 如果需要迁移数据，运行: ./migrate_database.sh")
        print("  3. 开始部署到 Render")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 连接失败!")
        print(f"错误信息: {e}\n")
        print("🔧 可能的解决方案:")
        print("  1. 检查网络连接")
        print("  2. 确认 Railway 数据库正在运行")
        print("  3. 验证连接信息是否正确")
        print("  4. 检查是否需要安装: pip install pymysql cryptography")
        
        return False

if __name__ == '__main__':
    test_railway_connection()
