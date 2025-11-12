#!/usr/bin/env python3
"""
添加 duration_seconds 字段到 Activity 表
支持精确到秒的活动时长控制
"""
import os
import sys

# Add the parent directory to sys.path to import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Activity
from sqlalchemy import text

def add_duration_seconds_field():
    """添加 duration_seconds 字段"""
    app = create_app()
    
    with app.app_context():
        try:
            # 检查字段是否已存在
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('activity')]
            
            if 'duration_seconds' in columns:
                print("✓ duration_seconds 字段已存在")
                return True
            
            print("开始添加 duration_seconds 字段...")
            
            # 添加新字段，默认为 NULL
            with db.engine.connect() as conn:
                conn.execute(text(
                    "ALTER TABLE activity ADD COLUMN duration_seconds INTEGER"
                ))
                conn.commit()
                print("✓ 成功添加 duration_seconds 字段")
            
            # 从现有的 duration_minutes 数据填充 duration_seconds
            # duration_seconds = duration_minutes * 60
            print("开始迁移现有数据...")
            activities = Activity.query.all()
            for activity in activities:
                if activity.duration_minutes:
                    activity.duration_seconds = activity.duration_minutes * 60
                else:
                    activity.duration_seconds = 300  # 默认5分钟
            
            db.session.commit()
            print(f"✓ 成功迁移 {len(activities)} 条活动记录")
            
            print("\n✅ 迁移完成！")
            print("说明：")
            print("  - duration_seconds: 活动总时长（秒），用于精确控制")
            print("  - duration_minutes: 保留用于向后兼容和显示")
            return True
            
        except Exception as e:
            print(f"\n❌ 迁移失败: {str(e)}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    success = add_duration_seconds_field()
    sys.exit(0 if success else 1)
