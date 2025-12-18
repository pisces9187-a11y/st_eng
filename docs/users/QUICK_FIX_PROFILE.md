# 🔧 Quick Fix Guide - Profile Settings

## 🔴 Vấn đề đã phát hiện

### 1. Form submit qua GET thay vì AJAX
**Triệu chứng:** URL có query params `?full_name=123&phone_number=12344...`
**Nguyên nhân:** Form không có `onsubmit="return false;"` → submit như HTML form
**Đã fix:** ✅ Thêm `onsubmit="return false;"` vào `<form>` tag

### 2. Toast system không load
**Triệu chứng:** `showSuccess()` không hiển thị toast
**Nguyên nhân:** Script load nhưng chưa có fallback
**Đã fix:** ✅ Thêm console logging + fallback alert nếu Toast không available

---

## ✅ Các thay đổi đã thực hiện

### File: `profile_settings.html`

#### 1. Form tag - Chặn default submit
```html
<!-- OLD -->
<form id="profileForm">

<!-- NEW -->
<form id="profileForm" onsubmit="return false;">
```

#### 2. Toast loading - Thêm logging
```javascript
<!-- OLD -->
<script src="{% static 'js/toast.js' %}"></script>
<script>
const API_BASE_URL = '/api/v1';

<!-- NEW -->
<script src="{% static 'js/toast.js' %}"></script>
<script>
console.log('🚀 Profile Settings Script Loading...');
console.log('Toast available:', typeof Toast !== 'undefined');

const API_BASE_URL = '/api/v1';
```

#### 3. showSuccess/showError - Thêm fallback
```javascript
// OLD
function showSuccess(message, title = 'Thành công') {
    window.showSuccess(title, message);
}

// NEW
function showSuccess(message, title = 'Thành công') {
    console.log('✅ showSuccess called:', title, message);
    if (typeof window.Toast !== 'undefined' && typeof window.showSuccess === 'function') {
        window.showSuccess(title, message);
    } else {
        console.error('❌ Toast system not available!');
        alert(`${title}\n${message}`);
    }
}
```

### File: `config/urls.py`
```python
# Thêm test route để debug toast
path('test/toast/', TemplateView.as_view(template_name='test_toast.html'), name='test-toast'),
```

---

## 🧪 Testing Steps

### Test 1: Kiểm tra Toast System
```
1. Mở: http://127.0.0.1:8000/test/toast/
2. Click các nút: Success, Error, Warning, Info
3. Kiểm tra:
   ✓ Toast xuất hiện góc phải màn hình
   ✓ Animation mượt mà
   ✓ Auto-hide sau 3 giây
   ✓ Console log không có lỗi
```

### Test 2: Profile Settings Form
```
1. Mở: http://127.0.0.1:8000/profile/settings/
2. Mở DevTools (F12) → Console tab
3. Kiểm tra logs:
   ✓ "🚀 Profile Settings Script Loading..."
   ✓ "Toast available: true"

4. Điền form:
   - Họ tên: "Nguyễn Văn A"
   - SĐT: "0123456789"
   - Ngày sinh: "1990-01-01"
   - Giới tính: "Nam"
   - Bio: "Test bio"

5. Click "Lưu thay đổi"

6. Kiểm tra Console:
   ✓ "✅ showSuccess called: Thành công, Cập nhật thông tin thành công!"
   ✓ Network tab: PATCH /api/v1/users/me/ → 200 OK
   ✓ Toast xuất hiện (hoặc alert nếu toast không load)

7. Reload trang (F5)
   ✓ Kiểm tra data vẫn còn trong form
```

### Test 3: Avatar Upload
```
1. Click "Tải ảnh lên"
2. Chọn file ảnh (< 5MB)
3. Kiểm tra:
   ✓ Console log upload progress
   ✓ Network: POST /api/v1/users/me/avatar/ → 200 OK
   ✓ Toast (hoặc alert): "Cập nhật ảnh đại diện thành công"
   ✓ Ảnh hiển thị ngay
```

### Test 4: Database Persistence
```powershell
cd c:\Users\n2t\Documents\english_study\backend
python manage.py shell
```

```python
from apps.users.models import User
user = User.objects.get(username='n2t')  # Thay 'n2t' bằng username của bạn

print(f"Phone: {user.phone}")
print(f"DOB: {user.date_of_birth}")
print(f"Gender: {user.gender}")
print(f"Bio: {user.bio}")
print(f"Avatar: {user.avatar}")

# Expected output (after saving):
# Phone: 0123456789
# DOB: 1990-01-01
# Gender: male
# Bio: Test bio
# Avatar: avatars/2025/12/filename.jpg
```

---

## 🐛 Troubleshooting

### Vấn đề: Toast vẫn không hiện, chỉ thấy alert

**Kiểm tra:**
```javascript
// In Browser Console:
console.log('Toast:', typeof Toast);
console.log('showSuccess:', typeof window.showSuccess);
```

**Nếu undefined:**
1. Check Network tab: `/static/js/toast.js` → 200 OK?
2. Nếu 404:
```powershell
cd c:\Users\n2t\Documents\english_study\backend
python manage.py collectstatic --noinput
```

3. Kiểm tra file:
```powershell
Test-Path "c:\Users\n2t\Documents\english_study\backend\staticfiles\js\toast.js"
# Should return: True
```

### Vấn đề: Form vẫn submit qua GET

**Triệu chứng:** URL thay đổi thành `?full_name=...`

**Fix:**
- Kiểm tra form tag có `onsubmit="return false;"`
- Hoặc thêm vào event listener:
```javascript
document.getElementById('profileForm').addEventListener('submit', function(e) {
    e.preventDefault();  // Chắc chắn prevent default
    // ... rest of save logic
});
```

### Vấn đề: API trả về 400 Bad Request

**Kiểm tra Console:**
```javascript
// Xem error response
const response = await apiRequest('/users/me/', { method: 'PATCH', body: ... });
const error = await response.json();
console.log('Error details:', error);
```

**Common errors:**
- `date_of_birth`: Phải format "YYYY-MM-DD"
- `phone`: String hoặc null (không để empty string "")
- `gender`: Phải là "male", "female", hoặc "other"

### Vấn đề: Token expired (401)

**Quick fix:**
```javascript
// In Browser Console:
localStorage.clear();
// Then reload and login again
```

---

## 📊 Expected Behavior (Sau khi fix)

### ✅ Profile Update Flow:

1. User điền form và click "Lưu thay đổi"
2. Button → Loading: "Đang xử lý..."
3. Console log: "✅ showSuccess called..."
4. Network: PATCH /api/v1/users/me/ → 200 OK
5. Toast xuất hiện (màu xanh, icon ✓)
6. Button → Normal: "Lưu thay đổi"
7. Reload → Data vẫn còn
8. Check DB → Data đã save

### ✅ Avatar Upload Flow:

1. User click "Tải ảnh lên"
2. Chọn file
3. Console log upload info
4. Network: POST /api/v1/users/me/avatar/ → 200 OK
5. Toast: "Cập nhật ảnh đại diện thành công"
6. Ảnh hiển thị ngay lập tức
7. Nút "Xóa ảnh" xuất hiện

### ✅ Toast System:

- Xuất hiện góc phải màn hình
- Animation: slide in từ phải
- Auto-hide sau 3 giây
- Progress bar chạy từ trái sang phải
- Click X để đóng sớm
- Multiple toasts stack vertically
- Responsive trên mobile

---

## 🎯 Next Steps (Nếu vẫn không work)

### 1. Hard Refresh Browser
```
Ctrl + Shift + R (Windows)
Cmd + Shift + R (Mac)
```

### 2. Clear Browser Cache
```
Chrome: Settings → Privacy → Clear browsing data → Cached images and files
```

### 3. Restart Django Server
```powershell
# Kill all Python processes
Get-Process python | Stop-Process -Force

# Restart
cd c:\Users\n2t\Documents\english_study\backend
python manage.py runserver
```

### 4. Verify Static Files Setup
```python
# In backend/config/settings/development.py
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
```

### 5. Test with curl
```powershell
# Test API directly
$headers = @{
    "Authorization" = "Bearer YOUR_TOKEN_HERE"
    "Content-Type" = "application/json"
}

$body = @{
    first_name = "Nguyen"
    last_name = "Van A"
    phone = "0123456789"
    date_of_birth = "1990-01-01"
    gender = "male"
    bio = "Test"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/users/me/" -Method PATCH -Headers $headers -Body $body
```

---

## 📝 Summary

**Files Changed:**
1. ✅ `profile_settings.html` - Fixed form submit + added toast logging
2. ✅ `config/urls.py` - Added test route
3. ✅ `test_toast.html` - Created test page

**What Should Work Now:**
1. ✅ Form không submit qua GET nữa → Dùng AJAX PATCH
2. ✅ Toast system có fallback → Hiện alert nếu không load
3. ✅ Console logging → Dễ debug
4. ✅ Test page → Kiểm tra toast độc lập

**URLs để test:**
- Toast test: http://127.0.0.1:8000/test/toast/
- Profile settings: http://127.0.0.1:8000/profile/settings/
- Profile view: http://127.0.0.1:8000/profile/

**Nếu vẫn không work, hãy:**
1. Mở http://127.0.0.1:8000/test/toast/ trước
2. Test các nút toast
3. Nếu toast work → Vấn đề ở profile_settings.html
4. Nếu toast không work → Vấn đề ở toast.js loading
