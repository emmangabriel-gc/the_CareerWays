const CACHE_NAME = 'careerways-v1';

const ASSETS = [
  '/index.html',
  '/dashboard.html',
  '/assessment.html',
  '/favorites.html',
  '/forgot-password.html',
  '/profile.html',
  '/results.html',

  '/css/style.css',
  '/css/index.css',
  '/css/dashboard.css',
  '/css/assessment.css',
  '/css/favorites.css',
  '/css/forgot-password.css',
  '/css/profile.css',
  '/css/results.css',
  '/css/verify-email.css',

  '/js/index.js',
  '/js/dashboard.js',
  '/js/assessment.js',
  '/js/favorites.js',
  '/js/forgot-password.js',
  '/js/profile.js',
  '/js/results.js',

  '/assets/logo.png',
  '/assets/web-app-manifest-192x192.png',
  '/assets/web-app-manifest-512x512.png',

  '/manifest.json'
];

// ── Install: cache all static assets ──────────────────────────────────────
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(ASSETS))
      .then(() => self.skipWaiting())
  );
});

// ── Activate: remove old caches ────────────────────────────────────────────
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys
          .filter(key => key !== CACHE_NAME)
          .map(key => caches.delete(key))
      )
    ).then(() => self.clients.claim())
  );
});

// ── Fetch: cache-first for assets, network for API ────────────────────────
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);

  // Always go to network for API calls — never cache these
  if (url.pathname.startsWith('/api/')) {
    e.respondWith(fetch(e.request));
    return;
  }

  // Cache-first for everything else
  e.respondWith(
    caches.match(e.request).then(cached => {
      if (cached) return cached;

      return fetch(e.request).then(response => {
        if (e.request.method === 'GET' && response.status === 200) {
          const copy = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(e.request, copy));
        }
        return response;
      });
    }).catch(() => {
      if (e.request.mode === 'navigate') {
        return caches.match('/index.html');
      }
    })
  );
});
