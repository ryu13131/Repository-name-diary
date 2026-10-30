// オフラインでも開けるようにするための仕組み
const CACHE = 'mydiet-v5';
const FILES = [
  './diet.html', './index.html', './manifest.webmanifest', './diary.webmanifest',
  './icons/diary-180.png', './icons/diary-192.png', './icons/diary-512.png',
  './icons/icon-180.png', './icons/icon-192.png', './icons/icon-512.png',
  './coach.html', './coach.webmanifest', './icons/coach-180.png', './icons/coach-192.png', './icons/coach-512.png',
  'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js',
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => Promise.allSettled(FILES.map(f => c.add(f)))).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});

// オフライン時に表示するページ
function fallbackPage(url) {
  const path = new URL(url).pathname;
  return ['diet.html', 'coach.html'].map(p => './' + p).find(p => path.endsWith(p.slice(2))) || './index.html';
}

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  if (new URL(e.request.url).hostname === 'api.anthropic.com') return;
  const isPage = e.request.mode === 'navigate';
  // GitHub上の記録は最新を優先し、オフライン時だけ前回の内容を表示
  if (new URL(e.request.url).hostname === 'raw.githubusercontent.com') {
    e.respondWith(fetch(e.request).then(res => {
      const copy = res.clone();
      const key = e.request.url.split('?')[0];
      if (res.ok) caches.open(CACHE).then(c => c.put(key, copy));
      return res;
    }).catch(() => caches.match(e.request.url.split('?')[0]).then(r => r || Response.error())));
    return;
  }
  if (isPage) {
    // ページは最新を優先し、オフライン時は保存しておいたものを表示
    e.respondWith(fetch(e.request).then(res => {
      const copy = res.clone();
      caches.open(CACHE).then(c => c.put(e.request, copy));
      return res;
    }).catch(() => caches.match(e.request, { ignoreSearch: true }).then(r => r || caches.match(fallbackPage(e.request.url)))));
  } else {
    e.respondWith(caches.match(e.request).then(r => r || fetch(e.request).then(res => {
      if (res.ok || res.type === 'opaque') { const copy = res.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); }
      return res;
    })));
  }
});
