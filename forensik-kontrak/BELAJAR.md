# CATATAN BELAJAR — perluasan dasar pengetahuan forensik (dimulai 2026-11-04)
Mandat user: pelajari semua referensi sebagai dasar pengetahuan; catat pola DAN cara; gabungkan menjadi pola pikir untuk berpikir jauh dalam menemukan kerentanan. Berkas ini = jurnal studi; hasil matangnya pindah ke POLA.md (kartu), POLA-KOMPOSIT.md, dan POLA-PIKIR.md (metode berpikir).

## Studi 1 — DeFiVulnLabs (SunWeb3Sec), 56 berkas kelas, ter-klon di ~/workspace/study/vulnlabs
Diff awal terhadap bank 21 kartu — kelas yang TIDAK punya kartu sendiri / kurang bobot di bank saat ini:
- **Read-only reentrancy** — reentrancy lewat fungsi view yang dibaca kontrak lain (oracle LP). Keluarga reentrancy kami belum memisahkannya sebagai kartu.
- **Phantom permit** — permit yang "berhasil" pada token tanpa permit (fallback sukses semu) → persetujuan hantu. Belum ada kartu.
- **Transient storage misuse** (EIP-1153) — kunci reentrancy/kekeliruan state di tstore yang gugur di akhir tx. Kelas frontier, belum ada.
- **Bypass isContract (extcodesize == 0 saat konstruksi)** — gerbang "hanya EOA" yang lolos dari konstruktor. Belum ada kartu.
- **Hash collision encoding** (abi.encodePacked string dinamis bertetangga) — tabrakan digest untuk tanda tangan/komitmen. Belum ada kartu.
- **Unprotected callback** — hook ERC1363/677/721/1155/777 sebagai permukaan reentrancy non-standar. Perlu kartu sendiri (keluarga callback kami masih umum).
- **Slippage/deadline hilang** pada swap internal protokol — nilai bocor ke MEV tanpa "bug" klasik. Belum ada kartu.
- **Self-transfer accounting** — transfer dari/ke alamat sama yang menggandakan saldo di akuntansi cacat (kelas nyata di beberapa token/protokol). Belum ada kartu.
- **Return-false / unchecked return** — token yang mengembalikan false, bukan revert; dan panggilan bernilai tanpa cek hasil. Klasik tapi belum jadi kartu eksplisit.
- **Storage collision proxy** & **uninitialized storage pointer / data-location** — keluarga tata-letak penyimpanan; bank kami punya bootstrap (P-12) tapi belum kartu tata-letak.
- **Deletion semantics** (array/struct deletion menyisakan celah), **dirty bytes**, **unsafe downcast**, **ecrecover malleability/alamat nol**, **selfdestruct pasca-EIP-6780**, **privatedata** (data "privat" terbaca on-chain), **randomness** (blockhash/timestamp sebagai sumber acak), **gas-price & empty-loop DoS** — campuran klasik-modern untuk kartu-kartu kecil.
- Berkas bernama **Invariant.sol** — pengingat metode: lab ini pun mengajarkan berpikir invariant, bukan hanya daftar bug.

## Studi 2 — DeFiHackLabs README (174KB, terunduh di ~/workspace/study/)
Indeks insiden kronologis ±691 reproduksi + folder academy. Nilai utamanya: setiap insiden punya PoC ter-eksekusi — bahan baku kartu kasus berbasis bukti, menggantikan ringkasan sekunder bila sebuah keluarga pola perlu jangkar yang bisa dijalankan.

## Menunggu penggabungan
- Hasil riset mendalam (kurikulum firma, taksonomi OWASP terbaru, kelas frontier 2023–2026, frekuensi temuan kontes) — digabung ke jurnal ini saat tiba.
- Setelah gabung: (1) kartu baru P-22+ ke POLA.md, (2) POLA-PIKIR.md — sintesis cara berpikir jauh: inversi asumsi, penelusuran angka lintas representasi, komposisi antar-lapis (mekanika protokol × semantik EVM × insentif ekonomi × waktu/komposabilitas), (3) pembaruan SKILL.md bila metode berubah.

## Studi 3 — Riset mendalam + sintesis (2026-11-04, SELESAI)
- Laporan riset penuh: ~/workspace/research_notes/smart-contract-forensics-learning-refere-20261104-0218/report.md (kurikulum, korpus, taksonomi OWASP 2026 terverifikasi dari halaman resmi, 13 kelas frontier berjangkar insiden, data frekuensi kontes, 22 platform latihan, 10 agregator).
- KOREKSI yang dibawa riset: (1) DeFiVulnLabs & DeFiHackLabs = SunWeb3Sec, bukan SlowMist; (2) hitungan PoC DeFiHackLabs bergerak (±700–840), jangan kutip satu angka; (3) hitungan temuan Solodit berbeda antar-sumber (50 rb+ vs 80 rb+) — perlakukan sebagai rentang berprovenien.
- Hasil matang: 12 kartu baru P-22…P-33 di POLA.md; komposit baru K-07 Spiral Utang Macet di POLA-KOMPOSIT.md (jangkar Venus THE/wUSDM, Aave CRV, Mango — termasuk pelajaran bahwa vektor K-07 pernah ditandai temuan kontes 2023 lalu dinilai tim "tanpa efek negatif"); dokumen POLA-PIKIR.md (inversi asumsi, klasifikasi efek, tiga peta: angka/waktu/peran, hukum H6–H8, prior frekuensi lending, rezim latihan shadow audit & reproduksi PoC).
- Pelajaran kalibrasi terpenting dari data frekuensi: yang memenuhi temuan nyata bukan kelas sinematik — kebasian, desync akuntansi, arah pembulatan, kesalahan fee, asumsi aktor tepercaya. Reentrancy jarang tetapi hampir selalu nyata bila ada (penerimaan 78%).
STATUS: fase belajar ini tuntas tersintesis. Perburuan berikutnya memakai POLA-PIKIR.md di Fase 0 dan memasukkan cek frontier (P-22…P-33) ke jaring Fase 3.
