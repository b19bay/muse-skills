# Matriks Routing Skill

Setiap jenis tugas → bundle skill yang mengaturnya, urut peran. Semua nama
skill di file ini diverifikasi ada pada 2026-11-14 (folder custom di
`~/workspace/custom-skills/`, folder sistem di `/opt/muse/skills/`).
Jangan menambahkan nama skill tanpa memverifikasi foldernya dulu.

Berlaku di SEMUA baris (tidak ditulis ulang per baris):
- `perkataan-mutlak` — doktrin tertinggi; akurasi berbasis bukti.
- `skill-foundation` — doktrin ini; mengatur routing, bundle, ledger.
- `humanize-skills` — overlay gaya tulis (standing order user 2026-11-21, "terapkan selalu"): berlaku di semua output tertulis (chat panjang, laporan, draf, lamaran, posting); baca core-rules + structural-pass + file bahasa yang dipakai; no-edit gate + fact-lock; tidak mengalahkan format wajib, sitasi, atau akurasi faktual.
- Bila ada bank pola untuk jenis tugas itu (mis. `~/workspace/makefun/pattern-bank.md`),
  baca sebelum mulai dan perbarui setelah selesai.

Peran: **O** = orkestrasi (mengatur fase + cakupan), **L** = lensa (cara
melihat masalah), **V** = validasi (memeriksa hasil), **P** = pengganda
(melipatgandakan nilai satu hasil).

## Audit & keamanan

| Jenis tugas | Bundle (urut peran) | Kapan | Pendamping opsional |
|---|---|---|---|
| Audit kontrak EVM | `security-audit` (O) + `forensik-kontrak` (L) + `bsc-contract-audit` atau `multichain-contract-audit` (V, gerbang + rubrik) + `token-integration-analyzer` (L, pola token aneh) + `property-based-testing` (V, invarian jadi test) + `variant-analysis` (P) | Audit kontrak/token EVM apa pun, termasuk bounty Immunefi | `onchain-price-accuracy` (bila harga on-chain menentukan), `supply-chain-risk-auditor` (dependensi repo) |
| Audit kontrak Solana | `multichain-contract-audit` (O+V, annex Solana) + `security-audit` (O) + `forensik-kontrak` (L) + `property-based-testing` (V) + `variant-analysis` (P) | Audit program Solana/Anchor atau token SPL | `supply-chain-risk-auditor` (dependensi Rust) |
| Audit keamanan codebase umum | `security-audit` (O) + `forensik-node` (L, duplikat & ketimpangan antar-subsistem) + `supply-chain-risk-auditor` (L) + `variant-analysis` (P) + `property-based-testing` (V) | Audit repo non-kontrak: web service, CLI, library, daemon | `hunt-llm-ai` (bila target ber-AI), `skill-security-audit` (bila targetnya skill) |
| Audit dependensi / supply-chain | `supply-chain-risk-auditor` (O+V) + `security-audit` (O, konteks) | Audit lockfile & dependensi npm/PyPI/Go | — |
| Variant hunting dari temuan | `variant-analysis` (O+P) + `forensik-kontrak` atau `forensik-node` (L) + `property-based-testing` (V, uji varian) | Setelah satu bug terkonfirmasi: cari di mana lagi bug yang sama bersembunyi | `security-audit` (coverage) |
| Property-based testing / fuzzing | `property-based-testing` (O+V) + `forensik-kontrak` (L, invarian) | Meng-encode invarian jadi property test / fuzzer (Echidna/Medusa, Hypothesis, proptest) | `variant-analysis` (generalisasi counterexample) |
| Hunting bug LLM / agent | `hunt-llm-ai` (O+L) + `serangan-agen` (L, pola serangan pipeline agen) + `security-audit` (O) + `bug-hunter` (V, metodologi + laporan) | Memburu bug di aplikasi LLM target; SELALU di bawah gerbang 3-tier pentest-web | `pentest-web` (gerbang), `recon-a-domain-passively` (permukaan pasif) |
| Pentest web (3-tier) | `pentest-web` (O, gerbang + pola) + `bug-hunter` (O, recon → laporan) + `recon-a-domain-passively` (L, Tier 1 pasif) + `obscura-forensik` (L, mata browser) | Pengujian keamanan aplikasi web; Tier 2 aktif hanya dengan izin tertulis | `hunt-llm-ai` (bila target ber-AI) |
| Recon pasif domain | `recon-a-domain-passively` (O+L) + `pentest-web` (Tier 1) + `bug-hunter` (konteks recon) | Inventaris aset domain/IP tanpa satu paket pun ke target; dipanggil eksplisit | — |
| Recon bug bounty | `bug-hunter` (O) + `recon-a-domain-passively` (L, pasif dulu) + `pentest-web` (gerbang) | Recon program bounty: subdomain, permukaan, teknologi | `obscura-forensik` (inspeksi halaman) |
| Audit pasar agen | `audit-pasar-agen` (O+L) + `serangan-agen` (L) + `security-audit` (O) | Audit marketplace/bundle agen AI (trust boundary, signing, skill tak ter-review) | `skill-security-audit` (skill di dalam bundle) |
| Impor skill baru (audit pra-instal) | `skill-security-audit` (O+V) | SEBELUM memasang skill dari luar (Hermes/ClawHub/GitHub): audit injeksi, kode berbahaya, exfil, dependensi | `skill-foundation` (pencatatan pasca-instal) |
| Forensik browser / halaman | `obscura-forensik` (O+L) | Inspeksi halaman web lewat headless browser untuk kebutuhan forensik | `pentest-web`, `forensik-kontrak` |
| Audit kurva launch token | `launch-curve-audit` (O+L) + `onchain-price-accuracy` (V) + `forensik-kontrak` (L) | Audit mekanisme launch curve / bonding curve token | `token-integration-analyzer` |

## Kripto, NFT, free-mint

| Jenis tugas | Bundle (urut peran) | Kapan | Pendamping opsional |
|---|---|---|---|
| Riset proyek NFT / free-mint | `riset-x` (O, filter) + `forensik-kontrak` (V, gerbang pabrik) + `nft-detail` (V, detail lengkap) + `onchain-price-accuracy` (V, harga) + `wayfinder-assist` (data cepat) | Menilai proyek agent/NFT dari X/medsos sebelum mint | `serok` (bila mencari mispricing) |
| Berburu NFT di bawah floor | `serok` (O+V) + `nft-detail` (V) + `onchain-price-accuracy` (V) | Mencari listing terverifikasi jauh di bawah floor koleksi | `forensik-kontrak` (identitas koleksi) |
| Cek harga on-chain | `onchain-price-accuracy` (O+V) | Harga/kuotasi yang harus akurat on-chain (bukan dari agregator) | `nft-detail` (bila NFT) |
| Data cepat Wayfinder | `wayfinder-assist` (O) | Tarik data Alpha Lab / wallet read-only lewat Wayfinder | — |

## Bounty, otomasi, eksekusi terjadwal

| Jenis tugas | Bundle (urut peran) | Kapan | Pendamping opsional |
|---|---|---|---|
| Bounty make.fun | `makefun-bounty` (O+V) + bank pola `~/workspace/makefun/pattern-bank.md` (L) + per-type bundle di bawah | Build + submit entri bounty make.fun; wajib baca pattern-bank sebelum build, perbarui setelah selesai | Per tipe: Agent server/router `+ property-based-testing (V) + forensik-node (L) + variant-analysis (P) + security-audit (V) + perf-profiling (V)`; Chess `+ property-based-testing (V, perft) + bounded_solver_retry (V)`; Forecasting `+ forecasting (O) + property-based-testing (V)`; Data dashboard `+ serok (L) + token-integration-analyzer (L)`; Creative text/image `+ video-gambar (O) + image-search (L) + judging-calibration (O)`; FPS/game `+ property-based-testing (V)`; Referral `+ social-content-performance (L) + square_post_preflight (V)`; semua build (studi P-13) `+ wide-research (O)` |
| Penjaga kursi / attempt langka | `contested_seat_watcher` (O) + `bounded_solver_retry` (V) | Watcher tanpa pengawasan untuk slot/attempt langka (launch shot, mint detik pembukaan) | — |
| Solver berbatas waktu | `bounded_solver_retry` (O+V) | Percobaan solver yang dibatasi kesesuaian jendela live + cap retry identik | — |
| Verifikasi pengiriman alert terjadwal | `scheduled_delivery_proof` (O+V) | Memastikan alert watcher sampai ke user sebagai pesan chat yang terlihat sebelum ditandai terkirim | — |

## Posting, riset, dokumen, pekerjaan umum

| Jenis tugas | Bundle (urut peran) | Kapan | Pendamping opsional |
|---|---|---|---|
| Posting Binance Square | `binance-square-post` (O, publish: teks via client.py, media via post-media.py; baca LOCAL-AMENDMENT.md untuk auth vault 2 akun; rutinitas 2 jam sekali, 12/hari/akun, media buatan sendiri: gambar KOIN, video ffmpeg TREN) + `humanize-skills` (O, overlay gaya teks postingan, mode social + en) + `square_post_preflight` (V, cek draf) + `multi_account_post_dedup` (V, dedupe lintas akun) + `scheduled_delivery_proof` (V, bukti terkirim) | Sebelum dan sesudah posting Square di akun mana pun | `social-publishing` (sistem, bila menjadwalkan/menerbitkan) |
| Pencarian + lamaran kerja remote | `wide-research` (O, riset luas — sistem) + `documents` (V, CV/dokumen — sistem) + `email-management` (sistem, bila via email) + `scheduling` (sistem, bila ada interview) | Cari lowongan, verifikasi masih buka, kirim lamaran | `knowledge-organization` (sistem, merapikan catatan lamaran) |
| Riset web luas | `wide-research` (O — sistem) | Riset paralel atas banyak input independen dengan skema output bersama | `documents` (sistem, bila output dokumen) |
| Dokumen / laporan | `documents` (O+V — sistem) | Baca, tulis, revisi dokumen/PDF/spreadsheet/presentasi | `knowledge-organization` (sistem) |
| Penulisan & penyuntingan teks | `humanize-skills` (O+V, surface + structural pass; mode + bahasa dari request) | Menulis draf baru, mengedit/meng-humanize teks, surat lamaran, laporan, posting | `documents` (sistem, bila output dokumen) |
| Penjadwalan | `scheduling` (O — sistem) | Cari waktu, buat undangan, kelola janji temu | `goals` (sistem, bila terkait goal) |
| Produksi video & gambar | `video-gambar` (O+V) | Membuat video dan gambar: iklan 15 detik, explainer, animasi kode, motion graphics | `image-search` (sistem, referensi visual) |

## Skill yang belum punya "rumah" di matriks

NOL untuk skill custom — ke-32 skill custom tercakup di atas (dua doktrin
`perkataan-mutlak` dan `skill-foundation` berlaku di semua baris, bukan
di satu baris). Skill sistem yang belum tercakup (52 dari 57) tetap
tersedia lewat `muse.skill_search` dan routing bawaan platform untuk
domainnya masing-masing (perjalanan, belanja, kesehatan, musik, dsb.);
bila salah satunya mulai dipakai berulang untuk pekerjaan user, tambahkan
baris matriks untuknya dan catat di ledger.

## Cara memperbarui matriks ini

- Tambah baris bila jenis tugas baru muncul berulang (≥2 kali) dan punya
  bundle yang jelas.
- Perbaiki bundle bila ledger menunjukkan routing yang salah atau skill
  yang baru ketahuan di tengah jalan.
- Jangan pernah menambahkan nama skill tanpa memverifikasi foldernya
  (`ls ~/workspace/custom-skills/<nama>/` atau `ls /opt/muse/skills/<nama>/`).
- Setiap perubahan matriks dicatat sebagai entri ledger dengan
  `skills: ["skill-foundation"]`.
