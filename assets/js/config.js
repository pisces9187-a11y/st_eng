/* ====================================
   APP CONFIGURATION
   English Learning Platform
   Backend Integration Config
   ==================================== */

/**
 * AppConfig - Application configuration for API connections
 */
const AppConfig = {
    // ====================================
    // API SETTINGS
    // ====================================
    api: {
        // Switch between mock and real backend
        useMockApi: false, // Set to true for development without backend
        
        // Django Backend URL
        baseUrl: 'http://127.0.0.1:8000/api/v1',
        
        // Timeout settings
        timeout: 30000,
        
        // Retry settings
        retryAttempts: 3,
        retryDelay: 1000
    },
    
    // ====================================
    // AUTH ENDPOINTS (Django JWT)
    // ====================================
    endpoints: {
        // Auth
        login: '/auth/token/',           // POST - Get JWT tokens
        tokenRefresh: '/auth/token/refresh/',  // POST - Refresh access token
        register: '/auth/register/',     // POST - User registration
        logout: '/auth/logout/',         // POST - Logout (blacklist token)
        
        // Social Auth
        googleAuth: '/auth/google/',     // POST - Google OAuth2 login
        facebookAuth: '/auth/facebook/', // POST - Facebook OAuth2 login
        
        // Password Reset
        passwordReset: '/auth/password/reset/',
        passwordResetConfirm: '/auth/password/reset/confirm/',
        
        // User Profile
        profile: '/users/me/',
        profileUpdate: '/users/me/',
        settings: '/users/settings/',
        
        // Courses & Lessons
        courses: '/courses/',
        lessons: '/lessons/',
        
        // Study Progress
        progress: '/progress/',
        flashcards: '/flashcards/',
        vocabulary: '/vocabulary/',
        
        // Achievements
        achievements: '/achievements/'
    },
    
    // ====================================
    // SOCIAL AUTH CONFIG
    // ====================================
    socialAuth: {
        // Google OAuth2
        // Lấy Client ID từ: https://console.cloud.google.com/apis/credentials
        google: {
            clientId: 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com',
            scope: 'openid email profile',
            redirectUri: 'http://localhost:3000/public/login.html'
        },
        
        // Facebook OAuth2
        // Lấy App ID từ: https://developers.facebook.com/apps/
        facebook: {
            appId: 'YOUR_FACEBOOK_APP_ID',
            scope: 'email,public_profile',
            version: 'v18.0',
            redirectUri: 'http://localhost:3000/public/login.html'
        }
    },
    
    // ====================================
    // JWT CONFIG
    // ====================================
    jwt: {
        accessTokenKey: 'access_token',
        refreshTokenKey: 'refresh_token',
        tokenExpiryKey: 'token_expiry',
        userDataKey: 'user_data',
        
        // Token lifetime (seconds) - should match backend settings
        accessTokenLifetime: 60 * 60, // 1 hour
        refreshTokenLifetime: 7 * 24 * 60 * 60 // 7 days
    },
    
    // ====================================
    // STORAGE KEYS
    // ====================================
    storage: {
        authToken: 'auth_token',
        refreshToken: 'refresh_token',
        tokenExpiry: 'token_expiry',
        userData: 'auth_user',
        rememberMe: 'auth_remember',
        theme: 'app_theme',
        language: 'app_language'
    },
    
    // ====================================
    // DEBUG MODE
    // ====================================
    debug: true,
    
    // ====================================
    // HELPER METHODS
    // ====================================
    getEndpoint(name) {
        return this.endpoints[name] || null;
    },
    
    getFullUrl(endpoint) {
        return `${this.api.baseUrl}${endpoint}`;
    }
};

// Make config globally available
window.AppConfig = AppConfig;

// Log configuration in debug mode
if (AppConfig.debug) {
    console.log('AppConfig loaded:', {
        useMockApi: AppConfig.api.useMockApi,
        baseUrl: AppConfig.api.baseUrl
    });
}
