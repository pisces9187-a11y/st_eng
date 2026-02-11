# Quick Start - Phase 2 URLs Fixed

## Lỗi đã fix:
- ✅ 404 errors cho `/flashcard-study.html`
- ✅ 404 errors cho `/progress-dashboard.html`  
- ✅ 404 errors cho `/achievements.html`
- ✅ 404 errors cho `/favicon.ico`
- ✅ Các đường dẫn assets (`../assets/` → `/assets/`)
- ✅ Các link nội bộ giữa các trang

## Các thay đổi:

### 1. Backend URLs (`backend/config/urls.py`)
Đã thêm các URL patterns mới:

```python
# Direct access to main HTML pages
path('flashcard-study.html', ...),
path('progress-dashboard.html', ...),
path('achievements.html', ...),
path('flashcard.html', ...),
path('dashboard.html', ...),
path('favicon.ico', ...),
```

### 2. HTML Files
Đã sửa tất cả đường dẫn từ relative (`../assets/`, `../public/`) sang absolute (`/assets/`, `/`):

- ✅ `flashcard-study.html`
- ✅ `progress-dashboard.html`  
- ✅ `achievements.html`

### 3. Favicon
Đã copy favicon.ico vào `/public/favicon.ico`

## Cách test:

### 1. Khởi động server:
```bash
cd /home/n2t/Documents/english_study/backend
python3 manage.py runserver
```

### 2. Truy cập các URL sau:

**Flashcard Study (NEW):**
```
http://localhost:8000/flashcard-study.html
```

**Progress Dashboard (NEW):**
```
http://localhost:8000/progress-dashboard.html
```

**Achievements:**
```
http://localhost:8000/achievements.html
```

**Dashboard (existing):**
```
http://localhost:8000/dashboard.html
```

**Alternative URLs (cũng hoạt động):**
```
http://localhost:8000/public/flashcard-study.html
http://localhost:8000/public/progress-dashboard.html
http://localhost:8000/public/achievements.html
```

## Kiểm tra trong browser:

1. ✅ Trang load không có lỗi 404
2. ✅ CSS được load (kiểm tra Network tab)
3. ✅ JavaScript files được load
4. ✅ Favicon hiển thị
5. ✅ Click vào links giữa các trang hoạt động

## URLs đã được fix:

### CSS:
- `/assets/css/theme.css` ✅
- `/assets/css/flashcard-audio-player.css` ✅

### JavaScript:
- `/assets/js/config.js` ✅
- `/assets/js/django-api.js` ✅
- `/assets/js/flashcard-audio-player.js` ✅
- `/assets/js/flashcard-study-session.js` ✅

### Navigation Links:
- `/dashboard.html` ✅
- `/flashcard-study.html` ✅
- `/progress-dashboard.html` ✅
- `/achievements.html` ✅

## Troubleshooting:

### Nếu vẫn thấy 404:

1. **Clear browser cache:**
   - Ctrl+Shift+R (hard refresh)
   - Hoặc F12 → Network → "Disable cache"

2. **Restart Django server:**
   ```bash
   # Stop server (Ctrl+C)
   python3 manage.py runserver
   ```

3. **Check file exists:**
   ```bash
   ls -la /home/n2t/Documents/english_study/public/flashcard-study.html
   ls -la /home/n2t/Documents/english_study/public/progress-dashboard.html
   ```

4. **Check Django logs:**
   - Xem terminal output khi truy cập URL
   - Tìm dòng "GET /flashcard-study.html HTTP/1.1" 200 (success)

### Nếu CSS/JS không load:

1. **Check assets directory:**
   ```bash
   ls -la /home/n2t/Documents/english_study/assets/js/
   ls -la /home/n2t/Documents/english_study/assets/css/
   ```

2. **Test direct access:**
   - http://localhost:8000/assets/js/django-api.js
   - http://localhost:8000/assets/css/theme.css

3. **Check browser console (F12):**
   - Xem có lỗi CORS hay 404 không

## Verification:

```bash
# Run verification script
cd /home/n2t/Documents/english_study
python3 verify_phase2.py

# Should show:
# ✅ Files Created: 7/7
# ✅ All components ready
```

## Next Steps:

1. ✅ URLs fixed
2. ✅ Files accessible
3. ⏳ Test với real user login
4. ⏳ Test API integration
5. ⏳ Test audio playback

## API Endpoints (for reference):

Các API endpoints này được gọi từ JavaScript:

```
POST /api/v1/vocabulary/flashcards/study/
POST /api/v1/vocabulary/flashcards/review/
GET  /api/v1/vocabulary/flashcards/due/
GET  /api/v1/vocabulary/audio/generate/
GET  /api/v1/vocabulary/progress/dashboard/
GET  /api/v1/vocabulary/achievements/
```

**Note:** Cần login để access các endpoints này.

## Done! 🎉

Tất cả URLs đã được fix. Reload browser và test ngay!
