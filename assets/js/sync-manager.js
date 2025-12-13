/* ====================================
   SYNC MANAGER MODULE
   English Learning Platform
   Phase 4: Backend Integration
   Created: 08/12/2025
   ==================================== */

/**
 * SyncManager - Handles bidirectional data synchronization
 * between local IndexedDB and remote server
 */
class SyncManager {
    constructor(db, apiService) {
        // ====================================
        // DEPENDENCIES
        // ====================================
        this.db = db || window.englishDB;
        this.api = apiService || window.api;

        // ====================================
        // CONFIGURATION
        // ====================================
        this.config = {
            syncInterval: 5 * 60 * 1000, // 5 minutes
            batchSize: 50,
            maxRetries: 3,
            conflictResolution: 'server-wins', // 'server-wins', 'client-wins', 'newest-wins'
            debug: true
        };

        // ====================================
        // STATE
        // ====================================
        this.state = {
            isSyncing: false,
            lastSyncTime: null,
            syncErrors: [],
            pendingChanges: 0,
            syncProgress: 0
        };

        // ====================================
        // SYNC QUEUES
        // ====================================
        this.syncQueues = {
            flashcardProgress: [],
            lessonProgress: [],
            practiceResults: [],
            vocabulary: [],
            settings: []
        };

        // ====================================
        // EVENT CALLBACKS
        // ====================================
        this.callbacks = {
            onSyncStart: [],
            onSyncComplete: [],
            onSyncError: [],
            onSyncProgress: [],
            onConflict: []
        };

        // Initialize
        this.init();
    }

    // ====================================
    // INITIALIZATION
    // ====================================

    async init() {
        this.log('Initializing SyncManager...');

        // Load last sync time
        await this.loadSyncMetadata();

        // Setup network listeners
        this.setupNetworkListeners();

        // Start periodic sync
        this.startPeriodicSync();

        // Listen for page visibility changes
        this.setupVisibilityListener();

        this.log('SyncManager initialized');
    }

    /**
     * Load sync metadata from IndexedDB
     */
    async loadSyncMetadata() {
        try {
            const metadata = await this.db.get('settings', 'sync_metadata');
            if (metadata) {
                this.state.lastSyncTime = metadata.lastSyncTime;
            }
        } catch (error) {
            this.log('Error loading sync metadata:', error);
        }
    }

    /**
     * Save sync metadata
     */
    async saveSyncMetadata() {
        try {
            await this.db.put('settings', {
                key: 'sync_metadata',
                lastSyncTime: this.state.lastSyncTime,
                updatedAt: Date.now()
            });
        } catch (error) {
            this.log('Error saving sync metadata:', error);
        }
    }

    /**
     * Setup network event listeners
     */
    setupNetworkListeners() {
        window.addEventListener('online', () => {
            this.log('Network online - triggering sync');
            this.syncAll();
        });
    }

    /**
     * Setup page visibility listener
     */
    setupVisibilityListener() {
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible' && navigator.onLine) {
                // Sync when user returns to page
                this.syncAll();
            }
        });
    }

    // ====================================
    // PERIODIC SYNC
    // ====================================

    /**
     * Start periodic sync
     */
    startPeriodicSync() {
        this.syncIntervalId = setInterval(() => {
            if (navigator.onLine && !this.state.isSyncing) {
                this.syncAll();
            }
        }, this.config.syncInterval);
    }

    /**
     * Stop periodic sync
     */
    stopPeriodicSync() {
        if (this.syncIntervalId) {
            clearInterval(this.syncIntervalId);
            this.syncIntervalId = null;
        }
    }

    // ====================================
    // MAIN SYNC METHODS
    // ====================================

    /**
     * Sync all data types
     */
    async syncAll() {
        if (this.state.isSyncing) {
            this.log('Sync already in progress');
            return;
        }

        if (!navigator.onLine) {
            this.log('Offline - skipping sync');
            return;
        }

        this.log('Starting full sync...');
        this.state.isSyncing = true;
        this.state.syncProgress = 0;
        this.state.syncErrors = [];
        this.triggerEvent('onSyncStart');

        try {
            // Sync in order of priority
            await this.syncFlashcardProgress();
            this.updateProgress(20);

            await this.syncLessonProgress();
            this.updateProgress(40);

            await this.syncPracticeResults();
            this.updateProgress(60);

            await this.syncVocabulary();
            this.updateProgress(80);

            await this.syncSettings();
            this.updateProgress(90);

            // Pull latest data from server
            await this.pullLatestData();
            this.updateProgress(100);

            // Update sync time
            this.state.lastSyncTime = Date.now();
            await this.saveSyncMetadata();

            this.log('Full sync completed successfully');
            this.triggerEvent('onSyncComplete', {
                success: true,
                errors: this.state.syncErrors
            });
        } catch (error) {
            this.log('Sync error:', error);
            this.state.syncErrors.push(error);
            this.triggerEvent('onSyncError', error);
        } finally {
            this.state.isSyncing = false;
        }
    }

    /**
     * Update sync progress
     */
    updateProgress(progress) {
        this.state.syncProgress = progress;
        this.triggerEvent('onSyncProgress', progress);
    }

    // ====================================
    // FLASHCARD SYNC
    // ====================================

    /**
     * Sync flashcard progress
     */
    async syncFlashcardProgress() {
        this.log('Syncing flashcard progress...');

        try {
            // Get unsynced progress records
            const unsyncedProgress = await this.db.getByIndex(
                'flashcardProgress',
                'synced',
                false
            );

            if (unsyncedProgress.length === 0) {
                this.log('No flashcard progress to sync');
                return;
            }

            // Batch sync
            const batches = this.createBatches(unsyncedProgress, this.config.batchSize);

            for (const batch of batches) {
                try {
                    const response = await this.api.syncFlashcardProgress(batch);

                    if (response.success) {
                        // Mark as synced
                        for (const record of batch) {
                            record.synced = true;
                            record.syncedAt = Date.now();
                            await this.db.put('flashcardProgress', record);
                        }

                        // Handle conflicts if any
                        if (response.data.conflicts) {
                            await this.handleConflicts('flashcardProgress', response.data.conflicts);
                        }
                    }
                } catch (error) {
                    this.log('Flashcard batch sync error:', error);
                    this.state.syncErrors.push({ type: 'flashcardProgress', error });
                }
            }

            this.log(`Synced ${unsyncedProgress.length} flashcard progress records`);
        } catch (error) {
            this.log('Flashcard sync error:', error);
            throw error;
        }
    }

    // ====================================
    // LESSON SYNC
    // ====================================

    /**
     * Sync lesson progress
     */
    async syncLessonProgress() {
        this.log('Syncing lesson progress...');

        try {
            const unsyncedProgress = await this.db.getByIndex(
                'lessonProgress',
                'synced',
                false
            );

            if (unsyncedProgress.length === 0) {
                this.log('No lesson progress to sync');
                return;
            }

            for (const progress of unsyncedProgress) {
                try {
                    const response = await this.api.updateLessonProgress(
                        progress.lessonId,
                        {
                            progress_percent: progress.progressPercent,
                            completed: progress.completed,
                            time_spent: progress.timeSpent,
                            last_position: progress.lastPosition
                        }
                    );

                    if (response.success) {
                        progress.synced = true;
                        progress.syncedAt = Date.now();
                        await this.db.put('lessonProgress', progress);
                    }
                } catch (error) {
                    this.log('Lesson progress sync error:', error);
                    this.state.syncErrors.push({ type: 'lessonProgress', error, lessonId: progress.lessonId });
                }
            }

            this.log(`Synced ${unsyncedProgress.length} lesson progress records`);
        } catch (error) {
            this.log('Lesson sync error:', error);
            throw error;
        }
    }

    // ====================================
    // PRACTICE RESULTS SYNC
    // ====================================

    /**
     * Sync practice results
     */
    async syncPracticeResults() {
        this.log('Syncing practice results...');

        try {
            const unsyncedResults = await this.db.getByIndex(
                'practiceResults',
                'synced',
                false
            );

            if (unsyncedResults.length === 0) {
                this.log('No practice results to sync');
                return;
            }

            for (const result of unsyncedResults) {
                try {
                    const response = await this.api.submitPracticeResult(
                        result.type,
                        {
                            score: result.score,
                            accuracy: result.accuracy,
                            time_spent: result.timeSpent,
                            details: result.details,
                            completed_at: result.date
                        }
                    );

                    if (response.success) {
                        result.synced = true;
                        result.syncedAt = Date.now();
                        result.serverId = response.data.id;
                        await this.db.put('practiceResults', result);
                    }
                } catch (error) {
                    this.log('Practice result sync error:', error);
                    this.state.syncErrors.push({ type: 'practiceResults', error });
                }
            }

            this.log(`Synced ${unsyncedResults.length} practice results`);
        } catch (error) {
            this.log('Practice results sync error:', error);
            throw error;
        }
    }

    // ====================================
    // VOCABULARY SYNC
    // ====================================

    /**
     * Sync vocabulary
     */
    async syncVocabulary() {
        this.log('Syncing vocabulary...');

        try {
            // Get locally modified vocabulary
            const allVocab = await this.db.getAll('vocabulary');
            const unsyncedVocab = allVocab.filter(v => !v.synced || v.modifiedAt > v.syncedAt);

            if (unsyncedVocab.length === 0) {
                this.log('No vocabulary to sync');
                return;
            }

            // Batch upload
            const batches = this.createBatches(unsyncedVocab, this.config.batchSize);

            for (const batch of batches) {
                try {
                    const response = await this.api.post('/vocabulary/sync', {
                        vocabulary: batch.map(v => ({
                            id: v.serverId || null,
                            word: v.word,
                            definition: v.definition,
                            example: v.example,
                            level: v.level,
                            topic: v.topic,
                            learned: v.learned,
                            notes: v.notes
                        }))
                    });

                    if (response.success) {
                        // Update local records with server IDs
                        for (let i = 0; i < batch.length; i++) {
                            batch[i].synced = true;
                            batch[i].syncedAt = Date.now();
                            if (response.data.ids && response.data.ids[i]) {
                                batch[i].serverId = response.data.ids[i];
                            }
                            await this.db.put('vocabulary', batch[i]);
                        }
                    }
                } catch (error) {
                    this.log('Vocabulary batch sync error:', error);
                    this.state.syncErrors.push({ type: 'vocabulary', error });
                }
            }

            this.log(`Synced ${unsyncedVocab.length} vocabulary items`);
        } catch (error) {
            this.log('Vocabulary sync error:', error);
            throw error;
        }
    }

    // ====================================
    // SETTINGS SYNC
    // ====================================

    /**
     * Sync user settings
     */
    async syncSettings() {
        this.log('Syncing settings...');

        try {
            const settings = await this.db.get('settings', 'user_settings');

            if (!settings || settings.synced) {
                this.log('No settings to sync');
                return;
            }

            const response = await this.api.updateSettings(settings.data);

            if (response.success) {
                settings.synced = true;
                settings.syncedAt = Date.now();
                await this.db.put('settings', settings);
            }

            this.log('Settings synced');
        } catch (error) {
            this.log('Settings sync error:', error);
            this.state.syncErrors.push({ type: 'settings', error });
        }
    }

    // ====================================
    // PULL DATA FROM SERVER
    // ====================================

    /**
     * Pull latest data from server
     */
    async pullLatestData() {
        this.log('Pulling latest data from server...');

        try {
            // Get last sync time
            const since = this.state.lastSyncTime 
                ? new Date(this.state.lastSyncTime).toISOString() 
                : null;

            // Pull flashcards
            await this.pullFlashcards(since);

            // Pull lessons
            await this.pullLessons(since);

            // Pull user progress
            await this.pullProgress(since);

            this.log('Data pull completed');
        } catch (error) {
            this.log('Data pull error:', error);
            this.state.syncErrors.push({ type: 'pull', error });
        }
    }

    /**
     * Pull flashcards from server
     */
    async pullFlashcards(since) {
        try {
            const params = since ? { updated_since: since } : {};
            const response = await this.api.get('/flashcards', { params });

            if (response.success && response.data.length > 0) {
                for (const flashcard of response.data) {
                    const existing = await this.db.get('flashcards', flashcard.id);
                    
                    // Handle conflict
                    if (existing && !existing.synced) {
                        await this.handleSingleConflict('flashcards', existing, flashcard);
                    } else {
                        await this.db.put('flashcards', {
                            ...flashcard,
                            synced: true,
                            syncedAt: Date.now()
                        });
                    }
                }
                this.log(`Pulled ${response.data.length} flashcards`);
            }
        } catch (error) {
            this.log('Flashcards pull error:', error);
        }
    }

    /**
     * Pull lessons from server
     */
    async pullLessons(since) {
        try {
            const params = since ? { updated_since: since } : {};
            const response = await this.api.getLessons(params);

            if (response.success && response.data.length > 0) {
                for (const lesson of response.data) {
                    await this.db.put('lessons', {
                        ...lesson,
                        synced: true,
                        syncedAt: Date.now()
                    });
                }
                this.log(`Pulled ${response.data.length} lessons`);
            }
        } catch (error) {
            this.log('Lessons pull error:', error);
        }
    }

    /**
     * Pull user progress from server
     */
    async pullProgress(since) {
        try {
            const response = await this.api.getDetailedProgress({ since });

            if (response.success) {
                // Update local progress with server data
                const serverProgress = response.data;

                // Update lesson progress
                if (serverProgress.lessons) {
                    for (const progress of serverProgress.lessons) {
                        const existing = await this.db.get('lessonProgress', progress.lesson_id);
                        
                        if (!existing || existing.synced || 
                            new Date(progress.updated_at) > new Date(existing.modifiedAt || 0)) {
                            await this.db.put('lessonProgress', {
                                lessonId: progress.lesson_id,
                                progressPercent: progress.progress_percent,
                                completed: progress.completed,
                                timeSpent: progress.time_spent,
                                lastPosition: progress.last_position,
                                synced: true,
                                syncedAt: Date.now()
                            });
                        }
                    }
                }

                this.log('Progress data pulled');
            }
        } catch (error) {
            this.log('Progress pull error:', error);
        }
    }

    // ====================================
    // CONFLICT RESOLUTION
    // ====================================

    /**
     * Handle sync conflicts
     */
    async handleConflicts(type, conflicts) {
        this.log(`Handling ${conflicts.length} conflicts for ${type}`);

        for (const conflict of conflicts) {
            await this.handleSingleConflict(type, conflict.local, conflict.server);
        }
    }

    /**
     * Handle single conflict
     */
    async handleSingleConflict(type, localData, serverData) {
        let resolved;

        switch (this.config.conflictResolution) {
            case 'server-wins':
                resolved = serverData;
                break;

            case 'client-wins':
                resolved = localData;
                break;

            case 'newest-wins':
                const localTime = localData.modifiedAt || localData.updatedAt || 0;
                const serverTime = new Date(serverData.updated_at || serverData.updatedAt || 0).getTime();
                resolved = serverTime > localTime ? serverData : localData;
                break;

            default:
                // Emit event for manual resolution
                this.triggerEvent('onConflict', { type, local: localData, server: serverData });
                return;
        }

        // Save resolved data
        await this.db.put(type, {
            ...resolved,
            synced: true,
            syncedAt: Date.now()
        });
    }

    // ====================================
    // QUEUE OPERATIONS
    // ====================================

    /**
     * Add to sync queue
     */
    async queueForSync(type, data) {
        const queueItem = {
            type,
            data,
            timestamp: Date.now(),
            synced: false
        };

        await this.db.put('syncQueue', queueItem);
        this.state.pendingChanges++;

        // Trigger immediate sync if online
        if (navigator.onLine && !this.state.isSyncing) {
            this.syncAll();
        }
    }

    /**
     * Get pending sync count
     */
    async getPendingSyncCount() {
        try {
            const queue = await this.db.getAll('syncQueue');
            return queue.filter(item => !item.synced).length;
        } catch (error) {
            return 0;
        }
    }

    // ====================================
    // UTILITY METHODS
    // ====================================

    /**
     * Create batches from array
     */
    createBatches(array, batchSize) {
        const batches = [];
        for (let i = 0; i < array.length; i += batchSize) {
            batches.push(array.slice(i, i + batchSize));
        }
        return batches;
    }

    /**
     * Force sync
     */
    async forceSync() {
        this.state.lastSyncTime = null;
        await this.saveSyncMetadata();
        return this.syncAll();
    }

    /**
     * Get sync status
     */
    getSyncStatus() {
        return {
            isSyncing: this.state.isSyncing,
            lastSyncTime: this.state.lastSyncTime,
            pendingChanges: this.state.pendingChanges,
            syncProgress: this.state.syncProgress,
            errors: this.state.syncErrors
        };
    }

    /**
     * Clear sync data
     */
    async clearSyncData() {
        this.state.lastSyncTime = null;
        this.state.syncErrors = [];
        await this.db.clear('syncQueue');
        await this.saveSyncMetadata();
    }

    // ====================================
    // EVENTS
    // ====================================

    /**
     * Register event callback
     */
    on(event, callback) {
        if (this.callbacks[event]) {
            this.callbacks[event].push(callback);
        }
    }

    /**
     * Unregister event callback
     */
    off(event, callback) {
        if (this.callbacks[event]) {
            this.callbacks[event] = this.callbacks[event].filter(cb => cb !== callback);
        }
    }

    /**
     * Trigger event callbacks
     */
    triggerEvent(event, data = null) {
        if (this.callbacks[event]) {
            this.callbacks[event].forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    this.log('Event callback error:', error);
                }
            });
        }
    }

    /**
     * Log helper
     */
    log(...args) {
        if (this.config.debug) {
            console.log('[SyncManager]', ...args);
        }
    }
}

// ====================================
// SYNC STATUS UI COMPONENT
// ====================================

/**
 * SyncStatusUI - Visual indicator for sync status
 */
class SyncStatusUI {
    constructor(syncManager, containerId = 'sync-status') {
        this.syncManager = syncManager;
        this.containerId = containerId;
        this.container = null;

        this.init();
    }

    init() {
        this.createUI();
        this.bindEvents();
    }

    createUI() {
        // Check if container exists
        this.container = document.getElementById(this.containerId);
        
        if (!this.container) {
            // Create container
            this.container = document.createElement('div');
            this.container.id = this.containerId;
            this.container.className = 'sync-status-indicator';
            document.body.appendChild(this.container);
        }

        this.container.innerHTML = `
            <div class="sync-status-inner">
                <span class="sync-icon">
                    <i class="fas fa-sync-alt"></i>
                </span>
                <span class="sync-text">Đã đồng bộ</span>
            </div>
        `;

        // Add styles if not already present
        if (!document.getElementById('sync-status-styles')) {
            const styles = document.createElement('style');
            styles.id = 'sync-status-styles';
            styles.textContent = `
                .sync-status-indicator {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    padding: 8px 16px;
                    background: var(--bs-body-bg, #fff);
                    border: 1px solid var(--bs-border-color, #dee2e6);
                    border-radius: 20px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    z-index: 1000;
                    transition: all 0.3s ease;
                    cursor: pointer;
                }
                .sync-status-indicator:hover {
                    box-shadow: 0 4px 15px rgba(0,0,0,0.15);
                }
                .sync-status-inner {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }
                .sync-icon i {
                    font-size: 14px;
                    color: #28a745;
                }
                .sync-icon.syncing i {
                    animation: spin 1s linear infinite;
                    color: #F47C26;
                }
                .sync-icon.error i {
                    color: #dc3545;
                }
                .sync-icon.offline i {
                    color: #6c757d;
                }
                .sync-text {
                    font-size: 12px;
                    color: var(--bs-body-color, #333);
                }
                @keyframes spin {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
                .sync-status-indicator.hidden {
                    opacity: 0;
                    pointer-events: none;
                }
            `;
            document.head.appendChild(styles);
        }
    }

    bindEvents() {
        this.syncManager.on('onSyncStart', () => this.updateStatus('syncing'));
        this.syncManager.on('onSyncComplete', (result) => this.updateStatus(result.errors.length > 0 ? 'error' : 'synced'));
        this.syncManager.on('onSyncError', () => this.updateStatus('error'));
        this.syncManager.on('onSyncProgress', (progress) => this.updateProgress(progress));

        // Network status
        window.addEventListener('online', () => this.updateStatus('synced'));
        window.addEventListener('offline', () => this.updateStatus('offline'));

        // Click to force sync
        this.container.addEventListener('click', () => {
            if (navigator.onLine) {
                this.syncManager.forceSync();
            }
        });
    }

    updateStatus(status) {
        const icon = this.container.querySelector('.sync-icon');
        const text = this.container.querySelector('.sync-text');

        icon.className = 'sync-icon';

        switch (status) {
            case 'syncing':
                icon.classList.add('syncing');
                icon.innerHTML = '<i class="fas fa-sync-alt"></i>';
                text.textContent = 'Đang đồng bộ...';
                break;
            case 'synced':
                icon.innerHTML = '<i class="fas fa-check-circle"></i>';
                text.textContent = 'Đã đồng bộ';
                break;
            case 'error':
                icon.classList.add('error');
                icon.innerHTML = '<i class="fas fa-exclamation-circle"></i>';
                text.textContent = 'Lỗi đồng bộ';
                break;
            case 'offline':
                icon.classList.add('offline');
                icon.innerHTML = '<i class="fas fa-wifi-slash"></i>';
                text.textContent = 'Offline';
                break;
        }
    }

    updateProgress(progress) {
        const text = this.container.querySelector('.sync-text');
        text.textContent = `Đồng bộ ${progress}%`;
    }

    show() {
        this.container.classList.remove('hidden');
    }

    hide() {
        this.container.classList.add('hidden');
    }
}

// ====================================
// GLOBAL INSTANCE
// ====================================

let syncManager = null;
let syncStatusUI = null;

// Initialize after DB and API are ready
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        if (window.englishDB && window.api) {
            syncManager = new SyncManager(window.englishDB, window.api);
            window.syncManager = syncManager;

            // Initialize UI if user is authenticated
            if (window.api.isAuthenticated()) {
                syncStatusUI = new SyncStatusUI(syncManager);
            }
        }
    }, 1000); // Wait for other modules to initialize
});

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { SyncManager, SyncStatusUI };
}
