# Bank Kasus 1 — Reentrancy & Callback (14 kasus terverifikasi)

Bagian dari bank pola skill `forensik_kontrak` v2. Diteliti 2026-11-04 dari postmortem publik (rekt.news, CertiK, BlockSec, SlowMist, PeckShield, Immunefi). Angka = kerugian saat kejadian menurut sumber.

**1. The DAO — 17 Jun 2016 — Ethereum — ~$60M (3,6 jt ETH)**
Reentrancy satu-fungsi klasik: `splitDAO()` mengirim ETH lewat `createTokenProxy.value(...)` dan `payOut` SEBELUM menolkan `balances[msg.sender]`, `paidOut`, dan mengurangi `totalSupply`; fallback penyerang memanggil ulang `splitDAO` secara rekursif terhadap saldo yang belum diperbarui.
*Tanda di kode:* external call pembawa nilai di tengah fungsi, penulisan saldo/supply secara fisik SETELAH call — tanpa lock, tanpa CEI.
Sumber: coininsider.org; dev.to/pavelespitia analisis.

**2. Uniswap V1 × imBTC + Lendf.Me/dForce — 18–19 Apr 2020 — Ethereum — ~$232rb + ~$25M**
Reentrancy hook ERC-777 dua kali dalam 24 jam. Hook `tokensReceived/tokensToSend` imBTC menyala SELAMA `transferFrom`, menyerahkan eksekusi ke penerima sebelum korban selesai menghitung. Di Lendf.Me (fork Compound tanpa guard), penyerang supply imBTC lalu di dalam hook menarik/mensupply ulang sehingga catatan kolateral menggelembung jauh di atas token yang benar-benar dipegang, lalu meminjam keluar ~$25M aset lain.
*Tanda:* menerima token ber-hook (ERC-777) di kontrak TANPA `nonReentrant` di mana pun + update saldo setelah `transferFrom`; integrasi token yang mengasumsikan semantik ERC-20 murni.
Sumber: quantstamp.com; cryptonews.com; thedefiant.io.

**3. Akropolis — 12 Nov 2020 — Ethereum — ~$2M DAI**
Reentrancy lintas-fungsi lewat token PALSU: `SavingsModule.deposit()` tidak pernah memeriksa token yang didepositkan adalah aset terdaftar. Selama `transferFrom` token palsu, penyerang masuk kembali ke `deposit()` dengan DAI asli hasil flash loan; saldo pool sudah naik, sehingga saham pool dicetak dua kali terhadap satu deposit riil dan ditebus ganda.
*Tanda:* `deposit()` menerima token tanpa `require(token == registeredAsset)`; pencetakan saham diturunkan dari `balanceOf` pool yang diukur melintasi external call.
Sumber: securityaffairs.com; cryptobriefing.com.

**4. Grim Finance — 18–19 Des 2021 — Fantom — ~$30M**
`depositFor` membiarkan PENGGUNA memilih token deposit (dan penerima). Token jahat penyerang masuk kembali ke `depositFor` lima kali dari hook transfernya selagi deposit pertama masih diproses — lima deposit fiktif ter kredit. Auditnya mengklaim ada reentrancy guard padahal tidak ada.
*Tanda:* fungsi deposit dengan parameter alamat `token` dari pengguna + transfer-sebelum-kredit + guard yang DIKLAIM tapi TIDAK ADA — selalu verifikasi guard di kode ter-deploy, bukan PDF audit.
Sumber: cointelegraph.com; coindesk.com.

**5. Revest Finance — 27 Mar 2022 — Ethereum — ~$2M**
Reentrancy lintas-fungsi ERC-1155: `FNFTHandler.mint()` melakukan mint ERC-1155 — menyalakan `onERC1155Received` pada penyerang — SEBELUM menaikkan `fnftsCreated`, penghitung di balik `getNextId()`. Di dalam callback, penyerang memanggil fungsi saudara `depositAdditionalToFNFT` yang membaca ID berikutnya yang basi dan menimpa konfigurasi FNFT yang sudah tercetak (supply 7,7 jt, deposit 0) dengan jumlah deposit riil, lalu menarik backing-nya.
*Tanda:* penghitung/ID dinaikkan SETELAH mint yang menyalakan callback + fungsi kedua yang memercayai penghitung itu dan menulis config TANPA cek keberadaan — bentuk kanonis "jaga satu fungsi, tinggalkan saudaranya terbuka".
Sumber: rekt.news/revest-finance-rekt; blocksec.com.

**6. Rari Capital / Fei (Fuse) — 30 Apr 2022 — Ethereum — ~$80M**
Reentrancy lintas-fungsi lewat callback mata uang native: `cEther.borrow()` fork Compound mengirim ETH dengan `call{value}` SEBELUM mencatat saldo utang. Di `receive()`, penyerang memanggil `exitMarket()` — satu-satunya fungsi yang lupa dimasukkan patch keamanan Rari April 2022 ke dalam reentrancy lock — yang melepas kolateral USDC 150 jt sementara utang ETH-nya lenyap; diulang di 7 pool Fuse dengan flash loan.
*Tanda:* cakupan guard SEBAGIAN — grep kontrak yang terguard untuk satu fungsi pengubah-state yang KEHILANGAN `nonReentrant`; `call{value}` native dieksekusi sebelum penulisan utang.
Sumber: certik.com; traversa (paragraph.com).

**7. XCarnival — 26 Jun 2022 — Ethereum — ~$3,8M (3.087 ETH; ~50% dikembalikan)**
Patahan state basi lintas-fungsi (saudara reentrancy — bahkan tanpa callback): menarik NFT yang digadaikan (BAYC #5110) mengembalikan NFT-nya tetapi membiarkan record pledge/order tetap bisa dipakai, sehingga jalur borrow masih menerima NFT yang SUDAH ditarik sebagai kolateral. Penyerang mengayuh pledge → borrow → withdraw → re-pledge lintas banyak transaksi.
*Tanda:* jalur withdraw/pengembalian kolateral yang mentransfer NFT keluar TANPA menghapus/menandai mapping pledge yang dipercayai fungsi borrow — buru pembersihan state yang asimetris antar fungsi berpasangan.
Sumber: cointelegraph.com; coindesk.com.

**8. Omni — 10 Jul 2022 — Ethereum — ~$1,4M**
Reentrancy ERC-721 ganda lintas-fungsi: `executeWithdrawERC721` mengembalikan kolateral via `safeTransferFrom`, yang hook `onERC721Received`-nya menyala sebelum Omni membereskan posisi; dari hook itu penyerang masuk kembali (juga lewat jalur likuidasi yang tak terguard), meminjam wETH terhadap kolateral Doodles, dan utangnya terlupakan — NFT tertarik sambil pinjaman di tangan.
*Tanda:* `safeTransferFrom` di dalam fungsi withdraw/likuidasi tanpa lock dan penyelesaian state SETELAH transfer; dua pintu masuk tak terguard berbagi state posisi yang sama.
Sumber: immunefi.com (hack analysis); dailycoin.com.

**9. Midas Capital (pool Jarvis) — 15–17 Jan 2023 — Polygon — ~$660rb**
Read-only reentrancy + callback native: kolateral adalah LP Curve WMATIC-stMATIC yang dihargai dari pool selagi pool bisa berada di tengah `remove_liquidity`, dan — meski tim mengasumsikan pool semua-aset-terbungkus kebal — leg token native dikirim via `raw_call`, memberi jendela masuk-kembali `receive()` di mana penyerang meminjam terhadap posisi yang salah hitung (diperkuat flash loan).
*Tanda:* oracle LP-token dibaca dalam transaksi yang sama dengan penghapusan likuiditas; aset native ditangani raw call di dalam desain yang berasumsi "khusus ERC-20".
Sumber: defillama.com; cryptotvplus.com.

**10. dForce — 10 Feb 2023 — Arbitrum & Optimism — ~$3,65M (dikembalikan)**
Read-only reentrancy buku teks: `remove_liquidity` Curve wstETH/ETH mengirim ETH native keluar SEBELUM membakar token LP, sehingga selama fallback penyerang, `get_virtual_price()` — view murni — masih membagi dengan supply yang belum terbakar dan mengembalikan harga tertekan. dForce memakai view itu sebagai oracle dan membiarkan penyerang melikuidasi posisi pengguna lain pada harga palsu.
*Tanda:* pihak ketiga menghargai kolateral dari `get_virtual_price()`/state pool live selagi fungsi penarikan pool sendiri sedang terbang (transfer-keluar mendahului burn); fungsi yang rentan adalah `view` — TAK ADA lock yang bisa melindungi pembacanya.
Sumber: hacked.slowmist.io; arxiv.org/html/2408.14621; defillama.com.

**11. Sentiment — 4 Apr 2023 — Arbitrum — ~$1M (~90% dikembalikan)**
Read-only reentrancy lewat Balancer: selama `exitPool`, Vault mengirim ETH (fallback menyala) SEBELUM saldo internal pool diperbarui, sementara supply BPT sudah turun. Dari fallback, penyerang memanggil `borrow` Sentiment, yang menghargai kolateral LP Balancer via `Vault.getPoolTokens()` — saldo basi-tinggi terhadap supply yang menyusut — menggelembungkan nilai kolateral dan meminjam ~$1M kurang kolateral.
*Tanda:* logika borrow/likuidasi yang membaca `getPoolTokens()`/saldo AMM live, bisa dijangkau dari hook `receive()` selama alur exit AMM itu sendiri.
Sumber: cointime.ai (analisis QuillAudits); certik.com.

**12. Sturdy Finance — 12 Jun 2023 — Ethereum — ~$800K (442 ETH)**
Keluarga read-only reentrancy Balancer yang sama: oracle Sturdy menurunkan harga token pool B-stETH-STABLE dari state pool live; selama jendela exit yang dimasuki kembali, saldo tidak konsisten, harga BPT termanipulasi naik, dan penyerang meminjam 442 ETH terhadap kolateral yang terlalu tinggi nilainya.
*Tanda:* oracle = fungsi dari saldo pool Balancer live/`getRate` yang tetap bisa dipanggil dan dipercaya selagi pool berada di tengah join/exit.
Sumber: coinedition.com; cryptonews.net.

**13. Curve (compiler Vyper) — 30 Jul 2023 — Ethereum — ~$52M (PeckShield; ~$61,7M harga saat kejadian per tim risiko Curve DAO)**
Guard ADA di source dan ABSEN dalam efek: Vyper 0.2.15/0.2.16/0.3.0 mengompilasi dekorator `@nonreentrant('lock')` menjadi lock yang cacat, sehingga `remove_liquidity` di pool alETH/msETH/pETH/CRV-ETH bisa dimasuki kembali selama payout `raw_call` ETH native, berulang kali menarik terhadap saldo pool yang belum diperbarui; ~70% kemudian pulih/dikembalikan.
*Tanda:* proteksi reentrancy yang bergantung pada kebenaran TOOLCHAIN — buruan = periksa versi compiler (di sini header versi Vyper) pada kontrak mana pun yang satu-satunya pertahanan adalah dekorator/modifier, plus ETH dikirim sebelum burn LP di `remove_liquidity`.
Sumber: unchainedcrypto.com; coinlaw.io (mengutip LlamaRisk).

**14. Penpie — 3 Sep 2024 — Ethereum & Arbitrum — ~$27M**
Reentrancy lewat PASAR PALSU yang didaftarkan tanpa izin: `registerPenpiePool` menerima Pendle market apa pun, jadi penyerang mendaftarkan satu yang dibangun di atas token SY jahatnya sendiri. `batchHarvestMarketRewards()` TANPA reentrancy guard dan menghitung reward sebagai delta saldo yang diukur melintasi external call ke SY itu; selama panggilan harvest, kode penyerang masuk kembali ke `deposit()` dengan token LP flash loan, menggelembungkan saldo terukur di tengah jendela sehingga gelembung itu dibayar sebagai "reward" (wstETH, sUSDe, agETH, rswETH).
*Tanda:* akuntansi `balanceAfter - balanceBefore` yang melingkupi call ke kontrak eksternal yang bisa didaftarkan pengguna, pada fungsi yang kehilangan `nonReentrant` — grep pola pengukuran-delta di dekat fungsi registrasi/listing tanpa izin apa pun.
Sumber: audithub.dev; vietcardano.io.vn.

## Sintesis keluarga
1. Di setiap kasus, sebuah external call mencapai kode yang bisa dipengaruhi penyerang — hook token (777/721/1155), `receive()` atas nilai native, token pilihan pengguna, pasar yang didaftarkan pengguna, callback AMM — SELAGI buku korban masih di tengah pembaruan.
2. Invariant yang patah hampir selalu soal URUTAN: nilai dikirim, atau harga/saldo diukur, sebelum state yang membatasinya (saldo, utang, penghitung ID, record pledge, supply LP) ditulis atau dibersihkan.
3. Guard gagal tiga cara: absen total (DAO, Lendf.Me), ada di sebagian fungsi tapi tidak di saudara yang berbagi state (Rari `exitMarket`, Revest `depositAdditionalToFNFT`), atau secara struktural mustahil/rusak untuk jalur yang dipakai (oracle `view` tak terguard dalam read-only reentrancy; lock Vyper yang salah kompilasi).
4. Komposabilitas tanpa izin memasok senjata dan leverage: token/pasar arbitrer bisa diperkenalkan siapa pun, token LP berlipat ganda sebagai oracle live, dan flash loan membuat jendela di-tengah-terbang layak dikuras dalam satu transaksi.
5. Sinyal andal sang pemburu bukanlah "tidak ada `nonReentrant`", melainkan: TEMUKAN momen apa pun saat kontrak membaca state yang belum selesai ditulisnya selagi pihak luar memegang eksekusi — lalu periksa setiap fungsi lain yang berbagi state itu.
