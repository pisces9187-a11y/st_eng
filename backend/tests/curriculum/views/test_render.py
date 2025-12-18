import os
import sys
import django

os.chdir('C:/Users/n2t/Documents/english_study/backend')
sys.path.insert(0, 'C:/Users/n2t/Documents/english_study/backend')
os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from apps.curriculum.models import Phoneme

User = get_user_model()

print("\n" + "="*70)
print("TESTING PRONUNCIATION PAGES RENDER")
print("="*70 + "\n")

client = Client()
user = User.objects.first()
client.force_login(user)

# Test learning pages
phonemes = list(Phoneme.objects.filter(is_active=True)[:5])
passed = 0
failed = 0

for phoneme in phonemes:
    try:
        response = client.get(f'/pronunciation/learning/{phoneme.id}/')
        if response.status_code == 200:
            print(f"[PASS] Learning page {phoneme.id} (/{phoneme.ipa_symbol}/): OK")
            passed += 1
        else:
            print(f"[FAIL] Learning page {phoneme.id}: Status {response.status_code}")
            failed += 1
    except AttributeError as e:
        print(f"[FAIL] Learning page {phoneme.id}: AttributeError - {e}")
        failed += 1
    except Exception as e:
        print(f"[FAIL] Learning page {phoneme.id}: {type(e).__name__} - {e}")
        failed += 1

# Test other pages
try:
    response = client.get('/pronunciation/discovery/')
    if response.status_code == 200:
        print(f"[PASS] Discovery page: OK")
        passed += 1
    else:
        print(f"[FAIL] Discovery page: Status {response.status_code}")
        failed += 1
except Exception as e:
    print(f"[FAIL] Discovery page: {type(e).__name__} - {e}")
    failed += 1

try:
    response = client.get('/pronunciation/dashboard/')
    if response.status_code == 200:
        print(f"[PASS] Dashboard page: OK")
        passed += 1
    else:
        print(f"[FAIL] Dashboard page: Status {response.status_code}")
        failed += 1
except Exception as e:
    print(f"[FAIL] Dashboard page: {type(e).__name__} - {e}")
    failed += 1

print("\n" + "="*70)
print(f"RESULT: {passed} passed, {failed} failed")
print("="*70)

if failed > 0:
    sys.exit(1)
