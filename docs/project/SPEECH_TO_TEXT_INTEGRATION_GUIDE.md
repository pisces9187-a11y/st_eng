# 🎤 Speech-to-Text Integration Guide

## Hiện trạng

**Tongue Twister Challenge** hiện đang sử dụng **mock scoring** dựa trên:
- ⏱️ Duration (thời gian đọc)
- 📊 Difficulty level (độ khó tongue twister)
- 🎲 Random variance (để tạo sự thực tế)

**Hạn chế:**
- ❌ Không phân tích âm thanh thực sự
- ❌ Không có transcript (văn bản phát hiện được)
- ❌ Không đánh giá từng từ
- ❌ Score chỉ là ước tính

---

## Giải pháp: Tích hợp Speech-to-Text

### Option 1: Google Cloud Speech-to-Text API ⭐ Recommended

**Ưu điểm:**
- ✅ Độ chính xác cao (~95%)
- ✅ Hỗ trợ phoneme-level analysis
- ✅ Word timestamps
- ✅ Confidence scores per word
- ✅ Pronunciation assessment

**Setup:**

```python
from google.cloud import speech_v1p1beta1 as speech
import io

def analyze_pronunciation(audio_file, expected_text):
    """
    Analyze pronunciation using Google Cloud Speech-to-Text.
    
    Returns:
        {
            'transcript': 'she sells seashells...',
            'words': [
                {'word': 'she', 'confidence': 0.95, 'start_time': 0.0, 'end_time': 0.3},
                {'word': 'sells', 'confidence': 0.89, 'start_time': 0.3, 'end_time': 0.6},
                ...
            ],
            'accuracy': 92.5,  # % words correctly pronounced
            'pronunciation_score': 88.0,  # Overall pronunciation quality
        }
    """
    
    client = speech.SpeechClient()
    
    # Read audio file
    with io.open(audio_file.path, 'rb') as f:
        content = f.read()
    
    audio = speech.RecognitionAudio(content=content)
    
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code='en-US',
        enable_word_time_offsets=True,
        enable_word_confidence=True,
        # Enable pronunciation assessment
        enable_automatic_punctuation=False,
        model='default',
        use_enhanced=True,
    )
    
    # Perform recognition
    response = client.recognize(config=config, audio=audio)
    
    # Parse results
    if not response.results:
        return {
            'transcript': '',
            'words': [],
            'accuracy': 0,
            'pronunciation_score': 0,
        }
    
    result = response.results[0]
    alternative = result.alternatives[0]
    
    # Extract words with timestamps and confidence
    words = []
    for word_info in alternative.words:
        words.append({
            'word': word_info.word,
            'confidence': word_info.confidence,
            'start_time': word_info.start_time.total_seconds(),
            'end_time': word_info.end_time.total_seconds(),
        })
    
    # Calculate accuracy by comparing with expected text
    expected_words = expected_text.lower().split()
    detected_words = [w['word'].lower() for w in words]
    
    # Use difflib to find matches
    from difflib import SequenceMatcher
    matcher = SequenceMatcher(None, expected_words, detected_words)
    accuracy = matcher.ratio() * 100
    
    # Calculate pronunciation score from word confidences
    if words:
        pronunciation_score = sum(w['confidence'] for w in words) / len(words) * 100
    else:
        pronunciation_score = 0
    
    return {
        'transcript': alternative.transcript,
        'words': words,
        'accuracy': accuracy,
        'pronunciation_score': pronunciation_score,
    }
```

**Installation:**
```bash
pip install google-cloud-speech
```

**Environment Variables:**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

---

### Option 2: Azure Speech Service

**Ưu điểm:**
- ✅ Pronunciation Assessment built-in
- ✅ Phoneme-level scoring
- ✅ Fluency, completeness, prosody scores
- ✅ Good for language learners

**Setup:**

```python
import azure.cognitiveservices.speech as speechsdk

def azure_pronunciation_assessment(audio_file, reference_text):
    """
    Assess pronunciation using Azure Speech Service.
    """
    
    # Setup speech config
    speech_config = speechsdk.SpeechConfig(
        subscription=settings.AZURE_SPEECH_KEY,
        region=settings.AZURE_SPEECH_REGION
    )
    
    # Setup pronunciation assessment config
    pronunciation_config = speechsdk.PronunciationAssessmentConfig(
        reference_text=reference_text,
        grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
        granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme,
        enable_miscue=True
    )
    
    # Recognize from audio file
    audio_config = speechsdk.audio.AudioConfig(filename=audio_file.path)
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        audio_config=audio_config
    )
    
    pronunciation_config.apply_to(speech_recognizer)
    
    result = speech_recognizer.recognize_once()
    
    # Parse pronunciation assessment results
    pronunciation_result = speechsdk.PronunciationAssessmentResult(result)
    
    return {
        'transcript': result.text,
        'accuracy_score': pronunciation_result.accuracy_score,
        'fluency_score': pronunciation_result.fluency_score,
        'completeness_score': pronunciation_result.completeness_score,
        'pronunciation_score': pronunciation_result.pronunciation_score,
        'words': [
            {
                'word': w.word,
                'accuracy_score': w.accuracy_score,
                'error_type': w.error_type,
            }
            for w in pronunciation_result.words
        ]
    }
```

**Installation:**
```bash
pip install azure-cognitiveservices-speech
```

---

### Option 3: AssemblyAI

**Ưu điểm:**
- ✅ Simple REST API
- ✅ Affordable pricing
- ✅ Word-level confidence
- ✅ Easy to integrate

```python
import requests

def assemblyai_transcribe(audio_file):
    """
    Transcribe using AssemblyAI.
    """
    
    # Upload audio file
    headers = {'authorization': settings.ASSEMBLYAI_API_KEY}
    
    with open(audio_file.path, 'rb') as f:
        response = requests.post(
            'https://api.assemblyai.com/v2/upload',
            headers=headers,
            data=f
        )
    
    audio_url = response.json()['upload_url']
    
    # Request transcription
    response = requests.post(
        'https://api.assemblyai.com/v2/transcript',
        json={'audio_url': audio_url},
        headers=headers
    )
    
    transcript_id = response.json()['id']
    
    # Poll for completion
    while True:
        response = requests.get(
            f'https://api.assemblyai.com/v2/transcript/{transcript_id}',
            headers=headers
        )
        
        status = response.json()['status']
        if status == 'completed':
            break
        elif status == 'error':
            raise Exception('Transcription failed')
        
        time.sleep(1)
    
    result = response.json()
    
    return {
        'transcript': result['text'],
        'words': result['words'],
        'confidence': result['confidence'],
    }
```

---

## Cách tích hợp vào hệ thống

### 1. Update `TongueTwisterSubmitView`

```python
# File: backend/apps/curriculum/views_tongue_twister.py

def post(self, request, *args, **kwargs):
    # ... existing code ...
    
    # Replace mock scoring with actual STT
    if settings.USE_SPEECH_TO_TEXT:
        # Use real Speech-to-Text
        stt_result = analyze_pronunciation(audio_file, twister.text)
        
        score = stt_result['pronunciation_score']
        words_detected = len(stt_result['words'])
        accuracy = stt_result['accuracy']
        transcript = stt_result['transcript']
        
    else:
        # Keep mock scoring for development
        score, words_detected, accuracy, transcript = self._mock_scoring(twister, duration)
    
    # Save with real data
    attempt = TongueTwisterAttempt.objects.create(
        user=request.user,
        tongue_twister=twister,
        audio_file=audio_file,
        duration=duration,
        score=score,
        words_detected=words_detected,
        words_expected=len(twister.text.split()),
        accuracy=accuracy
    )
    
    return JsonResponse({
        'success': True,
        'score': int(score),
        'transcript': transcript,  # Show what was detected
        'accuracy': int(accuracy),
        'words_detected': words_detected,
        'words_expected': len(twister.text.split()),
        # ... other fields ...
    })
```

### 2. Add Settings

```python
# File: backend/config/settings.py

# Speech-to-Text Configuration
USE_SPEECH_TO_TEXT = env.bool('USE_SPEECH_TO_TEXT', default=False)
STT_PROVIDER = env.str('STT_PROVIDER', default='google')  # google, azure, assemblyai

# Google Cloud Speech-to-Text
GOOGLE_APPLICATION_CREDENTIALS = env.str('GOOGLE_APPLICATION_CREDENTIALS', default='')

# Azure Speech Service
AZURE_SPEECH_KEY = env.str('AZURE_SPEECH_KEY', default='')
AZURE_SPEECH_REGION = env.str('AZURE_SPEECH_REGION', default='')

# AssemblyAI
ASSEMBLYAI_API_KEY = env.str('ASSEMBLYAI_API_KEY', default='')
```

### 3. Update Template

Template đã được update để hiển thị:
- ✅ Audio playback (nghe lại bản ghi)
- ✅ Transcript (văn bản phát hiện được)
- ✅ Words detected/expected
- ✅ Speed (words per second)

---

## Testing

### Manual Testing (without STT)

Hiện tại có thể test với mock scoring:

```bash
# Navigate to /pronunciation/tongue-twister/
# Record audio
# See mock results with:
# - Duration-based scoring
# - Estimated words detected
# - Audio playback
```

### With Real STT

```bash
# 1. Set up API credentials
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"

# 2. Enable STT in settings
export USE_SPEECH_TO_TEXT=True
export STT_PROVIDER=google

# 3. Test
python manage.py test apps.curriculum.tests.test_tongue_twister_stt
```

---

## Pricing Comparison

### Google Cloud Speech-to-Text
- **Free tier:** 60 minutes/month
- **Paid:** $0.006/15 seconds (~$0.024/minute)
- **Best for:** High accuracy, phoneme analysis

### Azure Speech Service
- **Free tier:** 5 hours/month
- **Paid:** $1.00/hour
- **Best for:** Language learners, pronunciation assessment

### AssemblyAI
- **Free tier:** 5 hours one-time
- **Paid:** $0.65/hour
- **Best for:** Budget-friendly, simple API

---

## Roadmap

### Phase 5.1: Basic STT Integration ✅ (Sau này)
- [ ] Google Cloud Speech-to-Text setup
- [ ] Transcript display
- [ ] Word-level confidence scores

### Phase 5.2: Advanced Pronunciation Assessment
- [ ] Phoneme-level analysis
- [ ] Identify specific mispronounced sounds
- [ ] Visual feedback (highlight wrong words)

### Phase 5.3: Personalized Practice
- [ ] Track common pronunciation errors
- [ ] Generate custom practice exercises
- [ ] Progress tracking over time

---

## Hiện tại (Mock Mode)

✅ **Đã có:**
- Recording với MediaRecorder API
- Audio playback (nghe lại)
- Mock scoring algorithm (realistic enough)
- Duration-based metrics
- Leaderboard & ranking

⏳ **Đang thiếu:**
- Real Speech-to-Text analysis
- Transcript comparison
- Word-level accuracy
- Phoneme feedback

**Note:** Mock mode vẫn rất useful cho:
- Development/testing
- Demo purposes
- Khi chưa có budget cho STT API
- Fallback khi API down
