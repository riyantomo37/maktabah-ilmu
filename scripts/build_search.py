"""Bangun indeks kata untuk pencarian statis.

Pemakaian:  python scripts/build_search.py d s
Hasil:
  s/books.json   [id kitab]  (urutan = nomor kitab di indeks)
  s/<k>.json     {kata: [nomor_kitab, ...]}   dipecah per dua huruf pertama kata

Browser memakai indeks ini untuk memilih kitab yang memuat semua kata yang dicari,
lalu mencari langsung di file d/<kitab>-<n>.json (tidak ada salinan teks ganda).
Normalisasi harus sama dengan fold()/stem() di index.html:
  harakat & tatwil dibuang; أإآٱ->ا, ى->ي, ة->ه, ؤ->و, ئ->ي; huruf kecil.
  Kata Arab disimpan tanpa awalan (و ف ب ل ك ال ...) supaya "صلاه" menemukan "والصلاه".
"""
import json, os, re, sys
from collections import defaultdict

D, S = sys.argv[1], sys.argv[2]
os.makedirs(S, exist_ok=True)

HARAKAT = re.compile('[ؐ-ًؚ-ٰٟۖ-ۭـ]')
FOLD = str.maketrans({'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ٱ': 'ا', 'ى': 'ي', 'ة': 'ه', 'ؤ': 'و', 'ئ': 'ي'})
def fold(t): return HARAKAT.sub('', t).translate(FOLD).lower()
PREFIX = re.compile(r'^(?:وبال|وال|فال|بال|كال|لل|ال|و|ف|ب|ل|ك)(?=..)')
def stem(tok):
    return PREFIX.sub('', tok) if '؀' <= tok[0] <= 'ۿ' else tok
TOKEN = re.compile(r'[a-z0-9À-ɏ؀-ۿ]{2,}')
def key(tok):
    return ''.join(c if c.isascii() and c.isalnum() else format(ord(c), 'x') for c in tok[:2])

idx = json.load(open(f'{D}/index.json', encoding='utf-8'))
words = defaultdict(set)
for bi, b in enumerate(idx):
    for c in range(b['chunks']):
        for rows in json.load(open(f'{D}/{b["id"]}-{c}.json', encoding='utf-8')).values():
            for r in rows:
                for x in r[1:8]:
                    if not isinstance(x, str) or not x: continue
                    for tok in set(TOKEN.findall(fold(x))):
                        if tok.isdigit(): continue
                        words[stem(tok)].add(bi)   # kata Arab hanya disimpan tanpa awalan
    print(f'{b["id"]:14} {len(words)} kata')
for f in os.listdir(S):
    if f.endswith('.json'): os.remove(f'{S}/{f}')
shards = defaultdict(dict)
for w, bs in words.items(): shards[key(w)][w] = sorted(bs)
size = 0
for k, m in shards.items():
    json.dump(m, open(f'{S}/{k}.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    size += os.path.getsize(f'{S}/{k}.json')
json.dump([b['id'] for b in idx], open(f'{S}/books.json', 'w', encoding='utf-8'))
big = max(shards, key=lambda k: len(json.dumps(shards[k], ensure_ascii=False)))
print(f'{len(words)} kata, {len(shards)} shard, {size/1e6:.1f} MB; shard terbesar {big}')
