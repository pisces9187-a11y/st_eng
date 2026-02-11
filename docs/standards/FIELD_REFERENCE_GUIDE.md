# 📋 PRONUNCIATION SYSTEM - FIELD REFERENCE GUIDE

Quick reference for correct field names to avoid AttributeError bugs.

---

## 🎵 PHONEME MODEL

**Model:** `apps.curriculum.models.Phoneme`

### ✅ Correct Field Names:
```python
phoneme.ipa_symbol              # NOT .symbol ❌
phoneme.vietnamese_approx       # Vietnamese approximation
phoneme.vietnamese_comparison   # Comparison text
phoneme.phoneme_type           # Type: 'short_vowel', 'consonant', etc.
phoneme.mouth_position_vi      # Mouth position description
phoneme.pronunciation_tips_vi  # Tips in Vietnamese
phoneme.vietnamese_mistake_audio  # Audio file for common mistakes
```

### Usage Example:
```python
# ✅ CORRECT
f"/{phoneme.ipa_symbol}/"  # → /ɪ/

# ❌ WRONG
f"/{phoneme.symbol}/"      # AttributeError!
```

---

## 📊 USER PHONEME PROGRESS

**Model:** `apps.users.models.UserPhonemeProgress`

### ✅ Correct Field Names:
```python
progress.discrimination_accuracy  # NOT .pronunciation_accuracy ❌
progress.times_practiced         # NOT .practice_count ❌
progress.discrimination_attempts
progress.discrimination_correct
progress.production_attempts
progress.production_best_score
progress.mastery_level
progress.current_stage
```

### Scale Notes:
- `discrimination_accuracy`: **0-1 scale** (multiply by 100 for %)
- `production_best_score`: **0-1 scale**

### Usage Example:
```python
# ✅ CORRECT
accuracy_percent = progress.discrimination_accuracy * 100
if accuracy_percent < 70:
    print(f"Need practice: {progress.times_practiced} attempts")

# ❌ WRONG
if progress.pronunciation_accuracy < 70:  # AttributeError!
    print(f"Attempts: {progress.practice_count}")  # AttributeError!
```

---

## 📚 USER PRONUNCIATION LESSON PROGRESS

**Model:** `apps.users.models.UserPronunciationLessonProgress`

### ✅ Correct Field Names:
```python
progress.pronunciation_lesson   # ForeignKey to PronunciationLesson
progress.status                 # 'not_started', 'in_progress', 'completed'
progress.completed_screens      # List [1, 2, 3, 4, 5]
progress.challenge_correct      # Correct challenge answers
progress.challenge_total        # Total challenge questions
progress.pronunciation_accuracy # Lesson-level accuracy (%)
```

### Challenge Accuracy Calculation:
```python
# ✅ CORRECT
if progress.challenge_total > 0:
    accuracy = (progress.challenge_correct / progress.challenge_total) * 100
```

---

## 🎯 PRONUNCIATION LESSON

**Model:** `apps.curriculum.models.PronunciationLesson`

### ✅ Correct Field Names:
```python
lesson.title_vi               # Vietnamese title
lesson.slug                   # URL slug
lesson.stage                  # ForeignKey to CurriculumStage
lesson.focus_phonemes         # ManyToMany to Phoneme
lesson.part_number           # Lesson number (1-15)
lesson.unit_number           # Unit within part
lesson.status                # 'draft', 'published'
```

---

## 🏆 CURRICULUM STAGE

**Model:** `apps.curriculum.models.CurriculumStage`

### ✅ Correct Field Names:
```python
stage.number        # 1-4
stage.name_vi       # Vietnamese name
stage.description_vi
stage.icon
stage.color
stage.focus_area
stage.lessons       # Related lessons (reverse FK)
```

---

## 🔍 COMMON BUGS & FIXES

### Bug 1: AttributeError on 'symbol'
```python
# ❌ WRONG
f"/{phoneme.symbol}/"

# ✅ FIX
f"/{phoneme.ipa_symbol}/"
```

### Bug 2: AttributeError on 'pronunciation_accuracy'
```python
# ❌ WRONG (UserPhonemeProgress)
if progress.pronunciation_accuracy < 70:

# ✅ FIX
accuracy_percent = progress.discrimination_accuracy * 100
if accuracy_percent < 70:
```

### Bug 3: AttributeError on 'practice_count'
```python
# ❌ WRONG
attempts = progress.practice_count

# ✅ FIX
attempts = progress.times_practiced
```

### Bug 4: Wrong Scale (0-1 vs 0-100)
```python
# ❌ WRONG (comparing 0-1 to 70)
if progress.discrimination_accuracy < 70:

# ✅ FIX (convert to percentage first)
accuracy_percent = progress.discrimination_accuracy * 100
if accuracy_percent < 70:
```

---

## 📝 TEMPLATE USAGE

### In Django Templates:
```django
{# ✅ CORRECT #}
{{ error.phoneme.ipa_symbol }}
{{ progress.times_practiced }}
{{ phoneme.vietnamese_comparison }}

{# ❌ WRONG #}
{{ error.phoneme.symbol }}  {# AttributeError! #}
{{ progress.practice_count }}  {# AttributeError! #}
```

---

## 🔗 RELATED MODELS QUICK REF

### MinimalPair
```python
pair.phoneme_1          # ForeignKey to Phoneme
pair.phoneme_2          # ForeignKey to Phoneme
pair.word_1, pair.word_2
pair.difficulty_level   # 1-3
```

### DiscriminationAttempt
```python
attempt.session         # ForeignKey to DiscriminationSession
attempt.is_correct      # Boolean
attempt.response_time   # Duration
```

---

## 🎯 QUICK LOOKUP TABLE

| What You Want | Correct Field | Common Mistake |
|---------------|---------------|----------------|
| IPA symbol | `phoneme.ipa_symbol` | `phoneme.symbol` ❌ |
| Practice count | `progress.times_practiced` | `progress.practice_count` ❌ |
| Phoneme accuracy | `progress.discrimination_accuracy * 100` | `progress.pronunciation_accuracy` ❌ |
| Lesson title (VN) | `lesson.title_vi` | `lesson.title` |
| Stage number | `stage.number` | `stage.stage_number` ❌ |

---

## 💡 TIPS

1. **Always multiply 0-1 accuracy by 100** before comparing to percentages
2. **Use `ipa_symbol`** not `symbol` for phonemes
3. **Use `times_practiced`** not `practice_count`
4. **Check field exists** with `hasattr()` when unsure
5. **Read model docstrings** - they document field purposes

---

**Last Updated:** January 5, 2026  
**Maintainer:** Development Team
