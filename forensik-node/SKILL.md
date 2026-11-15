---
name: forensik_node
description: Forensik Node — audit keamanan codebase node blockchain/L1 (terutama Go) untuk bug bounty, berbasis bank pola nyata dari program XE Protocol (194 laporan publik terpetakan, 4 laporan sendiri). Inti yang membedakan dari audit biasa: (1) petakan SELURUH tracker laporan + labelnya SEBELUM membaca kode — duplikat dinilai per mekanisme, dan peta taken adalah senjata utama; (2) berburu KETIMPANGAN validasi antar-subsistem (verifier memeriksa amplop bukan bukti, disiplin kesegaran yang timpang antar-saudara, cap yang gagal menutup menjadi blackout total); (3) standar laporan yang terbukti dibayar: tabel ringkasan, akar per fungsi:baris, tes deterministik per paket, dampak TERUKUR, batas jujur tertulis, paragraf "Duplicate check:" eksplisit, companion Fix PR format (1) The rule (2) Every site (3) Sibling sweep. Pasangan on-chain dari forensik_kontrak dan pasangan web dari pentest_web. Pakai skill ini setiap kali mengaudit repo node/L1/validator/client blockchain, memburu bounty program berbasis repo kode (bukan kontrak terdeploy), atau saat user meminta audit mendalam codebase Go blockchain.
---

# Forensik Node — Berburu dari Peta Duplikat & Ketimpangan Antar-Subsistem

Bank pola: `POLA-NODE.md` di folder skill ini (16 kartu N-01..N-16). Bahan studi mentah: `~/workspace/xe-bounty/laporan-orang-lain.md` (studi 194 issue + 149 PR XE), `~/workspace/xe-bounty/CATATAN-AUDIT.md` (audit XE ronde 1–3 + penilaian overlap terkoreksi). Kernel yang sama dengan `forensik_kontrak`: cari **KETIMPANGAN** — selisih antara perilaku yang seharusnya (desain, dokumen, invariant) dan perilaku aktual — dan temuan hanya sah setelah terbukti. Yang berubah hanyalah permukaannya: kode node, bukan kontrak; tracker laporan adalah medan perangnya.

## Pelajaran termahal (dari kegagalan nyata, jangan ulangi)

Pada program XE, tiga dari empat temuan terbukti kami ternyata sudah diterbitkan pemburu lain **berminggu-minggu sebelumnya** — bukan karena kalah cepat mengaudit, tetapi karena peta taken pra-audit hanya memuat 1 dari ±194 laporan publik. Tiga audit besar terbit di **hari pembukaan program yang sama**. Maka aturan pertama skill ini bersifat prosedural, bukan teknis: **tidak ada baris audit sebelum peta tracker selesai.**

## Fase 0 — Peta tracker & mekanik program (WAJIB, sebelum menyentuh kode)

1. **Enumerasi seluruh tracker publik**: semua issue + PR (open+closed, semua halaman) di repo target, plus daftar publik meja bounty (reports/leaderboard/stats/log bila ada). Baca label/statusnya: di XE label GitHub adalah cermin status meja (accepted 47 · awarded 27 · duplicate 43 · triaged 32 · invalid 10) dan **issue hampir tidak pernah ditutup — label adalah sinyal hasil, bukan status open/closed**.
2. **Bangun PETA TAKEN per mekanisme**: untuk setiap laporan terdahulu catat fungsi yang cacat + cek yang hilang + lapisnya (validasi inti / propagasi gossip / builder klien / penyimpanan). Duplikat dinilai per **mekanisme**, bukan per topik: laporan bertopik sama dengan fungsi berbeda bisa lolos (kasus #259), laporan bertopik beda dengan mekanisme sama gugur.
3. **Baca bundle para pemenang**: format, kedalaman bukti, dan batas jujur para hunter yang awarded adalah standar de facto program — tiru standarnya, jangan topiknya.
4. **Mekanik meja**: aturan publikasi (privat vs publik sejak pengajuan; tier tim baru tampil setelah fix), plafon vs award nyata (award sering DI BAWAH plafon — contoh Severe dibayar 12.500 dari 25.000), batas laju pengajuan, siapa yang tidak eligible. Catat juga: mengajukan privat menyembunyikan klaimmu dari pemburu lain, tetapi juga membuatmu buta terhadap klaim mereka.
5. **Kecepatan**: kelas terbaik biasanya diambil dalam 72 jam pertama. Untuk program yang baru dibuka: Fase 0 + audit inti di hari pertama, ajukan segera, perdalam belakangan.
6. **ATURAN SUMBER MENTAH (ditambahkan 2026-11-11 malam, dari kegagalan nyata kedua)**: cek duplikat WAJIB berjalan di atas **daftar judul mentah seluruh tracker** (semua issue+PR, semua halaman, diekspor ke file) — BUKAN di atas file studi/ringkasan/peta taken hasil sintesis, karena sintesis membuang judul yang tidak masuk klasternya. Kasus XE ronde 5: file studi tracker tidak pernah memuat judul issue #183 ("renew/settle races permanently split honest nodes", terbit 2026-10-29); grep kata kunci di atas file studi mengembalikan "bersih" padahal mekanismenya persis sudah diambil — tertangkap hanya oleh pencarian judul tracker mentah. Simpan ekspor judul itu sebagai artefak target (mis. `tracker-titles-all.txt`) dan grep di sana, dengan beberapa keluarga kata kunci per mekanisme (fungsi, gejala, akibat).
7. **Pisahkan pembuktian dari penilaian kebaruan**: agen yang membuktikan mekanisme TIDAK menilai kebaruannya sendiri. Agen induk wajib menjalankan ulang cek duplikat dari sumber mentah sebelum pengajuan — memverifikasi ulang tes PoC saja tidak cukup (ronde 5: tes B-1 diverifikasi ulang 5/5 PASS oleh agen induk, cek duplikatnya tidak — dan justru di situlah cacatnya).
8. **Alat pencarian yang tidak konsisten = alat rusak**: bila satu query mengembalikan 0 yang tidak masuk akal (istilah yang terbukti ada di tracker), hasil 0 itu BUKAN bukti ketiadaan. Ganti metode saat itu juga (enumerasi halaman penuh / daftar judul mentah), jangan kumpulkan lebih banyak angka 0 dari alat yang sama.

## Fase 1 — Sapuan subsistem (urutan tetap)

Sapulah dengan urutan: **inti uang** (ledger, saldo, supply/auditor, emisi) → **konsensus** (vote, quorum, finalisasi, rollback/cascade) → **governance/statechain** (multisig, keyset, aktivasi, oracle) → **jaringan** (gossip validator, sync, rate limit, ban) → **node/API** (handler, auth, provisioning, gateway) → **direktori/chat** (registrasi, routing, store) → **klien/CLI/dompét web** → **dokumen vs kode** → **dependensi**. Di SETIAP batas subsistem ajukan pertanyaan penyeberang: *subsistem A menegakkan disiplin X — apakah saudara B yang memercayai data yang sama juga menegakkannya?* (kesegaran, autentikasi, batas ukuran, validasi alamat). Mayoritas temuan XE lahir dari ketimpangan penyeberang ini, bukan dari satu fungsi yang bodoh.

Pertanyaan emas per fungsi penentu nilai/akses (warisan forensik):
1. Siapa yang bisa MENULIS inputnya — termasuk field yang tidak terlihat (header, field opsional, nilai dari subsistem lain)?
2. Siapa yang MEMBACA & MEMERCAYAINYA, dan keputusan apa yang bergantung padanya — di komponen mana pun, termasuk lapis propagasi dan builder di sisi klien?
3. Apa yang terjadi pada nilai tepi bertanda (negatif, MaxInt64, nol), pengulangan, dan versi lamanya?

## Fase 2 — Pembuktian (standar 4 lapis, tidak bisa ditawar)

1. Bukti source: fungsi:baris + cek yang hilang, dikutip persis.
2. Tes deterministik per paket yang MENJALANKAN perilakunya (Go test dengan kontrol positif/negatif: input sah lolos, tamper ditolak, varian sah dari klaim pemburu lain dibedakan). Klaim tanpa tes yang jalan = spekulasi = ditutup invalid oleh tim yang serius.
3. Bantah hipotesis sendiri: cari jalur yang menetralkan (konsumen yang menghitung ulang, store produksi yang berbeda, transport yang tidak diserve). Tuliskan hasilnya sebagai batas jujur.
4. **Dampak TERUKUR**: byte/entri, ms/PoW per unit serangan, jumlah node yang mati dalam rantai, angka emisi/saldo sebelum-sesudah. Laporan terukur menang atas laporan keras.

## Fase 3 — Penulisan & pengajuan

Struktur laporan yang terbukti dibayar (pola Khanhtnq/fahriiri206/harismanciripto111):
- Tabel ringkasan di atas (temuan/severity/komponen bila bundle).
- Per temuan: mekanisme → akar per fungsi:baris → bukti (tes + output) → dampak terukur → **batas jujur** (seksi "Not proven" / caveat biaya eksplisit; pisahkan klaim terbukti dari spekulatif) → remediasi.
- **Paragraf "Duplicate check:" WAJIB**: sebut laporan terdahulu terdekat satu per satu dan bedakan per mekanisme/fungsi/lapis. Ini satu-satunya pelindung untuk topik panas.
- Klaim severity = yang tertinggi yang bisa DIPERTAHANKAN dengan bukti, bukan yang tertinggi yang bisa dibayangkan.
- **Companion Fix PR** bila program menghargai kode: format (1) The rule (2) Every site across the tree (3) Sibling sweep + tes bernama skenario serangan. Tim XE memperbaiki lewat commit rilisnya sendiri (PR pemburu dibiarkan terbuka sebagai referensi; tepat satu PR pemburu pernah di-merge) — nilai PR adalah sinyal keseriusan, bukan jalur merge.
- Bundle vs satu-per-satu: bundle per subsistem menang di XE (satu tiket Critical berisi 4 temuan), tetapi satu bagian duplikat bisa menyeret sisanya; hunter volume (55 tiket, mayoritas Minor) juga mengumpulkan total setara satu Severe. Pilih sadar, jangan asal.

## Fase 4 — Pasca-pengajuan

- Pantau label/status, bukan janji: pipeline (tanpa label) → triaged → accepted → awarded; duplicate/invalid untuk sisanya.
- **Uji ulang setiap klaim "sudah diperbaiki"**: fix parsial atau salah-klaim adalah kelas temuan tersendiri yang diterima tim (kasus #228). Baca commit fix-nya, jalankan lagi PoC lamamu di HEAD baru.
- Temuan tetangga yang muncul dari pekerjaan orang lain (mereka menerbitkan, tim menambal sebagian) adalah permukaan segar — bukan alasan berhenti.
- Catat hasil akhir per laporan ke catatan audit + memori; koreksi penilaian lama secara eksplisit bila studi lanjutan membalikkannya (preseden: penilaian risiko duplikat XE dikoreksi total setelah enumerasi tracker penuh).

## Aturan keras

- Read-only terhadap sistem live; pembuktian lokal (unit test, fork, instans lokal) — bukti live hanya read-only reachability di testnet publik bila program mengizinkan (preseden #15: eksploitasi live DITAHAN, hanya reachability dikonfirmasi).
- Tidak ada pengajuan spekulatif: tanpa mekanisme + bukti yang bisa dijalankan, jangan ajukan.
- Nilai PII/kredensial pihak ketiga tidak pernah disalin ke laporan/catatan — catat keberadaan & bentuknya saja (warisan aturan DSW).
- Keputusan nominal & klaim mengikuti aturan user yang berlaku di chat forensik (laporan bounty dalam Bahasa Inggris; catatan internal boleh Bahasa Indonesia).

## Kriteria tuntas per target

Selesai bila: peta taken lengkap dan tercatat; semua subsistem Fase 1 tersapu atau dinyatakan belum dengan alasan; setiap kandidat lolos/gugur dengan bukti yang bisa dirujuk ulang; laporan terkirim memuat Duplicate check + batas jujur; hasil akhir (label/award/duplikat) dicatat dan pola baru disetor ke `POLA-NODE.md`.
