/* ====================================
   AUTH SERVICE MODULE
   English Learning Platform
   Phase 4: Backend Integration
   Created: 08/12/2025
   ==================================== */

/**
 * AuthService - Handles user authentication, session management, and user state
 */
class AuthService {
    constructor(apiService) {
        // ====================================
        // DEPENDENCIES
        // ====================================
        this.api = apiService || window.api;
        
        // ====================================
        // STATE
        // ====================================
        this.state = {
            user: null,
            isAuthenticated: false,
            isLoading: true,
            permissions: [],
            lastActivity: null
        };

        // ====================================
        // CONFIGURATION
        // ====================================
        this.config = {
            sessionTimeout: 30 * 60 * 1000, // 30 minutes
            activityCheckInterval: 60 * 1000, // 1 minute
            storageKey: 'auth_user',
            rememberMeKey: 'auth_remember',
            debug: true
        };

        // ====================================
        // EVENT CALLBACKS
        // ====================================
        this.callbacks = {
            onLogin: [],
            onLogout: [],
            onSessionExpired: [],
            onUserUpdated: []
        };

        // Initialize
        this.init();
    }

    // ====================================
    // INITIALIZATION
    // ====================================

    async init() {
        this.log('Initializing AuthService...');
        
        // Load user from storage
        this.loadUserFromStorage();
        
        // Verify token if exists
        if (this.api.isAuthenticated()) {
            await this.verifySession();
        } else {
            this.state.isLoading = false;
        }

        // Setup activity tracking
        this.setupActivityTracking();
        
        // Setup session timeout check
        this.startSessionTimeoutCheck();

        this.log('AuthService initialized');
    }

    // ====================================
    // AUTHENTICATION METHODS
    // ====================================

    /**
     * Login with email and password
     */
    async login(email, password, rememberMe = false) {
        this.log('Attempting login...');
        
        try {
            const response = await this.api.login(email, password);
            
            if (response.success) {
                this.state.user = response.data.user;
                this.state.isAuthenticated = true;
                this.state.permissions = response.data.permissions || [];
                this.state.lastActivity = Date.now();

                // Save remember me preference
                if (rememberMe) {
                    localStorage.setItem(this.config.rememberMeKey, 'true');
                }

                // Save user to storage
                this.saveUserToStorage();

                // Trigger callbacks
                this.triggerEvent('onLogin', this.state.user);

                this.log('Login successful');
                return { success: true, user: this.state.user };
            }

            return { success: false, error: response.data?.message || 'Đăng nhập thất bại' };
        } catch (error) {
            this.log('Login error:', error);
            return { 
                success: false, 
                error: error instanceof ApiError ? error.getUserMessage() : 'Đã xảy ra lỗi khi đăng nhập'
            };
        }
    }

    /**
     * Login with social provider
     */
    async socialLogin(provider, token) {
        this.log(`Attempting ${provider} login...`);
        
        try {
            const response = await this.api.post('/auth/social', {
                provider,
                token
            }, { skipAuth: true });

            if (response.success) {
                this.api.setTokens(
                    response.data.access_token,
                    response.data.refresh_token,
                    response.data.expires_in
                );

                this.state.user = response.data.user;
                this.state.isAuthenticated = true;
                this.state.permissions = response.data.permissions || [];
                
                this.saveUserToStorage();
                this.triggerEvent('onLogin', this.state.user);

                return { success: true, user: this.state.user };
            }

            return { success: false, error: 'Đăng nhập không thành công' };
        } catch (error) {
            return { 
                success: false, 
                error: error instanceof ApiError ? error.getUserMessage() : 'Đã xảy ra lỗi'
            };
        }
    }

    /**
     * Register new user
     */
    async register(userData) {
        this.log('Attempting registration...');
        
        try {
            // Validate input
            const validation = this.validateRegistration(userData);
            if (!validation.valid) {
                return { success: false, errors: validation.errors };
            }

            const response = await this.api.register(userData);

            if (response.success) {
                // Auto-login after registration if tokens provided
                if (response.data.access_token) {
                    this.api.setTokens(
                        response.data.access_token,
                        response.data.refresh_token,
                        response.data.expires_in
                    );

                    this.state.user = response.data.user;
                    this.state.isAuthenticated = true;
                    this.saveUserToStorage();
                    this.triggerEvent('onLogin', this.state.user);
                }

                return { success: true, user: response.data.user };
            }

            return { success: false, error: 'Đăng ký không thành công' };
        } catch (error) {
            this.log('Registration error:', error);
            
            // Handle validation errors from server
            if (error.status === 422 && error.data?.errors) {
                return { success: false, errors: error.data.errors };
            }

            return { 
                success: false, 
                error: error instanceof ApiError ? error.getUserMessage() : 'Đã xảy ra lỗi khi đăng ký'
            };
        }
    }

    /**
     * Logout user
     */
    async logout(everywhere = false) {
        this.log('Logging out...');
        
        try {
            if (everywhere) {
                await this.api.post('/auth/logout-all');
            } else {
                await this.api.logout();
            }
        } catch (error) {
            this.log('Logout API error:', error);
        }

        // Clear local state regardless of API result
        this.clearSession();
        this.triggerEvent('onLogout');

        return { success: true };
    }

    /**
     * Verify current session
     */
    async verifySession() {
        this.log('Verifying session...');
        this.state.isLoading = true;

        try {
            const response = await this.api.getProfile();
            
            if (response.success) {
                this.state.user = response.data;
                this.state.isAuthenticated = true;
                this.state.isLoading = false;
                this.saveUserToStorage();
                return true;
            }
        } catch (error) {
            this.log('Session verification failed:', error);
            
            if (error.isAuthError && error.isAuthError()) {
                this.clearSession();
                this.triggerEvent('onSessionExpired');
            }
        }

        this.state.isLoading = false;
        return false;
    }

    /**
     * Clear session data
     */
    clearSession() {
        this.state.user = null;
        this.state.isAuthenticated = false;
        this.state.permissions = [];
        this.api.clearTokens();
        localStorage.removeItem(this.config.storageKey);
        localStorage.removeItem(this.config.rememberMeKey);
    }

    // ====================================
    // PASSWORD MANAGEMENT
    // ====================================

    /**
     * Request password reset
     */
    async forgotPassword(email) {
        try {
            const response = await this.api.requestPasswordReset(email);
            return { 
                success: true, 
                message: 'Hướng dẫn đặt lại mật khẩu đã được gửi đến email của bạn' 
            };
        } catch (error) {
            // Don't reveal if email exists
            return { 
                success: true, 
                message: 'Nếu email tồn tại, bạn sẽ nhận được hướng dẫn đặt lại mật khẩu' 
            };
        }
    }

    /**
     * Reset password with token
     */
    async resetPassword(token, password, passwordConfirmation) {
        if (password !== passwordConfirmation) {
            return { success: false, error: 'Mật khẩu xác nhận không khớp' };
        }

        const validation = this.validatePassword(password);
        if (!validation.valid) {
            return { success: false, errors: { password: validation.errors } };
        }

        try {
            const response = await this.api.resetPassword(token, password);
            return { success: true, message: 'Mật khẩu đã được đặt lại thành công' };
        } catch (error) {
            return { 
                success: false, 
                error: error instanceof ApiError ? error.getUserMessage() : 'Đã xảy ra lỗi'
            };
        }
    }

    /**
     * Change password
     */
    async changePassword(currentPassword, newPassword, confirmPassword) {
        if (newPassword !== confirmPassword) {
            return { success: false, error: 'Mật khẩu xác nhận không khớp' };
        }

        const validation = this.validatePassword(newPassword);
        if (!validation.valid) {
            return { success: false, errors: { newPassword: validation.errors } };
        }

        try {
            const response = await this.api.post('/auth/change-password', {
                current_password: currentPassword,
                new_password: newPassword
            });
            return { success: true, message: 'Mật khẩu đã được thay đổi thành công' };
        } catch (error) {
            return { 
                success: false, 
                error: error instanceof ApiError ? error.getUserMessage() : 'Đã xảy ra lỗi'
            };
        }
    }

    // ====================================
    // EMAIL VERIFICATION
    // ====================================

    /**
     * Send verification email
     */
    async sendVerificationEmail() {
        try {
            await this.api.post('/auth/verify-email/send');
            return { success: true, message: 'Email xác thực đã được gửi' };
        } catch (error) {
            return { success: false, error: 'Không thể gửi email xác thực' };
        }
    }

    /**
     * Verify email with token
     */
    async verifyEmail(token) {
        try {
            const response = await this.api.post('/auth/verify-email', { token });
            
            if (response.success && this.state.user) {
                this.state.user.email_verified = true;
                this.saveUserToStorage();
                this.triggerEvent('onUserUpdated', this.state.user);
            }

            return { success: true, message: 'Email đã được xác thực thành công' };
        } catch (error) {
            return { success: false, error: 'Token không hợp lệ hoặc đã hết hạn' };
        }
    }

    // ====================================
    // USER PROFILE
    // ====================================

    /**
     * Get current user
     */
    getUser() {
        return this.state.user;
    }

    /**
     * Get user ID
     */
    getUserId() {
        return this.state.user?.id;
    }

    /**
     * Update user profile
     */
    async updateProfile(profileData) {
        try {
            const response = await this.api.updateProfile(profileData);
            
            if (response.success) {
                this.state.user = { ...this.state.user, ...response.data };
                this.saveUserToStorage();
                this.triggerEvent('onUserUpdated', this.state.user);
                return { success: true, user: this.state.user };
            }

            return { success: false, error: 'Cập nhật không thành công' };
        } catch (error) {
            return { 
                success: false, 
                error: error instanceof ApiError ? error.getUserMessage() : 'Đã xảy ra lỗi'
            };
        }
    }

    /**
     * Update user avatar
     */
    async updateAvatar(file) {
        if (!this.validateAvatarFile(file)) {
            return { success: false, error: 'File không hợp lệ. Vui lòng chọn ảnh JPG, PNG hoặc GIF dưới 5MB' };
        }

        try {
            const response = await this.api.uploadAvatar(file);
            
            if (response.success) {
                this.state.user.avatar = response.data.avatar_url;
                this.saveUserToStorage();
                this.triggerEvent('onUserUpdated', this.state.user);
                return { success: true, avatarUrl: response.data.avatar_url };
            }

            return { success: false, error: 'Upload không thành công' };
        } catch (error) {
            return { success: false, error: 'Đã xảy ra lỗi khi upload ảnh' };
        }
    }

    // ====================================
    // PERMISSIONS & AUTHORIZATION
    // ====================================

    /**
     * Check if user has permission
     */
    hasPermission(permission) {
        return this.state.permissions.includes(permission);
    }

    /**
     * Check if user has any of the permissions
     */
    hasAnyPermission(permissions) {
        return permissions.some(p => this.hasPermission(p));
    }

    /**
     * Check if user has all permissions
     */
    hasAllPermissions(permissions) {
        return permissions.every(p => this.hasPermission(p));
    }

    /**
     * Check if user has role
     */
    hasRole(role) {
        return this.state.user?.role === role;
    }

    /**
     * Check if user is admin
     */
    isAdmin() {
        return this.hasRole('admin') || this.hasRole('super_admin');
    }

    /**
     * Check if user is premium
     */
    isPremium() {
        return this.state.user?.subscription?.status === 'active';
    }

    // ====================================
    // SESSION MANAGEMENT
    // ====================================

    /**
     * Setup activity tracking
     */
    setupActivityTracking() {
        const events = ['mousedown', 'keydown', 'scroll', 'touchstart'];
        
        events.forEach(event => {
            document.addEventListener(event, () => {
                this.state.lastActivity = Date.now();
            }, { passive: true });
        });
    }

    /**
     * Start session timeout check
     */
    startSessionTimeoutCheck() {
        setInterval(() => {
            if (!this.state.isAuthenticated) return;
            
            const timeSinceActivity = Date.now() - this.state.lastActivity;
            const rememberMe = localStorage.getItem(this.config.rememberMeKey) === 'true';

            if (!rememberMe && timeSinceActivity > this.config.sessionTimeout) {
                this.log('Session timeout due to inactivity');
                this.logout();
                this.triggerEvent('onSessionExpired');
            }
        }, this.config.activityCheckInterval);
    }

    // ====================================
    // STORAGE
    // ====================================

    /**
     * Save user to local storage
     */
    saveUserToStorage() {
        if (this.state.user) {
            localStorage.setItem(this.config.storageKey, JSON.stringify(this.state.user));
        }
    }

    /**
     * Load user from storage
     */
    loadUserFromStorage() {
        try {
            const saved = localStorage.getItem(this.config.storageKey);
            if (saved) {
                this.state.user = JSON.parse(saved);
                this.state.isAuthenticated = this.api.isAuthenticated();
            }
        } catch (error) {
            this.log('Error loading user from storage:', error);
        }
    }

    // ====================================
    // VALIDATION
    // ====================================

    /**
     * Validate registration data
     */
    validateRegistration(data) {
        const errors = {};

        // Name validation
        if (!data.name || data.name.trim().length < 2) {
            errors.name = ['Tên phải có ít nhất 2 ký tự'];
        }

        // Email validation
        if (!data.email || !this.isValidEmail(data.email)) {
            errors.email = ['Email không hợp lệ'];
        }

        // Password validation
        const passwordValidation = this.validatePassword(data.password);
        if (!passwordValidation.valid) {
            errors.password = passwordValidation.errors;
        }

        // Password confirmation
        if (data.password !== data.password_confirmation) {
            errors.password_confirmation = ['Mật khẩu xác nhận không khớp'];
        }

        return {
            valid: Object.keys(errors).length === 0,
            errors
        };
    }

    /**
     * Validate password strength
     */
    validatePassword(password) {
        const errors = [];

        if (!password || password.length < 8) {
            errors.push('Mật khẩu phải có ít nhất 8 ký tự');
        }
        if (!/[A-Z]/.test(password)) {
            errors.push('Mật khẩu phải có ít nhất 1 chữ hoa');
        }
        if (!/[a-z]/.test(password)) {
            errors.push('Mật khẩu phải có ít nhất 1 chữ thường');
        }
        if (!/[0-9]/.test(password)) {
            errors.push('Mật khẩu phải có ít nhất 1 số');
        }

        return {
            valid: errors.length === 0,
            errors,
            strength: this.getPasswordStrength(password)
        };
    }

    /**
     * Get password strength score
     */
    getPasswordStrength(password) {
        if (!password) return 0;
        
        let score = 0;
        if (password.length >= 8) score += 1;
        if (password.length >= 12) score += 1;
        if (/[A-Z]/.test(password)) score += 1;
        if (/[a-z]/.test(password)) score += 1;
        if (/[0-9]/.test(password)) score += 1;
        if (/[^A-Za-z0-9]/.test(password)) score += 1;

        return Math.min(score, 5);
    }

    /**
     * Validate email format
     */
    isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    /**
     * Validate avatar file
     */
    validateAvatarFile(file) {
        const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
        const maxSize = 5 * 1024 * 1024; // 5MB

        return file && 
               allowedTypes.includes(file.type) && 
               file.size <= maxSize;
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

    // ====================================
    // UTILITY
    // ====================================

    /**
     * Check if authenticated
     */
    isAuthenticated() {
        return this.state.isAuthenticated && this.api.isAuthenticated();
    }

    /**
     * Check if loading
     */
    isLoading() {
        return this.state.isLoading;
    }

    /**
     * Log helper
     */
    log(...args) {
        if (this.config.debug) {
            console.log('[AuthService]', ...args);
        }
    }
}

// ====================================
// ROUTE GUARD MIXIN
// ====================================

/**
 * Route guard for protected pages
 */
const RouteGuard = {
    /**
     * Check if user can access current page
     */
    canAccess(authService, options = {}) {
        // Check authentication
        if (options.requireAuth && !authService.isAuthenticated()) {
            return { allowed: false, redirect: '/public/login.html' };
        }

        // Check if guest only
        if (options.guestOnly && authService.isAuthenticated()) {
            return { allowed: false, redirect: '/public/dashboard.html' };
        }

        // Check permissions
        if (options.permissions && options.permissions.length > 0) {
            if (!authService.hasAnyPermission(options.permissions)) {
                return { allowed: false, redirect: '/public/dashboard.html', reason: 'NO_PERMISSION' };
            }
        }

        // Check roles
        if (options.roles && options.roles.length > 0) {
            const hasRole = options.roles.some(role => authService.hasRole(role));
            if (!hasRole) {
                return { allowed: false, redirect: '/public/dashboard.html', reason: 'NO_ROLE' };
            }
        }

        // Check premium
        if (options.requirePremium && !authService.isPremium()) {
            return { allowed: false, redirect: '/public/pricing.html', reason: 'NOT_PREMIUM' };
        }

        // Check email verification
        if (options.requireVerified && !authService.getUser()?.email_verified) {
            return { allowed: false, redirect: '/public/verify-email.html', reason: 'NOT_VERIFIED' };
        }

        return { allowed: true };
    },

    /**
     * Protect page on load
     */
    protect(authService, options = {}) {
        const result = this.canAccess(authService, options);
        
        if (!result.allowed && result.redirect) {
            window.location.href = result.redirect;
            return false;
        }

        return true;
    }
};

// ====================================
// GLOBAL INSTANCE
// ====================================

let auth = null;

// Initialize after API is ready
document.addEventListener('DOMContentLoaded', () => {
    if (window.api) {
        auth = new AuthService(window.api);
        window.auth = auth;
    }
});

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AuthService, RouteGuard };
}
