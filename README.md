# EnglishMaster - Trang Web Học Tiếng Anh

## 🎨 Thiết kế & Màu sắc

### Bảng màu chủ đạo
- **Energetic Orange**: #F47C26 (Màu chính - CTA, nút bấm, điểm nhấn)
- **Navy Blue**: #183B56 (Màu phụ - Header section, Footer)
- **Charcoal Gray**: #4A4A4A (Màu chữ chính)
- **Light Gray**: #F9FAFC (Màu nền phụ)

### Font chữ
- **Heading**: Montserrat (Bold, 700-800)
- **Body**: Open Sans (Regular, 400-600)

## 🚀 Công nghệ sử dụng

- **Bootstrap 5.3.2** - Framework CSS responsive
- **Vue.js 3** - Progressive JavaScript Framework
- **Font Awesome 6.5.1** - Icons
- **AOS (Animate On Scroll)** - Animation library
- **Google Fonts** - Montserrat & Open Sans

## 📁 Cấu trúc thư mục

```
english_study/
│
├── index.html                 # Trang chủ chính
│
├── assets/
│   ├── css/
│   │   └── style.css         # CSS tùy chỉnh
│   │
│   ├── js/
│   │   └── main.js           # JavaScript chính (Vue.js app)
│   │
│   └── images/
│       ├── hero-student.png          # Ảnh hero section
│       ├── step-1.png               # Ảnh bước 1
│       ├── step-2.png               # Ảnh bước 2
│       ├── step-3.png               # Ảnh bước 3
│       │
│       ├── partners/                # Logo đối tác
│       │   ├── partner-1.png
│       │   ├── partner-2.png
│       │   ├── partner-3.png
│       │   ├── partner-4.png
│       │   └── partner-5.png
│       │
│       ├── teachers/                # Ảnh giáo viên
│       │   ├── teacher-1.jpg
│       │   ├── teacher-2.jpg
│       │   ├── teacher-3.jpg
│       │   └── teacher-4.jpg
│       │
│       └── testimonials/            # Avatar học viên
│           ├── avatar-1.jpg
│           ├── avatar-2.jpg
│           ├── avatar-3.jpg
│           └── avatar-4.jpg
│
└── README.md                 # File này
```

## 📋 Các section trong trang chủ

### 1. **Navigation (Sticky Header)**
   - Logo + Menu
   - Nút "Đăng ký ngay" (màu cam)
   - Sticky: Dính khi scroll

### 2. **Hero Section**
   - Layout 50/50: Text + Image
   - H1 tiêu đề chính
   - CTA button màu cam
   - Trust badge (10,000+ học viên)
   - Hình ảnh động với shapes

### 3. **Social Proof Banner**
   - Logo đối tác/báo chí
   - Grayscale effect
   - Nền xám nhạt

### 4. **Value Proposition**
   - 4 lợi ích nổi bật
   - Icon + Tiêu đề + Mô tả
   - Layout 4 cột responsive

### 5. **How It Works**
   - 3 bước học tập
   - Z-Pattern layout
   - Ảnh minh họa giao diện

### 6. **Teachers Section**
   - Nền Navy Blue
   - 4 giáo viên tiêu biểu
   - Ảnh tròn + Quốc tịch + Kinh nghiệm

### 7. **Testimonials**
   - Slider cảm nhận học viên
   - Quote format
   - Ảnh + Tên + Nghề nghiệp

### 8. **Final CTA**
   - Nền gradient cam
   - Lời kêu gọi cuối
   - 2 nút: Đăng ký + Test miễn phí

### 9. **Footer**
   - Nền Navy Blue
   - Links + Social Media + Liên hệ
   - Copyright

## 🎯 Tính năng UX/UI nổi bật

### Sticky Header
- Menu dính khi scroll
- Nút "Đăng ký" luôn hiển thị

### Micro-interactions
- Hover effect trên buttons (nảy lên + shadow)
- Card hover animation (translateY + shadow)
- Image lazy loading

### Animations
- AOS (Animate On Scroll)
- Smooth scroll
- Float animation cho hero image
- Rotate animation cho shapes

### Responsive Design
- Mobile-first approach
- Breakpoints: 991px, 767px
- Optimized cho tất cả thiết bị

## 🛠️ Cách sử dụng

### 1. Chuẩn bị hình ảnh

Bạn cần thêm các hình ảnh vào thư mục `assets/images/`:

**Hero Section:**
- `hero-student.png` - Học viên cầm máy tính bảng/điện thoại

**How It Works:**
- `step-1.png` - Giao diện bài test
- `step-2.png` - Giao diện lộ trình học
- `step-3.png` - Giao diện luyện tập/chứng chỉ

**Partners:**
- `partner-1.png` đến `partner-5.png` - Logo đối tác (grayscale)

**Teachers:**
- `teacher-1.jpg` đến `teacher-4.jpg` - Ảnh giáo viên (chân dung)

**Testimonials:**
- `avatar-1.jpg` đến `avatar-4.jpg` - Avatar học viên

### 2. Mở file HTML

Mở file `index.html` bằng trình duyệt web:
- Double click vào file
- Hoặc chuột phải > Open with > Chrome/Firefox/Edge

### 3. Tùy chỉnh nội dung

**Thay đổi văn bản:**
- Mở `index.html`
- Tìm và thay đổi text trong các thẻ HTML

**Thay đổi màu sắc:**
- Mở `assets/css/style.css`
- Chỉnh sửa biến CSS trong `:root`

**Thay đổi dữ liệu:**
- Mở `assets/js/main.js`
- Chỉnh sửa arrays: `features`, `teachers`, `testimonials`

## 🎨 Hướng dẫn tùy chỉnh màu sắc

Trong file `style.css`, tìm section `:root` và thay đổi:

```css
:root {
    --energetic-orange: #F47C26;  /* Màu cam chính */
    --navy-blue: #183B56;         /* Màu xanh than */
    --charcoal-gray: #4A4A4A;     /* Màu xám than */
}
```

## 📱 Responsive Breakpoints

- **Desktop**: > 991px
- **Tablet**: 768px - 991px
- **Mobile**: < 767px

## 🚀 Triển khai lên hosting

### GitHub Pages:
1. Tạo repository mới trên GitHub
2. Upload toàn bộ files
3. Settings > Pages > Deploy

### Netlify:
1. Kéo thả thư mục vào Netlify
2. Tự động deploy

### Vercel:
1. Import repository
2. Deploy tự động

## 📝 Ghi chú quan trọng

### Hình ảnh placeholder
- Hiện tại các đường dẫn hình ảnh là placeholder
- Bạn cần thay thế bằng hình ảnh thật
- Khuyến nghị: Dùng ảnh chất lượng cao, tối ưu size

### CDN Dependencies
- Bootstrap, Vue.js, Font Awesome đều load từ CDN
- Cần internet để xem đầy đủ tính năng
- Có thể download về local nếu cần

### Browser Support
- Chrome (khuyến nghị)
- Firefox
- Safari
- Edge
- IE11+ (giới hạn)

## 🎯 Nguyên tắc CRO đã áp dụng

### Mô hình A.I.D.A
- **Attention**: Hero section bắt mắt
- **Interest**: Value proposition hấp dẫn
- **Desire**: Social proof + Testimonials
- **Action**: Multiple CTAs

### Tâm lý học màu sắc
- **Cam**: Năng lượng, hành động, urgency
- **Xanh than**: Tin tưởng, chuyên nghiệp
- **Trắng**: Sạch sẽ, thoáng đãng

### White Space
- Padding lớn giữa sections (80-100px)
- Dễ đọc, dễ thở
- Focus vào nội dung quan trọng

### Multiple CTAs
- Hero: "Học thử miễn phí"
- Mid-page: "Kiểm tra trình độ"
- Final: "Đăng ký ngay"

## 🔧 Troubleshooting

### Lỗi không hiển thị CSS:
- Kiểm tra đường dẫn file `style.css`
- Đảm bảo cấu trúc thư mục đúng

### Lỗi Vue.js không hoạt động:
- Kiểm tra console log (F12)
- Đảm bảo CDN Vue.js load thành công

### Lỗi hình ảnh không hiển thị:
- Kiểm tra đường dẫn tương đối
- Đảm bảo file tồn tại trong thư mục

## 📞 Hỗ trợ

Nếu bạn cần hỗ trợ:
1. Kiểm tra console log (F12 > Console)
2. Xem lỗi trong Network tab
3. Đọc kỹ README này

## 📄 License

Free to use cho mục đích học tập và thương mại.

---

**Phát triển bởi**: Vue.js 3 + Bootstrap 5  
**Thiết kế**: Conversion Rate Optimization (CRO) Focused  
**Cập nhật**: December 2025

🎓 **Chúc bạn thành công với dự án học tiếng Anh!**
