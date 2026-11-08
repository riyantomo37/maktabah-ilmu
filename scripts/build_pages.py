"""Halaman statis per kitab (k/<id>.html) + sitemap.xml + robots.txt, agar setiap kitab
bisa ditemukan mesin pencari dan tampil rapi saat tautannya dibagikan (Open Graph).

Pakai:  python -X utf8 scripts/build_pages.py
Judul Indonesia diambil dari objek LOCAL.id di index.html; data kitab dari d/index.json.
Halaman ini hanya pintu masuk: tombolnya membuka kitab di aplikasi utama (index.html#kitab-<id>).
"""
import html, json, os, re

BASE = 'https://riyantomo37.github.io/maktabah-ilmu/'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
i = src.index('const LOCAL=')
j = src.index('\n id:{', i) + 5
k = src.index('},\n', j)
ID = {m.group(1): json.loads('"' + m.group(2) + '"') for m in re.finditer(r'(\w+):"((?:[^"\\]|\\.)*)"', src[j:k])}
# kategori per kitab (CATS) dan label Indonesia kategori
cats = json.loads(re.search(r'const CATS=(\[.*?\]\]\]);', src).group(1))
UIid = src[src.index('\n id:{', src.index('const UI')):]
lab = lambda key: (re.search(key + r':"([^"]*)"', UIid) or [None, key])[1]
catof = {}
for c in cats:
    for b in c[3]: catof[b] = (lab(c[1]), c[2])

idx = json.load(open(os.path.join(ROOT, 'd', 'index.json'), encoding='utf-8'))
by = {b['id']: b for b in idx}
LN = {'ara': 'Arab', 'ind': 'Indonesia', 'eng': 'Inggris', 'jpn': 'Jepang'}
os.makedirs(os.path.join(ROOT, 'k'), exist_ok=True)
for f in os.listdir(os.path.join(ROOT, 'k')):
    if f.endswith('.html'): os.remove(os.path.join(ROOT, 'k', f))
e = html.escape
urls = [BASE]
for b in idx:
    bid = b['id']
    title = ID.get(bid) or b.get('en') or b['ar']
    langs = set(b['langs'])
    for p in b.get('pairs', []):
        if p in by: langs |= set(by[p]['langs'])
    lang_txt = ', '.join(LN[x] for x in ('ara', 'ind', 'eng', 'jpn') if x in langs)
    auth = b.get('auth', '')
    cat = catof.get(bid) or next((catof[p] for p in b.get('pairs', []) if p in catof), ('', ''))
    mt = ' (sebagian terjemah dibuat AI)' if b.get('mt') else ''
    desc = (f"Baca {title} ({b['ar']})" + (f" karya {auth}" if auth else '') +
            f" secara gratis di Maktabah Ilmu: teks {lang_txt}{mt}. Tanpa daftar, tanpa iklan.")
    cover = b.get('cover') or (f'covers/{bid}.webp' if os.path.exists(os.path.join(ROOT, 'covers', bid + '.webp')) else 'og.png')
    secs = b.get('secs', [])
    sec_html = ''.join(
        f'<li><a href="../#read-{bid}-{str(s["k"]).replace(".", "_")}">{e(s["t"])}</a></li>' for s in secs[:60])
    more = f'<p class="more">… dan {len(secs) - 60} bab lainnya.</p>' if len(secs) > 60 else ''
    ld = {"@context": "https://schema.org", "@type": "Book", "name": title, "alternateName": b['ar'],
          "inLanguage": sorted(langs), "url": BASE + f'k/{bid}.html', "isAccessibleForFree": True,
          "publisher": {"@type": "Organization", "name": "Maktabah Ilmu"}}
    if auth: ld["author"] = {"@type": "Person", "name": auth}
    page = f'''<!doctype html>
<html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} · {e(b['ar'])} — Maktabah Ilmu</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{BASE}k/{bid}.html">
<meta property="og:type" content="book"><meta property="og:site_name" content="Maktabah Ilmu · مكتبة العلم">
<meta property="og:title" content="{e(title)} · {e(b['ar'])}"><meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{BASE}k/{bid}.html"><meta property="og:image" content="{BASE}{cover}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#1E3D34">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>body{{margin:0;background:#E9ECE6;color:#18241F;font:16px/1.6 system-ui,sans-serif}}main{{max-width:760px;margin:auto;padding:28px 18px 60px}}
a{{color:#234A73}}.top{{font-weight:700;text-decoration:none;color:#18241F}}.ar{{font-size:1.6rem;color:#94701F;direction:rtl;font-family:'Amiri','Scheherazade New',serif}}
h1{{margin:.2em 0;font-size:1.9rem;line-height:1.2}}.meta{{color:#5A6A62}}.btn{{display:inline-block;background:#18241F;color:#FAF9F4;padding:11px 20px;border-radius:999px;text-decoration:none;font-weight:600;margin:14px 8px 0 0}}
.cover{{float:right;width:150px;margin:0 0 12px 18px;border-radius:6px;box-shadow:0 6px 18px rgba(0,0,0,.2)}}ol{{padding-left:1.4em}}li a{{color:#18241F}}.more{{color:#5A6A62}}</style>
</head><body><main>
<a class="top" href="../">← Maktabah Ilmu · مكتبة العلم</a>
{f'<img class="cover" src="../{cover}" alt="Sampul {e(title)}">' if cover != 'og.png' else ''}
<p class="meta">{e(cat[0])}</p>
<div class="ar">{e(b['ar'])}</div>
<h1>{e(title)}</h1>
<p class="meta">{e(auth)}{f' · wafat {b["died"]} H' if b.get('died') else ''}<br>Tersedia: {e(lang_txt)}{e(mt)} · {b.get('total', 0):,} {('halaman' if b.get('kind') == 'pdf' else 'teks')}</p>
<p>{e(desc)}</p>
<a class="btn" href="../#kitab-{bid}">Buka kitab ini</a><a class="btn" style="background:#fff;color:#18241F;border:1px solid #C9D0C7" href="../">Lihat lemari ilmu</a>
<h2>Daftar isi</h2><ol>{sec_html}</ol>{more}
<p class="meta" style="margin-top:30px">Sumber: {e(b.get('src', ''))}</p>
</main></body></html>'''
    open(os.path.join(ROOT, 'k', bid + '.html'), 'w', encoding='utf-8').write(page)
    urls.append(BASE + f'k/{bid}.html')
open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8').write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    ''.join(f'<url><loc>{u}</loc></url>\n' for u in urls) + '</urlset>\n')
open(os.path.join(ROOT, 'robots.txt'), 'w', encoding='utf-8').write(f'User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n')
print(len(urls) - 1, 'halaman kitab')
