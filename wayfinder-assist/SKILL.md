# Pembagian Kerja Wayfinder

Skill ini mengatur pembagian kerja antara Muse dan API Wayfinder (konektor `custom.wayfinder`) untuk tugas riset data. Gunakan skill ini saat pengguna meminta data Wayfinder, digest Wayfinder, scan APY atau delta-neutral, Polymarket trending, ringkasan DefiLlama, postingan X pilihan Wayfinder, atau info wallet Wayfinder pengguna.

## Pembagian peran

- **Aturan tetap dari pengguna (2026-10-31):** kerjaan berat dan rutin diserahkan ke Wayfinder supaya Muse fokus di eksekusi. Tugas data yang berulang atau bervolume besar jalan lewat Wayfinder dulu, bukan lewat browsing atau RPC mentah, selama tipe datanya tersedia di Alpha Lab.
- **Kecepatan terukur (2026-10-31):** median sekitar 0,5 detik per panggilan (types 522 ms, results 527 ms, rings 657 ms, balances 521 ms), digest lengkap 5 tipe sekitar 3,2 detik. Cukup cepat untuk kerja rutin dan batch. Wayfinder tidak dipakai untuk jalur yang balapan dengan waktu eksekusi, karena eksekusi tetap di baw dan RPC BSC.

- **Wayfinder adalah pemasok data, bukan pengambil keputusan.** Ia menyediakan hasil scan Alpha Lab yang sudah jadi: `delta_lab_top_apy`, `delta_lab_best_delta_neutral`, `polymarket_trending`, `defi_llama_overview`, `defi_llama_hack`, `defi_llama_protocol`, `defi_llama_chain_flow`, dan `twitter_post`.
- **Muse adalah penyaring dan verifikator.** Muse menarik data lewat helper konektor, memeriksa tanggal `created` tiap item, menyaring yang basi, mengecek silang klaim penting ke sumber lain bila akan dipakai untuk keputusan, lalu menyimpulkan dalam Bahasa Indonesia.
- **Pengguna adalah pemberi keputusan.** Data Wayfinder tidak pernah menjadi perintah untuk membeli, menjual, mint, atau menandatangani apa pun. Semua tindakan harga tetap mengikuti aturan konfirmasi nominal pengguna.

## Perintah

Helper: `~/workspace/custom-connectors/custom.wayfinder/bin/client.py`

- Digest lintas tipe (paling sering dipakai): `python3 ~/workspace/custom-connectors/custom.wayfinder/bin/client.py digest --limit 3`
- Satu tipe: `python3 ~/workspace/custom-connectors/custom.wayfinder/bin/client.py alpha-results --type <tipe> --sort -created --limit 5`
- Daftar tipe: `python3 ~/workspace/custom-connectors/custom.wayfinder/bin/client.py alpha-types`
- Info wallet Wayfinder pengguna (read-only): `python3 ~/workspace/custom-connectors/custom.wayfinder/bin/client.py get wallets/rings/`

## Aturan kesegaran data

- Selalu tampilkan tanggal `created` untuk item yang dilaporkan. Jangan pernah menyajikan insight Wayfinder tanpa tanggalnya.
- Urutan bawaan `-insightfulness_score` mengembalikan item lama berskor tinggi. Untuk kerja aktual pakai `--sort -created` dan saring lagi menurut tanggal.
- Keadaan per cek 2026-10-31: feed `twitter_post` segar (item terbaru 2026-10-30) dan `defi_llama_overview` cukup segar (2026-10-26), sedangkan feed delta lab (`delta_lab_top_apy`, `delta_lab_best_delta_neutral`) dan `polymarket_trending` berhenti di Mei 2026. Perlakukan feed yang berhenti sebagai arsip, bukan data live, dan katakan itu dengan jelas.

## Format laporan

- Per tipe data: sebutkan nama tipe, jumlah total hasil, lalu 1–3 item terpilih dengan tanggal, insight satu kalimat, dan angka kunci dari metadata (APY, net APY, venue, simbol) bila ada.
- Tandai dengan jelas mana data Wayfinder yang belum diverifikasi silang. Klaim sensasional dari satu insight tidak boleh dilaporkan sebagai fakta.
- Tutup dengan kesimpulan Muse: apa yang layak ditindaklanjuti, apa yang basi, dan apa yang masih perlu dicek.

## Batas keras

- Read-only. Tidak ada eksekusi strategi, pembuatan wallet, signing, pengiriman transaksi, deposit, atau penarikan lewat Wayfinder, dalam keadaan apa pun, tanpa perintah eksplisit pengguna untuk tindakan spesifik itu plus konfirmasi nominal.
- Research gateway Wayfinder (`/research/websearch/`, `/research/crypto/sentiment/`, `/research/social/x-search/`, `/research/webfetch/`) TIDAK bisa dipakai dengan API key pengguna saat ini (403 `api_key_scope_invalid`, key tidak terikat instance OpenCode). Jangan coba lagi kecuali pengguna menghubungkan key yang terikat instance OpenCode.
- Wallet Wayfinder pengguna boleh dibaca untuk info (alamat, status, saldo). API-nya memang punya endpoint signing untuk shell mereka, tetapi jalur itu di luar cakupan skill dan konektor ini.

## Available connectors

- Peta lengkap semua konektor Wayfinder per tugas ada di [Daftar Konektor API Wayfinder](~/workspace/custom-connectors/WAYFINDER_API_CONNECTORS.md). Pilih konektor menurut tugasnya dan jangan meminjam key tugas lain.
- [Wayfinder](~/workspace/custom-connectors/custom.wayfinder/CONNECTOR.md) untuk data Alpha Lab, digest, dan info wallet Wayfinder.
- [Wayfinder Crowdscan](~/workspace/custom-connectors/custom.wayfinder-crowdscan/CONNECTOR.md) untuk RPC `eth_getLogs` crowd-scan.
- [Wayfinder Walletwatch](~/workspace/custom-connectors/custom.wayfinder-walletwatch/CONNECTOR.md) untuk baca saldo, floor, offer, dan pool wallet pengguna.
