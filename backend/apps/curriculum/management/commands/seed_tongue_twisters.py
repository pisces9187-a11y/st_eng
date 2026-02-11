"""
Management command to seed tongue twisters for practice.
"""

from django.core.management.base import BaseCommand
from apps.curriculum.models import TongueTwister, Phoneme


class Command(BaseCommand):
    help = 'Seed tongue twisters for pronunciation practice'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding tongue twisters...')
        
        # Define tongue twisters
        twisters_data = [
            # Easy - Short and simple
            {
                'text': 'She sells seashells by the seashore.',
                'meaning_vi': 'Cô ấy bán vỏ sò ở bờ biển.',
                'difficulty': 1,
                'difficulty_level': 'easy',
                'phoneme_symbol': 's'
            },
            {
                'text': 'Peter Piper picked a peck of pickled peppers.',
                'meaning_vi': 'Peter Piper hái một giỏ ớt ngâm chua.',
                'difficulty': 2,
                'difficulty_level': 'easy',
                'phoneme_symbol': 'p'
            },
            {
                'text': 'Red lorry, yellow lorry.',
                'meaning_vi': 'Xe tải đỏ, xe tải vàng.',
                'difficulty': 2,
                'difficulty_level': 'easy',
                'phoneme_symbol': 'r'
            },
            {
                'text': 'How much wood would a woodchuck chuck?',
                'meaning_vi': 'Một con sóc gỗ sẽ ném bao nhiêu củi?',
                'difficulty': 2,
                'difficulty_level': 'easy',
                'phoneme_symbol': 'w'
            },
            
            # Medium - Longer phrases
            {
                'text': 'Six thick thistle sticks.',
                'meaning_vi': 'Sáu que cây kế dày.',
                'difficulty': 3,
                'difficulty_level': 'medium',
                'phoneme_symbol': 'θ'
            },
            {
                'text': 'The thirty-three thieves thought that they thrilled the throne.',
                'meaning_vi': 'Ba mươi ba tên trộm nghĩ rằng họ đã làm rung chuyển ngai vàng.',
                'difficulty': 3,
                'difficulty_level': 'medium',
                'phoneme_symbol': 'θ'
            },
            {
                'text': 'I scream, you scream, we all scream for ice cream.',
                'meaning_vi': 'Tôi la hét, bạn la hét, tất cả chúng ta la hét vì kem.',
                'difficulty': 3,
                'difficulty_level': 'medium',
                'phoneme_symbol': 'iː'
            },
            {
                'text': 'Can you can a can as a canner can can a can?',
                'meaning_vi': 'Bạn có thể đóng hộp một cái hộp như một người đóng hộp có thể đóng hộp một cái hộp?',
                'difficulty': 3,
                'difficulty_level': 'medium',
                'phoneme_symbol': 'k'
            },
            {
                'text': 'Betty Botter bought some butter, but the butter was bitter.',
                'meaning_vi': 'Betty Botter mua một ít bơ, nhưng bơ bị đắng.',
                'difficulty': 3,
                'difficulty_level': 'medium',
                'phoneme_symbol': 'b'
            },
            
            # Hard - Complex and long
            {
                'text': 'If a dog chews shoes, whose shoes does he choose?',
                'meaning_vi': 'Nếu một con chó nhai giày, nó chọn giày của ai?',
                'difficulty': 4,
                'difficulty_level': 'hard',
                'phoneme_symbol': 'ʃ'
            },
            {
                'text': 'How can a clam cram in a clean cream can?',
                'meaning_vi': 'Làm thế nào một con nghêu có thể nhồi nhét vào một lon kem sạch?',
                'difficulty': 4,
                'difficulty_level': 'hard',
                'phoneme_symbol': 'k'
            },
            {
                'text': 'I saw a kitten eating chicken in the kitchen.',
                'meaning_vi': 'Tôi thấy một chú mèo con đang ăn gà trong bếp.',
                'difficulty': 4,
                'difficulty_level': 'hard',
                'phoneme_symbol': 'tʃ'
            },
            {
                'text': 'Through three cheese trees three free fleas flew.',
                'meaning_vi': 'Qua ba cây phô mai, ba con bọ chét tự do bay.',
                'difficulty': 5,
                'difficulty_level': 'hard',
                'phoneme_symbol': 'θ'
            },
            {
                'text': 'Fuzzy Wuzzy was a bear. Fuzzy Wuzzy had no hair. Fuzzy Wuzzy wasn\'t fuzzy, was he?',
                'meaning_vi': 'Fuzzy Wuzzy là một con gấu. Fuzzy Wuzzy không có lông. Fuzzy Wuzzy không xù xì, phải không?',
                'difficulty': 5,
                'difficulty_level': 'hard',
                'phoneme_symbol': 'z'
            },
            {
                'text': 'Pad kid poured curd pulled cod.',
                'meaning_vi': 'Đứa trẻ đổ sữa đông kéo cá tuyết.',
                'difficulty': 5,
                'difficulty_level': 'hard',
                'phoneme_symbol': 'k'
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for data in twisters_data:
            # Try to find phoneme
            phoneme = None
            if data.get('phoneme_symbol'):
                try:
                    phoneme = Phoneme.objects.get(ipa_symbol=data['phoneme_symbol'])
                except Phoneme.DoesNotExist:
                    self.stdout.write(self.style.WARNING(
                        f"Phoneme /{data['phoneme_symbol']}/ not found. Skipping phoneme link."
                    ))
            
            # Create or update tongue twister
            twister, created = TongueTwister.objects.update_or_create(
                text=data['text'],
                defaults={
                    'meaning_vi': data.get('meaning_vi', ''),
                    'difficulty': data.get('difficulty', 1),
                    'difficulty_level': data.get('difficulty_level', 'easy'),
                    'phoneme': phoneme,
                    'is_active': True,
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created: {twister.text[:50]}...'))
            else:
                updated_count += 1
                self.stdout.write(f'Updated: {twister.text[:50]}...')
        
        self.stdout.write(self.style.SUCCESS(
            f'\nCompleted! Created: {created_count}, Updated: {updated_count}'
        ))
