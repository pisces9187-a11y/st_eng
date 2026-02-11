"""
Management command to populate MinimalPair database with meaningful pairs.

This command creates minimal pair records for phoneme discrimination practice.
Minimal pairs are words that differ in only one phoneme, useful for
learning to distinguish between similar sounds.
"""

from django.core.management.base import BaseCommand
from apps.curriculum.models import Phoneme, MinimalPair


class Command(BaseCommand):
    help = 'Populate MinimalPair database with meaningful phoneme pairs'

    MINIMAL_PAIRS = [
        # /b/ vs /v/
        {'p1_sym': '/b/', 'p2_sym': '/v/', 'w1': 'bat', 'w2': 'vat', 'w1_ipa': '/bæt/', 'w2_ipa': '/væt/', 'w1_m': 'chim con', 'w2_m': 'bể'},
        {'p1_sym': '/b/', 'p2_sym': '/v/', 'w1': 'best', 'w2': 'vest', 'w1_ipa': '/best/', 'w2_ipa': '/vest/', 'w1_m': 'tốt nhất', 'w2_m': 'áo ghi-lê'},
        
        # /p/ vs /b/
        {'p1_sym': '/p/', 'p2_sym': '/b/', 'w1': 'pat', 'w2': 'bat', 'w1_ipa': '/pæt/', 'w2_ipa': '/bæt/', 'w1_m': 'vuốt', 'w2_m': 'chim con'},
        {'p1_sym': '/p/', 'p2_sym': '/b/', 'w1': 'pear', 'w2': 'bear', 'w1_ipa': '/peə/', 'w2_ipa': '/beə/', 'w1_m': 'lê', 'w2_m': 'gấu'},
        
        # /t/ vs /d/
        {'p1_sym': '/t/', 'p2_sym': '/d/', 'w1': 'tap', 'w2': 'dab', 'w1_ipa': '/tæp/', 'w2_ipa': '/dæb/', 'w1_m': 'gõ', 'w2_m': 'chạm lẹ'},
        {'p1_sym': '/t/', 'p2_sym': '/d/', 'w1': 'tear', 'w2': 'dear', 'w1_ipa': '/teə/', 'w2_ipa': '/dɪə/', 'w1_m': 'nước mắt', 'w2_m': 'thân yêu'},
        
        # /k/ vs /g/
        {'p1_sym': '/k/', 'p2_sym': '/g/', 'w1': 'cap', 'w2': 'gap', 'w1_ipa': '/kæp/', 'w2_ipa': '/gæp/', 'w1_m': 'mũ', 'w2_m': 'khoảng trống'},
        {'p1_sym': '/k/', 'p2_sym': '/g/', 'w1': 'kit', 'w2': 'git', 'w1_ipa': '/kɪt/', 'w2_ipa': '/gɪt/', 'w1_m': 'bộ', 'w2_m': 'tên người'},
        
        # /s/ vs /z/
        {'p1_sym': '/s/', 'p2_sym': '/z/', 'w1': 'seal', 'w2': 'zeal', 'w1_ipa': '/siːl/', 'w2_ipa': '/ziːl/', 'w1_m': 'con hải cẩu', 'w2_m': 'nhiệt tình'},
        {'p1_sym': '/s/', 'p2_sym': '/z/', 'w1': 'sue', 'w2': 'zoo', 'w1_ipa': '/suː/', 'w2_ipa': '/zuː/', 'w1_m': 'kiện', 'w2_m': 'vườn thú'},
        
        # /ʃ/ vs /tʃ/
        {'p1_sym': '/ʃ/', 'p2_sym': '/tʃ/', 'w1': 'share', 'w2': 'chair', 'w1_ipa': '/ʃeə/', 'w2_ipa': '/tʃeə/', 'w1_m': 'chia sẻ', 'w2_m': 'ghế'},
        {'p1_sym': '/ʃ/', 'p2_sym': '/tʃ/', 'w1': 'sheet', 'w2': 'cheat', 'w1_ipa': '/ʃiːt/', 'w2_ipa': '/tʃiːt/', 'w1_m': 'tờ', 'w2_m': 'gian lận'},
        
        # /ð/ vs /θ/
        {'p1_sym': '/ð/', 'p2_sym': '/θ/', 'w1': 'this', 'w2': 'thin', 'w1_ipa': '/ðɪs/', 'w2_ipa': '/θɪn/', 'w1_m': 'cái này', 'w2_m': 'mỏng'},
        {'p1_sym': '/ð/', 'p2_sym': '/θ/', 'w1': 'those', 'w2': 'though', 'w1_ipa': '/ðəʊz/', 'w2_ipa': '/ðəʊ/', 'w1_m': 'những cái đó', 'w2_m': 'mặc dù'},
        
        # /l/ vs /r/
        {'p1_sym': '/l/', 'p2_sym': '/r/', 'w1': 'light', 'w2': 'right', 'w1_ipa': '/laɪt/', 'w2_ipa': '/raɪt/', 'w1_m': 'ánh sáng', 'w2_m': 'đúng'},
        {'p1_sym': '/l/', 'p2_sym': '/r/', 'w1': 'long', 'w2': 'wrong', 'w1_ipa': '/lɔːŋ/', 'w2_ipa': '/rɔːŋ/', 'w1_m': 'dài', 'w2_m': 'sai'},
        
        # /w/ vs /v/
        {'p1_sym': '/w/', 'p2_sym': '/v/', 'w1': 'wine', 'w2': 'vine', 'w1_ipa': '/waɪn/', 'w2_ipa': '/vaɪn/', 'w1_m': 'rượu vang', 'w2_m': 'cây nho'},
        {'p1_sym': '/w/', 'p2_sym': '/v/', 'w1': 'wet', 'w2': 'vet', 'w1_ipa': '/wet/', 'w2_ipa': '/vet/', 'w1_m': 'ướt', 'w2_m': 'thú y'},
        
        # /ɪ/ vs /iː/
        {'p1_sym': '/ɪ/', 'p2_sym': '/iː/', 'w1': 'bit', 'w2': 'beat', 'w1_ipa': '/bɪt/', 'w2_ipa': '/biːt/', 'w1_m': 'miếng nhỏ', 'w2_m': 'nhịp đập'},
        {'p1_sym': '/ɪ/', 'p2_sym': '/iː/', 'w1': 'sit', 'w2': 'seat', 'w1_ipa': '/sɪt/', 'w2_ipa': '/siːt/', 'w1_m': 'ngồi', 'w2_m': 'ghế'},
        
        # /ʊ/ vs /uː/
        {'p1_sym': '/ʊ/', 'p2_sym': '/uː/', 'w1': 'book', 'w2': 'boot', 'w1_ipa': '/bʊk/', 'w2_ipa': '/buːt/', 'w1_m': 'sách', 'w2_m': 'ủng'},
        {'p1_sym': '/ʊ/', 'p2_sym': '/uː/', 'w1': 'foot', 'w2': 'food', 'w1_ipa': '/fʊt/', 'w2_ipa': '/fuːd/', 'w1_m': 'bàn chân', 'w2_m': 'thức ăn'},
        
        # /æ/ vs /ʌ/
        {'p1_sym': '/æ/', 'p2_sym': '/ʌ/', 'w1': 'cat', 'w2': 'cut', 'w1_ipa': '/kæt/', 'w2_ipa': '/kʌt/', 'w1_m': 'mèo', 'w2_m': 'cắt'},
        {'p1_sym': '/æ/', 'p2_sym': '/ʌ/', 'w1': 'bad', 'w2': 'bud', 'w1_ipa': '/bæd/', 'w2_ipa': '/bʌd/', 'w1_m': 'xấu', 'w2_m': 'mầm'},
        
        # /ɔː/ vs /ʌ/
        {'p1_sym': '/ɔː/', 'p2_sym': '/ʌ/', 'w1': 'got', 'w2': 'gut', 'w1_ipa': '/gɔːt/', 'w2_ipa': '/gʌt/', 'w1_m': 'có', 'w2_m': 'ruột'},
        {'p1_sym': '/ɔː/', 'p2_sym': '/ʌ/', 'w1': 'cot', 'w2': 'cut', 'w1_ipa': '/kɔːt/', 'w2_ipa': '/kʌt/', 'w1_m': 'cái nôi', 'w2_m': 'cắt'},
        
        # /e/ vs /æ/
        {'p1_sym': '/e/', 'p2_sym': '/æ/', 'w1': 'bed', 'w2': 'bad', 'w1_ipa': '/bed/', 'w2_ipa': '/bæd/', 'w1_m': 'giường', 'w2_m': 'xấu'},
        {'p1_sym': '/e/', 'p2_sym': '/æ/', 'w1': 'pen', 'w2': 'pan', 'w1_ipa': '/pen/', 'w2_ipa': '/pæn/', 'w1_m': 'bút', 'w2_m': 'chảo'},
        
        # /aɪ/ vs /ɔɪ/
        {'p1_sym': '/aɪ/', 'p2_sym': '/ɔɪ/', 'w1': 'mile', 'w2': 'moil', 'w1_ipa': '/maɪl/', 'w2_ipa': '/mɔɪl/', 'w1_m': 'dặm', 'w2_m': 'khuấy động'},
        {'p1_sym': '/aɪ/', 'p2_sym': '/ɔɪ/', 'w1': 'price', 'w2': 'choice', 'w1_ipa': '/praɪs/', 'w2_ipa': '/tʃɔɪs/', 'w1_m': 'giá', 'w2_m': 'lựa chọn'},
    ]

    def handle(self, *args, **options):
        created = 0
        skipped = 0

        for pair_data in self.MINIMAL_PAIRS:
            try:
                # Get phonemes
                phoneme_1 = Phoneme.objects.get(ipa_symbol=pair_data['p1_sym'])
                phoneme_2 = Phoneme.objects.get(ipa_symbol=pair_data['p2_sym'])

                # Check if pair already exists
                existing = MinimalPair.objects.filter(
                    phoneme_1=phoneme_1,
                    phoneme_2=phoneme_2,
                    word_1=pair_data['w1'],
                    word_2=pair_data['w2']
                ).exists()

                if existing:
                    skipped += 1
                    self.stdout.write(f"[SKIP] {pair_data['p1_sym']} vs {pair_data['p2_sym']}: {pair_data['w1']} vs {pair_data['w2']}")
                    continue

                # Create minimal pair
                MinimalPair.objects.create(
                    phoneme_1=phoneme_1,
                    phoneme_2=phoneme_2,
                    word_1=pair_data['w1'],
                    word_2=pair_data['w2'],
                    word_1_ipa=pair_data['w1_ipa'],
                    word_2_ipa=pair_data['w2_ipa'],
                    word_1_meaning=pair_data['w1_m'],
                    word_2_meaning=pair_data['w2_m'],
                    difference_note_vi=f"Contrast: {pair_data['p1_sym']} vs {pair_data['p2_sym']}"
                )

                created += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"[OK] {pair_data['p1_sym']} vs {pair_data['p2_sym']}: {pair_data['w1']} vs {pair_data['w2']}"
                    )
                )

            except Phoneme.DoesNotExist as e:
                skipped += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"[ERROR] Phoneme not found: {pair_data['p1_sym']} or {pair_data['p2_sym']}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Complete! Created: {created}, Skipped: {skipped}"
            )
        )
