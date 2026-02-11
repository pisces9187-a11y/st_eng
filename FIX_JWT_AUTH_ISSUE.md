# Fix JWT Authentication Issue

## 🔍 Vấn đề phát hiện

### 1. URL không đúng (404 Error)
```
❌ SAI: http://localhost:8000/vocabulary/flashcards/study/
✅ ĐÚNG: http://localhost:8000/vocabulary/flashcard/
```

**Nguyên nhân**: URL có thêm "s" (flashcards) trong documentation nhưng thực tế không có

### 2. JWT Cookie bị expire
**Triệu chứng**:
- Trang chủ vẫn đăng nhập được (vì có localStorage JWT)
- Nhưng `/vocabulary/flashcard/` yêu cầu JWT cookie
- Cookie đã hết hạn → Middleware xóa cookie → Redirect về login

**Nguyên nhân**: JWT middleware chỉ check cookie, không check localStorage

## ⚡ Giải pháp nhanh

### Bước 1: Login lại để lấy JWT cookie mới
```bash
1. Mở http://localhost:8000/login/
2. Đăng nhập với:
   - Email: n2t@studyenglish.com
   - Password: [your password]
3. Sau khi login, mở Developer Tools > Application > Cookies
4. Xác nhận có 2 cookies:
   - access_token
   - refresh_token
```

### Bước 2: Truy cập đúng URL
```
http://localhost:8000/vocabulary/flashcard/
```

## 🔧 Fix vĩnh viễn

### Option 1: Thêm URL alias (Khuyên dùng)
Thêm vào `backend/apps/vocabulary/page_urls.py`:

```python
urlpatterns = [
    # Flashcard study page
    path('flashcard/', views.flashcard_study_view, name='flashcard-study'),
    path('flashcards/study/', views.flashcard_study_view, name='flashcard-study-alt'),  # ← THÊM DÒNG NÀY
    path('flashcard/<int:deck_id>/', views.flashcard_study_view, name='flashcard-study-deck'),
    
    # Deck list page
    path('decks/', views.deck_list_view, name='deck-list'),
    
    # Dashboard
    path('dashboard/', views.vocabulary_dashboard_view, name='dashboard'),
]
```

### Option 2: Sync JWT middleware với localStorage
Cập nhật middleware để check cả localStorage (nếu có):

```python
def _get_token(self, request):
    """Extract JWT token from request."""
    # Try Authorization header first
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if auth_header.startswith('Bearer '):
        return auth_header[7:]
    
    # Try cookie
    token = request.COOKIES.get('access_token')
    if token:
        return token
    
    # Try localStorage (via custom header from frontend)
    token_from_storage = request.META.get('HTTP_X_ACCESS_TOKEN')
    if token_from_storage:
        return token_from_storage
    
    return None
```

## 🎯 Test sau khi fix

### Test 1: URL hoạt động
```bash
curl -I http://localhost:8000/vocabulary/flashcard/
# Expect: 302 (redirect to login if not authenticated)

curl -I http://localhost:8000/vocabulary/flashcards/study/
# Expect: 200 (after fix Option 1)
```

### Test 2: JWT authentication
```bash
# 1. Login qua API
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"n2t@studyenglish.com","password":"YOUR_PASSWORD"}' \
  -c cookies.txt

# 2. Access protected page with cookie
curl http://localhost:8000/vocabulary/flashcard/ -b cookies.txt
# Expect: 200 OK với HTML content
```

### Test 3: Browser flow
1. Xóa tất cả cookies (F12 > Application > Clear site data)
2. Login tại `/login/`
3. Truy cập `/vocabulary/flashcard/`
4. Kiểm tra không bị redirect về login

## 📊 Chi tiết kỹ thuật

### JWT Cookie Lifetime
```python
# Access token: 24 hours (86400 seconds)
response.set_cookie('access_token', token, max_age=86400, httponly=True)

# Refresh token: 30 days (2592000 seconds)
response.set_cookie('refresh_token', token, max_age=2592000, httponly=True)
```

### Middleware Flow
```
Request → Check cookie → Valid? → Set request.user → Continue
                      ↓ Invalid
                      → Try refresh token → Success? → Update cookies → Continue
                                          ↓ Failed
                                          → Clear cookies → Redirect to login
```

### URL Routing
```
Root:           http://localhost:8000/
Login:          http://localhost:8000/login/
Flashcard:      http://localhost:8000/vocabulary/flashcard/
Flashcard API:  http://localhost:8000/api/v1/vocabulary/flashcards/study/
```

## ✅ Checklist sau khi fix

- [ ] URL `/vocabulary/flashcard/` trả về 200
- [ ] URL `/vocabulary/flashcards/study/` trả về 200 (nếu dùng Option 1)
- [ ] Login tạo JWT cookies
- [ ] Cookies được tự động refresh khi hết hạn
- [ ] Không bị redirect loop ở `/dashboard/`
- [ ] F5 refresh page không mất authentication

## 🚀 Thực hiện fix ngay

Implement Option 1 (khuyên dùng vì đơn giản và không breaking changes):
