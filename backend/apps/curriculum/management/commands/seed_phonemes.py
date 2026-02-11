"""
Management command to seed English IPA phonemes (44 sounds) into database.
Run: python manage.py seed_phonemes
"""

from django.core.management.base import BaseCommand
from apps.curriculum.models import PhonemeCategory, Phoneme


class Command(BaseCommand):
    help = 'Seed English IPA phonemes (44 sounds) into database'

    def handle(self, *args, **options):
        self.stdout.write('Seeding phonemes...')
        
        # Clear existing data
        Phoneme.objects.all().delete()
        PhonemeCategory.objects.all().delete()
        
        # =====================================================================
        # 1. NGUYÊN ÂM NGẮN (Short Vowels) - 7 sounds
        # =====================================================================
        cat_short_vowels = PhonemeCategory.objects.create(
            name='Short Vowels',
            name_vi='Nguyên âm ngắn',
            category_type='vowel',
            order=1
        )
        
        Phoneme.objects.create(category=cat_short_vowels, ipa_symbol='ɪ', vietnamese_approx='i ngắn (sit)', phoneme_type='short_vowel', voicing='n/a', mouth_position_vi='Miệng mở nhẹ, lưỡi cao phía trước', pronunciation_tips_vi='Giống "i" ngắn. Ví dụ: sit, hit, bit', order=1)
        Phoneme.objects.create(category=cat_short_vowels, ipa_symbol='e', vietnamese_approx='e (bed)', phoneme_type='short_vowel', voicing='n/a', mouth_position_vi='Miệng mở vừa, lưỡi giữa-cao', pronunciation_tips_vi='Giống "e" tiếng Việt. Ví dụ: bed, red, pen', order=2)
        Phoneme.objects.create(category=cat_short_vowels, ipa_symbol='æ', vietnamese_approx='ê mở rộng (cat)', phoneme_type='short_vowel', voicing='n/a', mouth_position_vi='Miệng mở rộng, hàm hạ thấp', pronunciation_tips_vi='Mở miệng rộng. Ví dụ: cat, hat, bad', order=3)
        Phoneme.objects.create(category=cat_short_vowels, ipa_symbol='ʌ', vietnamese_approx='a ngắn (cup)', phoneme_type='short_vowel', voicing='n/a', mouth_position_vi='Miệng mở vừa, lưỡi thư giãn', pronunciation_tips_vi='Giống "a" ngắn. Ví dụ: cup, bus, love', order=4)
        Phoneme.objects.create(category=cat_short_vowels, ipa_symbol='ʊ', vietnamese_approx='u ngắn (book)', phoneme_type='short_vowel', voicing='n/a', mouth_position_vi='Môi tròn nhẹ, lưỡi phía sau', pronunciation_tips_vi='Giống "u" ngắn. Ví dụ: book, good, put', order=5)
        Phoneme.objects.create(category=cat_short_vowels, ipa_symbol='ɒ', vietnamese_approx='ô (hot)', phoneme_type='short_vowel', voicing='n/a', mouth_position_vi='Miệng mở rộng, môi tròn', pronunciation_tips_vi='Giống "ô" mở rộng. Ví dụ: hot, dog, what', order=6)
        Phoneme.objects.create(category=cat_short_vowels, ipa_symbol='ə', vietnamese_approx='ơ nhẹ (schwa)', phoneme_type='short_vowel', voicing='n/a', mouth_position_vi='Miệng và lưỡi thư giãn', pronunciation_tips_vi='Âm trung tính, rất ngắn. Ví dụ: about, sofa', order=7)
        
        # =====================================================================
        # 2. NGUYÊN ÂM DÀI (Long Vowels) - 5 sounds
        # =====================================================================
        cat_long_vowels = PhonemeCategory.objects.create(
            name='Long Vowels',
            name_vi='Nguyên âm dài',
            category_type='vowel',
            order=2
        )
        
        Phoneme.objects.create(category=cat_long_vowels, ipa_symbol='iː', vietnamese_approx='i dài (see)', phoneme_type='long_vowel', voicing='n/a', mouth_position_vi='Lưỡi cao phía trước, miệng cười nhẹ', pronunciation_tips_vi='Kéo dài âm "i". Ví dụ: see, meat, feet', order=1)
        Phoneme.objects.create(category=cat_long_vowels, ipa_symbol='uː', vietnamese_approx='u dài (food)', phoneme_type='long_vowel', voicing='n/a', mouth_position_vi='Môi tròn chu ra, lưỡi phía sau', pronunciation_tips_vi='Kéo dài âm "u", môi tròn. Ví dụ: food, blue, two', order=2)
        Phoneme.objects.create(category=cat_long_vowels, ipa_symbol='ɜː', vietnamese_approx='ơ dài (bird)', phoneme_type='long_vowel', voicing='n/a', mouth_position_vi='Lưỡi ở giữa, miệng mở vừa', pronunciation_tips_vi='Giống "ơ" dài. Ví dụ: bird, girl, word', order=3)
        Phoneme.objects.create(category=cat_long_vowels, ipa_symbol='ɔː', vietnamese_approx='ô dài (door)', phoneme_type='long_vowel', voicing='n/a', mouth_position_vi='Miệng mở tròn, môi chu ra', pronunciation_tips_vi='Giống "ô" dài, môi tròn. Ví dụ: door, law, call', order=4)
        Phoneme.objects.create(category=cat_long_vowels, ipa_symbol='ɑː', vietnamese_approx='a dài (car)', phoneme_type='long_vowel', voicing='n/a', mouth_position_vi='Miệng mở rộng, lưỡi thấp', pronunciation_tips_vi='Giống "a" dài. Ví dụ: car, father, dark', order=5)
        
        # =====================================================================
        # 3. NGUYÊN ÂM ĐÔI (Diphthongs) - 8 sounds
        # =====================================================================
        cat_diphthongs = PhonemeCategory.objects.create(
            name='Diphthongs',
            name_vi='Nguyên âm đôi',
            category_type='diphthong',
            order=3
        )
        
        Phoneme.objects.create(category=cat_diphthongs, ipa_symbol='eɪ', vietnamese_approx='ây (day)', phoneme_type='diphthong', voicing='n/a', mouth_position_vi='Từ e sang i', pronunciation_tips_vi='Trượt từ "e" lên "i". Ví dụ: day, make, say', order=1)
        Phoneme.objects.create(category=cat_diphthongs, ipa_symbol='aɪ', vietnamese_approx='ai (my)', phoneme_type='diphthong', voicing='n/a', mouth_position_vi='Từ a sang i', pronunciation_tips_vi='Trượt từ "a" lên "i". Ví dụ: my, time, high', order=2)
        Phoneme.objects.create(category=cat_diphthongs, ipa_symbol='ɔɪ', vietnamese_approx='ôi (boy)', phoneme_type='diphthong', voicing='n/a', mouth_position_vi='Từ ô sang i', pronunciation_tips_vi='Trượt từ "ô" lên "i". Ví dụ: boy, coin, toy', order=3)
        Phoneme.objects.create(category=cat_diphthongs, ipa_symbol='aʊ', vietnamese_approx='au (now)', phoneme_type='diphthong', voicing='n/a', mouth_position_vi='Từ a sang u', pronunciation_tips_vi='Trượt từ "a" lên "u". Ví dụ: now, house, loud', order=4)
        Phoneme.objects.create(category=cat_diphthongs, ipa_symbol='əʊ', vietnamese_approx='ơu (go)', phoneme_type='diphthong', voicing='n/a', mouth_position_vi='Từ ơ sang u', pronunciation_tips_vi='Trượt từ "ơ" lên "u". Ví dụ: go, know, home', order=5)
        Phoneme.objects.create(category=cat_diphthongs, ipa_symbol='ɪə', vietnamese_approx='ia (here)', phoneme_type='diphthong', voicing='n/a', mouth_position_vi='Từ i sang ơ', pronunciation_tips_vi='Trượt từ "i" xuống "ơ". Ví dụ: here, ear, beer', order=6)
        Phoneme.objects.create(category=cat_diphthongs, ipa_symbol='eə', vietnamese_approx='ea (hair)', phoneme_type='diphthong', voicing='n/a', mouth_position_vi='Từ e sang ơ', pronunciation_tips_vi='Trượt từ "e" xuống "ơ". Ví dụ: hair, care, there', order=7)
        Phoneme.objects.create(category=cat_diphthongs, ipa_symbol='ʊə', vietnamese_approx='ua (tour)', phoneme_type='diphthong', voicing='n/a', mouth_position_vi='Từ u sang ơ', pronunciation_tips_vi='Trượt từ "u" xuống "ơ". Ví dụ: tour, pure', order=8)
        
        # =====================================================================
        # 4. PHỤ ÂM VÔ THANH (Voiceless Consonants) - 9 sounds
        # =====================================================================
        cat_voiceless = PhonemeCategory.objects.create(
            name='Voiceless Consonants',
            name_vi='Phụ âm vô thanh',
            category_type='consonant',
            order=4
        )
        
        Phoneme.objects.create(category=cat_voiceless, ipa_symbol='p', vietnamese_approx='p (pen)', phoneme_type='plosive', voicing='voiceless', mouth_position_vi='Hai môi khép lại', pronunciation_tips_vi='Khép môi, tạo áp lực rồi mở nhanh. Ví dụ: pen, cup, happy', order=1)
        Phoneme.objects.create(category=cat_voiceless, ipa_symbol='t', vietnamese_approx='t (tea)', phoneme_type='plosive', voicing='voiceless', mouth_position_vi='Lưỡi chạm lợi trên', pronunciation_tips_vi='Lưỡi chạm lợi, bật ra nhanh. Ví dụ: tea, cat, little', order=2)
        Phoneme.objects.create(category=cat_voiceless, ipa_symbol='k', vietnamese_approx='k (cat)', phoneme_type='plosive', voicing='voiceless', mouth_position_vi='Cuống họng', pronunciation_tips_vi='Nâng phần sau lưỡi, bật không khí. Ví dụ: cat, book, school', order=3)
        Phoneme.objects.create(category=cat_voiceless, ipa_symbol='f', vietnamese_approx='f (fish)', phoneme_type='fricative', voicing='voiceless', mouth_position_vi='Răng cắn môi', pronunciation_tips_vi='Răng trên cắn môi dưới, thổi không khí. Ví dụ: fish, coffee, laugh', order=4)
        Phoneme.objects.create(category=cat_voiceless, ipa_symbol='θ', vietnamese_approx='th (think)', phoneme_type='fricative', voicing='voiceless', mouth_position_vi='Lưỡi giữa hai hàm răng', pronunciation_tips_vi='Lưỡi giữa răng, thổi không khí. Ví dụ: think, bath, three', order=5)
        Phoneme.objects.create(category=cat_voiceless, ipa_symbol='s', vietnamese_approx='s (sun)', phoneme_type='fricative', voicing='voiceless', mouth_position_vi='Lưỡi gần lợi trên', pronunciation_tips_vi='Tạo tiếng rít. Ví dụ: sun, miss, class', order=6)
        Phoneme.objects.create(category=cat_voiceless, ipa_symbol='ʃ', vietnamese_approx='sh (ship)', phoneme_type='fricative', voicing='voiceless', mouth_position_vi='Lưỡi sau lợi, môi chu', pronunciation_tips_vi='Chu môi, âm "sh". Ví dụ: ship, wash, special', order=7)
        Phoneme.objects.create(category=cat_voiceless, ipa_symbol='tʃ', vietnamese_approx='ch (chair)', phoneme_type='affricate', voicing='voiceless', mouth_position_vi='Kết hợp t và sh', pronunciation_tips_vi='Âm "ch". Ví dụ: chair, teacher, watch', order=8)
        Phoneme.objects.create(category=cat_voiceless, ipa_symbol='h', vietnamese_approx='h (hat)', phoneme_type='fricative', voicing='voiceless', mouth_position_vi='Thanh môn', pronunciation_tips_vi='Thở ra từ họng. Ví dụ: hat, hello, behind', order=9)
        
        # =====================================================================
        # 5. PHỤ ÂM HỮU THANH (Voiced Consonants) - 15 sounds
        # =====================================================================
        cat_voiced = PhonemeCategory.objects.create(
            name='Voiced Consonants',
            name_vi='Phụ âm hữu thanh',
            category_type='consonant',
            order=5
        )
        
        Phoneme.objects.create(category=cat_voiced, ipa_symbol='b', vietnamese_approx='b (boy)', phoneme_type='plosive', voicing='voiced', mouth_position_vi='Hai môi, rung dây thanh', pronunciation_tips_vi='Giống /p/ nhưng rung dây thanh. Ví dụ: boy, cab, rabbit', order=1)
        Phoneme.objects.create(category=cat_voiced, ipa_symbol='d', vietnamese_approx='d (dog)', phoneme_type='plosive', voicing='voiced', mouth_position_vi='Lưỡi chạm lợi, rung', pronunciation_tips_vi='Giống /t/ nhưng rung dây thanh. Ví dụ: dog, bad, middle', order=2)
        Phoneme.objects.create(category=cat_voiced, ipa_symbol='g', vietnamese_approx='g (go)', phoneme_type='plosive', voicing='voiced', mouth_position_vi='Cuống họng, rung', pronunciation_tips_vi='Giống /k/ nhưng rung dây thanh. Ví dụ: go, bag, bigger', order=3)
        Phoneme.objects.create(category=cat_voiced, ipa_symbol='v', vietnamese_approx='v (van)', phoneme_type='fricative', voicing='voiced', mouth_position_vi='Răng cắn môi, rung', pronunciation_tips_vi='Giống /f/ nhưng rung dây thanh. Ví dụ: van, live, love', order=4)
        Phoneme.objects.create(category=cat_voiced, ipa_symbol='ð', vietnamese_approx='th (this)', phoneme_type='fricative', voicing='voiced', mouth_position_vi='Lưỡi giữa răng, rung', pronunciation_tips_vi='Giống /θ/ nhưng rung dây thanh. Ví dụ: this, mother, breathe', order=5)
        Phoneme.objects.create(category=cat_voiced, ipa_symbol='z', vietnamese_approx='z (zoo)', phoneme_type='fricative', voicing='voiced', mouth_position_vi='Lưỡi gần lợi, rung', pronunciation_tips_vi='Giống /s/ nhưng rung dây thanh. Ví dụ: zoo, buzz, is', order=6)
        Phoneme.objects.create(category=cat_voiced, ipa_symbol='ʒ', vietnamese_approx='zh (vision)', phoneme_type='fricative', voicing='voiced', mouth_position_vi='Lưỡi sau lợi, rung', pronunciation_tips_vi='Giống /ʃ/ nhưng rung dây thanh. Ví dụ: vision, measure, beige', order=7)
        Phoneme.objects.create(category=cat_voiced, ipa_symbol='dʒ', vietnamese_approx='j (job)', phoneme_type='affricate', voicing='voiced', mouth_position_vi='Kết hợp d và zh', pronunciation_tips_vi='Âm "j". Ví dụ: job, bridge, large', order=8)
        Phoneme.objects.create(category=cat_voiced, ipa_symbol='m', vietnamese_approx='m (man)', phoneme_type='nasal', voicing='voiced', mouth_position_vi='Khép môi, không khí qua mũi', pronunciation_tips_vi='Khép môi, âm qua mũi. Ví dụ: man, mom, summer', order=9)
        Phoneme.objects.create(category=cat_voiced, ipa_symbol='n', vietnamese_approx='n (no)', phoneme_type='nasal', voicing='voiced', mouth_position_vi='Lưỡi chạm lợi, qua mũi', pronunciation_tips_vi='Lưỡi chạm lợi, âm qua mũi. Ví dụ: no, sun, runner', order=10)
        Phoneme.objects.create(category=cat_voiced, ipa_symbol='ŋ', vietnamese_approx='ng (sing)', phoneme_type='nasal', voicing='voiced', mouth_position_vi='Cuống họng, qua mũi', pronunciation_tips_vi='Âm "ng" tiếng Việt. Ví dụ: sing, bank, thinking', order=11)
        Phoneme.objects.create(category=cat_voiced, ipa_symbol='l', vietnamese_approx='l (leg)', phoneme_type='lateral', voicing='voiced', mouth_position_vi='Lưỡi chạm lợi, hai bên', pronunciation_tips_vi='Lưỡi chạm lợi, không khí qua hai bên. Ví dụ: leg, ball, hello', order=12)
        Phoneme.objects.create(category=cat_voiced, ipa_symbol='r', vietnamese_approx='r (red)', phoneme_type='approximant', voicing='voiced', mouth_position_vi='Cuốn lưỡi lên', pronunciation_tips_vi='Cuốn lưỡi lên, không chạm vòm miệng. Ví dụ: red, car, sorry', order=13)
        Phoneme.objects.create(category=cat_voiced, ipa_symbol='w', vietnamese_approx='w (wet)', phoneme_type='approximant', voicing='voiced', mouth_position_vi='Môi tròn như /u/', pronunciation_tips_vi='Chu môi tròn rồi mở nhanh. Ví dụ: wet, swim, queen', order=14)
        Phoneme.objects.create(category=cat_voiced, ipa_symbol='j', vietnamese_approx='y (yes)', phoneme_type='approximant', voicing='voiced', mouth_position_vi='Lưỡi cao như /i/', pronunciation_tips_vi='Giống "y" tiếng Việt. Ví dụ: yes, you, beyond', order=15)
        
        # Summary
        total = Phoneme.objects.count()
        categories = PhonemeCategory.objects.count()
        
        self.stdout.write(self.style.SUCCESS(
            f'✓ Successfully seeded {total} phonemes in {categories} categories'
        ))
        self.stdout.write(f'  - Short Vowels: 7')
        self.stdout.write(f'  - Long Vowels: 5')
        self.stdout.write(f'  - Diphthongs: 8')
        self.stdout.write(f'  - Voiceless Consonants: 9')
        self.stdout.write(f'  - Voiced Consonants: 15')
        self.stdout.write(f'  Total: 44 English phonemes')
