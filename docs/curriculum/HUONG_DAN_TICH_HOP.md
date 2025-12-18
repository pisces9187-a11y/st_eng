# Hướng Dẫn Tích Hợp Edge TTS cho Hệ Thống Học Tiếng Anh

## 📋 Tổng Quan
Edge TTS là API text-to-speech miễn phí của Microsoft, hỗ trợ nhiều giọng nói chất lượng cao. Hướng dẫn này giúp bạn tích hợp vào hệ thống học tiếng Anh.

---

## 🎯 Các Giọng Tiếng Anh Phổ Biến

### 🇺🇸 **Tiếng Anh Mỹ (en-US)** - Khuyên dùng cho học viên
| Tên Giọng | Giới Tính | Đặc Điểm | Phù Hợp Cho |
|-----------|-----------|----------|-------------|
| `en-US-AriaNeural` | Nữ | Giọng nữ rõ ràng, tự nhiên | Học từ vựng, hội thoại |
| `en-US-GuyNeural` | Nam | Giọng nam ấm, chuẩn | Bài đọc, câu chuyện |
| `en-US-JennyNeural` | Nữ | Giọng trẻ trung, năng động | Học sinh, thanh thiếu niên |
| `en-US-DavisNeural` | Nam | Giọng nam trầm, chuyên nghiệp | Nội dung học thuật |
| `en-US-AnaNeural` | Nữ (trẻ em) | Giọng em bé | Học viên nhỏ tuổi |

### 🇬🇧 **Tiếng Anh Anh (en-GB)** - Cho học viên muốn giọng British
| Tên Giọng | Giới Tính | Đặc Điểm |
|-----------|-----------|----------|
| `en-GB-SoniaNeural` | Nữ | Chuẩn BBC, sang trọng |
| `en-GB-RyanNeural` | Nam | Lịch lãm, chuyên nghiệp |
| `en-GB-LibbyNeural` | Nữ | Trẻ trung, hiện đại |

### 🇦🇺 **Tiếng Anh Úc (en-AU)**
- `en-AU-NatashaNeural` (Nữ)
- `en-AU-WilliamNeural` (Nam)

### 🇨🇦 **Tiếng Anh Canada (en-CA)**
- `en-CA-ClaraNeural` (Nữ)
- `en-CA-LiamNeural` (Nam)

### 🇮🇳 **Tiếng Anh Ấn Độ (en-IN)**
- `en-IN-NeerjaNeural` (Nữ)
- `en-IN-PrabhatNeural` (Nam)

---

## ⚡ Cài Đặt Nhanh

```bash
pip install edge-tts
```

---

## 🔧 Các Cách Tích Hợp

### **Phương Án 1: Tích Hợp Đơn Giản (Cơ Bản)**
Phù hợp cho: Ứng dụng nhỏ, chức năng phát âm từ vựng

```python
import edge_tts
import asyncio

async def text_to_speech_simple(text, voice="en-US-AriaNeural"):
    """
    Chuyển văn bản thành giọng nói và lưu file
    
    Args:
        text: Văn bản cần đọc
        voice: Tên giọng (mặc định: en-US-AriaNeural)
    
    Returns:
        Đường dẫn file audio
    """
    output_file = "output.mp3"
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)
    return output_file

# Sử dụng
asyncio.run(text_to_speech_simple("Hello, welcome to English learning!"))
```

### **Phương Án 2: Tích Hợp Với Tùy Chỉnh (Trung Cấp)**
Phù hợp cho: Tùy chỉnh tốc độ, cao độ giọng nói

```python
import edge_tts
import asyncio

async def text_to_speech_advanced(
    text, 
    voice="en-US-AriaNeural",
    rate=0,      # Tốc độ: -50 đến +50 (%)
    pitch=0,     # Cao độ: -20 đến +20 (Hz)
    output_file="output.mp3"
):
    """
    Chuyển văn bản với tùy chỉnh chi tiết
    
    Args:
        text: Văn bản cần đọc
        voice: Tên giọng
        rate: Tốc độ đọc (0 = bình thường, +10 = nhanh hơn 10%, -10 = chậm hơn 10%)
        pitch: Cao độ giọng (0 = bình thường)
        output_file: Tên file đầu ra
    
    Returns:
        Đường dẫn file audio
    """
    rate_str = f"{rate:+d}%"
    pitch_str = f"{pitch:+d}Hz"
    
    communicate = edge_tts.Communicate(
        text, 
        voice,
        rate=rate_str,
        pitch=pitch_str
    )
    
    await communicate.save(output_file)
    return output_file

# Sử dụng
asyncio.run(text_to_speech_advanced(
    "This is a slow speech for beginners",
    voice="en-US-JennyNeural",
    rate=-20,  # Chậm hơn 20% cho người mới học
    pitch=0
))
```

### **Phương Án 3: Class Tái Sử Dụng (Chuyên Nghiệp)**
Phù hợp cho: Hệ thống lớn, nhiều chức năng

```python
import edge_tts
import asyncio
from typing import Optional
import os

class EnglishTTS:
    """Class quản lý Text-to-Speech cho hệ thống học tiếng Anh"""
    
    # Danh sách giọng đề xuất
    VOICES = {
        "us_female_clear": "en-US-AriaNeural",      # Nữ Mỹ rõ ràng
        "us_male_standard": "en-US-GuyNeural",       # Nam Mỹ chuẩn
        "us_female_young": "en-US-JennyNeural",      # Nữ Mỹ trẻ
        "us_male_professional": "en-US-DavisNeural", # Nam Mỹ chuyên nghiệp
        "gb_female": "en-GB-SoniaNeural",            # Nữ Anh
        "gb_male": "en-GB-RyanNeural",               # Nam Anh
    }
    
    # Cấu hình tốc độ theo trình độ
    SPEED_LEVELS = {
        "beginner": -20,    # Người mới: chậm 20%
        "intermediate": 0,  # Trung cấp: bình thường
        "advanced": +10,    # Nâng cao: nhanh 10%
    }
    
    def __init__(self, output_dir: str = "audio_cache"):
        """
        Khởi tạo TTS engine
        
        Args:
            output_dir: Thư mục lưu file audio
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    async def generate_speech(
        self,
        text: str,
        voice_key: str = "us_female_clear",
        speed_level: str = "intermediate",
        filename: Optional[str] = None
    ) -> str:
        """
        Tạo file audio từ văn bản
        
        Args:
            text: Văn bản cần đọc
            voice_key: Key của giọng nói (xem VOICES)
            speed_level: Trình độ học viên (beginner/intermediate/advanced)
            filename: Tên file tùy chỉnh (không bao gồm đuôi)
        
        Returns:
            Đường dẫn file audio đã tạo
        """
        if not text.strip():
            raise ValueError("Text không được để trống")
        
        # Lấy voice name
        voice = self.VOICES.get(voice_key, self.VOICES["us_female_clear"])
        
        # Lấy tốc độ
        rate = self.SPEED_LEVELS.get(speed_level, 0)
        rate_str = f"{rate:+d}%"
        
        # Tạo tên file
        if filename is None:
            # Tạo tên file tự động từ hash của text
            import hashlib
            text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
            filename = f"{voice_key}_{speed_level}_{text_hash}"
        
        output_path = os.path.join(self.output_dir, f"{filename}.mp3")
        
        # Kiểm tra cache
        if os.path.exists(output_path):
            return output_path
        
        # Tạo audio
        communicate = edge_tts.Communicate(text, voice, rate=rate_str)
        await communicate.save(output_path)
        
        return output_path
    
    async def generate_word_pronunciation(
        self,
        word: str,
        accent: str = "us"  # "us" hoặc "gb"
    ) -> str:
        """
        Tạo audio phát âm từ vựng
        
        Args:
            word: Từ cần phát âm
            accent: Giọng Mỹ (us) hoặc Anh (gb)
        
        Returns:
            Đường dẫn file audio
        """
        voice_key = "us_female_clear" if accent == "us" else "gb_female"
        filename = f"word_{word.lower().replace(' ', '_')}_{accent}"
        
        return await self.generate_speech(
            text=word,
            voice_key=voice_key,
            speed_level="beginner",  # Phát âm từ thì chậm
            filename=filename
        )
    
    async def generate_sentence_audio(
        self,
        sentence: str,
        student_level: str = "intermediate",
        voice_type: str = "female"  # "female" hoặc "male"
    ) -> str:
        """
        Tạo audio cho câu
        
        Args:
            sentence: Câu cần đọc
            student_level: Trình độ học viên
            voice_type: Giọng nam/nữ
        
        Returns:
            Đường dẫn file audio
        """
        if voice_type == "female":
            voice_key = "us_female_clear"
        else:
            voice_key = "us_male_standard"
        
        return await self.generate_speech(
            text=sentence,
            voice_key=voice_key,
            speed_level=student_level
        )
    
    @staticmethod
    async def list_all_voices() -> list:
        """
        Lấy danh sách tất cả giọng nói có sẵn
        
        Returns:
            List các giọng nói
        """
        voices = await edge_tts.list_voices()
        return [
            {
                "name": v["ShortName"],
                "locale": v["Locale"],
                "gender": v["Gender"],
                "display": f"{v['ShortName']} - {v['Locale']} ({v['Gender']})"
            }
            for v in voices
            if v["Locale"].startswith("en-")  # Chỉ lấy giọng tiếng Anh
        ]


# ===== CÁCH SỬ DỤNG =====

async def main():
    # Khởi tạo TTS engine
    tts = EnglishTTS(output_dir="my_audio_files")
    
    # Ví dụ 1: Phát âm từ vựng
    word_audio = await tts.generate_word_pronunciation("beautiful", accent="us")
    print(f"Word audio: {word_audio}")
    
    # Ví dụ 2: Đọc câu cho người mới học
    sentence = "The weather is nice today."
    sentence_audio = await tts.generate_sentence_audio(
        sentence,
        student_level="beginner",
        voice_type="female"
    )
    print(f"Sentence audio: {sentence_audio}")
    
    # Ví dụ 3: Đọc đoạn văn cho người nâng cao
    paragraph = """
    Machine learning is a subset of artificial intelligence. 
    It enables computers to learn from data without being explicitly programmed.
    """
    advanced_audio = await tts.generate_speech(
        text=paragraph,
        voice_key="us_male_professional",
        speed_level="advanced"
    )
    print(f"Advanced audio: {advanced_audio}")
    
    # Ví dụ 4: Lấy danh sách tất cả giọng tiếng Anh
    all_voices = await tts.list_all_voices()
    print(f"\nCó {len(all_voices)} giọng tiếng Anh:")
    for v in all_voices[:5]:  # In 5 giọng đầu
        print(f"  - {v['display']}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🎓 Use Cases Cụ Thể Cho Học Tiếng Anh

### 1️⃣ **Flashcard Học Từ Vựng**
```python
async def create_flashcard_audio(word, definition, example):
    tts = EnglishTTS()
    
    # Phát âm từ
    word_audio = await tts.generate_word_pronunciation(word)
    
    # Đọc định nghĩa
    definition_audio = await tts.generate_speech(
        definition,
        voice_key="us_female_clear",
        speed_level="beginner"
    )
    
    # Đọc ví dụ
    example_audio = await tts.generate_sentence_audio(
        example,
        student_level="intermediate"
    )
    
    return {
        "word": word_audio,
        "definition": definition_audio,
        "example": example_audio
    }
```

### 2️⃣ **Luyện Nghe Với Nhiều Giọng**
```python
async def create_listening_exercise(text, num_voices=3):
    """Tạo cùng nội dung với nhiều giọng khác nhau"""
    tts = EnglishTTS()
    voices = ["us_female_clear", "us_male_standard", "gb_female"]
    
    audio_files = []
    for voice in voices[:num_voices]:
        audio = await tts.generate_speech(
            text,
            voice_key=voice,
            speed_level="intermediate"
        )
        audio_files.append(audio)
    
    return audio_files
```

### 3️⃣ **Dictation (Chính Tả)**
```python
async def create_dictation_levels(sentence):
    """Tạo 3 mức độ: chậm -> bình thường -> nhanh"""
    tts = EnglishTTS()
    
    levels = {
        "slow": await tts.generate_speech(
            sentence, 
            speed_level="beginner"
        ),
        "normal": await tts.generate_speech(
            sentence,
            speed_level="intermediate"
        ),
        "fast": await tts.generate_speech(
            sentence,
            speed_level="advanced"
        )
    }
    
    return levels
```

### 4️⃣ **So Sánh Giọng Mỹ vs Anh**
```python
async def compare_accents(word_or_sentence):
    tts = EnglishTTS()
    
    us_audio = await tts.generate_speech(
        word_or_sentence,
        voice_key="us_female_clear"
    )
    
    gb_audio = await tts.generate_speech(
        word_or_sentence,
        voice_key="gb_female"
    )
    
    return {"american": us_audio, "british": gb_audio}
```

---

## 💡 Lưu Ý Quan Trọng

### ✅ **Nên Làm**
1. **Cache audio**: Lưu file đã tạo để tránh tạo lại
2. **Xử lý bất đồng bộ**: Dùng `async/await` cho hiệu suất tốt
3. **Tùy chỉnh tốc độ**: 
   - Người mới: `-20%` đến `-30%`
   - Trung cấp: `0%`
   - Nâng cao: `+10%` đến `+20%`
4. **Chọn giọng phù hợp**:
   - Học sinh nhỏ: `JennyNeural`, `AnaNeural`
   - Người lớn: `AriaNeural`, `GuyNeural`
   - Học thuật: `DavisNeural`

### ❌ **Tránh Làm**
1. Không dùng `asyncio.run()` nhiều lần trong cùng 1 chương trình
2. Không tạo audio cho văn bản quá dài (>5000 ký tự) - nên chia nhỏ
3. Không quên xử lý lỗi khi mạng không ổn định

### ⚠️ **Giới Hạn**
- **Miễn phí**: Không giới hạn, nhưng cần internet
- **Độ trễ**: ~1-3 giây cho câu ngắn
- **Chất lượng**: MP3, tốt cho học tập

---

## 🔌 Tích Hợp Với Framework

### **Flask/FastAPI**
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
tts = EnglishTTS()

class TTSRequest(BaseModel):
    text: str
    voice: str = "us_female_clear"
    level: str = "intermediate"

@app.post("/api/tts")
async def generate_tts(request: TTSRequest):
    try:
        audio_path = await tts.generate_speech(
            request.text,
            voice_key=request.voice,
            speed_level=request.level
        )
        return {"audio_url": f"/audio/{os.path.basename(audio_path)}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### **Django**
```python
from django.http import JsonResponse
from asgiref.sync import async_to_sync
import asyncio

def generate_audio_view(request):
    text = request.POST.get('text')
    voice = request.POST.get('voice', 'us_female_clear')
    
    tts = EnglishTTS()
    audio_path = async_to_sync(tts.generate_speech)(
        text,
        voice_key=voice
    )
    
    return JsonResponse({"audio_url": f"/media/audio/{os.path.basename(audio_path)}"})
```

---

## 📊 So Sánh Giọng Nói

| Giọng | Tốc Độ Tự Nhiên | Độ Rõ Ràng | Phù Hợp Học |
|-------|------------------|------------|-------------|
| AriaNeural (US-F) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ Tốt nhất |
| GuyNeural (US-M) | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ Rất tốt |
| JennyNeural (US-F) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ Tốt (Trẻ) |
| SoniaNeural (GB-F) | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ Anh chuẩn |

---

## 🚀 Bắt Đầu Nhanh (Quick Start)

```python
import edge_tts
import asyncio

# Code tối thiểu để chạy
async def quick_demo():
    text = "Hello! Welcome to English learning with Edge TTS."
    communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
    await communicate.save("hello.mp3")
    print("✅ Audio saved to hello.mp3")

asyncio.run(quick_demo())
```

---

## 📞 Hỗ Trợ

- **Lỗi thường gặp**: Kiểm tra kết nối internet
- **Giọng không hoạt động**: Dùng `edge_tts.list_voices()` để xem danh sách mới nhất
- **Performance**: Dùng caching và xử lý background tasks

---

**Chúc bạn tích hợp thành công! 🎉**
