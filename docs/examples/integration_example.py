# ======================================================================
# EXAMPLE INTEGRATION - Ví dụ tích hợp Edge TTS cho hệ thống học tiếng Anh
# ======================================================================

import edge_tts
import asyncio
from typing import Optional, List, Dict
import os
import hashlib

class EnglishTTS:
    """
    Class quản lý Text-to-Speech cho hệ thống học tiếng Anh
    Hỗ trợ nhiều giọng nói, tùy chỉnh tốc độ theo trình độ học viên
    """
    
    # Danh sách giọng đề xuất cho học tiếng Anh
    VOICES = {
        # Giọng Mỹ (American English) - Phổ biến nhất
        "us_female_clear": "en-US-AriaNeural",          # 👍 Khuyên dùng - Nữ, rõ ràng nhất
        "us_male_standard": "en-US-GuyNeural",          # 👍 Khuyên dùng - Nam, chuẩn
        "us_female_young": "en-US-JennyNeural",         # Nữ, trẻ trung
        "us_male_professional": "en-US-DavisNeural",    # Nam, chuyên nghiệp
        "us_female_child": "en-US-AnaNeural",           # Giọng trẻ em
        
        # Giọng Anh (British English)
        "gb_female": "en-GB-SoniaNeural",               # 👍 Nữ, chuẩn BBC
        "gb_male": "en-GB-RyanNeural",                  # 👍 Nam, lịch lãm
        "gb_female_modern": "en-GB-LibbyNeural",        # Nữ, hiện đại
        
        # Giọng Úc (Australian)
        "au_female": "en-AU-NatashaNeural",
        "au_male": "en-AU-WilliamNeural",
        
        # Giọng Canada
        "ca_female": "en-CA-ClaraNeural",
        "ca_male": "en-CA-LiamNeural",
        
        # Giọng Ấn Độ (Indian English)
        "in_female": "en-IN-NeerjaNeural",
        "in_male": "en-IN-PrabhatNeural",
    }
    
    # Cấu hình tốc độ đọc theo trình độ học viên
    SPEED_LEVELS = {
        "beginner": -25,        # Người mới: chậm 25%
        "elementary": -15,      # Sơ cấp: chậm 15%
        "intermediate": 0,      # Trung cấp: bình thường
        "upper_intermediate": +5,  # Trung cấp cao: nhanh 5%
        "advanced": +10,        # Nâng cao: nhanh 10%
    }
    
    def __init__(self, output_dir: str = "audio_cache"):
        """
        Khởi tạo TTS engine
        
        Args:
            output_dir: Thư mục lưu file audio (sẽ tự tạo nếu chưa có)
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    async def generate_speech(
        self,
        text: str,
        voice_key: str = "us_female_clear",
        speed_level: str = "intermediate",
        pitch: int = 0,
        filename: Optional[str] = None
    ) -> str:
        """
        Tạo file audio từ văn bản
        
        Args:
            text: Văn bản cần đọc
            voice_key: Key của giọng nói (xem VOICES)
            speed_level: Trình độ học viên (beginner/intermediate/advanced)
            pitch: Cao độ giọng (-20 đến +20 Hz, 0 = mặc định)
            filename: Tên file tùy chỉnh (không bao gồm đuôi .mp3)
        
        Returns:
            Đường dẫn file audio đã tạo
            
        Raises:
            ValueError: Nếu text rỗng hoặc voice_key không hợp lệ
        """
        if not text.strip():
            raise ValueError("Text không được để trống")
        
        # Lấy voice name
        voice = self.VOICES.get(voice_key)
        if not voice:
            raise ValueError(f"Voice key không hợp lệ: {voice_key}")
        
        # Lấy tốc độ
        rate = self.SPEED_LEVELS.get(speed_level, 0)
        rate_str = f"{rate:+d}%"
        pitch_str = f"{pitch:+d}Hz"
        
        # Tạo tên file
        if filename is None:
            # Tạo tên file tự động từ hash của text
            text_hash = hashlib.md5(text.encode()).hexdigest()[:10]
            filename = f"{voice_key}_{speed_level}_{text_hash}"
        
        output_path = os.path.join(self.output_dir, f"{filename}.mp3")
        
        # Kiểm tra cache - nếu file đã tồn tại thì không tạo lại
        if os.path.exists(output_path):
            print(f"✅ Sử dụng cache: {output_path}")
            return output_path
        
        # Tạo audio mới
        print(f"🔊 Đang tạo audio: {filename}.mp3...")
        communicate = edge_tts.Communicate(text, voice, rate=rate_str, pitch=pitch_str)
        await communicate.save(output_path)
        print(f"✅ Đã tạo: {output_path}")
        
        return output_path
    
    async def generate_word_pronunciation(
        self,
        word: str,
        accent: str = "us",  # "us" hoặc "gb"
        repeat: int = 1      # Số lần lặp lại
    ) -> str:
        """
        Tạo audio phát âm từ vựng
        
        Args:
            word: Từ cần phát âm
            accent: Giọng Mỹ (us) hoặc Anh (gb)
            repeat: Số lần lặp lại từ (mặc định: 1)
        
        Returns:
            Đường dẫn file audio
        """
        # Chọn giọng phù hợp
        voice_key = "us_female_clear" if accent == "us" else "gb_female"
        
        # Lặp lại từ nếu cần
        text = " ... ".join([word] * repeat)
        
        filename = f"word_{word.lower().replace(' ', '_')}_{accent}"
        
        return await self.generate_speech(
            text=text,
            voice_key=voice_key,
            speed_level="beginner",  # Phát âm từ thì chậm hơn
            filename=filename
        )
    
    async def generate_sentence_audio(
        self,
        sentence: str,
        student_level: str = "intermediate",
        voice_type: str = "female",  # "female" hoặc "male"
        accent: str = "us"           # "us" hoặc "gb"
    ) -> str:
        """
        Tạo audio cho câu
        
        Args:
            sentence: Câu cần đọc
            student_level: Trình độ học viên
            voice_type: Giọng nam/nữ
            accent: Giọng Mỹ/Anh
        
        Returns:
            Đường dẫn file audio
        """
        # Chọn giọng phù hợp
        if accent == "us":
            voice_key = "us_female_clear" if voice_type == "female" else "us_male_standard"
        else:
            voice_key = "gb_female" if voice_type == "female" else "gb_male"
        
        return await self.generate_speech(
            text=sentence,
            voice_key=voice_key,
            speed_level=student_level
        )
    
    async def generate_conversation(
        self,
        dialogues: List[Dict[str, str]],
        student_level: str = "intermediate"
    ) -> List[str]:
        """
        Tạo audio cho hội thoại (nhiều người)
        
        Args:
            dialogues: List các dict {"speaker": "A/B", "text": "..."}
            student_level: Trình độ học viên
        
        Returns:
            List đường dẫn các file audio
        
        Example:
            dialogues = [
                {"speaker": "A", "text": "Hello, how are you?"},
                {"speaker": "B", "text": "I'm fine, thank you!"}
            ]
        """
        audio_files = []
        
        for i, dialogue in enumerate(dialogues):
            speaker = dialogue["speaker"]
            text = dialogue["text"]
            
            # Xen kẽ giọng nam/nữ
            voice_key = "us_female_clear" if speaker == "A" else "us_male_standard"
            
            audio_path = await self.generate_speech(
                text=text,
                voice_key=voice_key,
                speed_level=student_level,
                filename=f"dialogue_{i}_{speaker}"
            )
            
            audio_files.append(audio_path)
        
        return audio_files
    
    @staticmethod
    async def list_all_english_voices() -> List[Dict]:
        """
        Lấy danh sách TẤT CẢ giọng tiếng Anh có sẵn từ Edge TTS
        
        Returns:
            List các giọng nói tiếng Anh
        """
        print("📋 Đang lấy danh sách giọng nói...")
        voices = await edge_tts.list_voices()
        
        english_voices = [
            {
                "name": v["ShortName"],
                "locale": v["Locale"],
                "gender": v["Gender"],
                "display": f"{v['ShortName']} - {v['Locale']} ({v['Gender']})"
            }
            for v in voices
            if v["Locale"].startswith("en-")  # Chỉ lấy giọng tiếng Anh
        ]
        
        return english_voices


# ======================================================================
# CÁC VÍ DỤ SỬ DỤNG THỰC TẾ
# ======================================================================

async def example_1_word_pronunciation():
    """Ví dụ 1: Phát âm từ vựng"""
    print("\n" + "="*60)
    print("VÍ DỤ 1: PHÁT ÂM TỪ VỰNG")
    print("="*60)
    
    tts = EnglishTTS()
    
    words = ["beautiful", "pronunciation", "education"]
    
    for word in words:
        # Phát âm giọng Mỹ
        us_audio = await tts.generate_word_pronunciation(word, accent="us", repeat=2)
        print(f"✅ {word} (US): {us_audio}")
        
        # Phát âm giọng Anh
        gb_audio = await tts.generate_word_pronunciation(word, accent="gb", repeat=2)
        print(f"✅ {word} (GB): {gb_audio}")


async def example_2_sentences_by_level():
    """Ví dụ 2: Tạo audio câu với các trình độ khác nhau"""
    print("\n" + "="*60)
    print("VÍ DỤ 2: AUDIO CÂU THEO TRÌNH ĐỘ")
    print("="*60)
    
    tts = EnglishTTS()
    
    sentence = "The weather is beautiful today. Let's go for a walk in the park."
    
    levels = ["beginner", "intermediate", "advanced"]
    
    for level in levels:
        audio = await tts.generate_sentence_audio(
            sentence,
            student_level=level,
            voice_type="female"
        )
        print(f"✅ {level.upper()}: {audio}")


async def example_3_conversation():
    """Ví dụ 3: Tạo hội thoại 2 người"""
    print("\n" + "="*60)
    print("VÍ DỤ 3: HỘI THOẠI 2 NGƯỜI")
    print("="*60)
    
    tts = EnglishTTS()
    
    dialogues = [
        {"speaker": "A", "text": "Hi John! How was your weekend?"},
        {"speaker": "B", "text": "It was great! I went hiking with my family."},
        {"speaker": "A", "text": "That sounds wonderful! Where did you go?"},
        {"speaker": "B", "text": "We went to the mountains. The view was amazing!"},
    ]
    
    audio_files = await tts.generate_conversation(dialogues, student_level="intermediate")
    
    for i, audio in enumerate(audio_files):
        speaker = dialogues[i]["speaker"]
        print(f"✅ Speaker {speaker}: {audio}")


async def example_4_reading_passage():
    """Ví dụ 4: Đọc đoạn văn dài (IELTS/TOEFL style)"""
    print("\n" + "="*60)
    print("VÍ DỤ 4: ĐỌC ĐOẠN VĂN DÀI")
    print("="*60)
    
    tts = EnglishTTS()
    
    passage = """
    Climate change is one of the most pressing issues facing our planet today.
    Rising temperatures are causing ice caps to melt, leading to higher sea levels.
    Scientists around the world are working together to find solutions.
    We must take action now to protect our environment for future generations.
    """
    
    # Tạo cho người học nâng cao
    audio = await tts.generate_speech(
        text=passage.strip(),
        voice_key="us_male_professional",
        speed_level="advanced",
        filename="reading_passage_climate"
    )
    
    print(f"✅ Reading passage: {audio}")


async def example_5_compare_voices():
    """Ví dụ 5: So sánh nhiều giọng nói cho cùng một câu"""
    print("\n" + "="*60)
    print("VÍ DỤ 5: SO SÁNH GIỌNG NÓI")
    print("="*60)
    
    tts = EnglishTTS()
    
    sentence = "Welcome to our English learning platform!"
    
    voices = [
        "us_female_clear",
        "us_male_standard",
        "gb_female",
        "gb_male"
    ]
    
    for voice in voices:
        audio = await tts.generate_speech(
            text=sentence,
            voice_key=voice,
            speed_level="intermediate",
            filename=f"compare_{voice}"
        )
        print(f"✅ {voice}: {audio}")


async def example_6_list_all_voices():
    """Ví dụ 6: Xem tất cả giọng tiếng Anh có sẵn"""
    print("\n" + "="*60)
    print("VÍ DỤ 6: DANH SÁCH TẤT CẢ GIỌNG TIẾNG ANH")
    print("="*60)
    
    voices = await EnglishTTS.list_all_english_voices()
    
    print(f"\n📊 Tổng cộng: {len(voices)} giọng tiếng Anh\n")
    
    # Nhóm theo locale
    locales = {}
    for v in voices:
        locale = v["locale"]
        if locale not in locales:
            locales[locale] = []
        locales[locale].append(v)
    
    # In ra theo từng locale
    for locale, voice_list in sorted(locales.items()):
        print(f"\n🌍 {locale}:")
        for v in voice_list:
            print(f"   - {v['name']} ({v['gender']})")


async def example_7_flashcard_system():
    """Ví dụ 7: Hệ thống flashcard hoàn chỉnh"""
    print("\n" + "="*60)
    print("VÍ DỤ 7: HỆ THỐNG FLASHCARD")
    print("="*60)
    
    tts = EnglishTTS()
    
    flashcard = {
        "word": "perseverance",
        "definition": "continued effort to do or achieve something despite difficulties",
        "example": "Her perseverance led to success in her career.",
        "synonyms": ["persistence", "determination"]
    }
    
    # 1. Phát âm từ
    word_audio = await tts.generate_word_pronunciation(
        flashcard["word"],
        accent="us",
        repeat=2
    )
    print(f"✅ Word: {word_audio}")
    
    # 2. Đọc định nghĩa
    definition_audio = await tts.generate_speech(
        text=flashcard["definition"],
        voice_key="us_female_clear",
        speed_level="beginner",
        filename=f"def_{flashcard['word']}"
    )
    print(f"✅ Definition: {definition_audio}")
    
    # 3. Đọc ví dụ
    example_audio = await tts.generate_sentence_audio(
        sentence=flashcard["example"],
        student_level="intermediate",
        voice_type="female"
    )
    print(f"✅ Example: {example_audio}")
    
    # 4. Đọc từ đồng nghĩa
    synonyms_text = f"Synonyms: {', '.join(flashcard['synonyms'])}"
    synonyms_audio = await tts.generate_speech(
        text=synonyms_text,
        voice_key="us_female_clear",
        speed_level="intermediate",
        filename=f"syn_{flashcard['word']}"
    )
    print(f"✅ Synonyms: {synonyms_audio}")


# ======================================================================
# MAIN - Chạy tất cả ví dụ
# ======================================================================

async def main():
    """Chạy tất cả ví dụ"""
    print("\n" + "="*60)
    print("🎓 EDGE TTS - VÍ DỤ TÍCH HỢP CHO HỆ THỐNG HỌC TIẾNG ANH")
    print("="*60)
    
    # Chạy từng ví dụ
    await example_1_word_pronunciation()
    await example_2_sentences_by_level()
    await example_3_conversation()
    await example_4_reading_passage()
    await example_5_compare_voices()
    await example_6_list_all_voices()
    await example_7_flashcard_system()
    
    print("\n" + "="*60)
    print("✅ HOÀN THÀNH TẤT CẢ VÍ DỤ!")
    print("="*60)
    print(f"\n📁 Tất cả file audio đã được lưu trong thư mục: audio_cache/")
    print("💡 Bạn có thể sử dụng các ví dụ trên để tích hợp vào hệ thống của mình!")


if __name__ == "__main__":
    # Chạy chương trình
    asyncio.run(main())
