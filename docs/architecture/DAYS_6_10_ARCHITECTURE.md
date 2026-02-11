# Days 6-10 Architecture Design

**Following:** [DEVELOPMENT_WORKFLOW.md](/DEVELOPMENT_WORKFLOW.md) Phase 2

**Requirements:** [DAYS_6_10_REQUIREMENTS.md](/DAYS_6_10_REQUIREMENTS.md)

---

## ✅ EXISTING MODELS AUDIT

### Already Available ✅
```python
# apps/curriculum/models.py (Line 869-912)
class MinimalPair(models.Model):
    phoneme_1 = ForeignKey(Phoneme)
    phoneme_2 = ForeignKey(Phoneme)
    
    word_1 = CharField(max_length=100)
    word_1_ipa = CharField(max_length=200)
    word_1_meaning = CharField(max_length=200)
    word_1_audio = FileField(upload_to='minimal_pairs/audio/')
    
    word_2 = CharField(max_length=100)
    word_2_ipa = CharField(max_length=200)
    word_2_meaning = CharField(max_length=200)
    word_2_audio = FileField(upload_to='minimal_pairs/audio/')
    
    difference_note = TextField()
    difference_note_vi = TextField()
    difficulty = PositiveSmallIntegerField(default=1)  # 1-5
    order = PositiveIntegerField(default=0)
```

**✅ Perfect!** MinimalPair model exists and has everything we need:
- Two phonemes
- Two words with IPA and meaning
- Audio for both words
- Difficulty level (1-5)

### Need to Check Data
- [ ] Are there MinimalPair records in database?
- [ ] Do minimal pairs have audio files?
- [ ] Coverage: How many phoneme pairs have minimal pairs?

---

## 🆕 NEW MODELS TO CREATE

### 1. DiscriminationAttempt (apps/study/models.py)

**Purpose:** Track individual discrimination quiz attempts

```python
class DiscriminationAttempt(models.Model):
    """
    Records user's answer to a single discrimination question.
    Each question presents two phonemes and asks which matches a target sound.
    """
    # Foreign Keys
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='discrimination_attempts',
        verbose_name='Người dùng'
    )
    minimal_pair = models.ForeignKey(
        'curriculum.MinimalPair',
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name='Cặp tối thiểu'
    )
    
    # Question details
    question_type = models.CharField(
        max_length=20,
        choices=[
            ('which_word', 'Which word did you hear?'),
            ('same_different', 'Are these the same or different?'),
        ],
        default='which_word',
        verbose_name='Loại câu hỏi'
    )
    
    # For 'which_word' type
    correct_word = models.CharField(
        max_length=10,
        choices=[('word_1', 'Word 1'), ('word_2', 'Word 2')],
        verbose_name='Từ đúng'
    )
    user_answer = models.CharField(
        max_length=10,
        choices=[('word_1', 'Word 1'), ('word_2', 'Word 2')],
        verbose_name='Câu trả lời'
    )
    
    # Results
    is_correct = models.BooleanField(verbose_name='Đúng')
    response_time = models.FloatField(
        help_text='Time taken to answer in seconds',
        verbose_name='Thời gian phản hồi (giây)'
    )
    
    # Session tracking
    session_id = models.CharField(
        max_length=36,
        help_text='UUID to group questions from same quiz session',
        db_index=True,
        verbose_name='ID phiên'
    )
    question_number = models.PositiveSmallIntegerField(
        help_text='Question number within session (1-10)',
        verbose_name='Số câu hỏi'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')
    
    class Meta:
        db_table = 'discrimination_attempts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['session_id', 'question_number']),
        ]
        verbose_name = 'Lần thử phân biệt âm'
        verbose_name_plural = 'Lần thử phân biệt âm'
    
    def __str__(self):
        status = "✓" if self.is_correct else "✗"
        return f"{self.user.username} - {self.minimal_pair} [{status}]"


class DiscriminationSession(models.Model):
    """
    Groups multiple discrimination attempts into a quiz session.
    Stores session-level statistics.
    """
    # Foreign Keys
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='discrimination_sessions',
        verbose_name='Người dùng'
    )
    
    # Session details
    session_id = models.CharField(
        max_length=36,
        unique=True,
        help_text='UUID for this session',
        verbose_name='ID phiên'
    )
    total_questions = models.PositiveSmallIntegerField(
        default=10,
        verbose_name='Tổng số câu'
    )
    correct_answers = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='Số câu đúng'
    )
    accuracy = models.FloatField(
        default=0.0,
        help_text='Percentage: 0-100',
        verbose_name='Độ chính xác (%)'
    )
    
    # Time tracking
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='Bắt đầu')
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Hoàn thành'
    )
    time_limit_seconds = models.PositiveIntegerField(
        default=300,  # 5 minutes
        verbose_name='Giới hạn thời gian (giây)'
    )
    time_spent_seconds = models.PositiveIntegerField(
        default=0,
        verbose_name='Thời gian đã dùng (giây)'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('expired', 'Expired'),
            ('abandoned', 'Abandoned'),
        ],
        default='in_progress',
        db_index=True,
        verbose_name='Trạng thái'
    )
    
    class Meta:
        db_table = 'discrimination_sessions'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', '-started_at']),
            models.Index(fields=['status', '-started_at']),
        ]
        verbose_name = 'Phiên phân biệt âm'
        verbose_name_plural = 'Phiên phân biệt âm'
    
    def __str__(self):
        return f"{self.user.username} - {self.accuracy:.1f}% ({self.completed_at or 'in progress'})"
    
    def calculate_accuracy(self):
        """Calculate and update accuracy based on attempts"""
        if self.total_questions > 0:
            self.accuracy = (self.correct_answers / self.total_questions) * 100
            self.save(update_fields=['accuracy'])
```

---

### 2. ProductionRecording (apps/study/models.py)

**Purpose:** Store user pronunciation recordings

```python
class ProductionRecording(models.Model):
    """
    Stores audio recording of user's pronunciation attempt.
    Includes self-assessment and future AI scoring.
    """
    # Foreign Keys
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='production_recordings',
        verbose_name='Người dùng'
    )
    phoneme = models.ForeignKey(
        'curriculum.Phoneme',
        on_delete=models.CASCADE,
        related_name='user_recordings',
        verbose_name='Âm vị'
    )
    
    # Recording file
    recording_file = models.FileField(
        upload_to='user_recordings/%Y/%m/%d/',
        help_text='Audio file (WebM, MP4, etc.)',
        verbose_name='File ghi âm'
    )
    duration_seconds = models.FloatField(
        help_text='Recording duration in seconds',
        verbose_name='Thời lượng (giây)'
    )
    file_size_bytes = models.PositiveIntegerField(
        default=0,
        verbose_name='Kích thước file (bytes)'
    )
    mime_type = models.CharField(
        max_length=50,
        default='audio/webm',
        verbose_name='Loại MIME'
    )
    
    # Scoring
    self_assessment_score = models.PositiveSmallIntegerField(
        choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')],
        null=True,
        blank=True,
        help_text='User self-rating (1-5 stars)',
        verbose_name='Tự đánh giá (1-5 sao)'
    )
    ai_score = models.FloatField(
        null=True,
        blank=True,
        help_text='AI pronunciation analysis score (0-100). Future feature.',
        verbose_name='Điểm AI (0-100)'
    )
    ai_feedback = models.TextField(
        blank=True,
        help_text='AI-generated pronunciation feedback. Future feature.',
        verbose_name='Phản hồi từ AI'
    )
    
    # Metadata
    is_best = models.BooleanField(
        default=False,
        help_text='Mark as user\'s best recording for this phoneme',
        verbose_name='Ghi âm tốt nhất'
    )
    notes = models.TextField(
        blank=True,
        help_text='User notes about this recording',
        verbose_name='Ghi chú'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')
    
    class Meta:
        db_table = 'production_recordings'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'phoneme', '-created_at']),
            models.Index(fields=['user', 'is_best']),
        ]
        verbose_name = 'Ghi âm phát âm'
        verbose_name_plural = 'Ghi âm phát âm'
    
    def __str__(self):
        stars = '⭐' * (self.self_assessment_score or 0)
        return f"{self.user.username} - {self.phoneme.ipa_symbol} {stars}"
    
    def save(self, *args, **kwargs):
        # Auto-unmark previous "is_best" if this is marked as best
        if self.is_best:
            ProductionRecording.objects.filter(
                user=self.user,
                phoneme=self.phoneme,
                is_best=True
            ).exclude(pk=self.pk).update(is_best=False)
        super().save(*args, **kwargs)
```

---

### 3. Achievement System (apps/study/models.py)

**Purpose:** Define and track user achievements/badges

```python
class Achievement(models.Model):
    """
    Defines achievement milestones (badges).
    These are system-defined and created by admins.
    """
    # Identification
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text='Unique identifier (e.g., "first_10_phonemes")',
        verbose_name='Mã thành tích'
    )
    name = models.CharField(
        max_length=100,
        help_text='Display name (e.g., "Phoneme Pioneer")',
        verbose_name='Tên thành tích'
    )
    name_vi = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Tên tiếng Việt'
    )
    
    # Description
    description = models.TextField(
        help_text='What this achievement is for',
        verbose_name='Mô tả'
    )
    description_vi = models.TextField(
        blank=True,
        verbose_name='Mô tả tiếng Việt'
    )
    
    # Visual
    icon = models.CharField(
        max_length=50,
        help_text='Icon class or emoji (e.g., "🏆", "fas fa-trophy")',
        verbose_name='Icon'
    )
    color = models.CharField(
        max_length=20,
        default='#667eea',
        help_text='Badge color (hex)',
        verbose_name='Màu'
    )
    
    # Requirement (JSON structure)
    requirement_type = models.CharField(
        max_length=50,
        choices=[
            ('phonemes_learned', 'Number of phonemes learned'),
            ('discrimination_accuracy', 'Discrimination accuracy threshold'),
            ('production_recordings', 'Number of recordings made'),
            ('practice_streak', 'Consecutive days practiced'),
            ('total_practice_time', 'Total minutes practiced'),
        ],
        verbose_name='Loại yêu cầu'
    )
    requirement_value = models.FloatField(
        help_text='Threshold value (e.g., 10 for "10 phonemes")',
        verbose_name='Giá trị yêu cầu'
    )
    
    # Metadata
    order = models.PositiveIntegerField(
        default=0,
        help_text='Display order',
        verbose_name='Thứ tự'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Kích hoạt'
    )
    
    class Meta:
        db_table = 'achievements'
        ordering = ['order', 'requirement_value']
        verbose_name = 'Thành tích'
        verbose_name_plural = 'Thành tích'
    
    def __str__(self):
        return f"{self.icon} {self.name}"


class UserAchievement(models.Model):
    """
    Tracks which achievements a user has earned.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='achievements',
        verbose_name='Người dùng'
    )
    achievement = models.ForeignKey(
        Achievement,
        on_delete=models.CASCADE,
        related_name='user_achievements',
        verbose_name='Thành tích'
    )
    
    # Progress
    progress = models.FloatField(
        default=0.0,
        help_text='Current progress toward achievement (e.g., 7 out of 10)',
        verbose_name='Tiến độ'
    )
    is_earned = models.BooleanField(
        default=False,
        verbose_name='Đã đạt được'
    )
    
    # Timestamps
    earned_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Ngày đạt được'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Ngày tạo'
    )
    
    class Meta:
        db_table = 'user_achievements'
        ordering = ['-earned_at']
        unique_together = [['user', 'achievement']]
        indexes = [
            models.Index(fields=['user', 'is_earned']),
        ]
        verbose_name = 'Thành tích người dùng'
        verbose_name_plural = 'Thành tích người dùng'
    
    def __str__(self):
        status = "✓" if self.is_earned else f"{self.progress:.0f}%"
        return f"{self.user.username} - {self.achievement.name} [{status}]"
    
    def check_and_award(self):
        """Check if requirement is met and award achievement"""
        if self.progress >= self.achievement.requirement_value and not self.is_earned:
            self.is_earned = True
            self.earned_at = timezone.now()
            self.save()
            return True
        return False
```

---

## 📊 MODEL RELATIONSHIPS DIAGRAM

```
User (Django Auth)
├─→ DiscriminationSession
│   └─→ DiscriminationAttempt
│       └─→ MinimalPair (existing)
│           ├─→ Phoneme (existing)
│           └─→ Phoneme (existing)
│
├─→ ProductionRecording
│   └─→ Phoneme (existing)
│
├─→ UserAchievement
│   └─→ Achievement
│
└─→ UserPhonemeProgress (existing)
    └─→ Phoneme (existing)
```

---

## 🔗 API ENDPOINTS DESIGN

### Day 6-7: Discrimination Practice

#### 1. Start Quiz Session
```
POST /api/v1/discrimination/sessions/start/

Request: {}
Response: {
    "success": true,
    "session": {
        "session_id": "uuid-here",
        "total_questions": 10,
        "time_limit_seconds": 300,
        "started_at": "2025-12-16T10:00:00Z"
    },
    "questions": [
        {
            "question_number": 1,
            "minimal_pair_id": 123,
            "word_1": "ship",
            "word_1_ipa": "/ʃɪp/",
            "word_1_audio": "/media/minimal_pairs/audio/ship.mp3",
            "word_2": "sheep",
            "word_2_ipa": "/ʃiːp/",
            "word_2_audio": "/media/minimal_pairs/audio/sheep.mp3",
            "correct_word": "word_1",  # Will be validated server-side
            "phoneme_1": {
                "id": 12,
                "ipa_symbol": "/ɪ/"
            },
            "phoneme_2": {
                "id": 13,
                "ipa_symbol": "/iː/"
            }
        },
        // ... 9 more questions
    ]
}
```

#### 2. Submit Answer
```
POST /api/v1/discrimination/attempts/submit/

Request: {
    "session_id": "uuid-here",
    "question_number": 1,
    "minimal_pair_id": 123,
    "user_answer": "word_1",
    "response_time": 3.5
}

Response: {
    "success": true,
    "is_correct": true,
    "correct_answer": "word_1",
    "feedback": {
        "message": "Correct! 🎉",
        "explanation": "The word was 'ship' (/ʃɪp/) with the short /ɪ/ sound.",
        "phoneme_note": "/ɪ/ is a short vowel, while /iː/ is long."
    },
    "session_progress": {
        "answered": 1,
        "total": 10,
        "correct_so_far": 1,
        "current_accuracy": 100.0
    }
}
```

#### 3. Complete Session
```
POST /api/v1/discrimination/sessions/{session_id}/complete/

Request: {}

Response: {
    "success": true,
    "session": {
        "session_id": "uuid-here",
        "total_questions": 10,
        "correct_answers": 8,
        "accuracy": 80.0,
        "time_spent_seconds": 180,
        "completed_at": "2025-12-16T10:03:00Z"
    },
    "progress_updated": [
        {
            "phoneme_id": 12,
            "phoneme_symbol": "/ɪ/",
            "old_accuracy": 75.0,
            "new_accuracy": 77.5
        }
    ],
    "achievements_earned": [
        {
            "code": "discrimination_master",
            "name": "Discrimination Master",
            "icon": "🎯"
        }
    ]
}
```

#### 4. Get Session Results
```
GET /api/v1/discrimination/sessions/{session_id}/

Response: {
    "success": true,
    "session": { /* session details */ },
    "attempts": [ /* all 10 attempts with details */ ]
}
```

#### 5. Get User History
```
GET /api/v1/discrimination/sessions/history/
Query params: ?limit=10&offset=0

Response: {
    "success": true,
    "total_sessions": 25,
    "sessions": [ /* recent sessions */ ]
}
```

---

### Day 8-9: Production Practice

#### 1. Upload Recording
```
POST /api/v1/production/recordings/upload/

Content-Type: multipart/form-data

Form data:
- phoneme_id: 12
- recording_file: [audio blob]
- duration_seconds: 2.5
- self_assessment_score: 4 (optional)

Response: {
    "success": true,
    "recording": {
        "id": 456,
        "phoneme": {
            "id": 12,
            "ipa_symbol": "/ɪ/"
        },
        "recording_url": "/media/user_recordings/2025/12/16/recording_456.webm",
        "duration_seconds": 2.5,
        "self_assessment_score": 4,
        "is_best": false,
        "created_at": "2025-12-16T10:00:00Z"
    },
    "best_score_updated": false
}
```

#### 2. List Recordings for Phoneme
```
GET /api/v1/production/recordings/phoneme/{phoneme_id}/
Query params: ?limit=5

Response: {
    "success": true,
    "phoneme": {
        "id": 12,
        "ipa_symbol": "/ɪ/",
        "native_audio": "/media/phonemes/audio/i_short.mp3"
    },
    "recordings": [
        {
            "id": 456,
            "recording_url": "/media/...",
            "duration_seconds": 2.5,
            "self_assessment_score": 4,
            "is_best": true,
            "created_at": "2025-12-16T10:00:00Z"
        },
        // ... more recordings
    ],
    "best_score": 4,
    "total_recordings": 12
}
```

#### 3. Update Recording (Self-Assessment)
```
PATCH /api/v1/production/recordings/{id}/

Request: {
    "self_assessment_score": 5,
    "is_best": true,
    "notes": "My best attempt so far!"
}

Response: {
    "success": true,
    "recording": { /* updated recording */ },
    "progress_updated": {
        "phoneme_id": 12,
        "old_best_score": 4,
        "new_best_score": 5
    }
}
```

#### 4. Delete Recording
```
DELETE /api/v1/production/recordings/{id}/

Response: {
    "success": true,
    "message": "Recording deleted successfully"
}
```

---

### Day 10: Learning Hub Dashboard

#### 1. Get Dashboard Statistics
```
GET /api/v1/dashboard/stats/
Query params: ?period=30 (days)

Response: {
    "success": true,
    "overview": {
        "total_phonemes": 44,
        "phonemes_discovered": 20,
        "phonemes_learning": 5,
        "phonemes_mastered": 10,
        "overall_accuracy": 78.5,
        "total_practice_time_minutes": 450,
        "current_streak_days": 7,
        "longest_streak_days": 12
    },
    "discrimination": {
        "total_sessions": 25,
        "total_questions": 250,
        "correct_answers": 200,
        "accuracy": 80.0,
        "avg_response_time": 4.2
    },
    "production": {
        "total_recordings": 50,
        "phonemes_recorded": 15,
        "avg_self_assessment": 3.8
    }
}
```

#### 2. Get Chart Data
```
GET /api/v1/dashboard/charts/accuracy-trend/
Query params: ?days=30

Response: {
    "success": true,
    "chart_data": {
        "labels": ["Dec 1", "Dec 2", ..., "Dec 30"],
        "datasets": [
            {
                "label": "Discrimination Accuracy",
                "data": [70, 72, 75, 78, 80, ...]
            },
            {
                "label": "Production Score",
                "data": [3.0, 3.2, 3.5, 3.8, 4.0, ...]
            }
        ]
    }
}
```

#### 3. Get Practice Recommendations
```
GET /api/v1/dashboard/recommendations/

Response: {
    "success": true,
    "recommendations": [
        {
            "phoneme_id": 12,
            "ipa_symbol": "/ɪ/",
            "reason": "Low discrimination accuracy (65%)",
            "priority": "high",
            "suggested_action": "Practice minimal pairs: ship/sheep, sit/seat"
        },
        {
            "phoneme_id": 15,
            "ipa_symbol": "/æ/",
            "reason": "Not practiced in 7 days",
            "priority": "medium",
            "suggested_action": "Review this phoneme"
        },
        {
            "phoneme_id": 20,
            "ipa_symbol": "/θ/",
            "reason": "Low production score (2.5/5)",
            "priority": "high",
            "suggested_action": "Record more pronunciations"
        }
    ]
}
```

#### 4. Get Recent Activity
```
GET /api/v1/dashboard/activity/
Query params: ?limit=10

Response: {
    "success": true,
    "activities": [
        {
            "type": "discrimination_session",
            "timestamp": "2025-12-16T10:00:00Z",
            "details": {
                "accuracy": 80.0,
                "questions": 10
            },
            "message": "Completed discrimination quiz: 8/10 correct"
        },
        {
            "type": "production_recording",
            "timestamp": "2025-12-16T09:30:00Z",
            "details": {
                "phoneme": "/ɪ/",
                "score": 4
            },
            "message": "Recorded pronunciation of /ɪ/ (4⭐)"
        },
        // ... more activities
    ]
}
```

#### 5. Get Achievements
```
GET /api/v1/dashboard/achievements/

Response: {
    "success": true,
    "earned": [
        {
            "code": "first_10_phonemes",
            "name": "Phoneme Pioneer",
            "icon": "🎯",
            "earned_at": "2025-12-10T10:00:00Z"
        }
    ],
    "in_progress": [
        {
            "code": "discrimination_master",
            "name": "Discrimination Master",
            "icon": "🏆",
            "progress": 18,
            "required": 20,
            "progress_percent": 90
        }
    ],
    "locked": [
        {
            "code": "master_all_vowels",
            "name": "Vowel Master",
            "icon": "💎",
            "requirement": "Master all 20 vowel phonemes"
        }
    ]
}
```

---

## 🛣️ URL STRUCTURE

### Page URLs (Template Views)

```python
# apps/curriculum/urls.py (or create apps/study/urls.py)

urlpatterns = [
    # ... existing URLs ...
    
    # Discrimination Practice
    path('discrimination/start/', views.discrimination_start_view, name='discrimination_start'),
    path('discrimination/quiz/<str:session_id>/', views.discrimination_quiz_view, name='discrimination_quiz'),
    path('discrimination/results/<str:session_id>/', views.discrimination_results_view, name='discrimination_results'),
    
    # Production Practice
    path('production/phoneme/<int:phoneme_id>/', views.production_practice_view, name='production_practice'),
    path('production/recordings/', views.production_recordings_view, name='production_recordings'),
    
    # Learning Hub Dashboard (Day 10)
    path('learning-hub/', views.learning_hub_view, name='learning_hub'),
    path('learning-hub/achievements/', views.achievements_view, name='achievements'),
]
```

### API URLs

```python
# apps/study/urls.py or apps/curriculum/urls.py

from apps.study.api import (
    discrimination_api,
    production_api,
    dashboard_api
)

urlpatterns = [
    # Discrimination API
    path('api/v1/discrimination/sessions/start/', discrimination_api.start_session),
    path('api/v1/discrimination/attempts/submit/', discrimination_api.submit_attempt),
    path('api/v1/discrimination/sessions/<str:session_id>/', discrimination_api.get_session),
    path('api/v1/discrimination/sessions/<str:session_id>/complete/', discrimination_api.complete_session),
    path('api/v1/discrimination/sessions/history/', discrimination_api.get_history),
    
    # Production API
    path('api/v1/production/recordings/upload/', production_api.upload_recording),
    path('api/v1/production/recordings/phoneme/<int:phoneme_id>/', production_api.list_recordings),
    path('api/v1/production/recordings/<int:id>/', production_api.get_recording),
    path('api/v1/production/recordings/<int:id>/update/', production_api.update_recording),
    path('api/v1/production/recordings/<int:id>/delete/', production_api.delete_recording),
    
    # Dashboard API
    path('api/v1/dashboard/stats/', dashboard_api.get_stats),
    path('api/v1/dashboard/charts/accuracy-trend/', dashboard_api.get_accuracy_trend),
    path('api/v1/dashboard/charts/practice-frequency/', dashboard_api.get_practice_frequency),
    path('api/v1/dashboard/recommendations/', dashboard_api.get_recommendations),
    path('api/v1/dashboard/activity/', dashboard_api.get_recent_activity),
    path('api/v1/dashboard/achievements/', dashboard_api.get_achievements),
]
```

---

## ✅ MODEL FIELD VERIFICATION CHECKLIST

Before coding, verify these fields exist:

### Phoneme Model ✅
- [x] `id`
- [x] `ipa_symbol`
- [x] `audio_sample` (FileField)
- [x] `mouth_diagram` (ImageField)

### MinimalPair Model ✅
- [x] `id`
- [x] `phoneme_1` (ForeignKey)
- [x] `phoneme_2` (ForeignKey)
- [x] `word_1`, `word_1_ipa`, `word_1_audio`
- [x] `word_2`, `word_2_ipa`, `word_2_audio`
- [x] `difficulty` (1-5)

### UserPhonemeProgress Model ✅
- [x] `user`
- [x] `phoneme`
- [x] `discrimination_accuracy` (NOT discrimination_score)
- [x] `discrimination_attempts`
- [x] `production_best_score` (NOT production_score)
- [x] `times_practiced` (NOT practice_count)

---

## 🎨 FRONTEND LIBRARIES INTEGRATION

### Chart.js (Dashboard Charts)

```html
<!-- In dashboard template -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0"></script>

<script>
// Line chart: Accuracy trend
const ctx = document.getElementById('accuracyChart').getContext('2d');
new Chart(ctx, {
    type: 'line',
    data: {
        labels: chartData.labels,
        datasets: chartData.datasets
    },
    options: {
        responsive: true,
        plugins: {
            title: { display: true, text: 'Accuracy Trend (30 Days)' }
        }
    }
});
</script>
```

### WaveSurfer.js (Audio Waveforms)

```html
<!-- In production practice template -->
<script src="https://unpkg.com/wavesurfer.js@7.7.0"></script>

<script>
// Native speaker waveform
const nativeWave = WaveSurfer.create({
    container: '#native-waveform',
    waveColor: '#667eea',
    progressColor: '#764ba2',
    height: 80
});
nativeWave.load('/media/phonemes/audio/phoneme.mp3');

// User recording waveform
const userWave = WaveSurfer.create({
    container: '#user-waveform',
    waveColor: '#10b981',
    progressColor: '#059669',
    height: 80
});
</script>
```

---

## 🔄 DATA FLOW EXAMPLES

### Discrimination Quiz Flow

```
1. User clicks "Start Quiz"
   → POST /api/v1/discrimination/sessions/start/
   → Server creates DiscriminationSession (session_id)
   → Server generates 10 random questions from MinimalPair
   → Return session + questions

2. User answers question 1
   → POST /api/v1/discrimination/attempts/submit/
   → Server creates DiscriminationAttempt record
   → Server validates answer
   → Return is_correct + feedback
   → Update session progress

3. ... repeat for questions 2-10 ...

4. User finishes all 10 questions
   → POST /api/v1/discrimination/sessions/{id}/complete/
   → Server calculates session accuracy
   → Server updates UserPhonemeProgress.discrimination_accuracy
   → Server checks for new achievements
   → Return session results + achievements

5. Redirect to results page
   → GET /discrimination/results/{session_id}/
   → Show accuracy, breakdown, recommendations
```

### Production Recording Flow

```
1. User selects phoneme to practice
   → GET /production/phoneme/12/
   → Load page with native audio + recording UI

2. User requests mic permission
   → navigator.mediaDevices.getUserMedia({audio: true})
   → Browser prompts for permission

3. User clicks "Record"
   → Start MediaRecorder
   → Visualize waveform in real-time

4. User clicks "Stop"
   → Stop MediaRecorder
   → Get audio blob
   → Play back for review

5. User rates recording (4 stars)
   → POST /api/v1/production/recordings/upload/
   → FormData: phoneme_id, file, duration, score
   → Server saves to media/user_recordings/
   → Server creates ProductionRecording record
   → Server updates UserPhonemeProgress.production_best_score if higher
   → Return recording details

6. User views recording history
   → GET /api/v1/production/recordings/phoneme/12/?limit=5
   → Show last 5 recordings with playback
```

---

## 📦 DEPENDENCIES CHECK

### Python (Backend)
- ✅ Django 5.2.9 (already installed)
- ✅ Django REST Framework (already installed)
- ✅ Pillow (for images - already installed)
- ❓ **Need to verify:** Audio file handling libraries (if AI scoring in future)

### JavaScript (Frontend - CDN, no install needed)
- ✅ Vue.js 3 (already using)
- 🆕 Chart.js 4.4.0 (add to dashboard)
- 🆕 WaveSurfer.js 7.7.0 (add to production practice)

### Browser APIs
- 🆕 MediaRecorder API (modern browsers)
- 🆕 navigator.mediaDevices.getUserMedia (mic permission)

---

## 🧪 TESTING STRATEGY

### Model Tests
```python
# Test DiscriminationAttempt creation
# Test session accuracy calculation
# Test ProductionRecording file upload
# Test Achievement awarding logic
```

### API Tests
```python
# Test start_session endpoint
# Test submit_attempt validation
# Test recording upload (multipart/form-data)
# Test dashboard stats calculation
```

### Integration Tests
```python
# Complete discrimination quiz flow (10 questions)
# Record and playback production audio
# Dashboard data accuracy with mock data
```

### Manual Browser Tests
```
# Discrimination: Audio playback, timer, feedback
# Production: Mic permission, recording, waveform
# Dashboard: Charts rendering, responsive design
```

---

## ⚠️ POTENTIAL ISSUES & SOLUTIONS

### Issue 1: Audio file size
**Problem:** User recordings could be large (5MB+)  
**Solution:** Limit recording to 5 seconds, compress on server if needed

### Issue 2: Browser compatibility
**Problem:** Safari uses different audio codecs (MP4/AAC vs WebM)  
**Solution:** Detect browser, accept multiple formats, convert server-side if needed

### Issue 3: MinimalPair data availability
**Problem:** Not enough minimal pairs with audio  
**Solution:** 
- Phase 1: Use existing pairs
- Phase 2: Generate audio with TTS
- Phase 3: Record native speaker audio

### Issue 4: Timer accuracy
**Problem:** 5-minute quiz timer needs to be accurate  
**Solution:** 
- Server-side validation (compare started_at vs completed_at)
- Client-side countdown (UI only)
- Auto-submit when time expires

### Issue 5: Concurrent recording sessions
**Problem:** User opens multiple tabs, records simultaneously  
**Solution:** Check for active session before creating new one

---

## 📝 NEXT STEPS: PHASE 3 - UI/UX DESIGN

After user approval of this architecture, proceed to:

1. ✅ Wireframes for all 3 features
2. ✅ Component library usage (buttons, cards, modals)
3. ✅ Color scheme application
4. ✅ Responsive design considerations
5. ✅ Vue.js component structure

---

**Status:** ⏳ Awaiting user approval  
**Phase:** 2 - Architecture Design (COMPLETE)  
**Next Phase:** 3 - UI/UX Design

**Questions for User:**
1. Approve model structures? ✅ / ❌
2. Approve API endpoints? ✅ / ❌
3. Any changes needed before UI design?
4. Should I proceed to Phase 3 (UI/UX Design)?
