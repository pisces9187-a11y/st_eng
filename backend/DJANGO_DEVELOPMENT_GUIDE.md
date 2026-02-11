# 🏗️ DJANGO DEVELOPMENT GUIDE - ENGLISH LEARNING PLATFORM

**Version:** 1.0.0  
**Last Updated:** December 10, 2025  
**Django Version:** 5.2.9  
**Status:** MANDATORY - Bắt buộc tuân thủ

---

## 📁 CẤU TRÚC DJANGO APP

### **Nguyên tắc phân chia App**

```
backend/
├── apps/                          # Tất cả Django apps
│   ├── users/                     # 👤 User authentication, profiles, progress
│   ├── curriculum/                # 📚 Courses, lessons, content, TTS
│   └── study/                     # 📖 Study sessions, flashcard reviews
├── config/                        # ⚙️ Django settings, main urls
├── templates/                     # 🎨 Django templates
│   ├── base/                      # Base templates
│   ├── components/                # Reusable components
│   └── pages/                     # Page templates
├── media/                         # 📁 User uploads
├── static/                        # 📂 Static files
└── manage.py
```

### **Quy tắc mỗi App**

Mỗi Django app phải có cấu trúc sau:

```
apps/<app_name>/
├── __init__.py
├── admin.py                       # Django Admin configuration
├── apps.py                        # App configuration
├── models.py                      # Database models
├── serializers.py                 # DRF serializers
├── views.py                       # API views (ViewSets)
├── views_<feature>.py             # Feature-specific views (optional)
├── template_views.py              # Template-based views (nếu có)
├── urls.py                        # URL routing
├── signals.py                     # Django signals (optional)
├── services.py                    # Business logic services (optional)
├── middleware.py                  # Custom middleware (optional)
├── permissions.py                 # Custom permissions (optional)
├── tests/                         # Tests directory
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_views.py
│   └── test_serializers.py
├── management/                    # Management commands
│   └── commands/
│       └── seed_<data>.py
└── migrations/                    # Database migrations
```

---

## 🗂️ PHÂN CHIA TRÁCH NHIỆM APP

### **1. `users` App - Quản lý người dùng**

**Trách nhiệm:**
- Authentication (Login, Logout, Register)
- User profiles và settings
- User progress tracking
- Achievements và XP
- Subscription management
- Social auth (Google, Facebook)

**Models:**
```python
# users/models.py
- User (Custom user model)
- UserProfile
- UserSettings
- Achievement
- UserAchievement
- Subscription
- UserPronunciationLessonProgress
- UserPhonemeProgress
- UserPronunciationStreak
```

**URL Patterns:**
```python
# Page URLs (namespace='users')
/                           → home
/login/                     → login
/signup/                    → signup
/dashboard/                 → dashboard
/profile/                   → profile
/pronunciation/             → pronunciation-library
/pronunciation/lesson/<slug>/ → pronunciation-lesson

# API URLs
/api/v1/auth/token/         → JWT token
/api/v1/auth/register/      → registration
/api/v1/users/me/           → current user
/api/v1/users/me/profile/   → user profile
```

### **2. `curriculum` App - Nội dung học**

**Trách nhiệm:**
- Courses, Units, Lessons
- Sentences và Flashcards
- Grammar rules
- Pronunciation (Phonemes, Words, Lessons)
- TTS (Text-to-Speech)
- Content management

**Models:**
```python
# curriculum/models.py
- Course
- Unit
- Lesson
- Sentence
- Flashcard
- GrammarRule
- Phoneme
- PhonemeCategory
- PhonemeExample
- PhonemeMinimalPair
- PronunciationLesson
- PronunciationTongueTwister
```

**URL Patterns:**
```python
# API URLs (namespace='curriculum')
/api/v1/courses/            → course list/detail
/api/v1/units/              → unit list/detail
/api/v1/lessons/            → lesson list/detail
/api/v1/sentences/          → sentence list/detail
/api/v1/flashcards/         → flashcard list/detail
/api/v1/grammar/            → grammar rules
/api/v1/tts/speak/          → TTS synthesis
/api/v1/pronunciation/lessons/   → pronunciation lessons
/api/v1/pronunciation/phonemes/  → phoneme list
```

### **3. `study` App - Hoạt động học tập**

**Trách nhiệm:**
- Study sessions
- Flashcard reviews (SRS algorithm)
- Quiz attempts
- Progress tracking per session
- Analytics data

**Models:**
```python
# study/models.py
- StudySession
- FlashcardReview
- QuizAttempt
- DictationResult
- SpeakingPractice
```

---

## 📝 QUY TẮC NAMING CONVENTIONS

### **Python/Django**

```python
# ============ MODELS ============
# Class: PascalCase (danh từ)
class UserProfile(models.Model):
    pass

class PronunciationLesson(models.Model):
    pass

# Fields: snake_case
created_at = models.DateTimeField()
is_active = models.BooleanField()
total_xp = models.IntegerField()

# ============ VIEWS ============
# API ViewSet: <Model>ViewSet
class CourseViewSet(viewsets.ModelViewSet):
    pass

# API View: <Action><Resource>View
class SaveScreenProgressView(APIView):
    pass

class CompleteLessonView(APIView):
    pass

# Template View: <Page>PageView hoặc <Page>View
class DashboardPageView(TemplateView):
    pass

class PronunciationLibraryView(TemplateView):
    pass

# ============ SERIALIZERS ============
# Format: <Model>Serializer hoặc <Model><Action>Serializer
class UserSerializer(serializers.ModelSerializer):
    pass

class UserRegistrationSerializer(serializers.Serializer):
    pass

class LessonDetailSerializer(serializers.ModelSerializer):
    pass

# ============ URLS ============
# URL name: kebab-case
path('pronunciation-library/', ..., name='pronunciation-library')
path('lesson-player/', ..., name='lesson-player')

# API URL name: <resource>-<action>
path('progress/screen/', ..., name='pronunciation-screen-progress')
path('progress/complete/', ..., name='pronunciation-complete')

# ============ MANAGEMENT COMMANDS ============
# Format: <action>_<resource>.py
seed_pronunciation_lessons.py
import_phonemes.py
export_users.py
```

### **Database Tables**

```python
# Sử dụng Meta.db_table để đặt tên bảng rõ ràng
class PronunciationLesson(models.Model):
    class Meta:
        db_table = 'pronunciation_lessons'  # snake_case, số nhiều
        
# Tên bảng theo quy tắc:
# - Singular noun: users, courses, lessons (KHÔNG DÙNG)
# - Plural noun: users, courses, lessons ✓
# - Compound: pronunciation_lessons, user_achievements ✓
```

---

## 🔗 QUY TẮC URL ROUTING

### **Nguyên tắc chung**

```python
# config/urls.py - Main URL configuration
urlpatterns = [
    # 1. Admin
    path('admin/', admin.site.urls),
    
    # 2. Page URLs (Django Templates) - với namespace
    path('', include((page_urlpatterns, 'users'), namespace='users')),
    
    # 3. API Authentication
    path('api/v1/auth/', include(auth_urlpatterns)),
    
    # 4. API Resources - với namespace
    path('api/v1/', include('apps.curriculum.urls', namespace='curriculum')),
    path('api/v1/', include('apps.study.urls', namespace='study')),
    
    # 5. API User (không namespace vì conflict với page_urlpatterns)
    path('api/v1/users/', include('apps.users.urls')),
]
```

### **Page URLs trong Template**

```django
{# ĐÚNG - Sử dụng namespace #}
<a href="{% url 'users:dashboard' %}">Dashboard</a>
<a href="{% url 'users:pronunciation-library' %}">Pronunciation</a>
<a href="{% url 'users:pronunciation-lesson' slug=lesson.slug %}">Lesson</a>

{# SAI - Không có namespace #}
<a href="{% url 'dashboard' %}">Dashboard</a>  {# ❌ NoReverseMatch #}
```

### **API URLs trong JavaScript**

```javascript
// ĐÚNG - Relative paths cho API
const API_BASE = '/api/v1';

fetch(`${API_BASE}/pronunciation/lessons/`)
fetch(`${API_BASE}/tts/speak/`)
fetch(`${API_BASE}/users/me/`)

// SAI - Hardcode full URL
fetch('http://localhost:8000/api/v1/...')  // ❌
```

---

## 🔒 API STANDARDS

### **REST API Response Format**

```python
# SUCCESS Response
{
    "status": "success",
    "data": { ... },
    "message": "Operation completed successfully"
}

# ERROR Response
{
    "status": "error",
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "errors": {
        "field_name": ["Error message"]
    }
}

# PAGINATION Response
{
    "status": "success",
    "data": {
        "results": [...],
        "count": 100,
        "next": "http://api/v1/items/?page=2",
        "previous": null
    }
}
```

### **HTTP Status Codes**

```python
# Success
200 OK              # GET, PUT, PATCH thành công
201 Created         # POST tạo mới thành công
204 No Content      # DELETE thành công

# Client Errors
400 Bad Request     # Invalid request data
401 Unauthorized    # Authentication required
403 Forbidden       # Permission denied
404 Not Found       # Resource not found
422 Unprocessable   # Validation errors

# Server Errors
500 Internal Error  # Server error
503 Service Unavail # Service temporarily unavailable
```

### **ViewSet Template**

```python
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Course CRUD operations.
    
    Endpoints:
        GET    /api/v1/courses/          - List all courses
        POST   /api/v1/courses/          - Create new course
        GET    /api/v1/courses/{id}/     - Retrieve course
        PUT    /api/v1/courses/{id}/     - Update course
        DELETE /api/v1/courses/{id}/     - Delete course
    """
    queryset = Course.objects.filter(status='published')
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'
    
    def get_queryset(self):
        """Filter queryset based on request parameters."""
        queryset = super().get_queryset()
        level = self.request.query_params.get('level')
        if level:
            queryset = queryset.filter(cefr_level=level)
        return queryset
    
    @action(detail=True, methods=['post'])
    def enroll(self, request, slug=None):
        """Custom action to enroll user in course."""
        course = self.get_object()
        # Business logic here
        return Response({'status': 'enrolled'})
```

### **APIView Template**

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

class SaveProgressView(APIView):
    """
    Save user progress for a lesson.
    
    POST /api/v1/progress/save/
    
    Request Body:
        {
            "lesson_id": 1,
            "screen": 2,
            "score": 85,
            "time_spent": 120
        }
    
    Response:
        {
            "status": "success",
            "data": {
                "progress_id": 123,
                "xp_earned": 25
            }
        }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ProgressSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            progress = self.save_progress(
                user=request.user,
                **serializer.validated_data
            )
            return Response({
                'status': 'success',
                'data': ProgressResponseSerializer(progress).data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def save_progress(self, user, **data):
        """Business logic - có thể move sang services.py"""
        # Implementation here
        pass
```

---

## 🎨 TEMPLATE ORGANIZATION

### **Base Templates**

```
templates/
├── base/
│   ├── base.html              # Base layout cho tất cả pages
│   ├── base_auth.html         # Base cho auth pages (login, signup)
│   └── base_dashboard.html    # Base cho dashboard pages (có sidebar)
├── components/
│   ├── navbar.html            # Navigation bar
│   ├── sidebar.html           # Dashboard sidebar
│   ├── footer.html            # Footer
│   ├── alerts.html            # Alert messages
│   └── pagination.html        # Pagination component
└── pages/
    ├── home.html
    ├── dashboard.html
    ├── pronunciation_library.html
    └── pronunciation_lesson.html
```

### **Template Inheritance**

```django
{# base/base.html #}
<!DOCTYPE html>
<html lang="vi">
<head>
    {% block meta %}
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    {% endblock %}
    
    <title>{% block title %}English Learning{% endblock %}</title>
    
    {% block stylesheets %}
    {# Global CSS #}
    {% endblock %}
    
    {% block extra_css %}{% endblock %}
</head>
<body class="{% block body_class %}{% endblock %}">
    {% block navbar %}{% include "components/navbar.html" %}{% endblock %}
    
    {% block content %}{% endblock %}
    
    {% block footer %}{% include "components/footer.html" %}{% endblock %}
    
    {% block scripts %}
    {# Global JS #}
    {% endblock %}
    
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### **Page Template**

```django
{# pages/pronunciation_lesson.html #}
{% extends "base/base_dashboard.html" %}

{% block title %}{{ lesson.title }} - Pronunciation{% endblock %}

{% block extra_css %}
<style>
    /* Page-specific styles */
</style>
{% endblock %}

{% block content %}
<div id="app">
    {# Vue.js app content #}
</div>
{% endblock %}

{% block extra_js %}
<script>
    // Page data from Django
    const lessonData = {{ lesson_json|safe }};
    const phonemesData = {{ phonemes_json|safe }};
    
    // Vue.js app
    const { createApp } = Vue;
    createApp({
        delimiters: ['[[', ']]'],  // Avoid Django template conflict
        data() {
            return {
                lesson: lessonData,
                phonemes: phonemesData
            };
        }
    }).mount('#app');
</script>
{% endblock %}
```

---

## ⚡ VUE.JS INTEGRATION

### **Vue.js với Django Templates**

```javascript
// QUAN TRỌNG: Sử dụng delimiters khác để tránh conflict với Django
const { createApp } = Vue;

createApp({
    delimiters: ['[[', ']]'],  // ✓ Dùng [[ ]] thay vì {{ }}
    
    data() {
        return {
            // State
        };
    },
    
    computed: {
        // Computed properties
    },
    
    methods: {
        // Methods
    },
    
    mounted() {
        // Lifecycle
    }
}).mount('#app');
```

### **Truyền dữ liệu từ Django sang Vue**

```python
# views.py
class PronunciationLessonView(TemplateView):
    template_name = 'pages/pronunciation_lesson.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        lesson = PronunciationLesson.objects.get(slug=kwargs['slug'])
        
        # Serialize data to JSON
        context['lesson_json'] = json.dumps({
            'id': lesson.id,
            'title': lesson.title,
            'slug': lesson.slug,
            # ... other fields
        }, ensure_ascii=False)
        
        context['phonemes_json'] = json.dumps([
            {
                'id': p.id,
                'symbol': p.ipa_symbol,
                'name': p.name
            }
            for p in lesson.phonemes.all()
        ], ensure_ascii=False)
        
        return context
```

```django
{# template #}
<script>
    // Nhận dữ liệu từ Django
    const lessonData = {{ lesson_json|safe }};
    const phonemesData = {{ phonemes_json|safe }};
</script>
```

### **API Calls từ Vue**

```javascript
const app = createApp({
    delimiters: ['[[', ']]'],
    
    data() {
        return {
            loading: false,
            error: null,
            lessons: []
        };
    },
    
    methods: {
        async fetchLessons() {
            this.loading = true;
            this.error = null;
            
            try {
                const response = await fetch('/api/v1/pronunciation/lessons/', {
                    headers: {
                        'Content-Type': 'application/json',
                        // JWT token nếu authenticated
                        'Authorization': `Bearer ${this.getAccessToken()}`
                    }
                });
                
                if (!response.ok) {
                    throw new Error('Failed to fetch lessons');
                }
                
                const data = await response.json();
                this.lessons = data.results || data;
                
            } catch (error) {
                this.error = error.message;
                console.error('Error:', error);
            } finally {
                this.loading = false;
            }
        },
        
        async saveProgress(progressData) {
            try {
                const response = await fetch('/api/v1/pronunciation/progress/screen/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.getAccessToken()}`
                    },
                    body: JSON.stringify(progressData)
                });
                
                if (!response.ok) {
                    throw new Error('Failed to save progress');
                }
                
                return await response.json();
                
            } catch (error) {
                console.error('Save progress error:', error);
                throw error;
            }
        },
        
        getAccessToken() {
            return localStorage.getItem('access_token') || '';
        }
    },
    
    mounted() {
        this.fetchLessons();
    }
});
```

---

## 🧪 TESTING STANDARDS

### **Test File Structure**

```
apps/<app_name>/tests/
├── __init__.py
├── test_models.py       # Model tests
├── test_views.py        # API view tests
├── test_serializers.py  # Serializer tests
└── factories.py         # Test factories (factory_boy)
```

### **Test Naming Convention**

```python
# test_models.py
class TestUserModel:
    def test_user_creation_with_valid_data(self):
        """User model should create successfully with valid data."""
        pass
    
    def test_user_email_must_be_unique(self):
        """User creation should fail with duplicate email."""
        pass

# test_views.py
class TestCourseViewSet:
    def test_list_courses_returns_published_only(self):
        """GET /api/v1/courses/ should return only published courses."""
        pass
    
    def test_create_course_requires_authentication(self):
        """POST /api/v1/courses/ should return 401 for anonymous users."""
        pass
```

### **API Test Template**

```python
import pytest
from rest_framework.test import APIClient
from rest_framework import status

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client

class TestPronunciationLessonAPI:
    
    @pytest.mark.django_db
    def test_list_lessons_success(self, authenticated_client):
        """GET /api/v1/pronunciation/lessons/ should return lesson list."""
        response = authenticated_client.get('/api/v1/pronunciation/lessons/')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data or isinstance(response.data, list)
    
    @pytest.mark.django_db
    def test_save_progress_creates_record(self, authenticated_client, lesson):
        """POST /api/v1/pronunciation/progress/screen/ should save progress."""
        payload = {
            'lesson_id': lesson.id,
            'screen_number': 1,
            'score': 85
        }
        
        response = authenticated_client.post(
            '/api/v1/pronunciation/progress/screen/',
            data=payload,
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'success'
```

---

## 📦 MANAGEMENT COMMANDS

### **Seed Data Command Template**

```python
# management/commands/seed_pronunciation_lessons.py
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.curriculum.models import PronunciationLesson, Phoneme

class Command(BaseCommand):
    help = 'Seed pronunciation lessons with sample data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding'
        )
    
    def handle(self, *args, **options):
        self.stdout.write('Starting pronunciation lessons seed...')
        
        try:
            with transaction.atomic():
                if options['clear']:
                    self._clear_data()
                
                self._seed_lessons()
                
            self.stdout.write(
                self.style.SUCCESS('Successfully seeded pronunciation lessons!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error seeding data: {str(e)}')
            )
            raise
    
    def _clear_data(self):
        """Clear existing data."""
        PronunciationLesson.objects.all().delete()
        self.stdout.write('Cleared existing lessons')
    
    def _seed_lessons(self):
        """Seed lesson data."""
        lessons_data = [
            {
                'title': 'Vowel /iː/ vs /ɪ/',
                'slug': 'vowel-i-long-short',
                'description': 'Learn the difference...'
            },
            # More lessons...
        ]
        
        for data in lessons_data:
            lesson, created = PronunciationLesson.objects.get_or_create(
                slug=data['slug'],
                defaults=data
            )
            
            status = 'Created' if created else 'Exists'
            self.stdout.write(f'  {status}: {lesson.title}')
```

---

## 🔐 SECURITY BEST PRACTICES

### **Django Settings**

```python
# settings/base.py
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')  # NEVER hardcode

# settings/production.py
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
```

### **API Security**

```python
# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# CORS Settings (development)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

### **Input Validation**

```python
# serializers.py
class UserInputSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        min_length=8,
        write_only=True,
        validators=[validate_password]  # Django's password validators
    )
    
    def validate_email(self, value):
        """Validate email is not already registered."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already registered')
        return value.lower()  # Normalize
```

---

## 📋 CHECKLIST TRƯỚC KHI COMMIT

### **Code Quality**

- [ ] Tuân thủ PEP 8 style guide
- [ ] Docstrings cho tất cả classes và functions
- [ ] Type hints cho function parameters
- [ ] Không có hardcoded values (dùng settings/constants)
- [ ] Không có console.log/print statements không cần thiết

### **Database**

- [ ] Migrations đã được tạo và chạy
- [ ] Indexes cho frequently queried fields
- [ ] Foreign keys có on_delete behavior
- [ ] Không có N+1 query problems (dùng select_related/prefetch_related)

### **API**

- [ ] Response format consistent
- [ ] Proper HTTP status codes
- [ ] Error messages rõ ràng
- [ ] Authentication/Authorization đúng
- [ ] Input validation

### **Templates**

- [ ] Extends đúng base template
- [ ] URL tags sử dụng namespace
- [ ] Static files qua {% static %}
- [ ] No hardcoded URLs

### **Vue.js**

- [ ] Delimiters: ['[[', ']]']
- [ ] Data từ Django qua JSON
- [ ] Error handling cho API calls
- [ ] Loading states

---

## 🚫 ĐIỀU CẤM KỴ

1. ❌ **KHÔNG hardcode URLs** → Dùng `{% url %}` hoặc `reverse()`
2. ❌ **KHÔNG inline SQL queries** → Dùng Django ORM
3. ❌ **KHÔNG store passwords plain text** → Dùng Django's password hashing
4. ❌ **KHÔNG commit .env files** → Thêm vào .gitignore
5. ❌ **KHÔNG commit migrations chưa test** → Test locally trước
6. ❌ **KHÔNG dùng `*` import** → Import explicit
7. ❌ **KHÔNG bypass authentication** → Luôn check permissions
8. ❌ **KHÔNG return sensitive data** → Exclude password, tokens
9. ❌ **KHÔNG catch generic Exception** → Catch specific exceptions
10. ❌ **KHÔNG mix business logic trong views** → Tách sang services

---

**🔒 QUY CHUẨN NÀY LÀ BẮT BUỘC**

**Author:** Development Team  
**Review Cycle:** Monthly  
**Next Review:** January 10, 2026
