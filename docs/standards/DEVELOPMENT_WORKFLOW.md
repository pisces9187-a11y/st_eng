# QUY TRÌNH PHÁT TRIỂN PHẦN MỀM WEB - EnglishMaster
## Django + Bootstrap 5 + Vue.js Development Framework

---

## 📋 MỤC LỤC

1. [Quy trình 7 bước](#quy-trình-7-bước)
2. [Phase 1: Phân tích yêu cầu](#phase-1-phân-tích-yêu-cầu)
3. [Phase 2: Thiết kế kiến trúc](#phase-2-thiết-kế-kiến-trúc)
4. [Phase 3: Thiết kế giao diện](#phase-3-thiết-kế-giao-diện)
5. [Phase 4: Implementation](#phase-4-implementation)
6. [Phase 5: Testing](#phase-5-testing)
7. [Phase 6: Review & Validation](#phase-6-review--validation)
8. [Phase 7: Documentation](#phase-7-documentation)

---

## 🎯 QUY TRÌNH 7 BƯỚC

```
┌─────────────────────────────────────────────────────────────┐
│  1. PHÂN TÍCH YÊU CẦU (Requirements Analysis)              │
│     ↓ Làm rõ mọi chi tiết, xác nhận với user              │
├─────────────────────────────────────────────────────────────┤
│  2. THIẾT KẾ KIẾN TRÚC (Architecture Design)              │
│     ↓ Models, APIs, URLs, Views - CHECK TÁI SỬ DỤNG      │
├─────────────────────────────────────────────────────────────┤
│  3. THIẾT KẾ GIAO DIỆN (UI/UX Design)                     │
│     ↓ Wireframe, màu sắc, components - TUÂN THỦ CHUẨN    │
├─────────────────────────────────────────────────────────────┤
│  4. IMPLEMENTATION (Coding)                                │
│     ↓ Code theo design spec - ĐÚNG TÊN, ĐÚNG LOGIC        │
├─────────────────────────────────────────────────────────────┤
│  5. TESTING (Kiểm thử)                                     │
│     ↓ Unit tests, Integration tests - BẮT BUỘC           │
├─────────────────────────────────────────────────────────────┤
│  6. REVIEW & VALIDATION (Xem xét & Xác nhận)              │
│     ↓ Code review, User acceptance - CHECKLIST            │
├─────────────────────────────────────────────────────────────┤
│  7. DOCUMENTATION (Tài liệu hóa)                          │
│     ↓ API docs, User guide - CẬP NHẬT ĐỒNG BỘ           │
└─────────────────────────────────────────────────────────────┘
```

---

## PHASE 1: PHÂN TÍCH YÊU CẦU

### 📝 Template Nhận Yêu Cầu

```markdown
# YÊU CẦU TÍNH NĂNG: [Tên tính năng]

## 1. THÔNG TIN CƠ BẢN
- **Người yêu cầu:** [Tên]
- **Ngày yêu cầu:** [YYYY-MM-DD]
- **Độ ưu tiên:** [Cao/Trung bình/Thấp]
- **Sprint/Phase:** [Phase X - Day Y]

## 2. MÔ TẢ TỔNG QUAN
[Mô tả ngắn gọn tính năng cần phát triển]

## 3. USER STORIES
- **Là** [vai trò người dùng]
- **Tôi muốn** [hành động]
- **Để** [mục đích/lợi ích]

**Acceptance Criteria:**
- [ ] Tiêu chí 1
- [ ] Tiêu chí 2
- [ ] Tiêu chí 3

## 4. FUNCTIONAL REQUIREMENTS (Yêu cầu chức năng)
### 4.1. Chức năng chính
- [ ] **FR-1:** [Mô tả chức năng]
- [ ] **FR-2:** [Mô tả chức năng]

### 4.2. Business Logic
- **Rule-1:** [Quy tắc nghiệp vụ]
- **Rule-2:** [Quy tắc nghiệp vụ]

### 4.3. Data Requirements
- **Input:** [Dữ liệu đầu vào]
- **Output:** [Dữ liệu đầu ra]
- **Validation:** [Các điều kiện validation]

## 5. NON-FUNCTIONAL REQUIREMENTS
- **Performance:** [Yêu cầu về hiệu năng]
- **Security:** [Yêu cầu bảo mật]
- **Usability:** [Yêu cầu trải nghiệm người dùng]

## 6. CÂU HỎI LÀM RÕ (Developer → User)
### 6.1. Các câu hỏi cần xác nhận
1. **Q:** [Câu hỏi về logic nghiệp vụ]
   **A:** [Chờ user trả lời]

2. **Q:** [Câu hỏi về UI/UX]
   **A:** [Chờ user trả lời]

### 6.2. Edge Cases cần xử lý
- [ ] **Case 1:** [Tình huống đặc biệt]
- [ ] **Case 2:** [Tình huống lỗi]

## 7. ĐỀ XUẤT BỔ SUNG (Developer Suggestions)
### 7.1. Tính năng nên có thêm
- [ ] **Suggestion-1:** [Đề xuất] - *Lý do: [giải thích]*

### 7.2. Cải tiến UX
- [ ] **UX-1:** [Đề xuất cải thiện]

## 8. TÁI SỬ DỤNG CODE/COMPONENTS
### 8.1. Components có sẵn có thể dùng
- [ ] **Component:** [Tên] - *Đường dẫn: [path]*

### 8.2. Models/APIs có liên quan
- [ ] **Model:** [Tên model] - *Fields cần: [list]*
- [ ] **API:** [Endpoint] - *Response: [structure]*

## 9. DEPENDENCIES & CONSTRAINTS
- **Phụ thuộc vào:** [Tính năng/module khác]
- **Ràng buộc kỹ thuật:** [Giới hạn]
- **External APIs:** [API bên ngoài nếu có]

## 10. TIMELINE ESTIMATE
- **Phân tích & Design:** [X hours]
- **Implementation:** [Y hours]
- **Testing:** [Z hours]
- **Total:** [Total hours]

---
## ✅ SIGN-OFF
- [ ] **Developer hiểu rõ yêu cầu:** [Tên/Ngày]
- [ ] **User xác nhận requirements:** [Tên/Ngày]
- [ ] **Ready to design:** [Ngày]
```

---

## PHASE 2: THIẾT KẾ KIẾN TRÚC

### 🏗️ Architecture Design Checklist

```markdown
# THIẾT KẾ KIẾN TRÚC: [Tên tính năng]

## 1. DATABASE DESIGN

### 1.1. Models Analysis
**BƯỚC 1: Kiểm tra models hiện có**
```python
# File: backend/apps/[app_name]/models.py
# Các models đã có liên quan:
- Model A: [Tên model] - Fields: [list fields]
- Model B: [Tên model] - Relationships: [ForeignKey, etc]
```

**BƯỚC 2: Xác định models cần tạo mới/sửa đổi**
- [ ] **Tạo mới Model:** `[ModelName]`
- [ ] **Thêm fields vào Model:** `[ExistingModel]`
- [ ] **Tạo relationship:** `[Model A] → [Model B]`

### 1.2. Model Design Specification

#### Model: [ModelName]
```python
class [ModelName](models.Model):
    """
    [Mô tả model]
    
    Purpose: [Mục đích sử dụng]
    Related to: [Các model liên quan]
    """
    
    # Fields
    field_name = models.[FieldType](
        [parameters],
        verbose_name='[Tên hiển thị]',
        help_text='[Mô tả]'
    )
    
    # Relationships
    related_model = models.ForeignKey(
        '[RelatedModel]',
        on_delete=models.[CASCADE/SET_NULL/etc],
        related_name='[reverse_name]'
    )
    
    # Meta
    class Meta:
        db_table = '[table_name]'
        ordering = ['-created_at']
        verbose_name = '[Tên số ít]'
        verbose_name_plural = '[Tên số nhiều]'
        indexes = [
            models.Index(fields=['field1', 'field2'])
        ]
    
    # Methods
    def __str__(self):
        return f"[representation]"
    
    def get_absolute_url(self):
        return reverse('[url_name]', kwargs={'pk': self.pk})
```

**⚠️ VALIDATION CHECKLIST:**
- [ ] Tên field chính xác, không xung đột với Python reserved words
- [ ] Verbose_name đầy đủ cho admin
- [ ] Help_text giải thích rõ ràng
- [ ] Indexes cho các field hay query
- [ ] Related_name không trùng lặp
- [ ] On_delete phù hợp với business logic

---

## 2. API DESIGN

### 2.1. API Endpoints Planning

#### Endpoint: [API Name]
```
Method: GET/POST/PUT/DELETE
URL: /api/v1/[resource]/[action]/
Authentication: Required/Optional/None
Permissions: [Permission classes]
```

**Request:**
```json
{
    "field1": "value",
    "field2": 123,
    "nested": {
        "sub_field": "value"
    }
}
```

**Response (Success - 200/201):**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "field1": "value",
        "created_at": "2025-12-16T10:00:00Z"
    },
    "message": "Success message"
}
```

**Response (Error - 400/404/500):**
```json
{
    "success": false,
    "error": "Error message",
    "details": {
        "field": ["Error detail"]
    }
}
```

**⚠️ API NAMING CONVENTION:**
```
✅ ĐÚNG:
GET    /api/v1/pronunciation/phonemes/           # List
GET    /api/v1/pronunciation/phonemes/{id}/      # Detail
POST   /api/v1/pronunciation/phonemes/           # Create
PUT    /api/v1/pronunciation/phonemes/{id}/      # Update
DELETE /api/v1/pronunciation/phonemes/{id}/      # Delete
POST   /api/v1/pronunciation/phonemes/{id}/progress/  # Custom action

❌ SAI:
/api/v1/getPhonemesData/                         # Không dùng camelCase
/api/v1/phoneme-list/                            # Không dùng hyphens
/api/pronunciation/save/                         # Thiếu version
```

### 2.2. Serializer Design

```python
# File: backend/apps/[app]/serializers.py

class [ModelName]Serializer(serializers.ModelSerializer):
    """
    Serializer for [ModelName]
    
    Used in: [List APIs sử dụng]
    Fields: [Explain special fields]
    """
    
    # Custom fields
    custom_field = serializers.SerializerMethodField()
    related_data = [RelatedSerializer](read_only=True)
    
    class Meta:
        model = [ModelName]
        fields = [
            'id',
            'field1',
            'field2',
            'custom_field',
            'related_data',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_custom_field(self, obj):
        """Calculate custom field value"""
        return [logic]
    
    def validate_field1(self, value):
        """Validate specific field"""
        if [condition]:
            raise serializers.ValidationError("[Error message]")
        return value
```

---

## 3. URL ROUTING DESIGN

### 3.1. URL Structure

```python
# File: backend/apps/[app]/urls.py

urlpatterns = [
    # Page Views (Server-side rendered)
    path('feature/list/', views.feature_list_view, name='feature_list'),
    path('feature/<int:pk>/', views.feature_detail_view, name='feature_detail'),
    path('feature/<int:pk>/edit/', views.feature_edit_view, name='feature_edit'),
    
    # API Endpoints
    path('api/v1/features/', api_views.FeatureListCreateAPIView.as_view(), name='api_feature_list'),
    path('api/v1/features/<int:pk>/', api_views.FeatureDetailAPIView.as_view(), name='api_feature_detail'),
]
```

**⚠️ URL NAMING CONVENTION:**
- Template views: `[feature]_[action]` (e.g., `lesson_detail`, `phoneme_practice`)
- API endpoints: `api_[resource]_[action]` (e.g., `api_phoneme_list`)
- Dùng underscores, không dùng hyphens trong names
- URL paths dùng hyphens: `/pronunciation-practice/`

---

## 4. VIEW LAYER DESIGN

### 4.1. Template View Specification

```python
# File: backend/apps/[app]/views_[module].py

@login_required  # Decorator phù hợp
@require_http_methods(["GET"])  # Methods cho phép
def [feature]_view(request, [params]):
    """
    Render [feature] page.
    
    URL: /[path]/
    Template: pages/[template_name].html
    
    Context Data:
    - key1: [description]
    - key2: [description]
    
    Permissions: [Login required/Staff only/etc]
    """
    
    # 1. Get data from database
    try:
        obj = Model.objects.get(pk=[param])
    except Model.DoesNotExist:
        return render(request, 'errors/404.html', status=404)
    
    # 2. Prepare context data
    context = {
        'object': obj,
        'object_json': json.dumps({
            'id': obj.id,
            'field': obj.field,  # ⚠️ ĐÚNG TÊN FIELD
        }),
        'page_title': '[Page Title]',
        'meta_description': '[SEO description]',
    }
    
    # 3. Render template
    return render(request, 'pages/[template_name].html', context)
```

### 4.2. API View Specification

```python
# File: backend/apps/[app]/api/[module]_api.py

class [Feature]ListCreateAPIView(generics.ListCreateAPIView):
    """
    API for listing and creating [resource].
    
    GET: List all [resources] with filters
    POST: Create new [resource]
    
    Permissions: [IsAuthenticated/IsAdminUser/etc]
    Filters: [field1, field2]
    """
    
    queryset = Model.objects.all()
    serializer_class = [ModelSerializer]
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['field1', 'field2']
    ordering_fields = ['created_at', 'updated_at']
    
    def get_queryset(self):
        """Custom queryset with user-specific filtering"""
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        return queryset
    
    def perform_create(self, serializer):
        """Custom creation logic"""
        serializer.save(user=self.request.user)
```

---

## PHASE 3: THIẾT KẾ GIAO DIỆN

### 🎨 UI/UX Design Standards

#### 1. COLOR PALETTE (Tuân thủ nghiêm ngặt)

```css
/* File: backend/static/css/base.css */

:root {
    /* Primary Colors */
    --primary-color: #667eea;        /* Main brand color */
    --primary-dark: #5568d3;
    --primary-light: #8196f3;
    
    /* Secondary Colors */
    --secondary-color: #764ba2;
    --accent-color: #f093fb;
    
    /* Semantic Colors */
    --success-color: #10b981;
    --warning-color: #f59e0b;
    --error-color: #ef4444;
    --info-color: #3b82f6;
    
    /* Neutral Colors */
    --text-primary: #1f2937;
    --text-secondary: #6b7280;
    --text-muted: #9ca3af;
    --bg-primary: #ffffff;
    --bg-secondary: #f9fafb;
    --bg-tertiary: #f3f4f6;
    --border-color: #e5e7eb;
}
```

#### 2. TYPOGRAPHY

```css
/* Fonts */
--font-primary: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
--font-heading: 'Poppins', sans-serif;
--font-mono: 'Fira Code', monospace;

/* Font Sizes */
--fs-xs: 0.75rem;    /* 12px */
--fs-sm: 0.875rem;   /* 14px */
--fs-base: 1rem;     /* 16px */
--fs-lg: 1.125rem;   /* 18px */
--fs-xl: 1.25rem;    /* 20px */
--fs-2xl: 1.5rem;    /* 24px */
--fs-3xl: 1.875rem;  /* 30px */
--fs-4xl: 2.25rem;   /* 36px */

/* Font Weights */
--fw-normal: 400;
--fw-medium: 500;
--fw-semibold: 600;
--fw-bold: 700;
```

#### 3. SPACING SYSTEM

```css
/* Spacing Scale (8px base) */
--space-1: 0.25rem;  /* 4px */
--space-2: 0.5rem;   /* 8px */
--space-3: 0.75rem;  /* 12px */
--space-4: 1rem;     /* 16px */
--space-5: 1.5rem;   /* 24px */
--space-6: 2rem;     /* 32px */
--space-8: 3rem;     /* 48px */
--space-10: 4rem;    /* 64px */
```

#### 4. COMPONENT LIBRARY

##### 4.1. Button Styles
```html
<!-- Primary Button -->
<button class="btn btn-primary">
    <i class="bi bi-check"></i> Primary Action
</button>

<!-- Secondary Button -->
<button class="btn btn-outline-primary">
    Secondary Action
</button>

<!-- Icon Button -->
<button class="btn btn-icon">
    <i class="bi bi-heart"></i>
</button>
```

##### 4.2. Card Component
```html
<div class="card shadow-sm">
    <div class="card-header">
        <h5 class="card-title mb-0">Card Title</h5>
    </div>
    <div class="card-body">
        Content here
    </div>
    <div class="card-footer">
        <button class="btn btn-primary">Action</button>
    </div>
</div>
```

##### 4.3. Form Styles
```html
<div class="form-group mb-3">
    <label for="input" class="form-label">Label</label>
    <input type="text" 
           id="input" 
           class="form-control" 
           placeholder="Placeholder">
    <small class="form-text text-muted">Help text</small>
</div>
```

---

### 📐 Template Structure

```html
{% extends "base/_base.html" %}
{% load static %}

{% block title %}{{ page_title }}{% endblock %}

{% block extra_head %}
<style>
/* Component-specific styles */
.feature-container {
    /* Styles here */
}
</style>
{% endblock %}

{% block content %}
<div id="[feature]App" v-cloak>
    <!-- Hero Section (nếu có) -->
    <div class="hero-section">
        <div class="container">
            <h1>[Page Title]</h1>
        </div>
    </div>
    
    <!-- Main Content -->
    <div class="container py-4">
        <!-- Content here -->
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
const { createApp } = Vue;

createApp({
    delimiters: ['[[', ']]'],  // ⚠️ BẮT BUỘC dùng [[ ]] để tránh conflict với Django
    data() {
        return {
            // Data properties
        }
    },
    computed: {
        // Computed properties
    },
    methods: {
        // Methods
    },
    async mounted() {
        // Wait for Auth ready
        await Auth.waitUntilReady();
        
        // Check authentication if needed
        if (Auth.isAuthenticated()) {
            await this.loadData();
        }
    }
}).mount('#[feature]App');
</script>
{% endblock %}
```

---

## PHASE 4: IMPLEMENTATION

### 💻 Coding Standards

#### 1. IMPLEMENTATION CHECKLIST

```markdown
## PRE-CODING CHECKLIST
- [ ] Đã có design document đầy đủ
- [ ] Đã xác nhận với user về requirements
- [ ] Đã review kiến trúc hiện có (tái sử dụng code)
- [ ] Đã check model fields chính xác
- [ ] Đã thiết kế API contract đầy đủ

## CODING ORDER (Tuân thủ thứ tự)
1. [ ] **Models** - Tạo/sửa models trước
2. [ ] **Migrations** - Run makemigrations & migrate
3. [ ] **Admin** - Register models trong admin
4. [ ] **Serializers** - Tạo serializers cho APIs
5. [ ] **API Views** - Implement API endpoints
6. [ ] **URLs (API)** - Register API URLs
7. [ ] **Template Views** - Implement page views
8. [ ] **URLs (Pages)** - Register page URLs
9. [ ] **Templates** - Tạo HTML templates
10. [ ] **Frontend JS** - Implement Vue.js logic
11. [ ] **CSS** - Style components
12. [ ] **Tests** - Write unit tests

## POST-CODING CHECKLIST
- [ ] Code đã format chuẩn (PEP 8 for Python)
- [ ] Không có hardcoded values
- [ ] Error handling đầy đủ
- [ ] Logging phù hợp
- [ ] Comments cho code phức tạp
```

#### 2. MODEL IMPLEMENTATION

```python
# ⚠️ TRƯỚC KHI CODE - XÁC NHẬN:
# 1. Check model đã tồn tại chưa: grep -r "class ModelName"
# 2. Check field names chính xác theo design doc
# 3. Check relationships với các models khác

class [ModelName](models.Model):
    """
    [Docstring mô tả đầy đủ]
    """
    
    # Fields (theo thứ tự logic)
    # 1. Core fields
    # 2. Foreign keys
    # 3. Additional fields
    # 4. Metadata fields (created_at, updated_at)
    
    field_name = models.CharField(
        max_length=200,
        verbose_name='Tên hiển thị',
        help_text='Mô tả cho admin',
        db_index=True,  # Nếu hay query
    )
    
    # ⚠️ NAMING CONVENTION:
    # ✅ ĐÚNG: audio_sample, mouth_diagram, pronunciation_tips
    # ❌ SAI: audio_url, mouthDiagram, pronounciationTip
    
    class Meta:
        db_table = '[app]_[model_name]'
        verbose_name = '[Tên tiếng Việt]'
        verbose_name_plural = '[Tên số nhiều]'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.field1} - {self.field2}"
```

#### 3. API IMPLEMENTATION

```python
# File: backend/apps/[app]/api/[module]_api.py

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q

class [Feature]APIView(generics.GenericAPIView):
    """
    API documentation
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = [Serializer]
    
    def get(self, request, *args, **kwargs):
        """
        GET method documentation
        """
        try:
            # 1. Get query parameters
            param = request.query_params.get('param', None)
            
            # 2. Query database
            queryset = Model.objects.filter(user=request.user)
            
            # 3. Serialize data
            serializer = self.serializer_class(queryset, many=True)
            
            # 4. Return response
            return Response({
                'success': True,
                'data': serializer.data,
                'count': queryset.count()
            })
            
        except Exception as e:
            # ⚠️ ERROR HANDLING BẮT BUỘC
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
```

#### 4. VIEW IMPLEMENTATION

```python
# File: backend/apps/[app]/views_[module].py

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
import json

@login_required
@require_http_methods(["GET"])
def [feature]_view(request, param):
    """
    View documentation
    """
    
    # 1. Get object (with error handling)
    obj = get_object_or_404(Model, pk=param, is_active=True)
    
    # 2. Prepare data
    # ⚠️ XÁC NHẬN TÊN FIELDS CHÍNH XÁC
    obj_data = {
        'id': obj.id,
        'field1': obj.field1,  # ✅ Check model có field này
        'field2': obj.field2,  # ✅ Không gõ nhầm tên
    }
    
    # 3. Context
    context = {
        'object': obj,
        'object_json': json.dumps(obj_data),  # For Vue.js
        'page_title': f'[Title] - {obj.name}',
        'meta_description': '[SEO description]',
    }
    
    # 4. Render
    # ⚠️ KIỂM TRA TEMPLATE TỒN TẠI
    return render(request, 'pages/[template_name].html', context)
```

#### 5. TEMPLATE IMPLEMENTATION

```html
<!-- File: backend/templates/pages/[feature].html -->

{% extends "base/_base.html" %}
{% load static %}

{% block title %}{{ page_title }}{% endblock %}

{% block extra_head %}
<!-- Component CSS -->
<style>
/* Scoped styles */
</style>
{% endblock %}

{% block content %}
<div id="[feature]App" v-cloak>
    <!-- ⚠️ SỬ DỤNG [[ ]] CHO VUE.JS -->
    <h1>[[ title ]]</h1>
    
    <!-- ⚠️ CHECK TÊN PROPERTIES CHÍNH XÁC -->
    <div v-for="item in items" :key="item.id">
        <h3>[[ item.name ]]</h3>
        <!-- ⚠️ Đảm bảo object có property này -->
        <p>[[ item.description ]]</p>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
const { createApp } = Vue;

createApp({
    delimiters: ['[[', ']]'],
    data() {
        return {
            // ⚠️ PARSE JSON AN TOÀN
            object: {{ object_json|safe }},
            items: [],
            loading: false,
            error: null
        }
    },
    methods: {
        async loadData() {
            try {
                this.loading = true;
                
                // ⚠️ CHECK ENDPOINT ĐÚNG
                const response = await ApiClient.get('/api/v1/[resource]/');
                
                // ⚠️ CHECK RESPONSE STRUCTURE
                if (response.success) {
                    this.items = response.data;
                }
                
            } catch (error) {
                console.error('Error:', error);
                this.error = error.message;
            } finally {
                this.loading = false;
            }
        }
    },
    async mounted() {
        await Auth.waitUntilReady();
        await this.loadData();
    }
}).mount('#[feature]App');
</script>
{% endblock %}
```

---

## PHASE 5: TESTING

### 🧪 Testing Standards

#### 1. TESTING CHECKLIST

```markdown
## UNIT TESTS (BẮT BUỘC)
- [ ] Model tests (creation, validation, methods)
- [ ] Serializer tests (validation, representation)
- [ ] API tests (endpoints, permissions, responses)
- [ ] View tests (rendering, context data)
- [ ] Form tests (validation, submission)

## INTEGRATION TESTS
- [ ] Full workflow tests (user journey)
- [ ] API integration tests
- [ ] Database transaction tests

## MANUAL TESTS
- [ ] UI rendering on Chrome, Firefox, Safari
- [ ] Mobile responsiveness
- [ ] Error handling (404, 500, permissions)
- [ ] Performance (page load time < 2s)
```

#### 2. MODEL TESTS

```python
# File: backend/apps/[app]/tests/test_models.py

from django.test import TestCase
from apps.[app].models import [ModelName]

class [ModelName]TestCase(TestCase):
    """Test [ModelName] model"""
    
    def setUp(self):
        """Set up test data"""
        self.[instance] = [ModelName].objects.create(
            field1='value1',
            field2='value2'
        )
    
    def test_model_creation(self):
        """Test model can be created"""
        self.assertEqual(self.[instance].field1, 'value1')
        self.assertTrue(isinstance(self.[instance], [ModelName]))
    
    def test_str_representation(self):
        """Test __str__ method"""
        expected = f"[expected string]"
        self.assertEqual(str(self.[instance]), expected)
    
    def test_field_validation(self):
        """Test field validation"""
        # Test invalid data
        with self.assertRaises(ValidationError):
            invalid = [ModelName](field1='')
            invalid.full_clean()
```

#### 3. API TESTS

```python
# File: backend/apps/[app]/tests/test_api.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

class [Feature]APITestCase(TestCase):
    """Test [Feature] API endpoints"""
    
    def setUp(self):
        """Set up test client and data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_list_endpoint(self):
        """Test GET /api/v1/[resource]/"""
        response = self.client.get('/api/v1/[resource]/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
    
    def test_create_endpoint(self):
        """Test POST /api/v1/[resource]/"""
        data = {
            'field1': 'value1',
            'field2': 'value2'
        }
        
        response = self.client.post('/api/v1/[resource]/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
    
    def test_authentication_required(self):
        """Test authentication is required"""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/v1/[resource]/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
```

#### 4. VIEW TESTS

```python
# File: backend/apps/[app]/tests/test_views.py

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class [Feature]ViewTestCase(TestCase):
    """Test [Feature] views"""
    
    def setUp(self):
        """Set up test client"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_login(self.user)
    
    def test_page_renders(self):
        """Test page renders successfully"""
        url = reverse('[view_name]')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/[template].html')
    
    def test_context_data(self):
        """Test context contains required data"""
        url = reverse('[view_name]')
        response = self.client.get(url)
        
        self.assertIn('[key]', response.context)
        self.assertIsNotNone(response.context['[key]'])
    
    def test_login_required(self):
        """Test login is required"""
        self.client.logout()
        url = reverse('[view_name]')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)  # Redirect to login
```

#### 5. INTEGRATION TESTS

```python
# File: backend/tests/test_[feature]_integration.py

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from apps.[app].models import [Model]

User = get_user_model()

class [Feature]IntegrationTestCase(TestCase):
    """Integration tests for [feature] workflow"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_login(self.user)
    
    def test_complete_workflow(self):
        """Test complete user workflow"""
        
        # Step 1: User accesses feature page
        response = self.client.get('/[path]/')
        self.assertEqual(response.status_code, 200)
        
        # Step 2: User submits data via API
        data = {'field': 'value'}
        response = self.client.post('/api/v1/[endpoint]/', data)
        self.assertEqual(response.status_code, 201)
        
        # Step 3: Data is saved correctly
        obj = [Model].objects.get(user=self.user)
        self.assertEqual(obj.field, 'value')
        
        # Step 4: User can retrieve data
        response = self.client.get('/api/v1/[endpoint]/')
        self.assertEqual(len(response.data['data']), 1)
```

---

## PHASE 6: REVIEW & VALIDATION

### ✅ Pre-Release Checklist

```markdown
# VALIDATION CHECKLIST - [Feature Name]

## 1. CODE QUALITY
- [ ] Code follows PEP 8 (Python) and ESLint (JavaScript)
- [ ] No hardcoded values (use settings/constants)
- [ ] No commented-out code
- [ ] Meaningful variable/function names
- [ ] Proper error handling everywhere
- [ ] Logging added for important operations

## 2. FUNCTIONALITY
- [ ] All acceptance criteria met
- [ ] Edge cases handled
- [ ] Error messages user-friendly
- [ ] Form validation working
- [ ] API responses correct structure

## 3. DATABASE
- [ ] Migrations created and applied
- [ ] No missing fields
- [ ] Field names match design spec
- [ ] Indexes added for performance
- [ ] Data integrity constraints working

## 4. API
- [ ] Endpoints follow naming convention
- [ ] Request/response structure documented
- [ ] Authentication working
- [ ] Permissions correct
- [ ] Error codes appropriate (400, 404, 500)

## 5. FRONTEND
- [ ] Templates exist (no TemplateDoesNotExist)
- [ ] Vue.js data binding working
- [ ] API calls use correct endpoints
- [ ] Field names match backend (no AttributeError)
- [ ] Loading states implemented
- [ ] Error states handled

## 6. UI/UX
- [ ] Follows design system (colors, fonts)
- [ ] Responsive on mobile/tablet/desktop
- [ ] Accessible (keyboard navigation, ARIA labels)
- [ ] Loading indicators present
- [ ] Success/error messages shown

## 7. TESTING
- [ ] Unit tests written and passing
- [ ] Integration tests passing
- [ ] Manual testing completed
- [ ] Cross-browser tested
- [ ] Performance acceptable

## 8. SECURITY
- [ ] Authentication required where needed
- [ ] Authorization checks implemented
- [ ] CSRF protection enabled
- [ ] SQL injection prevented (use ORM)
- [ ] XSS prevented (template escaping)

## 9. DOCUMENTATION
- [ ] Code comments for complex logic
- [ ] API documentation updated
- [ ] README updated if needed
- [ ] Migration notes documented

## 10. DEPLOYMENT
- [ ] Environment variables configured
- [ ] Static files collected
- [ ] Database backed up
- [ ] Rollback plan ready
```

---

## PHASE 7: DOCUMENTATION

### 📚 Documentation Standards

#### 1. FEATURE DOCUMENTATION

```markdown
# [FEATURE NAME] - Implementation Documentation

## Overview
[Brief description of what was built]

## Architecture
### Models
- **[ModelName]** (`apps.[app].models.[ModelName]`)
  - Purpose: [What it stores]
  - Key fields: `field1`, `field2`, `field3`
  - Relationships: ForeignKey to `[OtherModel]`

### APIs
1. **List/Create API**
   - Endpoint: `GET/POST /api/v1/[resource]/`
   - View: `[app].api.[module]_api.[ViewClass]`
   - Serializer: `[Serializer]`

### Pages
1. **[Page Name]**
   - URL: `/[path]/`
   - View: `[app].views_[module].[view_function]`
   - Template: `pages/[template].html`

## Database Changes
### Migrations
- `[XXXX]_[migration_name].py` - [Description]

### New Fields
- `[Model].[field_name]` - [Purpose and type]

## API Endpoints
### GET /api/v1/[resource]/
**Request:** None
**Response:**
```json
{
    "success": true,
    "data": [...]
}
```

## Frontend Components
### Vue.js App: `[feature]App`
- **Data:** `items`, `loading`, `error`
- **Methods:** `loadData()`, `submitForm()`
- **API Calls:** Uses `ApiClient.get()`, `ApiClient.post()`

## Testing
- Unit tests: `apps.[app].tests.test_[module].py`
- Coverage: [X%]

## Known Issues
- [Issue 1 and workaround]

## Future Enhancements
- [Enhancement 1]
```

---

## 🚨 COMMON PITFALLS & HOW TO AVOID

### 1. AttributeError: 'Object' has no attribute 'field_name'

**❌ Problem:**
```python
# views.py
'audio_url': phoneme.audio_url  # Field doesn't exist!
```

**✅ Solution:**
```python
# ALWAYS CHECK MODEL FIRST
# 1. Read model file: apps/curriculum/models.py
# 2. Find class Phoneme
# 3. List all fields
# 4. Use EXACT field name

'audio_sample': phoneme.audio_sample.url if phoneme.audio_sample else None
```

**Prevention:**
- [ ] Before coding, grep model file
- [ ] Copy-paste field names from model
- [ ] Use IDE autocomplete

---

### 2. TemplateDoesNotExist

**❌ Problem:**
```python
return render(request, 'pronunciation_discrimination.html')  # Wrong path!
```

**✅ Solution:**
```python
# ALWAYS use 'pages/' prefix
return render(request, 'pages/pronunciation_discrimination.html')

# Before coding, create template file first
# File structure: backend/templates/pages/[name].html
```

**Prevention:**
- [ ] Create template file BEFORE view
- [ ] Use consistent naming: `[feature]_[action].html`
- [ ] Test template exists: `os.path.exists(template_path)`

---

### 3. API Response Structure Mismatch

**❌ Problem:**
```javascript
// Frontend expects flat array
this.phonemes = response;  // But API returns {success, categories: [...]}
```

**✅ Solution:**
```javascript
// ALWAYS check API response structure first
// Test: curl http://localhost:8000/api/v1/pronunciation/phonemes/

const response = await ApiClient.get('/pronunciation/phonemes/');
if (response.categories) {
    // Flatten nested structure
    this.phonemes = response.categories.flatMap(cat => cat.phonemes);
}
```

**Prevention:**
- [ ] Document API response structure in design
- [ ] Test API with curl/Postman first
- [ ] Add response validation in frontend

---

### 4. Field Name Inconsistency

**❌ Problem:**
```python
# Model
discrimination_accuracy = models.FloatField()

# View (WRONG!)
'discrimination_score': progress.discrimination_score  # Different name!
```

**✅ Solution:**
```python
# Use EXACT field name from model
'discrimination_accuracy': progress.discrimination_accuracy
```

**Prevention:**
- [ ] Create field name constants
- [ ] Use model serializers (auto field names)
- [ ] Add field name validation tests

---

## 📋 PROJECT-SPECIFIC CONVENTIONS

### Django Apps Structure
```
backend/
├── apps/
│   ├── curriculum/         # Course, Lesson, Phoneme models
│   ├── users/              # User, Profile, Progress models
│   └── study/              # Study session, Analytics models
```

### URL Patterns
```python
# Page URLs: /[feature]/[action]/[id]/
/pronunciation/discovery/
/pronunciation/learning/45/
/pronunciation/dashboard/

# API URLs: /api/v1/[resource]/[action]/
/api/v1/pronunciation/phonemes/
/api/v1/pronunciation/progress/
```

### Template Structure
```
templates/
├── base/
│   └── _base.html          # Base template
├── pages/                  # Feature pages
│   ├── pronunciation_discovery.html
│   ├── pronunciation_learning.html
│   └── ...
├── components/             # Reusable components
│   └── ...
└── errors/                 # Error pages
    ├── 404.html
    └── 500.html
```

### Static Files
```
static/
├── css/
│   ├── base.css           # Global styles
│   └── components.css     # Component styles
├── js/
│   ├── config.js          # Configuration
│   ├── api.js             # API client
│   ├── auth.js            # Authentication
│   └── utils.js           # Utilities
└── images/
```

---

## 🎓 WORKFLOW EXAMPLE: Adding New Feature

### Example: "Thêm tính năng Quiz Practice"

#### Phase 1: Requirements (30 phút)
```markdown
1. User story: Là học viên, tôi muốn làm quiz để kiểm tra kiến thức
2. Clarifying questions:
   - Q: Quiz có giới hạn thời gian không?
   - Q: Có cho xem đáp án sau khi hoàn thành không?
   - Q: Lưu điểm vào database hay chỉ hiển thị?
3. Suggestions:
   - Thêm leaderboard để tăng tính cạnh tranh
   - Thêm badges khi đạt milestone
```

#### Phase 2: Architecture (1 giờ)
```python
# Models needed:
- Quiz (title, description, difficulty)
- QuizQuestion (quiz FK, question_text, correct_answer)
- QuizAttempt (user FK, quiz FK, score, completed_at)

# APIs needed:
GET  /api/v1/quiz/list/
GET  /api/v1/quiz/{id}/questions/
POST /api/v1/quiz/{id}/submit/

# Pages needed:
/quiz/list/          → List all quizzes
/quiz/{id}/practice/ → Practice interface
/quiz/results/{id}/  → Results page
```

#### Phase 3: UI Design (1 giờ)
```
[Wireframe]
[Color scheme: Use existing primary colors]
[Components: Reuse button, card from library]
```

#### Phase 4: Implementation (4 giờ)
```
1. Models → 30 min
2. Migrations → 10 min
3. Serializers → 20 min
4. APIs → 1 hour
5. Views → 30 min
6. Templates → 1.5 hours
7. CSS → 30 min
```

#### Phase 5: Testing (1 giờ)
```
1. Model tests → 20 min
2. API tests → 20 min
3. View tests → 20 min
```

#### Phase 6: Review (30 phút)
```
Run checklist, manual testing
```

#### Phase 7: Documentation (30 phút)
```
Update API docs, write feature doc
```

**Total: ~8 hours** (1 working day)

---

## 🎯 SUCCESS METRICS

### Code Quality Metrics
- **Test Coverage:** > 80%
- **Code Duplication:** < 5%
- **Cyclomatic Complexity:** < 10 per function
- **Documentation:** All public APIs documented

### Performance Metrics
- **Page Load Time:** < 2 seconds
- **API Response Time:** < 200ms
- **Database Queries:** < 10 per page

### User Experience Metrics
- **Error Rate:** < 1%
- **User Satisfaction:** > 4/5 stars
- **Feature Adoption:** > 50% within 1 week

---

## 📞 ESCALATION PROCESS

### When to Ask User for Clarification
1. ❓ Requirements unclear or ambiguous
2. 🔀 Multiple implementation approaches possible
3. 🎨 UI/UX decisions needed
4. 💰 Feature requires additional resources/time
5. 🔒 Security/privacy implications

### When to Suggest Improvements
1. 💡 Better user experience possible
2. ⚡ Performance optimization opportunity
3. 🔧 Technical debt can be reduced
4. 🎁 Easy wins for user delight

---

## ✅ FINAL CHECKLIST BEFORE USER HANDOFF

```markdown
## DEPLOYMENT READINESS
- [ ] All tests passing (unit + integration)
- [ ] No console errors in browser
- [ ] No Django errors in logs
- [ ] Database migrations applied
- [ ] Static files collected
- [ ] Environment variables set

## DOCUMENTATION
- [ ] Feature documentation complete
- [ ] API documentation updated
- [ ] User guide created (if needed)
- [ ] Known issues documented

## USER ACCEPTANCE
- [ ] All acceptance criteria met
- [ ] Edge cases handled
- [ ] Error messages clear
- [ ] Performance acceptable
- [ ] Security reviewed

## HANDOFF
- [ ] Demo prepared
- [ ] User training scheduled (if needed)
- [ ] Support plan ready
- [ ] Rollback plan documented
```

---

## 📚 REFERENCES

### Internal Documentation
- `/SYSTEM_ANALYSIS.md` - Project architecture
- `/TEMPLATE_ARCHITECTURE.md` - Template structure
- `/API_GUIDELINES.md` - API conventions
- `/DJANGO_DEVELOPMENT_GUIDE.md` - Django best practices

### External Resources
- [Django Best Practices](https://docs.djangoproject.com/)
- [Vue.js 3 Guide](https://vuejs.org/guide/)
- [Bootstrap 5 Docs](https://getbootstrap.com/)
- [REST API Design](https://restfulapi.net/)

---

**Version:** 1.0.0  
**Last Updated:** 2025-12-16  
**Maintained by:** Development Team
