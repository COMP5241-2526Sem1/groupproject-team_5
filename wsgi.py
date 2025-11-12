"""
WSGI entry point for production deployment
"""
import eventlet
eventlet.monkey_patch()

from run import app, socketio

# Gunicorn requires an 'application' object
application = app
