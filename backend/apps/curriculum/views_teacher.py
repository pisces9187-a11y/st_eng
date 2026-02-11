"""
Teacher Dashboard view
"""

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from apps.curriculum.models import (
    Phoneme, MinimalPair, AudioSource, AudioVersion, PhonemeWord
)


@staff_member_required
def teacher_dashboard(request):
    """
    Teacher Dashboard showing:
    - Stats overview
    - Action items (what needs attention)
    - Quick actions
    """
    
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    # Phoneme stats
    total_phonemes = Phoneme.objects.filter(is_active=True).count()
    phonemes_with_audio = Phoneme.objects.filter(
        is_active=True,
        preferred_audio_source__isnull=False
    ).count()
    
    phonemes_with_native = AudioVersion.objects.filter(
        is_active=True,
        audio_source__source_type='native'
    ).values('phoneme').distinct().count()
    
    # Phonemes with good coverage (3+ minimal pairs)
    phonemes_good_coverage = Phoneme.objects.filter(
        is_active=True
    ).annotate(
        pair_count=Count('minimal_pairs_1') + Count('minimal_pairs_2')
    ).filter(pair_count__gte=3).count()
    
    # Minimal pair stats
    total_pairs = MinimalPair.objects.count()
    beginner_pairs = MinimalPair.objects.filter(difficulty_level='beginner').count()
    intermediate_pairs = MinimalPair.objects.filter(difficulty_level='intermediate').count()
    advanced_pairs = MinimalPair.objects.filter(difficulty_level='advanced').count()
    verified_pairs = MinimalPair.objects.filter(is_verified=True).count()
    
    # Audio stats
    total_audio = AudioSource.objects.count()
    native_audio = AudioSource.objects.filter(source_type='native').count()
    tts_audio = AudioSource.objects.filter(source_type='tts').count()
    generated_audio = AudioSource.objects.filter(source_type='generated').count()
    
    # Recent activity (last 7 days)
    week_ago = timezone.now() - timedelta(days=7)
    recent_pairs = MinimalPair.objects.filter(created_at__gte=week_ago).count()
    recent_audio = AudioVersion.objects.filter(created_at__gte=week_ago).count()
    
    # =========================================================================
    # ACTION ITEMS
    # =========================================================================
    
    # Phonemes needing audio
    phonemes_need_audio = Phoneme.objects.filter(
        is_active=True,
        preferred_audio_source__isnull=True
    ).select_related('category')[:10]
    
    # Phonemes needing more pairs (< 3 pairs)
    phonemes_need_pairs = Phoneme.objects.filter(
        is_active=True
    ).annotate(
        pair_count=Count('minimal_pairs_1') + Count('minimal_pairs_2')
    ).filter(pair_count__lt=3).select_related('category')[:10]
    
    # Phonemes needing native audio (only have TTS)
    phonemes_need_native = Phoneme.objects.filter(
        is_active=True,
        preferred_audio_source__source_type='tts'
    ).select_related('preferred_audio_source')[:10]
    
    # Pairs needing verification
    pairs_need_verification = MinimalPair.objects.filter(
        is_verified=False
    ).select_related('phoneme_1', 'phoneme_2')[:10]
    
    # =========================================================================
    # QUICK INSIGHTS
    # =========================================================================
    
    # Audio coverage percentage
    audio_coverage = (phonemes_with_audio / total_phonemes * 100) if total_phonemes > 0 else 0
    native_coverage = (phonemes_with_native / total_phonemes * 100) if total_phonemes > 0 else 0
    
    # Pair distribution
    pair_distribution = {
        'beginner': (beginner_pairs / total_pairs * 100) if total_pairs > 0 else 0,
        'intermediate': (intermediate_pairs / total_pairs * 100) if total_pairs > 0 else 0,
        'advanced': (advanced_pairs / total_pairs * 100) if total_pairs > 0 else 0,
    }
    
    context = {
        # Stats
        'total_phonemes': total_phonemes,
        'phonemes_with_audio': phonemes_with_audio,
        'phonemes_with_native': phonemes_with_native,
        'phonemes_good_coverage': phonemes_good_coverage,
        
        'total_pairs': total_pairs,
        'beginner_pairs': beginner_pairs,
        'intermediate_pairs': intermediate_pairs,
        'advanced_pairs': advanced_pairs,
        'verified_pairs': verified_pairs,
        
        'total_audio': total_audio,
        'native_audio': native_audio,
        'tts_audio': tts_audio,
        'generated_audio': generated_audio,
        
        'recent_pairs': recent_pairs,
        'recent_audio': recent_audio,
        
        # Action items
        'phonemes_need_audio': phonemes_need_audio,
        'phonemes_need_pairs': phonemes_need_pairs,
        'phonemes_need_native': phonemes_need_native,
        'pairs_need_verification': pairs_need_verification,
        
        # Insights
        'audio_coverage': round(audio_coverage, 1),
        'native_coverage': round(native_coverage, 1),
        'pair_distribution': pair_distribution,
    }
    
    return render(request, 'admin/teacher_dashboard.html', context)
