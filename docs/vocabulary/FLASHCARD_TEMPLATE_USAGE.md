# 📝 Flashcard Template Usage Guide

## 🎯 Mục đích

File `public/flashcard.html` là **template thiết kế gốc** (design reference) cho tính năng flashcard, được tạo trong giai đoạn mockup. Tuy nhiên, trong kiến trúc Django hiện tại, chúng ta **KHÔNG trực tiếp sử dụng** file này.

## 📂 Cấu trúc Template Hiện tại

### ✅ Template ĐÚNG (Django-integrated):
```
backend/templates/vocabulary/
├── flashcard_study.html    ← Template chính (extends base/_base_public.html)
├── deck_list.html           ← Danh sách bộ thẻ
└── dashboard.html           ← Dashboard từ vựng
```

### 📄 Template Tham khảo (Static mockup):
```
public/
└── flashcard.html           ← Design reference ONLY (không dùng trực tiếp)
```

## 🔄 Quy trình chuyển đổi đã thực hiện

### Bước 1: Phân tích design từ public/flashcard.html
```html
<!-- public/flashcard.html - DESIGN REFERENCE -->
<div class="flashcard-container">
    <div class="flashcard-inner">
        <!-- Front side -->
        <div class="flashcard-front">
            <h1>{{ word }}</h1>
        </div>
        <!-- Back side -->
        <div class="flashcard-back">
            <h3>{{ meaning }}</h3>
        </div>
    </div>
</div>
```

### Bước 2: Chuyển thành Django template với Vue.js
```django-html
<!-- backend/templates/vocabulary/flashcard_study.html - PRODUCTION -->
{% extends "base/_base_public.html" %}

<div id="app">
    <div class="flashcard-container" @click="flipCard">
        <div class="flashcard-inner" :class="{ 'is-flipped': isFlipped }">
            <!-- Front side -->
            <div class="flashcard-front">
                <h1>[[ currentCard.word ]]</h1>
            </div>
            <!-- Back side -->
            <div class="flashcard-back">
                <h3>[[ currentCard.meaning ]]</h3>
            </div>
        </div>
    </div>
</div>

<script>
createApp({
    delimiters: ['[[', ']]'],
    data() {
        return {
            isFlipped: false,
            currentCard: {}
        }
    },
    methods: {
        async loadCard() {
            const response = await fetch('/api/v1/vocabulary/flashcards/...');
            this.currentCard = await response.json();
        }
    }
}).mount('#app');
</script>
```

### Bước 3: Tích hợp Backend API
- `backend/apps/vocabulary/api/vocabulary_api.py` - ViewSets cho flashcards
- `backend/apps/vocabulary/views.py` - Template views với JWT auth
- `backend/apps/vocabulary/models.py` - Flashcard, Word, LearningProgress models

## ✅ Lý do KHÔNG dùng trực tiếp public/flashcard.html

### ❌ Vấn đề nếu dùng trực tiếp:

1. **Không có Django template engine**
   - Không thể dùng `{% url %}`, `{% static %}`
   - Không kế thừa base templates
   - Không có CSRF protection

2. **Không có authentication**
   - Public file không check JWT/session
   - Bất kỳ ai cũng truy cập được
   - Không track user progress

3. **Không kết nối database**
   - Dữ liệu hardcoded (static)
   - Không lưu learning progress
   - Không có SM-2 algorithm

4. **Không responsive với API changes**
   - Nếu API thay đổi, phải sửa 2 nơi
   - Dễ bị lỗi đồng bộ

### ✅ Ưu điểm khi dùng Django template:

1. **Template inheritance**
   ```django-html
   {% extends "base/_base_public.html" %}
   ```
   - Navbar, footer tự động
   - Authentication middleware
   - Consistent styling

2. **JWT Authentication**
   ```python
   @jwt_required
   def flashcard_study_view(request, deck_id=None):
       # Chỉ user đã login mới vào được
   ```

3. **Real-time API integration**
   ```javascript
   const response = await fetch('/api/v1/vocabulary/flashcards/', {
       headers: {
           'Authorization': `Bearer ${token}`
       }
   });
   ```

4. **SM-2 Algorithm integration**
   - Lưu learning progress
   - Calculate next review date
   - Track easiness factor

## 📋 Khi nào SỬ DỤNG public/flashcard.html?

### ✅ Sử dụng làm:

1. **Design Reference**
   - Copy CSS styles
   - Copy HTML structure
   - Copy animation effects

2. **UI/UX Testing**
   - Test responsive design
   - Test user interactions
   - Test accessibility

3. **Prototype Demo**
   - Demo cho stakeholders
   - Quick mockup testing
   - Design iteration

### ❌ KHÔNG sử dụng cho:

1. Production deployment
2. User-facing features
3. API integration
4. Database operations
5. Authentication flows

## 🔧 Migration Checklist

Khi cần cập nhật design từ public/flashcard.html → Django template:

### 1. Copy CSS
```bash
# From
public/flashcard.html <style>

# To
backend/templates/vocabulary/flashcard_study.html {% block extra_css %}
```

### 2. Convert HTML to Django template syntax
```html
<!-- From (static) -->
<h1>Decision</h1>

<!-- To (dynamic) -->
<h1>[[ currentCard.word ]]</h1>
```

### 3. Add API integration
```javascript
// Add in {% block extra_js %}
methods: {
    async loadFlashcards() {
        const token = this.getAuthToken();
        const response = await fetch('/api/v1/vocabulary/flashcards/', {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        this.cards = await response.json();
    }
}
```

### 4. Add authentication check
```django-html
<!-- Template view needs JWT decorator -->
{% extends "base/_base_public.html" %}
<!-- This ensures user is authenticated -->
```

### 5. Test thoroughly
```bash
# Test authentication
python manage.py test backend.tests.vocabulary

# Test API integration
curl -H "Authorization: Bearer <token>" http://127.0.0.1:8001/api/v1/vocabulary/flashcards/

# Test UI rendering
# Visit: http://127.0.0.1:8001/vocabulary/decks/
```

## 📊 Comparison Table

| Feature | public/flashcard.html | Django Template |
|---------|----------------------|-----------------|
| **Location** | `public/` | `backend/templates/vocabulary/` |
| **Purpose** | Design reference | Production use |
| **Authentication** | ❌ None | ✅ JWT required |
| **API Integration** | ❌ Mock data | ✅ Real API calls |
| **Database** | ❌ Static | ✅ Dynamic |
| **Template Engine** | ❌ Plain HTML | ✅ Django templates |
| **Inheritance** | ❌ Standalone | ✅ Extends base |
| **CSRF Protection** | ❌ No | ✅ Yes |
| **User Progress** | ❌ No tracking | ✅ SM-2 algorithm |
| **Responsive** | ✅ Yes | ✅ Yes |
| **Animations** | ✅ 3D flip | ✅ 3D flip |

## 🎓 Best Practices

### ✅ DO:
- Use Django templates for production
- Keep public/flashcard.html as design reference
- Test all API integrations
- Implement proper authentication
- Track user progress in database

### ❌ DON'T:
- Deploy public/flashcard.html to production
- Link public/ files in Django URLs
- Mix static mockups with dynamic templates
- Bypass authentication for convenience
- Hardcode data in templates

## 📚 Related Documentation

- [Vocabulary App Structure](./COMPLIANCE_FIX_SUMMARY.md)
- [Template Organization](../../PROJECT_ORGANIZATION_ANALYSIS.md)
- [Authentication Flow](../testing/AUTH_FLOW.md)
- [SM-2 Algorithm](./PHASE_5_COMPLETE_REPORT.md)

---

**Last Updated**: 2025-12-19  
**Status**: ✅ Production templates properly configured  
**Design Reference**: `public/flashcard.html` preserved for UI/UX reference only
