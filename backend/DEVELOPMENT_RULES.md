# 📋 BỘ QUY TẮC PHÁT TRIỂN DỰ ÁN
## English Learning Platform - Django + Vue.js

**Version:** 1.0  
**Ngày tạo:** 08/12/2025  
**Stack:** Django REST Framework + Vue.js 3 + PostgreSQL

---

## 🎯 MỤC TIÊU DỰ ÁN

### Vision
Xây dựng nền tảng học tiếng Anh toàn diện với phương pháp IC/DC độc đáo, tập trung vào thị trường Việt Nam.

### Core Features
1. **Học bài với IC/DC Grammar Highlighting** - Điểm khác biệt chính
2. **Nghe chép chính tả (Dictation)** - Câu riêng rẽ với audio
3. **Flashcard với SRS (Spaced Repetition)** - Thuật toán SuperMemo-2
4. **Gamification** - XP, Streak, Leaderboard, Achievements
5. **PWA + Offline Support** - Học mọi lúc mọi nơi

---

## 🏗️ KIẾN TRÚC HỆ THỐNG

### Tech Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Vue.js 3 + Vite + Pinia + Vue Router                   │    │
│  │  - Composition API                                       │    │
│  │  - TypeScript (recommended)                              │    │
│  │  - Tailwind CSS / Bootstrap 5                            │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ REST API (JSON)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         BACKEND                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Django 5.x + Django REST Framework                      │    │
│  │  - JWT Authentication (SimpleJWT)                        │    │
│  │  - drf-spectacular (OpenAPI docs)                        │    │
│  │  - django-cors-headers                                   │    │
│  │  - django-filter                                         │    │
│  │  - celery + redis (background tasks)                     │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         DATABASE                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  PostgreSQL 15+                                          │    │
│  │  - JSONB for grammar_analysis                            │    │
│  │  - Full-text search                                      │    │
│  │  - Indexing optimization                                 │    │
│  └─────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Redis                                                   │    │
│  │  - Caching                                               │    │
│  │  - Session storage                                       │    │
│  │  - Celery broker                                         │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         STORAGE                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  AWS S3 / MinIO / Local                                  │    │
│  │  - Audio files (sentences, vocabulary)                   │    │
│  │  - Images (avatars, thumbnails)                          │    │
│  │  - Videos (lessons)                                      │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### Cấu Trúc Thư Mục

```
english_study/
├── backend/                    # Django project
│   ├── config/                 # Project settings
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   └── production.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── users/              # User management
│   │   ├── curriculum/         # Courses, Lessons, Content
│   │   ├── study/              # User progress, SRS
│   │   ├── gamification/       # XP, Achievements, Leaderboard
│   │   └── payments/           # Subscriptions, Transactions
│   ├── api/
│   │   └── v1/                 # API version 1
│   ├── utils/                  # Shared utilities
│   ├── manage.py
│   └── requirements/
│       ├── base.txt
│       ├── development.txt
│       └── production.txt
│
├── frontend/                   # Vue.js project
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── composables/
│   │   ├── layouts/
│   │   ├── pages/
│   │   ├── router/
│   │   ├── stores/
│   │   ├── services/
│   │   └── types/
│   ├── public/
│   └── package.json
│
├── public/                     # Static HTML (existing)
├── admin/                      # Admin HTML (existing)
├── assets/                     # Shared assets
├── docs/                       # Documentation
└── docker/                     # Docker configs
```

---

## 📐 QUY TẮC CODE

### 1. Backend (Django/Python)

#### Naming Conventions
```python
# Models: PascalCase, số ít
class UserFlashcard(models.Model):
    pass

# Views/Serializers: PascalCase + hậu tố
class FlashcardViewSet(viewsets.ModelViewSet):
    pass
class FlashcardSerializer(serializers.ModelSerializer):
    pass

# Functions/Variables: snake_case
def calculate_next_review_date():
    user_progress = get_user_progress()

# Constants: UPPER_SNAKE_CASE
MAX_BOX_LEVEL = 5
DEFAULT_EASE_FACTOR = 2.5

# URLs: kebab-case
# /api/v1/user-flashcards/
# /api/v1/lesson-progress/
```

#### Code Style
```python
# Luôn sử dụng type hints
from typing import Optional, List

def get_due_flashcards(user_id: int, limit: Optional[int] = 20) -> List[dict]:
    """
    Lấy danh sách flashcard cần ôn tập.
    
    Args:
        user_id: ID của user
        limit: Số lượng tối đa
        
    Returns:
        Danh sách flashcard cần ôn
    """
    pass

# Sử dụng dataclasses hoặc Pydantic cho DTOs
from dataclasses import dataclass

@dataclass
class ReviewResult:
    flashcard_id: int
    quality: int  # 0-5
    time_spent_ms: int
```

#### API Response Format
```python
# Success Response
{
    "success": True,
    "data": { ... },
    "meta": {
        "total": 100,
        "page": 1,
        "per_page": 20
    }
}

# Error Response
{
    "success": False,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Dữ liệu không hợp lệ",
        "details": {
            "email": ["Email đã tồn tại"]
        }
    }
}
```

### 2. Frontend (Vue.js)

#### Naming Conventions
```typescript
// Components: PascalCase
// FlashcardViewer.vue
// LessonPlayer.vue

// Composables: useCamelCase
// useFlashcard.ts
// useAuth.ts

// Stores: camelCase + Store
// userStore.ts
// flashcardStore.ts

// Types/Interfaces: PascalCase + I prefix (optional)
interface IFlashcard {
    id: number;
    term: string;
    definition: string;
}
```

#### Component Structure
```vue
<script setup lang="ts">
// 1. Imports
import { ref, computed, onMounted } from 'vue'
import { useFlashcardStore } from '@/stores/flashcard'

// 2. Props & Emits
const props = defineProps<{
    flashcardId: number
}>()

const emit = defineEmits<{
    (e: 'review', quality: number): void
}>()

// 3. Composables & Stores
const store = useFlashcardStore()

// 4. Reactive State
const isFlipped = ref(false)

// 5. Computed
const currentCard = computed(() => store.currentCard)

// 6. Methods
const flipCard = () => {
    isFlipped.value = !isFlipped.value
}

// 7. Lifecycle
onMounted(() => {
    store.loadCard(props.flashcardId)
})
</script>

<template>
    <!-- Template -->
</template>

<style scoped>
/* Styles */
</style>
```

### 3. Database

#### Naming Conventions
```sql
-- Tables: snake_case, số nhiều
users, flashcards, user_flashcards

-- Columns: snake_case
user_id, created_at, next_review_date

-- Foreign Keys: {table}_id
user_id, lesson_id, flashcard_id

-- Indexes: idx_{table}_{columns}
idx_user_flashcards_user_next_review

-- Constraints: {table}_{type}_{description}
user_flashcards_unique_user_flashcard
```

---

## 🔐 QUY TẮC BẢO MẬT

### Authentication
```python
# Sử dụng JWT với refresh token
ACCESS_TOKEN_LIFETIME = timedelta(minutes=15)
REFRESH_TOKEN_LIFETIME = timedelta(days=7)

# Luôn validate input
from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8)
```

### Authorization
```python
# Sử dụng permissions
from rest_framework.permissions import IsAuthenticated

class FlashcardViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        # Chỉ trả về data của user hiện tại
        return Flashcard.objects.filter(
            user_flashcards__user=self.request.user
        )
```

### Data Protection
```python
# Hash passwords (Django tự động)
# Sanitize HTML input
import bleach

def sanitize_html(html_content: str) -> str:
    allowed_tags = ['p', 'strong', 'em', 'mark', 'span']
    return bleach.clean(html_content, tags=allowed_tags)
```

---

## 📊 QUY TẮC API

### Versioning
```
/api/v1/flashcards/
/api/v1/lessons/
```

### HTTP Methods
```
GET    /flashcards/           # List
GET    /flashcards/{id}/      # Detail
POST   /flashcards/           # Create
PUT    /flashcards/{id}/      # Update (full)
PATCH  /flashcards/{id}/      # Update (partial)
DELETE /flashcards/{id}/      # Delete

# Custom actions
POST   /flashcards/{id}/review/    # Record review
GET    /flashcards/due/            # Get due cards
```

### Pagination
```python
{
    "data": [...],
    "meta": {
        "total": 1000,
        "page": 1,
        "per_page": 20,
        "total_pages": 50,
        "has_next": True,
        "has_prev": False
    }
}
```

### Filtering & Sorting
```
GET /flashcards/?level=A1&word_type=noun&ordering=-created_at
GET /lessons/?course_id=1&is_completed=false
```

---

## 🧪 QUY TẮC TESTING

### Backend
```python
# Test file naming: test_{module}.py
# tests/test_flashcard.py

import pytest
from django.test import TestCase

class FlashcardAPITestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(...)
        
    def test_get_due_flashcards(self):
        """Test lấy danh sách flashcard cần ôn"""
        response = self.client.get('/api/v1/flashcards/due/')
        self.assertEqual(response.status_code, 200)
```

### Frontend
```typescript
// Component testing với Vitest
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import FlashcardViewer from '@/components/FlashcardViewer.vue'

describe('FlashcardViewer', () => {
    it('flips card on click', async () => {
        const wrapper = mount(FlashcardViewer)
        await wrapper.find('.card').trigger('click')
        expect(wrapper.find('.back').isVisible()).toBe(true)
    })
})
```

---

## 📝 QUY TẮC GIT

### Branch Naming
```
main              # Production
develop           # Development
feature/xxx       # New features
bugfix/xxx        # Bug fixes
hotfix/xxx        # Emergency fixes

# Examples:
feature/flashcard-srs
feature/user-authentication
bugfix/lesson-progress-not-saving
```

### Commit Messages
```
# Format: <type>(<scope>): <description>

feat(flashcard): add SRS algorithm
fix(auth): correct JWT refresh logic
docs(api): update flashcard endpoints
style(ui): improve card flip animation
refactor(models): optimize query performance
test(api): add flashcard review tests
chore(deps): update Django to 5.0

# Types: feat, fix, docs, style, refactor, test, chore
```

---

## 🚀 DEPLOYMENT CHECKLIST

### Pre-deployment
- [ ] All tests passing
- [ ] No console.log/print statements
- [ ] Environment variables configured
- [ ] Database migrations ready
- [ ] Static files collected
- [ ] Security headers configured

### Environment Variables
```bash
# Django
DJANGO_SECRET_KEY=xxx
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=example.com

# Database
DATABASE_URL=postgres://user:pass@host:5432/db

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=xxx
JWT_ACCESS_TOKEN_LIFETIME=15
JWT_REFRESH_TOKEN_LIFETIME=10080

# Storage
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
AWS_STORAGE_BUCKET_NAME=xxx
```

---

## 📚 THAM KHẢO

### Official Docs
- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Vue.js 3](https://vuejs.org/)
- [Pinia](https://pinia.vuejs.org/)

### Project-specific
- `SYSTEM_ANALYSIS.md` - Phân tích hệ thống
- `Hướng dẫn/Dưới đây là thiết kế Schema.ini` - Schema gốc
- `DEVELOPMENT_STANDARDS.md` - Tiêu chuẩn UI/UX

---

*Cập nhật bởi: Development Team*  
*Ngày cập nhật: 08/12/2025*
