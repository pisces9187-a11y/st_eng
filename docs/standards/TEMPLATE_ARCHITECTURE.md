# 🏗️ Kiến Trúc Template - EnglishMaster

## 📋 Tổng Quan

Hệ thống sử dụng **Django Template Inheritance** kết hợp **Bootstrap 5** và **Vue.js 3 CDN** để tạo ra giao diện nhất quán, dễ bảo trì.

---

## 🎨 Design System

### Color Palette

```css
/* Primary Colors */
--primary-orange: #F47C26;      /* CTA buttons, highlights */
--primary-dark: #183B56;        /* Headings, sidebar */
--primary-blue: #007BFF;        /* Links, info */

/* Neutral Colors */
--text-dark: #2C2C2C;           /* Main text */
--text-muted: #6C757D;          /* Secondary text */
--text-light: #ADB5BD;          /* Placeholder */
--bg-light: #F9FAFC;            /* Page background */
--bg-white: #FFFFFF;            /* Card background */
--border-color: #E8ECF0;        /* Borders */

/* Status Colors */
--success: #28A745;
--warning: #FFC107;
--danger: #DC3545;
--info: #17A2B8;
```

### Typography

```css
/* Fonts */
--font-heading: 'Montserrat', sans-serif;  /* 700, 800 */
--font-body: 'Open Sans', sans-serif;      /* 400, 600 */

/* Sizes */
--h1: 2.5rem;    /* 40px */
--h2: 2rem;      /* 32px */
--h3: 1.5rem;    /* 24px */
--h4: 1.25rem;   /* 20px */
--h5: 1rem;      /* 16px */
--body: 1rem;    /* 16px */
--small: 0.875rem; /* 14px */
```

### Spacing

```css
--spacing-xs: 0.25rem;   /* 4px */
--spacing-sm: 0.5rem;    /* 8px */
--spacing-md: 1rem;      /* 16px */
--spacing-lg: 1.5rem;    /* 24px */
--spacing-xl: 2rem;      /* 32px */
--spacing-xxl: 3rem;     /* 48px */
```

### Border Radius

```css
--radius-sm: 4px;
--radius-md: 8px;
--radius-lg: 12px;
--radius-xl: 16px;
--radius-full: 50%;
```

### Shadows

```css
--shadow-sm: 0 2px 4px rgba(0,0,0,0.05);
--shadow-md: 0 4px 12px rgba(0,0,0,0.1);
--shadow-lg: 0 8px 24px rgba(0,0,0,0.15);
--shadow-orange: 0 4px 16px rgba(244,124,38,0.3);
```

---

## 📁 Cấu Trúc Thư Mục

```
backend/
├── templates/
│   ├── base/
│   │   ├── _base.html              # Base tổng (head, scripts)
│   │   ├── _base_public.html       # Base cho trang Public
│   │   ├── _base_admin.html        # Base cho trang Admin
│   │   └── _base_auth.html         # Base cho Auth pages
│   │
│   ├── components/
│   │   ├── _navbar_public.html     # Navbar cho Public
│   │   ├── _navbar_admin.html      # Navbar cho Admin
│   │   ├── _sidebar_admin.html     # Sidebar Admin
│   │   ├── _footer_public.html     # Footer Public
│   │   ├── _alerts.html            # Alert messages
│   │   ├── _pagination.html        # Pagination
│   │   └── _modal.html             # Modal template
│   │
│   ├── public/                     # Trang người dùng
│   │   ├── home/
│   │   │   └── index.html
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   ├── signup.html
│   │   │   └── password_reset.html
│   │   ├── dashboard/
│   │   │   └── index.html
│   │   ├── lessons/
│   │   │   ├── library.html
│   │   │   └── player.html
│   │   └── profile/
│   │       └── index.html
│   │
│   └── admin_custom/               # Trang Admin (không dùng Django Admin)
│       ├── dashboard/
│       │   └── index.html
│       ├── lessons/
│       │   ├── list.html
│       │   └── editor.html         # Vue.js Sentence Editor
│       ├── users/
│       │   └── list.html
│       └── reports/
│           └── index.html
│
├── static/
│   ├── css/
│   │   ├── base.css                # Variables, reset, utilities
│   │   ├── components.css          # Buttons, cards, forms...
│   │   ├── public.css              # Styles cho Public
│   │   └── admin.css               # Styles cho Admin
│   │
│   ├── js/
│   │   ├── config.js               # API config
│   │   ├── api.js                  # API helper functions
│   │   ├── auth.js                 # Authentication
│   │   ├── utils.js                # Utilities
│   │   └── components/
│   │       ├── sentence-editor.js  # Vue component
│   │       └── flashcard.js        # Vue component
│   │
│   └── images/
│       ├── logo.svg
│       ├── logo-white.svg
│       └── icons/
```

---

## 🧬 Template Inheritance

### Hierarchy

```
_base.html
├── _base_public.html
│   ├── public/home/index.html
│   ├── public/dashboard/index.html
│   └── public/lessons/library.html
│
├── _base_admin.html
│   ├── admin_custom/dashboard/index.html
│   └── admin_custom/lessons/editor.html
│
└── _base_auth.html
    ├── public/auth/login.html
    └── public/auth/signup.html
```

---

## 📄 Template Examples

### 1. `_base.html` - Base Template

```html
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}EnglishMaster{% endblock %}</title>
    
    <!-- Favicon -->
    <link rel="icon" type="image/svg+xml" href="{% static 'images/favicon.svg' %}">
    
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700;800&family=Open+Sans:wght@400;600&display=swap" rel="stylesheet">
    
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    
    <!-- Base CSS -->
    <link rel="stylesheet" href="{% static 'css/base.css' %}">
    
    {% block extra_css %}{% endblock %}
</head>
<body class="{% block body_class %}{% endblock %}">
    {% block body %}{% endblock %}
    
    <!-- Bootstrap 5 JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- Vue.js 3 CDN -->
    <script src="https://unpkg.com/vue@3/dist/vue.global.prod.js"></script>
    
    <!-- Base JS -->
    <script src="{% static 'js/config.js' %}"></script>
    <script src="{% static 'js/api.js' %}"></script>
    
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### 2. `_base_public.html` - Public Base

```html
{% extends "base/_base.html" %}
{% load static %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/public.css' %}">
{% endblock %}

{% block body %}
<div id="app">
    <!-- Navbar -->
    {% include "components/_navbar_public.html" %}
    
    <!-- Main Content -->
    <main class="main-content">
        {% block content %}{% endblock %}
    </main>
    
    <!-- Footer -->
    {% include "components/_footer_public.html" %}
</div>
{% endblock %}

{% block extra_js %}
<script src="{% static 'js/auth.js' %}"></script>
{% block page_js %}{% endblock %}
{% endblock %}
```

### 3. `_base_admin.html` - Admin Base

```html
{% extends "base/_base.html" %}
{% load static %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/admin.css' %}">
{% endblock %}

{% block body_class %}admin-layout{% endblock %}

{% block body %}
<div id="admin-app">
    <!-- Sidebar -->
    {% include "components/_sidebar_admin.html" %}
    
    <!-- Main Content -->
    <div class="admin-main">
        <!-- Top Navbar -->
        {% include "components/_navbar_admin.html" %}
        
        <!-- Page Content -->
        <div class="admin-content">
            {% block content %}{% endblock %}
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="{% static 'js/auth.js' %}"></script>
{% block page_js %}{% endblock %}
{% endblock %}
```

### 4. Example Page - Dashboard

```html
{% extends "base/_base_public.html" %}
{% load static %}

{% block title %}Dashboard - EnglishMaster{% endblock %}

{% block content %}
<div class="container py-4">
    <!-- Welcome Section -->
    <div class="welcome-card mb-4">
        <h1 class="welcome-title">Chào mừng trở lại, <span id="user-name">{{ user.first_name }}</span>! 👋</h1>
        <p class="welcome-subtitle">Tiếp tục hành trình học tập của bạn</p>
    </div>
    
    <!-- Stats Cards -->
    <div class="row g-4 mb-4">
        <div class="col-md-4">
            <div class="stats-card">
                <i class="fas fa-trophy stats-icon text-warning"></i>
                <div class="stats-number" id="xp-points">0</div>
                <div class="stats-label">Tổng XP</div>
            </div>
        </div>
        <!-- More stats... -->
    </div>
    
    <!-- Learning Path -->
    <div class="learning-path-section">
        {% block learning_path %}{% endblock %}
    </div>
</div>
{% endblock %}

{% block page_js %}
<script>
const { createApp } = Vue;

createApp({
    data() {
        return {
            user: null,
            stats: {}
        }
    },
    async mounted() {
        await this.loadDashboard();
    },
    methods: {
        async loadDashboard() {
            // Load data from API
        }
    }
}).mount('#app');
</script>
{% endblock %}
```

---

## 🎯 Component Classes (Bootstrap 5 Extended)

### Buttons

```css
/* Primary CTA */
.btn-primary-orange {
    background: var(--primary-orange);
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: var(--radius-md);
    font-weight: 600;
    transition: all 0.3s ease;
}

.btn-primary-orange:hover {
    background: #e06b1f;
    transform: translateY(-2px);
    box-shadow: var(--shadow-orange);
}

/* Outline */
.btn-outline-orange {
    background: transparent;
    color: var(--primary-orange);
    border: 2px solid var(--primary-orange);
}
```

### Cards

```css
.card-custom {
    background: var(--bg-white);
    border: none;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
    transition: all 0.3s ease;
}

.card-custom:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-md);
}
```

### Forms

```css
.form-control-custom {
    border: 2px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 12px 16px;
    font-size: 1rem;
    transition: all 0.2s ease;
}

.form-control-custom:focus {
    border-color: var(--primary-orange);
    box-shadow: 0 0 0 3px rgba(244, 124, 38, 0.15);
}
```

---

## 🔧 Vue.js Components

### Sentence Editor (Admin)

```javascript
// static/js/components/sentence-editor.js
const SentenceEditor = {
    template: `
        <div class="sentence-editor">
            <div class="editor-toolbar">
                <button @click="highlightWord('noun')" class="btn btn-sm btn-outline-primary">Noun</button>
                <button @click="highlightWord('verb')" class="btn btn-sm btn-outline-success">Verb</button>
                <button @click="highlightWord('adjective')" class="btn btn-sm btn-outline-warning">Adj</button>
            </div>
            <div 
                class="editor-content"
                contenteditable="true"
                @mouseup="onTextSelect"
                v-html="content"
            ></div>
        </div>
    `,
    props: ['initialContent'],
    data() {
        return {
            content: this.initialContent,
            selectedText: null
        }
    },
    methods: {
        onTextSelect() {
            const selection = window.getSelection();
            this.selectedText = selection.toString();
        },
        highlightWord(type) {
            // Highlight logic
        }
    }
};
```

---

## 📱 Responsive Breakpoints

```css
/* Mobile First */
/* xs: 0 - 575px */
/* sm: 576px - 767px */
/* md: 768px - 991px */
/* lg: 992px - 1199px */
/* xl: 1200px - 1399px */
/* xxl: 1400px+ */

@media (max-width: 767px) {
    .sidebar { display: none; }
    .main-content { margin-left: 0; }
}
```

---

## ✅ Checklist Triển Khai

### Phase 1: Setup
- [ ] Cấu hình Django static files
- [ ] Tạo base templates
- [ ] Tạo CSS variables và utilities
- [ ] Setup Vue.js CDN

### Phase 2: Public Pages
- [ ] Home page
- [ ] Auth pages (login, signup, reset)
- [ ] Dashboard
- [ ] Lesson library & player
- [ ] Profile

### Phase 3: Admin Pages
- [ ] Admin dashboard
- [ ] Lesson editor với Vue.js
- [ ] User management
- [ ] Reports

### Phase 4: Components
- [ ] Sentence Editor (Vue)
- [ ] Flashcard component
- [ ] Quiz component
- [ ] Progress tracker

---

## 🚀 Lệnh Triển Khai

```bash
# Collect static files
python manage.py collectstatic

# Run server
python manage.py runserver
```

---

## 📝 Notes

1. **Không dùng Django Admin Form** cho việc edit lesson vì UX kém
2. **Vue.js CDN** được sử dụng thay vì build riêng để đơn giản hóa
3. **API-first approach**: Frontend gọi Django REST API
4. **Mobile-first CSS**: Thiết kế responsive từ mobile lên
5. **BEM naming convention** cho CSS classes tùy chỉnh

