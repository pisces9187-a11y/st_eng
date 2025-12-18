"""
Quick manual test for pronunciation API endpoints.
Run with: python manage.py shell < test_pronunciation_api_quick.py
"""

from django.contrib.auth import get_user_model
from apps.curriculum.models import Phoneme, PhonemeCategory, MinimalPair
from apps.users.models import UserPhonemeProgress

User = get_user_model()

print("\n" + "="*70)
print("QUICK TEST: Pronunciation Learning Flow API")
print("="*70)

# 1. Create or get test user
user, created = User.objects.get_or_create(
    username='test_pronunciation',
    defaults={'email': 'test@pronunciation.com'}
)
if created:
    user.set_password('testpass123')
    user.save()
print(f"✅ Test user: {user.username}")

# 2. Get or create phoneme category
category, _ = PhonemeCategory.objects.get_or_create(
    name='Test Vowels',
    defaults={'name_vi': 'Nguyên âm test', 'order': 1}
)
print(f"✅ Category: {category.name}")

# 3. Get or create test phonemes
phoneme_i, _ = Phoneme.objects.get_or_create(
    ipa_symbol='i:',
    defaults={
        'category': category,
        'vietnamese_approx': 'i dài',
        'phoneme_type': 'long_vowel',
        'tongue_position_vi': 'Lưỡi cao phía trước',
        'mouth_position_vi': 'Môi căng ngang',
        'pronunciation_tips_vi': 'Phát âm như "ee" trong "see"',
    }
)

phoneme_I, _ = Phoneme.objects.get_or_create(
    ipa_symbol='ɪ',
    defaults={
        'category': category,
        'vietnamese_approx': 'i ngắn',
        'phoneme_type': 'short_vowel',
        'tongue_position_vi': 'Lưỡi hơi thấp hơn',
        'mouth_position_vi': 'Môi lỏa hơn',
        'pronunciation_tips_vi': 'Phát âm như "i" trong "sit"',
    }
)

print(f"✅ Phoneme 1: /{phoneme_i.ipa_symbol}/")
print(f"✅ Phoneme 2: /{phoneme_I.ipa_symbol}/")

# 4. Test Stage 1: Discovery
progress_i, created = UserPhonemeProgress.objects.get_or_create(
    user=user,
    phoneme=phoneme_i
)
print(f"\n--- Stage 1: Discovery ---")
print(f"Initial stage: {progress_i.current_stage}")

progress_i.mark_as_discovered()
print(f"After discovery: {progress_i.current_stage}")
print(f"Discovery date: {progress_i.discovery_date}")
assert progress_i.current_stage == 'discovered', "❌ Discovery failed!"
print("✅ Discovery works!")

# 5. Test Stage 2: Start Learning
print(f"\n--- Stage 2: Learning ---")
progress_i.start_learning()
print(f"After start learning: {progress_i.current_stage}")
print(f"Learning started at: {progress_i.learning_started_at}")
assert progress_i.current_stage == 'learning', "❌ Learning start failed!"
print("✅ Learning start works!")

# 6. Test Stage 3: Discrimination
print(f"\n--- Stage 3: Discrimination ---")
print(f"Can practice discrimination? {progress_i.can_practice_discrimination()}")
assert progress_i.can_practice_discrimination() == True, "❌ Should be able to practice!"

progress_i.start_discrimination()
print(f"After start discrimination: {progress_i.current_stage}")
print(f"Discrimination started at: {progress_i.discrimination_started_at}")
assert progress_i.current_stage == 'discriminating', "❌ Discrimination start failed!"

# Simulate quiz: 8/10 correct
progress_i.update_discrimination_progress(correct=8, total=10)
print(f"After quiz (8/10): Accuracy = {progress_i.discrimination_accuracy:.2f}")
print(f"Can practice production? {progress_i.can_practice_production()}")
assert progress_i.discrimination_accuracy == 0.8, "❌ Accuracy calculation wrong!"
assert progress_i.can_practice_production() == True, "❌ Should unlock production at 80%!"
print("✅ Discrimination works! Production unlocked!")

# 7. Test Stage 4: Production
print(f"\n--- Stage 4: Production ---")
progress_i.start_production()
print(f"After start production: {progress_i.current_stage}")
print(f"Production started at: {progress_i.production_started_at}")
assert progress_i.current_stage == 'producing', "❌ Production start failed!"

# Simulate recording: 85% score
progress_i.update_production_progress(score=0.85)
print(f"After recording (85%): Best score = {progress_i.production_best_score}")
print(f"Production attempts: {progress_i.production_attempts}")
print(f"Current stage: {progress_i.current_stage}")

# Both discrimination (80%) and production (85%) >= 80% → should be mastered
assert progress_i.current_stage == 'mastered', "❌ Should be mastered!"
assert progress_i.mastered_at is not None, "❌ Mastered_at should be set!"
print(f"Mastered at: {progress_i.mastered_at}")
print("✅ Production works! Auto-mastered!")

# 8. Test helper methods
print(f"\n--- Helper Methods ---")
print(f"Stage display (VI): {progress_i.get_stage_display_vi()}")
print(f"Next action: {progress_i.get_next_stage_action()}")

# 9. Summary
print(f"\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"✅ All stage transitions work correctly!")
print(f"✅ Unlock logic (80% threshold) works!")
print(f"✅ Progress tracking accurate!")
print(f"✅ Auto-mastery at 80%+ both skills works!")
print(f"\nFinal state:")
print(f"  - Stage: {progress_i.current_stage}")
print(f"  - Discrimination: {progress_i.discrimination_accuracy:.0%} ({progress_i.discrimination_correct}/{progress_i.discrimination_attempts})")
print(f"  - Production: {progress_i.production_best_score:.0%} (best of {progress_i.production_attempts} attempts)")
print(f"  - Mastery Level: {progress_i.mastery_level}/5")
print("="*70)
print("✅ ALL TESTS PASSED!")
print("="*70 + "\n")
