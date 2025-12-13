"""
Pronunciation Learning API Views.

Endpoints:
- GET /api/v1/pronunciation/lessons/ - List pronunciation lessons
- GET /api/v1/pronunciation/lessons/<slug>/ - Get lesson detail
- GET /api/v1/pronunciation/progress/ - Get user's overall progress
- POST /api/v1/pronunciation/progress/screen/ - Save screen completion
- POST /api/v1/pronunciation/progress/complete/ - Complete lesson
- GET /api/v1/pronunciation/phonemes/ - Get all phonemes with user progress
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count, Avg, Q

from .models import (
    PronunciationLesson, 
    Phoneme, 
    PhonemeCategory,
    PhonemeWord,
    MinimalPair
)
from apps.users.models import (
    UserPronunciationLessonProgress,
    UserPhonemeProgress,
    UserPronunciationStreak
)


class PronunciationLessonListView(APIView):
    """
    List all pronunciation lessons with user progress.
    
    GET /api/v1/pronunciation/lessons/
    Query params:
    - part: Filter by part number (1, 2, 3...)
    - status: Filter by lesson status (published, draft)
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        lessons = PronunciationLesson.objects.filter(status='published')
        
        # Filter by part
        part = request.query_params.get('part')
        if part:
            lessons = lessons.filter(part_number=part)
        
        # Get user progress if authenticated
        user_progress = {}
        if request.user.is_authenticated:
            progress_qs = UserPronunciationLessonProgress.objects.filter(
                user=request.user,
                pronunciation_lesson__in=lessons
            )
            for p in progress_qs:
                user_progress[p.pronunciation_lesson_id] = {
                    'status': p.status,
                    'current_screen': p.current_screen,
                    'xp_earned': p.xp_earned,
                    'completed_at': p.completed_at.isoformat() if p.completed_at else None,
                }
        
        result = []
        for lesson in lessons:
            phonemes_list = list(lesson.phonemes.values('id', 'ipa_symbol', 'vietnamese_approx'))
            
            result.append({
                'id': lesson.id,
                'slug': lesson.slug,
                'title': lesson.title,
                'title_vi': lesson.title_vi,
                'description': lesson.description,
                'description_vi': lesson.description_vi,
                'lesson_type': lesson.lesson_type,
                'part_number': lesson.part_number,
                'unit_number': lesson.unit_number,
                'estimated_minutes': lesson.estimated_minutes,
                'xp_reward': lesson.xp_reward,
                'difficulty': lesson.difficulty,
                'phonemes': phonemes_list,
                'objectives': lesson.objectives,
                'user_progress': user_progress.get(lesson.id, None),
            })
        
        return Response({
            'success': True,
            'lessons': result,
            'count': len(result)
        })


class PronunciationLessonDetailView(APIView):
    """
    Get detailed lesson content for learning.
    
    GET /api/v1/pronunciation/lessons/<slug>/
    """
    permission_classes = [AllowAny]
    
    def get(self, request, slug):
        lesson = get_object_or_404(PronunciationLesson, slug=slug, status='published')
        
        # Get phonemes with example words
        phonemes_data = []
        for phoneme in lesson.phonemes.all():
            words = list(phoneme.example_words.values(
                'word', 'ipa_transcription', 'meaning_vi', 
                'phoneme_position', 'highlight_start', 'highlight_end'
            )[:6])  # Get up to 6 example words
            
            phonemes_data.append({
                'id': phoneme.id,
                'ipa_symbol': phoneme.ipa_symbol,
                'vietnamese_approx': phoneme.vietnamese_approx,
                'phoneme_type': phoneme.phoneme_type,
                'voicing': phoneme.voicing,
                'mouth_position': phoneme.mouth_position,
                'mouth_position_vi': phoneme.mouth_position_vi,
                'tongue_position_vi': phoneme.tongue_position_vi,
                'pronunciation_tips': phoneme.pronunciation_tips,
                'pronunciation_tips_vi': phoneme.pronunciation_tips_vi,
                'common_mistakes_vi': phoneme.common_mistakes_vi,
                'example_words': words,
            })
        
        # Get minimal pairs for this lesson's phonemes
        phoneme_ids = [p['id'] for p in phonemes_data]
        minimal_pairs = MinimalPair.objects.filter(
            Q(phoneme_1_id__in=phoneme_ids) | Q(phoneme_2_id__in=phoneme_ids)
        ).values(
            'id', 'word_1', 'word_1_ipa', 'word_1_meaning',
            'word_2', 'word_2_ipa', 'word_2_meaning',
            'difference_note_vi', 'difficulty',
            'phoneme_1__ipa_symbol', 'phoneme_2__ipa_symbol'
        )[:10]
        
        # Get tongue twisters
        tongue_twisters = list(lesson.tongue_twisters.values(
            'id', 'text', 'ipa_transcription', 'meaning_vi', 'difficulty'
        )[:3])
        
        # Get user progress if authenticated
        user_progress = None
        if request.user.is_authenticated:
            progress, created = UserPronunciationLessonProgress.objects.get_or_create(
                user=request.user,
                pronunciation_lesson=lesson,
                defaults={'status': 'in_progress'}
            )
            if created or progress.status == 'not_started':
                progress.status = 'in_progress'
                progress.save()
            
            user_progress = {
                'id': progress.id,
                'status': progress.status,
                'current_screen': progress.current_screen,
                'completed_screens': progress.completed_screens,
                'screen_data': progress.screen_data,
                'challenge_correct': progress.challenge_correct,
                'challenge_total': progress.challenge_total,
                'xp_earned': progress.xp_earned,
                'time_spent_seconds': progress.time_spent_seconds,
                'attempts': progress.attempts,
            }
        
        return Response({
            'success': True,
            'lesson': {
                'id': lesson.id,
                'slug': lesson.slug,
                'title': lesson.title,
                'title_vi': lesson.title_vi,
                'description': lesson.description,
                'description_vi': lesson.description_vi,
                'lesson_type': lesson.lesson_type,
                'lesson_content': lesson.lesson_content,
                'objectives': lesson.objectives,
                'part_number': lesson.part_number,
                'unit_number': lesson.unit_number,
                'estimated_minutes': lesson.estimated_minutes,
                'xp_reward': lesson.xp_reward,
                'difficulty': lesson.difficulty,
                'phonemes': phonemes_data,
                'minimal_pairs': list(minimal_pairs),
                'tongue_twisters': tongue_twisters,
            },
            'user_progress': user_progress,
        })


class SaveScreenProgressView(APIView):
    """
    Save progress for a specific screen in a lesson.
    
    POST /api/v1/pronunciation/progress/screen/
    {
        "lesson_id": 1,
        "screen_number": 2,
        "data": {
            "words_practiced": ["pen", "soap"],
            "recordings": [...],
            "time_spent": 120
        }
    }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        lesson_id = request.data.get('lesson_id')
        screen_number = request.data.get('screen_number')
        screen_data = request.data.get('data', {})
        
        if not lesson_id or not screen_number:
            return Response({
                'success': False,
                'error': 'Missing lesson_id or screen_number'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        lesson = get_object_or_404(PronunciationLesson, id=lesson_id)
        
        progress, created = UserPronunciationLessonProgress.objects.get_or_create(
            user=request.user,
            pronunciation_lesson=lesson,
            defaults={'status': 'in_progress'}
        )
        
        # Update screen data
        progress.complete_screen(screen_number, screen_data)
        
        # Update time spent
        time_spent = screen_data.get('time_spent', 0)
        if time_spent:
            progress.time_spent_seconds += time_spent
            progress.save()
        
        return Response({
            'success': True,
            'message': f'Screen {screen_number} progress saved',
            'progress': {
                'current_screen': progress.current_screen,
                'completed_screens': progress.completed_screens,
                'time_spent_seconds': progress.time_spent_seconds,
            }
        })


class SaveChallengeResultView(APIView):
    """
    Save quiz/challenge results from Screen 4.
    
    POST /api/v1/pronunciation/progress/challenge/
    {
        "lesson_id": 1,
        "correct": 4,
        "total": 5,
        "answers": [
            {"question_id": 1, "correct": true, "user_answer": "pea"},
            ...
        ]
    }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        lesson_id = request.data.get('lesson_id')
        correct = request.data.get('correct', 0)
        total = request.data.get('total', 0)
        answers = request.data.get('answers', [])
        
        if not lesson_id:
            return Response({
                'success': False,
                'error': 'Missing lesson_id'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        lesson = get_object_or_404(PronunciationLesson, id=lesson_id)
        
        progress = get_object_or_404(
            UserPronunciationLessonProgress,
            user=request.user,
            pronunciation_lesson=lesson
        )
        
        # Update challenge results
        progress.challenge_correct = correct
        progress.challenge_total = total
        progress.screen_data['challenge_answers'] = answers
        
        # Calculate accuracy
        if total > 0:
            progress.listening_accuracy = (correct / total) * 100
        
        progress.save()
        
        # Update phoneme progress
        for phoneme in lesson.phonemes.all():
            phoneme_progress, _ = UserPhonemeProgress.objects.get_or_create(
                user=request.user,
                phoneme=phoneme
            )
            phoneme_progress.update_progress(correct, total)
        
        return Response({
            'success': True,
            'message': 'Challenge results saved',
            'accuracy': progress.listening_accuracy,
            'challenge_correct': correct,
            'challenge_total': total,
        })


class CompleteLessonView(APIView):
    """
    Mark a lesson as completed and award XP.
    
    POST /api/v1/pronunciation/progress/complete/
    {
        "lesson_id": 1,
        "time_spent": 600  // total seconds
    }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        lesson_id = request.data.get('lesson_id')
        time_spent = request.data.get('time_spent', 0)
        
        if not lesson_id:
            return Response({
                'success': False,
                'error': 'Missing lesson_id'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        lesson = get_object_or_404(PronunciationLesson, id=lesson_id)
        
        progress = get_object_or_404(
            UserPronunciationLessonProgress,
            user=request.user,
            pronunciation_lesson=lesson
        )
        
        # Update final time
        progress.time_spent_seconds = time_spent
        
        # Complete lesson and get XP
        xp_earned = progress.complete_lesson()
        
        # Update pronunciation streak
        streak, _ = UserPronunciationStreak.objects.get_or_create(user=request.user)
        minutes = time_spent // 60
        streak.update_streak(minutes)
        streak.total_lessons_completed += 1
        streak.this_week_lessons += 1
        streak.save()
        
        return Response({
            'success': True,
            'message': 'Lesson completed!',
            'xp_earned': xp_earned,
            'total_xp': request.user.xp_points,
            'streak': {
                'current': streak.current_streak,
                'longest': streak.longest_streak,
            }
        })


class UserPronunciationProgressView(APIView):
    """
    Get user's overall pronunciation learning progress.
    
    GET /api/v1/pronunciation/progress/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get lesson progress stats
        lesson_stats = UserPronunciationLessonProgress.objects.filter(
            user=user
        ).aggregate(
            total=Count('id'),
            completed=Count('id', filter=Q(status='completed')),
            total_xp=Avg('xp_earned'),
            avg_accuracy=Avg('listening_accuracy'),
        )
        
        # Get phoneme mastery stats
        phoneme_stats = UserPhonemeProgress.objects.filter(
            user=user
        ).aggregate(
            total_practiced=Count('id'),
            mastered=Count('id', filter=Q(mastery_level__gte=4)),
            avg_accuracy=Avg('accuracy_rate'),
        )
        
        # Get streak info
        streak = UserPronunciationStreak.objects.filter(user=user).first()
        streak_data = None
        if streak:
            streak_data = {
                'current': streak.current_streak,
                'longest': streak.longest_streak,
                'total_lessons': streak.total_lessons_completed,
                'total_minutes': streak.total_practice_time_minutes,
                'this_week_lessons': streak.this_week_lessons,
                'this_week_minutes': streak.this_week_minutes,
            }
        
        # Get recent lessons
        recent_lessons = UserPronunciationLessonProgress.objects.filter(
            user=user
        ).select_related('pronunciation_lesson').order_by('-last_accessed_at')[:5]
        
        recent_data = []
        for p in recent_lessons:
            recent_data.append({
                'lesson_id': p.pronunciation_lesson.id,
                'lesson_slug': p.pronunciation_lesson.slug,
                'lesson_title': p.pronunciation_lesson.title_vi,
                'status': p.status,
                'current_screen': p.current_screen,
                'xp_earned': p.xp_earned,
                'last_accessed': p.last_accessed_at.isoformat(),
            })
        
        return Response({
            'success': True,
            'progress': {
                'total_xp': user.xp_points,
                'lessons': {
                    'total': lesson_stats['total'] or 0,
                    'completed': lesson_stats['completed'] or 0,
                    'avg_accuracy': round(lesson_stats['avg_accuracy'] or 0, 1),
                },
                'phonemes': {
                    'total_practiced': phoneme_stats['total_practiced'] or 0,
                    'mastered': phoneme_stats['mastered'] or 0,
                    'avg_accuracy': round(phoneme_stats['avg_accuracy'] or 0, 1),
                },
                'streak': streak_data,
                'recent_lessons': recent_data,
            }
        })


class PhonemeListWithProgressView(APIView):
    """
    Get all phonemes organized by category with user progress.
    
    GET /api/v1/pronunciation/phonemes/
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        categories = PhonemeCategory.objects.prefetch_related('phonemes').order_by('order')
        
        # Get user progress if authenticated
        user_progress = {}
        if request.user.is_authenticated:
            progress_qs = UserPhonemeProgress.objects.filter(user=request.user)
            for p in progress_qs:
                user_progress[p.phoneme_id] = {
                    'mastery_level': p.mastery_level,
                    'accuracy_rate': round(p.accuracy_rate, 1),
                    'times_practiced': p.times_practiced,
                }
        
        result = []
        for category in categories:
            phonemes = []
            for phoneme in category.phonemes.filter(is_active=True).order_by('order'):
                phonemes.append({
                    'id': phoneme.id,
                    'ipa_symbol': phoneme.ipa_symbol,
                    'vietnamese_approx': phoneme.vietnamese_approx,
                    'phoneme_type': phoneme.phoneme_type,
                    'voicing': phoneme.voicing,
                    'progress': user_progress.get(phoneme.id, None),
                })
            
            result.append({
                'id': category.id,
                'name': category.name,
                'name_vi': category.name_vi,
                'category_type': category.category_type,
                'description_vi': category.description_vi,
                'phonemes': phonemes,
            })
        
        return Response({
            'success': True,
            'categories': result,
        })
