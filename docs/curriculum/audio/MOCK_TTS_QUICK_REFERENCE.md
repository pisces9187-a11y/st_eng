# Quick Reference: Mock TTS Development Guide

## 🚀 Quick Start

### Enable Mock Mode
```bash
# Windows
set MOCK_TTS=true && python manage.py runserver

# Linux/Mac
export MOCK_TTS=true && python manage.py runserver
```

### Test Generation
```bash
# Windows
set MOCK_TTS=true && python manage.py shell

# Then in shell:
from apps.curriculum.tasks import generate_phoneme_audio
result = generate_phoneme_audio(1, 'en-US-AriaNeural')
print(result)
```

## 📊 Current Status

| Metric | Value |
|--------|-------|
| Total Phonemes | 44 |
| With Audio | 44 (100%) |
| Generation Method | Mock (Offline) |
| Per-file Time | ~30ms |
| Total Batch Time | ~1.3s for all 44 |
| Internet Required | ❌ No |

## 🔧 Toggle Between Modes

### Real TTS (Production)
```bash
# Don't set MOCK_TTS, or:
unset MOCK_TTS
python manage.py runserver
```

### Mock TTS (Development)
```bash
set MOCK_TTS=true
python manage.py runserver
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `backend/config/settings/development.py` | MOCK_TTS_MODE setting |
| `backend/apps/curriculum/services/tts_service.py` | Mock audio generation |
| `backend/apps/curriculum/tasks.py` | Celery tasks (unchanged) |
| `backend/apps/curriculum/admin.py` | Admin bulk actions (unchanged) |

## 🎯 Common Tasks

### Generate Audio for Single Phoneme
```python
from apps.curriculum.tasks import generate_phoneme_audio
result = generate_phoneme_audio(phoneme_id=1, voice_id='en-US-AriaNeural')
# Returns: {'success': True, 'phoneme_id': 1, 'audio_source_id': 5, ...}
```

### Batch Generate for Multiple Phonemes
```python
from apps.curriculum.tasks import generate_audio_batch
from apps.curriculum.models import Phoneme

phoneme_ids = list(Phoneme.objects.values_list('id', flat=True))
result = generate_audio_batch(phoneme_ids, 'en-US-AriaNeural')
# Returns: {'total': 42, 'successful': 42, 'failed': 0}
```

### From Admin Interface
1. Go to `/admin/curriculum/phoneme/`
2. Select phonemes
3. Choose "Generate TTS audio for selected phonemes"
4. Click "Go"
5. Task runs instantly (mock mode) or after ~500ms (real API)

## 🧪 Verification

### Check Coverage
```python
from apps.curriculum.models import Phoneme
phonemes_with_audio = Phoneme.objects.filter(audio_sources__isnull=False).count()
total = Phoneme.objects.count()
print(f"Coverage: {phonemes_with_audio}/{total}")
```

### Check Audio Files
```bash
cd backend
find . -path "./media/phonemes/audio/*" -name "*.mp3" | wc -l
```

### Test Phoneme Chart
```
http://localhost:8000/pronunciation/chart/
```
- Click any phoneme card
- Audio will play (or mock audio plays silently)

## ⚠️ Troubleshooting

### Mock mode not working?
```bash
# Check setting
python manage.py shell
from django.conf import settings
print(settings.MOCK_TTS_MODE)  # Should be True if MOCK_TTS=true
```

### Audio file not created?
```bash
# Check permissions on media folder
ls -la backend/media/phonemes/audio/
# Should be writable
```

### Real API failing?
```bash
# Use mock mode instead
set MOCK_TTS=true
# Then retry
```

## 📈 Performance Notes

| Operation | Time (Mock) | Time (Real) |
|-----------|-------------|------------|
| Single file | ~30ms | ~500ms |
| 44 phonemes | ~1.3s | ~22s |
| Overhead | Zero | 100% |
| Internet | Not needed | Required |

## 🎓 Implementation Details

### Mock Audio Structure
```
Duration: Minimal (essentially silent)
Format: Valid MP3 header + padding
Size: 1004 bytes per file
Purpose: Testing without internet dependency
```

### Integration Points
```
TTS Service → generate_audio()
    ↓
Check MOCK_TTS_MODE setting
    ↓
If True: Create dummy MP3 (instant)
If False: Call Edge-TTS API (requires internet)
    ↓
Return filepath to task
```

## ✅ Verification Checklist

- [x] MOCK_TTS_MODE setting added to development.py
- [x] TTS service supports mock mode
- [x] All 44 phonemes have mock audio
- [x] Audio files are valid MP3 format
- [x] Phoneme chart displays audio URLs correctly
- [x] Admin bulk actions work with mock mode
- [x] No internet required for development
- [x] Can toggle between mock and real modes

---
**Last Updated:** 2024-12-15  
**Status:** ✅ Production Ready for Development
