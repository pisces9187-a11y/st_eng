#!/usr/bin/env python3
"""
Phase 2 Frontend Files Verification
Checks that all Phase 2 frontend files exist and are properly structured
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists and return file size"""
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        size_kb = size / 1024
        print(f"✓ {description}")
        print(f"  Path: {filepath}")
        print(f"  Size: {size_kb:.1f} KB")
        return True, size
    else:
        print(f"✗ {description}")
        print(f"  Path: {filepath} NOT FOUND")
        return False, 0

def check_file_content(filepath, required_strings):
    """Check if file contains required content"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        missing = []
        for req in required_strings:
            if req not in content:
                missing.append(req)
        
        if missing:
            print(f"  ⚠ Missing content:")
            for m in missing:
                print(f"    - {m}")
            return False
        else:
            print(f"  ✓ All required content present")
            return True
    except Exception as e:
        print(f"  ✗ Error reading file: {e}")
        return False

def main():
    print("="*70)
    print("PHASE 2 - FRONTEND FILES VERIFICATION")
    print("="*70)
    
    base_dir = "/home/n2t/Documents/english_study"
    
    # Define files to check
    files_to_check = [
        {
            "path": f"{base_dir}/assets/js/flashcard-audio-player.js",
            "description": "Flashcard Audio Player Component",
            "required": [
                "FlashcardAudioPlayer",
                "VOICES",
                "SPEEDS",
                "loadWord",
                "changeVoice",
                "waveform"
            ]
        },
        {
            "path": f"{base_dir}/assets/css/flashcard-audio-player.css",
            "description": "Audio Player Styles",
            "required": [
                ".flashcard-audio-player",
                ".waveform",
                "@keyframes",
                "gradient"
            ]
        },
        {
            "path": f"{base_dir}/assets/js/flashcard-study-session.js",
            "description": "Flashcard Study Session Manager",
            "required": [
                "FlashcardStudySession",
                "startSession",
                "reviewCard",
                "endSession",
                "SM-2",
                "achievements"
            ]
        },
        {
            "path": f"{base_dir}/assets/js/django-api.js",
            "description": "Django API Service (Enhanced)",
            "required": [
                "startFlashcardSession",
                "reviewFlashcardCard",
                "generateAudio",
                "getFlashcardDashboard",
                "getFlashcardAchievements"
            ]
        },
        {
            "path": f"{base_dir}/public/flashcard-study.html",
            "description": "Enhanced Flashcard Study Page",
            "required": [
                "flashcard-audio-player.js",
                "flashcard-study-session.js",
                "rating-buttons",
                "streak-display",
                "daily-progress"
            ]
        },
        {
            "path": f"{base_dir}/public/progress-dashboard.html",
            "description": "Progress Dashboard Page",
            "required": [
                "Chart.js",
                "learningChart",
                "masteryChart",
                "accuracyChart",
                "calendar-heatmap"
            ]
        },
        {
            "path": f"{base_dir}/public/achievements.html",
            "description": "Achievements Page",
            "required": [
                "achievement",
                "confetti",
                "filter"
            ]
        }
    ]
    
    # Run checks
    results = []
    total_size = 0
    
    print("\n" + "="*70)
    print("FILE EXISTENCE & CONTENT CHECK")
    print("="*70 + "\n")
    
    for file_info in files_to_check:
        filepath = file_info["path"]
        description = file_info["description"]
        required = file_info.get("required", [])
        
        print(f"\n[{len(results) + 1}] {description}")
        print("-" * 70)
        
        exists, size = check_file_exists(filepath, description)
        
        if exists:
            total_size += size
            content_ok = check_file_content(filepath, required)
            results.append((description, True, content_ok))
        else:
            results.append((description, False, False))
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    files_exist = sum(1 for _, exists, _ in results if exists)
    content_valid = sum(1 for _, exists, valid in results if exists and valid)
    
    print(f"\nFiles Created: {files_exist}/{len(results)}")
    print(f"Content Valid: {content_valid}/{len(results)}")
    print(f"Total Size: {total_size / 1024:.1f} KB")
    
    print("\nDetailed Results:")
    for desc, exists, valid in results:
        if exists and valid:
            status = "✅ COMPLETE"
        elif exists:
            status = "⚠️  EXISTS (some content missing)"
        else:
            status = "❌ MISSING"
        
        print(f"{status} - {desc}")
    
    # Component Checklist
    print("\n" + "="*70)
    print("COMPONENT CHECKLIST")
    print("="*70)
    
    components = [
        ("Audio Player (Multi-voice)", files_exist >= 1),
        ("Session Manager (SM-2)", files_exist >= 3),
        ("Enhanced Study Page", files_exist >= 5),
        ("Progress Dashboard", files_exist >= 6),
        ("Achievements System", files_exist >= 7),
    ]
    
    for component, status in components:
        print(f"{'✓' if status else '✗'} {component}")
    
    # Final verdict
    print("\n" + "="*70)
    if files_exist == len(results) and content_valid == len(results):
        print("🎉 ALL PHASE 2 FRONTEND COMPONENTS READY!")
        print("="*70)
        print("\nNext Steps:")
        print("1. Start Django development server")
        print("2. Open: http://localhost:8000/flashcard-study.html")
        print("3. Test audio playback with all voices")
        print("4. Review flashcards with quality ratings")
        print("5. Check progress dashboard")
        print("6. Verify achievements unlock")
        return 0
    else:
        print("⚠️  PHASE 2 INCOMPLETE")
        print("="*70)
        print(f"\n{len(results) - files_exist} file(s) missing")
        print(f"{files_exist - content_valid} file(s) need content updates")
        return 1

if __name__ == '__main__':
    sys.exit(main())
