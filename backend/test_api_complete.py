#!/usr/bin/env python
"""Simple test to verify everything is working"""
import os
import sys
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
sys.path.insert(0, '/c/Users/n2t/Documents/english_study/backend')
django.setup()

from django.test import Client
from apps.curriculum.models import Phoneme

print("\n" + "="*70)
print("AUDIO PLAYBACK COMPLETE TEST")
print("="*70)

client = Client()
client.defaults['HTTP_HOST'] = 'localhost:8000'

# Get first 3 phonemes
phonemes = Phoneme.objects.all()[:3]

print(f"\nTesting {len(phonemes)} phonemes:\n")

for phoneme in phonemes:
    # Test API endpoint
    response = client.get(
        f'/api/v1/phonemes/{phoneme.id}/audio/url/',
        HTTP_HOST='localhost:8000'
    )
    
    print(f"Phoneme: {phoneme.ipa_symbol} (ID: {phoneme.id})")
    print(f"  API Status: {response.status_code}")
    
    if response.status_code == 200:
        data = json.loads(response.content)
        url = data.get('audio_url')
        print(f"  Audio URL: {url}")
        
        # Check if file exists
        if url:
            # Build correct path to media file
            media_root = os.path.join(os.path.dirname(__file__), 'media')
            audio_file_path = os.path.join(media_root, url.replace('/media/', ''))
            exists = os.path.exists(audio_file_path)
            print(f"  File path: {audio_file_path}")
            print(f"  File exists: {exists}")
            if exists:
                size = os.path.getsize(audio_file_path)
                print(f"  File size: {size} bytes")
                
                # Check MP3 signature
                with open(audio_file_path, 'rb') as f:
                    header = f.read(4)
                    is_mp3 = header[:2] == b'\xff\xfb' or header[:3] == b'ID3'
                    print(f"  Valid MP3: {is_mp3}")
    else:
        print(f"  Error: {response.content.decode()}")
    print()

print("="*70 + "\n")
