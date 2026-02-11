"""
Phase 4.2: Error Heatmap Dashboard View
Shows user's common pronunciation mistakes and patterns.
"""

from django.views.generic import TemplateView
from django.db.models import Count, Avg, Q
from apps.users.middleware import JWTRequiredMixin


class PronunciationErrorHeatmapView(JWTRequiredMixin, TemplateView):
    """
    Dashboard showing user's pronunciation error patterns.
    
    Features:
    - Error frequency by phoneme
    - Common mistake patterns
    - Improvement suggestions
    - Practice recommendations
    """
    template_name = 'curriculum/pronunciation/error_heatmap.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Import models
        from apps.curriculum.models import Phoneme, MinimalPair
        from apps.users.models import UserPhonemeProgress, UserPronunciationLessonProgress
        
        # 1. Get phonemes with low accuracy
        phoneme_errors = []
        for phoneme in Phoneme.objects.all():
            try:
                progress = UserPhonemeProgress.objects.get(user=user, phoneme=phoneme)
                accuracy_percent = progress.discrimination_accuracy * 100
                if accuracy_percent < 70:  # Less than 70% accuracy
                    phoneme_errors.append({
                        'phoneme': phoneme,
                        'accuracy': accuracy_percent,
                        'attempts': progress.times_practiced,
                        'error_rate': 100 - accuracy_percent
                    })
            except UserPhonemeProgress.DoesNotExist:
                pass
        
        # Sort by error rate (highest first)
        phoneme_errors.sort(key=lambda x: x['error_rate'], reverse=True)
        
        # 2. Get common mistake patterns from lesson progress
        common_mistakes = []
        lesson_progress = UserPronunciationLessonProgress.objects.filter(
            user=user,
            challenge_total__gt=0
        ).select_related('pronunciation_lesson__stage')
        
        for progress in lesson_progress:
            if progress.challenge_total > 0:
                accuracy = (progress.challenge_correct / progress.challenge_total) * 100
                if accuracy < 70:
                    common_mistakes.append({
                        'lesson': progress.pronunciation_lesson,
                        'accuracy': accuracy,
                        'correct': progress.challenge_correct,
                        'total': progress.challenge_total,
                        'stage': progress.pronunciation_lesson.stage
                    })
        
        # Sort by accuracy (lowest first)
        common_mistakes.sort(key=lambda x: x['accuracy'])
        
        # 3. Calculate overall stats
        total_lessons = UserPronunciationLessonProgress.objects.filter(user=user).count()
        completed_lessons = UserPronunciationLessonProgress.objects.filter(
            user=user,
            status='completed'
        ).count()
        
        avg_accuracy = 0
        lesson_progress_with_challenges = UserPronunciationLessonProgress.objects.filter(
            user=user,
            challenge_total__gt=0
        )
        if lesson_progress_with_challenges.exists():
            total_accuracy = sum(
                (lp.challenge_correct / lp.challenge_total * 100) 
                for lp in lesson_progress_with_challenges
            )
            avg_accuracy = total_accuracy / lesson_progress_with_challenges.count()
        
        # 4. Get practice recommendations
        recommendations = []
        
        # Recommend lessons for problematic phonemes
        for error in phoneme_errors[:5]:  # Top 5 errors
            phoneme = error['phoneme']
            # Find lessons containing this phoneme
            lessons = phoneme.pronunciation_lessons.filter(status='published').first()
            if lessons:
                recommendations.append({
                    'type': 'phoneme',
                    'title': f'Luyện tập âm /{phoneme.ipa_symbol}/',
                    'reason': f'Độ chính xác chỉ {error["accuracy"]:.0f}%',
                    'lesson': lessons,
                    'priority': 'high' if error['error_rate'] > 50 else 'medium'
                })
        
        # Recommend failed lessons
        for mistake in common_mistakes[:3]:  # Top 3 mistakes
            if mistake['accuracy'] < 50:
                recommendations.append({
                    'type': 'lesson',
                    'title': f'Học lại: {mistake["lesson"].title_vi}',
                    'reason': f'Chỉ {mistake["accuracy"]:.0f}% câu đúng',
                    'lesson': mistake['lesson'],
                    'priority': 'critical'
                })
        
        # 5. Identify mistake categories
        ending_sound_errors = 0
        cluster_errors = 0
        vowel_errors = 0
        consonant_errors = 0
        
        for error in phoneme_errors:
            phoneme_type = error['phoneme'].phoneme_type
            if phoneme_type in ['short_vowel', 'long_vowel']:
                vowel_errors += 1
            elif phoneme_type == 'diphthong':
                vowel_errors += 1
            else:
                consonant_errors += 1
        
        # Check for ending sound issues (Stage 4 lessons)
        stage4_lessons = UserPronunciationLessonProgress.objects.filter(
            user=user,
            pronunciation_lesson__stage__number=4,
            challenge_total__gt=0
        )
        
        for progress in stage4_lessons:
            if progress.challenge_total > 0:
                accuracy = (progress.challenge_correct / progress.challenge_total) * 100
                if accuracy < 70:
                    if 'ending' in progress.pronunciation_lesson.title.lower() or \
                       'cuối' in progress.pronunciation_lesson.title_vi.lower():
                        ending_sound_errors += 1
                    elif 'cluster' in progress.pronunciation_lesson.title.lower() or \
                         'tổ hợp' in progress.pronunciation_lesson.title_vi.lower():
                        cluster_errors += 1
        
        context.update({
            'phoneme_errors': phoneme_errors[:10],  # Top 10 errors
            'common_mistakes': common_mistakes[:5],  # Top 5 mistakes
            'recommendations': recommendations,
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'completion_rate': int((completed_lessons / total_lessons * 100)) if total_lessons > 0 else 0,
            'avg_accuracy': int(avg_accuracy),
            'error_categories': {
                'vowels': vowel_errors,
                'consonants': consonant_errors,
                'ending_sounds': ending_sound_errors,
                'clusters': cluster_errors
            },
            'has_errors': len(phoneme_errors) > 0 or len(common_mistakes) > 0
        })
        
        return context
