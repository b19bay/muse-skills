# INDEKS REFERENSI BELAJAR — Forensik Kontrak / Audit Keamanan EVM
Panen awal 2026-11-04 (perintah user: fokus belajar, referensi sebanyak-banyaknya termasuk situs hack-me/CTF). Indeks ini hidup — entri ditambah saat sumber baru terverifikasi. URL persis dari hasil pencarian/riset, tidak direkonstruksi.

## A. Korpus exploit yang bisa dieksekusi (belajar dari serangan nyata, dalam kode)
- **DeFiHackLabs** — https://github.com/SunWeb3Sec/DeFiHackLabs — insiden DeFi direproduksi sebagai PoC Foundry per insiden (`src/test/YYYY-MM/`, fork di blok−1; hitungan repo bergerak ±700–840 dan terus tumbuh — perlakukan sebagai rentang). Perpustakaan exploit ter-eksekusi terbaik; jangkar ideal untuk kartu kasus baru. KOREKSI atribusi: DeFiHackLabs & DeFiVulnLabs keduanya milik **SunWeb3Sec**, BUKAN SlowMist (kesalahan premis umum).
- **DeFiVulnLabs** — https://github.com/SunWeb3Sec/DeFiVulnLabs — 48 PoC kelas kerentanan dalam Foundry (termasuk read-only reentrancy, phantom permit, storage collision) — kelas-kelas yang sering hanya disebut sepintas di checklist.

## B. Situs latihan / hack-me / CTF (berpikir seperti penyerang, langsung praktik)
- **Ethernaut** (OpenZeppelin) — https://ethernaut.openzeppelin.com/ — 30+ level wargame Solidity di browser: reentrancy, delegatecall, tx.origin, DoS, overflow klasik.
- **Damn Vulnerable DeFi v4** — https://www.damnvulnerabledefi.xyz/ — 18 tantangan DeFi tingkat lanjut: flash loan, oracle, governance, lending, vault, likuidasi, merkle proof, penarikan bridge, meta-transaksi. Standar latihan auditor.
- **Capture the Ether** — https://capturetheether.com — teka-teki perilaku EVM & jebakan Solidity klasik (pemanasan).
- **Paradigm CTF** — https://ctf.paradigm.xyz/ — kompetisi tingkat riset, codebase besar, jalur exploit mirip audit sungguhan.
- **CodeHawks First Flights** (Cyfrin) — https://codehawks.cyfrin.io/first-flights — kontes audit pemula terstruktur.
- **Smart Contracts Hacking** — https://smartcontractshacking.com/tools/smart-contract-ctf — Ethernaut dibangun ulang sebagai tantangan Foundry.
- **blocksec-ctfs** (daftar kurasi wargame/CTF blockchain + writeup) — via agregator https://github.com/getblock-team/awesome-web3-security

## C. Kurikulum & basis pengetahuan terstruktur
- **Secureum** (bootcamp + RACE) dan **Cyfrin Updraft** — dua jalur kurikulum gratis yang paling dihormati (disebut berulang di semua roadmap).
- **cmichel — How to become a smart contract auditor** — https://cmichel.io/how-to-become-a-smart-contract-auditor/ — peta jalan + pendekatan fork modern untuk CTF.
- **SWC Registry** — klasifikasi kelemahan kontrak (kosakata kelas klasik).
- **OWASP Smart Contract Top 10 (edisi terbaru) + SCSVS + SCSTG + checklist** — standar verifikasi & panduan pengujian industri (tercatat di indeks Raiders0786 di bawah).
- **Consensys Smart Contract Best Practices** & **Trail of Bits Building Secure Contracts / blog riset** — checklist + pendalaman firma.

## D. Database temuan audit & laporan (belajar dari temuan orang lain)
- **Solodit** — https://solodit.cyfrin.io/ — mesin pencari temuan audit dari firma & kontes; cara pakai auditor: cari kelas bug, pelajari root cause + pola kode pencegahnya.
- **Code4rena Reports** — https://code4rena.com/reports — laporan kontes 100% publik (repo + temuan + penilaian).
- **Immunefi Reports + Past-Audit-Competitions** — https://reports.immunefi.com dan repo GitHub immunefi-team — temuan bounty & kompetisi resmi.
- **Cantina Portfolio** — https://cantina.xyz/portfolio — laporan PDF kompetisi & audit.
- **Rekt Leaderboard / Rekt News** — postmortem naratif exploit besar + akuntansi kerugian.
- **DeFiLlama Hacks** — basis data insiden (basis frekuensi bank kasus kami: 1.293 insiden).

## E. Agregator (pintu masuk ke ratusan referensi turunan)
- **getblock-team/awesome-web3-security** — https://github.com/getblock-team/awesome-web3-security/blob/HEAD/README.md
- **Raiders0786/web3-security-resources** — https://github.com/raiders0786/web3-security-resources/blob/HEAD/docs/resources/index.md — katalog berjenjang (Must Learn / Use in Real Audits / Advanced) + resources.yml terbaca mesin.
- **panditdhamdhere/master_smart_contracts** — https://github.com/panditdhamdhere/master_smart_contracts/blob/HEAD/README.md — kontrak produksi + dokumen/audit per protokol.
- **Anugrahsr/Awesome-web3-Security** — https://github.com/Anugrahsr/Awesome-web3-Security — materi pentester & bug hunter + mindmap kerentanan.

## F. Metode belajar yang dipanen dari roadmap (bukan situs, tapi teknik)
- **Shadow audit**: kerjakan ulang kontes/audit yang laporannya sudah terbit, lalu bandingkan temuanmu dengan laporan resmi — melatih kalibrasi severity & kelengkapan cakupan. (Sumber: roadmap peneliti keamanan Web3, beberapa versi.)
- **Reproduksi exploit historis di Foundry** (DeFiHackLabs) sebelum membaca postmortem-nya — pola dikenali dari kode serangan, bukan dari cerita.

## G. Taksonomi acuan (hasil riset 2026-11-04)
- **OWASP Smart Contract Top 10: 2026** — https://scs.owasp.org/sctop10/ (edisi terkini, terverifikasi dari halaman resmi; basis 122 insiden 2025 ≈$905,4 jt): SC01 Kontrol Akses, SC02 Logika Bisnis, SC03 Manipulasi Oracle Harga, SC04 Serangan Berfasilitasi Flash Loan, SC05 Kurang Validasi Input, SC06 Panggilan Eksternal Tak Dicek, SC07 Kesalahan Aritmetika (baru, terpisah), SC08 Reentrancy, SC09 Overflow/Underflow, SC10 Proxy & Upgradeability (baru). Sebutan kehormatan: permit front-running/nonce DoS, MEV lintas-rantai, kerentanan kriptografi/tanda tangan.
- **SWC Registry** — https://swcregistry.io — 37 kelas klasik SWC-100…136; TIDAK terpelihara sejak ±2020, tanpa kelas DeFi/ekonomi/L2 — kosakata dasar saja.
- **Immunefi Web3 Security Library** — https://github.com/immunefi-team/Web3-Security-Library + Bug Fix Reviews https://immunefi.com/blog/bug-fix-reviews/ (PoC: github.com/immunefi-team/bugfix-reviews-pocs) — bug produksi berbayar nyata per kelas; guru kalibrasi severity terbaik (Wormhole $10 jt, Aurora $6 jt, Polygon $2,2 jt).
- **Solodit** — https://solodit.cyfrin.io (docs: docs.solodit.cyfrin.io; API findings tersedia) — basis data temuan audit (klaim jumlah berbeda antar-sumber: 50 rb+ vs 80 rb+); saring per dampak/firma/tag/protokol sebelum mengaudit tipe protokol tertentu.
- **BlockThreat** — https://blockthreat.com — buletin mingguan intelijen ancaman sejak 2019; keunikannya: menghubungkan insiden baru ke kelas lama yang berulang (mis. Resupply 2025 = kelas Hundred Finance 2023, $51 jt+ untuk kelasnya).
- **SlowMist Hacked** — https://hacked.slowmist.io — arsip insiden terbesar (±2.100 peristiwa, angka self-reported bergerak).
- **Korpus kerentanan ekonomi** — https://github.com/tokendynamicsxyz/economic-vulnerabilities/blob/HEAD/list.md — tabel exploit ekonomi (depeg, salah kalibrasi LTV, utang macet) per protokol/kategori/kerugian.
- **Daftar temuan terkurasi berkategori** — https://github.com/0xscratch/smart-contract-vulnerabilities/blob/HEAD/README.md (temuan C4/Sherlock/Immunefi per kelas, contoh lending: rebasing di Abracadabra, penebusan menguras CDP sehat di Badger, akuntansi vault basi di BlueBerry, utang macet dari pemotongan di Isomorph).

## H. Platform latihan tambahan (dari tabel riset 22 platform)
- blocksec-ctfs (meta-daftar CTF) — https://github.com/blockthreat/blocksec-ctfs
- Curta (teka-teki on-chain, Flag NFT) — https://www.curta.wtf/
- Node Guardians — https://nodeguardians.io/quests?f=3%3D2&
- QuillCTF — https://academy.quillaudits.com/challenges/quillctf-challenges-1/stakeking
- EVM Puzzles — https://github.com/fvictorio/evm-puzzles
- Solidity Riddles (RareSkills) — https://github.com/RareSkills/solidity-riddles
- Mr Steal Yo Crypto (tantangan berbasis exploit nyata) — https://mrstealyocrypto.xyz/
- Underhanded Solidity Contest (latihan MENULIS bug yang tampak lugu — melatih mata peninjau) — https://underhanded.soliditylang.org/
- Secureum A-MAZE-X (= tantangan DeFi Security Summit, 8 tantangan DeFi) — https://github.com/secureum/AMAZEX-DSS-PARIS ; indeks https://secureum.gitbook.io/secureum-book/ctfs/ctfs
- BlazCTF (kompetisi generasi Paradigm) — https://ctf.blaz.ai/
- HackTheBox kategori Blockchain (berlangganan) — https://www.hackthebox.com/blog/new-blockchain-challenge-category

## I. Agregator tambahan
- gmh5225/awesome-web3-security — https://github.com/gmh5225/awesome-web3-security/blob/HEAD/README.md
- crytic/awesome-ethereum-security (Trail of Bits) — https://github.com/crytic/awesome-ethereum-security
- kcchu/awesome-smart-contract-bugs (kanon bug historis: DAO, Parity) — https://github.com/kcchu/awesome-smart-contract-bugs
- awesome-audits-checklists — https://github.com/cryptonomad21/awesome-audits-checklists/blob/HEAD/README.md
