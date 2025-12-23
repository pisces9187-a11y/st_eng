"""
Vocabulary page URLs (Django templates)
"""

from django.urls import path
from . import views

app_name = 'vocabulary_pages'

urlpatterns = [
    # Flashcard study page
    path('flashcard/', views.flashcard_study_view, name='flashcard-study'),
    path('flashcard/<int:deck_id>/', views.flashcard_study_view, name='flashcard-study-deck'),
    
    # Deck list page
    path('decks/', views.deck_list_view, name='deck-list'),
    
    # Dashboard
    path('dashboard/', views.vocabulary_dashboard_view, name='dashboard'),
]
