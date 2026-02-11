"""
Management command to seed complete phoneme data with Vietnamese-specific information.
Based on standard IPA chart: 44 phonemes for English.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.curriculum.models import PhonemeCategory, Phoneme


class Command(BaseCommand):
    help = 'Seeds complete phoneme data with Vietnamese comparisons and common mistakes'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('🔤 Seeding Phonemes...'))
        
        with transaction.atomic():
            self.create_categories()
            self.create_phonemes()
        
        total_phonemes = Phoneme.objects.count()
        self.stdout.write(self.style.SUCCESS(f'✅ Successfully seeded {total_phonemes} phonemes!'))

    def create_categories(self):
        """Create phoneme categories"""
        self.stdout.write('  📁 Creating categories...')
        
        categories = [
            {
                'name': 'Short Vowels',
                'name_vi': 'Nguyên âm ngắn',
                'category_type': 'vowel',
                'description': 'Short monophthong vowels',
                'description_vi': 'Các nguyên âm đơn ngắn',
                'icon': 'fa-circle',
                'order': 1
            },
            {
                'name': 'Long Vowels',
                'name_vi': 'Nguyên âm dài',
                'category_type': 'vowel',
                'description': 'Long monophthong vowels',
                'description_vi': 'Các nguyên âm đơn dài',
                'icon': 'fa-circle',
                'order': 2
            },
            {
                'name': 'Diphthongs',
                'name_vi': 'Nguyên âm đôi',
                'category_type': 'diphthong',
                'description': 'Double vowel sounds',
                'description_vi': 'Âm nguyên âm kép',
                'icon': 'fa-water',
                'order': 3
            },
            {
                'name': 'Plosives',
                'name_vi': 'Phụ âm bật hơi',
                'category_type': 'consonant',
                'description': 'Stop consonants',
                'description_vi': 'Phụ âm tắc',
                'icon': 'fa-fire',
                'order': 4
            },
            {
                'name': 'Fricatives',
                'name_vi': 'Phụ âm xát',
                'category_type': 'consonant',
                'description': 'Friction consonants',
                'description_vi': 'Phụ âm ma sát',
                'icon': 'fa-wind',
                'order': 5
            },
            {
                'name': 'Affricates',
                'name_vi': 'Phụ âm tắc xát',
                'category_type': 'consonant',
                'description': 'Combined stop and friction',
                'description_vi': 'Âm kết hợp tắc và xát',
                'icon': 'fa-bolt',
                'order': 6
            },
            {
                'name': 'Nasals',
                'name_vi': 'Phụ âm mũi',
                'category_type': 'consonant',
                'description': 'Nasal consonants',
                'description_vi': 'Phụ âm qua mũi',
                'icon': 'fa-wind',
                'order': 7
            },
            {
                'name': 'Approximants',
                'name_vi': 'Phụ âm tiếp cận',
                'category_type': 'consonant',
                'description': 'Approximant consonants',
                'description_vi': 'Phụ âm gần nguyên âm',
                'icon': 'fa-stream',
                'order': 8
            },
        ]
        
        for cat_data in categories:
            cat, created = PhonemeCategory.objects.update_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            action = '✨' if created else '🔄'
            self.stdout.write(f"    {action} {cat.name_vi}")

    def create_phonemes(self):
        """Create all 44 phonemes with detailed info"""
        self.stdout.write('  🔤 Creating phonemes...')
        
        # Get categories
        short_vowels = PhonemeCategory.objects.get(name='Short Vowels')
        long_vowels = PhonemeCategory.objects.get(name='Long Vowels')
        diphthongs = PhonemeCategory.objects.get(name='Diphthongs')
        plosives = PhonemeCategory.objects.get(name='Plosives')
        fricatives = PhonemeCategory.objects.get(name='Fricatives')
        affricates = PhonemeCategory.objects.get(name='Affricates')
        nasals = PhonemeCategory.objects.get(name='Nasals')
        approximants = PhonemeCategory.objects.get(name='Approximants')
        
        phonemes_data = [
            # SHORT VOWELS (7)
            {
                'category': short_vowels,
                'ipa_symbol': 'ɪ',
                'vietnamese_approx': 'i ngắn',
                'phoneme_type': 'short_vowel',
                'voicing': 'n/a',
                'mouth_position_vi': 'Miệng mở nhẹ, môi dẹt',
                'tongue_position_vi': 'Lưỡi nâng cao gần vòm miệng',
                'pronunciation_tips_vi': 'Giống "i" ngắn trong tiếng Việt nhưng môi dẹt hơn',
                'vietnamese_comparison': 'Âm /ɪ/ tiếng Anh ngắn và lười hơn "i" tiếng Việt. Ví dụ: sit, bit, hit',
                'common_mistakes_vi': 'Người Việt thường phát âm thành "i" dài /iː/. Ví dụ: "sit" đọc thành "seat"',
                'order': 1
            },
            {
                'category': short_vowels,
                'ipa_symbol': 'e',
                'vietnamese_approx': 'e',
                'phoneme_type': 'short_vowel',
                'voicing': 'n/a',
                'mouth_position_vi': 'Miệng mở vừa, môi dẹt',
                'pronunciation_tips_vi': 'Giống "e" trong "bed", "pen"',
                'vietnamese_comparison': 'Gần với "e" tiếng Việt nhưng miệng mở hơn một chút',
                'common_mistakes_vi': 'Thường nhầm với /æ/ (cat) hoặc /eɪ/ (cake)',
                'order': 2
            },
            {
                'category': short_vowels,
                'ipa_symbol': 'æ',
                'vietnamese_approx': 'á (giữa a và e)',
                'phoneme_type': 'short_vowel',
                'voicing': 'n/a',
                'mouth_position_vi': 'Miệng mở rộng, hàm hạ thấp',
                'pronunciation_tips_vi': 'Giống "a" nhưng môi kéo rộng hơn. Ví dụ: cat, hat, bat',
                'vietnamese_comparison': 'Tiếng Việt không có âm này. Nằm giữa "a" và "e"',
                'common_mistakes_vi': 'Người Việt thường đọc thành "a" hoặc "e". "Cat" đọc thành "cát" hoặc "két"',
                'order': 3
            },
            {
                'category': short_vowels,
                'ipa_symbol': 'ʌ',
                'vietnamese_approx': 'a ngắn (cup)',
                'phoneme_type': 'short_vowel',
                'voicing': 'n/a',
                'mouth_position_vi': 'Miệng mở vừa, môi thả lỏng',
                'pronunciation_tips_vi': 'Âm "a" ngắn, thả lỏng. Ví dụ: cup, but, run',
                'vietnamese_comparison': 'Giống "a" ngắn trong "cát" nhưng lười hơn',
                'common_mistakes_vi': 'Thường nhầm với /ɑː/ (dài). "Cup" vs "Carp"',
                'order': 4
            },
            {
                'category': short_vowels,
                'ipa_symbol': 'ɒ',
                'vietnamese_approx': 'o ngắn tròn',
                'phoneme_type': 'short_vowel',
                'voicing': 'n/a',
                'mouth_position_vi': 'Miệng mở tròn, hàm hạ',
                'pronunciation_tips_vi': 'Môi tròn, âm ngắn. Ví dụ: hot, dog, stop',
                'vietnamese_comparison': 'Tròn miệng hơn "o" tiếng Việt và ngắn hơn',
                'common_mistakes_vi': 'Phát âm thành "ó" hoặc "ọ" tiếng Việt',
                'order': 5
            },
            {
                'category': short_vowels,
                'ipa_symbol': 'ʊ',
                'vietnamese_approx': 'u ngắn',
                'phoneme_type': 'short_vowel',
                'voicing': 'n/a',
                'mouth_position_vi': 'Môi chu tròn nhẹ',
                'pronunciation_tips_vi': 'Âm "u" ngắn. Ví dụ: book, good, put',
                'vietnamese_comparison': 'Ngắn hơn "u" tiếng Việt, môi chu nhẹ hơn',
                'common_mistakes_vi': 'Nhầm với /uː/ dài. "Book" vs "Boot"',
                'order': 6
            },
            {
                'category': short_vowels,
                'ipa_symbol': 'ə',
                'vietnamese_approx': 'ơ (schwa)',
                'phoneme_type': 'short_vowel',
                'voicing': 'n/a',
                'mouth_position_vi': 'Miệng thả lỏng tự nhiên',
                'pronunciation_tips_vi': 'Âm trung tính, lười nhất. Ví dụ: about, camera, the',
                'vietnamese_comparison': 'Âm lười nhất trong tiếng Anh, giống "ơ" nhẹ',
                'common_mistakes_vi': 'Phát âm quá rõ ràng thay vì lười đi',
                'order': 7
            },
            
            # LONG VOWELS (5)
            {
                'category': long_vowels,
                'ipa_symbol': 'iː',
                'vietnamese_approx': 'i dài',
                'phoneme_type': 'long_vowel',
                'voicing': 'n/a',
                'mouth_position_vi': 'Môi kéo dẹt như đang cười',
                'pronunciation_tips_vi': 'Kéo dài hơi. Ví dụ: see, tea, eat',
                'vietnamese_comparison': 'Dài hơn và căng hơn "i" tiếng Việt',
                'common_mistakes_vi': 'Phát âm quá ngắn thành /ɪ/. "Seat" thành "sit"',
                'order': 1
            },
            {
                'category': long_vowels,
                'ipa_symbol': 'ɑː',
                'vietnamese_approx': 'a dài',
                'phoneme_type': 'long_vowel',
                'voicing': 'n/a',
                'mouth_position_vi': 'Miệng mở rộng, hàm hạ thấp',
                'pronunciation_tips_vi': 'Âm "a" dài, ngân vang. Ví dụ: car, far, star',
                'vietnamese_comparison': 'Dài và ngân vang hơn "a" tiếng Việt rất nhiều',
                'common_mistakes_vi': 'Phát âm quá ngắn. "Car" thành "cá"',
                'order': 2
            },
            {
                'category': long_vowels,
                'ipa_symbol': 'ɔː',
                'vietnamese_approx': 'ô dài',
                'phoneme_type': 'long_vowel',
                'voicing': 'n/a',
                'mouth_position_vi': 'Môi tròn, chu lại',
                'pronunciation_tips_vi': 'Âm "ô" dài. Ví dụ: door, more, four',
                'vietnamese_comparison': 'Môi tròn hơn và dài hơn "ô" tiếng Việt',
                'common_mistakes_vi': 'Phát âm thành /ɒ/ ngắn hoặc /oʊ/',
                'order': 3
            },
            {
                'category': long_vowels,
                'ipa_symbol': 'uː',
                'vietnamese_approx': 'u dài',
                'phoneme_type': 'long_vowel',
                'voicing': 'n/a',
                'mouth_position_vi': 'Môi chu tròn mạnh',
                'pronunciation_tips_vi': 'Âm "u" dài, chu môi mạnh. Ví dụ: food, blue, true',
                'vietnamese_comparison': 'Chu môi mạnh hơn và dài hơn "u" tiếng Việt',
                'common_mistakes_vi': 'Phát âm thành /ʊ/ ngắn. "Food" thành "foot"',
                'order': 4
            },
            {
                'category': long_vowels,
                'ipa_symbol': 'ɜː',
                'vietnamese_approx': 'ơ dài',
                'phoneme_type': 'long_vowel',
                'voicing': 'n/a',
                'mouth_position_vi': 'Miệng mở vừa, lưỡi ở giữa',
                'pronunciation_tips_vi': 'Âm "ơ" dài. Ví dụ: bird, her, learn',
                'vietnamese_comparison': 'Tiếng Việt không có âm này. Giống "ơ" kéo dài',
                'common_mistakes_vi': 'Thường nhầm với "a" hoặc "ơ" ngắn',
                'order': 5
            },
            
            # DIPHTHONGS (8)
            {
                'category': diphthongs,
                'ipa_symbol': 'eɪ',
                'vietnamese_approx': 'ay (ây)',
                'phoneme_type': 'diphthong',
                'voicing': 'n/a',
                'mouth_position_vi': 'Bắt đầu từ /e/ trượt lên /ɪ/',
                'pronunciation_tips_vi': 'Trượt từ "e" lên "i". Ví dụ: cake, day, make',
                'vietnamese_comparison': 'Trượt mượt hơn "ay" tiếng Việt',
                'common_mistakes_vi': 'Phát âm thành 2 âm riêng biệt "e-i"',
                'order': 1
            },
            {
                'category': diphthongs,
                'ipa_symbol': 'aɪ',
                'vietnamese_approx': 'ai',
                'phoneme_type': 'diphthong',
                'voicing': 'n/a',
                'mouth_position_vi': 'Bắt đầu từ /a/ trượt lên /ɪ/',
                'pronunciation_tips_vi': 'Trượt từ "a" lên "i". Ví dụ: I, my, fly',
                'vietnamese_comparison': 'Khá giống "ai" tiếng Việt',
                'common_mistakes_vi': 'Phát âm quá ngắn hoặc thành 2 âm',
                'order': 2
            },
            {
                'category': diphthongs,
                'ipa_symbol': 'ɔɪ',
                'vietnamese_approx': 'oi',
                'phoneme_type': 'diphthong',
                'voicing': 'n/a',
                'mouth_position_vi': 'Bắt đầu từ /ɔ/ trượt lên /ɪ/',
                'pronunciation_tips_vi': 'Trượt từ "ô" lên "i". Ví dụ: boy, toy, coin',
                'vietnamese_comparison': 'Giống "oi" tiếng Việt',
                'common_mistakes_vi': 'Ít gặp lỗi với âm này',
                'order': 3
            },
            {
                'category': diphthongs,
                'ipa_symbol': 'aʊ',
                'vietnamese_approx': 'ao (âu)',
                'phoneme_type': 'diphthong',
                'voicing': 'n/a',
                'mouth_position_vi': 'Bắt đầu từ /a/ trượt về /ʊ/',
                'pronunciation_tips_vi': 'Trượt từ "a" về "u". Ví dụ: now, house, down',
                'vietnamese_comparison': 'Giống "ao" tiếng Việt',
                'common_mistakes_vi': 'Phát âm thành "o" dài',
                'order': 4
            },
            {
                'category': diphthongs,
                'ipa_symbol': 'əʊ',
                'vietnamese_approx': 'ơu (ôu)',
                'phoneme_type': 'diphthong',
                'voicing': 'n/a',
                'mouth_position_vi': 'Bắt đầu từ /ə/ trượt về /ʊ/',
                'pronunciation_tips_vi': 'Trượt từ "ơ" về "u". Ví dụ: go, no, home',
                'vietnamese_comparison': 'Khác "o" tiếng Việt, phải trượt âm',
                'common_mistakes_vi': 'Phát âm thành "o" đơn thuần',
                'order': 5
            },
            {
                'category': diphthongs,
                'ipa_symbol': 'ɪə',
                'vietnamese_approx': 'ia',
                'phoneme_type': 'diphthong',
                'voicing': 'n/a',
                'mouth_position_vi': 'Bắt đầu từ /ɪ/ trượt về /ə/',
                'pronunciation_tips_vi': 'Trượt từ "i" về "ơ". Ví dụ: here, ear, beer',
                'vietnamese_comparison': 'Giống "ia" tiếng Việt',
                'common_mistakes_vi': 'Phát âm thành 2 âm riêng',
                'order': 6
            },
            {
                'category': diphthongs,
                'ipa_symbol': 'eə',
                'vietnamese_approx': 'ea',
                'phoneme_type': 'diphthong',
                'voicing': 'n/a',
                'mouth_position_vi': 'Bắt đầu từ /e/ trượt về /ə/',
                'pronunciation_tips_vi': 'Trượt từ "e" về "ơ". Ví dụ: hair, care, there',
                'vietnamese_comparison': 'Tiếng Việt không có âm này',
                'common_mistakes_vi': 'Nhầm với /eɪ/ hoặc /ɛ/',
                'order': 7
            },
            {
                'category': diphthongs,
                'ipa_symbol': 'ʊə',
                'vietnamese_approx': 'ua',
                'phoneme_type': 'diphthong',
                'voicing': 'n/a',
                'mouth_position_vi': 'Bắt đầu từ /ʊ/ trượt về /ə/',
                'pronunciation_tips_vi': 'Trượt từ "u" về "ơ". Ví dụ: tour, poor, sure',
                'vietnamese_comparison': 'Ít dùng trong tiếng Anh hiện đại',
                'common_mistakes_vi': 'Thường bị nhầm với /ɔː/',
                'order': 8
            },
            
            # PLOSIVES (6)
            {
                'category': plosives,
                'ipa_symbol': 'p',
                'vietnamese_approx': 'p',
                'phoneme_type': 'plosive',
                'voicing': 'voiceless',
                'mouth_position_vi': 'Mím môi, bật hơi',
                'pronunciation_tips_vi': 'Bật hơi mạnh. Ví dụ: pen, cup, stop',
                'vietnamese_comparison': 'Bật hơi MẠNH HƠN rất nhiều so với "p" tiếng Việt',
                'common_mistakes_vi': 'Không bật hơi đủ mạnh, nghe như "b"',
                'order': 1
            },
            {
                'category': plosives,
                'ipa_symbol': 'b',
                'vietnamese_approx': 'b',
                'phoneme_type': 'plosive',
                'voicing': 'voiced',
                'mouth_position_vi': 'Mím môi, rung cổ họng',
                'pronunciation_tips_vi': 'Cổ họng rung. Ví dụ: bed, job, big',
                'vietnamese_comparison': 'Rung cổ họng, giống "b" tiếng Việt',
                'common_mistakes_vi': 'Không rung cổ, thành "p"',
                'order': 2
            },
            {
                'category': plosives,
                'ipa_symbol': 't',
                'vietnamese_approx': 't',
                'phoneme_type': 'plosive',
                'voicing': 'voiceless',
                'mouth_position_vi': 'Lưỡi chạm vòm miệng, bật hơi',
                'pronunciation_tips_vi': 'Bật hơi mạnh. Ví dụ: tea, hit, cat',
                'vietnamese_comparison': 'Bật hơi mạnh hơn "t" tiếng Việt',
                'common_mistakes_vi': 'Không bật hơi, nghe như "d"',
                'order': 3
            },
            {
                'category': plosives,
                'ipa_symbol': 'd',
                'vietnamese_approx': 'd',
                'phoneme_type': 'plosive',
                'voicing': 'voiced',
                'mouth_position_vi': 'Lưỡi chạm vòm miệng, rung cổ',
                'pronunciation_tips_vi': 'Cổ họng rung. Ví dụ: dog, had, bed',
                'vietnamese_comparison': 'Rung cổ, giống "d" tiếng Việt',
                'common_mistakes_vi': 'Không rung cổ, thành "t"',
                'order': 4
            },
            {
                'category': plosives,
                'ipa_symbol': 'k',
                'vietnamese_approx': 'k',
                'phoneme_type': 'plosive',
                'voicing': 'voiceless',
                'mouth_position_vi': 'Cuống lưỡi chạm vòm miệng, bật hơi',
                'pronunciation_tips_vi': 'Bật hơi từ cuống lưỡi. Ví dụ: cat, back, key',
                'vietnamese_comparison': 'Bật hơi mạnh hơn "k" tiếng Việt',
                'common_mistakes_vi': 'Không bật hơi đủ mạnh',
                'order': 5
            },
            {
                'category': plosives,
                'ipa_symbol': 'g',
                'vietnamese_approx': 'g',
                'phoneme_type': 'plosive',
                'voicing': 'voiced',
                'mouth_position_vi': 'Cuống lưỡi chạm vòm miệng, rung cổ',
                'pronunciation_tips_vi': 'Cổ họng rung. Ví dụ: go, big, dog',
                'vietnamese_comparison': 'Rung cổ, giống "g" tiếng Việt',
                'common_mistakes_vi': 'Không rung cổ, thành "k"',
                'order': 6
            },
            
            # FRICATIVES (9)
            {
                'category': fricatives,
                'ipa_symbol': 'f',
                'vietnamese_approx': 'f',
                'phoneme_type': 'fricative',
                'voicing': 'voiceless',
                'mouth_position_vi': 'Cắn môi dưới, xì hơi',
                'pronunciation_tips_vi': 'Xì hơi qua khe. Ví dụ: fish, off, photo',
                'vietnamese_comparison': 'Giống "f" tiếng Việt',
                'common_mistakes_vi': 'Ít gặp lỗi',
                'order': 1
            },
            {
                'category': fricatives,
                'ipa_symbol': 'v',
                'vietnamese_approx': 'v',
                'phoneme_type': 'fricative',
                'voicing': 'voiced',
                'mouth_position_vi': 'Cắn môi dưới, rung cổ',
                'pronunciation_tips_vi': 'Rung cổ, xì hơi. Ví dụ: very, have, love',
                'vietnamese_comparison': 'Rung cổ, khác "v" tiếng Việt (không rung)',
                'common_mistakes_vi': 'Người Việt phát âm "v" không rung cổ, thành "f"',
                'order': 2
            },
            {
                'category': fricatives,
                'ipa_symbol': 'θ',
                'vietnamese_approx': 'th (lưỡi đưa ra)',
                'phoneme_type': 'fricative',
                'voicing': 'voiceless',
                'mouth_position_vi': 'Lưỡi chạm răng, xì hơi',
                'pronunciation_tips_vi': 'Đưa lưỡi ra giữa răng. Ví dụ: think, bath, three',
                'vietnamese_comparison': 'Tiếng Việt KHÔNG CÓ âm này',
                'common_mistakes_vi': 'Người Việt thường đọc thành "s" hoặc "t". "Think" thành "sink" hoặc "tink"',
                'order': 3
            },
            {
                'category': fricatives,
                'ipa_symbol': 'ð',
                'vietnamese_approx': 'dh (lưỡi đưa ra, rung)',
                'phoneme_type': 'fricative',
                'voicing': 'voiced',
                'mouth_position_vi': 'Lưỡi chạm răng, rung cổ',
                'pronunciation_tips_vi': 'Đưa lưỡi ra, rung cổ. Ví dụ: this, the, mother',
                'vietnamese_comparison': 'Tiếng Việt KHÔNG CÓ âm này',
                'common_mistakes_vi': 'Người Việt đọc thành "z" hoặc "d". "This" thành "zis" hoặc "dis"',
                'order': 4
            },
            {
                'category': fricatives,
                'ipa_symbol': 's',
                'vietnamese_approx': 's',
                'phoneme_type': 'fricative',
                'voicing': 'voiceless',
                'mouth_position_vi': 'Lưỡi gần vòm miệng, xì hơi',
                'pronunciation_tips_vi': 'Xì hơi sắc. Ví dụ: see, yes, bus',
                'vietnamese_comparison': 'Giống "s" tiếng Việt',
                'common_mistakes_vi': 'Ít gặp lỗi',
                'order': 5
            },
            {
                'category': fricatives,
                'ipa_symbol': 'z',
                'vietnamese_approx': 'z (rung)',
                'phoneme_type': 'fricative',
                'voicing': 'voiced',
                'mouth_position_vi': 'Lưỡi gần vòm miệng, rung cổ',
                'pronunciation_tips_vi': 'Xì hơi, rung cổ. Ví dụ: zoo, buzz, is',
                'vietnamese_comparison': 'Rung cổ, khác "s" ở chỗ cổ rung',
                'common_mistakes_vi': 'Phát âm thành "s" không rung. "Buzz" thành "bus"',
                'order': 6
            },
            {
                'category': fricatives,
                'ipa_symbol': 'ʃ',
                'vietnamese_approx': 'sh (s dài)',
                'phoneme_type': 'fricative',
                'voicing': 'voiceless',
                'mouth_position_vi': 'Cong môi, xì hơi',
                'pronunciation_tips_vi': 'Cong môi, lưỡi lùi. Ví dụ: she, fish, nation',
                'vietnamese_comparison': 'Dài hơn "s" tiếng Việt, cong môi mạnh',
                'common_mistakes_vi': 'Phát âm thành "s" thường hoặc "ch" tiếng Việt',
                'order': 7
            },
            {
                'category': fricatives,
                'ipa_symbol': 'ʒ',
                'vietnamese_approx': 'zh (s dài, rung)',
                'phoneme_type': 'fricative',
                'voicing': 'voiced',
                'mouth_position_vi': 'Cong môi, rung cổ',
                'pronunciation_tips_vi': 'Cong môi, rung cổ. Ví dụ: vision, measure, beige',
                'vietnamese_comparison': 'Tiếng Việt ít dùng, giống "gi" nhẹ',
                'common_mistakes_vi': 'Nhầm với "s" hoặc "z"',
                'order': 8
            },
            {
                'category': fricatives,
                'ipa_symbol': 'h',
                'vietnamese_approx': 'h',
                'phoneme_type': 'fricative',
                'voicing': 'voiceless',
                'mouth_position_vi': 'Thở hơi qua cổ họng',
                'pronunciation_tips_vi': 'Hơi thở nhẹ. Ví dụ: hot, house, help',
                'vietnamese_comparison': 'Giống "h" tiếng Việt',
                'common_mistakes_vi': 'Ít gặp lỗi',
                'order': 9
            },
            
            # AFFRICATES (2)
            {
                'category': affricates,
                'ipa_symbol': 'tʃ',
                'vietnamese_approx': 'ch',
                'phoneme_type': 'affricate',
                'voicing': 'voiceless',
                'mouth_position_vi': 'Cong môi, bật hơi mạnh',
                'pronunciation_tips_vi': 'Kết hợp /t/ + /ʃ/. Ví dụ: church, match, teach',
                'vietnamese_comparison': 'Giống "ch" tiếng Việt nhưng bật hơi mạnh hơn',
                'common_mistakes_vi': 'Không cong môi đủ hoặc không bật hơi đủ mạnh',
                'order': 1
            },
            {
                'category': affricates,
                'ipa_symbol': 'dʒ',
                'vietnamese_approx': 'j (gi)',
                'phoneme_type': 'affricate',
                'voicing': 'voiced',
                'mouth_position_vi': 'Cong môi, rung cổ, bật hơi',
                'pronunciation_tips_vi': 'Kết hợp /d/ + /ʒ/, rung cổ. Ví dụ: job, age, jump',
                'vietnamese_comparison': 'Giống "gi" tiếng Việt nhưng rung cổ mạnh hơn',
                'common_mistakes_vi': 'Không rung cổ đủ, thành /tʃ/',
                'order': 2
            },
            
            # NASALS (3)
            {
                'category': nasals,
                'ipa_symbol': 'm',
                'vietnamese_approx': 'm',
                'phoneme_type': 'nasal',
                'voicing': 'voiced',
                'mouth_position_vi': 'Mím môi, hơi qua mũi',
                'pronunciation_tips_vi': 'Mím môi, rung cổ. Ví dụ: man, some, time',
                'vietnamese_comparison': 'Giống "m" tiếng Việt',
                'common_mistakes_vi': 'Ít gặp lỗi',
                'order': 1
            },
            {
                'category': nasals,
                'ipa_symbol': 'n',
                'vietnamese_approx': 'n',
                'phoneme_type': 'nasal',
                'voicing': 'voiced',
                'mouth_position_vi': 'Lưỡi chạm vòm miệng, hơi qua mũi',
                'pronunciation_tips_vi': 'Lưỡi chạm trên. Ví dụ: no, pen, one',
                'vietnamese_comparison': 'Giống "n" tiếng Việt',
                'common_mistakes_vi': 'Nhầm với /l/. "Night" thành "light"',
                'order': 2
            },
            {
                'category': nasals,
                'ipa_symbol': 'ŋ',
                'vietnamese_approx': 'ng',
                'phoneme_type': 'nasal',
                'voicing': 'voiced',
                'mouth_position_vi': 'Cuống lưỡi chạm vòm miệng, hơi qua mũi',
                'pronunciation_tips_vi': 'Âm "ng" cuối từ. Ví dụ: sing, long, ring',
                'vietnamese_comparison': 'Giống "ng" tiếng Việt',
                'common_mistakes_vi': 'Thêm /g/ vào cuối. "Sing" thành "sing-g"',
                'order': 3
            },
            
            # APPROXIMANTS (4)
            {
                'category': approximants,
                'ipa_symbol': 'l',
                'vietnamese_approx': 'l',
                'phoneme_type': 'lateral',
                'voicing': 'voiced',
                'mouth_position_vi': 'Lưỡi chạm vòm miệng, hơi qua hai bên',
                'pronunciation_tips_vi': 'Lưỡi chạm trên. Ví dụ: love, ball, light',
                'vietnamese_comparison': 'Giống "l" tiếng Việt',
                'common_mistakes_vi': 'Nhầm với /n/. "Light" thành "night"',
                'order': 1
            },
            {
                'category': approximants,
                'ipa_symbol': 'r',
                'vietnamese_approx': 'r',
                'phoneme_type': 'approximant',
                'voicing': 'voiced',
                'mouth_position_vi': 'Lưỡi cong lên, không chạm vòm',
                'pronunciation_tips_vi': 'Lưỡi cong, không rung. Ví dụ: red, car, very',
                'vietnamese_comparison': 'KHÁC HOÀN TOÀN "r" tiếng Việt (không rung lưỡi)',
                'common_mistakes_vi': 'Người Việt phát âm thành "d". "Red" thành "ded", "reason" thành "dizzon"',
                'order': 2
            },
            {
                'category': approximants,
                'ipa_symbol': 'w',
                'vietnamese_approx': 'u (bán nguyên âm)',
                'phoneme_type': 'approximant',
                'voicing': 'voiced',
                'mouth_position_vi': 'Chu môi tròn mạnh',
                'pronunciation_tips_vi': 'Chu môi mạnh. Ví dụ: we, water, away',
                'vietnamese_comparison': 'Chu môi mạnh hơn "u" tiếng Việt',
                'common_mistakes_vi': 'Nhầm với /v/. "West" thành "vest"',
                'order': 3
            },
            {
                'category': approximants,
                'ipa_symbol': 'j',
                'vietnamese_approx': 'y',
                'phoneme_type': 'approximant',
                'voicing': 'voiced',
                'mouth_position_vi': 'Lưỡi nâng cao',
                'pronunciation_tips_vi': 'Giống "i" nhanh. Ví dụ: yes, you, year',
                'vietnamese_comparison': 'Giống "y" tiếng Việt',
                'common_mistakes_vi': 'Người Việt thường đọc thành "z" hoặc "d". "Yes" thành "zét" hoặc "dét"',
                'order': 4
            },
        ]
        
        for p_data in phonemes_data:
            phoneme, created = Phoneme.objects.update_or_create(
                ipa_symbol=p_data['ipa_symbol'],
                defaults=p_data
            )
            action = '✨' if created else '🔄'
            self.stdout.write(f"    {action} /{phoneme.ipa_symbol}/ - {phoneme.vietnamese_approx}")
        
        # Set paired phonemes
        self.set_paired_phonemes()
    
    def set_paired_phonemes(self):
        """Set up paired phonemes (voiced/voiceless)"""
        self.stdout.write('  🔗 Setting up phoneme pairs...')
        
        pairs = [
            ('p', 'b'),
            ('t', 'd'),
            ('k', 'g'),
            ('f', 'v'),
            ('θ', 'ð'),
            ('s', 'z'),
            ('ʃ', 'ʒ'),
            ('tʃ', 'dʒ'),
        ]
        
        for voiceless, voiced in pairs:
            try:
                p1 = Phoneme.objects.get(ipa_symbol=voiceless)
                p2 = Phoneme.objects.get(ipa_symbol=voiced)
                p1.paired_phoneme = p2
                p2.paired_phoneme = p1
                p1.save()
                p2.save()
                self.stdout.write(f"    ✓ Paired /{voiceless}/ ↔ /{voiced}/")
            except Phoneme.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"    ✗ Could not pair /{voiceless}/ ↔ /{voiced}/"))
