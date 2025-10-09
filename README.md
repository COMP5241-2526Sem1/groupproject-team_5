# Classroom Interaction Platform

A Flask-based web application for interactive classroom learning activities, developed for COMP5241.

## Features

### Core Requirements ✅
- **Activity Creation**: Support for polls, quizzes, word clouds, short-answer questions, and mini-games
- **Course and Student Management**: Course creation, CSV student import with ID linking
- **GenAI Integration**: OpenAI API for question generation and answer analysis
- **Reporting and Dashboards**: Comprehensive analytics and leaderboards
- **Admin Features**: Full administrative control panel
- **Responsive UI**: Mobile-friendly Bootstrap design
- **Deployment**: Docker support and cloud deployment ready

### Activity Types
- **Polls**: Multiple choice voting with real-time results
- **Quizzes**: Multiple choice, true/false, and fill-in-the-blank with automatic scoring
- **Short Answer**: Open-ended questions with word frequency analysis
- **Word Cloud**: Interactive word collection and visualization
- **Memory Game**: Sequence memorization training

### Advanced Features
- **Real-time Updates**: WebSocket communication for live interactions
- **AI Content Generation**: Automatic activity creation from teaching content
- **Answer Grouping**: AI-powered analysis and grouping of student responses
- **Data Export**: CSV export for all activities and results
- **Advanced Analytics**: Participation rates, response times, and learning insights

## Technology Stack

- **Backend**: Flask, SQLAlchemy, Flask-SocketIO
- **Frontend**: Bootstrap 5, jQuery, Socket.IO
- **Database**: SQLite (development), PostgreSQL (production)
- **AI Integration**: OpenAI API
- **Deployment**: Docker, Render/Heroku ready

## Installation

### Prerequisites
- Python 3.8+
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/classroom-interaction-platform.git
   cd classroom-interaction-platform
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables**
   ```bash
   # Create .env file
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///classroom.db
   ARK_API_KEY=your-bytedance-ark-api-key-optional
   OPENAI_API_KEY=your-openai-api-key-optional
   ```
   
   **Note**: The system supports both ByteDance Ark API and OpenAI API. If both are provided, Ark API will be used first. If neither is provided, fallback generation will be used.

5. **Initialize database (optional)**
   ```bash
   python run.py --init-db
   ```

6. **Run the application**
   ```bash
   python run.py
   ```

7. **Access the application**
   - Open http://localhost:5000 in your browser

### Docker Deployment

1. **Build the image**
   ```bash
   docker build -t classroom-platform .
   ```

2. **Run the container**
   ```bash
   docker run -p 5000:5000 -e SECRET_KEY=your-secret-key classroom-platform
   ```

## Usage

### Test Accounts
- **Admin**: admin@example.com / admin123
- **Instructor**: instructor@example.com / instructor123
- **Student**: student@example.com / student123

### Creating Activities
1. Login as instructor
2. Create or select a course
3. Click "Create Activity"
4. Choose activity type and configure settings
5. Start the activity for students to participate

### Student Participation
1. Login as student
2. View enrolled courses
3. Click on active activities
4. Submit responses in real-time

## Project Structure

```
├── app/
│   ├── __init__.py          # Flask app initialization
│   ├── models.py            # Database models
│   ├── forms.py             # WTForms definitions
│   ├── ai_utils.py          # AI integration utilities
│   ├── socket_events.py     # WebSocket event handlers
│   └── routes/              # Route blueprints
│       ├── main.py          # Main routes
│       ├── auth.py          # Authentication routes
│       ├── courses.py       # Course management routes
│       └── activities.py    # Activity management routes
├── templates/               # Jinja2 templates
├── static/                  # Static files (CSS, JS, images)
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
├── run.py                  # Application entry point
└── create_test_data.py     # Database initialization script
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is developed for educational purposes as part of COMP5241.

## Contact

For questions or support, please contact the development team.