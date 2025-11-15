{% load static %}
/* service-worker.js — Greg Logins Jr */

const CACHE_NAME = 'gregloginsjr-v1';

// Rutas que quieres precachear (app shell)
const URLS_TO_CACHE = [
  '/',       
  '/career/',               
  '/highlights/',
  '/blog/',
  '/contact/',
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

// FETCH: estrategia "cache first con actualización en segundo plano"
self.addEventListener('fetch', (event) => {
  // Solo GET, no toques POST/PUT, etc.
  if (event.request.method !== 'GET') return;

  event.respondWith(
    caches.match(event.request).then((cached) => {
      const networkFetch = fetch(event.request)
        .then((response) => {
          // Guardamos copia en caché para la próxima
          const respClone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, respClone);
          });
          return response;
        })
        .catch(() => cached || Promise.reject('no-match'));

      // Si hay caché, responde ya; si no, espera red.
      return cached || networkFetch;
    })
  );
});
