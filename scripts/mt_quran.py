"""Isi otomatis terjemah kutipan ayat utuh dengan terjemah resmi yang sudah ada di situs.

Pemakaian:  python scripts/mt_quran.py d <kitab>
Baris yang isinya hanya kutipan ayat {..} [Nama Surah: ayat(-ayat)] dan kutipannya mencakup
ayat secara utuh diberi terjemah Kemenag RI (Indonesia) dan M. Pickthall (Inggris) dari data
Al-Qur'an situs ini. Hasil: scripts/mt/<kitab>_90.json. Baris lain dicetak untuk diterjemah manual.
"""
import json, os, re, sys
D, bid = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
HAR = re.compile('[ؐ-ًؚ-ٰٟۖ-ۭـ]')
def norm(t):
    t = HAR.sub('', t or '')
    t = re.sub('[أإآٱ]', 'ا', t).replace('ى', 'ي').replace('ة', 'ه')
    return re.sub(r'[^ء-ي ]', '', t).replace(' ', '')

idx = json.load(open(f'{D}/index.json', encoding='utf-8'))
q = next(b for b in idx if b['id'] == 'quran')
names, latin = {}, {}
for s in q['secs']:
    n = int(s['k'])
    a = norm(s.get('ta', '')).replace('سوره', '')
    names[a] = n; names[a[2:] if a.startswith('ال') else 'ال' + a] = n
    latin[n] = s['t'].split(' · ')[0]
ALIAS = {'بنياسراييل': 17, 'المومن': 40, 'غافر': 40, 'براءه': 9, 'التوبه': 9, 'حمالسجده': 41, 'فصلت': 41, 'الدهر': 76, 'الانسان': 76,
         'تبارك': 67, 'الملك': 67, 'المجادله': 58, 'المجادلة': 58, 'ص': 38, 'ق': 50, 'طه': 20, 'يس': 36, 'النمل': 27}
names.update(ALIAS)
verses = {}
for c in range(q['chunks']):
    for k, rows in json.load(open(f'{D}/quran-{c}.json', encoding='utf-8')).items():
        for r in rows: verses[(int(k), r[0])] = r

b = next(x for x in idx if x['id'] == bid)
out, manual = {}, []
PAT = re.compile(r'^\W*(?:و?قوله(?: تعالى| سبحانه| عز وجل)?\W*)?\{(.+?)\}\s*\[([^\]:]+):\s*(\d+)(?:\s*-\s*(\d+))?\]\W*$')
for c in range(b['chunks']):
    for k, rows in json.load(open(f'{D}/{bid}-{c}.json', encoding='utf-8')).items():
        for r in rows:
            if len(r) > 8 and r[8]: continue
            m = PAT.match(r[1].strip())
            ok = False
            if m:
                quote, sname, a1 = m.group(1), norm(m.group(2)), int(m.group(3))
                a2 = int(m.group(4) or a1)
                sn = names.get(sname) or names.get(sname.replace('سوره', ''))
                if sn and all((sn, a) in verses for a in range(a1, a2 + 1)):
                    full = ''.join(norm(verses[(sn, a)][1]) for a in range(a1, a2 + 1))
                    qq = norm(quote)
                    if full and len(qq) >= 0.9 * len(full) and len(qq) <= 1.1 * len(full):
                        idt = ' '.join(verses[(sn, a)][3] for a in range(a1, a2 + 1))
                        ent = ' '.join(verses[(sn, a)][2] for a in range(a1, a2 + 1))
                        ref = f'{a1}' + (f'–{a2}' if a2 != a1 else '')
                        lead = r[1].strip().startswith(('وقوله', 'قوله'))
                        out[str(r[0])] = {'id': (('Firman-Nya: ' if lead else '') + f'"{idt}" (QS. {latin[sn]}: {ref}; terj. Kemenag RI)'),
                                          'en': (('And His saying: ' if lead else '') + f'"{ent}" (Qur\'an {latin[sn]} {ref}; tr. Pickthall)')}
                        ok = True
            if not ok: manual.append(f'{r[0]}| {r[1]}')
json.dump(out, open(os.path.join(HERE, 'mt', f'{bid}_90.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(f'# otomatis: {len(out)} baris; manual: {len(manual)} baris')
print('\n'.join(manual))
