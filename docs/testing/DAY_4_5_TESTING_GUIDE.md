# DAY 4-5 TESTING GUIDE
# Frontend Pages Testing Checklist

## Prerequisites
- Django development server running (`python manage.py runserver`)
- User account created and logged in
- At least 10 phonemes in database
- At least 5 minimal pairs in database

---

## Test 1: Discovery Page Load

### URL: `/pronunciation/discovery/`

**Expected Results:**
- [ ] Page loads without 404 or 500 errors
- [ ] Hero section displays with title "Khám Phá 44 Âm IPA"
- [ ] Progress overview shows 4 stat cards
- [ ] Stage legend shows 6 stages with colored icons
- [ ] Category tabs show: All, Nguyên âm, Phụ âm, Nguyên âm đôi
- [ ] Phoneme grid displays with cards
- [ ] No console errors in browser DevTools

**Console Commands:**
```javascript
// Check if Vue app mounted
console.log(document.querySelector('#discoveryApp').__vue_app__)

// Check if phonemes loaded
console.log(localStorage.getItem('phonemes'))

// Check API call
fetch('/api/v1/pronunciation/phonemes/')
  .then(r => r.json())
  .then(d => console.log(d))
```

---

## Test 2: Discovery Page - Filtering

**Steps:**
1. Click "Nguyên âm" tab
2. Observe grid filters to show only vowels
3. Click "Phụ âm" tab
4. Observe grid filters to show only consonants
5. Click "Nguyên âm đôi" tab
6. Observe grid filters to show only diphthongs
7. Click "Tất cả" tab
8. Observe grid shows all phonemes again

**Expected Results:**
- [ ] Grid updates without page reload
- [ ] Active tab has orange background
- [ ] Phoneme count in tab label is correct
- [ ] No flicker or lag when switching tabs

---

## Test 3: Discovery Page - Phoneme Modal

**Steps:**
1. Click any phoneme card
2. Modal opens
3. Check modal contains:
   - Large IPA symbol
   - Vietnamese approximation
   - Current status (if discovered)
   - Description text
   - Action button

**Expected Results:**
- [ ] Modal opens smoothly (fade-in animation)
- [ ] Backdrop appears (semi-transparent black)
- [ ] Modal shows correct phoneme data
- [ ] Close button (X) works
- [ ] Clicking backdrop closes modal

---

## Test 4: Discovery Action - Mark as Discovered

**Steps:**
1. Click a phoneme card that is "Chưa bắt đầu"
2. Click "Khám phá ngay" button in modal
3. Wait for API call to complete
4. Check success message appears
5. Check redirect to learning page

**Expected Results:**
- [ ] Button shows loading spinner during API call
- [ ] Success alert appears (green toast)
- [ ] Modal closes after 1 second
- [ ] Redirects to `/pronunciation/learning/{id}/`
- [ ] Phoneme card updates to "Đã khám phá" state (orange border)

**API Check:**
```bash
# Backend logs should show:
# POST /api/v1/pronunciation/phoneme/1/discover/ 201 CREATED
```

---

## Test 5: Learning Page Load

### URL: `/pronunciation/learning/1/` (replace 1 with valid phoneme ID)

**Expected Results:**
- [ ] Page loads without errors
- [ ] Header shows large IPA symbol
- [ ] Progress stepper shows 4 stages
- [ ] Current stage is highlighted (active)
- [ ] Audio player section visible
- [ ] Pronunciation tips list shows 5-6 items
- [ ] Example words grid displays
- [ ] Sidebar shows action card

**Console Check:**
```javascript
// Check phoneme data loaded
console.log(window.__phonemeData__)

// Check progress data
console.log(window.__progressData__)
```

---

## Test 6: Learning Page - Audio Playback

**Steps:**
1. Click the large play button
2. Audio should play
3. Button changes to pause icon
4. Button has pulse animation while playing
5. Click pause button
6. Audio stops

**Expected Results:**
- [ ] Audio file loads (check network tab)
- [ ] Play button transforms to pause button
- [ ] Pulse animation visible during playback
- [ ] Audio ends naturally, button returns to play
- [ ] Clicking pause stops audio immediately

**Debug:**
```javascript
// Check audio element
let audio = document.querySelector('audio')
console.log(audio.src)  // Should be audio URL
console.log(audio.duration)  // Should be > 0
audio.play()  // Should play audio
```

---

## Test 7: Learning Page - Start Learning Action

**Steps:**
1. Ensure phoneme is in "discovered" or "learning" stage
2. Click "Bắt đầu học" button in sidebar
3. Wait for API call
4. Check success message
5. Check redirect to discrimination page

**Expected Results:**
- [ ] Button shows loading spinner
- [ ] Success alert appears
- [ ] Redirects to `/pronunciation/discrimination/{id}/`
- [ ] (Currently will show 404 - expected, page not built yet)

**API Check:**
```bash
# Backend logs should show:
# POST /api/v1/pronunciation/phoneme/1/start-learning/ 200 OK
```

---

## Test 8: Responsive Design - Mobile

**Viewports to Test:**
- 320px (iPhone SE)
- 375px (iPhone 12)
- 768px (iPad)
- 1024px (iPad Pro)
- 1920px (Desktop)

**Steps:**
1. Open DevTools
2. Toggle device toolbar (Ctrl+Shift+M)
3. Test each viewport size

**Expected Results:**
- [ ] Discovery grid: 2-3 columns on mobile, 4+ on desktop
- [ ] Progress cards: Stack vertically on mobile
- [ ] Modal: Full-width on mobile, centered on desktop
- [ ] Learning page: Single column on mobile, 2 columns on desktop
- [ ] Text is readable (min 14px)
- [ ] Buttons are touch-friendly (min 44px height)

---

## Test 9: Authentication

**Steps:**
1. Open incognito/private browsing window
2. Navigate to `/pronunciation/discovery/`
3. Should redirect to login page

**Expected Results:**
- [ ] Redirects to `/login/?next=/pronunciation/discovery/`
- [ ] After login, returns to discovery page
- [ ] No flash of unauthenticated content

---

## Test 10: Error Handling

### Test API Failure:
**Steps:**
1. Open DevTools Network tab
2. Block all `/api/v1/pronunciation/` requests (offline mode)
3. Reload discovery page
4. Check error message appears

**Expected Results:**
- [ ] Page shows loading spinner initially
- [ ] After timeout, shows error message
- [ ] Error is user-friendly (Vietnamese)
- [ ] Provides retry action

### Test Invalid Phoneme ID:
**Steps:**
1. Navigate to `/pronunciation/learning/99999/`
2. Should show 404 page

**Expected Results:**
- [ ] Returns 404 status code
- [ ] Shows custom 404 template (if exists)
- [ ] Or shows Django default 404 page

---

## Test 11: Performance

**Metrics to Check:**
- [ ] Discovery page loads in < 2 seconds
- [ ] Learning page loads in < 1 second
- [ ] API calls return in < 500ms (local)
- [ ] No memory leaks (check DevTools Memory)
- [ ] Smooth animations (60 FPS)

**Tools:**
- Chrome DevTools Lighthouse
- Network tab (check payload sizes)
- Performance tab (check rendering)

---

## Test 12: Browser Compatibility

**Browsers to Test:**
- [ ] Chrome 120+ (primary)
- [ ] Firefox 120+ (primary)
- [ ] Safari 17+ (macOS/iOS)
- [ ] Edge 120+ (secondary)

**Expected:**
- CSS Grid works
- Fetch API works
- Vue.js 3 works
- Audio playback works
- No major visual bugs

---

## Bug Reporting Template

```markdown
## Bug Report

**Page:** Discovery / Learning
**Severity:** Critical / High / Medium / Low
**Browser:** Chrome 120.0
**Viewport:** 1920x1080

**Steps to Reproduce:**
1. Step 1
2. Step 2
3. Step 3

**Expected Result:**
What should happen

**Actual Result:**
What actually happened

**Screenshots:**
(attach if applicable)

**Console Errors:**
```
Error messages here
```

**Network Errors:**
```
API call details
```
```

---

## Common Issues & Fixes

### Issue 1: "Cannot read property 'ipa_symbol' of undefined"
**Cause:** Phoneme data not loaded from backend  
**Fix:** Check `phoneme_json` template variable is properly JSON-serialized  

### Issue 2: Audio not playing
**Cause:** Audio file doesn't exist or path is wrong  
**Fix:** Check `phoneme.audio_url` is valid, check media files exist  

### Issue 3: Modal doesn't open
**Cause:** Bootstrap JS not loaded or wrong version  
**Fix:** Check Bootstrap 5 bundle.js is included in base template  

### Issue 4: Vue not mounting
**Cause:** Vue.js CDN failed to load or syntax error  
**Fix:** Check browser console for errors, check CDN URL is correct  

### Issue 5: API returns 401 Unauthorized
**Cause:** Access token expired or missing  
**Fix:** Check localStorage has access_token, check auth.js is included  

---

## Next Steps After Testing

### If All Tests Pass:
✅ Day 4 Complete  
✅ Move to Day 5 (minor fixes and prepare for Day 6-7)

### If Tests Fail:
1. Document all bugs found
2. Prioritize by severity
3. Fix critical bugs first
4. Re-test after each fix
5. Update this checklist

---

## Automation Script (Optional)

```bash
#!/bin/bash
# test_pronunciation_pages.sh

echo "Testing pronunciation pages..."

# Test 1: Discovery page loads
curl -s -o /dev/null -w "Discovery Page: %{http_code}\n" \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/pronunciation/discovery/

# Test 2: Learning page loads
curl -s -o /dev/null -w "Learning Page: %{http_code}\n" \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/pronunciation/learning/1/

# Test 3: API endpoints
curl -s -o /dev/null -w "Phoneme List API: %{http_code}\n" \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/pronunciation/phonemes/

curl -s -o /dev/null -w "Overall Progress API: %{http_code}\n" \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/pronunciation/progress/overall/

echo "Testing complete!"
```

---

## Success Criteria

**Day 4-5 is complete when:**
- ✅ All 12 tests pass
- ✅ No critical bugs found
- ✅ Mobile responsive (tested on 3+ devices)
- ✅ Performance acceptable (< 2s load time)
- ✅ API integration working (200 status codes)
- ✅ Error handling graceful
- ✅ Documentation updated

**Current Status:** 🟡 Ready for Testing  
**Estimated Testing Time:** 2-3 hours
