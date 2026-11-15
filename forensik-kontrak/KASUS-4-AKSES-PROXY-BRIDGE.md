# Bank Kasus 4 — Access Control, Inisialisasi, Proxy/Upgrade, Arbitrary Call & Pemalsuan Pesan Lintas-Rantai (14 kasus terverifikasi)

Bagian dari bank pola skill `forensik_kontrak` v2. Diteliti 2026-11-04 dari postmortem publik (CertiK, SlowMist, Halborn, Chainalysis, OpenZeppelin).

**1. Poly Network — 10 Agt 2021 — Ethereum, BNB Chain, Polygon — ~$611M (hampir semua dikembalikan)**
`EthCrossChainManager` adalah OWNER dari `EthCrossChainData`, kontrak yang menyimpan kunci publik keeper tepercaya, dan executor lintas-rantainya menerima target kontrak dan nama metode PILIHAN pemanggil dari data pesan. Penyerang mem-brute-force string metode (`f1121318093`) yang selector 4-byte-nya bertabrakan dengan `putCurEpochConPubKeyBytes`, membuat manager memanggil kontrak data istimewanya sendiri dan memasang kunci penyerang sebagai keeper tunggal; sesudah itu ia menandatangani penarikannya sendiri.
*Tanda:* executor generik bisa memanggil kontrak saudara yang istimewa; tanpa daftar-tolak pada target/selector; kontrak yang mengeksekusi pesan lintas-rantai SENDIRINYA adalah owner/admin dari kontrak config yang bisa ditulis ulangnya.
Sumber: github.com/onchainattack/oak (T9.004); ponr.org.

**2. Wormhole (Portal) — 2 Feb 2022 — Solana ↔ Ethereum — ~$326M (120.000 wETH; ditopang Jump)**
Program Solana `verify_signatures` membaca hasil verifikasi tanda tangan via `load_instruction_at` yang terdepresiasi, yang TIDAK memeriksa akun yang dilewatkan benar-benar adalah sysvar instruksi. Penyerang memasok akun sysvar palsu berisi data fabrikasi "verifikasi secp256k1 berhasil", sehingga VAA (persetujuan guardian) palsu diterima dan 120 rb wETH tanpa backing tercetak — nol tanda tangan guardian asli.
*Tanda:* hasil verifikasi dibaca dari akun/objek PASOKAN pemanggil yang identitasnya (alamat/program/sysvar) tak pernah ditegaskan; loader tak-tercek yang terdepresiasi dipakai alih-alih varian `_checked`.
Sumber: nomoslabs.io; spark.money.

**3. Nomad — 1 Agt 2022 — Ethereum (bridge ke Moonbeam/Evmos) — ~$190M**
Upgrade rutin menginisialisasi root tepercaya/terkomit kontrak Replica ke `0x00`. Pesan yang belum terbukti juga secara default ber-root `0x00`, sehingga `acceptableRoot(0x00)` mengembalikan true dan `process()` mengeksekusi pesan penarikan yang sepenuhnya difabrikasi — tanpa bukti apa pun. Begitu publik, ~300 peniru me-replay calldata-nya dengan alamat penerima mereka sendiri.
*Tanda:* nilai sentinel/default (hash nol) berlipat ganda sebagai state valid setelah init/upgrade; `initialize()` memasang root kritis-keamanan ke nilai yang sudah dimiliki storage yang belum terinisialisasi.
Sumber: defi-intel.com; xemas.io.

**4. Qubit QBridge — 27–28 Jan 2022 — Ethereum → BNB Chain — ~$80M**
Saat `depositETH()` ditambahkan, jalur ERC-20 warisan `deposit()` tetap hidup, di mana alamat token aset native adalah `address(0)`. Handler memeriksa status whitelist dari *resourceID* (ETH = terwhitelist) tetapi tak pernah memvalidasi ulang alamat token; `safeTransferFrom` pada address(0) adalah panggilan ke akun tanpa kode yang berhasil secara hampa. Event `Deposit` terbit untuk 0 ETH aktual, dan 77.162 qXETH tercetak di BSC tanpa apa pun di belakangnya, lalu dipakai sebagai kolateral untuk menguras pool lending.
*Tanda:* pintu masuk paralel yang terdepresiasi untuk aset yang sama selamat dari refactor; bridge memercayai event yang terbit yang transfer di bawahnya adalah no-op (token == address(0), tanpa cek ukuran kode / delta saldo).
Sumber: certik.medium.com; slowmist.medium.com.

**5. Parity Multisig Library — 6 Nov 2017 — Ethereum — ~$150M BEKU (~513.774 ETH di 587 wallet)**
Semua wallet Parity adalah stub tipis yang mendelegatecall satu kontrak library bersama. Setelah perbaikan Juli 2017, `initWallet` diguard cek `only_uninitialized` pada storage PEMANGGIL — tetapi kontrak library-nya sendiri tak pernah terinisialisasi. Pengguna "devops199" memanggil `initWallet` langsung pada library, menjadi owner-nya, lalu memanggil `kill()`/selfdestruct, menghapus permanen kode yang digantungi setiap wallet.
*Tanda:* kontrak implementasi/library dibiarkan tak terinisialisasi — `initialize()` bisa dipanggil pada implementasi itu sendiri, bukan hanya lewat proxy; periksa slot owner implementasi LIVE, bukan hanya milik proxy.
Sumber: openzeppelin.com; smartcontractshacking.com.

**6. Ronin Bridge (Sky Mavis/Axie) — 23 Mar 2022 — Ethereum ↔ Ronin — ~$625M — *pola ops***
Penarikan butuh tanda tangan 5-dari-9 validator, tetapi Sky Mavis mengendalikan 4 validator sendiri, dan tanda tangan kelima (Axie DAO) bisa diperoleh via pengaturan RPC bebas-gas yang diberikan Nov 2021 dan TAK PERNAH DICABUT. Lazarus merekayasa sosial seorang insinyur senior (tawaran kerja palsu, PDF malware), mengekstrak 4 kunci Sky Mavis, dan mencapai ambang sepenuhnya lewat kompromi satu organisasi. Tanpa bug kontrak — kode berjalan persis seperti dirancang.
*Tanda:* ambang nominal ≠ ambang efektif: petakan siapa yang sungguh mengendalikan kunci penanda tangan dan buru delegasi/allowlist sementara yang basi dan tak pernah kedaluwarsa.
Sumber: spark.money; xemas.io.

**7. Harmony Horizon Bridge — 23 Jun 2022 — Ethereum/BNB ↔ Harmony — ~$100M — *pola ops***
Multisig bridge hanya mensyaratkan **2-dari-4** tanda tangan untuk menyetujui penarikan arbitrer. Penyerang (kemudian diatribusikan FBI ke Lazarus) mengkompromikan dua kunci privat dan cukup menandatangani transaksi penguras. Seorang peneliti telah memprediksi persis kegagalan ini secara publik ~3 bulan sebelumnya berdasarkan ambang yang terlihat.
*Tanda:* ambang on-chain yang begitu rendah (≤2) sehingga multisig adalah satu titik gagal; jumlah penanda tangan/ambang terbaca di kontrak vs nilai yang diamankannya.
Sumber: rya-sge.github.io; zircuit.com.

**8. Meter Passport — 5–6 Feb 2022 — Meter/Moonriver — $4,4M (plus ~$3,3M kerugian lanjutan di Hundred Finance)**
Fork Meter atas ChainBridge ChainSafe mengasumsikan deposit wrapped-native selalu tiba via `depositEth()`, yang memvalidasi `msg.value` terhadap jumlah yang diklaim. `deposit()` ERC-20 generik tetap bisa dipanggil publik dan TIDAK melakukan cek semacam itu — penyerang memanggilnya langsung dengan jumlah calldata arbitrer dan tanpa value terpasang, dan handler mengkreditkan/mencetak BNB dan WETH sesuai klaim.
*Tanda:* dua pintu masuk deposit publik untuk aset yang sama di mana hanya satu yang menegakkan `msg.value == jumlah`; kode fork yang asumsi kepercayaannya berlaku untuk jalur yang dimaksud tetapi tidak semua jalur yang bisa dijangkau.
Sumber: halborn.com.

**9. ChainSwap — 2 Jul & 10–11 Jul 2021 — multi-chain (20+ proyek terdampak) — ~$8M (serangan kedua)**
Per investigasi ChainSwap sendiri, jalur terima lintas-rantai tidak memvalidasi secara ketat tanda tangan/otorisasi kuota pada kontrak chain target — penyerang bisa mengotorisasi penarikan memakai tanda tangan yang dibuatnya sendiri alih-alih milik set node yang berwenang, menguras pool token proyek lintas chain.
*Tanda:* fungsi mint/release menerima blob tanda tangan tanpa mengikatnya secara kriptografis ke set penanda tangan berwenang, chain sumber, dan nonce/kuota — hasil `ecrecover` dibandingkan dengan tidak ada apa pun (atau dengan nilai pasokan pemanggil).
Sumber: odaily.news; beincrypto.com.

**10. pNetwork / pGALA — 3 Nov 2022 — BNB Chain — ~$4,5M terkuras dari pool PancakeSwap; kerusakan >$25M kemudian diklaim**
pGALA memakai TransparentProxy yang `proxyAdmin`-nya dimiliki EOA — dan kunci privat owner itu BOCOR DALAM PLAINTEXT DI GITHUB (SlowMist). Kepemilikan proxyAdmin diam-diam berubah ~70 hari sebelum insiden, memberi pihak tak dikenal kendali upgrade atas kontrak token (mint sesuka hati). pNetwork menemukan pengambilalihan itu dan secara kontroversial white-hat-mint ~55,6 M pGALA sendiri untuk menguras pool lebih dulu.
*Tanda:* admin proxy adalah EOA polos alih-alih multisig/timelock; perubahan kepemilikan peran istimewa on-chain tanpa pengumuman; kunci deployment muncul di repo publik/berkas config.
Sumber: chaincatcher.com (ringkasan akar masalah SlowMist); htx.com.

**11. Socket / Bungee — 16 Jan 2024 — Ethereum + chain EVM — ~$3,3M dari ~230 wallet**
Route yang baru ter-deploy (live 3 hari) mengekspos `performAction`, yang melewatkan `swapExtraData` pasokan pemanggil ke low-level call yang dieksekusi kontrak token. Satu-satunya `require` memvalidasi SALDO HASIL swap, bukan OPERASI yang dilakukan. Penyerang mengenkode `transferFrom(victim, attacker, amount)` sebagai "swap", dan SocketGateway mengeksekusinya memakai approval berdiri (sering tak terbatas) milik pengguna.
*Tanda:* `bytes` calldata/target pasokan pengguna mencapai `.call` tanpa validasi — tanpa allowlist alamat target atau selector fungsi; `require` di dekatnya memeriksa pasca-kondisi, bukan panggilan itu sendiri.
Sumber: certik.com; veridise.com.

**12. LI.FI — 16 Jul 2024 — Ethereum, Arbitrum — ~$11,6M dari 153 wallet**
Facet Diamond yang baru ter-deploy (`GasZipFacet`, live ~5 hari) mengekspos fungsi deposit yang melakukan panggilan LibSwap ke kontrak arbitrer TANPA validasi allowlist (alamat target + selector fungsi yang disetujui) yang ditegakkan setiap facet saudaranya — kesalahan manusia tinjauan deployment. Penyerang memanggil `transferFrom` lewat Diamond terhadap wallet dengan approval tak terbatas.
*Tanda:* satu facet/route dalam sistem modular (Diamond) melewatkan cek allowlist yang dimiliki semua saudaranya; modul yang baru ditambahkan mewarisi seluruh permukaan approval historis dari kontrak bersama.
Sumber: cryptonews.com (postmortem LI.FI); solanacompass.com.

**13. Multichain (ex-Anyswap) — 6–7 Jul 2023 — Fantom, Moonriver, Dogechain — ~$126M — *pola ops***
Jaringan penanda tangan MPC yang "terdesentralisasi" dalam praktiknya dikendalikan satu orang: CEO Zhaojun pribadi memegang kunci MPC/akses server. Setelah ia ditahan Mei 2023, tim kehilangan akses ke kunci, dan ~$126M cadangan bridge ditarik ke alamat tak dikenal; protokol ditutup beberapa hari kemudian. (Secara luas dibaca sebagai kompromi kunci/kejadian orang dalam, tak pernah terpecahkan penuh.)
*Tanda:* pemasaran MPC/ambang vs kustodi kunci manusia tunggal; tanpa bukti on-chain atas kendali terdistribusi (aksi admin bisa ditelusuri ke satu operator); kehidupannya seluruh bridge bergantung pada ketersediaan satu orang.
Sumber: defillama.com; hoge.gg.

**14. THORChain (ETH Router/Bifröst) — 16 Jul 2021 (~$5M) dan 23 Jul 2021 (~$8M)**
Pengamat off-chain Bifröst THORChain memperlakukan event `Deposit` sebagai bukti nilai diterima — tetapi event bisa diterbitkan oleh kontrak router PALSU milik penyerang sendiri. Pada serangan 23 Jul, penyerang men-deploy router/vault tiruan, menghasilkan event deposit palsu dengan memo yang dibuat khusus, dan Bifröst mengkreditkan "deposit" itu, melepas aset riil dari vault Asgard asli sebagai "refund" untuk nilai yang tak pernah didepositkan (varian 16 Jul menaruh kontrak serang di depan router asli untuk memalsukan transfer ETH).
*Tanda:* pengkreditan berbasis event di mana alamat kontrak PENERBIT event tidak dipaku ke satu-satunya router sah; memo/data-return diparse sebagai instruksi tanpa memverifikasi identitas kontrak lawan; jalur refund membayar keluar terhadap klaim masuk yang tak terverifikasi.
Sumber: coindesk.com; quadrigainitiative.com; analisis Halborn.

## Sintesis keluarga
1. Setiap kasus menyusut menjadi keputusan otorisasi yang dibuat terhadap input yang dikendalikan penyerang, subjek yang salah, nilai default, atau set kunci terkonsentrasi yang terkompromi — verifikator memeriksa SESUATU, hanya tak pernah hal yang penting.
2. Jendela deploy/upgrade adalah zona ledakan: implementasi tak terinisialisasi (Parity, Nomad), kunci bocor saat deployment (pGALA), dan route/facet baru yang dikirim tanpa allowlist saudara (Socket 3 hari, LI.FI 5 hari).
3. Permukaan eksekusi generik — target + calldata pasokan pemanggil, dispatch metode berbasis string, varian `deposit()` warisan yang tersisa — mengubah kelalaian validasi satu baris menjadi privilese tak terbatas, karena kontrak pengeksekusi memegang dana terpool atau approval berdiri pengguna.
4. Pesan dan event diperlakukan sebagai fakta alih-alih klaim: VAA palsu, event deposit palsu, router/memo yang dipalsukan diterima tanpa mengikatnya ke chain sumber, kontrak sumber, set penanda tangan, dan pergerakan saldo aktual (Qubit, THORChain, Meter, Wormhole).
5. Desentralisasi nominal menyembunyikan sentralisasi efektif — 5-dari-9 berarti satu perusahaan plus delegasi tak dicabut (Ronin), 2-dari-4 adalah seluruh vault (Harmony), "MPC" berarti satu CEO (Multichain) — jadi buru GRAF KENDALI EFEKTIF dan izin basinya, bukan ambang yang dipasarkan.
