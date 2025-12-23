"""
Vocabulary and Flashcard Models

Features:
- Oxford 3000/5000 word storage
- SM-2 spaced repetition algorithm
- Flashcard deck management
- Study session tracking
"""

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta

User = get_user_model()


class Word(models.Model):
    """
    Oxford word with full metadata for Vietnamese learners.
    
    Data sources:
    - Oxford 3000 (A1-B2)
    - Oxford 5000 (B2-C1)
    """
    
    # Basic information
    text = models.CharField(max_length=100, db_index=True)  # Removed unique=True
    pos = models.CharField(max_length=50, help_text="Part of speech: noun, verb, adj, etc.")
    cefr_level = models.CharField(
        max_length=10, 
        db_index=True,
        help_text="A1, A2, B1, B2, C1, C2"
    )
    
    # Pronunciation
    ipa = models.CharField(max_length=100, blank=True, help_text="General IPA")
    british_ipa = models.CharField(max_length=100, blank=True, help_text="UK pronunciation")
    american_ipa = models.CharField(max_length=100, blank=True, help_text="US pronunciation")
    
    # Meanings
    meaning_vi = models.CharField(max_length=500, help_text="Vietnamese translation")
    meaning_en = models.TextField(blank=True, help_text="English definition")
    
    # Examples
    example_en = models.TextField(blank=True, help_text="English example sentence")
    example_vi = models.TextField(blank=True, help_text="Vietnamese translation of example")
    
    # Learning aids (for Vietnamese learners)
    collocations = models.CharField(
        max_length=500, 
        blank=True,
        help_text="Common word combinations: make a decision, take a photo"
    )
    mnemonic = models.TextField(
        blank=True,
        help_text="Memory aid or visual association for Vietnamese learners"
    )
    etymology = models.TextField(blank=True, help_text="Word origin and history")
    
    # Related words
    synonyms = models.CharField(max_length=500, blank=True, help_text="Similar words")
    antonyms = models.CharField(max_length=500, blank=True, help_text="Opposite words")
    
    # Frequency and register
    frequency_rank = models.IntegerField(
        null=True, 
        blank=True,
        help_text="1 = most common, higher = less common"
    )
    register = models.CharField(
        max_length=50, 
        blank=True,
        help_text="formal, informal, slang, academic"
    )
    
    # Audio files
    audio_uk = models.FileField(upload_to='audio/words/uk/', blank=True)
    audio_us = models.FileField(upload_to='audio/words/us/', blank=True)
    
    # Visual aid
    image = models.ImageField(upload_to='images/words/', blank=True)
    
    # Relationships
    phonemes = models.ManyToManyField(
        'curriculum.Phoneme',
        blank=True,
        related_name='words',
        help_text="Phonemes contained in this word"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['frequency_rank', 'text']
        indexes = [
            models.Index(fields=['cefr_level', 'text']),
            models.Index(fields=['frequency_rank']),
            models.Index(fields=['pos']),
        ]
        unique_together = [['text', 'pos', 'cefr_level']]  # Unique combination
        verbose_name = "Word"
        verbose_name_plural = "Words"
    
    def __str__(self):
        return f"{self.text} ({self.cefr_level}) - {self.meaning_vi[:30]}"
    
    @property
    def primary_phoneme(self):
        """Get the first phoneme in word (usually the stressed syllable)"""
        return self.phonemes.first()
    
    @property
    def difficulty_score(self):
        """Calculate difficulty: 1=A1 (easiest) to 6=C2 (hardest)"""
        levels = {'A1': 1, 'A2': 2, 'B1': 3, 'B2': 4, 'C1': 5, 'C2': 6}
        return levels.get(self.cefr_level, 3)


class FlashcardDeck(models.Model):
    """
    Collection of flashcards for organized learning.
    
    Categories:
    - oxford: Oxford 3000/5000 words
    - pronunciation: Pronunciation practice
    - grammar: Grammar rules
    - idioms: Idiomatic expressions
    - custom: User-created decks
    """
    
    CATEGORIES = [
        ('oxford', 'Oxford Words'),
        ('pronunciation', 'Pronunciation'),
        ('grammar', 'Grammar'),
        ('idioms', 'Idioms & Phrases'),
        ('custom', 'Custom'),
    ]
    
    LEVELS = [
        ('A1', 'Beginner'),
        ('A2', 'Elementary'),
        ('B1', 'Intermediate'),
        ('B2', 'Upper-Intermediate'),
        ('C1', 'Advanced'),
        ('mixed', 'Mixed Levels'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=CATEGORIES, default='oxford')
    level = models.CharField(max_length=10, choices=LEVELS, blank=True)
    
    # Visibility
    is_public = models.BooleanField(default=True, help_text="Public decks are visible to all users")
    is_official = models.BooleanField(default=False, help_text="Official decks created by admin")
    
    # Appearance
    icon = models.CharField(max_length=100, default='📚', help_text="Emoji icon")
    color = models.CharField(max_length=7, default='#F47C26', help_text="Hex color code")
    
    # Ownership
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_decks')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_official', 'level', 'name']
        verbose_name = "Flashcard Deck"
        verbose_name_plural = "Flashcard Decks"
    
    def __str__(self):
        return f"{self.icon} {self.name} ({self.level})"
    
    @property
    def card_count(self):
        """Total number of flashcards in this deck"""
        return self.flashcards.count()
    
    @property
    def average_difficulty(self):
        """Average difficulty of cards in deck"""
        avg = self.flashcards.aggregate(models.Avg('difficulty'))['difficulty__avg']
        return round(avg, 1) if avg else 3.0


class Flashcard(models.Model):
    """
    Individual flashcard with front (question) and back (answer).
    
    Types:
    - word: English word → Vietnamese meaning
    - pronunciation: Phoneme → Examples
    - grammar: Rule → Usage
    - idiom: Expression → Meaning
    """
    
    FRONT_TYPES = [
        ('word', 'Word'),
        ('sentence', 'Sentence'),
        ('pronunciation', 'Pronunciation'),
        ('grammar', 'Grammar Rule'),
        ('image', 'Image'),
    ]
    
    # Relationships
    word = models.ForeignKey(
        Word, 
        on_delete=models.CASCADE, 
        related_name='flashcards',
        null=True,
        blank=True,
        help_text="Link to Word model if this is a vocabulary flashcard"
    )
    deck = models.ForeignKey(
        FlashcardDeck, 
        on_delete=models.CASCADE, 
        related_name='flashcards'
    )
    
    # Front side (Question)
    front_text = models.CharField(
        max_length=500,
        help_text="What user sees first (usually English word or question)"
    )
    front_type = models.CharField(max_length=50, choices=FRONT_TYPES, default='word')
    
    # Back side (Answer)
    back_text = models.TextField(help_text="Answer or translation")
    back_example = models.TextField(blank=True, help_text="Example usage")
    back_note = models.TextField(blank=True, help_text="Grammar notes or tips")
    
    # Hints
    hint = models.CharField(
        max_length=500, 
        blank=True,
        help_text="Hint to show before flipping card"
    )
    
    # Difficulty (1-5)
    difficulty = models.IntegerField(
        default=3,
        help_text="1=very easy, 5=very hard"
    )
    
    # Tags for filtering
    tags = models.CharField(
        max_length=500, 
        blank=True,
        help_text="Comma-separated tags: verbs, past-tense, irregular"
    )
    
    # Media
    audio_url = models.URLField(blank=True, help_text="URL to pronunciation audio")
    image_url = models.URLField(blank=True, help_text="URL to visual aid")
    
    # Order in deck
    order = models.IntegerField(default=0, help_text="Display order in deck")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'id']
        unique_together = [['word', 'deck']]  # Prevent duplicate word in same deck
        verbose_name = "Flashcard"
        verbose_name_plural = "Flashcards"
    
    def __str__(self):
        return f"{self.front_text} → {self.back_text[:50]}"


class UserFlashcardProgress(models.Model):
    """
    Implements SM-2 spaced repetition algorithm.
    
    SM-2 Algorithm:
    - E-Factor: Easiness factor (1.3 to 2.5)
    - Interval: Days until next review
    - Quality: User's recall rating (0-5)
    
    Quality ratings:
    0: Complete blackout
    1: Incorrect, but upon seeing answer it felt familiar
    2: Incorrect, but upon seeing answer it seemed easy
    3: Correct, but required significant effort
    4: Correct, after some hesitation
    5: Perfect recall
    """
    
    # Relationships
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vocabulary_progress')
    flashcard = models.ForeignKey(Flashcard, on_delete=models.CASCADE, related_name='vocabulary_user_progress')
    
    # SM-2 Algorithm fields
    easiness_factor = models.FloatField(
        default=2.5,
        help_text="E-Factor ranges from 1.3 to 2.5"
    )
    interval = models.IntegerField(
        default=1,
        help_text="Days until next review"
    )
    repetitions = models.IntegerField(
        default=0,
        help_text="Number of consecutive correct repetitions"
    )
    
    # Review scheduling
    next_review_date = models.DateTimeField()
    last_reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Quality of last recall (0-5)
    last_quality = models.IntegerField(
        null=True, 
        blank=True,
        help_text="0=blackout, 3=correct with effort, 5=perfect"
    )
    
    # Statistics
    total_reviews = models.IntegerField(default=0)
    total_correct = models.IntegerField(default=0)
    total_incorrect = models.IntegerField(default=0)
    streak = models.IntegerField(default=0, help_text="Current correct streak")
    best_streak = models.IntegerField(default=0, help_text="Best streak ever")
    
    # Status
    is_mastered = models.BooleanField(default=False, help_text="Card is mastered (interval > 30 days)")
    is_learning = models.BooleanField(default=True, help_text="Card is being learned")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['user', 'flashcard']]
        indexes = [
            models.Index(fields=['user', 'next_review_date']),
            models.Index(fields=['user', 'is_learning']),
        ]
        verbose_name = "User Flashcard Progress"
        verbose_name_plural = "User Flashcard Progress"
    
    def __str__(self):
        return f"{self.user.username} - {self.flashcard.front_text} (next: {self.next_review_date.date()})"
    
    def calculate_next_review(self, quality):
        """
        SM-2 Algorithm implementation.
        
        Args:
            quality (int): User's recall rating (0-5)
        
        Algorithm:
        1. Calculate new E-Factor
        2. Update repetitions
        3. Calculate new interval
        4. Schedule next review
        """
        
        # 1. Update E-Factor
        # Formula: EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        ef = self.easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        ef = max(1.3, ef)  # Minimum E-Factor is 1.3
        self.easiness_factor = ef
        
        # 2. Update repetitions and interval
        if quality < 3:
            # Incorrect response: reset repetitions
            self.repetitions = 0
            self.interval = 1
            self.is_learning = True
        else:
            # Correct response: increase interval
            self.repetitions += 1
            
            if self.repetitions == 1:
                self.interval = 1
            elif self.repetitions == 2:
                self.interval = 6
            else:
                self.interval = int(self.interval * ef)
            
            # Check if mastered (interval > 30 days)
            if self.interval >= 30:
                self.is_mastered = True
                self.is_learning = False
        
        # 3. Schedule next review
        self.next_review_date = timezone.now() + timedelta(days=self.interval)
        self.last_reviewed_at = timezone.now()
        self.last_quality = quality
        
        # 4. Update statistics
        self.total_reviews += 1
        
        if quality >= 3:
            self.total_correct += 1
            self.streak += 1
            if self.streak > self.best_streak:
                self.best_streak = self.streak
        else:
            self.total_incorrect += 1
            self.streak = 0
        
        self.save()
    
    @property
    def accuracy(self):
        """Calculate accuracy percentage"""
        if self.total_reviews == 0:
            return 0
        return round((self.total_correct / self.total_reviews) * 100, 1)
    
    @property
    def is_due(self):
        """Check if card is due for review"""
        return self.next_review_date <= timezone.now()


class StudySession(models.Model):
    """
    Track user study sessions for analytics.
    """
    
    # Relationships
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_sessions')
    deck = models.ForeignKey(FlashcardDeck, on_delete=models.CASCADE, related_name='study_sessions')
    
    # Session timing
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    # Cards studied
    cards_studied = models.IntegerField(default=0)
    cards_correct = models.IntegerField(default=0)
    cards_incorrect = models.IntegerField(default=0)
    cards_skipped = models.IntegerField(default=0)
    
    # Performance metrics
    accuracy = models.FloatField(default=0, help_text="Percentage of correct cards")
    time_spent_seconds = models.IntegerField(default=0)
    average_time_per_card = models.FloatField(default=0, help_text="Seconds per card")
    
    # Session notes
    notes = models.TextField(blank=True, help_text="User notes about this session")
    
    class Meta:
        ordering = ['-started_at']
        verbose_name = "Study Session"
        verbose_name_plural = "Study Sessions"
    
    def __str__(self):
        return f"{self.user.username} - {self.deck.name} ({self.started_at.date()})"
    
    def end_session(self):
        """End the study session and calculate metrics"""
        self.ended_at = timezone.now()
        
        # Calculate time spent
        duration = (self.ended_at - self.started_at).total_seconds()
        self.time_spent_seconds = int(duration)
        
        # Calculate accuracy
        if self.cards_studied > 0:
            self.accuracy = round((self.cards_correct / self.cards_studied) * 100, 1)
            self.average_time_per_card = round(duration / self.cards_studied, 1)
        
        self.save()
    
    @property
    def duration_minutes(self):
        """Session duration in minutes"""
        if not self.ended_at:
            return 0
        return int(self.time_spent_seconds / 60)
