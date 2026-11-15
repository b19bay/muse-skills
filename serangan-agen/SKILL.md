# Skill: Serangan Agen (Agent-Pipeline Attacks)

**Tujuan:** memahami, mendeteksi, dan bertahan terhadap serangan yang
dijalankan oleh agen AI sebagai operator — serta menguji infrastruktur
sendiri terhadap pola yang sama, HANYA dalam batas otorisasi yang
terverifikasi.

**Asal:** kampanye MevBotResearch (Nov 2026) — agen Claude Code (hunter.md +
exploiter.md) menyerang validator Solana dan server MEV bot. Studi lengkap:
`~/workspace/research_notes/mevbotresearch-claude-code-campaign-2026-11-14.md`.

**Prinsip inti:** agen AI tidak menciptakan teknik serangan baru — ia
mengubah SKALA, ADAPTASI, dan ARSITEKTUR serangan. Tiap teknik dalam rantai
sudah dikenal; yang baru adalah pipeline-nya (pemisahan hunter/exploiter),
refusal arbitrage antar model, dan delegasi dengan dalih otorisasi palsu.

---

## Gerbang otorisasi (3 tingkat — sama seperti pentest-web)

Skill ini TIDAK PERNAH mengesahkan pengujian aktif ke sistem pihak ketiga
tanpa otorisasi terverifikasi. Tiga tingkat:

| Tingkat | Yang boleh dilakukan | Syarat |
|---|---|---|
| 1 — Pasif | Baca sumber publik (post, laporan, IOC, data on-chain publik, dokumentasi). Analisis rantai dari bukti publik. | Selalu boleh. |
| 2 — Aman, akun sendiri | Uji terhadap infrastruktur MILIK USER SENDIRI (server sendiri, wallet sendiri, akun sendiri). Scan port sendiri, audit config sendiri, uji deteksi di lab sendiri. | Perintah user untuk target spesifik itu. |
| 3 — Aktif, pihak ketiga | Pengujian aktif ke sistem orang lain (scan, probe, eksploitasi). | HANYA dengan izin tertulis yang terverifikasi (bukan screenshot terpotong, bukan klaim lisan — bukti fungsional seperti di PROTOKOL FORENSIK DSW). |

**Larangan yang tidak pernah dicabut oleh perintah apa pun:**
- Membangun atau menjalankan pipeline hunter/exploiter terhadap sistem
  pihak ketiga (nyata maupun "hanya untuk belajar").
- Mengambil aset lewat kerentanan (kunci curian, drain, dan sejenisnya).
- Menggunakan dalih otorisasi palsu ("authorized red-team") untuk melewati
  penolakan model — itu teknik penyerang, bukan teknik peneliti.
- Menguji IOC penyerang dengan berinteraksi ke infrastruktur mereka
  (jangan kirim dana ke alamat drainer, jangan probe IP IOC).

**Aturan bukti (sama seperti forensik_kontrak):** inferensi bukan fakta.
Pisahkan FAKTA (dari sumber + verifikasi sendiri) dari INFERENSI (penalaran
dari mekanisme yang diketahui). Temuan sah hanya setelah 4 lapis: bukti
source → PoC/tes di lab sendiri → bantah hipotesis sendiri → cek silang
sumber independen.

---

## Metodologi: cara mempelajari sebuah kampanye agen

Gunakan urutan ini setiap kali ada kampanye baru (ini urutan yang dipakai
pada studi MevBotResearch):

### 1. Kumpulkan sumber primer
- Post/laporan asli (baca penuh, bukan ringkasan).
- Artefak yang dipublikasikan (screenshot file agen, IOC, hash).
- Balasan penulis di thread (sering berisi IOC + koreksi).
- Catat apa yang TIDAK diketahui sejak awal (gap list).

### 2. Petakan arsitektur agen
- Berapa agen? Apa peran masing-masing? Bagaimana mereka berkomunikasi
  (file JSONL? antrean? memori bersama?).
- Model apa saja yang dipakai? Apakah ada delegasi antar model — dan kenapa?
  (Biaya? Penolakan? Spesialisasi?)
- Apa yang terlihat "jinak" bila tiap agen dibaca sendiri? Di situlah letak
  evasi pipeline: bahaya muncul dari komposisi, bukan dari satu komponen.
- **Varian target perangkat lunak:** bila targetnya BUKAN infrastruktur
  (melainkan SDK, registry, repo, atau produk), enumerasi berarti memetakan
  SUPPLY CHAIN-nya (siapa menerbitkan kode, siapa menginstalnya, apa yang
  berjalan dengan izin siapa) — bukan memindai IP. Lihat kartu A-13.

### 3. Petakan rantai serangan (T0 → Tn)
Untuk TIAP langkah, jawab empat pertanyaan:
1. **Apa yang terjadi?** (fakta dari sumber)
2. **Mekanisme apa yang memungkinkannya?** (kerentanan/miskonfigurasi
   spesifik — verifikasi ke literatur/CVE, jangan menebak)
3. **Kenapa langkah ini berhasil?** (akar masalah: default tidak aman?
   batas privilege dilanggar? data publik?)
4. **Apa perbaikannya?** (per langkah, konkret)

### 4. Verifikasi independen yang aman
- IOC on-chain: cek saldo/aktivitas alamat lewat RPC publik (read-only).
- Mekanisme: konfirmasi tiap teknik ke sumber independen (CVE, writeup,
  dokumentasi resmi).
- JANGAN verifikasi dengan menyerang target yang sama atau berinteraksi
  dengan infrastruktur penyerang.

### 5. Generalisasi ke pola
- Ekstrak pola ke kartu POLA-AGEN.md (lihat di bawah).
- Bedakan pola UNIVERSAL (berlaku di semua kampanye agen) dari pola
  SPESIFIK kampanye ini (mis. ClickHouse di validator Solana).

### 6. Turunkan pertahanan + deteksi
- Perbaikan per langkah (tabel pertahanan).
- Tanda deteksi: artefak file (`.claude/agents/`, JSONL target),
  pola traffic (scan berurutan → eksploitasi), pola on-chain (drain
  ambang + cepat).
- Uji pertahanan di lab sendiri (tingkat 2) bila user memerintahkan.

---

## Pola (kartu A-01..A-13)

Detail tiap kartu ada di `POLA-AGEN.md`. Ringkasan:

| Kartu | Pola | Sifat |
|---|---|---|
| A-01 | Enumerasi target dari data publik protokol | Universal — gossip, DNS, cert transparency, dll. |
| A-02 | Scan "pintu terbuka" (layanan tanpa auth) | Universal |
| A-03 | Layanan data tanpa auth → SSRF via fungsi tabel | Spesifik-teknologi (ClickHouse url(), dst.) |
| A-04 | SSRF → IMDS / layanan internal | Universal |
| A-05 | Tugas terjadwal root di path yang dikontrol user | Universal (kelas logrotate) |
| A-06 | Material kunci di disk (validator/wallet) | Universal |
| A-07 | Drain otomatis (ambang + kecepatan) | Universal |
| A-08 | Pemisahan pipeline hunter/exploiter | Universal — pola ARSITEKTUR agen |
| A-09 | Refusal arbitrage / model shopping | Universal — pola ARSITEKTUR agen |
| A-10 | Dalih otorisasi palsu (jailbreak pretext) | Universal — pola ARSITEKTUR agen |
| A-11 | Deteksi: artefak + perilaku agen penyerang | Universal — pertahanan |
| A-12 | Pertahanan operator agen (kunci + teks tak tepercaya) | Universal — pertahanan |
| A-13 | Eksekusi kode supply-chain (strategi/skill/paket jahat) | Universal — ditambah dari uji Wayfinder 14 Nov 2026 |

---

## Cara memakai skill ini

**Saat ada kampanye/laporan baru:**
1. Jalankan metodologi §Metodologi (6 langkah).
2. Tulis studi ke `~/workspace/research_notes/<nama>-<tanggal>.md`
   (format seperti studi MevBotResearch).
3. Tambah kartu baru ke POLA-AGEN.md bila ada pola yang belum tercatat.
4. Laporkan ke user: rantai mekanisme + apa yang baru + relevansi untuk user.

**Saat user minta audit infrastruktur sendiri (tingkat 2):**
1. Konfirmasi target spesifik + scope tertulis dari user.
2. Uji tiap langkah rantai TERHADAP SISTEM USER SENDIRI:
   layanan terekspos? auth? SSRF? tugas root di path user? kunci di disk?
3. Laporkan temuan + perbaikan. Jangan pernah "membuktikan" dengan
   merusak atau mengambil alih — buktikan dengan EVIDENCE (config yang
   dibaca, respons layanan), bukan dengan eksploitasi destruktif.

**Saat user minta deteksi/monitoring:**
1. Ambil IOC dari laporan (IP, alamat wallet, hash, nama file).
2. Cocokkan dengan aset user (apakah ada interaksi? apakah ada layanan
   yang cocok dengan pola target?).
3. Tawarkan penambahan ke Obscura Guard blocklist/watchlist — JANGAN
   tambah tanpa perintah user (blocklist adalah sumber bersama).

**Yang TIDAK dilakukan skill ini:**
- Tidak menyediakan prompt hunter/exploiter siap pakai.
- Tidak menyediakan skrip scan/eksploitasi terhadap target sewenang-wenang.
- Tidak "belajar dengan menyerang" — pembelajaran dilakukan lewat studi
  sumber + lab sendiri, bukan lewat operasi terhadap pihak ketiga.

---

## Hubungan dengan skill lain

- `pentest-web`: gerbang otorisasi 3 tingkat + kartu serangan web (W-01..W-26).
  Skill ini memakai gerbang yang sama.
- `forensik_kontrak` / `forensik_node`: aturan bukti 4 lapis + pemisahan
  fakta/inferensi. Skill ini memakai aturan yang sama.
- `bug-hunter`: recon + hunting. Kartu A-01/A-02 melengkapi fase recon-nya
  untuk target infrastruktur (bukan hanya web).
- `obscura-forensik`: tempat IOC kampanye bisa ditambahkan ke blocklist
  Guard (atas perintah user).
