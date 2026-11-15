# Bank Kasus 2 — Manipulasi Harga/Oracle & Flash Loan (13 kasus terverifikasi)

Bagian dari bank pola skill `forensik_kontrak` v2. Diteliti 2026-11-04 dari postmortem publik (PeckShield, BlockSec, SlowMist, Immunefi, dokumen pengadilan CFTC). Angka menurut sumber yang dikutip.

**1. bZx (Fulcrum) — 14 & 18 Feb 2020 — Ethereum — ~$1M gabungan**
Serangan 1: flash loan dYdX memompa WBTC di Uniswap/Kyber dan bZx menyelesaikan posisi leverage penyerang terhadap harga pool yang termanipulasi. Serangan 2: sUSD dipompa ~2,5× di Kyber/Uniswap dan logika borrow bZx menilai kolateral sUSD penyerang pada harga spot itu — meminjam 6.796 ETH lalu gagal bayar.
*Tanda:* penilaian kolateral/penyelesaian margin yang memanggil harga spot satu DEX (`getReserves()`/kutipan swap) di dalam transaksi yang sama saat harga bisa digerakkan — `borrow()` memercayai harga tanpa TWAP, tanpa sumber kedua, tanpa batas deviasi.
Sumber: coindesk.com; theblock.co; ponr.org.

**2. Harvest Finance — 26 Okt 2020 — Ethereum — ~$24M**
Vault USDC/USDT Harvest menghargai deposit dan penarikan dari harga stablecoin seketika Curve Y Pool; penyerang memakai flash loan Uniswap $50M untuk berulang kali memiringkan Y Pool, mendeposit ke Harvest pada harga saham terdistorsi dan menarik pada harga sebenarnya, berputar ~30 kali dalam 7 menit.
*Tanda:* `deposit()`/`withdraw()` vault yang harga sahamnya = `pool.get_virtual_price` atau saldo spot yang dibaca live dari AMM eksternal di blok yang sama saat pengguna bertransaksi — tanpa jeda deposit/tarik, tanpa cap per-blok, tanpa TWAP pada rasio pool di bawahnya.
Sumber: coindesk.com; news.bitcoin.com.

**3. Cheese Bank — 6 Nov 2020 — Ethereum — $3,3M**
Cheese Bank menilai kolateral LP Uniswap V2 dari saldo/reserve ETH mentah pool; penyerang flash loan 21.000 ETH dari dYdX, mencetak LP CHEESE/ETH, lalu swap 20.000 ETH ke pool CHEESE yang kecil untuk menggelembungkan nilai terukur LP itu, menyegarkan oracle, dan menguras USDC/USDT/DAI lewat `borrow()` biasa.
*Tanda:* kolateral LP dihargai gaya `pair.balanceOf`/reserve — `(reserveETH × 2) / totalSupply` dari `getReserves()` live — dikonsumsi langsung oleh `borrow()`/`getBorrowLimit()`. Rumus harga LP apa pun yang membaca reserve kini (bukan invariant/`sqrt(k)`) adalah bug ini.
Sumber: peckshield.medium.com.

**4. Warp Finance — 17 Des 2020 — Ethereum — $7,76M**
Warp meminjamkan stablecoin terhadap kolateral LP Uniswap dan menghargai LP sebagai `(price₀·reserve₀ + price₁·reserve₁) / totalSupply` memakai saldo pool live; flash loan dYdX/Uniswap membiarkan penyerang menumpahkan ETH ke pool WETH/DAI, menggelembungkan saldo satu sisi sehingga "nilai" LP jauh melampaui nilai tebusnya, lalu meminjam $7,76M terhadapnya.
*Tanda:* `calculatePriceOfLP()` = Σ(balanceᵢ × priceᵢ)/totalSupply dengan `getReserves()` live (versi aman memakai invariant: `2·sqrt(k)·sqrt(priceRatio)/totalSupply`). Tanda bonus: harga token eksternal di-TWAP, tetapi SALDONya spot — komposisinya tetap bisa dimainkan.
Sumber: beincrypto.com; defillama.com.

**5. Venus (XVS) — 18–19 Mei 2021 — BNB Chain — utang macet >$100M (shortfall ~$77M menurut laporan protokol)**
Bukan bug kode — ekonomi: collateral factor XVS baru dinaikkan ke 80% selagi XVS diperdagangkan tipis; seekor whale memompa XVS ~$70 → ~$144 dengan pembelian pasar puluhan juta dolar (sebagian besar di Binance, yang dilacak oracle Venus), memasok ~2 jt XVS, meminjam ~4.100 BTC + ~14.000 ETH; saat XVS runtuh, kolateral tak bisa dilikuidasi ke pasar tipis dan protokol menelan shortfall.
*Tanda:* `collateralFactor` tinggi (≥60–80%) pada token governance SENDIRI atau aset apa pun yang harga oracle-nya bisa digerakkan dengan modal kecil relatif terhadap nilai maksimum yang bisa dipinjam; tanpa supply/borrow cap per pasar. Buru: `borrowCap = 0` (tak terbatas) + oracle yang mengikuti venue yang bisa dimanipulasi.
Sumber: quadrigainitiative.com; blog.upay.com.

**6. PancakeBunny — 19–20 Mei 2021 — BNB Chain — ~$45M**
Matematika pencetakan reward BUNNY menilai performance fee vault memakai harga spot dari pool PancakeSwap USDT/BNB dan BUNNY/BNB; penyerang mengambil 8 flash loan (total ~$707M), memiringkan reserve kedua pool, memanggil `getReward()`, dan rumusnya — melihat nilai fee semu yang raksasa — mencetak ~7 jt BUNNY dari udara tipis, lalu dibuang demi BNB.
*Tanda:* perhitungan `mint`/reward/fee apa pun yang mengonversi jumlah token pada harga AMM SPOT dari `getReserves()` dalam transaksi yang sama (di sini terutama pool PancakeSwap V1 yang terbengkalai dan nyaris kosong). Jika jumlah mint = f(rasio reserve), flash loan mengendalikan mint itu.
Sumber: merklescience.com; zipmex.com.

**7. Cream Finance — 27 Okt 2021 — Ethereum — ~$130M**
Cream menghargai token vault Yearn yUSD sebagai kolateral memakai `pricePerFullShare` vault itu sendiri (total underlying ÷ saham) — nilai buku yang sensitif donasi; dengan dana flash loan, penyerang meminjam nilai kolateral ~$2M, lalu MENTRANSFER langsung (mendonasikan) yUSD ke dalam vault, menggandakan `pricePerFullShare` secara atomik tanpa satu saham pun terbakar, dan meminjam seluruh aset Cream yang bisa dipinjam terhadap kolateral yang tergandakan.
*Tanda:* harga kolateral = `vault.getPricePerFullShare()` / `totalAssets()/totalSupply()` dari vault ala ERC-4626 yang `totalAssets()`-nya membaca `balanceOf(this)` mentah — harga apa pun yang diturunkan dari saldo kontrak sendiri yang bisa digelembungkan `transfer()` telanjang.
Sumber: github.com/onchainattack/oak (T9.001); quadrigainitiative.com; safeswap.online.

**8. Deus Finance (DEI) — 15 Mar 2022 (~$3M) dan lagi 28 Apr 2022 (~$13,4M) — Fantom**
`DeiLenderSolidex` membaca harga DEI langsung dari saldo token pasangan AMM USDC/DEI Solidly StableV1 (spot, tanpa TWAP); DEI flash loan membiarkan penyerang menggeser rasio pair, membuat pengguna tampak insolven pada harga palsu dan melikuidasi mereka (Maret), lalu menggelembungkan nilai kolateral DEI untuk meminjam dan menguras pool (April) — pola yang sama tak ditambal dua kali.
*Tanda:* `getPrice()` mengembalikan rasio reserve (mis. `balanceUSDC × 1e18 / balanceDEI`) dari satu pasangan AMM, dimasukkan ke `isSolvent()`/`liquidate()`/`borrow()`. Pasar lending yang cek likuidasinya membaca saldo pair live bisa dilikuidasi dengan flash loan sesuka hati.
Sumber: bigbullcrypto.com; hacked.slowmist.io.

**9. Inverse Finance — 2 Apr 2022 — Ethereum — $15,6M**
Kolateral INV dihargai oracle TWAP Keep3r atas pool SushiSwap INV/WETH — tetapi pool itu hanya berisi ~432 INV / 46 ETH, dan cacat sampling membuat TWAP 30 menit yang dimaksud efektif mencakup ~15 detik; penyerang membelanjakan ~300 ETH (tanpa flash loan) untuk mendorong INV >50×, memasang INV sebagai kolateral, dan meminjam 1.588 ETH, 94 WBTC, 39 YFI, ~$4M DOLA. (Pengulangan Juni 2022 memakai flash loan untuk menggelembungkan harga LP Curve.)
*Tanda:* TWAP yang jendela EFEKTIFnya runtuh (oracle hanya diperbarui/dicicipi saat seseorang memanggilnya, atau jendela ≪ jumlah blok yang dibutuhkan) atas pool berlikuiditas dua-digit ETH. Buru: parameter `period` vs jumlah observasi aktual, dan likuiditas pool < ~$1M di belakang TWAP apa pun yang memberi makan `borrow()`.
Sumber: sonicwallet.com; defillama.com.

**10. Beanstalk — 17 Apr 2022 — Ethereum — $182M (penyerang menyimpan ~$80M)** *(bersebelahan flash loan: governance, bukan harga)*
`emergencyCommit` mengeksekusi proposal apa pun yang memegang supermayoritas ⅔ Stalk setelah hanya 24 jam, tanpa jeda snapshot; penyerang flash loan ~$1M di Aave, mendeposit ke Silo LP Curve baru untuk merebut >78% Stalk selama satu transaksi, dan mengeksekusi proposal jahat (BIP-18, menunjuk kontrak yang belum ter-deploy saat proposal dibuat) yang menyapu aset protokol ke dirinya.
*Tanda:* kekuatan suara = deposit/saldo kini pada blok eksekusi; eksekusi `emergencyCommit`/jalur cepat tanpa timelock atau snapshot blok-lalu atas bobot suara. Governance mana pun tempat token flash loan bisa MEMILIH dan MENGEKSEKUSI dalam blok yang sama adalah bug ini.
Sumber: bleepingcomputer.com; hackenproof.com.

**11. Mango Markets — 11 Okt 2022 — Solana — ~$114M (~$67M dikembalikan via penyelesaian DAO)**
Mango menandai kolateral dan PnL perp ke oracle yang merata-rata harga MNGO di tiga venue tipis; Eisenberg memperdagangkan perp MNGO melawan dirinya sendiri dari dua akun dan membeli spot sampai MNGO naik ~$0,03–0,04 → ~$0,54–0,91 dalam ~30 menit, lalu memakai ~$423M KEUNTUNGAN PERP BELUM TEREALLYISASI pada harga oracle yang menggelembung sebagai daya pinjam untuk menguras setiap aset yang bisa dipinjam.
*Tanda:* `borrow()`/withdraw yang kredit tersedianya mencakup PnL belum terealisasi / nilai token referensi-diri yang ditandai ke oracle berlikuiditas rendah; tanpa borrow cap per pasar, tanpa batas posisi yang diskalakan ke likuiditas venue oracle. Jika menaikkan harga mark mencetak daya pinjam, penyerang mencetak kolateralnya sendiri.
Sumber: cftc.gov (keluhan Eisenberg); cryptotimes.io.

**12. BonqDAO — 1 Feb 2023 — Polygon — ~$120M nosional (hanya ~$1,7–1,85M benar-benar dicairkan — selisihnya sendiri pelajaran nosional vs terealisasi)**
Integrasi feed TellorFlex BonqDAO membaca `getCurrentValue` Tellor — harga TERAKHIR yang diserahkan, seketika, tanpa jendela sengketa/delay; siapa pun yang men-stake hanya 10 TRB (~$175) bisa `submitValue` harga WALBT arbitrer, jadi penyerang mendorongnya sangat tinggi, mencetak ~100 jt BEUR terhadap 0,1 WALBT, lalu mendorong harga mendekati nol dan melikuidasi 30+ trove pengguna lain.
*Tanda:* konsumen oracle yang memanggil `getCurrentValue()`/`latestAnswer()` pada oracle PELAPORAN TANPA IZIN (gaya Tellor/UMA) alih-alih bacaan tertunda waktu (`getDataBefore(timestamp - disputeWindow)`); tanpa batas kewarasan vs feed kedua. Jika orang asing bisa menulis harga yang dibaca `borrow()`-mu, di blok yang sama, itu bukan oracle — itu kolom input.
Sumber: blocksec.com; immunefi.com (hack analysis); beosin.com.

**13. Zunami Protocol — 13 Agt 2023 — Ethereum — ~$2,1M**
Harga token zETH/UZD Zunami dihitung dari saldo token mentah pool Curve; didanai flash loan Balancer, penyerang MENDONASIKAN token langsung ke kontrak pool, menggelembungkan harga berbasis saldo, lalu mencetak/menebus zStable terhadap harga palsu lintas dua transaksi dan keluar dengan ~1.152–1.179 ETH.
*Tanda:* keluarga yang sama dengan Cream (#7), satu tingkat lebih bawah: harga = f(`token.balanceOf(pool)`) atau exchange rate dari saldo live alih-alih invariant/akuntansi internal — penilaian apa pun yang bisa digerakkan `transfer()` tanpa izin ke alamat pool/vault. Donasi tidak boleh pernah mengubah harga yang dipercayai `mint()`/`redeem()`.
Sumber: decrypt.co; merklescience.com.

## Sintesis keluarga
1. **Satu angka yang bisa digerakkan, dikonsumsi secara atomik:** di hampir setiap kasus, satu harga — rasio reserve spot, `get_virtual_price`, `pricePerFullShare`, submisi oracle terakhir — sekaligus bisa dikendalikan penyerang dan dibaca oleh `borrow()`/`mint()`/`liquidate()` dalam transaksi atau blok yang sama.
2. **Asimetri likuiditas:** biaya menggerakkan sumber harga (pool tipis, token float rendah, stake pelapor $175, satu donasi) berorde-orde lebih kecil daripada nilai yang bisa diekstrak harga buruk itu; modal disewa via flash loan atau, seperti Inverse/Venus, hanya perlu besar selama beberapa menit.
3. **Harga turunan saldo adalah janji, bukan harga:** token LP dan saham vault yang dihargai dari `getReserves()`/`balanceOf`/`totalAssets()` live (Warp, Cheese Bank, Cream, Zunami) jatuh ke siapa pun yang bisa memiringkan saldo — lewat swap, penambahan likuiditas miring, atau donasi langsung.
4. **Rata-rata dan indireksi gagal saat salah konfigurasi:** TWAP berjendela runtuh (Inverse), harga TWAP dikali saldo spot (Warp), dan oracle optimistis yang dibaca tanpa delay sengketanya (BonqDAO) semuanya TAMPAK terpertahankan selagi tetap bisa dimainkan dalam satu blok.
5. **Pagar ekonomi yang hilang mengubah bug menjadi kurasan:** pinjam/pasar tanpa cap, collateral factor tinggi pada token terbitan sendiri atau tipis, dan tanpa circuit breaker deviasi berarti satu bacaan harga buruk bisa mengambil SEGALANYA (Mango, Venus, Cream) alih-alih irisan terbatas.
