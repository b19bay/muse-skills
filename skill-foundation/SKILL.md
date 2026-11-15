# Skill Foundation — Skill adalah Pondasi, Bukan Pajangan

Doktrin ini ditetapkan user 2026-11-14: semua skill dan bank pola WAJIB dipakai
dengan baik — selalu kaitkan skill/pola yang berhubungan, berpikir dari sudut
pandang berbeda sehingga muncul persepsi berbeda. SOUL (OMNIS MIND) adalah
landasan berpikir; skill + bank pola adalah tujuan akhir dari tujuan.

Masalah yang dipecahkan doktrin ini: skill yang hanya jadi referensi pasif akan
dilewati begitu agen memutuskan "tugas ini tidak butuh skill". Keputusan
itulahtitik lemahnya. Doktrin ini mengubah pemakaian skill dari pilihan menjadi
prosedur wajib yang bisa diaudit.

## Prinsip

- Setiap tugas substansial dimulai dari skill, bukan dari intuisi kosong.
  Sebelum bekerja, agen tahu skill mana yang mengatur pekerjaan itu.
- Satu skill hampir tidak pernah cukup. Pekerjaan nyata ditangani bundle:
  orkestrasi + lensa + validasi + pengganda.
- Skill yang dipakai akan tumbuh (umpan balik pelajaran). Skill yang tidak
  pernah dipakai akan ketahuan (ledger + review mingguan) — lalu diperbaiki
  deskripsinya, digabung, atau dipensiunkan dengan bukti.
- Bank pola diperlakukan sama seperti skill: bila ada bank pola untuk jenis
  tugas itu (mis. pattern-bank make.fun), baca dan pakai sebelum mulai, dan
  perbarui setelah selesai.

## Routing wajib pra-kerja

Jalankan sebelum MULAI pekerjaan substansial apa pun:

1. **Klasifikasikan tugas.** Jenis pekerjaan apa ini? (audit kontrak, pentest,
   riset proyek, bounty, dokumen, dst.)
2. **Buka ROUTING.md** di folder skill ini. Temukan baris jenis tugas itu dan
   bundle skill-nya.
3. **Baca SKILL.md skill yang mengatur pekerjaan itu SEBELUM mulai.**
   Minimal skill orkestrasi/utama dalam bundle; baca lensa dan validasi
   sebelum sampai pada tahap yang mereka atur. Jangan mulai dari ingatan
   tentang isi skill — baca file-nya.
4. **Bila tugas tidak ada di matriks:** cari lewat `muse.skill_search`
   dengan 2-3 kueri berbeda (istilah tugas, nama domain, nama alat). Bila
   ada yang cocok, pakai dan usulkan penambahan baris matriks di ledger.
5. **Bila tetap tidak ada skill yang cocok:** kerjakan dengan doktrin umum
   (perkataan-mutlak), catat entri ledger dengan `skills: []` +
   `notes` yang menyatakan "tanpa skill", dan pertimbangkan apakah jenis
   tugas ini cukup berulang untuk dijadikan skill baru.

Nyatakan di awal pekerjaan (ke diri sendiri, dan ke user bila relevan) skill
apa yang mengatur tugas itu. Pekerjaan yang dimulai tanpa penyebutan skill
adalah pekerjaan yang routing-nya dilewati — kembali ke langkah 1.

## Aturan bundle

- Jangan pernah mengandalkan satu skill bila matriks menamai bundle.
- Peran tiap skill dalam bundle (sesuai kolom ROUTING.md):
  - **Orkestrasi** — mengatur urutan fase dan cakupan pekerjaan.
  - **Lensa** — cara melihat masalah (pola, ketimpangan, anomali).
  - **Validasi** — memeriksa kebenaran hasil sebelum dinyatakan selesai.
  - **Pengganda** — melipatgandakan nilai satu hasil (varian, generalisasi).
- Bila dua skill dalam bundle bertabrakan prosedurnya, yang lebih spesifik
  untuk jenis tugas itu menang; catat benturan itu di ledger agar matriks
  bisa diperbaiki.

## Aturan pasca-kerja

Di AKHIR setiap tugas substansial:

1. **Tambah satu entri ke ledger** (`ledger.jsonl`, format di bawah).
   Yang mengisi adalah agen yang mengerjakan tugas itu, di akhir tugas.
   Jangan menunda pengisian ke tugas berikutnya.
2. **Umpan balik pelajaran ke skill/bank pola yang relevan SEBELUM build
   berikutnya yang sejenis.** Aturan yang sama dengan pattern-bank make.fun:
   pelajaran dicatat dulu, baru pekerjaan sejenis berikutnya dimulai.
   Bila pelajaran itu mengubah cara kerja, perbarui SKILL.md/ROUTING.md
   yang bersangkutan (bukan sekadar catatan di ledger).
3. Bila routing gagal (skill yang dipakai ternyata salah, atau skill yang
   benar baru ketahuan di tengah jalan), catat itu di `notes` entri ledger
   — itu sinyal matriks perlu diperbaiki.

## Format ledger

File: `ledger.jsonl` di folder skill ini. Append-only, satu baris JSON per
tugas selesai:

```json
{"date": "2026-11-14", "task": "nama tugas singkat", "skills": ["skill-satu", "skill-dua"], "outcome": "hasil satu kalimat", "lessons_fed_back": true, "notes": "catatan singkat bila ada"}
```

- `date`: tanggal WIB tugas selesai (YYYY-MM-DD).
- `skills`: nama folder skill yang benar-benar dibaca/dipakai (bukan yang
  hanya disebut). Kosong `[]` bila tidak ada skill yang cocok (lihat
  langkah 5 routing).
- `lessons_fed_back`: true bila pelajaran tugas ini sudah masuk ke
  skill/bank pola yang relevan (atau tidak ada pelajaran yang layak
  dicatat — jelaskan di `notes`); false bila belum dilakukan.
- Jangan pernah menghapus atau menulis ulang baris lama. Koreksi dilakukan
  dengan entri baru.

## Hierarki

- `perkataan-mutlak` tetap di atas doktrin ini: perkataan user adalah aturan
  tertinggi. Doktrin ini mengatur BAGAIMANA kerja dilakukan, bukan APA yang
  diputuskan.
- Bila doktrin ini bertabrakan dengan perintah user — termasuk perintah
  untuk bekerja cepat tanpa routing, atau perintah memakai cara lain —
  perintah user menang. Catat benturan itu di ledger bila material.
- Gerbang otorisasi yang hidup di dalam skill (mis. gerbang 3-tier di
  pentest-web, yang juga mengikat hunt-llm-ai) TIDAK PERNAH dilonggarkan
  oleh doktrin ini. Routing memilih skill; gerbang di dalam skill yang
  mengatur apa yang boleh dilakukan.

## Pengecualian

- Jawaban sepele satu kalimat tidak perlu routing: mis. menanyakan jam,
  mengonfirmasi penerimaan pesan, jawaban ya/tidak tanpa pekerjaan.
- Semua pekerjaan substansial wajib routing — termasuk pekerjaan yang
  tampak rutin (laporan terjadwal, cek berkala), karena di situlah skill
  paling mudah menjadi pajangan.
- Subagent yang didelegasikan pekerjaan substansial menerima bundle
  skill-nya di dalam brief penugasan; parent tetap mencatat pemakaian di
  ledger saat hasil kembali.

## Review mingguan

Job `skill-foundation-weekly-review` (Minggu ~09:00 WIB) membaca ledger,
menghitung pemakaian tiap skill 7 hari terakhir, mendaftarkan skill yang
tidak terpakai beserta hipotesis penyebabnya, mengusulkan penggabungan /
pensiun / perbaikan deskripsi bila ada bukti, dan memeriksa apakah
`lessons_fed_back` dilakukan. Laporannya dikirim ke chat konsolidasi
laporan job terjadwal. Review tidak pernah menghapus skill sendiri —
penghapusan/pensiun menunggu perintah user.
