/* ====================================
   DJANGO API SERVICE
   English Learning Platform
   Backend Integration with Django REST Framework + JWT
   ==================================== */

/**
 * DjangoApiService - Handles API communication with Django backend
 * Uses JWT for authentication
 */
class DjangoApiService {
    constructor() {
        this.config = window.AppConfig || {
            api: { baseUrl: 'http://127.0.0.1:8000/api/v1', timeout: 30000 },
            debug: true
        };
        
        this.baseUrl = this.config.api.baseUrl;
        this.timeout = this.config.api.timeout;
        
        // Token storage
        this.accessToken = localStorage.getItem('access_token');
        this.refreshToken = localStorage.getItem('refresh_token');
        
        this.log('DjangoApiService initialized');
    }
    
    // ====================================
    // LOGGING
    // ====================================
    
    log(...args) {
        if (this.config.debug) {
            console.log('[DjangoAPI]', ...args);
        }
    }
    
    error(...args) {
        console.error('[DjangoAPI Error]', ...args);
    }
    
    // ====================================
    // TOKEN MANAGEMENT
    // ====================================
    
    setTokens(access, refresh) {
        this.accessToken = access;
        this.refreshToken = refresh;
        localStorage.setItem('access_token', access);
        if (refresh) {
            localStorage.setItem('refresh_token', refresh);
        }
        this.log('Tokens saved');
    }
    
    clearTokens() {
        this.accessToken = null;
        this.refreshToken = null;
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_data');
        this.log('Tokens cleared');
    }
    
    isAuthenticated() {
        return !!this.accessToken;
    }
    
    // ====================================
    // HTTP REQUEST METHODS
    // ====================================
    
    async request(method, endpoint, data = null, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        // Add auth header if token exists and not skipping auth
        if (this.accessToken && !options.skipAuth) {
            headers['Authorization'] = `Bearer ${this.accessToken}`;
        }
        
        const fetchOptions = {
            method,
            headers,
            mode: 'cors'
        };
        
        if (data && method !== 'GET') {
            fetchOptions.body = JSON.stringify(data);
        }
        
        this.log(`${method} ${url}`, data ? { data } : '');
        
        try {
            const response = await fetch(url, fetchOptions);
            const responseData = await this.parseResponse(response);
            
            // Handle 401 - try to refresh token
            if (response.status === 401 && !options.skipAuth && !options.isRetry) {
                this.log('Token expired, attempting refresh...');
                const refreshed = await this.refreshAccessToken();
                if (refreshed) {
                    // Retry original request
                    return this.request(method, endpoint, data, { ...options, isRetry: true });
                } else {
                    // Refresh failed - redirect to login
                    this.clearTokens();
                    window.location.href = '/public/login.html';
                    return { success: false, error: 'Session expired' };
                }
            }
            
            if (!response.ok) {
                return {
                    success: false,
                    status: response.status,
                    error: responseData.detail || responseData.error || 'Request failed',
                    data: responseData
                };
            }
            
            return {
                success: true,
                status: response.status,
                data: responseData
            };
            
        } catch (error) {
            this.error('Request failed:', error);
            return {
                success: false,
                error: error.message || 'Network error'
            };
        }
    }
    
    async parseResponse(response) {
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return response.json();
        }
        return response.text();
    }
    
    // HTTP method shortcuts
    async get(endpoint, options = {}) {
        return this.request('GET', endpoint, null, options);
    }
    
    async post(endpoint, data, options = {}) {
        return this.request('POST', endpoint, data, options);
    }
    
    async put(endpoint, data, options = {}) {
        return this.request('PUT', endpoint, data, options);
    }
    
    async patch(endpoint, data, options = {}) {
        return this.request('PATCH', endpoint, data, options);
    }
    
    async delete(endpoint, options = {}) {
        return this.request('DELETE', endpoint, null, options);
    }
    
    // ====================================
    // AUTHENTICATION
    // ====================================
    
    /**
     * Login with email/username and password
     * Uses Django SimpleJWT /auth/token/ endpoint
     */
    async login(email, password) {
        this.log('Attempting login for:', email);
        
        const response = await this.post('/auth/token/', {
            email: email,
            password: password
        }, { skipAuth: true });
        
        if (response.success) {
            const { access, refresh, user } = response.data;
            this.setTokens(access, refresh);
            
            // Store user data
            if (user) {
                localStorage.setItem('user_data', JSON.stringify(user));
            }
            
            // Return in consistent format
            return {
                success: true,
                data: {
                    user: user,
                    access_token: access,
                    refresh_token: refresh
                }
            };
        }
        
        return {
            success: false,
            error: response.error || 'Invalid credentials'
        };
    }
    
    /**
     * Register new user
     */
    async register(userData) {
        this.log('Attempting registration for:', userData.email);
        
        const response = await this.post('/auth/register/', userData, { skipAuth: true });
        
        if (response.success) {
            // Auto-login after registration if tokens returned
            if (response.data.tokens) {
                this.setTokens(response.data.tokens.access, response.data.tokens.refresh);
            }
        }
        
        return response;
    }
    
    /**
     * Refresh access token using refresh token
     */
    async refreshAccessToken() {
        if (!this.refreshToken) {
            this.log('No refresh token available');
            return false;
        }
        
        try {
            const response = await this.post('/auth/token/refresh/', {
                refresh: this.refreshToken
            }, { skipAuth: true });
            
            if (response.success) {
                this.accessToken = response.data.access;
                localStorage.setItem('access_token', this.accessToken);
                this.log('Token refreshed successfully');
                return true;
            }
        } catch (error) {
            this.error('Token refresh failed:', error);
        }
        
        return false;
    }
    
    /**
     * Logout - blacklist current token
     */
    async logout() {
        try {
            // Call logout endpoint to blacklist token
            await this.post('/auth/logout/', {
                refresh: this.refreshToken
            });
        } catch (error) {
            this.error('Logout API call failed:', error);
        }
        
        this.clearTokens();
        return { success: true };
    }
    
    // ====================================
    // SOCIAL AUTH (Google, Facebook)
    // ====================================
    
    /**
     * Login with Google OAuth2
     * @param {string} accessToken - Google OAuth2 access token
     */
    async loginWithGoogle(accessToken) {
        this.log('Attempting Google login...');
        
        const response = await this.post('/auth/google/', {
            access_token: accessToken
        }, { skipAuth: true });
        
        if (response.success) {
            const { access, refresh, user, created } = response.data;
            this.setTokens(access, refresh);
            
            // Store user data
            if (user) {
                localStorage.setItem('user_data', JSON.stringify(user));
            }
            
            this.log(created ? 'New user created via Google' : 'Existing user logged in via Google');
            
            return {
                success: true,
                data: {
                    user: user,
                    access_token: access,
                    refresh_token: refresh,
                    created: created
                }
            };
        }
        
        return {
            success: false,
            error: response.error || 'Google authentication failed'
        };
    }
    
    /**
     * Login with Facebook OAuth2
     * @param {string} accessToken - Facebook access token
     */
    async loginWithFacebook(accessToken) {
        this.log('Attempting Facebook login...');
        
        const response = await this.post('/auth/facebook/', {
            access_token: accessToken
        }, { skipAuth: true });
        
        if (response.success) {
            const { access, refresh, user, created } = response.data;
            this.setTokens(access, refresh);
            
            // Store user data
            if (user) {
                localStorage.setItem('user_data', JSON.stringify(user));
            }
            
            this.log(created ? 'New user created via Facebook' : 'Existing user logged in via Facebook');
            
            return {
                success: true,
                data: {
                    user: user,
                    access_token: access,
                    refresh_token: refresh,
                    created: created
                }
            };
        }
        
        return {
            success: false,
            error: response.error || 'Facebook authentication failed'
        };
    }
    
    // ====================================
    // USER PROFILE
    // ====================================
    
    /**
     * Get current user profile
     */
    async getProfile() {
        return this.get('/users/me/');
    }
    
    /**
     * Update user profile
     */
    async updateProfile(data) {
        return this.patch('/users/me/', data);
    }
    
    /**
     * Get user settings
     */
    async getSettings() {
        return this.get('/users/me/settings/');
    }
    
    /**
     * Update user settings
     */
    async updateSettings(settings) {
        return this.patch('/users/me/settings/', settings);
    }
    
    // ====================================
    // PASSWORD RESET
    // ====================================
    
    async requestPasswordReset(email) {
        return this.post('/auth/password/reset/', { email }, { skipAuth: true });
    }
    
    async confirmPasswordReset(uid, token, newPassword) {
        return this.post('/auth/password/reset/confirm/', {
            uid, token,
            new_password: newPassword,
            re_new_password: newPassword
        }, { skipAuth: true });
    }
    
    // ====================================
    // COURSES & LESSONS
    // ====================================
    
    async getCourses(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.get(`/courses/${queryString ? '?' + queryString : ''}`);
    }
    
    async getCourse(id) {
        return this.get(`/courses/${id}/`);
    }
    
    async getLessons(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.get(`/lessons/${queryString ? '?' + queryString : ''}`);
    }
    
    async getLesson(id) {
        return this.get(`/lessons/${id}/`);
    }
    
    // ====================================
    // STUDY PROGRESS
    // ====================================
    
    async getProgress() {
        return this.get('/progress/');
    }
    
    async updateProgress(data) {
        return this.post('/progress/', data);
    }
    
    // ====================================
    // FLASHCARDS
    // ====================================
    
    async getFlashcards(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.get(`/flashcards/${queryString ? '?' + queryString : ''}`);
    }
    
    async getDueFlashcards() {
        return this.get('/flashcards/due/');
    }
    
    async reviewFlashcard(id, quality) {
        return this.post(`/flashcards/${id}/review/`, { quality });
    }
    
    // ====================================
    // ACHIEVEMENTS
    // ====================================
    
    async getAchievements() {
        return this.get('/achievements/');
    }
    
    async getUserAchievements() {
        return this.get('/users/me/achievements/');
    }
}

// Create and expose global instance
window.djangoApi = new DjangoApiService();

// Also expose as window.api for compatibility with existing code
// Only if not using mock API
if (window.AppConfig && !window.AppConfig.api.useMockApi) {
    window.api = window.djangoApi;
}
