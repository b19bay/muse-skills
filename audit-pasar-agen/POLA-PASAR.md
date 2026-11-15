# POLA-PASAR: Kartu Pemeriksa Marketplace Kode Agen

Kartu-kartu untuk skill `audit-pasar-agen`. Setiap kartu: apa yang
diperiksa, bagaimana memverifikasi, dan apa yang dianggap temuan.
Kode status: [U] = umum (berlaku di semua marketplace kode agen),
[S] = spesifik (tergantung desain platform).

## MP-01 — Review struktural vs perilaku [U]

**Periksa:** apakah review memeriksa PERILAKU artefak, atau hanya
BENTUK-nya (manifest valid, method ada, file ada)?
**Verifikasi:** baca aturan review di repo (doctor/linter/validator);
grep aturan keamanan (dangerous API, exfiltration, fund-flow).
Cek data live: bukti review per artefak (status, timestamp, isi).
**Temuan:** review hanya struktural + tidak ada jejak review perilaku
+ status "passed" tanpa bukti pendukung.
**Contoh:** Wayfinder — kinds.py "registry runs the same rules at
review", AST statis, nothing executed; doctor.py nol cek keamanan;
semua versi live: `review_state: "passed"`, timestamp null,
`review: {}`, `rebuild_match: null`.

## MP-02 — Isi skill/instruksi tidak direview [U]

**Periksa:** apakah instruksi bahasa alami (SKILL.md, prompt, policy)
diperiksa isinya, atau hanya keberadaannya?
**Verifikasi:** baca validator skill; grep pemindaian konten
(transfer, secret, key, approve, exfil, prompt-injection).
**Temuan:** validator hanya memeriksa file ADA / struktur — isi
instruksi bebas memerintahkan apa pun.
**Contoh:** Wayfinder `_validate_skill` — hanya cek SKILL.md ada;
75/86 path membawa skill.

## MP-03 — Model izin dan persetujuan install [U]

**Periksa:** apakah artefak mendeklarasikan izin? Apakah install
menampilkan ringkasan izin? Apakah ada gerbang trust-tier?
**Verifikasi:** baca skema manifest (field permission/capability);
baca alur install (prompt, gate, filter).
**Temuan:** tidak ada deklarasi izin + tidak ada ringkasan izin saat
install + tidak ada gerbang tier. "Signed intent" yang hanya mengikat
versi+hash BUKAN persetujuan atas kode.
**Contoh:** Wayfinder — manifest tanpa field izin; install tanpa
gerbang; intent server hanya mengikat slug+versi+sha256.

## MP-04 — Eksekusi tanpa sandbox [U]

**Periksa:** bagaimana artefak dimuat dan dijalankan? In-process?
Subprocess? Sandbox? Pembatasan impor?
**Verifikasi:** baca loader (importlib? exec? subprocess?) dan runner;
grep sandbox/restrict/jail/capability.
**Temuan:** impor Python biasa in-process tanpa pembatasan apa pun.
**Contoh:** Wayfinder `strategy_loader.py` — `spec_from_file_location`
+ `exec_module`, tanpa batasan.

## MP-05 — Callback signing tanpa gerbang [U]

**Periksa:** apa yang diberikan runtime ke artefak untuk menandatangani?
Apakah ada konfirmasi per panggilan, cek jumlah, cek tujuan?
**Verifikasi:** telusuri rantai callback (runner → builder → signer);
cek apakah ada approval hook di sepanjang rantai.
**Temuan:** callback menandatangani apa pun yang diminta; satu-satunya
gerbang adalah persetujuan SATU KALI saat menjalankan (atau tidak ada
sama sekali di CLI).
**Contoh:** Wayfinder `_build_signing_callback` — wallet lokal
menandatangani dengan private key mentah in-process; tanpa cek apa pun.

## MP-06 — Dependensi mengambang [U]

**Periksa:** apakah dependensi di-pin versi atau di-resolve lewat
slug/nama saja (mengambang ke terbaru)?
**Verifikasi:** baca skema dependensi (ada field versi?); baca
resolusi install (default ke latest?); cek urutan resolusi
(bawaan dulu vs registry dulu).
**Temuan:** dependensi tanpa pin versi + install default ke latest =
menguasai satu dependensi menguasai semua dependen.
**Contoh:** Wayfinder `PathSkillDependencyConfig` tanpa field versi;
install default `latest_version`. Mitigasi parsial: dependensi
archetype di-resolve ke skill bawaan SDK dulu.

## MP-07 — Artefak tanpa owner (unclaimed) [U]

**Periksa:** apakah ada artefak tanpa owner terverifikasi? Bagaimana
alur klaimnya? Siapa yang bisa klaim?
**Verifikasi:** hitung artefak unclaimed per kind/risk-tier dari
registry live; cari alur klaim di repo (bila tidak ada = web-only,
opaque).
**Temuan:** artefak eksekusi tanpa owner + alur klaim tak terlihat =
kemungkinan pengambilalihan kepemilikan (HIPOTESIS sampai alur klaim
diperiksa).
**Contoh:** Wayfinder — 19 unclaimed, 10 tier eksekusi termasuk 6
strategi; tidak ada alur klaim di SDK.

## MP-08 — Ekonomi bond/stake [U]

**Periksa:** apakah ada bond? Berapa nilainya? Opt-in atau wajib?
Apakah ada slashing? Pernah terjadi?
**Verifikasi:** baca parameter publish (default bonded?); baca nilai
bond dari API live (nominal + USD + IDR + kurs + waktu).
**Temuan:** bond opt-in + default mati + nilai kecil dibanding
potensi curian + artefak tanpa bond tetap installable.
**Contoh:** Wayfinder — default `--unbonded`; 42/86 unbonded; bond
≈10.300 PROMPT (~$155–175); install tanpa gerbang tier.

## MP-09 — Dualitas source/bundle [S]

**Periksa:** apakah yang direview/diaudit (source) sama dengan yang
dijalankan (bundle)? Siapa yang memverifikasi keduanya cocok?
**Verifikasi:** baca builder (apakah source dan bundle dibangun dari
file yang sama?); baca publish (apakah keduanya di-upload terpisah?);
cek field rebuild/verification di API.
**Temuan:** client tidak memverifikasi kecocokan + hasil verifikasi
server tidak tercatat (null) pada versi live.
**Contoh:** Wayfinder — source.zip dan bundle.zip di-upload terpisah;
`rebuild_match: null` pada semua versi yang diperiksa. (Review membaca
bundle, jadi mismatch menipu auditor manusia, bukan review.)

## MP-10 — Install lama yang di-grandfather [S]

**Periksa:** apakah install yang dibuat sebelum verifikasi modern
diperlakukan lebih longgar saat aktivasi?
**Verifikasi:** baca logika aktivasi (apa yang terjadi bila entri
lockfile tidak punya penanda integritas?).
**Temuan:** modifikasi pada install lama hanya menghasilkan warning,
bukan penolakan.
**Contoh:** Wayfinder — entri tanpa `integrity: verified`
di-"grandfather", aktivasi lanjut dengan warning.

## MP-11 — Sandbox applet/UI artefak [S]

**Periksa:** bila artefak membawa UI web (applet), bagaimana ia
di-sandbox? (iframe sandbox? origin isolation? postMessage hygiene?)
**Verifikasi:** baca kode hosting/preview applet; cek atribut sandbox
iframe dan cek `event.origin` pada listener pesan.
**Temuan:** postMessage target `*` + listener tanpa cek origin.
(Nilai temuan tergantung apa yang dilakukan parent pada pesan —
bila hanya label, LOW; bila aksi, HIGH.)
**Contoh:** Wayfinder preview.py — `postMessage(..., '*')`, listener
tanpa cek origin, parent hanya mengubah label (LOW, dev tool saja).

## MP-12 — Reputasi: ada, tipis, tidak ditampilkan [U]

**Periksa:** apakah ada sinyal reputasi (install, bintang, follower)?
Apakah ditampilkan saat install? Bisakah digaming?
**Verifikasi:** baca field reputasi di API; baca alur install
(apakah reputasi ditampilkan?).
**Temuan:** reputasi ada tapi tidak ditampilkan saat install, atau
angkanya terlalu kecil untuk bermakna.
**Contoh:** Wayfinder — `installs/stars/reputation` ada di API
(`ai-identity`: installs 2, stars 1); install tidak menampilkan.

## MP-13 — Gerbang MCP/agen atas artefak [U]

**Periksa:** bisakah agen meng-install/menjalankan artefak tanpa
persetujuan user? Tool apa yang menyentuh artefak, dan gerbangnya?
**Verifikasi:** enumerasi tool MCP yang menyentuh artefak
(install/run/execute); baca daftar allow/ask/deny.
**Temuan:** tool run/execute di allow tanpa gerbang, atau ada tool
install tanpa konfirmasi.
**Contoh (NEGATIF — tahan):** Wayfinder — `core_run_strategy`,
`core_run_script`, `onchain_send/swap`, `contracts_deploy/execute`
semua ASK; tidak ada tool MCP untuk install path;
`contracts_call` benar-benar read-only (eth_call) sehingga ALLOW
wajar. Gerbang MCP BUKAN kelemahannya — kelemahannya adalah setelah
satu ASK dilewati, eksekusi berjalan tanpa gerbang lebih lanjut
(lihat MP-04, MP-05).
