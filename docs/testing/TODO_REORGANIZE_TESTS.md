# TODO: Reorganize Remaining Test Files

**Priority:** Medium
**Estimated Time:** 30 minutes

---

## 📋 Files cần di chuyển

### Root folder test files (legacy):
```
test_real_edge_tts.py           → backend/tests/curriculum/services/
test_quick_phoneme.py           → backend/tests/curriculum/
test_pages_quick.py             → backend/tests/curriculum/views/
test_oxford_parser.py           → backend/tests/vocabulary/
test_mock_mode.py               → backend/tests/curriculum/services/
test_edge_tts_phonemes.py       → backend/tests/curriculum/services/
```

### Backend/ folder test files:
```
backend/test_api_complete.py              → backend/tests/curriculum/api/
backend/test_pronunciation_api_quick.py   → backend/tests/curriculum/api/
backend/test_edge_tts.py                  → backend/tests/curriculum/services/
```

---

## ✅ Checklist for each file

- [ ] Di chuyển file vào đúng folder trong `backend/tests/`
- [ ] Sửa imports (thêm backend_path resolution)
- [ ] Rename file theo convention: `test_{feature}_{type}.py`
- [ ] Run test để verify
- [ ] Xóa file cũ

---

## 🔧 Template để sửa imports

```python
"""
Test description
"""
import os
import sys
import django

# Add backend to path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, backend_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

# Rest of imports...
```

---

## 📝 Notes

- Đây là test files từ curriculum app (Edge TTS, phonemes, pronunciation)
- Không urgent vì các tests này đã hoạt động
- Nên di chuyển khi có thời gian để maintain consistency
- Vocabulary app đã tuân thủ đúng 100% ✅

---

**Created:** 2025-12-19
**Status:** Pending
