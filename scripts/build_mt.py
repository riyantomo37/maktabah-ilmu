"""Gabungkan terjemah mesin (AI) ke data kitab.

Pemakaian:  python scripts/build_mt.py d
Membaca scripts/mt/<kitab>_*.json :
  {"<nomor>": {"id": "...", "en": "...", "ja": "..."}, "_secs": {"<kunci bab>": {"id": "...", "en": "..."}}}
dan mengisi kolom Inggris (2), Indonesia (3), Jepang (5) pada d/<kitab>-*.json,
serta judul bab terjemahan (t_id, t_en, t_ja) di d/index.json.
Kolom yang sudah berisi terjemah dari sumber resmi tidak ditimpa.
Kitab yang mendapat terjemah ini diberi "mt": [kode bahasa] sehingga situs menampilkan label
"terjemah AI, belum ditinjau ahli". Terjemah dibuat oleh Claude (Anthropic) dari teks Arab.
Jalankan ulang setelah build_openiti.py / build.py membangun ulang data.
"""
import glob, json, os, re, sys
from collections import defaultdict

D = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
COL = {'en': (2, 'eng'), 'id': (3, 'ind'), 'ja': (5, 'jpn')}

tr, secs = defaultdict(dict), defaultdict(dict)
for f in sorted(glob.glob(os.path.join(HERE, 'mt', '*_*.json'))):
    bid = re.match(r'(.+?)_\d+\.json$', os.path.basename(f)).group(1)
    for n, v in json.load(open(f, encoding='utf-8')).items():
        if n == '_secs': secs[bid].update(v)
        else: tr[bid][str(n)] = v

idx = json.load(open(f'{D}/index.json', encoding='utf-8'))
for bid in sorted(set(tr) | set(secs)):
    b = next((x for x in idx if x['id'] == bid), None)
    if b is None: print('tidak ada kitab', bid); continue
    items = tr.get(bid, {})
    used, count = set(), 0
    for c in range(b['chunks']):
        p = f'{D}/{bid}-{c}.json'
        chunk = json.load(open(p, encoding='utf-8'))
        changed = False
        for rows in chunk.values():
            for r in rows:
                v = items.get(str(r[0]))
                if len(r) > 8 and r[8]: continue
                if str(r[0]) in items and not re.sub(r'<[^>]*>|\W', '', r[1] or ''):
                    count += 1; continue  # baris kosong/markup saja: dihitung selesai
                if not v: continue
                while len(r) < 6: r.append('')
                hit = False
                for k, (col, code) in COL.items():
                    if v.get(k) and (not r[col] or code in b.get('mt', []) or code not in b['langs']):
                        r[col] = v[k]; used.add(code); hit = True
                if hit: count += 1; changed = True
        if changed:
            json.dump(chunk, open(p, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    for s in b['secs']:
        st = secs.get(bid, {}).get(s['k'])
        if st:
            for k in ('id', 'en', 'ja'):
                if st.get(k): s['t_' + k] = st[k]
    new = used - set(b['langs'])
    b['mt'] = sorted(set(b.get('mt', [])) | new)
    b['langs'] = sorted(set(b['langs']) | used, key=['ara', 'eng', 'ind', 'jpn'].index)
    if not b['mt']: b.pop('mt')
    # berapa paragraf yang sudah diterjemah (untuk label "sebagian")
    total = b['total']
    b['mtDone'] = count if count < total else None
    if b['mtDone'] is None: b.pop('mtDone')
    print(f'{bid:16} {count}/{total} baris, judul bab: {len(secs.get(bid, {}))}, mt={b.get("mt")}')
json.dump(idx, open(f'{D}/index.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
