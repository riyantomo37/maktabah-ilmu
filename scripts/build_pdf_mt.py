"""Terjemah Indonesia (AI) per halaman untuk kitab yang hanya berupa PDF Arab.

Pakai:  python -X utf8 scripts/build_pdf_mt.py d

Membaca scripts/pdfmt/<kitab>_NN.json, isinya:
  {"_title": "Judul Indonesia", "_secs": {"3": {"id": "Judul bab"}}, "12": "terjemah halaman 12", ...}
Kunci angka = nomor halaman PDF (1 = halaman pertama berkas). Bab mengikuti daftar bab
kitab PDF (secs f..l = rentang halaman); hanya bab yang sudah punya halaman terjemah ikut tampil.
Hasilnya kitab kembar <kitab>id (kind "prose", bahasa Indonesia saja, berlabel terjemah AI dari
teks Arab) yang ditautkan (pairs) ke PDF Arab-nya. Teks Arab PDF tidak diubah sama sekali.
Dibuat ulang utuh setiap kali dijalankan.
"""
import glob, json, os, re, sys, time

D = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))


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


data = {}
for f in sorted(glob.glob(os.path.join(HERE, 'pdfmt', '*_*.json'))):
    bid = re.match(r'(.+?)_\d+\.json$', os.path.basename(f)).group(1)
    data.setdefault(bid, {'_secs': {}, 'pages': {}})
    for k, v in json.load(open(f, encoding='utf-8')).items():
        if k == '_secs': data[bid]['_secs'].update(v)
        elif k == '_title': data[bid]['_title'] = v
        else: data[bid]['pages'][int(k)] = v

idx = json.load(open(f'{D}/index.json', encoding='utf-8'))
by = {b['id']: b for b in idx}
for bid, dd in data.items():
    src = by[bid]
    sid = bid + 'id'
    pages = dd['pages']
    secs, chunk = [], {}
    for s in src['secs']:
        ps = sorted(p for p in pages if s['f'] <= p <= s['l'])
        if not ps: continue
        k = s['k']
        chunk[k] = [[p, '', '', pages[p]] for p in ps]
        secs.append({'k': k, 't': (dd['_secs'].get(k) or {}).get('id') or s['t'], 'ta': '',
                     'c': len(ps), 'f': ps[0], 'l': ps[-1], 'ch': 0})
    save_json(chunk, f'{D}/{sid}-0.json')
    e = by.get(sid) or {}
    new = {k: src[k] for k in ('auth', 'authar', 'died', 'cat', 'cover') if k in src}
    new.update(id=sid, en=dd.get('_title', src['en']), ar=src['ar'], kind='prose', langs=['ind'],
               mt=['ind'], secs=secs, total=len(pages), chunks=1,
               src='Terjemah AI (Claude) per halaman dari PDF Arab resmi hizb-ut-tahrir.org',
               pairs=[bid] + [x for x in src.get('pairs', []) if x != sid])
    if len(pages) < src['total']: new['mtDone'] = len(pages)
    if sid in by:
        idx[idx.index(e)] = new
    else:
        idx.insert(idx.index(src) + 1, new)
    by[sid] = new
    if sid not in src.setdefault('pairs', []): src['pairs'].append(sid)
    print(f'{sid:16} {len(pages)}/{src["total"]} halaman, {len(secs)} bab')
save_json(idx, f'{D}/index.json')
