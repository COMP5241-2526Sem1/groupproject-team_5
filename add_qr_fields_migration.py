"""
数据库迁移脚本：为 Activity 表添加二维码快速加入功能字段

添加字段：
- allow_quick_join: 是否允许二维码快速加入
- join_token: 加入令牌（唯一）
- token_expires_at: 令牌过期时间

使用方法：
python add_qr_fields_migration.py
"""

from app import create_app, db
from app.models import Activity
from datetime import datetime, timedelta
import secrets

def add_qr_fields():
    """为 Activity 表添加二维码相关字段"""
    app = create_app()
    
    with app.app_context():
        print("开始添加二维码字段...")
        
        try:
            # 使用原始 SQL 添加字段
            with db.engine.connect() as conn:
                # 添加 allow_quick_join 字段
                try:
                    conn.execute(db.text(
                        "ALTER TABLE activity ADD COLUMN allow_quick_join BOOLEAN DEFAULT TRUE"
                    ))
                    conn.commit()
                    print("✓ 已添加 allow_quick_join 字段")
                except Exception as e:
                    if "Duplicate column name" in str(e):
                        print("- allow_quick_join 字段已存在，跳过")
                    else:
                        raise
                
                # 添加 join_token 字段
                try:
                    conn.execute(db.text(
                        "ALTER TABLE activity ADD COLUMN join_token VARCHAR(64) UNIQUE"
                    ))
                    conn.commit()
                    print("✓ 已添加 join_token 字段")
                except Exception as e:
                    if "Duplicate column name" in str(e):
                        print("- join_token 字段已存在，跳过")
                    else:
                        raise
                
                # 添加 token_expires_at 字段
                try:
                    conn.execute(db.text(
                        "ALTER TABLE activity ADD COLUMN token_expires_at DATETIME"
                    ))
                    conn.commit()
                    print("✓ 已添加 token_expires_at 字段")
                except Exception as e:
                    if "Duplicate column name" in str(e):
                        print("- token_expires_at 字段已存在，跳过")
                    else:
                        raise
            
            # 为现有活动生成 token
            print("\n为现有活动生成加入令牌...")
            activities = Activity.query.filter(Activity.join_token.is_(None)).all()
            count = 0
            
            for activity in activities:
                activity.join_token = secrets.token_urlsafe(32)
                activity.allow_quick_join = True
                
                # 设置过期时间
                if activity.ended_at:
                    activity.token_expires_at = activity.ended_at + timedelta(hours=24)
                else:
                    activity.token_expires_at = datetime.utcnow() + timedelta(days=7)
                
                count += 1
            
            db.session.commit()
            print(f"✓ 已为 {count} 个活动生成加入令牌")
            
            print("\n✅ 数据库迁移完成！")
            
        except Exception as e:
            print(f"❌ 迁移失败: {str(e)}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    add_qr_fields()
