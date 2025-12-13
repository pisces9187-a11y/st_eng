# 🔌 API GUIDELINES - ENGLISH LEARNING PLATFORM

**Version:** 1.0.0  
**Last Updated:** December 10, 2025  
**Django REST Framework:** 3.15.x

---

## 📋 MỤC LỤC

1. [API Structure](#api-structure)
2. [URL Conventions](#url-conventions)
3. [Request/Response Format](#requestresponse-format)
4. [Authentication](#authentication)
5. [Error Handling](#error-handling)
6. [Pagination](#pagination)
7. [Filtering & Searching](#filtering--searching)
8. [Serializers](#serializers)
9. [ViewSets vs APIViews](#viewsets-vs-apiviews)
10. [Testing APIs](#testing-apis)

---

## 🏗️ API STRUCTURE

### **Base URL**

```
Production:  https://api.englishlearning.com/api/v1/
Development: http://127.0.0.1:8000/api/v1/
```

### **API Namespaces**

| Namespace | Base Path | App | Description |
|-----------|-----------|-----|-------------|
| `auth` | `/api/v1/auth/` | users | Authentication endpoints |
| `users` | `/api/v1/users/` | users | User management |
| `curriculum` | `/api/v1/` | curriculum | Courses, lessons, content |
| `study` | `/api/v1/` | study | Study sessions, reviews |

### **Endpoint Categories**

```
/api/v1/
├── auth/                    # Authentication
│   ├── token/              # JWT token obtain
│   ├── token/refresh/      # JWT token refresh
│   ├── register/           # User registration
│   └── logout/             # User logout
│
├── users/                   # User Management
│   ├── me/                 # Current user profile
│   ├── me/profile/         # Update profile
│   ├── me/settings/        # User settings
│   └── me/achievements/    # User achievements
│
├── courses/                 # Course Content
│   ├── /                   # List courses
│   ├── {slug}/             # Course detail
│   └── {slug}/enroll/      # Enroll in course
│
├── lessons/                 # Lessons
│   ├── /                   # List lessons
│   └── {slug}/             # Lesson detail
│
├── pronunciation/           # Pronunciation Learning
│   ├── lessons/            # Pronunciation lessons
│   ├── phonemes/           # Phoneme list
│   └── progress/           # User progress
│
└── tts/                     # Text-to-Speech
    ├── speak/              # Generate speech
    └── voices/             # Available voices
```

---

## 🔗 URL CONVENTIONS

### **RESTful URL Patterns**

```python
# CRUD Operations - Standard REST
GET    /api/v1/courses/              # List all courses
POST   /api/v1/courses/              # Create new course
GET    /api/v1/courses/{slug}/       # Retrieve single course
PUT    /api/v1/courses/{slug}/       # Full update course
PATCH  /api/v1/courses/{slug}/       # Partial update course
DELETE /api/v1/courses/{slug}/       # Delete course

# Nested Resources
GET    /api/v1/courses/{slug}/units/           # Units in course
GET    /api/v1/courses/{slug}/units/{id}/      # Specific unit

# Actions (Custom endpoints)
POST   /api/v1/courses/{slug}/enroll/          # Enroll action
POST   /api/v1/pronunciation/progress/screen/  # Save screen progress
POST   /api/v1/pronunciation/progress/complete/ # Complete lesson
```

### **URL Naming Rules**

```python
# urls.py
urlpatterns = [
    # Resource list/create: noun plural
    path('courses/', CourseViewSet.as_view({'get': 'list', 'post': 'create'}), name='course-list'),
    
    # Resource detail: noun-detail
    path('courses/<slug:slug>/', CourseViewSet.as_view({...}), name='course-detail'),
    
    # Custom actions: noun-action
    path('courses/<slug:slug>/enroll/', ..., name='course-enroll'),
    
    # Progress tracking: resource-action
    path('pronunciation/progress/screen/', ..., name='pronunciation-screen-progress'),
    path('pronunciation/progress/complete/', ..., name='pronunciation-complete'),
]
```

### **URL Parameter Types**

```python
# Use slug for public resources (SEO-friendly)
path('courses/<slug:slug>/', ...)          # /courses/english-a1/
path('lessons/<slug:slug>/', ...)          # /lessons/present-simple/

# Use int:pk for internal resources
path('flashcards/<int:pk>/', ...)          # /flashcards/123/

# Use uuid for sensitive resources
path('sessions/<uuid:session_id>/', ...)   # /sessions/550e8400-e29b-41d4-a716.../
```

---

## 📨 REQUEST/RESPONSE FORMAT

### **Request Headers**

```http
Content-Type: application/json
Accept: application/json
Authorization: Bearer <access_token>
X-CSRFToken: <csrf_token>          # For browser requests
```

### **Success Response Format**

```json
// Single Resource
{
    "status": "success",
    "data": {
        "id": 1,
        "title": "English A1",
        "slug": "english-a1",
        "description": "Beginner course",
        "created_at": "2025-12-10T10:30:00Z"
    }
}

// List Resources (Paginated)
{
    "status": "success",
    "data": {
        "count": 50,
        "next": "http://api/v1/courses/?page=2",
        "previous": null,
        "results": [
            { "id": 1, "title": "English A1", ... },
            { "id": 2, "title": "English A2", ... }
        ]
    }
}

// Action Response
{
    "status": "success",
    "message": "Lesson completed successfully",
    "data": {
        "xp_earned": 25,
        "total_xp": 1250,
        "achievement_unlocked": null
    }
}
```

### **Error Response Format**

```json
// Validation Error
{
    "status": "error",
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "errors": {
        "email": ["This field is required."],
        "password": ["Password must be at least 8 characters."]
    }
}

// Not Found Error
{
    "status": "error",
    "code": "NOT_FOUND",
    "message": "Course not found"
}

// Authentication Error
{
    "status": "error",
    "code": "AUTHENTICATION_FAILED",
    "message": "Invalid credentials"
}

// Permission Error
{
    "status": "error",
    "code": "PERMISSION_DENIED",
    "message": "You don't have permission to perform this action"
}
```

### **HTTP Status Codes**

| Code | Meaning | When to Use |
|------|---------|-------------|
| **200** | OK | GET, PUT, PATCH success |
| **201** | Created | POST create success |
| **204** | No Content | DELETE success |
| **400** | Bad Request | Invalid request body |
| **401** | Unauthorized | Missing/invalid token |
| **403** | Forbidden | Valid token but no permission |
| **404** | Not Found | Resource doesn't exist |
| **422** | Unprocessable | Validation failed |
| **429** | Too Many Requests | Rate limit exceeded |
| **500** | Server Error | Internal error |

---

## 🔐 AUTHENTICATION

### **JWT Token Flow**

```python
# 1. Obtain Token
POST /api/v1/auth/token/
{
    "email": "user@example.com",
    "password": "password123"
}

Response:
{
    "access": "eyJ0eXAiOiJKV1Q...",
    "refresh": "eyJ0eXAiOiJKV1Q..."
}

# 2. Use Access Token
GET /api/v1/users/me/
Headers:
    Authorization: Bearer eyJ0eXAiOiJKV1Q...

# 3. Refresh Token (when access expires)
POST /api/v1/auth/token/refresh/
{
    "refresh": "eyJ0eXAiOiJKV1Q..."
}

Response:
{
    "access": "eyJ0eXAiOiJKV1Q..." (new)
}
```

### **Permission Classes**

```python
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser

class CourseViewSet(viewsets.ModelViewSet):
    # Default: require authentication
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        # Allow unauthenticated for list/retrieve
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        # Require admin for create/update/delete
        if self.action in ['create', 'update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()
```

---

## ❌ ERROR HANDLING

### **Custom Exception Handler**

```python
# config/exception_handler.py
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if response is not None:
        error_data = {
            'status': 'error',
            'code': get_error_code(exc),
            'message': get_error_message(exc, response),
        }
        
        if hasattr(response.data, 'items'):
            error_data['errors'] = response.data
        
        response.data = error_data
    
    return response

def get_error_code(exc):
    """Map exception to error code."""
    from rest_framework.exceptions import (
        ValidationError, NotFound, PermissionDenied,
        AuthenticationFailed, NotAuthenticated
    )
    
    error_codes = {
        ValidationError: 'VALIDATION_ERROR',
        NotFound: 'NOT_FOUND',
        PermissionDenied: 'PERMISSION_DENIED',
        AuthenticationFailed: 'AUTHENTICATION_FAILED',
        NotAuthenticated: 'AUTHENTICATION_REQUIRED',
    }
    
    return error_codes.get(type(exc), 'SERVER_ERROR')
```

### **Settings Configuration**

```python
# settings.py
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'config.exception_handler.custom_exception_handler',
}
```

---

## 📄 PAGINATION

### **Standard Pagination**

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
```

### **Custom Pagination**

```python
# pagination.py
from rest_framework.pagination import PageNumberPagination

class StandardResultsPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'status': 'success',
            'data': {
                'count': self.page.paginator.count,
                'total_pages': self.page.paginator.num_pages,
                'current_page': self.page.number,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'results': data
            }
        })
```

---

## 🔍 FILTERING & SEARCHING

### **Using django-filter**

```python
# views.py
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    # Exact filters
    filterset_fields = ['cefr_level', 'status', 'is_free']
    
    # Search fields
    search_fields = ['title', 'description']
    
    # Ordering fields
    ordering_fields = ['created_at', 'title', 'order']
    ordering = ['order', 'title']  # Default ordering
```

### **Usage**

```http
# Filter by level
GET /api/v1/courses/?cefr_level=A1

# Search
GET /api/v1/courses/?search=beginner

# Ordering
GET /api/v1/courses/?ordering=-created_at

# Combined
GET /api/v1/courses/?cefr_level=A1&search=grammar&ordering=title
```

---

## 📝 SERIALIZERS

### **Model Serializer Template**

```python
# serializers.py
from rest_framework import serializers
from .models import Course, Unit

class CourseSerializer(serializers.ModelSerializer):
    """Serializer for Course model."""
    
    # Computed fields
    total_units = serializers.IntegerField(read_only=True)
    total_lessons = serializers.IntegerField(read_only=True)
    
    # Nested serializer (read-only)
    units = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'thumbnail',
            'cefr_level', 'estimated_hours', 'status',
            'is_free', 'is_featured', 'order',
            'total_units', 'total_lessons', 'units',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']
    
    def get_units(self, obj):
        """Return units for this course."""
        units = obj.units.filter(status='published')[:5]
        return UnitListSerializer(units, many=True).data


class CourseCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Course."""
    
    class Meta:
        model = Course
        fields = ['title', 'description', 'cefr_level', 'is_free']
    
    def validate_title(self, value):
        """Validate title is not duplicate."""
        if Course.objects.filter(title=value).exists():
            raise serializers.ValidationError('Course with this title already exists.')
        return value
```

### **Nested Write Serializer**

```python
class LessonWithSentencesSerializer(serializers.ModelSerializer):
    """Serializer for Lesson with nested Sentences (writable)."""
    
    sentences = SentenceSerializer(many=True, required=False)
    
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'content', 'sentences']
    
    def create(self, validated_data):
        sentences_data = validated_data.pop('sentences', [])
        lesson = Lesson.objects.create(**validated_data)
        
        for sentence_data in sentences_data:
            Sentence.objects.create(lesson=lesson, **sentence_data)
        
        return lesson
    
    def update(self, instance, validated_data):
        sentences_data = validated_data.pop('sentences', None)
        
        # Update lesson fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update sentences if provided
        if sentences_data is not None:
            instance.sentences.all().delete()
            for sentence_data in sentences_data:
                Sentence.objects.create(lesson=instance, **sentence_data)
        
        return instance
```

---

## 🎯 VIEWSETS VS APIVIEWS

### **Khi nào dùng ViewSet**

- CRUD operations đầy đủ
- Resources theo chuẩn REST
- Routing tự động với Router

```python
# views.py
from rest_framework import viewsets

class CourseViewSet(viewsets.ModelViewSet):
    """
    CRUD ViewSet for Course.
    
    Endpoints:
        GET    /courses/         - List
        POST   /courses/         - Create
        GET    /courses/{slug}/  - Retrieve
        PUT    /courses/{slug}/  - Update
        DELETE /courses/{slug}/  - Delete
    """
    queryset = Course.objects.filter(status='published')
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'
    
    @action(detail=True, methods=['post'])
    def enroll(self, request, slug=None):
        """Custom action: POST /courses/{slug}/enroll/"""
        course = self.get_object()
        # Enrollment logic
        return Response({'enrolled': True})
```

### **Khi nào dùng APIView**

- Custom logic phức tạp
- Không theo pattern CRUD
- Multiple operations trong 1 endpoint

```python
# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class SaveProgressView(APIView):
    """
    Save user learning progress.
    
    POST /api/v1/pronunciation/progress/screen/
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
            progress = self._save_progress(
                user=request.user,
                **serializer.validated_data
            )
            
            return Response({
                'status': 'success',
                'data': {
                    'progress_id': progress.id,
                    'xp_earned': progress.xp_earned
                }
            })
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _save_progress(self, user, lesson_id, screen_number, score):
        """Business logic for saving progress."""
        # Implementation
        pass
```

---

## 🧪 TESTING APIS

### **Test Structure**

```python
# tests/test_views.py
import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client

@pytest.fixture
def user(db):
    from apps.users.models import User
    return User.objects.create_user(
        email='test@example.com',
        password='testpass123'
    )


class TestCourseAPI:
    """Test cases for Course API."""
    
    @pytest.mark.django_db
    def test_list_courses_success(self, api_client):
        """GET /api/v1/courses/ returns 200 and course list."""
        url = reverse('curriculum:course-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data or isinstance(response.data, list)
    
    @pytest.mark.django_db
    def test_create_course_requires_auth(self, api_client):
        """POST /api/v1/courses/ returns 401 for anonymous user."""
        url = reverse('curriculum:course-list')
        response = api_client.post(url, {'title': 'Test'})
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.django_db
    def test_create_course_success(self, authenticated_client, admin_user):
        """POST /api/v1/courses/ creates course for admin."""
        authenticated_client.force_authenticate(user=admin_user)
        url = reverse('curriculum:course-list')
        
        payload = {
            'title': 'New Course',
            'description': 'Test description',
            'cefr_level': 'A1'
        }
        
        response = authenticated_client.post(url, payload, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'New Course'
```

---

## ✅ API CHECKLIST

### **Trước khi deploy API mới**

- [ ] URL theo RESTful convention
- [ ] Response format consistent
- [ ] HTTP status codes đúng
- [ ] Error messages rõ ràng (không leak sensitive info)
- [ ] Authentication/Authorization đúng
- [ ] Input validation đầy đủ
- [ ] Pagination cho list endpoints
- [ ] Docstrings cho ViewSet/APIView
- [ ] Unit tests
- [ ] API documentation (Swagger/ReDoc)

---

**🔒 TUÂN THỦ API GUIDELINES NÀY CHO TẤT CẢ ENDPOINTS**
