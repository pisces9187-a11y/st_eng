"""
Tests for UserPhonemeProgress stage management.

Tests cover:
- Stage transitions
- Unlock logic
- Progress tracking
- Helper methods
"""

from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from apps.users.models import User, UserPhonemeProgress
from apps.curriculum.models import Phoneme, PhonemeCategory


class UserPhonemeProgressStageTestCase(TestCase):
    """Test stage management in UserPhonemeProgress model."""
    
    def setUp(self):
        """Create test user and phonemes."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create phoneme category
        self.category = PhonemeCategory.objects.create(
            name='Vowels',
            name_vi='Nguyên âm',
            order=1
        )
        
        # Create test phonemes
        self.phoneme_i = Phoneme.objects.create(
            ipa_symbol='i:',
            category=self.category,
            vietnamese_approx='i dài như "see"',
            phoneme_type='long_vowel'
        )
        
        self.phoneme_I = Phoneme.objects.create(
            ipa_symbol='ɪ',
            category=self.category,
            vietnamese_approx='i ngắn như "sit"',
            phoneme_type='short_vowel'
        )
        
        # Create progress object
        self.progress = UserPhonemeProgress.objects.create(
            user=self.user,
            phoneme=self.phoneme_i
        )
    
    def test_initial_stage_is_not_started(self):
        """Test that newly created progress starts at 'not_started'."""
        self.assertEqual(self.progress.current_stage, 'not_started')
        self.assertIsNone(self.progress.discovery_date)
    
    def test_mark_as_discovered(self):
        """Test marking phoneme as discovered."""
        self.progress.mark_as_discovered()
        self.progress.refresh_from_db()
        
        self.assertEqual(self.progress.current_stage, 'discovered')
        self.assertIsNotNone(self.progress.discovery_date)
        self.assertAlmostEqual(
            self.progress.discovery_date,
            timezone.now(),
            delta=timedelta(seconds=5)
        )
    
    def test_mark_as_discovered_only_once(self):
        """Test that mark_as_discovered only works when not_started."""
        # First discovery
        self.progress.mark_as_discovered()
        first_discovery_date = self.progress.discovery_date
        
        # Try to mark again after advancing stage
        self.progress.current_stage = 'learning'
        self.progress.save()
        self.progress.mark_as_discovered()
        
        # Should not change
        self.assertEqual(self.progress.current_stage, 'learning')
        self.assertEqual(self.progress.discovery_date, first_discovery_date)
    
    def test_start_learning(self):
        """Test starting learning stage."""
        # Discover first
        self.progress.mark_as_discovered()
        
        # Start learning
        self.progress.start_learning()
        self.progress.refresh_from_db()
        
        self.assertEqual(self.progress.current_stage, 'learning')
        self.assertIsNotNone(self.progress.learning_started_at)
    
    def test_start_learning_from_not_started(self):
        """Test that start_learning can skip discovery."""
        self.progress.start_learning()
        self.progress.refresh_from_db()
        
        self.assertEqual(self.progress.current_stage, 'learning')
        self.assertIsNotNone(self.progress.learning_started_at)
    
    def test_start_discrimination(self):
        """Test starting discrimination practice."""
        # Must be in learning stage first
        self.progress.current_stage = 'learning'
        self.progress.save()
        
        self.progress.start_discrimination()
        self.progress.refresh_from_db()
        
        self.assertEqual(self.progress.current_stage, 'discriminating')
        self.assertIsNotNone(self.progress.discrimination_started_at)
    
    def test_cannot_start_discrimination_without_learning(self):
        """Test that discrimination requires learning first."""
        # Try from discovered stage
        self.progress.current_stage = 'discovered'
        self.progress.save()
        
        self.progress.start_discrimination()
        self.progress.refresh_from_db()
        
        # Should not change
        self.assertEqual(self.progress.current_stage, 'discovered')
    
    def test_can_practice_discrimination_logic(self):
        """Test can_practice_discrimination() method."""
        # Not allowed at start
        self.assertFalse(self.progress.can_practice_discrimination())
        
        # Not allowed when discovered
        self.progress.current_stage = 'discovered'
        self.assertFalse(self.progress.can_practice_discrimination())
        
        # Allowed when learning
        self.progress.current_stage = 'learning'
        self.assertTrue(self.progress.can_practice_discrimination())
        
        # Allowed when discriminating
        self.progress.current_stage = 'discriminating'
        self.assertTrue(self.progress.can_practice_discrimination())
        
        # Allowed when producing
        self.progress.current_stage = 'producing'
        self.assertTrue(self.progress.can_practice_discrimination())
        
        # Allowed when mastered
        self.progress.current_stage = 'mastered'
        self.assertTrue(self.progress.can_practice_discrimination())
    
    def test_update_discrimination_progress(self):
        """Test updating discrimination progress."""
        self.progress.current_stage = 'discriminating'
        self.progress.save()
        
        # First attempt: 7/10 correct
        self.progress.update_discrimination_progress(correct=7, total=10)
        self.progress.refresh_from_db()
        
        self.assertEqual(self.progress.discrimination_attempts, 10)
        self.assertEqual(self.progress.discrimination_correct, 7)
        self.assertAlmostEqual(self.progress.discrimination_accuracy, 0.7, places=2)
        self.assertIsNotNone(self.progress.last_practiced_at)
    
    def test_update_discrimination_progress_cumulative(self):
        """Test that discrimination progress accumulates over multiple sessions."""
        self.progress.current_stage = 'discriminating'
        self.progress.save()
        
        # Session 1: 7/10
        self.progress.update_discrimination_progress(correct=7, total=10)
        
        # Session 2: 9/10
        self.progress.update_discrimination_progress(correct=9, total=10)
        
        self.progress.refresh_from_db()
        
        # Total: 16/20 = 80%
        self.assertEqual(self.progress.discrimination_attempts, 20)
        self.assertEqual(self.progress.discrimination_correct, 16)
        self.assertAlmostEqual(self.progress.discrimination_accuracy, 0.8, places=2)
    
    def test_can_practice_production_requires_80_percent(self):
        """Test that production requires 80% discrimination accuracy."""
        self.progress.current_stage = 'discriminating'
        self.progress.save()
        
        # 70% accuracy - not allowed
        self.progress.update_discrimination_progress(correct=7, total=10)
        self.assertFalse(self.progress.can_practice_production())
        
        # 80% accuracy - allowed
        self.progress.update_discrimination_progress(correct=1, total=1)  # Now 8/11 = 72%
        self.assertFalse(self.progress.can_practice_production())
        
        # Add more correct answers to reach 80%
        self.progress.update_discrimination_progress(correct=9, total=9)  # Now 17/20 = 85%
        self.assertTrue(self.progress.can_practice_production())
    
    def test_start_production_requires_unlock(self):
        """Test that start_production checks unlock requirements."""
        self.progress.current_stage = 'discriminating'
        self.progress.discrimination_accuracy = 0.85  # 85% - unlocked
        self.progress.save()
        
        self.progress.start_production()
        self.progress.refresh_from_db()
        
        self.assertEqual(self.progress.current_stage, 'producing')
        self.assertIsNotNone(self.progress.production_started_at)
    
    def test_cannot_start_production_without_80_percent(self):
        """Test that production is locked under 80%."""
        self.progress.current_stage = 'discriminating'
        self.progress.discrimination_accuracy = 0.75  # 75% - locked
        self.progress.save()
        
        self.progress.start_production()
        self.progress.refresh_from_db()
        
        # Should not change
        self.assertEqual(self.progress.current_stage, 'discriminating')
        self.assertIsNone(self.progress.production_started_at)
    
    def test_update_production_progress(self):
        """Test updating production progress."""
        self.progress.current_stage = 'producing'
        self.progress.production_best_score = 0.0
        self.progress.save()
        
        # First attempt: 75%
        self.progress.update_production_progress(score=0.75)
        self.progress.refresh_from_db()
        
        self.assertEqual(self.progress.production_attempts, 1)
        self.assertEqual(self.progress.production_best_score, 0.75)
    
    def test_production_best_score_keeps_highest(self):
        """Test that production keeps only the best score."""
        self.progress.current_stage = 'producing'
        self.progress.save()
        
        # First attempt: 75%
        self.progress.update_production_progress(score=0.75)
        
        # Second attempt: 65% (worse)
        self.progress.update_production_progress(score=0.65)
        
        # Third attempt: 85% (better)
        self.progress.update_production_progress(score=0.85)
        
        self.progress.refresh_from_db()
        
        self.assertEqual(self.progress.production_attempts, 3)
        self.assertEqual(self.progress.production_best_score, 0.85)  # Keeps highest
    
    def test_auto_mastery_when_both_80_percent(self):
        """Test automatic mastery when both discrimination and production >= 80%."""
        self.progress.current_stage = 'producing'
        self.progress.discrimination_accuracy = 0.85  # 85%
        self.progress.save()
        
        # Reach 80% on production
        self.progress.update_production_progress(score=0.82)
        self.progress.refresh_from_db()
        
        self.assertEqual(self.progress.current_stage, 'mastered')
        self.assertIsNotNone(self.progress.mastered_at)
        self.assertEqual(self.progress.mastery_level, 5)
    
    def test_get_stage_display_vi(self):
        """Test Vietnamese stage display names."""
        test_cases = [
            ('not_started', 'Chưa bắt đầu'),
            ('discovered', 'Đã khám phá'),
            ('learning', 'Đang học'),
            ('discriminating', 'Đang phân biệt'),
            ('producing', 'Đang phát âm'),
            ('mastered', 'Đã thành thạo'),
        ]
        
        for stage, expected in test_cases:
            self.progress.current_stage = stage
            self.assertEqual(self.progress.get_stage_display_vi(), expected)
    
    def test_get_next_stage_action(self):
        """Test next action recommendations."""
        # Not started
        self.progress.current_stage = 'not_started'
        self.assertEqual(self.progress.get_next_stage_action(), 'Khám phá âm này')
        
        # Discovered
        self.progress.current_stage = 'discovered'
        self.assertEqual(self.progress.get_next_stage_action(), 'Học lý thuyết')
        
        # Learning
        self.progress.current_stage = 'learning'
        self.assertEqual(self.progress.get_next_stage_action(), 'Luyện phân biệt')
        
        # Discriminating - not yet unlocked production
        self.progress.current_stage = 'discriminating'
        self.progress.discrimination_accuracy = 0.65  # 65%
        action = self.progress.get_next_stage_action()
        self.assertIn('65/80%', action)
        self.assertIn('mở khóa phát âm', action)
        
        # Discriminating - unlocked production
        self.progress.discrimination_accuracy = 0.85  # 85%
        self.assertEqual(self.progress.get_next_stage_action(), 'Luyện phát âm')
        
        # Producing
        self.progress.current_stage = 'producing'
        self.assertEqual(self.progress.get_next_stage_action(), 'Hoàn thiện phát âm')
        
        # Mastered
        self.progress.current_stage = 'mastered'
        self.assertEqual(self.progress.get_next_stage_action(), 'Ôn tập')
    
    def test_stage_progression_full_journey(self):
        """Test complete learning journey from start to mastery."""
        # Stage 1: Discovery
        self.assertEqual(self.progress.current_stage, 'not_started')
        self.progress.mark_as_discovered()
        self.assertEqual(self.progress.current_stage, 'discovered')
        
        # Stage 2: Learning
        self.progress.start_learning()
        self.assertEqual(self.progress.current_stage, 'learning')
        
        # Stage 3: Discrimination
        self.progress.start_discrimination()
        self.assertEqual(self.progress.current_stage, 'discriminating')
        
        # Practice discrimination until 80%
        self.progress.update_discrimination_progress(correct=8, total=10)
        self.assertTrue(self.progress.can_practice_production())
        
        # Stage 4: Production
        self.progress.start_production()
        self.assertEqual(self.progress.current_stage, 'producing')
        
        # Practice production until 80%
        self.progress.update_production_progress(score=0.85)
        
        # Should auto-advance to mastered
        self.assertEqual(self.progress.current_stage, 'mastered')
        self.assertIsNotNone(self.progress.mastered_at)
        self.assertEqual(self.progress.mastery_level, 5)


class UserPhonemeProgressQueryTestCase(TestCase):
    """Test database queries and filtering."""
    
    def setUp(self):
        """Create test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.category = PhonemeCategory.objects.create(
            name='Vowels',
            name_vi='Nguyên âm',
            order=1
        )
        
        # Create 5 phonemes
        for i in range(5):
            phoneme = Phoneme.objects.create(
                ipa_symbol=f'vowel{i}',
                category=self.category,
                vietnamese_approx=f'Vowel {i}',
                phoneme_type='short_vowel'
            )
            
            # Create progress with different stages
            stages = ['not_started', 'discovered', 'learning', 'discriminating', 'producing']
            UserPhonemeProgress.objects.create(
                user=self.user,
                phoneme=phoneme,
                current_stage=stages[i]
            )
    
    def test_filter_by_stage(self):
        """Test filtering progress by stage."""
        discovered = UserPhonemeProgress.objects.filter(
            user=self.user,
            current_stage='discovered'
        )
        self.assertEqual(discovered.count(), 1)
        
        learning_or_discriminating = UserPhonemeProgress.objects.filter(
            user=self.user,
            current_stage__in=['learning', 'discriminating']
        )
        self.assertEqual(learning_or_discriminating.count(), 2)
    
    def test_count_by_stage(self):
        """Test counting progress grouped by stage."""
        from django.db.models import Count
        
        stage_counts = UserPhonemeProgress.objects.filter(
            user=self.user
        ).values('current_stage').annotate(
            count=Count('id')
        ).order_by('current_stage')
        
        self.assertEqual(len(stage_counts), 5)
        
        # Each stage should have 1 phoneme
        for item in stage_counts:
            self.assertEqual(item['count'], 1)
