"""
Add IPA transcriptions and mock audio for tongue twisters
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.curriculum.models import TongueTwister

# Update tongue twisters with IPA transcriptions
tongue_twisters_data = [
    {
        'text': 'She sells seashells by the seashore.',
        'ipa': '/ʃiː sɛlz ˈsiːʃɛlz baɪ ðə ˈsiːʃɔːr/',
    },
    {
        'text': 'Peter Piper picked a peck of pickled peppers.',
        'ipa': '/ˈpiːtər ˈpaɪpər pɪkt ə pɛk əv ˈpɪkəld ˈpɛpərz/',
    },
    {
        'text': 'How much wood would a woodchuck chuck?',
        'ipa': '/haʊ mʌtʃ wʊd wʊd ə ˈwʊdtʃʌk tʃʌk/',
    },
    {
        'text': 'Red lorry, yellow lorry.',
        'ipa': '/rɛd ˈlɒri ˈjɛloʊ ˈlɒri/',
    },
    {
        'text': 'Fuzzy Wuzzy was a bear.',
        'ipa': '/ˈfʌzi ˈwʌzi wɒz ə bɛr/',
    },
    {
        'text': 'I scream, you scream, we all scream for ice cream.',
        'ipa': '/aɪ skriːm juː skriːm wiː ɔːl skriːm fɔːr aɪs kriːm/',
    },
    {
        'text': 'Six slippery snails slid slowly seaward.',
        'ipa': '/sɪks ˈslɪpəri sneɪlz slɪd ˈsloʊli ˈsiːwərd/',
    },
    {
        'text': 'Thirty-three thousand feathers on a thrush.',
        'ipa': '/ˈθɜːrti θriː ˈθaʊzənd ˈfɛðərz ɒn ə θrʌʃ/',
    },
    {
        'text': 'Betty Botter bought some butter.',
        'ipa': '/ˈbɛti ˈbɒtər bɔːt sʌm ˈbʌtər/',
    },
    {
        'text': 'A proper copper coffee pot.',
        'ipa': '/ə ˈprɒpər ˈkɒpər ˈkɒfi pɒt/',
    },
]

print("Updating tongue twisters with IPA transcriptions...")
updated = 0

for data in tongue_twisters_data:
    twisters = TongueTwister.objects.filter(text__icontains=data['text'][:20])
    for twister in twisters:
        twister.ipa_transcription = data['ipa']
        twister.save()
        print(f"✅ Updated: {twister.text[:50]}")
        updated += 1

print(f"\n✅ Updated {updated} tongue twisters with IPA transcriptions!")
