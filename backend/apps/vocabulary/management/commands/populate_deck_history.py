"""
Management command to populate DeckStudyHistory from existing StudySessions.
Run after migration to backfill data for existing users.

Usage:
    python manage.py populate_deck_history
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from apps.vocabulary.models import StudySession
from apps.vocabulary.models_study_tracking import DeckStudyHistory

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate DeckStudyHistory from existing StudySessions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write(self.style.WARNING('=' * 70))
        self.stdout.write(self.style.WARNING('  Populating DeckStudyHistory from StudySessions'))
        self.stdout.write(self.style.WARNING('=' * 70))
        
        if dry_run:
            self.stdout.write(self.style.NOTICE('🔍 DRY RUN MODE - No data will be created\n'))
        
        # Get all sessions grouped by user and deck
        sessions = StudySession.objects.filter(
            deck__isnull=False
        ).select_related('user', 'deck').order_by('user', 'deck', 'started_at')
        
        if not sessions.exists():
            self.stdout.write(self.style.WARNING('⚠️  No sessions found with deck assignments'))
            return
        
        self.stdout.write(f'📊 Found {sessions.count()} sessions to process\n')
        
        # Group by user and deck
        user_deck_sessions = {}
        for session in sessions:
            key = (session.user.id, session.deck.id)
            if key not in user_deck_sessions:
                user_deck_sessions[key] = []
            user_deck_sessions[key].append(session)
        
        created_count = 0
        updated_count = 0
        error_count = 0
        
        for (user_id, deck_id), session_list in user_deck_sessions.items():
            try:
                user = session_list[0].user
                deck = session_list[0].deck
                
                # Calculate aggregated stats
                total_sessions = len(session_list)
                total_cards = sum(s.cards_studied for s in session_list)
                total_time = sum(s.duration_minutes for s in session_list)
                first_studied = min(s.started_at for s in session_list)
                last_studied = max(s.started_at for s in session_list)
                
                self.stdout.write(
                    f'  Processing: {user.username} - {deck.name} '
                    f'({total_sessions} sessions, {total_cards} cards)'
                )
                
                if not dry_run:
                    # Create or update history
                    history, created = DeckStudyHistory.objects.get_or_create(
                        user=user,
                        deck=deck,
                        defaults={
                            'total_sessions': total_sessions,
                            'total_cards_studied': total_cards,
                            'total_time_minutes': total_time,
                            'first_studied_at': first_studied,
                        }
                    )
                    
                    if not created:
                        # Update existing
                        history.total_sessions = total_sessions
                        history.total_cards_studied = total_cards
                        history.total_time_minutes = total_time
                        if first_studied < history.first_studied_at:
                            history.first_studied_at = first_studied
                        history.save()
                    
                    # Update progress stats
                    history.update_progress()
                    
                    if created:
                        created_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'    ✅ Created: {history.progress_percentage}% complete')
                        )
                    else:
                        updated_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'    🔄 Updated: {history.progress_percentage}% complete')
                        )
                else:
                    self.stdout.write(
                        self.style.NOTICE(
                            f'    Would create/update: '
                            f'{total_sessions} sessions, {total_cards} cards, {total_time} min'
                        )
                    )
                    created_count += 1
                
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'    ❌ Error: {str(e)}')
                )
        
        # Summary
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('📈 SUMMARY'))
        self.stdout.write('=' * 70)
        
        if dry_run:
            self.stdout.write(f'  Would create: {created_count} histories')
        else:
            self.stdout.write(self.style.SUCCESS(f'  ✅ Created: {created_count} histories'))
            self.stdout.write(self.style.SUCCESS(f'  🔄 Updated: {updated_count} histories'))
        
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'  ❌ Errors: {error_count}'))
        
        self.stdout.write(self.style.SUCCESS('\n✨ Done!'))
        
        if dry_run:
            self.stdout.write(
                self.style.NOTICE('\n💡 Run without --dry-run to actually create the data')
            )
