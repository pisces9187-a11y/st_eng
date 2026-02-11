#!/usr/bin/env python
"""
Quick script to check vocabulary database statistics
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.vocabulary.models import Word, FlashcardDeck, Flashcard

print('\n📊 VOCABULARY DATABASE STATISTICS\n')
print('='*50)

# Total words
total_words = Word.objects.count()
print(f'\n✅ Total Words: {total_words:,}')

# Words by level
print(f'\n📚 Words by CEFR Level:')
print('-'*50)
for level in ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']:
    count = Word.objects.filter(cefr_level=level).count()
    if count > 0:
        percentage = (count / total_words) * 100
        print(f'  {level}: {count:>6,} words ({percentage:>5.1f}%)')

# Words by POS
print(f'\n🔤 Words by Part of Speech (Top 10):')
print('-'*50)
from django.db.models import Count
pos_stats = Word.objects.values('pos').annotate(
    count=Count('pos')
).order_by('-count')[:10]

for item in pos_stats:
    pos = item['pos']
    count = item['count']
    percentage = (count / total_words) * 100
    print(f'  {pos:<20}: {count:>6,} ({percentage:>5.1f}%)')

# Flashcard decks
print(f'\n🎴 Flashcard Decks:')
print('-'*50)
total_decks = FlashcardDeck.objects.count()
print(f'\nTotal Decks: {total_decks}')

for deck in FlashcardDeck.objects.all().order_by('level', 'name'):
    card_count = Flashcard.objects.filter(deck=deck).count()
    print(f'  {deck.icon} {deck.name}')
    print(f'     └─ {card_count} flashcards')

# Total flashcards
total_flashcards = Flashcard.objects.count()
print(f'\n✅ Total Flashcards: {total_flashcards:,}')

print('\n' + '='*50)
print('✨ Import Complete!\n')
