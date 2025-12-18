#!/usr/bin/env python
"""Test direct file serving"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
sys.path.insert(0, '/c/Users/n2t/Documents/english_study/backend')
django.setup()

from apps.curriculum.models import Phoneme, AudioSource
from django.conf import settings
import urllib.parse

print("\n" + "="*70)
print("AUDIO URL TEST")
print("="*70)

phoneme = Phoneme.objects.filter(audio_sources__isnull=False).first()
audio = phoneme.audio_sources.first()

print(f"\nPhoneme: {phoneme.ipa_symbol}")
print(f"Audio file field value: {audio.audio_file}")
print(f"Audio file name: {audio.audio_file.name}")
print(f"Audio file path: {audio.audio_file.path}")

# Test URL
url = audio.get_url()
print(f"\nOriginal URL: {url}")

# Check if file exists at the path
file_path = audio.audio_file.path
exists = os.path.exists(file_path)
print(f"\nFile exists at path: {exists}")
print(f"File path: {file_path}")

if exists:
    size = os.path.getsize(file_path)
    print(f"File size: {size} bytes")
    
    # Read first 20 bytes to verify it's MP3
    with open(file_path, 'rb') as f:
        header = f.read(20)
        print(f"File header (hex): {header.hex()}")
        
        # Check for MP3 signature
        if header[:3] == b'ID3' or header[:2] == b'\xff\xfb' or header[:2] == b'\xff\xfa':
            print(f"✓ Valid MP3 file signature detected")
        else:
            print(f"✗ Not a valid MP3 file! First 2 bytes: {header[:2].hex()}")

# Test the API directly
print(f"\n\nTesting API endpoint directly:")
from django.test import Client
from django.urls import reverse

client = Client()
response = client.get(f'/api/v1/phonemes/{phoneme.id}/audio/url/')
print(f"API Response status: {response.status_code}")
print(f"API Response data: {response.json()}")

# Test file serving
print(f"\n\nTesting media file serving:")
# The actual URL that would be requested
test_url = f'/media/phonemes/audio/2025/12/15/{urllib.parse.quote(audio.audio_file.name.split("/")[-1])}'
print(f"Testing URL: {test_url}")

response = client.get(test_url)
print(f"File serving response status: {response.status_code}")
if response.status_code == 200:
    print(f"✓ File served successfully")
    print(f"Content-Type: {response.get('Content-Type', 'Not set')}")
    print(f"Content-Length: {len(response.content)} bytes")
else:
    print(f"✗ File serving failed!")
    print(f"Response content: {response.content[:200]}")

print("\n" + "="*70 + "\n")
