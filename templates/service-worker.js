{% load static %}

const CACHE_VERSION = 'v2';  // <-- súbelo cuando hagas cambios importantes
const CACHE_NAME = `gregloginsjr-${CACHE_VERSION}`;

// Rutas que quieres precachear (app shell: solo estáticos, no hace falta HTML)
const URLS_TO_CACHE = [
  '{% static "css/main.css" %}',
  '{% static "js/core/stats.js" %}',
  '{% static "js/core/animate-onload.js" %}',
  '{% static "js/core/share.js" %}',
  '{% static "img/greg-logo.png" %}',
];

// INSTALL: precache básico
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(URLS_TO_CACHE);
    })
  );
  self.skipWaiting();
});

// ACTIVATE: limpia cachés antiguas
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      )
    )
  );
  self.clients.claim();
});

// FETCH: network-first para HTML, cache-first para assets
self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;

  const request = event.request;
  const acceptHeader = request.headers.get('accept') || '';

  const isHtmlRequest =
    request.mode === 'navigate' || acceptHeader.includes('text/html');

  if (isHtmlRequest) {
    // Navegación/HTML -> network-first
    event.respondWith(
      fetch(request)
        .then((response) => {
          const respClone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(request, respClone);
          });
          return response;
        })
        .catch(() => {
          // Si no hay red, intenta servir la versión cacheada
          return caches.match(request);
        })
    );
  } else {
    // Assets (CSS, JS, imágenes) -> cache-first
    event.respondWith(
      caches.match(request).then((cached) => {
        if (cached) {
          return cached;
        }
        return fetch(request)
          .then((response) => {
            const respClone = response.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(request, respClone);
            });
            return response;
          });
      })
    );
  }
});
