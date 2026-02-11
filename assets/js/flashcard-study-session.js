/* ====================================
   FLASHCARD STUDY SESSION MANAGER
   Backend-integrated SM-2 Spaced Repetition
   Version: 2.0.0 - Phase 2
   ==================================== */

/**
 * FlashcardStudySession - Manages study sessions with backend API
 * 
 * Features:
 * - Backend-driven SM-2 algorithm
 * - Session tracking (start/end)
 * - Real-time statistics
 * - Achievement progress
 * - Daily goal tracking
 * - Streak monitoring
 */
const FlashcardStudySession = {
    // Configuration
    config: {
        defaultCardCount: 20,
        autoPlayAudio: false,
        showHints: true,
        keyboardShortcuts: true,
        confettiOnGoal: true
    },

    // Session state
    session: {
        id: null,
        deckId: null,
        cards: [],
        currentIndex: 0,
        startTime: null,
        stats: {
            cardsReviewed: 0,
            cardsCorrect: 0,
            cardsIncorrect: 0,
            timeSpent: 0,
            accuracy: 0
        },
        dailyProgress: {
            cardsToday: 0,
            dailyGoal: 20,
            progressPercentage: 0,
            isGoalReached: false
        },
        streak: {
            current: 0,
            longest: 0
        }
    },

    // Callbacks
    callbacks: {
        onSessionStart: null,
        onCardChange: null,
        onReviewComplete: null,
        onSessionEnd: null,
        onGoalReached: null,
        onAchievementUnlocked: null
    },

    /**
     * Start a new study session
     * @param {number} deckId - Deck ID (optional)
     * @param {number} cardCount - Number of cards
     * @param {string} level - Filter by level (A1, A2, etc.)
     * @returns {Promise<Object>} Session data
     */
    async startSession(deckId = null, cardCount = null, level = null) {
        try {
            console.log('[FlashcardStudySession] Starting session...');

            const params = {
                card_count: cardCount || this.config.defaultCardCount
            };
            if (deckId) params.deck_id = deckId;
            if (level) params.level = level;

            // Call API to start session
            const response = await window.djangoApi.startFlashcardSession(deckId, params.card_count, level);

            if (!response.success) {
                throw new Error(response.error || 'Failed to start session');
            }

            // Extract data from response wrapper
            const data = response.data || response;

            // Initialize session
            this.session.id = data.session_id;
            this.session.deckId = deckId;
            this.session.cards = data.cards || [];
            this.session.currentIndex = 0;
            this.session.startTime = new Date();
            this.session.dailyProgress = data.daily_progress || {};
            this.session.streak = data.streak || { current: 0, longest: 0 };

            // Reset stats
            this.session.stats = {
                cardsReviewed: 0,
                cardsCorrect: 0,
                cardsIncorrect: 0,
                timeSpent: 0,
                accuracy: 0
            };

            console.log(`[FlashcardStudySession] Session started with ${this.session.cards.length} cards`);

            // Trigger callback
            if (this.callbacks.onSessionStart) {
                this.callbacks.onSessionStart(this.session);
            }

            return {
                success: true,
                session: this.session,
                cards: this.session.cards
            };

        } catch (error) {
            console.error('[FlashcardStudySession] Start session error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    },

    /**
     * Get current card
     * @returns {Object|null} Current flashcard
     */
    getCurrentCard() {
        if (this.session.currentIndex >= this.session.cards.length) {
            return null;
        }
        return this.session.cards[this.session.currentIndex];
    },

    /**
     * Review current card
     * @param {number} quality - Quality rating (0-5)
     * @returns {Promise<Object>} Review result
     */
    async reviewCard(quality) {
        const card = this.getCurrentCard();
        if (!card) {
            return { success: false, error: 'No card to review' };
        }

        try {
            console.log(`[FlashcardStudySession] Reviewing card ${card.id} with quality ${quality}`);

            // Call API to review card
            const response = await window.djangoApi.reviewFlashcardCard(
                card.id,
                this.session.id,
                quality
            );

            if (!response.success) {
                throw new Error(response.error || 'Review failed');
            }

            // Extract data from response wrapper
            const data = response.data || response;

            // Update stats
            this.session.stats.cardsReviewed++;
            if (quality >= 3) {
                this.session.stats.cardsCorrect++;
            } else {
                this.session.stats.cardsIncorrect++;
            }

            // Calculate accuracy
            this.session.stats.accuracy = Math.round(
                (this.session.stats.cardsCorrect / this.session.stats.cardsReviewed) * 100
            );

            // Update card progress from response
            if (data.progress) {
                card.progress = data.progress;
                card.next_review = data.progress.next_review_at;
                card.is_mastered = data.progress.is_mastered;
            }

            // Check for achievements
            if (data.achievements_unlocked && data.achievements_unlocked.length > 0) {
                this.handleAchievementsUnlocked(data.achievements_unlocked);
            }

            // Check daily goal
            if (data.daily_progress) {
                this.session.dailyProgress = data.daily_progress;
                
                if (data.daily_progress.is_goal_reached && !this.session.goalReached) {
                    this.session.goalReached = true;
                    this.handleGoalReached();
                }
            }

            // Trigger callback
            if (this.callbacks.onReviewComplete) {
                this.callbacks.onReviewComplete(card, quality, data);
            }

            return {
                success: true,
                card,
                progress: data.progress,
                stats: this.session.stats
            };

        } catch (error) {
            console.error('[FlashcardStudySession] Review error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    },

    /**
     * Move to next card
     * @returns {Object|null} Next card or null if finished
     */
    nextCard() {
        this.session.currentIndex++;
        
        const nextCard = this.getCurrentCard();
        
        // Trigger callback
        if (this.callbacks.onCardChange) {
            this.callbacks.onCardChange(nextCard, this.session.currentIndex);
        }

        return nextCard;
    },

    /**
     * Check if session is complete
     * @returns {boolean}
     */
    isComplete() {
        return this.session.currentIndex >= this.session.cards.length;
    },

    /**
     * Get session progress
     * @returns {Object} Progress data
     */
    getProgress() {
        const total = this.session.cards.length;
        const reviewed = this.session.stats.cardsReviewed;
        const remaining = total - reviewed;
        const percentage = total > 0 ? Math.round((reviewed / total) * 100) : 0;

        return {
            total,
            reviewed,
            remaining,
            percentage,
            currentIndex: this.session.currentIndex
        };
    },

    /**
     * End current session
     * @returns {Promise<Object>} Session summary
     */
    async endSession() {
        if (!this.session.id) {
            return { success: false, error: 'No active session' };
        }

        try {
            console.log('[FlashcardStudySession] Ending session...');

            // Calculate time spent
            if (this.session.startTime) {
                const endTime = new Date();
                this.session.stats.timeSpent = Math.round(
                    (endTime - this.session.startTime) / 1000
                );
            }

            // Call API to end session
            const response = await window.djangoApi.endFlashcardSession(this.session.id);

            if (!response.success) {
                throw new Error(response.error || 'Failed to end session');
            }

            const summary = {
                ...this.session.stats,
                sessionStats: response.session_stats,
                dailyProgress: response.daily_progress,
                streak: response.streak,
                achievementsUnlocked: response.achievements_unlocked || []
            };

            // Trigger callback
            if (this.callbacks.onSessionEnd) {
                this.callbacks.onSessionEnd(summary);
            }

            // Clear session
            this.clearSession();

            console.log('[FlashcardStudySession] Session ended');
            return {
                success: true,
                summary
            };

        } catch (error) {
            console.error('[FlashcardStudySession] End session error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    },

    /**
     * Clear session data
     */
    clearSession() {
        this.session = {
            id: null,
            deckId: null,
            cards: [],
            currentIndex: 0,
            startTime: null,
            stats: {
                cardsReviewed: 0,
                cardsCorrect: 0,
                cardsIncorrect: 0,
                timeSpent: 0,
                accuracy: 0
            },
            dailyProgress: {
                cardsToday: 0,
                dailyGoal: 20,
                progressPercentage: 0,
                isGoalReached: false
            },
            streak: {
                current: 0,
                longest: 0
            }
        };
    },

    /**
     * Handle goal reached
     */
    handleGoalReached() {
        console.log('[FlashcardStudySession] 🎉 Daily goal reached!');

        // Show confetti animation
        if (this.config.confettiOnGoal && typeof confetti === 'function') {
            confetti({
                particleCount: 100,
                spread: 70,
                origin: { y: 0.6 }
            });
        }

        // Show notification
        if (typeof showToast === 'function') {
            showToast('🎉 Daily goal reached! Great job!', 'success', 3000);
        }

        // Trigger callback
        if (this.callbacks.onGoalReached) {
            this.callbacks.onGoalReached(this.session.dailyProgress);
        }
    },

    /**
     * Handle achievements unlocked
     * @param {Array} achievements - Unlocked achievements
     */
    handleAchievementsUnlocked(achievements) {
        console.log('[FlashcardStudySession] 🏆 Achievements unlocked:', achievements);

        // Show confetti
        if (typeof confetti === 'function') {
            confetti({
                particleCount: 150,
                spread: 90,
                origin: { y: 0.6 },
                colors: ['#FFD700', '#FFA500', '#FF6347']
            });
        }

        // Show notifications for each achievement
        achievements.forEach(achievement => {
            if (typeof showToast === 'function') {
                showToast(
                    `🏆 Achievement Unlocked: ${achievement.name}!`,
                    'success',
                    5000
                );
            }
        });

        // Trigger callback
        if (this.callbacks.onAchievementUnlocked) {
            this.callbacks.onAchievementUnlocked(achievements);
        }
    },

    /**
     * Set callback
     * @param {string} event - Event name
     * @param {Function} callback - Callback function
     */
    on(event, callback) {
        const callbackName = `on${event.charAt(0).toUpperCase()}${event.slice(1)}`;
        if (this.callbacks.hasOwnProperty(callbackName)) {
            this.callbacks[callbackName] = callback;
        } else {
            console.warn(`[FlashcardStudySession] Unknown event: ${event}`);
        }
    },

    /**
     * Get session statistics
     * @returns {Object} Stats object
     */
    getStats() {
        return {
            ...this.session.stats,
            progress: this.getProgress(),
            dailyProgress: this.session.dailyProgress,
            streak: this.session.streak
        };
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FlashcardStudySession;
}
