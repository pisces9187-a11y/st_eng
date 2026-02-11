"""
Pronunciation Learning Flow API Views.

7 core endpoints for the 4-stage learning journey:
1. POST /phoneme/<id>/discover/ - Mark phoneme as discovered
2. POST /phoneme/<id>/start-learning/ - Start learning stage
3. GET /phoneme/<id>/discrimination/quiz/ - Get discrimination quiz
4. POST /phoneme/<id>/discrimination/submit/ - Submit discrimination answer
5. GET /phoneme/<id>/production/reference/ - Get production reference audio
6. POST /phoneme/<id>/production/submit/ - Submit production recording
7. GET /progress/ - Get overall progress

Design principles:
- RESTful API design
- JWT authentication required
- Proper error handling with meaningful messages
- Vietnamese feedback for better UX
"""

import random
import logging
from datetime import timedelta

from django.utils import timezone
from django.db.models import Count, Q, Avg
from django.shortcuts import get_object_or_404
from django.http import Http404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser

from apps.curriculum.models import Phoneme, MinimalPair, AudioSource
from apps.users.models import User, UserPhonemeProgress
from apps.curriculum.serializers import (
    UserPhonemeProgressSerializer,
    DiscriminationQuizSerializer,
    DiscriminationSubmitSerializer,
    DiscriminationResultSerializer,
    ProductionReferenceSerializer,
    ProductionSubmitSerializer,
    ProductionResultSerializer,
    OverallProgressSerializer,
)

logger = logging.getLogger(__name__)


class PhonemeDiscoverAPIView(APIView):
    """
    POST /api/v1/pronunciation/phoneme/<pk>/discover/
    
    Mark phoneme as discovered when user first interacts with it.
    Creates UserPhonemeProgress if doesn't exist.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        """Mark phoneme as discovered."""
        try:
            phoneme = get_object_or_404(Phoneme, pk=pk)
            
            # Get or create progress
            progress, created = UserPhonemeProgress.objects.get_or_create(
                user=request.user,
                phoneme=phoneme
            )
            
            # Mark as discovered
            progress.mark_as_discovered()
            
            serializer = UserPhonemeProgressSerializer(progress)
            
            return Response({
                'success': True,
                'message': f'Đã khám phá âm /{phoneme.ipa_symbol}/',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Http404:
            raise  # Let 404s pass through
        except Exception as e:
            logger.error(f"Error discovering phoneme {pk}: {str(e)}")
            return Response({
                'success': False,
                'error': 'Có lỗi xảy ra khi khám phá âm này.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PhonemeStartLearningAPIView(APIView):
    """
    POST /api/v1/pronunciation/phoneme/<pk>/start-learning/
    
    Mark learning stage started when user opens detail page.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        """Start learning stage."""
        try:
            phoneme = get_object_or_404(Phoneme, pk=pk)
            
            # Get or create progress
            progress, created = UserPhonemeProgress.objects.get_or_create(
                user=request.user,
                phoneme=phoneme
            )
            
            # Start learning
            progress.start_learning()
            
            serializer = UserPhonemeProgressSerializer(progress)
            
            return Response({
                'success': True,
                'message': f'Bắt đầu học âm /{phoneme.ipa_symbol}/',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Http404:
            raise  # Let 404s pass through
        except Exception as e:
            logger.error(f"Error starting learning for phoneme {pk}: {str(e)}")
            return Response({
                'success': False,
                'error': 'Có lỗi xảy ra khi bắt đầu học.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DiscriminationQuizAPIView(APIView):
    """
    GET /api/v1/pronunciation/phoneme/<pk>/discrimination/quiz/
    
    Generate discrimination quiz with 10 questions.
    Uses minimal pairs to test user's ability to distinguish sounds.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        """Generate discrimination quiz."""
        try:
            phoneme = get_object_or_404(Phoneme, pk=pk)
            
            # Get or create progress
            progress, created = UserPhonemeProgress.objects.get_or_create(
                user=request.user,
                phoneme=phoneme
            )
            
            # Check if can practice discrimination
            if not progress.can_practice_discrimination():
                return Response({
                    'success': False,
                    'error': 'Bạn cần hoàn thành giai đoạn học lý thuyết trước.'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Get minimal pairs for this phoneme
            minimal_pairs = MinimalPair.objects.filter(
                Q(phoneme_1=phoneme) | Q(phoneme_2=phoneme)
            ).select_related('phoneme_1', 'phoneme_2')
            
            if minimal_pairs.count() < 5:
                return Response({
                    'success': False,
                    'error': 'Chưa có đủ dữ liệu bài tập cho âm này.'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Generate 10 questions (random selection with replacement)
            questions = []
            pair_list = list(minimal_pairs)
            
            for i in range(10):
                pair = random.choice(pair_list)
                
                # Randomly choose which phoneme to play
                play_phoneme_1 = random.choice([True, False])
                
                if play_phoneme_1:
                    correct_phoneme = pair.phoneme_1
                    audio_source = pair.phoneme_1.preferred_audio_source
                else:
                    correct_phoneme = pair.phoneme_2
                    audio_source = pair.phoneme_2.preferred_audio_source
                
                # Get audio URL
                audio_url = None
                if audio_source and audio_source.audio_file:
                    audio_url = audio_source.audio_file.url
                
                questions.append({
                    'question_number': i + 1,
                    'phoneme_a_id': pair.phoneme_1.id,
                    'phoneme_a_symbol': pair.phoneme_1.ipa_symbol,
                    'phoneme_a_example': pair.word_1 or '',
                    'phoneme_b_id': pair.phoneme_2.id,
                    'phoneme_b_symbol': pair.phoneme_2.ipa_symbol,
                    'phoneme_b_example': pair.word_2 or '',
                    'audio_url': audio_url or '',
                    'correct_phoneme_id': correct_phoneme.id,
                })
            
            # Start discrimination stage
            if progress.current_stage == 'learning':
                progress.start_discrimination()
            
            quiz_data = {
                'phoneme_id': phoneme.id,
                'phoneme_symbol': phoneme.ipa_symbol,
                'total_questions': 10,
                'questions': questions,
                'current_accuracy': progress.discrimination_accuracy,
                'unlock_threshold': 0.8,
            }
            
            serializer = DiscriminationQuizSerializer(quiz_data)
            
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Http404:
            raise  # Let 404s pass through
        except Exception as e:
            logger.error(f"Error generating quiz for phoneme {pk}: {str(e)}")
            return Response({
                'success': False,
                'error': 'Có lỗi xảy ra khi tạo bài quiz.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DiscriminationSubmitAPIView(APIView):
    """
    POST /api/v1/pronunciation/phoneme/<pk>/discrimination/submit/
    
    Submit answer for discrimination quiz.
    Tracks progress and unlocks production when accuracy >= 80%.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        """Submit discrimination answer."""
        try:
            phoneme = get_object_or_404(Phoneme, pk=pk)
            
            # Validate input
            submit_serializer = DiscriminationSubmitSerializer(data=request.data)
            if not submit_serializer.is_valid():
                return Response({
                    'success': False,
                    'errors': submit_serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get progress
            progress = get_object_or_404(
                UserPhonemeProgress,
                user=request.user,
                phoneme=phoneme
            )
            
            # Get selected and correct phonemes from request
            selected_id = submit_serializer.validated_data['selected_phoneme_id']
            correct_id = request.data.get('correct_phoneme_id')
            
            if not correct_id:
                return Response({
                    'success': False,
                    'error': 'Thiếu thông tin câu trả lời đúng.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if correct
            is_correct = (selected_id == int(correct_id))
            
            # Update progress
            progress.update_discrimination_progress(
                correct=1 if is_correct else 0,
                total=1
            )
            
            # Get phoneme objects for response
            selected_phoneme = get_object_or_404(Phoneme, pk=selected_id)
            correct_phoneme = get_object_or_404(Phoneme, pk=correct_id)
            
            # Build comparison data
            comparison = {}
            if not is_correct:
                comparison = {
                    'correct_tongue_position': correct_phoneme.tongue_position_vi or correct_phoneme.tongue_position,
                    'selected_tongue_position': selected_phoneme.tongue_position_vi or selected_phoneme.tongue_position,
                    'correct_mouth_position': correct_phoneme.mouth_position_vi or correct_phoneme.mouth_position,
                    'selected_mouth_position': selected_phoneme.mouth_position_vi or selected_phoneme.mouth_position,
                }
            
            # Build explanation
            if is_correct:
                explanation = f"Chính xác! Đây là âm /{correct_phoneme.ipa_symbol}/."
            else:
                explanation = f"Không đúng. Âm vừa nghe là /{correct_phoneme.ipa_symbol}/, không phải /{selected_phoneme.ipa_symbol}/."
            
            # Check if production unlocked
            production_unlocked = progress.can_practice_production()
            
            result_data = {
                'is_correct': is_correct,
                'correct_phoneme_id': correct_id,
                'correct_phoneme_symbol': correct_phoneme.ipa_symbol,
                'selected_phoneme_id': selected_id,
                'selected_phoneme_symbol': selected_phoneme.ipa_symbol,
                'explanation': explanation,
                'comparison': comparison,
                'total_correct': progress.discrimination_correct,
                'total_attempts': progress.discrimination_attempts,
                'accuracy': progress.discrimination_accuracy,
                'production_unlocked': production_unlocked,
            }
            
            result_serializer = DiscriminationResultSerializer(result_data)
            
            return Response({
                'success': True,
                'data': result_serializer.data
            }, status=status.HTTP_200_OK)
            
        except Http404:
            raise  # Let 404s pass through
        except Exception as e:
            logger.error(f"Error submitting discrimination for phoneme {pk}: {str(e)}")
            return Response({
                'success': False,
                'error': 'Có lỗi xảy ra khi nộp câu trả lời.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductionReferenceAPIView(APIView):
    """
    GET /api/v1/pronunciation/phoneme/<pk>/production/reference/
    
    Get reference audio and guidelines for production practice.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        """Get production reference data."""
        try:
            phoneme = get_object_or_404(Phoneme, pk=pk)
            
            # Get progress
            progress = get_object_or_404(
                UserPhonemeProgress,
                user=request.user,
                phoneme=phoneme
            )
            
            # Check if can practice production
            if not progress.can_practice_production():
                return Response({
                    'success': False,
                    'error': f'Bạn cần đạt 80% độ chính xác phân biệt âm trước. Hiện tại: {int(progress.discrimination_accuracy * 100)}%',
                    'current_accuracy': progress.discrimination_accuracy,
                    'required_accuracy': 0.8,
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Get reference audio
            audio_source = phoneme.preferred_audio_source
            audio_url = None
            audio_duration = 0
            
            if audio_source:
                audio_duration = audio_source.audio_duration
                if audio_source.audio_file:
                    audio_url = audio_source.audio_file.url
            
            # Get mouth diagram
            mouth_diagram_url = None
            if phoneme.mouth_diagram:
                mouth_diagram_url = phoneme.mouth_diagram.url
            
            # Estimate target duration range (±20% of reference)
            target_duration_min = audio_duration * 0.8 if audio_duration else 0.5
            target_duration_max = audio_duration * 1.2 if audio_duration else 1.5
            
            reference_data = {
                'phoneme_id': phoneme.id,
                'phoneme_symbol': phoneme.ipa_symbol,
                'reference_audio_url': audio_url or '',
                'audio_duration': audio_duration,
                'mouth_diagram_url': mouth_diagram_url or '',
                'video_tutorial_url': '',  # TODO: Add video field to Phoneme model
                'pronunciation_tips': phoneme.pronunciation_tips_vi or phoneme.pronunciation_tips or '',
                'target_duration_min': target_duration_min,
                'target_duration_max': target_duration_max,
            }
            
            serializer = ProductionReferenceSerializer(reference_data)
            
            # Start production stage if not already
            if progress.current_stage == 'discriminating':
                progress.start_production()
            
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Http404:
            raise  # Let 404s pass through
        except Exception as e:
            logger.error(f"Error getting production reference for phoneme {pk}: {str(e)}")
            return Response({
                'success': False,
                'error': 'Có lỗi xảy ra khi tải dữ liệu tham khảo.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductionSubmitAPIView(APIView):
    """
    POST /api/v1/pronunciation/phoneme/<pk>/production/submit/
    
    Submit user's pronunciation recording for evaluation.
    Simple duration-based scoring (Phase 1 - no AI).
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request, pk):
        """Submit production recording."""
        try:
            phoneme = get_object_or_404(Phoneme, pk=pk)
            
            # Validate input
            submit_serializer = ProductionSubmitSerializer(data=request.data)
            if not submit_serializer.is_valid():
                return Response({
                    'success': False,
                    'errors': submit_serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get progress
            progress = get_object_or_404(
                UserPhonemeProgress,
                user=request.user,
                phoneme=phoneme
            )
            
            # Get reference duration
            audio_source = phoneme.preferred_audio_source
            reference_duration = audio_source.audio_duration if audio_source else 1.0
            
            # Get user recording duration
            user_duration = submit_serializer.validated_data['duration']
            
            # Calculate duration difference
            duration_diff = user_duration - reference_duration
            duration_diff_percent = abs(duration_diff) / reference_duration if reference_duration > 0 else 0
            
            # Simple scoring based on duration similarity
            # Within 20%: 1.0 score
            # Within 40%: 0.8 score
            # Within 60%: 0.6 score
            # Beyond 60%: 0.4 score
            if duration_diff_percent <= 0.2:
                score = 1.0
                duration_feedback = "Tốt! Thời lượng chính xác."
            elif duration_diff_percent <= 0.4:
                score = 0.8
                duration_feedback = "Khá tốt! Gần đúng thời lượng."
            elif duration_diff_percent <= 0.6:
                score = 0.6
                if duration_diff > 0:
                    duration_feedback = "Audio của bạn hơi dài. Hãy ngắn lại một chút."
                else:
                    duration_feedback = "Audio của bạn hơi ngắn. Hãy kéo dài hơn."
            else:
                score = 0.4
                if duration_diff > 0:
                    duration_feedback = "Audio của bạn quá dài. Hãy phát âm ngắn hơn."
                else:
                    duration_feedback = "Audio của bạn quá ngắn. Hãy kéo dài âm."
            
            # Update progress
            old_best = progress.production_best_score
            progress.update_production_progress(score)
            
            # Check if this is best attempt
            is_best_attempt = score > old_best
            
            # Build overall feedback
            if score >= 0.8:
                overall_feedback = f"Xuất sắc! Bạn phát âm âm /{phoneme.ipa_symbol}/ rất tốt."
            elif score >= 0.6:
                overall_feedback = f"Tốt! Bạn đang tiến bộ với âm /{phoneme.ipa_symbol}/."
            else:
                overall_feedback = f"Tiếp tục luyện tập! Hãy nghe lại audio mẫu và so sánh."
            
            # Check if mastered
            mastered = progress.current_stage == 'mastered'
            
            result_data = {
                'score': score,
                'duration_diff': duration_diff,
                'duration_feedback': duration_feedback,
                'overall_feedback': overall_feedback,
                'is_best_attempt': is_best_attempt,
                'attempts_count': progress.production_attempts,
                'best_score': progress.production_best_score,
                'mastered': mastered,
            }
            
            result_serializer = ProductionResultSerializer(result_data)
            
            return Response({
                'success': True,
                'message': 'Đã lưu lần thử của bạn!',
                'data': result_serializer.data
            }, status=status.HTTP_200_OK)
            
        except Http404:
            raise  # Let 404s pass through
        except Exception as e:
            logger.error(f"Error submitting production for phoneme {pk}: {str(e)}")
            return Response({
                'success': False,
                'error': 'Có lỗi xảy ra khi xử lý bản ghi âm.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OverallProgressAPIView(APIView):
    """
    GET /api/v1/pronunciation/progress/
    
    Get user's overall pronunciation learning progress.
    Shows stats across all phonemes.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get overall progress."""
        try:
            user = request.user
            
            # Get all phonemes count
            total_phonemes = Phoneme.objects.filter(is_active=True).count()
            
            # Get user's progress
            all_progress = UserPhonemeProgress.objects.filter(user=user)
            
            # Count by stage
            stage_counts = all_progress.values('current_stage').annotate(
                count=Count('id')
            )
            
            stage_dict = {item['current_stage']: item['count'] for item in stage_counts}
            
            not_started_count = total_phonemes - all_progress.count()
            discovered_count = stage_dict.get('discovered', 0)
            learning_count = stage_dict.get('learning', 0)
            discriminating_count = stage_dict.get('discriminating', 0)
            producing_count = stage_dict.get('producing', 0)
            mastered_count = stage_dict.get('mastered', 0)
            
            # Calculate percentages
            discovery_percentage = (all_progress.count() / total_phonemes * 100) if total_phonemes > 0 else 0
            mastery_percentage = (mastered_count / total_phonemes * 100) if total_phonemes > 0 else 0
            
            # Recently practiced (last 7 days)
            seven_days_ago = timezone.now() - timedelta(days=7)
            recently_practiced = all_progress.filter(
                last_practiced_at__gte=seven_days_ago
            ).order_by('-last_practiced_at')[:5]
            
            # Recommended next phonemes (discovered but not learning)
            recommended_next = list(all_progress.filter(
                current_stage='discovered'
            ).values_list('phoneme_id', flat=True)[:3])
            
            # Calculate averages
            avg_discrimination_accuracy = all_progress.filter(
                discrimination_attempts__gt=0
            ).aggregate(avg=Avg('discrimination_accuracy'))['avg'] or 0.0
            
            avg_production_score = all_progress.filter(
                production_attempts__gt=0
            ).aggregate(avg=Avg('production_best_score'))['avg'] or 0.0
            
            # Estimate practice time (rough: 5 min per phoneme practiced)
            total_practice_time = all_progress.filter(
                last_practiced_at__isnull=False
            ).count() * 5
            
            # Current streak (TODO: implement proper streak tracking)
            current_streak = 0
            
            # Pass queryset directly - serializer will handle it
            progress_data = {
                'total_phonemes': total_phonemes,
                'not_started_count': not_started_count,
                'discovered_count': discovered_count,
                'learning_count': learning_count,
                'discriminating_count': discriminating_count,
                'producing_count': producing_count,
                'mastered_count': mastered_count,
                'discovery_percentage': round(discovery_percentage, 1),
                'mastery_percentage': round(mastery_percentage, 1),
                'recently_practiced': list(recently_practiced),  # Convert to list for serializer
                'recommended_next': recommended_next,
                'total_practice_time': total_practice_time,
                'current_streak': current_streak,
                'avg_discrimination_accuracy': round(avg_discrimination_accuracy, 2),
                'avg_production_score': round(avg_production_score, 2),
            }
            
            serializer = OverallProgressSerializer(progress_data)
            
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Http404:
            raise  # Let 404s pass through
        except Exception as e:
            logger.error(f"Error getting overall progress: {str(e)}")
            return Response({
                'success': False,
                'error': 'Có lỗi xảy ra khi tải tiến độ.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
