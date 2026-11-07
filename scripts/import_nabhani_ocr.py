"""Impor terjemah Indonesia kitab an-Nabhani dari teks OCR archive.org (_djvu.txt).

Dipakai untuk terbitan HTI-Press yang PDF-nya memakai font tersandi (teks tidak bisa
diekstrak langsung). Teks diambil apa adanya dari OCR archive.org; yang dibuang hanya
kepala/kaki halaman, nomor halaman, daftar isi, dan baris kutipan Arab yang rusak
dibaca OCR. Salah ketik OCR tidak dikoreksi.

Pakai:
  python -X utf8 scripts/import_nabhani_ocr.py nijtimai <path/_djvu.txt> d
"""
import json, os, re, sys, time

BOOKS = {
    'nijtimai': dict(
        title='Sistem Pergaulan dalam Islam',
        running='Sistem Pergaulan Dalam Islam',
        item='08SistemPergaulanIslamCet7',
        fix={'A z 1': "'Azl"},
        src='HTI-Press 2014 (cet. VII), via archive.org: teks OCR, mungkin ada salah ketik',
    ),
}

bid, path, D = sys.argv[1], sys.argv[2], sys.argv[3]
cfg = BOOKS[bid]
raw = open(path, encoding='utf-8').read().replace('\r', '')
lines = raw.split('\n')

def norm(s):
    return re.sub(r'[^a-z]', '', s.lower())

# ---- daftar isi: "Judul  123"
i0 = next(i for i, l in enumerate(lines) if norm(l) == 'daftarisi')
toc, i = [], i0 + 1
pend = ''
while i < len(lines):
    l = lines[i].strip()
    i += 1
    if not l:
        continue
    m = re.match(r'^(.*?\D)\s*(\d{1,3})$', l)
    if m:
        toc.append((pend + ' ' + m.group(1)).strip()); pend = ''
        if norm(m.group(1)) == 'silaturahim': break
    else:
        pend = (pend + ' ' + l).strip()
toc = [cfg.get('fix', {}).get(re.sub(r'\s+', ' ', t), re.sub(r'\s+', ' ', t)) for t in toc]
body = lines[i:]
toc_n = [norm(t) for t in toc]
run_n = norm(cfg['running'])

def is_running(l):
    s = l.strip()
    if re.fullmatch(r'[\divxlIVXL\s.]+', s): return True  # nomor halaman
    m = re.match(r'^(\d{1,3})\s+(.*)$', s)
    if m and norm(m.group(2)) == run_n: return True
    m = re.match(r'^(.*?)\s+(\d{1,3})$', s)
    if m and len(norm(m.group(1))) >= 4 and any(t.startswith(norm(m.group(1))) for t in toc_n): return True
    return False

from difflib import SequenceMatcher
def tocish(s):
    n = norm(s)
    L = re.findall(r'[A-Za-z]', s)
    return len(n) >= 3 and sum(c.isupper() for c in L) >= len(L) * 0.7 and any(SequenceMatcher(None, n, t).ratio() >= 0.7 for t in toc_n)

Q = '\'"“”‘’'
WORD = re.compile('[\\[(' + Q + '*]*[A-Za-z][A-Za-z\\-' + Q + ']*[\\].,;:!?)' + Q + '*]*'
                  '|[\\[(]?\\d+[\\]).,:;\\-]*\\d*[\\]).,:;]*')

def is_garbage(l):
    s = l.strip()
    if not s: return False
    if tocish(s): return False
    if re.search(r'[\^~\\|{}<>&@#*_=]', s): return True
    letters = len(re.findall(r'[A-Za-z]', s))
    if letters < len(s.replace(' ', '')) * 0.6: return True
    words = re.findall(r'[A-Za-z]{2,}', s)
    if not words: return True
    if re.search(r'[$»«§¥£¢]', s): return True
    toks = s.split()
    good = [t for t in toks if WORD.fullmatch(t) and not re.search('[a-z][A-Z]', t)
            and len(re.sub('[^A-Za-z0-9]', '', t)) >= 2]
    return len(good) < len(toks) * 0.75

# ---- susun paragraf
paras, cur = [], []
for l in body:
    if is_running(l) or is_garbage(l):
        continue
    if not l.strip():
        if cur: paras.append(cur); cur = []
        continue
    cur.append(l.strip())
if cur: paras.append(cur)

def join(ls):
    out = ''
    for l in ls:
        l = re.sub(r'\s+', ' ', l)
        if out.endswith('-') and l[:1].islower() and not re.search(r'\b(al|an|ar|as|asy|ad|at|az|wa|bi|li)-$', out):
            out = out[:-1] + l
        elif out.endswith('-'):
            out += l
        else:
            out = (out + ' ' + l).strip()
    return out

texts = []
for p in paras:
    t = join(p)
    # sambung paragraf yang terpotong pergantian halaman
    if texts and t[:1].islower() and not re.search(r'[.!?:”"’)]\s*$', texts[-1]):
        texts[-1] = join([texts[-1], t]); continue
    texts.append(t)
texts = [t for t in texts if len(re.findall(r'[A-Za-z]{2,}', t)) >= 2 or tocish(t)]
texts = [t for t in texts if not (len(t) < 40 and re.search('[a-z][A-Z]', t) and not tocish(t))]

# ---- bagi per bab menurut daftar isi (judul di badan teks ditulis kapital/tanpa nomor)
def caps(t):
    L = re.findall(r'[A-Za-z]', t)
    return L and sum(c.isupper() for c in L) >= len(L) * 0.7

from difflib import SequenceMatcher
def sim(a, b): return SequenceMatcher(None, a, b).ratio()
# kandidat judul: paragraf pendek yang seluruhnya huruf kapital
cand = [k for k, t in enumerate(texts) if caps(t) and len(t.split()) <= 9 and len(norm(t)) >= 3]
starts, pos, missing = [], 0, []
for j in range(len(toc)):
    found = None
    for k in cand:
        if k < pos: continue
        n = norm(texts[k])
        if sim(n, toc_n[j]) >= 0.6 or (len(n) >= 6 and (toc_n[j].startswith(n) or n.startswith(toc_n[j]))):
            found = (k, toc[j], k); break
    if found: starts.append(found); pos = found[2] + 1
    else: missing.append(toc[j])
secs_raw = []
if starts and starts[0][0] > 0:
    secs_raw.append(('Ayat-ayat Pembuka', texts[:starts[0][0]]))
for n, (k, t, he) in enumerate(starts):
    e = starts[n + 1][0] if n + 1 < len(starts) else len(texts)
    secs_raw.append((t, texts[he + 1:e]))

chunk, secs, num = {}, [], 0
for si, (t, ps) in enumerate(secs_raw, 1):
    rows = []
    for p in ps:
        num += 1; rows.append([num, '', '', p])
    if not rows: continue
    chunk[str(si)] = rows
    secs.append({'k': str(si), 't': t, 'ta': '', 'c': len(rows), 'f': rows[0][0], 'l': rows[-1][0], 'ch': 0})

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

sid = bid + 'id'
save_json(chunk, f'{D}/{sid}-0.json')
idx = json.load(open(f'{D}/index.json', encoding='utf-8'))
idx = [b for b in idx if b['id'] != sid]
by = {b['id']: b for b in idx}
ar = by[bid]
entry = dict(auth=ar['auth'], authar=ar['authar'], died=ar['died'], cat='nabhani', id=sid,
             en=cfg['title'], ar=ar['ar'], cover=ar['cover'], kind='prose', langs=['ind'],
             secs=secs, total=num, chunks=1, src=cfg['src'],
             pairs=[x for x in [bid, bid + 'en'] if x in by])
for x in entry['pairs']:
    p = by[x].setdefault('pairs', [])
    if sid not in p: p.append(sid)
pos = max(k for k, b in enumerate(idx) if b['id'] in entry['pairs']) + 1
idx.insert(pos, entry)
save_json(idx, f'{D}/index.json')
print(f'{sid}: {len(secs)} bab, {num} paragraf; daftar isi {len(toc)} judul; tidak ketemu: {missing}')
