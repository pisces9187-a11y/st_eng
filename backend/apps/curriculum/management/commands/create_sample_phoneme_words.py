"""
Create sample PhonemeWord data for testing auto_generate_minimal_pairs
"""

from django.core.management.base import BaseCommand
from apps.curriculum.models import Phoneme, PhonemeWord


class Command(BaseCommand):
    help = 'Create sample PhonemeWord data for common phonemes'

    def handle(self, *args, **options):
        sample_data = {
            'p': [
                ('Pen', '/pen/', 'Bút', 'initial'),
                ('Pat', '/pæt/', 'Vỗ nhẹ', 'initial'),
                ('Pack', '/pæk/', 'Đóng gói', 'initial'),
                ('Pig', '/pɪɡ/', 'Con lợn', 'initial'),
                ('Pin', '/pɪn/', 'Ghim', 'initial'),
                ('Pet', '/pet/', 'Thú cưng', 'initial'),
                ('Pit', '/pɪt/', 'Hố', 'initial'),
                ('Pot', '/pɒt/', 'Cái nồi', 'initial'),
            ],
            'b': [
                ('Ben', '/ben/', 'Tên người', 'initial'),
                ('Bat', '/bæt/', 'Con dơi', 'initial'),
                ('Back', '/bæk/', 'Lưng', 'initial'),
                ('Big', '/bɪɡ/', 'To lớn', 'initial'),
                ('Bin', '/bɪn/', 'Thùng', 'initial'),
                ('Bet', '/bet/', 'Cá cược', 'initial'),
                ('Bit', '/bɪt/', 'Chút', 'initial'),
                ('Bot', '/bɒt/', 'Robot', 'initial'),
            ],
            't': [
                ('Tin', '/tɪn/', 'Thiếc', 'initial'),
                ('Ten', '/ten/', 'Số 10', 'initial'),
                ('Tan', '/tæn/', 'Nâu', 'initial'),
                ('Tie', '/taɪ/', 'Cà vạt', 'initial'),
                ('Tip', '/tɪp/', 'Đầu', 'initial'),
                ('Top', '/tɒp/', 'Đỉnh', 'initial'),
            ],
            'd': [
                ('Din', '/dɪn/', 'Ồn ào', 'initial'),
                ('Den', '/den/', 'Hang', 'initial'),
                ('Dan', '/dæn/', 'Tên người', 'initial'),
                ('Die', '/daɪ/', 'Chết', 'initial'),
                ('Dip', '/dɪp/', 'Nhúng', 'initial'),
                ('Don', '/dɒn/', 'Tên người', 'initial'),
            ],
            'iː': [
                ('Sheep', '/ʃiːp/', 'Con cừu', 'medial'),
                ('Seat', '/siːt/', 'Chỗ ngồi', 'medial'),
                ('Feet', '/fiːt/', 'Bàn chân', 'medial'),
                ('Beat', '/biːt/', 'Đánh', 'medial'),
                ('Heat', '/hiːt/', 'Nóng', 'medial'),
            ],
            'ɪ': [
                ('Ship', '/ʃɪp/', 'Con tàu', 'medial'),
                ('Sit', '/sɪt/', 'Ngồi', 'medial'),
                ('Fit', '/fɪt/', 'Vừa vặn', 'medial'),
                ('Bit', '/bɪt/', 'Chút', 'medial'),
                ('Hit', '/hɪt/', 'Đánh', 'medial'),
            ],
        }

        created_count = 0
        skipped_count = 0

        for ipa_symbol, words in sample_data.items():
            try:
                phoneme = Phoneme.objects.get(ipa_symbol=ipa_symbol)
                
                self.stdout.write(f"\n📚 Processing /{ipa_symbol}/...")
                
                for word, ipa, meaning, position in words:
                    # Check if exists
                    if PhonemeWord.objects.filter(
                        phoneme=phoneme,
                        word=word
                    ).exists():
                        skipped_count += 1
                        self.stdout.write(
                            self.style.WARNING(f"  ⏭️  {word} already exists")
                        )
                        continue
                    
                    # Create
                    PhonemeWord.objects.create(
                        phoneme=phoneme,
                        word=word,
                        ipa_transcription=ipa,
                        meaning_vi=meaning,
                        phoneme_position=position,
                        order=created_count
                    )
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"  ✅ Created: {word} {ipa}")
                    )
                
            except Phoneme.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f"\n⚠️  Phoneme /{ipa_symbol}/ not found - skipping"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n\n✅ Migration complete!\n"
                f"   Created: {created_count} PhonemeWords\n"
                f"   Skipped: {skipped_count} (already exist)\n"
                f"   Total: {created_count + skipped_count}"
            )
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"\n💡 Now you can run:\n"
                f"   python manage.py auto_generate_minimal_pairs --phoneme1 p --phoneme2 b"
            )
        )
