/* ====================================
   SERVICE WORKER - English Learning Platform
   Phase 1: PWA + Offline Support
   Created: 08/12/2025
   ==================================== */

const CACHE_VERSION = 'v1.0.0';
const CACHE_NAME = `english-learning-${CACHE_VERSION}`;

// Assets to cache immediately on install
const STATIC_ASSETS = [
    // HTML Pages - Public
    '/public/index.html',
    '/public/login.html',
    '/public/signup.html',
    '/public/dashboard.html',
    '/public/flashcard.html',
    '/public/vocabulary-list.html',
    '/public/dictation.html',
    '/public/speaking-practice.html',
    '/public/writing-practice.html',
    '/public/lesson-player.html',
    '/public/lesson-library.html',
    '/public/grammar-wiki.html',
    '/public/practice-test.html',
    '/public/assessment.html',
    '/public/assessment-result.html',
    '/public/profile.html',
    '/public/progress-tracker.html',
    '/public/leaderboard.html',
    '/public/achievements.html',
    '/public/notifications.html',
    
    // CSS
    '/assets/css/theme.css',
    '/assets/css/style.css',
    '/assets/css/responsive.css',
    '/assets/css/auth.css',
    '/assets/css/profile.css',
    '/assets/css/onboarding.css',
    
    // JavaScript
    '/assets/js/main.js',
    '/assets/js/db.js',
    '/assets/js/components.js',
    '/assets/js/onboarding.js',
    
    // Manifest
    '/manifest.json',
    
    // Offline page
    '/public/offline.html'
];

// External CDN resources to cache
const CDN_ASSETS = [
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
    'https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700;800&family=Open+Sans:wght@400;600&display=swap',
    'https://unpkg.com/vue@3/dist/vue.global.js'
];

// Cache strategies
const CACHE_STRATEGIES = {
    // Cache first, network fallback (for static assets)
    CACHE_FIRST: 'cache-first',
    // Network first, cache fallback (for API calls)
    NETWORK_FIRST: 'network-first',
    // Stale while revalidate (for frequently updated content)
    STALE_WHILE_REVALIDATE: 'stale-while-revalidate',
    // Network only (for sensitive data)
    NETWORK_ONLY: 'network-only'
};

// ====================================
// INSTALL EVENT
// ====================================
self.addEventListener('install', (event) => {
    console.log('[SW] Installing Service Worker...');
    
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('[SW] Caching static assets');
                
                // Cache static assets
                const staticPromise = cache.addAll(STATIC_ASSETS.map(url => {
                    return new Request(url, { cache: 'reload' });
                })).catch(err => {
                    console.warn('[SW] Some static assets failed to cache:', err);
                });
                
                // Cache CDN assets
                const cdnPromise = Promise.all(
                    CDN_ASSETS.map(url => {
                        return fetch(url, { mode: 'cors' })
                            .then(response => {
                                if (response.ok) {
                                    return cache.put(url, response);
                                }
                            })
                            .catch(err => {
                                console.warn('[SW] CDN asset failed:', url);
                            });
                    })
                );
                
                return Promise.all([staticPromise, cdnPromise]);
            })
            .then(() => {
                console.log('[SW] Installation complete');
                // Force waiting service worker to become active
                return self.skipWaiting();
            })
    );
});

// ====================================
// ACTIVATE EVENT
// ====================================
self.addEventListener('activate', (event) => {
    console.log('[SW] Activating Service Worker...');
    
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames
                        .filter((name) => name.startsWith('english-learning-') && name !== CACHE_NAME)
                        .map((name) => {
                            console.log('[SW] Deleting old cache:', name);
                            return caches.delete(name);
                        })
                );
            })
            .then(() => {
                console.log('[SW] Activation complete');
                // Take control of all pages immediately
                return self.clients.claim();
            })
    );
});

// ====================================
// FETCH EVENT
// ====================================
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }
    
    // Skip chrome-extension and other non-http requests
    if (!url.protocol.startsWith('http')) {
        return;
    }
    
    // Determine cache strategy based on request type
    const strategy = getCacheStrategy(url, request);
    
    switch (strategy) {
        case CACHE_STRATEGIES.CACHE_FIRST:
            event.respondWith(cacheFirst(request));
            break;
        case CACHE_STRATEGIES.NETWORK_FIRST:
            event.respondWith(networkFirst(request));
            break;
        case CACHE_STRATEGIES.STALE_WHILE_REVALIDATE:
            event.respondWith(staleWhileRevalidate(request));
            break;
        case CACHE_STRATEGIES.NETWORK_ONLY:
            event.respondWith(networkOnly(request));
            break;
        default:
            event.respondWith(cacheFirst(request));
    }
});

// ====================================
// CACHE STRATEGY HELPERS
// ====================================

/**
 * Determine cache strategy based on URL and request type
 */
function getCacheStrategy(url, request) {
    // API calls - Network first
    if (url.pathname.startsWith('/api/')) {
        return CACHE_STRATEGIES.NETWORK_FIRST;
    }
    
    // Static assets - Cache first
    if (isStaticAsset(url.pathname)) {
        return CACHE_STRATEGIES.CACHE_FIRST;
    }
    
    // CDN resources - Cache first
    if (isCDNResource(url.href)) {
        return CACHE_STRATEGIES.CACHE_FIRST;
    }
    
    // HTML pages - Stale while revalidate
    if (url.pathname.endsWith('.html')) {
        return CACHE_STRATEGIES.STALE_WHILE_REVALIDATE;
    }
    
    // Default - Cache first
    return CACHE_STRATEGIES.CACHE_FIRST;
}

/**
 * Check if URL is a static asset
 */
function isStaticAsset(pathname) {
    const staticExtensions = ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf', '.eot'];
    return staticExtensions.some(ext => pathname.endsWith(ext));
}

/**
 * Check if URL is from CDN
 */
function isCDNResource(href) {
    const cdnHosts = ['cdn.jsdelivr.net', 'cdnjs.cloudflare.com', 'fonts.googleapis.com', 'fonts.gstatic.com', 'unpkg.com'];
    return cdnHosts.some(host => href.includes(host));
}

/**
 * Cache First Strategy
 * Try cache first, fall back to network
 */
async function cacheFirst(request) {
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse) {
        return cachedResponse;
    }
    
    try {
        const networkResponse = await fetch(request);
        
        // Cache the new response
        if (networkResponse.ok) {
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.error('[SW] Cache first failed:', error);
        return getOfflineFallback(request);
    }
}

/**
 * Network First Strategy
 * Try network first, fall back to cache
 */
async function networkFirst(request) {
    try {
        const networkResponse = await fetch(request);
        
        // Cache the new response
        if (networkResponse.ok) {
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.log('[SW] Network first falling back to cache');
        
        const cachedResponse = await caches.match(request);
        
        if (cachedResponse) {
            return cachedResponse;
        }
        
        return getOfflineFallback(request);
    }
}

/**
 * Stale While Revalidate Strategy
 * Return cached version immediately, update cache in background
 */
async function staleWhileRevalidate(request) {
    const cache = await caches.open(CACHE_NAME);
    const cachedResponse = await caches.match(request);
    
    // Fetch from network in background
    const fetchPromise = fetch(request)
        .then((networkResponse) => {
            if (networkResponse.ok) {
                cache.put(request, networkResponse.clone());
            }
            return networkResponse;
        })
        .catch(() => {
            console.log('[SW] Stale while revalidate network failed');
        });
    
    // Return cached response immediately if available
    return cachedResponse || fetchPromise || getOfflineFallback(request);
}

/**
 * Network Only Strategy
 * Only use network, no caching
 */
async function networkOnly(request) {
    try {
        return await fetch(request);
    } catch (error) {
        return getOfflineFallback(request);
    }
}

/**
 * Get offline fallback response
 */
async function getOfflineFallback(request) {
    const url = new URL(request.url);
    
    // For HTML requests, return offline page
    if (request.headers.get('accept')?.includes('text/html') || url.pathname.endsWith('.html')) {
        const offlinePage = await caches.match('/public/offline.html');
        if (offlinePage) {
            return offlinePage;
        }
    }
    
    // For images, return placeholder
    if (request.headers.get('accept')?.includes('image')) {
        return new Response(
            '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200"><rect fill="#f0f0f0" width="200" height="200"/><text fill="#999" font-family="sans-serif" font-size="14" x="50%" y="50%" text-anchor="middle" dy=".3em">Offline</text></svg>',
            { headers: { 'Content-Type': 'image/svg+xml' } }
        );
    }
    
    // For API requests, return error JSON
    if (url.pathname.startsWith('/api/')) {
        return new Response(
            JSON.stringify({ error: 'Offline', message: 'Bạn đang offline. Vui lòng kiểm tra kết nối mạng.' }),
            { 
                status: 503,
                headers: { 'Content-Type': 'application/json' } 
            }
        );
    }
    
    // Generic offline response
    return new Response('Offline', { status: 503 });
}

// ====================================
// BACKGROUND SYNC
// ====================================
self.addEventListener('sync', (event) => {
    console.log('[SW] Background sync:', event.tag);
    
    if (event.tag === 'sync-flashcard-progress') {
        event.waitUntil(syncFlashcardProgress());
    }
    
    if (event.tag === 'sync-learning-progress') {
        event.waitUntil(syncLearningProgress());
    }
});

/**
 * Sync flashcard progress to server
 */
async function syncFlashcardProgress() {
    try {
        // Get pending sync data from IndexedDB
        const pendingData = await getPendingSyncData('flashcard-progress');
        
        if (pendingData && pendingData.length > 0) {
            const response = await fetch('/api/flashcard/sync', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(pendingData)
            });
            
            if (response.ok) {
                await clearPendingSyncData('flashcard-progress');
                console.log('[SW] Flashcard progress synced successfully');
            }
        }
    } catch (error) {
        console.error('[SW] Flashcard sync failed:', error);
        throw error; // Re-throw to retry
    }
}

/**
 * Sync learning progress to server
 */
async function syncLearningProgress() {
    try {
        const pendingData = await getPendingSyncData('learning-progress');
        
        if (pendingData && pendingData.length > 0) {
            const response = await fetch('/api/progress/sync', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(pendingData)
            });
            
            if (response.ok) {
                await clearPendingSyncData('learning-progress');
                console.log('[SW] Learning progress synced successfully');
            }
        }
    } catch (error) {
        console.error('[SW] Learning progress sync failed:', error);
        throw error;
    }
}

// ====================================
// PUSH NOTIFICATIONS
// ====================================
self.addEventListener('push', (event) => {
    console.log('[SW] Push notification received');
    
    let data = {
        title: 'English Learning',
        body: 'Đến lúc ôn tập rồi!',
        icon: '/assets/images/icons/icon-192x192.png',
        badge: '/assets/images/icons/badge-72x72.png',
        tag: 'default',
        data: { url: '/public/dashboard.html' }
    };
    
    if (event.data) {
        try {
            data = { ...data, ...event.data.json() };
        } catch (e) {
            data.body = event.data.text();
        }
    }
    
    const options = {
        body: data.body,
        icon: data.icon,
        badge: data.badge,
        tag: data.tag,
        data: data.data,
        vibrate: [100, 50, 100],
        actions: [
            { action: 'open', title: 'Mở ứng dụng' },
            { action: 'dismiss', title: 'Bỏ qua' }
        ],
        requireInteraction: false
    };
    
    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});

self.addEventListener('notificationclick', (event) => {
    console.log('[SW] Notification clicked');
    
    event.notification.close();
    
    if (event.action === 'dismiss') {
        return;
    }
    
    const urlToOpen = event.notification.data?.url || '/public/dashboard.html';
    
    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true })
            .then((windowClients) => {
                // Check if there's already a window open
                for (const client of windowClients) {
                    if (client.url.includes(urlToOpen) && 'focus' in client) {
                        return client.focus();
                    }
                }
                
                // Open new window
                if (clients.openWindow) {
                    return clients.openWindow(urlToOpen);
                }
            })
    );
});

// ====================================
// MESSAGE HANDLING
// ====================================
self.addEventListener('message', (event) => {
    console.log('[SW] Message received:', event.data);
    
    if (event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data.type === 'CLEAR_CACHE') {
        event.waitUntil(
            caches.delete(CACHE_NAME).then(() => {
                event.ports[0].postMessage({ success: true });
            })
        );
    }
    
    if (event.data.type === 'CACHE_URLS') {
        event.waitUntil(
            caches.open(CACHE_NAME).then((cache) => {
                return cache.addAll(event.data.urls);
            })
        );
    }
    
    if (event.data.type === 'GET_CACHE_SIZE') {
        event.waitUntil(
            getCacheSize().then((size) => {
                event.ports[0].postMessage({ size });
            })
        );
    }
});

// ====================================
// UTILITY FUNCTIONS
// ====================================

/**
 * Get total cache size
 */
async function getCacheSize() {
    const cache = await caches.open(CACHE_NAME);
    const keys = await cache.keys();
    let totalSize = 0;
    
    for (const key of keys) {
        const response = await cache.match(key);
        if (response) {
            const blob = await response.blob();
            totalSize += blob.size;
        }
    }
    
    return totalSize;
}

/**
 * Get pending sync data from IndexedDB
 * (Placeholder - actual implementation in db.js)
 */
async function getPendingSyncData(storeName) {
    // This will be implemented through IndexedDB
    return [];
}

/**
 * Clear pending sync data from IndexedDB
 * (Placeholder - actual implementation in db.js)
 */
async function clearPendingSyncData(storeName) {
    // This will be implemented through IndexedDB
    return true;
}

console.log('[SW] Service Worker loaded');
