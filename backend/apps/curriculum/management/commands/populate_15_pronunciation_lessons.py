"""
Management command to populate 15 pronunciation lessons following the 4-stage curriculum.
Based on "Phương pháp luyện phát âm tiếng Anh chuẩn"
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.curriculum.models import CurriculumStage, PronunciationLesson, Phoneme


class Command(BaseCommand):
    help = 'Populates 15 pronunciation lessons following the 4-stage curriculum'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('📚 Creating 15 pronunciation lessons...'))
        
        with transaction.atomic():
            # Get stages
            self.stage_1 = CurriculumStage.objects.get(number=1)
            self.stage_2 = CurriculumStage.objects.get(number=2)
            self.stage_3 = CurriculumStage.objects.get(number=3)
            self.stage_4 = CurriculumStage.objects.get(number=4)
            
            # Create lessons
            self.create_stage_1_lessons()  # 4 lessons
            self.create_stage_2_lessons()  # 6 lessons
            self.create_stage_3_lessons()  # 2 lessons
            self.create_stage_4_lessons()  # 3 lessons
        
        total = PronunciationLesson.objects.filter(status='published').count()
        self.stdout.write(self.style.SUCCESS(f'✅ Successfully created {total} pronunciation lessons!'))

    def create_stage_1_lessons(self):
        """Giai đoạn 1: Nguyên âm đơn (4 bài)"""
        self.stdout.write('  🎯 Stage 1: Nguyên âm đơn...')
        
        # Bài 1: Nguyên âm ngắn /ɪ/ /æ/ /ə/
        lesson = self.create_lesson(
            stage=self.stage_1,
            part_number=1,
            unit_number=1,
            title='Short Vowels: /ɪ/ /æ/ /ə/',
            title_vi='Nguyên âm ngắn: /ɪ/ /æ/ /ə/',
            description_vi='Học 3 nguyên âm ngắn quan trọng nhất với khẩu hình miệng dẹt hoặc mở rộng vừa phải.',
            phoneme_symbols=['ɪ', 'æ', 'ə'],
            lesson_type='group',
            estimated_minutes=15,
            xp_reward=20,
            difficulty=1,
            objectives=[
                'Phân biệt được /ɪ/ (sit) và /iː/ (seat)',
                'Phát âm đúng /æ/ (cat) - âm giữa a và e',
                'Hiểu và dùng schwa /ə/ - âm lười nhất',
                'Tránh lỗi phát âm /ɪ/ thành /iː/ dài'
            ],
            lesson_content=[
                {
                    'screen': 1,
                    'type': 'intro',
                    'title': 'Giới thiệu',
                    'content': {
                        'text': 'Nguyên âm là linh hồn của từ. Trong bài này, bạn sẽ học 3 nguyên âm ngắn quan trọng nhất.',
                        'importance': 'Người Việt hay nhầm /ɪ/ với /iː/ dài, làm "sit" thành "seat"',
                        'focus': 'Khẩu hình miệng và độ ngắn'
                    }
                },
                {
                    'screen': 2,
                    'type': 'theory',
                    'title': 'Lý thuyết: 3 Nguyên âm ngắn',
                    'phonemes': [
                        {
                            'ipa': 'ɪ',
                            'example_words': ['sit', 'hit', 'bit'],
                            'mouth_shape': 'Môi dẹt nhẹ, miệng mở vừa',
                            'common_mistake': 'Đọc thành /iː/ dài → "sit" thành "seat"'
                        },
                        {
                            'ipa': 'æ',
                            'example_words': ['cat', 'hat', 'bat'],
                            'mouth_shape': 'Miệng mở RỘNG, hàm hạ thấp',
                            'common_mistake': 'Đọc thành "a" hoặc "e" tiếng Việt'
                        },
                        {
                            'ipa': 'ə',
                            'example_words': ['about', 'camera', 'the'],
                            'mouth_shape': 'Thả lỏng tự nhiên - âm LƯỜI nhất',
                            'common_mistake': 'Phát âm quá rõ ràng thay vì lười'
                        }
                    ]
                },
                {
                    'screen': 3,
                    'type': 'practice',
                    'title': 'Luyện tập',
                    'exercises': [
                        {
                            'type': 'listen_repeat',
                            'words': [
                                {'word': 'sit', 'ipa': 'sɪt', 'meaning': 'ngồi'},
                                {'word': 'cat', 'ipa': 'kæt', 'meaning': 'mèo'},
                                {'word': 'about', 'ipa': 'əˈbaʊt', 'meaning': 'về'}
                            ]
                        }
                    ]
                },
                {
                    'screen': 4,
                    'type': 'challenge',
                    'title': 'Thử thách: Phân biệt âm',
                    'minimal_pairs': [
                        ['sit', 'seat'],
                        ['ship', 'sheep'],
                        ['hit', 'heat']
                    ]
                }
            ]
        )
        self.stdout.write(f'    ✨ Lesson 1: {lesson.title_vi}')
        
        # Bài 2: Nguyên âm ngắn /ɒ/ /ʊ/ /e/
        lesson = self.create_lesson(
            stage=self.stage_1,
            part_number=1,
            unit_number=2,
            title='Short Vowels: /ɒ/ /ʊ/ /e/',
            title_vi='Nguyên âm ngắn: /ɒ/ /ʊ/ /e/',
            description_vi='Học 3 nguyên âm ngắn với khẩu hình miệng tròn và chu mỏ.',
            phoneme_symbols=['ɒ', 'ʊ', 'e'],
            lesson_type='group',
            estimated_minutes=15,
            xp_reward=20,
            difficulty=1,
            objectives=[
                'Phát âm đúng /ɒ/ (hot) với miệng tròn',
                'Phân biệt /ʊ/ (book) và /uː/ (boot)',
                'Phát âm /e/ (bed) không nhầm với /æ/ (bad)'
            ],
            lesson_content=[
                {
                    'screen': 1,
                    'type': 'intro',
                    'title': 'Khẩu hình tròn và chu mỏ',
                    'content': {
                        'text': '3 nguyên âm này đều cần chu môi hoặc tròn miệng.',
                        'focus': 'Hình dạng môi và độ mở miệng'
                    }
                }
            ]
        )
        self.stdout.write(f'    ✨ Lesson 2: {lesson.title_vi}')
        
        # Bài 3: Nguyên âm dài /iː/ /ɑː/
        lesson = self.create_lesson(
            stage=self.stage_1,
            part_number=1,
            unit_number=3,
            title='Long Vowels: /iː/ /ɑː/',
            title_vi='Nguyên âm dài: /iː/ /ɑː/',
            description_vi='Kéo dài hơi, khẩu hình miệng dẹt như đang cười hoặc tròn và ngân vang.',
            phoneme_symbols=['iː', 'ɑː'],
            lesson_type='pair_contrast',
            estimated_minutes=15,
            xp_reward=20,
            difficulty=2,
            objectives=[
                'Kéo dài âm /iː/ đủ thời gian (see, tea)',
                'Phát âm /ɑː/ ngân vang (car, far)',
                'Phân biệt rõ ngắn vs dài: sit/seat, cap/carp'
            ]
        )
        self.stdout.write(f'    ✨ Lesson 3: {lesson.title_vi}')
        
        # Bài 4: Nguyên âm dài /uː/ /ɔː/ /ɜː/
        lesson = self.create_lesson(
            stage=self.stage_1,
            part_number=1,
            unit_number=4,
            title='Long Vowels: /uː/ /ɔː/ /ɜː/',
            title_vi='Nguyên âm dài: /uː/ /ɔː/ /ɜː/',
            description_vi='Luyện độ ngân vang và kéo dài hơi với khẩu hình chu mỏi hoặc tròn miệng.',
            phoneme_symbols=['uː', 'ɔː', 'ɜː'],
            lesson_type='group',
            estimated_minutes=15,
            xp_reward=20,
            difficulty=2,
            objectives=[
                'Chu môi mạnh cho /uː/ (food, blue)',
                'Tròn miệng cho /ɔː/ (door, more)',
                'Phát âm /ɜː/ đặc biệt (bird, her, learn)'
            ]
        )
        self.stdout.write(f'    ✨ Lesson 4: {lesson.title_vi}')

    def create_stage_2_lessons(self):
        """Giai đoạn 2: Phụ âm theo cặp (6 bài)"""
        self.stdout.write('  🔥 Stage 2: Phụ âm theo cặp...')
        
        # Bài 5: /p/ - /b/
        lesson = self.create_lesson(
            stage=self.stage_2,
            part_number=2,
            unit_number=5,
            title='Consonant Pair: /p/ - /b/',
            title_vi='Cặp phụ âm môi - môi: /p/ - /b/',
            description_vi='Mím môi và bật hơi. Học kỹ thuật đặt tay lên cổ để kiểm tra độ rung.',
            phoneme_symbols=['p', 'b'],
            lesson_type='pair_contrast',
            estimated_minutes=12,
            xp_reward=18,
            difficulty=2,
            objectives=[
                'Bật hơi MẠNH cho /p/ (pen, cup)',
                'Rung cổ họng cho /b/ (bed, job)',
                'Phân biệt pin/bin, cap/cab',
                'Kỹ thuật: Đặt tay lên cổ để cảm nhận rung'
            ],
            lesson_content=[
                {
                    'screen': 1,
                    'type': 'intro',
                    'title': 'Âm gió vs Âm rung',
                    'content': {
                        'text': 'Đây là cặp phụ âm đầu tiên bạn học. Điểm khác biệt: /p/ KHÔNG rung cổ, /b/ RUNG cổ.',
                        'technique': 'Đặt tay lên cổ họng khi phát âm để kiểm tra',
                        'importance': 'Người Việt hay không bật hơi đủ mạnh cho /p/'
                    }
                },
                {
                    'screen': 2,
                    'type': 'theory',
                    'title': 'So sánh /p/ và /b/',
                    'comparison': {
                        'voiceless': {
                            'ipa': 'p',
                            'name': 'Vô thanh (Voiceless)',
                            'throat': 'KHÔNG rung',
                            'aspiration': 'Bật hơi MẠNH',
                            'examples': ['pen', 'cup', 'stop']
                        },
                        'voiced': {
                            'ipa': 'b',
                            'name': 'Hữu thanh (Voiced)',
                            'throat': 'RUNG',
                            'aspiration': 'Không bật hơi',
                            'examples': ['bed', 'job', 'big']
                        }
                    }
                }
            ]
        )
        self.stdout.write(f'    ✨ Lesson 5: {lesson.title_vi}')
        
        # Bài 6-10: Tương tự cho các cặp khác
        pairs = [
            (6, 't', 'd', 'đầu lưỡi - răng', 'Lưỡi chạm vòm miệng', ['tea', 'hit', 'cat'], ['dog', 'had', 'bed']),
            (7, 'k', 'g', 'cuống lưỡi', 'Cuống lưỡi chạm vòm miệng', ['cat', 'back', 'key'], ['go', 'big', 'dog']),
            (8, 's', 'z', 'âm xì', 'Lưỡi gần vòm miệng, xì hơi', ['see', 'yes', 'bus'], ['zoo', 'buzz', 'is']),
            (9, 'ʃ', 'ʒ', 'cong môi', 'Cong môi, lưỡi lùi', ['she', 'fish', 'nation'], ['vision', 'measure', 'beige']),
            (10, 'tʃ', 'dʒ', 'bật hơi', 'Kết hợp tắc và xát', ['church', 'match', 'teach'], ['job', 'age', 'jump'])
        ]
        
        for unit_num, voiceless, voiced, position, technique, ex_voiceless, ex_voiced in pairs:
            lesson = self.create_lesson(
                stage=self.stage_2,
                part_number=2,
                unit_number=unit_num,
                title=f'Consonant Pair: /{voiceless}/ - /{voiced}/',
                title_vi=f'Cặp phụ âm {position}: /{voiceless}/ - /{voiced}/',
                description_vi=f'{technique}. Phân biệt âm gió (voiceless) và âm rung (voiced).',
                phoneme_symbols=[voiceless, voiced],
                lesson_type='pair_contrast',
                estimated_minutes=12,
                xp_reward=18,
                difficulty=2,
                objectives=[
                    f'Phát âm đúng /{voiceless}/ không rung cổ',
                    f'Phát âm đúng /{voiced}/ rung cổ họng',
                    f'Phân biệt các cặp từ tối thiểu',
                    'Kỹ thuật: Đặt tay lên cổ để kiểm tra'
                ]
            )
            self.stdout.write(f'    ✨ Lesson {unit_num}: {lesson.title_vi}')

    def create_stage_3_lessons(self):
        """Giai đoạn 3: Nguyên âm đôi (2 bài)"""
        self.stdout.write('  🌊 Stage 3: Nguyên âm đôi...')
        
        # Bài 11: /aɪ/ /eɪ/ /ɔɪ/
        lesson = self.create_lesson(
            stage=self.stage_3,
            part_number=3,
            unit_number=11,
            title='Diphthongs ending in /ɪ/: /aɪ/ /eɪ/ /ɔɪ/',
            title_vi='Nguyên âm đôi tận cùng /ɪ/: /aɪ/ /eɪ/ /ɔɪ/',
            description_vi='Chú ý kéo dài hơi và khẩu hình tròn hơn tiếng Việt.',
            phoneme_symbols=['aɪ', 'eɪ', 'ɔɪ'],
            lesson_type='group',
            estimated_minutes=15,
            xp_reward=20,
            difficulty=3,
            objectives=[
                'Trượt âm mượt mà từ âm đầu sang âm cuối',
                'Không phát âm thành 2 âm riêng biệt',
                'Phát âm đúng: I, my, fly (aɪ)',
                'Phát âm đúng: cake, day, make (eɪ)'
            ],
            lesson_content=[
                {
                    'screen': 1,
                    'type': 'intro',
                    'title': 'Sự hòa quyện âm thanh',
                    'content': {
                        'text': 'Nguyên âm đôi là sự kết hợp 2 nguyên âm thành 1 âm liền mạch.',
                        'importance': 'Người Việt hay phát âm thành 2 âm riêng biệt',
                        'technique': 'Trượt mượt mà, không ngắt quãng'
                    }
                }
            ]
        )
        self.stdout.write(f'    ✨ Lesson 11: {lesson.title_vi}')
        
        # Bài 12: /aʊ/ /əʊ/
        lesson = self.create_lesson(
            stage=self.stage_3,
            part_number=3,
            unit_number=12,
            title='Diphthongs ending in /ʊ/: /aʊ/ /əʊ/',
            title_vi='Nguyên âm đôi tận cùng /ʊ/: /aʊ/ /əʊ/',
            description_vi='Sự chuyển dịch từ âm /a/ hoặc /ə/ sang /u/.',
            phoneme_symbols=['aʊ', 'əʊ'],
            lesson_type='pair_contrast',
            estimated_minutes=12,
            xp_reward=18,
            difficulty=3,
            objectives=[
                'Trượt từ /a/ về /ʊ/: now, house, down',
                'Trượt từ /ə/ về /ʊ/: go, no, home',
                'Không phát âm thành "o" đơn thuần'
            ]
        )
        self.stdout.write(f'    ✨ Lesson 12: {lesson.title_vi}')

    def create_stage_4_lessons(self):
        """Giai đoạn 4: Kỹ thuật nâng cao (3 bài)"""
        self.stdout.write('  🚀 Stage 4: Kỹ thuật nâng cao...')
        
        # Bài 13: Ending Sounds
        lesson = self.create_lesson(
            stage=self.stage_4,
            part_number=4,
            unit_number=13,
            title='Ending Sounds - Never Drop the Final Sound',
            title_vi='Âm cuối - Tầm quan trọng của âm đuôi',
            description_vi='Lỗi phổ biến nhất của người Việt: BỎ SÓT ÂM CUỐI. Học cách phát âm đầy đủ.',
            phoneme_symbols=['p', 't', 'k', 'd', 'g', 's', 'z'],
            lesson_type='review',
            estimated_minutes=20,
            xp_reward=25,
            difficulty=4,
            objectives=[
                'Hiểu tầm quan trọng của âm cuối',
                'Phát âm đúng: like vs lie, lived vs live',
                'Phát âm ending: -p, -t, -k, -b, -d, -g, -s, -z',
                'Tránh "cắt cụt" từ'
            ],
            lesson_content=[
                {
                    'screen': 1,
                    'type': 'intro',
                    'title': 'Lỗi nguy hiểm nhất',
                    'content': {
                        'text': 'Bỏ sót âm cuối là lỗi phổ biến nhất và nguy hiểm nhất của người Việt.',
                        'examples': [
                            '"like" → "lie" (thích → nói dối)',
                            '"lived" → "live" (đã sống → sống)',
                            '"cap" → "ca" (mũ → ?)'
                        ],
                        'importance': 'Có thể gây hiểu lầm nghiêm trọng trong giao tiếp'
                    }
                },
                {
                    'screen': 2,
                    'type': 'theory',
                    'title': 'Các âm cuối phổ biến',
                    'ending_consonants': [
                        {'sound': 'p', 'examples': ['stop', 'cap', 'cup'], 'technique': 'Mím môi, giữ lại hơi'},
                        {'sound': 't', 'examples': ['cat', 'hat', 'sit'], 'technique': 'Lưỡi chạm trên, giữ lại'},
                        {'sound': 'k', 'examples': ['back', 'book', 'like'], 'technique': 'Cuống lưỡi chặn hơi'},
                        {'sound': 'd', 'examples': ['had', 'bed', 'played'], 'technique': 'Lưỡi chạm trên, rung nhẹ'},
                        {'sound': 's', 'examples': ['bus', 'yes', 'cats'], 'technique': 'Xì hơi nhẹ cuối từ'},
                        {'sound': 'z', 'examples': ['is', 'has', 'dogs'], 'technique': 'Xì hơi + rung cổ'}
                    ]
                },
                {
                    'screen': 3,
                    'type': 'practice',
                    'title': 'Luyện tập: Minimal Pairs',
                    'pairs': [
                        ['lie', 'like'],
                        ['bee', 'beat'],
                        ['sea', 'seat'],
                        ['play', 'played']
                    ]
                }
            ]
        )
        self.stdout.write(f'    ✨ Lesson 13: {lesson.title_vi}')
        
        # Bài 14: Consonant Clusters
        lesson = self.create_lesson(
            stage=self.stage_4,
            part_number=4,
            unit_number=14,
            title='Consonant Clusters - Multiple Consonants Together',
            title_vi='Tổ hợp phụ âm - Nhiều phụ âm liền nhau',
            description_vi='Luyện phát âm 2-3 phụ âm cùng lúc: spring, street, plane. Không thêm nguyên âm vào giữa!',
            phoneme_symbols=['s', 'p', 'r', 't', 'k', 'l', 'b'],
            lesson_type='review',
            estimated_minutes=20,
            xp_reward=25,
            difficulty=5,
            objectives=[
                'Phát âm clusters đầu từ: sp-, st-, sk-, pl-, bl-, tr-, dr-, str-',
                'Phát âm clusters cuối từ: -ks, -ts, -dz, -mps, -nts',
                'KHÔNG thêm nguyên âm vào giữa',
                'Ví dụ: "spring" KHÔNG phải "si-pring"'
            ],
            lesson_content=[
                {
                    'screen': 1,
                    'type': 'intro',
                    'title': 'Thử thách khó nhất',
                    'content': {
                        'text': 'Tiếng Việt không có tổ hợp phụ âm, nên người Việt hay BỎ BỚT hoặc THÊM nguyên âm vào.',
                        'examples': [
                            '"spring" → "bring" (bỏ /s/)',
                            '"street" → "stet-reet" (thêm nguyên âm)',
                            '"texts" → "tek-s" (tách riêng)'
                        ]
                    }
                },
                {
                    'screen': 2,
                    'type': 'theory',
                    'title': 'Initial Clusters (đầu từ)',
                    'clusters': [
                        {'pattern': 'sp-', 'examples': ['spring', 'speak', 'spin'], 'technique': 'Phát /s/ và /p/ liền mạch'},
                        {'pattern': 'st-', 'examples': ['street', 'stop', 'student'], 'technique': 'Không ngắt quãng giữa s và t'},
                        {'pattern': 'sk-', 'examples': ['sky', 'school', 'skill'], 'technique': 'Phát âm liên tục'},
                        {'pattern': 'pl-', 'examples': ['plane', 'play', 'please'], 'technique': 'Từ /p/ sang /l/ nhanh'},
                        {'pattern': 'str-', 'examples': ['street', 'strong', 'straight'], 'technique': '3 phụ âm liền - khó nhất!'}
                    ]
                },
                {
                    'screen': 3,
                    'type': 'theory',
                    'title': 'Final Clusters (cuối từ)',
                    'clusters': [
                        {'pattern': '-ks', 'examples': ['books', 'backs', 'talks'], 'technique': 'Phát /k/ rồi /s/ nhẹ'},
                        {'pattern': '-ts', 'examples': ['cats', 'hats', 'wants'], 'technique': 'Từ /t/ sang /s/'},
                        {'pattern': '-mps', 'examples': ['lamps', 'jumps', 'stamps'], 'technique': '3 âm cuối liền'}
                    ]
                }
            ]
        )
        self.stdout.write(f'    ✨ Lesson 14: {lesson.title_vi}')
        
        # Bài 15: Common Vietnamese Mistakes
        lesson = self.create_lesson(
            stage=self.stage_4,
            part_number=4,
            unit_number=15,
            title='Fix Common Vietnamese Mistakes: R/D, N/L, /j/',
            title_vi='Sửa lỗi đặc thù người Việt: R/D, N/L, /j/',
            description_vi='Khắc phục các lỗi mà 90% người Việt mắc phải khi nói tiếng Anh.',
            phoneme_symbols=['r', 'd', 'n', 'l', 'j'],
            lesson_type='review',
            estimated_minutes=20,
            xp_reward=25,
            difficulty=5,
            objectives=[
                'Sửa lỗi R → D: "reason" KHÔNG phải "dizzon"',
                'Phân biệt N và L: "night" vs "light"',
                'Phát âm đúng /j/: "yes" KHÔNG phải "zét" hay "dét"',
                'Hiểu nguyên nhân lỗi từ tiếng mẹ đẻ'
            ],
            lesson_content=[
                {
                    'screen': 1,
                    'type': 'intro',
                    'title': 'Ba lỗi "đặc sản" người Việt',
                    'content': {
                        'text': 'Đây là những lỗi mà hầu hết người Việt đều mắc phải do ảnh hưởng từ tiếng mẹ đẻ.',
                        'statistics': '90% người Việt học tiếng Anh gặp phải ít nhất 1 trong 3 lỗi này'
                    }
                },
                {
                    'screen': 2,
                    'type': 'theory',
                    'title': 'Lỗi 1: R thành D',
                    'mistake': {
                        'problem': 'Âm /r/ tiếng Anh HOÀN TOÀN khác "r" tiếng Việt',
                        'vietnamese_r': 'Tiếng Việt: Lưỡi RUNG (như "r" trong "rau")',
                        'english_r': 'Tiếng Anh: Lưỡi CONG LÊN, KHÔNG rung',
                        'common_errors': [
                            '"red" → "ded"',
                            '"reason" → "dizzon"',
                            '"right" → "dite"'
                        ],
                        'technique': 'Cong lưỡi lên phía sau, KHÔNG chạm vòm miệng, KHÔNG rung'
                    }
                },
                {
                    'screen': 3,
                    'type': 'theory',
                    'title': 'Lỗi 2: N và L nhầm lẫn',
                    'mistake': {
                        'problem': 'Người Việt miền Nam hay nhầm N ↔ L',
                        'examples': [
                            '"night" → "light" (đêm → ánh sáng)',
                            '"long" → "nong"'
                        ],
                        'technique_n': '/n/: Lưỡi chạm vòm miệng, hơi qua mũi',
                        'technique_l': '/l/: Lưỡi chạm vòm miệng, hơi qua HAI BÊN lưỡi'
                    }
                },
                {
                    'screen': 4,
                    'type': 'theory',
                    'title': 'Lỗi 3: Âm /j/ (yes)',
                    'mistake': {
                        'problem': 'Người Việt đọc "yes" thành "zét" hoặc "dét"',
                        'english_j': 'Âm /j/ giống "y" trong "yêu", KHÔNG phải "z" hay "d"',
                        'examples': [
                            '"yes" → "zét" ❌',
                            '"year" → "dia" ❌',
                            '"you" → "du" ❌'
                        ],
                        'technique': 'Phát âm nhanh như "i" trong "yêu", lưỡi nâng cao'
                    }
                },
                {
                    'screen': 5,
                    'type': 'practice',
                    'title': 'Luyện tập tổng hợp',
                    'sentences': [
                        'The red car is right there.',
                        'Did you see the light last night?',
                        'Yes, I know you are young.'
                    ]
                }
            ]
        )
        self.stdout.write(f'    ✨ Lesson 15: {lesson.title_vi}')

    def create_lesson(self, stage, part_number, unit_number, title, title_vi, 
                     description_vi, phoneme_symbols, lesson_type, estimated_minutes,
                     xp_reward, difficulty, objectives=None, lesson_content=None):
        """Helper method to create a lesson"""
        
        lesson, created = PronunciationLesson.objects.update_or_create(
            part_number=part_number,
            unit_number=unit_number,
            defaults={
                'stage': stage,
                'title': title,
                'title_vi': title_vi,
                'description_vi': description_vi,
                'lesson_type': lesson_type,
                'estimated_minutes': estimated_minutes,
                'xp_reward': xp_reward,
                'difficulty': difficulty,
                'status': 'published',
                'objectives': objectives or [],
                'lesson_content': lesson_content or [],
                'order': unit_number
            }
        )
        
        # Add phonemes
        if phoneme_symbols:
            phonemes = Phoneme.objects.filter(ipa_symbol__in=phoneme_symbols)
            lesson.phonemes.set(phonemes)
        
        return lesson
