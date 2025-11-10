"""
Database Migration: Add is_correct, score and points_earned fields to Response model
This script adds the missing fields to the response table.
"""

import os
import sys

# Add the app directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from sqlalchemy import text

def migrate_database():
    """Add is_correct, score and points_earned columns to response table"""
    app = create_app()
    
    with app.app_context():
        try:
            print("=" * 60)
            print("  Database Migration: Add Response Fields")
            print("=" * 60)
            print()
            
            # Check if we're using SQLite or MySQL
            db_type = db.engine.url.drivername
            print(f"Database type detected: {db_type}")
            print()
            
            if 'sqlite' in db_type:
                print("Adding columns to SQLite database...")
                print()
                
                # For SQLite, add columns if they don't exist
                try:
                    db.session.execute(text("ALTER TABLE response ADD COLUMN is_correct BOOLEAN DEFAULT 0"))
                    print("✓ Added is_correct column")
                except Exception as e:
                    if "duplicate column" in str(e).lower():
                        print("ℹ️  is_correct column already exists")
                    else:
                        raise
                
                try:
                    db.session.execute(text("ALTER TABLE response ADD COLUMN score INTEGER DEFAULT 0"))
                    print("✓ Added score column")
                except Exception as e:
                    if "duplicate column" in str(e).lower():
                        print("ℹ️  score column already exists")
                    else:
                        raise
                
                try:
                    db.session.execute(text("ALTER TABLE response ADD COLUMN points_earned INTEGER DEFAULT 0"))
                    print("✓ Added points_earned column")
                except Exception as e:
                    if "duplicate column" in str(e).lower():
                        print("ℹ️  points_earned column already exists")
                    else:
                        raise
                
                db.session.commit()
                
            elif 'mysql' in db_type:
                print("Adding columns to MySQL database...")
                print()
                
                # For MySQL, check if columns exist first
                result = db.session.execute(text(
                    "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
                    "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'response'"
                ))
                existing_columns = [row[0] for row in result]
                
                if 'is_correct' not in existing_columns:
                    db.session.execute(text(
                        "ALTER TABLE response ADD COLUMN is_correct TINYINT(1) DEFAULT 0"
                    ))
                    db.session.commit()
                    print("✓ Added is_correct column")
                else:
                    print("ℹ️  is_correct column already exists")
                
                if 'score' not in existing_columns:
                    db.session.execute(text(
                        "ALTER TABLE response ADD COLUMN score INT DEFAULT 0"
                    ))
                    db.session.commit()
                    print("✓ Added score column")
                else:
                    print("ℹ️  score column already exists")
                
                if 'points_earned' not in existing_columns:
                    db.session.execute(text(
                        "ALTER TABLE response ADD COLUMN points_earned INT DEFAULT 0"
                    ))
                    db.session.commit()
                    print("✓ Added points_earned column")
                else:
                    print("ℹ️  points_earned column already exists")
            
            else:
                print(f"Unsupported database type: {db_type}")
                print("Please manually add the following columns to the response table:")
                print("  - is_correct BOOLEAN DEFAULT FALSE")
                print("  - score INTEGER DEFAULT 0")
                print("  - points_earned INTEGER DEFAULT 0")
                return
            
            print()
            print("=" * 60)
            print("  Migration completed successfully!")
            print("=" * 60)
            print()
            print("✅ The response table now has is_correct, score and points_earned fields.")
            print()
            
        except Exception as e:
            print(f"\n❌ Error during migration: {str(e)}")
            print()
            if 'mysql' in db_type:
                print("If you're using MySQL, you can manually run:")
                print("ALTER TABLE response ADD COLUMN is_correct TINYINT(1) DEFAULT 0;")
                print("ALTER TABLE response ADD COLUMN score INT DEFAULT 0;")
                print("ALTER TABLE response ADD COLUMN points_earned INT DEFAULT 0;")
            db.session.rollback()
            sys.exit(1)

if __name__ == '__main__':
    migrate_database()
