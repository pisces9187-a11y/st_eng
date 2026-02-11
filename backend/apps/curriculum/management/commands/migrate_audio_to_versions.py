"""
Management command to migrate existing AudioSource records to AudioVersion.

This creates Version 1 for each existing AudioSource and activates it.

Usage:
    python manage.py migrate_audio_to_versions
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from apps.curriculum.models import AudioSource, AudioVersion

class Command(BaseCommand):
    help = 'Migrate existing AudioSource records to AudioVersion system'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔄 Starting audio version migration...'))
        
        # Get all AudioSources
        audio_sources = AudioSource.objects.select_related('phoneme').all()
        
        if not audio_sources.exists():
            self.stdout.write(self.style.WARNING('No AudioSource records found. Nothing to migrate.'))
            return
        
        self.stdout.write(f'Found {audio_sources.count()} AudioSource records')
        
        created_count = 0
        skipped_count = 0
        
        with transaction.atomic():
            for audio in audio_sources:
                # Check if version already exists
                existing_version = AudioVersion.objects.filter(
                    phoneme=audio.phoneme,
                    audio_source=audio
                ).first()
                
                if existing_version:
                    self.stdout.write(
                        f'  ⏭️  Skipped /{audio.phoneme.ipa_symbol}/ - '
                        f'version already exists (v{existing_version.version_number})'
                    )
                    skipped_count += 1
                    continue
                
                # Create version 1 for this audio
                version = AudioVersion.objects.create(
                    phoneme=audio.phoneme,
                    audio_source=audio,
                    change_reason='Migrated from existing AudioSource',
                    usage_count=0
                )
                
                # Activate if this is the preferred audio
                if audio.phoneme.preferred_audio_source == audio:
                    version.is_active = True
                    version.save(update_fields=['is_active'])
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✅ Created and activated /{audio.phoneme.ipa_symbol}/ v{version.version_number}'
                        )
                    )
                else:
                    self.stdout.write(
                        f'  ✓ Created /{audio.phoneme.ipa_symbol}/ v{version.version_number} (inactive)'
                    )
                
                created_count += 1
        
        # Summary
        self.stdout.write(self.style.SUCCESS(f'\n✅ Migration complete!'))
        self.stdout.write(f'   Created: {created_count} versions')
        self.stdout.write(f'   Skipped: {skipped_count} (already exist)')
        self.stdout.write(f'   Total: {created_count + skipped_count}')
