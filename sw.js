self.addEventListener('install', e => {
  e.waitUntil(
    caches.open('lnmd-cache').then(cache => {
      return cache.addAll(['index.html', 'https://cdn.tailwindcss.com']);
    })
  );
});

self.addEventListener('fetch', e => {
  e.respondWith(
    caches.match(e.request).then(response => {
      return response || fetch(e.request);
    })
  );
});
