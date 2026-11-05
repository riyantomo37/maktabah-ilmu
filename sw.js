// Service worker Maktabah Ilmu
// - Halaman utama: ambil dari jaringan dulu (selalu versi terbaru), cadangan dari cache bila offline.
// - Data kitab, indeks pencarian, ikon & library: dari cache, lalu diperbarui di latar (stale-while-revalidate).
// - Permintaan PDF per bagian (header Range) dilewatkan langsung ke jaringan.
const VERSION = 'v2';
const SHELL = `shell-${VERSION}`;
const DATA = 'data-v1';
const SHELL_FILES = ['./', 'index.html', 'manifest.webmanifest', 'vendor/page-flip.browser.js', 'icons/icon-192.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(SHELL).then(c => c.addAll(SHELL_FILES)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k.startsWith('shell-') && k !== SHELL).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET' || req.headers.has('range')) return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;
  const isPage = req.mode === 'navigate' || url.pathname.endsWith('/') || url.pathname.endsWith('/index.html')
    || url.pathname.endsWith('/d/index.json') || url.pathname.endsWith('/s/books.json');
  if (isPage && !req.mode.startsWith('navigate') && !url.pathname.endsWith('/') && !url.pathname.endsWith('index.html')) {
    e.respondWith(fetch(req, { cache: 'no-store' }).then(res => {
      const copy = res.clone(); caches.open(DATA).then(c => c.put(req, copy)); return res;
    }).catch(() => caches.match(req)));
    return;
  }
  if (isPage) {
    e.respondWith(fetch(req, { cache: 'no-store' }).then(res => {
      const copy = res.clone(); caches.open(SHELL).then(c => c.put('index.html', copy)); return res;
    }).catch(() => caches.match('index.html')));
    return;
  }
  if (/\/(d|s|icons|vendor)\//.test(url.pathname) || url.pathname.endsWith('.webmanifest')) {
    e.respondWith(caches.open(DATA).then(async c => {
      const hit = await c.match(req);
      const net = fetch(req).then(res => { if (res.ok) c.put(req, res.clone()); return res; }).catch(() => hit);
      return hit || net;
    }));
  }
});
