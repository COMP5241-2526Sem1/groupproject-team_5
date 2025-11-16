#!/usr/bin/env python3
"""
添加 started_at 和 ended_at 字段到 Activity 表的迁移脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text

def migrate_add_activity_timestamps():
    """添加 started_at 和 ended_at 字段到 Activity 表"""
    app = create_app()
    
    with app.app_context():
        try:
            # 检查 started_at 字段是否已存在
            result = db.session.execute(text("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'activity' 
                AND COLUMN_NAME = 'started_at'
                AND TABLE_SCHEMA = DATABASE()
            """)).scalar()
            
            if result == 0:
                print("添加 started_at 字段到 Activity 表...")
                db.session.execute(text("""
                    ALTER TABLE activity 
                    ADD COLUMN started_at DATETIME NULL 
                    AFTER created_at
                """))
                print("✅ started_at 字段添加成功!")
            else:
                print("ℹ️  started_at 字段已存在，跳过")
            
            # 检查 ended_at 字段是否已存在
            result = db.session.execute(text("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'activity' 
                AND COLUMN_NAME = 'ended_at'
                AND TABLE_SCHEMA = DATABASE()
            """)).scalar()
            
            if result == 0:
                print("添加 ended_at 字段到 Activity 表...")
                db.session.execute(text("""
                    ALTER TABLE activity 
                    ADD COLUMN ended_at DATETIME NULL 
                    AFTER started_at
                """))
                print("✅ ended_at 字段添加成功!")
            else:
                print("ℹ️  ended_at 字段已存在，跳过")
                
            db.session.commit()
                
        except Exception as e:
            print(f"❌ 迁移失败: {e}")
            db.session.rollback()
            return False
            
    return True

if __name__ == '__main__':
    if migrate_add_activity_timestamps():
        print("🎉 数据库迁移完成!")
    else:
        print("💥 数据库迁移失败!")
        sys.exit(1)
