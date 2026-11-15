# POLA-NODE.md — Bank Pola Forensik Node (kasus XE Protocol, 2026-11)

16 kartu N-01..N-16. Format per kartu: **Sinyal** (yang dicari di kode) · **Cara membuktikan** · **Jebakan** (yang menetralkan / false positive) · **Jangkar** (kasus nyata + statusnya). Semua jangkar dari program XE Protocol (repo xeprotocol/xe, meja bounty.xe.network) kecuali disebut lain; angka label per 2026-11-11.

---

## N-01 — Verifier Memeriksa Amplop, Bukan Bukti
**Sinyal:** fungsi `Verify*` untuk artefak yang diterbitkan sendiri (self-signed attestation/certificate) hanya memeriksa hash ulang, ikatan kunci, tanda tangan, dan FORMAT field bukti (panjang hex, rentang nilai) — tanpa menghitung ulang skor, tanpa memverifikasi proof-of-work, tanpa mencocokkan root atestasi ke kunci tepercaya mana pun.
**Buktikan:** buat artefak palsu ekstrem (skor 1e9, pengali harga maksimum, proof sampah) dengan kunci sendiri → harus DITERIMA verifier; kontrol: tamper pasca-tanda tangan ditolak, kunci asing ditolak.
**Jebakan:** jalur ingest kedua yang lebih ketat (selalu cek SEMUA jalur: RPC, gossip validator, impor file); konsumen hilir yang menghitung ulang (di XE tidak ada — harga lease dipatok dari field palsu).
**Jangkar:** XE-4847 (kita, High) & Khanhtnq #6 §2 (XE-0001, accepted+awarded, klaim Critical — menyerang Score/expiry/storage dari cacat yang sama; versi pengali harga: #354 urelkdubdqwr). Kelas yang sama, tiga pemburu, satu akar: `VerifyCertificateContent`.

## N-02 — Disiplin Timpang Antar-Saudara
**Sinyal:** satu subsistem menegakkan disiplin (skew waktu, autentikasi, validasi alamat, batas ukuran) sementara subsistem saudara yang memercayai data sejenis tidak. Cari pasangan: envelope chat (skew 5 mnt) vs registrasi direktori (tanpa skew); endpoint baca (rate limit) vs endpoint tulis (tanpa); validasi di ledger vs builder di node.
**Buktikan:** tunjukkan kedua sisi dalam satu tes/laporan berdampingan — kontrasnya adalah argumennya.
**Jebakan:** disiplin ternyata ditegakkan di lapis bersama yang dipakai keduanya (grep pemanggil bersama sebelum mengklaim).
**Jangkar:** XE-4894 (kita) & #6 §3 & #169 — direktori tanpa cek kesegaran sementara envelope chat menegakkan MaxEnvelopeSkew.

## N-03 — Pin Monotonik Largest-Wins + TTL Satu Arah
**Sinyal:** penyimpanan "yang terbesar menang" (`existing.X >= new.X → no-op`) digabung kedaluwarsa satu arah (`now − ts > ttl`). Nilai masa depan ekstrem (MaxInt64) menjadi abadi (umur negatif tak pernah > ttl), tak bisa digeser registrasi jujur, tak ada jalur cabut (Remove lokal tak pernah disebarkan). Varian: ts negatif → overflow int64 pada `now − ts` membypass TTL dari arah lain.
**Buktikan:** tes dua langkah (entri ekstrem masuk → entri jujur kalah → lookup tetap entri ekstrem); ukur juga varian negatifnya.
**Jebakan:** batas atas implisit di serde/transport; mekanisme cabut yang disebarkan lewat jalur lain.
**Jangkar:** #6 §3 (MaxInt64 + overflow negatif + map tak terbatas — cakupan lebih luas dari XE-4894 kita yang hanya +8760 jam); #156 membingkai ulang sebagai banjir akun hantu unauthenticated (triaged — bingkai berbeda, mekanisme sama).

## N-04 — Endpoint Tulis Tanpa Auth yang Mem-Panic Mesh
**Sinyal:** endpoint/gossip handler yang menerima artefak publik lalu memotong string tak tervalidasi sebagai argumen yang DIEVALUASI SEBELUM cek level (log `Debugf(..., x[:12])`) — panic untuk input pendek yang tetap lolos verifikasi (length-prefixed canonical bytes membuat tanda tangan sah untuk nilai 1 byte); goroutine handler tanpa recover → satu request membunuh node, dan mesh meneruskannya.
**Buktikan:** uji unit panjang 1/3/8 byte + kontrol negatif (ID asli 52 char → node hidup) + rantai 3 node (node C mati tanpa pernah dihubungi penyerang). Eksploitasi live ditahan; hanya reachability yang dikonfirmasi.
**Jangkar:** #15 harismanciripto111 → tiket XE-0006, AWARDED Severe 12.500 XE (dari plafon 25.000). Duplikatnya: #89. Fix yang diklaim selesai ternyata belum: lihat N-12.

## N-05 — Set Dedupe yang Gagal Menutup Menjadi Blackout Total
**Sinyal:** cache dedupe ber-cap yang prune-nya berbasis umur (`cutoff = now − 2×skew`) tetapi menolak SEMUA input baru saat penuh dan tak ada yang cukup tua untuk dibuang; digabung store tanpa batas global (cap per-kunci saja, kunci = string arbitrer, penerima tak perlu ada).
**Buktikan:** isi cap dengan ID segar → input sah berikutnya ditolak sebagai "duplikat"; ukur biaya banjirnya dengan jujur (ms/PoW × cap — caveat biaya bisa menurunkan klaimmu sendiri, dan itu benar untuk ditulis).
**Jebakan:** prune berbasis jumlah (evict-oldest) yang diam-diam ada; cap yang tidak terjangkau karena PoW mahal (hitung, jangan tebak).
**Jangkar:** XE-4934 (kita, Minor) & #258 fahriiri206 (mekanisme identik, label duplicate — ia membuka laporannya dengan paragraf "Duplicate check:" dan caveat biaya yang menurunkan klaimnya ke Low-Medium; itulah standar kejujuran program ini) & #6 §4 (retensi tanpa batas) & #269 (cap per-akun sebagai senjata eviction — vektor berbeda, store sama).

## N-06 — Tally Hantu di Konsensus
**Sinyal:** mesin quorum menghitung kandidat yang badannya tidak ada / tidak tervalidasi; bobot diambil dari wire atau dari snapshot yang bisa dipengaruhi; kandidat phantom bertahan karena buffer vote untuk konflik tak dikenal.
**Buktikan:** konstruksi konflik di mana kandidat tanpa body mencapai ambang di atas kertas; tunjukkan penjaga `promotable()`/validasi staged ada atau absen per jalur.
**Jebakan:** di XE HEAD, kandidat phantom terbukti tidak bisa di-tally (winner wajib promotable) — jalur ini BERSIH di versi yang kami audit; kartu ini tetap hidup untuk codebase/versi lain.
**Jangkar:** #42 byfor8 (awarded, High — "conflict resolution can finalize a block that never held 67% of final vote weight"); #8 Khanhtnq (vote hex malleability → kuorum palsu di satu store, korupsi finalitas di store lain).

## N-07 — Alokasi Sebelum Cap (Sync/Pagination)
**Sinyal:** handler sync/pagination men-decode & mengalokasikan satu halaman penuh SEBELUM memeriksa cap jumlah item; atau mengikuti `total` klaim server tanpa dedup/kemajuan halaman (sisi klien).
**Buktikan:** satu request/halaman jahat → alokasi terukur; di sisi klien, server rintisan yang mengulang halaman yang sama → akumulasi duplikat tanpa batas.
**Jebakan:** LimitReader pada stream menutup sebagian jalur (cek per-decode, bukan per-koneksi).
**Jangkar:** #44 byfor8 (awarded, High — klien sync OOM satu peer); XE-0023 (High — varian frontier sync); sisi klien XE: `client.GetChain` (catatan ronde 3 kami, ditahan sebagai Minor self-harm).

## N-08 — Helper Tes yang Ter-Ekspor di Build Produksi
**Sinyal:** fungsi `*ForTesting`/`Seed*` yang melewati gerbang otorisasi (minter allowlist, dsb.) ter-ekspor dari paket inti. Dua pertanyaan terpisah: (a) adakah pemanggil non-tes hari ini? (b) apakah permukaan ekspornya sendiri (library dipakai pihak ketiga, plugin, RPC tak sengaja) bisa menjangkaunya?
**Buktikan:** grep pemanggil repo-penuh + uji pemanggilan langsung; nyatakan status keterjangkauan dengan persis.
**Jebakan:** mengklaim kritis tanpa jalur — tim menutup yang spekulatif sebagai invalid; tetapi jangan pula membuangnya: di XE permukaan ini tetap diajukan pemburu lain (XE-5072) karena program membayar permukaan program.
**Jangkar:** XE-5072 (2026-11-11, `MintForTesting`/`SeedAssetForTesting` tanpa cek minter) vs penilaian ronde-1 kami (tanpa pemanggil → jalan buntu). Kebenaran operasional: ajukan sebagai permukaan dengan batas jujur, jangan dikubur dan jangan dilebihkan.

## N-09 — Divergensi Dua Implementasi Satu Interface
**Sinyal:** dua store/engine mengimplementasikan interface yang sama (mem vs badger, cache vs DB) dan salah satunya kehilangan guard: underflow tanpa cek, no-op senyap untuk record hilang (yang lain abort), pointer bersama antara hasil fetch dan state tersimpan (mutasi dari luar menulis ulang state).
**Buktikan:** tes diferensial — input identik ke kedua implementasi, salida dibandingkan (kasus XE: pending 5 dikurangi 10 → wrap ke 2⁶⁴−15 di satu, error+tak berubah di yang lain).
**Jebakan:** implementasi lemah tak pernah di-wire produksi (di XE: nol pemanggil) → latensi saja; nilai hanya sebagai Minor/pertahanan-berlapis dan harus dilabeli begitu.
**Jangkar:** ronde-3 kami (memdivergence, 3/3 tes PASS, DITAHAN tidak diajukan — preseden penilaian: tanpa jalur produksi, jangan bakar kredibilitas).

## N-10 — Audit Cakupan Hash (Metode Hasil-Negatif)
**Sinyal (metode):** untuk setiap tipe pesan bertanda tangan: enumerasi field struct → preimage hash kanonik → payload tanda tangan → setiap field yang DIBACA validasi/akuntansi. Field di luar cakupan hanya berbahaya bila dibaca; yang tidak pernah dibaca / dilucuti pra-verifikasi / menghancurkan dirinya saat dimutasi (nonce PoW) adalah bersih — dan kebersihannya bisa DIBUKTIKAN dengan tes invariansi hash.
**Buktikan:** suite tes invariansi: mutasi setiap field luar-cakupan → hash & keputusan validasi tidak berubah; kontrol: mutasi field dalam-cakupan → berubah.
**Jebakan:** field yang dibaca jalur yang jarang (auditor supply, tampilan spendable) — sapuan baca harus repo-penuh per field.
**Jangkar:** ronde-3 kami di XE: 5/5 tes invariansi PASS — permukaan ini bersih dan terbukti bersih; kartu disimpan karena metodenya menutup satu kelas utuh dengan murah di target berikutnya.

## N-11 — Permukaan Program Itu Sendiri
**Sinyal:** meja bounty / tooling DAO / alur akun program adalah kode juga: flow account-link yang menghormati parameter dari sesi pemrakarsa (`link_to`) untuk siapa pun yang menyelesaikan flow → pengambilalihan akun reporter beserta alamat payout-nya; invite/magic-link basi yang tetap sah pasca-recovery; field profil (nama tampilan) yang mem-500-kan semua permukaan note/reply.
**Buktikan:** reproduksi end-to-end di instans lokal ASLI platformnya, dengan kontrol negatif (preseden: 24/24 cek).
**Jebakan:** scope program bisa mengecualikan platformnya — baca scope; di XE permukaan ini in-scope dan dibayar.
**Jangkar:** #253 josephdenne (AWARDED — account-link merge takeover) + #326/#327 (saudara, awarded). josephdenne juga pemilik satu-satunya PR pemburu yang pernah di-merged tim (#251).

## N-12 — Klaim "Sudah Diperbaiki" yang Belum
**Sinyal:** laporan ditandai fixed / triage doc mengklaim selesai, tetapi potongan kode rentan masih ada di master (fix menyentuh jalur saudara, bukan jalur yang dilaporkan; atau fix hanya di cabang/PR yang tak pernah masuk).
**Buktikan:** jalankan PoC asli terhadap HEAD terbaru; kutip baris rentan yang masih ada + nomor commit fix yang diklaim.
**Jebakan:** perbaikan ekuivalen dengan bentuk berbeda (baca semantiknya, bukan bentuknya).
**Jangkar:** #228 ox-code (fix #15 dinyatakan selesai via #1028→#1029, slice rentan masih di master → crash tereproduksi; triaged) + pola tim menambal subset ledger dari #4 sementara subset node/API dibiarkan bertahun-versi.

## N-13 — Klasifikasi Op yang Bocor ke Gerbang Ringan
**Sinyal:** tabel klasifikasi (`IsSpendingOp`, daftar tipe per gerbang) yang menghilangkan tipe yang berdampak dana dari gerbang kuat (threshold penuh) ke gerbang ringan (1-of-N, any-signer), sementara jalur apply-nya mengeksekusi efek penuh (menimpa delegasi, mengunci stake, membatalkan lease). Varian: dedup signer dengan normalisasi yang tak konsisten antar-fungsi (raw vs lowercase) sehingga satu kunci dihitung dua kali.
**Buktikan:** untuk setiap tipe blok/op: gerbang yang diminta vs efek yang dijalankan — tabel ketimpangannya adalah laporannya; tes 1-signer menjalankan efek dana.
**Jebakan:** cek kedua di jalur apply yang diam-diam menaikkan gerbang (baca apply-nya, bukan hanya klasifikasinya).
**Jangkar:** #6 §1 Khanhtnq (Critical — BlockReceive non-spending tetapi apply menimpa 100% delegasi; lease accept/cancel/settle absen dari IsSpendingOp; varian kapital lolos dedup 2-of-N).

## N-14 — Klien/Library yang Menelan Error
**Sinyal:** jalur baca library yang tak pernah memeriksa status HTTP dan membuang error decode (`_ =`) → server error terbaca sebagai "hasil kosong, tanpa error" (saldo hantu nol); builder CLI yang mengabaikan error GetChain/GetBalances lalu menandatangani dari state kosong.
**Buktikan:** server rintisan membalas 500/HTML → klien mengembalikan kosong + err=nil.
**Jebakan:** validasi ulang di ledger membatasi dampak ke kebingungan lokal (self-harm) — ajukan hanya sebagai Minor dengan bingkai persis itu, atau tahan.
**Jangkar:** ronde-2/3 kami di XE (CLI builders + `client/` read paths, tes PASS, DITAHAN — keluarga self-harm; dicatat agar tidak diburu ulang sebagai hal baru).

## N-15 — Perlombaan & Jendela Plan→Apply
**Sinyal:** mesin overlay/cascade/scheduler yang membaca state saat merencanakan dan menerapkannya kemudian tanpa CAS/sinkronisasi ulang (stale overlay reads, swap melewati verifikasi kredensial, accept scheduler menandai kegagalan transien sebagai done sehingga tak pernah di-retry).
**Buktikan:** dua operasi tersusun waktu yang menunjukkan baca-basi menjadi tulis-sah; untuk scheduler: kegagalan transien yang tercatat permanen.
**Jebakan:** kunci global yang membuat jendelanya teoretis (di XE mayoritas jalur ini terbukti terkunci/ter-CAS dengan benar — klaim pemburu lain di wilayah ini spesifik di jendela plan→apply yang sempit).
**Jangkar:** #226 ket4min-susan (5 temuan cascade/rollback, triaged), #328 Khanhtnq (conflict RMW tak tersinkron), #348 (goroutine Stop() race), ronde-3 kami (scheduler accept — catatan source-only, tidak diajukan).

## N-16 — Ekonomi Dokumen & Konsistensi Auditor
**Sinyal:** (a) dokumen ekonomi yang salah secara material (syarat faucet, formula emisi) — dibayar sebagai temuan karena operator/pengguna bertindak atasnya; (b) auditor konservasi yang melewatkan blok aset-invalid untuk issuance tetapi tetap menjumlahkan saldonya (conserved=false permanen), atau rekonstruksi lease yang menghilangkan tipe renew dari switch.
**Buktikan:** (a) kutip dokumen vs konstanta kode berdampingan; (b) untuk auditor: eksekusi contoh dokumen terhadap kode (angka cocok = bersih, dan itu hasil yang sah untuk dicatat), atau tampilkan conserved=false dari endpoint live read-only + baris switch yang hilang.
**Jebakan:** dokumen yang mendahului fitur (stale tak berbahaya) vs yang mengubah keputusan ekonomi — hanya yang kedua temuan.
**Jangkar:** #82 (docs faucet salah — AWARDED); #356 urelkdubdqwr (auditor supply, Medium); keluarga #4 temuan 3 / #68 / #336 (label duplicate tidak konsisten untuk akar yang sama — pelajaran prosedural: jangan percaya label orang lain sebagai vonis atas mekanismemu; bedakan sendiri per N-aturan Duplicate check).

---

## Setoran pola baru

Setiap target tuntas: tambahkan kartu dengan jangkar nyata (bukan teori), perbarui hitungan di baris pertama berkas ini, dan catat di SKILL.md bila pelajarannya prosedural (bukan pola kode). Kartu tanpa kasus nyata yang terverifikasi tidak masuk bank ini.
