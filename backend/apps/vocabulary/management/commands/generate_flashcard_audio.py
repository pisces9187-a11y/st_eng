"""
Management command to generate audio for all flashcard words.

Usage:
    python manage.py generate_flashcard_audio --voice us_male --speed normal --limit 100
    python manage.py generate_flashcard_audio --level A1 --voice us_female
    python manage.py generate_flashcard_audio --all
"""

from django.core.management.base import BaseCommand
from django.db.models import Q
from apps.vocabulary.models import Word
from services.tts_flashcard_service import get_tts_service
import time


class Command(BaseCommand):
    help = 'Generate TTS audio for flashcard words'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--voice',
            type=str,
            default='us_male',
            choices=['us_male', 'us_female', 'uk_male', 'uk_female'],
            help='Voice to use for generation'
        )
        
        parser.add_argument(
            '--speed',
            type=str,
            default='normal',
            choices=['slow', 'normal', 'fast'],
            help='Speed to use for generation'
        )
        
        parser.add_argument(
            '--level',
            type=str,
            choices=['A1', 'A2', 'B1', 'B2', 'C1'],
            help='Generate only for specific CEFR level'
        )
        
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit number of words to generate'
        )
        
        parser.add_argument(
            '--all',
            action='store_true',
            help='Generate for all words (ignore limit)'
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force regeneration even if audio exists'
        )
    
    def handle(self, *args, **options):
        voice = options['voice']
        speed = options['speed']
        level = options.get('level')
        limit = options.get('limit')
        generate_all = options['all']
        force = options['force']
        
        # Get TTS service
        tts_service = get_tts_service()
        
        # Build query
        queryset = Word.objects.all()
        
        if level:
            queryset = queryset.filter(cefr_level=level)
        
        if not generate_all and limit:
            queryset = queryset[:limit]
        
        total_words = queryset.count()
        
        self.stdout.write(self.style.SUCCESS(
            f'\n🎵 Flashcard Audio Generation'
        ))
        self.stdout.write(f'='*60)
        self.stdout.write(f'Voice: {voice}')
        self.stdout.write(f'Speed: {speed}')
        if level:
            self.stdout.write(f'Level: {level}')
        self.stdout.write(f'Total words: {total_words}')
        self.stdout.write(f'Force regenerate: {force}')
        self.stdout.write(f'='*60)
        
        # Generate audio
        success_count = 0
        failed_count = 0
        skipped_count = 0
        start_time = time.time()
        
        for i, word in enumerate(queryset, 1):
            # Check if audio exists
            if not force:
                existing_url = tts_service.get_audio_url(
                    word.text,
                    tts_service.VOICES[voice],
                    speed
                )
                if existing_url:
                    skipped_count += 1
                    if i % 50 == 0:
                        self.stdout.write(f'Progress: {i}/{total_words} ({skipped_count} skipped)')
                    continue
            
            # Generate audio
            try:
                audio_url = tts_service.generate_audio(
                    word.text,
                    voice,
                    speed,
                    force_regenerate=force
                )
                
                if audio_url:
                    success_count += 1
                    self.stdout.write(
                        f'✓ [{i}/{total_words}] {word.text} -> {audio_url}'
                    )
                else:
                    failed_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'✗ [{i}/{total_words}] {word.text} - Failed')
                    )
                
                # Small delay to avoid rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                failed_count += 1
                self.stdout.write(
                    self.style.ERROR(f'✗ [{i}/{total_words}] {word.text} - Error: {e}')
                )
        
        # Summary
        elapsed_time = time.time() - start_time
        
        self.stdout.write(f'\n{"="*60}')
        self.stdout.write(self.style.SUCCESS('✅ Audio Generation Complete!'))
        self.stdout.write(f'{"="*60}')
        self.stdout.write(f'Total words: {total_words}')
        self.stdout.write(self.style.SUCCESS(f'Success: {success_count}'))
        self.stdout.write(self.style.WARNING(f'Skipped: {skipped_count}'))
        self.stdout.write(self.style.ERROR(f'Failed: {failed_count}'))
        self.stdout.write(f'Time elapsed: {elapsed_time:.1f} seconds')
        self.stdout.write(f'Average: {elapsed_time/max(success_count, 1):.2f} sec/word')
        
        # Storage stats
        stats = tts_service.get_storage_stats()
        self.stdout.write(f'\n📊 Storage Statistics:')
        self.stdout.write(f'   Total audio files: {stats["total_files"]}')
        self.stdout.write(f'   Total size: {stats["total_size_mb"]} MB')
        self.stdout.write(f'{"="*60}\n')
