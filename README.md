# Maktabah Ilmu · مكتبة العلم

Perpustakaan ilmu Islam gratis yang bisa dibaca siapa saja: Al-Qur'an, kitab tafsir, Kutubus Sittah, dan kitab hadits lainnya dalam teks Arab dengan terjemah Indonesia, Inggris, dan Jepang.

Website ini statis (HTML + JSON), jadi tidak perlu server, database, atau biaya hosting.

## Isi folder

```
index.html        seluruh tampilan & logika (rak buku, mode Buku/Gulir, pembatas, mode fokus)
d/index.json      katalog kitab: judul, bab/surah, dan file data mana yang memuat bab itu
d/<kitab>-<n>.json  isi kitab, dipecah per ~1,6 MB supaya cepat dimuat
scripts/          skrip Python yang membuat folder d/ dari sumber data terbuka
.nojekyll         supaya GitHub Pages tidak mengolah ulang file
s/                indeks kata untuk pencarian (dibuat oleh scripts/build_search.py; jalankan ulang setelah menambah kitab)
vendor/           StPageFlip (efek halaman melengkung) dan pdf.js (menampilkan PDF Arab)
pdf/              PDF Arab karya an-Nabhani, apa adanya dari penerbit
```

Format satu baris teks di `d/<kitab>-<n>.json`:
`[nomor, arab, inggris, indonesia, derajat, jepang, ayat_quran (khusus tafsir), nomor_akhir (khusus tafsir)]`

## Mencoba di komputer sendiri

Halaman memuat data dengan `fetch()`, jadi harus dibuka lewat server lokal, bukan klik dua kali file:

```bash
cd maktabah-ilmu
python3 -m http.server 8000
# buka http://localhost:8000
```

## Online gratis dengan GitHub Pages

1. Buat repository baru di GitHub, misalnya `maktabah-ilmu` (Public).
2. Upload semua isi folder ini (atau `git push`, lihat bawah).
3. Buka **Settings → Pages**, pilih *Deploy from a branch*, branch `main`, folder `/ (root)`, lalu Save.
4. Beberapa menit kemudian website aktif di `https://<username>.github.io/maktabah-ilmu/`.

```bash
cd maktabah-ilmu
git init
git add .
git commit -m "Maktabah Ilmu: versi pertama"
git branch -M main
git remote add origin https://github.com/<username>/maktabah-ilmu.git
git push -u origin main
```

Alternatif tanpa Git: **Cloudflare Pages** atau **Netlify** (seret folder ini ke dashboard mereka).

## Sumber data

| Kitab | Sumber |
|---|---|
| Kutubus Sittah, Muwatta, Arba'in Nawawi, Hadits Qudsi | [fawazahmed0/hadith-api](https://github.com/fawazahmed0/hadith-api) (Unlicense) |
| Al-Qur'an (Utsmani, Kemenag RI, Pickthall, Ryoichi Mita) | [fawazahmed0/quran-api](https://github.com/fawazahmed0/quran-api) |
| Tafsir Ibnu Katsir, as-Sa'di, al-Jalalain, al-Mukhtashar | [spa5k/tafsir_api](https://github.com/spa5k/tafsir_api) |
| Terjemah Indonesia Tafsir al-Jalalain | [Tanzil](https://tanzil.net/trans/) (`id.jalalayn`, non-komersial, teks tidak diubah); `scripts/import_jalalayn_id.py` |
| Musnad Ahmad (sebagian), Sunan ad-Darimi | [gadingnst/hadith-api](https://github.com/gadingnst/hadith-api) |
| Riyadhus Shalihin, Bulughul Maram, Al-Adab al-Mufrad, Syamail, Misykat | [AhmedBaset/hadith-json](https://github.com/AhmedBaset/hadith-json) |
| Karya Imam Ahmad (Musnad lengkap, az-Zuhd, Ushul as-Sunnah), al-Ghazali (Ihya', Bidayatul Hidayah, al-Munqidz, Kimiya' as-Sa'adah, Misykat al-Anwar, Tahafut), Muqaddimah Ibnu Khaldun, Muruj adz-Dzahab, rihlah Ibnu Battutah, Ibnu Jubair, Ibnu Fadhlan, al-I'tibar, 'Aja'ib al-Hind, al-Idrisi, Hayy bin Yaqzhan, Ibnu Sina (al-Qanun, al-Isyarat, an-Najat) | [OpenITI](https://github.com/OpenITI) (CC BY-NC-SA 4.0), teks Arab; dibangun dengan `scripts/build_openiti.py` |
| Tafsir ath-Thabari, al-Qurthubi, al-Baghawi, al-Itqan, at-Tibyan; Shahih Ibnu Khuzaimah, Shahih Ibnu Hibban (al-Ihsan), Fathul Bari; al-Adzkar; Sirah Ibnu Hisyam, Zadul Ma'ad, Qashashul Anbiya'; al-Bidayah wan-Nihayah, Tarikh al-Khulafa'; al-Ahkam as-Sulthaniyyah, as-Siyasah asy-Syar'iyyah, al-Hisbah; al-'Aqidah al-Wasithiyyah, ad-Da' wad-Dawa', Madarijus Salikin, al-Wabil ash-Shayyib | [OpenITI](https://github.com/OpenITI) (CC BY-NC-SA 4.0), teks Arab; `scripts/build_openiti.py` |
| **Fikih & Ushul Fikih**: al-Fiqh al-Akbar & Musnad Abu Hanifah; Kitab al-Atsar (Abu Yusuf & asy-Syaibani), al-Kharaj, al-Jami' ash-Shaghir, as-Siyar; al-Mudawwanah al-Kubra; ar-Risalah al-Qairawani; Bidayatul Mujtahid; al-Muwafaqat; ar-Risalah, al-Umm, Ikhtilaf al-Hadits, Musnad & Diwan asy-Syafi'i | [OpenITI](https://github.com/OpenITI) (CC BY-NC-SA 4.0), teks Arab; edisi cetak tercantum di halaman tiap kitab; `scripts/build_openiti.py` |
| **Sejarah**: Tarikh ath-Thabari, al-Kamil fit-Tarikh (Ibnul Atsir), 'Aja'ib al-Atsar (al-Jabarti), Tarikh ad-Daulah al-'Aliyyah al-'Utsmaniyyah (Muhammad Farid Bek); Kitab al-'Ibar II & III dan at-Ta'rif (Ibnu Khaldun, ed. Khalil Syahadah, Dar al-Fikr 1988) | [OpenITI](https://github.com/OpenITI) (CC BY-NC-SA 4.0), teks Arab |
| Terjemah Inggris: The Confessions of Al Ghazzali & The Alchemy of Happiness (Claud Field), Hayy ibn Yaqzan (Simon Ockley, 1708) | Wikisource & Project Gutenberg (domain publik); dibangun dengan `scripts/build_translations.py` |
| Karya Syekh Taqiyuddin an-Nabhani (24 kitab Arab; terjemah Inggris 10, Indonesia 6) | PDF Arab & terjemah Inggris resmi dari [hizb-ut-tahrir.org](http://www.hizb-ut-tahrir.org/index.php/AR/books) (penerbit mengizinkan penerbitan ulang tanpa diubah dengan menyebut sumber); terjemah Indonesia HTI-Press via archive.org; dibangun dengan `scripts/build_nabhani.py` |
| Sistem Pergaulan dalam Islam (terjemah Indonesia an-Nizham al-Ijtima'i) | HTI-Press 2014 via archive.org [`08SistemPergaulanIslamCet7`](https://archive.org/details/08SistemPergaulanIslamCet7), teks OCR archive.org (PDF-nya memakai font tersandi); `scripts/import_nabhani_ocr.py` |

Sampul sebagian kitab diambil dari scan cetakan lama yang sudah domain publik (terbit sebelum 1929) di Internet Archive (`scripts/build_covers.py`, sumber tercatat di `coverSrc`); sampul kitab an-Nabhani dari halaman pertama PDF resminya; kitab lain memakai sampul jilid kulit buatan situs.

Mode Buku memakai [StPageFlip](https://github.com/Nodlik/StPageFlip) (MIT, `vendor/`) untuk efek halaman melengkung.

Teks Arab kitab klasik adalah warisan bersama. Sebagian terjemah masih milik penerjemahnya, jadi website ini sebaiknya tetap gratis dan non-komersial, dengan sumber tetap dicantumkan.

Sekitar 70 hadits pada data Arab sumber kehilangan satu huruf; di website ditandai dengan ◌.
