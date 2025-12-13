# English Learning Platform - Django Backend

Hệ thống backend cho nền tảng học tiếng Anh, được xây dựng với Django 5.x và Django REST Framework.

## 🛠️ Tech Stack

- **Framework**: Django 5.x
- **API**: Django REST Framework 3.14+
- **Database**: PostgreSQL 15+ (production) / SQLite (development)
- **Cache**: Redis
- **Task Queue**: Celery
- **Authentication**: JWT (djangorestframework-simplejwt)

## 📁 Project Structure

```
backend/
├── apps/                       # Django applications
│   ├── users/                  # User management & authentication
│   │   ├── models.py          # User, Profile, Settings, Subscription, Achievement
│   │   ├── serializers.py     # DRF serializers
│   │   ├── views.py           # API views
│   │   ├── urls.py            # URL routing
│   │   └── admin.py           # Admin configuration
│   │
│   ├── curriculum/            # Course content management
│   │   ├── models.py          # Course, Unit, Lesson, Sentence, Flashcard, GrammarRule
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── admin.py
│   │
│   └── study/                 # Learning progress & SRS
│       ├── models.py          # Progress, UserFlashcard, PracticeSession, Streak
│       ├── serializers.py
│       ├── views.py
│       ├── urls.py
│       └── admin.py
│
├── config/                    # Django configuration
│   ├── settings/
│   │   ├── base.py           # Base settings
│   │   ├── development.py    # Development settings
│   │   └── production.py     # Production settings
│   ├── urls.py               # Root URL configuration
│   ├── wsgi.py               # WSGI application
│   └── asgi.py               # ASGI application
│
├── requirements/              # Python dependencies
│   ├── base.txt              # Core dependencies
│   ├── development.txt       # Development tools
│   └── production.txt        # Production dependencies
│
├── manage.py                  # Django management script
└── .env.example              # Environment variables template
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.11+
- PostgreSQL 15+ (for production)
- Redis (for caching & Celery)

### 2. Setup Development Environment

```bash
# Clone repository
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements/development.txt

# Copy environment file
cp .env.example .env

# Edit .env with your settings
```

### 3. Database Setup

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# (Optional) Load sample data
python manage.py loaddata fixtures/sample_data.json
```

### 4. Run Development Server

```bash
python manage.py runserver
```

Server will be available at: http://localhost:8000

### 5. Access Admin Panel

- URL: http://localhost:8000/admin/
- Login with superuser credentials

## 📚 API Documentation

After starting the server, API documentation is available at:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## 🔑 API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register/` | Register new user |
| POST | `/api/v1/auth/token/` | Get JWT tokens |
| POST | `/api/v1/auth/token/refresh/` | Refresh access token |
| POST | `/api/v1/auth/password-reset/` | Request password reset |

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/me/` | Get current user |
| PATCH | `/api/v1/users/me/` | Update current user |
| GET | `/api/v1/users/me/profile/` | Get user profile |
| GET | `/api/v1/users/me/settings/` | Get user settings |
| GET | `/api/v1/users/me/subscription/` | Get subscription info |
| GET | `/api/v1/users/leaderboard/` | Get leaderboard |

### Curriculum

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/courses/` | List courses |
| GET | `/api/v1/courses/{slug}/` | Get course detail |
| GET | `/api/v1/units/{id}/` | Get unit detail |
| GET | `/api/v1/lessons/{slug}/` | Get lesson detail |
| GET | `/api/v1/flashcards/` | List flashcards |
| GET | `/api/v1/grammar/` | List grammar rules |

### Study & Progress

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/dashboard/` | Get dashboard data |
| GET | `/api/v1/enrollments/` | List course enrollments |
| POST | `/api/v1/enrollments/` | Enroll in course |
| GET | `/api/v1/srs/flashcards/due/` | Get due flashcards |
| POST | `/api/v1/srs/flashcards/review/` | Submit review |
| GET | `/api/v1/goals/` | List learning goals |
| GET | `/api/v1/streaks/` | Get streak history |

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps

# Run specific app tests
pytest apps/users/tests/
```

## 🔧 Development Commands

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run Celery worker
celery -A config worker -l info

# Run Celery beat (scheduler)
celery -A config beat -l info

# Shell
python manage.py shell_plus
```

## 📦 Deployment

### Using Docker

```bash
# Build image
docker build -t english-study-backend .

# Run container
docker-compose up -d
```

### Using Gunicorn

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

## 📄 License

This project is proprietary and confidential.

## 👥 Authors

- Development Team - English Learning Platform
