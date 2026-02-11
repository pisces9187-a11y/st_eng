# Hướng Dẫn Sử Dụng Hệ Thống Edge TTS Mới

## 📋 Tổng Quan

Hệ thống Edge TTS mới đã được tích hợp vào platform học tiếng Anh với các tính năng:

✅ **Tự động tạo audio cho phoneme** khi không có sẵn  
✅ **Nhiều giọng nói** (Mỹ, Anh, Úc, Canada, Ấn Độ)  
✅ **Tùy chỉnh tốc độ** theo trình độ học viên  
✅ **Cache thông minh** để tối ưu hiệu suất  
✅ **API đơn giản** dễ sử dụng  

---

## 🚀 Cài Đặt

### 1. Cài Edge TTS

```bash
pip install edge-tts
```

### 2. Cấu hình (Đã tích hợp sẵn)

File `backend/config/settings/base.py` đã được cấu hình:

```python
TTS_DEFAULT_VOICE_KEY = 'us_female_clear'
TTS_DEFAULT_SPEED_LEVEL = 'intermediate'
TTS_AUDIO_DIR = os.path.join(MEDIA_ROOT, 'tts_audio')
MOCK_TTS_MODE = False  # Set True để test offline
```

---

## 💻 Cách Sử Dụng

### 1️⃣ **Lấy Audio cho Phoneme (Tự Động)**

```python
from apps.curriculum.services.audio_service import PhonemeAudioService
from apps.curriculum.models import Phoneme

# Khởi tạo service
audio_service = PhonemeAudioService()

# Lấy phoneme
phoneme = Phoneme.objects.get(ipa_symbol='i:')

# Lấy audio - TỰ ĐỘNG TẠO nếu chưa có!
audio = audio_service.get_audio_for_phoneme(
    phoneme=phoneme,
    auto_generate=True  # ✨ Tính năng mới!
)

if audio:
    print(f"Audio URL: {audio.get_url()}")
    print(f"Source type: {audio.source_type}")  # 'native', 'tts', hoặc 'generated'
else:
    print("Không thể tạo audio")
```

### 2️⃣ **Tạo Audio cho Câu**

```python
from apps.curriculum.services.audio_service import PhonemeAudioService

audio_service = PhonemeAudioService()

# Tạo audio cho câu
audio_path = audio_service.generate_sentence_audio(
    text="The weather is beautiful today.",
    voice_key="us_female_clear",  # Chọn giọng
    speed_level="beginner"  # Chậm hơn cho người mới
)

print(f"Audio saved at: {audio_path}")
```

### 3️⃣ **Tạo Audio Hội Thoại**

```python
dialogues = [
    {"speaker": "A", "text": "Hello! How are you?"},
    {"speaker": "B", "text": "I'm fine, thank you!"},
    {"speaker": "A", "text": "What are you doing today?"},
    {"speaker": "B", "text": "I'm going shopping."}
]

audio_files = audio_service.generate_conversation_audio(
    dialogues=dialogues,
    speed_level="intermediate"
)

for i, audio_path in enumerate(audio_files):
    print(f"Speaker {dialogues[i]['speaker']}: {audio_path}")
```

### 4️⃣ **Tạo Audio cho Flashcard**

```python
audio_dict = audio_service.generate_flashcard_audio(
    word="perseverance",
    definition="continued effort to do something despite difficulties",
    example="Her perseverance led to success.",
    accent="us"  # hoặc "gb" cho giọng Anh
)

print(f"Word audio: {audio_dict['word']}")
print(f"Definition audio: {audio_dict['definition']}")
print(f"Example audio: {audio_dict['example']}")
```

### 5️⃣ **Sử Dụng EnglishTTSService Trực Tiếp**

```python
from apps.curriculum.services.edge_tts_service import get_tts_service

tts = get_tts_service()

# Phát âm từ (repeat 2 lần, chậm)
word_audio = await tts.generate_word_pronunciation(
    word="beautiful",
    accent="us",
    repeat=2,
    speed_level="beginner"
)

# Hoặc dùng sync
word_audio = tts.generate_word_pronunciation_sync(
    word="beautiful",
    accent="us",
    repeat=2
)

print(f"Audio: {word_audio}")
```

---

## 🎯 Các Giọng Nói Có Sẵn

### Giọng Mỹ (Khuyên dùng)

| Voice Key | Giới Tính | Mô Tả | Phù Hợp |
|-----------|-----------|-------|---------|
| `us_female_clear` | Nữ | Rõ ràng nhất | ✅ Từ vựng, hội thoại |
| `us_male_standard` | Nam | Chuẩn, ấm | ✅ Bài đọc |
| `us_female_young` | Nữ | Trẻ trung | Học sinh |
| `us_male_professional` | Nam | Chuyên nghiệp | Học thuật |

### Giọng Anh

| Voice Key | Giới Tính | Mô Tả |
|-----------|-----------|-------|
| `gb_female` | Nữ | Chuẩn BBC |
| `gb_male` | Nam | Lịch lãm |

### Giọng Khác

- `au_female`, `au_male` - Úc
- `ca_female`, `ca_male` - Canada
- `in_female`, `in_male` - Ấn Độ

---

## ⚙️ Các Trình Độ Tốc Độ

| Level | Tốc Độ | Phù Hợp |
|-------|--------|---------|
| `beginner` | -25% | Người mới bắt đầu |
| `elementary` | -15% | Sơ cấp |
| `intermediate` | 0% | Trung cấp (mặc định) |
| `upper_intermediate` | +5% | Trung cấp cao |
| `advanced` | +10% | Nâng cao |
| `native` | +15% | Người bản ngữ |

---

## 🔌 Tích Hợp Vào Views/API

### Django View

```python
from django.http import JsonResponse
from apps.curriculum.services.audio_service import PhonemeAudioService

def generate_audio_view(request):
    text = request.POST.get('text')
    voice_key = request.POST.get('voice', 'us_female_clear')
    speed_level = request.POST.get('speed', 'intermediate')
    
    audio_service = PhonemeAudioService()
    audio_path = audio_service.generate_sentence_audio(
        text=text,
        voice_key=voice_key,
        speed_level=speed_level
    )
    
    if audio_path:
        # Convert to URL
        from django.conf import settings
        import os
        relative_path = os.path.relpath(audio_path, settings.MEDIA_ROOT)
        audio_url = os.path.join(settings.MEDIA_URL, relative_path).replace('\\', '/')
        
        return JsonResponse({
            'success': True,
            'audio_url': audio_url
        })
    
    return JsonResponse({'success': False, 'error': 'Failed to generate audio'})
```

### Django REST Framework

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.curriculum.services.audio_service import PhonemeAudioService

class GenerateAudioView(APIView):
    def post(self, request):
        text = request.data.get('text')
        voice_key = request.data.get('voice', 'us_female_clear')
        speed_level = request.data.get('speed', 'intermediate')
        
        audio_service = PhonemeAudioService()
        audio_path = audio_service.generate_sentence_audio(
            text=text,
            voice_key=voice_key,
            speed_level=speed_level
        )
        
        if audio_path:
            # Get URL
            from apps.curriculum.services.edge_tts_service import get_tts_service
            tts = get_tts_service()
            audio_url = tts.get_audio_url(audio_path)
            
            return Response({
                'success': True,
                'audio_url': audio_url
            })
        
        return Response({
            'success': False,
            'error': 'Failed to generate audio'
        }, status=400)
```

---

## 🎪 Celery Tasks (Async Generation)

```python
# backend/apps/curriculum/tasks.py

from celery import shared_task
from apps.curriculum.services.audio_service import PhonemeAudioService
from apps.curriculum.models import Phoneme

@shared_task
def generate_phoneme_audio_task(phoneme_id, voice_key='us_female_clear'):
    """
    Celery task để tạo audio cho phoneme.
    """
    try:
        phoneme = Phoneme.objects.get(id=phoneme_id)
        audio_service = PhonemeAudioService()
        
        audio = audio_service._generate_phoneme_audio(phoneme, voice_key)
        
        if audio:
            return {
                'success': True,
                'audio_id': audio.id,
                'phoneme': phoneme.ipa_symbol
            }
        
        return {'success': False, 'error': 'Failed to generate'}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}


@shared_task
def bulk_generate_phoneme_audio_task(voice_key='us_female_clear'):
    """
    Tạo audio cho tất cả phoneme chưa có audio.
    """
    from apps.curriculum.models import Phoneme
    
    audio_service = PhonemeAudioService()
    missing_phonemes = audio_service.get_missing_audio_phonemes()
    
    results = audio_service.bulk_generate_phoneme_audio(
        phonemes=missing_phonemes,
        voice_key=voice_key
    )
    
    return {
        'total': len(missing_phonemes),
        'generated': len(results),
        'success': True
    }
```

**Sử dụng:**

```python
# Trong Django shell hoặc view
from apps.curriculum.tasks import generate_phoneme_audio_task

# Tạo audio cho phoneme ID 1
generate_phoneme_audio_task.delay(1)

# Bulk generate
from apps.curriculum.tasks import bulk_generate_phoneme_audio_task
bulk_generate_phoneme_audio_task.delay()
```

---

## 🧪 Testing & Development

### Mock Mode (Offline Testing)

```bash
# Set environment variable
export MOCK_TTS=true  # Linux/Mac
set MOCK_TTS=true     # Windows

# Hoặc trong settings
MOCK_TTS_MODE = True
```

Khi bật Mock mode:
- Không cần internet
- Tạo audio sine wave tone (440 Hz) để test
- Tốc độ nhanh

### Test Trong Django Shell

```python
python manage.py shell

# Test tạo audio
from apps.curriculum.services.edge_tts_service import get_tts_service
tts = get_tts_service()

# Test sync
audio_path = tts.generate_word_pronunciation_sync("hello", "us")
print(audio_path)

# Test phoneme auto-generation
from apps.curriculum.services.audio_service import PhonemeAudioService
from apps.curriculum.models import Phoneme

service = PhonemeAudioService()
phoneme = Phoneme.objects.first()
audio = service.get_audio_for_phoneme(phoneme, auto_generate=True)
print(audio)
```

---

## 📊 Management Commands

### Tạo Audio cho Tất Cả Phonemes

```python
# backend/apps/curriculum/management/commands/generate_phoneme_audio.py

from django.core.management.base import BaseCommand
from apps.curriculum.services.audio_service import PhonemeAudioService
from apps.curriculum.models import Phoneme

class Command(BaseCommand):
    help = 'Generate audio for all phonemes'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--voice',
            type=str,
            default='us_female_clear',
            help='Voice key to use'
        )
    
    def handle(self, *args, **options):
        voice_key = options['voice']
        
        audio_service = PhonemeAudioService()
        missing = audio_service.get_missing_audio_phonemes()
        
        self.stdout.write(f"Found {len(missing)} phonemes without audio")
        
        results = audio_service.bulk_generate_phoneme_audio(
            phonemes=missing,
            voice_key=voice_key
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Generated audio for {len(results)}/{len(missing)} phonemes"
            )
        )
```

**Chạy:**

```bash
python manage.py generate_phoneme_audio --voice us_female_clear
```

---

## 🔧 Utilities

### Kiểm Tra Audio Quality

```python
from backend.utils.audio_utils import validate_audio_quality

result = validate_audio_quality("path/to/audio.mp3")

if result['valid']:
    print("✅ Audio hợp lệ")
else:
    print("❌ Lỗi:", result['errors'])
    print("⚠️ Cảnh báo:", result['warnings'])
```

### Tối Ưu Audio

```python
from backend.utils.audio_utils import optimize_audio

optimized = optimize_audio(
    input_path="large_audio.mp3",
    output_path="optimized.mp3",
    bitrate="96k",  # Giảm dung lượng
    mono=True  # Chuyển sang mono
)
```

### Batch Optimization

```python
from backend.utils.audio_utils import batch_optimize_audio

optimized_files = batch_optimize_audio(
    input_dir="media/tts_audio",
    output_dir="media/tts_audio_optimized",
    bitrate="96k",
    mono=True
)

print(f"Optimized {len(optimized_files)} files")
```

---

## 🐛 Troubleshooting

### Lỗi: "edge-tts không tìm thấy"

```bash
pip install edge-tts
```

### Lỗi: "No module named 'pydub'"

```bash
pip install pydub
# Cài ffmpeg (cần cho audio processing)
# Windows: choco install ffmpeg
# Mac: brew install ffmpeg
# Ubuntu: apt-get install ffmpeg
```

### Audio không tạo được

1. Kiểm tra internet connection
2. Bật Mock mode để test: `MOCK_TTS=true`
3. Xem logs: `tail -f logs/django.log`

### Cache không hoạt động

```python
# Clear cache
from apps.curriculum.services.audio_service import PhonemeAudioService

service = PhonemeAudioService()
service.clear_all_audio_cache()
```

---

## 📚 API Reference

### EnglishTTSService

```python
from apps.curriculum.services.edge_tts_service import get_tts_service

tts = get_tts_service()

# Methods (async):
await tts.generate_speech(text, voice_key, speed_level)
await tts.generate_word_pronunciation(word, accent, repeat)
await tts.generate_sentence_audio(sentence, student_level, voice_type, accent)
await tts.generate_conversation(dialogues, student_level)
await tts.generate_flashcard_audio(word, definition, example, accent)

# Methods (sync - dùng trong Django views):
tts.generate_speech_sync(...)
tts.generate_word_pronunciation_sync(...)
tts.generate_sentence_audio_sync(...)
tts.generate_conversation_sync(...)
tts.generate_flashcard_audio_sync(...)
```

### PhonemeAudioService

```python
from apps.curriculum.services.audio_service import PhonemeAudioService

service = PhonemeAudioService()

# Get audio with auto-generation
audio = service.get_audio_for_phoneme(phoneme, auto_generate=True)

# Generate specific types
audio_path = service.generate_sentence_audio(text, voice_key, speed_level)
audio_files = service.generate_conversation_audio(dialogues, speed_level)
audio_dict = service.generate_flashcard_audio(word, definition, example, accent)

# Bulk operations
results = service.bulk_generate_phoneme_audio(phonemes, voice_key)
```

---

## 🎓 Best Practices

1. **Sử dụng auto_generate=True** khi lấy audio phoneme
2. **Cache** được bật mặc định - tận dụng để tăng tốc
3. **Chọn voice phù hợp**:
   - Từ vựng: `us_female_clear`
   - Bài đọc: `us_male_professional`
   - Học sinh nhỏ: `us_female_young`
4. **Tốc độ phù hợp**:
   - Người mới: `beginner`
   - Người học lâu năm: `advanced`
5. **Sử dụng Celery** cho batch generation
6. **Cleanup** audio cũ định kỳ để tiết kiệm dung lượng

---

## ✨ Tính Năng Nổi Bật

✅ **Auto-generation**: Tự động tạo audio khi không có  
✅ **Smart fallback**: Native -> TTS -> Generated  
✅ **Multi-accent**: Mỹ, Anh, Úc, Canada  
✅ **Speed levels**: 6 mức tốc độ khác nhau  
✅ **Caching**: Cache thông minh, tối ưu performance  
✅ **Batch operations**: Tạo hàng loạt nhanh chóng  
✅ **Offline mode**: Mock TTS cho development  

---

## 📞 Support

Nếu có vấn đề:
1. Check logs: `logs/django.log`
2. Test với Mock mode: `MOCK_TTS=true`
3. Xem ví dụ trong `example_integration.py`

---

**Chúc bạn sử dụng thành công! 🎉**
