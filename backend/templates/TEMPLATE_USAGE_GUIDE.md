# Hướng Dẫn Sử Dụng Template Architecture

## Tổng Quan

Hệ thống template được thiết kế theo chuẩn Django với tính năng kế thừa (template inheritance), giúp:
- Dễ bảo trì và mở rộng
- Nhất quán về giao diện
- Tái sử dụng code hiệu quả
- Tách biệt concerns rõ ràng

---

## Cấu Trúc Thư Mục

```
backend/
├── templates/
│   ├── base/
│   │   ├── _base.html              # Base template gốc
│   │   ├── _base_public.html       # Base cho trang public
│   │   ├── _base_admin.html        # Base cho trang admin
│   │   └── _base_auth.html         # Base cho trang auth
│   │
│   ├── components/
│   │   ├── _navbar_public.html     # Navbar public
│   │   ├── _navbar_admin.html      # Navbar admin
│   │   ├── _sidebar_admin.html     # Sidebar admin
│   │   └── _footer_public.html     # Footer public
│   │
│   └── [app_name]/                 # Templates theo app
│       ├── list.html
│       ├── detail.html
│       └── form.html
│
├── static/
│   ├── css/
│   │   ├── base.css                # CSS variables, reset, utilities
│   │   ├── components.css          # UI components
│   │   ├── public.css              # Public pages styles
│   │   ├── admin.css               # Admin pages styles
│   │   └── auth.css                # Auth pages styles
│   │
│   ├── js/
│   │   ├── config.js               # App configuration
│   │   ├── api.js                  # API client
│   │   ├── auth.js                 # Authentication
│   │   ├── utils.js                # Utility functions
│   │   └── admin.js                # Admin panel functions
│   │
│   └── images/
│       └── ...
```

---

## Cách Sử Dụng Templates

### 1. Tạo Trang Public

```django
{% extends "base/_base_public.html" %}

{% block title %}Tiêu đề trang{% endblock %}
{% block meta_description %}Mô tả trang{% endblock %}

{% block page_css %}
<style>
    /* CSS riêng cho trang này (nếu cần) */
</style>
{% endblock %}

{% block content %}
<div class="container">
    <!-- Nội dung trang -->
    <h1>Heading</h1>
    <p>Content here...</p>
</div>
{% endblock %}

{% block page_js %}
<script>
    // JavaScript riêng cho trang này
</script>
{% endblock %}
```

### 2. Tạo Trang Admin

```django
{% extends "base/_base_admin.html" %}

{% block title %}Tiêu đề Admin{% endblock %}

{% block breadcrumb %}
<nav class="admin-breadcrumb">
    <a href="{% url 'admin:dashboard' %}">Dashboard</a>
    <span class="separator">/</span>
    <span class="current">Tên trang</span>
</nav>
{% endblock %}

{% block page_header %}
<div class="d-flex justify-content-between align-items-center">
    <div>
        <h1 class="page-title">Quản lý XYZ</h1>
        <p class="page-subtitle">Mô tả ngắn</p>
    </div>
    <div class="page-header-actions">
        <button class="btn btn-primary-orange">
            <i class="fas fa-plus me-2"></i>Thêm mới
        </button>
    </div>
</div>
{% endblock %}

{% block content %}
<!-- Nội dung trang admin -->
<div class="admin-table-wrapper">
    <!-- Table content -->
</div>
{% endblock %}

{% block modal_content %}
<!-- Modals nếu cần -->
{% endblock %}

{% block page_js %}
<script>
    // JavaScript riêng
</script>
{% endblock %}
```

### 3. Tạo Trang Auth

```django
{% extends "base/_base_auth.html" %}

{% block title %}Đăng nhập{% endblock %}

{% block auth_content %}
<div class="auth-header">
    <h1 class="auth-title">Đăng nhập</h1>
    <p class="auth-subtitle">Chào mừng bạn quay trở lại!</p>
</div>

<form class="auth-form" id="loginForm">
    <div class="form-group">
        <label for="email">Email</label>
        <input type="email" class="form-control" id="email" required>
    </div>
    
    <div class="form-group">
        <label for="password">Mật khẩu</label>
        <div class="password-input-wrapper">
            <input type="password" class="form-control" id="password" required>
            <button type="button" class="password-toggle">
                <i class="fas fa-eye"></i>
            </button>
        </div>
    </div>
    
    <button type="submit" class="btn btn-primary-orange auth-submit">
        Đăng nhập
    </button>
</form>
{% endblock %}

{% block auth_footer %}
<p>Chưa có tài khoản? <a href="{% url 'signup' %}">Đăng ký ngay</a></p>
{% endblock %}
```

---

## CSS Classes Có Sẵn

### Buttons

```html
<!-- Primary Orange -->
<button class="btn btn-primary-orange">Primary</button>
<button class="btn btn-primary-orange-outline">Outline</button>

<!-- Primary Blue -->
<button class="btn btn-primary-blue">Blue</button>
<button class="btn btn-primary-blue-outline">Outline</button>

<!-- Sizes -->
<button class="btn btn-primary-orange btn-sm">Small</button>
<button class="btn btn-primary-orange btn-lg">Large</button>

<!-- Loading state -->
<button class="btn btn-primary-orange btn-loading" disabled>
    <span class="spinner-border spinner-border-sm me-2"></span>
    Loading...
</button>
```

### Cards

```html
<!-- Stats Card -->
<div class="stats-card">
    <div class="stats-icon blue">
        <i class="fas fa-users"></i>
    </div>
    <div class="stats-content">
        <h3 class="stats-value">1,234</h3>
        <p class="stats-label">Total Users</p>
    </div>
</div>

<!-- Custom Card -->
<div class="card custom-card">
    <div class="card-header">
        <h5 class="card-title">Title</h5>
    </div>
    <div class="card-body">Content</div>
    <div class="card-footer">Footer</div>
</div>
```

### Forms

```html
<div class="form-group">
    <label class="form-label">Label</label>
    <input type="text" class="form-control custom-input">
    <div class="form-text">Helper text</div>
</div>

<!-- Validation states -->
<input class="form-control is-valid">
<input class="form-control is-invalid">
<div class="invalid-feedback">Error message</div>
<div class="valid-feedback">Success message</div>
```

### Alerts

```html
<div class="alert alert-success custom-alert">
    <i class="fas fa-check-circle alert-icon"></i>
    <div>
        <strong>Success!</strong> Message here.
    </div>
</div>

<!-- Other types: alert-danger, alert-warning, alert-info -->
```

### Badges

```html
<span class="badge badge-success">Active</span>
<span class="badge badge-danger">Error</span>
<span class="badge badge-warning">Pending</span>
<span class="badge badge-info">Info</span>
```

### Avatars

```html
<div class="avatar avatar-sm">
    <img src="..." alt="User">
</div>
<div class="avatar avatar-md">...</div>
<div class="avatar avatar-lg">...</div>
<div class="avatar avatar-xl">...</div>
```

---

## JavaScript Utilities

### API Calls

```javascript
// GET request
const users = await ApiClient.get('/users/');

// POST request
const result = await ApiClient.post('/users/', { name: 'John' });

// PUT request
await ApiClient.put('/users/1/', { name: 'Updated' });

// DELETE request
await ApiClient.delete('/users/1/');

// Upload file
const formData = new FormData();
formData.append('file', fileInput.files[0]);
await ApiClient.upload('/upload/', formData);
```

### Authentication

```javascript
// Login
const result = await Auth.login(email, password);
if (result.success) {
    window.location.href = '/dashboard/';
} else {
    Utils.showToast(result.error, 'error');
}

// Register
const result = await Auth.register({
    email: 'user@example.com',
    password: 'Password123!',
    full_name: 'Nguyen Van A',
});

// Logout
await Auth.logout();

// Check auth status
if (Auth.isAuthenticated()) {
    const user = Auth.getCurrentUser();
}

// Password validation
const validation = Auth.validatePassword('mypassword');
console.log(validation.strength); // 'weak', 'fair', 'good', 'strong'
```

### Utilities

```javascript
// Toast notifications
Utils.showToast('Success!', 'success');
Utils.showToast('Error occurred', 'error');
Utils.showToast('Warning!', 'warning');
Utils.showToast('Info message', 'info');

// Confirmation modal
const confirmed = await Utils.confirm('Are you sure?', {
    title: 'Confirm Delete',
    type: 'danger',
    confirmText: 'Delete',
    cancelText: 'Cancel',
});

// Format helpers
Utils.formatNumber(1234567);     // "1,234,567"
Utils.formatCurrency(500000);    // "500.000 ₫"
Utils.formatDate(new Date());    // "25/01/2025"
Utils.timeAgo('2025-01-24');     // "1 ngày trước"

// Debounce & Throttle
const debouncedSearch = Utils.debounce((query) => {
    // Search logic
}, 300);

// Copy to clipboard
await Utils.copyToClipboard('Text to copy');

// Scroll to element
Utils.scrollTo('#section', 100); // 100px offset for navbar
```

---

## CSS Variables (Custom Properties)

Có thể override trong file CSS riêng:

```css
:root {
    /* Colors */
    --primary-orange: #F47C26;
    --primary-dark: #183B56;
    --primary-blue: #2C5282;
    
    /* Typography */
    --font-heading: 'Montserrat', sans-serif;
    --font-body: 'Open Sans', sans-serif;
    
    /* Spacing */
    --spacing-xs: 4px;
    --spacing-sm: 8px;
    --spacing-md: 16px;
    --spacing-lg: 24px;
    --spacing-xl: 32px;
    
    /* Shadows */
    --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
    --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
    
    /* Border Radius */
    --radius-sm: 4px;
    --radius-md: 8px;
    --radius-lg: 12px;
    --radius-full: 9999px;
}
```

---

## Conventions & Best Practices

### 1. Đặt tên Templates

```
[app_name]/
├── [model]_list.html       # Danh sách
├── [model]_detail.html     # Chi tiết
├── [model]_form.html       # Form tạo/sửa
├── [model]_confirm_delete.html  # Xác nhận xóa
└── partials/               # Partial templates
    └── _[partial_name].html
```

### 2. Đặt tên CSS Classes

```css
/* Component-based naming */
.card { }
.card-header { }
.card-body { }
.card-footer { }

/* State modifiers */
.is-active { }
.is-loading { }
.is-disabled { }

/* Utility classes */
.text-primary { }
.bg-light { }
.shadow-md { }
```

### 3. JavaScript Modules

```javascript
// Namespace pattern
const MyModule = {
    init() {
        this.bindEvents();
    },
    
    bindEvents() {
        // Event listeners
    },
    
    handleAction() {
        // Logic
    },
};

// Initialize when DOM ready
document.addEventListener('DOMContentLoaded', () => {
    MyModule.init();
});
```

---

## Vue.js Integration (CDN)

Cho các trang cần reactive UI:

```django
{% block content %}
<div id="app">
    <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary"></div>
    </div>
    
    <div v-else>
        <div v-for="item in items" :key="item.id" class="card mb-3">
            <div class="card-body">
                <h5>{{ item.title }}</h5>
                <p>{{ item.description }}</p>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block page_js %}
<script>
const { createApp, ref, onMounted } = Vue;

createApp({
    setup() {
        const loading = ref(true);
        const items = ref([]);
        
        onMounted(async () => {
            try {
                items.value = await ApiClient.get('/api/items/');
            } finally {
                loading.value = false;
            }
        });
        
        return { loading, items };
    }
}).mount('#app');
</script>
{% endblock %}
```

---

## Troubleshooting

### Static files không load

```bash
# Kiểm tra cấu hình STATICFILES_DIRS trong settings
# Chạy collectstatic
python manage.py collectstatic

# Kiểm tra STATIC_URL và STATIC_ROOT
```

### Template không tìm thấy

```python
# Kiểm tra TEMPLATES['DIRS'] trong settings
TEMPLATES = [
    {
        'DIRS': [BASE_DIR / 'templates'],
        # ...
    }
]
```

### CSS không apply

```html
<!-- Đảm bảo thứ tự load CSS đúng -->
{% load static %}
<link rel="stylesheet" href="{% static 'css/base.css' %}">
<link rel="stylesheet" href="{% static 'css/components.css' %}">
<link rel="stylesheet" href="{% static 'css/public.css' %}">
<!-- Page-specific CSS -->
{% block page_css %}{% endblock %}
```

---

## Liên Hệ & Hỗ Trợ

Nếu gặp vấn đề hoặc cần hỗ trợ, vui lòng:
1. Kiểm tra documentation này trước
2. Xem các ví dụ trong `templates/examples/`
3. Liên hệ team lead hoặc tạo issue trên Git
