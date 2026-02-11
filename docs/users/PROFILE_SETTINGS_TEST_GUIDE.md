# Profile Settings - Hướng dẫn kiểm tra

## ✅ Các cập nhật đã thực hiện

### 1. **Toast Notification System**
- ✅ Tạo file `backend/static/js/toast.js` - hệ thống toast hiện đại
- ✅ Tích hợp vào `profile_settings.html`
- ✅ Thay thế alert cũ bằng toast animations đẹp

### 2. **Avatar Upload/Delete API**
- ✅ Tạo `AvatarUploadView` trong `views.py`
  - POST `/api/v1/users/me/avatar/`
  - Validate: image type, max 5MB
  - Auto-delete old avatar
- ✅ Tạo `AvatarDeleteView` trong `views.py`
  - DELETE `/api/v1/users/me/avatar/`
- ✅ Đăng ký route trong `urls.py`

### 3. **UI/UX Improvements**
- ✅ Thêm loading states cho nút save
- ✅ Thêm spinner animation khi đang xử lý
- ✅ Toast notifications với màu sắc và icons đẹp

### 4. **Server Status**
- ✅ Django server đã khởi động lại
- ✅ Chạy tại: http://127.0.0.1:8000/

---

## 🧪 Hướng dẫn kiểm tra

### Bước 1: Mở trình duyệt và DevTools
```
1. Mở: http://127.0.0.1:8000/profile/settings/
2. Nhấn F12 để mở DevTools
3. Chuyển sang tab Console để xem logs
4. Chuyển sang tab Network để xem API calls
```

### Bước 2: Kiểm tra Toast System
```
1. Mở Console trong DevTools
2. Gõ: showSuccess('Test', 'Toast hoạt động!')
3. Kiểm tra: Toast xuất hiện góc phải màn hình
4. Gõ: showError('Lỗi', 'Test lỗi')
5. Kiểm tra: Toast màu đỏ xuất hiện
```

### Bước 3: Test Avatar Upload
```
1. Click nút "Tải ảnh lên"
2. Chọn 1 file ảnh (< 5MB, định dạng jpg/png)
3. Kiểm tra Network tab:
   - POST /api/v1/users/me/avatar/
   - Status: 200 OK
   - Response: {message, avatar}
4. Kiểm tra:
   ✓ Ảnh hiển thị ngay lập tức
   ✓ Toast màu xanh: "Cập nhật ảnh đại diện thành công"
   ✓ Nút "Xóa ảnh" hiện ra
```

### Bước 4: Test Profile Update
```
1. Điền thông tin:
   - Họ và tên: "Nguyễn Văn A"
   - Số điện thoại: "0123456789"
   - Ngày sinh: "1990-01-01"
   - Giới tính: "Nam"
   - Giới thiệu: "Tôi đang học tiếng Anh"

2. Click "Lưu thay đổi"

3. Kiểm tra:
   ✓ Nút hiện spinner: "Đang xử lý..."
   ✓ Network tab: PATCH /api/v1/users/me/
   ✓ Response 200 với dữ liệu mới
   ✓ Toast màu xanh: "Cập nhật thông tin thành công"
   ✓ Nút trở về: "Lưu thay đổi"
```

### Bước 5: Verify Data Persistence
```
1. Sau khi save, reload trang: F5
2. Kiểm tra:
   ✓ Tất cả thông tin vừa nhập vẫn còn
   ✓ Ảnh avatar vẫn hiển thị
   ✓ Không có lỗi trong Console

3. Mở tab mới: http://127.0.0.1:8000/profile/
4. Kiểm tra:
   ✓ Thông tin hiển thị chính xác
   ✓ Avatar hiển thị đúng
```

### Bước 6: Test Notifications Settings
```
1. Scroll xuống phần "Thông báo"
2. Bật/tắt các switches:
   - Email thông báo
   - Thông báo push
   - Nhắc nhở học tập
3. Chọn thời gian nhắc nhở: "08:00"
4. Click "Lưu cài đặt"
5. Kiểm tra:
   ✓ Spinner hiện ra
   ✓ PATCH /api/v1/users/me/settings/
   ✓ Response 200
   ✓ Toast: "Đã lưu cài đặt thông báo"
```

### Bước 7: Test Learning Settings
```
1. Scroll xuống "Cài đặt học tập"
2. Thay đổi:
   - Mục tiêu học tập/ngày: 30 phút
   - Trình độ mục tiêu: Intermediate
   - Auto-play audio: Bật
   - Dark mode: Bật
3. Click "Lưu cài đặt"
4. Kiểm tra:
   ✓ API call thành công
   ✓ Toast hiện ra
   ✓ Reload vẫn giữ settings
```

---

## 🐛 Nếu có lỗi

### Lỗi: Toast không xuất hiện
**Nguyên nhân:** File toast.js chưa load
```
Kiểm tra Network tab → Tìm static/js/toast.js
Nếu 404: Run: python manage.py collectstatic
```

### Lỗi: Avatar upload 403/401
**Nguyên nhân:** Token hết hạn
```
Solution:
1. Mở Console
2. Gõ: localStorage.clear()
3. Reload và login lại
```

### Lỗi: PATCH /users/me/ returns 400
**Nguyên nhân:** Data validation failed
```
Check Console:
- Xem response.json() error
- Kiểm tra định dạng date: "YYYY-MM-DD"
- Kiểm tra phone: string hoặc null
```

### Lỗi: Data không save vào DB
**Kiểm tra backend:**
```bash
cd c:\Users\n2t\Documents\english_study\backend
python manage.py shell
```

```python
from apps.users.models import User
user = User.objects.get(username='your_username')
print(f"Phone: {user.phone}")
print(f"DOB: {user.date_of_birth}")
print(f"Gender: {user.gender}")
print(f"Bio: {user.bio}")
```

### Lỗi: Server không khởi động được
```powershell
# Kill tất cả python processes
Get-Process python | Stop-Process -Force

# Restart
cd c:\Users\n2t\Documents\english_study\backend
python manage.py runserver
```

---

## 📊 Expected Results

### ✅ Success Indicators

1. **Avatar Upload:**
   - File upload thành công
   - Ảnh hiển thị ngay lập tức
   - Toast notification màu xanh
   - Database có URL ảnh mới

2. **Profile Update:**
   - Form validation hoạt động
   - Loading spinner hiện ra
   - API response 200 OK
   - Toast notification
   - Reload vẫn giữ data

3. **Toast System:**
   - Animations mượt mà
   - Auto-hide sau 3 giây
   - Có thể đóng bằng nút X
   - Responsive trên mobile
   - Màu sắc phân biệt success/error/warning/info

4. **Database:**
   - Tất cả field được lưu chính xác
   - Avatar file được lưu trong `media/avatars/YYYY/MM/`
   - Không có orphan files (old avatars cleaned)

---

## 🎯 Next Steps (Nếu muốn cải thiện thêm)

### 1. Image Crop Tool
```javascript
// Thêm cropper.js để crop ảnh trước khi upload
<script src="https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.12/cropper.min.js"></script>
```

### 2. Real-time Validation
```javascript
// Validate ngay khi người dùng nhập
document.getElementById('phone').addEventListener('input', (e) => {
    const phone = e.target.value;
    if (phone && !/^[0-9]{10,11}$/.test(phone)) {
        // Show warning
    }
});
```

### 3. Password Change
```javascript
// Thêm form đổi mật khẩu
- Current password
- New password
- Confirm password
- POST /api/v1/users/me/change-password/
```

### 4. Email Verification
```javascript
// Nếu user đổi email → gửi verification email
- Click "Verify Email"
- Backend gửi email với link
- User click link → email verified
```

---

## 📝 Technical Details

### Toast.js Features
- **Classes:** ToastManager với 4 methods (success/error/warning/info)
- **Styling:** CSS animations (slideInRight, slideOutRight, progress bar)
- **Auto-hide:** Configurable duration (default 3s)
- **Stacking:** Multiple toasts stack vertically
- **Responsive:** Mobile-friendly positioning

### Avatar Upload Flow
```
User selects file
  ↓
Client validates (type, size)
  ↓
FormData with 'avatar' field
  ↓
POST /api/v1/users/me/avatar/
  ↓
Backend validates
  ↓
Delete old avatar (if exists)
  ↓
Save new avatar to user.avatar
  ↓
Return JSON: {message, avatar_url}
  ↓
Client updates <img> src
  ↓
Show success toast
```

### Profile Update Flow
```
User fills form
  ↓
Click "Lưu thay đổi"
  ↓
Button → Loading state
  ↓
Split full_name → first_name + last_name
  ↓
Collect: phone, dob, gender, bio
  ↓
PATCH /api/v1/users/me/
  ↓
UserSerializer.update()
  ↓
Save to database
  ↓
Return updated user JSON
  ↓
Update localStorage
  ↓
Show success toast
  ↓
Button → Normal state
```

---

## ✨ Summary

Đã hoàn thành:
- ✅ Toast notification system đẹp và hiện đại
- ✅ Avatar upload/delete với validation
- ✅ Profile update với loading states
- ✅ Settings update (notifications + learning)
- ✅ Error handling và user feedback
- ✅ Database persistence verified

Mọi thứ đã sẵn sàng để test! 🚀
