/**
 * API.JS - API Client Module
 * Handles all HTTP requests with JWT authentication
 */

const ApiClient = {
    /**
     * Get stored access token
     */
    getToken() {
        return localStorage.getItem(AppConfig.AUTH.TOKEN_KEY);
    },

    /**
     * Get stored refresh token
     */
    getRefreshToken() {
        return localStorage.getItem(AppConfig.AUTH.REFRESH_KEY);
    },

    /**
     * Build headers for requests
     */
    getHeaders(includeAuth = true, contentType = 'application/json') {
        const headers = {
            'Content-Type': contentType,
        };

        if (includeAuth) {
            const token = this.getToken();
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }
        }

        // Add CSRF token for Django
        const csrfToken = this.getCsrfToken();
        if (csrfToken) {
            headers['X-CSRFToken'] = csrfToken;
        }

        return headers;
    },

    /**
     * Get CSRF token from cookie
     */
    getCsrfToken() {
        const name = 'csrftoken';
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                return cookie.substring(name.length + 1);
            }
        }
        return null;
    },

    /**
     * Generic fetch wrapper with error handling
     */
    async request(endpoint, options = {}) {
        const url = `${AppConfig.API.BASE_URL}${endpoint}`;
        const config = {
            ...options,
            headers: {
                ...this.getHeaders(options.auth !== false),
                ...options.headers,
            },
        };

        try {
            const response = await fetch(url, config);

            // Handle 401 - Try refresh token
            if (response.status === 401 && options.auth !== false) {
                const refreshed = await this.refreshToken();
                if (refreshed) {
                    // Retry with new token
                    config.headers['Authorization'] = `Bearer ${this.getToken()}`;
                    const retryResponse = await fetch(url, config);
                    return this.handleResponse(retryResponse);
                } else {
                    // Redirect to login
                    Auth.logout();
                    window.location.href = AppConfig.ROUTES.PUBLIC.LOGIN;
                    throw new Error('Session expired');
                }
            }

            return this.handleResponse(response);
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    },

    /**
     * Handle response and parse JSON
     */
    async handleResponse(response) {
        let data = null;

        // Try to parse JSON
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            data = await response.json();
        } else {
            data = await response.text();
        }

        if (!response.ok) {
            const error = new Error(data.message || data.detail || 'Request failed');
            error.status = response.status;
            error.data = data;
            throw error;
        }

        return data;
    },

    /**
     * Refresh access token
     */
    async refreshToken() {
        const refreshToken = this.getRefreshToken();
        if (!refreshToken) return false;

        try {
            const response = await fetch(`${AppConfig.API.BASE_URL}/users/token/refresh/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh: refreshToken }),
            });

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem(AppConfig.AUTH.TOKEN_KEY, data.access);
                if (data.refresh) {
                    localStorage.setItem(AppConfig.AUTH.REFRESH_KEY, data.refresh);
                }
                return true;
            }
        } catch (error) {
            console.error('Token refresh failed:', error);
        }

        return false;
    },

    // =====================================
    // HTTP Methods
    // =====================================

    /**
     * GET request
     */
    async get(endpoint, params = {}, options = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;
        return this.request(url, { method: 'GET', ...options });
    },

    /**
     * POST request
     */
    async post(endpoint, data = {}, options = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data),
            ...options,
        });
    },

    /**
     * PUT request
     */
    async put(endpoint, data = {}, options = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data),
            ...options,
        });
    },

    /**
     * PATCH request
     */
    async patch(endpoint, data = {}, options = {}) {
        return this.request(endpoint, {
            method: 'PATCH',
            body: JSON.stringify(data),
            ...options,
        });
    },

    /**
     * DELETE request
     */
    async delete(endpoint, options = {}) {
        return this.request(endpoint, { method: 'DELETE', ...options });
    },

    /**
     * Upload file (multipart/form-data)
     */
    async upload(endpoint, formData, options = {}) {
        const headers = {
            'Authorization': `Bearer ${this.getToken()}`,
        };
        
        const csrfToken = this.getCsrfToken();
        if (csrfToken) {
            headers['X-CSRFToken'] = csrfToken;
        }

        const response = await fetch(`${AppConfig.API.BASE_URL}${endpoint}`, {
            method: 'POST',
            headers,
            body: formData,
            ...options,
        });

        return this.handleResponse(response);
    },
};

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ApiClient;
}
