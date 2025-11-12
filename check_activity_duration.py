#!/usr/bin/env python3
"""
Debug script to check activity duration values
"""
import sys
sys.path.insert(0, '/Users/dududu/Documents/GitHub/groupproject-team_5/team5')

from app import create_app, db
from app.models import Activity

app = create_app()

with app.app_context():
    activities = Activity.query.order_by(Activity.id.desc()).limit(10).all()
    
    print("\n📊 Recent Activities Duration Check:\n")
    print(f"{'ID':<5} {'Title':<30} {'Duration (min)':<15} {'Created At'}")
    print("=" * 80)
    
    for activity in activities:
        print(f"{activity.id:<5} {activity.title[:28]:<30} {activity.duration_minutes:<15} {activity.created_at}")
    
    print("\n" + "=" * 80)
    print(f"\nTotal activities checked: {len(activities)}")
