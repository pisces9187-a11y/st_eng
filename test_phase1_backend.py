"""
Test script for Phase 1 Backend APIs.
Tests new endpoints for deck history, progress tracking, and review modes.

Run: python test_phase1_backend.py
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1/vocabulary/flashcards"

# Replace with your JWT token from login
TOKEN = "your_jwt_token_here"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}


def print_section(title):
    """Print section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_recent_decks():
    """Test GET /decks/recent/"""
    print_section("TEST 1: Get Recent Decks")
    
    url = f"{BASE_URL}/decks/recent/"
    response = requests.get(url, headers=headers)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {len(data)} recent decks\n")
        
        for idx, deck_history in enumerate(data, 1):
            print(f"  [{idx}] {deck_history['deck']['name']} ({deck_history['deck']['level']})")
            print(f"      Progress: {deck_history['progress_percentage']}%")
            print(f"      Sessions: {deck_history['total_sessions']}")
            print(f"      Cards: {deck_history['cards_mastered']} mastered, "
                  f"{deck_history['cards_learning']} learning, "
                  f"{deck_history['cards_new']} new")
            print(f"      Last studied: {deck_history['last_studied_at']}")
    else:
        print(f"❌ Error: {response.text}")


def test_deck_progress(deck_id):
    """Test GET /decks/{id}/progress/"""
    print_section(f"TEST 2: Get Deck Progress (deck_id={deck_id})")
    
    url = f"{BASE_URL}/decks/{deck_id}/progress/"
    response = requests.get(url, headers=headers)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"✅ Deck: {data['deck']['name']}\n")
        
        print("  History:")
        print(f"    First studied: {data['history']['first_studied_at']}")
        print(f"    Last studied: {data['history']['last_studied_at']}")
        print(f"    Total sessions: {data['history']['total_sessions']}")
        print(f"    Total time: {data['history']['total_time_minutes']} minutes")
        
        print("\n  Progress:")
        progress = data['progress']
        print(f"    Total cards: {progress['total_cards']}")
        print(f"    New: {progress['cards_new']}")
        print(f"    Learning: {progress['cards_learning']}")
        print(f"    Mastered: {progress['cards_mastered']}")
        print(f"    Difficult: {progress['cards_difficult']}")
        print(f"    Due: {progress['cards_due']}")
        print(f"    Progress: {progress['progress_percentage']}%")
    else:
        print(f"❌ Error: {response.text}")


def test_start_session_normal(deck_id):
    """Test POST /study/start_session/ with normal mode"""
    print_section("TEST 3: Start Session - Normal Mode")
    
    url = f"{BASE_URL}/study/start_session/"
    data = {
        "deck_id": deck_id,
        "card_count": 20,
        "review_mode": "normal"
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Session started: {result['session_id']}")
        print(f"   Cards returned: {len(result['cards'])}")
        print(f"   Current streak: {result['streak']['current']} days")
    else:
        print(f"❌ Error: {response.text}")


def test_start_session_difficult(deck_id):
    """Test POST /study/start_session/ with difficult mode"""
    print_section("TEST 4: Start Session - Difficult Mode")
    
    url = f"{BASE_URL}/study/start_session/"
    data = {
        "deck_id": deck_id,
        "card_count": 10,
        "review_mode": "difficult"
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Session started: {result['session_id']}")
        print(f"   Difficult cards returned: {len(result['cards'])}")
        
        if result['cards']:
            print("\n   Sample difficult words:")
            for card in result['cards'][:3]:
                print(f"     - {card['word']['text']} ({card['word']['cefr_level']})")
    else:
        print(f"❌ Error: {response.text}")


def test_start_session_due(deck_id):
    """Test POST /study/start_session/ with due mode"""
    print_section("TEST 5: Start Session - Due Cards Mode")
    
    url = f"{BASE_URL}/study/start_session/"
    data = {
        "deck_id": deck_id,
        "card_count": 10,
        "review_mode": "due"
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Session started: {result['session_id']}")
        print(f"   Due cards returned: {len(result['cards'])}")
    else:
        print(f"❌ Error: {response.text}")


def test_tag_card(flashcard_id):
    """Test POST /flashcards/{id}/tag-card/"""
    print_section(f"TEST 6: Tag Card as Difficult (flashcard_id={flashcard_id})")
    
    url = f"{BASE_URL}/{flashcard_id}/tag-card/"
    data = {
        "tag": "difficult",
        "action": "add",
        "notes": "Hard to remember pronunciation"
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ {result['message']}")
        print(f"   Tag: {result['tag']}")
        print(f"   Created: {result['created']}")
    else:
        print(f"❌ Error: {response.text}")


def test_start_session_tagged(deck_id):
    """Test POST /study/start_session/ with tagged mode"""
    print_section("TEST 7: Start Session - Tagged Cards (Difficult)")
    
    url = f"{BASE_URL}/study/start_session/"
    data = {
        "deck_id": deck_id,
        "card_count": 10,
        "review_mode": "tagged",
        "tag": "difficult"
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Session started: {result['session_id']}")
        print(f"   Tagged cards returned: {len(result['cards'])}")
        
        if result['cards']:
            print("\n   Tagged difficult words:")
            for card in result['cards']:
                print(f"     - {card['word']['text']}")
    else:
        print(f"❌ Error: {response.text}")


def main():
    """Run all tests"""
    print("=" * 70)
    print("  PHASE 1 BACKEND API TESTS")
    print("=" * 70)
    print(f"  Base URL: {BASE_URL}")
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if TOKEN == "your_jwt_token_here":
        print("\n⚠️  WARNING: Please set your JWT token in the TOKEN variable!")
        print("   Login at http://localhost:8000/api/v1/auth/login/ to get token")
        return
    
    # Run tests
    try:
        test_recent_decks()
        
        # Use deck_id=1 for testing (Oxford A1)
        deck_id = 1
        test_deck_progress(deck_id)
        test_start_session_normal(deck_id)
        test_start_session_difficult(deck_id)
        test_start_session_due(deck_id)
        
        # Use flashcard_id=1 for tagging test
        flashcard_id = 1
        test_tag_card(flashcard_id)
        test_start_session_tagged(deck_id)
        
        print_section("ALL TESTS COMPLETED")
        print("✨ Phase 1 Backend is ready!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
