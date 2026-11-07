"""Buat entri terjemah Indonesia (AI) untuk kitab an-Nabhani yang hanya punya terjemah Inggris resmi.

Pakai:  python -X utf8 scripts/make_mt_twin.py d <kitab> "<judul Indonesia>"
Menyalin d/<kitab>en-*.json menjadi d/<kitab>id-*.json (teks Inggris tetap di kolom 2 sebagai
sumber/cadangan), lalu menambah entri katalog <kitab>id dengan mtFrom="eng" dan menautkannya
(pairs) ke PDF Arab dan edisi Inggris. Terjemah Indonesianya diisi lewat scripts/mt/<kitab>id_*.json
dan scripts/build_mt.py, sehingga tampil berlabel "terjemah AI dari edisi Inggris".
Data yang sudah ada tidak ditimpa bila entri <kitab>id sudah ada.
"""
import copy, json, os, shutil, sys, time

D, bid, title = sys.argv[1], sys.argv[2], sys.argv[3]
src, sid = bid + 'en', bid + 'id'

def save_json(obj, p):
    tmp = p + '.tmp'
    for a in range(8):
        try:
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(obj, f, ensure_ascii=False, separators=(',', ':'))
            os.replace(tmp, p); return
        except OSError:
            if a == 7: raise
            time.sleep(0.5 * (a + 1))

idx = json.load(open(f'{D}/index.json', encoding='utf-8'))
by = {b['id']: b for b in idx}
if sid in by:
    sys.exit(f'{sid} sudah ada')
e = copy.deepcopy(by[src])
for c in range(e['chunks']):
    shutil.copyfile(f'{D}/{src}-{c}.json', f'{D}/{sid}-{c}.json')
e.update(id=sid, en=title, mtFrom='eng', src='Terjemah AI (Claude) dari edisi Inggris resmi hizb-ut-tahrir.org',
         pairs=[x for x in [bid, src] if x in by])
for x in e['pairs']:
    p = by[x].setdefault('pairs', [])
    if sid not in p: p.append(sid)
idx.insert(idx.index(by[src]) + 1, e)
save_json(idx, f'{D}/index.json')
print(sid, 'dibuat:', e['total'], 'paragraf,', len(e['secs']), 'bab')
