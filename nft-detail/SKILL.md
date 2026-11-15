# Detail NFT

Skill ini melihat detail lengkap sebuah NFT dan pasarnya: metadata token, di marketplace mana saja ia dijual, floor koleksi, volume, penjualan terakhir, dan offer (tawaran beli) yang aktif. Gunakan skill ini saat pengguna meminta detail NFT, cek market sebuah koleksi, floor, volume, offer, atau "di mana saja dijual" untuk satu token atau satu koleksi.

Skill ini melengkapi, bukan menggantikan, skill serok: serok menandai listing yang salah harga, skill ini menampilkan detail pasarnya apa adanya, terverifikasi atau tidak.

## Tentukan target dulu

- Catat yang diperintahkan: chain, alamat kontrak, token id, atau alamat wallet kalau yang diminta adalah semua koleksi di wallet itu.
- Jangan bekerja hanya dari nama koleksi. Nama saja tidak cukup: banyak koleksi tiruan dan nama mirip di chain berbeda.
- Kalau alamat kontrak belum diketahui, ambil dulu dari sumber yang mengikat token itu, misalnya halaman token di block explorer (contoh: BscScan untuk BSC) lewat browser live, bukan dari hasil pencarian nama.
- Kalau kontrak tidak bisa dipastikan, laporkan detail itu sebagai tidak terverifikasi dan jangan tempelkan data koleksi lain yang namanya mirip.

## Ambil detail token

- Identitas: nama koleksi, nama token, token id, standar (ERC-721 / BEP-721 / ERC-1155), chain, alamat kontrak.
- Kepemilikan dan supply: pemilik saat ini kalau bisa dibaca on-chain, totalSupply dan supplyCap kalau ada, status mint (masih buka / sold out).
- Metadata dari tokenURI: traits, tier, rarity rank, reward kalau ada (contoh: token reward per mint), dan tautan gambar.
- Jangan laporkan token id dari simulasi atau preview sebagai token id final; token id final hanya dari receipt / ownerOf on-chain.

## Cek marketplace, di mana saja dijual

- Cek dulu marketplace resmi proyek itu sendiri, sebelum marketplace umum, karena koleksi baru sering hanya diperdagangkan di situsnya sendiri. Biaya marketplace di data resmi proyek adalah petunjuk adanya marketplace asli itu.
- Lanjutkan ke marketplace umum hanya dengan alamat kontrak yang sama, bukan nama saja.
- Untuk tiap marketplace, catat: nama marketplace, URL halaman koleksi/token, apakah token itu listed atau not listed, harga listing dan mata uangnya, dan apakah tombol buy aktif.
- Bedakan dengan tegas: listing adalah harga jual dari penjual, offer adalah tawaran beli dari pembeli. Jangan pernah melaporkan harga listing sebagai offer, atau sebaliknya.
- Catat juga cara jual marketplace itu kalau situsnya menyatakan: mata uang settlement, apakah NFT tetap di wallet penjual sampai terjual, royalti, dan biaya marketplace.

## Ambil floor, volume, dan penjualan

- Floor: harga listing aktif termurah di marketplace yang sama dengan listing yang dilaporkan, beserta mata uangnya. Jangan campur floor dari marketplace A dengan listing dari marketplace B.
- Volume: laporkan angka persis seperti sumbernya, beserta jendelanya (misalnya 24 jam, 30 menit terakhir, 1 jam terakhir, atau total). Kalau sumbernya tidak menyebut jendela, katakan tidak ada jendela. Jangan mengubah volume 24 jam menjadi volume 30 menit dengan membagi.
- Penjualan: last sale (token id, harga, mata uang, waktu), highest sale kalau ditampilkan, dan jumlah listing aktif.
- Kalau sebuah angka tidak ditampilkan di marketplace yang diperiksa, katakan tidak ditampilkan / tidak terverifikasi, dan jangan mengarangnya.
- Marketplace dinamis yang tidak bisa dibaca dari teks halaman saja harus dicek lewat browser live; kalau tetap tidak terbaca, laporkan sebagai tidak terverifikasi dari rute itu, bukan ditebak.

## Cek offer

- Untuk tiap token dan tiap koleksi, cek apakah marketplace itu punya fitur offer/bid sama sekali (misalnya tombol Make Offer, tab Offers).
- Kalau ada, catat offer aktif: token id yang dituju, harga offer dan mata uangnya, expiry kalau ditampilkan, dan sumbernya.
- Kalau tidak ada offer yang tampil, katakan tidak ada offer terverifikasi, dan sebutkan di mana sudah dicari (halaman koleksi, halaman token, tab Offers).
- Untuk token soulbound / identitas (contoh: Agent ID), floor dan offer tidak berlaku seperti koleksi dagang biasa; katakan itu dengan jelas, dan jangan menggantinya dengan floor produk lain yang mirip namanya.
- Jangan membuat, menerima, atau membatalkan offer tanpa persetujuan eksplisit pengguna untuk item dan harga itu.

## Watcher real-time

Skill ini juga punya mode watcher: memantau satu token atau satu koleksi secara berkala, dan memberi tahu begitu ada perubahan yang diperintahkan pengguna. Gunakan mode ini saat pengguna meminta "pantau", "watcher", "real-time", atau "kasih tahu kalau ada perubahan".

- Tanyakan dulu apa yang dipantau, karena watcher tanpa target yang jelas hanya membanjiri notifikasi: floor berubah, listing baru di bawah ambang tertentu, token tertentu jadi listed / tidak listed, offer baru, penjualan baru, atau volume melewati ambang.
- Catat ambang dan interval yang diperintahkan pengguna, misalnya cek tiap 60 detik, tiap 5 menit, atau tiap 1 jam. Jangan kunci interval ke satu angka.
- "Real-time" di sini berarti polling berkala ke marketplace yang sama, kecuali marketplace itu menyediakan websocket atau API streaming — kalau tidak ada, katakan itu dengan jelas, jangan klaim streaming padahal polling.
- Setiap cek harus membaca ulang data dari sumber aslinya (marketplace resmi dulu, lalu marketplace umum dengan kontrak yang sama), lalu membandingkan dengan snapshot sebelumnya dengan `~/workspace/custom-skills/nft-detail/scripts/watch.py`.
- Yang dianggap perubahan: floor naik/turun, jumlah listing berubah, harga listing termurah berubah, token yang dipantau berubah status listed, offer baru muncul atau hilang, dan penjualan baru tercatat. Perubahan harga karena kurs rupiah bergerak saja bukan perubahan pasar NFT, kecuali pengguna memang meminta pantau kurs.
- Kegagalan cek (halaman kosong, 502, Service busy, rate limit 429) bukan perubahan dan bukan bukti listing hilang: catat sebagai error, lanjutkan polling, dan jangan mengirim notifikasi palsu. Berhenti memanggil sumber itu setelah 429, sesuai batas layanannya.
- Notifikasi hanya berisi perubahan yang terverifikasi: apa yang berubah, nilai lama dan baru, mata uang, sumber, dan waktu cek. Jangan mengirim notifikasi untuk cek yang tidak berubah, kecuali pengguna meminta laporan berkala (misalnya tiap 5 menit) secara eksplisit.
- Watcher tidak boleh berhenti diam-diam. Pelajaran dari pemantauan sebelumnya: proses custom bisa mati karena restart VM, supervisor yang berhenti pada satu temuan lama, atau perintah yang menutup output watcher. Karena itu: jalankan watcher tanpa pipa yang menutup outputnya, simpan log dengan timestamp tiap cek, jalankan supervisor yang me-restart watcher kalau lognya basi lebih dari 2x interval, dan pasang cron sebagai cadangan pemulihan setelah VM berganti — cron itu yang me-restart watcher kalau lognya basi.
- Saat pengguna membatalkan pemantauan, hentikan watcher, supervisor, dan cron-nya, verifikasi ketiganya benar-benar berhenti, dan katakan itu dengan jelas. Jangan biarkan watcher berjalan setelah dibatalkan.
- Watcher hanya membaca dan memberi tahu. Ia tidak membeli, menawar, listing, atau menandatangani apa pun, dan tidak boleh memblokir atau menunggu balasan pengguna sebelum mencatat perubahan berikutnya, kecuali pengguna memerintahkan sebaliknya untuk satu aksi tertentu.

## Konversi ke rupiah

- Kalau pengguna meminta konversi ke rupiah, ambil kurs saat itu dari sumber yang bisa dikutip (misalnya BNB/IDR, USDT/IDR, USD/IDR), catat kurs dan waktunya, lalu hitung dengan `~/workspace/custom-skills/nft-detail/scripts/convert.py`.
- Sajikan hasil konversi sebagai perkiraan, karena kurs bergerak, dan bedakan floor dari snapshot lama dengan floor live hari ini: konversi floor snapshot lama ke kurs hari ini bukan berarti floor hari ini masih sama.

## Konfirmasi nominal — berlaku untuk semua yang berhubungan dengan harga, fiat atau crypto

- Aturan ini berlaku untuk semua aksi yang berhubungan dengan harga, baik fiat maupun crypto: beli, jual, listing, offer, bid, mint berbayar, floor, dan ambang watcher.
- Sebelum bertindak, pastikan nominalnya dua arah: tunjukkan nominal asli persis seperti yang diperintahkan (misalnya 0.01 USDT, bukan 0.1 USDT, bukan 1 USDT, bukan 0.01 USD kalau yang dimaksud USDT), lengkap dengan desimalnya, lalu tunjukkan padanannya dalam rupiah dengan kurs yang dikutip saat itu beserta waktunya, misalnya "0.01 USDT ≈ Rp181 pada kurs Rp18.139,60 per USDT" — bukan Rp180 bulat tanpa kurs, karena pembulatan bisa menutupi kesalahan desimal.
- Tanyakan balik dengan kalimat konfirmasi yang jelas, misalnya: "Apakah anda akan menjual NFT ini seharga 0.01 USDT atau 180 rupiah?" — dan tunggu jawaban pengguna untuk item dan nominal itu sebelum bertindak.
- Sertakan juga total yang harus dibayar/diterima: harga, fee marketplace, royalti kalau ada, dan gas, karena total bisa berbeda dari harga nominal.
- Jangan pernah mengasumsikan nominal dari konteks, membulatkan desimal, atau menukar mata uang (USDT/USD/IDR/BNB) tanpa konfirmasi.
- Aturan ini mengalahkan perintah "langsung beli" dari watcher: begitu watcher menemukan listing di bawah ambang, yang pertama dilakukan adalah menampilkan token, harga persis, padanan rupiah, fee, dan total untuk dikonfirmasi — pembelian hanya jalan setelah pengguna mengonfirmasi item dan nominal itu.

## Verifikasi sebelum menyajikan

- Baca ulang harga, floor, dan offer di halaman atau API aslinya sebelum menyajikan, karena hasil pencarian bisa basi dan angka mint bisa bergerak selama pengecekan.
- Waspadai koleksi tiruan, listing palsu, dan listing yang sudah terjual.
- Jangan membeli, menawar, listing, atau menandatangani transaksi tanpa persetujuan eksplisit pengguna untuk item dan harga itu.

## Sajikan hasil

- Sajikan dalam bahasa pengguna, singkat, dan bisa dicek ulang.
- Format per token/koleksi: identitas, marketplace tempat dijual, floor, volume beserta jendelanya, last sale, offer aktif, dan status token itu sendiri (listed / not listed).
- Akhiri dengan daftar mana yang terverifikasi dan mana yang tidak terverifikasi, lengkap dengan sumber dan waktu cek untuk tiap angka.
- Jika tidak ada hasil yang lolos verifikasi, katakan tidak ada, dan jangan mengarang angka.

## Available connectors

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

## Websites

- [BscScan](https://bscscan.com/) untuk identitas token BSC, kontrak, pemilik, dan supply on-chain.
- [OpenSea](https://opensea.io/) untuk listing, floor, dan offer di banyak chain, dicek dengan alamat kontrak, bukan nama saja.
- [Blur](https://blur.io/) untuk listing, floor, dan offer NFT Ethereum.
- [Magic Eden](https://magiceden.io/) untuk listing, floor, dan offer NFT Solana dan chain lain yang didukung.
