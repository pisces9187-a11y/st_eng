# GitHub Copilot Instructions - EnglishMaster Project

> **⚠️ CRITICAL**: All development MUST follow [DEVELOPMENT_WORKFLOW.md](/DEVELOPMENT_WORKFLOW.md)
> Read this workflow document before implementing ANY feature.

---

## 🎯 Project Overview

**Project Name:** EnglishMaster  
**Stack:** Django 5.2.9 + Bootstrap 5 + Vue.js 3  
**Purpose:** E-learning platform for teaching English pronunciation to Vietnamese learners  
**Architecture:** Monolithic Django with Vue.js frontend components

---

## 📋 MANDATORY WORKFLOW - 7 PHASES

### ⚠️ BEFORE ANY IMPLEMENTATION

1. **Read Requirements Carefully** - Use template in DEVELOPMENT_WORKFLOW.md Phase 1
2. **Ask Clarifying Questions** - Don't assume, always confirm with user
3. **Check Existing Code** - Review models, APIs, templates for reuse
4. **Design First, Code Later** - Complete Phase 2 & 3 before Phase 4
5. **Test Everything** - Phase 5 is NOT optional

### Phase Order (STRICT)
```
1. Requirements Analysis → Ask questions, clarify edge cases
2. Architecture Design   → Check models, plan APIs, verify field names
3. UI/UX Design         → Follow design system, reuse components
4. Implementation       → Code in ORDER: Models→APIs→Views→Templates
5. Testing              → Unit tests + Integration tests (mandatory)
6. Review & Validation  → Run all checklists
7. Documentation        → Update docs, write feature summary
```

**🚨 DO NOT SKIP PHASES. DO NOT CODE BEFORE DESIGN.**

---

## 🏗️ Project Structure

> **⚠️ CRITICAL ORGANIZATION RULES**:
> - Templates MUST be organized by app
> - Tests MUST follow Django structure
> - Documentation MUST be categorized
> - See [PROJECT_ORGANIZATION_ANALYSIS.md](/docs/PROJECT_ORGANIZATION_ANALYSIS.md) for details

```
english_study/
├── backend/
│   ├── apps/
│   │   ├── curriculum/          # Course, Lesson, Phoneme, Quiz models
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views_[module].py  # Organized by feature
│   │   │   ├── api/
│   │   │   │   └── [module]_api.py
│   │   │   ├── management/
│   │   │   │   └── commands/
│   │   │   │       ├── seed_phonemes.py
│   │   │   │       └── generate_audio.py
│   │   │   └── admin.py
│   │   │
│   │   ├── users/               # User, Profile, Progress models
│   │   │   └── [same structure]
│   │   │
│   │   └── study/               # Study sessions, Analytics
│   │       └── [same structure]
│   │
│   ├── tests/                   # ⚠️ NEW: Organized test structure
│   │   ├── conftest.py          # Shared fixtures
│   │   ├── curriculum/
│   │   │   ├── models/
│   │   │   │   └── test_phoneme.py
│   │   │   ├── api/
│   │   │   │   └── test_pronunciation_api.py
│   │   │   ├── services/
│   │   │   │   └── test_edge_tts.py
│   │   │   ├── views/
│   │   │   │   └── test_pronunciation_views.py
│   │   │   └── integration/
│   │   │       └── test_audio_flow.py
│   │   ├── users/
│   │   │   └── [same structure]
│   │   └── study/
│   │       └── [same structure]
│   │
│   ├── backend/                 # Django settings
│   │   ├── settings.py
│   │   └── urls.py
│   │
│   ├── templates/               # ⚠️ NEW: App-organized templates
│   │   ├── base/
│   │   │   ├── _base.html       # Base template
│   │   │   ├── _base_public.html
│   │   │   └── _base_admin.html
│   │   │
│   │   ├── components/          # Shared components
│   │   │   ├── _navbar.html
│   │   │   └── _footer.html
│   │   │
│   │   ├── errors/
│   │   │   ├── 404.html
│   │   │   └── 500.html
│   │   │
│   │   ├── curriculum/          # Curriculum app templates
│   │   │   ├── pronunciation/
│   │   │   │   ├── discovery.html
│   │   │   │   ├── learning.html
│   │   │   │   └── lesson_detail.html
│   │   │   ├── phoneme/
│   │   │   │   ├── chart.html
│   │   │   │   └── detail.html
│   │   │   ├── discrimination/
│   │   │   │   ├── start.html
│   │   │   │   ├── quiz.html
│   │   │   │   └── results.html
│   │   │   └── production/
│   │   │       ├── record.html
│   │   │       └── history.html
│   │   │
│   │   ├── users/               # Users app templates
│   │   │   ├── profile.html
│   │   │   └── settings.html
│   │   │
│   │   ├── study/               # Study app templates
│   │   │   └── dashboard.html
│   │   │
│   │   └── public/              # Public pages
│   │       ├── home.html
│   │       └── about.html
│   │
│   ├── static/
│   │   ├── css/
│   │   │   ├── base.css         # Global styles + CSS variables
│   │   │   └── components.css   # Component library
│   │   ├── js/
│   │   │   ├── config.js        # Load FIRST
│   │   │   ├── api.js           # ApiClient class
│   │   │   ├── auth.js          # Auth class with polling
│   │   │   └── utils.js         # Utilities
│   │   └── images/
│   │
│   ├── media/                   # User uploads
│   │   ├── phonemes/
│   │   │   ├── audio/
│   │   │   └── diagrams/
│   │   └── lessons/
│   │
│   └── manage.py
│
├── docs/                        # ⚠️ NEW: Organized documentation
│   ├── README.md                # Documentation index
│   ├── project/                 # Project-level docs
│   ├── standards/               # Development standards
│   ├── architecture/            # System architecture
│   ├── curriculum/              # Curriculum app docs
│   │   └── audio/               # Audio subsystem docs
│   ├── users/                   # Users app docs
│   ├── study/                   # Study app docs
│   ├── testing/                 # Testing guides
│   ├── changelog/               # Change logs
│   └── examples/                # Code examples
├── tests/                       # Integration tests
└── DEVELOPMENT_WORKFLOW.md      # **MAIN GUIDE - READ THIS**
```

---

## 🚨 COMMON MISTAKES TO AVOID

### 1. AttributeError - Wrong Field Names

**❌ WRONG:**
```python
# views.py
'audio_url': phoneme.audio_url  # Field doesn't exist!
'description': phoneme.description  # Wrong field name!
```

**✅ CORRECT:**
```python
# ALWAYS check model first!
# File: apps/curriculum/models.py, class Phoneme

'audio_sample': phoneme.audio_sample.url if phoneme.audio_sample else None
'pronunciation_tips': phoneme.pronunciation_tips_vi or phoneme.pronunciation_tips
```

**Prevention Steps:**
1. ✅ Before coding, run: `grep -A 50 "class ModelName" apps/*/models.py`
2. ✅ List ALL fields in model
3. ✅ Copy-paste exact field names
4. ✅ NEVER guess field names

---

### 2. TemplateDoesNotExist

**❌ WRONG:**
```python
return render(request, 'pronunciation_page.html')  # Missing 'pages/' prefix!
```

**✅ CORRECT:**
```python
# ALWAYS use 'pages/' prefix for feature pages
return render(request, 'pages/pronunciation_page.html')

# File must exist: backend/templates/pages/pronunciation_page.html
```

**Prevention Steps:**
1. ✅ Create template file BEFORE writing view
2. ✅ Use consistent naming: `pages/[feature]_[action].html`
3. ✅ Check file exists before rendering

---

### 3. API Response Structure Mismatch

**❌ WRONG:**
```javascript
// Frontend assumes flat array
this.phonemes = response;  
// But API returns: {success: true, categories: [{phonemes: [...]}]}
```

**✅ CORRECT:**
```javascript
// ALWAYS test API endpoint first with curl/Postman
// Document response structure in design phase

const response = await ApiClient.get('/pronunciation/phonemes/');
if (response.categories) {
    // Flatten nested structure
    let allPhonemes = [];
    response.categories.forEach(cat => {
        allPhonemes = allPhonemes.concat(cat.phonemes || []);
    });
    this.phonemes = allPhonemes;
}
```

**Prevention Steps:**
1. ✅ Test API with curl before frontend code
2. ✅ Document response structure in Phase 2
3. ✅ Add response validation in frontend

---

### 4. Field Name Inconsistency Between Models

**❌ WRONG:**
```python
# Model: UserPhonemeProgress
discrimination_accuracy = models.FloatField()

# View (WRONG!)
'discrimination_score': progress.discrimination_score  # Different name!
```

**✅ CORRECT:**
```python
# Use EXACT field name from model
'discrimination_accuracy': progress.discrimination_accuracy
'discrimination_attempts': progress.discrimination_attempts
'production_best_score': progress.production_best_score  # Not 'production_score'
'times_practiced': progress.times_practiced  # Not 'practice_count'
```

---

## 📐 NAMING CONVENTIONS

### Python/Django (snake_case)
```python
# Models
class UserPhonemeProgress(models.Model):
    discrimination_accuracy = models.FloatField()  # ✅
    audio_sample = models.FileField()              # ✅
    
    # ❌ NEVER:
    discriminationAccuracy = ...  # NO camelCase
    audio-sample = ...            # NO hyphens

# Views
def pronunciation_learning_view(request, phoneme_id):  # ✅
def pronunciationLearning(request):                    # ❌

# Variables
user_progress = ...   # ✅
userProgress = ...    # ❌
```

### URLs (kebab-case for paths, snake_case for names)
```python
# urls.py
urlpatterns = [
    # Page URLs
    path('pronunciation/discovery/', views.view, name='pronunciation_discovery'),  # ✅
    path('pronunciation-learning/<int:id>/', views.view, name='lesson_detail'),    # ✅
    
    # API URLs
    path('api/v1/pronunciation/phonemes/', api_views.List.as_view()),              # ✅
    
    # ❌ NEVER:
    path('pronunciationDiscovery/', ...),   # NO camelCase in URL
    path('api/getPhonemesData/', ...),      # NO camelCase, always use /api/v1/
]
```

### JavaScript/Vue.js (camelCase)
```javascript
// Vue.js data/methods
data() {
    return {
        currentPhoneme: null,      // ✅ camelCase
        isLoading: false,          // ✅
        phonemeList: []            # ✅
    }
},
methods: {
    loadPhonemeData() { },         // ✅ camelCase
    async fetchUserProgress() { }  // ✅
}

// ❌ NEVER use snake_case in JavaScript:
load_phoneme_data() { }            // ❌
```

### Templates (kebab-case for files)
```
templates/
├── pages/
│   ├── pronunciation-discovery.html    # ✅ kebab-case
│   ├── lesson-detail.html              # ✅
│   └── user-profile.html               # ✅
│
└── components/
    └── phoneme-card.html               # ✅
```

---

## 🎨 DESIGN SYSTEM (STRICT)

### Colors (MUST USE CSS Variables)
```css
/* backend/static/css/base.css */

:root {
    /* Primary Colors - DON'T CHANGE */
    --primary-color: #667eea;
    --primary-dark: #5568d3;
    --primary-light: #8196f3;
    
    /* Secondary Colors */
    --secondary-color: #764ba2;
    --accent-color: #f093fb;
    
    /* Semantic Colors */
    --success-color: #10b981;
    --warning-color: #f59e0b;
    --error-color: #ef4444;
    --info-color: #3b82f6;
}

/* ✅ CORRECT Usage */
.button-primary {
    background: var(--primary-color);  /* Use variable */
}

/* ❌ WRONG - Hardcoded colors */
.button {
    background: #667eea;  /* DON'T hardcode! */
}
```

### Typography
```css
/* Font Families */
--font-primary: 'Inter', -apple-system, sans-serif;
--font-heading: 'Poppins', sans-serif;

/* Font Sizes (use these, don't make new ones) */
--fs-xs: 0.75rem;    /* 12px */
--fs-sm: 0.875rem;   /* 14px */
--fs-base: 1rem;     /* 16px */
--fs-lg: 1.125rem;   /* 18px */
--fs-xl: 1.25rem;    /* 20px */
```

### Spacing (8px base grid)
```css
/* Use these for margin/padding */
--space-2: 0.5rem;   /* 8px */
--space-4: 1rem;     /* 16px */
--space-6: 2rem;     /* 32px */
--space-8: 3rem;     /* 48px */
```

---

## 🔧 VUE.JS INTEGRATION

### Template Structure (MANDATORY)
```html
{% extends "base/_base.html" %}
{% load static %}

{% block extra_head %}
<style>
/* Component-specific styles */
</style>
{% endblock %}

{% block content %}
<div id="featureApp" v-cloak>
    <!-- ⚠️ MUST use [[ ]] delimiters, NOT {{ }} -->
    <h1>[[ title ]]</h1>
    
    <div v-for="item in items" :key="item.id">
        <p>[[ item.name ]]</p>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
const { createApp } = Vue;

createApp({
    delimiters: ['[[', ']]'],  // ⚠️ REQUIRED - avoid conflict with Django
    
    data() {
        return {
            // ⚠️ Parse JSON safely
            initialData: {{ data_json|safe }},
            items: [],
            loading: false
        }
    },
    
    methods: {
        async loadData() {
            try {
                // ⚠️ Use ApiClient, NOT fetch()
                const response = await ApiClient.get('/api/v1/resource/');
                
                // ⚠️ Check response structure
                if (response.success) {
                    this.items = response.data;
                }
            } catch (error) {
                console.error('Error:', error);
            }
        }
    },
    
    async mounted() {
        // ⚠️ ALWAYS wait for Auth
        await Auth.waitUntilReady();
        
        if (Auth.isAuthenticated()) {
            await this.loadData();
        }
    }
}).mount('#featureApp');
</script>
{% endblock %}
```

### Script Loading Order (CRITICAL)
```html
<!-- base/_base.html -->
<script src="{% static 'js/config.js' %}"></script>      <!-- 1. FIRST -->
<script src="{% static 'js/api.js' %}"></script>         <!-- 2. -->
<script src="{% static 'js/auth.js' %}"></script>        <!-- 3. -->
<script src="{% static 'js/utils.js' %}"></script>       <!-- 4. -->
<script src="https://cdn.jsdelivr.net/npm/vue@3"></script> <!-- 5. -->

<!-- ❌ WRONG ORDER causes Auth race conditions -->
```

---

## 📝 CODE IMPLEMENTATION ORDER

### STRICT SEQUENCE (DO NOT SKIP)

```markdown
1. ✅ **Models** (apps/[app]/models.py)
   - Define fields with correct types
   - Add verbose_name, help_text
   - Create indexes for frequently queried fields
   - Write __str__ method

2. ✅ **Migrations**
   python manage.py makemigrations
   python manage.py migrate

3. ✅ **Admin** (apps/[app]/admin.py)
   - Register models
   - Configure list_display, search_fields

4. ✅ **Serializers** (apps/[app]/serializers.py)
   - Use ModelSerializer when possible
   - Add validation methods
   - Document fields

5. ✅ **API Views** (apps/[app]/api/[module]_api.py)
   - Implement endpoints
   - Add permission classes
   - Handle errors properly

6. ✅ **API URLs** (apps/[app]/urls.py)
   - Register API endpoints under /api/v1/

7. ✅ **Template Views** (apps/[app]/views_[module].py)
   - Prepare context data
   - Use get_object_or_404
   - Add error handling

8. ✅ **Page URLs** (apps/[app]/urls.py)
   - Register page routes

9. ✅ **Templates** (templates/pages/[feature].html)
   - Create HTML structure
   - Add Vue.js app
   - Use design system components

10. ✅ **Frontend JS** (in template)
    - Initialize Vue app
    - Implement methods
    - Call APIs correctly

11. ✅ **CSS** (in template or static/css/)
    - Use CSS variables
    - Follow spacing system

12. ✅ **Tests** (apps/[app]/tests/)
    - Write model tests
    - Write API tests
    - Write view tests
```

---

## 🧪 TESTING REQUIREMENTS

### Unit Tests (MANDATORY)

```python
# apps/curriculum/tests/test_models.py

from django.test import TestCase
from apps.curriculum.models import Phoneme

class PhonemeModelTest(TestCase):
    def setUp(self):
        self.phoneme = Phoneme.objects.create(
            ipa_symbol='ɪ',
            vietnamese_approx='i ngắn'
        )
    
    def test_phoneme_creation(self):
        """Test phoneme can be created"""
        self.assertEqual(self.phoneme.ipa_symbol, 'ɪ')
    
    def test_str_representation(self):
        """Test __str__ method"""
        expected = '/ɪ/ - i ngắn'
        self.assertEqual(str(self.phoneme), expected)
```

### API Tests (MANDATORY)

```python
# apps/curriculum/tests/test_api.py

from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class PhonemeAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test',
            password='test123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_list_phonemes(self):
        """Test GET /api/v1/pronunciation/phonemes/"""
        response = self.client.get('/api/v1/pronunciation/phonemes/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
```

---

## ✅ PRE-IMPLEMENTATION CHECKLIST

Before writing ANY code, verify:

```markdown
## Phase 1: Requirements
- [ ] User requirements fully understood
- [ ] Clarifying questions asked and answered
- [ ] Edge cases identified
- [ ] Acceptance criteria defined

## Phase 2: Architecture
- [ ] Checked existing models (grep "class ModelName")
- [ ] Listed all model fields accurately
- [ ] Designed API endpoints with correct naming
- [ ] Planned URL structure

## Phase 3: Design
- [ ] Reviewed design system (colors, fonts, spacing)
- [ ] Identified reusable components
- [ ] Created wireframe/mockup

## Phase 4: Ready to Code
- [ ] Have complete design document
- [ ] Know exact field names from models
- [ ] Know API response structures
- [ ] Templates planned with correct paths
```

---

## 🚫 ABSOLUTE DON'TS

### ❌ NEVER Do These:

1. **Don't code before design**
   - Always complete Phase 1-3 before Phase 4

2. **Don't guess field names**
   - Always check model file first
   - Copy-paste exact names

3. **Don't assume API structure**
   - Test endpoint with curl first
   - Document in design phase

4. **Don't skip tests**
   - Write tests while coding
   - Run tests before declaring complete

5. **Don't hardcode values**
   ```python
   # ❌ BAD
   if score > 80:  # Magic number
   
   # ✅ GOOD
   MASTERY_THRESHOLD = 80
   if score > MASTERY_THRESHOLD:
   ```

6. **Don't mix naming conventions**
   - Python: `snake_case`
   - JavaScript: `camelCase`
   - URLs: `kebab-case`

7. **Don't create files in wrong locations**
   - Models → `apps/[app]/models.py`
   - APIs → `apps/[app]/api/`
   - Templates → `templates/pages/`

8. **Don't use Django templates in Vue.js**
   ```html
   <!-- ❌ WRONG -->
   <p>{{ user.name }}</p>  
   
   <!-- ✅ CORRECT -->
   <p>[[ user.name ]]</p>
   ```

---

## 📞 WHEN TO ASK USER

Ask user for clarification when:

1. ❓ Requirements unclear or ambiguous
2. 🔀 Multiple implementation approaches possible
3. 🎨 UI/UX design decisions needed
4. 💰 Feature requires significant time/resources
5. 🔒 Security or privacy implications
6. 🏗️ Architecture changes needed
7. 📊 Data model changes impact existing data

**Format for questions:**
```markdown
## Question: [Topic]

**Context:** [Explain situation]

**Options:**
1. [Option 1] - [Pros/Cons]
2. [Option 2] - [Pros/Cons]

**Recommendation:** [Your suggestion with reasoning]

**Question:** [Specific question for user]
```

---

## 📂 PROJECT ORGANIZATION RULES

> **⚠️ MANDATORY**: Follow these rules strictly to maintain project organization

### 🎨 Template Organization Rules

**ALWAYS organize templates by app:**

```python
# ❌ WRONG - All templates in one folder
backend/templates/pages/
├── pronunciation_discovery.html
├── pronunciation_learning.html
├── user_profile.html
└── study_dashboard.html

# ✅ CORRECT - Organized by app
backend/templates/
├── curriculum/
│   ├── pronunciation/
│   │   ├── discovery.html
│   │   └── learning.html
│   └── phoneme/
│       └── chart.html
├── users/
│   └── profile.html
└── study/
    └── dashboard.html
```

**Template Naming Convention:**

```python
# ❌ WRONG
'pages/pronunciation_lesson.html'
'pages/user_profile_settings.html'

# ✅ CORRECT
'curriculum/pronunciation/lesson_detail.html'
'users/profile_settings.html'
```

**When creating a NEW template:**

1. **Identify the app** - Which app does this feature belong to?
2. **Create folder structure** - `templates/{app}/{feature}/`
3. **Use descriptive names** - `{feature}/{action}.html` (e.g., `pronunciation/discovery.html`)
4. **Update view** - Use correct path in `render()`

```python
# Example: Creating new pronunciation feature
# Step 1: Create file at correct location
touch backend/templates/curriculum/pronunciation/practice.html

# Step 2: Update view
def pronunciation_practice_view(request):
    return render(request, 'curriculum/pronunciation/practice.html', context)
```

**Shared Templates:**

```
templates/
├── base/              # Base layouts
│   ├── _base.html
│   ├── _base_public.html
│   └── _base_admin.html
├── components/        # Reusable components
│   ├── _navbar.html
│   ├── _footer.html
│   └── _audio_player.html
└── errors/           # Error pages
    ├── 404.html
    └── 500.html
```

---

### 📄 Documentation Organization Rules

**NEVER create docs in root folder.** Always use `docs/` with proper categorization:

```bash
# ❌ WRONG - All docs in root
PRONUNCIATION_IMPLEMENTATION.md
AUDIO_SYSTEM_DESIGN.md
USER_AUTHENTICATION_FIX.md
DAY_4_TESTING.md

# ✅ CORRECT - Categorized in docs/
docs/
├── curriculum/
│   ├── PRONUNCIATION_IMPLEMENTATION.md
│   └── audio/
│       └── AUDIO_SYSTEM_DESIGN.md
├── users/
│   └── USER_AUTHENTICATION_FIX.md
└── testing/
    └── DAY_4_TESTING.md
```

**Documentation Categories:**

| Category | Purpose | Examples |
|----------|---------|----------|
| `docs/project/` | Project-level docs | QUICK_START.md, README.md |
| `docs/standards/` | Development standards | DEVELOPMENT_STANDARDS.md |
| `docs/architecture/` | System architecture | SYSTEM_ANALYSIS.md |
| `docs/curriculum/` | Curriculum app docs | PRONUNCIATION_DESIGN.md |
| `docs/users/` | Users app docs | AUTH_SYSTEM.md |
| `docs/study/` | Study app docs | ANALYTICS_DESIGN.md |
| `docs/testing/` | Testing guides | TESTING_GUIDE.md |
| `docs/changelog/` | Change logs | 2025-12-18_FEATURE_X.md |
| `docs/examples/` | Code examples | integration_example.py |

**Naming Convention for Changelogs:**

```bash
# ❌ WRONG
DAY_4_COMPLETE.md
BUG_FIXES.md

# ✅ CORRECT
docs/changelog/2025-12-16_DAY_4_COMPLETE.md
docs/changelog/2025-12-18_PHONEME_BUG_FIX.md
```

**When creating NEW documentation:**

```bash
# Step 1: Identify category
# Is this about curriculum? users? architecture?

# Step 2: Check if category folder exists
ls docs/curriculum/

# Step 3: Create in correct location
# Format: {FEATURE}_{TYPE}.md
# Types: DESIGN, IMPLEMENTATION, GUIDE, ANALYSIS, TEST_REPORT

# Examples:
docs/curriculum/PRONUNCIATION_LESSON_DESIGN.md
docs/curriculum/audio/EDGE_TTS_IMPLEMENTATION.md
docs/users/PROFILE_SETTINGS_GUIDE.md
docs/testing/BROWSER_TESTING_GUIDE.md
```

**Required doc structure:**

```markdown
# {Title}

**Ngày:** {Date}
**App:** {curriculum/users/study}
**Status:** {Draft/Review/Complete}

---

## 🎯 Mục đích

## 📋 Nội dung

## 🔗 Related Documents
- [Link to related doc]
```

---

### 🧪 Test Organization Rules

**ALWAYS follow Django test structure:**

```
backend/tests/
├── conftest.py              # Shared fixtures
├── {app}/
│   ├── __init__.py
│   ├── conftest.py          # App-specific fixtures
│   ├── models/
│   │   └── test_{model}.py
│   ├── api/
│   │   └── test_{feature}_api.py
│   ├── services/
│   │   └── test_{service}.py
│   ├── views/
│   │   └── test_{feature}_views.py
│   └── integration/
│       └── test_{flow}.py
```

**Test File Naming:**

```python
# ❌ WRONG - Tests in root or random locations
test_pronunciation.py
test_phoneme_quick.py
check_audio.py

# ✅ CORRECT - Organized by app and type
backend/tests/curriculum/models/test_phoneme.py
backend/tests/curriculum/api/test_pronunciation_api.py
backend/tests/curriculum/services/test_audio_service.py
backend/tests/curriculum/views/test_pronunciation_views.py
backend/tests/curriculum/integration/test_audio_flow.py
```

**Test Class Naming:**

```python
# Format: Test{Feature}{Type}
class TestPhonemeModel(TestCase):
    """Test Phoneme model functionality."""
    pass

class TestPronunciationAPI(APITestCase):
    """Test Pronunciation API endpoints."""
    pass

class TestEdgeTTSService(TestCase):
    """Test Edge TTS integration service."""
    pass
```

**When creating NEW tests:**

```bash
# Step 1: Identify app and type
# App: curriculum, users, study
# Type: models, api, services, views, integration

# Step 2: Create in correct location
touch backend/tests/curriculum/services/test_tts_generator.py

# Step 3: Use shared fixtures from conftest.py
# backend/tests/conftest.py
@pytest.fixture
def authenticated_client(user):
    client = Client()
    client.force_login(user)
    return client

# Step 4: Import and use
from conftest import authenticated_client

def test_pronunciation_view(authenticated_client):
    response = authenticated_client.get('/pronunciation/discovery/')
    assert response.status_code == 200
```

**Running tests by category:**

```bash
# Run all curriculum tests
pytest backend/tests/curriculum/

# Run only API tests
pytest backend/tests/curriculum/api/

# Run specific test file
pytest backend/tests/curriculum/models/test_phoneme.py

# Run with coverage
pytest --cov=backend/apps/curriculum backend/tests/curriculum/
```

---

### 🛠️ Management Commands Organization

**NEVER create management commands in root.** Always in app structure:

```
backend/apps/{app}/management/commands/
├── __init__.py
└── {command_name}.py
```

**Examples:**

```bash
# ❌ WRONG - Commands in root
generate_phoneme_tts.py
seed_data.py
check_audio_quality.py

# ✅ CORRECT - In app management/commands
backend/apps/curriculum/management/commands/
├── generate_phoneme_audio.py
├── seed_phonemes.py
└── check_audio_quality.py

backend/apps/users/management/commands/
├── create_test_users.py
└── cleanup_inactive_users.py
```

**Command naming convention:**

```python
# Format: {action}_{resource}.py
generate_phoneme_audio.py    # ✅
seed_lessons.py              # ✅
cleanup_old_sessions.py      # ✅

# NOT
phoneme_gen.py               # ❌
make_audio.py                # ❌
```

---

### 🗂️ Temporary Files Management

**NEVER commit temp files.** Use designated folders:

```bash
# Create temp folder if needed
mkdir -p temp/

# Add to .gitignore
echo "temp/" >> .gitignore
echo "test_*.html" >> .gitignore
echo "*_temp.*" >> .gitignore
```

**Temp file naming:**

```bash
# Format: temp_{feature}_{description}.{ext}
temp/
├── temp_pronunciation_test.html
├── temp_audio_debug.py
└── temp_api_response.json
```

**Cleanup:**

```bash
# Remove temp files regularly
rm -rf temp/*

# Or use git clean (careful!)
git clean -fdx temp/
```

---

### ✅ FILE CREATION CHECKLIST

Before creating ANY new file, ask:

- [ ] **Is this a template?** → Put in `templates/{app}/{feature}/`
- [ ] **Is this documentation?** → Put in `docs/{category}/`
- [ ] **Is this a test?** → Put in `backend/tests/{app}/{type}/`
- [ ] **Is this a command?** → Put in `apps/{app}/management/commands/`
- [ ] **Is this temporary?** → Put in `temp/` and add to .gitignore
- [ ] **Does it follow naming convention?**
- [ ] **Is there an existing similar file I should check first?**

---

### 🚫 ABSOLUTE DON'TS - File Organization

1. **DON'T create templates in `pages/` folder**
   - Use app-specific folders instead

2. **DON'T create docs in root folder**
   - Use `docs/` with proper categorization

3. **DON'T create tests in root or backend/ directly**
   - Use `backend/tests/{app}/` structure

4. **DON'T use inconsistent naming**
   - Stick to conventions: snake_case, descriptive names

5. **DON'T leave temp files uncommitted**
   - Clean up or move to `temp/` folder

6. **DON'T create files without checking existing structure**
   - Always run `ls` or `tree` first

7. **DON'T mix Vietnamese and English in filenames**
   - Use English for code/files, Vietnamese for content only

---

## 🎯 QUALITY STANDARDS

### Code Quality
- ✅ PEP 8 compliant (Python)
- ✅ ESLint compliant (JavaScript)
- ✅ No hardcoded values
- ✅ Comprehensive error handling
- ✅ Meaningful variable names
- ✅ Comments for complex logic

### Performance
- ✅ Page load < 2 seconds
- ✅ API response < 200ms
- ✅ < 10 database queries per page
- ✅ Optimized images
- ✅ Efficient Vue.js reactivity

### Testing
- ✅ Test coverage > 80%
- ✅ All unit tests passing
- ✅ Integration tests for workflows
- ✅ Manual testing on Chrome/Firefox/Safari

### Documentation
- ✅ Docstrings for all functions/classes
- ✅ API endpoints documented
- ✅ Complex logic explained
- ✅ README updated

---

## 📚 PROJECT-SPECIFIC KNOWLEDGE

### Authentication Flow
```javascript
// ALWAYS wait for Auth before API calls
await Auth.waitUntilReady();

if (Auth.isAuthenticated()) {
    // User is logged in
    await this.loadUserData();
} else {
    // Show login prompt
}
```

### API Client Usage
```javascript
// ✅ CORRECT - Use ApiClient
const response = await ApiClient.get('/api/v1/resource/');
const data = await ApiClient.post('/api/v1/resource/', {field: 'value'});

// ❌ WRONG - Don't use fetch directly
fetch('/api/v1/resource/')...  // Missing CSRF, auth headers
```

### Database Models
```python
# Main apps:
apps.curriculum  # Course, Lesson, Phoneme, Quiz, MinimalPair
apps.users       # User, UserProfile, UserProgress
apps.study       # StudySession, Analytics

# Key relationships:
User → UserPhonemeProgress → Phoneme
User → UserLessonProgress → Lesson
```

---

## 🔄 CONTINUOUS IMPROVEMENT

After each feature:
1. ✅ Update DEVELOPMENT_WORKFLOW.md if new patterns emerge
2. ✅ Document lessons learned
3. ✅ Add to common pitfalls if error found
4. ✅ Update copilot.instructions.md (this file)

---

## 📖 REFERENCES

- **Main Workflow:** [DEVELOPMENT_WORKFLOW.md](/DEVELOPMENT_WORKFLOW.md)
- **System Analysis:** [SYSTEM_ANALYSIS.md](/SYSTEM_ANALYSIS.md)
- **Django Guide:** [backend/DJANGO_DEVELOPMENT_GUIDE.md](/backend/DJANGO_DEVELOPMENT_GUIDE.md)
- **API Guidelines:** [backend/API_GUIDELINES.md](/backend/API_GUIDELINES.md)

---

**Last Updated:** 2025-12-16  
**Project Version:** 1.0.0  
**Copilot Version:** Latest

---

## 💡 REMEMBER

> "The best code is code that doesn't need to be changed.  
> The second best code is code that can be easily changed.  
> To achieve both: **FOLLOW THE WORKFLOW**."

**When in doubt:**
1. Read DEVELOPMENT_WORKFLOW.md
2. Check existing code for patterns
3. Ask user for clarification
4. Design first, code later
5. Test everything
