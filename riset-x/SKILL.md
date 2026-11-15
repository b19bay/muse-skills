# Riset Proyek X

Skill ini meriset proyek agent dan NFT gratis yang ditemukan di X (Twitter), lalu menyaringnya dengan filter yang diperintahkan, sebelum proyek itu direkomendasikan untuk di-mint atau dibeli. Gunakan skill ini saat pengguna meminta riset proyek di X, cari proyek agent/NFT baru, atau "proyek apa yang bagus di X".

Riset ini nantinya dipakai sebagai alat untuk mint, jadi aturannya harus jelas dan hasilnya harus siap mint: tiap proyek yang lolos harus membawa semua data yang dibutuhkan tahap mint (kontrak terverifikasi, status mint, harga, jatah, dan bukti keramaian saat mint), bukan hanya "katanya bagus". Kalau satu data kunci itu tidak terverifikasi, proyek itu tidak boleh dilaporkan sebagai siap mint.

Jawab dulu pertanyaan pengguna: tidak ada skill bawaan yang persis seperti ini. Skill ini dibuat khusus untuk itu, dan memakai pencarian web untuk postingan X (misalnya `site:x.com` plus kata kunci), pembacaan profil dan situs proyek dan `llms.txt`-nya, verifikasi on-chain, serta skill `nft-detail` untuk detail pasar dan `serok` untuk cek salah harga — bukan satu konektor X resmi, karena tidak ada konektor X di katalog. Catatan penting: `social.search` hanya mencakup Instagram, Threads, dan Facebook, bukan X, jadi jangan mengklaim hasil `social.search` sebagai hasil dari X; untuk X pakai pencarian web dan pembacaan halaman X yang publik.

## Tentukan perintah riset dulu

- Catat yang diperintahkan: tema (agent, NFT gratis, atau keduanya), chain, jumlah proyek yang dicari, dan ambang filter untuk riset itu. Jangan kunci ambang ke satu angka selamanya.
- Akun besar bukan syarat. Yang penting adalah akunnya ramai ketika proses minting berjalan — lihat filter "Ramai saat mint" di bawah. Akun kecil boleh lolos kalau mint-nya ramai dan filter lain lolos; akun besar boleh ditolak kalau mint-nya sepi atau sudah mati.
- Catat daftar KOL yang dimaksud pengguna, kalau ada, sebagai nilai tambah (bonus), bukan syarat wajib. "Di-follow KOL" tidak boleh diklaim tanpa nama KOL-nya: sebutkan akun KOL mana yang follow, repost, atau berinteraksi dengan proyek itu, dengan tautan postingannya. Kalau bukti KOL bernama itu ada, proyek itu mendapat +1 nilai tambah dan naik peringkatnya, tapi bonus itu tidak bisa menyelamatkan proyek yang gagal satu filter utama.
- Kalau pengguna tidak menyebut ambang, pakai ambang awal di bawah ini dan katakan itu ambang awal, bukan perintah pengguna: aktif = ada postingan dalam 7 hari terakhir, ramai saat mint = ada bukti keramaian saat mint (lihat filter 2), harga = floor di atas 0 dan ada penjualan terakhir, bukan spam = tidak ada sinyal spam di bawah ini.

## Kumpulkan kandidat dari X

- Cari di X lewat pencarian web (misalnya `site:x.com` plus kata kunci tema, misalnya mint gratis, agent-only, free mint, dan nama chain-nya). Catat handle X, tautan postingan, dan tanggal postingan untuk tiap kandidat. Jangan pakai `social.search` untuk X, karena alat itu tidak mencakup X.
- Buka profil X proyek itu dan situs yang ditautkan dari profilnya, bukan dari tautan acak di balasan. Kalau situsnya tidak ada atau tautannya mengarah ke domain lain yang tidak terkait, tandai sebagai mencurigakan.
- Deduplikasi: proyek yang sama dengan handle atau kontrak yang sama hanya dihitung sekali, walaupun muncul di banyak postingan.

## Terapkan filter, satu per satu

Hitung lolos/tolak tiap filter dengan `~/workspace/custom-skills/riset-x/scripts/score.py`, dan jangan meloloskan proyek yang gagal satu filter utama hanya karena filter lain bagus.

## Skor dan bonus

- Skor dasar terdiri dari 5 filter wajib: aktif, ramai saat mint, harga nyata, bukan spam, gratis. LOLOS hanya jika kelima-limanya lolos (5/5).
- Dukungan KOL bernama (akun KOL yang follow, repost, quote, atau berkomentar substantif, dengan tautan) menambah **+1 bonus** di atas skor dasar, misalnya "5/5 +1 bonus KOL".
- **Market saat mint menambah +1 bonus lagi, dan ini satu poin bagus yang berdiri sendiri.** Syaratnya: mint masih berjalan (mintActive dan totalMinted masih di bawah supplyCap) TAPI di saat yang sama sudah ada floor di atas 0 ATAU offer aktif untuk koleksi itu, di marketplace yang sama dengan kontrak yang sama, dengan waktu snapshot dicatat. Floor adalah harga jual penjual, offer adalah tawaran beli pembeli — bedakan keduanya saat melapor, tapi salah satu saja sudah cukup untuk poin ini, bukan +1 per jenis. Ini sinyal kuat karena pasar sekunder sudah hidup sebelum mint habis, jadi ada pembeli yang siap menyerap hasil mint — kebalikannya adalah proyek yang transfernya terkunci sampai mint habis, sehingga belum ada pasar sama sekali saat mint berjalan.
- **Situs web terverifikasi menambah +1 bonus lagi.** Ini bukan sekadar "punya situs". Syaratnya harus lolos semua: situs resmi yang ditautkan dari profil X proyek (bukan tautan acak di balasan), situs bisa dibuka dan isinya jelas (apa proyeknya, cara mint, syarat, dan harga), ada dokumen yang bisa dicek — misalnya `llms.txt`, whitepaper, atau docs — dan kontrak yang tercantum di situs cocok dengan kontrak on-chain. Situs placeholder, situs yang kontraknya tidak cocok, situs yang isinya hanya klaim "FREE" tanpa penjelasan mint, atau situs yang tidak bisa dibuka, tidak mendapat bonus ini.
- Semua bonus **tidak bisa menyelamatkan** proyek yang gagal satu filter dasar: proyek 4/5 + bonus tetap DITOLAK, berapa pun bonusnya.
- Proyek LOLOS diurutkan berdasarkan skor total termasuk semua bonus: 5/5 + bonus di atas 5/5 tanpa bonus. Tampilkan tiap bonus secara terpisah di skor, jangan digabung menjadi angka tanpa penjelasan, misalnya "5/5 +1 bonus KOL +1 bonus market saat mint +1 bonus situs web".

1. **Aktif.** Lolos hanya jika: ada postingan proyek dalam jendela yang diperintahkan, mint atau market-nya masih live (dicek on-chain atau di situs resminya, bukan hanya klaim di postingan), dan tidak ada pengumuman berhenti, sold out permanen yang disembunyikan, atau akun yang sudah tidak aktif. Proyek sold out dicatat sebagai sold out, bukan aktif.
2. **Ramai saat mint.** Lolos hanya jika ada bukti keramaian ketika mint berjalan, bukan ukuran akunnya: banyak akun berbeda yang memposting, membalas, atau mengklaim mint dalam jendela mint itu; supply yang bergerak selama mint (totalMinted naik); dan/atau aktivitas pasar yang nyata setelah mint. Jumlah follower saja bukan bukti — follower bisa dibeli, dan interaksi bot tidak dihitung. Dukungan KOL bernama (follow, repost, quote, komentar substantif, dengan tautan) tetap masuk sebagai nilai tambah +1, bukan syarat wajib, dan akun besar tanpa keramaian saat mint tidak lolos filter ini.
3. **Koleksinya ada harga, bukan spam.** Lolos hanya jika koleksi itu punya harga yang bisa dicek: floor di atas 0 di marketplace-nya sendiri atau marketplace umum dengan kontrak yang sama, ada listing aktif, dan ada penjualan terakhir. **Harga saja tidak cukup: NFT yang bagus pasti ada market jual beli, volume, dan aktivitas.** Jadi filter ini juga mensyaratkan: ada marketplace yang benar-benar bisa dipakai jual beli (bukan sekadar halaman "coming soon"), ada volume perdagangan nyata dengan jendelanya dinyatakan (misalnya volume 24 jam, 7 hari, atau total — jangan membagi volume jangka panjang menjadi jendela pendek), dan ada aktivitas perdagangan yang masih berjalan (penjualan/transaksi terbaru, bukan hanya satu penjualan lama yang sudah basi). Koleksi tanpa floor, tanpa listing, tanpa penjualan, tanpa volume, atau tanpa aktivitas terbaru — atau hanya ramai di postingan tapi tidak ada pasarnya — ditolak untuk rekomendasi harga.
4. **Bukan spam / tiruan.** Tolak jika ada salah satu: kontrak di situs tidak cocok dengan kontrak on-chain, situs meniru proyek terkenal dengan nama mirip, janji return pasti atau giveaway yang meminta kirim dana dulu, engagement farming yang jelas (komentar bot berulang, like jauh di atas komentar dan repost yang masuk akal), akun baru dibuat mendadak hanya untuk satu mint, atau tidak ada tim, dokumen, atau kontrak yang bisa dicek sama sekali.
5. **Gratis, kalau yang dicari gratis.** Untuk riset NFT gratis: lolos hanya jika harga mint-nya 0 atau mint pertama gratis (gas saja), diverifikasi on-chain lewat `quoteMint` atau fungsi harga yang setara, bukan hanya tulisan "FREE" di situs. Kalau ternyata berbayar, laporkan harganya dan jangan direkomendasikan sebagai gratis.
6. **Link aman.** Berlaku aturan tetap pengguna: setiap link yang dikirim atau ditemukan harus dipastikan aman dulu sebelum dipakai — cocokkan domain, situs, dan kontraknya dengan data on-chain, dan jangan hubungkan wallet atau tanda tangan di situs yang belum terverifikasi.

## Profil yang menghasilkan uang — contoh referensi, bukan janji profit

Pengguna menunjuk Ptah dan NONCE sebagai contoh proyek gratis / berbiaya rendah yang menghasilkan uang. Pakai keduanya sebagai profil yang dicari, dengan perbedaannya dijaga tetap jelas, bukan disamaratakan:

- NONCE Genesis: mint gratis, gas saja, dengan tantangan yang harus diselesaikan; setelah sold out 7.777/7.777, floor sempat terverifikasi 12,8 USDT dengan volume dan penjualan nyata. Jadi keuntungannya, kalau ada, berasal dari selisih floor terhadap biaya gas — bukan dari janji return.
- Ptah Relics: mint berbayar (USDT dan BNB, maks 4 per Agent ID), sold out 100.000 pada pagi 23 Okt 2026, dengan laporan floor $23 dan volume $928.000 pada hari itu. Keuntungannya, kalau ada, berasal dari selisih harga jual terhadap harga mint, bukan dari mint gratis.
- Ptah Proof of Agent card: gratis, gas saja, satu per Agent ID, tapi soulbound — tidak bisa dijual. Potensi nilainya bukan dari penjualan kartu, melainkan dari undian PTAH harian lewat posting #ProofOfAgent, dan mint-nya tutup 8 Nov 2026 pukul 04:44 UTC. Jangan pernah melaporkan kartu soulbound sebagai aset yang bisa dijual.

Profil buruan yang ditarik dari contoh-contoh itu: biaya mint gratis atau jauh di bawah floor, mint ramai dan cepat habis, floor dan volume nyata setelah mint, dan keramaian saat mint terverifikasi. "Gratis" saja tidak cukup; "ada floor" saja tidak cukup; keduanya harus ada, dengan biaya dan floor yang bisa dibandingkan angkanya. Dan ingat: selain harga, NFT yang bagus pasti ada market jual beli, volume, dan aktivitas — jadi floor tanpa market yang hidup, tanpa volume, dan tanpa aktivitas perdagangan terbaru bukan profil yang bagus.

## Checklist siap mint — wajib untuk proyek yang lolos

Karena riset ini adalah alat untuk mint, tiap proyek LOLOS harus dilengkapi checklist ini, supaya tahap mint tidak perlu riset ulang:

- Link aman terverifikasi: domain, situs, dan kontrak di situs cocok dengan data on-chain.
- Kontrak dan chain terverifikasi, dengan alamat kontrak lengkap.
- Status mint live: `mintActive` atau setara, totalMinted dan supplyCap, serta jatah per wallet/Agent ID.
- Harga mint terverifikasi on-chain: 0 / gratis pertama, atau harga berbayar persisnya kalau memang berbayar — dengan catatan berbayar tidak boleh di-mint tanpa perintah bayar dari awal.
- Syarat khusus mint, kalau ada: misalnya proof-of-work, SAT challenge, Agent ID, atau EOA only, beserta cara verifikasinya sebelum kirim.
- Bukti keramaian saat mint, sesuai filter 2, dengan tautan dan tanggalnya.
- Perkiraan gas dan saldo wallet saat ini, supaya jelas apakah mint itu bisa dieksekusi atau harus top up dulu.
- Langkah berikutnya yang jelas: misalnya "mint gratis 1, gas saja, setelah konfirmasi nominal" — dan konfirmasi nominal itu tetap wajib sebelum eksekusi, sesuai aturan uang.

## Verifikasi setelah lolos filter

- Untuk tiap proyek yang lolos, verifikasi dengan skill `nft-detail`: kontrak, token, supply, mintable, harga mint, marketplace tempat dijual, floor, volume beserta jendelanya, last sale, dan offer.
- Kalau proyek itu juga dicurigai salah harga, cek dengan skill `serok` — jangan campur hasil serok dengan hasil riset ini.
- Kalau satu angka tidak bisa diverifikasi, tulis tidak terverifikasi dan jangan mengarangnya. Proyek dengan angka kunci yang tidak terverifikasi tidak boleh dilaporkan sebagai lolos penuh.

## Aturan uang dan nominal

- Aturan tetap pengguna berlaku penuh di sini: semua yang berhubungan dengan harga, fiat atau crypto, harus dikonfirmasi nominalnya dulu — mata uang, desimal, padanan rupiah dengan kurs dan waktunya, fee, dan total — sebelum aksi apa pun.
- Setelah link aman, hanya yang gratis yang di-mint, tidak yang berbayar, kecuali pengguna dari awal memang memerintahkan bayar untuk proyek itu.
- Riset ini hanya merekomendasikan. Ia tidak membeli, mint, listing, atau menandatangani apa pun tanpa persetujuan eksplisit pengguna untuk item dan nominal itu.

## Sajikan hasil

- Sajikan dalam bahasa pengguna, singkat, dan bisa dicek ulang, diurutkan dari skor total tertinggi, termasuk semua nilai tambah.
- Format per proyek: nama, handle X dan tautan postingan, situs, chain, kontrak, harga mint, supply, bukti aktif, bukti ramai saat mint, bukti KOL bernama kalau ada (nilai tambah +1, dengan nama dan tautan), bukti market saat mint kalau ada (floor atau offer yang sudah ada selagi mint berjalan, dengan snapshot waktu dan marketplace-nya), bukti pemeriksaan situs web kalau ada (situs resmi dari profil X, dokumen yang dicek, dan kecocokan kontrak situs dengan on-chain — nilai tambah +1 hanya kalau semua lolos), floor/volume/last sale, sinyal spam kalau ada, checklist siap mint, dan verdict LOLOS atau DITOLAK beserta alasan filter yang gagal.
- Akhiri dengan daftar proyek yang lolos saja yang boleh dilanjutkan ke tahap mint — dan untuk tiap proyek itu, sebutkan langkah berikutnya (misalnya "mint gratis 1, gas saja, setelah konfirmasi nominal").
- Jika tidak ada proyek yang lolos, katakan tidak ada, dan jangan mengarang proyek.
