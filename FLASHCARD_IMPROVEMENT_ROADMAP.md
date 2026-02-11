# Flashcard System Improvement Roadmap

## ✅ Completed Issues

### Issue 1: Auto-play interrupting manual rating
**Status**: FIXED
- Stop auto-play timers when user manually rates a card
- Auto-play mode remains enabled for user to resume

### Issue 2: Study Again button not reloading same deck
**Status**: FIXED
- Added `sessionState` to track current deck and card count
- "Study Again" button now reloads the same deck
- Added "Choose Different Deck" option in completion screen
- Display deck name in completion screen

---

## 🔄 In Progress Issues

### Issue 3: Progress Tracking Dashboard (A1-C1)

**Problem**: Users cannot see their overall progress across CEFR levels (A1-C1)

**Solution Components**:

#### 3.1. Deck Progress Cards (Quick Win - 2 hours)
```html
<!-- On dashboard or flashcard page -->
<div class="deck-progress-grid">
    {% for deck in decks %}
    <div class="deck-card">
        <h5>{{ deck.name }}</h5>
        <div class="progress-ring">
            <span>{{ deck.learned_percentage }}%</span>
        </div>
        <p>{{ deck.cards_learned }} / {{ deck.total_cards }} cards</p>
        <small>
            New: {{ deck.new_cards }} | 
            Learning: {{ deck.learning_cards }} | 
            Mastered: {{ deck.mastered_cards }}
        </small>
    </div>
    {% endfor %}
</div>
```

**Backend Changes Needed**:
```python
# In views.py
def get_deck_progress(user, deck):
    """Calculate user's progress in a specific deck"""
    total_cards = deck.flashcards.count()
    
    # Get user's progress for this deck
    progress = UserFlashcardProgress.objects.filter(
        user=user,
        flashcard__deck=deck
    )
    
    mastered = progress.filter(is_mastered=True).count()
    learning = progress.filter(is_learning=True, is_mastered=False).count()
    new_cards = total_cards - progress.count()
    
    return {
        'total_cards': total_cards,
        'cards_learned': progress.count(),
        'mastered_cards': mastered,
        'learning_cards': learning,
        'new_cards': new_cards,
        'learned_percentage': round((progress.count() / total_cards * 100), 1) if total_cards > 0 else 0
    }
```

#### 3.2. CEFR Level Overview (Medium - 4 hours)
**Visual**: Horizontal progress bar showing A1 → A2 → B1 → B2 → C1

```html
<div class="cefr-journey">
    <div class="level-milestone completed">
        <div class="level-icon">A1</div>
        <div class="level-stats">
            <strong>Basic User</strong>
            <p>898/898 cards (100%)</p>
        </div>
    </div>
    <div class="level-milestone in-progress">
        <div class="level-icon">A2</div>
        <div class="level-stats">
            <strong>Elementary</strong>
            <p>450/866 cards (52%)</p>
        </div>
    </div>
    <!-- ... B1, B2, C1 -->
</div>
```

#### 3.3. Study History Calendar (Advanced - 6 hours)
**Visual**: GitHub-style contribution graph

```python
# Backend API
@action(detail=False, methods=['get'])
def study_calendar(self, request):
    """Get daily study activity for last 365 days"""
    today = timezone.now().date()
    start_date = today - timedelta(days=365)
    
    # Get daily card counts
    daily_stats = (
        UserFlashcardProgress.objects
        .filter(
            user=request.user,
            last_reviewed_at__date__gte=start_date
        )
        .annotate(date=TruncDate('last_reviewed_at'))
        .values('date')
        .annotate(cards_reviewed=Count('id'))
        .order_by('date')
    )
    
    return Response({'calendar': list(daily_stats)})
```

---

### Issue 4: Review System for Difficult Cards

**Problem**: Cards marked as "Again" or "Hard" are not easily accessible for review

**Solution Components**:

#### 4.1. Review Filters (Quick Win - 2 hours)

**Add filter buttons on deck selector**:
```html
<div class="review-filters">
    <button onclick="startReviewSession('due')">
        <i class="fas fa-clock"></i>
        Due for Review ({{ due_count }})
    </button>
    <button onclick="startReviewSession('difficult')">
        <i class="fas fa-exclamation-triangle"></i>
        Difficult Cards ({{ difficult_count }})
    </button>
    <button onclick="startReviewSession('failed')">
        <i class="fas fa-times-circle"></i>
        Failed Cards ({{ failed_count }})
    </button>
</div>
```

**Backend Implementation**:
```python
# In utils_flashcard.py
def get_difficult_cards(user, limit=20):
    """Get cards that user marked as Again or Hard (quality < 3)"""
    progress = UserFlashcardProgress.objects.filter(
        user=user,
        is_learning=True,
        easiness_factor__lt=2.5  # Low easiness = difficult
    ).order_by('easiness_factor', 'next_review_date')
    
    return [p.flashcard for p in progress[:limit]]

def get_failed_cards(user, limit=20):
    """Get cards that user failed recently"""
    progress = UserFlashcardProgress.objects.filter(
        user=user,
        is_learning=True,
        interval_days=0  # Interval 0 means failed/again
    ).order_by('-last_reviewed_at')
    
    return [p.flashcard for p in progress[:limit]]
```

#### 4.2. Card Tags/Labels (Medium - 3 hours)

Allow users to tag cards:
- 🔴 Difficult
- ⭐ Important
- 📝 Review Later
- ✅ Mastered

```python
# New model
class FlashcardUserTag(models.Model):
    user = models.ForeignKey(User)
    flashcard = models.ForeignKey(Flashcard)
    tag = models.CharField(max_length=20, choices=[
        ('difficult', 'Difficult'),
        ('important', 'Important'),
        ('review_later', 'Review Later'),
        ('mastered', 'Mastered'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
```

#### 4.3. Smart Review Scheduling (Advanced - 8 hours)

**Spaced Repetition Dashboard**:
```
Cards due today: 45
Cards due this week: 230
Cards overdue: 12

Recommended study time: 25 minutes
```

**Auto-suggest review sessions**:
- Morning notification: "You have 45 cards due for review!"
- Show "Review Due Cards" button prominently when cards are due

---

## Implementation Priority

### Phase 1: Quick Wins (1 week)
1. ✅ Fix auto-play interrupt
2. ✅ Fix Study Again button
3. ⏳ Deck Progress Cards (Issue 3.1)
4. ⏳ Review Filters (Issue 4.1)

### Phase 2: Enhanced Tracking (2 weeks)
5. CEFR Level Overview (Issue 3.2)
6. Card Tags/Labels (Issue 4.2)

### Phase 3: Advanced Features (3 weeks)
7. Study History Calendar (Issue 3.3)
8. Smart Review Scheduling (Issue 4.3)

---

## Next Steps

### Immediate Action Items:

1. **Add Deck Progress API** (30 minutes)
   ```python
   # In views_flashcard.py
   @action(detail=True, methods=['get'])
   def progress(self, request, pk=None):
       deck = self.get_object()
       stats = get_deck_progress(request.user, deck)
       return Response(stats)
   ```

2. **Update Dashboard to Show Progress** (1 hour)
   - Add progress bars to deck cards
   - Show learned/total cards
   - Color-code by completion level

3. **Add Review Filter to start_session** (1 hour)
   ```python
   def start_session(self, request):
       review_type = request.data.get('review_type', 'normal')  # normal, due, difficult, failed
       
       if review_type == 'difficult':
           cards = get_difficult_cards(request.user, limit=card_count)
       elif review_type == 'failed':
           cards = get_failed_cards(request.user, limit=card_count)
       else:
           cards = get_cards_for_study(...)
   ```

4. **Add Progress Summary to Completion Screen** (30 minutes)
   ```html
   <div class="deck-progress-summary">
       <h5>Your Progress in {{ deck.name }}</h5>
       <p>You've now mastered {{ mastered_count }}/{{ total_cards }} cards!</p>
       <div class="progress">
           <div class="progress-bar" style="width: {{ progress }}%"></div>
       </div>
   </div>
   ```

---

## Database Schema Already Supports This

Good news! The `UserFlashcardProgress` model already tracks:
- ✅ `easiness_factor` - Difficulty level (SM-2 algorithm)
- ✅ `interval_days` - Review interval (0 = failed, 1+ = learning)
- ✅ `next_review_date` - When card is due
- ✅ `is_mastered` - Whether user has mastered the card
- ✅ `total_reviews` - How many times reviewed
- ✅ `consecutive_correct` - Streak of correct answers

**We just need to expose this data in the UI!**

---

## Quick Mockup: Dashboard with Progress

```
┌─────────────────────────────────────────────┐
│  📚 Your Flashcard Progress                │
├─────────────────────────────────────────────┤
│                                             │
│  🎯 Overall Progress                        │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 45%  │
│  2,387 / 5,311 cards learned               │
│                                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐    │
│  │   A1    │  │   A2    │  │   B1    │    │
│  │ ████████│  │ ████▁▁▁▁│  │ ██▁▁▁▁▁▁│    │
│  │  100%   │  │   52%   │  │   25%   │    │
│  │898/898  │  │450/866  │  │202/807  │    │
│  └─────────┘  └─────────┘  └─────────┘    │
│                                             │
│  📌 Quick Actions                           │
│  • 45 cards due for review today            │
│  • 12 difficult cards need attention        │
│  • 5 cards failed last session              │
│                                             │
└─────────────────────────────────────────────┘
```

---

## User Story Examples

### Story 1: Maria wants to see her progress
**Before**: "I don't know how many words I've learned. Am I making progress?"
**After**: Opens dashboard → Sees "You've learned 2,387/5,311 words (45%)" → "Wow, I'm almost done with A2!"

### Story 2: John failed some difficult words
**Before**: Hard words get mixed with easy ones. He forgets which ones he struggled with.
**After**: Clicks "Review Difficult Cards (12)" → Gets focused practice on his weak points

### Story 3: Sarah completed a session
**Before**: "Study Again" → Goes to deck selector → "Wait, which deck was I studying?"
**After**: "Study Same Deck Again" → Immediately starts new session with same deck

---

## Technical Debt to Address

1. **Missing indexes** for faster queries:
   ```python
   class Meta:
       indexes = [
           models.Index(fields=['user', 'next_review_date']),
           models.Index(fields=['user', 'is_mastered']),
           models.Index(fields=['flashcard', 'user']),
       ]
   ```

2. **Caching** for expensive queries:
   ```python
   from django.core.cache import cache
   
   def get_user_progress_summary(user):
       cache_key = f'progress_summary_{user.id}'
       cached = cache.get(cache_key)
       if cached:
           return cached
       
       summary = calculate_progress(user)
       cache.set(cache_key, summary, timeout=3600)  # 1 hour
       return summary
   ```

---

## Estimated Timeline

**Week 1**: Issues 1-2 (✅ Done!) + Issue 3.1 + Issue 4.1
**Week 2**: Issue 3.2 + Issue 4.2
**Week 3-4**: Issue 3.3 + Issue 4.3

**Total**: ~4 weeks for complete implementation
