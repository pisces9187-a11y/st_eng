# Quick Test Script for Pronunciation Pages
# Run from project root: python test_pages_quick.py

import os
import sys

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Set Django settings before importing anything
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from apps.curriculum.models import Phoneme

User = get_user_model()

def test_pronunciation_pages():
    """Test that pronunciation pages load without errors"""
    
    print("\n" + "="*60)
    print("TESTING PRONUNCIATION PAGES")
    print("="*60 + "\n")
    
    # Create test client
    client = Client()
    
    # Create or get test user
    user, created = User.objects.get_or_create(
        email='test@example.com',
        defaults={'username': 'testuser'}
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print("✓ Created test user")
    else:
        print("✓ Using existing test user")
    
    # Login
    client.login(email='test@example.com', password='testpass123')
    print("✓ Logged in\n")
    
    # Test 1: Discovery Page
    print("Test 1: Discovery Page")
    try:
        response = client.get('/pronunciation/discovery/')
        if response.status_code == 200:
            print(f"  ✓ Status: {response.status_code} OK")
            if b'Kh\xc3\xa1m Ph\xc3\xa1 44 \xc3\x82m IPA' in response.content:
                print("  ✓ Content: Title found")
            if b'Vue.js' in response.content or b'discoveryApp' in response.content:
                print("  ✓ Vue.js: App mounted")
        else:
            print(f"  ✗ Status: {response.status_code}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    print()
    
    # Test 2: Learning Page
    print("Test 2: Learning Page")
    try:
        # Get first phoneme
        phoneme = Phoneme.objects.filter(is_active=True).first()
        if phoneme:
            response = client.get(f'/pronunciation/learning/{phoneme.id}/')
            if response.status_code == 200:
                print(f"  ✓ Status: {response.status_code} OK")
                print(f"  ✓ Phoneme: {phoneme.ipa_symbol}")
                if b'learningApp' in response.content:
                    print("  ✓ Vue.js: App mounted")
            else:
                print(f"  ✗ Status: {response.status_code}")
        else:
            print("  ⚠ Warning: No phonemes in database")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    print()
    
    # Test 3: Dashboard Page
    print("Test 3: Dashboard Page")
    try:
        response = client.get('/pronunciation/dashboard/')
        if response.status_code == 200:
            print(f"  ✓ Status: {response.status_code} OK")
            if b'progressApp' in response.content:
                print("  ✓ Vue.js: App mounted")
        else:
            print(f"  ✗ Status: {response.status_code}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    print()
    
    # Test 4: Check Static Files
    print("Test 4: Static Files")
    static_files = [
        '/static/js/config.js',
        '/static/js/api.js',
        '/static/js/auth.js',
        '/static/js/utils.js',
    ]
    
    for file_path in static_files:
        try:
            response = client.get(file_path)
            if response.status_code == 200:
                print(f"  ✓ {file_path}")
            else:
                print(f"  ✗ {file_path} - Status: {response.status_code}")
        except Exception as e:
            print(f"  ✗ {file_path} - Error: {e}")
    
    print()
    
    # Test 5: API Endpoints
    print("Test 5: API Endpoints")
    api_endpoints = [
        '/api/v1/pronunciation/phonemes/',
        '/api/v1/pronunciation/progress/overall/',
    ]
    
    for endpoint in api_endpoints:
        try:
            response = client.get(endpoint)
            if response.status_code == 200:
                print(f"  ✓ {endpoint}")
            else:
                print(f"  ⚠ {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"  ✗ {endpoint} - Error: {e}")
    
    print("\n" + "="*60)
    print("TESTING COMPLETE")
    print("="*60 + "\n")

if __name__ == '__main__':
    test_pronunciation_pages()
