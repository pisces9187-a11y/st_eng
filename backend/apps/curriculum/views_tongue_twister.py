"""
Phase 4.4: Tongue Twister Challenge
Phase 5: Speech-to-Text Integration
Gamification feature for pronunciation practice with real STT analysis.
"""

from django.views.generic import TemplateView, View
from django.http import JsonResponse
from django.db.models import Avg, Count
from apps.users.middleware import JWTRequiredMixin
from .speech_to_text import analyze_tongue_twister_audio, generate_pronunciation_feedback
import json
import logging

logger = logging.getLogger(__name__)


class TongueTwisterChallengeView(JWTRequiredMixin, TemplateView):
    """
    Tongue twister challenge page - fun pronunciation game.
    
    Features:
    - Random tongue twister selection
    - Recording with timer
    - Speech recognition scoring
    - Leaderboard
    """
    template_name = 'curriculum/pronunciation/tongue_twister_challenge.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        from apps.curriculum.models import TongueTwister
        from apps.users.models import TongueTwisterAttempt
        
        # Get difficulty from query param (easy, medium, hard)
        difficulty = self.request.GET.get('difficulty', 'easy')
        
        # Get random tongue twister
        twister = TongueTwister.objects.filter(
            difficulty_level=difficulty,
            is_active=True
        ).order_by('?').first()
        
        if not twister:
            # Fallback to any active twister
            twister = TongueTwister.objects.filter(is_active=True).order_by('?').first()
        
        # Get user's best score for this twister
        user_best = None
        if twister:
            user_best = TongueTwisterAttempt.objects.filter(
                user=self.request.user,
                tongue_twister=twister
            ).order_by('-score').first()
        
        # Get leaderboard (top 10)
        leaderboard = []
        if twister:
            leaderboard = TongueTwisterAttempt.objects.filter(
                tongue_twister=twister
            ).select_related('user').order_by('-score', 'duration')[:10]
        
        # Get user stats
        user_stats = TongueTwisterAttempt.objects.filter(
            user=self.request.user
        ).aggregate(
            total_attempts=Count('id'),
            avg_score=Avg('score'),
            best_score=Avg('score')
        )
        
        context.update({
            'twister': twister,
            'difficulty': difficulty,
            'user_best': user_best,
            'leaderboard': leaderboard,
            'user_stats': user_stats,
        })
        
        return context


class TongueTwisterSubmitView(JWTRequiredMixin, View):
    """
    API endpoint to submit tongue twister attempt.
    Accepts audio file and calculates score.
    """
    
    def post(self, request, *args, **kwargs):
        from apps.curriculum.models import TongueTwister
        from apps.users.models import TongueTwisterAttempt
        from django.conf import settings
        
        # Get parameters
        twister_id = request.POST.get('twister_id')
        duration = float(request.POST.get('duration', 0))
        audio_file = request.FILES.get('audio')
        
        # Validate
        if not twister_id or not audio_file:
            return JsonResponse({
                'success': False,
                'error': 'Missing required parameters'
            }, status=400)
        
        try:
            twister = TongueTwister.objects.get(id=twister_id)
        except TongueTwister.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Tongue twister not found'
            }, status=404)
        
        # PHASE 5: Real Speech-to-Text Analysis
        logger.info(f"Processing tongue twister attempt - ID: {twister_id}, User: {request.user.username}")
        
        try:
            # Use STT service (falls back to mock if not configured)
            stt_result = analyze_tongue_twister_audio(audio_file, twister.text)
            
            # Extract metrics from STT
            final_score = stt_result['pronunciation_score']
            words_detected = stt_result['words_detected']
            word_count = stt_result['words_expected']
            accuracy = stt_result['accuracy']
            transcript = stt_result['transcript']
            detected_duration = stt_result['duration']
            
            # Use detected duration if available, otherwise use submitted duration
            if detected_duration > 0:
                duration = detected_duration
            
            logger.info(f"STT Result - Score: {final_score:.1f}, Accuracy: {accuracy:.1f}%, Transcript: '{transcript[:50]}...'")
            
        except Exception as e:
            logger.error(f"STT analysis failed: {str(e)}", exc_info=True)
            # Fallback to legacy mock scoring
            return self._fallback_scoring(request, twister, duration, audio_file)
        
        # Save attempt with real data
        attempt = TongueTwisterAttempt.objects.create(
            user=request.user,
            tongue_twister=twister,
            audio_file=audio_file,
            duration=duration,
            score=final_score,
            words_detected=words_detected,
            words_expected=word_count,
            accuracy=accuracy
        )
        
        # Check if this is a new personal best
        is_personal_best = not TongueTwisterAttempt.objects.filter(
            user=request.user,
            tongue_twister=twister,
            score__gt=final_score
        ).exists()
        
        # Get ranking
        better_scores = TongueTwisterAttempt.objects.filter(
            tongue_twister=twister,
            score__gt=final_score
        ).values('user').distinct().count()
        
        rank = better_scores + 1
        
        # Generate detailed feedback using STT result
        feedback = generate_pronunciation_feedback(stt_result, twister.difficulty)
        
        # Calculate speed (words per second)
        speed = words_detected / duration if duration > 0 else 0
        
        # Phase 5.2: Extract phoneme analysis if available
        phoneme_analysis = stt_result.get('phoneme_analysis', {})
        recommendations = phoneme_analysis.get('recommendations', [])
        
        return JsonResponse({
            'success': True,
            'score': int(final_score),
            'duration': round(duration, 2),
            'is_personal_best': is_personal_best,
            'rank': rank,
            'feedback': feedback,
            'words_detected': words_detected,
            'words_expected': word_count,
            'accuracy': int(accuracy),
            'transcript': transcript,
            'speed': round(speed, 2),
            'word_details': stt_result.get('words', []),  # Individual word confidences
            # Phase 5.2: Phoneme-level analysis
            'phoneme_recommendations': recommendations,
            'total_phoneme_issues': phoneme_analysis.get('total_issues', 0),
        })
    
    def _fallback_scoring(self, request, twister, duration, audio_file):
        """
        Fallback to legacy mock scoring if STT fails.
        Used as emergency backup only.
        """
        from apps.users.models import TongueTwisterAttempt
        import random
        
        logger.warning("Using fallback mock scoring")
        
        expected_words = twister.text.split()
        word_count = len(expected_words)
        expected_duration = word_count * 0.4
        
        # Calculate score components (0-100)
        
        # 1. Duration score (40% weight)
        if duration < expected_duration * 0.6:
            duration_score = max(0, 50 - (expected_duration * 0.6 - duration) * 20)
        elif duration > expected_duration * 1.8:
            duration_score = max(0, 70 - (duration - expected_duration * 1.8) * 10)
        else:
            timing_diff = abs(duration - expected_duration) / expected_duration
            duration_score = 100 - (timing_diff * 100)
        
        # 2. Complexity score (30% weight)
        complexity_score = 100 - (twister.difficulty * 10)
        
        # 3. Consistency score (30% weight)
        consistency_score = random.randint(70, 95)
        
        # Calculate final score
        final_score = (
            duration_score * 0.4 + 
            complexity_score * 0.3 + 
            consistency_score * 0.3
        )
        
        final_score = max(0, min(100, final_score + random.randint(-5, 5)))
        
        # Mock word detection
        if duration < expected_duration * 0.7:
            words_detected = max(1, int(word_count * 0.6))
        elif duration > expected_duration * 1.5:
            words_detected = max(1, int(word_count * 0.8))
        else:
            words_detected = word_count
        
        accuracy = (words_detected / word_count) * 100
        
        # Save attempt
        attempt = TongueTwisterAttempt.objects.create(
            user=request.user,
            tongue_twister=twister,
            audio_file=audio_file,
            duration=duration,
            score=final_score,
            words_detected=words_detected,
            words_expected=word_count,
            accuracy=accuracy
        )
        
        is_personal_best = not TongueTwisterAttempt.objects.filter(
            user=request.user,
            tongue_twister=twister,
            score__gt=final_score
        ).exists()
        
        better_scores = TongueTwisterAttempt.objects.filter(
            tongue_twister=twister,
            score__gt=final_score
        ).values('user').distinct().count()
        
        rank = better_scores + 1
        
        feedback = self._generate_detailed_feedback(
            final_score, duration, expected_duration, 
            words_detected, word_count
        )
        
        speed = words_detected / duration if duration > 0 else 0
        
        return JsonResponse({
            'success': True,
            'score': int(final_score),
            'duration': round(duration, 2),
            'is_personal_best': is_personal_best,
            'rank': rank,
            'feedback': feedback,
            'words_detected': words_detected,
            'words_expected': word_count,
            'accuracy': int(accuracy),
            'transcript': '[Mock mode - no transcript]',
            'speed': round(speed, 2),
            'word_details': [],
        })
    
    def _generate_detailed_feedback(self, score, duration, expected_duration, words_detected, words_expected):
        """Generate detailed encouraging feedback based on performance"""
        
        # Speed assessment
        if duration < expected_duration * 0.7:
            speed_feedback = "Bạn đọc hơi nhanh, thử chậm lại để rõ ràng hơn."
        elif duration > expected_duration * 1.5:
            speed_feedback = "Bạn đọc hơi chậm, có thể tăng tốc độ tự nhiên hơn."
        else:
            speed_feedback = "Tốc độ đọc của bạn rất tốt!"
        
        # Accuracy assessment
        accuracy = (words_detected / words_expected) * 100
        if accuracy >= 90:
            accuracy_feedback = "Phát âm rõ ràng, xuất sắc!"
        elif accuracy >= 70:
            accuracy_feedback = "Phát âm tốt, một số từ cần cải thiện."
        else:
            accuracy_feedback = "Cần luyện tập thêm để phát âm rõ hơn."
        
        # Overall feedback based on score
        if score >= 90:
            overall = f"🎉 Xuất sắc! {speed_feedback} {accuracy_feedback}"
        elif score >= 75:
            overall = f"👍 Tốt lắm! {speed_feedback} {accuracy_feedback}"
        elif score >= 60:
            overall = f"💪 Khá tốt! {speed_feedback} {accuracy_feedback}"
        else:
            overall = f"🔄 Cố gắng thêm! {speed_feedback} {accuracy_feedback}"
        
        return overall
    
    def _generate_feedback(self, score, duration, expected_duration):
        """Legacy method - kept for backward compatibility"""
        return self._generate_detailed_feedback(
            score, duration, expected_duration, 
            int(score / 10), 10  # Mock values
        )


class TongueTwisterLeaderboardView(JWTRequiredMixin, TemplateView):
    """
    Global leaderboard for all tongue twisters.
    """
    template_name = 'curriculum/pronunciation/tongue_twister_leaderboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        from apps.curriculum.models import TongueTwister
        from apps.users.models import TongueTwisterAttempt
        
        # Get all twisters with stats
        twisters = TongueTwister.objects.filter(is_active=True).annotate(
            attempt_count=Count('attempts'),
            avg_score=Avg('attempts__score')
        )
        
        # Global top performers
        top_performers = TongueTwisterAttempt.objects.values(
            'user__username', 'user__first_name', 'user__last_name'
        ).annotate(
            total_attempts=Count('id'),
            avg_score=Avg('score'),
            best_score=Avg('score')
        ).order_by('-avg_score')[:20]
        
        # Recent attempts
        recent_attempts = TongueTwisterAttempt.objects.select_related(
            'user', 'tongue_twister'
        ).order_by('-created_at')[:10]
        
        context.update({
            'twisters': twisters,
            'top_performers': top_performers,
            'recent_attempts': recent_attempts,
        })
        
        return context
