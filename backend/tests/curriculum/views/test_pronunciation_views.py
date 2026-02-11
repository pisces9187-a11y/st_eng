"""
Test that pronunciation pages actually render without errors.
This catches AttributeErrors that static tests miss.
"""
import sys
import os
import django

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
os.chdir(backend_path)  # Change to backend directory
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from apps.curriculum.models import Phoneme

User = get_user_model()


def test_pronunciation_pages():
    """Test that all pronunciation pages render without AttributeErrors."""
    print("\n" + "="*70)
    print("PRONUNCIATION PAGES RENDER TEST")
    print("Testing that pages load without AttributeError")
    print("="*70 + "\n")
    
    client = Client()
    
    # Create test user
    try:
        user = User.objects.get(username='test_render')
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='test_render',
            email='test@test.com',
            password='testpass123'
        )
    
    # Login
    client.force_login(user)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Discovery page
    print("TEST 1: Discovery Page")
    try:
        response = client.get('/pronunciation/discovery/')
        if response.status_code == 200:
            print("[PASS] Discovery page renders successfully")
            tests_passed += 1
        else:
            print(f"[FAIL] Discovery page returned status {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"[FAIL] Discovery page error: {e}")
        tests_failed += 1
    
    # Test 2-4: Learning pages with different phoneme IDs
    phonemes = list(Phoneme.objects.filter(is_active=True).values_list('id', 'ipa_symbol')[:3])
    
    for phoneme_id, ipa_symbol in phonemes:
        print(f"\nTEST: Learning Page - Phoneme {phoneme_id} (/{ipa_symbol}/)")
        try:
            response = client.get(f'/pronunciation/learning/{phoneme_id}/')
            if response.status_code == 200:
                print(f"[PASS] Learning page for /{ipa_symbol}/ renders successfully")
                tests_passed += 1
            else:
                print(f"[FAIL] Learning page returned status {response.status_code}")
                tests_failed += 1
        except AttributeError as e:
            print(f"[FAIL] AttributeError: {e}")
            tests_failed += 1
        except Exception as e:
            print(f"[FAIL] Error: {e}")
            tests_failed += 1
    
    # Test 5: Dashboard page
    print("\nTEST: Dashboard Page")
    try:
        response = client.get('/pronunciation/dashboard/')
        if response.status_code == 200:
            print("[PASS] Dashboard page renders successfully")
            tests_passed += 1
        else:
            print(f"[FAIL] Dashboard page returned status {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"[FAIL] Dashboard page error: {e}")
        tests_failed += 1
    
    # Test 6-7: Discrimination and Production stubs
    if phonemes:
        phoneme_id, ipa_symbol = phonemes[0]
        
        print(f"\nTEST: Discrimination Page - Phoneme {phoneme_id}")
        try:
            response = client.get(f'/pronunciation/discrimination/{phoneme_id}/')
            if response.status_code == 200:
                print(f"[PASS] Discrimination page renders successfully")
                tests_passed += 1
            else:
                print(f"[FAIL] Discrimination page returned status {response.status_code}")
                tests_failed += 1
        except Exception as e:
            print(f"[FAIL] Discrimination page error: {e}")
            tests_failed += 1
        
        print(f"\nTEST: Production Page - Phoneme {phoneme_id}")
        try:
            response = client.get(f'/pronunciation/production/{phoneme_id}/')
            if response.status_code == 200:
                print(f"[PASS] Production page renders successfully")
                tests_passed += 1
            else:
                print(f"[FAIL] Production page returned status {response.status_code}")
                tests_failed += 1
        except Exception as e:
            print(f"[FAIL] Production page error: {e}")
            tests_failed += 1
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    total = tests_passed + tests_failed
    print(f"Total: {tests_passed}/{total} tests passed")
    
    if tests_failed == 0:
        print("\n[SUCCESS] All pronunciation pages render without errors!")
        print("Ready for manual browser testing.")
        return True
    else:
        print(f"\n[FAILED] {tests_failed} tests failed. Please fix AttributeErrors.")
        return False


if __name__ == '__main__':
    success = test_pronunciation_pages()
    sys.exit(0 if success else 1)
