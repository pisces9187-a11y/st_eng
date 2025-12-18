# 🎨 PHASE 2 IMPLEMENTATION - VISUAL LEARNING SYSTEM

**Duration:** Week 3-4 (10 working days)  
**Focus:** Build Interactive Phoneme Learning Interface  
**Status:** READY TO PLAN

---

## 📋 MỤC TIÊU PHASE 2

### Xây Dựng Hệ Thống Học Trực Quan
1. **Interactive Phoneme Chart** - Bảng IPA tương tác với audio
2. **Mouth Position Visualizer** - Hình ảnh minh họa vị trí miệng/lưỡi
3. **Minimal Pair Practice** - Luyện tập phân biệt âm tương tự
4. **Progress Tracking UI** - Theo dõi tiến độ học
5. **Responsive Design** - Mobile-first theo DEVELOPMENT_STANDARDS.md

### Tech Stack
- **Frontend:** Vue.js 3 (CDN) + Bootstrap 5
- **Backend:** Django REST API (đã có)
- **Design:** Tuân thủ 100% DEVELOPMENT_STANDARDS.md
- **Template:** Sử dụng TEMPLATE_ARCHITECTURE.md

---

## 🗓️ TIMELINE CHI TIẾT

### **DAY 1-2: Setup Template Structure & Phoneme Chart**
- Tạo base templates theo TEMPLATE_ARCHITECTURE
- Build Interactive Phoneme Chart (IPA table)
- API integration cho audio playback

### **DAY 3-4: Mouth Position Visualizer**
- Upload & manage mouth diagram images
- Create slider component cho tongue position
- Responsive image viewer

### **DAY 5-6: Minimal Pair Practice**
- Build practice exercise component
- Audio comparison interface
- Score tracking

### **DAY 7-8: Progress Dashboard**
- User progress API integration
- Chart visualization với Chart.js
- Achievement badges

### **DAY 9-10: Testing & Refinement**
- Responsive testing (mobile/tablet/desktop)
- Performance optimization
- Bug fixes

---

## 📁 FILE STRUCTURE

```
backend/
├── templates/
│   └── public/
│       └── pronunciation/
│           ├── phoneme-chart.html      # DAY 1-2
│           ├── phoneme-detail.html     # DAY 3-4
│           ├── minimal-pairs.html      # DAY 5-6
│           └── progress.html           # DAY 7-8
│
├── static/
│   ├── css/
│   │   └── pronunciation.css           # Phase 2 styles
│   │
│   ├── js/
│   │   └── pronunciation/
│   │       ├── phoneme-chart.js        # Vue component
│   │       ├── mouth-visualizer.js     # Vue component
│   │       ├── minimal-pairs.js        # Vue component
│   │       └── progress-tracker.js     # Vue component
│   │
│   └── images/
│       └── phonemes/
│           └── mouth-diagrams/         # Mouth position images
│
└── apps/curriculum/
    ├── api_views.py                    # Extend với pronunciation endpoints
    └── template_views.py               # Add pronunciation views
```

---

## 🎨 DAY 1-2: INTERACTIVE PHONEME CHART

### Objectives
- Tạo bảng IPA tương tác với 44 phonemes
- Tích hợp audio playback từ PhonemeAudioService
- Responsive design cho mobile/tablet/desktop

### Step 1: Create Django View

**File:** `backend/apps/curriculum/template_views.py`

```python
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import PhonemeCategory, Phoneme

class PhonemeChartView(LoginRequiredMixin, TemplateView):
    """
    Interactive phoneme chart with IPA symbols.
    
    Features:
    - Visual IPA chart organized by categories
    - Audio playback on click
    - Vietnamese approximation tooltips
    - Color-coded by vowels/consonants
    """
    template_name = 'public/pronunciation/phoneme-chart.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all phoneme categories with phonemes
        context['vowels'] = PhonemeCategory.objects.filter(
            category_type='vowel'
        ).prefetch_related('phonemes__audio_sources')
        
        context['diphthongs'] = PhonemeCategory.objects.filter(
            category_type='diphthong'
        ).prefetch_related('phonemes__audio_sources')
        
        context['consonants'] = PhonemeCategory.objects.filter(
            category_type='consonant'
        ).prefetch_related('phonemes__audio_sources')
        
        return context
```

### Step 2: Create URL Route

**File:** `backend/apps/curriculum/urls.py`

```python
from django.urls import path
from .template_views import PhonemeChartView, PhonemeDetailView

app_name = 'pronunciation'

urlpatterns = [
    # ... existing patterns ...
    
    # Pronunciation System
    path('pronunciation/chart/', PhonemeChartView.as_view(), name='phoneme_chart'),
    path('pronunciation/phoneme/<int:pk>/', PhonemeDetailView.as_view(), name='phoneme_detail'),
]
```

### Step 3: Create Template

**File:** `backend/templates/public/pronunciation/phoneme-chart.html`

```html
{% extends "base/_base_public.html" %}
{% load static %}

{% block title %}IPA Phoneme Chart - EnglishMaster{% endblock %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'css/pronunciation.css' %}">
<style>
    /* Page-specific styles following DEVELOPMENT_STANDARDS */
    .phoneme-chart-container {
        background: var(--color-bg-main);
        min-height: 100vh;
        padding: var(--spacing-xl) 0;
    }
    
    .chart-header {
        background: linear-gradient(135deg, var(--color-secondary) 0%, var(--color-secondary-dark) 100%);
        color: var(--color-text-white);
        padding: var(--spacing-xxl);
        border-radius: var(--radius-lg);
        margin-bottom: var(--spacing-xl);
        box-shadow: var(--shadow-lg);
    }
    
    .chart-title {
        font-family: var(--font-heading);
        font-size: var(--font-size-4xl);
        font-weight: var(--font-weight-bold);
        margin-bottom: var(--spacing-md);
    }
    
    .chart-subtitle {
        font-family: var(--font-body);
        font-size: var(--font-size-lg);
        opacity: 0.9;
    }
    
    /* Category Section */
    .phoneme-category {
        background: var(--color-bg-white);
        border-radius: var(--radius-lg);
        padding: var(--spacing-xl);
        margin-bottom: var(--spacing-xl);
        box-shadow: var(--shadow-sm);
        transition: all 0.3s ease;
    }
    
    .phoneme-category:hover {
        box-shadow: var(--shadow-md);
    }
    
    .category-header {
        display: flex;
        align-items: center;
        gap: var(--spacing-md);
        margin-bottom: var(--spacing-lg);
        padding-bottom: var(--spacing-md);
        border-bottom: 2px solid var(--color-border);
    }
    
    .category-icon {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
        border-radius: var(--radius-md);
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--color-text-white);
        font-size: var(--font-size-xl);
    }
    
    .category-title {
        font-family: var(--font-heading);
        font-size: var(--font-size-2xl);
        font-weight: var(--font-weight-bold);
        color: var(--color-secondary);
        margin: 0;
    }
    
    .category-count {
        margin-left: auto;
        background: var(--color-primary-light);
        color: var(--color-text-white);
        padding: 4px 12px;
        border-radius: var(--radius-full);
        font-size: var(--font-size-sm);
        font-weight: var(--font-weight-semibold);
    }
    
    /* Phoneme Grid */
    .phoneme-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
        gap: var(--spacing-md);
    }
    
    @media (max-width: 768px) {
        .phoneme-grid {
            grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
            gap: var(--spacing-sm);
        }
    }
    
    /* Phoneme Card */
    .phoneme-card {
        background: var(--color-bg-white);
        border: 2px solid var(--color-border);
        border-radius: var(--radius-md);
        padding: var(--spacing-lg);
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .phoneme-card:hover {
        border-color: var(--color-primary);
        box-shadow: var(--shadow-md);
        transform: translateY(-4px);
    }
    
    .phoneme-card.active {
        border-color: var(--color-primary);
        background: linear-gradient(135deg, var(--color-primary-light) 0%, var(--color-primary) 100%);
    }
    
    .phoneme-card.active .phoneme-symbol,
    .phoneme-card.active .phoneme-approx {
        color: var(--color-text-white);
    }
    
    /* Audio indicator */
    .phoneme-card.playing::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: var(--color-primary);
        animation: progress 2s ease-in-out;
    }
    
    @keyframes progress {
        from { width: 0%; }
        to { width: 100%; }
    }
    
    .phoneme-symbol {
        font-size: var(--font-size-3xl);
        font-weight: var(--font-weight-bold);
        color: var(--color-secondary);
        margin-bottom: var(--spacing-sm);
        font-family: 'Doulos SIL', 'Charis SIL', serif; /* IPA font */
    }
    
    .phoneme-approx {
        font-size: var(--font-size-sm);
        color: var(--color-text-secondary);
        font-family: var(--font-body);
        line-height: var(--line-height-normal);
    }
    
    /* Audio quality badge */
    .audio-badge {
        position: absolute;
        top: 8px;
        right: 8px;
        width: 24px;
        height: 24px;
        border-radius: var(--radius-full);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 10px;
    }
    
    .audio-badge.native {
        background: var(--color-success);
        color: white;
    }
    
    .audio-badge.tts {
        background: var(--color-info);
        color: white;
    }
    
    .audio-badge.none {
        background: var(--color-text-light);
        color: white;
    }
    
    /* Loading state */
    .loading-spinner {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
    }
</style>
{% endblock %}

{% block content %}
<div id="phoneme-chart-app" class="phoneme-chart-container">
    <div class="container">
        <!-- Header -->
        <div class="chart-header">
            <h1 class="chart-title">
                <i class="fas fa-language"></i>
                Bảng Phiên Âm Quốc Tế (IPA)
            </h1>
            <p class="chart-subtitle">
                44 âm tiếng Anh - Nhấp vào mỗi âm để nghe phát âm chuẩn
            </p>
        </div>
        
        <!-- Vowels Section -->
        <div class="phoneme-category" v-for="category in vowels" :key="category.id">
            <div class="category-header">
                <div class="category-icon">
                    <i class="fas fa-circle"></i>
                </div>
                <h2 class="category-title">${category.name_vi}</h2>
                <span class="category-count">${category.phonemes.length} âm</span>
            </div>
            
            <div class="phoneme-grid">
                <div 
                    v-for="phoneme in category.phonemes" 
                    :key="phoneme.id"
                    class="phoneme-card"
                    :class="{ active: currentPhoneme?.id === phoneme.id, playing: isPlaying && currentPhoneme?.id === phoneme.id }"
                    @click="playPhoneme(phoneme)"
                >
                    <!-- Audio quality badge -->
                    <div class="audio-badge" :class="getAudioQualityClass(phoneme)">
                        <i :class="getAudioIcon(phoneme)"></i>
                    </div>
                    
                    <div class="phoneme-symbol">/${phoneme.ipa_symbol}/</div>
                    <div class="phoneme-approx">${phoneme.vietnamese_approx}</div>
                </div>
            </div>
        </div>
        
        <!-- Diphthongs Section -->
        <div class="phoneme-category" v-for="category in diphthongs" :key="category.id">
            <div class="category-header">
                <div class="category-icon">
                    <i class="fas fa-code-branch"></i>
                </div>
                <h2 class="category-title">${category.name_vi}</h2>
                <span class="category-count">${category.phonemes.length} âm</span>
            </div>
            
            <div class="phoneme-grid">
                <div 
                    v-for="phoneme in category.phonemes" 
                    :key="phoneme.id"
                    class="phoneme-card"
                    :class="{ active: currentPhoneme?.id === phoneme.id, playing: isPlaying && currentPhoneme?.id === phoneme.id }"
                    @click="playPhoneme(phoneme)"
                >
                    <div class="audio-badge" :class="getAudioQualityClass(phoneme)">
                        <i :class="getAudioIcon(phoneme)"></i>
                    </div>
                    <div class="phoneme-symbol">/${phoneme.ipa_symbol}/</div>
                    <div class="phoneme-approx">${phoneme.vietnamese_approx}</div>
                </div>
            </div>
        </div>
        
        <!-- Consonants Section -->
        <div class="phoneme-category" v-for="category in consonants" :key="category.id">
            <div class="category-header">
                <div class="category-icon">
                    <i class="fas fa-square"></i>
                </div>
                <h2 class="category-title">${category.name_vi}</h2>
                <span class="category-count">${category.phonemes.length} âm</span>
            </div>
            
            <div class="phoneme-grid">
                <div 
                    v-for="phoneme in category.phonemes" 
                    :key="phoneme.id"
                    class="phoneme-card"
                    :class="{ active: currentPhoneme?.id === phoneme.id, playing: isPlaying && currentPhoneme?.id === phoneme.id }"
                    @click="playPhoneme(phoneme)"
                >
                    <div class="audio-badge" :class="getAudioQualityClass(phoneme)">
                        <i :class="getAudioIcon(phoneme)"></i>
                    </div>
                    <div class="phoneme-symbol">/${phoneme.ipa_symbol}/</div>
                    <div class="phoneme-approx">${phoneme.vietnamese_approx}</div>
                </div>
            </div>
        </div>
        
        <!-- Loading overlay -->
        <div v-if="loading" class="loading-spinner">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Đang tải...</span>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block page_js %}
<script>
const { createApp } = Vue;

createApp({
    delimiters: ['${', '}'],  // Avoid conflict with Django template tags
    data() {
        return {
            vowels: {{ vowels|safe }},  // Django context to JSON
            diphthongs: {{ diphthongs|safe }},
            consonants: {{ consonants|safe }},
            currentPhoneme: null,
            isPlaying: false,
            loading: false,
            audioElement: null
        };
    },
    methods: {
        async playPhoneme(phoneme) {
            // Stop current audio if playing
            if (this.audioElement) {
                this.audioElement.pause();
                this.audioElement = null;
            }
            
            this.currentPhoneme = phoneme;
            this.isPlaying = true;
            
            try {
                // Call API to get audio URL
                const response = await fetch(`/api/pronunciation/phoneme/${phoneme.id}/audio/`);
                const data = await response.json();
                
                if (data.audio_url) {
                    // Play audio
                    this.audioElement = new Audio(data.audio_url);
                    this.audioElement.play();
                    
                    this.audioElement.addEventListener('ended', () => {
                        this.isPlaying = false;
                    });
                } else {
                    // Fallback to Web Speech API
                    this.speakWithWebSpeech(phoneme.vietnamese_approx || phoneme.ipa_symbol);
                }
            } catch (error) {
                console.error('Error playing audio:', error);
                this.isPlaying = false;
                alert('Không thể phát âm thanh. Vui lòng thử lại.');
            }
        },
        
        speakWithWebSpeech(text) {
            if ('speechSynthesis' in window) {
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.lang = 'en-US';
                utterance.rate = 0.8;  // Slower for clarity
                
                utterance.addEventListener('end', () => {
                    this.isPlaying = false;
                });
                
                speechSynthesis.speak(utterance);
            } else {
                this.isPlaying = false;
                alert('Trình duyệt không hỗ trợ phát âm.');
            }
        },
        
        getAudioQualityClass(phoneme) {
            // Check if phoneme has audio sources
            if (phoneme.audio_sources && phoneme.audio_sources.length > 0) {
                const hasNative = phoneme.audio_sources.some(a => a.source_type === 'native');
                return hasNative ? 'native' : 'tts';
            }
            return 'none';
        },
        
        getAudioIcon(phoneme) {
            const quality = this.getAudioQualityClass(phoneme);
            if (quality === 'native') return 'fas fa-star';
            if (quality === 'tts') return 'fas fa-volume-up';
            return 'fas fa-volume-mute';
        }
    },
    mounted() {
        console.log('Phoneme Chart loaded');
        console.log('Total phonemes:', 
            this.vowels.reduce((sum, cat) => sum + cat.phonemes.length, 0) +
            this.diphthongs.reduce((sum, cat) => sum + cat.phonemes.length, 0) +
            this.consonants.reduce((sum, cat) => sum + cat.phonemes.length, 0)
        );
    }
}).mount('#phoneme-chart-app');
</script>
{% endblock %}
```

### Step 4: Create API Endpoint

**File:** `backend/apps/curriculum/api_views.py` (ADD to existing)

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services.audio_service import PhonemeAudioService
from .models import Phoneme

class PhonemeAudioAPIView(APIView):
    """
    Get audio URL for a specific phoneme.
    
    GET /api/pronunciation/phoneme/<id>/audio/
    
    Returns:
        {
            "phoneme_id": 1,
            "ipa_symbol": "i:",
            "audio_url": "/media/phonemes/audio/2025/12/15/i_native.mp3",
            "source_type": "native",
            "quality_score": 100
        }
    """
    
    def get(self, request, pk):
        try:
            phoneme = Phoneme.objects.get(pk=pk)
        except Phoneme.DoesNotExist:
            return Response(
                {"error": "Phoneme not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Use PhonemeAudioService to get audio
        service = PhonemeAudioService()
        audio_source = service.get_audio_for_phoneme(phoneme)
        
        if audio_source:
            return Response({
                "phoneme_id": phoneme.id,
                "ipa_symbol": phoneme.ipa_symbol,
                "audio_url": audio_source.get_url(),
                "source_type": audio_source.source_type,
                "quality_score": audio_source.get_quality_score(),
                "vietnamese_approx": phoneme.vietnamese_approx
            })
        else:
            # No audio available
            return Response({
                "phoneme_id": phoneme.id,
                "ipa_symbol": phoneme.ipa_symbol,
                "audio_url": None,
                "source_type": "web_speech",
                "quality_score": 0,
                "vietnamese_approx": phoneme.vietnamese_approx
            })
```

### Step 5: Add API URL Route

**File:** `backend/apps/curriculum/urls.py`

```python
from django.urls import path
from .api_views import PhonemeAudioAPIView

# API patterns
api_patterns = [
    path('api/pronunciation/phoneme/<int:pk>/audio/', 
         PhonemeAudioAPIView.as_view(), 
         name='phoneme_audio_api'),
]

urlpatterns = [
    # ... existing patterns ...
] + api_patterns
```

### Step 6: Create CSS File

**File:** `backend/static/css/pronunciation.css`

```css
/* 
 * Pronunciation System Styles
 * Following DEVELOPMENT_STANDARDS.md
 */

/* Import Doulos SIL font for IPA symbols */
@import url('https://fonts.googleapis.com/css2?family=Doulos+SIL&display=swap');

/* Global IPA font */
.ipa-symbol {
    font-family: 'Doulos SIL', 'Charis SIL', serif;
}

/* Animation utilities */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.fade-in {
    animation: fadeIn 0.5s ease-out;
}

/* Responsive utilities */
@media (max-width: 768px) {
    .phoneme-chart-container {
        padding: var(--spacing-md) 0;
    }
    
    .chart-header {
        padding: var(--spacing-lg);
    }
    
    .chart-title {
        font-size: var(--font-size-3xl);
    }
}
```

### Testing Checklist

```
✅ DAY 1-2 Checklist:
[ ] View loads correctly with all categories
[ ] Phonemes displayed in grid layout
[ ] Audio plays on click (native/TTS/Web Speech fallback)
[ ] Active state shows correctly
[ ] Audio badge shows correct quality (native/TTS/none)
[ ] Responsive on mobile (grid adjusts)
[ ] Loading spinner works
[ ] Error handling for missing audio
[ ] Vue.js delimiters don't conflict with Django
[ ] Colors follow DEVELOPMENT_STANDARDS
```

---

## 🖼️ DAY 3-4: MOUTH POSITION VISUALIZER

### Objectives
- Display mouth/tongue position diagrams
- Interactive slider for tongue movement
- Tips for pronunciation
- Link to phoneme detail page

### Implementation Details

**New Template:** `phoneme-detail.html`
- Extends `_base_public.html`
- Shows single phoneme with detailed info
- Mouth diagram viewer
- Pronunciation tips
- Example words
- Minimal pairs

**Vue Component:** `mouth-visualizer.js`
- Image viewer with zoom
- Slider for tongue position stages
- Animated transitions

---

## 🎮 DAY 5-6: MINIMAL PAIR PRACTICE

### Objectives
- Practice distinguishing similar sounds
- Audio comparison interface
- Score tracking
- Immediate feedback

### Features
- Display two phonemes side-by-side (e.g., /i:/ vs /ɪ/)
- Play audio for each
- Quiz: Which sound did you hear?
- Track correct/incorrect answers
- Show progress bar

---

## 📊 DAY 7-8: PROGRESS TRACKING

### Objectives
- User progress dashboard
- Chart visualization
- Achievement badges
- Streak tracking

### Tech
- Chart.js for visualizations
- API to track phoneme mastery
- Badge system

---

## ✅ PHASE 2 DELIVERABLES

### Frontend Components
1. ✅ Phoneme Chart (Interactive IPA table)
2. ✅ Phoneme Detail Page (with mouth diagrams)
3. ✅ Minimal Pair Practice (exercise component)
4. ✅ Progress Dashboard (tracking UI)

### Backend APIs
1. ✅ Phoneme Audio API (already exists)
2. ✅ Progress Tracking API (new)
3. ✅ Minimal Pair API (new)
4. ✅ Achievement API (new)

### Design Compliance
- ✅ 100% theo DEVELOPMENT_STANDARDS.md
- ✅ Bootstrap 5 + Vue.js 3 CDN
- ✅ Responsive mobile-first
- ✅ Color palette: 60-30-10 rule
- ✅ Typography: Montserrat + Open Sans

---

## 🚀 NEXT: PHASE 3

Sau khi hoàn thành Phase 2, chuyển sang Phase 3:
- TTS Generation với Celery
- Batch audio processing
- Voice variety support
- Audio file optimization

---

**Status:** READY FOR IMPLEMENTATION  
**Start Date:** TBD  
**Estimated Completion:** 10 working days
