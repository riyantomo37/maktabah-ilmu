# Prompt untuk melanjutkan di PC (Claude Code)

Buka terminal di dalam folder `maktabah-ilmu`, jalankan `claude`, lalu tempel prompt di bawah ini.

---

Ini project **Maktabah Ilmu**: website statis perpustakaan ilmu Islam gratis (Al-Qur'an, tafsir, kitab hadits) dengan teks Arab dan terjemah Indonesia, Inggris, Jepang. Baca `README.md` dulu untuk struktur folder dan format data.

Ringkasnya:
- `index.html` berisi seluruh UI dalam satu file (CSS + JS vanilla, tanpa framework). Fitur: rak buku per kategori, halaman detail kitab, mode baca "Buku" (halaman berproporsi buku, 1 atau 2 halaman, animasi balik halaman, ukuran huruf mengikuti ukuran halaman), mode "Gulir", mode fokus, ganti bahasa ID/EN/AR/JA tanpa pindah posisi, pembatas buku per kitab, dan "Lanjutkan membaca" (disimpan di localStorage).
- `d/index.json` adalah katalog; isi kitab ada di `d/<id>-<n>.json`, dimuat dengan `fetch()` relatif.
- `scripts/` berisi skrip Python yang membangun folder `d/` dari sumber data terbuka.

Tugas pertama:
1. Jalankan `python3 -m http.server 8000`, buka website-nya, dan pastikan rak, mode Buku, dan ganti bahasa berjalan.
2. Siapkan Git dan buat repository GitHub publik bernama `maktabah-ilmu` (pakai `gh repo create` kalau `gh` sudah login, atau tunjukkan langkahnya ke saya).
3. Push semua file, aktifkan GitHub Pages dari branch `main` folder root, lalu beri saya link websitenya.

Setelah online, ide lanjutan (tanya saya dulu sebelum mengerjakan):
- Pencarian teks di seluruh kitab (misalnya indeks pencarian per kitab yang dimuat saat dibutuhkan).
- PWA supaya bisa dipasang di HP dan dibaca offline.
- Menambah kitab baru dari `spa5k/tafsir_api` (misalnya Tafsir al-Qurthubi atau al-Baghawi) dengan pola `scripts/build2.py`.
- Menerjemahkan nama bab ke bahasa Indonesia dan Jepang.
- Domain sendiri (misalnya lewat Cloudflare).

Aturan penting:
- Jangan menyalin isi PDF terjemahan cetak yang hak ciptanya tidak jelas. Gunakan hanya sumber dengan lisensi terbuka, dan cantumkan sumbernya di README dan di catatan kaki website.
- Jangan mengubah teks Arab sumber; tandai kerusakan data, jangan menebak hurufnya.
- Pertahankan desain yang sudah ada (rak kayu, kertas, emas, tema terang & gelap).
