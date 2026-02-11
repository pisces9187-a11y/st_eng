#!/usr/bin/env python
"""
Check vocabulary data quality and statistics.
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.vocabulary.models import Word
from django.db.models import Count


def check_data_quality():
    """Check data quality and print statistics."""
    
    print("\n" + "="*70)
    print("📊 VOCABULARY DATA QUALITY REPORT")
    print("="*70)
    
    # Total statistics
    total_words = Word.objects.count()
    print(f"\n✅ Total Words in Database: {total_words}")
    
    # By CEFR level
    print("\n📈 Words by CEFR Level:")
    for level in ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']:
        count = Word.objects.filter(cefr_level=level).count()
        if count > 0:
            print(f"   {level}: {count:4d} words")
    
    # By Part of Speech
    print("\n📚 Words by Part of Speech:")
    pos_stats = Word.objects.values('pos').annotate(
        count=Count('pos')
    ).order_by('-count')[:15]
    
    for item in pos_stats:
        print(f"   {item['pos']:20s}: {item['count']:4d} words")
    
    # Data quality checks
    print("\n🔍 Data Quality Checks:")
    
    # Missing IPA
    missing_ipa = Word.objects.filter(ipa='').count()
    print(f"   Missing IPA: {missing_ipa} words")
    
    # Missing meaning
    missing_meaning = Word.objects.filter(meaning_vi='').count()
    print(f"   Missing Vietnamese meaning: {missing_meaning} words")
    
    # Empty text
    empty_text = Word.objects.filter(text='').count()
    print(f"   Empty text: {empty_text} words")
    
    # Duplicate check
    print("\n🔁 Checking for duplicates...")
    duplicates = Word.objects.values('text', 'pos', 'cefr_level').annotate(
        count=Count('id')
    ).filter(count__gt=1)
    
    if duplicates.count() > 0:
        print(f"   ⚠️  Found {duplicates.count()} duplicate entries:")
        for dup in duplicates[:5]:
            print(f"      - {dup['text']} ({dup['pos']}, {dup['cefr_level']}): {dup['count']} times")
    else:
        print(f"   ✅ No duplicates found!")
    
    # Sample words from each level
    print("\n📝 Sample Words from Each Level:")
    for level in ['A1', 'A2', 'B1', 'B2', 'C1']:
        words = Word.objects.filter(cefr_level=level).order_by('?')[:2]
        if words.exists():
            print(f"\n   {level}:")
            for word in words:
                print(f"      • {word.text} ({word.pos})")
                print(f"        /{word.ipa}/ - {word.meaning_vi}")
    
    # Words with longest text
    print("\n📏 Longest Words:")
    long_words = Word.objects.all().order_by('-text')[:5]
    for word in long_words:
        print(f"   {word.text} ({len(word.text)} chars) - {word.cefr_level}")
    
    print("\n" + "="*70)
    print("✨ Report complete!")
    print("="*70 + "\n")


if __name__ == '__main__':
    check_data_quality()
