#!/usr/bin/env python
"""
Verification script for Day 4 bug fixes
Checks that all files are properly configured
"""

import os
import sys

def check_file_exists(path, description):
    """Check if a file exists"""
    exists = os.path.exists(path)
    status = "✓" if exists else "✗"
    print(f"  {status} {description}: {path}")
    return exists

def check_file_contains(path, search_string, description):
    """Check if a file contains a string"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            found = search_string in content
            status = "✓" if found else "✗"
            print(f"  {status} {description}")
            return found
    except Exception as e:
        print(f"  ✗ Error checking {description}: {e}")
        return False

def verify_day4_fixes():
    """Verify all Day 4 fixes are in place"""
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    backend_path = os.path.join(base_path, 'backend')
    
    print("\n" + "="*70)
    print("DAY 4 BUG FIX VERIFICATION")
    print("="*70 + "\n")
    
    all_ok = True
    
    # 1. Check base templates
    print("1. Checking Base Templates")
    print("-" * 70)
    
    base_html = os.path.join(backend_path, 'templates', 'base', '_base.html')
    if check_file_exists(base_html, "Base HTML template"):
        all_ok &= check_file_contains(
            base_html, 
            "<script src=\"{% static 'js/auth.js' %}\"></script>",
            "auth.js loaded in _base.html"
        )
        all_ok &= check_file_contains(
            base_html,
            "config.js",
            "config.js loaded in _base.html"
        )
        all_ok &= check_file_contains(
            base_html,
            "api.js",
            "api.js loaded in _base.html"
        )
    else:
        all_ok = False
    
    print()
    
    # 2. Check pronunciation pages
    print("2. Checking Pronunciation Pages")
    print("-" * 70)
    
    pages = [
        ('pronunciation_discovery.html', 'Discovery'),
        ('pronunciation_learning.html', 'Learning'),
        ('pronunciation_progress.html', 'Progress'),
    ]
    
    for filename, label in pages:
        filepath = os.path.join(backend_path, 'templates', 'pages', filename)
        if check_file_exists(filepath, f"{label} page"):
            all_ok &= check_file_contains(
                filepath,
                "function initialize",
                f"{label} page has deferred initialization"
            )
            all_ok &= check_file_contains(
                filepath,
                "typeof Auth === 'undefined'",
                f"{label} page checks for Auth availability"
            )
            all_ok &= check_file_contains(
                filepath,
                "Auth.isAuthenticated()",
                f"{label} page uses Auth.isAuthenticated()"
            )
        else:
            all_ok = False
    
    print()
    
    # 3. Check static files
    print("3. Checking Static JavaScript Files")
    print("-" * 70)
    
    static_files = [
        ('config.js', 'Configuration'),
        ('api.js', 'API Client'),
        ('auth.js', 'Authentication'),
        ('utils.js', 'Utilities'),
    ]
    
    for filename, label in static_files:
        filepath = os.path.join(backend_path, 'static', 'js', filename)
        if check_file_exists(filepath, f"{label} module"):
            pass
        else:
            all_ok = False
    
    print()
    
    # 4. Check URL routing
    print("4. Checking URL Routes")
    print("-" * 70)
    
    urls_file = os.path.join(backend_path, 'apps', 'curriculum', 'urls.py')
    if check_file_exists(urls_file, "Curriculum URLs"):
        all_ok &= check_file_contains(
            urls_file,
            "pronunciation_discovery_view",
            "Discovery view imported and configured"
        )
        all_ok &= check_file_contains(
            urls_file,
            "pronunciation_learning_view",
            "Learning view imported and configured"
        )
        all_ok &= check_file_contains(
            urls_file,
            "pronunciation_progress_dashboard_view",
            "Dashboard view imported and configured"
        )
    else:
        all_ok = False
    
    print()
    
    # 5. Check view functions
    print("5. Checking View Functions")
    print("-" * 70)
    
    views_file = os.path.join(backend_path, 'apps', 'curriculum', 'views_pronunciation.py')
    if check_file_exists(views_file, "Pronunciation views"):
        all_ok &= check_file_contains(
            views_file,
            "def pronunciation_discovery_view",
            "pronunciation_discovery_view function defined"
        )
        all_ok &= check_file_contains(
            views_file,
            "def pronunciation_learning_view",
            "pronunciation_learning_view function defined"
        )
        all_ok &= check_file_contains(
            views_file,
            "def pronunciation_progress_dashboard_view",
            "pronunciation_progress_dashboard_view function defined"
        )
    else:
        all_ok = False
    
    print()
    
    # Summary
    print("="*70)
    if all_ok:
        print("✓ ALL CHECKS PASSED - Ready for testing!")
    else:
        print("✗ SOME CHECKS FAILED - Please review the items marked with ✗")
    print("="*70 + "\n")
    
    return all_ok

if __name__ == '__main__':
    success = verify_day4_fixes()
    sys.exit(0 if success else 1)
