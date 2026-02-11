# 🎵 Hướng Dẫn Tạo TTS Audio cho Phonemes

## 📋 Quy Trình

### 1️⃣ Bước 1: Xem Danh Sách Phonemes
```
Django Admin → Curriculum Management → Phonemes
http://127.0.0.1:8000/admin/curriculum/phoneme/
```

### 2️⃣ Bước 2: Chọn Phonemes Để Tạo Audio
- **Tìm kiếm**: Nhập IPA symbol (e.g., "i", "p", "b")
- **Lọc**: Dùng các filter bên phải (loại âm, danh mục, status)
- **Chọn phonemes**: Tick checkbox bên trái các phoneme

### 3️⃣ Bước 3: Chạy Action Để Tạo TTS Audio
1. Bên trên danh sách, chọn action: **🎵 Generate TTS audio for selected phonemes**
2. Click **GO**
3. Xem thông báo: `✅ Started TTS generation for X phoneme(s)`

### 4️⃣ Bước 4: Theo Dõi Quá Trình
**Celery Worker Terminal** sẽ hiển thị:
```
[2025-12-15 13:50:00,123: INFO/MainProcess] generate_phoneme_audio[...] Starting TTS...
Generating TTS for phoneme /i:/ (ID: 5)
✅ TTS generated successfully for /i:/ (AudioSource ID: 42)
```

---

## ✨ Kết Quả

Sau khi task hoàn tất:
- ✅ **AudioSource** được tạo tự động
- ✅ **AudioCache** lưu thông tin file
- ✅ Audio file được lưu trong `/media/phonemes/audio/`

### Xem Audio Đã Tạo
```
http://127.0.0.1:8000/admin/curriculum/audiosource/
```

Bạn sẽ thấy các Audio Sources mới với:
- Phoneme IPA symbol
- Source type: `tts` (Text-to-Speech)
- Voice ID: `en-US-AriaNeural`
- Audio player để test

---

## 🎯 Ví Dụ Thực Tế

### Tạo Audio Cho 5 Phonemes Đầu Tiên

1. **Vào Admin Phoneme**:
   ```
   http://127.0.0.1:8000/admin/curriculum/phoneme/
   ```

2. **Chọn 5 phonemes** (checkbox tất cả hoặc từng cái)

3. **Action dropdown** → **🎵 Generate TTS audio...**

4. **Nhấn GO** → Celery bắt đầu tạo

5. **Kiểm tra Celery logs**:
   ```
   Terminal Celery sẽ hiển thị:
   ✅ TTS generated successfully for /p/ (AudioSource ID: 1)
   ✅ TTS generated successfully for /b/ (AudioSource ID: 2)
   ✅ TTS generated successfully for /t/ (AudioSource ID: 3)
   ...
   ```

6. **Xem kết quả** ở `/admin/curriculum/audiosource/`

---

## 🔍 Troubleshooting

### ❌ Action Không Xuất Hiện
- Reload trang browser
- Clear browser cache
- Restart Django dev server

### ❌ Task Không Chạy
- Kiểm tra Celery Worker đang chạy
- Kiểm tra Redis đang chạy (`redis-server`)
- Xem logs: Celery terminal sẽ hiển thị errors

### ❌ Audio File Không Được Lưu
- Kiểm tra thư mục `media/phonemes/audio/` tồn tại
- FFmpeg warning: OK, audio vẫn được tạo (chỉ không optimize)

---

## 📊 Phoneme Admin Features

| Cột | Mô Tả |
|-----|-------|
| **IPA Symbol** | Ký hiệu phiên âm (e.g., /p/, /b/) |
| **Vietnamese Approx** | Âm tương đương tiếng Việt |
| **Phoneme Type** | Loại: consonant, vowel, diphthong |
| **Has TTS Audio** | ✅ Đã có audio / ❌ Chưa có |
| **Category** | Danh mục: Plosives, Fricatives, v.v. |

---

## 🚀 Next Steps

- **Tạo audio cho tất cả 44 phonemes**: Select All → Generate
- **Xem phoneme chart**: `http://127.0.0.1:8000/pronunciation/chart/` → Nhấp audio để nghe
- **Monitor storage**: Kiểm tra dung lượng file audio trong `/media/`
