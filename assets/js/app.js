/* ====================================
   APP INITIALIZER - English Learning Platform
   Phase 1: PWA + Offline + Core Features
   Created: 08/12/2025
   ==================================== */

/**
 * AppInitializer - Handles PWA registration and app-wide initialization
 */
const AppInitializer = {
    // ====================================
    // CONFIGURATION
    // ====================================
    config: {
        serviceWorkerPath: '/service-worker.js',
        manifestPath: '/manifest.json',
        debug: true
    },

    // State
    state: {
        isOnline: navigator.onLine,
        isPWA: false,
        serviceWorkerRegistration: null,
        deferredPrompt: null
    },

    // ====================================
    // INITIALIZATION
    // ====================================
    
    /**
     * Initialize the application
     */
    async init() {
        this.log('Initializing application...');
        
        // Check if running as PWA
        this.checkPWAMode();
        
        // Register Service Worker
        await this.registerServiceWorker();
        
        // Setup online/offline listeners
        this.setupNetworkListeners();
        
        // Setup install prompt
        this.setupInstallPrompt();
        
        // Initialize offline indicator
        this.initOfflineIndicator();
        
        // Add PWA meta tags if not present
        this.ensurePWAMetaTags();
        
        // Initialize database
        await this.initDatabase();
        
        this.log('Application initialized successfully');
    },

    // ====================================
    // SERVICE WORKER
    // ====================================
    
    /**
     * Register the service worker
     */
    async registerServiceWorker() {
        if (!('serviceWorker' in navigator)) {
            this.log('Service Workers not supported');
            return;
        }

        try {
            const registration = await navigator.serviceWorker.register(
                this.config.serviceWorkerPath,
                { scope: '/' }
            );

            this.state.serviceWorkerRegistration = registration;
            this.log('Service Worker registered:', registration.scope);

            // Handle updates
            registration.addEventListener('updatefound', () => {
                const newWorker = registration.installing;
                this.log('New Service Worker found');

                newWorker.addEventListener('statechange', () => {
                    if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                        this.showUpdateNotification();
                    }
                });
            });

            // Listen for messages from service worker
            navigator.serviceWorker.addEventListener('message', (event) => {
                this.handleServiceWorkerMessage(event.data);
            });

        } catch (error) {
            this.log('Service Worker registration failed:', error);
        }
    },

    /**
     * Handle messages from Service Worker
     */
    handleServiceWorkerMessage(data) {
        this.log('Message from SW:', data);

        switch (data.type) {
            case 'CACHE_UPDATED':
                this.log('Cache has been updated');
                break;
            case 'OFFLINE_READY':
                UIComponents?.toast?.success('Ứng dụng sẵn sàng hoạt động offline!');
                break;
        }
    },

    /**
     * Show update notification
     */
    showUpdateNotification() {
        if (typeof UIComponents !== 'undefined') {
            UIComponents.modal.confirm({
                title: 'Cập nhật mới!',
                message: 'Có phiên bản mới của ứng dụng. Bạn có muốn cập nhật ngay?',
                confirmText: 'Cập nhật',
                cancelText: 'Để sau',
                icon: 'fas fa-download'
            }).then((confirmed) => {
                if (confirmed) {
                    this.applyUpdate();
                }
            });
        } else {
            if (confirm('Có phiên bản mới. Cập nhật ngay?')) {
                this.applyUpdate();
            }
        }
    },

    /**
     * Apply service worker update
     */
    applyUpdate() {
        if (this.state.serviceWorkerRegistration?.waiting) {
            this.state.serviceWorkerRegistration.waiting.postMessage({ type: 'SKIP_WAITING' });
        }
        window.location.reload();
    },

    // ====================================
    // NETWORK STATUS
    // ====================================
    
    /**
     * Setup online/offline listeners
     */
    setupNetworkListeners() {
        window.addEventListener('online', () => {
            this.state.isOnline = true;
            this.handleOnline();
        });

        window.addEventListener('offline', () => {
            this.state.isOnline = false;
            this.handleOffline();
        });

        // Initial check
        if (!navigator.onLine) {
            this.handleOffline();
        }
    },

    /**
     * Handle coming online
     */
    handleOnline() {
        this.log('App is online');
        
        // Hide offline indicator
        this.hideOfflineIndicator();
        
        // Show toast
        if (typeof UIComponents !== 'undefined') {
            UIComponents.toast.success('Đã kết nối lại mạng!');
        }

        // Trigger background sync
        this.triggerBackgroundSync();

        // Dispatch custom event
        window.dispatchEvent(new CustomEvent('app:online'));
    },

    /**
     * Handle going offline
     */
    handleOffline() {
        this.log('App is offline');
        
        // Show offline indicator
        this.showOfflineIndicator();
        
        // Show toast
        if (typeof UIComponents !== 'undefined') {
            UIComponents.toast.warning('Bạn đang offline. Một số tính năng có thể bị hạn chế.');
        }

        // Dispatch custom event
        window.dispatchEvent(new CustomEvent('app:offline'));
    },

    /**
     * Initialize offline indicator
     */
    initOfflineIndicator() {
        // Create indicator element
        const indicator = document.createElement('div');
        indicator.id = 'offlineIndicator';
        indicator.className = 'offline-indicator';
        indicator.innerHTML = `
            <i class="fas fa-wifi-slash"></i>
            <span>Bạn đang offline</span>
        `;
        document.body.appendChild(indicator);

        // Add styles
        const styles = document.createElement('style');
        styles.textContent = `
            .offline-indicator {
                position: fixed;
                bottom: 80px;
                left: 50%;
                transform: translateX(-50%) translateY(100px);
                background: #dc3545;
                color: white;
                padding: 12px 24px;
                border-radius: 50px;
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 0.9rem;
                font-weight: 600;
                box-shadow: 0 4px 12px rgba(220, 53, 69, 0.4);
                z-index: 9998;
                transition: transform 0.3s ease;
            }
            
            .offline-indicator.show {
                transform: translateX(-50%) translateY(0);
            }
            
            @media (min-width: 768px) {
                .offline-indicator {
                    bottom: 20px;
                }
            }
        `;
        document.head.appendChild(styles);

        // Show if already offline
        if (!navigator.onLine) {
            this.showOfflineIndicator();
        }
    },

    /**
     * Show offline indicator
     */
    showOfflineIndicator() {
        const indicator = document.getElementById('offlineIndicator');
        if (indicator) {
            indicator.classList.add('show');
        }
    },

    /**
     * Hide offline indicator
     */
    hideOfflineIndicator() {
        const indicator = document.getElementById('offlineIndicator');
        if (indicator) {
            indicator.classList.remove('show');
        }
    },

    // ====================================
    // BACKGROUND SYNC
    // ====================================
    
    /**
     * Trigger background sync
     */
    async triggerBackgroundSync() {
        if (!this.state.serviceWorkerRegistration) return;

        try {
            // Sync flashcard progress
            await this.state.serviceWorkerRegistration.sync.register('sync-flashcard-progress');
            this.log('Background sync registered: flashcard-progress');

            // Sync learning progress
            await this.state.serviceWorkerRegistration.sync.register('sync-learning-progress');
            this.log('Background sync registered: learning-progress');
        } catch (error) {
            this.log('Background sync not supported:', error);
            // Fallback: manual sync
            this.manualSync();
        }
    },

    /**
     * Manual sync fallback
     */
    async manualSync() {
        if (typeof englishDB === 'undefined') return;

        try {
            const pendingItems = await englishDB.getPendingSyncItems();
            this.log('Pending sync items:', pendingItems.length);

            // Process each item
            for (const item of pendingItems) {
                try {
                    // Make API call based on type
                    // await this.syncItem(item);
                    await englishDB.markSyncCompleted(item.id);
                } catch (error) {
                    this.log('Sync item failed:', error);
                }
            }
        } catch (error) {
            this.log('Manual sync failed:', error);
        }
    },

    // ====================================
    // PWA INSTALL
    // ====================================
    
    /**
     * Check if running as PWA
     */
    checkPWAMode() {
        this.state.isPWA = window.matchMedia('(display-mode: standalone)').matches ||
                          window.navigator.standalone === true ||
                          document.referrer.includes('android-app://');
        
        this.log('Running as PWA:', this.state.isPWA);

        if (this.state.isPWA) {
            document.body.classList.add('is-pwa');
        }
    },

    /**
     * Setup install prompt
     */
    setupInstallPrompt() {
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            this.state.deferredPrompt = e;
            this.log('Install prompt captured');
            
            // Show install button
            this.showInstallButton();
        });

        // Listen for successful install
        window.addEventListener('appinstalled', () => {
            this.state.deferredPrompt = null;
            this.log('PWA installed successfully');
            this.hideInstallButton();
            
            if (typeof UIComponents !== 'undefined') {
                UIComponents.toast.success('Ứng dụng đã được cài đặt!');
            }
        });
    },

    /**
     * Show install button
     */
    showInstallButton() {
        // Only show if not already installed
        if (this.state.isPWA) return;

        let installBanner = document.getElementById('pwaInstallBanner');
        
        if (!installBanner) {
            installBanner = document.createElement('div');
            installBanner.id = 'pwaInstallBanner';
            installBanner.className = 'pwa-install-banner';
            installBanner.innerHTML = `
                <div class="install-content">
                    <i class="fas fa-mobile-alt"></i>
                    <div class="install-text">
                        <strong>Cài đặt ứng dụng</strong>
                        <span>Trải nghiệm tốt hơn với ứng dụng</span>
                    </div>
                </div>
                <div class="install-actions">
                    <button class="btn-install-dismiss" onclick="AppInitializer.dismissInstallBanner()">
                        Để sau
                    </button>
                    <button class="btn-install" onclick="AppInitializer.promptInstall()">
                        Cài đặt
                    </button>
                </div>
            `;
            document.body.appendChild(installBanner);

            // Add styles
            if (!document.getElementById('pwaInstallStyles')) {
                const styles = document.createElement('style');
                styles.id = 'pwaInstallStyles';
                styles.textContent = `
                    .pwa-install-banner {
                        position: fixed;
                        bottom: 0;
                        left: 0;
                        right: 0;
                        background: white;
                        padding: 16px 20px;
                        box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.1);
                        display: flex;
                        align-items: center;
                        justify-content: space-between;
                        z-index: 9999;
                        transform: translateY(100%);
                        transition: transform 0.3s ease;
                    }
                    
                    .pwa-install-banner.show {
                        transform: translateY(0);
                    }
                    
                    .install-content {
                        display: flex;
                        align-items: center;
                        gap: 12px;
                    }
                    
                    .install-content i {
                        font-size: 2rem;
                        color: #F47C26;
                    }
                    
                    .install-text {
                        display: flex;
                        flex-direction: column;
                    }
                    
                    .install-text strong {
                        color: #183B56;
                        font-size: 1rem;
                    }
                    
                    .install-text span {
                        color: #6c757d;
                        font-size: 0.85rem;
                    }
                    
                    .install-actions {
                        display: flex;
                        gap: 12px;
                    }
                    
                    .btn-install-dismiss {
                        background: none;
                        border: none;
                        color: #6c757d;
                        font-size: 0.9rem;
                        cursor: pointer;
                    }
                    
                    .btn-install {
                        background: #F47C26;
                        color: white;
                        border: none;
                        padding: 10px 20px;
                        border-radius: 50px;
                        font-weight: 600;
                        cursor: pointer;
                        transition: background 0.3s ease;
                    }
                    
                    .btn-install:hover {
                        background: #D35400;
                    }
                    
                    @media (max-width: 576px) {
                        .pwa-install-banner {
                            flex-direction: column;
                            gap: 16px;
                            padding-bottom: calc(16px + env(safe-area-inset-bottom));
                        }
                        
                        .install-actions {
                            width: 100%;
                            justify-content: space-between;
                        }
                        
                        .btn-install {
                            flex: 1;
                        }
                    }
                `;
                document.head.appendChild(styles);
            }
        }

        // Show with animation
        setTimeout(() => {
            installBanner.classList.add('show');
        }, 3000); // Show after 3 seconds
    },

    /**
     * Hide install button
     */
    hideInstallButton() {
        const banner = document.getElementById('pwaInstallBanner');
        if (banner) {
            banner.classList.remove('show');
            setTimeout(() => banner.remove(), 300);
        }
    },

    /**
     * Dismiss install banner
     */
    dismissInstallBanner() {
        this.hideInstallButton();
        // Remember dismissal for 7 days
        localStorage.setItem('pwaInstallDismissed', Date.now() + 7 * 24 * 60 * 60 * 1000);
    },

    /**
     * Prompt for PWA installation
     */
    async promptInstall() {
        if (!this.state.deferredPrompt) {
            this.log('No install prompt available');
            return;
        }

        this.state.deferredPrompt.prompt();
        const { outcome } = await this.state.deferredPrompt.userChoice;
        
        this.log('Install prompt outcome:', outcome);
        
        if (outcome === 'accepted') {
            this.hideInstallButton();
        }

        this.state.deferredPrompt = null;
    },

    // ====================================
    // META TAGS
    // ====================================
    
    /**
     * Ensure PWA meta tags are present
     */
    ensurePWAMetaTags() {
        const head = document.head;

        // Theme color
        if (!document.querySelector('meta[name="theme-color"]')) {
            const themeColor = document.createElement('meta');
            themeColor.name = 'theme-color';
            themeColor.content = '#F47C26';
            head.appendChild(themeColor);
        }

        // Apple meta tags
        if (!document.querySelector('meta[name="apple-mobile-web-app-capable"]')) {
            const appleMeta = document.createElement('meta');
            appleMeta.name = 'apple-mobile-web-app-capable';
            appleMeta.content = 'yes';
            head.appendChild(appleMeta);
        }

        if (!document.querySelector('meta[name="apple-mobile-web-app-status-bar-style"]')) {
            const appleStatusBar = document.createElement('meta');
            appleStatusBar.name = 'apple-mobile-web-app-status-bar-style';
            appleStatusBar.content = 'default';
            head.appendChild(appleStatusBar);
        }

        // Manifest link
        if (!document.querySelector('link[rel="manifest"]')) {
            const manifest = document.createElement('link');
            manifest.rel = 'manifest';
            manifest.href = this.config.manifestPath;
            head.appendChild(manifest);
        }
    },

    // ====================================
    // DATABASE
    // ====================================
    
    /**
     * Initialize IndexedDB
     */
    async initDatabase() {
        if (typeof englishDB !== 'undefined') {
            try {
                await englishDB.ready();
                this.log('Database initialized');
            } catch (error) {
                this.log('Database initialization failed:', error);
            }
        }
    },

    // ====================================
    // UTILITIES
    // ====================================
    
    /**
     * Log with prefix
     */
    log(...args) {
        if (this.config.debug) {
            console.log('[App]', ...args);
        }
    },

    /**
     * Check if app is online
     */
    isOnline() {
        return this.state.isOnline;
    },

    /**
     * Check if running as PWA
     */
    isPWA() {
        return this.state.isPWA;
    },

    /**
     * Get cache size
     */
    async getCacheSize() {
        if ('storage' in navigator && 'estimate' in navigator.storage) {
            const estimate = await navigator.storage.estimate();
            return {
                used: estimate.usage,
                quota: estimate.quota,
                usedMB: (estimate.usage / (1024 * 1024)).toFixed(2),
                quotaMB: (estimate.quota / (1024 * 1024)).toFixed(2)
            };
        }
        return null;
    },

    /**
     * Clear all cached data
     */
    async clearCache() {
        // Clear service worker cache
        if ('caches' in window) {
            const cacheNames = await caches.keys();
            await Promise.all(cacheNames.map(name => caches.delete(name)));
        }

        // Clear IndexedDB
        if (typeof englishDB !== 'undefined') {
            await englishDB.clear('syncQueue');
        }

        this.log('Cache cleared');
        
        if (typeof UIComponents !== 'undefined') {
            UIComponents.toast.success('Đã xóa cache!');
        }
    }
};

// ====================================
// AUTO INITIALIZE
// ====================================
document.addEventListener('DOMContentLoaded', () => {
    AppInitializer.init();
});

// Export
window.AppInitializer = AppInitializer;

console.log('[App] Initializer module loaded');
