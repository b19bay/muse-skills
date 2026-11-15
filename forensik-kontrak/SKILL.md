---
name: forensik_kontrak
description: Bedah forensik smart contract untuk Immunefi bug bounty dengan POLA PIKIR BERBASIS POLA SERANGAN: mulai dari 68 kasus eksploitasi nyata yang disuling menjadi 21 kartu pola + 5 hukum lapangan, cocokkan target ke pola yang paling mirip, buru invariant nilai sampai patah, dan buktikan dengan PoC fork read-only. Pakai skill ini setiap kali memeriksa kontrak untuk kerentanan/bug bounty, atau saat user meminta bedah keamanan kontrak/repo GitHub.
---

# Forensik Kontrak v2 — Berburu dari Pola, Bukan dari Daftar Fungsi

Protokol lengkap: `~/workspace/immunefi-bounty/PROTOKOL-FORENSIK.md`. Rancangan v2: `~/workspace/immunefi-bounty/RANCANGAN-FORENSIK-UNIVERSAL-V2.md`. Bank pola di folder skill ini: `POLA.md` (21 kartu pola + data frekuensi) dan `KASUS-1` s.d. `KASUS-5` (68 kasus nyata terverifikasi dengan sumber).

## Mengapa v2 (pelajaran yang mahal)

Cara lama — baca kode fungsi demi fungsi, cocokkan checklist 12 kelas, nyatakan bersih — menemukan apa yang dicari checklist dan melewatkan sisanya. Penyerang nyata tidak membaca secara linier: mereka tiba membawa POLA dari kasus yang sudah berhasil (donasi ke pasar kosong, view yang dibaca di tengah callback, harga dari saldo live) dan mencari bentuk pola itu di target baru. Data mendukung mereka: kelas teknik terbesar yang menguras DeFi (access control, manipulasi harga spot, reentrancy, akuntansi saham, donasi) 100% insidennya dapat ditemukan murni dari membaca kode — oleh pembaca yang tahu bentuk apa yang dicari. v2 membalik urutan kerja: **pola dulu, peta kemudian; hipotesis dulu, pembacaan melayani hipotesis.**

## Prinsip inti (tetap)

Forensik menilai kontrak untuk menemukan **KETIMPANGAN**: selisih antara perilaku yang seharusnya (desain, dokumentasi, respon yang diharapkan) dan perilaku aktual. Temuan hanya sah bila ketimpangannya **terbukti** berdampak — inferensi bukan fakta, angka simulasi bukan hasil final, dan hasil "diperiksa, bersih" dicatat sama pentingnya.

## Pola pikir baru (doktrin berburu)

### Lima hukum lapangan — tulang punggung setiap pemeriksaan (detail + data di POLA.md)
- **H1 Batas dua representasi.** Kerugian lahir di batas antara dua representasi dari hal yang sama (saldo internal vs `balanceOf`, harga vs nilai, ambang tertulis vs efektif). Buru batasnya, bukan fungsinya.
- **H2 Angka yang bisa digerakkan tak boleh dipercaya di blok yang sama.** Bila penyerang bisa mengubah angka yang dibaca fungsi bernilai dalam tx/blok yang sama, itu jalur drain.
- **H3 Keadaan kosong/debu paling berbahaya.** Uji selalu pada pasar kosong, supply nol, saldo 1–100 wei, pengguna pertama.
- **H4 Kesalahan kecil yang bisa diulang searah = drain.** Uji pengulangan atomik (loop/batch/flash loan), bukan kejadian tunggal.
- **H5 Prasyarat yang bisa disewa bukan prasyarat.** Untuk setiap syarat, hitung biaya memenuhinya selama tepat satu transaksi.

### Tiga pertanyaan emas — wajib untuk SETIAP fungsi/angka penentu nilai
1. **Siapa yang bisa MENULIS inputnya?** (termasuk lewat donasi, registrasi, event, pesan, observasi oracle — bukan hanya pemanggilan langsung)
2. **Siapa yang MEMBACA hasilnya, dan keputusan nilai apa yang bergantung padanya?** (konsumen angka sering berada di kontrak lain — Sentiment jatuh bukan karena kontraknya sendiri)
3. **Apa yang terjadi pada keadaan kosong, debu, dan pengulangan ke-1.000?**

### Analogi kasus — langkah pertama, bukan langkah terakhir
Sebelum membaca kode secara mendalam, jawab tertulis: "Target ini paling mirip kasus nyata apa, dan kenapa?" Klasifikasikan target ke keluarga (vault 4626 / lending fork / AMM / bridge / staking / governance / aggregator) lalu tarik kartu pola yang relevan dari POLA.md sebagai hipotesis awal. Fork dari protokol terkenal mewarisi bug protokol induknya yang belum ditambal (kelas Compound-fork membuktikan ini berulang kali) — periksa riwayat bug induknya secara eksplisit.

### Berburu invariant, bukan bug
Untuk tiap target, tulis daftar INVARIANT NILAI-nya (contoh: "total klaim tidak pernah melebihi total aset riil", "harga saham tidak berubah oleh transfer biasa", "satu kolateral hanya bisa menanggung satu utang"). Setiap invariant lalu diserang dengan lima tuas universal: **donasi** (ubah saldo tanpa jalur resmi), **callback** (masuk di tengah pembaruan), **urutan** (tukar urutan operasi sah), **debu** (nilai terkecil/keadaan kosong), **sewa** (penuhi prasyarat selama satu blok). Invariant yang selamat dari kelimanya pada fork adalah bukti bersih yang sesungguhnya.

### Komposisi & orde kedua
Kontrak yang aman sendirian bisa jatuh karena (a) siapa yang mengonsumsi angkanya, (b) kontrak apa yang boleh didaftarkan/dipasangkan dengannya tanpa izin, (c) keadaan kontrak lain di tengah operasinya (pool yang sedang exit). Peta permukaan wajib mencakup PEMBACA dan PENULIS eksternal setiap angka penting, bukan hanya kontrak target.

### Waktu adalah permukaan
Periksa garis waktu on-chain: umur tiap kontrak/facet/pasar, celah deploy→init→seed→nilai masuk, upgrade terakhir, peran yang berubah tangan. Keadaan jam pertama adalah keadaan paling telanjang (P-21), dan modul termuda adalah yang paling mungkin melewatkan cek yang dimiliki saudaranya (P-14).

## Alur kerja per target

- **Fase 0 · Scope & analogi.** Aset in-scope, aturan program, alamat/repo/versi compiler dicatat. Analogi kasus + hipotesis pola awal ditulis SEBELUM membaca logika. TVL/dana berisiko diverifikasi dari rantai (bukan hanya DefiLlama).
- **Fase 1 · Peta nilai.** Bukan peta fungsi: peta ANGKA — angka apa yang menjaga nilai (harga, rate, index, root, counter, ambang), siapa menulisnya, siapa membacanya, di batas kepercayaan mana. Ditambah peta permukaan klasik (kontrak × fungsi × aktor) dan graf kendali efektif (P-17).
- **Fase 2 · Uji pola.** Untuk setiap kartu pola yang cocok: jalankan uji termurah yang bisa membuktikan/menggugurkannya (baca terarah, probe read-only live, simulasi fork). Baca kode secara mendalam HANYA di sekitar pola yang belum gugur.
- **Fase 3 · Register unknown & pass sisa.** Semua yang belum diketahui dicatat sebagai unknown berdampak/tidak; jalankan pass yang belum tersentuh: logika, arus ujung-ke-ujung, waktu & urutan, insentif, ketergantungan eksternal, mode kegagalan. Fase divergen (asumsi dibalik, "apa yang tidak seharusnya bisa terjadi?") wajib mendahului fase konvergen (uji bukti). Checklist 12 kelas v1 dipakai di sini sebagai jaring pengaman TERAKHIR, bukan sebagai metode utama: (1) kontrol akses; (2) reentrancy single/cross-function/read-only; (3) pembukuan timpang & inflasi saham; (4) manipulasi oracle/flash loan; (5) replay tanda tangan EIP-712/ecrecover; (6) proxy/initialize/upgrade; (7) pajak/kunci transfer/blacklist; (8) mint/burn tanpa batas; (9) logika waktu/fase/penghitung; (10) arbitrary call/delegatecall/approval; (11) DoS pembeku dana; (12) pembulatan & presisi/desimal.
- **Fase 4 · Pembuktian (PoC fork).** Kandidat yang selamat dibuktikan di fork lokal dekat blok submisi, sebagai akun tanpa hak istimewa, saldo/state sebelum–sesudah tercatat. Standar negatif: uji akses yang revert WAJIB disertai kontrol positif (jalur publik yang memang terbuka harus terbukti sukses di harness yang sama) agar revert bermakna. Standar 4 lapis: bukti source → PoC fork → upaya membantah hipotesis sendiri → cek silang laporan audit/postmortem agar tidak melaporkan temuan lama/terdokumentasi.
- **Fase 5 · Severity.** Petakan dampak TERBUKTI ke matriks program itu sendiri + gerbang khususnya (mis. jalur live, nilai minimum berisiko). Fakta terbukti tanpa dampak dicatat sebagai fakta, tidak dilaporkan.
- **Fase 6 · Laporan.** Format Immunefi, BAHASA INGGRIS (aturan user 2026-11-04): judul, aset in-scope, ringkasan ketimpangan, langkah reproduksi, PoC yang bisa dijalankan ulang, dampak terukur, saran perbaikan. Login Immunefi dipakai hanya pada tahap submit dan hanya bila ada temuan terbukti.
- **Fase 7 · Setor ke bank pola.** Setiap target yang tuntas wajib menyetor: pola baru, atau konfirmasi pola lama, atau pola yang GUGUR beserta bukti gugurnya — ditulis ke POLA.md/KASUS dengan tanggal. Skill harus lebih tajam setelah setiap target.

Satu berkas catatan per target di `~/workspace/immunefi-bounty/<target>/CATATAN-FORENSIK.md` mengikuti fase di atas. Target **tuntas** bila: hipotesis pola awal semuanya terbukti atau tercatat gugur, register unknown tak menyisakan unknown berdampak yang belum diuji, invariant nilai utama sudah diserang dengan lima tuas, dan uji negatif (bila ada) disertai kontrol positif.

## Aturan keras (tidak berubah)

1. Hanya kontrak **in-scope** program Immunefi target yang diburu hadiahnya. Target di luar program hanya atas perintah user.
2. Bukti selalu **read-only**: simulasi eth_call, fork lokal, test vector. Tidak pernah eksploitasi mainnet; tidak menyentuh dana pengguna lain. (Batas disepakati user 2026-11-01; pemicu "lakukan simulasi nyata" tidak mengubah larangan mengambil aset pihak lain.)
3. Satu target dituntaskan per fase; hasil negatif (diperiksa, bersih) dicatat sama pentingnya dengan temuan.
4. Temuan tidak dipublikasikan di luar Immunefi sebelum triase selesai; tidak dipakai untuk keuntungan pribadi.
5. Dampak dinyatakan apa adanya sesuai bukti; tidak over-claim severity. Perilaku yang TERDOKUMENTASI oleh proyek bukan temuan — tetapi implementasi yang MELANGGAR dokumentasinya sendiri adalah ketimpangan inti.
6. Nominal & keadaan diverifikasi dari rantai pada saat pemeriksaan, bukan dari ingatan atau snapshot lama.

## Rute teknis yang terbukti di lingkungan ini

- Baca chain berat lewat pool Wayfinder (`~/workspace/tools/wayfinder-pool/client.py --provider custom.wayfinder-walletwatch rpc ...`); params sebagai SATU argumen array JSON. Allowlist Wayfinder tidak punya eth_getCode/eth_getTransactionReceipt — untuk receipt/input tx pakai RPC publik via curl lewat proxy (drpc/publicnode terbukti untuk ETH/Base/BSC/dll).
- Foundry 1.9.0 di `~/workspace/tools/foundry/bin` (tambahkan ke PATH manual); impersonasi anvil (`anvil_impersonateAccount` + `anvil_setBalance` + `cast send --unlocked --from`) terbukti andal.
- Selector/keccak: `~/workspace/tools/keccak.py`. Alamat di calldata wajib huruf kecil.
- BscScan/Blockscout kadang terblokir untuk otomasi — jalur sumber kode cadangan: Sourcify, repo GitHub resmi proyek, mirror Etherscan. Jangan menyimpulkan "sumber tidak ada" dari satu jalur yang gagal.
- Revert diyakini hanya setelah mendekode satu tx SUKSES (fungsi + argumen + value asli) lalu simulasi ulang dengannya.

## Penunjuk belajar (ditambah 2026-11-04)
- **POLA-PIKIR.md** (folder ini) = cara berpikir jauh: inversi asumsi, klasifikasi efek, tiga peta (angka/waktu/peran), hukum H6–H8, prior frekuensi. WAJIB dibaca di Fase 0 setiap target.
- **REFERENSI.md** = indeks sumber belajar hidup (korpus exploit ter-eksekusi, platform CTF/hack-me, kurikulum, database temuan, agregator).
- **BELAJAR.md** = jurnal studi + rezim latihan (shadow audit, reproduksi PoC DeFiHackLabs, baca berwaktu).
- Kartu gelombang 2: P-22…P-33 di POLA.md; komposit K-07 di POLA-KOMPOSIT.md. Checklist Fase 3 kini mencakup cek frontier: read-only reentrancy, kebasian/sequencer-uptime, phantom permit, transient storage, asumsi EIP-7702, hook pihak ketiga, kuorum verifikator lintas-rantai (dibaca LIVE), token rebasing/FoT, reset klaim sebagian, kesalahan fee, enumerasi peran tepercaya.
