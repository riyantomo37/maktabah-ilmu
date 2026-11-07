# Tambahkan terjemahan Indonesia Tafsir Jalalain dari Tanzil (id.jalalayn) ke d/jalalayn-*.json.
# Sumber: https://tanzil.net/trans/  (non-komersial, teks tidak diubah, tautan balik ke Tanzil)
# Pakai: python -X utf8 scripts/import_jalalayn_id.py <path/id.jalalayn.txt> [d]
import glob, json, os, sys, time

src = sys.argv[1]
D = sys.argv[2] if len(sys.argv) > 2 else 'd'

ID = {}
for line in open(src, encoding='utf-8'):
    if not line.strip() or line.startswith('#'):
        continue
    s, a, t = line.rstrip('\n').split('|', 2)
    ID[(int(s), int(a))] = t.strip()
assert len(ID) == 6236, len(ID)

def save_json(obj, path):
    tmp = path + '.tmp'
    for attempt in range(8):
        try:
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(obj, f, ensure_ascii=False, separators=(',', ':'))
            os.replace(tmp, path); return
        except OSError:
            if attempt == 7: raise
            time.sleep(0.5 * (attempt + 1))

used = set()
for p in sorted(glob.glob(f'{D}/jalalayn-*.json')):
    chunk = json.load(open(p, encoding='utf-8'))
    for sura, rows in chunk.items():
        s = int(sura)
        for r in rows:
            first = int(r[0]); last = int(r[7]) if len(r) > 7 and r[7] else first
            parts = []
            for a in range(first, last + 1):
                t = ID.get((s, a), '')
                if not t: continue
                used.add((s, a))
                parts.append(t if a == first else f'﴿{a}﴾ {t}')
            r[3] = '\n'.join(parts)
    save_json(chunk, p)

idx = json.load(open(f'{D}/index.json', encoding='utf-8'))
for b in idx:
    if b['id'] == 'jalalayn':
        if 'ind' not in b['langs']:
            b['langs'] = ['ara', 'eng', 'ind']
        b['src'] = ('spa5k/tafsir_api (Arabic; English tr. Feras Hamza); '
                    'Indonesian: id.jalalayn via Tanzil (tanzil.net/trans)')
save_json(idx, f'{D}/index.json')
print('ayat dipakai:', len(used), 'dari', len(ID))
