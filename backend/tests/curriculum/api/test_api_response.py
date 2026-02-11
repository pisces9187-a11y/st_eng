#!/usr/bin/env python
"""
Quick test to verify the phoneme discovery API response structure
"""

import requests
import json
from pathlib import Path

# Get Django token from user
def test_api():
    # Test unauthenticated first
    url = "http://localhost:8000/api/v1/pronunciation/phonemes/"
    
    print("Testing Phoneme List API...")
    print(f"URL: {url}\n")
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}\n")
        
        data = response.json()
        print("Response Structure:")
        print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])
        
        # Check key fields
        print("\n\nChecking Response Structure:")
        if 'categories' in data:
            print("✓ Has 'categories' field")
            categories = data['categories']
            print(f"  - Categories count: {len(categories)}")
            
            if categories:
                first_cat = categories[0]
                print(f"  - First category name: {first_cat.get('name', 'N/A')}")
                
                if 'phonemes' in first_cat:
                    phonemes = first_cat['phonemes']
                    print(f"  - Phonemes in first category: {len(phonemes)}")
                    
                    if phonemes:
                        first_phone = phonemes[0]
                        print(f"\n  First phoneme structure:")
                        for key, value in first_phone.items():
                            if key == 'progress':
                                print(f"    - {key}: {value}")
                            else:
                                print(f"    - {key}: {value}")
        
        if 'success' in data:
            print(f"✓ Has 'success' field: {data['success']}")
        
        if 'data' in data:
            print("✓ Has 'data' field")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api()
