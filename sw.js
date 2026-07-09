const VERSION = "ssc-v2";
const ASSETS = ["./", "index.html", "chapters.json", "manifest.json", "icon-192.png", "icon-512.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== VERSION).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

// Cache-first for same-origin; network-first fallback for fonts etc.
self.addEventListener("fetch", e => {
  const url = new URL(e.request.url);
  if (url.origin === location.origin) {
    e.respondWith(
      caches.match(e.request).then(hit => hit ||
        fetch(e.request).then(res => {
          const copy = res.clone();
          caches.open(VERSION).then(c => c.put(e.request, copy));
          return res;
        })
      )
    );
  } else {
    // Google Fonts: try cache, then network, cache successful responses
    e.respondWith(
      caches.match(e.request).then(hit => hit ||
        fetch(e.request).then(res => {
          const copy = res.clone();
          caches.open(VERSION).then(c => c.put(e.request, copy));
          return res;
        }).catch(() => new Response("", {status: 503}))
      )
    );
  }
});
