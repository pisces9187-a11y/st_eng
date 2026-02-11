import sys
sys.path.insert(0, 'c:/Users/n2t/Documents/english_study/backend')

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.vocabulary.models import Word, FlashcardDeck, Flashcard

print(f'📚 Words: {Word.objects.count()}')
print(f'📦 Decks: {FlashcardDeck.objects.count()}')
print(f'🃏 Flashcards: {Flashcard.objects.count()}')
print()

for deck in FlashcardDeck.objects.all().order_by('level'):
    print(f'{deck.icon} {deck.name}: {deck.card_count} cards')

print()
print('Sample words by level:')
for level in ['A1', 'A2', 'B1', 'B2']:
    count = Word.objects.filter(cefr_level=level).count()
    sample = Word.objects.filter(cefr_level=level).first()
    print(f'  {level}: {count} words (e.g., "{sample.text}" - {sample.pos})')
