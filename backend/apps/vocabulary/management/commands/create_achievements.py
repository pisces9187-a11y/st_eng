"""
Management command to create default achievements.
"""

from django.core.management.base import BaseCommand
from apps.vocabulary.models_achievement import Achievement


class Command(BaseCommand):
    help = 'Create default achievements for flashcard system'
    
    def handle(self, *args, **options):
        achievements = [
            # Milestone achievements
            {
                'key': 'first_10_cards',
                'name': '🎓 First Steps',
                'description': 'Learn your first 10 cards',
                'icon': '🎓',
                'category': 'milestone',
                'requirement_type': 'cards_learned',
                'requirement_value': 10,
                'points': 10,
                'order': 1
            },
            {
                'key': 'first_50_cards',
                'name': '📚 Bookworm',
                'description': 'Learn 50 cards',
                'icon': '📚',
                'category': 'milestone',
                'requirement_type': 'cards_learned',
                'requirement_value': 50,
                'points': 50,
                'order': 2
            },
            {
                'key': 'first_100_cards',
                'name': '🏆 Century Maker',
                'description': 'Learn 100 cards',
                'icon': '🏆',
                'category': 'milestone',
                'requirement_type': 'cards_learned',
                'requirement_value': 100,
                'points': 100,
                'order': 3
            },
            {
                'key': 'first_500_cards',
                'name': '⭐ Vocabulary Master',
                'description': 'Learn 500 cards',
                'icon': '⭐',
                'category': 'milestone',
                'requirement_type': 'cards_learned',
                'requirement_value': 500,
                'points': 500,
                'order': 4
            },
            
            # Streak achievements
            {
                'key': 'streak_3_days',
                'name': '🔥 Getting Started',
                'description': 'Maintain a 3-day streak',
                'icon': '🔥',
                'category': 'streak',
                'requirement_type': 'streak_days',
                'requirement_value': 3,
                'points': 15,
                'order': 5
            },
            {
                'key': 'streak_7_days',
                'name': '🔥 Week Warrior',
                'description': 'Maintain a 7-day streak',
                'icon': '🔥',
                'category': 'streak',
                'requirement_type': 'streak_days',
                'requirement_value': 7,
                'points': 35,
                'order': 6
            },
            {
                'key': 'streak_30_days',
                'name': '🔥 Month Master',
                'description': 'Maintain a 30-day streak',
                'icon': '🔥',
                'category': 'streak',
                'requirement_type': 'streak_days',
                'requirement_value': 30,
                'points': 150,
                'order': 7
            },
            {
                'key': 'streak_100_days',
                'name': '🔥 Legend',
                'description': 'Maintain a 100-day streak',
                'icon': '🔥',
                'category': 'streak',
                'requirement_type': 'streak_days',
                'requirement_value': 100,
                'points': 500,
                'order': 8
            },
            
            # Speed achievements
            {
                'key': 'speed_20_day',
                'name': '⚡ Quick Learner',
                'description': 'Learn 20 cards in one day',
                'icon': '⚡',
                'category': 'speed',
                'requirement_type': 'cards_per_day',
                'requirement_value': 20,
                'points': 20,
                'order': 9
            },
            {
                'key': 'speed_50_day',
                'name': '⚡ Speed Demon',
                'description': 'Learn 50 cards in one day',
                'icon': '⚡',
                'category': 'speed',
                'requirement_type': 'cards_per_day',
                'requirement_value': 50,
                'points': 50,
                'order': 10
            },
            
            # Mastery achievements
            {
                'key': 'accuracy_80',
                'name': '🎯 Sharp Shooter',
                'description': 'Achieve 80% overall accuracy',
                'icon': '🎯',
                'category': 'mastery',
                'requirement_type': 'accuracy_rate',
                'requirement_value': 80,
                'points': 40,
                'order': 11
            },
            {
                'key': 'accuracy_90',
                'name': '🎯 Precision Master',
                'description': 'Achieve 90% overall accuracy',
                'icon': '🎯',
                'category': 'mastery',
                'requirement_type': 'accuracy_rate',
                'requirement_value': 90,
                'points': 80,
                'order': 12
            },
            
            # Level achievements
            {
                'key': 'complete_a1',
                'name': '🎓 A1 Complete',
                'description': 'Master 80% of A1 vocabulary',
                'icon': '🎓',
                'category': 'level',
                'requirement_type': 'level_completed',
                'requirement_value': 80,
                'requirement_data': {'level': 'A1'},
                'points': 100,
                'order': 13
            },
            {
                'key': 'complete_a2',
                'name': '🎓 A2 Complete',
                'description': 'Master 80% of A2 vocabulary',
                'icon': '🎓',
                'category': 'level',
                'requirement_type': 'level_completed',
                'requirement_value': 80,
                'requirement_data': {'level': 'A2'},
                'points': 150,
                'order': 14
            },
            {
                'key': 'complete_b1',
                'name': '🎓 B1 Complete',
                'description': 'Master 80% of B1 vocabulary',
                'icon': '🎓',
                'category': 'level',
                'requirement_type': 'level_completed',
                'requirement_value': 80,
                'requirement_data': {'level': 'B1'},
                'points': 200,
                'order': 15
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for ach_data in achievements:
            achievement, created = Achievement.objects.update_or_create(
                key=ach_data['key'],
                defaults=ach_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {achievement.icon} {achievement.name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'↻ Updated: {achievement.icon} {achievement.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Done! Created {created_count}, Updated {updated_count} achievements'
            )
        )
