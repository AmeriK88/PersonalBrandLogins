
{% load static %}

const CACHE_VERSION = 'v5';
const CACHE_PREFIX = 'gregloginsjr-';
const CACHE_NAME = `${CACHE_PREFIX}${CACHE_VERSION}`;

// Precache shared application assets.
// Page-specific stylesheets are cached when visited.
const URLS_TO_CACHE = [
  // Global CSS
  '{% static "css/main.css" %}',
  '{% static "css/animations.css" %}',
  '{% static "css/layout.css" %}',
  '{% static "css/components.css" %}',

  // Shared JavaScript
  '{% static "js/core/stats.js" %}',
  '{% static "js/core/animate-onload.js" %}',
  '{% static "js/core/share.js" %}',

  // Branding
  '{% static "img/greg-logo.png" %}',
];

// INSTALL
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(URLS_TO_CACHE);
    })
  );

  self.skipWaiting();
});

// ACTIVATE
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) =>
        Promise.all(
          keys
            .filter(
              (key) =>
                key.startsWith(CACHE_PREFIX) &&
                key !== CACHE_NAME
            )
            .map((key) => caches.delete(key))
        )
      )
      .then(() => self.clients.claim())
  );
});

// FETCH
self.addEventListener('fetch', (event) => {
  const request = event.request;

  if (request.method !== 'GET') {
    return;
  }

  // Safari audio/video compatibility.
  // Never intercept Range requests or media files.
  const destination = request.destination;

  if (
    request.headers.has('range') ||
    destination === 'audio' ||
    destination === 'video' ||
    /\.(mp3|m4a|wav|ogg|flac|mp4|m4v|mov|webm)(\?|$)/i.test(request.url)
  ) {
    return;
  }

  const acceptHeader = request.headers.get('accept') || '';

  const isHtmlRequest =
    request.mode === 'navigate' ||
    acceptHeader.includes('text/html');

  if (isHtmlRequest) {
    // Network-first for HTML.
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response.ok && response.type === 'basic') {
            const responseClone = response.clone();

            event.waitUntil(
              caches.open(CACHE_NAME).then((cache) =>
                cache.put(request, responseClone)
              )
            );
          }

          return response;
        })
        .catch(async () => {
          const cachedResponse = await caches.match(request);

          return cachedResponse || Response.error();
        })
    );

    return;
  }

  // Only cache same-origin static resources.
  const url = new URL(request.url);

  const isSameOrigin = url.origin === self.location.origin;

  const isStaticAsset =
    ['style', 'script', 'image', 'font'].includes(destination);

  if (!isSameOrigin || !isStaticAsset) {
    return;
  }

  // Cache-first for static assets.
  event.respondWith(
    caches.match(request).then(async (cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }

      const response = await fetch(request);

      if (response.ok && response.type === 'basic') {
        const responseClone = response.clone();

        event.waitUntil(
          caches.open(CACHE_NAME).then((cache) =>
            cache.put(request, responseClone)
          )
        );
      }

      return response;
    })
  );
});
