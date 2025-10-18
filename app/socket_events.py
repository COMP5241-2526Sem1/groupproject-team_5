from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from app import socketio, db
from app.models import Activity, Response

@socketio.on('join_activity')
def on_join_activity(data):
    """Join an activity room for real-time updates"""
    if not current_user.is_authenticated:
        return False
    
    activity_id = data.get('activity_id')
    if activity_id:
        join_room(f'activity_{activity_id}')
        emit('status', {'message': f'Joined activity {activity_id}'})

@socketio.on('leave_activity')
def on_leave_activity(data):
    """Leave an activity room"""
    if not current_user.is_authenticated:
        return False
    
    activity_id = data.get('activity_id')
    if activity_id:
        leave_room(f'activity_{activity_id}')
        emit('status', {'message': f'Left activity {activity_id}'})

@socketio.on('activity_status_update')
def on_activity_status_update(data):
    """Handle activity status updates"""
    if not current_user.is_authenticated:
        return False
    
    activity_id = data.get('activity_id')
    activity = Activity.query.get(activity_id)
    
    if not activity:
        return False
    
    # Check permissions
    if current_user.role == 'student':
        # Students can only view status
        response_count = Response.query.filter_by(activity_id=activity_id).count()
        my_response = Response.query.filter_by(student_id=current_user.id, activity_id=activity_id).first()
        
        emit('activity_status', {
            'is_active': activity.is_active,
            'response_count': response_count,
            'has_responded': my_response is not None,
            'my_answer': my_response.answer if my_response else None
        }, room=f'activity_{activity_id}')
    
    elif current_user.role in ['admin', 'instructor']:
        # Instructors and admins can see detailed status
        response_count = Response.query.filter_by(activity_id=activity_id).count()
        
        emit('activity_status', {
            'is_active': activity.is_active,
            'response_count': response_count,
            'started_at': activity.started_at.isoformat() if activity.started_at else None,
            'ended_at': activity.ended_at.isoformat() if activity.ended_at else None
        }, room=f'activity_{activity_id}')

@socketio.on('new_response')
def on_new_response(data):
    """Handle new response submissions"""
    if not current_user.is_authenticated:
        return False
    
    activity_id = data.get('activity_id')
    activity = Activity.query.get(activity_id)
    
    if not activity or not activity.is_active:
        return False
    
    # Emit to all users in the activity room
    emit('response_added', {
        'activity_id': activity_id,
        'response_count': Response.query.filter_by(activity_id=activity_id).count(),
        'message': 'New response submitted'
    }, room=f'activity_{activity_id}')

def broadcast_activity_update(activity_id, update_type, data):
    """Broadcast activity updates to all connected users"""
    socketio.emit('activity_update', {
        'activity_id': activity_id,
        'update_type': update_type,
        'data': data
    }, room=f'activity_{activity_id}')



