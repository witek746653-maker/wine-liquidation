// Service Worker для PWA (кеш “обложки” приложения)
// **Service worker**: скрипт, который может хранить файлы оффлайн и ускорять загрузку.

const CACHE_NAME = "wine-liquidation-v1";
const ASSETS = [
  "./",
  "./index.html",
  "./wine-liquidation-list.html",
  "./manifest.webmanifest",
  "./icons/icon.svg",
  "./images/wine-liquidation-list-background.jpg",
  "./%D0%94%D0%BE%D0%BF%D1%80%D0%BE%D0%B4%D0%B0%D0%B5%D0%BC%20%D0%B2%D0%B8%D0%BD%D0%B0%20(1).xlsx"
];

self.addEventListener("install", (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS);
    })
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    Promise.all([
      self.clients.claim(),
      caches.keys().then((keys) =>
        Promise.all(keys.map((k) => (k === CACHE_NAME ? Promise.resolve() : caches.delete(k))))
      ),
    ])
  );
});

// Стратегия: сначала кеш, потом сеть (для “обложки”)
self.addEventListener("fetch", (event) => {
  const req = event.request;

  // Не трогаем не-GET запросы
  if (req.method !== "GET") return;

  const url = new URL(req.url);

  // Не кешируем запросы к Supabase (данные всегда свежие)
  if (url.hostname.includes("supabase.co")) return;

  event.respondWith(
    caches.match(req).then((cached) => {
      if (cached) return cached;
      return fetch(req)
        .then((res) => {
          // Положим в кеш только “наши” файлы
          if (res.ok && url.origin === self.location.origin) {
            const copy = res.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(req, copy));
          }
          return res;
        })
        .catch(() => cached);
    })
  );
});

