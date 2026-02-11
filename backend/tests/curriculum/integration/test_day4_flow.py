#!/usr/bin/env python
"""
Day 4 Comprehensive Testing Report
Tests all fixes for Auth loading race condition and frontend issues
"""

import os
import sys
import re
from pathlib import Path

def check_file_content(filepath, pattern):
    """Check if a file contains a pattern"""
    if not os.path.exists(filepath):
        return False, "File not found"
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if isinstance(pattern, str):
                return pattern in content, content
            else:  # regex pattern
                return bool(re.search(pattern, content)), content
    except Exception as e:
        return False, str(e)

def test_auth_loading_fix():
    """Verify Auth loading race condition is fixed"""
    print("\n" + "="*70)
    print("TEST 1: Auth Loading Race Condition Fix")
    print("="*70)
    
    base_path = Path(__file__).parent / "backend" / "templates" / "base" / "_base.html"
    
    # Check 1: Auth script is in _base.html
    has_auth, content = check_file_content(str(base_path), "auth.js")
    print(f"[PASS] auth.js loaded in _base.html: {has_auth}")
    
    # Check 2: Script loading order (config -> api -> auth -> utils)
    config_pos = content.find("config.js") if has_auth else -1
    api_pos = content.find("api.js") if has_auth else -1
    auth_pos = content.find("auth.js") if has_auth else -1
    utils_pos = content.find("utils.js") if has_auth else -1
    
    correct_order = config_pos < api_pos < auth_pos < utils_pos if all(p > -1 for p in [config_pos, api_pos, auth_pos, utils_pos]) else False
    print(f"[PASS] Script loading order correct (config→api→auth→utils): {correct_order}")
    
    return has_auth and correct_order

def test_deferred_initialization():
    """Verify deferred Vue initialization pattern"""
    print("\n" + "="*70)
    print("TEST 2: Deferred Vue.js Initialization")
    print("="*70)
    
    pages = [
        ("Discovery", "backend/templates/pages/pronunciation_discovery.html"),
        ("Learning", "backend/templates/pages/pronunciation_learning.html"),
        ("Progress", "backend/templates/pages/pronunciation_progress.html"),
    ]
    
    all_good = True
    for name, page_path in pages:
        full_path = Path(__file__).parent / page_path
        
        # Check deferred init function
        has_init, content = check_file_content(str(full_path), "function initialize")
        
        # Check Auth check with polling
        has_auth_check, _ = check_file_content(str(full_path), "typeof Auth === 'undefined'")
        
        # Check setTimeout for retry
        has_timeout, _ = check_file_content(str(full_path), "setTimeout(initialize")
        
        status = "[PASS]" if (has_init and has_auth_check and has_timeout) else "[FAIL]"
        print(f"{status} {name} page: deferred init={has_init}, auth check={has_auth_check}, polling={has_timeout}")
        
        if not (has_init and has_auth_check and has_timeout):
            all_good = False
    
    return all_good

def test_template_existence():
    """Verify all required templates exist"""
    print("\n" + "="*70)
    print("TEST 3: Template Files Existence")
    print("="*70)
    
    templates = [
        "backend/templates/pages/pronunciation_discovery.html",
        "backend/templates/pages/pronunciation_learning.html",
        "backend/templates/pages/pronunciation_progress.html",
    ]
    
    all_exist = True
    for template in templates:
        full_path = Path(__file__).parent / template
        exists = full_path.exists()
        status = "[PASS]" if exists else "[FAIL]"
        print(f"{status} {template.split('/')[-1]}: {exists}")
        if not exists:
            all_exist = False
    
    return all_exist

def test_url_routes():
    """Verify URL routes are configured"""
    print("\n" + "="*70)
    print("TEST 4: URL Routes Configuration")
    print("="*70)
    
    urls_path = Path(__file__).parent / "backend" / "apps" / "curriculum" / "urls.py"
    
    routes = [
        ("discovery", "pronunciation_discovery_view"),
        ("learning/<int:phoneme_id>/", "pronunciation_learning_view"),
        ("discrimination/<int:phoneme_id>/", "pronunciation_discrimination_view"),
        ("production/<int:phoneme_id>/", "pronunciation_production_view"),
        ("dashboard/", "pronunciation_progress_dashboard_view"),
    ]
    
    has_urls, content = check_file_content(str(urls_path), "pronunciation")
    all_routes_exist = True
    
    for route, view in routes:
        route_exists = route in content and view in content
        status = "[PASS]" if route_exists else "[FAIL]"
        print(f"{status} Route: pronunciation/{route} → {view}")
        if not route_exists:
            all_routes_exist = False
    
    return has_urls and all_routes_exist

def test_view_functions():
    """Verify view functions are defined"""
    print("\n" + "="*70)
    print("TEST 5: View Functions Definition")
    print("="*70)
    
    views_path = Path(__file__).parent / "backend" / "apps" / "curriculum" / "views_pronunciation.py"
    
    views = [
        "pronunciation_discovery_view",
        "pronunciation_learning_view",
        "pronunciation_discrimination_view",
        "pronunciation_production_view",
        "pronunciation_progress_dashboard_view",
    ]
    
    has_views, content = check_file_content(str(views_path), "def pronunciation")
    all_views_exist = True
    
    for view in views:
        view_exists = f"def {view}" in content
        status = "[PASS]" if view_exists else "[FAIL]"
        print(f"{status} View function: {view}()")
        if not view_exists:
            all_views_exist = False
    
    return has_views and all_views_exist

def test_api_client_fix():
    """Verify ApiClient references are correct"""
    print("\n" + "="*70)
    print("TEST 6: API Client Reference Fixes")
    print("="*70)
    
    pages = [
        ("Discovery", "backend/templates/pages/pronunciation_discovery.html"),
        ("Learning", "backend/templates/pages/pronunciation_learning.html"),
    ]
    
    all_good = True
    for name, page_path in pages:
        full_path = Path(__file__).parent / page_path
        
        # Check for correct ApiClient (capital A)
        has_correct, content = check_file_content(str(full_path), "ApiClient")
        
        # Check for incorrect apiClient (should NOT exist)
        has_incorrect, _ = check_file_content(str(full_path), r"\bapiClient\b")
        
        # ApiClient.get should be used
        has_get_method, _ = check_file_content(str(full_path), "ApiClient.get")
        
        status = "[PASS]" if (has_correct and not has_incorrect and has_get_method) else "[FAIL]"
        print(f"{status} {name}: ApiClient correct={has_correct}, no lowercase={not has_incorrect}, using get()={has_get_method}")
        
        if not (has_correct and not has_incorrect and has_get_method):
            all_good = False
    
    return all_good

def test_auth_methods():
    """Verify Auth method calls are correct"""
    print("\n" + "="*70)
    print("TEST 7: Authentication Method Calls")
    print("="*70)
    
    pages = [
        ("Discovery", "backend/templates/pages/pronunciation_discovery.html"),
        ("Learning", "backend/templates/pages/pronunciation_learning.html"),
        ("Progress", "backend/templates/pages/pronunciation_progress.html"),
    ]
    
    all_good = True
    for name, page_path in pages:
        full_path = Path(__file__).parent / page_path
        
        # Check for Auth.isAuthenticated() (with Auth prefix)
        has_correct, content = check_file_content(str(full_path), "Auth.isAuthenticated()")
        
        # Check for incorrect isAuthenticated() (should NOT exist standalone)
        has_incorrect, _ = check_file_content(str(full_path), r"if\s*\(\s*isAuthenticated\(\)")
        
        status = "[PASS]" if has_correct and not has_incorrect else "[FAIL]"
        print(f"{status} {name}: Auth.isAuthenticated()={has_correct}, no standalone isAuthenticated()={not has_incorrect}")
        
        if not (has_correct and not has_incorrect):
            all_good = False
    
    return all_good

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("DAY 4 COMPREHENSIVE TESTING REPORT")
    print("Testing Auth Loading Race Condition Fixes")
    print("="*70)
    
    results = {
        "Auth Loading Fix": test_auth_loading_fix(),
        "Deferred Initialization": test_deferred_initialization(),
        "Template Existence": test_template_existence(),
        "URL Routes": test_url_routes(),
        "View Functions": test_view_functions(),
        "API Client Fix": test_api_client_fix(),
        "Auth Methods": test_auth_methods(),
    }
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "[PASS] PASS" if result else "[FAIL] FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nALL TESTS PASSED! Frontend is ready for manual browser testing.")
        print("\nTo test manually:")
        print("1. Start Django server: python manage.py runserver")
        print("2. Open browser: http://localhost:8000/pronunciation/discovery/")
        print("3. Check console (F12) for JavaScript errors")
        print("4. Test interactive features")
        return 0
    else:
        print(f"\n{total - passed} test(s) failed. Review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
