"""
Management command to seed minimal pairs from CSV file.
"""

import csv
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.curriculum.models import MinimalPair, Phoneme


class Command(BaseCommand):
    help = 'Seeds minimal pairs from CSV file'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('🔤 Seeding Minimal Pairs...'))
        
        csv_path = os.path.join('backend', 'data', 'minimal_pairs.csv')
        if not os.path.exists(csv_path):
            # Try without backend prefix
            csv_path = os.path.join('data', 'minimal_pairs.csv')
        
        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f'❌ CSV file not found: {csv_path}'))
            return
        
        created_count = 0
        updated_count = 0
        error_count = 0
        
        with transaction.atomic():
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    try:
                        # Get phonemes
                        phoneme_1_symbol = row['phoneme_1']
                        phoneme_2_symbol = row['phoneme_2']
                        
                        try:
                            phoneme_1 = Phoneme.objects.get(ipa_symbol=phoneme_1_symbol)
                            phoneme_2 = Phoneme.objects.get(ipa_symbol=phoneme_2_symbol)
                        except Phoneme.DoesNotExist:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'  ⚠️  Phoneme not found: /{phoneme_1_symbol}/ or /{phoneme_2_symbol}/'
                                )
                            )
                            error_count += 1
                            continue
                        
                        # Create or update minimal pair
                        pair, created = MinimalPair.objects.update_or_create(
                            phoneme_1=phoneme_1,
                            phoneme_2=phoneme_2,
                            word_1=row['word_1'],
                            word_2=row['word_2'],
                            defaults={
                                'word_1_ipa': row['word_1_ipa'],
                                'word_1_meaning': row['word_1_meaning'],
                                'word_2_ipa': row['word_2_ipa'],
                                'word_2_meaning': row['word_2_meaning'],
                                'difficulty': int(row['difficulty']),
                                'difference_note_vi': row.get('difference_note_vi', ''),
                                'order': created_count + updated_count
                            }
                        )
                        
                        if created:
                            created_count += 1
                            if created_count % 10 == 0:
                                self.stdout.write(f'  ✨ Created {created_count} pairs...')
                        else:
                            updated_count += 1
                    
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'  ❌ Error processing row: {str(e)}')
                        )
                        error_count += 1
                        continue
        
        total = MinimalPair.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Successfully seeded minimal pairs!\n'
                f'   Created: {created_count}\n'
                f'   Updated: {updated_count}\n'
                f'   Errors: {error_count}\n'
                f'   Total in DB: {total}'
            )
        )
        
        # Show some examples
        self.stdout.write('\n📊 Sample minimal pairs:')
        examples = MinimalPair.objects.all()[:5]
        for pair in examples:
            self.stdout.write(
                f'  • /{pair.phoneme_1.ipa_symbol}/ vs /{pair.phoneme_2.ipa_symbol}/: '
                f'{pair.word_1} ({pair.word_1_meaning}) ↔ {pair.word_2} ({pair.word_2_meaning})'
            )
