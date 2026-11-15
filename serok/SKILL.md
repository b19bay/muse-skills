# Serok

Skill ini mencari NFT yang salah pasang harga, yaitu listing aktif yang harganya jauh di bawah floor koleksinya dan di bawah harga pasar terbaru, lalu menyajikannya setelah diverifikasi. Gunakan skill ini saat pengguna meminta NFT murah, NFT salah harga, atau NFT di bawah floor.

## Tentukan target

- Tanyakan chain, marketplace, koleksi, dan mata uang sebelum memindai, kecuali pengguna sudah menyebutkannya.

- Sesuaikan marketplace dengan perintah pengguna saat itu, dan jangan kunci skill ini ke satu marketplace saja.

- Catat jendela waktu yang diperintahkan, misalnya 30 menit terakhir atau 1 jam terakhir, dan jangan kunci jendela itu ke 1 menit.

- Catat ambang salah harga dari pengguna, misalnya harga listing di bawah 0.01 dolar saat floor 20 dolar.

- Gunakan ambang rasio, bukan hanya angka absolut, agar satu ambang bisa dipakai di koleksi lain.

- Jangan memindai semua koleksi tanpa batas, karena itu membuang kuota API dan menenggelamkan hasil yang benar benar murah.

## Periksa aturan utama

- Aturan utama adalah volume besar, floor tinggi, dan aktif, dan ketiganya harus lolos bersamaan.

- Lanjutkan hanya jika koleksi masih aktif, yaitu masih bisa diperdagangkan dan tidak dihentikan atau dibekukan di marketplace yang dipakai.

- Lanjutkan hanya jika volume besar dalam jendela yang diperintahkan, misalnya 30 menit terakhir atau 1 jam terakhir, bukan sekadar ada satu transaksi.

- Lanjutkan hanya jika floor tinggi, yaitu floor jauh di atas harga listing yang dicari, bukan floor rendah yang mudah goyah.

- Tolak koleksi yang volumenya kecil, floornya rendah, atau tidak aktif, karena floor dan harga pasarnya tidak bisa dipercaya.

## Ambil floor dan listing

- Cari dulu marketplace resmi proyek itu sendiri, sebelum marketplace umum, karena koleksi baru sering hanya diperdagangkan di situsnya sendiri, dan biaya marketplace di data resmi proyek adalah petunjuk adanya marketplace asli itu.

- Ambil floor koleksi dari sumber marketplace yang sama dengan listing, agar perbandingannya adil.

- Ambil listing aktif saja, dan catat waktu pengambilan untuk tiap listing.

- Baca ulang harga listing di halaman atau API aslinya sebelum menyajikan hasil, karena hasil pencarian bisa basi.

- Pisahkan harga listing, biaya marketplace, dan biaya gas, karena total bayar bisa jauh di atas harga listing.

## Hitung dan tandai salah harga

- Hitung rasio harga listing terhadap floor dan persentase diskon untuk tiap listing dengan `~/workspace/custom-skills/serok/scripts/discount.py`.

- Ambil juga harga jual terakhir koleksi itu, dan pakai hanya penjualan dalam jendela yang diperintahkan, misalnya 30 menit terakhir atau 1 jam terakhir, sebagai pembanding terbaru.

- Tandai listing sebagai salah harga hanya jika harga listing di bawah floor dan di bawah harga jual terakhir yang masih segar itu, dan listing masih aktif saat dicek ulang.

- Jika tidak ada penjualan dalam jendela yang diperintahkan, catat itu dengan jelas dan jangan mengklaim harga jual terakhir sebagai pembanding segar.

- Urutkan hasil dari diskon terbesar, dan tampilkan hanya hasil teratas yang lolos verifikasi.

- Simpan bukti berupa nama koleksi, token id, harga listing, floor, harga jual terakhir dan waktunya, volume, rasio, diskon, tautan listing, dan waktu cek.

## Verifikasi sebelum bertindak

- Periksa koleksi terverifikasi, kontrak yang benar, dan riwayat penjualan terakhir sebelum merekomendasikan pembelian.

- Waspadai listing palsu, koleksi tiruan, harga yang berubah saat checkout, dan listing yang sudah terjual.

- Jangan membeli, menawar, atau menandatangani transaksi tanpa persetujuan eksplisit pengguna untuk item dan harga itu.

- Jika harga berubah, listing hilang, atau floor berubah drastis, batalkan rekomendasi dan beri tahu pengguna.

## Sajikan hasil

- Sajikan hasil dalam bahasa pengguna, singkat, dengan angka yang bisa dicek ulang.

- Sertakan tautan listing dan sumber floor untuk tiap hasil.

- Jelaskan dengan jelas mana yang sudah diverifikasi dan mana yang masih perlu dicek ulang.

- Jika tidak ada hasil yang lolos, katakan tidak ada, dan jangan mengarang listing.

## Available connectors

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

## Websites

- [OpenSea](https://opensea.io/) for listing dan floor NFT di banyak chain. Bawa nama koleksi dan kontrak ke pencarian, dan verifikasi harga di halaman listing aslinya.

- [Blur](https://blur.io/) for listing dan floor NFT Ethereum. Bawa nama koleksi dan kontrak ke pencarian, dan verifikasi harga di halaman listing aslinya.

- [Magic Eden](https://magiceden.io/) for listing dan floor NFT Solana dan chain lain yang didukung. Bawa nama koleksi dan kontrak ke pencarian, dan verifikasi harga di halaman listing aslinya.

## Alternatives for better results

- Tanyakan ambang yang lebih longgar jika tidak ada hasil, misalnya diskon minimal yang lebih kecil atau floor yang berbeda.

- Pantau satu atau beberapa koleksi favorit saja, karena pemindaian yang sempit lebih cepat dan lebih akurat.

- Minta pengguna menyebut anggaran maksimal dan biaya gas maksimal, agar hasil yang disajikan masih masuk akal untuk dibeli.
