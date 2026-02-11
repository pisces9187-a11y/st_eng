# Quick Start Guide - Phase 1 + Phase 2 Features

## 🚀 Start in 3 Steps

### 1. Start Server
```bash
cd /home/n2t/Documents/english_study/backend
python3 manage.py runserver 0.0.0.0:8000
```

### 2. Open Browser
```
http://localhost:8000/vocabulary/flashcards/study/
```

### 3. Start Studying!

---

## 📖 Feature Guide

### 🔄 Recent Decks Carousel

**What it does**: Shows your 5 most recently studied decks

**How to use**:
1. Look at the top of the deck selection screen
2. See your recent decks with progress rings
3. Click any deck to instantly resume studying

**What you'll see**:
- 📚 Oxford A1 - 17.5% progress
- ✅ 157 cards learning
- 🕐 "2 hours ago"

---

### 🎯 Review Modes

**What it does**: Study only the cards you need

**Modes**:
1. **Normal** (⚪ Blue): Mix of due cards + new cards
2. **Difficult** (🔴 Red): Only cards you struggle with
3. **Due** (🟡 Yellow): Only cards due for review today

**How to use**:
1. Select a review mode (radio buttons)
2. Choose your deck
3. Click "Start Study Session"

**When to use each**:
- Use **Normal** for daily study
- Use **Difficult** before exams
- Use **Due** to maintain retention

---

### ⭐ Tag Difficult Cards

**What it does**: Mark cards for later review

**How to use**:
1. During study, see a hard word?
2. Click the ⭐ button (top-right of card)
3. Button turns red ✅
4. Card is saved to "Difficult" collection

**Find your tagged cards**:
- Use "Difficult" review mode
- Shows only cards you tagged

---

### 📊 Progress Indicators

**What it does**: Visual progress for each deck

**What you see**:
- 🟢 Progress ring (0-100%)
- ✅ **50** Mastered (green)
- 📖 **100** Learning (yellow)
- 🆕 **300** New (gray)

**Progress updates**:
- After each study session
- Real-time on deck cards
- Recent decks carousel

---

### 📈 Enhanced Deck Info

**What it does**: Shows your study history

**Information displayed**:
- Total cards in deck
- Session history count
- Progress percentage
- Cards breakdown

**Example**:
```
📚 Oxford A1 - Selected
898 cards | 24 sessions | 17.5% complete
```

---

## 🎮 Complete Workflow Example

### Scenario: Study for 10 minutes

1. **Open Page**
   ```
   → See recent decks carousel
   → See Oxford A1 at 17.5%
   ```

2. **Choose What to Study**
   ```
   → Click "Difficult" mode
   → Select Oxford A1
   → Info shows: "898 cards | 24 sessions"
   ```

3. **Start Session**
   ```
   → Click "Start Study Session"
   → System loads 20 difficult cards
   ```

4. **Study Cards**
   ```
   → Flip card (Space or Click)
   → See hard word? → Click ⭐ button
   → Rate card: Again/Hard/Good/Easy
   ```

5. **Complete**
   ```
   → See session summary
   → Progress updated: 17.5% → 18.2%
   → Click "Study Same Deck Again"
   ```

6. **Next Time**
   ```
   → Return to page
   → See Oxford A1 in recent decks
   → Progress ring shows 18.2%
   → 1 more card marked as difficult
   ```

---

## 💡 Pro Tips

### Maximize Learning
- ✅ Use **Normal mode** daily (builds foundation)
- ✅ Switch to **Difficult mode** weekly (reinforcement)
- ✅ Tag cards during first encounter (don't wait)

### Track Progress
- 📊 Watch progress rings fill up
- 🎯 Aim for 80%+ mastery before moving levels
- 🔄 Review recent decks to maintain skills

### Efficient Study
- ⏱️ Study 20 cards per session (10-15 minutes)
- 🎯 Focus on one deck until 50% mastery
- 🔁 Use "Due" mode to prevent forgetting

---

## 🎯 Study Goals

### Beginner (First Week)
- [ ] Complete 5 sessions in Oxford A1
- [ ] Tag 10+ difficult words
- [ ] Reach 10% progress in A1

### Intermediate (First Month)
- [ ] Master 100+ A1 words (green)
- [ ] Start Oxford A2
- [ ] Use all 3 review modes

### Advanced (3 Months)
- [ ] Complete Oxford A1 (80%+ mastery)
- [ ] Progress through A2 & B1
- [ ] Maintain streak with "Due" mode

---

## 🐛 Troubleshooting

### Recent Decks Don't Show
**Cause**: No study history yet  
**Solution**: Complete at least 1 session

### Progress Ring Shows 0%
**Cause**: No cards rated yet  
**Solution**: Rate cards during study

### Tag Button Doesn't Work
**Cause**: Not logged in  
**Solution**: Check JWT token in browser localStorage

### "No cards available"
**Cause**: Selected "Difficult" but no difficult cards  
**Solution**: Use "Normal" mode first to build history

---

## 🎉 You're Ready!

All features are working and tested ✅

**Start studying now**: [http://localhost:8000/vocabulary/flashcards/study/](http://localhost:8000/vocabulary/flashcards/study/)

**Questions?** Check [PHASE1_PHASE2_COMPLETE.md](PHASE1_PHASE2_COMPLETE.md) for full technical details.
