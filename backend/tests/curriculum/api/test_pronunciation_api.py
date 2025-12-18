"""
Comprehensive API tests for Pronunciation Learning Flow.

Tests all 7 endpoints:
1. PhonemeDiscoverAPIView - POST /phoneme/<id>/discover/
2. PhonemeStartLearningAPIView - POST /phoneme/<id>/start-learning/
3. DiscriminationQuizAPIView - GET /phoneme/<id>/discrimination/quiz/
4. DiscriminationSubmitAPIView - POST /phoneme/<id>/discrimination/submit/
5. ProductionReferenceAPIView - GET /phoneme/<id>/production/reference/
6. ProductionSubmitAPIView - POST /phoneme/<id>/production/submit/
7. OverallProgressAPIView - GET /progress/overall/

Each test covers:
- Success cases (200, 201)
- Error cases (400, 403, 404, 500)
- Authentication required
- Validation rules
- Edge cases
"""

import io
from django.test import TestCase
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User, UserPhonemeProgress
from apps.curriculum.models import (
    Phoneme, PhonemeCategory, MinimalPair, AudioSource
)


class BaseAPITestCase(TestCase):
    """Base test case with common setup for all API tests."""
    
    def setUp(self):
        """Create test user, phonemes, and authenticate."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create another user for permission tests
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        # Create category
        self.category = PhonemeCategory.objects.create(
            name='Vowels',
            name_vi='Nguyên âm',
            order=1
        )
        
        # Create test phonemes
        self.phoneme_i = Phoneme.objects.create(
            ipa_symbol='i:',
            category=self.category,
            vietnamese_approx='i dài',
            phoneme_type='long_vowel',
            tongue_position_vi='Lưỡi cao phía trước',
            mouth_position_vi='Môi căng ngang',
            pronunciation_tips_vi='Phát âm như "ee" trong "see"',
        )
        
        self.phoneme_I = Phoneme.objects.create(
            ipa_symbol='ɪ',
            category=self.category,
            vietnamese_approx='i ngắn',
            phoneme_type='short_vowel',
            tongue_position_vi='Lưỡi hơi thấp hơn',
            mouth_position_vi='Môi lỏa hơn',
            pronunciation_tips_vi='Phát âm như "i" trong "sit"',
        )
        
        # Create minimal pair
        self.minimal_pair = MinimalPair.objects.create(
            phoneme_1=self.phoneme_i,
            phoneme_2=self.phoneme_I,
            word_1='seat',
            word_1_ipa='/si:t/',
            word_1_meaning='chỗ ngồi',
            word_2='sit',
            word_2_ipa='/sɪt/',
            word_2_meaning='ngồi',
            difficulty=1
        )
        
        # Setup API client with authentication
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Setup unauthenticated client
        self.unauth_client = APIClient()
    
    def get_url(self, endpoint):
        """Helper to generate API URLs without namespace issues."""
        return f'/api/v1/{endpoint}'


class PhonemeDiscoverAPITestCase(BaseAPITestCase):
    """Test POST /api/v1/pronunciation/phoneme/<id>/discover/"""
    
    def test_discover_phoneme_success(self):
        """Test successfully discovering a phoneme."""
        url = self.get_url(f'pronunciation/phoneme/{self.phoneme_i.pk}/discover/')
        
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('Đã khám phá âm', response.data['message'])
        
        # Check progress created
        progress = UserPhonemeProgress.objects.get(
            user=self.user,
            phoneme=self.phoneme_i
        )
        self.assertEqual(progress.current_stage, 'discovered')
        self.assertIsNotNone(progress.discovery_date)
    
    def test_discover_phoneme_creates_progress_if_not_exists(self):
        """Test that discover creates UserPhonemeProgress if doesn't exist."""
        self.assertEqual(UserPhonemeProgress.objects.count(), 0)
        
        url = self.get_url(f'pronunciation/phoneme/{self.phoneme_i.pk}/discover/')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(UserPhonemeProgress.objects.count(), 1)
    
    def test_discover_phoneme_idempotent(self):
        """Test that discovering same phoneme multiple times is idempotent."""
        url = self.get_url(f'pronunciation/phoneme/{self.phoneme_i.pk}/discover/')
        
        # First discovery
        response1 = self.client.post(url)
        progress1 = UserPhonemeProgress.objects.get(user=self.user, phoneme=self.phoneme_i)
        discovery_date1 = progress1.discovery_date
        
        # Second discovery (should not change date)
        response2 = self.client.post(url)
        progress2 = UserPhonemeProgress.objects.get(user=self.user, phoneme=self.phoneme_i)
        
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(progress2.discovery_date, discovery_date1)
    
    def test_discover_phoneme_not_found(self):
        """Test discovering non-existent phoneme returns 404."""
        url = self.get_url(f'pronunciation/phoneme/{9999}/discover/')
        
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_discover_phoneme_requires_authentication(self):
        """Test that authentication is required."""
        url = self.get_url(f'pronunciation/phoneme/{self.phoneme_i.pk}/discover/')
        
        response = self.unauth_client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PhonemeStartLearningAPITestCase(BaseAPITestCase):
    """Test POST /api/v1/pronunciation/phoneme/<id>/start-learning/"""
    
    def test_start_learning_success(self):
        """Test successfully starting learning stage."""
        url = self.get_url(f'pronunciation/phoneme/{self.phoneme_i.pk}/start-learning/')
        
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('Bắt đầu học âm', response.data['message'])
        
        # Check progress
        progress = UserPhonemeProgress.objects.get(
            user=self.user,
            phoneme=self.phoneme_i
        )
        self.assertEqual(progress.current_stage, 'learning')
        self.assertIsNotNone(progress.learning_started_at)
    
    def test_start_learning_from_not_started(self):
        """Test starting learning directly from not_started."""
        url = self.get_url(f'pronunciation/phoneme/{self.phoneme_i.pk}/start-learning/')
        
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        progress = UserPhonemeProgress.objects.get(user=self.user, phoneme=self.phoneme_i)
        self.assertEqual(progress.current_stage, 'learning')
    
    def test_start_learning_from_discovered(self):
        """Test starting learning from discovered stage."""
        # Create progress in discovered stage
        progress = UserPhonemeProgress.objects.create(
            user=self.user,
            phoneme=self.phoneme_i,
            current_stage='discovered'
        )
        progress.discovery_date = timezone.now()
        progress.save()
        
        url = self.get_url(f'pronunciation/phoneme/{self.phoneme_i.pk}/start-learning/')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        progress.refresh_from_db()
        self.assertEqual(progress.current_stage, 'learning')
    
    def test_start_learning_not_found(self):
        """Test starting learning for non-existent phoneme."""
        url = self.get_url(f'pronunciation/phoneme/{9999}/start-learning/')
        
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_start_learning_requires_authentication(self):
        """Test authentication required."""
        url = self.get_url(f'pronunciation/phoneme/{self.phoneme_i.pk}/start-learning/')
        
        response = self.unauth_client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DiscriminationQuizAPITestCase(BaseAPITestCase):
    """Test GET /api/v1/pronunciation/phoneme/<id>/discrimination/quiz/"""
    
    def setUp(self):
        super().setUp()
        # Create multiple minimal pairs for testing
        for i in range(5):
            MinimalPair.objects.create(
                phoneme_1=self.phoneme_i,
                phoneme_2=self.phoneme_I,
                word_1=f'word_a_{i}',
                word_1_ipa=f'/wɜrd{i}a/',
                word_1_meaning=f'Nghĩa A {i}',
                word_2=f'word_b_{i}',
                word_2_ipa=f'/wɜrd{i}b/',
                word_2_meaning=f'Nghĩa B {i}',
                difficulty=2
            )
    
    def test_get_quiz_success(self):
        """Test successfully getting a discrimination quiz."""
        # Start learning first
        progress = UserPhonemeProgress.objects.create(
            user=self.user,
            phoneme=self.phoneme_i,
            current_stage='learning'
        )
        
        url = self.get_url(f'pronunciation/phoneme/{self.phoneme_i.pk}/discrimination/quiz/')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        quiz_data = response.data['data']
        self.assertEqual(quiz_data['phoneme_id'], self.phoneme_i.pk)
        self.assertEqual(quiz_data['total_questions'], 10)
        self.assertEqual(len(quiz_data['questions']), 10)
        self.assertEqual(quiz_data['unlock_threshold'], 0.8)
        
        # Check question structure
        question = quiz_data['questions'][0]
        self.assertIn('question_number', question)
        self.assertIn('phoneme_a_id', question)
        self.assertIn('phoneme_b_id', question)
        self.assertIn('audio_url', question)
    
    def test_get_quiz_auto_starts_discrimination_stage(self):
        """Test that getting quiz auto-starts discrimination stage."""
        progress = UserPhonemeProgress.objects.create(
            user=self.user,
            phoneme=self.phoneme_i,
            current_stage='learning'
        )
        
        url = self.get_url(f'pronunciation/phoneme/{self.phoneme_i.pk}/discrimination/quiz/')
        response = self.client.get(url)
        
        progress.refresh_from_db()
        self.assertEqual(progress.current_stage, 'discriminating')
        self.assertIsNotNone(progress.discrimination_started_at)
    
    def test_get_quiz_forbidden_without_learning(self):
        """Test that quiz is forbidden if not in learning stage."""
        # Create progress in discovered stage
        UserPhonemeProgress.objects.create(
            user=self.user,
            phoneme=self.phoneme_i,
            current_stage='discovered'
        )
        
        url = self.get_url(f'pronunciation/phoneme/{self.phoneme_i.pk}/discrimination/quiz/')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data['success'])
        self.assertIn('học lý thuyết', response.data['error'])
    
    def test_get_quiz_insufficient_data(self):
        """Test error when not enough minim1l pairs exist."""
        # Delete most minimal pairs
        MinimalPair.objects.filter(phoneme_1=self.phoneme_i).delete()
        
        UserPhonemeProgress.objects.create(
            user=self.user,
            phoneme=self.phoneme_i,
            current_stage='learning'
        )
        
        url = self.get_url(f'pronunciation/phoneme/{self.phoneme_i.pk}/discrimination/quiz/')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.data['success'])
        self.assertIn('Chưa có đủ dữ liệu', response.data['error'])
    
    def test_get_quiz_not_found(self):
        """Test getting quiz for non-existent phoneme."""
        url = self.get_url(f'pronunciation/phoneme/{9999}/discrimination/quiz/')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_get_quiz_requires_authentication(self):
        """Test authentication required."""
        url = self.get_url(f'pronunciation/phoneme/{self.phoneme_i.pk}/discrimination/quiz/')
        
        response = self.unauth_client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DiscriminationSubmitAPITestCase(BaseAPITestCase):
    """Test POST /api/v1/pronunciation/phoneme/<id>/discrimination/submit/"""
    
    def setUp(self):
        super().setUp()
        # Create progress in discriminating stage
        self.progress = UserPhonemeProgress.objects.create(
            user=self.user,
            phoneme=self.phoneme_i,
            current_stage='discriminating'
        )
    
    def test_submit_correct_answer(self):
        """Test submitting a correct answer."""
        url = self.get_url(f'pronunciation/phoneme/{self.phoneme_i.pk}/discrimination/submit/')
        
        data = {
            'question_number': 1,
            'selected_phoneme_id': self.phoneme_i.pk,
            'correct_phoneme_id': self.phoneme_i.pk,
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        result = response.data['data']
        self.assertTrue(result['is_correct'])
        self.assertEqual(result['total_correct'], 1)
        self.assertEqual(result['total_attempts'], 1)
        self.assertEqual(result['accuracy'], 1.0)
        self.assertIn('Chính xác', result['explanation'])
    
    def test_submit_incorrect_answer(self):
        """Test submitting an incorrect answer."""
        url = self.get_url(f'pronunciation/phoneme/{self.phoneme_i.pk}/discrimination/submit/')
        
        data = {
            'question_number': 1,
            'selected_phoneme_id': self.phoneme_I.pk,  # Wrong
            'correct_phoneme_id': self.phoneme_i.pk,   # Correct
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.data['data']
        
        self.assertFalse(result['is_correct'])
        self.assertIn('Không đúng', result['explanation'])
        self.assertIn('comparison', result)
        self.assertIsNotNone(result['comparison'])
    
    def test_submit_unlocks_production_at_80_percent(self):
        """Test that 80% accuracy unlocks production."""
        url = self.get_url(f'pronunciation/phoneme/{self.phoneme_i.pk}/discrimination/submit/')
        
        # Submit 10 answers: 8 correct, 2 incorrect = 80%
        answers = [True, True, False, True, True, True, True, True, False, True]  # 8/10 = 80%
        
        for i, is_correct in enumerate(answers):
            data = {
                'question_number': i + 1,
                'selected_phoneme_id': self.phoneme_i.pk if is_correct else self.phoneme_I.pk,
                'correct_phoneme_id': self.phoneme_i.pk,
            }
            response = self.client.post(url, data, format='json')
            
            # Check accuracy is calculating correctly
            expected_accuracy = sum(answers[:i+1]) / (i + 1)
            actual_accuracy = response.data['data']['accuracy']
            self.assertAlmostEqual(actual_accuracy, expected_accuracy, places=2)
            
            # Before reaching 80%, production should NOT be unlocked
            # At exactly 80% (after 10th answer), it SHOULD be unlocked
            if expected_accuracy < 0.8:
                self.assertFalse(response.data['data']['production_unlocked'],
                                f"Production should not unlock at {expected_accuracy*100}%")
            else:
                self.assertTrue(response.data['data']['production_unlocked'],
                               f"Production should unlock at {expected_accuracy*100}%")
        
        # Final verification
        self.progress.refresh_from_db()
        self.assertEqual(self.progress.discrimination_accuracy, 0.8)
        self.assertTrue(self.progress.can_practice_production())
    
    def test_submit_cumulative_accuracy(self):
        """Test that accuracy accumulates correctly."""
        url = self.get_url(f'pronunciation/phoneme/{self.phoneme_i.pk}/discrimination/submit/')
        
        # First answer: correct
        data1 = {
            'question_number': 1,
            'selected_phoneme_id': self.phoneme_i.pk,
            'correct_phoneme_id': self.phoneme_i.pk,
        }
        response1 = self.client.post(url, data1, format='json')
        self.assertEqual(response1.data['data']['accuracy'], 1.0)  # 1/1
        
        # Second answer: incorrect
        data2 = {
            'question_number': 2,
            'selected_phoneme_id': self.phoneme_I.pk,
            'correct_phoneme_id': self.phoneme_i.pk,
        }
        response2 = self.client.post(url, data2, format='json')
        self.assertEqual(response2.data['data']['accuracy'], 0.5)  # 1/2
        
        # Third answer: correct
        data3 = {
            'question_number': 3,
            'selected_phoneme_id': self.phoneme_i.pk,
            'correct_phoneme_id': self.phoneme_i.pk,
        }
        response3 = self.client.post(url, data3, format='json')
        self.assertAlmostEqual(response3.data['data']['accuracy'], 0.667, places=2)  # 2/3
    
    def test_submit_invalid_question_number(self):
        """Test validation for question_number."""
        url = self.get_url(f'pronunciation/phoneme/{self.phoneme_i.pk}/discrimination/submit/')
        
        data = {
            'question_number': 11,  # Invalid (must be 1-10)
            'selected_phoneme_id': self.phoneme_i.pk,
            'correct_phoneme_id': self.phoneme_i.pk,
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_submit_missing_correct_answer(self):
        """Test error when correct_phoneme_id is missing."""
        url = self.get_url(f'pronunciation/phoneme/{self.phoneme_i.pk}/discrimination/submit/')
        
        data = {
            'question_number': 1,
            'selected_phoneme_id': self.phoneme_i.pk,
            # Missing correct_phoneme_id
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_submit_requires_authentication(self):
        """Test authentication required."""
        url = self.get_url(f'pronunciation/phoneme/{self.phoneme_i.pk}/discrimination/submit/')
        
        data = {
            'question_number': 1,
            'selected_phoneme_id': self.phoneme_i.pk,
            'correct_phoneme_id': self.phoneme_i.pk,
        }
        
        response = self.unauth_client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProductionReferenceAPITestCase(BaseAPITestCase):
    """Test GET /api/v1/pronunciation/phoneme/<id>/production/reference/"""
    
    def setUp(self):
        super().setUp()
        # Create progress with 80% discrimination accuracy (unlocked)
        self.progress = UserPhonemeProgress.objects.create(
            user=self.user,
            phoneme=self.phoneme_i,
            current_stage='discriminating',
            discrimination_attempts=10,
            discrimination_correct=8,
            discrimination_accuracy=0.8
        )
        
        # Create audio source for reference
        self.audio_source = AudioSource.objects.create(
            phoneme=self.phoneme_i,
            source_type='tts',
            voice_id='en-US-AriaNeural',
            language='en-US',
            audio_duration=1.5
        )
        self.phoneme_i.preferred_audio_source = self.audio_source
        self.phoneme_i.save()
    
    def test_get_reference_success(self):
        """Test successfully getting production reference."""
        url = self.get_url(f'pronunciation/phoneme/{self.phoneme_i.pk}/production/reference/')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        data = response.data['data']
        self.assertEqual(data['phoneme_id'], self.phoneme_i.pk)
        self.assertEqual(data['phoneme_symbol'], self.phoneme_i.ipa_symbol)
        self.assertEqual(data['audio_duration'], 1.5)
        self.assertIn('pronunciation_tips', data)
        self.assertIn('target_duration_min', data)
        self.assertIn('target_duration_max', data)
    
    def test_get_reference_auto_starts_production(self):
        """Test that getting reference auto-starts production stage."""
        url = self.get_url(f'pronunciation/phoneme/{self.phoneme_i.pk}/production/reference/')
        
        response = self.client.get(url)
        
        self.progress.refresh_from_db()
        self.assertEqual(self.progress.current_stage, 'producing')
        self.assertIsNotNone(self.progress.production_started_at)
    
    def test_get_reference_forbidden_under_80_percent(self):
        """Test that reference is forbidden if discrimination < 80%."""
        # Update progress to 70%
        self.progress.discrimination_accuracy = 0.7
        self.progress.save()
        
        url = self.get_url(f'pronunciation/phoneme/{self.phoneme_i.pk}/production/reference/')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data['success'])
        self.assertIn('80%', response.data['error'])
        self.assertEqual(response.data['current_accuracy'], 0.7)
        self.assertEqual(response.data['required_accuracy'], 0.8)
    
    def test_get_reference_target_duration_calculation(self):
        """Test that target duration is calculated correctly (±20%)."""
        url = self.get_url(f'pronunciation/phoneme/{self.phoneme_i.pk}/production/reference/')
        
        response = self.client.get(url)
        
        data = response.data['data']
        # Reference: 1.5 seconds
        # Min: 1.5 * 0.8 = 1.2
        # Max: 1.5 * 1.2 = 1.8
        self.assertAlmostEqual(data['target_duration_min'], 1.2, places=1)
        self.assertAlmostEqual(data['target_duration_max'], 1.8, places=1)
    
    def test_get_reference_not_found(self):
        """Test getting reference for non-existent phoneme."""
        url = self.get_url(f'pronunciation/phoneme/{9999}/production/reference/')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_get_reference_requires_authentication(self):
        """Test authentication required."""
        url = self.get_url(f'pronunciation/phoneme/{self.phoneme_i.pk}/production/reference/')
        
        response = self.unauth_client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProductionSubmitAPITestCase(BaseAPITestCase):
    """Test POST /api/v1/pronunciation/phoneme/<id>/production/submit/"""
    
    def setUp(self):
        super().setUp()
        # Create progress in producing stage
        self.progress = UserPhonemeProgress.objects.create(
            user=self.user,
            phoneme=self.phoneme_i,
            current_stage='producing',
            discrimination_accuracy=0.85  # Already unlocked
        )
        
        # Create audio source with duration
        self.audio_source = AudioSource.objects.create(
            phoneme=self.phoneme_i,
            source_type='native',
            voice_id='native-speaker',
            language='en-US',
            audio_duration=1.0
        )
        self.phoneme_i.preferred_audio_source = self.audio_source
        self.phoneme_i.save()
        
        # Create mock audio file
        self.audio_file = SimpleUploadedFile(
            "test_audio.webm",
            b"fake audio content",
            content_type="audio/webm"
        )
    
    def test_submit_production_perfect_duration(self):
        """Test submitting recording with perfect duration match."""
        url = self.get_url(f'pronunciation/phoneme/{self.phoneme_i.pk}/production/submit/')
        
        data = {
            'audio_file': self.audio_file,
            'duration': 1.0  # Exactly matches reference
        }
        
        response = self.client.post(url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        result = response.data['data']
        self.assertEqual(result['score'], 1.0)
        self.assertEqual(result['duration_diff'], 0.0)
        self.assertIn('Tốt', result['duration_feedback'])
        self.assertTrue(result['is_best_attempt'])
    
    def test_submit_production_good_duration(self):
        """Test submitting recording with good duration (within 20%)."""
        url = self.get_url(f'pronunciation/phoneme/{self.phoneme_i.pk}/production/submit/')
        
        data = {
            'audio_file': self.audio_file,
            'duration': 1.15  # 15% longer (within 20%)
        }
        
        response = self.client.post(url, data, format='multipart')
        
        result = response.data['data']
        self.assertEqual(result['score'], 1.0)
    
    def test_submit_production_fair_duration(self):
        """Test submitting recording with fair duration (within 40%)."""
        url = self.get_url(f'pronunciation/phoneme/{self.phoneme_i.pk}/production/submit/')
        
        data = {
            'audio_file': self.audio_file,
            'duration': 0.7  # 30% shorter (within 40%)
        }
        
        response = self.client.post(url, data, format='multipart')
        
        result = response.data['data']
        self.assertEqual(result['score'], 0.8)
        self.assertIn('Khá tốt', result['duration_feedback'])
    
    def test_submit_production_poor_duration(self):
        """Test submitting recording with poor duration (beyond 60%)."""
        url = self.get_url(f'pronunciation/phoneme/{self.phoneme_i.pk}/production/submit/')
        
        data = {
            'audio_file': self.audio_file,
            'duration': 0.3  # 70% shorter (beyond 60%)
        }
        
        response = self.client.post(url, data, format='multipart')
        
        result = response.data['data']
        self.assertEqual(result['score'], 0.4)
        self.assertIn('quá ngắn', result['duration_feedback'])
    
    def test_submit_production_tracks_best_score(self):
        """Test that only the best score is kept."""
        url = self.get_url(f'pronunciation/phoneme/{self.phoneme_i.pk}/production/submit/')
        
        # First attempt: 75%
        data1 = {
            'audio_file': SimpleUploadedFile("test1.webm", b"audio1", content_type="audio/webm"),
            'duration': 0.75
        }
        response1 = self.client.post(url, data1, format='multipart')
        self.assertEqual(response1.data['data']['best_score'], 0.8)
        
        # Second attempt: 60% (worse)
        data2 = {
            'audio_file': SimpleUploadedFile("test2.webm", b"audio2", content_type="audio/webm"),
            'duration': 0.5
        }
        response2 = self.client.post(url, data2, format='multipart')
        self.assertEqual(response2.data['data']['best_score'], 0.8)  # Still 0.8
        self.assertFalse(response2.data['data']['is_best_attempt'])
        
        # Third attempt: 100% (better)
        data3 = {
            'audio_file': SimpleUploadedFile("test3.webm", b"audio3", content_type="audio/webm"),
            'duration': 1.0
        }
        response3 = self.client.post(url, data3, format='multipart')
        self.assertEqual(response3.data['data']['best_score'], 1.0)  # Updated
        self.assertTrue(response3.data['data']['is_best_attempt'])
    
    def test_submit_production_auto_mastery(self):
        """Test auto-mastery when both skills >= 80%."""
        url = self.get_url(f'pronunciation/phoneme/{self.phoneme_i.pk}/production/submit/')
        
        # Discrimination already at 85%
        # Submit production at 85%
        data = {
            'audio_file': self.audio_file,
            'duration': 1.0  # Score: 1.0 (100%)
        }
        
        response = self.client.post(url, data, format='multipart')
        
        result = response.data['data']
        self.assertTrue(result['mastered'])
        
        self.progress.refresh_from_db()
        self.assertEqual(self.progress.current_stage, 'mastered')
        self.assertIsNotNone(self.progress.mastered_at)
        self.assertEqual(self.progress.mastery_level, 5)
    
    def test_submit_production_file_size_validation(self):
        """Test file size validation (max 5MB)."""
        url = self.get_url(f'pronunciation/phoneme/{self.phoneme_i.pk}/production/submit/')
        
        # Create file > 5MB
        large_file = SimpleUploadedFile(
            "large.webm",
            b"x" * (6 * 1024 * 1024),  # 6MB
            content_type="audio/webm"
        )
        
        data = {
            'audio_file': large_file,
            'duration': 1.0
        }
        
        response = self.client.post(url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_submit_production_duration_validation(self):
        """Test duration validation (0.1 - 10 seconds)."""
        url = self.get_url(f'pronunciation/phoneme/{self.phoneme_i.pk}/production/submit/')
        
        # Too short
        data1 = {
            'audio_file': self.audio_file,
            'duration': 0.05  # < 0.1
        }
        response1 = self.client.post(url, data1, format='multipart')
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Too long
        data2 = {
            'audio_file': SimpleUploadedFile("test2.webm", b"audio2", content_type="audio/webm"),
            'duration': 11.0  # > 10
        }
        response2 = self.client.post(url, data2, format='multipart')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_submit_production_requires_authentication(self):
        """Test authentication required."""
        url = self.get_url(f'pronunciation/phoneme/{self.phoneme_i.pk}/production/submit/')
        
        data = {
            'audio_file': self.audio_file,
            'duration': 1.0
        }
        
        response = self.unauth_client.post(url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OverallProgressAPITestCase(BaseAPITestCase):
    """Test GET /api/v1/pronunciation/progress/overall/"""
    
    def setUp(self):
        super().setUp()
        # Create multiple phonemes with different stages
        phonemes = []
        for i in range(10):
            phoneme = Phoneme.objects.create(
                ipa_symbol=f'test{i}',
                category=self.category,
                vietnamese_approx=f'Test {i}',
                phoneme_type='short_vowel'
            )
            phonemes.append(phoneme)
        
        # Create progress in different stages
        stages = ['discovered', 'learning', 'discriminating', 'producing', 'mastered']
        for i, phoneme in enumerate(phonemes[:5]):
            UserPhonemeProgress.objects.create(
                user=self.user,
                phoneme=phoneme,
                current_stage=stages[i],
                discrimination_accuracy=0.7 + (i * 0.05),
                production_best_score=0.6 + (i * 0.05),
                last_practiced_at=timezone.now()
            )
    
    def test_get_overall_progress_success(self):
        """Test getting overall progress successfully."""
        url = self.get_url('pronunciation/progress/overall/')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        data = response.data['data']
        self.assertIn('total_phonemes', data)
        self.assertIn('discovered_count', data)
        self.assertIn('mastered_count', data)
        self.assertIn('discovery_percentage', data)
        self.assertIn('mastery_percentage', data)
    
    def test_get_overall_progress_stage_counts(self):
        """Test that stage counts are accurate."""
        url = self.get_url('pronunciation/progress/overall/')
        
        response = self.client.get(url)
        data = response.data['data']
        
        # We created 5 progresses in different stages
        self.assertEqual(data['discovered_count'], 1)
        self.assertEqual(data['learning_count'], 1)
        self.assertEqual(data['discriminating_count'], 1)
        self.assertEqual(data['producing_count'], 1)
        self.assertEqual(data['mastered_count'], 1)
        
        # Total phonemes includes the 2 from setup + 10 from this test
        total_phonemes = data['total_phonemes']
        not_started = total_phonemes - 5  # 5 have progress
        self.assertEqual(data['not_started_count'], not_started)
    
    def test_get_overall_progress_percentages(self):
        """Test percentage calculations."""
        url = self.get_url('pronunciation/progress/overall/')
        
        response = self.client.get(url)
        data = response.data['data']
        
        total = data['total_phonemes']
        
        # Discovery percentage = (progresses / total) * 100
        expected_discovery = (5 / total) * 100
        self.assertAlmostEqual(data['discovery_percentage'], expected_discovery, places=1)
        
        # Mastery percentage = (mastered / total) * 100
        expected_mastery = (1 / total) * 100
        self.assertAlmostEqual(data['mastery_percentage'], expected_mastery, places=1)
    
    def test_get_overall_progress_recently_practiced(self):
        """Test recently practiced phonemes list."""
        url = self.get_url('pronunciation/progress/overall/')
        
        response = self.client.get(url)
        data = response.data['data']
        
        # Should have recently_practiced list (max 5)
        self.assertIn('recently_practiced', data)
        self.assertLessEqual(len(data['recently_practiced']), 5)
        
        # Each item should have phoneme info
        if len(data['recently_practiced']) > 0:
            item = data['recently_practiced'][0]
            self.assertIn('phoneme_symbol', item)
            self.assertIn('current_stage', item)
    
    def test_get_overall_progress_recommended_next(self):
        """Test recommended next phonemes."""
        url = self.get_url('pronunciation/progress/overall/')
        
        response = self.client.get(url)
        data = response.data['data']
        
        # Should have recommended_next list (phoneme IDs)
        self.assertIn('recommended_next', data)
        self.assertIsInstance(data['recommended_next'], list)
    
    def test_get_overall_progress_averages(self):
        """Test average accuracy calculations."""
        url = self.get_url('pronunciation/progress/overall/')
        
        response = self.client.get(url)
        data = response.data['data']
        
        self.assertIn('avg_discrimination_accuracy', data)
        self.assertIn('avg_production_score', data)
        
        # Averages should be between 0 and 1
        self.assertGreaterEqual(data['avg_discrimination_accuracy'], 0.0)
        self.assertLessEqual(data['avg_discrimination_accuracy'], 1.0)
        self.assertGreaterEqual(data['avg_production_score'], 0.0)
        self.assertLessEqual(data['avg_production_score'], 1.0)
    
    def test_get_overall_progress_empty_for_new_user(self):
        """Test progress for user with no practice."""
        # Create new user
        new_user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='testpass123'
        )
        
        # Authenticate as new user
        refresh = RefreshToken.for_user(new_user)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = self.get_url('pronunciation/progress/overall/')
        response = client.get(url)
        
        data = response.data['data']
        self.assertEqual(data['not_started_count'], data['total_phonemes'])
        self.assertEqual(data['discovered_count'], 0)
        self.assertEqual(data['mastered_count'], 0)
        self.assertEqual(data['discovery_percentage'], 0.0)
        self.assertEqual(data['mastery_percentage'], 0.0)
    
    def test_get_overall_progress_requires_authentication(self):
        """Test authentication required."""
        url = self.get_url('pronunciation/progress/overall/')
        
        response = self.unauth_client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PermissionTestCase(BaseAPITestCase):
    """Test that users can only access their own progress."""
    
    def setUp(self):
        super().setUp()
        # Create progress for user1
        self.progress_user1 = UserPhonemeProgress.objects.create(
            user=self.user,
            phoneme=self.phoneme_i,
            current_stage='learning'
        )
        
        # Create progress for other_user
        self.progress_other = UserPhonemeProgress.objects.create(
            user=self.other_user,
            phoneme=self.phoneme_i,
            current_stage='mastered',
            mastery_level=5
        )
    
    def test_user_cannot_see_other_user_progress(self):
        """Test that progress is isolated per user."""
        url = self.get_url('pronunciation/progress/overall/')
        
        response = self.client.get(url)
        data = response.data['data']
        
        # User should see their own progress (learning stage)
        # Not the other user's progress (mastered)
        self.assertEqual(data['learning_count'], 1)
        self.assertEqual(data['mastered_count'], 0)

