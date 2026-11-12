/* Pincelada — service worker. Lo genera build.py: no lo edites a mano. */
const VERSION = "1.1.1";
const CACHE = 'pincelada-app-' + VERSION;
const RT = 'pincelada-externos';
const SHELL = ["./index.html", "./manifest.webmanifest", "./icon-192.png", "./icon-512.png", "./icon-maskable-512.png", "./apple-touch-icon.png"];
const CDN = [
  "https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js",
  "https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js",
  "https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/TransformControls.js",
  "https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"
];
const EXT_HOSTS = ['cdnjs.cloudflare.com', 'cdn.jsdelivr.net', 'fonts.googleapis.com', 'fonts.gstatic.com'];

self.addEventListener('install', e => {
  e.waitUntil((async () => {
    const c = await caches.open(CACHE);
    await c.addAll(SHELL.map(u => new Request(u, {cache: 'reload'})));
    const rt = await caches.open(RT);
    await Promise.all(CDN.map(async u => {
      if (await rt.match(u)) return;
      try { await rt.put(u, await fetch(u, {mode: 'no-cors'})); } catch (err) {}
    }));
  })());
});

self.addEventListener('activate', e => {
  e.waitUntil((async () => {
    for (const k of await caches.keys()) if (k.startsWith('pincelada-app-') && k !== CACHE) await caches.delete(k);
    await self.clients.claim();
  })());
});

self.addEventListener('message', e => { if (e.data === 'skip') self.skipWaiting(); });

// La página se pide siempre a internet primero (así llegan los arreglos); sin conexión se usa la guardada
async function pagina(req) {
  const c = await caches.open(CACHE);
  try {
    const res = await Promise.race([
      fetch(req.url, {cache: 'no-cache', credentials: 'same-origin'}),
      new Promise(r => setTimeout(() => r(null), 6000))
    ]);
    if (res && res.ok) { c.put('./index.html', res.clone()); return res; }
    throw new Error(res ? 'http ' + res.status : 'lento');
  } catch (err) {
    return (await c.match('./index.html')) || (await caches.match(req)) || Response.error();
  }
}

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin === location.origin) {
    if (url.pathname.endsWith('/version.json')) return;
    if (req.mode === 'navigate' || url.pathname.endsWith('/') || url.pathname.endsWith('/index.html')) { e.respondWith(pagina(req)); return; }
    e.respondWith(caches.match(req, {ignoreSearch: true}).then(r => r || fetch(req).then(res => {
      if (res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); }
      return res;
    })));
    return;
  }
  if (EXT_HOSTS.includes(url.hostname)) {
    e.respondWith(caches.match(req).then(r => r || fetch(req).then(res => {
      if (res.ok || res.type === 'opaque') { const copy = res.clone(); caches.open(RT).then(c => c.put(req, copy)); }
      return res;
    })));
  }
});
