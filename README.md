# 🎓 Q&A Education Platform - Intelligent Q&A Learning System

## 🌐 Live Demo

**🚀 Deployed Application:** [https://qa-platform-zmd.onrender.com](https://qa-platform-zmd.onrender.com)

---

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![Flask Version](https://img.shields.io/badge/flask-2.3.3-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

A modern online education Q&A platform integrating intelligent AI assistance, real-time interaction, and multi-role management features, providing a complete online learning solution for learners and educators.

## 🌟 Project Highlights

### ✨ Core Features
- **🔐 Secure Authentication System**: Email verification code registration, multi-role permission management
- **📚 Intelligent Course Management**: Complete course lifecycle management
- **💬 Efficient Q&A System**: Support for voting, best answers, real-time notifications
- **🎯 Interactive Activity Center**: Real-time voting, Q&A activities, Quiz tests, points incentives
- **📱 QR Code Quick Join**: Scan QR code to automatically register and join activities (⭐ New Feature)
- **⏱️ Flexible Duration Control**: Support for hour/minute/second precise activity duration settings (⭐ New Feature)
- **🔄 Activity Restart Function**: Support for one-click restart of ended activities
- **📱 Responsive Design**: Modern interface adapted to all devices
- **🔍 Smart Pagination**: Optimized browsing experience for large data volumes

### 🎨 User Experience
- **📊 Personalized Dashboard**: Data visualization learning status panel
- **🕒 Beijing Time Synchronization**: Global UTC+8 timezone, all time displays accurate
- **👍 Intuitive Voting System**: Friendly interaction with thumbs up/down
- **🔄 Overflow Prevention Design**: Smart display limits to keep interface clean
- **📄 Smart Pagination Navigation**: Support for page numbers and ellipsis optimization
- **✅ Instant Feedback System**: Real-time success messages and content preview after submission
- **🔄 Automatic UI Updates**: Countdown ends automatically update button status, no refresh needed
- **🌐 Fully English Interface**: All prompts fully in English

### 🤖 AI-Enhanced Features
- **Intelligent Question Generation**: AI question recommendations based on text or documents (PDF/Word/PPT)
- **Multiple Input Methods**: Support for text paste and document upload for AI generation
- **Content Quality Analysis**: AI-assisted answer quality assessment
- **Personalized Recommendations**: Intelligent content recommendations based on learning behavior

### 🎯 Supported Activity Types
- **📊 Poll Activity**: Multi-option real-time voting statistics
- **✍️ Short Answer**: Open-ended Q&A
- **📝 Quiz**: Multiple choice, true/false, fill-in-the-blank question types
- **☁️ Word Cloud**: Keyword visualization display
- **🎮 Memory Game**: Interactive learning game

## 🏗️ Technology Stack

### 🔧 Backend Technologies
- **Core Framework**: Flask 2.3.3 + SQLAlchemy ORM
- **Authentication System**: Flask-Login + Email Verification
- **Real-time Communication**: Flask-SocketIO + WebSocket
- **Database**: MySQL 5.7+ / PyMySQL Driver
- **Email Service**: SMTP + 163 Email Integration
- **QR Code Generation**: qrcode + Pillow Image Processing
- **AI Integration**: OpenAI API / Custom AI Services

### 🎨 Frontend Technologies
- **UI Framework**: Bootstrap 5 + Custom CSS
- **Template Engine**: Jinja2 + Smart Filters
- **Icon Library**: Bootstrap Icons + Font Awesome
- **Interaction Enhancement**: jQuery + Native JavaScript
- **Real-time Updates**: Socket.IO Client
- **QR Code Scanning**: Native camera support on mobile devices

## 🚀 Quick Start

### 📋 Prerequisites

```
Python 3.8+          # Core runtime environment
MySQL 5.7+           # Database service 
2GB+ RAM             # Recommended memory
Docker (optional)    # Containerized deployment

# Main Python packages
Flask 2.3.3          # Web framework
SQLAlchemy           # ORM database
Flask-SocketIO       # Real-time communication
qrcode               # QR code generation
Pillow               # Image processing
PyMySQL              # MySQL driver
python-docx          # Word document processing
PyPDF2               # PDF document processing
python-pptx          # PPT document processing
```

### ⚡ Local Development Setup

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd groupproject-team_5
```

#### 2. Create Python Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Set Up MySQL Database

**Option A: Docker (Recommended)**

```bash
docker run -p 3307:3306 --name qa_platform_db \
  -e MYSQL_ROOT_PASSWORD=1234 \
  -e MYSQL_DATABASE=qa_education_platform \
  -d mysql:latest
```

**Option B: Local MySQL**

```sql
mysql -u root -p
CREATE DATABASE qa_education_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### 5. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# Database Configuration
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3307
MYSQL_USER=root
MYSQL_PASSWORD=1234
MYSQL_DATABASE=qa_education_platform

# Email Configuration (Optional)
MAIL_SERVER=smtp.163.com
MAIL_PORT=25
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@163.com
MAIL_PASSWORD=your-email-auth-code
MAIL_DEFAULT_SENDER=your-email@163.com

# AI API Configuration (Optional)
ARK_API_KEY=your-ark-api-key
OPENAI_API_KEY=your-openai-api-key
```

#### 6. Initialize Database

```bash
python run.py --init-db
```

Or manually initialize:

```bash
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
...     from app.models import User
...     from werkzeug.security import generate_password_hash
...     admin = User(email='admin@example.com', 
...                  password_hash=generate_password_hash('admin123'),
...                  name='Admin', role='admin')
...     db.session.add(admin)
...     db.session.commit()
```

#### 7. Run the Application

```bash
python run.py
```

The application will be available at `http://localhost:5001`

#### 8. Create Test Data (Optional)

```bash
python create_final_test_data.py
```

This will create:
- Teacher account: `teacher@test.com` / `teacher123`
- Test student account: `test_student@test.com` / `student123`
- 3 courses with various activities
- 150 student accounts with responses

### 📝 Default Admin Account

```
Email: admin@example.com
Password: admin123
```

> 💡 **Note**: The admin account is automatically created on first run

## 🌐 Deployment to Render

### Prerequisites

1. **GitHub Account**: Push your code to GitHub
2. **Render Account**: Sign up at https://render.com
3. **MySQL Database**: Use Railway MySQL or PlanetScale (see below)

### Step 1: Set Up MySQL Database

#### Option A: Railway MySQL (Recommended for Free Tier)

1. Go to https://railway.app
2. Sign up with GitHub
3. Create a new project
4. Click "New" → "Database" → "MySQL"
5. Wait for database creation (about 1 minute)
6. Go to "Connect" tab and copy connection details:
   - `MYSQL_HOST`: e.g., `xxxxx.railway.app`
   - `MYSQL_PORT`: e.g., `3306`
   - `MYSQL_USER`: usually `root`
   - `MYSQL_PASSWORD`: provided password
   - `MYSQL_DATABASE`: usually `railway`

#### Option B: PlanetScale

1. Go to https://planetscale.com
2. Create a free account
3. Create a new database
4. Get connection details from dashboard

### Step 2: Deploy to Render

1. **Create New Web Service**
   - Go to https://render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repository: `groupproject-team_5`

2. **Configure Service Settings**
   ```
   Name: qa-education-platform
   Region: Singapore (or closest to you)
   Branch: main (or your working branch)
   Root Directory: (leave empty)
   Runtime: Python 3
   ```

3. **Set Build & Start Commands**
   ```
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn --bind 0.0.0.0:$PORT --worker-class=eventlet --workers=1 run:app
   ```

4. **Configure Environment Variables**

   Click "Advanced" → "Add Environment Variable" and add:

   **Required Variables:**
   ```env
   PYTHON_VERSION=3.9.16
   FLASK_ENV=production
   
   # Generate SECRET_KEY with: python -c "import secrets; print(secrets.token_hex(32))"
   SECRET_KEY=<your-generated-secret-key>
   
   # Database Configuration (from Railway or PlanetScale)
   MYSQL_HOST=<your-mysql-host>
   MYSQL_PORT=<your-mysql-port>
   MYSQL_USER=<your-mysql-user>
   MYSQL_PASSWORD=<your-mysql-password>
   MYSQL_DATABASE=<your-mysql-database>
   ```

   **Optional Variables:**
   ```env
   # Email Configuration
   MAIL_SERVER=smtp.163.com
   MAIL_PORT=25
   MAIL_USE_TLS=True
   MAIL_USERNAME=<your-email@163.com>
   MAIL_PASSWORD=<your-email-auth-code>
   MAIL_DEFAULT_SENDER=<your-email@163.com>
   
   # AI API Configuration
   ARK_API_KEY=<your-ark-api-key>
   OPENAI_API_KEY=<your-openai-api-key>
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Wait 3-5 minutes for deployment
   - Your app will be available at `https://qa-education-platform.onrender.com`

### Step 3: Initialize Database on Render

1. **Open Render Shell**
   - Go to your service dashboard
   - Click "Shell" tab
   - Open a shell session

2. **Run Database Initialization**
   ```bash
   python
   >>> from app import create_app, db
   >>> app = create_app()
   >>> with app.app_context():
   ...     db.create_all()
   ...     from app.models import User
   ...     from werkzeug.security import generate_password_hash
   ...     admin = User(email='admin@example.com',
   ...                  password_hash=generate_password_hash('admin123'),
   ...                  name='Admin', role='admin')
   ...     db.session.add(admin)
   ...     db.session.commit()
   ...     print("Database initialized successfully!")
   ```

3. **Create Test Data (Optional)**
   ```bash
   python create_final_test_data.py
   ```

### Step 4: Verify Deployment

1. Visit your Render URL: `https://qa-education-platform.onrender.com`
2. Test registration and login
3. Try creating a course (as instructor)
4. Test QR code quick join feature

## 📁 Project Structure

```
groupproject-team_5/
├── app/                          # Core application directory
│   ├── __init__.py              # Flask app factory
│   ├── models.py                # Database models
│   ├── forms.py                 # WTForms forms
│   ├── ai_utils.py              # AI functionality
│   ├── email_utils.py           # Email utilities
│   ├── qr_utils.py              # QR code utilities
│   ├── utils.py                 # Time utilities
│   ├── socket_events.py         # SocketIO events
│   └── routes/                  # Route modules
│       ├── main.py              # Main routes & dashboard
│       ├── auth.py              # Authentication
│       ├── courses.py           # Course management
│       ├── activities.py        # Activity management
│       └── qa.py                # Q&A system
├── templates/                   # Jinja2 templates
│   ├── base.html               # Base template
│   ├── index.html              # Home page
│   ├── auth/                   # Authentication pages
│   ├── courses/                # Course pages
│   ├── activities/             # Activity pages
│   └── qa/                     # Q&A pages
├── static/                      # Static files
│   ├── css/                    # Stylesheets
│   ├── js/                     # JavaScript files
│   └── images/                 # Images
├── migrations/                  # Database migration scripts
├── docs/                        # Documentation files
├── scripts/                     # Utility scripts
│   └── test_scripts/           # Test scripts
├── create_final_test_data.py   # Test data generation script
├── run.py                       # Application entry point
├── wsgi.py                      # WSGI entry for production
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker configuration
└── README.md                    # This file
```

## ⚙️ Configuration

### Core Configuration

The application reads configuration from environment variables. Key variables:

- `SECRET_KEY`: Flask secret key for session encryption (required)
- `FLASK_ENV`: Environment mode (`development` or `production`)
- `MYSQL_*`: Database connection settings (required)
- `MAIL_*`: Email service configuration (optional)
- `ARK_API_KEY` / `OPENAI_API_KEY`: AI API keys (optional)

### Pagination Configuration

Default pagination settings (can be adjusted in code):

- Questions per page: 10
- Answers per page: 5
- Replies per page: 5
- Courses per page: 8
- Dashboard courses limit: 4
- Dashboard replies limit: 4

## 🔧 Troubleshooting

### Common Issues

**1. Database Connection Failed**
- Check MySQL service is running
- Verify database credentials in `.env`
- Test connection: `mysql -h HOST -P PORT -u USER -p`

**2. Email Not Sending**
- Verify SMTP credentials
- Check email is using app password (not regular password)
- Check spam folder

**3. Static Files Not Loading**
- Clear browser cache: `Ctrl+F5`
- Check `static` folder permissions
- Verify Flask static file configuration

**4. Render Deployment Failed**
- Check build logs for errors
- Verify all environment variables are set
- Ensure `requirements.txt` is correct
- Check Python version matches `PYTHON_VERSION`

**5. Database Initialization Issues**
- Run initialization in Render Shell
- Check database connection string
- Verify database user has CREATE privileges

## 📚 Documentation

Additional documentation can be found in the `docs/` directory:

- `docs/DEPLOYMENT.md` - Detailed deployment guide
- `docs/RENDER_DEPLOYMENT_GUIDE.md` - Render-specific deployment
- `docs/RAILWAY_SETUP_GUIDE.md` - Railway MySQL setup
- `docs/QRCODE_USAGE_GUIDE.md` - QR code feature usage
- And more...

## 🤝 Contributing

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Commit: `git commit -m "feat: add amazing feature"`
5. Push: `git push origin feature/amazing-feature`
6. Create Pull Request

### Code Style

- Follow PEP 8 Python style guide
- Use type hints where possible
- Write docstrings for functions
- Keep commits atomic and descriptive

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Flask](https://flask.palletsprojects.com/) - Web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM toolkit
- [Bootstrap](https://getbootstrap.com/) - UI framework
- [Font Awesome](https://fontawesome.com/) - Icons
- [Socket.IO](https://socket.io/) - Real-time communication

---

<div align="center">

### 🎉 **Making Learning More Engaging, Making Education More Efficient!**

[⭐ Star this repo](https://github.com/your-repo/qa-platform) | [🐛 Report Bug](https://github.com/your-repo/qa-platform/issues) | [💡 Request Feature](https://github.com/your-repo/qa-platform/issues/new)

**If this project helps you, please consider giving us a ⭐ Star!**

</div>
