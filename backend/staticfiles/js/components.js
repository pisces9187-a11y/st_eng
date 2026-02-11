/* ====================================
   UI Components - English Learning Platform
   Phase 1: Error Handling & Loading States
   Created: 08/12/2025
   ==================================== */

/**
 * UIComponents - Reusable UI component library
 * Includes: Loading states, Error handling, Toasts, Modals, Skeletons
 */
const UIComponents = {
    
    // ====================================
    // CONFIGURATION
    // ====================================
    config: {
        toastDuration: 4000,
        loadingDelay: 300, // Delay before showing loading (prevents flash)
        animationDuration: 300
    },

    // ====================================
    // LOADING STATES
    // ====================================
    loading: {
        /**
         * Show full page loading overlay
         */
        showFullPage(message = 'Đang tải...') {
            this.removeFullPage(); // Remove existing first
            
            const overlay = document.createElement('div');
            overlay.id = 'fullPageLoading';
            overlay.className = 'loading-overlay';
            overlay.innerHTML = `
                <div class="loading-content">
                    <div class="loading-spinner">
                        <div class="spinner-ring"></div>
                        <div class="spinner-ring"></div>
                        <div class="spinner-ring"></div>
                    </div>
                    <p class="loading-message">${message}</p>
                </div>
            `;
            
            document.body.appendChild(overlay);
            document.body.style.overflow = 'hidden';
            
            // Animate in
            requestAnimationFrame(() => {
                overlay.classList.add('show');
            });
        },

        /**
         * Hide full page loading overlay
         */
        hideFullPage() {
            const overlay = document.getElementById('fullPageLoading');
            if (overlay) {
                overlay.classList.remove('show');
                setTimeout(() => {
                    overlay.remove();
                    document.body.style.overflow = '';
                }, UIComponents.config.animationDuration);
            }
        },

        /**
         * Remove full page loading immediately
         */
        removeFullPage() {
            const overlay = document.getElementById('fullPageLoading');
            if (overlay) {
                overlay.remove();
                document.body.style.overflow = '';
            }
        },

        /**
         * Show inline loading spinner
         */
        showInline(container, size = 'md') {
            const element = typeof container === 'string' 
                ? document.querySelector(container) 
                : container;
            
            if (!element) return;

            const spinner = document.createElement('div');
            spinner.className = `inline-loading inline-loading-${size}`;
            spinner.innerHTML = `
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Đang tải...</span>
                </div>
            `;

            element.innerHTML = '';
            element.appendChild(spinner);
        },

        /**
         * Show button loading state
         */
        buttonStart(button, text = 'Đang xử lý...') {
            const btn = typeof button === 'string'
                ? document.querySelector(button)
                : button;
            
            if (!btn) return;

            btn.dataset.originalText = btn.innerHTML;
            btn.disabled = true;
            btn.innerHTML = `
                <span class="spinner-border spinner-border-sm me-2" role="status"></span>
                ${text}
            `;
        },

        /**
         * Reset button from loading state
         */
        buttonEnd(button) {
            const btn = typeof button === 'string'
                ? document.querySelector(button)
                : button;
            
            if (!btn) return;

            btn.disabled = false;
            btn.innerHTML = btn.dataset.originalText || btn.innerHTML;
        },

        /**
         * Show skeleton loading
         */
        showSkeleton(container, type = 'card', count = 1) {
            const element = typeof container === 'string'
                ? document.querySelector(container)
                : container;
            
            if (!element) return;

            const skeletons = [];
            for (let i = 0; i < count; i++) {
                skeletons.push(this.getSkeletonTemplate(type));
            }

            element.innerHTML = skeletons.join('');
        },

        /**
         * Get skeleton template by type
         */
        getSkeletonTemplate(type) {
            const templates = {
                card: `
                    <div class="skeleton-card">
                        <div class="skeleton-image skeleton-animate"></div>
                        <div class="skeleton-body">
                            <div class="skeleton-title skeleton-animate"></div>
                            <div class="skeleton-text skeleton-animate"></div>
                            <div class="skeleton-text skeleton-animate" style="width: 60%"></div>
                        </div>
                    </div>
                `,
                list: `
                    <div class="skeleton-list-item">
                        <div class="skeleton-avatar skeleton-animate"></div>
                        <div class="skeleton-list-content">
                            <div class="skeleton-title skeleton-animate" style="width: 40%"></div>
                            <div class="skeleton-text skeleton-animate"></div>
                        </div>
                    </div>
                `,
                table: `
                    <div class="skeleton-table-row">
                        <div class="skeleton-cell skeleton-animate"></div>
                        <div class="skeleton-cell skeleton-animate"></div>
                        <div class="skeleton-cell skeleton-animate"></div>
                        <div class="skeleton-cell skeleton-animate"></div>
                    </div>
                `,
                text: `
                    <div class="skeleton-paragraph">
                        <div class="skeleton-text skeleton-animate"></div>
                        <div class="skeleton-text skeleton-animate"></div>
                        <div class="skeleton-text skeleton-animate" style="width: 80%"></div>
                    </div>
                `,
                flashcard: `
                    <div class="skeleton-flashcard">
                        <div class="skeleton-flashcard-front skeleton-animate"></div>
                    </div>
                `
            };

            return templates[type] || templates.card;
        }
    },

    // ====================================
    // TOAST NOTIFICATIONS
    // ====================================
    toast: {
        container: null,

        /**
         * Initialize toast container
         */
        init() {
            if (!this.container) {
                this.container = document.createElement('div');
                this.container.id = 'toastContainer';
                this.container.className = 'toast-container';
                document.body.appendChild(this.container);
            }
        },

        /**
         * Show toast notification
         */
        show(message, type = 'info', duration = null) {
            this.init();

            const id = 'toast-' + Date.now();
            const icons = {
                success: 'fas fa-check-circle',
                error: 'fas fa-exclamation-circle',
                warning: 'fas fa-exclamation-triangle',
                info: 'fas fa-info-circle'
            };

            const toast = document.createElement('div');
            toast.id = id;
            toast.className = `toast-item toast-${type}`;
            toast.innerHTML = `
                <div class="toast-icon">
                    <i class="${icons[type] || icons.info}"></i>
                </div>
                <div class="toast-content">
                    <p class="toast-message">${message}</p>
                </div>
                <button class="toast-close" onclick="UIComponents.toast.dismiss('${id}')">
                    <i class="fas fa-times"></i>
                </button>
                <div class="toast-progress"></div>
            `;

            this.container.appendChild(toast);

            // Animate in
            requestAnimationFrame(() => {
                toast.classList.add('show');
            });

            // Auto dismiss
            const timeout = duration || UIComponents.config.toastDuration;
            setTimeout(() => {
                this.dismiss(id);
            }, timeout);

            return id;
        },

        /**
         * Show success toast
         */
        success(message, duration) {
            return this.show(message, 'success', duration);
        },

        /**
         * Show error toast
         */
        error(message, duration) {
            return this.show(message, 'error', duration);
        },

        /**
         * Show warning toast
         */
        warning(message, duration) {
            return this.show(message, 'warning', duration);
        },

        /**
         * Show info toast
         */
        info(message, duration) {
            return this.show(message, 'info', duration);
        },

        /**
         * Dismiss a toast
         */
        dismiss(id) {
            const toast = document.getElementById(id);
            if (toast) {
                toast.classList.remove('show');
                toast.classList.add('hide');
                setTimeout(() => {
                    toast.remove();
                }, UIComponents.config.animationDuration);
            }
        },

        /**
         * Dismiss all toasts
         */
        dismissAll() {
            if (this.container) {
                this.container.querySelectorAll('.toast-item').forEach(toast => {
                    this.dismiss(toast.id);
                });
            }
        }
    },

    // ====================================
    // ERROR HANDLING
    // ====================================
    error: {
        /**
         * Show error message inline
         */
        showInline(container, message, retryCallback = null) {
            const element = typeof container === 'string'
                ? document.querySelector(container)
                : container;
            
            if (!element) return;

            const errorHtml = `
                <div class="error-state">
                    <div class="error-icon">
                        <i class="fas fa-exclamation-triangle"></i>
                    </div>
                    <h4 class="error-title">Đã xảy ra lỗi</h4>
                    <p class="error-message">${message}</p>
                    ${retryCallback ? `
                        <button class="btn btn-primary btn-retry" onclick="(${retryCallback.toString()})()">
                            <i class="fas fa-redo me-2"></i>Thử lại
                        </button>
                    ` : ''}
                </div>
            `;

            element.innerHTML = errorHtml;
        },

        /**
         * Show network error
         */
        showNetworkError(container, retryCallback = null) {
            this.showInline(
                container,
                'Không thể kết nối đến máy chủ. Vui lòng kiểm tra kết nối mạng.',
                retryCallback
            );
        },

        /**
         * Show empty state
         */
        showEmpty(container, message = 'Không có dữ liệu', icon = 'fas fa-inbox', action = null) {
            const element = typeof container === 'string'
                ? document.querySelector(container)
                : container;
            
            if (!element) return;

            const emptyHtml = `
                <div class="empty-state">
                    <div class="empty-icon">
                        <i class="${icon}"></i>
                    </div>
                    <h4 class="empty-title">${message}</h4>
                    ${action ? `
                        <button class="btn btn-primary mt-3" onclick="(${action.callback.toString()})()">
                            <i class="${action.icon || 'fas fa-plus'} me-2"></i>${action.text}
                        </button>
                    ` : ''}
                </div>
            `;

            element.innerHTML = emptyHtml;
        },

        /**
         * Handle API error response
         */
        handleApiError(error, showToast = true) {
            let message = 'Đã xảy ra lỗi. Vui lòng thử lại.';
            
            if (error.response) {
                // Server responded with error
                const status = error.response.status;
                switch (status) {
                    case 400:
                        message = 'Dữ liệu không hợp lệ.';
                        break;
                    case 401:
                        message = 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.';
                        // Redirect to login
                        setTimeout(() => {
                            window.location.href = '/public/login.html';
                        }, 2000);
                        break;
                    case 403:
                        message = 'Bạn không có quyền thực hiện hành động này.';
                        break;
                    case 404:
                        message = 'Không tìm thấy dữ liệu.';
                        break;
                    case 429:
                        message = 'Quá nhiều yêu cầu. Vui lòng đợi một chút.';
                        break;
                    case 500:
                        message = 'Lỗi máy chủ. Vui lòng thử lại sau.';
                        break;
                    default:
                        message = error.response.data?.message || message;
                }
            } else if (error.request) {
                // No response received
                message = 'Không thể kết nối đến máy chủ.';
            } else {
                // Error setting up request
                message = error.message || message;
            }

            if (showToast) {
                UIComponents.toast.error(message);
            }

            return message;
        }
    },

    // ====================================
    // MODAL HELPERS
    // ====================================
    modal: {
        /**
         * Show confirmation modal
         */
        confirm(options = {}) {
            return new Promise((resolve) => {
                const {
                    title = 'Xác nhận',
                    message = 'Bạn có chắc chắn muốn thực hiện hành động này?',
                    confirmText = 'Xác nhận',
                    cancelText = 'Hủy',
                    confirmClass = 'btn-primary',
                    icon = 'fas fa-question-circle',
                    dangerous = false
                } = options;

                const id = 'confirmModal-' + Date.now();
                const modal = document.createElement('div');
                modal.innerHTML = `
                    <div class="modal fade" id="${id}" tabindex="-1" data-bs-backdrop="static">
                        <div class="modal-dialog modal-dialog-centered">
                            <div class="modal-content">
                                <div class="modal-body text-center py-4">
                                    <div class="confirm-icon ${dangerous ? 'text-danger' : 'text-primary'} mb-3">
                                        <i class="${icon}" style="font-size: 3rem;"></i>
                                    </div>
                                    <h5 class="modal-title mb-3">${title}</h5>
                                    <p class="text-muted">${message}</p>
                                </div>
                                <div class="modal-footer justify-content-center border-0 pb-4">
                                    <button type="button" class="btn btn-outline-secondary px-4" data-action="cancel">
                                        ${cancelText}
                                    </button>
                                    <button type="button" class="btn ${dangerous ? 'btn-danger' : confirmClass} px-4" data-action="confirm">
                                        ${confirmText}
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;

                document.body.appendChild(modal);

                const modalElement = document.getElementById(id);
                const bsModal = new bootstrap.Modal(modalElement);

                // Handle button clicks
                modalElement.querySelector('[data-action="confirm"]').addEventListener('click', () => {
                    bsModal.hide();
                    resolve(true);
                });

                modalElement.querySelector('[data-action="cancel"]').addEventListener('click', () => {
                    bsModal.hide();
                    resolve(false);
                });

                // Cleanup on hide
                modalElement.addEventListener('hidden.bs.modal', () => {
                    modal.remove();
                });

                bsModal.show();
            });
        },

        /**
         * Show alert modal
         */
        alert(options = {}) {
            return new Promise((resolve) => {
                const {
                    title = 'Thông báo',
                    message = '',
                    buttonText = 'Đồng ý',
                    icon = 'fas fa-info-circle',
                    type = 'info' // info, success, warning, error
                } = options;

                const typeClasses = {
                    info: 'text-primary',
                    success: 'text-success',
                    warning: 'text-warning',
                    error: 'text-danger'
                };

                const id = 'alertModal-' + Date.now();
                const modal = document.createElement('div');
                modal.innerHTML = `
                    <div class="modal fade" id="${id}" tabindex="-1">
                        <div class="modal-dialog modal-dialog-centered">
                            <div class="modal-content">
                                <div class="modal-body text-center py-4">
                                    <div class="${typeClasses[type] || typeClasses.info} mb-3">
                                        <i class="${icon}" style="font-size: 3rem;"></i>
                                    </div>
                                    <h5 class="modal-title mb-3">${title}</h5>
                                    <p class="text-muted">${message}</p>
                                </div>
                                <div class="modal-footer justify-content-center border-0 pb-4">
                                    <button type="button" class="btn btn-primary px-4" data-bs-dismiss="modal">
                                        ${buttonText}
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;

                document.body.appendChild(modal);

                const modalElement = document.getElementById(id);
                const bsModal = new bootstrap.Modal(modalElement);

                modalElement.addEventListener('hidden.bs.modal', () => {
                    modal.remove();
                    resolve();
                });

                bsModal.show();
            });
        }
    },

    // ====================================
    // PROGRESS INDICATORS
    // ====================================
    progress: {
        /**
         * Show progress bar
         */
        show(container, percent, options = {}) {
            const element = typeof container === 'string'
                ? document.querySelector(container)
                : container;
            
            if (!element) return;

            const {
                label = '',
                showPercent = true,
                color = 'primary',
                striped = false,
                animated = false
            } = options;

            const stripedClass = striped ? 'progress-bar-striped' : '';
            const animatedClass = animated ? 'progress-bar-animated' : '';

            element.innerHTML = `
                <div class="progress-wrapper">
                    ${label ? `<div class="progress-label">${label}</div>` : ''}
                    <div class="progress" style="height: 8px;">
                        <div class="progress-bar bg-${color} ${stripedClass} ${animatedClass}" 
                             role="progressbar" 
                             style="width: ${percent}%"
                             aria-valuenow="${percent}" 
                             aria-valuemin="0" 
                             aria-valuemax="100">
                        </div>
                    </div>
                    ${showPercent ? `<div class="progress-percent">${Math.round(percent)}%</div>` : ''}
                </div>
            `;
        },

        /**
         * Update progress value
         */
        update(container, percent) {
            const element = typeof container === 'string'
                ? document.querySelector(container)
                : container;
            
            if (!element) return;

            const bar = element.querySelector('.progress-bar');
            const percentText = element.querySelector('.progress-percent');

            if (bar) {
                bar.style.width = `${percent}%`;
                bar.setAttribute('aria-valuenow', percent);
            }

            if (percentText) {
                percentText.textContent = `${Math.round(percent)}%`;
            }
        }
    },

    // ====================================
    // FORM VALIDATION
    // ====================================
    form: {
        /**
         * Validate form field
         */
        validateField(field, rules) {
            const value = field.value.trim();
            let isValid = true;
            let message = '';

            for (const rule of rules) {
                switch (rule.type) {
                    case 'required':
                        if (!value) {
                            isValid = false;
                            message = rule.message || 'Trường này là bắt buộc';
                        }
                        break;
                    case 'email':
                        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                        if (value && !emailRegex.test(value)) {
                            isValid = false;
                            message = rule.message || 'Email không hợp lệ';
                        }
                        break;
                    case 'minLength':
                        if (value && value.length < rule.value) {
                            isValid = false;
                            message = rule.message || `Tối thiểu ${rule.value} ký tự`;
                        }
                        break;
                    case 'maxLength':
                        if (value && value.length > rule.value) {
                            isValid = false;
                            message = rule.message || `Tối đa ${rule.value} ký tự`;
                        }
                        break;
                    case 'pattern':
                        if (value && !rule.value.test(value)) {
                            isValid = false;
                            message = rule.message || 'Định dạng không hợp lệ';
                        }
                        break;
                    case 'match':
                        const matchField = document.querySelector(rule.value);
                        if (matchField && value !== matchField.value) {
                            isValid = false;
                            message = rule.message || 'Giá trị không khớp';
                        }
                        break;
                }

                if (!isValid) break;
            }

            this.setFieldState(field, isValid, message);
            return isValid;
        },

        /**
         * Set field validation state
         */
        setFieldState(field, isValid, message = '') {
            const wrapper = field.closest('.form-group') || field.parentElement;
            let feedback = wrapper.querySelector('.invalid-feedback');

            field.classList.remove('is-valid', 'is-invalid');
            field.classList.add(isValid ? 'is-valid' : 'is-invalid');

            if (!isValid && message) {
                if (!feedback) {
                    feedback = document.createElement('div');
                    feedback.className = 'invalid-feedback';
                    field.parentNode.insertBefore(feedback, field.nextSibling);
                }
                feedback.textContent = message;
            }
        },

        /**
         * Clear form validation
         */
        clearValidation(form) {
            const formElement = typeof form === 'string'
                ? document.querySelector(form)
                : form;
            
            if (!formElement) return;

            formElement.querySelectorAll('.is-valid, .is-invalid').forEach(field => {
                field.classList.remove('is-valid', 'is-invalid');
            });

            formElement.querySelectorAll('.invalid-feedback').forEach(feedback => {
                feedback.remove();
            });
        }
    },

    // ====================================
    // INITIALIZATION
    // ====================================
    init() {
        // Inject required CSS
        this.injectStyles();
        
        // Initialize toast container
        this.toast.init();

        console.log('[UI] Components initialized');
    },

    /**
     * Inject component styles
     */
    injectStyles() {
        if (document.getElementById('uiComponentStyles')) return;

        const styles = document.createElement('style');
        styles.id = 'uiComponentStyles';
        styles.textContent = `
            /* Loading Overlay */
            .loading-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(255, 255, 255, 0.95);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 9999;
                opacity: 0;
                transition: opacity 0.3s ease;
            }
            
            .loading-overlay.show {
                opacity: 1;
            }
            
            .loading-content {
                text-align: center;
            }
            
            .loading-spinner {
                position: relative;
                width: 80px;
                height: 80px;
                margin: 0 auto 20px;
            }
            
            .spinner-ring {
                position: absolute;
                width: 100%;
                height: 100%;
                border: 3px solid transparent;
                border-top-color: #F47C26;
                border-radius: 50%;
                animation: spin 1.2s linear infinite;
            }
            
            .spinner-ring:nth-child(2) {
                width: 70%;
                height: 70%;
                top: 15%;
                left: 15%;
                border-top-color: #183B56;
                animation-duration: 1s;
            }
            
            .spinner-ring:nth-child(3) {
                width: 40%;
                height: 40%;
                top: 30%;
                left: 30%;
                border-top-color: #F47C26;
                animation-duration: 0.8s;
            }
            
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            
            .loading-message {
                color: #183B56;
                font-size: 1rem;
                font-weight: 600;
            }
            
            /* Inline Loading */
            .inline-loading {
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 40px;
            }
            
            .inline-loading-sm { padding: 20px; }
            .inline-loading-lg { padding: 60px; }
            
            /* Skeleton Loading */
            .skeleton-animate {
                background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
                background-size: 200% 100%;
                animation: skeleton-loading 1.5s infinite;
            }
            
            @keyframes skeleton-loading {
                0% { background-position: 200% 0; }
                100% { background-position: -200% 0; }
            }
            
            .skeleton-card {
                background: white;
                border-radius: 12px;
                overflow: hidden;
                margin-bottom: 16px;
            }
            
            .skeleton-image {
                height: 180px;
            }
            
            .skeleton-body {
                padding: 16px;
            }
            
            .skeleton-title {
                height: 20px;
                margin-bottom: 12px;
                border-radius: 4px;
            }
            
            .skeleton-text {
                height: 14px;
                margin-bottom: 8px;
                border-radius: 4px;
            }
            
            .skeleton-avatar {
                width: 50px;
                height: 50px;
                border-radius: 50%;
            }
            
            .skeleton-list-item {
                display: flex;
                gap: 16px;
                padding: 16px;
                background: white;
                border-radius: 8px;
                margin-bottom: 8px;
            }
            
            .skeleton-list-content {
                flex: 1;
            }
            
            .skeleton-table-row {
                display: flex;
                gap: 16px;
                padding: 12px;
                border-bottom: 1px solid #f0f0f0;
            }
            
            .skeleton-cell {
                flex: 1;
                height: 16px;
                border-radius: 4px;
            }
            
            .skeleton-flashcard {
                width: 100%;
                max-width: 400px;
                height: 250px;
                margin: 20px auto;
            }
            
            .skeleton-flashcard-front {
                width: 100%;
                height: 100%;
                border-radius: 16px;
            }
            
            /* Toast Container */
            .toast-container {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                display: flex;
                flex-direction: column;
                gap: 12px;
                max-width: 400px;
            }
            
            .toast-item {
                display: flex;
                align-items: flex-start;
                gap: 12px;
                padding: 16px;
                background: white;
                border-radius: 12px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
                transform: translateX(120%);
                transition: transform 0.3s ease;
                position: relative;
                overflow: hidden;
            }
            
            .toast-item.show {
                transform: translateX(0);
            }
            
            .toast-item.hide {
                transform: translateX(120%);
            }
            
            .toast-icon {
                font-size: 1.25rem;
                flex-shrink: 0;
            }
            
            .toast-success .toast-icon { color: #28a745; }
            .toast-error .toast-icon { color: #dc3545; }
            .toast-warning .toast-icon { color: #ffc107; }
            .toast-info .toast-icon { color: #17a2b8; }
            
            .toast-content {
                flex: 1;
            }
            
            .toast-message {
                margin: 0;
                font-size: 0.95rem;
                color: #333;
            }
            
            .toast-close {
                background: none;
                border: none;
                color: #999;
                cursor: pointer;
                padding: 0;
                font-size: 1rem;
            }
            
            .toast-close:hover {
                color: #333;
            }
            
            .toast-progress {
                position: absolute;
                bottom: 0;
                left: 0;
                height: 3px;
                background: currentColor;
                animation: toast-progress 4s linear forwards;
            }
            
            .toast-success .toast-progress { background: #28a745; }
            .toast-error .toast-progress { background: #dc3545; }
            .toast-warning .toast-progress { background: #ffc107; }
            .toast-info .toast-progress { background: #17a2b8; }
            
            @keyframes toast-progress {
                from { width: 100%; }
                to { width: 0%; }
            }
            
            /* Error/Empty States */
            .error-state,
            .empty-state {
                text-align: center;
                padding: 60px 20px;
            }
            
            .error-icon,
            .empty-icon {
                font-size: 4rem;
                margin-bottom: 20px;
            }
            
            .error-icon { color: #dc3545; }
            .empty-icon { color: #6c757d; }
            
            .error-title,
            .empty-title {
                font-size: 1.25rem;
                font-weight: 600;
                margin-bottom: 8px;
                color: #183B56;
            }
            
            .error-message {
                color: #6c757d;
                margin-bottom: 20px;
            }
            
            /* Progress Wrapper */
            .progress-wrapper {
                margin-bottom: 16px;
            }
            
            .progress-label {
                font-size: 0.875rem;
                color: #6c757d;
                margin-bottom: 8px;
            }
            
            .progress-percent {
                font-size: 0.875rem;
                color: #183B56;
                font-weight: 600;
                text-align: right;
                margin-top: 4px;
            }
            
            /* Mobile Toast Position */
            @media (max-width: 576px) {
                .toast-container {
                    left: 20px;
                    right: 20px;
                    top: auto;
                    bottom: 20px;
                }
                
                .toast-item {
                    transform: translateY(120%);
                }
                
                .toast-item.show {
                    transform: translateY(0);
                }
                
                .toast-item.hide {
                    transform: translateY(120%);
                }
            }
        `;

        document.head.appendChild(styles);
    }
};

// ====================================
// AUTO INITIALIZE
// ====================================
document.addEventListener('DOMContentLoaded', () => {
    UIComponents.init();
});

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UIComponents;
}

window.UIComponents = UIComponents;

console.log('[UI] Components module loaded');
