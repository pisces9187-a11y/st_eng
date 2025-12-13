# UI SPECIFICATIONS - AUTHENTICATION & USER PROFILE
**Dự án:** Hệ thống học Tiếng Anh A1-C1  
**Phiên bản:** 1.0  
**Ngày:** 07/12/2025  
**Design System:** Energetic Orange Theme

---

## 📋 MỤC LỤC
1. [Hệ thống Màu & Font](#1-hệ-thống-màu--font)
2. [Màn hình Đăng nhập/Đăng ký](#2-màn-hình-đăng-nhậpđăng-ký)
3. [Màn hình Hồ sơ người dùng](#3-màn-hình-hồ-sơ-người-dùng)
4. [Hướng dẫn Kỹ thuật Django](#4-hướng-dẫn-kỹ-thuật-django)

---

## 1. HỆ THỐNG MÀU & FONT

### 1.1 Typography
```css
/* Tiêu đề */
font-family: 'Montserrat', sans-serif;
font-weight: 700; /* Bold */
font-weight: 800; /* ExtraBold */

/* Nội dung */
font-family: 'Open Sans', sans-serif;
font-weight: 400; /* Regular */
```

### 1.2 Color Palette
```css
/* Primary Colors */
--primary-orange: #F47C26;        /* Nút chính, Highlight */
--secondary-navy: #183B56;        /* Sidebar, Tiêu đề lớn */

/* Background */
--bg-light: #F9FAFC;              /* Nền tổng thể */
--bg-white: #FFFFFF;              /* Card, Form */
--bg-input: #F2F4F8;              /* Input fields */

/* Text */
--text-primary: #2C3E50;          /* Chữ chính */
--text-secondary: #6C757D;        /* Chữ phụ */
--text-muted: #95A5A6;            /* Placeholder, disabled */

/* Status */
--success: #27AE60;               /* Đã liên kết */
--warning: #F39C12;               /* Cảnh báo */
--error: #E74C3C;                 /* Lỗi */

/* Social */
--facebook-blue: #1877F2;
--google-border: #DADCE0;
```

### 1.3 Spacing & Borders
```css
--border-radius: 8px;
--border-radius-lg: 12px;
--box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
--box-shadow-hover: 0 4px 12px rgba(244, 124, 38, 0.15);
```

---

## 2. MÀN HÌNH ĐĂNG NHẬP/ĐĂNG KÝ

### 2.1 Layout Overview
**Split Screen (50-50):**
- **Trái:** Branding Area (Cố định)
- **Phải:** Authentication Form (Scrollable)

### 2.2 Branding Area (Bên Trái)

```html
<!-- Kích thước: 50vw x 100vh -->
<div class="auth-branding">
  <!-- Nền: #183B56 -->
  
  <div class="branding-content">
    <!-- Logo -->
    <img src="logo.svg" alt="Logo" class="logo" />
    <!-- Kích thước: 120px height -->
    
    <!-- Slogan -->
    <h1 class="slogan">
      Chinh phục Tiếng Anh<br>sau 3 tháng
    </h1>
    <!-- Font: Montserrat ExtraBold, 42px, #FFFFFF -->
    
    <!-- Illustration (Optional) -->
    <img src="illustration-learning.svg" class="illustration" />
  </div>
</div>
```

**CSS Specs:**
```css
.auth-branding {
  background: linear-gradient(135deg, #183B56 0%, #1a4363 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
}

.slogan {
  font-family: 'Montserrat', sans-serif;
  font-weight: 800;
  font-size: 42px;
  line-height: 1.3;
  color: #FFFFFF;
  text-align: center;
  margin-top: 30px;
}
```

### 2.3 Form Area (Bên Phải)

#### 2.3.1 Container
```css
.auth-form-container {
  background: #FFFFFF;
  padding: 60px 80px;
  max-width: 500px;
  margin: 0 auto;
}
```

#### 2.3.2 Heading
```html
<h2 class="form-title">Chào mừng trở lại!</h2>
```
```css
.form-title {
  font-family: 'Montserrat', sans-serif;
  font-weight: 700;
  font-size: 32px;
  color: #183B56;
  margin-bottom: 40px;
  text-align: center;
}
```

#### 2.3.3 Social Login Buttons

**⚠️ Ưu tiên hiển thị trên cùng!**

```html
<div class="social-login">
  <!-- Google Button -->
  <button class="btn-social btn-google">
    <img src="icon-google.svg" alt="Google" width="20" height="20" />
    <span>Tiếp tục với Google</span>
  </button>
  
  <!-- Facebook Button -->
  <button class="btn-social btn-facebook">
    <img src="icon-facebook.svg" alt="Facebook" width="20" height="20" />
    <span>Tiếp tục với Facebook</span>
  </button>
</div>
```

**CSS Specs:**
```css
.btn-social {
  width: 100%;
  height: 52px;
  border-radius: 8px;
  font-family: 'Open Sans', sans-serif;
  font-weight: 600;
  font-size: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 16px;
}

.btn-google {
  background: #FFFFFF;
  border: 1.5px solid #DADCE0;
  color: #3C4043;
}

.btn-google:hover {
  background: #F8F9FA;
  border-color: #BABFC5;
}

.btn-facebook {
  background: #1877F2;
  border: none;
  color: #FFFFFF;
}

.btn-facebook:hover {
  background: #166FE5;
}
```

#### 2.3.4 Divider
```html
<div class="divider">
  <span>Hoặc đăng nhập bằng Email</span>
</div>
```
```css
.divider {
  display: flex;
  align-items: center;
  margin: 30px 0;
  color: #95A5A6;
  font-size: 14px;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #E0E0E0;
}

.divider span {
  padding: 0 15px;
}
```

#### 2.3.5 Input Fields

```html
<form class="auth-form">
  <!-- Email Input -->
  <div class="form-group">
    <label for="email">Email</label>
    <input 
      type="email" 
      id="email" 
      class="form-input" 
      placeholder="example@email.com"
      required
    />
  </div>
  
  <!-- Password Input -->
  <div class="form-group">
    <label for="password">Mật khẩu</label>
    <input 
      type="password" 
      id="password" 
      class="form-input" 
      placeholder="••••••••"
      required
    />
  </div>
</form>
```

**CSS Specs:**
```css
.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  font-family: 'Open Sans', sans-serif;
  font-weight: 600;
  font-size: 14px;
  color: #2C3E50;
  margin-bottom: 8px;
}

.form-input {
  width: 100%;
  height: 48px;
  padding: 0 16px;
  background: #F2F4F8;
  border: 2px solid transparent;
  border-radius: 8px;
  font-family: 'Open Sans', sans-serif;
  font-size: 15px;
  color: #2C3E50;
  transition: all 0.2s ease;
}

.form-input::placeholder {
  color: #95A5A6;
}

.form-input:focus {
  outline: none;
  border-color: #F47C26;
  background: #FFFFFF;
}

.form-input:disabled {
  background: #E8EAED;
  color: #95A5A6;
  cursor: not-allowed;
}
```

#### 2.3.6 Primary CTA Button

```html
<button type="submit" class="btn-primary">
  ĐĂNG NHẬP
</button>
```

**CSS Specs:**
```css
.btn-primary {
  width: 100%;
  height: 52px;
  background: #F47C26;
  border: none;
  border-radius: 8px;
  font-family: 'Montserrat', sans-serif;
  font-weight: 700;
  font-size: 16px;
  color: #FFFFFF;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(244, 124, 38, 0.25);
  transition: all 0.3s ease;
  margin-top: 10px;
}

.btn-primary:hover {
  background: #E86F1E;
  box-shadow: 0 6px 16px rgba(244, 124, 38, 0.35);
  transform: translateY(-2px);
}

.btn-primary:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(244, 124, 38, 0.25);
}
```

#### 2.3.7 Secondary Links

```html
<div class="auth-footer">
  <a href="/password-reset" class="link-secondary">
    Quên mật khẩu?
  </a>
  
  <p class="signup-prompt">
    Chưa có tài khoản? 
    <a href="/signup" class="link-primary">Đăng ký ngay</a>
  </p>
</div>
```

**CSS Specs:**
```css
.auth-footer {
  margin-top: 30px;
  text-align: center;
}

.link-secondary {
  color: #183B56;
  font-size: 14px;
  text-decoration: underline;
  transition: color 0.2s;
}

.link-secondary:hover {
  color: #0F2538;
}

.signup-prompt {
  margin-top: 20px;
  font-size: 14px;
  color: #6C757D;
}

.link-primary {
  color: #F47C26;
  font-weight: 600;
  text-decoration: none;
  transition: color 0.2s;
}

.link-primary:hover {
  color: #E86F1E;
  text-decoration: underline;
}
```

### 2.4 Responsive Behavior

```css
@media (max-width: 992px) {
  /* Ẩn Branding Area trên tablet/mobile */
  .auth-branding {
    display: none;
  }
  
  .auth-form-container {
    padding: 40px 30px;
    max-width: 100%;
  }
}
```

---

## 3. MÀN HÌNH HỒ SƠ NGƯỜI DÙNG

### 3.1 Layout Overview

```
┌─────────────────────────────────────────┐
│  [Sidebar]  │  [Main Content Area]      │
│   260px     │      Flexible Width       │
└─────────────────────────────────────────┘
```

### 3.2 Sidebar Navigation

#### 3.2.1 Structure
```html
<aside class="sidebar">
  <div class="sidebar-header">
    <img src="logo-white.svg" alt="Logo" class="sidebar-logo" />
  </div>
  
  <nav class="sidebar-nav">
    <a href="/dashboard" class="nav-item">
      <span class="nav-icon">🏠</span>
      <span>Tổng quan</span>
    </a>
    
    <a href="/courses" class="nav-item">
      <span class="nav-icon">📚</span>
      <span>Khóa học của tôi</span>
    </a>
    
    <a href="/flashcards" class="nav-item">
      <span class="nav-icon">⚡</span>
      <span>Ôn tập Flashcard</span>
    </a>
    
    <a href="/profile" class="nav-item active">
      <span class="nav-icon">👤</span>
      <span>Hồ sơ cá nhân</span>
    </a>
    
    <a href="/settings" class="nav-item">
      <span class="nav-icon">⚙️</span>
      <span>Cài đặt</span>
    </a>
  </nav>
</aside>
```

#### 3.2.2 CSS Specs
```css
.sidebar {
  width: 260px;
  height: 100vh;
  background: #183B56;
  position: fixed;
  left: 0;
  top: 0;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
}

.sidebar-header {
  padding: 30px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-logo {
  height: 40px;
}

.sidebar-nav {
  flex: 1;
  padding: 20px 0;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 24px;
  color: rgba(255, 255, 255, 0.7);
  font-family: 'Open Sans', sans-serif;
  font-size: 15px;
  text-decoration: none;
  transition: all 0.2s ease;
  border-left: 3px solid transparent;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #FFFFFF;
}

.nav-item.active {
  background: rgba(244, 124, 38, 0.1);
  color: #F47C26;
  border-left-color: #F47C26;
}

.nav-icon {
  font-size: 20px;
  width: 24px;
  text-align: center;
}
```

### 3.3 Main Content Area

```css
.main-content {
  margin-left: 260px;
  min-height: 100vh;
  background: #F9FAFC;
  padding: 40px;
}

.page-title {
  font-family: 'Montserrat', sans-serif;
  font-weight: 700;
  font-size: 28px;
  color: #183B56;
  margin-bottom: 30px;
}
```

### 3.4 Khu vực 1: Profile Header Card

```html
<div class="profile-card">
  <div class="profile-header">
    <!-- Avatar Section -->
    <div class="avatar-container">
      <img src="avatar.jpg" alt="Avatar" class="avatar" />
      <button class="avatar-edit-btn">
        <span>📷</span>
      </button>
    </div>
    
    <!-- Info Section -->
    <div class="profile-info">
      <h2 class="profile-name">Nguyễn Văn A</h2>
      
      <div class="form-group">
        <label for="bio">Giới thiệu</label>
        <textarea 
          id="bio" 
          class="form-textarea" 
          rows="3"
          placeholder="Ví dụ: Mục tiêu IELTS 7.0 trong năm nay"
        >Mục tiêu: IELTS 7.0 trong năm nay</textarea>
      </div>
      
      <button class="btn-save">
        Lưu thay đổi
      </button>
    </div>
  </div>
</div>
```

**CSS Specs:**
```css
.profile-card {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  margin-bottom: 30px;
}

.profile-header {
  display: flex;
  gap: 40px;
  align-items: flex-start;
}

/* Avatar */
.avatar-container {
  position: relative;
  flex-shrink: 0;
}

.avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid #F2F4F8;
}

.avatar-edit-btn {
  position: absolute;
  bottom: 5px;
  right: 5px;
  width: 36px;
  height: 36px;
  background: #F47C26;
  border: 3px solid #FFFFFF;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 16px;
  transition: background 0.2s;
}

.avatar-edit-btn:hover {
  background: #E86F1E;
}

/* Profile Info */
.profile-info {
  flex: 1;
}

.profile-name {
  font-family: 'Montserrat', sans-serif;
  font-weight: 700;
  font-size: 24px;
  color: #183B56;
  margin-bottom: 20px;
}

.form-textarea {
  width: 100%;
  padding: 12px 16px;
  background: #F2F4F8;
  border: 2px solid transparent;
  border-radius: 8px;
  font-family: 'Open Sans', sans-serif;
  font-size: 14px;
  color: #2C3E50;
  resize: vertical;
  transition: all 0.2s ease;
}

.form-textarea:focus {
  outline: none;
  border-color: #F47C26;
  background: #FFFFFF;
}

.btn-save {
  margin-top: 20px;
  padding: 12px 32px;
  background: #F47C26;
  border: none;
  border-radius: 8px;
  font-family: 'Montserrat', sans-serif;
  font-weight: 600;
  font-size: 14px;
  color: #FFFFFF;
  cursor: pointer;
  transition: all 0.2s ease;
  float: right;
}

.btn-save:hover {
  background: #E86F1E;
}
```

### 3.5 Khu vực 2: Gamification Stats

**⚠️ Quan trọng: Hiển thị nổi bật để tăng động lực học tập!**

```html
<div class="stats-container">
  <h3 class="section-title">Thống kê học tập</h3>
  
  <div class="stats-grid">
    <!-- Level Card -->
    <div class="stat-card stat-level">
      <div class="stat-icon">🎓</div>
      <div class="stat-content">
        <div class="stat-value">A2</div>
        <div class="stat-label">Trình độ hiện tại</div>
      </div>
    </div>
    
    <!-- Streak Card -->
    <div class="stat-card stat-streak">
      <div class="stat-icon">🔥</div>
      <div class="stat-content">
        <div class="stat-value">12 Ngày</div>
        <div class="stat-label">Học liên tiếp</div>
      </div>
    </div>
    
    <!-- XP Card -->
    <div class="stat-card stat-xp">
      <div class="stat-icon">💎</div>
      <div class="stat-content">
        <div class="stat-value">1,250 XP</div>
        <div class="stat-label">Tổng điểm</div>
      </div>
    </div>
  </div>
</div>
```

**CSS Specs:**
```css
.stats-container {
  margin-bottom: 30px;
}

.section-title {
  font-family: 'Montserrat', sans-serif;
  font-weight: 700;
  font-size: 20px;
  color: #183B56;
  margin-bottom: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.stat-card {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  gap: 20px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  font-size: 48px;
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  flex-shrink: 0;
}

/* Level Card - Blue */
.stat-level .stat-icon {
  background: linear-gradient(135deg, #3498DB 0%, #2980B9 100%);
}

/* Streak Card - Orange (Brand Color) */
.stat-streak .stat-icon {
  background: linear-gradient(135deg, #F47C26 0%, #E86F1E 100%);
}

/* XP Card - Purple/Gold */
.stat-xp .stat-icon {
  background: linear-gradient(135deg, #9B59B6 0%, #8E44AD 100%);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-family: 'Montserrat', sans-serif;
  font-weight: 800;
  font-size: 28px;
  color: #183B56;
  margin-bottom: 4px;
}

.stat-label {
  font-family: 'Open Sans', sans-serif;
  font-size: 14px;
  color: #6C757D;
}

/* Responsive */
@media (max-width: 992px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
```

### 3.6 Khu vực 3: Account Settings

```html
<div class="settings-card">
  <h3 class="section-title">Thông tin tài khoản</h3>
  
  <!-- Email (Read-only) -->
  <div class="form-group">
    <label>Email</label>
    <input 
      type="email" 
      class="form-input" 
      value="user@example.com" 
      disabled
    />
    <small class="form-hint">Email không thể thay đổi</small>
  </div>
  
  <!-- Password Reset -->
  <div class="form-group">
    <label>Mật khẩu</label>
    <button class="btn-secondary">
      Gửi email đặt lại mật khẩu
    </button>
  </div>
  
  <!-- Social Links -->
  <div class="form-group">
    <label>Liên kết tài khoản</label>
    
    <div class="social-links">
      <!-- Google -->
      <div class="social-link-item">
        <div class="social-link-info">
          <img src="icon-google.svg" alt="Google" width="24" height="24" />
          <span>Google</span>
        </div>
        <span class="badge badge-success">Đã liên kết</span>
      </div>
      
      <!-- Facebook -->
      <div class="social-link-item">
        <div class="social-link-info">
          <img src="icon-facebook.svg" alt="Facebook" width="24" height="24" />
          <span>Facebook</span>
        </div>
        <span class="badge badge-muted">Chưa liên kết</span>
      </div>
    </div>
  </div>
</div>
```

**CSS Specs:**
```css
.settings-card {
  background: #FFFFFF;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.form-hint {
  display: block;
  margin-top: 6px;
  font-size: 13px;
  color: #95A5A6;
}

.btn-secondary {
  padding: 12px 24px;
  background: #FFFFFF;
  border: 2px solid #183B56;
  border-radius: 8px;
  font-family: 'Open Sans', sans-serif;
  font-weight: 600;
  font-size: 14px;
  color: #183B56;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: #183B56;
  color: #FFFFFF;
}

/* Social Links */
.social-links {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.social-link-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #F9FAFC;
  border-radius: 8px;
}

.social-link-info {
  display: flex;
  align-items: center;
  gap: 12px;
  font-family: 'Open Sans', sans-serif;
  font-weight: 600;
  font-size: 15px;
  color: #2C3E50;
}

.badge {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.badge-success {
  background: #D5F5E3;
  color: #27AE60;
}

.badge-muted {
  background: #E8EAED;
  color: #95A5A6;
}
```

---

## 4. HƯỚNG DẪN KỸ THUẬT DJANGO

### 4.1 Yêu cầu Package

```bash
# Requirements.txt
django>=4.2
django-allauth>=0.57.0
pillow>=10.0.0  # For image handling
python-decouple  # For environment variables
```

### 4.2 Setup django-allauth

**settings.py:**
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Required by allauth
    
    # Third-party
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    
    # Your apps
    'users',
    'courses',
]

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Allauth Configuration
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = 'optional'  # or 'mandatory'

# Social Login
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_QUERY_EMAIL = True

# Redirects
LOGIN_REDIRECT_URL = '/dashboard/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/login/'

# Google OAuth2
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'APP': {
            'client_id': 'YOUR_GOOGLE_CLIENT_ID',
            'secret': 'YOUR_GOOGLE_SECRET',
            'key': ''
        }
    },
    'facebook': {
        'METHOD': 'oauth2',
        'SCOPE': ['email', 'public_profile'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'FIELDS': [
            'id',
            'email',
            'name',
            'first_name',
            'last_name',
            'picture',
        ],
        'APP': {
            'client_id': 'YOUR_FACEBOOK_APP_ID',
            'secret': 'YOUR_FACEBOOK_SECRET',
            'key': ''
        }
    }
}
```

**urls.py:**
```python
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('users.urls')),
]
```

### 4.3 Custom User Model

**users/models.py:**
```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    LEVEL_CHOICES = [
        ('A1', 'Beginner'),
        ('A2', 'Elementary'),
        ('B1', 'Intermediate'),
        ('B2', 'Upper Intermediate'),
        ('C1', 'Advanced'),
    ]
    
    email = models.EmailField(unique=True)
    avatar = models.ImageField(
        upload_to='avatars/', 
        blank=True, 
        null=True
    )
    bio = models.TextField(max_length=500, blank=True)
    
    # Gamification Fields
    current_level = models.CharField(
        max_length=2, 
        choices=LEVEL_CHOICES, 
        default='A1'
    )
    xp_points = models.IntegerField(default=0)
    streak_days = models.IntegerField(default=0)
    last_active_date = models.DateField(null=True, blank=True)
    
    # Social Login Info
    google_id = models.CharField(max_length=255, blank=True, null=True)
    facebook_id = models.CharField(max_length=255, blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email
```

**Migrations:**
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4.4 Template Override

**Cấu trúc thư mục templates:**
```
templates/
├── account/
│   ├── login.html          # Override allauth login
│   ├── signup.html         # Override allauth signup
│   └── password_reset.html
└── users/
    ├── profile.html
    └── dashboard.html
```

**templates/account/login.html:**
```django
{% extends 'base.html' %}
{% load socialaccount %}

{% block content %}
<div class="auth-container">
  <!-- Branding Area -->
  <div class="auth-branding">
    <div class="branding-content">
      <img src="{% static 'images/logo-white.svg' %}" alt="Logo" class="logo">
      <h1 class="slogan">Chinh phục Tiếng Anh<br>sau 3 tháng</h1>
    </div>
  </div>
  
  <!-- Form Area -->
  <div class="auth-form-container">
    <h2 class="form-title">Chào mừng trở lại!</h2>
    
    <!-- Social Login -->
    <div class="social-login">
      <a href="{% provider_login_url 'google' %}" class="btn-social btn-google">
        <img src="{% static 'images/icon-google.svg' %}" alt="Google">
        <span>Tiếp tục với Google</span>
      </a>
      
      <a href="{% provider_login_url 'facebook' %}" class="btn-social btn-facebook">
        <img src="{% static 'images/icon-facebook.svg' %}" alt="Facebook">
        <span>Tiếp tục với Facebook</span>
      </a>
    </div>
    
    <div class="divider">
      <span>Hoặc đăng nhập bằng Email</span>
    </div>
    
    <!-- Email/Password Form -->
    <form method="post" class="auth-form">
      {% csrf_token %}
      
      <div class="form-group">
        <label for="id_login">Email</label>
        <input type="email" name="login" id="id_login" class="form-input" required>
      </div>
      
      <div class="form-group">
        <label for="id_password">Mật khẩu</label>
        <input type="password" name="password" id="id_password" class="form-input" required>
      </div>
      
      <button type="submit" class="btn-primary">ĐĂNG NHẬP</button>
    </form>
    
    <div class="auth-footer">
      <a href="{% url 'account_reset_password' %}" class="link-secondary">
        Quên mật khẩu?
      </a>
      <p class="signup-prompt">
        Chưa có tài khoản? 
        <a href="{% url 'account_signup' %}" class="link-primary">Đăng ký ngay</a>
      </p>
    </div>
  </div>
</div>
{% endblock %}
```

### 4.5 Signal Handlers (Auto-populate Social Login Data)

**users/signals.py:**
```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.socialaccount.signals import pre_social_login
from allauth.socialaccount.models import SocialAccount
from .models import User

@receiver(pre_social_login)
def populate_user_from_social(sender, request, sociallogin, **kwargs):
    """
    Tự động lấy Avatar và thông tin từ Google/Facebook
    """
    user = sociallogin.user
    
    if sociallogin.account.provider == 'google':
        data = sociallogin.account.extra_data
        user.google_id = data.get('id')
        
        # Lấy avatar từ Google
        picture_url = data.get('picture')
        if picture_url and not user.avatar:
            # Download và save avatar
            # (Implement download logic here)
            pass
            
    elif sociallogin.account.provider == 'facebook':
        data = sociallogin.account.extra_data
        user.facebook_id = data.get('id')
        
        # Lấy avatar từ Facebook
        picture_data = data.get('picture', {}).get('data', {})
        picture_url = picture_data.get('url')
        if picture_url and not user.avatar:
            # Download và save avatar
            pass
    
    user.save()

@receiver(post_save, sender=User)
def handle_new_user(sender, instance, created, **kwargs):
    """
    User mới -> Redirect tới Onboarding Quiz
    """
    if created and instance.current_level == 'A1':
        # Set flag để redirect tới quiz
        instance.needs_onboarding = True
        instance.save()
```

**users/apps.py:**
```python
from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    
    def ready(self):
        import users.signals  # Import signals
```

### 4.6 Views

**users/views.py:**
```python
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import User
from .forms import ProfileUpdateForm

@login_required
def profile_view(request):
    """
    Trang Profile cá nhân
    """
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    # Check social account links
    has_google = request.user.google_id is not None
    has_facebook = request.user.facebook_id is not None
    
    context = {
        'form': form,
        'has_google': has_google,
        'has_facebook': has_facebook,
    }
    return render(request, 'users/profile.html', context)

@login_required
def dashboard_view(request):
    """
    Dashboard - Check nếu user mới cần làm Onboarding Quiz
    """
    if hasattr(request.user, 'needs_onboarding') and request.user.needs_onboarding:
        return redirect('onboarding_quiz')
    
    return render(request, 'users/dashboard.html')
```

### 4.7 Forms

**users/forms.py:**
```python
from django import forms
from .models import User

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Ví dụ: Mục tiêu IELTS 7.0 trong năm nay'
            }),
        }
```

### 4.8 URLs

**users/urls.py:**
```python
from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
]
```

---

## 5. CHECKLIST CHO DEVELOPER

### Frontend Tasks
- [ ] Cài đặt Google Fonts: Montserrat & Open Sans
- [ ] Implement CSS Variables theo color palette
- [ ] Code màn hình Login/Signup (Split Screen)
- [ ] Code Social Login Buttons (Google/Facebook)
- [ ] Code Sidebar Navigation
- [ ] Code Profile Header Card (Avatar upload)
- [ ] Code Gamification Stats Cards (Level/Streak/XP)
- [ ] Code Account Settings Section
- [ ] Test responsive trên mobile/tablet
- [ ] Verify hover effects và transitions

### Backend Tasks
- [ ] Cài đặt `django-allauth` và dependencies
- [ ] Config OAuth2 cho Google & Facebook
- [ ] Tạo Custom User Model với gamification fields
- [ ] Run migrations
- [ ] Override allauth templates
- [ ] Implement signals cho social login
- [ ] Tạo Profile view & form
- [ ] Test flow: Đăng ký → Login → Dashboard → Profile
- [ ] Test Social Login flow
- [ ] Verify avatar upload từ Google/Facebook

### Integration Tasks
- [ ] Connect frontend CSS với Django templates
- [ ] Verify form validation & error messages
- [ ] Test redirect logic (Login → Dashboard/Onboarding)
- [ ] Test streak & XP display
- [ ] Test avatar upload & display
- [ ] Performance testing
- [ ] Cross-browser testing

---

## 6. GHI CHÚ BẢO MẬT

### OAuth2 Setup
1. **Google Console:**
   - Tạo project tại: https://console.cloud.google.com
   - Enable Google+ API
   - Tạo OAuth2 credentials
   - Thêm redirect URI: `http://localhost:8000/accounts/google/login/callback/`

2. **Facebook Developers:**
   - Tạo app tại: https://developers.facebook.com
   - Add Facebook Login product
   - Thêm redirect URI: `http://localhost:8000/accounts/facebook/login/callback/`

3. **Environment Variables:**
   ```bash
   # .env file
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_SECRET=your_google_secret
   FACEBOOK_APP_ID=your_facebook_app_id
   FACEBOOK_SECRET=your_facebook_secret
   SECRET_KEY=your_django_secret_key
   ```

---

## 7. THAM KHẢO THÊM

- **Django Allauth Docs:** https://django-allauth.readthedocs.io/
- **Google OAuth2 Guide:** https://developers.google.com/identity/protocols/oauth2
- **Facebook Login Guide:** https://developers.facebook.com/docs/facebook-login/
- **CSS Grid Guide:** https://css-tricks.com/snippets/css/complete-guide-grid/
- **Flexbox Guide:** https://css-tricks.com/snippets/css/a-guide-to-flexbox/

---

**Liên hệ hỗ trợ:** Nếu có vấn đề khi implement, vui lòng liên hệ Product Manager/Tech Lead.

**Version History:**
- v1.0 (07/12/2025): Initial release
