"""
Test Vocabulary API endpoints using Django test client
"""
import os
import sys
import django
import json

# Add backend to path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, backend_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

def test_api():
    """Test vocabulary API endpoints"""
    
    client = Client()
    
    # Create test user
    print("[1] Creating test user...")
    try:
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'is_active': True
            }
        )
        user.set_password('TestPass123!')
        user.save()
        print(f"    User: {user.username} (created={created})")
    except Exception as e:
        print(f"    Error: {e}")
        return
    
    # Login
    print("\n[2] Logging in...")
    api_client = APIClient()
    api_client.force_authenticate(user=user)
    print(f"    API client authenticated as: {user.username}")
    
    # Get words
    print("\n[3] Testing words endpoint...")
    response = api_client.get('/api/v1/vocabulary/words/?search=about')
    print(f"    Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])
        print(f"    Found: {len(results)} words")
        if results:
            w = results[0]
            print(f"    Example: {w['text']} ({w.get('pos', 'N/A')}) - {w.get('cefr_level', 'N/A')}")
    else:
        print(f"    Error: {response.content.decode()[:200]}")
    
    # Get decks
    print("\n[4] Fetching flashcard decks...")
    response = api_client.get('/api/v1/vocabulary/decks/')
    print(f"    Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])
        print(f"    Available: {len(results)} decks")
        for deck in results[:3]:
            print(f"    - {deck.get('icon', '')} {deck['name']}: {deck.get('card_count', 0)} cards")
    else:
        print(f"    Error: {response.content.decode()[:200]}")
    
    # Test word levels
    print("\n[5] Testing word filtering by level...")
    for level in ['A1', 'A2', 'B1', 'B2']:
        response = api_client.get(f'/api/v1/vocabulary/words/?level={level}')
        if response.status_code == 200:
            data = response.json()
            count = len(data.get('results', []))
            total = data.get('count', 0)
            print(f"    {level}: {count} in page (total: {total})")
        else:
            print(f"    {level}: Error {response.status_code}")
    
    print("\n[OK] All tests completed!")

if __name__ == "__main__":
    test_api()
