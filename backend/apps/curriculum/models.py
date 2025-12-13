"""Curriculum models - Course, Unit, Lesson, Sentence, Flashcard."""

from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from datetime import timedelta


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
        related_name='preferred_for_phoneme',
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
        ordering = ['part_number', 'unit_number', 'order']
        verbose_name = 'Bài học phát âm'
        verbose_name_plural = 'Bài học phát âm'
    
    def __str__(self):
        return f"Part {self.part_number} - Lesson {self.unit_number}: {self.title_vi}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"part-{self.part_number}-lesson-{self.unit_number}-{self.title}")
        super().save(*args, **kwargs)


class TongueTwister(models.Model):
    """
    Tongue twisters for pronunciation practice.
    """
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
    order = models.PositiveIntegerField(default=0)
    
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
        delta = timezone.now() - self.generated_at
        return delta.days
    
    def is_stale(self, max_days=30):
        """Check if cache is stale (older than max_days)."""
        return self.get_age_days() > max_days