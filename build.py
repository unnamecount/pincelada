"""Construye la app instalable a partir de pincelada.html (la misma página que el artefacto de Claude).

Uso:  python build.py
Crea index.html, sw.js y version.json con la versión más reciente de cambios.json.
Para publicar una actualización: añade una entrada nueva ARRIBA en cambios.json, ejecuta este script,
y sube los cambios a GitHub (git add -A && git commit && git push). La app instalada avisa sola.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
src = (ROOT / 'pincelada.html').read_text(encoding='utf-8')
cambios = json.loads((ROOT / 'cambios.json').read_text(encoding='utf-8'))
ultima = cambios[0]
VER = ultima['version']

MARK = '<!-- ============ GALERÍA ============ -->'
assert src.count(MARK) == 1, 'No encuentro el inicio de la galería en pincelada.html'
head_part, body_part = src.split(MARK)

HEAD = f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover,user-scalable=no">
<meta name="description" content="Dibuja y pinta: pinceles, acuarela que mezcla colores, capas, fotos y modo 3D.">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" type="image/png" sizes="192x192" href="icon-192.png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<meta name="theme-color" content="#f2eff1" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#141113" media="(prefers-color-scheme: dark)">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Pincelada">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<script>window.PINCELADA_VERSION = {json.dumps(VER)}; window.ESTUDIO_URL = "../";</script>
'''
html = HEAD + head_part + '</head>\n<body>\n' + MARK + body_part + '\n</body>\n</html>\n'
(ROOT / 'index.html').write_text(html, encoding='utf-8')

SHELL = ['./index.html', './manifest.webmanifest', './icon-192.png', './icon-512.png', './icon-maskable-512.png', './apple-touch-icon.png']
CDN = [
    'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js',
    'https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js',
    'https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/TransformControls.js',
    'https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js',
]
for u in CDN:
    assert u in src, f'pincelada.html ya no usa {u}: actualiza la lista CDN de build.py'

SW = f'''/* Pincelada — service worker. Lo genera build.py: no lo edites a mano. */
const VERSION = {json.dumps(VER)};
const CACHE = 'pincelada-app-' + VERSION;
const RT = 'pincelada-externos';
const SHELL = {json.dumps(SHELL)};
const CDN = {json.dumps(CDN, indent=2)};
const EXT_HOSTS = ['cdnjs.cloudflare.com', 'cdn.jsdelivr.net', 'fonts.googleapis.com', 'fonts.gstatic.com'];

self.addEventListener('install', e => {{
  e.waitUntil((async () => {{
    const c = await caches.open(CACHE);
    await c.addAll(SHELL.map(u => new Request(u, {{cache: 'reload'}})));
    const rt = await caches.open(RT);
    await Promise.all(CDN.map(async u => {{
      if (await rt.match(u)) return;
      try {{ await rt.put(u, await fetch(u, {{mode: 'no-cors'}})); }} catch (err) {{}}
    }}));
  }})());
}});

self.addEventListener('activate', e => {{
  e.waitUntil((async () => {{
    for (const k of await caches.keys()) if (k.startsWith('pincelada-app-') && k !== CACHE) await caches.delete(k);
    await self.clients.claim();
  }})());
}});

self.addEventListener('message', e => {{ if (e.data === 'skip') self.skipWaiting(); }});

// La página se pide siempre a internet primero (así llegan los arreglos); sin conexión se usa la guardada
async function pagina(req) {{
  const c = await caches.open(CACHE);
  try {{
    const res = await Promise.race([
      fetch(req.url, {{cache: 'no-cache', credentials: 'same-origin'}}),
      new Promise(r => setTimeout(() => r(null), 6000))
    ]);
    if (res && res.ok) {{ c.put('./index.html', res.clone()); return res; }}
    throw new Error(res ? 'http ' + res.status : 'lento');
  }} catch (err) {{
    return (await c.match('./index.html')) || (await caches.match(req)) || Response.error();
  }}
}}

self.addEventListener('fetch', e => {{
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin === location.origin) {{
    if (url.pathname.endsWith('/version.json')) return;
    if (req.mode === 'navigate' || url.pathname.endsWith('/') || url.pathname.endsWith('/index.html')) {{ e.respondWith(pagina(req)); return; }}
    e.respondWith(caches.match(req, {{ignoreSearch: true}}).then(r => r || fetch(req).then(res => {{
      if (res.ok) {{ const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); }}
      return res;
    }})));
    return;
  }}
  if (EXT_HOSTS.includes(url.hostname)) {{
    e.respondWith(caches.match(req).then(r => r || fetch(req).then(res => {{
      if (res.ok || res.type === 'opaque') {{ const copy = res.clone(); caches.open(RT).then(c => c.put(req, copy)); }}
      return res;
    }})));
  }}
}});
'''
(ROOT / 'sw.js').write_text(SW, encoding='utf-8')
(ROOT / 'version.json').write_text(json.dumps({'version': VER, 'fecha': ultima.get('fecha'), 'notas': ultima.get('notas', [])}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('Pincelada', VER, '-> index.html, sw.js, version.json')
