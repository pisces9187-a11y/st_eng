"""
Management command to auto-generate minimal pairs based on phoneme similarity.

Usage:
    python manage.py auto_generate_minimal_pairs --phoneme1 p --phoneme2 b
    python manage.py auto_generate_minimal_pairs --auto --max-pairs 50
    python manage.py auto_generate_minimal_pairs --suggest (preview only)
"""

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from apps.curriculum.models import Phoneme, PhonemeWord, MinimalPair
import difflib


class Command(BaseCommand):
    help = 'Auto-generate minimal pairs from phoneme words based on similarity'

    def add_arguments(self, parser):
        parser.add_argument(
            '--phoneme1',
            type=str,
            help='First phoneme IPA symbol (e.g., "p")'
        )
        parser.add_argument(
            '--phoneme2',
            type=str,
            help='Second phoneme IPA symbol (e.g., "b")'
        )
        parser.add_argument(
            '--auto',
            action='store_true',
            help='Auto-detect all phoneme pairs and generate'
        )
        parser.add_argument(
            '--max-pairs',
            type=int,
            default=50,
            help='Maximum number of pairs to generate (default: 50)'
        )
        parser.add_argument(
            '--suggest',
            action='store_true',
            help='Only suggest pairs without creating them'
        )
        parser.add_argument(
            '--min-similarity',
            type=float,
            default=0.7,
            help='Minimum word similarity score (0-1, default: 0.7)'
        )

    def handle(self, *args, **options):
        phoneme1_ipa = options.get('phoneme1')
        phoneme2_ipa = options.get('phoneme2')
        auto = options.get('auto')
        max_pairs = options.get('max_pairs')
        suggest_only = options.get('suggest')
        min_similarity = options.get('min_similarity')

        if auto:
            self.auto_generate_all(max_pairs, suggest_only, min_similarity)
        elif phoneme1_ipa and phoneme2_ipa:
            self.generate_for_pair(
                phoneme1_ipa, phoneme2_ipa, suggest_only, min_similarity
            )
        else:
            raise CommandError(
                'Please provide either --phoneme1 and --phoneme2, or --auto'
            )

    def auto_generate_all(self, max_pairs, suggest_only, min_similarity):
        """Auto-detect and generate pairs for all similar phonemes"""
        self.stdout.write(
            self.style.SUCCESS('📊 Analyzing phonemes for similarity...')
        )

        phonemes = Phoneme.objects.filter(is_active=True)
        pair_candidates = []

        # Find similar phoneme pairs
        for i, p1 in enumerate(phonemes):
            for p2 in phonemes[i+1:]:
                similarity = self.calculate_phoneme_similarity(p1, p2)
                if similarity >= 0.5:  # Similar enough to be confusing
                    pairs = self.find_minimal_pairs(p1, p2, min_similarity)
                    if pairs:
                        for pair in pairs:
                            pair_candidates.append({
                                'phoneme1': p1,
                                'phoneme2': p2,
                                'pair': pair,
                                'similarity': similarity,
                                'score': pair['similarity'] * similarity
                            })

        # Sort by score (best pairs first)
        pair_candidates.sort(key=lambda x: x['score'], reverse=True)

        # Limit to max_pairs
        top_pairs = pair_candidates[:max_pairs]

        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎯 Found {len(pair_candidates)} potential minimal pairs'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'📝 Showing top {len(top_pairs)} pairs:\n'
            )
        )

        # Display pairs
        for i, candidate in enumerate(top_pairs, 1):
            p1 = candidate['phoneme1']
            p2 = candidate['phoneme2']
            pair = candidate['pair']
            
            self.stdout.write(
                f"{i}. /{p1.ipa_symbol}/ vs /{p2.ipa_symbol}/: "
                f"{pair['word1']} ({pair['ipa1']}) ↔ "
                f"{pair['word2']} ({pair['ipa2']}) "
                f"[score: {candidate['score']:.2f}]"
            )

        if suggest_only:
            self.stdout.write(
                self.style.WARNING(
                    '\n💡 Suggestion mode - no pairs created. '
                    'Run without --suggest to create them.'
                )
            )
            return

        # Confirm before creating
        if not self.confirm_action(
            f'\nCreate these {len(top_pairs)} minimal pairs in database?'
        ):
            self.stdout.write(self.style.WARNING('Cancelled.'))
            return

        # Create pairs
        created_count = 0
        skipped_count = 0

        for candidate in top_pairs:
            p1 = candidate['phoneme1']
            p2 = candidate['phoneme2']
            pair = candidate['pair']
            
            # Check if pair already exists
            exists = MinimalPair.objects.filter(
                Q(phoneme_1=p1, phoneme_2=p2, word_1=pair['word1'], word_2=pair['word2']) |
                Q(phoneme_1=p2, phoneme_2=p1, word_1=pair['word2'], word_2=pair['word1'])
            ).exists()
            
            if exists:
                skipped_count += 1
                continue
            
            # Create minimal pair
            MinimalPair.objects.create(
                phoneme_1=p1,
                phoneme_2=p2,
                word_1=pair['word1'],
                word_2=pair['word2'],
                ipa_1=pair['ipa1'],
                ipa_2=pair['ipa2'],
                meaning_1=pair.get('meaning1', ''),
                meaning_2=pair.get('meaning2', ''),
                difficulty_level=self.calculate_difficulty(p1, p2),
                difference_note=self.generate_difference_note(p1, p2),
                is_verified=False
            )
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Created {created_count} minimal pairs'
            )
        )
        self.stdout.write(
            self.style.WARNING(
                f'⏭️  Skipped {skipped_count} (already exist)'
            )
        )

    def generate_for_pair(self, phoneme1_ipa, phoneme2_ipa, suggest_only, min_similarity):
        """Generate minimal pairs for a specific phoneme pair"""
        try:
            phoneme1 = Phoneme.objects.get(ipa_symbol=phoneme1_ipa)
            phoneme2 = Phoneme.objects.get(ipa_symbol=phoneme2_ipa)
        except Phoneme.DoesNotExist as e:
            raise CommandError(f'Phoneme not found: {e}')

        self.stdout.write(
            self.style.SUCCESS(
                f'🔍 Finding minimal pairs for /{phoneme1.ipa_symbol}/ vs /{phoneme2.ipa_symbol}/...'
            )
        )

        pairs = self.find_minimal_pairs(phoneme1, phoneme2, min_similarity)

        if not pairs:
            self.stdout.write(
                self.style.WARNING(
                    f'❌ No minimal pairs found for /{phoneme1.ipa_symbol}/ vs /{phoneme2.ipa_symbol}/'
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Found {len(pairs)} potential minimal pairs:\n'
            )
        )

        for i, pair in enumerate(pairs, 1):
            self.stdout.write(
                f"{i}. {pair['word1']} ({pair['ipa1']}) ↔ "
                f"{pair['word2']} ({pair['ipa2']}) "
                f"[similarity: {pair['similarity']:.2f}]"
            )

        if suggest_only:
            self.stdout.write(
                self.style.WARNING(
                    '\n💡 Suggestion mode - no pairs created. '
                    'Run without --suggest to create them.'
                )
            )
            return

        if not self.confirm_action('\nCreate these pairs in database?'):
            self.stdout.write(self.style.WARNING('Cancelled.'))
            return

        # Create pairs
        created_count = 0
        skipped_count = 0

        for pair in pairs:
            # Check if pair already exists
            exists = MinimalPair.objects.filter(
                Q(phoneme_1=phoneme1, phoneme_2=phoneme2, 
                  word_1=pair['word1'], word_2=pair['word2']) |
                Q(phoneme_1=phoneme2, phoneme_2=phoneme1, 
                  word_1=pair['word2'], word_2=pair['word1'])
            ).exists()
            
            if exists:
                skipped_count += 1
                continue
            
            # Create minimal pair
            MinimalPair.objects.create(
                phoneme_1=phoneme1,
                phoneme_2=phoneme2,
                word_1=pair['word1'],
                word_2=pair['word2'],
                ipa_1=pair['ipa1'],
                ipa_2=pair['ipa2'],
                meaning_1=pair.get('meaning1', ''),
                meaning_2=pair.get('meaning2', ''),
                difficulty_level=self.calculate_difficulty(phoneme1, phoneme2),
                difference_note=self.generate_difference_note(phoneme1, phoneme2),
                is_verified=False
            )
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Created {created_count} minimal pairs'
            )
        )
        if skipped_count:
            self.stdout.write(
                self.style.WARNING(
                    f'⏭️  Skipped {skipped_count} (already exist)'
                )
            )

    def find_minimal_pairs(self, phoneme1, phoneme2, min_similarity=0.7):
        """
        Find minimal pairs between two phonemes by comparing their example words.
        
        A minimal pair is two words that differ by only one phoneme.
        """
        words1 = PhonemeWord.objects.filter(phoneme=phoneme1)
        words2 = PhonemeWord.objects.filter(phoneme=phoneme2)
        
        # Check if we have data
        if not words1.exists():
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️  No example words found for /{phoneme1.ipa_symbol}/. '
                    f'Please add PhonemeWord entries for this phoneme.'
                )
            )
        
        if not words2.exists():
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️  No example words found for /{phoneme2.ipa_symbol}/. '
                    f'Please add PhonemeWord entries for this phoneme.'
                )
            )
        
        pairs = []
        
        for w1 in words1:
            for w2 in words2:
                # Calculate word similarity
                similarity = difflib.SequenceMatcher(
                    None, 
                    w1.word.lower(), 
                    w2.word.lower()
                ).ratio()
                
                # Check if words are similar enough (minimal pair condition)
                if similarity >= min_similarity:
                    # Words should have similar length (differ by 1-2 chars max)
                    len_diff = abs(len(w1.word) - len(w2.word))
                    if len_diff <= 1:
                        pairs.append({
                            'word1': w1.word,
                            'word2': w2.word,
                            'ipa1': w1.ipa_transcription or f"/{phoneme1.ipa_symbol}/",
                            'ipa2': w2.ipa_transcription or f"/{phoneme2.ipa_symbol}/",
                            'meaning1': w1.meaning_vi or '',
                            'meaning2': w2.meaning_vi or '',
                            'similarity': similarity
                        })
        
        # Sort by similarity (best matches first)
        pairs.sort(key=lambda x: x['similarity'], reverse=True)
        
        return pairs

    def calculate_phoneme_similarity(self, phoneme1, phoneme2):
        """
        Calculate similarity between two phonemes based on features.
        Returns score 0-1.
        """
        score = 0.0
        
        # Same type (vowel vs consonant)
        if phoneme1.phoneme_type == phoneme2.phoneme_type:
            score += 0.3
        
        # Same voicing
        if phoneme1.voicing == phoneme2.voicing:
            score += 0.2
        
        # Similar mouth position
        if phoneme1.mouth_position == phoneme2.mouth_position:
            score += 0.3
        
        # Similar Vietnamese approximation (if available)
        if (phoneme1.vietnamese_approximation and 
            phoneme2.vietnamese_approximation):
            similarity = difflib.SequenceMatcher(
                None,
                phoneme1.vietnamese_approximation.lower(),
                phoneme2.vietnamese_approximation.lower()
            ).ratio()
            score += similarity * 0.2
        
        return score

    def calculate_difficulty(self, phoneme1, phoneme2):
        """Calculate difficulty level for a minimal pair"""
        # Vowel vs vowel = easier
        if phoneme1.phoneme_type == 'vowel' and phoneme2.phoneme_type == 'vowel':
            return 'intermediate'
        
        # Consonant vs consonant with same features = harder
        if (phoneme1.phoneme_type == 'consonant' and 
            phoneme2.phoneme_type == 'consonant'):
            if phoneme1.voicing == phoneme2.voicing:
                return 'advanced'
            else:
                return 'intermediate'
        
        return 'beginner'

    def generate_difference_note(self, phoneme1, phoneme2):
        """Generate a note explaining the difference between phonemes"""
        notes = []
        
        if phoneme1.voicing != phoneme2.voicing:
            notes.append(
                f"/{phoneme1.ipa_symbol}/ is {phoneme1.voicing or 'unvoiced'}, "
                f"/{phoneme2.ipa_symbol}/ is {phoneme2.voicing or 'unvoiced'}"
            )
        
        if phoneme1.mouth_position != phoneme2.mouth_position:
            notes.append(
                f"Different mouth positions: {phoneme1.mouth_position or 'N/A'} vs "
                f"{phoneme2.mouth_position or 'N/A'}"
            )
        
        if phoneme1.vietnamese_approximation and phoneme2.vietnamese_approximation:
            notes.append(
                f"Vietnamese: {phoneme1.vietnamese_approximation} vs "
                f"{phoneme2.vietnamese_approximation}"
            )
        
        return '. '.join(notes) if notes else 'Practice listening carefully to distinguish these sounds.'

    def confirm_action(self, message):
        """Ask for user confirmation"""
        response = input(f"{message} (y/n): ")
        return response.lower() in ['y', 'yes']
