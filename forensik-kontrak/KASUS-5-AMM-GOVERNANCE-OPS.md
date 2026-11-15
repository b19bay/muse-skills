# Bank Kasus 5 — Matematika AMM, Governance/Ekonomi & Kompromi Kunci/Ops (15 kasus terverifikasi)

Bagian dari bank pola skill `forensik_kontrak` v2. Diteliti 2026-11-04 dari postmortem publik (Halborn, Trail of Bits, OpenZeppelin, Elliptic/Chainalysis). Catatan akurasi: pencurian Wintermute terjadi 20 Sep 2022 (kuncinya DIBUAT Juni 2022 dengan alat yang cacat); Compound Prop 289 memindahkan $0 — dibatalkan dalam jendela timelock setelah negosiasi, $24–25M yang BERISIKO, bukan hilang.

## Grup 1 — Matematika AMM/DEX & invariant

**1. KyberSwap Elastic — 22 Nov 2023 — Ethereum + 5 chain — ~$48M penyerang utama (~$55M termasuk bot frontrun)**
Dua fungsi yang masing-masing benar tidak sepakat di batas tick: `calcReachAmount` (termasuk likuiditas reinvestasi) mengatakan swap TIDAK mencapai tick berikutnya, sementara logika langkah swap mengasumsikan harga akhir mendarat tepat DI tick — sehingga `updateLiquidityAndCrossTick` dilewati dalam perjalanan keluar tetapi dieksekusi dalam perjalanan masuk, menghitung ganda likuiditas satu posisi dan membiarkan penyerang menarik jauh lebih banyak daripada yang didepositkan.
*Tanda:* di kode CLMM, bandingkan predikat "akan-melintasi-tick" terhadap perhitungan jumlah/harga untuk langkah yang SAMA — tempat mana pun di mana reach-amount, target sqrtPrice, dan pembaruan delta-likuiditas memakai pembulatan atau input likuiditas yang berbeda adalah kandidat. Fuzz khusus untuk swap yang berakhir dalam ±1 wei dari batas tick.
Sumber: halborn.com; coinlaw.io.

**2. Cetus Protocol — 22 Mei 2025 — Sui — ~$223M (~$162M dibekukan/dipulihkan lewat voting validator)**
`checked_shlw` library `integer-mate` memakai ambang overflow yang salah, sehingga nilai tertentu >192 bit lolos cek dan lalu terpotong diam-diam pada `<< 64` (VM Move tidak abort pada overflow shift). Penyerang membuka posisi sempit pada rentang tick ekstrem dengan nilai likuiditas yang dibuat khusus; 1 token deposit dikreditkan sebagai likuiditas raksasa, lalu ditarik menjadi aset pool riil.
*Tanda:* audit PENJAGANYA SENDIRI, bukan hanya kode yang dijaga: pembungkus math `checked_*` buatan tangan, shift, atau cast pelebaran mana pun yang konstanta prasyaratnya tidak persis cocok dengan lebar bit target. Inventaris semua library math pihak ketiga sebagai kode in-scope — tiga audit melewatkan ini karena library diperlakukan tepercaya.
Sumber: hackenproof.com; stingrai.io.

**3. Balancer V2 Composable Stable Pools — 3 Nov 2025 — Ethereum + 8 chain EVM lain — ~$120–128M**
`ComposableStablePool` menimpa `_scalingFactors` untuk melipat rate tukar token, melanggar asumsi terdokumentasi pool dasar StablePool tentang faktor penskala uniter; `_upscale` memakai `mulDown` (pemotongan searah). Dengan menggerakkan saldo satu token pool ke ~8–9 wei via settlement tertunda batchSwap, penyerang membuat kesalahan pembulatan ~12,5% per operasi dan merangkai ~65 micro-swap untuk melipatgandakannya menjadi harga BPT terdistorsi.
*Tanda:* buru (1) fungsi penskala/rate yang ditimpa vs komentar kelas dasar yang memperingatkan untuk tidak melakukannya, (2) pembulatan yang selalu searah melintasi perjalanan pulang-pergi scale→compute→unscale, (3) absennya jumlah swap minimum / penjaga saldo debu. Matematika invariant apa pun yang berperilaku berbeda pada saldo <100 wei daripada saldo normal adalah bendera merah.
Sumber: safestackai.com; techtimes.com.

**4. Curve Finance pools — 30 Jul 2023 — Ethereum — ~$69M bruto (~$52M bersih setelah pemulihan whitehat)**
Bug compiler, bukan bug source: Vyper 0.2.15/0.2.16/0.3.0 mengalokasikan slot storage TERPISAH untuk lock `@nonreentrant` tiap fungsi alih-alih satu slot bersama, sehingga `remove_liquidity` bisa dimasuki kembali dari `add_liquidity` (dan sebaliknya) selama callback ETH, menghargai operasi LP pada state pool basi. Menimpa pool CRV/ETH, alETH, msETH, pETH serentak.
*Tanda:* toolchain adalah permukaan serangan. Untuk target apa pun: catat versi compiler persis dari metadata/bytecode dan silangkan terhadap daftar bug compiler yang dikenal. Di tingkat bytecode, verifikasi bahwa dua fungsi terguard benar-benar SLOAD/SSTORE slot lock yang SAMA — keberadaan `@nonreentrant`/`nonReentrant` di level source tidak membuktikan apa-apa.
Sumber: hacken.io; unchainedcrypto.com.

**5. Bunni V2 (hook Uniswap v4) — 2 Sep 2025 — Ethereum + Unichain — ~$8,4M**
Liquidity Distribution Function (LDF) kustom Bunni menyeimbangkan ulang setelah swap memakai akuntansi saldo idle-nya sendiri; kesalahan arah pembulatan membuat tiap swap/withdraw exact-input yang diukur cermat MENYUSUTKAN likuiditas aktif secara tak proporsional terhadap saham yang terbakar (saldo satu pool digerakkan 28 wei → 4 wei). Flash loan membiarkan penyerang mengulang 44 micro-withdrawal dalam transaksi atomik, melipatgandakan drift menjadi nilai yang bisa diekstrak — selagi setiap langkah tetap memenuhi invariant settlement PoolManager Uniswap v4.
*Tanda:* di kode hook/akuntansi kustom (terutama hook v4): terpenuhinya invariant AMM inti TIDAK memvalidasi buku besar internal hook. Cari saldo yang dipelihara hook dan diperbarui per-swap dengan pembagian integer, ambang yang memicu penyeimbangan ulang, dan matematika penarikan di mana `saham terbakar : aset keluar` bisa berdrift saat saldo didorong mendekati nol.
Sumber: blog.trailofbits.com; recap deecurity 2025.

## Grup 2 — Governance & ekonomi

**6. Beanstalk Farms — 17 Apr 2022 — Ethereum — kerugian protokol ~$182M (profit penyerang ~$76–80M)**
Penyerang flash loan ~$1M (Aave), mengonversi ke LP/Stalk Beanstalk untuk memegang >67% kekuatan suara selama satu transaksi, dan memanggil `emergencyCommit` — jalur yang membiarkan supermayoritas ⅔ mengeksekusi proposal SEKETIKA, tanpa timelock. Proposal "donasi ke Ukraina" (BIP-18/19) membawa sisipan yang mentransfer seluruh kolateral protokol ke penyerang; pinjaman dilunasi di tx yang sama.
*Tanda:* bendera merah governance dalam kombinasi: kekuatan suara di-snapshot pada/dekat blok eksekusi suara (bisa di-flash-loan), jalur eksekusi darurat/instan apa pun yang memintas timelock, dan payload proposal yang calldata tereksekusinya tidak terikat pada apa yang ditinjau pemilih. Hitung "biaya memperoleh saham pengesah selama satu blok" vs nilai treasury.
Sumber: hackenproof.com; cointelegraph.com.

**7. Build Finance — Feb 2022 — Ethereum — ~$470rb (160 ETH)**
Penangkapan oleh apati murni: seorang aktor mengakumulasi cukup BUILD untuk meloloskan proposal (pada percobaan kedua) yang mentransfer kendali kontrak token BUILD/otoritas mint ke dirinya — turnout hanya ~5.000 suara ya dari 130.000 supply (~3,8%), tanpa lantai kuorum, tanpa veto/timelock tinjauan efektif; penyerang juga menonaktifkan bot notifikasi proposal dan GitBook. Lalu mencetak >1 M BUILD, menguras treasury dan posisi LP.
*Tanda:* bandingkan kuorum/ambang terhadap TURNOUT AKTUAL historis, bukan total supply; periksa apakah governance bisa menyerahkan mint/kepemilikan kontrak token itu sendiri dalam satu proposal; periksa pemantauan/alerting atas proposal baru sebagai kendali riil (ketidakhadiran atau sabotasenya adalah bagian dari serangan).
Sumber: decrypt.co; wikipedia.

**8. Tornado Cash governance — 20 Mei 2023 — Ethereum — ~$1M terekstrak + pengambilalihan DAO total**
Kontrak proposal meniru proposal yang sebelumnya lolos tetapi berisi `emergencyStop()` + `SELFDESTRUCT`. Setelah voting lolos, penyerang menghancurkan kontrak dan men-deploy ulang kode BERBEDA pada alamat yang sama via CREATE2 (kontrak metamorfik), sehingga governance mengeksekusi logika yang tak ditinjau siapa pun; itu memberi penyerang 1,2 jt suara palsu vs ~700 rb yang sah, lalu menguras suara terkunci dari kontrak governance.
*Tanda:* kontrak target proposal apa pun yang berisi `SELFDESTRUCT`, bisa di-deploy ulang CREATE2, atau indireksi upgradeable/delegatecall berarti ALAMAT yang disetujui pemilih tidak terikat pada KODE yang akan dieksekusi. Verifikasi eksekusi proposal membaca codehash pada waktu eksekusi, atau bahwa target immutable/non-metamorfik. (EIP-6780 sejak itu menyempitkan, bukan menghapus, kelas ini.)
Sumber: web3isgoinggreat.com; fatso-blog (github).

**9. Compound — Proposal 289 / "Golden Boys" — Jul 2024 — Ethereum — $0 berpindah; ~$24–25M (499.000 COMP) berisiko, dibatalkan pasca-negosiasi**
Ekonomi, bukan teknis: whale "Humpy" menghabiskan berbulan-bulan mengakumulasi COMP dan delegasi lewat program insentif, lalu — pada percobaan ketiga, setelah dua penolakan — secara sempit meloloskan (682.191 vs 633.636) proposal yang mengirim 5% treasury ke vault goldCOMP yang dikendalikan multisig kelompoknya sendiri. Tanpa bug kode; pertahanan yang bekerja bersifat sosial: multisig komunitas mengambil Timelock Admin + penyelesaian produk staking yang dinegosiasikan sebelum timelock 2 hari kedaluwarsa.
*Tanda:* lacak konsentrasi delegasi dari waktu ke waktu (satu blok mendekati ambang lolos unilateral), proposal berulang dengan jumlah meningkat setelah penolakan, dan transfer treasury yang PENERIMAnya adalah multisig yang dikendalikan pengusul. Jendela timelock adalah satu-satunya jendela intervensi — periksa cukup panjang dan ada yang mengawasinya.
Sumber: bankless.com; web3isgoinggreat.com.

**10. Moola Market — 18 Okt 2022 — Celo — ~$8,4M (93,1% kemudian dikembalikan demi bounty)**
Pompa kolateral-diri tanpa eksploitasi kode: penyerang mendeposit 60 rb CELO, meminjam 1,8 jt token MOO milik protokol yang diperdagangkan tipis, lalu memompa harga oracle TWAP Ubeswap MOO dari $0,018 ke ~$5,60 dengan sisa CELO — dan memakai MOO YANG DIPINJAM itu sebagai kolateral untuk meminjam keluar ~$8,4M CELO/cUSD/cEUR. Harga kolateral ditetapkan oleh pasar yang bisa digerakkan peminjam dengan hasil pinjamannya sendiri.
*Tanda:* pasar lending mana pun di mana (a) token milik protokol/berlikuiditas rendah diterima sebagai kolateral, (b) harganya datang dari TWAP/spot on-chain dangkal yang bisa digerakkan peminjam, dan (c) tanpa borrow cap, mode isolasi, atau LTV yang disesuaikan likuiditas. Model: "bisakah penyerang meminjam aset X, memompa X, dan meminjam kembali terhadap X dalam satu putaran?" — jika ya, itu temuan bahkan dengan kode sempurna.
Sumber: cryptobriefing.com; bitcoinist.com.

## Grup 3 — Kompromi kunci / ops / frontend

**11. Bybit — 21 Feb 2025 — Ethereum (cold wallet multisig Safe) — ~$1,46–1,5 M, pencurian kripto terbesar dalam catatan (FBI mengatribusikan ke DPRK TraderTraitor/Lazarus)**
Penyerang mengkompromikan mesin seorang developer Safe{Wallet} dan menyuntikkan JavaScript jahat ke aplikasi web Safe yang di-host AWS, ditargetkan hanya aktif untuk wallet Bybit. Para penanda tangan (termasuk CEO) melihat transfer rutin cold→warm; payload yang benar-benar ditandatangani adalah delegatecall yang mengganti implementasi/logika Safe, menyerahkan kendali ke penyerang. Kunci dan kontrak Safe sendiri tak pernah terkompromi.
*Tanda ops/kepercayaan:* rantai verifikasi penanda tangan berakhir pada UI WEB yang merender data transaksi — tanpa perbandingan hash independen di luar jalur, tanpa clear-signing hardware wallet atas payload aktual, frontend vendor tunggal sebagai satu-satunya sumber kebenaran. Proses treasury mana pun di mana apa-yang-kamu-lihat dilayani aplikasi web pihak ketiga adalah bug ini.
Sumber: stingrai.io; coinchoose.com.

**12. WazirX — 18 Jul 2024 — Ethereum (multisig Safe via kustodi Liminal) — ~$235M**
Keluarga yang sama dengan Bybit/Radiant: ketidaksesuaian antara data transaksi yang ditampilkan di antarmuka Liminal dan payload yang benar-benar ditandatangani membiarkan penyerang memperoleh tanda tangan atas transaksi jahat yang meng-upgrade kontrak multisig dan mencabut perlindungannya, lalu menguras 200+ aset (~45% cadangan). Penyerang berlatih on-chain selama ~8 hari sebelumnya; diatribusikan ke Lazarus. (WazirX dan Liminal secara publik menyengketakan kesimpulan forensik — ketidaksesuaian tampil-vs-payload adalah keterangan laporan awal bursa itu sendiri.)
*Tanda:* kustodi terbelah dua organisasi (5 kunci WazirX + 1 Liminal, 4 dibutuhkan) di mana TAK SATU pihak pun secara independen merekonstruksi dan memverifikasi calldata mentah; whitelist/limit ditegakkan di lapis UI vendor alih-alih on-chain di kontrak wallet itu sendiri.
Sumber: wikipedia; rya-sge.github.io.

**13. Radiant Capital — 16 Okt 2024 — Arbitrum + BNB Chain — ~$50M**
Aktor DPRK UNC4736 menyamar sebagai mantan kontraktor tepercaya di Telegram dan mengirim ZIP yang PDF umpannya memasang backdoor macOS INLETDRIFT pada perangkat setidaknya 3 kontributor inti (ditanam 11 Sep 2024). Selama operasi rutin multisig Safe 3-dari-11, malware menampilkan transaksi jinak di frontend selagi hardware wallet mereka menandatangani payload `transferOwnership` di latar belakang, merebut kontrak lending di kedua chain.
*Tanda:* endpoint penanda tangan adalah perimeter: perangkat personal/kontraktor, pengiriman rekayasa sosial via aplikasi chat, ambang multisig rendah (3-dari-11) yang bisa dijangkau dengan mengkompromikan MINORITAS penanda tangan, dan tanpa syarat memverifikasi hash payload pada perangkat kedua yang bersih. Pola pendahulu Bybit, empat bulan lebih awal.
Sumber: defi-intel.com; itokenly.com.

**14. Wintermute — 20 Sep 2022 — Ethereum — ~$160M**
Alamat admin/operator DeFi Wintermute adalah alamat vanity (`0x0000000…`) yang dihasilkan Profanity, yang menurunkan kunci 256-bit dari ruang seed hanya 32-bit — bisa di-brute-force, sebagaimana diungkap publik oleh 1inch beberapa hari sebelumnya. Penyerang memulihkan kunci privat dan memakai privilese `setCommonAdmin` alamat itu untuk menguras ~90 aset. Wintermute sedang dalam proses mempensiunkan kunci itu, tetapi menurut CEO-nya, kesalahan manusia mem-blacklist kontrak yang salah, membiarkan admin yang terkompromi tetap aktif.
*Tanda:* alamat istimewa mana pun dengan awalan berpola/vanity patut dicurigai sampai alat pembuatnya terbukti sehat; pembuatan kunci berentropi lemah di mana pun dalam sejarah organisasi, dan rotasi kunci yang gagal/tak tuntas setelah pengungkapan publik. Tanyakan: "bagaimana setiap kunci owner/admin dibuat, dan apa runbook pemensiunannya?"
Sumber: beosin.com; coinchange.io.

**15. Ledger Connect Kit — 14 Des 2023 — supply chain JavaScript (dApp lintas chain EVM) — ~$600rb**
Seorang MANTAN karyawan Ledger yang akses npm-nya masih hidup ter-phishing; penyerang menerbitkan versi jahat `@ledgerhq/connect-kit` 1.1.5–1.1.7 yang menyematkan kit Angel Drainer. Karena dApp (SushiSwap, Zapper, Phantom, Balancer, Revoke.cash) memuat library dari npm/CDN tanpa versi terpaku yang dicek integritasnya, drainer dieksekusi di browser pengguna akhir dalam hitungan menit; jendela aktif ~2 jam.
*Tanda:* pipeline build/rilis adalah kunci penanda tangan: akses basi untuk mantan karyawan, tanpa persetujuan rilis 2-orang/berbasis hardware untuk paket yang dikonsumsi luas, dan dApp hilir yang menarik `latest` secara otomatis alih-alih versi terpaku dengan verifikasi SRI/lockfile. Satu akun maintainer = ribuan korban hilir.
Sumber: halborn.com; kryczkal/ethcannes2026 (github).

## Sintesis lintas grup
1. Kerugian tiap grup terkonsentrasi di tempat **komponen tepercaya dikeluarkan dari telaah**: library math (Cetus), fungsi dasar yang ditimpa (Balancer), versi compiler (Curve), buku besar sampingan hook (Bunni, Kyber), frontend vendor (Bybit, WazirX, Radiant), akun npm (Ledger).
2. Celah yang bisa dieksploitasi hampir selalu berada di **batas antara dua representasi dari hal yang sama** — reach-amount vs langkah swap, scale vs unscale, tx yang ditampilkan vs payload yang ditandatangani, kode yang ditinjau vs kode yang dieksekusi (CREATE2), harga spot/TWAP vs nilai kolateral.
3. Penyerang untung dengan **mengulang ketidaksesuaian kecil**: pembulatan 1 wei, saldo 8 wei, 44 micro-withdrawal, ~65 micro-swap — kesalahan satu-kali tampak seperti debu; tandanya adalah *bisa diulang searah*, jadi selalu uji input berukuran debu secara berputar, bukan hanya ukuran normal.
4. Mekanisme sah menjadi senjata saat asumsi keselamatannya bisa disewa atau menganggur: flash loan menyewa governance (Beanstalk) dan dampak harga (Bunni), turnout rendah menganggurkannya (Build, Compound), dan token pinjaman mengkolateralkan dirinya sendiri (Moola) — periksa siapa yang bisa *sementara* memenuhi setiap prasyarat.
5. Pertahanan berlapis gagal di tepat satu lapis setiap kali dan tak ada cek kedua yang independen — timelock, realisme kuorum, pengikatan codehash, verifikasi payload di luar jalur, dan limit on-chain (bukan UI) adalah kendali murah yang KETIDAKHADIRANNYA, terlihat di kode/config, itu sendiri adalah tanda forensik.
