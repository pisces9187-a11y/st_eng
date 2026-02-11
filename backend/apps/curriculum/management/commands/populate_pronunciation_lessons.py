"""
Populate all pronunciation lessons with proper structure.

Parts:
- Part 1: Monophthongs (Nguyên âm đơn) - 12 phonemes
- Part 2: Diphthongs (Nguyên âm đôi) - 8 phonemes  
- Part 3: Consonants (Phụ âm) - 24 phonemes

All lessons are published (unlocked) by default.
"""

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.curriculum.models import PronunciationLesson, Phoneme


class Command(BaseCommand):
    help = 'Populate all pronunciation lessons for IPA phonemes'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting to populate pronunciation lessons...'))
        
        # Part 1: Monophthongs (Nguyên âm đơn)
        self.create_monophthong_lessons()
        
        # Part 2: Diphthongs (Nguyên âm đôi)
        self.create_diphthong_lessons()
        
        # Part 3: Consonants (Phụ âm)
        self.create_consonant_lessons()
        
        self.stdout.write(self.style.SUCCESS('✅ All pronunciation lessons created successfully!'))
        
        # Print summary
        total = PronunciationLesson.objects.filter(status='published').count()
        self.stdout.write(self.style.SUCCESS(f'\n📊 Total published lessons: {total}'))

    def create_monophthong_lessons(self):
        """Create lessons for monophthongs (single vowels)."""
        self.stdout.write(self.style.WARNING('\n📘 Part 1: Creating Monophthong Lessons...'))
        
        lessons_data = [
            # Unit 1: Short vowels - High position
            {
                'unit': 1,
                'slug': 'short-vowels-i-u',
                'title': 'Short High Vowels: /ɪ/ vs /ʊ/',
                'title_vi': 'Nguyên âm ngắn cao: /ɪ/ và /ʊ/',
                'description': 'Learn the difference between short high vowels /ɪ/ (as in "sit") and /ʊ/ (as in "book")',
                'description_vi': 'Học phân biệt các nguyên âm ngắn ở vị trí cao: /ɪ/ (như "sit") và /ʊ/ (như "book"). Hai âm này đều ngắn và ở vị trí cao trong miệng.',
                'phonemes': ['ɪ', 'ʊ'],
                'objectives': [
                    'Hiểu sự khác biệt giữa /ɪ/ (môi rộng) và /ʊ/ (môi tròn)',
                    'Phát âm chuẩn các từ chứa /ɪ/ và /ʊ/',
                    'Phân biệt được hai âm này khi nghe'
                ],
                'difficulty': 1,
                'estimated_minutes': 12,
            },
            # Unit 2: Short vowels - Mid position
            {
                'unit': 2,
                'slug': 'short-vowels-e-schwa',
                'title': 'Short Mid Vowels: /e/ vs /ə/',
                'title_vi': 'Nguyên âm ngắn giữa: /e/ và /ə/',
                'description': 'Master the short mid vowels /e/ (as in "bed") and /ə/ (as in "about")',
                'description_vi': 'Nắm vững các nguyên âm ngắn ở vị trí giữa: /e/ (như "bed") và /ə/ (schwa - âm yếu nhất trong tiếng Anh). Schwa xuất hiện rất nhiều trong từ đa âm tiết.',
                'phonemes': ['e', 'ə'],
                'objectives': [
                    'Nhận biết âm /ə/ (schwa) - âm xuất hiện nhiều nhất',
                    'Phát âm chuẩn /e/ với độ mở miệng vừa phải',
                    'Hiểu khi nào dùng schwa trong từ đa âm tiết'
                ],
                'difficulty': 2,
                'estimated_minutes': 15,
            },
            # Unit 3: Short vowels - Low position
            {
                'unit': 3,
                'slug': 'short-vowels-ae-a',
                'title': 'Short Low Vowels: /æ/ vs /ʌ/',
                'title_vi': 'Nguyên âm ngắn thấp: /æ/ và /ʌ/',
                'description': 'Learn the low short vowels /æ/ (as in "cat") and /ʌ/ (as in "cup")',
                'description_vi': 'Học các nguyên âm ngắn ở vị trí thấp: /æ/ (như "cat" - miệng mở rộng) và /ʌ/ (như "cup" - miệng mở vừa). Hai âm này người Việt thường nhầm lẫn.',
                'phonemes': ['æ', 'ʌ'],
                'objectives': [
                    'Mở miệng đủ rộng khi phát âm /æ/',
                    'Phân biệt /ʌ/ (ngắn) với /ɑː/ (dài)',
                    'Luyện tập các từ thông dụng chứa /æ/ và /ʌ/'
                ],
                'difficulty': 2,
                'estimated_minutes': 15,
            },
            # Unit 4: Long vowels - High position
            {
                'unit': 4,
                'slug': 'long-vowels-i-u',
                'title': 'Long High Vowels: /iː/ vs /uː/',
                'title_vi': 'Nguyên âm dài cao: /iː/ và /uː/',
                'description': 'Master the long high vowels /iː/ (as in "see") and /uː/ (as in "food")',
                'description_vi': 'Nắm vững các nguyên âm dài ở vị trí cao: /iː/ (như "see") và /uː/ (như "food"). Độ dài là yếu tố quan trọng để phân biệt nghĩa.',
                'phonemes': ['iː', 'uː'],
                'objectives': [
                    'Kéo dài âm đủ 2-3 đơn vị thời gian',
                    'So sánh với âm ngắn /ɪ/ và /ʊ/',
                    'Phát âm chuẩn các từ một âm tiết và đa âm tiết'
                ],
                'difficulty': 1,
                'estimated_minutes': 12,
            },
            # Unit 5: Long vowels - Mid-low position
            {
                'unit': 5,
                'slug': 'long-vowels-a-o',
                'title': 'Long Vowels: /ɑː/ vs /ɔː/',
                'title_vi': 'Nguyên âm dài: /ɑː/ và /ɔː/',
                'description': 'Learn the long vowels /ɑː/ (as in "car") and /ɔː/ (as in "door")',
                'description_vi': 'Học các nguyên âm dài: /ɑː/ (như "car" - miệng mở rộng) và /ɔː/ (như "door" - môi tròn). Hai âm này cần giữ độ dài ổn định.',
                'phonemes': ['ɑː', 'ɔː'],
                'objectives': [
                    'Giữ độ dài ổn định trong suốt quá trình phát âm',
                    'Phân biệt /ɑː/ (miệng rộng) và /ɔː/ (môi tròn)',
                    'Nhận diện các chính tả khác nhau của cùng một âm'
                ],
                'difficulty': 2,
                'estimated_minutes': 15,
            },
            # Unit 6: Long vowel - Central position
            {
                'unit': 6,
                'slug': 'long-vowel-er',
                'title': 'Long Central Vowel: /ɜː/',
                'title_vi': 'Nguyên âm dài giữa: /ɜː/',
                'description': 'Master the long central vowel /ɜː/ (as in "bird", "work", "learn")',
                'description_vi': 'Nắm vững nguyên âm dài ở vị trí giữa: /ɜː/ (như trong "bird", "work", "learn"). Đây là âm đặc trưng của tiếng Anh, không có trong tiếng Việt.',
                'phonemes': ['ɜː'],
                'objectives': [
                    'Phát âm chuẩn âm /ɜː/ - âm đặc trưng tiếng Anh',
                    'Nhận biết các chính tả khác nhau: -ir-, -ur-, -ear-, -or-',
                    'Không nhầm lẫn với /əː/ hay /ɔː/'
                ],
                'difficulty': 3,
                'estimated_minutes': 15,
            },
        ]
        
        for data in lessons_data:
            self._create_lesson(part=1, **data)

    def create_diphthong_lessons(self):
        """Create lessons for diphthongs (double vowels)."""
        self.stdout.write(self.style.WARNING('\n📗 Part 2: Creating Diphthong Lessons...'))
        
        lessons_data = [
            # Unit 1: Closing diphthongs - ending in /ɪ/
            {
                'unit': 1,
                'slug': 'diphthongs-closing-i',
                'title': 'Closing Diphthongs: /eɪ/ /aɪ/ /ɔɪ/',
                'title_vi': 'Nguyên âm đôi kết thúc bằng /ɪ/: /eɪ/ /aɪ/ /ɔɪ/',
                'description': 'Learn diphthongs that end with /ɪ/ sound: /eɪ/ (day), /aɪ/ (my), /ɔɪ/ (boy)',
                'description_vi': 'Học các nguyên âm đôi kết thúc bằng âm /ɪ/: /eɪ/ (như "day"), /aɪ/ (như "my"), /ɔɪ/ (như "boy"). Âm đầu mạnh, âm cuối yếu dần.',
                'phonemes': ['eɪ', 'aɪ', 'ɔɪ'],
                'objectives': [
                    'Hiểu nguyên tắc "âm đầu mạnh, âm cuối yếu"',
                    'Trượt âm mượt mà từ vị trí đầu sang vị trí cuối',
                    'Phân biệt /eɪ/ /aɪ/ /ɔɪ/ qua vị trí bắt đầu'
                ],
                'difficulty': 2,
                'estimated_minutes': 18,
            },
            # Unit 2: Closing diphthongs - ending in /ʊ/
            {
                'unit': 2,
                'slug': 'diphthongs-closing-u',
                'title': 'Closing Diphthongs: /aʊ/ /əʊ/',
                'title_vi': 'Nguyên âm đôi kết thúc bằng /ʊ/: /aʊ/ /əʊ/',
                'description': 'Master diphthongs ending with /ʊ/ sound: /aʊ/ (now), /əʊ/ (go)',
                'description_vi': 'Nắm vững các nguyên âm đôi kết thúc bằng âm /ʊ/: /aʊ/ (như "now") và /əʊ/ (như "go"). Môi cần chu tròn dần khi kết thúc.',
                'phonemes': ['aʊ', 'əʊ'],
                'objectives': [
                    'Chu tròn môi khi trượt sang /ʊ/',
                    'So sánh /əʊ/ (British) với /oʊ/ (American)',
                    'Luyện tập minimal pairs: low/law, coat/caught'
                ],
                'difficulty': 2,
                'estimated_minutes': 15,
            },
            # Unit 3: Centering diphthongs
            {
                'unit': 3,
                'slug': 'diphthongs-centering',
                'title': 'Centering Diphthongs: /ɪə/ /eə/ /ʊə/',
                'title_vi': 'Nguyên âm đôi hướng tâm: /ɪə/ /eə/ /ʊə/',
                'description': 'Learn centering diphthongs that end with schwa: /ɪə/ (here), /eə/ (hair), /ʊə/ (tour)',
                'description_vi': 'Học các nguyên âm đôi hướng về trung tâm (kết thúc bằng schwa): /ɪə/ (như "here"), /eə/ (như "hair"), /ʊə/ (như "tour"). Chỉ xuất hiện trước nguyên âm.',
                'phonemes': ['ɪə', 'eə', 'ʊə'],
                'objectives': [
                    'Nhận biết centering diphthongs trong British English',
                    'Phân biệt với monophthongs trong American English',
                    'Phát âm chuẩn trong từ có chứa r-sound'
                ],
                'difficulty': 3,
                'estimated_minutes': 15,
            },
        ]
        
        for data in lessons_data:
            self._create_lesson(part=2, **data)

    def create_consonant_lessons(self):
        """Create lessons for consonants."""
        self.stdout.write(self.style.WARNING('\n📕 Part 3: Creating Consonant Lessons...'))
        
        lessons_data = [
            # Unit 1: Plosives (Stops) - Voiceless vs Voiced (Labial)
            {
                'unit': 1,
                'slug': 'plosives-labial-p-b',
                'title': 'Labial Plosives: /p/ vs /b/',
                'title_vi': 'Phụ âm bật môi: /p/ và /b/',
                'description': 'Learn bilabial plosives /p/ (voiceless) and /b/ (voiced)',
                'description_vi': 'Học các phụ âm bật hơi ở môi: /p/ (vô thanh) và /b/ (hữu thanh). Khẩu hình giống nhau nhưng khác nhau ở độ rung thanh quản.',
                'phonemes': ['p', 'b'],
                'objectives': [
                    'Cảm nhận sự khác biệt giữa vô thanh và hữu thanh',
                    'Bật hơi mạnh khi phát âm /p/ đầu từ',
                    'Phân biệt pen/Ben, cap/cab'
                ],
                'difficulty': 1,
                'estimated_minutes': 12,
            },
            # Unit 2: Plosives - Alveolar
            {
                'unit': 2,
                'slug': 'plosives-alveolar-t-d',
                'title': 'Alveolar Plosives: /t/ vs /d/',
                'title_vi': 'Phụ âm bật lợi: /t/ và /d/',
                'description': 'Master alveolar plosives /t/ (voiceless) and /d/ (voiced)',
                'description_vi': 'Nắm vững các phụ âm bật hơi ở lợi: /t/ (vô thanh) và /d/ (hữu thanh). Đầu lưỡi chạm vào lợi răng trên.',
                'phonemes': ['t', 'd'],
                'objectives': [
                    'Đặt đầu lưỡi đúng vị trí (lợi răng trên)',
                    'Nhận biết các biến thể: flap /t/, glottal stop',
                    'Phân biệt tin/din, bat/bad'
                ],
                'difficulty': 1,
                'estimated_minutes': 12,
            },
            # Unit 3: Plosives - Velar
            {
                'unit': 3,
                'slug': 'plosives-velar-k-g',
                'title': 'Velar Plosives: /k/ vs /ɡ/',
                'title_vi': 'Phụ âm bật vòm: /k/ và /ɡ/',
                'description': 'Learn velar plosives /k/ (voiceless) and /ɡ/ (voiced)',
                'description_vi': 'Học các phụ âm bật hơi ở vòm miệng: /k/ (vô thanh) và /ɡ/ (hữu thanh). Phía sau lưỡi chạm vào vòm miệng mềm.',
                'phonemes': ['k', 'ɡ'],
                'objectives': [
                    'Tìm đúng vị trí tiếp xúc ở vòm miệng',
                    'Phân biệt các chính tả: c, k, ck, ch / g, gh',
                    'Luyện tập: cat/gap, back/bag'
                ],
                'difficulty': 1,
                'estimated_minutes': 12,
            },
            # Unit 4: Fricatives - Labiodental
            {
                'unit': 4,
                'slug': 'fricatives-labiodental-f-v',
                'title': 'Labiodental Fricatives: /f/ vs /v/',
                'title_vi': 'Phụ âm xát môi-răng: /f/ và /v/',
                'description': 'Master labiodental fricatives /f/ (voiceless) and /v/ (voiced)',
                'description_vi': 'Nắm vững các phụ âm xát môi-răng: /f/ (vô thanh) và /v/ (hữu thanh). Răng trên chạm vào môi dưới, người Việt thường nhầm /v/ thành /w/.',
                'phonemes': ['f', 'v'],
                'objectives': [
                    'Đặt răng trên lên môi dưới (KHÔNG phải /w/!)',
                    'Tạo ma sát đủ mạnh để tạo âm xát',
                    'Phân biệt: fan/van, safe/save'
                ],
                'difficulty': 2,
                'estimated_minutes': 15,
            },
            # Unit 5: Fricatives - Dental (TH sounds)
            {
                'unit': 5,
                'slug': 'fricatives-dental-th',
                'title': 'Dental Fricatives: /θ/ vs /ð/',
                'title_vi': 'Phụ âm xát răng (TH): /θ/ và /ð/',
                'description': 'Learn the challenging dental fricatives /θ/ (think) and /ð/ (this)',
                'description_vi': 'Học các phụ âm xát răng khó nhất: /θ/ (như "think") và /ð/ (như "this"). Lưỡi phải thò ra giữa hai hàm răng, không có trong tiếng Việt.',
                'phonemes': ['θ', 'ð'],
                'objectives': [
                    'Đặt lưỡi giữa hai hàm răng (quan trọng!)',
                    'Phân biệt /θ/ /ð/ với /s/ /z/ và /f/ /v/',
                    'Luyện tập: think/sink, this/dis'
                ],
                'difficulty': 3,
                'estimated_minutes': 18,
            },
            # Unit 6: Fricatives - Alveolar
            {
                'unit': 6,
                'slug': 'fricatives-alveolar-s-z',
                'title': 'Alveolar Fricatives: /s/ vs /z/',
                'title_vi': 'Phụ âm xát lợi: /s/ và /z/',
                'description': 'Master alveolar fricatives /s/ (voiceless) and /z/ (voiced)',
                'description_vi': 'Nắm vững các phụ âm xát lợi: /s/ (vô thanh) và /z/ (hữu thanh). Đầu lưỡi gần lợi răng, tạo luồng khí mạnh.',
                'phonemes': ['s', 'z'],
                'objectives': [
                    'Tạo luồng khí mạnh qua khe hẹp',
                    'Nhận biết /z/ trong từ tận cùng -s (dogs, his)',
                    'Phân biệt: sue/zoo,rice/rise'
                ],
                'difficulty': 1,
                'estimated_minutes': 12,
            },
            # Unit 7: Fricatives - Post-alveolar
            {
                'unit': 7,
                'slug': 'fricatives-postalveolar-sh-zh',
                'title': 'Post-alveolar Fricatives: /ʃ/ vs /ʒ/',
                'title_vi': 'Phụ âm xát sau lợi: /ʃ/ và /ʒ/',
                'description': 'Learn post-alveolar fricatives /ʃ/ (ship) and /ʒ/ (vision)',
                'description_vi': 'Học các phụ âm xát sau lợi: /ʃ/ (như "ship") và /ʒ/ (như "vision"). Lưỡi rút ra sau so với /s/ /z/, môi chu tròn.',
                'phonemes': ['ʃ', 'ʒ'],
                'objectives': [
                    'Rút lưỡi ra sau so với vị trí /s/',
                    'Chu tròn môi khi phát âm',
                    'Nhận biết /ʒ/ ít phổ biến trong tiếng Anh'
                ],
                'difficulty': 2,
                'estimated_minutes': 15,
            },
            # Unit 8: Fricatives - Glottal
            {
                'unit': 8,
                'slug': 'fricative-glottal-h',
                'title': 'Glottal Fricative: /h/',
                'title_vi': 'Phụ âm xát thanh môn: /h/',
                'description': 'Master the glottal fricative /h/ (house, behind)',
                'description_vi': 'Nắm vững phụ âm xát thanh môn /h/ (như "house"). Khí thoát ra từ thanh quản, không có tiếp xúc ở miệng.',
                'phonemes': ['h'],
                'objectives': [
                    'Phát âm /h/ nhẹ nhàng, không quá mạnh',
                    'Nhận biết "silent h" trong một số từ (hour, honest)',
                    'Phân biệt /h/ với không có âm (eat vs heat)'
                ],
                'difficulty': 1,
                'estimated_minutes': 10,
            },
            # Unit 9: Affricates
            {
                'unit': 9,
                'slug': 'affricates-ch-j',
                'title': 'Affricates: /tʃ/ vs /dʒ/',
                'title_vi': 'Phụ âm tắc xát: /tʃ/ và /dʒ/',
                'description': 'Learn affricates /tʃ/ (church) and /dʒ/ (judge)',
                'description_vi': 'Học các phụ âm tắc xát (kết hợp giữa tắc và xát): /tʃ/ (như "church") và /dʒ/ (như "judge"). Bắt đầu bằng âm tắc, kết thúc bằng âm xát.',
                'phonemes': ['tʃ', 'dʒ'],
                'objectives': [
                    'Hiểu cơ chế: stop + fricative',
                    'Phát âm liền mạch, không tách thành 2 âm',
                    'Phân biệt: cheap/jeep, batch/badge'
                ],
                'difficulty': 2,
                'estimated_minutes': 15,
            },
            # Unit 10: Nasals
            {
                'unit': 10,
                'slug': 'nasals-m-n-ng',
                'title': 'Nasal Consonants: /m/ /n/ /ŋ/',
                'title_vi': 'Phụ âm mũi: /m/ /n/ /ŋ/',
                'description': 'Master nasal consonants /m/ (mouth), /n/ (nose), /ŋ/ (sing)',
                'description_vi': 'Nắm vững các phụ âm mũi: /m/ (môi), /n/ (lợi), /ŋ/ (vòm). Khí thoát ra qua mũi, miệng bị chặn.',
                'phonemes': ['m', 'n', 'ŋ'],
                'objectives': [
                    'Phân biệt 3 vị trí chặn: môi, lợi, vòm',
                    'Nhận biết /ŋ/ không bao giờ ở đầu từ trong tiếng Anh',
                    'Luyện tập: sum/sun/sung'
                ],
                'difficulty': 2,
                'estimated_minutes': 15,
            },
            # Unit 11: Liquids
            {
                'unit': 11,
                'slug': 'liquids-l-r',
                'title': 'Liquid Consonants: /l/ vs /r/',
                'title_vi': 'Phụ âm lỏng: /l/ và /r/',
                'description': 'Learn liquid consonants /l/ (lateral) and /r/ (approximant)',
                'description_vi': 'Học các phụ âm lỏng: /l/ (bên) và /r/ (tiếp cận). Người châu Á thường gặp khó khăn với /r/ và /l/.',
                'phonemes': ['l', 'r'],
                'objectives': [
                    'Đặt đầu lưỡi lên lợi cho /l/',
                    'Phát âm /r/ kiểu Mỹ (môi chu tròn) vs Anh (không cuộn lưỡi)',
                    'Phân biệt: light/right, glass/grass'
                ],
                'difficulty': 3,
                'estimated_minutes': 18,
            },
            # Unit 12: Glides (Semivowels)
            {
                'unit': 12,
                'slug': 'glides-w-y',
                'title': 'Glides (Semivowels): /w/ vs /j/',
                'title_vi': 'Bán nguyên âm: /w/ và /j/',
                'description': 'Master glides /w/ (we) and /j/ (yes)',
                'description_vi': 'Nắm vững các bán nguyên âm: /w/ (như "we") và /j/ (như "yes"). Giống nguyên âm nhưng ngắn và trượt nhanh.',
                'phonemes': ['w', 'j'],
                'objectives': [
                    'Chu tròn môi cho /w/ (người Việt thường phát âm thành /v/)',
                    'Nâng lưỡi lên cho /j/',
                    'Phân biệt: wet/vet, year/ear'
                ],
                'difficulty': 2,
                'estimated_minutes': 15,
            },
        ]
        
        for data in lessons_data:
            self._create_lesson(part=3, **data)

    def _create_lesson(self, part, unit, slug, title, title_vi, description, 
                       description_vi, phonemes, objectives, difficulty, estimated_minutes):
        """Helper method to create a lesson."""
        
        # Get or create lesson
        lesson, created = PronunciationLesson.objects.update_or_create(
            slug=slug,
            defaults={
                'title': title,
                'title_vi': title_vi,
                'description': description,
                'description_vi': description_vi,
                'lesson_type': 'pair_contrast' if len(phonemes) > 1 else 'single_phoneme',
                'part_number': part,
                'unit_number': unit,
                'estimated_minutes': estimated_minutes,
                'xp_reward': 10 + (difficulty * 5),  # 15-25 XP based on difficulty
                'difficulty': difficulty,
                'status': 'published',  # All lessons unlocked
                'objectives': objectives,
                'lesson_content': [],  # Will be populated by Vue.js frontend
            }
        )
        
        # Add phonemes to lesson
        phoneme_objs = []
        for ipa_symbol in phonemes:
            try:
                phoneme = Phoneme.objects.get(ipa_symbol=ipa_symbol)
                phoneme_objs.append(phoneme)
            except Phoneme.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'  ⚠️  Phoneme /{ipa_symbol}/ not found, skipping...')
                )
        
        if phoneme_objs:
            lesson.phonemes.set(phoneme_objs)
        
        part_name = {1: 'Monophthongs', 2: 'Diphthongs', 3: 'Consonants'}[part]
        status = '✅ Created' if created else '🔄 Updated'
        
        self.stdout.write(
            f'  {status} Part {part} Unit {unit}: {title_vi} '
            f'(/{"/".join(phonemes)}/)'
        )
