/**
 * AUTH.JS - Authentication Module
 * Login, Register, Logout, Token Management
 */

const Auth = {
    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        const token = localStorage.getItem(AppConfig.AUTH.TOKEN_KEY);
        return !!token;
    },

    /**
     * Get current user data
     */
    getCurrentUser() {
        const userData = localStorage.getItem(AppConfig.AUTH.USER_KEY);
        return userData ? JSON.parse(userData) : null;
    },

    /**
     * Store authentication data
     */
    setAuth(accessToken, refreshToken, userData = null) {
        localStorage.setItem(AppConfig.AUTH.TOKEN_KEY, accessToken);
        if (refreshToken) {
            localStorage.setItem(AppConfig.AUTH.REFRESH_KEY, refreshToken);
        }
        if (userData) {
            localStorage.setItem(AppConfig.AUTH.USER_KEY, JSON.stringify(userData));
        }
    },

    /**
     * Clear authentication data
     */
    clearAuth() {
        localStorage.removeItem(AppConfig.AUTH.TOKEN_KEY);
        localStorage.removeItem(AppConfig.AUTH.REFRESH_KEY);
        localStorage.removeItem(AppConfig.AUTH.USER_KEY);
    },

    /**
     * Login user
     */
    async login(email, password) {
        try {
            const response = await ApiClient.post('/users/login/', {
                email,
                password,
            }, { auth: false });

            this.setAuth(
                response.tokens.access,
                response.tokens.refresh,
                response.user
            );

            return { success: true, user: response.user };
        } catch (error) {
            return {
                success: false,
                error: error.data?.detail || error.message || 'Đăng nhập thất bại',
            };
        }
    },

    /**
     * Register new user
     */
    async register(data) {
        try {
            const response = await ApiClient.post('/users/register/', data, { auth: false });
            return { success: true, data: response };
        } catch (error) {
            return {
                success: false,
                errors: error.data || { detail: error.message || 'Đăng ký thất bại' },
            };
        }
    },

    /**
     * Verify email with OTP
     */
    async verifyEmail(email, otp) {
        try {
            const response = await ApiClient.post('/users/verify-email/', {
                email,
                otp,
            }, { auth: false });

            // Auto login after verification
            if (response.tokens) {
                this.setAuth(
                    response.tokens.access,
                    response.tokens.refresh,
                    response.user
                );
            }

            return { success: true, data: response };
        } catch (error) {
            return {
                success: false,
                error: error.data?.detail || error.message || 'Xác thực thất bại',
            };
        }
    },

    /**
     * Resend verification email
     */
    async resendVerification(email) {
        try {
            await ApiClient.post('/users/resend-verification/', { email }, { auth: false });
            return { success: true };
        } catch (error) {
            return {
                success: false,
                error: error.data?.detail || error.message || 'Không thể gửi lại mã',
            };
        }
    },

    /**
     * Request password reset
     */
    async requestPasswordReset(email) {
        try {
            await ApiClient.post('/users/password-reset/', { email }, { auth: false });
            return { success: true };
        } catch (error) {
            return {
                success: false,
                error: error.data?.detail || error.message || 'Không thể gửi email đặt lại mật khẩu',
            };
        }
    },

    /**
     * Reset password with token
     */
    async resetPassword(token, password, confirmPassword) {
        try {
            await ApiClient.post('/users/password-reset/confirm/', {
                token,
                password,
                confirm_password: confirmPassword,
            }, { auth: false });
            return { success: true };
        } catch (error) {
            return {
                success: false,
                error: error.data?.detail || error.message || 'Đặt lại mật khẩu thất bại',
            };
        }
    },

    /**
     * Change password (authenticated)
     */
    async changePassword(currentPassword, newPassword) {
        try {
            await ApiClient.post('/users/change-password/', {
                current_password: currentPassword,
                new_password: newPassword,
            });
            return { success: true };
        } catch (error) {
            return {
                success: false,
                error: error.data?.detail || error.message || 'Đổi mật khẩu thất bại',
            };
        }
    },

    /**
     * Logout user
     */
    async logout() {
        try {
            const refreshToken = localStorage.getItem(AppConfig.AUTH.REFRESH_KEY);
            if (refreshToken) {
                await ApiClient.post('/users/logout/', { refresh: refreshToken });
            }
        } catch (error) {
            console.error('Logout API error:', error);
        } finally {
            this.clearAuth();
        }
    },

    /**
     * Get user profile
     */
    async getProfile() {
        try {
            const response = await ApiClient.get('/users/profile/');
            localStorage.setItem(AppConfig.AUTH.USER_KEY, JSON.stringify(response));
            return { success: true, user: response };
        } catch (error) {
            return {
                success: false,
                error: error.data?.detail || error.message,
            };
        }
    },

    /**
     * Update user profile
     */
    async updateProfile(data) {
        try {
            const response = await ApiClient.patch('/users/profile/', data);
            localStorage.setItem(AppConfig.AUTH.USER_KEY, JSON.stringify(response));
            return { success: true, user: response };
        } catch (error) {
            return {
                success: false,
                errors: error.data || { detail: error.message },
            };
        }
    },

    /**
     * Validate password strength
     */
    validatePassword(password) {
        const result = {
            isValid: true,
            strength: 'weak',
            score: 0,
            messages: [],
        };

        // Length check
        if (password.length < AppConfig.VALIDATION.PASSWORD_MIN_LENGTH) {
            result.isValid = false;
            result.messages.push(`Mật khẩu phải có ít nhất ${AppConfig.VALIDATION.PASSWORD_MIN_LENGTH} ký tự`);
        } else {
            result.score += 20;
        }

        // Uppercase check
        if (/[A-Z]/.test(password)) {
            result.score += 20;
        } else {
            result.messages.push('Nên có ít nhất 1 chữ in hoa');
        }

        // Lowercase check
        if (/[a-z]/.test(password)) {
            result.score += 20;
        }

        // Number check
        if (/[0-9]/.test(password)) {
            result.score += 20;
        } else {
            result.messages.push('Nên có ít nhất 1 số');
        }

        // Special character check
        if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
            result.score += 20;
        } else {
            result.messages.push('Nên có ký tự đặc biệt');
        }

        // Determine strength
        if (result.score >= 80) {
            result.strength = 'strong';
        } else if (result.score >= 60) {
            result.strength = 'good';
        } else if (result.score >= 40) {
            result.strength = 'fair';
        } else {
            result.strength = 'weak';
        }

        return result;
    },

    /**
     * Validate email format
     */
    validateEmail(email) {
        return AppConfig.VALIDATION.EMAIL_REGEX.test(email);
    },

    /**
     * Initialize auth state (call on page load)
     */
    init() {
        // Check if token exists and update UI
        const isAuth = this.isAuthenticated();
        document.body.classList.toggle('user-authenticated', isAuth);
        document.body.classList.toggle('user-guest', !isAuth);

        // Update UI elements based on auth state
        this.updateAuthUI(isAuth);

        return isAuth;
    },

    /**
     * Update UI elements based on auth state
     */
    updateAuthUI(isAuthenticated) {
        // Show/hide elements based on auth state
        document.querySelectorAll('[data-auth="required"]').forEach(el => {
            el.style.display = isAuthenticated ? '' : 'none';
        });

        document.querySelectorAll('[data-auth="guest"]').forEach(el => {
            el.style.display = isAuthenticated ? 'none' : '';
        });

        // Update user info in UI
        if (isAuthenticated) {
            const user = this.getCurrentUser();
            if (user) {
                document.querySelectorAll('[data-user="name"]').forEach(el => {
                    el.textContent = user.full_name || user.email;
                });
                document.querySelectorAll('[data-user="email"]').forEach(el => {
                    el.textContent = user.email;
                });
                document.querySelectorAll('[data-user="avatar"]').forEach(el => {
                    if (user.avatar) {
                        el.src = user.avatar;
                    }
                });
            }
        }
    },
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    Auth.init();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Auth;
}
