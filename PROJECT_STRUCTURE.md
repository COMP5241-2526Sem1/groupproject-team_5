# Project Structure

```
classroom-interaction-platform/
├── app/                          # Main application package
│   ├── __init__.py              # Flask app factory
│   ├── models.py                # Database models
│   ├── forms.py                 # WTForms definitions
│   ├── ai_utils.py              # AI integration utilities
│   ├── socket_events.py         # WebSocket event handlers
│   └── routes/                  # Route blueprints
│       ├── __init__.py
│       ├── main.py              # Main routes (dashboard, leaderboard)
│       ├── auth.py              # Authentication routes
│       ├── courses.py           # Course management routes
│       └── activities.py        # Activity management routes
├── templates/                    # HTML templates
│   ├── base.html               # Base template
│   ├── index.html              # Homepage
│   ├── *_dashboard.html        # Dashboard templates
│   ├── auth/                   # Authentication templates
│   ├── courses/                # Course-related templates
│   └── activities/             # Activity-related templates
├── tests/                       # Test files
│   ├── test_app.py             # Basic app functionality tests
│   └── test_ark_api.py         # AI API integration tests
├── instance/                    # Database files (auto-generated)
├── run.py                      # Main application entry point
├── create_test_data.py         # Test data generation script
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
├── env_example.txt            # Environment variables template
├── README.md                   # Project documentation
├── USER_MANUAL.md             # User manual
├── QUICK_START.md             # Quick start guide
└── PROJECT_STRUCTURE.md       # This file
```

## Key Files

- **`run.py`**: Main entry point with integrated database initialization
- **`app/`**: Core application logic and routes
- **`templates/`**: HTML templates for the web interface
- **`tests/`**: Test scripts for functionality verification
- **`env_example.txt`**: Template for environment variables

## Removed Files

- **`start.py`**: Merged into `run.py` for simplicity
- **`test_app.py`**: Moved to `tests/` directory
- **`test_ark_api.py`**: Moved to `tests/` directory
