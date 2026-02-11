/**
 * UTILS.JS - Utility Functions
 * Common helper functions used across the application
 */

const Utils = {
    // =====================================
    // DOM Utilities
    // =====================================

    /**
     * Query selector shorthand
     */
    $(selector, context = document) {
        return context.querySelector(selector);
    },

    /**
     * Query selector all shorthand
     */
    $$(selector, context = document) {
        return [...context.querySelectorAll(selector)];
    },

    /**
     * Create element with attributes
     */
    createElement(tag, attributes = {}, children = []) {
        const el = document.createElement(tag);
        Object.entries(attributes).forEach(([key, value]) => {
            if (key === 'class') {
                el.className = value;
            } else if (key === 'style' && typeof value === 'object') {
                Object.assign(el.style, value);
            } else if (key.startsWith('data')) {
                el.setAttribute(key, value);
            } else {
                el[key] = value;
            }
        });
        children.forEach(child => {
            if (typeof child === 'string') {
                el.appendChild(document.createTextNode(child));
            } else {
                el.appendChild(child);
            }
        });
        return el;
    },

    // =====================================
    // String Utilities
    // =====================================

    /**
     * Capitalize first letter
     */
    capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    },

    /**
     * Truncate string with ellipsis
     */
    truncate(str, length = 50, suffix = '...') {
        if (str.length <= length) return str;
        return str.substring(0, length).trim() + suffix;
    },

    /**
     * Generate random string
     */
    randomString(length = 10) {
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        return Array.from({ length }, () => chars.charAt(Math.floor(Math.random() * chars.length))).join('');
    },

    /**
     * Slugify string
     */
    slugify(str) {
        return str
            .toLowerCase()
            .trim()
            .replace(/[^\w\s-]/g, '')
            .replace(/[\s_-]+/g, '-')
            .replace(/^-+|-+$/g, '');
    },

    // =====================================
    // Number Utilities
    // =====================================

    /**
     * Format number with commas
     */
    formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    },

    /**
     * Format currency (VND)
     */
    formatCurrency(amount, currency = 'VND') {
        return new Intl.NumberFormat('vi-VN', {
            style: 'currency',
            currency: currency,
        }).format(amount);
    },

    /**
     * Format percentage
     */
    formatPercent(value, decimals = 0) {
        return `${value.toFixed(decimals)}%`;
    },

    /**
     * Clamp number between min and max
     */
    clamp(num, min, max) {
        return Math.min(Math.max(num, min), max);
    },

    // =====================================
    // Date Utilities
    // =====================================

    /**
     * Format date
     */
    formatDate(date, format = 'DD/MM/YYYY') {
        const d = new Date(date);
        const day = String(d.getDate()).padStart(2, '0');
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const year = d.getFullYear();
        const hours = String(d.getHours()).padStart(2, '0');
        const minutes = String(d.getMinutes()).padStart(2, '0');

        return format
            .replace('DD', day)
            .replace('MM', month)
            .replace('YYYY', year)
            .replace('HH', hours)
            .replace('mm', minutes);
    },

    /**
     * Get relative time (e.g., "2 giờ trước")
     */
    timeAgo(date) {
        const seconds = Math.floor((new Date() - new Date(date)) / 1000);
        const intervals = [
            { label: 'năm', seconds: 31536000 },
            { label: 'tháng', seconds: 2592000 },
            { label: 'tuần', seconds: 604800 },
            { label: 'ngày', seconds: 86400 },
            { label: 'giờ', seconds: 3600 },
            { label: 'phút', seconds: 60 },
            { label: 'giây', seconds: 1 },
        ];

        for (const interval of intervals) {
            const count = Math.floor(seconds / interval.seconds);
            if (count >= 1) {
                return `${count} ${interval.label} trước`;
            }
        }
        return 'Vừa xong';
    },

    /**
     * Format duration (seconds to HH:MM:SS)
     */
    formatDuration(seconds) {
        const h = Math.floor(seconds / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        const s = Math.floor(seconds % 60);

        if (h > 0) {
            return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
        }
        return `${m}:${String(s).padStart(2, '0')}`;
    },

    // =====================================
    // Validation Utilities
    // =====================================

    /**
     * Check if value is empty
     */
    isEmpty(value) {
        return value === null || value === undefined || value === '' ||
            (Array.isArray(value) && value.length === 0) ||
            (typeof value === 'object' && Object.keys(value).length === 0);
    },

    /**
     * Validate email
     */
    isValidEmail(email) {
        return AppConfig.VALIDATION.EMAIL_REGEX.test(email);
    },

    /**
     * Validate phone (Vietnam)
     */
    isValidPhone(phone) {
        return AppConfig.VALIDATION.PHONE_REGEX.test(phone);
    },

    // =====================================
    // Function Utilities
    // =====================================

    /**
     * Debounce function
     */
    debounce(func, wait = 300) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * Throttle function
     */
    throttle(func, limit = 300) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    // =====================================
    // Storage Utilities
    // =====================================

    /**
     * Set localStorage with JSON
     */
    setStorage(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.error('LocalStorage set error:', e);
        }
    },

    /**
     * Get localStorage with JSON parse
     */
    getStorage(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (e) {
            console.error('LocalStorage get error:', e);
            return defaultValue;
        }
    },

    /**
     * Remove localStorage item
     */
    removeStorage(key) {
        localStorage.removeItem(key);
    },

    // =====================================
    // URL Utilities
    // =====================================

    /**
     * Get URL parameters
     */
    getUrlParams() {
        return Object.fromEntries(new URLSearchParams(window.location.search));
    },

    /**
     * Get single URL parameter
     */
    getUrlParam(name) {
        return new URLSearchParams(window.location.search).get(name);
    },

    /**
     * Build URL with parameters
     */
    buildUrl(base, params = {}) {
        const url = new URL(base, window.location.origin);
        Object.entries(params).forEach(([key, value]) => {
            if (value !== null && value !== undefined) {
                url.searchParams.set(key, value);
            }
        });
        return url.toString();
    },

    // =====================================
    // UI Utilities
    // =====================================

    /**
     * Show loading state on button
     */
    setButtonLoading(button, isLoading, text = null) {
        if (isLoading) {
            button.disabled = true;
            button.dataset.originalText = button.innerHTML;
            button.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>${text || 'Đang xử lý...'}`;
        } else {
            button.disabled = false;
            button.innerHTML = button.dataset.originalText || text || 'Submit';
        }
    },

    /**
     * Copy text to clipboard
     */
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (err) {
            // Fallback for older browsers
            const textarea = document.createElement('textarea');
            textarea.value = text;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            return true;
        }
    },

    /**
     * Scroll to element
     */
    scrollTo(element, offset = 0) {
        const el = typeof element === 'string' ? document.querySelector(element) : element;
        if (el) {
            const top = el.getBoundingClientRect().top + window.scrollY - offset;
            window.scrollTo({ top, behavior: 'smooth' });
        }
    },

    // =====================================
    // Toast Notifications
    // =====================================

    /**
     * Show toast notification
     */
    showToast(message, type = 'info', duration = AppConfig.UI.TOAST_DURATION) {
        // Create toast container if not exists
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '1100';
            document.body.appendChild(container);
        }

        // Icon mapping
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-times-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle',
        };

        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast show toast-${type}`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="toast-header">
                <i class="fas ${icons[type]} text-${type === 'error' ? 'danger' : type} me-2"></i>
                <strong class="me-auto">${this.capitalize(type)}</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">${message}</div>
        `;

        container.appendChild(toast);

        // Auto remove after duration
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, duration);

        // Close button handler
        toast.querySelector('.btn-close').addEventListener('click', () => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        });
    },

    // =====================================
    // Modal Helpers
    // =====================================

    /**
     * Show confirmation modal
     */
    confirm(message, options = {}) {
        return new Promise((resolve) => {
            const modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.innerHTML = `
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${options.title || 'Xác nhận'}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <p>${message}</p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">
                                ${options.cancelText || 'Hủy'}
                            </button>
                            <button type="button" class="btn btn-${options.type || 'primary'} confirm-btn">
                                ${options.confirmText || 'Xác nhận'}
                            </button>
                        </div>
                    </div>
                </div>
            `;

            document.body.appendChild(modal);
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();

            modal.querySelector('.confirm-btn').addEventListener('click', () => {
                bsModal.hide();
                resolve(true);
            });

            modal.addEventListener('hidden.bs.modal', () => {
                modal.remove();
                resolve(false);
            });
        });
    },
};

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Utils;
}
