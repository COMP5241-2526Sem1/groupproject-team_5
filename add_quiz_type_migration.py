#!/usr/bin/env python3
"""
添加 quiz_type 字段到 Activity 表的迁移脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text

def migrate_add_quiz_type():
    """添加 quiz_type 字段到 Activity 表"""
    app = create_app()
    
    with app.app_context():
        try:
            # 检查字段是否已存在
            result = db.session.execute(text("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'activity' 
                AND COLUMN_NAME = 'quiz_type'
                AND TABLE_SCHEMA = DATABASE()
            """)).scalar()
            
            if result == 0:
                print("添加 quiz_type 字段到 Activity 表...")
                db.session.execute(text("""
                    ALTER TABLE activity 
                    ADD COLUMN quiz_type VARCHAR(50) NULL 
                    AFTER type
                """))
                db.session.commit()
                print("✅ quiz_type 字段添加成功!")
            else:
                print("ℹ️  quiz_type 字段已存在，跳过迁移")
                
        except Exception as e:
            print(f"❌ 迁移失败: {e}")
            db.session.rollback()
            return False
            
    return True

if __name__ == '__main__':
    if migrate_add_quiz_type():
        print("🎉 数据库迁移完成!")
    else:
        print("💥 数据库迁移失败!")
        sys.exit(1)
