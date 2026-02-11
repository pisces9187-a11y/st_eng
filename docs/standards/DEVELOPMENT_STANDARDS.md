# 📐 QUY CHUẨN PHÁT TRIỂN - ENGLISH LEARNING PLATFORM

**Version:** 1.0.0  
**Last Updated:** December 7, 2025  
**Status:** MANDATORY - Bắt buộc tuân thủ cho TẤT CẢ các trang

---

## 🎨 HỆ THỐNG MÀU (COLOR SYSTEM)

### **CSS Variables - Khai báo trong `assets/css/theme.css`**

```css
:root {
    /* PRIMARY COLORS - Brand Identity */
    --color-primary: #F47C26;           /* Energetic Orange */
    --color-primary-dark: #D35400;      /* Orange Hover State */
    --color-primary-light: #FFB380;     /* Orange Light Tint */
    
    /* SECONDARY COLORS - Professional Balance */
    --color-secondary: #183B56;         /* Deep Ocean Blue */
    --color-secondary-dark: #0F2538;    /* Navy Dark */
    --color-secondary-light: #2E5F7F;   /* Blue Light Tint */
    
    /* BACKGROUND COLORS - Eye-friendly */
    --color-bg-main: #F9FAFC;           /* Soft White Blue */
    --color-bg-white: #FFFFFF;          /* Pure White for Cards */
    --color-bg-dark: #2C3E50;           /* Dark Background */
    
    /* TEXT COLORS - Readability */
    --color-text-primary: #2C3E50;      /* Charcoal Gray - Body Text */
    --color-text-secondary: #57606F;    /* Neutral Gray - Subtext */
    --color-text-light: #95A5A6;        /* Light Gray - Placeholder */
    --color-text-white: #FFFFFF;        /* White Text */
    
    /* SEMANTIC COLORS - User Feedback */
    --color-success: #2ECC71;           /* Green - Correct Answer */
    --color-success-bg: #EAFAF1;        /* Green Light Background */
    --color-error: #E74C3C;             /* Red - Wrong Answer */
    --color-error-bg: #FADBD8;          /* Red Light Background */
    --color-warning: #F39C12;           /* Yellow - Warning */
    --color-info: #3498DB;              /* Blue - Information */
    
    /* BORDER & DIVIDER */
    --color-border: #E0E6ED;            /* Light Gray Border */
    --color-divider: #DFE6E9;           /* Divider Line */
    
    /* SHADOWS */
    --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.08);
    --shadow-lg: 0 10px 30px rgba(0, 0, 0, 0.12);
    --shadow-xl: 0 20px 60px rgba(0, 0, 0, 0.15);
}
```

### **Quy tắc 60-30-10**

| Tỷ lệ | Màu | Áp dụng |
|-------|-----|---------|
| **60%** | `--color-bg-main` (#F9FAFC) | Nền chính toàn trang |
| **30%** | `--color-secondary` (#183B56) | Header, Footer, Tiêu đề |
| **10%** | `--color-primary` (#F47C26) | CTA Buttons, Icons, Highlights |

---

## 🔤 HỆ THỐNG TYPOGRAPHY

### **Font Import - Đặt trong `<head>` mọi trang**

```html
<!-- Google Fonts: Montserrat + Open Sans -->
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700;800&family=Open+Sans:wght@400;500;600&display=swap" rel="stylesheet">
```

### **CSS Font Variables**

```css
:root {
    /* FONT FAMILIES */
    --font-heading: 'Montserrat', sans-serif;
    --font-body: 'Open Sans', sans-serif;
    
    /* FONT SIZES - Mobile First */
    --font-size-xs: 0.75rem;    /* 12px */
    --font-size-sm: 0.875rem;   /* 14px */
    --font-size-base: 1rem;     /* 16px - MINIMUM */
    --font-size-lg: 1.125rem;   /* 18px */
    --font-size-xl: 1.25rem;    /* 20px */
    --font-size-2xl: 1.5rem;    /* 24px */
    --font-size-3xl: 1.875rem;  /* 30px */
    --font-size-4xl: 2.25rem;   /* 36px */
    --font-size-5xl: 3rem;      /* 48px */
    
    /* FONT WEIGHTS */
    --font-weight-regular: 400;
    --font-weight-medium: 500;
    --font-weight-semibold: 600;
    --font-weight-bold: 700;
    --font-weight-extrabold: 800;
    
    /* LINE HEIGHTS - Critical for Readability */
    --line-height-tight: 1.2;   /* Headings */
    --line-height-normal: 1.5;  /* UI Elements */
    --line-height-relaxed: 1.6; /* Body Text (MUST) */
    --line-height-loose: 1.8;   /* Long Reading */
}
```

### **Typography Rules**

| Element | Font Family | Weight | Size | Line Height | Color |
|---------|-------------|--------|------|-------------|-------|
| **H1** | Montserrat | 700/800 | 2.25rem (36px) | 1.2 | --color-secondary |
| **H2** | Montserrat | 700 | 1.875rem (30px) | 1.2 | --color-secondary |
| **H3** | Montserrat | 700 | 1.5rem (24px) | 1.2 | --color-secondary |
| **H4** | Montserrat | 600 | 1.25rem (20px) | 1.2 | --color-text-primary |
| **Body (p)** | Open Sans | 400 | 1rem (16px) | 1.6 | --color-text-primary |
| **Small** | Open Sans | 400 | 0.875rem (14px) | 1.5 | --color-text-secondary |
| **Button** | Montserrat | 600 | 1rem (16px) | 1.5 | --color-text-white |

### **CSS Implementation**

```css
/* HEADINGS */
h1, h2, h3, h4, h5, h6 {
    font-family: var(--font-heading);
    color: var(--color-secondary);
    line-height: var(--line-height-tight);
    margin-bottom: 1rem;
}

h1 { font-size: var(--font-size-4xl); font-weight: var(--font-weight-bold); }
h2 { font-size: var(--font-size-3xl); font-weight: var(--font-weight-bold); }
h3 { font-size: var(--font-size-2xl); font-weight: var(--font-weight-bold); }
h4 { font-size: var(--font-size-xl); font-weight: var(--font-weight-semibold); }

/* BODY TEXT - CRITICAL */
body {
    font-family: var(--font-body);
    font-size: var(--font-size-base);  /* MINIMUM 16px */
    line-height: var(--line-height-relaxed);  /* MUST 1.6 */
    color: var(--color-text-primary);
    background-color: var(--color-bg-main);
}

p, li, span {
    font-family: var(--font-body);
    font-weight: var(--font-weight-regular);
    line-height: var(--line-height-relaxed);
}

/* BUTTONS */
.btn {
    font-family: var(--font-heading);
    font-weight: var(--font-weight-semibold);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
```

---

## 📦 BOOTSTRAP 5 CONFIGURATION

### **CDN Links - Đặt trong `<head>`**

```html
<!-- Bootstrap 5.3.0 CSS -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

<!-- Font Awesome 6.4.0 -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

<!-- Custom Theme CSS -->
<link rel="stylesheet" href="../assets/css/theme.css">
```

### **Bootstrap Overrides**

```css
/* BOOTSTRAP OVERRIDES - Trong theme.css */

/* Primary Color Override */
.btn-primary {
    background-color: var(--color-primary);
    border-color: var(--color-primary);
    color: var(--color-text-white);
}

.btn-primary:hover {
    background-color: var(--color-primary-dark);
    border-color: var(--color-primary-dark);
}

/* Secondary Color Override */
.btn-secondary {
    background-color: var(--color-secondary);
    border-color: var(--color-secondary);
}

.text-primary { color: var(--color-primary) !important; }
.text-secondary { color: var(--color-secondary) !important; }
.bg-primary { background-color: var(--color-primary) !important; }
.bg-secondary { background-color: var(--color-secondary) !important; }

/* Card Styling */
.card {
    border: 1px solid var(--color-border);
    border-radius: 12px;
    box-shadow: var(--shadow-sm);
    transition: all 0.3s ease;
}

.card:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
}

/* Form Controls */
.form-control, .form-select {
    border: 1px solid var(--color-border);
    border-radius: 8px;
    font-family: var(--font-body);
    font-size: var(--font-size-base);
}

.form-control:focus, .form-select:focus {
    border-color: var(--color-primary);
    box-shadow: 0 0 0 0.25rem rgba(244, 124, 38, 0.25);
}
```

---

## ⚡ VUE.JS 3 CONFIGURATION

### **CDN Links - Đặt trước `</body>`**

```html
<!-- Vue.js 3 -->
<script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>

<!-- Chart.js (if needed) -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<!-- Sortable.js (if needed) -->
<script src="https://cdn.jsdelivr.net/npm/sortablejs@1.15.0/Sortable.min.js"></script>

<!-- Bootstrap 5 JS Bundle -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
```

### **Vue.js Standard Setup**

```javascript
const { createApp } = Vue;

createApp({
    data() {
        return {
            // Component state here
        };
    },
    computed: {
        // Computed properties
    },
    methods: {
        // Component methods
    },
    mounted() {
        // Lifecycle hook
    }
}).mount('#app');
```

---

## 🧩 COMPONENT STANDARDS

### **Button Styles**

```css
/* PRIMARY BUTTON - Main CTA */
.btn-primary {
    background: var(--color-primary);
    color: var(--color-text-white);
    padding: 12px 32px;
    border-radius: 8px;
    font-weight: var(--font-weight-semibold);
    text-transform: uppercase;
    transition: all 0.3s ease;
}

.btn-primary:hover {
    background: var(--color-primary-dark);
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

/* SECONDARY BUTTON */
.btn-secondary {
    background: var(--color-secondary);
    color: var(--color-text-white);
}

/* OUTLINE BUTTON */
.btn-outline-primary {
    border: 2px solid var(--color-primary);
    color: var(--color-primary);
    background: transparent;
}

.btn-outline-primary:hover {
    background: var(--color-primary);
    color: var(--color-text-white);
}
```

### **Card Styles**

```css
/* STANDARD CARD */
.card {
    background: var(--color-bg-white);
    border: 1px solid var(--color-border);
    border-radius: 12px;
    box-shadow: var(--shadow-sm);
    padding: 24px;
}

/* CARD HOVER EFFECT */
.card-hover {
    transition: all 0.3s ease;
}

.card-hover:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
}

/* CARD HEADER */
.card-header {
    border-bottom: 1px solid var(--color-border);
    padding-bottom: 16px;
    margin-bottom: 16px;
}
```

### **Badge Styles**

```css
/* SUCCESS BADGE */
.badge-success {
    background: var(--color-success);
    color: white;
    padding: 6px 12px;
    border-radius: 6px;
    font-size: var(--font-size-sm);
}

/* ERROR BADGE */
.badge-error {
    background: var(--color-error);
    color: white;
}

/* WARNING BADGE */
.badge-warning {
    background: var(--color-warning);
    color: white;
}
```

---

## 📱 RESPONSIVE DESIGN RULES

### **Breakpoints (Bootstrap 5 Standard)**

```css
/* Mobile First Approach */

/* Extra Small (xs) - Default: < 576px */
/* Small (sm): >= 576px */
@media (min-width: 576px) { }

/* Medium (md): >= 768px */
@media (min-width: 768px) { }

/* Large (lg): >= 992px */
@media (min-width: 992px) { }

/* Extra Large (xl): >= 1200px */
@media (min-width: 1200px) { }

/* XXL: >= 1400px */
@media (min-width: 1400px) { }
```

### **Font Size Responsive**

```css
/* Headings scale down on mobile */
@media (max-width: 768px) {
    h1 { font-size: var(--font-size-3xl); }
    h2 { font-size: var(--font-size-2xl); }
    h3 { font-size: var(--font-size-xl); }
    
    /* Body text STAYS 16px minimum */
    body, p { font-size: var(--font-size-base); }
}
```

---

## 📄 STANDARD HTML TEMPLATE

```html
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page Title - English Learning Platform</title>
    
    <!-- Bootstrap 5.3.0 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Font Awesome 6.4.0 -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- Google Fonts: Montserrat + Open Sans -->
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700;800&family=Open+Sans:wght@400;600&display=swap" rel="stylesheet">
    
    <!-- Custom Theme CSS -->
    <link rel="stylesheet" href="../assets/css/theme.css">
    
    <style>
        /* Page-specific styles here */
    </style>
</head>
<body>
    <div id="app">
        <!-- Page content here -->
    </div>

    <!-- Bootstrap 5 JS Bundle -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- Vue.js 3 -->
    <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
    
    <!-- App Logic -->
    <script>
        const { createApp } = Vue;

        createApp({
            data() {
                return {
                    // State
                };
            },
            methods: {
                // Methods
            }
        }).mount('#app');
    </script>
</body>
</html>
```

---

## ✅ CHECKLIST TRƯỚC KHI COMMIT

Mọi trang mới phải đáp ứng:

- [ ] **Font:** Montserrat (headings) + Open Sans (body)
- [ ] **Colors:** Sử dụng CSS Variables từ `theme.css`
- [ ] **Bootstrap 5.3.0:** CDN đầy đủ
- [ ] **Vue.js 3:** Reactive components
- [ ] **Responsive:** Mobile-first approach
- [ ] **Line Height:** Body text = 1.6 (bắt buộc)
- [ ] **Font Size:** Minimum 16px cho body text
- [ ] **Button:** Uppercase + Montserrat font
- [ ] **Card:** Border radius 12px + shadow
- [ ] **Hover Effects:** Smooth transitions 0.3s

---

## 🚫 ĐIỀU CẤM KỴ (NEVER DO)

1. ❌ **Không dùng màu trắng tinh (#FFFFFF) cho nền chính** → Dùng #F9FAFC
2. ❌ **Không dùng font size < 16px cho body text** → Gây cận thị
3. ❌ **Không dùng line-height < 1.6 cho đoạn văn** → Khó đọc
4. ❌ **Không dùng màu đen tuyền (#000000)** → Dùng #2C3E50
5. ❌ **Không lạm dụng màu cam** → Chỉ 10% cho CTA
6. ❌ **Không mix font khác** → Chỉ Montserrat + Open Sans
7. ❌ **Không inline styles trực tiếp** → Dùng CSS Variables
8. ❌ **Không hardcode colors** → Luôn dùng CSS Variables

---

## 📚 FILE STRUCTURE

```
assets/
├── css/
│   ├── theme.css          ← CSS Variables + Overrides (BẮT BUỘC)
│   ├── components.css     ← Reusable components
│   └── utilities.css      ← Helper classes
├── js/
│   ├── main.js            ← Global JavaScript
│   └── components/        ← Vue components
└── images/
    ├── icons/
    ├── illustrations/
    └── photos/
```

---

**🔒 QUY CHUẨN NÀY LÀ BẮT BUỘC - KHÔNG ĐƯỢC VI PHẠM**

**Version Control:** Mọi thay đổi phải được approve bởi Lead Developer  
**Last Review:** December 7, 2025  
**Next Review:** January 7, 2026
