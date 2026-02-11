#!/usr/bin/env python
"""
Import Oxford 3000/5000 vocabulary from CSV files into database.

This script:
1. Reads CSV files for each CEFR level (A1, A2, B1, B2, C1)
2. Cleans data (removes extra whitespace)
3. Parses part of speech (POS) tags
4. Creates Word entries with proper unique constraints
5. Handles duplicates gracefully

Usage:
    python backend/import_oxford_vocabulary.py
"""

import os
import sys
import django
import csv
from pathlib import Path

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.vocabulary.models import Word
from django.db import transaction


# CEFR levels to import
CEFR_LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1']

# CSV file paths
BASE_DIR = Path(__file__).resolve().parent.parent
DICTIONARY_DIR = BASE_DIR / 'dictionary'


def clean_text(text):
    """Remove extra whitespace from text."""
    if not text:
        return ''
    return text.strip()


def parse_pos(pos_text):
    """
    Parse part of speech from CSV format.
    
    Examples:
    - "n" -> "noun"
    - "verb" -> "verb"
    - "adj" -> "adjective"
    - "preposition, adverb" -> "preposition"  (take first)
    - "(money) n" -> "noun"
    """
    if not pos_text:
        return 'other'
    
    # Clean the text
    pos_text = clean_text(pos_text)
    
    # Remove parenthetical notes like "(money)", "(type)"
    import re
    pos_text = re.sub(r'\([^)]*\)', '', pos_text)
    pos_text = pos_text.strip()
    
    # Handle multiple POS separated by comma - take the first one
    if ',' in pos_text:
        pos_text = pos_text.split(',')[0].strip()
    
    # Handle slash separated - take the first one
    if '/' in pos_text:
        pos_text = pos_text.split('/')[0].strip()
    
    # Normalize abbreviations
    pos_map = {
        'n': 'noun',
        'v': 'verb',
        'adj': 'adjective',
        'adv': 'adverb',
        'prep': 'preposition',
        'conj': 'conjunction',
        'pron': 'pronoun',
        'det': 'determiner',
        'exclam': 'exclamation',
        'modal': 'modal verb',
        'auxiliary': 'auxiliary verb',
        'number': 'number',
    }
    
    # Try to match abbreviation
    pos_lower = pos_text.lower()
    for abbr, full in pos_map.items():
        if pos_lower.startswith(abbr):
            return full
    
    # Return as-is if already full form
    if pos_lower in ['noun', 'verb', 'adjective', 'adverb', 'preposition', 
                     'conjunction', 'pronoun', 'determiner', 'exclamation']:
        return pos_lower
    
    # Default
    return pos_text if pos_text else 'other'


def import_csv_file(file_path, cefr_level):
    """
    Import words from a single CSV file.
    
    CSV format:
    text, pos, ipa, meaning_vi
    
    Returns:
    - (created_count, updated_count, skipped_count)
    """
    print(f"\n{'='*60}")
    print(f"Importing {cefr_level} vocabulary from: {file_path}")
    print(f"{'='*60}")
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return (0, 0, 0)
    
    created_count = 0
    updated_count = 0
    skipped_count = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        # Read CSV with proper handling
        reader = csv.reader(f)
        
        for row_num, row in enumerate(reader, start=1):
            # Skip empty rows
            if not row or len(row) < 4:
                continue
            
            # Extract fields
            text = clean_text(row[0])
            pos_raw = clean_text(row[1])
            ipa = clean_text(row[2])
            meaning_vi = clean_text(row[3])
            
            # Skip invalid entries
            if not text or not meaning_vi:
                skipped_count += 1
                continue
            
            # Skip header-like rows
            if text.lower() in ['about', '©'] and row_num == 1:
                continue
            
            # Skip copyright notices
            if '©' in text or 'Oxford' in text:
                skipped_count += 1
                continue
            
            # Skip malformed entries
            if text.startswith('#') or meaning_vi.startswith('#'):
                skipped_count += 1
                continue
            
            # Parse POS
            pos = parse_pos(pos_raw)
            
            try:
                with transaction.atomic():
                    # Try to find existing word with same text, pos, and cefr_level
                    word, created = Word.objects.get_or_create(
                        text=text,
                        pos=pos,
                        cefr_level=cefr_level,
                        defaults={
                            'ipa': ipa,
                            'meaning_vi': meaning_vi,
                            'meaning_en': '',
                        }
                    )
                    
                    if created:
                        created_count += 1
                        if created_count % 50 == 0:
                            print(f"  ✓ Created {created_count} words...")
                    else:
                        # Update existing word
                        word.ipa = ipa
                        word.meaning_vi = meaning_vi
                        word.save()
                        updated_count += 1
                        
            except Exception as e:
                print(f"  ⚠ Error on row {row_num} ({text}): {e}")
                skipped_count += 1
                continue
    
    print(f"\n📊 Import Summary for {cefr_level}:")
    print(f"  ✅ Created: {created_count}")
    print(f"  🔄 Updated: {updated_count}")
    print(f"  ⏭️  Skipped: {skipped_count}")
    
    return (created_count, updated_count, skipped_count)


def main():
    """Main import function."""
    print("\n" + "="*60)
    print("🚀 Oxford Vocabulary Import Tool")
    print("="*60)
    
    # Confirm before proceeding
    print("\nThis will import vocabulary from CSV files:")
    for level in CEFR_LEVELS:
        csv_path = DICTIONARY_DIR / f'{level}.csv'
        status = "✓" if csv_path.exists() else "✗"
        print(f"  {status} {level}: {csv_path}")
    
    response = input("\nProceed with import? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("❌ Import cancelled.")
        return
    
    # Import each level
    total_created = 0
    total_updated = 0
    total_skipped = 0
    
    for level in CEFR_LEVELS:
        csv_path = DICTIONARY_DIR / f'{level}.csv'
        created, updated, skipped = import_csv_file(csv_path, level)
        total_created += created
        total_updated += updated
        total_skipped += skipped
    
    # Final summary
    print("\n" + "="*60)
    print("🎉 IMPORT COMPLETE!")
    print("="*60)
    print(f"Total Created:  {total_created}")
    print(f"Total Updated:  {total_updated}")
    print(f"Total Skipped:  {total_skipped}")
    print(f"Total Processed: {total_created + total_updated + total_skipped}")
    
    # Show database stats
    print("\n📈 Database Statistics:")
    for level in CEFR_LEVELS:
        count = Word.objects.filter(cefr_level=level).count()
        print(f"  {level}: {count} words")
    
    total_words = Word.objects.count()
    print(f"\n  Total Words in Database: {total_words}")
    print("\n✨ Import successful!\n")


if __name__ == '__main__':
    main()
