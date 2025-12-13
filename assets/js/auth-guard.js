/* ====================================
   AUTH GUARD MODULE
   English Learning Platform
   Protects pages requiring authentication
   ==================================== */

/**
 * AuthGuard - Protects pages and manages user session
 */
const AuthGuard = {
    // Check if user is authenticated
    isAuthenticated() {
        const token = localStorage.getItem('access_token');
        return !!token;
    },
    
    // Get current user data from storage
    getUser() {
        const userData = localStorage.getItem('user_data');
        if (userData) {
            try {
                return JSON.parse(userData);
            } catch (e) {
                return null;
            }
        }
        return null;
    },
    
    // Get access token
    getToken() {
        return localStorage.getItem('access_token');
    },
    
    // Redirect to login if not authenticated
    requireAuth(redirectUrl = 'login.html') {
        if (!this.isAuthenticated()) {
            console.log('[AuthGuard] Not authenticated, redirecting to login');
            window.location.href = redirectUrl;
            return false;
        }
        return true;
    },
    
    // Logout user
    async logout() {
        console.log('[AuthGuard] Logging out...');
        
        // Call API to blacklist token
        if (window.djangoApi) {
            try {
                await window.djangoApi.logout();
            } catch (e) {
                console.error('[AuthGuard] Logout API error:', e);
            }
        }
        
        // Clear local storage
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_data');
        localStorage.removeItem('auth_remember');
        
        // Redirect to login
        window.location.href = 'login.html';
    },
    
    // Update user data in storage
    updateUser(userData) {
        localStorage.setItem('user_data', JSON.stringify(userData));
    },
    
    // Get user display name
    getDisplayName() {
        const user = this.getUser();
        if (!user) return 'Guest';
        
        if (user.first_name && user.last_name) {
            return `${user.first_name} ${user.last_name}`;
        }
        if (user.first_name) return user.first_name;
        if (user.username) return user.username;
        return user.email.split('@')[0];
    },
    
    // Get user avatar URL
    getAvatarUrl() {
        const user = this.getUser();
        if (user && user.avatar) {
            return user.avatar;
        }
        return '../assets/images/avatar-default.jpg';
    },
    
    // Get user level display
    getLevelDisplay() {
        const user = this.getUser();
        return user ? (user.current_level || 'A1') : 'A1';
    },
    
    // Get XP points
    getXpPoints() {
        const user = this.getUser();
        return user ? (user.xp_points || 0) : 0;
    },
    
    // Get streak days
    getStreakDays() {
        const user = this.getUser();
        return user ? (user.streak_days || 0) : 0;
    }
};

// Make globally available
window.AuthGuard = AuthGuard;

console.log('[AuthGuard] Module loaded');
