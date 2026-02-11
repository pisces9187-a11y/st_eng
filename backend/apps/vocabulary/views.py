"""
Vocabulary template views for frontend pages
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from apps.users.middleware import jwt_required
from .models import FlashcardDeck, Word


@jwt_required
def flashcard_study_view(request, deck_id=None):
    """
    Enhanced Flashcard study page with Phase 2 features:
    - Multi-voice audio player
    - SM-2 spaced repetition
    - Quality ratings (Again/Hard/Good/Easy)
    - Real-time statistics
    - Achievement tracking
    
    URL: /vocabulary/flashcard/ or /vocabulary/flashcard/{deck_id}/
    """
    deck = None
    if deck_id:
        deck = get_object_or_404(FlashcardDeck, id=deck_id)
    
    # Get all available decks for deck selector
    decks = FlashcardDeck.objects.filter(is_public=True).order_by('level', 'name')
    
    # Get user stats for display
    user = request.user
    
    context = {
        'deck': deck,
        'decks': decks,
        'page_title': f'Flashcard - {deck.name}' if deck else 'Flashcard Study',
        'user': user,
    }
    
    return render(request, 'vocabulary/flashcard_study_v2.html', context)


@jwt_required
def deck_list_view(request):
    """
    List all available flashcard decks
    Uses JWT authentication for consistency with dashboard.
    
    URL: /vocabulary/decks/
    """
    decks = FlashcardDeck.objects.filter(is_public=True).order_by('-is_official', 'level', 'name')
    
    # Group by level
    decks_by_level = {}
    for deck in decks:
        level = deck.level or 'mixed'
        if level not in decks_by_level:
            decks_by_level[level] = []
        decks_by_level[level].append(deck)
    
    context = {
        'decks': decks,
        'decks_by_level': decks_by_level,
        'page_title': 'Flashcard Decks',
    }
    
    return render(request, 'vocabulary/deck_list.html', context)


@jwt_required
def vocabulary_dashboard_view(request):
    """
    User's vocabulary learning dashboard with statistics
    Uses JWT authentication for consistency across the app.
    
    URL: /vocabulary/dashboard/
    """
    context = {
        'page_title': 'Vocabulary Dashboard',
    }
    
    return render(request, 'vocabulary/dashboard.html', context)
