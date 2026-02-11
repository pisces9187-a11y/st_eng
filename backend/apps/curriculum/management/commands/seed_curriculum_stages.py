"""
Management command to seed 4 Curriculum Stages for pronunciation learning.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.curriculum.models import CurriculumStage


class Command(BaseCommand):
    help = 'Seeds 4 curriculum stages for pronunciation learning'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('🎯 Seeding Curriculum Stages...'))
        
        with transaction.atomic():
            self.create_stages()
        
        self.stdout.write(self.style.SUCCESS('✅ Successfully seeded 4 curriculum stages!'))

    def create_stages(self):
        """Create 4 curriculum stages"""
        
        stages_data = [
            {
                'number': 1,
                'name': 'Monophthongs - The Soul of Words',
                'name_vi': 'Nguyên âm đơn - Linh hồn của từ',
                'description': 'Master single vowel sounds with correct mouth shapes and duration.',
                'description_vi': 'Làm chủ các âm nguyên âm đơn với khẩu hình và độ dài chính xác.',
                'icon': 'fa-circle',
                'color': '#3B82F6',
                'focus_area': 'Khẩu hình miệng, độ dài nguyên âm (ngắn vs dài)',
                'objectives': [
                    'Phân biệt nguyên âm ngắn và dài',
                    'Làm chủ 7 nguyên âm ngắn: /ɪ/ /e/ /æ/ /ʌ/ /ɒ/ /ʊ/ /ə/',
                    'Làm chủ 5 nguyên âm dài: /iː/ /ɑː/ /ɔː/ /uː/ /ɜː/',
                    'Hiểu được tầm quan trọng của khẩu hình miệng'
                ],
                'estimated_lessons': 4,
                'estimated_hours': 2.0,
                'order': 1
            },
            {
                'number': 2,
                'name': 'Consonant Pairs - Voiced vs Voiceless',
                'name_vi': 'Phụ âm theo cặp - Âm gió và Âm rung',
                'description': 'Learn consonant pairs and master the throat vibration technique.',
                'description_vi': 'Học các cặp phụ âm và làm chủ kỹ thuật rung cổ họng.',
                'icon': 'fa-fire',
                'color': '#EF4444',
                'focus_area': 'Rung cổ họng, bật hơi, vị trí lưỡi',
                'objectives': [
                    'Phân biệt âm hữu thanh (voiced) và vô thanh (voiceless)',
                    'Kỹ thuật đặt tay lên cổ để kiểm tra độ rung',
                    'Làm chủ 6 cặp phụ âm chính',
                    'Khắc phục lỗi không bật hơi đủ mạnh'
                ],
                'estimated_lessons': 6,
                'estimated_hours': 3.0,
                'order': 2
            },
            {
                'number': 3,
                'name': 'Diphthongs - Sound Gliding',
                'name_vi': 'Nguyên âm đôi - Sự hòa quyện âm thanh',
                'description': 'Master gliding vowel sounds that change mid-pronunciation.',
                'description_vi': 'Làm chủ âm nguyên âm trượt, thay đổi trong quá trình phát âm.',
                'icon': 'fa-water',
                'color': '#10B981',
                'focus_area': 'Trượt âm, chuyển động khẩu hình',
                'objectives': [
                    'Hiểu cách kết hợp 2 nguyên âm thành 1 âm đôi',
                    'Làm chủ 8 nguyên âm đôi: /eɪ/ /aɪ/ /ɔɪ/ /aʊ/ /əʊ/ /ɪə/ /eə/ /ʊə/',
                    'Tránh phát âm thành 2 âm riêng biệt',
                    'Kéo dài và trượt âm đúng cách'
                ],
                'estimated_lessons': 2,
                'estimated_hours': 1.5,
                'order': 3
            },
            {
                'number': 4,
                'name': 'Advanced Techniques - Fix Vietnamese Mistakes',
                'name_vi': 'Kỹ thuật nâng cao - Sửa lỗi người Việt',
                'description': 'Master ending sounds, consonant clusters, and fix common Vietnamese mistakes.',
                'description_vi': 'Làm chủ âm cuối, tổ hợp phụ âm, và sửa các lỗi đặc thù người Việt.',
                'icon': 'fa-rocket',
                'color': '#8B5CF6',
                'focus_area': 'Âm cuối, consonant clusters, lỗi R/D, N/L, /j/',
                'objectives': [
                    'Không bỏ sót âm cuối (ending sounds)',
                    'Phát âm tổ hợp phụ âm (spring, street, plane)',
                    'Sửa lỗi R thành D (reason → "dizzon")',
                    'Sửa lỗi nhầm N và L',
                    'Phát âm đúng âm /j/ (yes, year)'
                ],
                'estimated_lessons': 3,
                'estimated_hours': 2.0,
                'order': 4
            }
        ]
        
        for stage_data in stages_data:
            stage, created = CurriculumStage.objects.update_or_create(
                number=stage_data['number'],
                defaults=stage_data
            )
            
            action = '✨ Created' if created else '🔄 Updated'
            self.stdout.write(
                f"  {action} Stage {stage.number}: {stage.name_vi}"
            )
        
        # Set up prerequisites (Stage 2 requires Stage 1, etc.)
        stage_1 = CurriculumStage.objects.get(number=1)
        stage_2 = CurriculumStage.objects.get(number=2)
        stage_3 = CurriculumStage.objects.get(number=3)
        stage_4 = CurriculumStage.objects.get(number=4)
        
        stage_2.required_previous_stages.set([stage_1])
        stage_3.required_previous_stages.set([stage_1, stage_2])
        stage_4.required_previous_stages.set([stage_1, stage_2, stage_3])
        
        self.stdout.write('  🔗 Set up stage prerequisites')
