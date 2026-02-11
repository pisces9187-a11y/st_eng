"""Curriculum models - Course, Unit, Lesson, Sentence, Flashcard."""

from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from datetime import timedelta


#============================================================================
# PRONUNCIATION CURRICULUM STAGE MODEL
#============================================================================

class CurriculumStage(models.Model):
    """
    4 Giai đoạn học phát âm theo phương pháp chuẩn:
    - Giai đoạn 1: Nguyên âm đơn (Monophthongs) - Linh hồn của từ
    - Giai đoạn 2: Phụ âm theo cặp (Consonant Pairs) - Âm gió vs Âm rung
    - Giai đoạn 3: Nguyên âm đôi (Diphthongs) - Sự hòa quyện
    - Giai đoạn 4: Nâng cao - Ending Sounds, Clusters, Lỗi người Việt
    """
    
    number = models.PositiveSmallIntegerField(
        unique=True,
        verbose_name='Số giai đoạn',
        help_text='1-4'
    )
    name = models.CharField(max_length=100, verbose_name='Tên giai đoạn')
    name_vi = models.CharField(max_length=100, verbose_name='Tên tiếng Việt')
    description = models.TextField(blank=True, verbose_name='Mô tả')
    description_vi = models.TextField(blank=True, verbose_name='Mô tả tiếng Việt')
    
    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Icon class',
        help_text='Font Awesome icon class'
    )
    color = models.CharField(
        max_length=20,
        default='#F47C26',
        verbose_name='Màu đại diện'
    )
    
    # Focus area
    focus_area = models.TextField(
        blank=True,
        verbose_name='Trọng tâm',
        help_text='Ví dụ: Khẩu hình miệng, Rung cổ họng, etc.'
    )
    
    # Learning objectives
    objectives = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Mục tiêu học tập',
        help_text='List of learning objectives'
    )
    
    # Prerequisites
    required_previous_stages = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='unlocks_stages',
        verbose_name='Giai đoạn tiên quyết'
    )
    
    # Estimated completion
    estimated_lessons = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='Số bài học ước tính'
    )
    estimated_hours = models.FloatField(
        default=0,
        verbose_name='Thời gian ước tính (giờ)'
    )
    
    order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True, verbose_name='Kích hoạt')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'curriculum'
        db_table = 'curriculum_stages'
        ordering = ['order', 'number']
        verbose_name = 'Giai đoạn học'
        verbose_name_plural = 'Giai đoạn học'
    
    def __str__(self):
        return f"Giai đoạn {self.number}: {self.name_vi}"
    
    @property
    def total_lessons(self):
        """Return total number of published lessons in this stage."""
        return self.lessons.filter(status='published').count()
    
    @property
    def progress_percentage(self, user):
        """Calculate user's progress in this stage."""
        from apps.study.models import UserPronunciationLessonProgress
        
        total = self.total_lessons
        if total == 0:
            return 0
        
        completed = UserPronunciationLessonProgress.objects.filter(
            user=user,
            lesson__stage=self,
            completed=True
        ).count()
        
        return int((completed / total) * 100)


#============================================================================
# COURSE MODELS
#============================================================================

class Course(models.Model):
    """
    Course model representing a language course at a specific CEFR level.
    
    A course contains multiple units and tracks overall progress.
    Example: "English A1 - Beginner", "English B2 - Upper Intermediate"
    """
    
    CEFR_LEVEL_CHOICES = [
        ('A1', 'A1 - Beginner'),
        ('A2', 'A2 - Elementary'),
        ('B1', 'B1 - Intermediate'),
        ('B2', 'B2 - Upper Intermediate'),
        ('C1', 'C1 - Advanced'),
        ('C2', 'C2 - Proficiency'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    # Basic info
    title = models.CharField(max_length=200, verbose_name='Tên khóa học')
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name='Mô tả')
    thumbnail = models.ImageField(
        upload_to='courses/thumbnails/',
        blank=True,
        null=True,
        verbose_name='Hình thu nhỏ'
    )
    
    # Level and requirements
    cefr_level = models.CharField(
        max_length=2,
        choices=CEFR_LEVEL_CHOICES,
        default='A1',
        db_index=True,
        verbose_name='Trình độ CEFR'
    )
    estimated_hours = models.PositiveIntegerField(
        default=0,
        verbose_name='Thời gian ước tính (giờ)'
    )
    
    # Status and visibility
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft',
        db_index=True
    )
    is_free = models.BooleanField(default=False, verbose_name='Miễn phí')
    is_featured = models.BooleanField(default=False, verbose_name='Nổi bật')
    
    # Ordering
    order = models.PositiveIntegerField(default=0, db_index=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'courses'
        ordering = ['cefr_level', 'order', 'title']
        verbose_name = 'Khóa học'
        verbose_name_plural = 'Khóa học'
        indexes = [
            models.Index(fields=['status', 'cefr_level']),
            models.Index(fields=['is_featured', 'status']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.cefr_level})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
    
    @property
    def total_units(self):
        """Return total number of units in this course."""
        return self.units.count()
    
    @property
    def total_lessons(self):
        """Return total number of lessons across all units."""
        return Lesson.objects.filter(unit__course=self).count()


class Unit(models.Model):
    """
    Unit model representing a module within a course.
    
    Each unit focuses on a specific topic or theme and contains multiple lessons.
    Example: "Unit 1: Greetings and Introductions"
    """
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='units',
        verbose_name='Khóa học'
    )
    
    # Basic info
    title = models.CharField(max_length=200, verbose_name='Tên unit')
    slug = models.SlugField(max_length=220, blank=True)
    description = models.TextField(blank=True, verbose_name='Mô tả')
    thumbnail = models.ImageField(
        upload_to='units/thumbnails/',
        blank=True,
        null=True
    )
    
    # Topic/Theme for this unit
    topic = models.CharField(max_length=100, blank=True, verbose_name='Chủ đề')
    
    # Status and ordering
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft',
        db_index=True
    )
    order = models.PositiveIntegerField(default=0, db_index=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'units'
        ordering = ['course', 'order', 'title']
        verbose_name = 'Unit'
        verbose_name_plural = 'Units'
        unique_together = [['course', 'slug']]
        indexes = [
            models.Index(fields=['course', 'status', 'order']),
        ]
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    @property
    def total_lessons(self):
        """Return total number of lessons in this unit."""
        return self.lessons.count()


class Lesson(models.Model):
    """
    Lesson model representing a single learning session.
    
    Each lesson contains sentences for practice and can include various content types.
    Example: "Lesson 1: Saying Hello"
    """
    
    LESSON_TYPE_CHOICES = [
        ('vocabulary', 'Vocabulary'),
        ('grammar', 'Grammar'),
        ('listening', 'Listening'),
        ('speaking', 'Speaking'),
        ('reading', 'Reading'),
        ('writing', 'Writing'),
        ('mixed', 'Mixed Skills'),
        ('review', 'Review'),
        ('test', 'Test'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    unit = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name='Unit'
    )
    
    # Basic info
    title = models.CharField(max_length=200, verbose_name='Tên bài học')
    slug = models.SlugField(max_length=220, blank=True)
    description = models.TextField(blank=True, verbose_name='Mô tả')
    thumbnail = models.ImageField(
        upload_to='lessons/thumbnails/',
        blank=True,
        null=True
    )
    
    # Lesson type and difficulty
    lesson_type = models.CharField(
        max_length=20,
        choices=LESSON_TYPE_CHOICES,
        default='mixed',
        db_index=True,
        verbose_name='Loại bài học'
    )
    difficulty = models.PositiveSmallIntegerField(
        default=1,
        verbose_name='Độ khó (1-10)'
    )
    
    # Content - HTML content for theory/explanation
    content_html = models.TextField(blank=True, verbose_name='Nội dung HTML')
    
    # Objectives - JSON array of learning objectives
    objectives = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Mục tiêu học tập'
    )
    
    # Duration in minutes
    estimated_minutes = models.PositiveIntegerField(
        default=15,
        verbose_name='Thời gian ước tính (phút)'
    )
    
    # XP reward for completing
    xp_reward = models.PositiveIntegerField(
        default=10,
        verbose_name='XP thưởng'
    )
    
    # Status and ordering
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft',
        db_index=True
    )
    order = models.PositiveIntegerField(default=0, db_index=True)
    
    # Premium content flag
    is_premium = models.BooleanField(default=False, verbose_name='Nội dung Premium')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lessons'
        ordering = ['unit', 'order', 'title']
        verbose_name = 'Bài học'
        verbose_name_plural = 'Bài học'
        unique_together = [['unit', 'slug']]
        indexes = [
            models.Index(fields=['unit', 'status', 'order']),
            models.Index(fields=['lesson_type', 'status']),
        ]
    
    def __str__(self):
        return f"{self.unit.title} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    @property
    def total_sentences(self):
        """Return total number of sentences in this lesson."""
        return self.sentences.count()
    
    @property
    def total_flashcards(self):
        """Return total number of flashcards in this lesson."""
        return self.flashcards.count()
    
    @property
    def course(self):
        """Return the course this lesson belongs to."""
        return self.unit.course


class Sentence(models.Model):
    """
    Sentence model for practice content.
    
    Contains the actual learning content with audio, IPA transcription,
    translation, and grammar analysis.
    """
    
    SENTENCE_TYPE_CHOICES = [
        ('statement', 'Statement'),
        ('question', 'Question'),
        ('exclamation', 'Exclamation'),
        ('imperative', 'Imperative'),
        ('dialogue', 'Dialogue'),
    ]
    
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='sentences',
        verbose_name='Bài học'
    )
    
    # Main content
    text_content = models.TextField(verbose_name='Nội dung câu')
    text_vi = models.TextField(blank=True, verbose_name='Bản dịch tiếng Việt')
    
    # Audio for pronunciation
    audio_file = models.FileField(
        upload_to='sentences/audio/',
        blank=True,
        null=True,
        verbose_name='File âm thanh'
    )
    audio_duration = models.FloatField(
        default=0,
        verbose_name='Thời lượng (giây)'
    )
    
    # Phonetic transcription
    ipa_transcription = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Phiên âm IPA'
    )
    
    # Grammar analysis - JSON structure:
    # {
    #     "parts_of_speech": [{"word": "...", "pos": "noun", "index": 0}],
    #     "tense": "present_simple",
    #     "structure": "S + V + O",
    #     "notes": "..."
    # }
    grammar_analysis = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Phân tích ngữ pháp'
    )
    
    # Vocabulary highlights - JSON array of words to highlight
    # [{"word": "hello", "definition": "...", "example": "..."}]
    vocabulary_highlights = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Từ vựng nổi bật'
    )
    
    # Sentence type and properties
    sentence_type = models.CharField(
        max_length=20,
        choices=SENTENCE_TYPE_CHOICES,
        default='statement'
    )
    
    # Slow audio for learning
    audio_slow = models.FileField(
        upload_to='sentences/audio_slow/',
        blank=True,
        null=True,
        verbose_name='Audio chậm'
    )
    
    # Context or situation description
    context = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Ngữ cảnh'
    )
    
    # Ordering
    order = models.PositiveIntegerField(default=0, db_index=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sentences'
        ordering = ['lesson', 'order']
        verbose_name = 'Câu'
        verbose_name_plural = 'Câu'
        indexes = [
            models.Index(fields=['lesson', 'order']),
        ]
    
    def __str__(self):
        preview = self.text_content[:50]
        if len(self.text_content) > 50:
            preview += '...'
        return f"{self.lesson.title}: {preview}"
    
    @property
    def word_count(self):
        """Return the number of words in this sentence."""
        return len(self.text_content.split())


class Flashcard(models.Model):
    """
    Flashcard model for vocabulary learning.
    
    Contains a front (question/word) and back (answer/definition) side,
    along with additional learning content.
    """
    
    CARD_TYPE_CHOICES = [
        ('vocabulary', 'Vocabulary'),
        ('phrase', 'Phrase'),
        ('sentence', 'Sentence'),
        ('grammar', 'Grammar Point'),
        ('idiom', 'Idiom'),
        ('collocation', 'Collocation'),
    ]
    
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='flashcards',
        null=True,
        blank=True,
        verbose_name='Bài học'
    )
    
    # Can also link to a specific sentence
    sentence = models.ForeignKey(
        Sentence,
        on_delete=models.SET_NULL,
        related_name='flashcards',
        null=True,
        blank=True,
        verbose_name='Câu liên quan'
    )
    
    # Card content
    front_text = models.TextField(verbose_name='Mặt trước (từ/câu hỏi)')
    back_text = models.TextField(verbose_name='Mặt sau (định nghĩa/đáp án)')
    
    # Additional info
    front_audio = models.FileField(
        upload_to='flashcards/audio/',
        blank=True,
        null=True,
        verbose_name='Audio mặt trước'
    )
    front_image = models.ImageField(
        upload_to='flashcards/images/',
        blank=True,
        null=True,
        verbose_name='Hình mặt trước'
    )
    
    # IPA for pronunciation
    ipa = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Phiên âm IPA'
    )
    
    # Example sentences - JSON array
    # [{"en": "Hello, how are you?", "vi": "Xin chào, bạn khỏe không?"}]
    examples = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Câu ví dụ'
    )
    
    # Part of speech for vocabulary cards
    part_of_speech = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Từ loại'
    )
    
    # Card type
    card_type = models.CharField(
        max_length=20,
        choices=CARD_TYPE_CHOICES,
        default='vocabulary',
        db_index=True
    )
    
    # Difficulty level (1-5)
    difficulty = models.PositiveSmallIntegerField(
        default=1,
        verbose_name='Độ khó (1-5)'
    )
    
    # Tags for categorization - JSON array
    tags = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Tags'
    )
    
    # Active flag
    is_active = models.BooleanField(default=True)
    
    # Ordering
    order = models.PositiveIntegerField(default=0, db_index=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'flashcards'
        ordering = ['lesson', 'order']
        verbose_name = 'Flashcard'
        verbose_name_plural = 'Flashcards'
        indexes = [
            models.Index(fields=['lesson', 'card_type']),
            models.Index(fields=['card_type', 'is_active']),
        ]
    
    def __str__(self):
        preview = self.front_text[:30]
        if len(self.front_text) > 30:
            preview += '...'
        return f"Flashcard: {preview}"


class GrammarRule(models.Model):
    """
    Grammar rule model for grammar wiki and lesson references.
    
    Contains detailed grammar explanations with examples.
    """
    
    CEFR_LEVEL_CHOICES = [
        ('A1', 'A1 - Beginner'),
        ('A2', 'A2 - Elementary'),
        ('B1', 'B1 - Intermediate'),
        ('B2', 'B2 - Upper Intermediate'),
        ('C1', 'C1 - Advanced'),
        ('C2', 'C2 - Proficiency'),
    ]
    
    # Basic info
    title = models.CharField(max_length=200, verbose_name='Tên quy tắc')
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    
    # Category (e.g., "Tenses", "Articles", "Prepositions")
    category = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name='Danh mục'
    )
    
    # Level
    cefr_level = models.CharField(
        max_length=2,
        choices=CEFR_LEVEL_CHOICES,
        default='A1',
        db_index=True
    )
    
    # Content - HTML formatted explanation
    explanation_html = models.TextField(verbose_name='Giải thích')
    explanation_vi = models.TextField(
        blank=True,
        verbose_name='Giải thích tiếng Việt'
    )
    
    # Structure pattern
    structure = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Cấu trúc'
    )
    
    # Examples - JSON array
    # [{"en": "I am a student.", "vi": "Tôi là sinh viên.", "note": "..."}]
    examples = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Ví dụ'
    )
    
    # Common mistakes - JSON array
    # [{"wrong": "...", "correct": "...", "explanation": "..."}]
    common_mistakes = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Lỗi thường gặp'
    )
    
    # Related rules
    related_rules = models.ManyToManyField(
        'self',
        blank=True,
        verbose_name='Quy tắc liên quan'
    )
    
    # Active flag
    is_active = models.BooleanField(default=True)
    
    # Ordering
    order = models.PositiveIntegerField(default=0, db_index=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'grammar_rules'
        ordering = ['category', 'order', 'title']
        verbose_name = 'Quy tắc ngữ pháp'
        verbose_name_plural = 'Quy tắc ngữ pháp'
        indexes = [
            models.Index(fields=['category', 'cefr_level']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.cefr_level})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


# =============================================================================
# PRONUNCIATION / IPA LEARNING MODELS
# =============================================================================

class PhonemeCategory(models.Model):
    """
    Category for phonemes (Vowels, Consonants, Diphthongs).
    """
    CATEGORY_TYPES = [
        ('vowel', 'Nguyên âm đơn (Monophthongs)'),
        ('diphthong', 'Nguyên âm đôi (Diphthongs)'),
        ('consonant', 'Phụ âm (Consonants)'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Tên danh mục')
    name_vi = models.CharField(max_length=100, verbose_name='Tên tiếng Việt')
    category_type = models.CharField(
        max_length=20,
        choices=CATEGORY_TYPES,
        default='vowel',
        db_index=True
    )
    description = models.TextField(blank=True, verbose_name='Mô tả')
    description_vi = models.TextField(blank=True, verbose_name='Mô tả tiếng Việt')
    icon = models.CharField(max_length=50, blank=True, verbose_name='Icon class')
    order = models.PositiveIntegerField(default=0, db_index=True)
    
    preferred_audio_source = models.ForeignKey(
        'AudioSource',  # Forward reference vì AudioSource định nghĩa sau
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='preferred_for_phonemes',
        verbose_name='Audio ưu tiên'
    )
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'phoneme_categories'
        ordering = ['order', 'name']
        verbose_name = 'Danh mục âm'
        verbose_name_plural = 'Danh mục âm'
    
    def __str__(self):
        return f"{self.name_vi} ({self.name})"


class Phoneme(models.Model):
    """
    Individual phoneme (sound) with IPA symbol.
    Example: /i:/, /ɪ/, /p/, /b/
    """
    PHONEME_TYPES = [
        ('short_vowel', 'Nguyên âm ngắn'),
        ('long_vowel', 'Nguyên âm dài'),
        ('diphthong', 'Nguyên âm đôi'),
        ('plosive', 'Âm bật hơi (Plosives)'),
        ('fricative', 'Âm xát (Fricatives)'),
        ('affricate', 'Âm tắc xát (Affricates)'),
        ('nasal', 'Âm mũi (Nasals)'),
        ('approximant', 'Âm tiếp cận (Approximants)'),
        ('lateral', 'Âm bên (Laterals)'),
    ]
    
    VOICING_TYPES = [
        ('voiced', 'Hữu thanh (Voiced)'),
        ('voiceless', 'Vô thanh (Voiceless/Unvoiced)'),
        ('n/a', 'Không áp dụng'),
    ]
    
    category = models.ForeignKey(
        PhonemeCategory,
        on_delete=models.CASCADE,
        related_name='phonemes',
        verbose_name='Danh mục'
    )
    
    # IPA symbol
    ipa_symbol = models.CharField(max_length=10, unique=True, verbose_name='Ký hiệu IPA')
    
    # Vietnamese approximation
    vietnamese_approx = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Phát âm gần đúng (tiếng Việt)'
    )
    
    # Vietnamese comparison - NEW FIELD
    vietnamese_comparison = models.TextField(
        blank=True,
        verbose_name='So sánh với tiếng Việt',
        help_text='Ví dụ: /p/ tiếng Anh bật hơi mạnh hơn /p/ tiếng Việt'
    )
    
    # Type and voicing
    phoneme_type = models.CharField(
        max_length=20,
        choices=PHONEME_TYPES,
        default='short_vowel',
        db_index=True
    )
    voicing = models.CharField(
        max_length=10,
        choices=VOICING_TYPES,
        default='n/a'
    )
    
    # Paired phoneme (for voiced/voiceless pairs like /p/-/b/)
    paired_phoneme = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pair',
        verbose_name='Âm ghép cặp'
    )
    
    # Mouth position description
    mouth_position = models.TextField(blank=True, verbose_name='Vị trí miệng')
    mouth_position_vi = models.TextField(blank=True, verbose_name='Vị trí miệng (tiếng Việt)')
    
    # Tongue position
    tongue_position = models.TextField(blank=True, verbose_name='Vị trí lưỡi')
    tongue_position_vi = models.TextField(blank=True, verbose_name='Vị trí lưỡi (tiếng Việt)')
    
    # Tips for pronunciation
    pronunciation_tips = models.TextField(blank=True, verbose_name='Mẹo phát âm')
    pronunciation_tips_vi = models.TextField(blank=True, verbose_name='Mẹo phát âm (tiếng Việt)')
    
    # Audio sample
    audio_sample = models.FileField(
        upload_to='phonemes/audio/',
        blank=True,
        null=True,
        verbose_name='Audio mẫu'
    )
    
    # Image showing mouth position
    mouth_diagram = models.ImageField(
        upload_to='phonemes/diagrams/',
        blank=True,
        null=True,
        verbose_name='Hình miệng'
    )
    
    # Common mistakes Vietnamese speakers make
    common_mistakes_vi = models.TextField(blank=True, verbose_name='Lỗi người Việt hay mắc')
    
    # Audio of common Vietnamese mistake - NEW FIELD
    vietnamese_mistake_audio = models.FileField(
        upload_to='phonemes/mistake_audio/',
        blank=True,
        null=True,
        verbose_name='Audio lỗi người Việt hay mắc',
        help_text='Recording demonstrating the common mistake'
    )
    
    preferred_audio_source = models.ForeignKey(
        'AudioSource',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='preferred_for_phoneme',
        verbose_name='Audio ưu tiên'
    )
    order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'phonemes'
        ordering = ['category', 'order']
        verbose_name = 'Âm vị (Phoneme)'
        verbose_name_plural = 'Âm vị (Phonemes)'
    
    def __str__(self):
        return f"/{self.ipa_symbol}/ - {self.vietnamese_approx}"


class PhonemeWord(models.Model):
    """
    Example words for each phoneme.
    """
    POSITION_CHOICES = [
        ('initial', 'Đầu từ'),
        ('medial', 'Giữa từ'),
        ('final', 'Cuối từ'),
    ]
    
    phoneme = models.ForeignKey(
        Phoneme,
        on_delete=models.CASCADE,
        related_name='example_words',
        verbose_name='Âm vị'
    )
    
    word = models.CharField(max_length=100, verbose_name='Từ')
    ipa_transcription = models.CharField(max_length=200, verbose_name='Phiên âm IPA')
    meaning_vi = models.CharField(max_length=200, blank=True, verbose_name='Nghĩa tiếng Việt')
    
    # Position of the phoneme in word
    phoneme_position = models.CharField(
        max_length=10,
        choices=POSITION_CHOICES,
        default='initial'
    )
    
    # Highlight range in IPA (start, end index)
    highlight_start = models.PositiveSmallIntegerField(default=0)
    highlight_end = models.PositiveSmallIntegerField(default=1)
    
    # Audio
    audio_file = models.FileField(
        upload_to='phoneme_words/audio/',
        blank=True,
        null=True
    )
    audio_slow = models.FileField(
        upload_to='phoneme_words/audio_slow/',
        blank=True,
        null=True
    )
    
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'phoneme_words'
        ordering = ['phoneme', 'order']
        verbose_name = 'Từ ví dụ'
        verbose_name_plural = 'Từ ví dụ'
    
    def __str__(self):
        return f"{self.word} /{self.ipa_transcription}/"


class MinimalPair(models.Model):
    """
    Minimal pairs for phoneme contrast exercises.
    Example: ship/sheep, bat/bad
    """
    phoneme_1 = models.ForeignKey(
        Phoneme,
        on_delete=models.CASCADE,
        related_name='minimal_pairs_1',
        verbose_name='Âm 1'
    )
    phoneme_2 = models.ForeignKey(
        Phoneme,
        on_delete=models.CASCADE,
        related_name='minimal_pairs_2',
        verbose_name='Âm 2'
    )
    
    word_1 = models.CharField(max_length=100, verbose_name='Từ 1')
    word_1_ipa = models.CharField(max_length=200, verbose_name='IPA từ 1')
    word_1_meaning = models.CharField(max_length=200, blank=True, verbose_name='Nghĩa từ 1')
    word_1_audio = models.FileField(upload_to='minimal_pairs/audio/', blank=True, null=True)
    
    word_2 = models.CharField(max_length=100, verbose_name='Từ 2')
    word_2_ipa = models.CharField(max_length=200, verbose_name='IPA từ 2')
    word_2_meaning = models.CharField(max_length=200, blank=True, verbose_name='Nghĩa từ 2')
    word_2_audio = models.FileField(upload_to='minimal_pairs/audio/', blank=True, null=True)
    
    # Explanation of difference
    difference_note = models.TextField(blank=True, verbose_name='Ghi chú khác biệt')
    difference_note_vi = models.TextField(blank=True, verbose_name='Ghi chú khác biệt (TV)')
    
    difficulty = models.PositiveSmallIntegerField(default=1, verbose_name='Độ khó (1-5)')
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'minimal_pairs'
        ordering = ['phoneme_1', 'order']
        verbose_name = 'Cặp tối thiểu'
        verbose_name_plural = 'Cặp tối thiểu'
    
    def __str__(self):
        return f"{self.word_1} vs {self.word_2}"


class PronunciationLesson(models.Model):
    """
    Structured pronunciation lesson combining phonemes.
    Follows the lesson structure from the curriculum document.
    """
    LESSON_TYPES = [
        ('single', 'Âm đơn lẻ'),
        ('pair_contrast', 'Cặp đối lập'),
        ('group', 'Nhóm âm'),
        ('review', 'Ôn tập'),
        ('test', 'Kiểm tra'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Nháp'),
        ('published', 'Đã xuất bản'),
        ('archived', 'Lưu trữ'),
    ]
    
    # Basic info
    title = models.CharField(max_length=200, verbose_name='Tiêu đề')
    title_vi = models.CharField(max_length=200, verbose_name='Tiêu đề tiếng Việt')
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    
    description = models.TextField(blank=True, verbose_name='Mô tả')
    description_vi = models.TextField(blank=True, verbose_name='Mô tả tiếng Việt')
    
    # Curriculum Stage
    stage = models.ForeignKey(
        CurriculumStage,
        on_delete=models.PROTECT,
        related_name='lessons',
        verbose_name='Giai đoạn',
        null=True,
        blank=True,
        help_text='Giai đoạn học (1-4)'
    )
    
    # Lesson type
    lesson_type = models.CharField(
        max_length=20,
        choices=LESSON_TYPES,
        default='pair_contrast',
        db_index=True
    )
    
    # Phonemes covered in this lesson
    phonemes = models.ManyToManyField(
        Phoneme,
        related_name='pronunciation_lessons',
        verbose_name='Âm vị trong bài'
    )
    
    # Lesson content - JSON structure for screens/steps
    # [{
    #     "screen": 1,
    #     "type": "intro|theory|practice|drill|challenge|summary",
    #     "title": "...",
    #     "content": {...}
    # }]
    lesson_content = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Nội dung bài học'
    )
    
    # Learning objectives
    objectives = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Mục tiêu học tập'
    )
    
    # Estimated time
    estimated_minutes = models.PositiveIntegerField(default=10, verbose_name='Thời gian (phút)')
    
    # XP reward
    xp_reward = models.PositiveIntegerField(default=15, verbose_name='XP thưởng')
    
    # Difficulty (1-10)
    difficulty = models.PositiveSmallIntegerField(default=1, verbose_name='Độ khó')
    
    # Prerequisites - other pronunciation lessons to complete first
    prerequisites = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='unlocks',
        verbose_name='Điều kiện tiên quyết'
    )
    
    # Part/Module number (e.g., Part 1: Vowels, Part 2: Consonants)
    part_number = models.PositiveSmallIntegerField(default=1, verbose_name='Phần')
    unit_number = models.PositiveSmallIntegerField(default=1, verbose_name='Bài số')
    
    # Status
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft',
        db_index=True
    )
    
    order = models.PositiveIntegerField(default=0, db_index=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'pronunciation_lessons'
        ordering = ['stage__order', 'part_number', 'unit_number', 'order']
        verbose_name = 'Bài học phát âm'
        verbose_name_plural = 'Bài học phát âm'
    
    def __str__(self):
        stage_info = f"Stage {self.stage.number} - " if self.stage else ""
        return f"{stage_info}Part {self.part_number} - Lesson {self.unit_number}: {self.title_vi}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = f"part-{self.part_number}-lesson-{self.unit_number}-{self.title}"
            self.slug = slugify(base_slug)
        super().save(*args, **kwargs)
    
    def can_access(self, user):
        """
        Check if user can access this lesson based on prerequisites.
        Returns (can_access: bool, reason: str)
        """
        if not user or not user.is_authenticated:
            # Public lessons or allow guest preview
            return (True, 'guest')
        
        # Check stage prerequisites
        if self.stage and self.stage.required_previous_stages.exists():
            from apps.users.models import UserPronunciationLessonProgress
            
            for prev_stage in self.stage.required_previous_stages.all():
                # Check if all lessons in previous stage are completed
                prev_lessons = prev_stage.lessons.filter(status='published')
                for prev_lesson in prev_lessons:
                    if not UserPronunciationLessonProgress.objects.filter(
                        user=user,
                        pronunciation_lesson=prev_lesson,
                        status='completed'
                    ).exists():
                        return (False, f'Hoàn thành Giai đoạn {prev_stage.number} trước')
        
        # Check lesson prerequisites
        if self.prerequisites.exists():
            from apps.users.models import UserPronunciationLessonProgress
            
            for prereq_lesson in self.prerequisites.all():
                if not UserPronunciationLessonProgress.objects.filter(
                    user=user,
                    pronunciation_lesson=prereq_lesson,
                    status='completed'
                ).exists():
                    return (False, f'Hoàn thành bài "{prereq_lesson.title_vi}" trước')
        
        return (True, 'unlocked')
    
    def get_user_progress(self, user):
        """
        Get progress percentage for this lesson for a user.
        Returns int 0-100
        """
        if not user or not user.is_authenticated:
            return 0
        
        from apps.users.models import UserPronunciationLessonProgress
        try:
            progress = UserPronunciationLessonProgress.objects.get(
                user=user,
                pronunciation_lesson=self
            )
            # Calculate percentage based on completed screens (5 screens total)
            if progress.status == 'completed':
                return 100
            elif len(progress.completed_screens) > 0:
                return int((len(progress.completed_screens) / 5) * 100)
            else:
                return 0
        except UserPronunciationLessonProgress.DoesNotExist:
            return 0


class TongueTwister(models.Model):
    """
    Tongue twisters for pronunciation practice.
    """
    DIFFICULTY_CHOICES = [
        ('easy', 'Dễ'),
        ('medium', 'Trung bình'),
        ('hard', 'Khó'),
    ]
    
    phoneme = models.ForeignKey(
        Phoneme,
        on_delete=models.CASCADE,
        related_name='tongue_twisters',
        null=True,
        blank=True,
        verbose_name='Âm vị chính'
    )
    
    pronunciation_lesson = models.ForeignKey(
        PronunciationLesson,
        on_delete=models.SET_NULL,
        related_name='tongue_twisters',
        null=True,
        blank=True,
        verbose_name='Bài học'
    )
    
    text = models.TextField(verbose_name='Nội dung')
    ipa_transcription = models.TextField(blank=True, verbose_name='Phiên âm IPA')
    meaning_vi = models.TextField(blank=True, verbose_name='Nghĩa tiếng Việt')
    
    audio_normal = models.FileField(upload_to='tongue_twisters/audio/', blank=True, null=True)
    audio_slow = models.FileField(upload_to='tongue_twisters/audio_slow/', blank=True, null=True)
    
    difficulty = models.PositiveSmallIntegerField(default=1, verbose_name='Độ khó (1-5)')
    difficulty_level = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default='easy',
        verbose_name='Mức độ khó'
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, verbose_name='Kích hoạt')
    
    class Meta:
        db_table = 'tongue_twisters'
        ordering = ['difficulty', 'order']
        verbose_name = 'Câu xoắn lưỡi'
        verbose_name_plural = 'Câu xoắn lưỡi'
    
    def __str__(self):
        return self.text[:50] + '...' if len(self.text) > 50 else self.text


#============================================================================
# PHASE 1: AUDIO SYSTEM MODELS
#============================================================================

from datetime import timedelta


class AudioSource(models.Model):
    """
    AudioSource: Centralized audio file management for phonemes.
    
    Supports multiple audio sources with intelligent fallback:
    1. Native speaker recordings (100% quality) - BEST
    2. Cached TTS audio (90% quality, instant) - GOOD  
    3. On-demand TTS (80% quality, async) - FALLBACK
    
    Example usage:
        # Create native audio
        audio = AudioSource.objects.create(
            phoneme=phoneme,
            source_type='native',
            audio_file='path/to/file.mp3'
        )
        
        # Check if cached
        if audio.is_cached():
            print(f"Quality: {audio.get_quality_score()}%")
    """
    
    SOURCE_TYPE_CHOICES = [
        ('native', 'Native Speaker Recording'),
        ('tts', 'TTS Generated (Cached)'),
        ('generated', 'TTS Generated (On-Demand)'),
    ]
    
    phoneme = models.ForeignKey(
        Phoneme,
        on_delete=models.CASCADE,
        related_name='audio_sources',
        verbose_name='Âm vị'
    )
    
    source_type = models.CharField(
        max_length=20,
        choices=SOURCE_TYPE_CHOICES,
        db_index=True,
        verbose_name='Loại nguồn âm thanh'
    )
    
    voice_id = models.CharField(
        max_length=50,
        default='en-US-AriaNeural',
        blank=True,
        db_index=True,
        verbose_name='ID giọng nói TTS'
    )
    
    language = models.CharField(
        max_length=10,
        default='en-US',
        verbose_name='Ngôn ngữ'
    )
    
    audio_file = models.FileField(
        upload_to='phonemes/audio/%Y/%m/%d/',
        verbose_name='File âm thanh'
    )
    
    audio_duration = models.FloatField(
        default=0,
        verbose_name='Thời lượng (giây)'
    )
    
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Metadata bổ sung'
    )
    
    cached_until = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True,
        verbose_name='Lưu cache đến'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'curriculum_audiosource'
        ordering = ['-created_at']
        verbose_name = 'Audio Source'
        verbose_name_plural = 'Audio Sources'
        indexes = [
            models.Index(fields=['phoneme', 'source_type']),
            models.Index(fields=['voice_id', 'created_at']),
        ]
    
    def __str__(self):
        return f"/{self.phoneme.ipa_symbol}/ - {self.get_source_type_display()}"
    
    def is_native(self):
        """Check if this is a native speaker recording."""
        return self.source_type == 'native'
    
    def is_cached(self):
        """Check if this audio is cached and still valid."""
        if self.source_type == 'native':
            return True  # Native never expires
        if not self.cached_until:
            return False
        return timezone.now() < self.cached_until
    
    def needs_regeneration(self):
        """Check if TTS audio needs regeneration."""
        if self.source_type == 'native':
            return False
        if not self.cached_until:
            return True
        return timezone.now() >= self.cached_until
    
    def get_quality_score(self):
        """Get quality score (100, 90, or 80)."""
        if self.source_type == 'native':
            return 100
        elif self.source_type == 'tts':
            return 90
        else:
            return 80
    
    def get_url(self):
        """Get audio file URL."""
        if self.audio_file:
            return self.audio_file.url
        return None


class AudioCache(models.Model):
    """
    AudioCache: Track usage and performance metrics for audio files.
    
    One-to-one relationship with AudioSource.
    Tracks usage count, file size, and access patterns.
    """
    
    audio_source = models.OneToOneField(
        AudioSource,
        on_delete=models.CASCADE,
        related_name='cache',
        verbose_name='Audio Source'
    )
    
    file_size = models.BigIntegerField(
        default=0,
        verbose_name='Kích thước file (bytes)'
    )
    
    generated_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Ngày tạo cache'
    )
    
    last_accessed_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Lần truy cập cuối'
    )
    
    usage_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Số lần phát'
    )
    
    class Meta:
        db_table = 'curriculum_audiocache'
        verbose_name = 'Audio Cache'
        verbose_name_plural = 'Audio Caches'
        indexes = [
            models.Index(fields=['usage_count', '-last_accessed_at']),
        ]
    
    def __str__(self):
        return f"Cache for {self.audio_source}"
    
    def increment_usage(self):
        """Increment usage counter."""
        self.usage_count += 1
        self.save(update_fields=['usage_count', 'last_accessed_at'])
    
    def get_age_days(self):
        """Get cache age in days."""
        if not self.generated_at:
            return 0
        delta = timezone.now() - self.generated_at
        return delta.days
    
    def is_stale(self, max_days=30):
        """Check if cache is stale (older than max_days)."""
        return self.get_age_days() > max_days


class AudioVersion(models.Model):
    """
    Tracks all versions of audio for a phoneme over time.
    
    Supports intelligent version management with activation/deactivation,
    allowing admins to switch between different audio versions easily.
    
    Example usage:
        # Create new version
        version = AudioVersion.objects.create(
            phoneme=phoneme,
            audio_source=audio_source,
            change_reason="Better quality recording"
        )
        
        # Activate it (auto-deactivates others)
        version.activate(user=request.user)
        
        # View history
        versions = AudioVersion.objects.filter(phoneme=phoneme)
    """
    
    # Core fields
    phoneme = models.ForeignKey(
        Phoneme,
        on_delete=models.CASCADE,
        related_name='audio_versions',
        verbose_name='Âm vị'
    )
    
    audio_source = models.ForeignKey(
        AudioSource,
        on_delete=models.PROTECT,
        related_name='versions',
        verbose_name='Audio Source'
    )
    
    # Version tracking
    version_number = models.PositiveIntegerField(
        verbose_name='Số phiên bản',
        help_text='Auto-increment cho mỗi phoneme'
    )
    
    # Activation status
    is_active = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name='Đang sử dụng',
        help_text='Chỉ có 1 version active cho mỗi phoneme'
    )
    
    # Time tracking
    effective_from = models.DateTimeField(
        default=timezone.now,
        verbose_name='Có hiệu lực từ',
        help_text='Thời điểm version này được activate'
    )
    
    effective_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Hết hiệu lực',
        help_text='Thời điểm version này bị deactivate (None = vẫn active)'
    )
    
    # Metadata
    uploaded_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_audio_versions',
        verbose_name='Người upload'
    )
    
    upload_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Ngày upload'
    )
    
    change_reason = models.TextField(
        blank=True,
        verbose_name='Lý do thay đổi',
        help_text='Ví dụ: "Giọng rõ hơn", "Fix background noise"'
    )
    
    # Analytics for A/B testing
    usage_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Số lần phát',
        help_text='Đếm số lần audio được phát'
    )
    
    avg_user_rating = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Đánh giá TB',
        help_text='Rating trung bình từ users (1-5 sao)'
    )
    
    user_rating_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Số lượt đánh giá'
    )
    
    class Meta:
        db_table = 'curriculum_audio_version'
        ordering = ['phoneme', '-version_number']
        verbose_name = 'Audio Version'
        verbose_name_plural = 'Audio Versions'
        unique_together = [['phoneme', 'version_number']]
        indexes = [
            models.Index(fields=['phoneme', 'is_active']),
            models.Index(fields=['effective_from']),
            models.Index(fields=['-version_number']),
        ]
    
    def __str__(self):
        status = "✓ ACTIVE" if self.is_active else "✗ INACTIVE"
        return f"/{self.phoneme.ipa_symbol}/ v{self.version_number} ({status})"
    
    def save(self, *args, **kwargs):
        """Auto-increment version_number for phoneme"""
        if not self.version_number:
            last_version = AudioVersion.objects.filter(
                phoneme=self.phoneme
            ).aggregate(models.Max('version_number'))['version_number__max']
            
            self.version_number = (last_version or 0) + 1
        
        super().save(*args, **kwargs)
    
    def activate(self, user=None, reason=''):
        """
        Activate this version and deactivate all others for this phoneme.
        
        Args:
            user: User who activated (for audit trail)
            reason: Reason for activation
        
        Example:
            version.activate(user=request.user, reason="Better quality")
        """
        from django.db import transaction
        
        with transaction.atomic():
            # Deactivate all other versions
            AudioVersion.objects.filter(
                phoneme=self.phoneme,
                is_active=True
            ).exclude(
                pk=self.pk
            ).update(
                is_active=False,
                effective_until=timezone.now()
            )
            
            # Activate this version
            self.is_active = True
            self.effective_from = timezone.now()
            self.effective_until = None
            
            if reason:
                self.change_reason = reason
            
            self.save(update_fields=[
                'is_active', 
                'effective_from', 
                'effective_until',
                'change_reason'
            ])
            
            # Update phoneme's preferred_audio_source
            self.phoneme.preferred_audio_source = self.audio_source
            self.phoneme.save(update_fields=['preferred_audio_source'])
    
    def get_duration_text(self):
        """Get human-readable duration"""
        if not self.effective_until:
            if self.is_active:
                days = (timezone.now() - self.effective_from).days
                return f"Active for {days} days"
            else:
                return "Never activated"
        else:
            days = (self.effective_until - self.effective_from).days
            return f"Was active for {days} days"
    
    def increment_usage(self):
        """Increment usage counter (called when audio is played)"""
        self.usage_count = models.F('usage_count') + 1
        self.save(update_fields=['usage_count'])
    
    def add_rating(self, rating):
        """
        Add user rating (1-5 stars).
        
        Args:
            rating: Integer 1-5
        """
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        
        total = (self.avg_user_rating or 0) * self.user_rating_count
        total += rating
        self.user_rating_count += 1
        self.avg_user_rating = total / self.user_rating_count
        
        self.save(update_fields=['avg_user_rating', 'user_rating_count'])


#============================================================================
# PHASE 5.4: PHONEME ATTEMPT TRACKING MODEL
#============================================================================


class PhonemeAttempt(models.Model):
    """
    Individual practice attempt record for detailed history tracking.
    
    Stores each attempt with audio, transcript, and phoneme-level analysis.
    Supports progress visualization over time.
    
    Example usage:
        # Create attempt after recording
        attempt = PhonemeAttempt.objects.create(
            user=user,
            phoneme=phoneme,
            accuracy=85,
            audio_recording=audio_blob,
            transcript_text="She sells seashells",
            phoneme_analysis={...}
        )
        
        # Query recent attempts
        recent = PhonemeAttempt.objects.filter(
            user=user
        ).order_by('-attempted_at')[:10]
    """
    
    # Core relationships
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='phoneme_attempts',
        verbose_name='User'
    )
    
    phoneme = models.ForeignKey(
        Phoneme,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name='Phoneme'
    )
    
    # Attempt data
    accuracy = models.FloatField(
        verbose_name='Accuracy (%)',
        help_text='0-100'
    )
    
    attempt_duration = models.FloatField(
        default=0,
        verbose_name='Duration (seconds)'
    )
    
    exercise_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Exercise Type',
        help_text='tongue_twister, minimal_pair, production, etc.'
    )
    
    # Audio recording (optional)
    audio_recording = models.FileField(
        upload_to='user_phoneme_attempts/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name='Audio Recording'
    )
    
    # Transcript and analysis
    transcript_text = models.TextField(
        blank=True,
        verbose_name='Transcript',
        help_text='STT output'
    )
    
    target_text = models.TextField(
        blank=True,
        verbose_name='Target Text',
        help_text='Expected text (for tongue twisters)'
    )
    
    # Phase 5.2 phoneme analysis data
    phoneme_analysis = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Phoneme Analysis',
        help_text='Detailed phoneme-level results from Phase 5.2'
    )
    
    # Problem phonemes detected
    problem_phonemes = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Problem Phonemes',
        help_text='List of problematic phonemes in this attempt'
    )
    
    # Score breakdown
    pronunciation_score = models.FloatField(
        default=0,
        verbose_name='Pronunciation Score'
    )
    
    fluency_score = models.FloatField(
        default=0,
        verbose_name='Fluency Score'
    )
    
    completeness_score = models.FloatField(
        default=0,
        verbose_name='Completeness Score'
    )
    
    # Feedback
    ai_feedback = models.TextField(
        blank=True,
        verbose_name='AI Feedback',
        help_text='Auto-generated feedback'
    )
    
    # Timestamp
    attempted_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Attempted At'
    )
    
    class Meta:
        db_table = 'phoneme_attempts'
        ordering = ['-attempted_at']
        verbose_name = 'Phoneme Attempt'
        verbose_name_plural = 'Phoneme Attempts'
        indexes = [
            models.Index(fields=['user', '-attempted_at']),
            models.Index(fields=['phoneme', '-attempted_at']),
            models.Index(fields=['exercise_type', '-attempted_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - /{self.phoneme.ipa_symbol}/ - {self.accuracy:.1f}% @ {self.attempted_at.strftime('%Y-%m-%d %H:%M')}"
    
    def was_successful(self):
        """Check if attempt was successful (>= 70%)."""
        return self.accuracy >= 70
    
    def get_grade(self):
        """Get letter grade A-F."""
        if self.accuracy >= 90:
            return 'A'
        elif self.accuracy >= 80:
            return 'B'
        elif self.accuracy >= 70:
            return 'C'
        elif self.accuracy >= 60:
            return 'D'
        else:
            return 'F'
    
    def get_duration_text(self):
        """Get human-readable duration."""
        if self.attempt_duration < 60:
            return f"{self.attempt_duration:.1f}s"
        else:
            minutes = int(self.attempt_duration // 60)
            seconds = int(self.attempt_duration % 60)
            return f"{minutes}m {seconds}s"

    
    # Attempt data
    accuracy = models.FloatField(
        verbose_name='Accuracy (%)',
        help_text='0-100'
    )
    
    attempt_duration = models.FloatField(
        default=0,
        verbose_name='Duration (seconds)'
    )
    
    exercise_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Exercise Type',
        help_text='tongue_twister, minimal_pair, production, etc.'
    )
    
    # Audio recording (optional)
    audio_recording = models.FileField(
        upload_to='user_phoneme_attempts/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name='Audio Recording'
    )
    
    # Transcript and analysis
    transcript_text = models.TextField(
        blank=True,
        verbose_name='Transcript',
        help_text='STT output'
    )
    
    target_text = models.TextField(
        blank=True,
        verbose_name='Target Text',
        help_text='Expected text (for tongue twisters)'
    )
    
    # Phase 5.2 phoneme analysis data
    phoneme_analysis = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Phoneme Analysis',
        help_text='Detailed phoneme-level results from Phase 5.2'
    )
    
    # Problem phonemes detected
    problem_phonemes = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Problem Phonemes',
        help_text='List of problematic phonemes in this attempt'
    )
    
    # Score breakdown
    pronunciation_score = models.FloatField(
        default=0,
        verbose_name='Pronunciation Score'
    )
    
    fluency_score = models.FloatField(
        default=0,
        verbose_name='Fluency Score'
    )
    
    completeness_score = models.FloatField(
        default=0,
        verbose_name='Completeness Score'
    )
    
    # Feedback
    ai_feedback = models.TextField(
        blank=True,
        verbose_name='AI Feedback',
        help_text='Auto-generated feedback'
    )
    
    # Timestamp
    attempted_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Attempted At'
    )
    
    class Meta:
        db_table = 'phoneme_attempts'
        ordering = ['-attempted_at']
        verbose_name = 'Phoneme Attempt'
        verbose_name_plural = 'Phoneme Attempts'
        indexes = [
            models.Index(fields=['user', '-attempted_at']),
            models.Index(fields=['phoneme', '-attempted_at']),
            models.Index(fields=['exercise_type', '-attempted_at']),
        ]
    
    def __str__(self):
        return f"{self.progress.user.username} - /{self.progress.phoneme.ipa_symbol}/ - {self.accuracy:.1f}% @ {self.attempted_at.strftime('%Y-%m-%d %H:%M')}"
    
    def was_successful(self):
        """Check if attempt was successful (>= 70%)."""
        return self.accuracy >= 70
    
    def get_grade(self):
        """Get letter grade A-F."""
        if self.accuracy >= 90:
            return 'A'
        elif self.accuracy >= 80:
            return 'B'
        elif self.accuracy >= 70:
            return 'C'
        elif self.accuracy >= 60:
            return 'D'
        else:
            return 'F'
    
    def get_duration_text(self):
        """Get human-readable duration."""
        if self.attempt_duration < 60:
            return f"{self.attempt_duration:.1f}s"
        else:
            minutes = int(self.attempt_duration // 60)
            seconds = int(self.attempt_duration % 60)
            return f"{minutes}m {seconds}s"

