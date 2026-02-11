/* ====================================
   API SERVICE MODULE
   English Learning Platform
   Phase 4: Backend Integration
   Created: 08/12/2025
   ==================================== */

/**
 * ApiService - Centralized API communication layer
 * Handles all HTTP requests with error handling, retry logic, and caching
 */
class ApiService {
    constructor(options = {}) {
        // ====================================
        // CONFIGURATION
        // ====================================
        this.config = {
            baseUrl: options.baseUrl || '/api/v1',
            timeout: options.timeout || 30000,
            retryAttempts: options.retryAttempts || 3,
            retryDelay: options.retryDelay || 1000,
            cacheEnabled: options.cacheEnabled !== false,
            cacheDuration: options.cacheDuration || 5 * 60 * 1000, // 5 minutes
            debug: options.debug || false
        };

        // ====================================
        // STATE
        // ====================================
        this.state = {
            isOnline: navigator.onLine,
            pendingRequests: new Map(),
            cache: new Map(),
            requestQueue: []
        };

        // ====================================
        // AUTH TOKEN
        // ====================================
        this.authToken = null;
        this.refreshToken = null;
        this.tokenExpiry = null;

        // Setup event listeners
        this.setupEventListeners();
        
        this.log('ApiService initialized');
    }

    // ====================================
    // SETUP
    // ====================================

    setupEventListeners() {
        // Online/Offline detection
        window.addEventListener('online', () => {
            this.state.isOnline = true;
            this.log('Network online - processing queued requests');
            this.processRequestQueue();
        });

        window.addEventListener('offline', () => {
            this.state.isOnline = false;
            this.log('Network offline - requests will be queued');
        });
    }

    // ====================================
    // AUTHENTICATION
    // ====================================

    /**
     * Set authentication tokens
     */
    setTokens(accessToken, refreshToken = null, expiresIn = 3600) {
        this.authToken = accessToken;
        this.refreshToken = refreshToken;
        this.tokenExpiry = Date.now() + (expiresIn * 1000);
        
        // Store in localStorage for persistence
        if (accessToken) {
            localStorage.setItem('auth_token', accessToken);
            localStorage.setItem('token_expiry', this.tokenExpiry.toString());
        }
        if (refreshToken) {
            localStorage.setItem('refresh_token', refreshToken);
        }
        
        this.log('Tokens updated');
    }

    /**
     * Load tokens from localStorage
     */
    loadTokens() {
        this.authToken = localStorage.getItem('auth_token');
        this.refreshToken = localStorage.getItem('refresh_token');
        this.tokenExpiry = parseInt(localStorage.getItem('token_expiry')) || null;
        
        // Check if token is expired
        if (this.tokenExpiry && Date.now() > this.tokenExpiry) {
            this.log('Token expired, attempting refresh');
            return this.refreshAuthToken();
        }
        
        return Promise.resolve(!!this.authToken);
    }

    /**
     * Clear authentication
     */
    clearTokens() {
        this.authToken = null;
        this.refreshToken = null;
        this.tokenExpiry = null;
        localStorage.removeItem('auth_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('token_expiry');
        this.log('Tokens cleared');
    }

    /**
     * Refresh authentication token
     */
    async refreshAuthToken() {
        if (!this.refreshToken) {
            this.clearTokens();
            return false;
        }

        try {
            const response = await this.post('/auth/refresh', {
                refresh_token: this.refreshToken
            }, { skipAuth: true });

            if (response.success) {
                this.setTokens(
                    response.data.access_token,
                    response.data.refresh_token,
                    response.data.expires_in
                );
                return true;
            }
        } catch (error) {
            this.log('Token refresh failed:', error);
        }

        this.clearTokens();
        return false;
    }

    /**
     * Check if authenticated
     */
    isAuthenticated() {
        return !!this.authToken && (!this.tokenExpiry || Date.now() < this.tokenExpiry);
    }

    // ====================================
    // CORE HTTP METHODS
    // ====================================

    /**
     * GET request
     */
    async get(endpoint, options = {}) {
        return this.request('GET', endpoint, null, options);
    }

    /**
     * POST request
     */
    async post(endpoint, data, options = {}) {
        return this.request('POST', endpoint, data, options);
    }

    /**
     * PUT request
     */
    async put(endpoint, data, options = {}) {
        return this.request('PUT', endpoint, data, options);
    }

    /**
     * PATCH request
     */
    async patch(endpoint, data, options = {}) {
        return this.request('PATCH', endpoint, data, options);
    }

    /**
     * DELETE request
     */
    async delete(endpoint, options = {}) {
        return this.request('DELETE', endpoint, null, options);
    }

    // ====================================
    // MAIN REQUEST HANDLER
    // ====================================

    /**
     * Main request method with retry and error handling
     */
    async request(method, endpoint, data = null, options = {}) {
        const url = this.buildUrl(endpoint, options.params);
        const cacheKey = `${method}:${url}`;

        // Check cache for GET requests
        if (method === 'GET' && this.config.cacheEnabled && !options.skipCache) {
            const cached = this.getFromCache(cacheKey);
            if (cached) {
                this.log(`Cache hit: ${cacheKey}`);
                return cached;
            }
        }

        // Check if offline
        if (!this.state.isOnline && !options.forceOnline) {
            if (options.queueIfOffline !== false) {
                return this.queueRequest(method, endpoint, data, options);
            }
            throw new ApiError('OFFLINE', 'Không có kết nối mạng', 0);
        }

        // Build request configuration
        const requestConfig = this.buildRequestConfig(method, data, options);

        // Execute request with retry logic
        let lastError;
        const maxAttempts = options.retryAttempts || this.config.retryAttempts;

        for (let attempt = 1; attempt <= maxAttempts; attempt++) {
            try {
                const response = await this.executeRequest(url, requestConfig, options);
                
                // Cache successful GET responses
                if (method === 'GET' && this.config.cacheEnabled && !options.skipCache) {
                    this.addToCache(cacheKey, response, options.cacheDuration);
                }

                return response;
            } catch (error) {
                lastError = error;
                
                // Don't retry on certain errors
                if (this.shouldNotRetry(error)) {
                    throw error;
                }

                // Wait before retrying
                if (attempt < maxAttempts) {
                    const delay = this.config.retryDelay * Math.pow(2, attempt - 1);
                    this.log(`Retry attempt ${attempt}/${maxAttempts} in ${delay}ms`);
                    await this.sleep(delay);
                }
            }
        }

        throw lastError;
    }

    /**
     * Build full URL with query parameters
     */
    buildUrl(endpoint, params = {}) {
        let url = endpoint.startsWith('http') 
            ? endpoint 
            : `${this.config.baseUrl}${endpoint}`;

        if (Object.keys(params).length > 0) {
            const queryString = new URLSearchParams(params).toString();
            url += `?${queryString}`;
        }

        return url;
    }

    /**
     * Build request configuration
     */
    buildRequestConfig(method, data, options) {
        const config = {
            method,
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                ...options.headers
            }
        };

        // Add auth token
        if (!options.skipAuth && this.authToken) {
            config.headers['Authorization'] = `Bearer ${this.authToken}`;
        }

        // Add body for non-GET requests
        if (data && method !== 'GET') {
            config.body = JSON.stringify(data);
        }

        return config;
    }

    /**
     * Execute the actual fetch request
     */
    async executeRequest(url, config, options) {
        const controller = new AbortController();
        const timeout = options.timeout || this.config.timeout;
        
        const timeoutId = setTimeout(() => controller.abort(), timeout);
        config.signal = controller.signal;

        try {
            this.log(`${config.method} ${url}`);
            const response = await fetch(url, config);
            clearTimeout(timeoutId);

            // Handle token expiry
            if (response.status === 401 && !options.skipAuth) {
                const refreshed = await this.refreshAuthToken();
                if (refreshed) {
                    // Retry with new token
                    config.headers['Authorization'] = `Bearer ${this.authToken}`;
                    const retryResponse = await fetch(url, config);
                    return this.handleResponse(retryResponse);
                }
                throw new ApiError('UNAUTHORIZED', 'Phiên đăng nhập hết hạn', 401);
            }

            return this.handleResponse(response);
        } catch (error) {
            clearTimeout(timeoutId);
            
            if (error.name === 'AbortError') {
                throw new ApiError('TIMEOUT', 'Yêu cầu quá thời gian chờ', 408);
            }
            
            throw error;
        }
    }

    /**
     * Handle API response
     */
    async handleResponse(response) {
        const contentType = response.headers.get('content-type');
        let data;

        if (contentType && contentType.includes('application/json')) {
            data = await response.json();
        } else {
            data = await response.text();
        }

        if (!response.ok) {
            throw new ApiError(
                data.code || 'ERROR',
                data.message || 'Đã xảy ra lỗi',
                response.status,
                data
            );
        }

        return {
            success: true,
            data: data.data || data,
            meta: data.meta || {},
            status: response.status
        };
    }

    /**
     * Check if error should not be retried
     */
    shouldNotRetry(error) {
        const noRetryStatuses = [400, 401, 403, 404, 422];
        return error instanceof ApiError && noRetryStatuses.includes(error.status);
    }

    // ====================================
    // CACHE MANAGEMENT
    // ====================================

    /**
     * Get from cache
     */
    getFromCache(key) {
        const cached = this.state.cache.get(key);
        if (!cached) return null;
        
        if (Date.now() > cached.expiry) {
            this.state.cache.delete(key);
            return null;
        }
        
        return cached.data;
    }

    /**
     * Add to cache
     */
    addToCache(key, data, duration) {
        const expiry = Date.now() + (duration || this.config.cacheDuration);
        this.state.cache.set(key, { data, expiry });
        
        // Limit cache size
        if (this.state.cache.size > 100) {
            const firstKey = this.state.cache.keys().next().value;
            this.state.cache.delete(firstKey);
        }
    }

    /**
     * Clear cache
     */
    clearCache(pattern = null) {
        if (pattern) {
            for (const key of this.state.cache.keys()) {
                if (key.includes(pattern)) {
                    this.state.cache.delete(key);
                }
            }
        } else {
            this.state.cache.clear();
        }
    }

    // ====================================
    // OFFLINE QUEUE
    // ====================================

    /**
     * Queue request for later execution
     */
    queueRequest(method, endpoint, data, options) {
        const queueItem = {
            id: Date.now() + Math.random().toString(36),
            method,
            endpoint,
            data,
            options,
            timestamp: Date.now()
        };

        this.state.requestQueue.push(queueItem);
        this.saveQueueToStorage();

        this.log(`Request queued: ${method} ${endpoint}`);

        return {
            success: false,
            queued: true,
            queueId: queueItem.id,
            message: 'Yêu cầu đã được lưu để gửi khi có kết nối mạng'
        };
    }

    /**
     * Process queued requests when online
     */
    async processRequestQueue() {
        if (!this.state.isOnline || this.state.requestQueue.length === 0) {
            return;
        }

        this.log(`Processing ${this.state.requestQueue.length} queued requests`);

        const queue = [...this.state.requestQueue];
        this.state.requestQueue = [];

        const results = [];

        for (const item of queue) {
            try {
                const result = await this.request(
                    item.method,
                    item.endpoint,
                    item.data,
                    { ...item.options, queueIfOffline: false }
                );
                results.push({ id: item.id, success: true, data: result });
            } catch (error) {
                results.push({ id: item.id, success: false, error });
                // Re-queue failed requests that are retryable
                if (!this.shouldNotRetry(error)) {
                    this.state.requestQueue.push(item);
                }
            }
        }

        this.saveQueueToStorage();

        // Emit event for queue processing complete
        window.dispatchEvent(new CustomEvent('api:queue-processed', { detail: results }));

        return results;
    }

    /**
     * Save queue to localStorage
     */
    saveQueueToStorage() {
        localStorage.setItem('api_request_queue', JSON.stringify(this.state.requestQueue));
    }

    /**
     * Load queue from localStorage
     */
    loadQueueFromStorage() {
        try {
            const saved = localStorage.getItem('api_request_queue');
            if (saved) {
                this.state.requestQueue = JSON.parse(saved);
            }
        } catch (error) {
            this.log('Error loading queue from storage:', error);
        }
    }

    // ====================================
    // API ENDPOINTS - AUTH
    // ====================================

    /**
     * Login user
     */
    async login(email, password) {
        const response = await this.post('/auth/login', { email, password }, { skipAuth: true });
        if (response.success) {
            this.setTokens(
                response.data.access_token,
                response.data.refresh_token,
                response.data.expires_in
            );
        }
        return response;
    }

    /**
     * Register user
     */
    async register(userData) {
        return this.post('/auth/register', userData, { skipAuth: true });
    }

    /**
     * Logout user
     */
    async logout() {
        try {
            await this.post('/auth/logout');
        } finally {
            this.clearTokens();
        }
    }

    /**
     * Request password reset
     */
    async requestPasswordReset(email) {
        return this.post('/auth/forgot-password', { email }, { skipAuth: true });
    }

    /**
     * Reset password
     */
    async resetPassword(token, password) {
        return this.post('/auth/reset-password', { token, password }, { skipAuth: true });
    }

    // ====================================
    // API ENDPOINTS - USER
    // ====================================

    /**
     * Get current user profile
     */
    async getProfile() {
        return this.get('/user/profile');
    }

    /**
     * Update user profile
     */
    async updateProfile(data) {
        return this.put('/user/profile', data);
    }

    /**
     * Upload avatar
     */
    async uploadAvatar(file) {
        const formData = new FormData();
        formData.append('avatar', file);
        
        return this.request('POST', '/user/avatar', null, {
            headers: {
                'Content-Type': 'multipart/form-data'
            },
            body: formData
        });
    }

    /**
     * Get user settings
     */
    async getSettings() {
        return this.get('/user/settings');
    }

    /**
     * Update user settings
     */
    async updateSettings(settings) {
        return this.put('/user/settings', settings);
    }

    // ====================================
    // API ENDPOINTS - LEARNING
    // ====================================

    /**
     * Get lessons list
     */
    async getLessons(params = {}) {
        return this.get('/lessons', { params });
    }

    /**
     * Get single lesson
     */
    async getLesson(lessonId) {
        return this.get(`/lessons/${lessonId}`);
    }

    /**
     * Get lesson content (for offline use)
     */
    async getLessonContent(lessonId) {
        return this.get(`/lessons/${lessonId}/content`);
    }

    /**
     * Update lesson progress
     */
    async updateLessonProgress(lessonId, progress) {
        return this.put(`/lessons/${lessonId}/progress`, progress);
    }

    /**
     * Complete lesson
     */
    async completeLesson(lessonId, data) {
        return this.post(`/lessons/${lessonId}/complete`, data);
    }

    // ====================================
    // API ENDPOINTS - FLASHCARDS
    // ====================================

    /**
     * Get flashcard decks
     */
    async getFlashcardDecks(params = {}) {
        return this.get('/flashcards/decks', { params });
    }

    /**
     * Get flashcards for review
     */
    async getFlashcardsForReview(deckId = null) {
        const endpoint = deckId 
            ? `/flashcards/decks/${deckId}/review`
            : '/flashcards/review';
        return this.get(endpoint);
    }

    /**
     * Submit flashcard review
     */
    async submitFlashcardReview(cardId, result) {
        return this.post(`/flashcards/${cardId}/review`, result);
    }

    /**
     * Batch sync flashcard progress
     */
    async syncFlashcardProgress(progressData) {
        return this.post('/flashcards/sync', { progress: progressData });
    }

    // ====================================
    // API ENDPOINTS - PRACTICE
    // ====================================

    /**
     * Get practice exercises
     */
    async getPracticeExercises(type, params = {}) {
        return this.get(`/practice/${type}`, { params });
    }

    /**
     * Submit practice result
     */
    async submitPracticeResult(type, result) {
        return this.post(`/practice/${type}/submit`, result);
    }

    /**
     * Get dictation exercises
     */
    async getDictationExercises(params = {}) {
        return this.getPracticeExercises('dictation', params);
    }

    /**
     * Submit dictation result
     */
    async submitDictationResult(result) {
        return this.submitPracticeResult('dictation', result);
    }

    /**
     * Get writing prompts
     */
    async getWritingPrompts(params = {}) {
        return this.getPracticeExercises('writing', params);
    }

    /**
     * Submit writing for analysis
     */
    async submitWriting(data) {
        return this.submitPracticeResult('writing', data);
    }

    /**
     * Get quiz questions
     */
    async getQuizQuestions(params = {}) {
        return this.getPracticeExercises('quiz', params);
    }

    /**
     * Submit quiz result
     */
    async submitQuizResult(result) {
        return this.submitPracticeResult('quiz', result);
    }

    // ====================================
    // API ENDPOINTS - PROGRESS & STATS
    // ====================================

    /**
     * Get user progress overview
     */
    async getProgressOverview() {
        return this.get('/progress/overview');
    }

    /**
     * Get detailed progress
     */
    async getDetailedProgress(params = {}) {
        return this.get('/progress/detailed', { params });
    }

    /**
     * Get skill breakdown
     */
    async getSkillBreakdown() {
        return this.get('/progress/skills');
    }

    /**
     * Get learning streak
     */
    async getLearningStreak() {
        return this.get('/progress/streak');
    }

    /**
     * Get achievements
     */
    async getAchievements() {
        return this.get('/achievements');
    }

    /**
     * Get leaderboard
     */
    async getLeaderboard(params = {}) {
        return this.get('/leaderboard', { params });
    }

    // ====================================
    // API ENDPOINTS - VOCABULARY
    // ====================================

    /**
     * Get vocabulary list
     */
    async getVocabularyList(params = {}) {
        return this.get('/vocabulary', { params });
    }

    /**
     * Add word to vocabulary
     */
    async addVocabulary(word) {
        return this.post('/vocabulary', word);
    }

    /**
     * Update vocabulary item
     */
    async updateVocabulary(wordId, data) {
        return this.put(`/vocabulary/${wordId}`, data);
    }

    /**
     * Delete vocabulary item
     */
    async deleteVocabulary(wordId) {
        return this.delete(`/vocabulary/${wordId}`);
    }

    // ====================================
    // API ENDPOINTS - NOTIFICATIONS
    // ====================================

    /**
     * Get notifications
     */
    async getNotifications(params = {}) {
        return this.get('/notifications', { params });
    }

    /**
     * Mark notification as read
     */
    async markNotificationRead(notificationId) {
        return this.put(`/notifications/${notificationId}/read`);
    }

    /**
     * Mark all notifications as read
     */
    async markAllNotificationsRead() {
        return this.put('/notifications/read-all');
    }

    // ====================================
    // UTILITY METHODS
    // ====================================

    /**
     * Sleep helper
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Log helper
     */
    log(...args) {
        if (this.config.debug) {
            console.log('[ApiService]', ...args);
        }
    }
}

// ====================================
// API ERROR CLASS
// ====================================

class ApiError extends Error {
    constructor(code, message, status, data = null) {
        super(message);
        this.name = 'ApiError';
        this.code = code;
        this.status = status;
        this.data = data;
    }

    /**
     * Check if error is network related
     */
    isNetworkError() {
        return this.code === 'OFFLINE' || this.code === 'TIMEOUT';
    }

    /**
     * Check if error is authentication related
     */
    isAuthError() {
        return this.code === 'UNAUTHORIZED' || this.status === 401;
    }

    /**
     * Get user-friendly message
     */
    getUserMessage() {
        const messages = {
            'OFFLINE': 'Không có kết nối mạng. Vui lòng kiểm tra kết nối.',
            'TIMEOUT': 'Yêu cầu quá thời gian chờ. Vui lòng thử lại.',
            'UNAUTHORIZED': 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.',
            'FORBIDDEN': 'Bạn không có quyền thực hiện hành động này.',
            'NOT_FOUND': 'Không tìm thấy tài nguyên yêu cầu.',
            'VALIDATION_ERROR': 'Dữ liệu không hợp lệ. Vui lòng kiểm tra lại.',
            'SERVER_ERROR': 'Lỗi máy chủ. Vui lòng thử lại sau.'
        };

        return messages[this.code] || this.message;
    }
}

// ====================================
// GLOBAL INSTANCE
// ====================================

// Create global API instance
const api = new ApiService({
    baseUrl: '/api/v1',
    debug: true
});

// Load tokens on startup
api.loadTokens();

// Load queued requests
api.loadQueueFromStorage();

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ApiService, ApiError, api };
}
