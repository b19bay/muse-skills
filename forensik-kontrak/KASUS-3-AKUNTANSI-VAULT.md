# Bank Kasus 3 — Akuntansi Vault & Lending (13 kasus terverifikasi)

Bagian dari bank pola skill `forensik_kontrak` v2. Diteliti 2026-11-04 dari postmortem publik (BlockSec, Halborn, OpenZeppelin, ChainSecurity). Angka menurut sumber; catatan akurasi di akhir.

**1. ResupplyFi — 26 Jun 2025 — Ethereum — ≈ $9,6M**
Vault kolateral ERC-4626 yang baru ter-deploy dan nyaris kosong (cvcrvUSD) digelembungkan lewat donasi: penyerang mendonasikan 2.000 crvUSD langsung ke vault dan mencetak hanya 1 wei saham, membuat wei itu mengklaim seluruh saldo. ResupplyPair lalu menghitung exchange rate-nya sebagai `_exchangeRate = 1e36 / oraclePrice`; dengan harga termanipulasi > 1e36, pembagian floor integer meruntuhkan rate ke **0**, sehingga `_isSolvent()` mengembalikan true untuk utang berapa pun — 1 wei kolateral meminjam 10 jt reUSD.
*Tanda:* `exchangeRate = KONSTANTA / harga` dengan pembagian floor, TANPA cek kewarasan `require(rate > 0)`, dan `convertToAssets` kolateral yang dihargai dari `balanceOf(vault)` di pasar berlikuiditas nol.
Sumber: blocksec.com; openzeppelin.com; guardrail.ai.

**2. zkLend — 11–12 Feb 2025 — Starknet — ≈ $9,6M**
Di pasar wstETH yang kosong, penyerang memakai "donasi" flash loan (membayar fee menggelembung) untuk memompa `lending_accumulator` global. Matematika bakar-saham memakai pembagian terpotong: menarik 6,104 wstETH seharusnya membakar 1,5 unit `raw_balance` tetapi membulat ke bawah jadi 1,0, sehingga siklus deposit/withdraw berulang menumbuhkan `raw_balance` dari 4 → 1.724 — kolateral hantu lalu meminjam aset riil dari pool lain.
*Tanda:* `sharesBurned = withdrawAmount / accumulator` membulat ke bawah MENGUNTUNGKAN penarik; accumulator sendiri bisa digelembungkan donasi/flash loan dan pasar diluncurkan dengan likuiditas benih nol.
Sumber: halborn.com; hacked.slowmist.io; openzeppelin.com.

**3. Yearn yETH — 30 Nov 2025 — Ethereum — ≈ $9M**
Stableswap tertimbang kustom di balik yETH didorong keluar dari domain valid solver-nya oleh deposit tak seimbang sampai suku produk internal Π runtuh ke 0, mendesync supply tersimpan/balance virtual. Setelah menguras pool hingga supply internal terbaca 0 sementara saldo ERC-20 masih tersisa, penyerang masuk kembali ke jalur BOOTSTRAP (inisialisasi) dengan deposit debu 16 wei yang melanggar A·Σ ≥ D·Π; sebuah `unsafe_sub` underflow dan mencetak ~2,35×10^56 yETH, ditukar keluar via Curve/Balancer.
*Tanda:* aritmetika tak-tercek (`unsafe_sub`) di jalur mint + cabang bootstrap/deposit-pertama yang bisa dijangkau lagi kapan pun `supply == 0` tersimpan — pencetakan saham tidak terikat pada state valid invariant.
Sumber: blog.verichains.io; ringkasan postmortem Yearn (binance square).

**4. Sonne Finance — 15 Mei 2024 — Optimism — ≈ $20M**
Fork Compound V2; pasar VELO baru dibuat lewat transaksi proposal timelock yang BISA DIEKSEKUSI SIAPA PUN, menyisakan jendela di mana pasar ada dengan collateral factor terpasang tapi deposit nol. Penyerang mengeksekusi tx yang mengantre itu, mendonasikan ke pasar cToken kosong untuk menggelembungkan exchange rate turunan saldo, lalu meminjam terhadap kolateral debu dan menebus via cacat pembulatan fork-nya.
*Tanda:* `exchangeRate = (getCash() + totalBorrows − reserves) / totalSupply` dengan `getCash() = underlying.balanceOf(cToken)` — rate bisa dikendalikan donasi kapan pun `totalSupply ≈ 0`; deployment/penyemaian terpisah lintas transaksi.
Sumber: tokeninsight.com; bankless.com.

**5. Radiant Capital — 3 Jan 2024 — Arbitrum — ≈ $4,5M (1.900 ETH)**
Penyerang menyambar pasar USDC native yang BARU DIAKTIFKAN enam detik setelah deployment, menjadi pemasok pertama selagi `totalSupply = 0`. Dengan flash loan mereka memanipulasi `liquidityIndex` fork Aave; kesalahan pembulatan yang dikenal di `rayDiv` (pembagian presisi ray yang terpotong) membiarkan siklus deposit/withdraw berulang menggeser index jauh di atas nilai sebenarnya, mencetak saldo aToken menggelembung yang dipakai meminjam WETH pool.
*Tanda:* akuntansi saham berbasis index (`balance = scaledBalance × liquidityIndex`) di mana index bisa digerakkan depositor pertama di pasar yang belum terinisialisasi dan `rayDiv` membulat menguntungkan pengguna.
Sumber: blog.solidityscan.com; coinmarketcap.com.

**6. Hundred Finance — 15 Apr 2023 — Optimism — ≈ $7,4M**
Dua kontrak hWBTC ada; yang tak terpakai kosong. Penyerang flash loan ~500 WBTC, mendonasikan 200 WBTC ke kontrak hToken kosong itu sehingga `exchangeRate` (dihitung dari saldo kontrak mentah) meledak, lalu memakai ~2 wei hWBTC — kini "bernilai" seluruh pool pada rate palsu — sebagai kolateral untuk meminjam keluar pasar riil; kesalahan pembulatan `redeem` fork-nya (kehilangan presisi exchange rate pada supply kecil) juga membiarkan mereka memulihkan donasinya.
*Tanda:* `exchangeRateStoredInternal = (getCash() + borrows − reserves) / totalSupply` dengan `getCash() = balanceOf(this)`, tanpa dead shares, dan pemotongan pembagian di sisi redeem pada supply mendekati nol.
Sumber: blocksec.com; halborn.com.

**7. Onyx Protocol — 1 Nov 2023 — Ethereum — ≈ $2,1M**
Kelas Compound V2 yang sama: pasar oPEPE ter-deploy lima hari sebelumnya dengan likuiditas nol. Penyerang flash loan 4.000 ETH → PEPE, mendonasikan ke pasar kosong untuk menggelembungkan exchange rate-nya, meminjam aset riil dari pasar likuid terhadap oPEPE yang menggelembung, lalu menebus donasinya kembali keluar dengan mengeksploitasi isu pembulatan `redeemFresh` fork-nya yang sudah dikenal.
*Tanda:* cabang `totalSupply == 0 → initialExchangeRate` pasar kosong plus rate berbasis saldo sesudahnya; tanpa seed mint, tanpa kunci likuiditas minimum.
Sumber: defillama.com; merklescience.com.

**8. Midas Capital — 17 Jun 2023 — BNB Chain — ≈ $0,6M (DefiLlama mencatat $340rb)**
Fork Compound V2 (pasar LP HAY/BUSD) memakai library matematika pihak ketiga yang `divUInt`-nya terpotong. Penyerang memasok token LP, menebus hampir semuanya menyisakan ~1.001 wei cToken, lalu mendonasikan ~259.826 token LP untuk mendorong exchange rate ke ≈1.001; jumlah `redeemUnderlying` yang dibuat khusus, yang seharusnya membakar 1,9999… cToken, membulat ke BAWAH jadi 1 — membelah biayanya setiap putaran dan berlipat menjadi ~$600rb terekstrak.
*Tanda:* `redeemTokens = redeemAmount / exchangeRate` terpotong menguntungkan penebus, bisa dieksploitasi begitu donasi membuat 1 wei cToken ≈ klaim underlying yang besar.
Sumber: hacked.slowmist.io; olympix.ai; cointime.ai (SharkTeam).

**9. Raft Finance — 10 Nov 2023 — Ethereum — $6,7M R tercetak tanpa backing (≈ $3,3–3,6M bersih terekstrak)**
CDP fork Liquity (stablecoin R vs kolateral LST). Bug kehilangan presisi dalam pencetakan token saham posisi: cbETH flash loan 6.000 didepositkan/didonasikan sehingga konversi saham posisi memakai nilai index yang teramplifikasi, mencetak saham posisi ekstra bagi penyerang; saham itu membacking pencetakan 6,7 jt R tanpa backing. (Penyerang lalu membakar sebagian besar hasilnya — 1.570 ETH — lewat bug di kontrak eksploitasinya sendiri.)
*Tanda:* konversi gaya `sharesMinted = deposit × index / …` di mana index/harga saham dihitung dari saldo kontrak yang bisa dimanipulasi dan membulat menguntungkan pencetak — utang terbit terhadap saham yang tak pernah dibayar depositnya.
Sumber: cointelegraph.com; dlnews.com.

**10. Sentiment — 4 Apr 2023 — Arbitrum — ≈ $1M (~90% dikembalikan)**
Read-only reentrancy lewat Balancer: selama `exitPool` dengan payout ETH native, Vault Balancer mengirim ETH via `call` tingkat rendah SETELAH membakar BPT tetapi SEBELUM memperbarui saldo internal pool. Di fallback penyerang, `WeightedBalancerLPOracle.getPrice()` Sentiment membaca `Vault.getPoolTokens()` (saldo basi, masih penuh) dibagi `totalSupply()` BPT yang sudah berkurang — harga BPT yang sangat menggelembung yang dipakai penyerang meminjam ~$1M.
*Tanda:* harga kolateral = `Σ(saldoPool × harga) / BPT.totalSupply()` di mana pembilang dan penyebut DIBACA DARI DUA KONTRAK BERBEDA PADA MOMEN YANG TIDAK KONSISTEN; fungsi view bisa dipakai di tengah callback karena reentrancy guard tidak bisa memblokir panggilan `view`.
Sumber: postmortem resmi Sentiment (hackmd); cointime.ai.

**11. Balancer V2 (boosted pools) — diungkap 22 Agt 2023, dieksploitasi 27 Agt 2023 — Ethereum + sidechain — ≈ $2,1M total**
Kerentanan kritis di pool boosted V2 yang valuasi BPT-nya diturunkan dari exchange rate linear-pool/wrapper (`getRate()`) dan saldo internal; Balancer memitigasi ~99% TVL berisiko setelah pengungkapan tetapi tidak bisa mempause pool, dan penyerang menguras sisanya yang belum bermigrasi dengan flash loan lintas Ethereum, Fantom, Optimism.
*Tanda:* harga saham LP yang dibaca dari sumber rate live yang bisa dimanipulasi (`linearPool.getRate()` / rate wrapper tersimpan) alih-alih nilai akuntansi internal yang dicek invariant.
Sumber: hacked.slowmist.io; decrypt.co.

**12. Balancer V2 ComposableStablePools — 3 Nov 2025 — Ethereum + banyak chain/fork — ≈ $116–128M**
`ComposableStablePool` menimpa `_scalingFactors()` untuk melipat rate token (mis. wstETH/osETH ~1,058), tetapi `_upscale` masih memakai `FixedPoint.mulDown`: meng-upscale jumlah kecil (17 wei × 1,058 → 17,98 → terpotong ke 17) diam-diam menghapus seluruh premi rate. Pada swap GIVEN_OUT ini secara sistematis kurang menagih `amountIn`. Penyerang pertama-tama memakai `batchSwap` untuk menggerus saldo pool ke zona bahaya 8–9 wei, lalu merangkai puluhan micro-swap sehingga tiap pemotongan mencukur invariant (harga virtual BPT 1,027 → ~0,02), dan akhirnya swap kembali pada harga yang rusak.
*Tanda:* `_upscale(amount, rate)` membulat ke BAWAH (harusnya ke atas melawan pengguna) dengan faktor penskala non-uniter, tanpa ukuran swap minimum, dan primitif amplifikasi (`batchSwap`) yang membuat pemotongan selevel wei bisa diulang ratusan kali per tx.
Sumber: safestackai.com (ringkasan postmortem OpenZeppelin); github.com/adeshh/defi-hack-labs; openzeppelin.com.

**13. Morpho Blue / Morpho Vault V2 — kasus desain, 2024–2025 — Ethereum — tanpa kerugian terealisasi di core Blue (pola risiko, bukan kurasan)**
Pembuatan pasar Blue sepenuhnya tanpa izin — siapa pun bisa membuat pasar `(loanToken, collateralToken, oracle, irm, lltv)` dengan token kolateral terbitan sendiri yang tak bernilai dan oracle yang dikendalikan sendiri yang mengutip harga berapa pun. Ini aman di lapis core HANYA karena pasar terisolasi dan tak ada yang dipaksa meminjamkan ke dalamnya; risikonya berpindah ke siapa pun yang mengalokasi. Audit ChainSecurity atas Vault V2 (Critical CS-MORPHO-VLT2-016, "totalAssets Can Be Manipulated", diperbaiki pra-rilis) membuktikan mode gagalnya: buat pasar palsu dengan oracle termanipulasi, hadiahkan posisi supply raksasa ke MorphoBlueAdapter milik vault, lalu `forceDeallocate()` mendaftarkan posisi hantu itu dalam `assetsInMarket`, menggelembungkan `totalAssets` vault dan harga sahamnya.
*Tanda:* `totalAssets()` ERC-4626 yang menjumlahkan nilai posisi yang DILAPORKAN EKSTERNAL (`assetsInMarket[marketId]`) yang bisa didaftarkan pihak ketiga tanpa izin — solvabilitas vault mewarisi pasar terlemah yang bisa dibuat siapa pun.
Sumber: audit ChainSecurity (morpho-org/vault-v2); bestdapps.com.

## Sintesis keluarga
1. Setiap kasus berawal di batas akuntansi tempat **harga saham = aset ÷ supply dihitung dari input live yang bisa digerakkan penyerang** (saldo `balanceOf` mentah, accumulator/index global, `getRate()` pool) alih-alih buku besar internal yang tahan donasi.
2. Patahnya hampir selalu **keadaan kosong atau nyaris kosong** — pasar baru, `totalSupply` nol, saldo debu (8–9 wei) — tempat pembulatan dan pembagian per unit berhenti menjadi derau dan menjadi seluruh harga.
3. Langkah pembagian atau penskalaan **membulat menguntungkan pemanggil** (burn/mint/redeem terpotong ke bawah, `mulDown` pada upscale, rumus rate yang bisa runtuh ke 0) tanpa batas kewarasan (tanpa `rate > 0`, tanpa swap/deposit minimum, tanpa virtual shares/offset dead-share).
4. **Flash loan dan primitif komposabilitas** (batchSwap, callback, pembuatan pasar tanpa izin) memasok modal dan pengulangan untuk mengamplifikasi desync selevel wei menjadi kurasan penuh dalam satu transaksi.
5. Kerugian hanya menjadi nyata saat **sistem kedua memercayai angka yang rusak itu** — cek solvabilitas, peminjaman, `totalAssets` vault — jadi invariant yang diaudit bukanlah satu fungsi, melainkan setiap tempat saham/index/harga melintasi batas kepercayaan.

*Catatan akurasi:* tanggal terverifikasi Sonne = Mei 2024. Angka utama Raft $6,7M adalah R tercetak tanpa backing; nilai bersih terekstrak ~$3,3–3,6M. Kerugian Midas dilaporkan ~$600rb oleh PeckShield/SlowMist dan $340rb oleh DefiLlama. Estimasi Balancer Nov 2025 berkisar $116M–$128M antar pelacak.
