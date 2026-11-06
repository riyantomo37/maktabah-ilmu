# Maktabah Ilmu: Daftar Tambahan & Prompt Lanjutan

File ini untuk Claude Code di PC. Buka terminal di folder `maktabah-ilmu`, jalankan `claude`, lalu tulis:

> Baca `README.md` dan `ROADMAP.md`. Kerjakan roadmap ini bertahap sesuai urutan prioritas. Di awal setiap tahap, tunjukkan dulu rencananya ke saya. Setelah tiap tahap selesai, jalankan website secara lokal, cek hasilnya, lalu commit.

---

## Konteks singkat untuk Claude Code

- Website statis: `index.html` (UI + logika, vanilla JS) + `d/index.json` (katalog) + `d/<id>-<n>.json` (isi kitab, dipecah per ±1,6 MB).
- Format baris: `[nomor, arab, inggris, indonesia, derajat_atau_"H", jepang, ayat_quran, nomor_akhir]`. Kolom yang tidak ada boleh dikosongkan atau dipotong.
- Jenis kitab (`kind`) di katalog:
  - `hadith`: setiap baris satu hadits.
  - `quran`: setiap baris satu ayat.
  - `tafsir`: setiap baris satu kelompok ayat, kolom ke-7 berisi teks ayatnya.
  - `prose`: prosa per paragraf. Baris dengan kolom ke-5 = `"H"` adalah subjudul.
- Rak di layar diatur oleh `CATS` di `index.html`. Nama, warna, dan tinggi punggung buku ada di `LOCAL`, `SPINE`, `SPINE_AR`, `COLORS`, `HEIGHT`.
- Pola builder yang sudah ada:
  - `scripts/build.py`: Kutubus Sittah.
  - `scripts/build2.py`: Al-Qur'an, tafsir, dan hadits lain.
  - `scripts/build3.py`: kitab prosa dari file OpenITI mARkdown (contohnya Tarikh Ibnu Khaldun). Pola inilah yang dipakai untuk hampir semua kitab baru di bawah.
- Pindah dari Claude artifact ke GitHub Pages membuat batas 256 MB hilang. Batas GitHub sekitar 1 GB per repo dan 100 MB per file, jadi kitab besar seperti Tarikh ath-Thabari sekarang muat.

## Sumber teks kitab klasik: OpenITI

- Korpus: `https://github.com/OpenITI/<XXXX>AH`. `XXXX` adalah tahun wafat penulis (Hijriah), dibulatkan ke atas ke kelipatan 25. Contoh: wafat 204 H masuk `0225AH`, wafat 774 H masuk `0775AH`.
- Path file: `data/<URI_penulis>/<URI_kitab>/<URI_kitab>.<versi>-ara1` (kadang berakhiran `.mARkdown` atau `.completed`).
- Contoh yang sudah dipakai: `0825AH/data/0808IbnKhaldun/0808IbnKhaldun.Tarikh/0808IbnKhaldun.Tarikh.Shamela0012320-ara1.mARkdown`.
- Cari URI dan versi yang tepat lewat metadata OpenITI (rilis di Zenodo, atau katalog `catalog.perseus.org` dengan `urn:cts:arabicLit:<URI>`). Kalau ada beberapa versi, pilih yang berakhiran `.mARkdown`/`.completed`, atau yang paling lengkap dan punya penanda halaman `PageV..P..`.
- Selalu catat edisi (`#META# 040.EdEDITOR`, `043.EdPUBLISHER`) di katalog (`src`) dan di README.

---

## Tahap 1: Online (prioritas tertinggi)

- [x] Buat repo GitHub publik `maktabah-ilmu`, push, aktifkan GitHub Pages (branch `main`, root).
- [ ] Cek di HP: rak, mode Buku, mode fokus, ganti bahasa, pembatas.

## Tahap 2: Rak baru "Fikih & Ushul Fikih" (teks Arab, OpenITI)

Imam Abu Hanifah dan mazhab Hanafi:
- [x] *Al-Fiqh al-Akbar* (dinisbatkan kepada Abu Hanifah, w. 150 H). Tampilkan catatan bahwa penisbatannya diperdebatkan.
- [x] *Kitab al-Atsar* (riwayat Abu Yusuf atau Muhammad asy-Syaibani).
- [x] *Al-Kharaj*, Abu Yusuf (w. 182 H).
- [x] *Al-Jami' ash-Shaghir* / *As-Siyar al-Kabir*, Muhammad asy-Syaibani (w. 189 H), kalau tersedia.

Imam Malik dan mazhab Maliki:
- [x] *Al-Mudawwanah al-Kubra*, Sahnun (w. 240 H), berisi jawaban Imam Malik riwayat Ibnul Qasim.
- [x] *Ar-Risalah*, Ibnu Abi Zaid al-Qairawani (w. 386 H).
- [x] *Al-Muwafaqat*, asy-Syathibi (w. 790 H), tentang maqashid syariah.
- [x] *Bidayatul Mujtahid*, Ibnu Rusyd (w. 595 H), tentang fikih perbandingan mazhab.

Imam asy-Syafi'i:
- [x] *Ar-Risalah* (URI OpenITI: `0204IbnIdrisShafici.Risala`), kitab ushul fikih pertama.
- [x] *Al-Umm* (`0204IbnIdrisShafici.Umm`).
- [x] *Ikhtilaf al-Hadits* dan *Musnad asy-Syafi'i*, kalau tersedia.
- [x] *Diwan asy-Syafi'i* (syair hikmah), kalau tersedia.

(Kitab Imam Ahmad sudah ada. Musnad Ahmad lengkap bisa dicari juga di OpenITI `0250AH`, lihat Tahap 6.)

## Tahap 3: Rak "Sejarah & Peradaban" (dari masa awal hingga modern)

Urutkan di rak sesuai zaman yang diliput:
- [x] *Tarikh al-Khulafa'*, as-Suyuthi (w. 911 H): biografi para khalifah.
- [x] *Tarikh ar-Rusul wal-Muluk* (Tarikh ath-Thabari, w. 310 H): sejarah hingga 302 H.
- [x] *Muruj adz-Dzahab*, al-Mas'udi (w. 346 H).
- [x] *Al-Kamil fit-Tarikh*, Ibnul Atsir (w. 630 H): hingga 628 H, termasuk Perang Salib dan awal serangan Mongol.
- [x] *Al-Bidayah wan-Nihayah*, Ibnu Katsir (w. 774 H).
- [ ] *Tarikh al-Islam* dan/atau *Siyar A'lam an-Nubala'*, adz-Dzahabi (w. 748 H). Keduanya sangat besar, jadi pertimbangkan dimasukkan bertahap.
- [x] *'Aja'ib al-Atsar*, al-Jabarti (w. 1240 H): Mesir masa Utsmani hingga Muhammad Ali.
- [x] *Tarikh ad-Daulah al-'Aliyyah al-'Utsmaniyyah*, Muhammad Farid Bek (w. 1338 H / 1919 M).
- (Sudah ada: Muqaddimah, Al-'Ibar II, Al-'Ibar III, At-Ta'rif karya Ibnu Khaldun.)
- [ ] Tambahan: halaman/garis waktu "Zaman-zaman Islam" yang menautkan setiap era ke kitab dan bab yang membahasnya: Nabi ﷺ, Khulafaur Rasyidin, Umayyah, Abbasiyah, Andalusia, Fathimiyah, Ayyubiyah, Mamluk, Utsmani, runtuhnya khilafah 1924, dan zaman modern.

## Tahap 4: Rak "Bacaan Kontemporer" (ringkasan + tautan, BUKAN teks lengkap)

Semua karya di bawah masih dilindungi hak cipta. Buat kartu buku berisi: judul, penulis, tahun, bahasa, ringkasan singkat yang ditulis sendiri, dan tautan ke penerbit resmi, toko, atau perpustakaan digital legal. Masukkan teks lengkap hanya kalau penulis, ahli waris, atau lembaganya membebaskan karya itu secara resmi.

Fikih & pemikiran (wasathiyah):
- Yusuf al-Qaradawi: *Al-Halal wal-Haram fil-Islam*, *Fiqh az-Zakah*, *Fiqh al-Awlawiyyat*, *Ash-Shahwah al-Islamiyyah baina al-Juhud wat-Tatharruf*.
- Muhammad al-Ghazali (Mesir): *Khuluq al-Muslim*, *As-Sunnah an-Nabawiyyah baina Ahlil Fiqh wa Ahlil Hadits*.
- Sayyid Sabiq: *Fiqh as-Sunnah*.
- Wahbah az-Zuhaili: *Al-Fiqh al-Islami wa Adillatuhu*, *Tafsir al-Munir*.
- Abdullah bin Bayyah: karya tentang maqashid, fikih minoritas, perdamaian.
- Abul Hasan Ali an-Nadwi: *Madza Khasiral 'Alam bi Inhithathil Muslimin*.

Indonesia:
- Buya Hamka: *Tafsir al-Azhar*, *Tasawuf Modern*, *Lembaga Hidup*, *Sejarah Umat Islam*.
- M. Quraish Shihab: *Tafsir al-Mishbah*, *Wawasan Al-Qur'an*, *Membumikan Al-Qur'an*.
- KH Hasyim Asy'ari: *Adabul 'Alim wal Muta'allim*. Penulis wafat 1947, jadi teks Arab aslinya kemungkinan sudah bebas. Cek dulu, kalau bebas boleh dimasukkan lengkap.

Sirah & sejarah modern:
- Shafiyyurrahman al-Mubarakfuri: *Ar-Rahiq al-Makhtum*.
- Ali Muhammad ash-Shallabi: seri sirah, Khulafaur Rasyidin, Umayyah, Abbasiyah, *Ad-Daulah al-'Utsmaniyyah: 'Awamil an-Nuhudh wa Asbab as-Suquth*.
- Mahmud Syakir: *At-Tarikh al-Islami* (22 jilid).
- Ahmad Syalabi: *Mausu'ah at-Tarikh al-Islami*.
- Bahasa Inggris: Tamim Ansary *Destiny Disrupted*; Hugh Kennedy *The Prophet and the Age of the Caliphates*; Marshall Hodgson *The Venture of Islam*; Ira Lapidus *A History of Islamic Societies*.

## Tahap 5: Rak "Segera Hadir" yang sudah ada

- [x] *Shahih Ibnu Khuzaimah*, *Shahih Ibnu Hibban*: cari di OpenITI (`0325AH`, `0375AH`).
- [x] *As-Sirah an-Nabawiyyah*, Ibnu Hisyam (w. 218 H): `0225AH`.
- [x] *Zadul Ma'ad*, Ibnul Qayyim (w. 751 H): `0775AH`.
- [x] *Fathul Bari*, Ibnu Hajar (w. 852 H): sangat besar, `0875AH`.
- [x] *Ihya' 'Ulumiddin*, al-Ghazali (w. 505 H): `0525AH`.
- [x] *Tafsir ath-Thabari*, *al-Qurthubi*, *al-Baghawi*: tersedia di `spa5k/tafsir_api`. Pakai pola tafsir di `scripts/build2.py` (kelompokkan ayat yang tafsirnya sama supaya hemat ruang).

## Tahap 6: Melengkapi yang sudah ada

- [x] *Musnad Ahmad* lengkap (sekarang baru 4.305 hadits): cari versi lengkap di OpenITI `0250AH/data/0241IbnHanbal/...`. Teks Indonesia lengkap hanya kalau sumbernya legal.
- [ ] Terjemah Indonesia untuk Riyadhus Shalihin, Bulughul Maram, Al-Adab al-Mufrad, kalau ada sumber terbuka.
- [ ] Terjemahkan nama bab/kitab ke bahasa Indonesia dan Jepang (tambah kolom `t_id`, `t_ja` di `d/index.json`).

## Tahap 7: Fitur

- [x] Pencarian teks: indeks per kitab yang hanya dimuat saat dibutuhkan, dengan pencarian Arab tanpa harakat.
- [x] PWA: bisa dipasang di HP dan dibaca offline (service worker + cache data kitab yang pernah dibuka).
- [ ] Garis waktu sejarah interaktif (lihat Tahap 3).
- [ ] Catatan/sorotan pribadi di samping pembatas buku.
- [ ] Domain sendiri lewat Cloudflare (opsional).

---

## Aturan yang wajib dijaga

1. Hanya gunakan sumber dengan lisensi terbuka atau domain publik. Jangan menyalin isi PDF terjemahan cetak yang hak ciptanya tidak jelas.
2. Cantumkan sumber dan edisi setiap kitab di catatan kaki website dan di README.
3. Jangan mengubah teks Arab sumber. Kalau ada huruf yang rusak, tandai dengan ◌, jangan menebak hurufnya.
4. Untuk kitab yang penisbatannya diperdebatkan (misalnya *Al-Fiqh al-Akbar*), tampilkan keterangannya di halaman kitab.
5. Pertahankan desain yang ada: rak kayu, kertas, aksen emas, tema terang & gelap, dan mode Buku dengan proporsi halaman.
6. Website tetap gratis, non-komersial, tanpa iklan.
