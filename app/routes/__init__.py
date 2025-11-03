"""
Routes package for the Q&A Education Platform

This package contains all the route handlers organized by functionality:
- main: Main application routes (dashboard, index)
- auth: Authentication routes (login, register)
- courses: Course management routes
- activities: Activity management routes
- qa: Q&A system routes
"""

# Import all route modules for easier access
from . import main
from . import auth
from . import courses
from . import activities
from . import qa

# Make blueprints available at package level
__all__ = ['main', 'auth', 'courses', 'activities', 'qa']