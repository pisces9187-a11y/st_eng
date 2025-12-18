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
                    'current_stage': p.current_stage,
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


# ============================================================================
# PAGE VIEWS (Frontend HTML Rendering)
# ============================================================================

from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from functools import wraps
import json


def jwt_required(view_func):
    """Decorator to check JWT authentication for template views."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not getattr(request, 'jwt_authenticated', False):
            next_url = request.get_full_path()
            return redirect(f'/login/?next={next_url}')
        return view_func(request, *args, **kwargs)
    return wrapper


@jwt_required
@require_http_methods(["GET"])
def pronunciation_discovery_view(request):
    """
    Render the phoneme discovery page.
    
    Shows all 44 IPA phonemes in an interactive grid.
    Users can click to mark phonemes as discovered.
    """
    context = {
        'page_title': 'Khám phá âm IPA',
        'meta_description': 'Khám phá và học 44 âm IPA tiếng Anh qua hệ thống 4 giai đoạn SMART',
    }
    
    return render(request, 'pages/pronunciation_discovery.html', context)


@jwt_required
@require_http_methods(["GET"])
def pronunciation_learning_view(request, phoneme_id):
    """
    Render the learning page for a specific phoneme.
    
    Shows:
    - Phoneme details (IPA symbol, Vietnamese approximation)
    - Audio playback for reference pronunciation
    - Mouth diagram and pronunciation tips
    - Example words
    - Current learning progress
    """
    # Get phoneme
    phoneme = get_object_or_404(Phoneme, pk=phoneme_id, is_active=True)
    
    # Get user's progress for this phoneme
    progress, _ = UserPhonemeProgress.objects.get_or_create(
        user=request.user,
        phoneme=phoneme
    )
    
    # Prepare phoneme data for JSON serialization
    phoneme_data = {
        'id': phoneme.id,
        'ipa_symbol': phoneme.ipa_symbol,
        'vietnamese_approx': phoneme.vietnamese_approx,
        'phoneme_type': phoneme.phoneme_type,
        'voicing': phoneme.voicing,
        'mouth_position': phoneme.mouth_position_vi or phoneme.mouth_position,
        'tongue_position': phoneme.tongue_position_vi or phoneme.tongue_position,
        'audio_sample': phoneme.audio_sample.url if phoneme.audio_sample else None,
        'mouth_diagram': phoneme.mouth_diagram.url if phoneme.mouth_diagram else None,
        'pronunciation_tips': _get_pronunciation_tips(phoneme),
        'example_words': _get_example_words(phoneme),
    }
    
    # Prepare progress data
    progress_data = {
        'current_stage': progress.current_stage,
        'mastery_level': progress.mastery_level,
        'discrimination_accuracy': progress.discrimination_accuracy,
        'discrimination_attempts': progress.discrimination_attempts,
        'production_best_score': progress.production_best_score,
        'production_attempts': progress.production_attempts,
        'times_practiced': progress.times_practiced,
        'accuracy_rate': progress.accuracy_rate,
    }
    
    context = {
        'phoneme': phoneme,
        'phoneme_json': json.dumps(phoneme_data),
        'progress': progress,
        'progress_json': json.dumps(progress_data),
        'page_title': f'Học âm {phoneme.ipa_symbol}',
        'meta_description': f'Học cách phát âm chuẩn âm IPA {phoneme.ipa_symbol} qua lý thuyết và thực hành',
    }
    
    return render(request, 'pages/pronunciation_learning.html', context)


def _get_pronunciation_tips(phoneme):
    """
    Get pronunciation tips for a phoneme.
    
    In future, this could be stored in database.
    For now, returns generic tips based on phoneme type.
    """
    tips = []
    
    # Generic tips applicable to all phonemes
    tips.append(f'Chú ý đến hình dạng môi và vị trí lưỡi khi phát âm /{phoneme.ipa_symbol}/')
    tips.append('Nghe và bắt chước âm mẫu nhiều lần để quen tai')
    
    # Type-specific tips
    if phoneme.phoneme_type in ['long_vowel', 'short_vowel']:
        tips.append('Nguyên âm cần giữ nguyên vị trí miệng trong suốt quá trình phát âm')
        tips.append(f'So sánh với âm tiếng Việt "{phoneme.vietnamese_approx}" để dễ nhớ')
    elif phoneme.phoneme_type == 'diphthong':
        tips.append('Nguyên âm đôi: bắt đầu từ một âm và trượt sang âm khác')
        tips.append('Âm đầu tiên mạnh hơn, âm thứ hai nhẹ dần')
    elif phoneme.phoneme_type in ['voiced_consonant', 'unvoiced_consonant']:
        tips.append('Phụ âm: chú ý đến cách khí thoát ra và rung dây thanh')
        if phoneme.phoneme_type == 'voiced_consonant':
            tips.append('Đây là phụ âm hữu thanh - dây thanh rung khi phát âm')
        else:
            tips.append('Đây là phụ âm vô thanh - dây thanh không rung')
    
    # Add specific tips from model if available
    if phoneme.pronunciation_tips_vi:
        tips.append(phoneme.pronunciation_tips_vi)
    elif phoneme.pronunciation_tips:
        tips.append(phoneme.pronunciation_tips)
    
    return tips


def _get_example_words(phoneme):
    """
    Get example words containing this phoneme.
    
    In future, this could be fetched from database (MinimalPair or Sentence models).
    For now, returns sample data.
    """
    # This is a placeholder - in production, query from database
    examples = []
    
    # TODO: Query from MinimalPair where phoneme_a or phoneme_b matches
    # TODO: Or create a new ExampleWord model
    
    # Sample data based on common phonemes
    sample_examples = {
        '/iː/': [
            {'word': 'see', 'phonetic': 'siː', 'meaning': 'nhìn', 'audio_url': None},
            {'word': 'tree', 'phonetic': 'triː', 'meaning': 'cây', 'audio_url': None},
            {'word': 'eat', 'phonetic': 'iːt', 'meaning': 'ăn', 'audio_url': None},
        ],
        '/ɪ/': [
            {'word': 'sit', 'phonetic': 'sɪt', 'meaning': 'ngồi', 'audio_url': None},
            {'word': 'big', 'phonetic': 'bɪg', 'meaning': 'lớn', 'audio_url': None},
            {'word': 'fish', 'phonetic': 'fɪʃ', 'meaning': 'cá', 'audio_url': None},
        ],
        '/æ/': [
            {'word': 'cat', 'phonetic': 'kæt', 'meaning': 'mèo', 'audio_url': None},
            {'word': 'hat', 'phonetic': 'hæt', 'meaning': 'mũ', 'audio_url': None},
            {'word': 'man', 'phonetic': 'mæn', 'meaning': 'đàn ông', 'audio_url': None},
        ],
    }
    
    # Return examples if available for this phoneme
    if phoneme.ipa_symbol in sample_examples:
        return sample_examples[phoneme.ipa_symbol]
    
    # Return empty list if no examples found
    return examples


@jwt_required
@require_http_methods(["GET"])
def pronunciation_discrimination_view(request, phoneme_id):
    """
    Render the discrimination practice page.
    
    Shows quiz interface for minimal pair discrimination.
    """
    phoneme = get_object_or_404(Phoneme, pk=phoneme_id, is_active=True)
    
    context = {
        'phoneme': phoneme,
        'page_title': f'Luyện phân biệt âm {phoneme.ipa_symbol}',
        'meta_description': f'Luyện tập phân biệt âm {phoneme.ipa_symbol} qua các cặp từ tối thiểu',
    }
    
    return render(request, 'pages/pronunciation_discrimination.html', context)


@jwt_required
@require_http_methods(["GET"])
def pronunciation_production_view(request, phoneme_id):
    """
    Render the production practice page.
    
    Shows recording interface for pronunciation practice.
    """
    phoneme = get_object_or_404(Phoneme, pk=phoneme_id, is_active=True)
    
    context = {
        'phoneme': phoneme,
        'page_title': f'Luyện phát âm {phoneme.ipa_symbol}',
        'meta_description': f'Thực hành phát âm chuẩn âm {phoneme.ipa_symbol}',
    }
    
    return render(request, 'pages/pronunciation_production.html', context)


@jwt_required
@require_http_methods(["GET"])
def pronunciation_progress_dashboard_view(request):
    """
    Render the overall progress dashboard.
    
    Shows:
    - Overall statistics
    - Recently practiced phonemes
    - Recommended next phonemes
    - Stage-by-stage breakdown
    """
    context = {
        'page_title': 'Tiến độ học phát âm',
        'meta_description': 'Xem tiến độ học và thành tích phát âm tiếng Anh của bạn',
    }
    
    return render(request, 'pages/pronunciation_progress.html', context)

# ==================== Day 6-7: Discrimination Quiz Views ====================

@jwt_required
@require_http_methods(["GET"])
def discrimination_start_view(request):
    """
    Discrimination quiz start page.
    
    Shows:
    - Quiz instructions (10 questions, 5 minutes)
    - User's best score and session count
    - Start Quiz button
    """
    from apps.study.models import DiscriminationSession
    
    # Get user stats
    completed_sessions = DiscriminationSession.objects.filter(
        user=request.user,
        status='completed'
    )
    
    best_session = completed_sessions.order_by('-accuracy').first()
    total_sessions = completed_sessions.count()
    
    context = {
        'page_title': 'Discrimination Practice - Luyện phân biệt âm',
        'meta_description': 'Luyện phân biệt các cặp âm tương tự trong tiếng Anh',
        'best_score': best_session.accuracy if best_session else 0,
        'total_sessions': total_sessions,
    }
    
    return render(request, 'pages/discrimination_start.html', context)

# ==================== Day 10: Learning Hub Dashboard View ====================

@jwt_required
@require_http_methods(["GET"])
def learning_hub_dashboard_view(request):
    """
    Learning Hub Dashboard - Main overview page.
    
    Shows:
    - Overall statistics (30 days)
    - Progress charts (Chart.js)
    - Top 3 phoneme recommendations
    - Recent activity feed
    - Quick action buttons
    """
    context = {
        'page_title': 'Learning Hub - Dashboard',
        'meta_description': 'Tổng quan tiến độ học phát âm tiếng Anh',
    }
    return render(request, 'pages/learning_hub_dashboard.html', context)
# ==================== Day 8-9: Production Recording Views ====================

@jwt_required
@require_http_methods(["GET"])
def production_record_view(request, phoneme_id):
    """Production recording interface for a specific phoneme."""
    phoneme = get_object_or_404(Phoneme, id=phoneme_id)
    
    from apps.study.models import ProductionRecording
    recordings_qs = ProductionRecording.objects.filter(
        user=request.user, phoneme=phoneme
    ).order_by('-created_at')[:5]
    
    # Serialize recordings for JSON
    recordings_data = []
    for rec in recordings_qs:
        recordings_data.append({
            'id': rec.id,
            'recording_url': request.build_absolute_uri(rec.recording_file.url),
            'duration_seconds': rec.duration_seconds,
            'self_assessment_score': rec.self_assessment_score,
            'is_best': rec.is_best,
            'created_at': rec.created_at.isoformat(),
        })
    
    context = {
        'page_title': f'Practice Recording - {phoneme.ipa_symbol}',
        'meta_description': f'Luyện phát âm {phoneme.name_vi}',
        'phoneme': phoneme,
        'recordings': json.dumps(recordings_data),
    }
    return render(request, 'pages/production_record.html', context)


@jwt_required
@require_http_methods(["GET"])
def production_history_view(request):
    """Production recording history page."""
    from apps.study.models import ProductionRecording
    
    phoneme_id = request.GET.get('phoneme_id')
    recordings_qs = ProductionRecording.objects.filter(
        user=request.user
    ).select_related('phoneme').order_by('-created_at')
    
    if phoneme_id:
        recordings_qs = recordings_qs.filter(phoneme_id=phoneme_id)
    
    total_recordings = recordings_qs.count()
    unique_phonemes = recordings_qs.values('phoneme').distinct().count()
    avg_score = recordings_qs.filter(
        self_assessment_score__isnull=False
    ).aggregate(Avg('self_assessment_score'))['self_assessment_score__avg'] or 0
    
    # Serialize recordings for JSON
    recordings_data = []
    for rec in recordings_qs[:50]:
        recordings_data.append({
            'id': rec.id,
            'phoneme': {
                'id': rec.phoneme.id,
                'ipa_symbol': rec.phoneme.ipa_symbol,
                'name_vi': rec.phoneme.name_vi,
            },
            'recording_url': request.build_absolute_uri(rec.recording_file.url),
            'duration_seconds': rec.duration_seconds,
            'self_assessment_score': rec.self_assessment_score,
            'is_best': rec.is_best,
            'created_at': rec.created_at.isoformat(),
        })
    
    phonemes = Phoneme.objects.all().order_by('ipa_symbol')
    
    context = {
        'page_title': 'Recording History',
        'meta_description': 'Lịch sử ghi âm luyện phát âm',
        'recordings': json.dumps(recordings_data),
        'phonemes': phonemes,
        'selected_phoneme_id': int(phoneme_id) if phoneme_id else None,
        'stats': {
            'total_recordings': total_recordings,
            'unique_phonemes': unique_phonemes,
            'avg_score': round(avg_score, 2)
        }
    }
    return render(request, 'pages/production_history.html', context)

@jwt_required
@require_http_methods(["GET"])
def discrimination_quiz_view(request, session_id):
    """
    Active discrimination quiz interface.
    
    Validates session exists and belongs to user.
    Vue.js handles the quiz interaction.
    """
    from apps.study.models import DiscriminationSession
    
    session = get_object_or_404(
        DiscriminationSession,
        session_id=session_id,
        user=request.user
    )
    
    if session.status != 'in_progress':
        # Redirect to results if already completed
        if session.status == 'completed':
            return redirect('curriculum:discrimination-results', session_id=session_id)
        # Redirect to start if expired/abandoned
        return redirect('curriculum:discrimination-start')
    
    context = {
        'page_title': 'Discrimination Quiz',
        'meta_description': 'Luyện phân biệt âm tiếng Anh',
        'session_id': session_id,
    }
    
    return render(request, 'pages/discrimination_quiz.html', context)


@jwt_required
@require_http_methods(["GET"])
def discrimination_results_view(request, session_id):
    """
    Discrimination quiz results page.
    
    Shows:
    - Final score
    - Question breakdown
    - Time spent
    - Progress updates
    """
    from apps.study.models import DiscriminationSession, DiscriminationAttempt
    
    session = get_object_or_404(
        DiscriminationSession,
        session_id=session_id,
        user=request.user
    )
    
    if session.status != 'completed':
        return redirect('curriculum:discrimination-start')
    
    # Get all attempts
    attempts = DiscriminationAttempt.objects.filter(
        session=session
    ).select_related('minimal_pair', 'minimal_pair__phoneme_1', 'minimal_pair__phoneme_2').order_by('question_number')
    
    # Calculate stats
    total_time = (session.completed_at - session.started_at).total_seconds() if session.completed_at else 0
    avg_response_time = attempts.aggregate(Avg('response_time'))['response_time__avg'] or 0
    
    context = {
        'page_title': 'Quiz Results',
        'meta_description': 'Kết quả bài tập phân biệt âm',
        'session': session,
        'attempts': attempts,
        'total_time': total_time,
        'avg_response_time': avg_response_time,
    }
    
    return render(request, 'pages/discrimination_results.html', context)