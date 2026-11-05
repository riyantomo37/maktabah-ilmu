"""Bangun kitab dari korpus OpenITI (teks Arab, mARkdown) ke format d/<id>-<n>.json.

Pemakaian:  python scripts/build_openiti.py <folder_sumber_openiti> d
Sumber: https://github.com/OpenITI (lisensi CC BY-NC-SA 4.0). Daftar file ada di BOOKS di bawah.

Format baris: [nomor, arab, en, id, derajat, ja, '', '', jenis]  (jenis 1 = subjudul)
Teks Arab tidak diubah: hanya penanda halaman (PageV..P..), milestone (ms..) dan
penanda baris OpenITI (#, ~~, %~%) yang dibuang.
"""
import json, re, sys, os

SRC, OUT = sys.argv[1], sys.argv[2]
LIMIT = 1_600_000          # ukuran maks satu file chunk
SEC_MAX = 120_000          # bab lebih besar dari ini dipecah jadi beberapa bagian (mode Buku tetap ringan)

def M(en, ar, auth, authar, died, cat, kind='prose', **kw):
    d = dict(en=en, ar=ar, auth=auth, authar=authar, died=died, cat=cat, kind=kind, langs=['ara'])
    d.update(kw); return d

# id, file OpenITI, metadata, opsi
BOOKS = [
 ('musnad', '0241IbnHanbal.Musnad.Shamela0025794-ara1.mARkdown',
   M('Musnad Imam Ahmad (complete Arabic)', 'مسند الإمام أحمد بن حنبل', 'Imam Ahmad bin Hanbal', 'الإمام أحمد بن حنبل', 241, 'ahmad', 'hadith'), {'hadith': True}),
 ('zuhd', '0241IbnHanbal.Zuhd.Shamela0008494-ara1.mARkdown',
   M('Kitab az-Zuhd', 'كتاب الزهد', 'Imam Ahmad bin Hanbal', 'الإمام أحمد بن حنبل', 241, 'ahmad'), {}),
 ('usulsunnah', '0241IbnHanbal.UsulSunna.Shamela0006418-ara1',
   M('Usul as-Sunnah', 'أصول السنة', 'Imam Ahmad bin Hanbal', 'الإمام أحمد بن حنبل', 241, 'ahmad'), {}),
 ('ihya', '0505Ghazali.IhyaCulumDin.Shamela0009472-ara1.completed',
   M("Ihya' 'Ulum ad-Din", 'إحياء علوم الدين', 'Imam al-Ghazali', 'الإمام أبو حامد الغزالي', 505, 'ghazali'), {}),
 ('bidayah', '0505Ghazali.BidayatHidaya.Shamela0012718-ara1',
   M('Bidayat al-Hidayah', 'بداية الهداية', 'Imam al-Ghazali', 'الإمام أبو حامد الغزالي', 505, 'ghazali'), {}),
 ('munqidh', '0505Ghazali.Munqidh.Shamela0009246-ara1',
   M('Al-Munqidh min ad-Dalal', 'المنقذ من الضلال', 'Imam al-Ghazali', 'الإمام أبو حامد الغزالي', 505, 'ghazali'), {}),
 ('kimiya', '0505Ghazali.KimiyaSacada.Shamela0009261-ara1',
   M("Kimiya' as-Sa'adah", 'كيمياء السعادة', 'Imam al-Ghazali', 'الإمام أبو حامد الغزالي', 505, 'ghazali'), {}),
 ('misykatanwar', '0505Ghazali.MishkatAnwar.Shamela0012421-ara1',
   M('Mishkat al-Anwar', 'مشكاة الأنوار', 'Imam al-Ghazali', 'الإمام أبو حامد الغزالي', 505, 'ghazali'), {}),
 ('tahafut', '0505Ghazali.Tahafut.Shamela0011055-ara1',
   M('Tahafut al-Falasifah', 'تهافت الفلاسفة', 'Imam al-Ghazali', 'الإمام أبو حامد الغزالي', 505, 'ghazali'), {}),
 ('muqaddimah', '0808IbnKhaldun.Tarikh.Shamela0012320-ara1.mARkdown',
   M('Al-Muqaddimah', 'مقدمة ابن خلدون', 'Ibn Khaldun', 'عبد الرحمن بن خلدون', 808, 'tarikh'), {'until': '### | الكتاب الثاني'}),
 ('muruj', '0346Mascudi.MurujDhahab.JK010344-ara1.completed',
   M('Muruj adh-Dhahab', 'مروج الذهب ومعادن الجوهر', "Al-Mas'udi", 'المسعودي', 346, 'tarikh'), {}),
 ('battutah', '0779IbnBattuta.Rihla.Shamela0011769-ara1.completed',
   M('Rihlah Ibn Battutah', 'رحلة ابن بطوطة: تحفة النظار في غرائب الأمصار', 'Ibn Battutah', 'ابن بطوطة', 779, 'rihlah'), {}),
 ('jubayr', '0614IbnJubayr.Rihla.Shamela0010883-ara1',
   M('Rihlah Ibn Jubayr', 'رحلة ابن جبير', 'Ibn Jubayr', 'ابن جبير', 614, 'rihlah'), {}),
 ('fadlan', '0309IbnFadlan.Rihla.Shamela0011772-ara1.completed',
   M('Risalah Ibn Fadlan', 'رسالة ابن فضلان', 'Ahmad ibn Fadlan', 'أحمد بن فضلان', 309, 'rihlah'), {}),
 ('itibar', '0584IbnMunqidhShayzari.Ictibar.Shamela0021564-ara1.mARkdown',
   M("Kitab al-I'tibar", 'كتاب الاعتبار', "Usamah ibn Munqidh", 'أسامة بن منقذ', 584, 'rihlah'), {}),
 ('ajaib', '0350BuzurgIbnShahriyarRamhurmuzi.CajaibHind.Masaha004386-ara1',
   M("'Aja'ib al-Hind", 'عجائب الهند بره وبحره وجزائره', 'Buzurg ibn Shahriyar', 'بزرك بن شهريار الرامهرمزي', 350, 'rihlah'), {}),
 ('idrisi', '0560SharifIdrisi.NuzhatMushtaq.Shamela0011787-ara1.mARkdown',
   M('Nuzhat al-Mushtaq', 'نزهة المشتاق في اختراق الآفاق', 'Asy-Syarif al-Idrisi', 'الشريف الإدريسي', 560, 'rihlah'), {}),
 ('hayy', '0581IbnTufayl.HayyIbnYaqzan.Shamela0009734-ara1',
   M('Hayy ibn Yaqzan', 'حي بن يقظان', 'Ibn Tufayl', 'ابن طفيل', 581, 'rihlah'), {}),
 ('qanun', '0428IbnSina.QanunFiTibb.Shamela0010706-ara1.completed',
   M('Al-Qanun fi at-Tibb', 'القانون في الطب', 'Ibn Sina (Avicenna)', 'ابن سينا', 428, 'sina'), {}),
 ('isharat', '0428IbnSina.IsharatWaTanbihat.Shamela0006534BK1-ara1.mARkdown',
   M("Al-Isharat wa at-Tanbihat", 'الإشارات والتنبيهات', 'Ibn Sina (Avicenna)', 'ابن سينا', 428, 'sina'), {}),
 ('najat', '0428IbnSina.Najat.MP002-ara1',
   M('An-Najat', 'النجاة', 'Ibn Sina (Avicenna)', 'ابن سينا', 428, 'sina'), {}),
 # --- tambahan: rak "Segera Hadir" dan kitab lain
 ('ibnkhuzaimah', '0311IbnKhuzaymaNaysaburi.Sahih.Shamela0001446-ara1',
   M('Sahih Ibn Khuzaymah', 'صحيح ابن خزيمة', 'Imam Ibn Khuzaymah', 'الإمام ابن خزيمة', 311, 'hadith', 'hadith'), {'hadith': True}),
 ('ibnhibban', '0739CalaDinIbnBalban.Ihsan.Sham19Y0001729-ara1',
   M('Sahih Ibn Hibban (al-Ihsan)', 'الإحسان في تقريب صحيح ابن حبان', 'Imam Ibn Hibban · arr. Ibn Balban', 'الإمام ابن حبان، ترتيب ابن بلبان', 354, 'hadith', 'hadith'), {'hadith': True}),
 ('fathulbari', '0852IbnHajarCasqalani.FathBari.Shamela0001673-ara1',
   M('Fath al-Bari', 'فتح الباري شرح صحيح البخاري', "Ibn Hajar al-'Asqalani", 'ابن حجر العسقلاني', 852, 'hadith'), {}),
 ('thabari', '0310Tabari.JamicBayan.Shamela0000043-ara1',
   M('Tafsir at-Tabari', 'جامع البيان عن تأويل آي القرآن', 'Imam at-Tabari', 'الإمام الطبري', 310, 'quran'), {}),
 ('qurthubi', '0671AbuCabdAllahQurtubi.JamicLiAhkamQuran.Shamela0020855-ara1',
   M('Tafsir al-Qurtubi', 'الجامع لأحكام القرآن', 'Imam al-Qurtubi', 'الإمام القرطبي', 671, 'quran'), {}),
 ('baghawi', '0510IbnMascudBaghawi.Tafsir.Shamela0000041-ara1.completed',
   M('Tafsir al-Baghawi', 'معالم التنزيل', 'Imam al-Baghawi', 'الإمام البغوي', 510, 'quran'), {}),
 ('itqan', '0911Suyuti.Itqan.Shamela0011728-ara1',
   M("Al-Itqan fi 'Ulum al-Qur'an", 'الإتقان في علوم القرآن', 'Imam as-Suyuti', 'الإمام السيوطي', 911, 'quran'), {}),
 ('tibyan', '0676Nawawi.Tibyan.Shamela0001969-ara1',
   M("At-Tibyan fi Adab Hamalat al-Qur'an", 'التبيان في آداب حملة القرآن', 'Imam an-Nawawi', 'الإمام النووي', 676, 'quran'), {}),
 ('sirahhisyam', '0213IbnHisham.SiraNabawiyya.Shamela0023833-ara1.completed',
   M('Sirah Ibn Hisham', 'السيرة النبوية لابن هشام', 'Ibn Hisham', 'ابن هشام', 213, 'sirah'), {}),
 ('zadulmaad', '0751IbnQayyimJawziyya.ZadMacad.Shamela0021713-ara1',
   M("Zad al-Ma'ad", 'زاد المعاد في هدي خير العباد', 'Ibn al-Qayyim', 'ابن قيم الجوزية', 751, 'sirah'), {}),
 ('qisasanbiya', '0774IbnKathir.QisasAnbiya.Shamela0000932-ara1',
   M("Qisas al-Anbiya'", 'قصص الأنبياء', 'Ibn Kathir', 'ابن كثير', 774, 'sirah'), {}),
 ('bidayahnihayah', '0774IbnKathir.Bidaya.Shamela0004445-ara1.completed',
   M('Al-Bidayah wa an-Nihayah', 'البداية والنهاية', 'Ibn Kathir', 'ابن كثير', 774, 'tarikh'), {}),
 ('tarikhkhulafa', '0911Suyuti.TarikhKhulafa.Shamela0011997-ara1.completed',
   M('Tarikh al-Khulafa', 'تاريخ الخلفاء', 'Imam as-Suyuti', 'الإمام السيوطي', 911, 'tarikh'), {}),
 ('adzkar', '0676Nawawi.Adhkar.Shamela0010639-ara1',
   M('Al-Adhkar', 'الأذكار', 'Imam an-Nawawi', 'الإمام النووي', 676, 'adab'), {}),
 ('ahkamsulthaniyah', '0450AbuHasanMawardi.AhkamSultaniyya.Shamela0022881-ara1.mARkdown',
   M('Al-Ahkam as-Sultaniyyah', 'الأحكام السلطانية', 'Al-Mawardi', 'الماوردي', 450, 'siyasah'), {}),
 ('siyasahsyariyah', '0728IbnTaymiyya.SiyasaSharciyya.Shamela0031237-ara1',
   M("As-Siyasah ash-Shar'iyyah", 'السياسة الشرعية', 'Ibn Taymiyyah', 'ابن تيمية', 728, 'siyasah'), {}),
 ('hisbah', '0728IbnTaymiyya.Hisba.Shamela0007263-ara1',
   M('Al-Hisbah fi al-Islam', 'الحسبة في الإسلام', 'Ibn Taymiyyah', 'ابن تيمية', 728, 'siyasah'), {}),
 ('wasithiyah', '0728IbnTaymiyya.CaqidaWasitiyya.Shamela0022665-ara1',
   M("Al-'Aqidah al-Wasitiyyah", 'العقيدة الواسطية', 'Ibn Taymiyyah', 'ابن تيمية', 728, 'tazkiyah'), {}),
 ('daawadawa', '0751IbnQayyimJawziyya.DaWaDawa.Shamela0000158-ara1',
   M("Ad-Da' wa ad-Dawa'", 'الداء والدواء', 'Ibn al-Qayyim', 'ابن قيم الجوزية', 751, 'tazkiyah'), {}),
 ('madarij', '0751IbnQayyimJawziyya.MadarijSalikin.Shamela0008370-ara1',
   M('Madarij as-Salikin', 'مدارج السالكين', 'Ibn al-Qayyim', 'ابن قيم الجوزية', 751, 'tazkiyah'), {}),
 ('wabil', '0751IbnQayyimJawziyya.WabilSayyib.Shamela0000216-ara1',
   M('Al-Wabil as-Sayyib', 'الوابل الصيب من الكلم الطيب', 'Ibn al-Qayyim', 'ابن قيم الجوزية', 751, 'tazkiyah'), {}),
]

NOISE = re.compile(r'PageV\d+P\d+|\bms\d+\b|#~:\w+:|@\w+@|\bAUTO\b')
def tidy(s):
    s = NOISE.sub(' ', s).replace('%~%', '  ').replace('�', '')
    return re.sub(r'[ \t]+', ' ', s).strip()

def parse(path, until=None):
    t = open(path, encoding='utf-8').read()
    t = t.split('#META#Header#End#', 1)[-1]
    if until:
        i = t.find(until); t = t[:i] if i > 0 else t
    items = []  # ('h', level, text) | ('p', text)
    cur = None
    for line in t.splitlines():
        if line.startswith('### '):
            m = re.match(r'### (\|+) ?(.*)', line)
            if cur: items.append(('p', cur)); cur = None
            if m:
                txt = tidy(m.group(2))
                if txt: items.append(('h', len(m.group(1)), txt))
            continue
        if line.startswith('# '):
            if cur: items.append(('p', cur))
            cur = line[2:]
        elif line.startswith('~~'):
            cur = (cur + ' ' if cur else '') + line[2:]
        elif re.fullmatch(r'\s*PageV\d+P\d+\s*', line) or not line.strip():
            continue
        else:
            cur = (cur + ' ' if cur else '') + line
    if cur: items.append(('p', cur))
    out = []
    for it in items:
        if it[0] == 'p':
            s = tidy(it[1])
            if s and not re.fullmatch(r'[\W\d_]*', s): out.append(('p', s))
        else: out.append(it)
    return out

def pick_level(items):
    """Level judul terdangkal yang membagi kitab jadi bab yang cukup kecil."""
    levels = sorted({it[1] for it in items if it[0] == 'h'})
    total = sum(len(it[1].encode()) for it in items if it[0] == 'p')
    best = None
    for L in levels:
        n = sum(1 for it in items if it[0] == 'h' and it[1] <= L)
        best = L
        if n >= 8 and total / max(n, 1) <= 60_000: break
    return best

def build(bid, fname, meta, opt):
    items = parse(os.path.join(SRC, fname), opt.get('until'))
    L = pick_level(items) if any(i[0] == 'h' for i in items) else None
    hadith = opt.get('hadith')
    secs = []  # [title, rows]
    cur = None; n = 0; last_h = 0
    def new_sec(title):
        nonlocal cur
        cur = [title, []]; secs.append(cur)
    def add_row(r):
        if cur is None: new_sec(meta['ar'])
        cur[1].append(r)
    for it in items:
        if it[0] == 'h':
            if L is not None and it[1] <= L:
                new_sec(it[2])
            else:
                add_row([n + 0.5, it[2], '', '', '', '', '', '', 1])
            continue
        txt = it[1]
        if hadith:
            # nomor hadits bisa muncul di tengah paragraf sumber: pecah di "N - " bila N = nomor berikutnya
            pieces, pos = [], 0
            for mm in re.finditer(r'(?<!\S)(\d{1,5}) - ', txt):
                if mm.start() > 0 and int(mm.group(1)) == last_h + 1 + len(pieces):
                    pieces.append(mm.start())
            if pieces:
                cuts = [0] + pieces + [len(txt)]
                segs = [txt[a:b].strip() for a, b in zip(cuts, cuts[1:])]
                head, rest = segs[0], segs[1:]
            else:
                head, rest = txt, []
            for txt in [head] + rest:
              if not txt: continue
              m = re.match(r'(\d+)\s*-\s*', txt)
              if m and int(m.group(1)) > last_h:
                last_h = int(m.group(1)); n = last_h
                add_row([n, txt]); continue
              rows = cur[1] if cur else []
              if rows and rows[-1][0] == n and len(rows[-1]) == 2:
                rows[-1][1] += '\n' + txt
              else:
                add_row([n + 0.5, txt, '', '', '', '', '', '', 1]) if len(txt) < 80 else add_row([n + 0.25, txt])
            continue
        if False:
            m = None
            if m and int(m.group(1)) > last_h:
                last_h = int(m.group(1)); n = last_h
                add_row([n, txt]); continue
            rows = cur[1] if cur else []
            if rows and rows[-1][0] == n and len(rows[-1]) == 2:
                rows[-1][1] += '\n' + txt
            else:
                add_row([n + 0.5, txt, '', '', '', '', '', '', 1]) if len(txt) < 80 else add_row([n + 0.25, txt])
            continue
        n += 1; add_row([n, txt])
    # pecah bab besar; buang bab kosong
    final = []
    for title, rows in secs:
        if not any(len(r) == 2 for r in rows):
            if final and rows: final[-1][1].extend(rows)  # subjudul tanpa isi: gabung ke bab sebelumnya
            continue
        parts = [[]]; size = 0
        for r in rows:
            s = len(r[1].encode())
            if size and size + s > SEC_MAX and len(r) == 2:
                parts.append([]); size = 0
            parts[-1].append(r); size += s
        for i, p in enumerate(parts):
            final.append([title + (f' ({i+1})' if len(parts) > 1 else ''), p])
    # tulis chunk
    entries = []; chunk = {}; size = 0; ci = 0
    def flush():
        nonlocal chunk, size, ci
        if chunk:
            json.dump(chunk, open(f'{OUT}/{bid}-{ci}.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
            ci += 1; chunk = {}; size = 0
    for i, (title, rows) in enumerate(final, 1):
        s = len(json.dumps(rows, ensure_ascii=False).encode())
        if size and size + s > LIMIT: flush()
        k = str(i); chunk[k] = rows; size += s
        body = [r for r in rows if len(r) == 2]
        entries.append({'k': k, 't': title, 'ta': '', 'c': len(body), 'f': body[0][0], 'l': body[-1][0], 'ch': ci})
    flush()
    e = dict(meta); e.update(id=bid, secs=entries, total=sum(s['c'] for s in entries), chunks=ci,
                             src=f'OpenITI: {fname} (CC BY-NC-SA 4.0)')
    print(f'{bid:14} level={L} secs={len(entries):5} chunks={ci:3} texts={e["total"]}')
    return e

if __name__ == '__main__':
    only = set(sys.argv[3:])
    idx = json.load(open(f'{OUT}/index.json', encoding='utf-8'))
    ids = {b[0] for b in BOOKS}
    for b in BOOKS:
        if only and b[0] not in only: continue
        for f in os.listdir(OUT):
            if re.fullmatch(re.escape(b[0]) + r'-\d+\.json', f): os.remove(f'{OUT}/{f}')
        e = build(*b)
        idx = [x for x in idx if x['id'] != b[0]] + [e]
    order = {b[0]: i for i, b in enumerate(BOOKS)}
    idx.sort(key=lambda x: (x['id'] in ids, order.get(x['id'], 0)))
    json.dump(idx, open(f'{OUT}/index.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
