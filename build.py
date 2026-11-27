#!/usr/bin/env python3
"""Construit la version autonome (GitHub Pages, hors ligne) dans docs/ à partir de scores-skull-king.html.

Usage : python3 build.py
"""
import hashlib, json, re
from pathlib import Path

ROOT = Path(__file__).parent
DOCS = ROOT / "docs"
src = (ROOT / "scores-skull-king.html").read_text(encoding="utf8")

# La page source est écrite pour claude.ai (qui ajoute l'en-tête HTML) : on retire ce qui lui est propre.
src = src.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', "")
src = re.sub(r"<title>.*?</title>\n", "", src, count=1)
# Le lien Google Fonts reste : il sert la police du texte quand il y a du réseau ; hors ligne, la police système prend le relais.
assert "<title>" not in src

HEAD = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Scores Skull King</title>
<meta name="robots" content="noindex">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Skull King">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="theme-color" content="#EAD9B5">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icon-180.png">
<style>
:root{color-scheme:light;box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
body{margin:0;padding:0}
[hidden]{display:none!important}
@font-face{font-family:"Pirata One";font-style:normal;font-weight:400;font-display:swap;src:url(pirata-one.woff2) format("woff2")}
</style>
</head>
<body>
"""
TAIL = """
<script>
if ('serviceWorker' in navigator) navigator.serviceWorker.register('sw.js').catch(() => {});
</script>
</body>
</html>
"""
index = HEAD + src + TAIL
(DOCS / "index.html").write_text(index, encoding="utf8")

FILES = ["./", "index.html", "manifest.webmanifest", "pirata-one.woff2", "icon-180.png", "icon-512.png"]
# La version change aussi quand une icône change, pour que les appareils rechargent le cache.
version = hashlib.sha256(index.encode("utf8") + b"".join((DOCS / f).read_bytes() for f in ("icon-180.png", "icon-512.png"))).hexdigest()[:12]
SW = """// Généré par build.py : ne pas modifier à la main.
const CACHE = 'skull-king-scores-%s';
const FILES = %s;

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});
// Page : réseau d'abord (pour recevoir les mises à jour), cache si hors ligne. Le reste : cache d'abord.
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  if (e.request.mode === 'navigate') {
    e.respondWith(fetch(e.request)
      .then(r => { const copy = r.clone(); caches.open(CACHE).then(c => c.put('index.html', copy)); return r; })
      .catch(() => caches.match('index.html')));
    return;
  }
  e.respondWith(caches.match(e.request).then(hit => hit || fetch(e.request)));
});
""" % (version, json.dumps(FILES))
(DOCS / "sw.js").write_text(SW, encoding="utf8")

MANIFEST = {
    "name": "Scores Skull King", "short_name": "Skull King", "lang": "fr",
    "start_url": "./", "scope": "./", "display": "standalone",
    "background_color": "#EAD9B5", "theme_color": "#EAD9B5",
    "icons": [
        {"src": "icon-180.png", "sizes": "180x180", "type": "image/png"},
        {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"},
    ],
}
(DOCS / "manifest.webmanifest").write_text(json.dumps(MANIFEST, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
print("docs/ construit, version", version)
