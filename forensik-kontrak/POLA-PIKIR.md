# POLA PIKIR — cara berpikir jauh dalam menemukan kerentanan
Sintesis 2026-11-04 dari studi referensi (REFERENSI.md) + pengalaman lapangan Origin/Lista/Alchemix. Dokumen ini mengatur CARA berpikir; POLA.md mengatur APA yang dicari; SKILL.md mengatur URUTAN kerja. Baca dokumen ini di Fase 0 setiap target.

## Titik berangkat: inversi, bukan daftar
Setiap kontrak aman hanya karena sejumlah asumsi selalu benar. Pekerjaan penyerang adalah mendaftar asumsi itu lalu menanyakan, satu per satu: "di mana tepatnya asumsi ini bisa salah — oleh siapa, kapan, dengan biaya berapa?" Checklist menemukan bug yang sudah dikenal; inversi menemukan bug yang belum bernama. Untuk setiap fungsi bernilai, tiga pertanyaan emas lama tetap berlaku, ditambah dua baru:
4. Apa yang harus SELALU benar (invariant) agar fungsi ini aman, dan input/keadaan apa yang membuatnya salah?
5. Siapa yang dipercaya di sini, dan apa bukti batas kepercayaan itu? (P-33)

## Klasifikasi berbasis efek (RareSkills)
Kelompokkan setiap dugaan bukan menurut nama bug-nya, melainkan menurut EFEK nilainya: (a) dana bisa DICURI, (b) dana bisa TERKUNCI, (c) imbalan/hasil KURANG dari seharusnya, (d) imbalan/hasil LEBIH dari seharusnya. Klasifikasi efek mencegah kebutaan kategori: bug "sepele" yang efeknya (d) pada skala besar adalah Critical; bug "terkenal" yang efeknya nol bukan apa-apa.

## Tiga peta, bukan satu
Peta angka (siapa menulis/membaca tiap angka penentu nilai) tetap yang utama. Studi menambahkan dua peta yang selama ini implisit:
- **Peta WAKTU**: setiap angka punya umur. Kapan angka ini terakhir benar? Apa yang terjadi di antara dua pembaruan (blok, epoch, jendela aktivasi, jeda sekuen L2, tenggat root)? Separuh kelas frekuensi tinggi (P-23 kebasian) hidup di peta ini.
- **Peta PERAN**: enumerasi semua peran tepercaya + batas buktinya (P-33). Volume temuan kontes terbesar adalah asumsi aktor tepercaya — bukan karena auditor suka mengeluh, tetapi karena batas peran jarang dibuktikan.

## Tiga hukum lapangan baru (melengkapi H1–H5)
- **H6 — Waktu adalah dimensi serangan.** Harga basi, jendela aktivasi, antrean penebusan, masa tenggang: setiap desain yang benar "pada akhirnya" bisa salah "untuk sementara", dan sementara itu cukup.
- **H7 — Konfigurasi adalah kode.** Kuorum verifikator 1-of-1, cap yang tidak mengikat jalur nyata, bound oracle yang tak disetel: keamanan live ditentukan NILAI konfigurasi, bukan niat di kode. Baca konfigurasi live sebelum menyimpulkan dari kode (pola ini sudah menyelamatkan K-01/K-02 di Lista; kini jadi hukum).
- **H8 — Setiap EIP baru menulis ulang asumsi lama.** EIP-6780 mengubah selfdestruct, EIP-1153 menciptakan residu lintas-callback, EIP-7702 menghapus "EOA tak berkode". Untuk target apa pun, tanyakan: asumsi EVM diam-diam apa yang dipakai kode ini, dan apakah asumsi itu masih benar di fork saat ini?

## Prior frekuensi — ke mana perhatian dialokasikan
Data kontes (Sherlock 1.032 temuan tere konsiliasi; Code4rena 271 bug vs 35 exploit) memberi urutan prioritas untuk protokol lending/vault/CDP: manipulasi oracle → kebasian → likuidasi → pembulatan → kontrol akses → reentrancy. Catatan kalibrasi: reentrancy volumenya kecil tetapi tingkat penerimaannya tertinggi (78%) — bila ditemukan, hampir selalu nyata; manipulasi oracle volumenya besar tetapi sering spekulatif (diterima 36%) — tuntut bukti jalur eksekusi penuh sebelum mengklaim. Kelas yang jarang masuk top-10 tetapi memenuhi temuan nyata: kebasian sebagai kelas sendiri, kesalahan fee, inkompatibilitas token rebasing/fee-on-transfer, arah pembulatan saham, kelalaian sequencer-uptime, bug reset klaim sebagian.

## Metode berpikir jauh (langkah berpikir, bukan langkah kerja)
1. **Fungsi kembar**: bila satu fungsi memvalidasi, cari kembarannya yang tidak. Kelas produksi teratas menurut samczsun adalah validasi input yang hilang — biasanya hilang di jalur saudara, bukan jalur utama.
2. **Invariant dulu, serang kemudian**: tulis invariant protokol dalam kalimat ("total klaim ≤ total aset", "satu posisi satu klaim") sebelum membaca implementasi; lalu setiap fungsi diuji sebagai calon pelanggar invariant, bukan sebagai calon bug bernama.
3. **Komposisi antar-lapis**: bug besar jarang tinggal di satu lapis. Tumpuk: mekanika protokol × semantik EVM (callback, transient, delegasi) × insentif ekonomi (apakah likuidator/keeper/solver akan benar-benar datang?) × waktu (urutan dalam blok, lintas blok, lintas rantai). Seri K adalah bentuk formalnya; K-07 (spiral utang macet) lahir dari menumpuk donasi × pasar tipis × rasionalitas likuidator.
4. **Tanya harga asumsi**: untuk setiap gerbang "hanya X yang boleh", tanya berapa biaya menjadi X (menyewa ambang, membeli peran, meminjam prasyarat — H5) dan berapa lama gerbang itu harus bertahan.
5. **Buktikan negatifmu**: kesimpulan "bersih" wajib menyebut apa yang akan terlihat bila kelas itu ada, dan bahwa tanda itu sudah dicari. (Pelajaran Fase 8 Origin: unknown ditutup dengan enumerasi bukti, bukan dibiarkan sebagai residu.)

## Rezim latihan (menjaga pola pikir tetap tajam di luar perburuan)
- **Shadow audit**: kerjakan ulang satu kontes/audit berjangka waktu yang laporannya sudah terbit; bandingkan temuan + severity dengan laporan resmi; catat selisih kalibrasi di BELAJAR.md.
- **Reproduksi sebelum membaca**: untuk insiden dari DeFiHackLabs, jalankan/tulis PoC-nya dulu dari tx-nya, baca postmortem sesudahnya.
- **Baca berwaktu (RACE)**: sesekali baca protokol cacat dengan batas waktu untuk melatih kecepatan mengenali pola di bawah tekanan kontes.
- **Setor atau lupakan**: setiap sesi belajar berakhir dengan setoran ke bank (kartu, hukum, atau koreksi) — pengetahuan yang tidak tersetor dianggap belum dipelajari.
