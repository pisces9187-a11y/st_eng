/**
 * CONFIG.JS - Application Configuration
 * Global settings and constants
 */

const AppConfig = {
    // API Settings
    API: {
        BASE_URL: '/api/v1',
        TIMEOUT: 30000,
        RETRY_ATTEMPTS: 3,
        RETRY_DELAY: 1000,
    },

    // Authentication
    AUTH: {
        TOKEN_KEY: 'access_token',
        REFRESH_KEY: 'refresh_token',
        USER_KEY: 'user_data',
        TOKEN_EXPIRY_BUFFER: 5 * 60 * 1000, // 5 minutes before expiry
    },

    // Storage Keys
    STORAGE: {
        THEME: 'theme_preference',
        LANGUAGE: 'preferred_language',
        SIDEBAR_STATE: 'sidebar_collapsed',
        RECENT_SEARCHES: 'recent_searches',
    },

    // UI Settings
    UI: {
        TOAST_DURATION: 5000,
        DEBOUNCE_DELAY: 300,
        ANIMATION_DURATION: 300,
        SIDEBAR_WIDTH: 260,
        NAVBAR_HEIGHT: 64,
    },

    // Validation Rules
    VALIDATION: {
        EMAIL_REGEX: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
        PHONE_REGEX: /^(\+84|84|0)?[1-9]\d{8,9}$/,
        PASSWORD_MIN_LENGTH: 8,
        USERNAME_MIN_LENGTH: 3,
        USERNAME_MAX_LENGTH: 30,
    },

    // Routes
    ROUTES: {
        PUBLIC: {
            HOME: '/',
            LOGIN: '/login/',
            SIGNUP: '/signup/',
            PASSWORD_RESET: '/password-reset/',
            PRICING: '/pricing/',
        },
        DASHBOARD: {
            HOME: '/dashboard/',
            LESSONS: '/lessons/',
            PROFILE: '/profile/',
            SETTINGS: '/settings/',
        },
        ADMIN: {
            DASHBOARD: '/admin-portal/',
            USERS: '/admin-portal/users/',
            COURSES: '/admin-portal/courses/',
            REPORTS: '/admin-portal/reports/',
        },
    },

    // Language Levels
    LEVELS: ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'],

    // Skill Types
    SKILLS: [
        { key: 'listening', label: 'Nghe', icon: 'fa-headphones' },
        { key: 'speaking', label: 'Nói', icon: 'fa-microphone' },
        { key: 'reading', label: 'Đọc', icon: 'fa-book-open' },
        { key: 'writing', label: 'Viết', icon: 'fa-pen' },
        { key: 'grammar', label: 'Ngữ pháp', icon: 'fa-spell-check' },
        { key: 'vocabulary', label: 'Từ vựng', icon: 'fa-language' },
    ],

    // Date Formats
    DATE_FORMAT: {
        SHORT: 'DD/MM/YYYY',
        LONG: 'DD MMMM, YYYY',
        TIME: 'HH:mm',
        DATETIME: 'DD/MM/YYYY HH:mm',
    },

    // Feature Flags
    FEATURES: {
        SOCIAL_LOGIN: true,
        LIVE_CLASSES: true,
        AI_SPEAKING: true,
        GAMIFICATION: true,
        DARK_MODE: false, // Coming soon
    },

    // Environment
    IS_DEV: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1',
    VERSION: '1.0.0',
};

// Freeze config to prevent modifications
Object.freeze(AppConfig);
Object.freeze(AppConfig.API);
Object.freeze(AppConfig.AUTH);
Object.freeze(AppConfig.STORAGE);
Object.freeze(AppConfig.UI);
Object.freeze(AppConfig.VALIDATION);
Object.freeze(AppConfig.ROUTES);
Object.freeze(AppConfig.FEATURES);

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AppConfig;
}
