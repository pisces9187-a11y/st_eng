#!/usr/bin/env python
"""
Project Organization Migration Script

This script helps migrate files to the new organized structure.
Run with: python scripts/migrate_organization.py --dry-run (to preview)
Run with: python scripts/migrate_organization.py --execute (to actually move files)
"""

import os
import shutil
import argparse
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent

# Migration mappings
TEMPLATE_MIGRATIONS = {
    # Curriculum app templates
    'backend/templates/pages/pronunciation_discovery.html': 
        'backend/templates/curriculum/pronunciation/discovery.html',
    'backend/templates/pages/pronunciation_learning.html': 
        'backend/templates/curriculum/pronunciation/learning.html',
    'backend/templates/pages/pronunciation_lesson.html': 
        'backend/templates/curriculum/pronunciation/lesson_detail.html',
    'backend/templates/pages/pronunciation_library.html': 
        'backend/templates/curriculum/pronunciation/library.html',
    'backend/templates/pages/pronunciation_progress.html': 
        'backend/templates/curriculum/pronunciation/progress.html',
    'backend/templates/pages/pronunciation_discrimination.html': 
        'backend/templates/curriculum/pronunciation/discrimination.html',
    'backend/templates/pages/pronunciation_production.html': 
        'backend/templates/curriculum/pronunciation/production.html',
    
    'backend/templates/pages/phoneme_chart.html': 
        'backend/templates/curriculum/phoneme/chart.html',
    'backend/templates/pages/phoneme_detail.html': 
        'backend/templates/curriculum/phoneme/detail.html',
    
    'backend/templates/pages/minimal_pair_practice.html': 
        'backend/templates/curriculum/minimal_pair/practice.html',
    
    'backend/templates/pages/discrimination_start.html': 
        'backend/templates/curriculum/discrimination/start.html',
    'backend/templates/pages/discrimination_quiz.html': 
        'backend/templates/curriculum/discrimination/quiz.html',
    'backend/templates/pages/discrimination_results.html': 
        'backend/templates/curriculum/discrimination/results.html',
    
    'backend/templates/pages/production_record.html': 
        'backend/templates/curriculum/production/record.html',
    'backend/templates/pages/production_history.html': 
        'backend/templates/curriculum/production/history.html',
    
    'backend/templates/pages/lesson_library.html': 
        'backend/templates/curriculum/lesson/library.html',
    'backend/templates/pages/lesson_player.html': 
        'backend/templates/curriculum/lesson/player.html',
    
    # Study app templates
    'backend/templates/pages/learning_hub_dashboard.html': 
        'backend/templates/study/dashboard.html',
    
    # Public templates
    'backend/templates/pages/home.html': 
        'backend/templates/public/home.html',
}

DOC_MIGRATIONS = {
    # Curriculum docs
    'PRONUNCIATION_LEARNING_IMPLEMENTATION.md': 
        'docs/curriculum/PRONUNCIATION_LEARNING_IMPLEMENTATION.md',
    'PRONUNCIATION_LESSON_ENHANCEMENT_PROPOSAL.md': 
        'docs/curriculum/PRONUNCIATION_LESSON_ENHANCEMENT_PROPOSAL.md',
    'QUICK_WINS_IMPLEMENTATION_SUMMARY.md': 
        'docs/curriculum/QUICK_WINS_IMPLEMENTATION_SUMMARY.md',
    'TEACHER_DASHBOARD_DESIGN.md': 
        'docs/curriculum/TEACHER_DASHBOARD_DESIGN.md',
    'TEACHER_DASHBOARD_IMPLEMENTATION.md': 
        'docs/curriculum/TEACHER_DASHBOARD_IMPLEMENTATION.md',
    'HUONG_DAN_TICH_HOP.md': 
        'docs/curriculum/HUONG_DAN_TICH_HOP.md',
    
    # Audio docs
    'AUDIO_VERSIONING_DESIGN.md': 
        'docs/curriculum/audio/AUDIO_VERSIONING_DESIGN.md',
    'AUDIO_VERSIONING_IMPLEMENTATION.md': 
        'docs/curriculum/audio/AUDIO_VERSIONING_IMPLEMENTATION.md',
    'EDGE_TTS_INTEGRATION_SUMMARY.md': 
        'docs/curriculum/audio/EDGE_TTS_INTEGRATION_SUMMARY.md',
    'EDGE_TTS_TEST_REPORT.md': 
        'docs/curriculum/audio/EDGE_TTS_TEST_REPORT.md',
    'EDGE_TTS_USAGE_GUIDE.md': 
        'docs/curriculum/audio/EDGE_TTS_USAGE_GUIDE.md',
    'MOCK_TTS_IMPLEMENTATION.md': 
        'docs/curriculum/audio/MOCK_TTS_IMPLEMENTATION.md',
    'MOCK_TTS_QUICK_REFERENCE.md': 
        'docs/curriculum/audio/MOCK_TTS_QUICK_REFERENCE.md',
    'TTS_GENERATION_GUIDE.md': 
        'docs/curriculum/audio/TTS_GENERATION_GUIDE.md',
    
    # Users docs
    'AUTH_LOADING_FIX.md': 
        'docs/users/AUTH_LOADING_FIX.md',
    'PROFILE_SETTINGS_TEST_GUIDE.md': 
        'docs/users/PROFILE_SETTINGS_TEST_GUIDE.md',
    'QUICK_FIX_PROFILE.md': 
        'docs/users/QUICK_FIX_PROFILE.md',
    
    # Standards
    'DEVELOPMENT_STANDARDS.md': 
        'docs/standards/DEVELOPMENT_STANDARDS.md',
    'DEVELOPMENT_WORKFLOW.md': 
        'docs/standards/DEVELOPMENT_WORKFLOW.md',
    'TEMPLATE_ARCHITECTURE.md': 
        'docs/standards/TEMPLATE_ARCHITECTURE.md',
    
    # Architecture
    'SYSTEM_ANALYSIS.md': 
        'docs/architecture/SYSTEM_ANALYSIS.md',
    'SYSTEM_GAP_ANALYSIS.md': 
        'docs/architecture/SYSTEM_GAP_ANALYSIS.md',
    'SITEMAP_ADMIN.md': 
        'docs/architecture/SITEMAP_ADMIN.md',
    'SITEMAP_PUBLIC.md': 
        'docs/architecture/SITEMAP_PUBLIC.md',
    'DAYS_6_10_ARCHITECTURE.md': 
        'docs/architecture/DAYS_6_10_ARCHITECTURE.md',
    
    # Requirements
    'DAYS_6_10_REQUIREMENTS.md': 
        'docs/requirements/DAYS_6_10_REQUIREMENTS.md',
    
    # Design
    'DAYS_6_10_UI_DESIGN.md': 
        'docs/design/DAYS_6_10_UI_DESIGN.md',
    
    # Implementation
    'IMPLEMENTATION_COMPLETE.md': 
        'docs/implementation/IMPLEMENTATION_COMPLETE.md',
    'IMPLEMENTATION_SUMMARY.md': 
        'docs/implementation/IMPLEMENTATION_SUMMARY.md',
    'TRIỂN_KHAI_HỎI_ĐÁP.md': 
        'docs/implementation/TRIỂN_KHAI_HỎI_ĐÁP.md',
    
    'IMPLEMENTATION_ROADMAP.md': 
        'docs/implementation/roadmap/IMPLEMENTATION_ROADMAP.md',
    'IMPLEMENTATION_ROADMAP_DETAILED.md': 
        'docs/implementation/roadmap/IMPLEMENTATION_ROADMAP_DETAILED.md',
    
    'PHASE_1_DAY_1_EXECUTION.md': 
        'docs/implementation/phases/PHASE_1_DAY_1_EXECUTION.md',
    'PHASE_1_IMPLEMENTATION.md': 
        'docs/implementation/phases/PHASE_1_IMPLEMENTATION.md',
    'PHASE_2_IMPLEMENTATION.md': 
        'docs/implementation/phases/PHASE_2_IMPLEMENTATION.md',
    'PHASE_3_IMPLEMENTATION.md': 
        'docs/implementation/phases/PHASE_3_IMPLEMENTATION.md',
    
    # Testing
    'BROWSER_TESTING_GUIDE.md': 
        'docs/testing/BROWSER_TESTING_GUIDE.md',
    'DAY_4_5_TESTING_GUIDE.md': 
        'docs/testing/DAY_4_5_TESTING_GUIDE.md',
    'DAY_4_5_TESTING_SUMMARY.md': 
        'docs/testing/DAY_4_5_TESTING_SUMMARY.md',
    'DAY_4_TESTING_COMPLETE.md': 
        'docs/testing/DAY_4_TESTING_COMPLETE.md',
    
    # Changelog
    'DAY_3_COMPLETION_SUMMARY.md': 
        'docs/changelog/2025-12-15_DAY_3.md',
    'DAY_4_COMPLETE_FINAL.md': 
        'docs/changelog/2025-12-16_DAY_4.md',
    'DAY_4_5_DOCUMENTATION_INDEX.md': 
        'docs/changelog/2025-12-17_DAY_4_5.md',
    'DAY_6_7_COMPLETE.md': 
        'docs/changelog/2025-12-18_DAY_6_7.md',
    'DAY_8_9_COMPLETE.md': 
        'docs/changelog/2025-12-19_DAY_8_9.md',
    'BUG_FIXES_DAY_4.md': 
        'docs/changelog/BUG_FIXES_DAY_4.md',
    'BUG_FIXES_TEACHER_DASHBOARD.md': 
        'docs/changelog/BUG_FIXES_TEACHER_DASHBOARD.md',
    'DETAILED_CODE_CHANGES.md': 
        'docs/changelog/DETAILED_CODE_CHANGES.md',
    'FIX_PHONEME_FILTER_ERROR.md': 
        'docs/changelog/FIX_PHONEME_FILTER_ERROR.md',
    'LEARNING_PAGE_FIX_COMPLETE.md': 
        'docs/changelog/LEARNING_PAGE_FIX_COMPLETE.md',
    'PHONEME_FILTER_FIX_COMPLETE.md': 
        'docs/changelog/PHONEME_FILTER_FIX_COMPLETE.md',
    'STATUS_DAY_4_5_COMPLETE.md': 
        'docs/changelog/STATUS_DAY_4_5_COMPLETE.md',
    
    # Project
    'COMPLETION_CHECKLIST.md': 
        'docs/project/COMPLETION_CHECKLIST.md',
    'FINAL_REPORT.md': 
        'docs/project/FINAL_REPORT.md',
    
    # Examples
    'example_integration.py': 
        'docs/examples/integration_example.py',
}

TEST_MIGRATIONS = {
    # Curriculum tests - models
    'backend/tests/test_pronunciation/test_audio_models.py': 
        'backend/tests/curriculum/models/test_audio.py',
    
    # Curriculum tests - API
    'backend/tests/test_curriculum/test_pronunciation_api.py': 
        'backend/tests/curriculum/api/test_pronunciation_api.py',
    'test_api_response.py': 
        'backend/tests/curriculum/api/test_api_response.py',
    'backend/test_pronunciation_api_quick.py': 
        'backend/tests/curriculum/api/test_pronunciation_api.py',
    
    # Curriculum tests - services
    'backend/tests/test_pronunciation/test_audio_service.py': 
        'backend/tests/curriculum/services/test_audio_service.py',
    'test_edge_tts_direct.py': 
        'backend/tests/curriculum/services/test_edge_tts.py',
    'backend/test_edge_tts.py': 
        'backend/tests/curriculum/services/test_edge_tts.py',
    'backend/test_mock_tts.py': 
        'backend/tests/curriculum/services/test_mock_tts.py',
    'backend/test_mock_tts_new.py': 
        'backend/tests/curriculum/services/test_mock_tts_new.py',
    
    # Curriculum tests - views
    'test_pronunciation_pages_render.py': 
        'backend/tests/curriculum/views/test_pronunciation_views.py',
    'test_render.py': 
        'backend/tests/curriculum/views/test_render.py',
    
    # Curriculum tests - integration
    'test_day4_comprehensive.py': 
        'backend/tests/curriculum/integration/test_day4_flow.py',
    'backend/test_audio_serving.py': 
        'backend/tests/curriculum/integration/test_audio_serving.py',
    
    # Users tests
    'backend/tests/test_users/test_phoneme_progress_stages.py': 
        'backend/tests/users/test_phoneme_progress_stages.py',
}

COMMAND_MIGRATIONS = {
    'generate_phoneme_tts.py': 
        'backend/apps/curriculum/management/commands/generate_phoneme_audio.py',
    'generate_phoneme_examples.py': 
        'backend/apps/curriculum/management/commands/generate_phoneme_examples.py',
    'regenerate_phoneme_audio.py': 
        'backend/apps/curriculum/management/commands/regenerate_audio.py',
    'check_mock_mode.py': 
        'backend/apps/curriculum/management/commands/check_audio_quality.py',
}

def create_directory(path):
    """Create directory if it doesn't exist."""
    path.parent.mkdir(parents=True, exist_ok=True)

def move_file(source, dest, dry_run=True):
    """Move file from source to destination."""
    source_path = PROJECT_ROOT / source
    dest_path = PROJECT_ROOT / dest
    
    if not source_path.exists():
        print(f"  ⚠️  Source not found: {source}")
        return False
    
    if dest_path.exists():
        print(f"  ⚠️  Destination already exists: {dest}")
        return False
    
    if dry_run:
        print(f"  📄 Would move: {source}")
        print(f"     → {dest}")
    else:
        create_directory(dest_path)
        shutil.move(str(source_path), str(dest_path))
        print(f"  ✅ Moved: {source}")
        print(f"     → {dest}")
    
    return True

def migrate_templates(dry_run=True):
    """Migrate template files."""
    print("\n📁 MIGRATING TEMPLATES...")
    print("=" * 80)
    
    success_count = 0
    for source, dest in TEMPLATE_MIGRATIONS.items():
        if move_file(source, dest, dry_run):
            success_count += 1
    
    print(f"\n✅ Templates: {success_count}/{len(TEMPLATE_MIGRATIONS)} would be moved")

def migrate_docs(dry_run=True):
    """Migrate documentation files."""
    print("\n📄 MIGRATING DOCUMENTATION...")
    print("=" * 80)
    
    success_count = 0
    for source, dest in DOC_MIGRATIONS.items():
        if move_file(source, dest, dry_run):
            success_count += 1
    
    print(f"\n✅ Docs: {success_count}/{len(DOC_MIGRATIONS)} would be moved")

def migrate_tests(dry_run=True):
    """Migrate test files."""
    print("\n🧪 MIGRATING TESTS...")
    print("=" * 80)
    
    success_count = 0
    for source, dest in TEST_MIGRATIONS.items():
        if move_file(source, dest, dry_run):
            success_count += 1
    
    print(f"\n✅ Tests: {success_count}/{len(TEST_MIGRATIONS)} would be moved")

def migrate_commands(dry_run=True):
    """Migrate management commands."""
    print("\n🛠️  MIGRATING MANAGEMENT COMMANDS...")
    print("=" * 80)
    
    success_count = 0
    for source, dest in COMMAND_MIGRATIONS.items():
        if move_file(source, dest, dry_run):
            success_count += 1
    
    print(f"\n✅ Commands: {success_count}/{len(COMMAND_MIGRATIONS)} would be moved")

def cleanup_temp_files(dry_run=True):
    """Cleanup temporary files."""
    print("\n🗑️  CLEANING UP TEMP FILES...")
    print("=" * 80)
    
    temp_patterns = [
        'temp_*.html',
        'test_*.html',
    ]
    
    for pattern in temp_patterns:
        for file_path in PROJECT_ROOT.glob(pattern):
            if dry_run:
                print(f"  🗑️  Would delete: {file_path.name}")
            else:
                file_path.unlink()
                print(f"  ✅ Deleted: {file_path.name}")

def main():
    parser = argparse.ArgumentParser(description='Migrate project to new organization')
    parser.add_argument('--execute', action='store_true', 
                       help='Actually execute the migration (default is dry-run)')
    parser.add_argument('--templates', action='store_true', 
                       help='Only migrate templates')
    parser.add_argument('--docs', action='store_true', 
                       help='Only migrate documentation')
    parser.add_argument('--tests', action='store_true', 
                       help='Only migrate tests')
    parser.add_argument('--commands', action='store_true', 
                       help='Only migrate management commands')
    parser.add_argument('--cleanup', action='store_true', 
                       help='Only cleanup temp files')
    
    args = parser.parse_args()
    
    dry_run = not args.execute
    
    if dry_run:
        print("\n" + "=" * 80)
        print("🔍 DRY RUN MODE - No files will be moved")
        print("Run with --execute to actually move files")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("⚠️  EXECUTE MODE - Files will be moved")
        print("=" * 80)
        response = input("\nAre you sure you want to proceed? (yes/no): ")
        if response.lower() != 'yes':
            print("Migration cancelled.")
            return
    
    # If no specific flags, do all
    do_all = not any([args.templates, args.docs, args.tests, 
                      args.commands, args.cleanup])
    
    if args.templates or do_all:
        migrate_templates(dry_run)
    
    if args.docs or do_all:
        migrate_docs(dry_run)
    
    if args.tests or do_all:
        migrate_tests(dry_run)
    
    if args.commands or do_all:
        migrate_commands(dry_run)
    
    if args.cleanup or do_all:
        cleanup_temp_files(dry_run)
    
    print("\n" + "=" * 80)
    if dry_run:
        print("✅ DRY RUN COMPLETE - No files were moved")
        print("Run with --execute to actually move files")
    else:
        print("✅ MIGRATION COMPLETE")
        print("\n📝 Next steps:")
        print("1. Update view imports and render() calls")
        print("2. Run tests: pytest backend/tests/")
        print("3. Update any hardcoded paths in documentation")
        print("4. Commit changes: git add . && git commit -m 'Reorganize project structure'")
    print("=" * 80)

if __name__ == '__main__':
    main()
