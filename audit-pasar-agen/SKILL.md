# Skill: Audit Pasar Agen (Agent-Marketplace Audit)

Meng-audit marketplace kode agen — path, skill, strategi, MCP server,
atau artefak lain yang dibuat satu user dan dijalankan user lain —
untuk kelemahan rantai pasok dan batas kepercayaan.

Dibangun dari audit Wayfinder 13–14 Nov 2026
(`~/workspace/wayfinder-check/PATHS-DEEP-AUDIT.md` + `ARSIP.md`).

## Kapan dipakai

- Targetnya adalah ekosistem tempat kode/instruksi buatan user
  didistribusikan ke user lain (registry, marketplace, hub skill).
- Pertanyaannya bukan "apakah kodenya benar?" melainkan "apa yang
  terjadi bila author-nya jahat?" dan "apa yang melindungi korban?".
- Dipakai BERSAMA skill forensik-kontrak / pentest-web / serangan-agen,
  bukan menggantikan mereka: skill ini mengaudit PASAR-nya, skill lain
  mengaudit KODE atau JARINGAN-nya.

## Prinsip inti (pelajaran dari audit Wayfinder)

**Audit sistem untuk APA sistem itu, bukan hanya apa yang dilakukan
kodenya.** Marketplace kode agen BUKAN library — batas kepercayaan
utamanya adalah author→korban, bukan klien→server. Audit yang hanya
memeriksa batas jaringan, config, dan kriptografi akan melewatkan
seluruh permukaan ini (kesalahan yang terjadi pada pass 1–2 audit
Wayfinder: modul paths/ 13.549 baris tidak diperiksa sebagai batas
kepercayaan).

Pertanyaan pemandu, dalam urutan:
1. Apa yang dijual/didistribusikan, dan siapa yang membuatnya?
2. Apa yang dilihat/diperiksa sebelum artefak itu sampai ke korban?
3. Apa yang diketahui korban sebelum menjalankan, dan apa yang
   dimintai persetujuannya?
4. Dengan izin apa artefak itu berjalan, dan apa yang bisa dilakukannya?
5. Apa yang terjadi bila author berbalik jahat, kuncinya dicuri,
   atau artefaknya diambil alih?

## Peta alur kepercayaan (diperiksa berurutan)

```
AUTHOR → PUBLISH → REVIEW → REGISTRY → DISCOVERY → INSTALL
→ ACTIVATION → EXECUTION → DEPENDENCIES
```

Setiap panah adalah satu kontrol yang harus diuji. Kartu-kartu
pemeriksaannya ada di `POLA-PASAR.md` (MP-01..MP-13).

## Metode (7 langkah)

### 1. Petakan sistem
- Enumerasi modul registry/publish/install/review/eksekusi di repo.
- Catat: jenis artefak, siapa bisa publish, apa yang disimpan
  registry per artefak (field metadata), bagaimana artefak
  ditemukan/di-install/dijalankan.
- Jangan mulai dari kode — mulai dari DOKUMEN produk (whitepaper,
  docs, halaman registry) untuk memahami APA sistem itu.

### 2. Periksa REVIEW: struktural vs perilaku
- Baca aturan review yang terlihat di repo (doctor/linter/validator).
  Bedakan cek STRUKTUR (manifest valid, method ada, file ada) dari
  cek PERILAKU (apa yang dilakukan kode/instruksi).
- Cek data live: apa bukti review yang terlihat publik per artefak?
  (status, timestamp, isi laporan, hasil rebuild). Status "passed"
  tanpa jejak apa pun = klaim tanpa bukti.
- Catat apa yang TIDAK terlihat (review server-side) sebagai
  "unknown", bukan sebagai "aman".

### 3. Periksa INSTALL: model izin dan persetujuan
- Apakah manifest mendeklarasikan izin/kapabilitas? Apakah install
  menampilkan ringkasan izin? Apakah ada gerbang trust-tier?
- Apakah "signed intent" / persetujuan yang ada adalah persetujuan
  ATAS KODE, atau hanya pengikatan ke versi+hash?
- Apakah install default ke versi terbaru (floating) atau ter-pin?

### 4. Periksa EKSEKUSI: sandboxing dan kapabilitas runtime
- Bagaimana artefak dimuat dan dijalankan? (in-process? subprocess?
  sandbox? pembatasan impor?)
- Apa yang diberikan runtime ke artefak? (callback signing, akses
  file, jaringan, kredensial?) Apakah ada gerbang per-aksi?
- Periksa callback signing: apa yang ditandatangani, siapa yang
  menyetujui, apakah ada cek jumlah/tujuan/policy?

### 5. Periksa DEPENDENSI dan artefak turunan
- Apakah dependensi di-pin versi atau mengambang (slug saja)?
- Apakah ada dependensi yang disuntikkan otomatis (archetype,
  template, default)? Dari mana mereka di-resolve (bawaan dulu
  atau registry dulu)?
- Apakah ada artefak tanpa owner (unclaimed)? Bagaimana alur klaimnya?
  Apakah alur itu terlihat dari repo?

### 6. Periksa ekonomi kepercayaan
- Apakah ada bond/stake? Berapa nilainya (nominal + USD + IDR)?
  Opt-in atau wajib? Default-nya apa?
- Apakah ada slashing? Pernahkah terjadi (bila bisa diverifikasi)?
- Apakah ada reputasi (install, bintang, follower)? Apakah reputasi
  ditampilkan saat install? Bisakah digaming?

### 7. Verifikasi live + susun rantai serangan
- Query registry live (read-only, key sendiri): hitung artefak per
  trust-tier, kind, risk-tier, status klaim. Identifikasi artefak
  paling berisiko (eksekusi + tanpa bond + tanpa owner).
- Susun rantai serangan ujung-ke-ujung (nol celah → publish →
  review → install → eksekusi → dampak). Setiap rantai harus
  menyebut kontrol yang dilewati dan bukti source-nya.
- Bedakan dengan tegas: TERBUKTI (source + live) vs HIPOTESIS
  (butuh tes yang belum dilakukan) vs UNKNOWN (sisi server, tak
  terlihat). Jangan mengubah hipotesis menjadi temuan.

## Gerbang otorisasi (mengikat — turunan pentest-web 3 tingkat)

- **Tier 1 (selalu boleh):** baca source publik, query registry
  read-only dengan key sendiri, analisis statis.
- **Tier 2 (akun sendiri):** tes dengan DUA akun milik user (mis.
  publish artefak tes dengan akun A, coba update dengan akun B).
  Publish artefak tes ke registry publik butuh persetujuan eksplisit
  user (artefak tes harus ditandai jelas sebagai tes dan tidak
  berbahaya).
- **Tier 3 (DILARANG tanpa otorisasi tertulis dari operator):**
  publish/klaim/ubah artefak milik orang lain; pengujian aktif
  terhadap backend registry; eksploitasi celah yang ditemukan untuk
  mengubah artefak pihak ketiga; download bundle yang memerlukan
  pembuatan install-intent TANPA persetujuan user (karena membuat
  catatan di server).
- Temuan dilaporkan secara privat ke operator (saluran yang dipilih
  user), bukan dipublikasikan.

## Standar bukti

- Setiap temuan: file:line di source ATAU respons API live yang
  dikutip. "Review lemah" bukan temuan — "doctor.py tidak mengandung
  satu pun cek keamanan (grep: ...)" adalah temuan.
- Angka dari data live: sebutkan tanggal, total populasi, dan cara
  hitung. Jangan mengutip angka dari ingatan.
- Jangan pernah menyatakan artefak tertentu JAHAT tanpa membaca
  kodenya. "Mencurigakan secara struktur" (tanpa bond + tier
  eksekusi + tanpa owner) bukan bukti kejahatan.

## Contoh worked (Wayfinder, Nov 2026)

Lihat `~/workspace/wayfinder-check/PATHS-DEEP-AUDIT.md` (11 temuan:
review struktural saja, skill tak direview, tanpa model izin,
eksekusi tanpa sandbox + callback signing tanpa gerbang, dependensi
mengambang, 19 path unclaimed, bond opt-in ~$175) dan
`~/workspace/wayfinder-check/ARSIP.md` (arsip lengkap + pelajaran).
