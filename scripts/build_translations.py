"""Terjemah Inggris domain publik untuk kitab-kitab OpenITI.

Pemakaian:  python scripts/build_translations.py <folder_kerja> d
Mengunduh dari Wikisource dan Project Gutenberg, lalu menulis d/<id>-<n>.json
dan entri katalog dengan "pair" (id kitab Arab pasangannya).

Sumber (semuanya domain publik; penerjemah wafat lebih dari 70 tahun lalu):
- The Confessions of Al Ghazzali, terj. Claud Field (1909)        -> Wikisource
- The Alchemy of Happiness, terj. Claud Field (1910)              -> Wikisource
- The Improvement of Human Reason (Hayy ibn Yaqzan), terj. Simon Ockley (1708) -> Gutenberg #16831
"""
import json, os, re, sys, urllib.parse, urllib.request
from html.parser import HTMLParser

WORK, OUT = sys.argv[1], sys.argv[2]
os.makedirs(WORK, exist_ok=True)
UA = {'User-Agent': 'MaktabahIlmu-builder/1.0 (static library site)'}

def get(url, cache):
    p = os.path.join(WORK, cache)
    if not os.path.exists(p):
        import time
        for attempt in range(6):
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                    open(p, 'wb').write(r.read())
                break
            except urllib.error.HTTPError as e:
                if e.code != 429 or attempt == 5: raise
                time.sleep(10 * (attempt + 1))
        time.sleep(2)
    return open(p, encoding='utf-8').read()

class Paras(HTMLParser):
    """Ambil <p>/<h2-4> dari HTML Wikisource, abaikan header navigasi, catatan kaki & gaya."""
    SKIP = ('ws-noexport', 'wst-header', 'reference', 'references', 'mw-editsection', 'noprint')
    def __init__(self):
        super().__init__(); self.out = []; self.buf = None; self.kind = None; self.skip = 0; self.stack = []
    def handle_starttag(self, tag, a):
        cls = dict(a).get('class') or ''
        skipping = tag in ('style', 'script', 'sup') or any(c in cls for c in self.SKIP)
        if tag not in ('br', 'img', 'hr', 'meta', 'link', 'wbr'):
            self.stack.append(skipping)
            if skipping: self.skip += 1
        if self.skip: return
        if tag in ('p', 'h2', 'h3', 'h4', 'dd'):
            self.buf = []; self.kind = 'h' if tag[0] == 'h' else 'p'
        elif tag == 'br' and self.buf is not None:
            self.buf.append(' ')
    def handle_endtag(self, tag):
        if tag in ('br', 'img', 'hr', 'meta', 'link', 'wbr'): return
        if self.stack and self.stack.pop(): self.skip -= 1; return
        if self.skip: return
        if tag in ('p', 'h2', 'h3', 'h4', 'dd') and self.buf is not None:
            t = re.sub(r'\s+', ' ', ''.join(self.buf)).strip()
            if t: self.out.append((self.kind, t))
            self.buf = None
    def handle_data(self, d):
        if self.buf is not None and not self.skip: self.buf.append(d)

def wikisource(title, parts):
    secs = []
    for part in parts:
        page = f'{title}/{part}'
        url = 'https://en.wikisource.org/w/api.php?' + urllib.parse.urlencode(
            {'action': 'parse', 'page': page, 'prop': 'text', 'formatversion': 2, 'format': 'json'})
        html = json.loads(get(url, re.sub(r'\W+', '_', page) + '.json'))['parse']['text']
        p = Paras(); p.feed(html)
        items = []
        for k, t in p.out:
            if re.fullmatch(r'[\d\W]*', t) or t.startswith('Printed by') or t == 'Notes': continue
            if k == 'p' and len(t) < 90 and t.upper() == t: k = 'h'      # judul bab ditulis kapital sebagai <p>
            items.append((k, t))
        while items and items[-1][0] == 'h': items.pop()
        heads = [t for k, t in items if k == 'h' and not re.match(r'(CHAPTER|SECTION|THE CONFESSIONS|THE ALCHEMY)', t)]
        stitle = part + (' · ' + heads[0].title() if heads else '')
        secs.append((stitle, items))
    return secs

def gutenberg_hayy():
    t = get('https://www.gutenberg.org/cache/epub/16831/pg16831.txt', 'pg16831.txt')
    t = t[t.index('_Abu Jaaphar Ebn Tophail_'):t.index('\nAPPENDIX.')]
    blocks = re.split(r'\n\s*FOOTNOTES:\s*\n', t)
    secs = []
    for i, b in enumerate(blocks):
        b = re.sub(r'\[Footnote \d+:.*?\]\s*(?=\n\s*\n|\Z)', '', b, flags=re.S)   # isi catatan kaki
        b = re.sub(r'\[Illustration[^\]]*\]', '', b)
        b = re.sub(r'\[\d+\]', '', b)                                               # penanda catatan kaki
        paras = [re.sub(r'\s+', ' ', x).replace('_', '').strip() for x in re.split(r'\n\s*\n', b)]
        paras = [x for x in paras if x and not re.fullmatch(r'[\W\d]*', x) and not x.startswith('[Footnote')]
        if paras: secs.append(("Ibn Tufayl's Introduction" if not secs else 'The History of Hai Ebn Yokdhan', [('p', x) for x in paras]))
    return secs

BOOKS = [
 ('confessions', 'munqidh', dict(en='The Confessions of Al Ghazzali', ar='المنقذ من الضلال', auth='Imam al-Ghazali · tr. Claud Field (1909)',
   authar='الإمام أبو حامد الغزالي', died=505, cat='ghazali', src='Wikisource: The Confessions of Al Ghazzali (Claud Field, 1909), public domain'),
   lambda: wikisource('The Confessions of Al Ghazzali', ['Introduction'] + [f'Section {i}' for i in range(1, 9)])),
 ('alchemy', 'kimiya', dict(en='The Alchemy of Happiness', ar='كيمياء السعادة', auth='Imam al-Ghazali · tr. Claud Field (1910)',
   authar='الإمام أبو حامد الغزالي', died=505, cat='ghazali', src='Wikisource: The Alchemy of Happiness (Claud Field, 1910, from the Persian Kimiya-yi Sa\'adat), public domain'),
   lambda: wikisource('The Alchemy of Happiness (Field)', ['Introduction'] + [f'Chapter {r}' for r in 'I II III IV V VI VII VIII'.split()])),
 ('hayyen', 'hayy', dict(en='Hayy ibn Yaqzan (The Improvement of Human Reason)', ar='حي بن يقظان', auth='Ibn Tufayl · tr. Simon Ockley (1708)',
   authar='ابن طفيل', died=581, cat='rihlah', src='Project Gutenberg #16831 (Simon Ockley, 1708), public domain'),
   gutenberg_hayy),
]

def emit(bid, meta, secs):
    rows_by = []; n = 0
    for title, items in secs:
        rows = []
        for kind, txt in items:
            if kind == 'h':
                rows.append([n + 0.5, '', txt, '', '', '', '', '', 2])
            else:
                n += 1; rows.append([n, '', txt])
        if not any(len(r) == 3 for r in rows): continue
        parts, size = [[]], 0                      # bab panjang dipecah supaya mode Buku ringan
        for r in rows:
            if size > 40_000 and len(r) == 3: parts.append([]); size = 0
            parts[-1].append(r); size += len(r[2])
        for j, pr in enumerate(parts):
            rows_by.append((title + (f' ({j + 1})' if len(parts) > 1 else ''), pr))
    chunk = {}
    entries = []
    for i, (title, rows) in enumerate(rows_by, 1):
        body = [r for r in rows if len(r) == 3]
        chunk[str(i)] = rows
        entries.append({'k': str(i), 't': title, 'ta': '', 'c': len(body), 'f': body[0][0], 'l': body[-1][0], 'ch': 0})
    json.dump(chunk, open(f'{OUT}/{bid}-0.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    e = dict(meta); e.update(id=bid, kind='prose', langs=['eng'], secs=entries, total=sum(x['c'] for x in entries), chunks=1)
    print(f'{bid:12} secs={len(entries)} paras={e["total"]}')
    return e

if __name__ == '__main__':
    idx = json.load(open(f'{OUT}/index.json', encoding='utf-8'))
    for bid, pair, meta, fetch in BOOKS:
        e = emit(bid, dict(meta, pair=pair), fetch())
        idx = [x for x in idx if x['id'] != bid] + [e]
        for x in idx:
            if x['id'] == pair: x['pair'] = bid
    json.dump(idx, open(f'{OUT}/index.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
