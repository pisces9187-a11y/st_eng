# Hướng Dẫn Cấu Hình Đăng Nhập Google & Facebook OAuth2

## 📋 Tổng Quan

Hệ thống hỗ trợ đăng nhập bằng tài khoản Google và Facebook. Người dùng đăng nhập bằng mạng xã hội sẽ tự động được tạo tài khoản trong database PostgreSQL `englishstudy`.

## 🔧 Cấu Hình Google OAuth2

### Bước 1: Tạo Project trên Google Cloud Console

1. Truy cập [Google Cloud Console](https://console.cloud.google.com/)
2. Tạo project mới hoặc chọn project có sẵn
3. Vào **APIs & Services** > **OAuth consent screen**
4. Chọn **External** và điền thông tin:
   - App name: `English Study Platform`
   - User support email: Email của bạn
   - Developer contact email: Email của bạn
5. Click **Save and Continue**

### Bước 2: Tạo OAuth 2.0 Client ID

1. Vào **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth 2.0 Client ID**
3. Application type: **Web application**
4. Name: `English Study Web Client`
5. **Authorized JavaScript origins:**
   ```
   http://localhost:3000
   http://127.0.0.1:3000
   ```
6. **Authorized redirect URIs:**
   ```
   http://localhost:3000/public/login.html
   http://127.0.0.1:3000/public/login.html
   ```
7. Click **Create**
8. Sao chép **Client ID** và **Client Secret**

### Bước 3: Cập nhật cấu hình

1. Mở file `backend/.env` và cập nhật:
   ```
   GOOGLE_OAUTH2_CLIENT_ID=your-client-id.apps.googleusercontent.com
   GOOGLE_OAUTH2_CLIENT_SECRET=your-client-secret
   ```

2. Mở file `assets/js/config.js` và cập nhật:
   ```javascript
   socialAuth: {
       google: {
           clientId: 'your-client-id.apps.googleusercontent.com',
           // ...
       }
   }
   ```

---

## 🔷 Cấu Hình Facebook OAuth2

### Bước 1: Tạo Facebook App

1. Truy cập [Facebook Developers](https://developers.facebook.com/)
2. Click **My Apps** > **Create App**
3. Chọn **Consumer** > **Next**
4. Điền thông tin:
   - App name: `English Study Platform`
   - App contact email: Email của bạn
5. Click **Create App**

### Bước 2: Cấu hình Facebook Login

1. Trong Dashboard của app, tìm **Facebook Login** và click **Set Up**
2. Chọn **Web**
3. Site URL: `http://localhost:3000`
4. Click **Save**
5. Vào **Facebook Login** > **Settings**
6. **Valid OAuth Redirect URIs:**
   ```
   http://localhost:3000/public/login.html
   ```
7. Click **Save Changes**

### Bước 3: Lấy App ID và App Secret

1. Vào **Settings** > **Basic**
2. Sao chép **App ID** và **App Secret**

### Bước 4: Cập nhật cấu hình

1. Mở file `backend/.env` và cập nhật:
   ```
   FACEBOOK_APP_ID=your-app-id
   FACEBOOK_APP_SECRET=your-app-secret
   ```

2. Mở file `assets/js/config.js` và cập nhật:
   ```javascript
   socialAuth: {
       facebook: {
           appId: 'your-app-id',
           // ...
       }
   }
   ```

---

## 🗄️ Cơ Sở Dữ Liệu

### User được tạo từ Social Auth

Khi người dùng đăng nhập bằng Google hoặc Facebook lần đầu:

1. **User mới được tạo** trong bảng `users_user`:
   - `email`: Email từ Google/Facebook
   - `username`: `email_google` hoặc `fb_{fb_id}`
   - `first_name`, `last_name`: Từ profile mạng xã hội
   - `avatar`: Tự động download từ mạng xã hội

2. **Liên kết Social Auth** được lưu trong bảng `social_auth_usersocialauth`:
   - `provider`: `google-oauth2` hoặc `facebook`
   - `uid`: ID người dùng trên mạng xã hội
   - `extra_data`: JSON chứa thông tin bổ sung

### Xem users trong database

```bash
cd backend
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
User = get_user_model()

# Liệt kê tất cả users
for u in User.objects.all():
    print(f"{u.email} - {u.username} - Social: {u.social_auth.exists()}")

# Xem social auth
from social_django.models import UserSocialAuth
for sa in UserSocialAuth.objects.all():
    print(f"{sa.user.email} - {sa.provider} - {sa.uid}")
```

---

## 🔐 API Endpoints

### POST `/api/v1/auth/google/`

Đăng nhập bằng Google

**Request:**
```json
{
    "access_token": "google_oauth2_access_token"
}
```

**Response:**
```json
{
    "access": "jwt_access_token",
    "refresh": "jwt_refresh_token",
    "user": {
        "id": 1,
        "email": "user@gmail.com",
        "username": "user_google",
        "first_name": "User",
        "last_name": "Name",
        "current_level": "A1",
        "xp_points": 0,
        "streak_days": 0,
        "is_premium": false
    },
    "created": true  // true nếu user mới được tạo
}
```

### POST `/api/v1/auth/facebook/`

Đăng nhập bằng Facebook

**Request:**
```json
{
    "access_token": "facebook_access_token"
}
```

**Response:** (Tương tự Google)

---

## 🧪 Test Đăng Nhập

### 1. Khởi động servers

```bash
# Terminal 1 - Backend
cd backend
python manage.py runserver 8000

# Terminal 2 - Frontend
cd ..
python -m http.server 3000
```

### 2. Mở trình duyệt

1. Truy cập: `http://localhost:3000/public/login.html`
2. Click **Tiếp tục với Google** hoặc **Tiếp tục với Facebook**
3. Đăng nhập bằng tài khoản Google/Facebook
4. Sau khi thành công, bạn sẽ được chuyển đến Dashboard

### 3. Kiểm tra database

```bash
cd backend
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
User = get_user_model()

# Xem user mới nhất
latest = User.objects.latest('date_joined')
print(f"Email: {latest.email}")
print(f"Name: {latest.first_name} {latest.last_name}")
print(f"Username: {latest.username}")
```

---

## ⚠️ Lưu Ý Quan Trọng

1. **Development Mode**: Facebook App cần ở chế độ Development để test. Chỉ admin của app mới có thể đăng nhập.

2. **HTTPS cho Production**: Google và Facebook yêu cầu HTTPS cho production. Localhost được miễn.

3. **Tài khoản trùng email**: Nếu người dùng đã có tài khoản bằng email/password, đăng nhập bằng Google/Facebook sẽ liên kết với tài khoản hiện có (nếu cùng email).

4. **Avatar**: Hệ thống tự động download avatar từ mạng xã hội và lưu vào thư mục `media/avatars/`.

---

## 🔄 Flow Đăng Nhập

```
┌─────────────┐     ┌────────────────┐     ┌──────────────┐
│   Frontend  │────▶│  Google/FB     │────▶│   Backend    │
│  login.html │◀────│  OAuth Server  │◀────│  Django API  │
└─────────────┘     └────────────────┘     └──────────────┘
       │                    │                     │
       │ 1. Click Login     │                     │
       ├───────────────────▶│                     │
       │                    │                     │
       │ 2. Redirect to     │                     │
       │    Google/FB       │                     │
       │◀───────────────────│                     │
       │                    │                     │
       │ 3. User Login      │                     │
       ├───────────────────▶│                     │
       │                    │                     │
       │ 4. Access Token    │                     │
       │◀───────────────────│                     │
       │                    │                     │
       │ 5. Send token to   │                     │
       │    /auth/google/   │                     │
       ├──────────────────────────────────────────▶│
       │                                           │
       │ 6. Verify token with Google/FB           │
       │    Create/Get User                       │
       │    Generate JWT                          │
       │◀──────────────────────────────────────────│
       │                                           │
       │ 7. Store JWT & Redirect to Dashboard     │
       │                                           │
```

---

## 📝 Credentials Mẫu

Sau khi cấu hình xong, bạn có thể test với các tài khoản:

- **Email đăng nhập thông thường:**
  - `test@englishstudy.com` / `Test@123`
  - `admin@englishstudy.com` / `Admin@123`

- **Google/Facebook:** Sử dụng tài khoản thật của bạn

---

*Tài liệu này được tạo cho English Study Platform - Version 1.0*
