"""Tampilkan teks Arab kitab untuk diterjemahkan:  python scripts/mt_dump.py d <kitab> [dari] [jumlah]"""
import json, sys
D, bid = sys.argv[1], sys.argv[2]
start = int(sys.argv[3]) if len(sys.argv) > 3 else 0
cnt = int(sys.argv[4]) if len(sys.argv) > 4 else 10**9
b = next(x for x in json.load(open(f'{D}/index.json', encoding='utf-8')) if x['id'] == bid)
titles = {s['k']: s['t'] for s in b['secs']}
i = 0
for c in range(b['chunks']):
    for k, rows in json.load(open(f'{D}/{bid}-{c}.json', encoding='utf-8')).items():
        for r in rows:
            if len(r) > 8 and r[8]: continue
            if start <= i < start + cnt:
                if r is rows[0] or (i == start): print(f'## [{k}] {titles.get(k, "")}')
                print(f'{r[0]}| {r[1]}')
            i += 1
