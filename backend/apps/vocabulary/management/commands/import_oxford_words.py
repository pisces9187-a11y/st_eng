"""
Management command to import Oxford 3000/5000 words and create flashcard decks.

Usage:
    python manage.py import_oxford_words --csv=path/to/oxford.csv --level=A1

Options:
    --csv: Path to CSV file (optional, will create sample data if not provided)
    --level: CEFR level (A1, A2, B1, B2, C1)
    --create-decks: Create flashcard decks automatically
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from apps.vocabulary.models import Word, FlashcardDeck, Flashcard
import csv
import os

User = get_user_model()


class Command(BaseCommand):
    help = 'Import Oxford words and create flashcard decks'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv',
            type=str,
            help='Path to CSV file with words (word,pos,level,meaning_vi,example_en)',
        )
        parser.add_argument(
            '--level',
            type=str,
            default='',
            help='Filter by CEFR level: A1, A2, B1, B2, C1',
        )
        parser.add_argument(
            '--create-decks',
            action='store_true',
            help='Automatically create flashcard decks after import',
        )
        parser.add_argument(
            '--sample',
            action='store_true',
            help='Create sample words and decks for testing',
        )

    def handle(self, *args, **options):
        if options['sample']:
            self.create_sample_data()
            return

        csv_file = options.get('csv')
        level_filter = options.get('level')
        create_decks = options.get('create_decks')

        if not csv_file:
            self.stdout.write(self.style.ERROR(
                'Please provide --csv path or use --sample for demo data'
            ))
            return

        if not os.path.exists(csv_file):
            raise CommandError(f'CSV file not found: {csv_file}')

        # Import words
        imported_count = self.import_words_from_csv(csv_file, level_filter)
        
        self.stdout.write(self.style.SUCCESS(
            f'Successfully imported {imported_count} words'
        ))

        # Create decks if requested
        if create_decks:
            self.create_flashcard_decks()

    def parse_oxford_line(self, line):
        """
        Parse Oxford CSV line format.
        
        Formats:
        1. "about prep., adv. A1" -> [('about', 'prep.', 'A1'), ('about', 'adv.', 'A1')]
        2. "account n. B1, v. B2" -> [('account', 'n.', 'B1'), ('account', 'v.', 'B2')]
        3. "a,an indefinite article A1" -> [('a', 'indefinite article', 'A1'), ('an', 'indefinite article', 'A1')]
        4. "abandon v. B2" -> [('abandon', 'v.', 'B2')]
        5. "all det., pron. A1, adv. A2" -> [('all', 'det.', 'A1'), ('all', 'pron.', 'A1'), ('all', 'adv.', 'A2')]
        
        Returns list of (word, pos, level) tuples
        """
        import re
        
        # Split by whitespace, keeping all parts
        parts = line.strip().split()
        
        if len(parts) < 2:
            return []
        
        # First part is the word(s)
        word_part = parts[0].rstrip(',')
        
        # Handle cases like "a,an" -> multiple words
        words = [w.strip() for w in word_part.split(',')]
        
        # Rest is pos and level info
        info_text = ' '.join(parts[1:])
        
        # Strategy: Split by comma, track accumulated POS until we hit a level
        pos_level_pairs = []
        accumulated_pos = []
        
        segments = [s.strip() for s in info_text.split(',')]
        
        for segment in segments:
            # Check if this segment contains a level
            level_match = re.search(r'\b([ABC][12])\b', segment)
            
            if level_match:
                level = level_match.group(1)
                # Extract pos before the level (if any)
                pos_part = segment[:level_match.start()].strip()
                
                if pos_part:
                    accumulated_pos.append(pos_part)
                
                # Assign this level to all accumulated POS
                for pos in accumulated_pos:
                    pos_level_pairs.append((pos, level))
                
                # Reset for next group
                accumulated_pos = []
            else:
                # No level in this segment, just accumulate the POS
                accumulated_pos.append(segment)
        
        # Create results for each word with each pos/level combination
        results = []
        for word in words:
            for pos, level in pos_level_pairs:
                results.append((word, pos, level))
        
        return results
    
    def import_words_from_csv(self, csv_file, level_filter=''):
        """
        Import words from Oxford CSV file.
        
        Format: "word pos level" or "word pos1 level1, pos2 level2"
        Examples:
        - "about prep., adv. A1"
        - "account n. B1, v. B2"
        - "abandon v. B2"
        """
        imported = 0
        skipped = 0
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                if not line:
                    continue
                
                # Parse the line
                parsed = self.parse_oxford_line(line)
                
                if not parsed:
                    self.stdout.write(self.style.WARNING(
                        f'Line {line_num}: Could not parse "{line}"'
                    ))
                    continue
                
                # Create Word entries for each word/pos/level combination
                for word_text, pos, cefr_level in parsed:
                    word_text = word_text.lower().strip()
                    pos = pos.strip()
                    cefr_level = cefr_level.strip().upper()
                    
                    # Skip if level filter doesn't match
                    if level_filter and cefr_level != level_filter:
                        continue
                    
                    if not word_text or not cefr_level:
                        continue
                    
                    # Check if this exact word+pos combination exists
                    existing = Word.objects.filter(
                        text=word_text,
                        pos=pos,
                        cefr_level=cefr_level
                    ).first()
                    
                    if existing:
                        skipped += 1
                        continue
                    
                    # Map pos abbreviations to full names
                    pos_map = {
                        'n.': 'noun',
                        'v.': 'verb',
                        'adj.': 'adjective',
                        'adv.': 'adverb',
                        'prep.': 'preposition',
                        'pron.': 'pronoun',
                        'conj.': 'conjunction',
                        'det.': 'determiner',
                        'modal v.': 'modal verb',
                        'auxiliary v.': 'auxiliary verb',
                        'exclam.': 'exclamation',
                        'number': 'number',
                        'indefinite article': 'article',
                    }
                    
                    pos_full = pos_map.get(pos, pos)
                    
                    # Create or get word (skip duplicates)
                    word, created = Word.objects.get_or_create(
                        text=word_text,
                        pos=pos_full,
                        cefr_level=cefr_level,
                        defaults={
                            'meaning_vi': '',  # Will be filled later
                            'frequency_rank': imported + 1,  # Use import order as frequency
                        }
                    )
                    
                    if created:
                        imported += 1
                    else:
                        skipped += 1
                    
                    if (imported + skipped) % 100 == 0:
                        self.stdout.write(f'Processed {imported + skipped} words (imported: {imported}, skipped: {skipped})...')
        
        self.stdout.write(self.style.SUCCESS(
            f'\nImport complete: {imported} words imported, {skipped} skipped'
        ))
        
        return imported

    def create_flashcard_decks(self):
        """Create flashcard decks for each CEFR level"""
        
        # Get or create admin user for official decks
        admin_user = User.objects.filter(is_staff=True).first()
        if not admin_user:
            self.stdout.write(self.style.WARNING(
                'No admin user found. Creating decks with first user.'
            ))
            admin_user = User.objects.first()
        
        if not admin_user:
            self.stdout.write(self.style.ERROR(
                'No users found. Please create a user first.'
            ))
            return

        levels = [
            ('A1', 'Beginner', '📗'),
            ('A2', 'Elementary', '📘'),
            ('B1', 'Intermediate', '📙'),
            ('B2', 'Upper-Intermediate', '📕'),
            ('C1', 'Advanced', '📚'),
        ]

        for level_code, level_name, icon in levels:
            # Count words for this level
            word_count = Word.objects.filter(cefr_level=level_code).count()
            
            if word_count == 0:
                self.stdout.write(self.style.WARNING(
                    f'No words found for level {level_code}, skipping deck'
                ))
                continue

            # Create or get deck
            deck, created = FlashcardDeck.objects.get_or_create(
                name=f'Oxford {level_code} - {level_name}',
                defaults={
                    'description': f'Essential vocabulary for {level_name} ({level_code}) learners. {word_count} words from Oxford word list.',
                    'category': 'oxford',
                    'level': level_code,
                    'is_public': True,
                    'is_official': True,
                    'icon': icon,
                    'created_by': admin_user,
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(
                    f'Created deck: {deck.name}'
                ))
                
                # Create flashcards for words in this level
                words = Word.objects.filter(cefr_level=level_code)[:100]  # Limit to 100 per deck initially
                
                for i, word in enumerate(words):
                    Flashcard.objects.create(
                        word=word,
                        deck=deck,
                        front_text=word.text,
                        front_type='word',
                        back_text=word.meaning_vi,
                        back_example=word.example_en if word.example_en else '',
                        back_note=f'IPA: {word.ipa}' if word.ipa else '',
                        difficulty=word.difficulty_score,
                        tags=f'{word.pos}, {word.cefr_level}',
                        order=i,
                    )
                
                self.stdout.write(self.style.SUCCESS(
                    f'Created {words.count()} flashcards for {deck.name}'
                ))
            else:
                self.stdout.write(self.style.WARNING(
                    f'Deck already exists: {deck.name}'
                ))

    def create_sample_data(self):
        """Create sample words and decks for testing"""
        
        self.stdout.write('Creating sample vocabulary data...')
        
        # Get or create admin user
        admin_user = User.objects.filter(is_staff=True).first()
        if not admin_user:
            admin_user = User.objects.create_user(
                username='admin',
                email='admin@example.com',
                password='admin123',
                is_staff=True,
            )
            self.stdout.write(self.style.SUCCESS('Created admin user'))

        # Sample words (A1 level)
        sample_words = [
            {
                'text': 'hello',
                'pos': 'exclamation',
                'cefr_level': 'A1',
                'meaning_vi': 'xin chào',
                'example_en': 'Hello! How are you?',
                'ipa': '/həˈləʊ/',
                'frequency_rank': 1,
            },
            {
                'text': 'book',
                'pos': 'noun',
                'cefr_level': 'A1',
                'meaning_vi': 'sách',
                'example_en': 'I am reading a book.',
                'ipa': '/bʊk/',
                'frequency_rank': 2,
            },
            {
                'text': 'study',
                'pos': 'verb',
                'cefr_level': 'A1',
                'meaning_vi': 'học, nghiên cứu',
                'example_en': 'I study English every day.',
                'ipa': '/ˈstʌdi/',
                'frequency_rank': 3,
            },
            {
                'text': 'decision',
                'pos': 'noun',
                'cefr_level': 'B1',
                'meaning_vi': 'quyết định',
                'example_en': 'Making decisions can be difficult.',
                'ipa': '/dɪˈsɪʒn/',
                'collocations': 'make a decision, reach a decision',
                'frequency_rank': 150,
            },
            {
                'text': 'collaborate',
                'pos': 'verb',
                'cefr_level': 'B2',
                'meaning_vi': 'cộng tác, hợp tác',
                'example_en': 'We collaborate with international partners.',
                'ipa': '/kəˈlæbəreɪt/',
                'synonyms': 'cooperate, work together',
                'frequency_rank': 500,
            },
        ]

        # Create words
        created_words = []
        for word_data in sample_words:
            word, created = Word.objects.get_or_create(
                text=word_data['text'],
                defaults=word_data
            )
            if created:
                created_words.append(word)
                self.stdout.write(f'Created word: {word.text}')

        # Create sample deck
        deck, created = FlashcardDeck.objects.get_or_create(
            name='Sample Vocabulary',
            defaults={
                'description': 'Sample flashcard deck for testing',
                'category': 'oxford',
                'level': 'mixed',
                'is_public': True,
                'is_official': True,
                'icon': '🎯',
                'created_by': admin_user,
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'Created deck: {deck.name}'))
            
            # Create flashcards
            for i, word in enumerate(created_words):
                Flashcard.objects.create(
                    word=word,
                    deck=deck,
                    front_text=word.text,
                    front_type='word',
                    back_text=word.meaning_vi,
                    back_example=word.example_en,
                    back_note=f'IPA: {word.ipa}' if word.ipa else '',
                    difficulty=word.difficulty_score,
                    tags=f'{word.pos}, {word.cefr_level}',
                    order=i,
                )
            
            self.stdout.write(self.style.SUCCESS(
                f'Created {len(created_words)} flashcards'
            ))

        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
