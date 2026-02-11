"""
Management command to seed pronunciation lessons.
Creates sample lessons following the structure from chi tiết.md
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.curriculum.models import (
    Phoneme, PhonemeCategory, PhonemeWord, 
    PronunciationLesson, MinimalPair, TongueTwister
)


class Command(BaseCommand):
    help = 'Seeds sample pronunciation lessons into the database'

    def handle(self, *args, **options):
        self.stdout.write('Seeding pronunciation lessons...')
        
        with transaction.atomic():
            self.create_lessons()
            self.create_example_words()
            self.create_minimal_pairs()
            self.create_tongue_twisters()
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded pronunciation lessons!'))

    def create_lessons(self):
        """Create pronunciation lessons following the curriculum."""
        
        lessons_data = [
            # Part 2: Monophthongs (Vowels)
            {
                'title': 'Short vs Long "I"',
                'title_vi': 'Cặp Âm "I" - /iː/ và /ɪ/',
                'slug': 'vowel-i-long-short',
                'description': 'Learn to distinguish long /iː/ and short /ɪ/',
                'description_vi': 'Học cách phân biệt âm "i" dài /iː/ (Sheep) và âm "i" ngắn /ɪ/ (Ship). Đây là cặp âm người Việt dễ nhầm lẫn nhất!',
                'lesson_type': 'pair_contrast',
                'part_number': 2,
                'unit_number': 1,
                'phoneme_symbols': ['iː', 'ɪ'],
                'objectives': [
                    'Phân biệt được độ dài của âm /iː/ và /ɪ/',
                    'Hiểu khẩu hình miệng khi phát âm hai âm này',
                    'Luyện tập với các từ Ship/Sheep, Sit/Seat',
                ],
                'xp_reward': 15,
                'estimated_minutes': 10,
                'difficulty': 1,
            },
            {
                'title': 'Short vs Long "U"',
                'title_vi': 'Cặp Âm "U" - /uː/ và /ʊ/',
                'slug': 'vowel-u-long-short',
                'description': 'Learn to distinguish long /uː/ and short /ʊ/',
                'description_vi': 'Học cách phân biệt âm "u" dài /uː/ (Food) và âm "u" ngắn /ʊ/ (Foot). Âm /ʊ/ gần giống âm "ư" trong tiếng Việt.',
                'lesson_type': 'pair_contrast',
                'part_number': 2,
                'unit_number': 2,
                'phoneme_symbols': ['uː', 'ʊ'],
                'objectives': [
                    'Phân biệt được độ dài của âm /uː/ và /ʊ/',
                    'Biết cách chu môi đúng khi phát âm',
                    'Luyện tập với các từ Food/Foot, Moon/Look',
                ],
                'xp_reward': 15,
                'estimated_minutes': 10,
                'difficulty': 1,
            },
            {
                'title': 'The Schwa Sound',
                'title_vi': 'Cặp Âm "Ơ" - /ɜː/ và /ə/',
                'slug': 'vowel-schwa',
                'description': 'Learn the most common vowel sound in English',
                'description_vi': 'Âm Schwa /ə/ là âm xuất hiện nhiều nhất trong tiếng Anh! Học cách phát âm "ờ" nhẹ nhàng và so sánh với âm /ɜː/ dài.',
                'lesson_type': 'pair_contrast',
                'part_number': 2,
                'unit_number': 3,
                'phoneme_symbols': ['ɜː', 'ə'],
                'objectives': [
                    'Nhận biết âm Schwa /ə/ trong các từ thông dụng',
                    'Phân biệt /ɜː/ dài (Bird, Work) và /ə/ ngắn (Teacher)',
                    'Hiểu vai trò của trọng âm trong việc tạo ra âm Schwa',
                ],
                'xp_reward': 20,
                'estimated_minutes': 12,
                'difficulty': 2,
            },
            # Part 4: Consonants - Plosives
            {
                'title': 'The Popping Sounds /p/ vs /b/',
                'title_vi': 'Âm Bật Hơi - /p/ và /b/',
                'slug': 'consonant-p-b',
                'description': 'Learn voiceless /p/ and voiced /b/ plosives',
                'description_vi': 'Học cặp âm "sinh đôi" thú vị nhất: /p/ và /b/. Miệng làm động tác Y HỆT nhau, nhưng khác nhau ở độ rung thanh quản!',
                'lesson_type': 'pair_contrast',
                'part_number': 4,
                'unit_number': 7,
                'phoneme_symbols': ['p', 'b'],
                'objectives': [
                    'Hiểu khẩu hình miệng giống nhau của /p/ và /b/',
                    'Phân biệt được Vô thanh (Unvoiced) và Hữu thanh (Voiced)',
                    'Luyện tập từ vựng chứa âm /p/ và /b/',
                ],
                'xp_reward': 15,
                'estimated_minutes': 10,
                'difficulty': 1,
            },
            {
                'title': 'The Popping Sounds /t/ vs /d/',
                'title_vi': 'Âm Bật Hơi - /t/ và /d/',
                'slug': 'consonant-t-d',
                'description': 'Learn voiceless /t/ and voiced /d/ plosives',
                'description_vi': 'Học cặp âm /t/ và /d/. Đầu lưỡi chạm vào phía sau răng cửa trên, sau đó bật ra. /t/ vô thanh, /d/ hữu thanh.',
                'lesson_type': 'pair_contrast',
                'part_number': 4,
                'unit_number': 8,
                'phoneme_symbols': ['t', 'd'],
                'objectives': [
                    'Hiểu vị trí đặt lưỡi khi phát âm /t/ và /d/',
                    'Phân biệt được âm vô thanh /t/ và hữu thanh /d/',
                    'Luyện tập với các từ Tea/Day, Tie/Die',
                ],
                'xp_reward': 15,
                'estimated_minutes': 10,
                'difficulty': 1,
            },
            {
                'title': 'The TH Sounds',
                'title_vi': 'Âm "TH" - /θ/ và /ð/',
                'slug': 'consonant-th',
                'description': 'Learn the infamous TH sounds',
                'description_vi': 'Hai âm "thè lưỡi" đặc trưng của tiếng Anh! Lưỡi phải thò ra giữa hai răng. /θ/ trong "Think", /ð/ trong "This".',
                'lesson_type': 'pair_contrast',
                'part_number': 4,
                'unit_number': 9,
                'phoneme_symbols': ['θ', 'ð'],
                'objectives': [
                    'Biết cách đặt lưỡi giữa hai răng để phát âm TH',
                    'Phân biệt /θ/ vô thanh (Think) và /ð/ hữu thanh (This)',
                    'Tránh phát âm thành /s/, /z/, /t/, /d/ như người Việt thường mắc',
                ],
                'xp_reward': 20,
                'estimated_minutes': 15,
                'difficulty': 3,
            },
        ]
        
        for lesson_data in lessons_data:
            phoneme_symbols = lesson_data.pop('phoneme_symbols')
            objectives = lesson_data.pop('objectives')
            
            lesson, created = PronunciationLesson.objects.update_or_create(
                slug=lesson_data['slug'],
                defaults={
                    **lesson_data,
                    'objectives': objectives,
                    'status': 'published',
                }
            )
            
            # Link phonemes
            phonemes = Phoneme.objects.filter(ipa_symbol__in=phoneme_symbols)
            lesson.phonemes.set(phonemes)
            
            action = 'Created' if created else 'Updated'
            self.stdout.write(f'  {action} lesson: {lesson.title_vi}')

    def create_example_words(self):
        """Create example words for phonemes."""
        
        words_data = {
            'p': [
                {'word': 'Pen', 'ipa': '/pen/', 'meaning': 'Cây bút', 'position': 'initial'},
                {'word': 'Pop', 'ipa': '/pɒp/', 'meaning': 'Tiếng nổ', 'position': 'initial'},
                {'word': 'Soup', 'ipa': '/suːp/', 'meaning': 'Súp', 'position': 'final'},
                {'word': 'Apple', 'ipa': '/ˈæpəl/', 'meaning': 'Quả táo', 'position': 'medial'},
                {'word': 'Pea', 'ipa': '/piː/', 'meaning': 'Hạt đậu', 'position': 'initial'},
                {'word': 'Stop', 'ipa': '/stɒp/', 'meaning': 'Dừng lại', 'position': 'final'},
            ],
            'b': [
                {'word': 'Bad', 'ipa': '/bæd/', 'meaning': 'Tệ', 'position': 'initial'},
                {'word': 'Bob', 'ipa': '/bɒb/', 'meaning': 'Tên Bob', 'position': 'initial'},
                {'word': 'Web', 'ipa': '/web/', 'meaning': 'Mạng', 'position': 'final'},
                {'word': 'Boat', 'ipa': '/bəʊt/', 'meaning': 'Thuyền', 'position': 'initial'},
                {'word': 'Brother', 'ipa': '/ˈbrʌðər/', 'meaning': 'Anh/Em trai', 'position': 'initial'},
                {'word': 'Cab', 'ipa': '/kæb/', 'meaning': 'Taxi', 'position': 'final'},
            ],
            't': [
                {'word': 'Tea', 'ipa': '/tiː/', 'meaning': 'Trà', 'position': 'initial'},
                {'word': 'Tie', 'ipa': '/taɪ/', 'meaning': 'Cà vạt', 'position': 'initial'},
                {'word': 'Cat', 'ipa': '/kæt/', 'meaning': 'Con mèo', 'position': 'final'},
                {'word': 'Water', 'ipa': '/ˈwɔːtər/', 'meaning': 'Nước', 'position': 'medial'},
                {'word': 'Top', 'ipa': '/tɒp/', 'meaning': 'Đỉnh', 'position': 'initial'},
                {'word': 'Sit', 'ipa': '/sɪt/', 'meaning': 'Ngồi', 'position': 'final'},
            ],
            'd': [
                {'word': 'Day', 'ipa': '/deɪ/', 'meaning': 'Ngày', 'position': 'initial'},
                {'word': 'Die', 'ipa': '/daɪ/', 'meaning': 'Chết', 'position': 'initial'},
                {'word': 'Bad', 'ipa': '/bæd/', 'meaning': 'Tệ', 'position': 'final'},
                {'word': 'Under', 'ipa': '/ˈʌndər/', 'meaning': 'Bên dưới', 'position': 'medial'},
                {'word': 'Door', 'ipa': '/dɔːr/', 'meaning': 'Cửa', 'position': 'initial'},
                {'word': 'Red', 'ipa': '/red/', 'meaning': 'Đỏ', 'position': 'final'},
            ],
            'iː': [
                {'word': 'Sheep', 'ipa': '/ʃiːp/', 'meaning': 'Con cừu', 'position': 'medial'},
                {'word': 'Tea', 'ipa': '/tiː/', 'meaning': 'Trà', 'position': 'final'},
                {'word': 'See', 'ipa': '/siː/', 'meaning': 'Nhìn', 'position': 'final'},
                {'word': 'Feet', 'ipa': '/fiːt/', 'meaning': 'Bàn chân', 'position': 'medial'},
                {'word': 'Seat', 'ipa': '/siːt/', 'meaning': 'Ghế ngồi', 'position': 'medial'},
                {'word': 'Beach', 'ipa': '/biːtʃ/', 'meaning': 'Bãi biển', 'position': 'medial'},
            ],
            'ɪ': [
                {'word': 'Ship', 'ipa': '/ʃɪp/', 'meaning': 'Con tàu', 'position': 'medial'},
                {'word': 'Sit', 'ipa': '/sɪt/', 'meaning': 'Ngồi', 'position': 'medial'},
                {'word': 'Fit', 'ipa': '/fɪt/', 'meaning': 'Vừa vặn', 'position': 'medial'},
                {'word': 'Big', 'ipa': '/bɪg/', 'meaning': 'To lớn', 'position': 'medial'},
                {'word': 'Bit', 'ipa': '/bɪt/', 'meaning': 'Một chút', 'position': 'medial'},
                {'word': 'Fish', 'ipa': '/fɪʃ/', 'meaning': 'Con cá', 'position': 'medial'},
            ],
            'θ': [
                {'word': 'Think', 'ipa': '/θɪŋk/', 'meaning': 'Nghĩ', 'position': 'initial'},
                {'word': 'Thank', 'ipa': '/θæŋk/', 'meaning': 'Cảm ơn', 'position': 'initial'},
                {'word': 'Bath', 'ipa': '/bɑːθ/', 'meaning': 'Tắm', 'position': 'final'},
                {'word': 'Math', 'ipa': '/mæθ/', 'meaning': 'Toán', 'position': 'final'},
                {'word': 'Throw', 'ipa': '/θrəʊ/', 'meaning': 'Ném', 'position': 'initial'},
                {'word': 'Tooth', 'ipa': '/tuːθ/', 'meaning': 'Răng', 'position': 'final'},
            ],
            'ð': [
                {'word': 'This', 'ipa': '/ðɪs/', 'meaning': 'Cái này', 'position': 'initial'},
                {'word': 'That', 'ipa': '/ðæt/', 'meaning': 'Cái đó', 'position': 'initial'},
                {'word': 'The', 'ipa': '/ðə/', 'meaning': 'Mạo từ xác định', 'position': 'initial'},
                {'word': 'Mother', 'ipa': '/ˈmʌðər/', 'meaning': 'Mẹ', 'position': 'medial'},
                {'word': 'Brother', 'ipa': '/ˈbrʌðər/', 'meaning': 'Anh/Em trai', 'position': 'medial'},
                {'word': 'Weather', 'ipa': '/ˈweðər/', 'meaning': 'Thời tiết', 'position': 'medial'},
            ],
        }
        
        for symbol, words in words_data.items():
            try:
                phoneme = Phoneme.objects.get(ipa_symbol=symbol)
                
                for idx, word_data in enumerate(words):
                    PhonemeWord.objects.update_or_create(
                        phoneme=phoneme,
                        word=word_data['word'],
                        defaults={
                            'ipa_transcription': word_data['ipa'],
                            'meaning_vi': word_data['meaning'],
                            'phoneme_position': word_data['position'],
                            'order': idx,
                        }
                    )
                
                self.stdout.write(f'  Created words for /{symbol}/')
            except Phoneme.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  Phoneme /{symbol}/ not found'))

    def create_minimal_pairs(self):
        """Create minimal pairs for lessons."""
        
        pairs_data = [
            # /p/ vs /b/
            {
                'p1': 'p', 'p2': 'b',
                'word_1': 'Pea', 'word_1_ipa': '/piː/', 'word_1_meaning': 'Hạt đậu',
                'word_2': 'Bee', 'word_2_ipa': '/biː/', 'word_2_meaning': 'Con ong',
                'note': '/p/ là vô thanh (chỉ bật hơi), /b/ là hữu thanh (rung cổ họng).',
                'difficulty': 1,
            },
            {
                'p1': 'p', 'p2': 'b',
                'word_1': 'Pop', 'word_1_ipa': '/pɒp/', 'word_1_meaning': 'Tiếng nổ',
                'word_2': 'Bob', 'word_2_ipa': '/bɒb/', 'word_2_meaning': 'Tên Bob',
                'note': 'Cả đầu và cuối từ đều có sự khác biệt giữa /p/ và /b/.',
                'difficulty': 1,
            },
            {
                'p1': 'p', 'p2': 'b',
                'word_1': 'Cap', 'word_1_ipa': '/kæp/', 'word_1_meaning': 'Cái mũ',
                'word_2': 'Cab', 'word_2_ipa': '/kæb/', 'word_2_meaning': 'Taxi',
                'note': 'Âm cuối /p/ ngắt rất nhanh. Âm cuối /b/ kéo dài hơn một chút.',
                'difficulty': 2,
            },
            {
                'p1': 'p', 'p2': 'b',
                'word_1': 'Pat', 'word_1_ipa': '/pæt/', 'word_1_meaning': 'Vỗ nhẹ',
                'word_2': 'Bat', 'word_2_ipa': '/bæt/', 'word_2_meaning': 'Con dơi',
                'note': 'Tập trung vào âm đầu.',
                'difficulty': 1,
            },
            {
                'p1': 'p', 'p2': 'b',
                'word_1': 'Rope', 'word_1_ipa': '/rəʊp/', 'word_1_meaning': 'Sợi dây',
                'word_2': 'Robe', 'word_2_ipa': '/rəʊb/', 'word_2_meaning': 'Áo choàng',
                'note': 'Chú ý âm cuối.',
                'difficulty': 2,
            },
            # /t/ vs /d/
            {
                'p1': 't', 'p2': 'd',
                'word_1': 'Tea', 'word_1_ipa': '/tiː/', 'word_1_meaning': 'Trà',
                'word_2': 'Dee', 'word_2_ipa': '/diː/', 'word_2_meaning': 'Chữ D',
                'note': '/t/ vô thanh, /d/ hữu thanh.',
                'difficulty': 1,
            },
            {
                'p1': 't', 'p2': 'd',
                'word_1': 'Tie', 'word_1_ipa': '/taɪ/', 'word_1_meaning': 'Cà vạt',
                'word_2': 'Die', 'word_2_ipa': '/daɪ/', 'word_2_meaning': 'Chết',
                'note': 'Lưu ý độ rung thanh quản.',
                'difficulty': 1,
            },
            {
                'p1': 't', 'p2': 'd',
                'word_1': 'Cat', 'word_1_ipa': '/kæt/', 'word_1_meaning': 'Con mèo',
                'word_2': 'Cad', 'word_2_ipa': '/kæd/', 'word_2_meaning': 'Kẻ vô lại',
                'note': 'Âm cuối /t/ ngắt gọn, /d/ có độ rung nhẹ.',
                'difficulty': 2,
            },
            # /iː/ vs /ɪ/
            {
                'p1': 'iː', 'p2': 'ɪ',
                'word_1': 'Sheep', 'word_1_ipa': '/ʃiːp/', 'word_1_meaning': 'Con cừu',
                'word_2': 'Ship', 'word_2_ipa': '/ʃɪp/', 'word_2_meaning': 'Con tàu',
                'note': '/iː/ kéo dài, miệng mỉm cười. /ɪ/ ngắn gọn.',
                'difficulty': 1,
            },
            {
                'p1': 'iː', 'p2': 'ɪ',
                'word_1': 'Seat', 'word_1_ipa': '/siːt/', 'word_1_meaning': 'Ghế ngồi',
                'word_2': 'Sit', 'word_2_ipa': '/sɪt/', 'word_2_meaning': 'Ngồi',
                'note': 'Chú ý độ dài của âm "i".',
                'difficulty': 1,
            },
            {
                'p1': 'iː', 'p2': 'ɪ',
                'word_1': 'Feet', 'word_1_ipa': '/fiːt/', 'word_1_meaning': 'Bàn chân',
                'word_2': 'Fit', 'word_2_ipa': '/fɪt/', 'word_2_meaning': 'Vừa vặn',
                'note': '/iː/ căng hơn và dài hơn /ɪ/.',
                'difficulty': 1,
            },
            {
                'p1': 'iː', 'p2': 'ɪ',
                'word_1': 'Beach', 'word_1_ipa': '/biːtʃ/', 'word_1_meaning': 'Bãi biển',
                'word_2': 'Bitch', 'word_2_ipa': '/bɪtʃ/', 'word_2_meaning': 'Chó cái',
                'note': 'CẨN THẬN: Phát âm sai có thể gây hiểu lầm nghiêm trọng!',
                'difficulty': 2,
            },
            # /θ/ vs /ð/
            {
                'p1': 'θ', 'p2': 'ð',
                'word_1': 'Thin', 'word_1_ipa': '/θɪn/', 'word_1_meaning': 'Mỏng/Gầy',
                'word_2': 'Then', 'word_2_ipa': '/ðen/', 'word_2_meaning': 'Sau đó',
                'note': '/θ/ vô thanh (thổi hơi), /ð/ hữu thanh (rung).',
                'difficulty': 2,
            },
            {
                'p1': 'θ', 'p2': 'ð',
                'word_1': 'Thought', 'word_1_ipa': '/θɔːt/', 'word_1_meaning': 'Suy nghĩ',
                'word_2': 'Though', 'word_2_ipa': '/ðəʊ/', 'word_2_meaning': 'Mặc dù',
                'note': 'Lưỡi đều thò ra giữa răng.',
                'difficulty': 2,
            },
        ]
        
        for pair_data in pairs_data:
            try:
                p1 = Phoneme.objects.get(ipa_symbol=pair_data['p1'])
                p2 = Phoneme.objects.get(ipa_symbol=pair_data['p2'])
                
                MinimalPair.objects.update_or_create(
                    word_1=pair_data['word_1'],
                    word_2=pair_data['word_2'],
                    defaults={
                        'phoneme_1': p1,
                        'phoneme_2': p2,
                        'word_1_ipa': pair_data['word_1_ipa'],
                        'word_1_meaning': pair_data['word_1_meaning'],
                        'word_2_ipa': pair_data['word_2_ipa'],
                        'word_2_meaning': pair_data['word_2_meaning'],
                        'difference_note_vi': pair_data['note'],
                        'difficulty': pair_data['difficulty'],
                    }
                )
                
                self.stdout.write(f'  Created pair: {pair_data["word_1"]} vs {pair_data["word_2"]}')
            except Phoneme.DoesNotExist as e:
                self.stdout.write(self.style.WARNING(f'  Phoneme not found: {e}'))

    def create_tongue_twisters(self):
        """Create tongue twisters for lessons."""
        
        twisters_data = [
            {
                'phoneme': 'p',
                'lesson_slug': 'consonant-p-b',
                'text': 'Peter Piper picked a peck of pickled peppers.',
                'ipa': '/ˈpiːtər ˈpaɪpər pɪkt ə pek əv ˈpɪkəld ˈpepərz/',
                'meaning': 'Peter Piper đã nhặt một đấu ớt ngâm chua.',
                'difficulty': 3,
            },
            {
                'phoneme': 'b',
                'lesson_slug': 'consonant-p-b',
                'text': 'Betty Botter bought some butter.',
                'ipa': '/ˈbeti ˈbɒtər bɔːt sʌm ˈbʌtər/',
                'meaning': 'Betty Botter đã mua một ít bơ.',
                'difficulty': 2,
            },
            {
                'phoneme': 'θ',
                'lesson_slug': 'consonant-th',
                'text': 'The thirty-three thieves thought that they thrilled the throne throughout Thursday.',
                'ipa': '/ðə ˈθɜːti θriː θiːvz θɔːt ðæt ðeɪ θrɪld ðə θrəʊn θruːˈaʊt ˈθɜːzdeɪ/',
                'meaning': 'Ba mươi ba tên trộm nghĩ rằng họ đã làm rung động ngai vàng suốt ngày thứ Năm.',
                'difficulty': 5,
            },
            {
                'phoneme': 'iː',
                'lesson_slug': 'vowel-i-long-short',
                'text': 'She sees cheese.',
                'ipa': '/ʃiː siːz tʃiːz/',
                'meaning': 'Cô ấy nhìn thấy phô mai.',
                'difficulty': 1,
            },
        ]
        
        for twister_data in twisters_data:
            try:
                phoneme = Phoneme.objects.get(ipa_symbol=twister_data['phoneme'])
                
                lesson = None
                if twister_data['lesson_slug']:
                    try:
                        lesson = PronunciationLesson.objects.get(slug=twister_data['lesson_slug'])
                    except PronunciationLesson.DoesNotExist:
                        pass
                
                TongueTwister.objects.update_or_create(
                    text=twister_data['text'],
                    defaults={
                        'phoneme': phoneme,
                        'pronunciation_lesson': lesson,
                        'ipa_transcription': twister_data['ipa'],
                        'meaning_vi': twister_data['meaning'],
                        'difficulty': twister_data['difficulty'],
                    }
                )
                
                self.stdout.write(f'  Created tongue twister: {twister_data["text"][:30]}...')
            except Phoneme.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  Phoneme not found: {twister_data["phoneme"]}'))
