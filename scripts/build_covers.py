"""Sampul dari scan cetakan lama (domain publik, terbit sebelum 1929) di Internet Archive.

Pemakaian:  python scripts/build_covers.py d
Mengunduh halaman terpilih lewat IIIF archive.org, memotong latar gelap hasil scan,
menyimpan covers/<id>.webp, dan mencatat "cover" + "coverSrc" di d/index.json.
Kitab tanpa scan lama yang jelas tetap memakai sampul jilid kulit buatan situs.
"""
import io, json, os, sys, urllib.request
from PIL import Image, ImageOps

D = sys.argv[1]
# id kitab: (identifier archive.org, nomor halaman, keterangan cetakan)
COVERS = {
 'bukhari': ('harris_038a', 0, 'Sahih al-Bukhari, jilid kulit (ca. 1800)'),
 'muslim': ('AAlexandrina-106677', 4, 'Sahih Muslim, cetakan Istanbul (awal abad ke-20)'),
 'tirmidhi': ('jamialtirmidhi00tirm', 4, "Jami' at-Tirmidzi, litografi India"),
 'malik': ('1_20230831_20230831_0947', 0, "Syarh az-Zurqani 'ala al-Muwaththa' (1892)"),
 'nawawi': ('AAlexandrina-193566', 4, "Matn al-Arba'in an-Nawawiyyah (1903)"),
 'quran': ('mushafMukhalatiCollated', 0, 'Mushaf (ca. 1890)'),
 'jalalayn': ('baha-2026-10', 5, 'Tafsir al-Jalalain, cetakan batu (1874)'),
 'ihya': ('20230623_20230623_0636', 0, "Ihya' 'Ulum ad-Din, cetakan batu India (1864)"),
 'bidayah': ('AAlexandrina-140979', 0, 'Bidayat al-Hidayah, sampul kertas (1908)'),
 'munqidh': ('AAlexandrina-144980', 4, 'Al-Munqidh min ad-Dalal, halaman pembuka (abad ke-19)'),
 'itibar': ('AAlexandrina-143316', 4, "Kitab al-I'tibar, ed. Derenbourg (1886)"),
 'hayy': ('bim_eighteenth-century_the-improvement-of-human_abu-bakr-ibn-al-tufail-_1711', 0, 'Hayy ibn Yaqzan, gravir frontispiece (1711)'),
 'hayyen': ('bim_eighteenth-century_the-improvement-of-human_abu-bakr-ibn-al-tufail-_1711', 1, 'The Improvement of Human Reason, Ockley (1711)'),
 'alchemy': ('alchemyofhappine00algh', 0, 'The Alchemy of Happiness, Field (1910)'),
 'qanun': ('6652963.med.yale.edu', 0, 'Al-Qanun fi at-Tibb, jilid kulit (1811)'),
 'fathulbari': ('AAlexandrina-224158', 4, 'Hady as-Sari, Muqaddimah Fath al-Bari (1928)'),
 'baghawi': ('MS.ARA.102', 0, "Ma'alim at-Tanzil, jilid naskah (1833)"),
 'itqan': ('AAlexandrina-187992', 4, "Al-Itqan fi 'Ulum al-Qur'an (1925)"),
 'tarikhkhulafa': ('AAlexandrina-193521', 0, "Tarikh al-Khulafa', sampul kertas (1913)"),
 'adzkar': ('BULAC.RES.MON.4.132', 0, 'Al-Adhkar, jilid kulit (1865)'),
}

def fetch(ident, k, w=560):
    for url in (f'https://archive.org/download/{ident}/page/n{k}_w{w}.jpg',
                f'https://iiif.archive.org/iiif/3/{ident}${k}/full/{w},/0/default.jpg'):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (MaktabahIlmu cover builder)'})
            with urllib.request.urlopen(req, timeout=90) as r:
                return Image.open(io.BytesIO(r.read())).convert('RGB')
        except Exception:
            pass
    return None

def trim_dark(im):
    g = ImageOps.grayscale(im)
    box = g.point(lambda v: 255 if v > 48 else 0).getbbox()
    if box and (box[2] - box[0]) > im.width * .5 and (box[3] - box[1]) > im.height * .5:
        im = im.crop(box)
    return im

if __name__ == '__main__':
    os.makedirs('covers', exist_ok=True)
    idx = json.load(open(f'{D}/index.json', encoding='utf-8'))
    byid = {b['id']: b for b in idx}
    for bid, (ident, k, note) in COVERS.items():
        if bid not in byid: continue
        im = fetch(ident, k)
        if im is None:
            print('gagal', bid); continue
        im = trim_dark(im)
        im.thumbnail((420, 620))
        im.save(f'covers/{bid}.webp', 'WEBP', quality=80, method=6)
        byid[bid]['cover'] = f'covers/{bid}.webp'
        byid[bid]['coverSrc'] = f'{note} - archive.org/details/{ident}'
        print(f'{bid:16} {im.size} {ident}')
    json.dump(idx, open(f'{D}/index.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
