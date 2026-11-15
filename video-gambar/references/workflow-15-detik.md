# Workflow Iklan 15 Detik (diadaptasi dari @okapi_fukugyo, 7 Nov 2026)

Sumber alur ini adalah postingan
https://x.com/okapi_fukugyo/status/2119064562284831078
yang ditujukan untuk pemula total. Versi di sini diadaptasi untuk Muse:
Muse berperan sebagai sutradara, pembuat gambar, dan penggerak video,
sehingga pengguna cukup memberi tema dan memilih ide.

Catatan: roadmap 30 hari menuju penjualan pertama yang detail ada di artikel
berbayar penulis di note.com. Artikel itu tidak termasuk dalam skill ini.
Yang dipakai di sini hanya alur enam langkah gratis dari postingannya.

## Langkah 1: tentukan tema (5 menit)

Pilih tema yang dekat dan menyenangkan untuk dibuat, misalnya promosi kafe
atau perkenalan hewan peliharaan. Tema yang menyenangkan lebih mudah
diselesaikan sampai jadi daripada tema yang ambisius tapi membosankan.

## Langkah 2: buka Muse sebagai sutradara (3 menit)

Muse sudah terbuka di chat ini. Tidak ada pendaftaran atau aplikasi lain
yang diperlukan untuk tahap rancangan.

## Langkah 3: minta rancangan lengkap (1 menit)

Minta Muse menyusun rancangan dengan template berikut, ganti [tema] dengan
tema dari langkah 1:

> Kamu adalah sutradara iklan media sosial. Buatkan iklan animasi 15 detik
> untuk [tema], format vertikal. Berikan 3 ide konsep, deskripsi karakter
> utama, storyboard 5 cut masing-masing 3 detik, dan prompt gambar bahasa
> Inggris untuk setiap cut. Jelaskan tanpa istilah teknis.

Hasil langkah ini adalah cetak biru video: ide, karakter, storyboard, dan
prompt gambar. Jangan generate gambar sebelum cetak biru ini ada.

## Langkah 4: pilih satu ide (5 menit)

Pilih ide yang paling menarik. Bila ragu, pilih yang paling lucu atau
paling menggemaskan. Satu ide yang dieksekusi penuh lebih baik daripada
tiga ide yang setengah jalan.

## Langkah 5: buat gambar diam lalu gerakkan (30 menit)

Tempel prompt gambar tiap cut ke `media.generate_image` untuk membuat
gambar diam, lalu gerakkan tiap gambar dengan ffmpeg Ken Burns memakai
`scripts/kenburns-seg.sh`.
Prompt yang lahir dari storyboard jauh lebih tepat sasaran daripada prompt
yang dikarang langsung tanpa rancangan.

Rakit segmen-segmen menjadi satu video 15 detik dengan concat ffmpeg atau
`scripts/stitch-clips.sh`. Periksa frame tengah tiap cut secara visual
sebelum menyatakan selesai.

## Langkah 6: posting (5 menit)

Posting video ke X dengan teks singkat bahwa video ini dibuat dengan AI
dan bahwa pengguna bisa membuatkan video perkenalan toko atau produk.
Video pertama yang tayang lebih berharga daripada video sempurna yang
tidak pernah diposting.

## Roadmap 30 hari (ringkasan umum)

- Minggu 1: selesaikan satu video sampai tayang.
- Minggu 2: buat portofolio tiga video.
- Minggu 3: tawarkan satu video gratis ke toko kenalan.
- Minggu 4: ambil satu job berbayar pertama.

Setelah portofolio ada, yang menentukan adalah cara menawarkan jasa, bukan
lagi cara membuat video: harga, cara menyapa calon klien, dan alur
penyerahan hasil.
