"""
Test Oxford CSV parser
"""
import sys
sys.path.insert(0, 'c:/Users/n2t/Documents/english_study/backend')

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.vocabulary.management.commands.import_oxford_words import Command

cmd = Command()

# Test cases
test_lines = [
    "about prep., adv. A1",
    "account n. B1, v. B2",
    "abandon v. B2",
    "a,an indefinite article A1",
    "all det., pron. A1, adv. A2",
    "average adj., n. A2, v. B1",
]

print("Testing Oxford CSV parser:\n")
for line in test_lines:
    print(f"Input:  {line}")
    results = cmd.parse_oxford_line(line)
    print(f"Output: {results}")
    print()
