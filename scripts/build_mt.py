"""Gabungkan terjemah mesin (AI) ke data kitab.

Pemakaian:  python scripts/build_mt.py d
Membaca scripts/mt/<kitab>_*.json  ->  {"<nomor>": {"id": "...", "ja": "..."}}
dan mengisi kolom Indonesia (3) dan Jepang (5) pada d/<kitab>-*.json.
Kitab yang mendapat terjemah ini diberi "mt": [kode bahasa], sehingga situs
menampilkan label "terjemah AI, belum ditinjau ahli".
Terjemah dibuat oleh Claude (Anthropic) dari teks Arab, dengan terjemah Inggris sebagai pembanding.
"""
import glob, json, os, re, sys
from collections import defaultdict

D = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
COL = {'id': (3, 'ind'), 'ja': (5, 'jpn')}

tr = defaultdict(dict)
for f in sorted(glob.glob(os.path.join(HERE, 'mt', '*_*.json'))):
    bid = re.match(r'(.+?)_\d+\.json$', os.path.basename(f)).group(1)
    for n, v in json.load(open(f, encoding='utf-8')).items():
        tr[bid][str(n)] = v

idx = json.load(open(f'{D}/index.json', encoding='utf-8'))
for bid, items in tr.items():
    b = next(x for x in idx if x['id'] == bid)
    used = set()
    for c in range(b['chunks']):
        p = f'{D}/{bid}-{c}.json'
        chunk = json.load(open(p, encoding='utf-8'))
        for rows in chunk.values():
            for r in rows:
                v = items.get(str(r[0]))
                if not v: continue
                while len(r) < 6: r.append('')
                for k, (col, code) in COL.items():
                    if v.get(k):
                        r[col] = v[k]; used.add(code)
        json.dump(chunk, open(p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    b['langs'] = sorted(set(b['langs']) | used, key=['ara', 'eng', 'ind', 'jpn'].index)
    b['mt'] = sorted(used)
    print(bid, 'terjemah AI:', len(items), 'hadits/paragraf', b['mt'])
json.dump(idx, open(f'{D}/index.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
