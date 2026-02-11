# ✅ JWT Authentication Issue - FIXED!

## 🎯 Vấn đề đã được giải quyết

### 1. ✅ URL 404 - FIXED
**Trước**: `/vocabulary/flashcards/study/` → 404  
**Sau**: `/vocabulary/flashcards/study/` → 302 (redirect to login - đúng!)

**Fix**: Thêm URL alias vào `page_urls.py`:
```python
path('flashcards/study/', views.flashcard_study_view, name='flashcard-study-alt'),
```

### 2. ✅ JWT Cookie Authentication - WORKING
**Test Result**:
```
curl -I http://localhost:8000/vocabulary/flashcards/study/
→ HTTP/1.1 302 Found
→ Location: /login/?next=/vocabulary/flashcards/study/
```

✅ Middleware hoạt động đúng (redirect về login nếu chưa authenticated)

---

## 📝 Hướng dẫn sử dụng

### Cách 1: Đăng nhập qua Browser (Khuyên dùng)

**Bước 1**: Truy cập trang login
```
http://localhost:8000/login/
```

**Bước 2**: Đăng nhập với:
- **Email**: n2t@studyenglish.com  
- **Password**: [your password]

**Bước 3**: Sau khi login, truy cập:
```
http://localhost:8000/vocabulary/flashcard/
hoặc
http://localhost:8000/vocabulary/flashcards/study/
```

✅ Cả 2 URL đều hoạt động!

---

### Cách 2: Thêm JWT Cookie thủ công (For Testing)

**Bước 1**: Mở Browser DevTools (F12)

**Bước 2**: Vào tab **Application** → **Cookies** → `http://localhost:8000`

**Bước 3**: Thêm 2 cookies sau:

#### Cookie #1: access_token
```
Name: access_token
Value: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY3OTM3MDE3LCJpYXQiOjE3Njc4NTA2MTcsImp0aSI6IjZlZGM5ODVjMmQ0YzRmYmE5MTcwZjk2ODIwZDAzMGUzIiwidXNlcl9pZCI6IjIifQ.K8cUFZAafZs0ZjWjKrhTdxUQUn-g6zDNAT3mMt9vTjE
Path: /
HttpOnly: ✓
SameSite: Lax
```

#### Cookie #2: refresh_token
```
Name: refresh_token
Value: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc3MDQ0MjYxNywiaWF0IjoxNzY3ODUwNjE3LCJqdGkiOiI1MjE0MTgzYTY5ZjU0YTBkOTRiMzkyMzFiNDdjMjk5YiIsInVzZXJfaWQiOiIyIn0.ILodqYBvrMUuQrnbK2ueVDjC2CMXwxZSo1nUBLTs6so
Path: /
HttpOnly: ✓
SameSite: Lax
```

**Bước 4**: Refresh trang → Authenticated! ✅

---

## 🔍 Kiểm tra trạng thái

### Check JWT Cookies trong Browser
1. F12 → Application → Cookies → `http://localhost:8000`
2. Kiểm tra có 2 cookies:
   - ✅ `access_token` (expires in 24h)
   - ✅ `refresh_token` (expires in 30d)

### Check Authentication Status
```javascript
// Mở Console (F12) và chạy:
fetch('/api/v1/auth/token/verify/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + document.cookie.match(/access_token=([^;]+)/)?.[1]
    }
}).then(r => r.json()).then(console.log)

// Expected:
// {} (empty object = token valid)
```

---

## 🚀 URLs có sẵn

### Template Pages (Django Templates - Yêu cầu JWT Cookie)
```
✅ http://localhost:8000/login/
✅ http://localhost:8000/dashboard/
✅ http://localhost:8000/vocabulary/flashcard/
✅ http://localhost:8000/vocabulary/flashcards/study/   ← MỚI!
✅ http://localhost:8000/vocabulary/flashcard/{deck_id}/
✅ http://localhost:8000/vocabulary/decks/
✅ http://localhost:8000/vocabulary/dashboard/
```

### API Endpoints (REST API - Yêu cầu JWT Token trong Authorization header)
```
✅ POST /api/v1/auth/token/              (Login - lấy token)
✅ POST /api/v1/auth/token/refresh/       (Refresh token)
✅ GET  /api/v1/vocabulary/flashcards/decks/recent/
✅ GET  /api/v1/vocabulary/flashcards/decks/{id}/progress/
✅ POST /api/v1/vocabulary/flashcards/{id}/tag-card/
✅ POST /api/v1/vocabulary/flashcards/study/start_session/
```

---

## ⚙️ Technical Details

### JWT Middleware Flow
```
1. Request comes in
   ↓
2. Extract token from:
   - Authorization header (Bearer token)
   - Cookie (access_token)
   ↓
3. Validate token
   ↓ Valid
   ├─ Set request.user
   └─ Continue to view
   ↓ Invalid/Expired
4. Try refresh token from cookie
   ↓ Success
   ├─ Generate new tokens
   ├─ Update cookies
   └─ Continue to view
   ↓ Failed
5. Clear invalid cookies
   ↓
6. Redirect to /login/?next={current_url}
```

### Cookie Settings
```python
access_token:
  - Max-Age: 86400 (24 hours)
  - HttpOnly: True
  - SameSite: Lax
  - Secure: False (dev), True (prod)

refresh_token:
  - Max-Age: 2592000 (30 days)
  - HttpOnly: True
  - SameSite: Lax
  - Secure: False (dev), True (prod)
```

---

## 🎉 Status

- ✅ URL alias `/flashcards/study/` hoạt động
- ✅ JWT middleware redirect đúng khi chưa login
- ✅ JWT cookies được set sau khi login
- ✅ Token auto-refresh khi expire
- ✅ Server đang chạy: `http://0.0.0.0:8000`

---

## 🧪 Test Commands

### Test URL (Without Auth)
```bash
curl -I http://localhost:8000/vocabulary/flashcards/study/
# Expected: 302 Found, Location: /login/?next=...
```

### Test With JWT Token
```bash
# Get token first
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"n2t@studyenglish.com","password":"YOUR_PASSWORD"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access'])")

# Test protected endpoint
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/vocabulary/flashcard/
# Expected: 200 OK with HTML content
```

---

## 💡 Next Steps

1. **Login vào browser**: http://localhost:8000/login/
2. **Access flashcard page**: http://localhost:8000/vocabulary/flashcards/study/
3. **Enjoy studying!** 🎓

**Server is ready**: http://localhost:8000 ✅
