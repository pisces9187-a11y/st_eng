/**
 * Toast Notification System
 * Beautiful and responsive toast notifications
 */

class ToastManager {
    constructor() {
        this.container = null;
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }
    
    init() {
        // Create toast container if it doesn't exist
        if (!document.getElementById('toast-container')) {
            this.container = document.createElement('div');
            this.container.id = 'toast-container';
            this.container.className = 'toast-container';
            document.body.appendChild(this.container);
            
            // Add styles
            this.addStyles();
        } else {
            this.container = document.getElementById('toast-container');
        }
    }
    
    addStyles() {
        if (document.getElementById('toast-styles')) {
            return;
        }
        
        const style = document.createElement('style');
        style.id = 'toast-styles';
        style.textContent = `
            .toast-container {
                position: fixed !important;
                top: 20px !important;
                right: 20px !important;
                z-index: 9999 !important;
                display: flex !important;
                flex-direction: column !important;
                gap: 10px !important;
                max-width: 400px !important;
                pointer-events: auto !important;
            }
            
            .toast {
                background: white !important;
                border-radius: 12px !important;
                padding: 16px 20px !important;
                box-shadow: 0 4px 24px rgba(0, 0, 0, 0.15) !important;
                display: flex !important;
                align-items: flex-start !important;
                gap: 12px !important;
                animation: slideInRight 0.3s ease-out !important;
                position: relative !important;
                overflow: hidden !important;
                margin: 0 !important;
                opacity: 1 !important;
                visibility: visible !important;
            }
            
            .toast.hiding {
                animation: slideOutRight 0.3s ease-in forwards !important;
            }
            
            @keyframes slideInRight {
                from {
                    transform: translateX(400px);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            
            @keyframes slideOutRight {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(400px);
                    opacity: 0;
                }
            }
            
            .toast-icon {
                width: 24px !important;
                height: 24px !important;
                border-radius: 50% !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                flex-shrink: 0 !important;
                font-size: 14px !important;
            }
            
            .toast-icon.success {
                background: #D1FAE5 !important;
                color: #059669 !important;
            }
            
            .toast-icon.error {
                background: #FEE2E2 !important;
                color: #DC2626 !important;
            }
            
            .toast-icon.warning {
                background: #FEF3C7 !important;
                color: #D97706 !important;
            }
            
            .toast-icon.info {
                background: #DBEAFE !important;
                color: #2563EB !important;
            }
            
            .toast-content {
                flex: 1 !important;
            }
            
            .toast-title {
                font-weight: 600 !important;
                font-size: 14px !important;
                color: #1F2937 !important;
                margin-bottom: 4px !important;
                margin: 0 !important;
            }
            
            .toast-message {
                font-size: 13px !important;
                color: #6B7280 !important;
                line-height: 1.4 !important;
                margin: 0 !important;
            }
            
            .toast-close {
                width: 20px !important;
                height: 20px !important;
                border-radius: 50% !important;
                background: transparent !important;
                border: none !important;
                color: #9CA3AF !important;
                cursor: pointer !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                transition: all 0.2s !important;
                flex-shrink: 0 !important;
            }
            
            .toast-close:hover {
                background: #F3F4F6;
                color: #4B5563;
            }
            
            .toast-progress {
                position: absolute;
                bottom: 0;
                left: 0;
                height: 3px;
                background: currentColor;
                opacity: 0.3;
                animation: progress 3s linear forwards;
            }
            
            @keyframes progress {
                from {
                    width: 100%;
                }
                to {
                    width: 0%;
                }
            }
            
            .toast.success .toast-progress {
                color: #059669;
            }
            
            .toast.error .toast-progress {
                color: #DC2626;
            }
            
            .toast.warning .toast-progress {
                color: #D97706;
            }
            
            .toast.info .toast-progress {
                color: #2563EB;
            }
            
            @media (max-width: 640px) {
                .toast-container {
                    left: 10px;
                    right: 10px;
                    max-width: none;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    show(type, title, message, duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icons = {
            success: '✓',
            error: '✕',
            warning: '⚠',
            info: 'ℹ'
        };
        
        toast.innerHTML = `
            <div class="toast-icon ${type}">${icons[type]}</div>
            <div class="toast-content">
                <div class="toast-title">${title}</div>
                ${message ? `<div class="toast-message">${message}</div>` : ''}
            </div>
            <button class="toast-close">✕</button>
            <div class="toast-progress"></div>
        `;
        
        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => this.hide(toast));
        
        this.container.appendChild(toast);
        
        // Auto hide
        if (duration > 0) {
            setTimeout(() => this.hide(toast), duration);
        }
        
        return toast;
    }
    
    hide(toast) {
        toast.classList.add('hiding');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }
    
    success(title, message, duration) {
        return this.show('success', title, message, duration);
    }
    
    error(title, message, duration) {
        return this.show('error', title, message, duration);
    }
    
    warning(title, message, duration) {
        return this.show('warning', title, message, duration);
    }
    
    info(title, message, duration) {
        return this.show('info', title, message, duration);
    }
}

// Create global instance
window.Toast = new ToastManager();

// Convenience functions
window.showSuccess = (title, message, duration) => window.Toast.success(title, message, duration);
window.showError = (title, message, duration) => window.Toast.error(title, message, duration);
window.showWarning = (title, message, duration) => window.Toast.warning(title, message, duration);
window.showInfo = (title, message, duration) => window.Toast.info(title, message, duration);
