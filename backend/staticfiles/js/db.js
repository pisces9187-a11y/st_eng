/* ====================================
   IndexedDB Database Manager
   English Learning Platform
   Phase 1: Offline Storage
   Created: 08/12/2025
   ==================================== */

/**
 * EnglishDB - IndexedDB wrapper for offline data storage
 * Handles flashcards, progress, user data, and sync queue
 */
class EnglishDB {
    constructor() {
        this.dbName = 'EnglishLearningDB';
        this.dbVersion = 1;
        this.db = null;
        this.isReady = false;
        this.readyPromise = this.init();
    }

    // ====================================
    // DATABASE INITIALIZATION
    // ====================================

    /**
     * Initialize the database
     */
    async init() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, this.dbVersion);

            request.onerror = (event) => {
                console.error('[DB] Error opening database:', event.target.error);
                reject(event.target.error);
            };

            request.onsuccess = (event) => {
                this.db = event.target.result;
                this.isReady = true;
                console.log('[DB] Database opened successfully');
                resolve(this.db);
            };

            request.onupgradeneeded = (event) => {
                console.log('[DB] Database upgrade needed');
                const db = event.target.result;
                this.createStores(db);
            };
        });
    }

    /**
     * Create object stores (tables)
     */
    createStores(db) {
        // ====================================
        // USER STORE
        // ====================================
        if (!db.objectStoreNames.contains('users')) {
            const userStore = db.createObjectStore('users', { keyPath: 'id' });
            userStore.createIndex('email', 'email', { unique: true });
            console.log('[DB] Created users store');
        }

        // ====================================
        // FLASHCARDS STORE
        // ====================================
        if (!db.objectStoreNames.contains('flashcards')) {
            const flashcardStore = db.createObjectStore('flashcards', { keyPath: 'id' });
            flashcardStore.createIndex('level', 'level', { unique: false });
            flashcardStore.createIndex('topic', 'topic', { unique: false });
            flashcardStore.createIndex('type', 'type', { unique: false });
            flashcardStore.createIndex('nextReview', 'nextReview', { unique: false });
            flashcardStore.createIndex('masteryLevel', 'masteryLevel', { unique: false });
            console.log('[DB] Created flashcards store');
        }

        // ====================================
        // FLASHCARD PROGRESS STORE
        // ====================================
        if (!db.objectStoreNames.contains('flashcardProgress')) {
            const progressStore = db.createObjectStore('flashcardProgress', { keyPath: 'id', autoIncrement: true });
            progressStore.createIndex('flashcardId', 'flashcardId', { unique: false });
            progressStore.createIndex('reviewDate', 'reviewDate', { unique: false });
            progressStore.createIndex('synced', 'synced', { unique: false });
            console.log('[DB] Created flashcardProgress store');
        }

        // ====================================
        // LESSONS STORE
        // ====================================
        if (!db.objectStoreNames.contains('lessons')) {
            const lessonStore = db.createObjectStore('lessons', { keyPath: 'id' });
            lessonStore.createIndex('level', 'level', { unique: false });
            lessonStore.createIndex('topic', 'topic', { unique: false });
            lessonStore.createIndex('unitId', 'unitId', { unique: false });
            console.log('[DB] Created lessons store');
        }

        // ====================================
        // LESSON PROGRESS STORE
        // ====================================
        if (!db.objectStoreNames.contains('lessonProgress')) {
            const lessonProgressStore = db.createObjectStore('lessonProgress', { keyPath: 'lessonId' });
            lessonProgressStore.createIndex('completed', 'completed', { unique: false });
            lessonProgressStore.createIndex('lastAccessed', 'lastAccessed', { unique: false });
            lessonProgressStore.createIndex('synced', 'synced', { unique: false });
            console.log('[DB] Created lessonProgress store');
        }

        // ====================================
        // VOCABULARY STORE
        // ====================================
        if (!db.objectStoreNames.contains('vocabulary')) {
            const vocabStore = db.createObjectStore('vocabulary', { keyPath: 'id' });
            vocabStore.createIndex('word', 'word', { unique: false });
            vocabStore.createIndex('level', 'level', { unique: false });
            vocabStore.createIndex('topic', 'topic', { unique: false });
            vocabStore.createIndex('learned', 'learned', { unique: false });
            console.log('[DB] Created vocabulary store');
        }

        // ====================================
        // PRACTICE RESULTS STORE
        // ====================================
        if (!db.objectStoreNames.contains('practiceResults')) {
            const practiceStore = db.createObjectStore('practiceResults', { keyPath: 'id', autoIncrement: true });
            practiceStore.createIndex('type', 'type', { unique: false }); // speaking, writing, listening, reading
            practiceStore.createIndex('date', 'date', { unique: false });
            practiceStore.createIndex('synced', 'synced', { unique: false });
            console.log('[DB] Created practiceResults store');
        }

        // ====================================
        // SYNC QUEUE STORE
        // ====================================
        if (!db.objectStoreNames.contains('syncQueue')) {
            const syncStore = db.createObjectStore('syncQueue', { keyPath: 'id', autoIncrement: true });
            syncStore.createIndex('type', 'type', { unique: false });
            syncStore.createIndex('timestamp', 'timestamp', { unique: false });
            syncStore.createIndex('status', 'status', { unique: false });
            console.log('[DB] Created syncQueue store');
        }

        // ====================================
        // SETTINGS STORE
        // ====================================
        if (!db.objectStoreNames.contains('settings')) {
            db.createObjectStore('settings', { keyPath: 'key' });
            console.log('[DB] Created settings store');
        }

        // ====================================
        // CACHE METADATA STORE
        // ====================================
        if (!db.objectStoreNames.contains('cacheMetadata')) {
            const cacheStore = db.createObjectStore('cacheMetadata', { keyPath: 'url' });
            cacheStore.createIndex('cachedAt', 'cachedAt', { unique: false });
            cacheStore.createIndex('expiresAt', 'expiresAt', { unique: false });
            console.log('[DB] Created cacheMetadata store');
        }
    }

    /**
     * Wait for database to be ready
     */
    async ready() {
        if (this.isReady) return this.db;
        return this.readyPromise;
    }

    // ====================================
    // GENERIC CRUD OPERATIONS
    // ====================================

    /**
     * Add or update a record
     */
    async put(storeName, data) {
        await this.ready();
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);
            const request = store.put(data);

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Add multiple records
     */
    async putMany(storeName, dataArray) {
        await this.ready();
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);
            let completed = 0;

            dataArray.forEach(data => {
                const request = store.put(data);
                request.onsuccess = () => {
                    completed++;
                    if (completed === dataArray.length) {
                        resolve(completed);
                    }
                };
                request.onerror = () => reject(request.error);
            });
        });
    }

    /**
     * Get a record by key
     */
    async get(storeName, key) {
        await this.ready();
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readonly');
            const store = transaction.objectStore(storeName);
            const request = store.get(key);

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Get all records from a store
     */
    async getAll(storeName) {
        await this.ready();
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readonly');
            const store = transaction.objectStore(storeName);
            const request = store.getAll();

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Get records by index
     */
    async getByIndex(storeName, indexName, value) {
        await this.ready();
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readonly');
            const store = transaction.objectStore(storeName);
            const index = store.index(indexName);
            const request = index.getAll(value);

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Get records by index range
     */
    async getByIndexRange(storeName, indexName, lowerBound, upperBound) {
        await this.ready();
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readonly');
            const store = transaction.objectStore(storeName);
            const index = store.index(indexName);
            const range = IDBKeyRange.bound(lowerBound, upperBound);
            const request = index.getAll(range);

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Delete a record by key
     */
    async delete(storeName, key) {
        await this.ready();
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);
            const request = store.delete(key);

            request.onsuccess = () => resolve(true);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Clear all records from a store
     */
    async clear(storeName) {
        await this.ready();
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);
            const request = store.clear();

            request.onsuccess = () => resolve(true);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Count records in a store
     */
    async count(storeName) {
        await this.ready();
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readonly');
            const store = transaction.objectStore(storeName);
            const request = store.count();

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    // ====================================
    // FLASHCARD SPECIFIC METHODS
    // ====================================

    /**
     * Save flashcard with progress
     */
    async saveFlashcard(flashcard) {
        const data = {
            ...flashcard,
            lastUpdated: new Date().toISOString()
        };
        return this.put('flashcards', data);
    }

    /**
     * Get flashcards due for review
     */
    async getDueFlashcards(limit = 20) {
        const now = new Date().toISOString();
        const allCards = await this.getAll('flashcards');
        
        return allCards
            .filter(card => !card.nextReview || card.nextReview <= now)
            .sort((a, b) => {
                // Prioritize cards never reviewed, then by next review date
                if (!a.nextReview) return -1;
                if (!b.nextReview) return 1;
                return new Date(a.nextReview) - new Date(b.nextReview);
            })
            .slice(0, limit);
    }

    /**
     * Update flashcard after review
     */
    async updateFlashcardReview(flashcardId, quality) {
        const flashcard = await this.get('flashcards', flashcardId);
        if (!flashcard) return null;

        // Apply SM-2 algorithm
        const updated = this.calculateSM2(flashcard, quality);
        updated.lastReview = new Date().toISOString();
        updated.timesReviewed = (updated.timesReviewed || 0) + 1;
        
        if (quality >= 3) {
            updated.timesCorrect = (updated.timesCorrect || 0) + 1;
        } else {
            updated.timesIncorrect = (updated.timesIncorrect || 0) + 1;
        }
        
        // Calculate mastery level
        updated.masteryLevel = Math.round(
            (updated.timesCorrect / updated.timesReviewed) * 100
        );

        await this.put('flashcards', updated);

        // Add to progress history
        await this.put('flashcardProgress', {
            flashcardId,
            quality,
            reviewDate: new Date().toISOString(),
            synced: false
        });

        // Add to sync queue
        await this.addToSyncQueue('flashcard-review', {
            flashcardId,
            quality,
            timestamp: new Date().toISOString()
        });

        return updated;
    }

    /**
     * SM-2 Spaced Repetition Algorithm
     */
    calculateSM2(card, quality) {
        // quality: 0-2 (fail), 3 (hard), 4 (good), 5 (easy)
        let { repetition = 0, interval = 1, easeFactor = 2.5 } = card;

        if (quality < 3) {
            // Failed - reset
            repetition = 0;
            interval = 1;
        } else {
            // Passed
            if (repetition === 0) {
                interval = 1;
            } else if (repetition === 1) {
                interval = 6;
            } else {
                interval = Math.round(interval * easeFactor);
            }
            repetition++;
        }

        // Update ease factor
        easeFactor = Math.max(1.3,
            easeFactor + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
        );

        // Calculate next review date
        const nextReview = new Date();
        nextReview.setDate(nextReview.getDate() + interval);

        return {
            ...card,
            repetition,
            interval,
            easeFactor,
            nextReview: nextReview.toISOString()
        };
    }

    /**
     * Get flashcard statistics
     */
    async getFlashcardStats() {
        const cards = await this.getAll('flashcards');
        const now = new Date();

        return {
            total: cards.length,
            mastered: cards.filter(c => c.masteryLevel >= 90).length,
            learning: cards.filter(c => c.masteryLevel > 0 && c.masteryLevel < 90).length,
            new: cards.filter(c => !c.masteryLevel || c.masteryLevel === 0).length,
            dueToday: cards.filter(c => {
                if (!c.nextReview) return true;
                return new Date(c.nextReview) <= now;
            }).length
        };
    }

    // ====================================
    // LESSON PROGRESS METHODS
    // ====================================

    /**
     * Update lesson progress
     */
    async updateLessonProgress(lessonId, progress) {
        const existing = await this.get('lessonProgress', lessonId) || {};
        
        const updated = {
            lessonId,
            ...existing,
            ...progress,
            lastAccessed: new Date().toISOString(),
            synced: false
        };

        await this.put('lessonProgress', updated);

        // Add to sync queue
        await this.addToSyncQueue('lesson-progress', updated);

        return updated;
    }

    /**
     * Get lesson progress
     */
    async getLessonProgress(lessonId) {
        return this.get('lessonProgress', lessonId);
    }

    /**
     * Get all lesson progress
     */
    async getAllLessonProgress() {
        return this.getAll('lessonProgress');
    }

    // ====================================
    // SYNC QUEUE METHODS
    // ====================================

    /**
     * Add item to sync queue
     */
    async addToSyncQueue(type, data) {
        return this.put('syncQueue', {
            type,
            data,
            timestamp: new Date().toISOString(),
            status: 'pending'
        });
    }

    /**
     * Get pending sync items
     */
    async getPendingSyncItems(type = null) {
        const items = await this.getByIndex('syncQueue', 'status', 'pending');
        if (type) {
            return items.filter(item => item.type === type);
        }
        return items;
    }

    /**
     * Mark sync item as completed
     */
    async markSyncCompleted(id) {
        const item = await this.get('syncQueue', id);
        if (item) {
            item.status = 'completed';
            item.syncedAt = new Date().toISOString();
            await this.put('syncQueue', item);
        }
    }

    /**
     * Clear completed sync items
     */
    async clearCompletedSync() {
        const completed = await this.getByIndex('syncQueue', 'status', 'completed');
        for (const item of completed) {
            await this.delete('syncQueue', item.id);
        }
        return completed.length;
    }

    // ====================================
    // SETTINGS METHODS
    // ====================================

    /**
     * Save a setting
     */
    async setSetting(key, value) {
        return this.put('settings', { key, value, updatedAt: new Date().toISOString() });
    }

    /**
     * Get a setting
     */
    async getSetting(key, defaultValue = null) {
        const setting = await this.get('settings', key);
        return setting ? setting.value : defaultValue;
    }

    /**
     * Get all settings
     */
    async getAllSettings() {
        const settings = await this.getAll('settings');
        return settings.reduce((acc, item) => {
            acc[item.key] = item.value;
            return acc;
        }, {});
    }

    // ====================================
    // PRACTICE RESULTS METHODS
    // ====================================

    /**
     * Save practice result
     */
    async savePracticeResult(type, result) {
        const data = {
            type,
            ...result,
            date: new Date().toISOString(),
            synced: false
        };

        await this.put('practiceResults', data);
        await this.addToSyncQueue('practice-result', data);

        return data;
    }

    /**
     * Get practice results by type
     */
    async getPracticeResults(type, limit = 10) {
        const results = await this.getByIndex('practiceResults', 'type', type);
        return results
            .sort((a, b) => new Date(b.date) - new Date(a.date))
            .slice(0, limit);
    }

    /**
     * Get practice statistics
     */
    async getPracticeStats(type, days = 30) {
        const results = await this.getByIndex('practiceResults', 'type', type);
        const cutoff = new Date();
        cutoff.setDate(cutoff.getDate() - days);

        const recent = results.filter(r => new Date(r.date) >= cutoff);

        return {
            totalSessions: recent.length,
            averageScore: recent.length > 0
                ? Math.round(recent.reduce((sum, r) => sum + (r.score || 0), 0) / recent.length)
                : 0,
            totalTime: recent.reduce((sum, r) => sum + (r.duration || 0), 0),
            streak: this.calculateStreak(recent)
        };
    }

    /**
     * Calculate learning streak
     */
    calculateStreak(results) {
        if (results.length === 0) return 0;

        const sortedDates = [...new Set(results.map(r => 
            new Date(r.date).toDateString()
        ))].sort((a, b) => new Date(b) - new Date(a));

        let streak = 0;
        const today = new Date().toDateString();
        const yesterday = new Date(Date.now() - 86400000).toDateString();

        // Check if practiced today or yesterday
        if (sortedDates[0] !== today && sortedDates[0] !== yesterday) {
            return 0;
        }

        // Count consecutive days
        for (let i = 0; i < sortedDates.length; i++) {
            const expectedDate = new Date();
            expectedDate.setDate(expectedDate.getDate() - i);
            
            if (sortedDates[i] === expectedDate.toDateString()) {
                streak++;
            } else {
                break;
            }
        }

        return streak;
    }

    // ====================================
    // UTILITY METHODS
    // ====================================

    /**
     * Export all data for backup
     */
    async exportData() {
        const data = {
            exportDate: new Date().toISOString(),
            version: this.dbVersion,
            flashcards: await this.getAll('flashcards'),
            flashcardProgress: await this.getAll('flashcardProgress'),
            lessonProgress: await this.getAll('lessonProgress'),
            vocabulary: await this.getAll('vocabulary'),
            practiceResults: await this.getAll('practiceResults'),
            settings: await this.getAll('settings')
        };

        return JSON.stringify(data, null, 2);
    }

    /**
     * Import data from backup
     */
    async importData(jsonString) {
        try {
            const data = JSON.parse(jsonString);
            
            if (data.flashcards) {
                await this.putMany('flashcards', data.flashcards);
            }
            if (data.flashcardProgress) {
                await this.putMany('flashcardProgress', data.flashcardProgress);
            }
            if (data.lessonProgress) {
                await this.putMany('lessonProgress', data.lessonProgress);
            }
            if (data.vocabulary) {
                await this.putMany('vocabulary', data.vocabulary);
            }
            if (data.practiceResults) {
                await this.putMany('practiceResults', data.practiceResults);
            }
            if (data.settings) {
                await this.putMany('settings', data.settings);
            }

            return { success: true, message: 'Import completed' };
        } catch (error) {
            return { success: false, message: error.message };
        }
    }

    /**
     * Get database size estimate
     */
    async getDatabaseSize() {
        if ('storage' in navigator && 'estimate' in navigator.storage) {
            const estimate = await navigator.storage.estimate();
            return {
                used: estimate.usage,
                quota: estimate.quota,
                usedMB: (estimate.usage / (1024 * 1024)).toFixed(2),
                quotaMB: (estimate.quota / (1024 * 1024)).toFixed(2),
                percentUsed: ((estimate.usage / estimate.quota) * 100).toFixed(1)
            };
        }
        return null;
    }

    /**
     * Close the database connection
     */
    close() {
        if (this.db) {
            this.db.close();
            this.db = null;
            this.isReady = false;
        }
    }
}

// ====================================
// SINGLETON INSTANCE
// ====================================
const englishDB = new EnglishDB();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = englishDB;
}

// Make available globally
window.englishDB = englishDB;

console.log('[DB] IndexedDB module loaded');
