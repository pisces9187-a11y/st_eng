# 📊 PHÂN TÍCH HỆ THỐNG ENGLISH LEARNING PLATFORM - ĐÁNH GIÁ TOÀN DIỆN

**Ngày phân tích:** 07/12/2025  
**Phân tích bởi:** System Architect & UX Analyst

---

## 📁 CẤU TRÚC THƯ MỤC ĐÃ TỔ CHỨC

```
english_study/
├── public/                     # TRANG WEB CHÍNH (16 files)
│   ├── index.html             # Landing page
│   ├── login.html             # Đăng nhập
│   ├── signup.html            # Đăng ký
│   ├── password-reset.html    # Quên mật khẩu
│   ├── onboarding.html        # Onboarding mới
│   ├── dashboard.html         # Dashboard học viên
│   ├── lesson-player.html     # Học bài
│   ├── flashcard.html         # Ôn flashcard
│   ├── dictation.html         # Luyện dictation
│   ├── grammar-wiki.html      # Wiki ngữ pháp
│   ├── assessment.html        # Kiểm tra đầu vào
│   ├── assessment-result.html # Kết quả kiểm tra
│   ├── profile.html           # Hồ sơ cá nhân
│   ├── pricing.html           # Bảng giá
│   ├── checkout.html          # Thanh toán
│   └── logout.html            # Đăng xuất
│
├── admin/                      # ADMIN PANEL (6 files)
│   ├── admin-dashboard.html   # Dashboard quản trị
│   ├── admin-lesson-editor.html # Biên tập bài học
│   ├── admin-flashcard.html   # Quản lý flashcard
│   ├── admin-users.html       # Quản lý học viên
│   ├── admin-revenue.html     # Quản lý doanh thu
│   └── admin-settings.html    # Cài đặt hệ thống
│
├── assets/
│   ├── css/
│   ├── js/
│   └── images/
├── Hướng dẫn/
└── welcome-email.html         # Email template
```

---

## 🔍 PHÂN TÍCH LUỒNG NGƯỜI DÙNG (USER JOURNEY)

### ✅ HIỆN CÓ - Những gì đã hoàn thành

#### **GIAI ĐOẠN 1: TIẾP CẬN (Acquisition)**
| Trang | Chức năng | Trạng thái |
|-------|-----------|------------|
| `index.html` | Landing page, giới thiệu | ✅ Hoàn thành |
| `pricing.html` | Bảng giá 3 gói | ✅ Hoàn thành |

#### **GIAI ĐOẠN 2: ĐĂNG KÝ & XÁC THỰC (Authentication)**
| Trang | Chức năng | Trạng thái |
|-------|-----------|------------|
| `signup.html` | Đăng ký tài khoản | ✅ Hoàn thành |
| `login.html` | Đăng nhập | ✅ Hoàn thành |
| `password-reset.html` | Quên mật khẩu | ✅ Hoàn thành |
| `onboarding.html` | Onboarding người mới | ✅ Hoàn thành |

#### **GIAI ĐOẠN 3: ĐÁNH GIÁ TRÌNH ĐỘ (Assessment)**
| Trang | Chức năng | Trạng thái |
|-------|-----------|------------|
| `assessment.html` | Kiểm tra đầu vào | ✅ Hoàn thành |
| `assessment-result.html` | Kết quả + lộ trình | ✅ Hoàn thành |

#### **GIAI ĐOẠN 4: HỌC TẬP (Learning)**
| Trang | Chức năng | Trạng thái |
|-------|-----------|------------|
| `dashboard.html` | Tổng quan tiến độ | ✅ Hoàn thành |
| `lesson-player.html` | Học bài với IC/DC | ✅ Hoàn thành |
| `flashcard.html` | Ôn tập từ vựng | ✅ Hoàn thành |
| `dictation.html` | Luyện nghe viết chính tả | ✅ Hoàn thành |
| `grammar-wiki.html` | Tra cứu ngữ pháp | ✅ Hoàn thành |

#### **GIAI ĐOẠN 5: THANH TOÁN (Monetization)**
| Trang | Chức năng | Trạng thái |
|-------|-----------|------------|
| `checkout.html` | Thanh toán QR/Momo/Stripe | ✅ Hoàn thành |

#### **GIAI ĐOẠN 6: QUẢN LÝ CÁ NHÂN (Profile)**
| Trang | Chức năng | Trạng thái |
|-------|-----------|------------|
| `profile.html` | Hồ sơ, thành tích | ✅ Hoàn thành |
| `logout.html` | Đăng xuất | ✅ Hoàn thành |

---

## ❌ THIẾU SÓT NGHIÊM TRỌNG - Trang Web Chính

### 🚨 **CRITICAL - Ảnh hưởng trực tiếp đến trải nghiệm học tập**

#### 1. **LESSON LIBRARY (Thư viện bài học)** - THIẾU
**Vấn đề:** Học viên không có cách nào duyệt toàn bộ bài học theo cấp độ/chủ đề
**Cần có:**
- Lọc theo cấp độ (A1-C1)
- Lọc theo chủ đề (Business, Travel, Daily Life)
- Tìm kiếm bài học
- Preview bài học trước khi học
- Đánh dấu bài đã hoàn thành
- Hiển thị progress bar từng unit

#### 2. **VOCABULARY LIST (Danh sách từ vựng)** - THIẾU
**Vấn đề:** Không có nơi tập trung tất cả từ đã học
**Cần có:**
- Danh sách tất cả từ đã học
- Phân loại theo chủ đề/cấp độ
- Đánh dấu từ khó/dễ quên
- Thống kê số lần ôn tập
- Export PDF để in
- Ghi chú cá nhân cho từng từ

#### 3. **SPEAKING PRACTICE (Luyện nói)** - THIẾU HOÀN TOÀN
**Vấn đề:** Không có tính năng luyện phát âm
**Cần có:**
- Record giọng học viên
- So sánh với giọng native
- AI phân tích phát âm (speech recognition)
- Điểm số phát âm từng từ
- Luyện tập câu pattern
- Shadowing exercise

#### 4. **WRITING PRACTICE (Luyện viết)** - THIẾU HOÀN TOÀN
**Vấn đề:** Chỉ có nghe/đọc/nói, thiếu kỹ năng viết
**Cần có:**
- Viết câu theo mẫu
- Grammar check tự động
- Vocabulary suggestions
- Viết đoạn văn ngắn
- Chấm điểm bằng AI
- Lưu lịch sử bài viết

#### 5. **PRACTICE TEST (Bài tập thực hành)** - THIẾU
**Vấn đề:** Không có bài tập sau mỗi bài học
**Cần có:**
- Multiple choice questions
- Fill in the blanks
- Sentence reordering
- Error correction
- Kết quả ngay lập tức
- Giải thích chi tiết

#### 6. **PROGRESS TRACKER (Theo dõi tiến độ chi tiết)** - YẾU
**Vấn đề:** Dashboard chỉ hiển thị tổng quan
**Cần có:**
- Biểu đồ tiến độ theo tuần/tháng
- Heatmap học tập (giống GitHub)
- Streak counter (chuỗi ngày học liên tục)
- Time spent per skill
- Weak areas analysis
- Goal setting & tracking

#### 7. **DISCUSSION FORUM (Diễn đàn học tập)** - THIẾU
**Vấn đề:** Không có nơi học viên tương tác
**Cần có:**
- Đặt câu hỏi về bài học
- Chia sẻ kinh nghiệm
- Study groups
- Teacher Q&A
- Comment trên từng bài học

#### 8. **CERTIFICATE (Chứng chỉ hoàn thành)** - THIẾU
**Vấn đề:** Không có động lực hoàn thành khóa học
**Cần có:**
- Certificate PDF sau khi hoàn thành level
- Shareable certificate link
- LinkedIn integration
- Digital badge system

#### 9. **NOTIFICATION CENTER (Trung tâm thông báo)** - THIẾU
**Vấn đề:** Không có cách nhận thông báo hệ thống
**Cần có:**
- Thông báo bài học mới
- Nhắc nhở ôn tập
- Thông báo từ giáo viên
- Cập nhật hệ thống
- Mark as read/unread

#### 10. **LEADERBOARD (Bảng xếp hạng)** - THIẾU
**Vấn đề:** Thiếu yếu tố cạnh tranh lành mạnh
**Cần có:**
- XP leaderboard
- Streak leaderboard
- Weekly/Monthly champions
- Friend comparison
- Achievement badges

### 📊 **HIGH PRIORITY - Cải thiện engagement**

#### 11. **LIVE CLASS SCHEDULE (Lịch học trực tiếp)** - THIẾU
**Cần có:**
- Lịch các buổi live class
- Đăng ký tham gia
- Zoom/Google Meet integration
- Recording replay
- Attendance tracking

#### 12. **LEARNING STATISTICS (Thống kê chi tiết)** - THIẾU
**Cần có:**
- Words learned per day
- Accuracy rate per skill
- Time spent analysis
- Comparison with peers
- Personal best records

#### 13. **MOBILE APP DOWNLOAD PAGE** - THIẾU
**Cần có:**
- Giới thiệu mobile app
- QR code download
- App Store/Google Play links
- Mobile-specific features

#### 14. **HELP CENTER (Trung tâm trợ giúp)** - THIẾU
**Cần có:**
- FAQ section
- Video tutorials
- Contact support form
- Live chat widget
- Knowledge base

#### 15. **BLOG/NEWS (Blog học tập)** - THIẾU
**Cần có:**
- Bài viết học tiếng Anh
- Tips & tricks
- Student success stories
- Platform updates

---

## 🔧 ADMIN PANEL - PHÂN TÍCH QUẢN TRỊ

### ✅ HIỆN CÓ

| Module | Tính năng | Đánh giá |
|--------|-----------|----------|
| **Dashboard** | Thống kê tổng quan, biểu đồ | ⭐⭐⭐⭐ Tốt |
| **Lesson Editor** | Tạo/sửa bài, grammar highlight | ⭐⭐⭐⭐⭐ Xuất sắc |
| **Flashcard Manager** | CRUD flashcard, import CSV | ⭐⭐⭐⭐ Tốt |
| **User Management** | Quản lý học viên, filter | ⭐⭐⭐⭐ Tốt |
| **Revenue** | Doanh thu, giao dịch | ⭐⭐⭐⭐ Tốt |
| **Settings** | Cấu hình hệ thống | ⭐⭐⭐⭐ Tốt |

### ❌ THIẾU SÓT ADMIN PANEL

#### 1. **CONTENT MANAGEMENT SYSTEM (CMS)** - THIẾU
**Cần có:**
- Quản lý tất cả nội dung trang web
- Edit landing page sections
- Manage blog posts
- Upload images/videos bulk
- SEO settings per page

#### 2. **TEACHER MANAGEMENT** - THIẾU HOÀN TOÀN
**Cần có:**
- Thêm/xóa giáo viên
- Phân quyền giáo viên
- Schedule management
- Teacher performance metrics
- Student assignment to teachers

#### 3. **ASSESSMENT CREATOR** - THIẾU
**Cần có:**
- Tạo bài kiểm tra từ question bank
- Drag-drop question builder
- Auto-grading setup
- Difficulty level tagging
- Statistics per question

#### 4. **EMAIL CAMPAIGN MANAGER** - THIẾU
**Cần có:**
- Tạo email marketing campaign
- Segment users (free/pro/inactive)
- Email templates library
- Schedule email sending
- Open rate/click rate analytics

#### 5. **COUPON/DISCOUNT MANAGER** - THIẾU
**Cần có:**
- Tạo mã giảm giá
- Set expiry date/usage limit
- Track coupon usage
- Bulk coupon generation
- Referral program management

#### 6. **ANALYTICS DASHBOARD ADVANCED** - YẾU
**Cần có:**
- User retention rate
- Churn rate analysis
- A/B testing results
- Funnel conversion analysis
- Heat map user behavior

#### 7. **NOTIFICATION MANAGER** - THIẾU
**Cần có:**
- Gửi thông báo hàng loạt
- Schedule notifications
- Push notification to mobile
- In-app announcement banner
- Target specific user segments

#### 8. **REPORT GENERATOR** - THIẾU
**Cần có:**
- Export user progress reports
- Revenue reports by period
- Course completion reports
- Custom report builder
- Auto-generate monthly reports

#### 9. **SUPPORT TICKET SYSTEM** - THIẾU
**Cần có:**
- View user support tickets
- Assign tickets to staff
- Ticket status tracking
- Response templates
- Satisfaction ratings

#### 10. **AUDIT LOG** - THIẾU
**Cần có:**
- Xem lịch sử thay đổi
- Who edited what and when
- User login history
- Payment transaction log
- System error log

#### 11. **ROLE & PERMISSION MANAGER** - THIẾU
**Cần có:**
- Tạo role (Admin/Teacher/Moderator)
- Set permission per role
- Multi-admin support
- Activity restrictions

#### 12. **EXERCISE BANK MANAGER** - THIẾU
**Cần có:**
- Quản lý ngân hàng câu hỏi
- Tag by topic/grammar/level
- Reuse questions across lessons
- Import questions from Excel
- Question difficulty stats

---

## 🎯 ĐỀ XUẤT ƯU TIÊN PHÁT TRIỂN

### **PHASE 1: CRITICAL (4-6 tuần)**
**Mục tiêu:** Hoàn thiện trải nghiệm học tập cơ bản

1. ✅ **Lesson Library** - Tuần 1-2
2. ✅ **Practice Test System** - Tuần 2-3
3. ✅ **Vocabulary List** - Tuần 3-4
4. ✅ **Progress Tracker Advanced** - Tuần 4-5
5. ✅ **Notification Center** - Tuần 5-6

### **PHASE 2: HIGH PRIORITY (6-8 tuần)**
**Mục tiêu:** Thêm tính năng engagement & retention

6. ✅ **Speaking Practice** - Tuần 7-9
7. ✅ **Writing Practice** - Tuần 9-11
8. ✅ **Leaderboard & Gamification** - Tuần 11-12
9. ✅ **Discussion Forum** - Tuần 12-14

### **PHASE 3: ADMIN ENHANCEMENT (4-6 tuần)**
**Mục tiêu:** Tối ưu vận hành & quản lý

10. ✅ **Teacher Management** - Tuần 15-16
11. ✅ **Assessment Creator** - Tuần 17-18
12. ✅ **Coupon Manager** - Tuần 18-19
13. ✅ **Support Ticket System** - Tuần 19-20

### **PHASE 4: SCALING (4-6 tuần)**
**Mục tiêu:** Mở rộng & tối ưu

14. ✅ **Email Campaign Manager** - Tuần 21-22
15. ✅ **Advanced Analytics** - Tuần 22-23
16. ✅ **CMS System** - Tuần 23-24
17. ✅ **Mobile App Integration** - Tuần 24-26

---

## 🏆 SO SÁNH VỚI CÁC PLATFORM HÀNG ĐẦU

| Tính năng | Hệ thống hiện tại | Duolingo | Memrise | Babbel | Rosetta Stone |
|-----------|-------------------|----------|---------|--------|---------------|
| Lesson Player | ✅ Có IC/DC | ✅ | ✅ | ✅ | ✅ |
| Flashcard | ✅ | ✅ | ✅ | ✅ | ✅ |
| Speaking Practice | ❌ | ✅ | ✅ | ✅ | ✅ |
| Writing Practice | ❌ | ✅ | ✅ | ✅ | ✅ |
| Gamification | ⚠️ Yếu | ✅✅ | ✅ | ✅ | ✅ |
| Community Forum | ❌ | ✅ | ✅ | ✅ | ❌ |
| Live Class | ❌ | ❌ | ❌ | ✅ | ✅ |
| Certificate | ❌ | ✅ | ✅ | ✅ | ✅ |
| Mobile App | ❌ | ✅ | ✅ | ✅ | ✅ |
| Offline Mode | ❌ | ✅ | ✅ | ✅ | ✅ |
| Progress Tracking | ⚠️ Basic | ✅✅ | ✅ | ✅ | ✅ |
| Personalized Learning | ❌ | ✅ | ✅ | ✅ | ✅✅ |

**Điểm mạnh hiện tại:**
- ✅ Grammar highlighting (IC/DC/Linking) - Độc đáo
- ✅ Vietnamese market focus (VietQR)
- ✅ Clean UI/UX
- ✅ Comprehensive admin panel

**Điểm yếu cần khắc phục ngay:**
- ❌ Thiếu Speaking & Writing (2 kỹ năng quan trọng)
- ❌ Gamification yếu (không có streak, leaderboard)
- ❌ Không có mobile app
- ❌ Thiếu personalization

---

## 💡 CÔNG NGHỆ ĐỀ XUẤT BỔ SUNG

### **Frontend Enhancements**
```javascript
// 1. Web Speech API - Cho Speaking Practice
const recognition = new webkitSpeechRecognition();
recognition.lang = 'en-US';

// 2. Web Audio API - Phân tích phát âm
const audioContext = new AudioContext();

// 3. Service Worker - Offline mode
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js');
}

// 4. IndexedDB - Local storage
const db = await openDB('english-learning', 1);

// 5. Push Notification API
Notification.requestPermission();
```

### **Backend Services (Đề xuất)**
```
1. Speech Recognition API
   - Google Cloud Speech-to-Text
   - Azure Speech Service
   
2. AI Grammar Checker
   - LanguageTool API
   - Grammarly API
   
3. Personalization Engine
   - TensorFlow.js
   - Spaced Repetition Algorithm (SM-2)
   
4. Analytics
   - Google Analytics 4
   - Mixpanel
   - Hotjar (Heatmap)
   
5. Communication
   - SendGrid (Email)
   - Twilio (SMS)
   - Firebase (Push notification)
```

### **Infrastructure**
```
1. CDN: Cloudflare
2. Database: PostgreSQL + Redis (caching)
3. File Storage: AWS S3 / Cloudinary
4. Video Streaming: Vimeo API
5. Real-time: Socket.io (Chat, Live class)
```

---

## 📈 KPI CẦN THEO DÕI

### **User Metrics**
- DAU (Daily Active Users)
- WAU (Weekly Active Users)
- Retention Rate (D1, D7, D30)
- Churn Rate
- Session Duration
- Lessons Completed per User

### **Business Metrics**
- Conversion Rate (Free → Pro)
- ARPU (Average Revenue Per User)
- LTV (Lifetime Value)
- CAC (Customer Acquisition Cost)
- MRR (Monthly Recurring Revenue)
- Refund Rate

### **Learning Metrics**
- Average Completion Rate per Lesson
- Time to Complete Level
- Quiz Pass Rate
- Word Retention Rate (7 days)
- Skills Progress (Speaking/Writing/Reading/Listening)

---

## 🎨 UX IMPROVEMENTS ĐỀ XUẤT

### **Onboarding Flow**
```
Current: 4 steps (Goal → Level → Time → Plan)
Đề xuất thêm:
Step 5: Learning Style Quiz (Visual/Audio/Kinesthetic)
Step 6: Topic Interest Selection
Step 7: First Lesson Preview
```

### **Gamification Elements**
```
1. Daily Streak Counter (top-right corner)
2. XP Points animation (+ 10 XP)
3. Level Up celebration modal
4. Achievement Unlock notification
5. Progress ring around avatar
6. Weekly challenge widget
```

### **Accessibility**
```
1. Dark mode toggle
2. Font size adjustment
3. High contrast mode
4. Keyboard shortcuts
5. Screen reader support
6. Closed captions for videos
```

---

## ⚡ PERFORMANCE OPTIMIZATION

### **Current Issues (Đánh giá)**
- ❌ Không có lazy loading images
- ❌ Không minify CSS/JS
- ❌ Không có caching strategy
- ❌ Chưa optimize fonts

### **Đề xuất**
```html
<!-- 1. Lazy Loading -->
<img src="image.jpg" loading="lazy" alt="...">

<!-- 2. Font Optimization -->
<link rel="preload" href="fonts/Montserrat.woff2" as="font" type="font/woff2" crossorigin>

<!-- 3. Critical CSS -->
<style>
  /* Inline critical CSS here */
</style>

<!-- 4. Defer non-critical JS -->
<script src="analytics.js" defer></script>
```

### **Target Metrics**
- First Contentful Paint: < 1.5s
- Time to Interactive: < 3.5s
- Lighthouse Score: > 90

---

## 🔒 BẢO MẬT CẦN BỔ SUNG

### **Authentication**
- ✅ JWT Token (implement trong backend)
- ❌ Refresh Token rotation
- ❌ Email verification required
- ❌ Rate limiting login attempts
- ❌ IP-based blocking

### **Data Protection**
- ✅ HTTPS (mentioned in settings)
- ❌ CORS policy
- ❌ XSS protection
- ❌ CSRF token
- ❌ SQL injection prevention
- ❌ Data encryption at rest

### **Privacy Compliance**
- ❌ GDPR compliance notice
- ❌ Cookie consent banner
- ❌ Privacy policy page
- ❌ Terms of service page
- ❌ Data export feature
- ❌ Account deletion option

---

## 📱 MOBILE STRATEGY

### **Đề xuất**
1. **Progressive Web App (PWA)** - Phase 1 (Quick win)
   - Add manifest.json
   - Implement service worker
   - Add to home screen prompt
   
2. **Responsive Enhancement** - Phase 1
   - Mobile-first redesign
   - Touch-friendly buttons (min 44px)
   - Swipe gestures for flashcards
   
3. **Native App** - Phase 2 (Long term)
   - React Native / Flutter
   - App Store + Google Play
   - Push notifications
   - Offline mode full support

---

## 💰 MONETIZATION ENHANCEMENTS

### **Current:** 3 gói (Free/Pro/Lifetime)

### **Đề xuất thêm:**
1. **In-app Purchases**
   - Mua thêm bài học chuyên sâu
   - Unlock special courses (IELTS, TOEIC)
   - Premium grammar wiki access
   
2. **Subscription Tiers mở rộng**
   - Pro Monthly: 120k/tháng
   - Pro Yearly: 1,200k/năm (giảm 17%)
   - Premium: 2,500k/năm (có live class)
   
3. **B2B Licensing**
   - Corporate training packages
   - School/University licenses
   - Bulk discount 20+ users
   
4. **Affiliate Program**
   - Referral commission 20%
   - Custom landing pages
   - Marketing materials

---

## ✅ CHECKLIST HOÀN THIỆN HỆ THỐNG

### **Trang Web Chính**
- [x] Landing page
- [x] Authentication (Login/Signup/Reset)
- [x] Onboarding
- [x] Assessment
- [x] Dashboard
- [x] Lesson Player
- [x] Flashcard
- [x] Dictation
- [x] Grammar Wiki
- [x] Profile
- [x] Pricing
- [x] Checkout
- [x] Logout
- [ ] **Lesson Library**
- [ ] **Vocabulary List**
- [ ] **Speaking Practice**
- [ ] **Writing Practice**
- [ ] **Practice Test**
- [ ] **Progress Tracker Advanced**
- [ ] **Notification Center**
- [ ] **Leaderboard**
- [ ] **Forum**
- [ ] **Certificate**
- [ ] **Live Class Schedule**
- [ ] **Help Center**
- [ ] **Blog**
- [ ] **Privacy Policy**
- [ ] **Terms of Service**

### **Admin Panel**
- [x] Dashboard
- [x] Lesson Editor
- [x] Flashcard Manager
- [x] User Management
- [x] Revenue Management
- [x] Settings
- [ ] **Teacher Management**
- [ ] **Assessment Creator**
- [ ] **Question Bank**
- [ ] **CMS**
- [ ] **Email Campaign**
- [ ] **Coupon Manager**
- [ ] **Analytics Advanced**
- [ ] **Notification Manager**
- [ ] **Report Generator**
- [ ] **Support Tickets**
- [ ] **Audit Log**
- [ ] **Role & Permission**

---

## 🎯 KẾT LUẬN & HÀNH ĐỘNG

### **Đánh giá tổng quan:**
⭐⭐⭐ **3/5 stars - Foundation Solid, Needs Enhancement**

**Điểm mạnh:**
- UI/UX đẹp, nhất quán
- Grammar highlighting độc đáo
- Admin panel đầy đủ cơ bản
- Payment integration tốt

**Điểm yếu:**
- Thiếu Speaking & Writing (CRITICAL)
- Gamification yếu
- Không có community features
- Admin thiếu automation tools

### **Recommendation Priority:**

🔴 **MUST HAVE (Bắt buộc - 2 tháng)**
1. Lesson Library
2. Speaking Practice
3. Writing Practice
4. Progress Tracker Advanced
5. Practice Test System

🟡 **SHOULD HAVE (Nên có - 3 tháng)**
6. Vocabulary List
7. Leaderboard & Gamification
8. Notification Center
9. Certificate System
10. Teacher Management

🟢 **NICE TO HAVE (Tốt nếu có - 4-6 tháng)**
11. Discussion Forum
12. Live Class
13. Mobile App
14. Advanced Analytics
15. CMS System

---

**Prepared by:** System Analyst Team  
**Next Review:** Q1 2026  
**Contact:** architecture@englishlearning.vn
