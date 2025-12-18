# Quick Browser Testing Guide

## Server Status
- **Django Server:** Running at http://localhost:8000
- **Status:** Ready for testing

## Test URLs

### Discovery Page
```
http://localhost:8000/pronunciation/discovery/
```
**Tests:**
- [ ] Page loads without errors
- [ ] Phoneme grid displays
- [ ] Category filtering works
- [ ] Modal opens on click

### Learning Page (Phoneme #1)
```
http://localhost:8000/pronunciation/learning/1/
```
**Tests:**
- [ ] Page loads phoneme details
- [ ] Audio player works
- [ ] Progress stepper displays
- [ ] Next button navigates to learning/2/

### Progress Dashboard
```
http://localhost:8000/pronunciation/dashboard/
```
**Tests:**
- [ ] Stats display
- [ ] Progress bars show
- [ ] Quick actions available

## Console Testing (F12 → Console)

### Expected Results
- ✅ 0 JavaScript errors
- ✅ 0 "Auth is not defined" messages
- ✅ Warnings only (if any) about unused CSS/deprecations
- ✅ Network tab shows all requests returning 200-204

### Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| Auth errors | Hard refresh (Ctrl+F5) and clear cache |
| API errors | Check Django server is running |
| Page not loading | Check Network tab for 404 errors |
| No data in grid | Check if phonemes exist in database |

## Testing Workflow

1. **Start Server**
   ```bash
   cd backend
   python manage.py runserver
   ```

2. **Open Discovery Page**
   - Browser: http://localhost:8000/pronunciation/discovery/
   - Check: No console errors

3. **Click a Phoneme**
   - Check: Modal dialog opens
   - Check: Phoneme details display

4. **Click "Khám phá ngay"**
   - Check: Page navigates to learning page
   - Check: Phoneme details load

5. **Test Navigation**
   - Click next/previous buttons
   - Check: Different phoneme loads
   - Check: No errors in console

6. **Visit Dashboard**
   - Browser: http://localhost:8000/pronunciation/dashboard/
   - Check: Stats display
   - Check: No console errors

## Critical Verification Points

### JavaScript Initialization
```javascript
// In Console, should be able to run:
console.log(typeof Auth);           // "object"
console.log(typeof ApiClient);      // "object"
console.log(typeof AppConfig);      // "object"
console.log(typeof Vue);            // "function"
```

### Authentication Check
```javascript
// In Console:
Auth.isAuthenticated()              // true (if logged in)
Auth.getToken()                     // returns bearer token
```

### API Client Check
```javascript
// In Console:
ApiClient.get('/api/v1/pronunciation/phonemes/').then(r => console.log(r))
// Should return { success: true, data: [...], message: "..." }
```

## Expected Output

### Discovery Page Response
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "ipa": "/p/",
      "examples": "pen, apple, happy",
      "progress": {
        "current_stage": "discovered",
        "accuracy": 0
      }
    },
    // ... 43 more phonemes
  ],
  "message": "Phonemes retrieved successfully"
}
```

### Learning Page Response
```json
{
  "success": true,
  "data": {
    "id": 1,
    "ipa": "/p/",
    "description": "Voiceless bilabial plosive",
    "tips": [
      "Close both lips",
      "Release air suddenly"
    ],
    "examples": [
      "pen", "apple", "happy"
    ]
  },
  "message": "Phoneme details retrieved"
}
```

## If You See Errors

### "ReferenceError: Auth is not defined"
- **Status:** Should NOT see this - it's fixed!
- **If seen:** Hard refresh (Ctrl+Shift+Delete → Clear Cache → Refresh)

### "Cannot read property 'get' of undefined"
- **Issue:** ApiClient not loaded
- **Fix:** Check Network tab → ensure api.js loaded before page scripts

### "Cannot GET /api/v1/pronunciation/phonemes/"
- **Issue:** API endpoint not working
- **Fix:** Check Django server logs for errors

### "TemplateDoesNotExist"
- **Issue:** Template file missing
- **Fix:** All templates created - shouldn't happen

## Success Indicators

✅ **Page loads without errors**
- No red text in Console
- Page renders with CSS styling
- Interactive elements respond to clicks

✅ **Data displays correctly**
- Phoneme grid shows 44 items
- Stats show current progress
- Audio player is visible

✅ **API integration works**
- Network tab shows GET/POST requests
- Responses are 200-204 status
- Response JSON is valid

✅ **Authentication works**
- Logged in users can access pages
- Logged out users redirected to /login/
- Auth token included in requests

✅ **No console errors**
- Console is clean (0 red messages)
- Only info/log messages visible
- Warnings are acceptable

## Performance Notes

### Expected Load Times
- Discovery page: < 1 second
- Learning page: < 1 second
- API response: < 200ms

### Expected Network Requests
- Discovery page: 4-5 requests (HTML, CSS, JS, API)
- Learning page: 5-6 requests (HTML, CSS, JS, API, audio)
- Total page size: < 500KB

## Next Actions

1. **If all tests pass:**
   - ✅ Day 4 complete and verified
   - Move to Day 5 (minor refinements)
   - Proceed to Day 6-7 (Discrimination UI)

2. **If any test fails:**
   - Review error message in Console
   - Check Network tab for failed requests
   - Restart Django server
   - Clear browser cache (Ctrl+Shift+Delete)
   - Try again

---

**All tests should pass with 0 JavaScript errors.**

If you encounter any issues, refer to [AUTH_LOADING_FIX.md](AUTH_LOADING_FIX.md) for troubleshooting.
