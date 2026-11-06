"""Koleksi karya Syekh Taqiyuddin an-Nabhani.

Pemakaian:  python scripts/build_nabhani.py <folder_kerja> d pdf
  <folder_kerja>/ar/<id>.pdf  PDF Arab resmi (hizb-ut-tahrir.org)
  <folder_kerja>/en/<id>.pdf  terjemah Inggris resmi (hizb-ut-tahrir.org)
  <folder_kerja>/id/<id>.pdf  terjemah Indonesia HTI-Press (archive.org, PDF digital)

Hasil:
  pdf/<id>.pdf               salinan PDF Arab apa adanya (ditampilkan halaman per halaman)
  d/<id>en-0.json, d/<id>id-0.json   teks terjemah, format baris [n, '', en, id, ...]
  entri katalog: kind "pdf" untuk Arab, kind "prose" untuk terjemah, saling tertaut lewat "pairs".

Izin: Hizb ut-Tahrir mengizinkan kutipan dan penerbitan ulang tanpa memotong/mengubah
teks dengan menyebut sumber. Teks PDF Arab memakai pemetaan font khusus sehingga tidak bisa
diekstrak; karena itu teks Arab ditampilkan sebagai halaman PDF aslinya.
Dari PDF terjemah hanya dibuang: kepala/kaki halaman, nomor halaman dan halaman daftar isi.
Simbol font AGA Arabesque dipetakan menurut konteks: setelah Allah/He/His -> (swt),
selainnya -> ﷺ; kurung hias -> ﴾ ﴿.
"""
import json, os, re, shutil, statistics, sys
from collections import Counter
import pymupdf

WORK, OUT, PDFDIR = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(PDFDIR, exist_ok=True)
SRC = 'hizb-ut-tahrir.org (PDF resmi)'
AUTH = dict(auth='Taqiyuddin an-Nabhani', authar='تقي الدين النبهاني', died=1398, cat='nabhani')

# id: (judul Arab, judul Inggris, judul Indonesia)
BOOKS = {
 'nnizham': ('نظام الإسلام', 'The System of Islam', 'Peraturan Hidup dalam Islam'),
 'ntakattul': ('التكتل الحزبي', 'Structuring of a Party', 'Pembentukan Partai Politik Islam'),
 'nmafahim': ('مفاهيم حزب التحرير', 'Concepts of Hizb ut-Tahrir', 'Mafahim Hizbut Tahrir'),
 'ndawlah': ('الدولة الإسلامية', 'The Islamic State', 'Daulah Islam'),
 'nhukm': ('نظام الحكم في الإسلام', 'The Ruling System in Islam', None),
 'nijtimai': ('النظام الاجتماعي في الإسلام', 'The Social System in Islam', None),
 'niqtisadi': ('النظام الاقتصادي في الإسلام', 'The Economic System of Islam', None),
 'nsiyasi': ('مفاهيم سياسية لحزب التحرير', 'Political Concepts of Hizb ut-Tahrir', 'Konsepsi Politik Hizbut Tahrir'),
 'ndustura': ('مقدمة الدستور - القسم الأول', None, None),
 'ndusturb': ('مقدمة الدستور - القسم الثاني', 'The Draft Constitution, Vol. 2', None),
 'nsyakhsiyaha': ('الشخصية الإسلامية - الجزء الأول', None, None),
 'nsyakhsiyahb': ('الشخصية الإسلامية - الجزء الثاني', None, None),
 'nsyakhsiyahc': ('الشخصية الإسلامية - الجزء الثالث', None, None),
 'nnazharat': ('نظرات سياسية لحزب التحرير', None, None),
 'nnida': ('نداء حار إلى المسلمين', 'A Warm Call from Hizb ut-Tahrir', None),
 'ntafkir': ('التفكير', None, None),
 'nbadiha': ('سرعة البديهة', 'Presence of Mind', None),
 'nnuqthah': ('نقطة الانطلاق', None, None),
 'ndukhul': ('دخول المجتمع', None, None),
 'nfikr': ('الفكر الإسلامي', 'Islamic Thought', 'Fikrul Islam'),
 'nsiyasahiqt': ('السياسة الاقتصادية المثلى', None, None),
 'nnaqdh': ('نقض الاشتراكية الماركسية', None, None),
 'nkaifa': ('كيف هدمت الخلافة', 'How the Khilafah was Destroyed', None),
 'nbayyinat': ('أحكام البينات', None, None),
}

# ---------------------------------------------------------------- Arabic PDFs
def pdf_entry(bid, title_ar):
    src = f'{WORK}/ar/{bid}.pdf'
    shutil.copyfile(src, f'{PDFDIR}/{bid}.pdf')
    d = pymupdf.open(src)
    n = d.page_count
    toc = [t for t in d.get_toc() if 1 <= t[2] <= n]
    lv = min((t[0] for t in toc), default=1)
    top = [t for t in toc if t[0] == lv]
    if len(top) < 3 and any(t[0] == lv + 1 for t in toc):
        top = [t for t in toc if t[0] <= lv + 1]
    top.sort(key=lambda t: t[2])
    secs = []
    starts = [1] + [t[2] for t in top] if (not top or top[0][2] > 1) else [t[2] for t in top]
    titles = (['المقدمة'] if (not top or top[0][2] > 1) else []) + [re.sub(r'\s+', ' ', t[1]).strip() for t in top]
    # buang judul ganda di halaman yang sama
    seen = []
    for s, t in zip(starts, titles):
        if seen and seen[-1][0] == s: seen[-1] = (s, seen[-1][1] + ' · ' + t); continue
        seen.append((s, t))
    for i, (s, t) in enumerate(seen):
        e = (seen[i + 1][0] - 1) if i + 1 < len(seen) else n
        e = max(e, s)
        secs.append({'k': str(i + 1), 't': t or title_ar, 'ta': '', 'c': e - s + 1, 'f': s, 'l': e, 'ch': 0})
    r = d[0].rect
    # sampul = halaman pertama PDF resmi (judul kaligrafi khas terbitan Hizbut Tahrir)
    os.makedirs('covers', exist_ok=True)
    from PIL import Image
    z = 420 / r.width; pix = d[0].get_pixmap(matrix=pymupdf.Matrix(z, z))
    Image.frombytes('RGB', (pix.width, pix.height), pix.samples).save(f'covers/{bid}.webp', 'WEBP', quality=78, method=6)
    return dict(AUTH, id=bid, en=title_ar, ar=title_ar, kind='pdf', langs=['ara'], file=f'{PDFDIR}/{bid}.pdf', cover=f'covers/{bid}.webp',
                ratio=round(r.width / r.height, 4), secs=secs, total=n, chunks=0, src=SRC)

# ---------------------------------------------------------------- translations
PUA_OPEN, PUA_CLOSE, PUA_SWT, PUA_R = '', '', '', ''
GODWORDS = {'allah', 'he', 'his', 'him', 'himself', 'god', 'lord'}
def span_text(spans, i):
    s = spans[i]; t = s['text']; f = s['font']
    if 'Arabesque' in f:
        out = ''
        prev = ''.join(x['text'] for x in spans[:i])[-30:]
        pw = (re.findall(r'[A-Za-z]+', prev) or [''])[-1].lower()
        for ch in t:
            if ch == PUA_OPEN: out += '﴾'
            elif ch == PUA_CLOSE: out += '﴿'
            elif ch == PUA_SWT: out += ' (swt)'
            elif ch == PUA_R: out += ' (swt)' if pw in GODWORDS else ' ﷺ'
        return out
    if 'Dingbat' in f or 'Symbol' in f: return ''
    return t.replace('­', '')

ENDP = re.compile(r'[.!?:;"”’)\]﴿»]\s*$')
TOCLINE = re.compile(r'(\.{3,}|…{2,}|\s{3,})\s*\d{1,3}\s*$')

ARABIC = re.compile(r'[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]+')
GARBAGE = re.compile(r'[<>@\]\[^„‹›÷ﬂﬁ⁄Ð¨ß¾½¼±§¶~`|\\]')
def clean_line(t):
    # kutipan Arab di PDF terjemah sering memakai font lama (urutan/huruf rusak); teks Arab
    # aslinya utuh di edisi PDF Arab, jadi di sini dihapus
    t = ARABIC.sub(' ', t)
    t = re.sub(r'^\s*(\d{1,3}\s+)?(\S.{2,40}?)(?:\s+\2){2,}\s*', '', t)
    t = re.sub(r'(?:\b[A-Za-z] ){7,}[A-Za-z]\b', ' ', t)    # kepala halaman berhuruf renggang
    t = re.sub(r'\s+', ' ', t).strip()
    letters = len(re.findall(r'[A-Za-z]', t))
    if t and len(GARBAGE.findall(t)) >= 3 and letters < len(t) * 0.6: return ''
    if t and not re.search(r'[A-Za-z0-9]', t): return ''
    return t

def norm_key(t):
    return re.sub(r'[\d\W_]+', '', t).lower()

def extract(path, lang):
    d = pymupdf.open(path)
    pages, sizes = [], Counter()
    for pg in d:
        H = pg.rect.height
        lines = []
        blocks = [b for b in pg.get_text('dict', flags=pymupdf.TEXT_PRESERVE_WHITESPACE)['blocks'] if b.get('type') == 0]
        # urutan baca atas->bawah: di PDF judul bab sering disimpan SETELAH paragraf pembukanya
        blocks.sort(key=lambda b: (round(b['bbox'][1] / 4), b['bbox'][0]))
        for b in blocks:
            bl = []
            for l in b['lines']:
                sp = l['spans']
                txt = ''.join(span_text(sp, i) for i in range(len(sp)))
                txt = re.sub(r'[\ue000-\uf8ff]', '', txt)          # sisa glyph font hiasan
                txt = clean_line(txt)
                txt = re.sub(r'\s+', ' ', txt).strip()
                if not txt: continue
                size = max((s['size'] for s in sp if s['text'].strip()), default=0)
                bold = all(('Bold' in s['font'] or s['flags'] & 16) for s in sp if s['text'].strip())
                bl.append(dict(t=txt, size=round(size, 1), bold=bold, y0=l['bbox'][1], y1=l['bbox'][3], H=H))
                sizes[round(size, 1)] += len(txt)
            if bl: lines.append(bl)
        pages.append(lines)
    body = sizes.most_common(1)[0][0] if sizes else 10
    edge_of = lambda ln: ln['y0'] < ln['H'] * 0.11 or ln['y1'] > ln['H'] * 0.91
    # kepala/kaki halaman berulang (huruf berjarak & nomor halaman diabaikan)
    edge = Counter()
    for lines in pages:
        seen = set()
        for bl in lines:
            for ln in bl:
                k = norm_key(ln['t'])
                if edge_of(ln) and k and k not in seen: edge[k] += 1; seen.add(k)
    running = {k for k, v in edge.items() if v >= max(3, len(pages) * 0.05)}
    def is_running(t):
        k = norm_key(t)
        if k and any(len(r) >= 6 and k.replace(r, '') == '' for r in running): return True
        return bool(k) and (k in running or any(len(r) >= 6 and k.startswith(r) and len(k) <= len(r) * 4 for r in running))
    items = []  # (kind, text, size, page)
    for pno, lines in enumerate(pages):
        flat = [ln for bl in lines for ln in bl]
        if flat and sum(1 for ln in flat if TOCLINE.search(ln['t'])) >= max(4, len(flat) * 0.35):
            continue  # halaman daftar isi
        for bl in lines:
            keep = []
            for ln in bl:
                if (is_running(ln['t']) and len(ln['t']) < 160) or edge_of(ln) and (is_running(ln['t']) or re.fullmatch(r'[\W\d_ivxlcIVXLC]{1,8}', ln['t'])): continue
                # kepala/kaki halaman berhuruf kecil (judul bab di atas halaman, nomor halaman)
                if edge_of(ln) and ln['size'] < body * 0.85 and len(ln['t']) < 90: continue
                keep.append(ln)
            if not keep: continue
            text = ''
            for ln in keep:
                t = ln['t']
                if text.endswith('-') and re.match(r'[a-z]', t): text = text[:-1] + t
                else: text = (text + ' ' + t).strip()
            text = re.sub(r'^\s*(\d{1,3}\s+)?(\S.{2,40}?)(?:\s+\2){2,}\s*', '', text).strip()
            if not text: continue
            big = statistics.mean(ln['size'] for ln in keep)
            head = (big >= body * 1.15 or all(ln['bold'] for ln in keep)) and len(text) < 140 and len(keep) <= 3 and not ENDP.search(text.rstrip('"”'))
            items.append(['h' if head else 'p', text, big, pno])
    first = next((pno for pno in range(len(pages)) if sum(len(it[1]) for it in items if it[3] == pno and it[0] == 'p') >= 600), 0)
    items = [it for it in items if it[3] >= first]
    # huruf awal besar (drop cap): "K" + "etika" -> "Ketika"
    out = []
    for i, it in enumerate(items):
        nxt = items[i + 1] if i + 1 < len(items) else None
        m = re.fullmatch(r'(.*?)\s*\b([A-Z])', it[1]) if it[0] == 'h' else None
        if m and nxt and nxt[0] == 'p' and re.match(r'[a-z]', nxt[1]):
            nxt[1] = m.group(2) + nxt[1]
            if m.group(1).strip(): out.append(['h', m.group(1).strip(), it[2], it[3]])
            continue
        out.append(it)
    items = [it for it in out if not (it[0] == 'h' and len(norm_key(it[1])) < 2)]
    dedup = []
    for it in items:
        a = norm_key(it[1])
        def same(x):
            # lapisan teks ganda / huruf awal besar ganda: teks pendek termuat UTUH dalam teks panjang
            if x[1][:60] == it[1][:60]: return True
            if x[0] != 'p' or it[0] != 'p': return False
            b = norm_key(x[1]); sh, lo = sorted((a, b), key=len)
            return len(sh) >= 8 and sh[2:] in lo
        hit = next((x for x in dedup[-8:] if same(x)), None)  # lapisan teks ganda di PDF
        if hit is not None:
            if len(it[1]) > len(hit[1]): hit[1] = it[1]
            continue
        dedup.append(it)
    items = dedup
    # gabungkan paragraf yang terpotong pergantian halaman/blok
    merged = []
    for it in items:
        if merged and it[0] == 'p' and merged[-1][0] == 'p' and not ENDP.search(merged[-1][1]) and re.match(r'[a-z(,;]', it[1]):
            prev = merged[-1][1]
            merged[-1][1] = (prev[:-1] + it[1]) if prev.endswith('-') else prev + ' ' + it[1]
        else:
            merged.append(it)
    # pembagian bab: pakai daftar isi PDF bila ada, selain itu ukuran judul
    toc = [t for t in d.get_toc() if t[2] >= 1]
    starts = {}
    if len(toc) >= 3:
        lv = min(t[0] for t in toc)
        top = [t for t in toc if t[0] == lv]
        if len(top) < 3: top = [t for t in toc if t[0] <= lv + 1]
        for t in top: starts.setdefault(t[2] - 1, re.sub(r'\s+', ' ', t[1]).strip())
    secs, cur = [], None
    if starts:
        done = set()
        for it in merged:
            pno = it[3]
            for sp in sorted(k for k in starts if k <= pno and k not in done):
                done.add(sp); cur = [starts[sp], []]; secs.append(cur)
            if cur is None: cur = ['Preface' if lang == 'en' else 'Pengantar', []]; secs.append(cur)
            if it[0] == 'h' and norm_key(it[1]) and norm_key(it[1]) in norm_key(cur[0]) and not cur[1]: continue
            cur[1].append((it[0], it[1]))
        return drop_contents(secs)
    hs = Counter(round(it[2]) for it in merged if it[0] == 'h')
    cands = sorted((sz for sz, c in hs.items() if c >= 3), reverse=True)
    sec_size = None
    for sz in cands:
        n = sum(1 for it in merged if it[0] == 'h' and round(it[2]) >= sz)
        if n >= 4: sec_size = sz; break
    for it in merged:
        k, t, sz = it[0], it[1], it[2]
        if k == 'h' and sec_size is not None and round(sz) >= sec_size:
            if cur and not any(x[0] == 'p' for x in cur[1]):
                cur[0] = (cur[0] + ' · ' + t) if cur[0] not in ('Preface', 'Pengantar') else t; continue
            cur = [t, []]; secs.append(cur); continue
        if cur is None: cur = ['Preface' if lang == 'en' else 'Pengantar', []]; secs.append(cur)
        cur[1].append((k, t))
    return drop_contents(secs)

def drop_contents(secs):
    out = []
    for t, items in secs:
        items = [x for x in items if not (x[0] == 'h' and norm_key(x[1]) == norm_key(t))]
        if out and norm_key(out[-1][0]) == norm_key(t): out[-1][1].extend(items); continue
        out.append([t, items])
    secs = out
    if len(secs) == 1 and secs[0][0] in ('Preface', 'Pengantar'): secs[0][0] = ''
    return [s for s in secs if not re.match(r'(?i)\s*(contents|table of contents|daftar isi)\b', s[0])]

def text_entry(bid, lang, title, ar_title, pair_ids):
    secs = extract(f'{WORK}/{lang}/{bid}.pdf', lang)
    col = 2 if lang == 'en' else 3
    rows_by, n = [], 0
    for title_s, items in secs:
        rows = []
        for k, t in items:
            r = [n + 0.5, '', '', '', '', '', '', '', 2] if k == 'h' else None
            if r is None:
                n += 1; r = [n, '', '', '']
            r[col] = t
            rows.append(r)
        if not any(r[8:] == [] for r in rows): continue
        parts, size = [[]], 0
        for r in rows:
            if size > 40_000 and len(r) == 4: parts.append([]); size = 0
            parts[-1].append(r); size += len(r[col])
        for j, pr in enumerate(parts):
            if not title_s: rows_by.append((('Part ' if lang == 'en' else 'Bagian ') + str(j + 1), pr)); continue
            rows_by.append((title_s[:120] + (f' ({j + 1})' if len(parts) > 1 else ''), pr))
    sid = bid + lang
    chunk, entries = {}, []
    for i, (t, rows) in enumerate(rows_by, 1):
        body = [r for r in rows if len(r) == 4]
        chunk[str(i)] = rows
        entries.append({'k': str(i), 't': t, 'ta': '', 'c': len(body), 'f': body[0][0], 'l': body[-1][0], 'ch': 0})
    json.dump(chunk, open(f'{OUT}/{sid}-0.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    src = SRC.replace('PDF resmi', 'terjemah Inggris resmi') if lang == 'en' else 'HTI-Press, via archive.org (PDF digital)'
    e = dict(AUTH, id=sid, en=title, ar=ar_title, cover=f'covers/{bid}.webp', kind='prose', langs=['eng' if lang == 'en' else 'ind'],
             secs=entries, total=sum(x['c'] for x in entries), chunks=1, src=src, pairs=pair_ids)
    print(f'  {sid:16} secs={len(entries):3} paras={e["total"]}')
    return e

if __name__ == '__main__':
    idx = json.load(open(f'{OUT}/index.json', encoding='utf-8'))
    idx = [b for b in idx if b.get('cat') != 'nabhani']
    new = []
    for bid, (ar, en, ind) in BOOKS.items():
        group = [bid] + ([bid + 'en'] if en and os.path.exists(f'{WORK}/en/{bid}.pdf') else []) + ([bid + 'id'] if ind and os.path.exists(f'{WORK}/id/{bid}.pdf') else [])
        e = pdf_entry(bid, ar); e['pairs'] = [g for g in group if g != bid]
        print(f'{bid:16} pdf pages={e["total"]} secs={len(e["secs"])}')
        new.append(e)
        if bid + 'en' in group: new.append(text_entry(bid, 'en', en, ar, [g for g in group if g != bid + 'en']))
        if bid + 'id' in group: new.append(text_entry(bid, 'id', ind, ar, [g for g in group if g != bid + 'id']))
    json.dump(idx + new, open(f'{OUT}/index.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
