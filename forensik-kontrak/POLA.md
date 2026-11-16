# POLA — Kartu Pola Serangan (bank pola forensik_kontrak v2)

Disuling 2026-11-04 dari 68 kasus eksploitasi terverifikasi (berkas KASUS-1 s.d. KASUS-5 di folder ini) + data frekuensi DeFiLlama (1.293 insiden, $21,1M hilang), OWASP Smart Contract Top 10 (2025/2026), dan konsensus laporan kerugian 2024 (Immunefi/De.Fi/Hacken/CertiK).

Cara pakai: di awal pemeriksaan target, cocokkan target ke kartu-kartu ini SEBELUM membaca kode secara linier. Kartu yang cocok menjadi hipotesis pertama yang diuji. Setiap kartu: kasus jangkar → mekanisme → tanda di kode → prasyarat → uji termurah → pertanyaan pemburu.

## Data frekuensi (mengapa urutan ini)

- Kelas kegagalan terbesar (DeFiLlama): **Access Control** 226 insiden/$2,0M · **Manipulasi Oracle** 161/$892jt · **Reentrancy** 63/$458jt. Per teknik: Improper Access Control 141/$1,2M · Spot Price Manipulation 133/$833jt · Reentrancy 58/$385jt.
- Studi reproduksibilitas DeFiLlama/Firepan: kelas teknik yang 100% insidennya bisa ditemukan murni dari kode — improper access control, manipulasi harga spot, reentrancy, kesalahan akuntansi saham, kesalahan aritmetika, serangan donasi. Inilah lahan buruan Immunefi.
- Kerugian uang terbesar justru di luar kode (kunci/ops: 65–78% kerugian 2024), tetapi 77,5% hadiah Immunefi yang dibayarkan adalah untuk bug smart contract. Berburu di irisan: terlihat dari kode × sering × dibayar.
- OWASP SC Top 10 — 2025: Access Control ($953jt di 2024), Price Oracle Manipulation, Logic Errors, Lack of Input Validation, Reentrancy, Unchecked External Calls, Flash Loan Attacks, Integer Overflow, Insecure Randomness, DoS. 2026 menambah: Arithmetic Errors + Proxy & Upgradeability.

## Lima hukum lapangan (meta-pola dari 68 kasus)

- **H1 — Batas dua representasi.** Hampir semua kerugian lahir di batas antara dua representasi dari hal yang sama: saldo internal vs `balanceOf`, harga spot vs nilai, tx yang ditampilkan vs payload yang ditandatangani, kode yang ditinjau vs kode yang dieksekusi, ambang tertulis vs ambang efektif. Buru batasnya, bukan fungsinya.
- **H2 — Angka yang bisa digerakkan tak boleh dipercaya di blok yang sama.** Jika penyerang bisa mengubah sebuah angka (saldo, harga, index, rate, root, counter) dan fungsi bernilai membacanya dalam transaksi/blok yang sama, itu jalur drain — terlepas dari nama polanya.
- **H3 — Keadaan kosong/debu adalah keadaan paling berbahaya.** Pasar baru, `totalSupply` nol, saldo 8 wei: di sanalah pembagian dan pembulatan menjadi seluruh harga. Uji selalu pada keadaan kosong, debu, dan satu-satunya pengguna.
- **H4 — Kesalahan kecil yang bisa diulang searah = drain penuh.** 1 wei × pengulangan atomik (flash loan, batch, putaran) adalah mekanisme amplifikasi universal. Uji bukan "apakah ada selisih" tapi "apakah selisihnya sistematis searah dan bisa diulang dalam satu tx".
- **H5 — Prasyarat yang bisa disewa bukan prasyarat.** Modal, suara governance, likuiditas, bahkan identitas bisa disewa satu blok (flash loan, delegasi, pasar yang dibuat sendiri). Untuk setiap syarat keamanan, tanya: berapa biaya memenuhinya selama tepat satu transaksi?

## Kartu pola

### P-01 · Call sebelum tulis (reentrancy klasik)
Jangkar: The DAO ($60M). Mekanisme: nilai keluar lewat external call sebelum saldo/utang ditulis; fungsi yang sama masuk lagi terhadap state lama.
Tanda: external call pembawa nilai di tengah fungsi; SSTORE saldo/supply SETELAH call; tanpa lock. Grep: urutan `call{value` / `transfer(` lalu penulisan `balances[`/`totalSupply` sesudahnya.
Prasyarat: fungsi bisa dipanggil ulang dari penerima call. Uji fork: kontrak penerima jahat yang memanggil ulang fungsi yang sama di fallback; bandingkan saldo sebelum/sesudah.
Pertanyaan: "State apa yang seharusnya sudah berubah sebelum call ini, tapi belum?"

### P-02 · Guard sebagian — saudara yang tertinggal
Jangkar: Rari/Fei `exitMarket` ($80M), Revest `depositAdditionalToFNFT` ($2M). Mekanisme: patch/lock menutup fungsi utama; fungsi saudara yang berbagi state yang sama tertinggal tanpa guard.
Tanda: sebagian fungsi ber-`nonReentrant`, sebagian tidak, di kontrak yang sama; dua fungsi menulis mapping/posisi yang sama.
Uji: daftar semua fungsi pengubah-state yang menyentuh state bersama; untuk yang tak terguard, rancang masuk-kembali lewat yang terguard.
Pertanyaan: "Fungsi mana yang paling jarang dipakai di sini — apakah ia berbagi state dengan yang terguard?"

### P-03 · Read-only reentrancy — view yang dibaca di tengah callback
Jangkar: dForce ($3,65M), Sentiment ($1M), Sturdy ($800rb), Midas ($660rb). Mekanisme: AMM mengirim nilai keluar sebelum bukunya beres; pihak KETIGA membaca fungsi `view` (harga LP, `get_virtual_price`, `getPoolTokens`) di jendela itu dan memercayainya untuk borrow/likuidasi. Guard pada pembaca tidak menolong — view tidak bisa diblokir lock.
Tanda: harga kolateral diturunkan dari state pool live; AMM di bawahnya punya jalur keluar yang membayar sebelum burn/update.
Uji fork: panggil fungsi harga target DARI DALAM fallback saat pool di tengah exit; bandingkan dengan harga di luar jendela.
Pertanyaan: "Siapa membaca angka ini, dan bisakah aku membuat angka itu dibaca saat sumbernya setengah jadi?"

### P-04 · Token/pasar yang bisa didaftarkan penyerang
Jangkar: Penpie ($27M), Grim ($30M), Akropolis ($2M), Lendf.Me/imBTC ($25M). Mekanisme: sistem menerima token/market/pasar dari siapa pun; token jahat membawa hook atau akuntansi delta yang diukur melintasi call ke kontrak penyerang.
Tanda: parameter `token` dari pengguna tanpa `require(token == terdaftar)`; registrasi pool/market tanpa izin; akuntansi `balanceAfter - balanceBefore` melingkupi external call; token ber-hook (777/721/1155) diterima kontrak tanpa guard.
Uji fork: daftarkan token jahat minimal (hook yang masuk kembali / transferFrom yang berbohong secara terukur) dan jalankan jalur deposit/harvest.
Pertanyaan: "Siapa yang boleh memperkenalkan kontrak baru ke dalam arus nilai ini?"

### P-05 · Pembersihan state asimetris antar fungsi berpasangan
Jangkar: XCarnival ($3,8M). Mekanisme: fungsi A (withdraw/return) mengeluarkan aset tetapi tidak menghapus record yang dipercayai fungsi B (borrow) — tanpa callback pun, urutan transaksi biasa menguras.
Tanda: pasangan fungsi yang berbagi mapping; satu sisi menulis, sisi lain tidak membersihkan/menandai.
Uji: jalankan urutan A→B→A→B di fork dan lacak apakah hak yang sama terpakai dua kali.
Pertanyaan: "Record apa yang tetap hidup setelah fungsi pasangannya selesai?"

### P-06 · Harga spot satu pool dikonsumsi fungsi bernilai
Jangkar: bZx ($1M), Deus (2×, $16,4M), PancakeBunny ($45M), Mango ($114M, varian mark).
Mekanisme: `borrow()`/`mint()`/`liquidate()`/reward membaca rasio reserve satu pool tipis di blok yang sama saat penyerang menggerakkannya.
Tanda: `getReserves()`, `getAmountsOut`, rasio saldo pair di dalam jalur pinjam/cetak/likuidasi; tanpa TWAP/sumber kedua/batas deviasi.
Uji fork: flash loan → geser pool → panggil fungsi bernilai → ukur nilai terekstrak vs biaya menggeser.
Pertanyaan: "Berapa biaya memindahkan harga ini 2×, dan berapa nilai yang dibuka harga 2× itu?"

### P-07 · Harga dari saldo live (donasi mengubah harga)
Jangkar: Cream/yUSD ($130M), Zunami ($2,1M), Harvest ($24M), Warp + Cheese Bank (LP dari reserve).
Mekanisme: harga = f(`balanceOf`/`totalAssets`/`getReserves`) kontrak/pool; `transfer()` telanjang (donasi) atau swap miring mengubah harga tanpa menyentuh logika pencetakan.
Tanda: `pricePerFullShare`, `totalAssets()/totalSupply` dari saldo mentah, rumus LP Σ(balance×price)/supply, `get_virtual_price` dikonsumsi langsung.
Uji fork: donasikan jumlah terukur ke alamat harga-sumber; baca harga sebelum/sesudah; bila berubah, rangkai ke fungsi konsumennya.
Pertanyaan: "Bisakah transfer biasa — tanpa memanggil fungsi apa pun milik target — mengubah harga yang dipercayai target?"

### P-08 · Oracle yang bisa ditulis orang asing / jendela yang runtuh
Jangkar: BonqDAO ($120M nosional), Inverse ($15,6M). Mekanisme: oracle pelaporan-tanpa-izin dibaca pada nilai TERAKHIR tanpa jendela sengketa; atau TWAP yang observasinya hanya bertambah saat dipanggil sehingga jendela efektifnya runtuh ke hitungan detik.
Tanda: `getCurrentValue()`/`latestAnswer()` pada oracle optimistis; parameter `period` TWAP vs jumlah observasi aktual; likuiditas venue di belakang feed < nilai yang diamankannya.
Uji: tulis/geser satu observasi secara sah (sebagai pengguna biasa) lalu baca harga efektif yang dikonsumsi target.
Pertanyaan: "Siapa yang boleh menulis angka ini, berapa biayanya, dan berapa lama angka tulisku bertahan sebagai 'harga'?"

### P-09 · Kolateral referensi-diri / pasar tipis tanpa cap
Jangkar: Mango ($114M), Venus XVS (utang macet >$100M), Moola ($8,4M). Mekanisme: token terbitan sendiri/float tipis diterima sebagai kolateral dengan faktor tinggi; PnL belum terealisasi dihitung sebagai daya pinjam; hasil pinjaman dipakai memompa kolateralnya sendiri.
Tanda: collateralFactor ≥60–80% pada token sendiri/tipis; `borrowCap = 0`; kredit mencakup PnL unrealized; tanpa mode isolasi.
Uji: model ekonomi di fork — pinjam X, pompa X, pinjam lagi terhadap X; hitung apakah putarannya positif.
Pertanyaan: "Bisakah aset yang kupinjam menjadi kolateral untuk pinjaman berikutnya?"

### P-10 · Inflasi pasar kosong (donasi + supply ≈ 0)
Jangkar: Sonne ($20M), Hundred ($7,4M), Onyx Protocol ($2,1M), Resupply ($9,6M), Radiant Jan-2024 ($4,5M).
Mekanisme: pasar/vault baru dengan `totalSupply` nol atau debu; donasi menggelembungkan exchange rate turunan saldo; debu saham mengklaim nilai raksasa sebagai kolateral.
Tanda: `exchangeRate = (getCash + borrows − reserves)/totalSupply` dengan `getCash = balanceOf(this)`; tanpa dead shares/virtual offset/seed terkunci; deployment dan penyemaian terpisah transaksi; proposal pembuatan pasar bisa dieksekusi siapa pun.
Uji fork: pada pasar kosong/debu — donasi, cetak jumlah minimum, baca klaim per saham, coba pinjam terhadapnya.
Pertanyaan: "Apa yang terjadi pada pengguna PERTAMA, dan pada donasi PERTAMA, di pasar ini?"

### P-11 · Pembulatan searah yang bisa diulang
Jangkar: Balancer 2025 ($116–128M), zkLend ($9,6M), Midas ($0,6M), Bunni ($8,4M).
Mekanisme: pembagian/upscale membulat menguntungkan pemanggil secara sistematis; primitif batch/putaran mengulanginya ratusan kali per tx sampai invariant terkuras.
Tanda: `mulDown` pada upscale ber-rate non-uniter; `redeemTokens = amount / rate` terpotong untuk penebus; tanpa jumlah minimum; perilaku berbeda pada saldo <100 wei.
Uji fork/fuzz: operasi berukuran debu diulang dalam loop; ukur drift per iterasi dan total setelah N iterasi; uji khusus saldo 1–100 wei.
Pertanyaan: "Jika kulakukan operasi terkecil yang mungkin 1.000 kali, ke mana nilainya mengalir?"

### P-12 · Jalur bootstrap yang bisa dijangkau ulang
Jangkar: Yearn yETH ($9M). Mekanisme: cabang inisialisasi/deposit-pertama (dengan asumsi dan aritmetika longgarnya, mis. `unsafe_sub`) menjadi bisa dijangkau lagi saat supply tersimpan kembali ke 0 sementara saldo riil masih ada.
Tanda: cabang khusus `if (totalSupply == 0)`; aritmetika `unchecked`/`unsafe_` di jalur mint; cache supply terpisah dari saldo token aktual.
Uji: kuras sistem ke supply 0 dengan saldo sisa, lalu panggil jalur masuk sebagai "pengguna pertama" baru.
Pertanyaan: "Bisakah keadaan 'baru lahir' diciptakan lagi di tengah umur kontrak?"

### P-13 · Rate runtuh ke nol / tanpa pagar kewarasan
Jangkar: Resupply ($9,6M). Mekanisme: rumus `RATE = KONSTANTA / harga` dengan pembagian floor menghasilkan 0 pada harga termanipulasi; cek solvabilitas membaca 0 sebagai "aman untuk utang berapa pun".
Tanda: pembagian yang hasilnya memberi makan `isSolvent`/batas pinjam tanpa `require(rate > 0)`; tanpa batas atas/bawah pada harga/rate yang dikonsumsi.
Uji: dorong input ke ekstrem (harga maksimum yang bisa ditulis) dan baca rate + keputusan solvabilitasnya.
Pertanyaan: "Nilai ekstrem apa yang membuat rumus ini menghasilkan 0, tak hingga, atau negatif — dan siapa yang membaca hasil itu?"

### P-14 · Executor generik atas calldata pengguna
Jangkar: Poly Network ($611M), Socket ($3,3M), LI.FI ($11,6M). Mekanisme: kontrak istimewa (memegang dana/approval) mengeksekusi target+calldata pasokan pengguna; validasi memeriksa hasil, bukan operasi; atau satu modul baru melewatkan allowlist yang dimiliki semua saudaranya.
Tanda: `.call(` dengan target/data dari input; dispatch metode berbasis string/selector hasil tabrakan; tidak ada allowlist selector+target; facet/route termuda berbeda pola dari saudaranya.
Uji fork: enkodekan `transferFrom(korban, aku, jumlah)` sebagai "swap"/aksi; periksa apakah require pasca-kondisi menangkapnya.
Pertanyaan: "Operasi paling berbahaya apa yang bisa kuenkodekan ke dalam bytes yang boleh kulewatkan ini?"

### P-15 · Pesan/event diperlakukan sebagai fakta
Jangkar: Wormhole ($326M), Nomad ($190M), Qubit ($80M), THORChain ($13M), Meter ($4,4M).
Mekanisme: sistem mengkreditkan nilai berdasarkan KLAIM — pesan lintas-rantai, event deposit, memo, hasil verifikasi — tanpa mengikat klaim ke sumber (chain, kontrak, set penanda tangan) dan pergerakan saldo aktual.
Tanda: hasil verifikasi dibaca dari objek pasokan pemanggil; event yang alamat penerbitnya tak dipaku; `deposit()` yang event-nya bisa terbit untuk transfer no-op (token address(0)); jalur refund membayar terhadap klaim masuk tak terverifikasi.
Uji: buat klaim paling murah (kontrak penerbit event sendiri, pesan tanpa bukti, deposit nol) dan lihat apakah sisi penerima mengkreditkannya.
Pertanyaan: "Apa buktinya hal ini terjadi — dan apakah bukti itu bisa kubuat sendiri?"

### P-16 · Implementasi tak terinisialisasi & sentinel yang valid
Jangkar: Parity ($150M beku), Nomad ($190M). Mekanisme: `initialize()` bisa dipanggil pada implementasi/library itu sendiri; atau init memasang nilai kritis (root, owner) ke nilai yang sama dengan storage kosong sehingga "belum diatur" terbaca sebagai "sah".
Tanda: implementasi live dengan slot owner/governor masih 0 tetapi `initialize` belum terkunci; nilai keamanan default = 0x00/0; upgrade yang menginisialisasi ulang.
Uji read-only: baca slot owner/root IMPLEMENTASI (bukan proxy); simulasi `initialize` di fork dari akun acak.
Pertanyaan: "Kontrak mana yang bisa 'dilahirkan' oleh orang asing hari ini?"

### P-17 · Ambang efektif ≠ ambang nominal
Jangkar: Ronin ($625M, 5-dari-9 = satu perusahaan + delegasi basi), Harmony ($100M, 2-dari-4), Multichain ($126M, "MPC" = satu CEO), pGALA (admin proxy EOA, kunci bocor di GitHub).
Mekanisme: kendali tertulis terdistribusi, kendali nyata terkonsentrasi — atau izin sementara tak pernah dicabut.
Tanda: admin proxy berupa EOA; ambang ≤2; perubahan kepemilikan peran tanpa pengumuman; delegasi/allowlist tanpa kedaluwarsa.
Uji read-only: petakan graf kendali efektif dari data on-chain (siapa memegang peran apa, sejak kapan, lewat alamat apa).
Pertanyaan: "Berapa MANUSIA yang sungguh harus berkompromi agar brankas ini terbuka?" (Untuk Immunefi: laporkan hanya bila terwujud sebagai cacat kode/config in-scope.)

### P-18 · Dua fungsi tidak sepakat di batas
Jangkar: KyberSwap Elastic ($48M), Balancer scaling ($120M+), Bunni LDF ($8,4M).
Mekanisme: dua perhitungan atas hal yang sama (predikat lintas-tick vs langkah swap; scale vs unscale; buku hook vs invariant AMM) memakai input/pembulatan berbeda dan tidak sepakat tepat di nilai batas.
Tanda: fungsi yang ditimpa menyimpang dari asumsi terdokumentasi kelas dasarnya; pasangan fungsi yang menghitung kuantitas yang sama dengan cara berbeda; perilaku berubah di dekat tick/ambang/skala.
Uji fuzz terarah: input yang berakhir ±1 wei dari setiap batas internal (tick, ambang rebalance, batas skala).
Pertanyaan: "Kuantitas apa yang dihitung dua kali dengan dua cara di sistem ini?"

### P-19 · Komponen tepercaya di luar telaah
Jangkar: Curve/Vyper ($52–69M), Cetus library ($223M), Ledger Connect Kit ($600rb), Bybit via frontend Safe ($1,5M).
Mekanisme: pertahanan/kebenaran bergantung pada komponen yang dianggap selesai — versi compiler, library math pihak ketiga, frontend vendor, hook — dan komponen itulah yang cacat.
Tanda: versi compiler yang punya bug publik; library `checked_*` buatan sendiri; lock yang slot-nya tidak terbukti bersama di bytecode; ketergantungan pada UI untuk verifikasi payload.
Uji: catat versi compiler dari metadata; silangkan ke daftar bug compiler; SLOAD/SSTORE slot lock di bytecode untuk dua fungsi terguard; inventarisasi library sebagai in-scope.
Pertanyaan: "Apa yang kupercayai tanpa membaca di tumpukan ini — dan siapa yang terakhir memverifikasinya?"

### P-20 · Governance yang bisa disewa / payload tak terikat kode
Jangkar: Beanstalk ($182M), Tornado governance ($1M + pengambilalihan), Build Finance ($470rb), Compound Prop 289 ($25M berisiko, $0 hilang).
Mekanisme: suara dihitung dari saldo blok eksekusi (bisa flash loan); eksekusi darurat memintas timelock; target proposal metamorfik (CREATE2/selfdestruct) sehingga kode tereksekusi ≠ kode tertinjau; atau kuorum nominal jauh di atas turnout nyata.
Tanda: snapshot suara di blok yang sama dengan eksekusi; `emergencyCommit`; target proposal upgradeable/ber-SELFDESTRUCT; kuorum vs riwayat turnout.
Uji: hitung biaya memperoleh suara pengesah selama satu blok vs nilai treasury; bandingkan kuorum dengan turnout 10 proposal terakhir.
Pertanyaan: "Berapa harga demokrasi protokol ini selama tepat satu blok?"

### P-21 · Jendela deploy/upgrade/aktivasi (pola waktu)
Jangkar: Sonne (pasar dieksekusi siapa pun sebelum disemai), Radiant (pasar disambar 6 detik setelah aktivasi), Socket (route berumur 3 hari), LI.FI (facet 5 hari), Nomad (upgrade).
Mekanisme: keadaan paling rentan sebuah sistem adalah jam-jam pertamanya: config belum lengkap, pasar belum disemai, allowlist belum konsisten, root belum benar.
Tanda (di riwayat on-chain): kontrak/facet/pasar berumur <30 hari yang sudah memegang nilai; celah waktu antara deploy dan penyemaian/konfigurasi; transaksi inisialisasi yang bisa dieksekusi/di-frontrun publik.
Uji read-only: rekonstruksi garis waktu deploy→init→seed→nilai masuk; tandai setiap celah di mana nilai bisa masuk sebelum config selesai.
Pertanyaan: "Kapan kontrak ini paling telanjang, dan apakah jendela itu masih terbuka untuk bagian yang baru ditambah?"

---
*Bank pola ini hidup: setiap target yang selesai diperiksa wajib menyetor pola baru atau konfirmasi pola lama (lihat SKILL.md, Mesin Belajar). Kasus lengkap: KASUS-1 s.d. KASUS-5.*

---

## Setoran pola — Origin Protocol, uji ulang mode penyerang (2026-11-04)
- **P-15 (pesan/pool lintas-rantai dianggap fakta): KONFIRMASI NEGATIF dengan bukti penuh.** Asumsi satu-tenant pada pool WETH bersama adapter Superbridge diverifikasi lewat sweep eth_getLogs riwayat PENUH kedua chain (ETH 26.232.939–26.337.912; Base 52.847.378–53.481.733): tepat satu event Authorised per chain (strategi yang sama, 4 blok pasca-deploy), nol Revoked. Pelajaran metode: unknown bertipe "siapa saja yang pernah diberi hak X" SELALU bisa ditutup tuntas lewat enumerasi event sejak blok deploy — jangan pernah tinggalkan sebagai residu bila event-nya ada.
- **Komponen tepercaya (keluarga P-19): lolos uji bermusuhan.** BeaconProofsLib (verifikasi SSZ staking) dibedah sebagai pemalsu: panjang bukti terkunci persis, indeks tergeneralisasi terikat indeks riil, ekstraksi potongan leaf benar. Konfirmasi bahwa pembacaan bermusuhan atas komponen "teraudit, lewati" tetap wajib — di target ini ia bersih, dan kebersihannya kini terbukti, bukan diasumsikan.
- **Arbitrase harga market-maker (H4): GUGUR.** Bila buy < cross < sell konsisten dalam pita sempit menguntungkan protokol di SEMUA aset dan tak ada kaki di atas par, loop pengulangan tidak punya bahan bakar — cek konfigurasi live empat angka ini lebih dulu sebelum menulis PoC arbitrase apa pun.

## Setoran lapangan — Lista DAO (2026-11-04, target tuntas tanpa temuan)
- **Uji independensi sumber SEBELUM K-01**: di Lista, "tiga mesin harga" (CDP/Moolah/CDP-oracle) ternyata berbagi akar ResilientOracle — angka live identik membunuh K-01 dalam satu batch baca. Pelajaran: perbandingan harga hanya bermakna bila sumbernya terbukti independen; cek dulu apakah satu sisi sekadar membungkus sisi lain (OracleAdaptor→Resilient).
- **createMarket bergerbang kondisional** (Morpho-fork Lista): `require(roleCount(OPERATOR)==0 || hasRole(...))` — publik hanya bila NOL operator terdaftar. Nilai live (OPERATOR=3) mematikan pembuatan pasar publik; pola "gerbang bergantung hitungan peran" wajib dicek LIVE, bukan dari kode saja.
- **Broker-sebagai-oracle, dua mode kesehatan** (pola desain baru): pasar broker memakai harga teradjustasi per-pengguna untuk konversi seize, tetapi gerbang kesehatan/likuidasi MENIMPA ke harga asli + total utang broker. Saat menemui oracle per-pengguna di fork mana pun: petakan jalur mana memakai harga mana — ketidaksepakatan antar-jalur adalah tempat polanya patah, kesepakatan penuh adalah tanda desain matang.
- **Referensi positif P-15**: leaf merkle skor kredit Lista = keccak(chainid, kontrak, user, score, versionId) + rotasi root dua langkah bertenggat waktu — ikatan lima dimensi; jadikan tolok ukur saat menilai sistem bukti di target lain.

## Setoran lapangan — Alchemix V3 (2026-11-04, target tuntas tanpa temuan)
- **Bobot kelangsungan proporsional (pola desain anti-P-18)**: earmark/redemption dibebankan lewat bobot Q128 global (epoch+index) ke semua utang secara proporsional, tanpa iterasi per akun. Akibat buruan: serangan urutan/pemilihan korban mati secara struktural; permukaan yang tersisa hanya pembulatan pembaruan bobotnya — dan di Alchemix arah bulatnya dijaga eksplisit (revert bila selisih melewati ambang debu). Kenali pola ini di target lain: bila ada "survival/index weight", uji di situ, bukan di alur per akun.
- **Likuidasi model keeper-antre**: kolateral sitaan masuk antrean penebusan (transmuter), likuidator hanya menerima fee — insentif dan arah aliran berbeda total dari likuidasi diskon ala Compound/Morpho. Saat memetakan target, tentukan dulu keluarga likuidasinya; asumsi keluarga yang salah membuat seluruh uji P-18 meleset.
- **CDP tanpa oracle = risiko terkonsentrasi di harga saham vault**: Alchemix menilai kolateral murni dari convertToAssets MYT. Pertanyaan emasnya menyempit jadi satu: "siapa bisa menggerakkan convertToAssets vault itu" (donasi/strategi di bawahnya). Di sini dijawab Morpho VaultV2 yang menghitung aset dari akuntansi adapter, bukan saldo mentah — donasi langsung mati; residu hanya jalur dua-lompatan via vault eksternal.
- **Circuit breaker bad-debt**: deposit & mint berhenti saat protokol dalam keadaan bad debt (_isProtocolInBadDebt) — pola pengaman yang layak dicari keberadaannya di target CDP lain; ketiadaannya memperbesar dampak temuan solvabilitas.

## Gelombang 2 — kartu dari studi referensi (2026-11-04; sumber: OWASP SC Top 10 2026, data frekuensi kontes Sherlock/Code4rena, DeFiVulnLabs, riset frontier — rujukan lengkap di REFERENSI.md)
- **P-22 Read-only reentrancy** — fungsi VIEW dibaca kontrak lain saat state penulisnya setengah jadi (klasik: `get_virtual_price` Curve dibaca pasar lending di tengah callback withdraw). Jangkar: dForce ±$3,6 jt (2023), Midas, Market.xyz. Uji: setiap harga dari pool LP — apakah ada jalur callback yang membuka jendela state tak konsisten saat harga itu dibaca?
- **P-23 Kebasian (staleness) sebagai kelas sendiri** — bukan manipulasi: hanya cek kesegaran yang HILANG (updatedAt, answeredInRound, heartbeat) atau, di L2, feed sekuen mati yang tampak segar karena waktu blok ikut berhenti. Wajib cek Sequencer Uptime Feed + grace period di setiap target L2. Bukti frekuensi: volume submisi kontes #2 (174, diterima 49%) — kelas yang paling sering ditemukan auditor sungguhan namun jarang jadi kartu sendiri.
- **P-24 Phantom permit & permit front-run** — permit "sukses semu" pada token tanpa permit (fallback tak revert) dan front-running permit yang menggagalkan tx korban / nonce yang bisa dimacetkan (sebutan kehormatan OWASP 2026). Uji: jalur yang memanggil permit sebelum transfer — apa yang terjadi bila permit sebenarnya tidak ada/gagal/setengah jalan?
- **P-25 Transient storage (EIP-1153)** — nilai tstore hidup lintas callback dalam satu tx: residu terbaca kontrak lain (SIR.trading ±$355 rb), guard dengan slot tulis/baca tak cocok = kunci yang tidak mengunci (temuan CodeHawks), dan bug kompiler via-IR SOL-2026-1 untuk delete pada variabel transient (solc 0.8.28–0.8.33). Uji: petakan semua tstore/tload per slot + siapa bisa membaca residunya.
- **P-26 Delegasi EIP-7702** — asumsi "EOA tak bisa berkode" runtuh: extcodesize/tx.origin sebagai gerbang EOA kini bisa dilewati delegasi; otorisasi chain_id=0 replay lintas rantai; storage EOA persisten antar re-delegasi → tabrakan slot; protokol yang mengoperasikan EOA terdelegasi mewarisi bug delegate-nya. Jangkar: Fusion by IPOR $336 rb (Jan 2026, kasus tingkat-protokol pertama terkonfirmasi).
- **P-27 Hook pihak ketiga (Uniswap v4)** — PoolManager hanya menjamin invariant settlement, BUKAN logika aplikasi hook: pembuatan pool permissionless, cek pemanggil yang hilang pada callback hook, dan tanda/pembulatan delta custom-accounting adalah permukaan nilai. Jangkar: Cork ±$12 jt, Bunni $8,4 jt (keduanya BUKAN bug inti v4); katalog 7 pola gagal Trail of Bits.
- **P-28 Ambang verifikator pesan lintas-rantai** — kekuatan bridge = konfigurasi kuorum verifikatornya, bukan merek teknologinya: DVN 1-of-1 (KelpDAO ±$292 jt, Apr 2026), root batch yang bisa ditimpa relayer (zkLink ±$783 rb). Aturan buruan baru: untuk setiap jembatan/OFT, baca konfigurasi verifikator LIVE (berapa-dari-berapa, siapa) sebelum membaca kode verifikasinya.
- **P-29 Squatting & metamorfik CREATE2** — persetujuan token ke alamat yang belum ter-deploy lalu kode jahat dipasang di alamat itu (±$60 jt operasi pencurian); kontrak proposal diganti via CREATE2+SELFDESTRUCT setelah disetujui (Tornado Cash governance 2023). EIP-6780 mempersempit, bukan menghapus. Uji: persetujuan/alamat masa depan yang diasumsikan "akan berisi kode baik".
- **P-30 Kesalahan fee & drift imbalan** — keluarga akuntansi tersendiri (bukan pembulatan murni): basis fee salah, fee diambil dari pokok yang salah, imbalan mengakru pada penyebut basi. Bukti frekuensi: diterima 50% dari 109 submisi kontes — volume tinggi, jarang masuk daftar top-10.
- **P-31 Reset state pada klaim sebagian** — klaim parsial yang tidak mereset/menandai state dengan benar → sisa bisa diklaim ulang atau klaim berikutnya mewarisi status basi. Saudara sekuensial K-06 (yang lintas-jalur); yang ini DALAM satu jalur. Contoh berkategori: penebusan menguras CDP sehat (Badger), akuntansi vault basi → likuidasi prematur (BlueBerry), utang macet persisten dari pemotongan (Isomorph).
- **P-32 Token tak kompatibel di pasar lending** — rebasing & fee-on-transfer mengubah saldo tanpa transfer yang terlihat akuntansi internal; pasar yang mengasumsikan 1 token masuk = 1 kredit akan bocor/desync (contoh temuan: rebasing di Abracadabra). Catatan scope: di sebagian program kelas ini dinyatakan tidak didukung (Enzyme) — sebagai POLA tetap dipetakan; keputusan lapor mengikuti scope program.
- **P-33 Asumsi aktor tepercaya** — volume submisi kontes TERBESAR (311; diterima 51%): setiap peran tepercaya (curator, operator, relayer, bot, keeper) adalah klaim keamanan yang harus dibuktikan batasnya — apa yang bisa dilakukan peran itu bila jahat/dikompromikan, dan apakah batas itu sesuai yang diasumsikan desain. Enumerasi peran + batas bukti per peran kini langkah wajib Fase 1.

### Setoran uji ulang 2026-11-04 (Origin/Lista/Alchemix dengan lensa gelombang-2)
- **P-23, pelajaran kalibrasi (dari Lista, LIVE)**: toleransi basi oracle HARUS melebihi heartbeat feed-nya, jadi setiap feed ber-heartbeat panjang membawa jendela basi struktural sebesar toleransinya (USDT di ResilientOracle Lista: 86.700 dtk vs 360 dtk aset lain, karena heartbeat Chainlink USDT/BSC = 24 jam). Aturan buruan: bandingkan toleransi vs heartbeat PER ASET; outlier toleransi = tempat kelas ini tinggal. Eksploitasinya hampir selalu mensyaratkan kegagalan feed eksternal → biasanya observasi, bukan temuan — tetapi ukur dan catat selalu.
- **P-23/P-28, pelajaran negatif (dari Origin)**: kelas bisa gugur karena TIDAK BERLAKU secara struktural (slot priceProvider vault Origin sudah deprecated — tak ada feed di jalur nilai). Buktikan ketidakberlakuan dari kode+live, jangan hanya menyatakan "tidak ditemukan".
- **P-33, pelajaran bukti (dari Alchemix)**: enumerasi peran belum selesai sampai jenis pemegang peran dibuktikan on-chain (admin kedua instance = Gnosis Safe 3-dari-7, terbaca dari getThreshold/getOwners) — "admin adalah multisig" adalah klaim yang harus dibaca, bukan diasumsikan.

- **P-34 Pemisahan utang-kas via pinjaman terdelegasi (borrowBehalf) + panen persetujuan tepat waktu** — fungsi pinjam-atas-nama memisahkan DUA hal yang biasanya satu: utang menempel di pemberi delegasi, kas mengalir ke pemanggil. Satu persetujuan delegasi + allowance token dari pemegang dominan = pengambilalihan posisi penuh tanpa menyentuh kunci privat. Jangkar terverifikasi uji kontrol Venus THE (Mar 2026): korban memegang 84,24% pasokan pasar + utang berjalan; persetujuan delegasi & allowance tak terbatas diberikan 13 blok (±6 detik) sebelum serangan — prasyaratnya TEMPORAL, tidak terlihat pada audit state sebelumnya. Aturan buruan: (1) setiap permukaan delegasi/allowance dari pemegang dominan adalah permukaan serangan kelas-satu, sejajar bug kode; (2) pertanyaan "siapa yang mau menyetujui penyerang" DILARANG membuang hipotesis — jawabannya adalah peristiwa sosial (phishing/alat palsu) yang tidak bisa diramalkan dari kode, tetapi BISA dideteksi real-time: persetujuan baru dari pemegang dominan ke alamat segar/tanpa kode = sinyal kritis.
- **P-35 Settlement mengukur saldo, bukan transfer (balance-delta settlement)** — di AMM singleton yang `settle`-nya mengkredit `balanceNow − reservesBefore`, *setiap* kenaikan saldo tanpa transfer menjadi kredit yang bisa ditarik: rebasing, akrual bunga aToken, donasi ke kontrak underlying, airdrop ke alamat pool. Serangan butuh (1) kenaikan mendarat antara sync dan settle dalam satu unlock, (2) pemicu permissionless atau timing yang bisa dikontrol penyerang. Disproof termurah: (a) cek dokumentasi ("not supported" → hampir pasti ditolak), (b) ukur saldo on-chain pool atas token itu, (c) hitung gain maks = saldo × rate × staleness indeks maks — bila di bawah gas, GUGUR. Jangkar: Uniswap v4 K-1 (terbukti fork 13/13, 2026-11-16) — stETH 129,83 di PoolManager tapi rebase oracle-gated; aToken total ~$11,3 rb, gain terbaik ~$0,0033 → GUGUR sebagai laporan, pola tetap valid.
- **P-36 Deployed-vs-repo drift pada fork yang diaudit** — selalu verifikasi versi DEPLOYED (getRevision / Sourcify / diff token-vs-tag) SEBELUM memakai repo sebagai ground truth: repo Spark HEAD mengandung v1.1.0 sementara deployed adalah pra-v1.1.0. Diff token-level (strip whitespace/komentar) deployed vs tag fork-base mengisolasi delta fork dengan tepat — di Spark hanya Jan-10 patch + getReservesCount + revision bump + satu rename konstanta error. Bila deployed = upstream murni + patch kecil yang terdokumentasi, permukaan bug BARU praktis hanya ada di kode khas-fork (oracle/strategi/automator) — alokasikan waktu ke sana. Fix upstream yang sudah publik (v1.1.0, 27 hari) hampir pasti known-issue di triase — kuantifikasi dulu, laporkan hanya bila dampak material & bukan sekadar delta yang sudah diperbaiki. Jangkar: audit Spark 16 Nov 2026 (24/24 file logika inti token-identical dengan Aave v1.19.2; spot-check koordinator 2/2).
- **P-37 Konfigurasi yang di-append di calldata tanpa ikatan pemanggil (config-injection via EIP-1271)** — singleton yang membaca konfigurasi kritis-keamanan (kunci, verifier, parameter) dari calldata yang di-append proxy tepercaya bisa dipalsukan kapan pun SIAPA PUN bisa memanggilnya langsung dengan calldata yang dikontrol penyerang. Jalur EIP-1271 contract-signature adalah vektor pengiriman: kontrak owner Safe menerima byte `contractSignature` yang sepenuhnya dikontrol penyerang (bagian dari `signatures` yang disubmit), jadi bila singleton itu sendiri adalah owner, penyerang meng-append konfigurasinya sendiri dan menandatangani dengan kuncinya sendiri. Cek panjang/batas pada encoding signature bisa dilewati dengan menggelembungkan panjang dinamis yang dideklarasikan untuk menutupi byte yang di-append (kontennya hanya di-hash, tidak pernah di-parse). Uji: (1) jadikan singleton owner di fork; (2) submit contract signature dengan config penyerang + panjang yang digelembungkan; (3) buktikan kontrol proxy-owner gagal. Perbaikan: tegakkan invarian proxy-only di kode (guard delegatecall-only — preseden MultiSend: `address(this)` harus berbeda dari alamat singleton itu sendiri), bukan hanya di docstring. Preseden: singleton passkey Safe v0.2.1 (K-S1, terbukti fork 2026-11-16, nol target live). Pelajaran: docstring MUST yang tidak ditegakkan kode BUKAN batas keamanan — verifikasi invarian ditegakkan, bukan hanya dinyatakan.
- **P-38 Settlement nominal-saja tanpa rekonsiliasi saldo (varian jembatan optimistis)** — di jembatan intent-based yang spesifikasi settlement-nya menghitung repayment/refund/running-balance murni dari nominal event — tidak pernah mengecek saldo token aktual — token apa pun yang jumlah terkirimnya ≠ nominal (FoT, OApp yang memungut fee, rebasing, dust-removal) merusak settlement bukan dengan pencurian melainkan dengan **leaf-bricking**: amountToReturn > saldo aktual → eksekusi refund-leaf revert selamanya → semua refund dalam leaf itu (repayment relayer + refund depositor untuk token/rantai itu dalam bundle itu) terdampar permanen; shortfall disosialisasikan ke LP via utilizedReserves yang overstated. Pertahanan sepenuhnya off-chain (allowlist token admin + vetting dataworker); on-chain tidak ada cek saldo. Deteksi: (1) baca spesifikasi settlement untuk cek saldo (UMIP-179: tidak ada); (2) enumerasi token live yang dikonfigurasi/disetel dan cek masing-masing untuk perilaku transfer non-standar; (3) bila semua standar → mechanism-only, nol target live. Berbeda dari P-35 (settlement balance-delta — tentang *memakai* delta saldo): ini tentang *ketiadaan* rekonsiliasi saldo dalam sistem nominal-event. Jangkar: Across H-F (2026-11-16) — 4 token live standar; ditutup out-of-scope/admin-gated.
- **P-39 Jumlah yang di-attest depository vs jumlah event Transfer (oracle mempercayai event token itu sendiri)** — di jembatan intent-based, oracle off-chain sering meng-attest jumlah deposit dari event `Transfer` token itu sendiri (bukan event kontrak deposit, bukan balance-delta). Implikasi: (a) FoT net-logging → attestasi konsisten; (b) FoT gross-logging → over-mint; (c) token jahat bisa memalsukan event Transfer untuk mencetak saldo tanpa backing — tapi ekstraksi butuh depository memegang token yang sama dari pengguna lain ATAU likuiditas DEX untuk token palsu itu. Uji: (1) baca attestor — event mana sumber jumlahnya? (2) enumerasi token yang benar-benar dipakai live (bukan hanya "didukung"); (3) bandingkan totalSupply Hub vs saldo depository per tokenId — shortfall adalah signaturenya. Jangkar: Relay K-5 (2026-11-16) — attestor EVM memakai `Transfer.amount`; 297 token Hub, nol FoT live; semua major depository ≥ supply Hub. Status: mekanisme terbukti, nol target live di Relay.
- **P-40 NatSpec deployed vs NatSpec repo (P-36 untuk dokumentasi)** — diff deployed-vs-repo WAJIB mencakup KOMENTAR/NatSpec, bukan hanya kode: tim bisa menghapus disclosure keamanan dari NatSpec deployed (Relay Executor: disclosure front-running hanya ada di repo HEAD) ATAU membuat klaim keamanan yang lebih kuat di NatSpec deployed yang tidak ditegakkan kode (Relay BasicCallResolver deployed: "no funds can actually be stolen" — salah untuk leftover antar-eksekusi). Klaim deployed yang dilanggar implementasi lebih kuat daripada limitasi yang didokumentasikan dengan jujur. Jangkar: Relay (2026-11-16) — 16 source Blockscout terverifikasi vs repo HEAD; 5 identik, 10 diff kecil, 1 semantik (removeSource).
- **P-41 Migration-husk diamond (post-reseed scope drift)** — setelah migrasi L1→L2, alamat L1 yang terkenal bisa berupa husk yang facet-nya sudah dicopot (Beanstalk L1: 5 facet, `season()` hilang) sementara protokol yang hidup adalah diamond di chain lain yang di scope page hanya disebut "L2 Beanstalk". Selalu enumerasi facet live di SETIAP chain dalam scope sebelum mengalokasikan waktu audit; alamat terkenal bisa berupa cangkang hampir kosong dan permukaan sebenarnya tinggal di tempat lain. Catatan teknis: loupe Beanstalk hanya mengekspos `facets()` — `facetAddresses()` revert "Diamond: Function does not exist" — jadi enumerasi facet pakai `facets()` (0x7a0ed627), bukan `facetAddresses()`. Jangkar: Beanstalk BIP-50 Reseed, terverifikasi live 2026-11-16 (L1: 5 facet, season() revert; L2 Arbitrum: 31 facet, season 43,515). Catatan pendamping: fungsi issue reseed-merkle (`issueDeposits`/`issuePlots`/dll.) memakai flag sekali-pakai + receiver binding dengan total global yang pre-seeded — pertanyaan auditnya adalah apakah issuance per-akun bisa melampaui total global yang pre-seeded, dan apakah fungsi issue sibling sepakat soal overwrite-vs-accumulate (di sini deposits +=, plots overwrite — H-M2).

### Setoran Immutable zkEVM Bridge (2026-11-04)
- **Jembatan GMP (Axelar) vs jembatan merkle adalah dua keluarga berbeda**: verifikasi pesan GMP = validasi gateway vendor (commandId sekali-pakai) + pemakuan string sumber (chain+address) di adaptor + gerbang onlyAdaptor di bridge. Uji ketiganya sebagai satu rantai; titik lemah realistisnya adalah peran yang bisa mengganti string target (TARGET_MGR) — enumerasi pemegangnya adalah uji P-28 yang sebenarnya di keluarga ini.
- **Antrean penarikan ber-delay adalah kontrol, bukan bug**: pola finalise yang aman terbukti = entri di-delete SEBELUM transfer + penanda kosong diperiksa (indeks ganda revert WithdrawalAlreadyProcessed, teruji fork). Saat menilai antrean/vesting pihak lain, dua baris itu adalah cek pertama K-06/P-31.
- **Template clone yang terinisialisasi bukan temuan**: clone tidak mewarisi storage template; yang penting adalah siapa _bridge di CLONE yang hidup. Cek template hanya untuk memastikan bridge tidak pernah memakai template itu sendiri sebagai token.
- **Migrasi peran adalah peristiwa yang bisa dibaca**: pola sehat yang teramati dua kali (Origin & Immutable) — EOA deployer menyerahkan admin ke Safe dalam hitungan blok setelah init, lalu rotasi berkala via RoleGranted. Peta peran yang hanya membaca keadaan SEKARANG tanpa sejarah grant bisa salah menyimpulkan konsentrasi kekuasaan; baca event sejak blok init (blok init ditemukan via binary search nilai slot/getter, karena RPC umum membatasi rentang getLogs: drpc 10 rb blok, RPC zkEVM 5 rb blok — mevblockerRPC terbukti sanggup rentang penuh untuk Ethereum).

### Setoran Uji Kontrol Positif — Venus THE (2026-11-04)
- **Diff deployed-vs-HEAD adalah langkah wajib, bukan pelengkap**: repo Venus di HEAD SUDAH memuat perbaikan pasca-serangan (getCashPrior → internalCash "immune to donation attacks"). Berburu dari HEAD saja akan menyatakan target rentan-donasi ini BERSIH. Source yang dinilai selalu source yang ter-deploy pada blok acuan (Sourcify exact-match), dan selisihnya terhadap HEAD adalah peta tambalan — sekaligus peta lubang versi lama di tempat lain.
- **Donasi yang terikat CF<1 tidak bisa mencuri dari diri sendiri**: bila kapasitas pinjam naik hanya CF×pangsa×donasi dan agunan sejati yang disita selalu melebihi utang, rantai donasi murni PASTI mandek — tanyakan segera "neraca siapa yang menyerap rugi" (korban delegasi, antrean keluar, atau sosialisasi utang macet). Uji kontrol membuktikan amplifikasinya di fork (donasi 5 jt THE → likuiditas paus +$623.454, cocok teori CF×pangsa×D×harga dalam 0,02%) sekaligus membuktikan pinjaman $2 jt ditolak tepat di kapasitas.
- **Pangsa pasokan dominan adalah prasyarat kelas donasi**: pemegang 84,24% menangkap hampir semua nilai donasi; akun segar berpangsa 0,69% hanya menangkap remah. Sensus pemegang pasar (scan event Mint) adalah langkah Fase 1 untuk semua target lending berkode saldo-riil.

### Setoran Uniswap v4 (2026-11-16)
- **Konfirmasi P-32 (rebasing/FoT):** diperkuat — `settle` v4 adalah instans paling murni (nol pengecekan sumber kenaikan saldo).
- **Konfirmasi P-27 (hook return-delta):** diperkuat oleh T2a/T2b — akuntansi delta inti menegakkan konservasi (hook harus menyelesaikan deltanya sendiri; zeroing hanya mengalihkan pembayaran swapper ke hook, tidak menciptakan nilai).
- **Pelajaran harness:** router tes v4-core memiliki SATU posisi per (router, ticks, salt) — tes multi-LP WAJIB memakai salt berbeda per LP, atau `add` LP2 diam-diam mengoleksi fee LP1 (nyaris menyesatkan T5). Build v4-core penuh via-IR + 44M runs tidak praktis di VM ini (>55 mnt); pakai proyek Foundry terpisah dengan optimizer ringan + `allow_paths` (36 dtk, logika identik).
- **Pelajaran kalibrasi K-1:** mekanisme terbukti Critical-class bisa gugur DUA kali secara independen — terdokumentasi ("not supported") DAN tanpa target live (gain maks terukur ~$0,0033). Selalu ukur target live SEBELUM menulis laporan: saldo on-chain + rate + staleness = angka gain maks.

### Setoran Spark / SparkLend (2026-11-16)
- **Alamat dari memori adalah racun:** klaim awal "GNO tak ada source" salah karena alamat GNO diambil dari memori (0x9C58… adalah GNO di chain Gnosis; mainnet = 0x6810e776…). Alamat selalu dibaca dari sumber resmi/scope, bukan diingat.
- **Klaim "tanpa cek" harus dibuktikan dari kode, bukan dari absennya bacaan:** klaim awal "eMode switch tanpa cek HF" salah — HF divalidasi saat keluar eMode. Hipotesis negatif wajib dibuktikan dengan membaca jalur itu sampai tuntas.
- **Kuantifikasi debu membunuh kelas pembulatan:** pembulatan pra-v1.1.0 terkuantifikasi <$2e-7 total HF error; round-trip ≤1 wei/siklus butuh index ≥1,5 RAY vs live max ~1,24 → GUGUR dengan angka, bukan dengan intuisi.

### Setoran Safe (2026-11-16)
- **ERC-7579 TIDAK ada di halaman bounty → out of scope:** scope dibaca dari halaman program, bukan dari asumsi "Safe = semua produk Safe". Kode main-branch yang belum rilis (native P256 v==2, EIP-7702) juga out of scope karena tidak ter-deploy.
- **Teknik sekunder (catatan pengujian, bukan pola):** evaluasi Yul kanan-ke-kiri bersifat load-bearing untuk cek return precompile berbentuk `and(eq(returndatasize(),32), eq(mload(0),1), staticcall(...))` — verifikasi empiris dengan urutan valid-lalu-invalid dalam SATU call frame; guard `mstore(0, 0)` sebelum ekspresi membuat evaluasi kiri-ke-kanan yang hipotetis fail-safe (selalu false), bukan stale true.
- **Preseden misconfiguration-gated dibayar:** Safe #229 (self-owner) dibayar $5.000 Medium — temuan yang butuh misconfigurasi korban BUKAN otomatis ditolak; nilai laporan bergantung pada preseden program, bukan hanya pada ada/tidaknya target live saat ini.

### Setoran CoW Protocol (2026-11-16)
- **Pola revert-guard `simulateDelegatecall`:** entry delegatecall-arbitrer publik aman JIKA DAN HANYA JIKA (a) panggilan dalam selalu revert di akhir (semua perubahan state dalam frame di-rollback), (b) pasca-Cancun SELFDESTRUCT tak bisa menghapus host (EIP-6780), (c) host itu sendiri tak memegang hak istimewa (settlement BUKAN solver — terverifikasi on-chain). Ketiganya WAJIB dicek; hilangnya satu saja membuka jalur. Bukti: T1–T4 (pull relayer 100 ether dalam frame BERHASIL lalu di-rollback oleh revert).
- **Bentuk zero-order repeat-fill (konfirmasi, bukan baru — sudah di README CoW):** filledAmount maju sebesar jumlah yang dieksekusi; bila jumlah yang dieksekusi 0, filledAmount tak pernah maju sementara fee penuh ditarik tiap eksekusi. Batas eksak: repeatable hanya bila jumlah yang dilacak filledAmount adalah 0 (kedua jumlah 0; atau order BUY dengan buyAmount=0). Bukti: ZeroOrderTest (3 eksekusi menguras 3 ether fee, trader terima 0).
- **Gotcha layout storage slot ter-packing:** pada kontrak upgradeable dengan Initializable + variabel sendiri, Solidity mem-packing variabel base + derived ke satu slot — manager GPv2AllowListAuthentication ada di slot 0 offset 2, bukan slot 1. Selalu verifikasi layout dari source, jangan tebak slot.
- **Gotcha harness Foundry:** (a) Foundry 1.9 membuang remapping `src/`/`test/` yang bertabrakan dengan direktori proyek — pakai symlink ke clone; (b) `vm.prank` dikonsumsi oleh staticcall pertama yang dievaluasi sebagai argumen — resolve alamat SEBELUM prank.
- **Pelajaran scope CoW:** solver adalah pihak TEPERCAYA — setiap laporan harus menamai penyerang non-solver, yang menutup seluruh permukaan solver-jahat. CoW AMM TIDAK in scope; GPv2VaultRelayer bukan aset. Settlement hanya memegang ~$10rb debu; dana riil yang berisiko adalah allowance user ke relayer (agregat tak terukur tanpa indexer — catat sebagai unknown, jangan ditebak).

### Setoran Across Protocol (2026-11-16)

- **Observasi pendamping P-38 (bukan pola baru): "deposit tanpa gerbang + refund terjamin"** — deposit permissionless tanpa whitelist rute/token aman hanya karena jalur refund deposit kedaluwarsa (dari saldo SpokePool asal sendiri) tidak bergantung pada konfigurasi rute. Bila menilai deposit tanpa gerbang, pertama cek apakah jalur refund bergantung pada konfigurasi rute yang sama.
- **Repo relayer/dataworker HILANG (404 asli, bukan blokir IP):** `across-protocol/relayer` dan `relayer-v3` keduanya 404 (terverifikasi koordinator: 404 vs kontrol 200 untuk `across-protocol/contracts`). UMIP-157/179 dipakai sebagai pengganti spesifikasi yang ditegakkan disputer. Bila repo implementasi hilang, spesifikasi yang ditegakkan pihak ketiga (disputer) adalah ground truth berikutnya — tapi perilaku implementasi di luar spesifikasi itu tetap unknown dan WAJIB dicatat di unknown register.
- **Pelajaran toolchain RPC:** drpc kena 429 mid-task (hard stop dihormati; sisa kerja pindah ke publicnode). Limit getLogs drpc yang sebenarnya ~100 blok, bukan 10.000 seperti klaim pesan errornya — jangan percaya klaim limit dari pesan error provider.
- **Mekanisme counterfactual root-update adalah best-effort tanpa version gate on-chain** — root basi tetap executable sampai seseorang meng-update-nya (terdokumentasi; jendela dibatasi expiry signature). Saat mengaudit skema update best-effort, ukur jendela basi yang tersisa dan apa yang membatasinya.

### Setoran Relay (2026-11-16)

- **P-36 TERBUKTI BERHARGA:** tanpa diff deployed-vs-repo, K-2 + P-40 terlewat; repo HEAD saja menyesatkan — fix ada di repo tapi belum di-deploy (removeSource masih ada di IdempotencyStore yang ter-deploy).
- **P-28 TERBUKTI:** threshold 2-of-5, admin EOA, oracle V1/V2, pemegang role hanya bisa diketahui dari chain; klaim multisig di docs SALAH (admin segalanya = satu EOA 0xF61A305199fa1135d76FFaB3752D42F55cBd775A).
- **P-38 TERKONFIRMASI sebagai arsitektur di Relay** (attestasi berbasis event, tanpa balance-delta) — dengan nuansa P-39 bahwa sumber jumlah adalah event Transfer token.
- **Oracle address mismatch diselesaikan live:** docs mencantumkan V1 (0xd4b9…, tx terakhir 2026-07-24, mati); V2 (0xd180…) yang live. Jangan percaya alamat di docs tanpa cek aktivitas on-chain.
- **Pelajaran toolchain Relay Chain:** RPC lambat via proxy (cast ~3 dtk/call; curl mentah butuh timeout 120 dtk); Blockscout v1 module `proxy` disabled — pakai RPC langsung + API v2.
- **AccessControl non-enumerable:** daftar pemegang role hanya bisa dicek per-kandidat via `hasRole`, bukan enumerasi penuh — catat sebagai gap, bukan klaim lengkap.

### Setoran Beanstalk (2026-11-16)

- **Program PAUSED + vault $0 — prep-only, bukan "clean".** Status diverifikasi live dua kali + on-chain (vault 0 BEAN + 0 ETH). Jangan bakar jam audit di program tertutup; hasil prep adalah work list siap eksekusi untuk reopening (diff P-36 31 facet L2 + baca 26 laporan audit + 27 BIR, lalu H-M6/H-M8/H-M9/H-M10).
- **Reward limiter khusus Beanstalk:** untuk kontrak upgradeable/pausable hanya kerusakan serangan jam pertama yang dihitung — Beanstalk keduanya. **Pinto cross-exclusion:** submission valid yang memengaruhi Beanstalk dan Pinto dihitung known di program lain.
- **P-40 datapoint:** SDK vs UI tidak sepakat soal alamat Arbitrum Beanstalk Price (0xA560…D321 vs 0xC218…9E7) — salah satunya basi; alamat di docs harus diverifikasi live per file, bukan per repo.
- **Alamat dari memori adalah racun (konfirmasi Spark):** alamat L1 diamond yang "diingat" (…cB5624f0) SALAH; repo konsisten 27× menulis …db5624C5, dikonfirmasi live.
- **Scope page mengklaim 22 aset tapi hanya 12 dinamai** — 10 aset lainnya unknown terbuka; jangan klaim scope lengkap dari halaman yang tidak lengkap.
