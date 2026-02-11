/* ====================================
   FLASHCARD ENGINE - SM-2 Spaced Repetition
   Phase 2: Core Features
   Version: 1.0.0
   ==================================== */

/**
 * FlashcardEngine - Complete flashcard learning system with SM-2 algorithm
 * 
 * SM-2 Algorithm:
 * - EF (Easiness Factor): 1.3 - 2.5, default 2.5
 * - Quality: 0-5 (0-2: fail, 3: hard, 4: good, 5: easy)
 * - Interval calculation based on repetition count and EF
 */
const FlashcardEngine = {
    // ====================================
    // CONFIGURATION
    // ====================================
    config: {
        minEF: 1.3,           // Minimum easiness factor
        maxEF: 2.5,           // Maximum easiness factor
        defaultEF: 2.5,       // Starting easiness factor
        graduatingInterval: 1, // Days after first successful review
        easyBonus: 1.3,       // Multiplier for "easy" responses
        hardMultiplier: 0.8,  // Multiplier for "hard" responses
        newCardsPerDay: 20,   // Max new cards per day
        reviewsPerDay: 100,   // Max reviews per day
        lapseInterval: 1,     // Days after forgetting
        audioEnabled: true,   // Auto-play pronunciation
        debug: true
    },

    // State
    state: {
        currentDeck: null,
        currentCard: null,
        cardIndex: 0,
        sessionCards: [],
        sessionStats: {
            reviewed: 0,
            correct: 0,
            incorrect: 0,
            newLearned: 0,
            totalTime: 0,
            startTime: null
        },
        isReviewMode: false
    },

    // ====================================
    // INITIALIZATION
    // ====================================
    
    /**
     * Initialize the flashcard engine
     */
    async init(options = {}) {
        this.config = { ...this.config, ...options };
        this.log('Flashcard Engine initialized');
        
        // Ensure database is ready
        if (typeof englishDB !== 'undefined') {
            await englishDB.ready();
        }
        
        return this;
    },

    // ====================================
    // DECK MANAGEMENT
    // ====================================
    
    /**
     * Create a new deck
     */
    async createDeck(name, description = '', options = {}) {
        const deck = {
            id: Date.now(),
            name,
            description,
            cardCount: 0,
            newCount: 0,
            dueCount: 0,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            settings: {
                newCardsPerDay: options.newCardsPerDay || this.config.newCardsPerDay,
                reviewsPerDay: options.reviewsPerDay || this.config.reviewsPerDay
            }
        };

        if (typeof englishDB !== 'undefined') {
            await englishDB.add('flashcardDecks', deck);
        }

        this.log('Deck created:', deck.name);
        return deck;
    },

    /**
     * Get all decks with stats
     */
    async getDecks() {
        if (typeof englishDB === 'undefined') return [];

        const decks = await englishDB.getAll('flashcardDecks');
        
        // Update stats for each deck
        for (const deck of decks) {
            const stats = await this.getDeckStats(deck.id);
            deck.newCount = stats.newCount;
            deck.dueCount = stats.dueCount;
            deck.cardCount = stats.totalCount;
        }

        return decks;
    },

    /**
     * Get deck statistics
     */
    async getDeckStats(deckId) {
        if (typeof englishDB === 'undefined') {
            return { totalCount: 0, newCount: 0, dueCount: 0, masteredCount: 0 };
        }

        const cards = await englishDB.getByIndex('flashcards', 'deckId', deckId);
        const now = new Date();

        let newCount = 0;
        let dueCount = 0;
        let masteredCount = 0;

        for (const card of cards) {
            const progress = await englishDB.get('flashcardProgress', card.id);
            
            if (!progress) {
                newCount++;
            } else if (progress.interval >= 21) {
                masteredCount++;
                // Still check if due
                if (new Date(progress.nextReviewDate) <= now) {
                    dueCount++;
                }
            } else if (new Date(progress.nextReviewDate) <= now) {
                dueCount++;
            }
        }

        return {
            totalCount: cards.length,
            newCount,
            dueCount,
            masteredCount
        };
    },

    // ====================================
    // CARD MANAGEMENT
    // ====================================
    
    /**
     * Add a new flashcard
     */
    async addCard(deckId, front, back, options = {}) {
        const card = {
            id: Date.now() + Math.random(),
            deckId,
            front,
            back,
            pronunciation: options.pronunciation || null,
            audioUrl: options.audioUrl || null,
            example: options.example || null,
            image: options.image || null,
            tags: options.tags || [],
            notes: options.notes || '',
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
        };

        if (typeof englishDB !== 'undefined') {
            await englishDB.add('flashcards', card);
        }

        this.log('Card added:', card.front);
        return card;
    },

    /**
     * Add multiple cards at once
     */
    async addCards(deckId, cards) {
        const results = [];
        for (const cardData of cards) {
            const card = await this.addCard(
                deckId,
                cardData.front,
                cardData.back,
                cardData
            );
            results.push(card);
        }
        return results;
    },

    /**
     * Get cards for study session
     */
    async getStudyCards(deckId, options = {}) {
        const { includeNew = true, limit = 50 } = options;
        
        if (typeof englishDB === 'undefined') return [];

        const allCards = await englishDB.getByIndex('flashcards', 'deckId', deckId);
        const now = new Date();
        
        const newCards = [];
        const dueCards = [];
        const learningCards = [];

        for (const card of allCards) {
            const progress = await englishDB.get('flashcardProgress', card.id);
            
            if (!progress) {
                // New card
                if (includeNew) {
                    newCards.push({ ...card, isNew: true, progress: null });
                }
            } else {
                const nextReview = new Date(progress.nextReviewDate);
                
                if (nextReview <= now) {
                    if (progress.repetitions === 0) {
                        // Learning card (failed before graduating)
                        learningCards.push({ ...card, isNew: false, progress });
                    } else {
                        // Review card
                        dueCards.push({ ...card, isNew: false, progress });
                    }
                }
            }
        }

        // Prioritize: Learning > Due > New
        // Shuffle each group
        this.shuffleArray(learningCards);
        this.shuffleArray(dueCards);
        this.shuffleArray(newCards);

        // Apply daily limits
        const todayStats = await this.getTodayStats(deckId);
        const remainingNew = Math.max(0, this.config.newCardsPerDay - todayStats.newLearned);
        const remainingReviews = Math.max(0, this.config.reviewsPerDay - todayStats.reviewed);

        const limitedNewCards = newCards.slice(0, remainingNew);
        const limitedDueCards = [...learningCards, ...dueCards].slice(0, remainingReviews);

        const studyCards = [...limitedDueCards, ...limitedNewCards].slice(0, limit);
        
        this.log(`Study cards: ${studyCards.length} (${limitedNewCards.length} new, ${limitedDueCards.length} due)`);
        
        return studyCards;
    },

    /**
     * Get today's study statistics
     */
    async getTodayStats(deckId) {
        if (typeof englishDB === 'undefined') {
            return { reviewed: 0, newLearned: 0, correct: 0 };
        }

        const today = new Date().toISOString().split('T')[0];
        const reviews = await englishDB.getAll('flashcardReviews');
        
        const todayReviews = reviews.filter(r => 
            r.deckId === deckId && 
            r.reviewedAt.startsWith(today)
        );

        return {
            reviewed: todayReviews.length,
            newLearned: todayReviews.filter(r => r.wasNew).length,
            correct: todayReviews.filter(r => r.quality >= 3).length
        };
    },

    // ====================================
    // SM-2 ALGORITHM
    // ====================================
    
    /**
     * Calculate next review using SM-2 algorithm
     * @param {Object} currentProgress - Current card progress
     * @param {number} quality - Response quality (0-5)
     * @returns {Object} Updated progress
     */
    calculateSM2(currentProgress, quality) {
        // Default values for new cards
        let repetitions = currentProgress?.repetitions || 0;
        let easinessFactor = currentProgress?.easinessFactor || this.config.defaultEF;
        let interval = currentProgress?.interval || 0;

        // Quality check
        if (quality < 0 || quality > 5) {
            throw new Error('Quality must be between 0 and 5');
        }

        // Calculate new easiness factor
        // EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        const efDelta = 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02);
        easinessFactor = Math.max(this.config.minEF, easinessFactor + efDelta);
        easinessFactor = Math.min(this.config.maxEF, easinessFactor);

        // Calculate interval
        if (quality < 3) {
            // Failed - reset
            repetitions = 0;
            interval = this.config.lapseInterval;
        } else {
            // Success
            if (repetitions === 0) {
                interval = 1; // First successful review
            } else if (repetitions === 1) {
                interval = 6; // Second successful review
            } else {
                // Subsequent reviews
                interval = Math.round(interval * easinessFactor);
            }
            
            // Apply modifiers
            if (quality === 3) {
                // Hard - reduce interval
                interval = Math.round(interval * this.config.hardMultiplier);
            } else if (quality === 5) {
                // Easy - increase interval
                interval = Math.round(interval * this.config.easyBonus);
            }
            
            repetitions++;
        }

        // Calculate next review date
        const nextReviewDate = new Date();
        nextReviewDate.setDate(nextReviewDate.getDate() + interval);

        return {
            repetitions,
            easinessFactor: Math.round(easinessFactor * 100) / 100,
            interval,
            nextReviewDate: nextReviewDate.toISOString(),
            lastReviewDate: new Date().toISOString(),
            lastQuality: quality
        };
    },

    /**
     * Process card review
     * @param {Object} card - The card being reviewed
     * @param {number} quality - Response quality (0-5)
     */
    async reviewCard(card, quality) {
        const wasNew = card.isNew || !card.progress;
        const currentProgress = card.progress || {};
        
        // Calculate new progress
        const newProgress = this.calculateSM2(currentProgress, quality);
        newProgress.cardId = card.id;

        // Save progress
        if (typeof englishDB !== 'undefined') {
            await englishDB.put('flashcardProgress', newProgress);
            
            // Log review for statistics
            await englishDB.add('flashcardReviews', {
                id: Date.now(),
                cardId: card.id,
                deckId: card.deckId,
                quality,
                wasNew,
                interval: newProgress.interval,
                easinessFactor: newProgress.easinessFactor,
                reviewedAt: new Date().toISOString()
            });

            // Add to sync queue for offline
            await englishDB.addToSyncQueue('flashcard-review', {
                cardId: card.id,
                quality,
                reviewedAt: new Date().toISOString()
            });
        }

        // Update session stats
        this.state.sessionStats.reviewed++;
        if (quality >= 3) {
            this.state.sessionStats.correct++;
        } else {
            this.state.sessionStats.incorrect++;
        }
        if (wasNew) {
            this.state.sessionStats.newLearned++;
        }

        this.log(`Reviewed card ${card.id}: quality=${quality}, interval=${newProgress.interval} days`);
        
        return newProgress;
    },

    /**
     * Map button press to quality score
     */
    getQualityFromButton(button) {
        const mapping = {
            'again': 1,      // Complete fail
            'hard': 3,       // Difficult recall
            'good': 4,       // Successful recall
            'easy': 5        // Perfect recall
        };
        return mapping[button] || 4;
    },

    /**
     * Get interval text for next review
     */
    getIntervalText(quality, currentProgress) {
        const preview = this.calculateSM2(currentProgress, quality);
        const days = preview.interval;

        if (days === 0) return 'Ngay bây giờ';
        if (days === 1) return '1 ngày';
        if (days < 7) return `${days} ngày`;
        if (days < 30) return `${Math.round(days / 7)} tuần`;
        if (days < 365) return `${Math.round(days / 30)} tháng`;
        return `${Math.round(days / 365)} năm`;
    },

    // ====================================
    // STUDY SESSION
    // ====================================
    
    /**
     * Start a study session
     */
    async startSession(deckId, options = {}) {
        this.state.currentDeck = deckId;
        this.state.cardIndex = 0;
        this.state.sessionStats = {
            reviewed: 0,
            correct: 0,
            incorrect: 0,
            newLearned: 0,
            totalTime: 0,
            startTime: Date.now()
        };

        // Get study cards
        this.state.sessionCards = await this.getStudyCards(deckId, options);
        
        if (this.state.sessionCards.length === 0) {
            return { 
                success: false, 
                message: 'Không có thẻ nào cần ôn tập!',
                stats: await this.getDeckStats(deckId)
            };
        }

        this.state.currentCard = this.state.sessionCards[0];
        this.state.isReviewMode = true;

        this.log(`Session started with ${this.state.sessionCards.length} cards`);

        return {
            success: true,
            totalCards: this.state.sessionCards.length,
            currentCard: this.state.currentCard
        };
    },

    /**
     * Get current card in session
     */
    getCurrentCard() {
        return this.state.currentCard;
    },

    /**
     * Process answer and move to next card
     */
    async answerCard(button) {
        if (!this.state.currentCard) return null;

        const quality = this.getQualityFromButton(button);
        const progress = await this.reviewCard(this.state.currentCard, quality);

        // If failed, add card back to queue (with some delay)
        if (quality < 3 && this.state.sessionCards.length > 1) {
            // Remove current card
            this.state.sessionCards.splice(this.state.cardIndex, 1);
            // Add it back later in the queue
            const insertPosition = Math.min(
                this.state.cardIndex + 3 + Math.floor(Math.random() * 3),
                this.state.sessionCards.length
            );
            this.state.currentCard.progress = progress;
            this.state.sessionCards.splice(insertPosition, 0, this.state.currentCard);
        } else {
            // Move to next card
            this.state.cardIndex++;
        }

        // Check if session complete
        if (this.state.cardIndex >= this.state.sessionCards.length) {
            return this.endSession();
        }

        // Get next card
        this.state.currentCard = this.state.sessionCards[this.state.cardIndex];

        return {
            done: false,
            progress: this.state.cardIndex / this.state.sessionCards.length * 100,
            remaining: this.state.sessionCards.length - this.state.cardIndex,
            currentCard: this.state.currentCard,
            stats: { ...this.state.sessionStats }
        };
    },

    /**
     * End study session
     */
    endSession() {
        this.state.sessionStats.totalTime = Date.now() - this.state.sessionStats.startTime;
        this.state.isReviewMode = false;

        const result = {
            done: true,
            stats: {
                ...this.state.sessionStats,
                accuracy: this.state.sessionStats.reviewed > 0 
                    ? Math.round(this.state.sessionStats.correct / this.state.sessionStats.reviewed * 100)
                    : 0,
                avgTimePerCard: this.state.sessionStats.reviewed > 0
                    ? Math.round(this.state.sessionStats.totalTime / this.state.sessionStats.reviewed / 1000)
                    : 0
            }
        };

        this.log('Session ended:', result.stats);
        return result;
    },

    /**
     * Skip current card
     */
    skipCard() {
        if (!this.state.currentCard) return null;

        this.state.cardIndex++;
        
        if (this.state.cardIndex >= this.state.sessionCards.length) {
            return this.endSession();
        }

        this.state.currentCard = this.state.sessionCards[this.state.cardIndex];

        return {
            done: false,
            currentCard: this.state.currentCard,
            remaining: this.state.sessionCards.length - this.state.cardIndex
        };
    },

    // ====================================
    // AUDIO & PRONUNCIATION
    // ====================================
    
    /**
     * Play pronunciation using Web Speech API
     */
    speak(text, lang = 'en-US') {
        if (!('speechSynthesis' in window)) {
            this.log('Speech synthesis not supported');
            return false;
        }

        // Cancel any ongoing speech
        speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = lang;
        utterance.rate = 0.9;
        utterance.pitch = 1;

        // Try to use a native English voice
        const voices = speechSynthesis.getVoices();
        const englishVoice = voices.find(v => 
            v.lang.startsWith('en') && (v.name.includes('Google') || v.name.includes('Microsoft'))
        );
        if (englishVoice) {
            utterance.voice = englishVoice;
        }

        speechSynthesis.speak(utterance);
        return true;
    },

    /**
     * Play card audio
     */
    async playCardAudio(card) {
        if (card.audioUrl) {
            // Play from URL
            const audio = new Audio(card.audioUrl);
            await audio.play();
        } else if (card.front) {
            // Use TTS
            this.speak(card.front);
        }
    },

    // ====================================
    // IMPORT/EXPORT
    // ====================================
    
    /**
     * Import cards from CSV
     */
    async importFromCSV(deckId, csvText, options = {}) {
        const { delimiter = ',', hasHeader = true } = options;
        
        const lines = csvText.trim().split('\n');
        const startIndex = hasHeader ? 1 : 0;
        const cards = [];

        for (let i = startIndex; i < lines.length; i++) {
            const parts = lines[i].split(delimiter).map(p => p.trim().replace(/^"|"$/g, ''));
            
            if (parts.length >= 2) {
                cards.push({
                    front: parts[0],
                    back: parts[1],
                    pronunciation: parts[2] || null,
                    example: parts[3] || null,
                    tags: parts[4] ? parts[4].split(';') : []
                });
            }
        }

        const added = await this.addCards(deckId, cards);
        this.log(`Imported ${added.length} cards from CSV`);
        
        return added;
    },

    /**
     * Export deck to CSV
     */
    async exportToCSV(deckId) {
        if (typeof englishDB === 'undefined') return '';

        const cards = await englishDB.getByIndex('flashcards', 'deckId', deckId);
        
        const header = 'front,back,pronunciation,example,tags\n';
        const rows = cards.map(card => {
            return [
                `"${card.front}"`,
                `"${card.back}"`,
                `"${card.pronunciation || ''}"`,
                `"${card.example || ''}"`,
                `"${(card.tags || []).join(';')}"`
            ].join(',');
        });

        return header + rows.join('\n');
    },

    /**
     * Import from Anki format
     */
    async importFromAnki(deckId, ankiText) {
        // Anki uses tab-separated values
        return this.importFromCSV(deckId, ankiText, { delimiter: '\t' });
    },

    // ====================================
    // STATISTICS
    // ====================================
    
    /**
     * Get learning statistics
     */
    async getStatistics(deckId, period = 30) {
        if (typeof englishDB === 'undefined') {
            return { daily: [], total: {} };
        }

        const reviews = await englishDB.getAll('flashcardReviews');
        const cutoffDate = new Date();
        cutoffDate.setDate(cutoffDate.getDate() - period);

        // Filter by deck and period
        const filteredReviews = reviews.filter(r => 
            (!deckId || r.deckId === deckId) &&
            new Date(r.reviewedAt) >= cutoffDate
        );

        // Group by day
        const dailyStats = {};
        for (const review of filteredReviews) {
            const day = review.reviewedAt.split('T')[0];
            if (!dailyStats[day]) {
                dailyStats[day] = { reviewed: 0, correct: 0, newLearned: 0 };
            }
            dailyStats[day].reviewed++;
            if (review.quality >= 3) dailyStats[day].correct++;
            if (review.wasNew) dailyStats[day].newLearned++;
        }

        // Convert to array
        const daily = Object.entries(dailyStats)
            .map(([date, stats]) => ({ date, ...stats }))
            .sort((a, b) => a.date.localeCompare(b.date));

        // Calculate totals
        const total = {
            reviewed: filteredReviews.length,
            correct: filteredReviews.filter(r => r.quality >= 3).length,
            newLearned: filteredReviews.filter(r => r.wasNew).length,
            avgAccuracy: filteredReviews.length > 0
                ? Math.round(filteredReviews.filter(r => r.quality >= 3).length / filteredReviews.length * 100)
                : 0
        };

        return { daily, total };
    },

    /**
     * Get streak information
     */
    async getStreak() {
        if (typeof englishDB === 'undefined') return { current: 0, longest: 0 };

        const reviews = await englishDB.getAll('flashcardReviews');
        const reviewDays = new Set(reviews.map(r => r.reviewedAt.split('T')[0]));
        
        let currentStreak = 0;
        let longestStreak = 0;
        let tempStreak = 0;
        
        const today = new Date().toISOString().split('T')[0];
        let checkDate = new Date();

        // Check current streak
        while (true) {
            const dateStr = checkDate.toISOString().split('T')[0];
            if (reviewDays.has(dateStr)) {
                currentStreak++;
                checkDate.setDate(checkDate.getDate() - 1);
            } else if (dateStr === today) {
                // Today not reviewed yet, continue checking
                checkDate.setDate(checkDate.getDate() - 1);
            } else {
                break;
            }
        }

        // Calculate longest streak
        const sortedDays = Array.from(reviewDays).sort();
        for (let i = 0; i < sortedDays.length; i++) {
            if (i === 0) {
                tempStreak = 1;
            } else {
                const prevDate = new Date(sortedDays[i - 1]);
                const currDate = new Date(sortedDays[i]);
                const diffDays = (currDate - prevDate) / (1000 * 60 * 60 * 24);
                
                if (diffDays === 1) {
                    tempStreak++;
                } else {
                    longestStreak = Math.max(longestStreak, tempStreak);
                    tempStreak = 1;
                }
            }
        }
        longestStreak = Math.max(longestStreak, tempStreak);

        return { current: currentStreak, longest: longestStreak };
    },

    // ====================================
    // UTILITIES
    // ====================================
    
    /**
     * Shuffle array in place
     */
    shuffleArray(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
        return array;
    },

    /**
     * Debug logging
     */
    log(...args) {
        if (this.config.debug) {
            console.log('[Flashcard]', ...args);
        }
    }
};

// Export
window.FlashcardEngine = FlashcardEngine;

console.log('[Flashcard Engine] Module loaded');
