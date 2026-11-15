# Pola Komposit — Teknik Serangan Gabungan (Seri K)

Ditulis 2026-11-04 atas perintah user: teknik serangan TIDAK berdiri sendiri — teknik selalu tumpang tindih dan saling melengkapi. Seri K adalah teknik BARU yang diturunkan secara sistematis dengan menggabungkan kartu pola P-01..P-21: baca target sebagai TEMPAT BERTEMUNYA pola, bukan sebagai daftar pola. Setiap kartu menyebut pola induknya, mekanisme gabungannya, prasyarat, tanda di kode, dan uji termurah. Status membedakan: TERVALIDASI KASUS (sudah ada insiden nyata berbentuk komposit ini), TERVALIDASI LAB (dibuktikan di lab lokal), dan PROYEKSI (belum ada kasus terkenal — hipotesis buruan paling berharga).

## K-01 Retakan Dua Oracle — P-06 x P-08 x P-18
Dua pembaca harga yang seharusnya sepakat tetapi mengambil dari sumber berbeda dengan irama pembaruan berbeda (spot vs TWAP, Chainlink vs fallback internal, harga pinjam vs harga likuidasi).
- Mekanisme: gerakkan sumber cepat dalam jendela lag sumber lambat; lakukan aksi bernilai di pembaca yang tertinggal. Tiap sumber secara individual "benar" — kerugiannya lahir di SELISIH keduanya (H1 murni).
- Prasyarat: >=2 jalur harga untuk aset yang sama; satu bisa digerakkan murah; tidak ada pemeriksa deviasi antar-sumber.
- Tanda di kode: dua fungsi harga berbeda untuk aset sama di kontrak berbeda; fallback oracle; TWAP window pendek berdampingan dengan feed heartbeat panjang.
- Uji termurah: di fork, geser harga spot pool, lalu panggil KEDUA pembaca dalam blok yang sama dan bandingkan.
- Status: PROYEKSI (keluarga dekat: serangan lag TWAP dan depeg fallback sudah ada; bentuk dua-pembaca-resmi belum jadi kasus terkenal).

## K-02 Kolateral Cetakan Sendiri Lintas Pasar — P-04 x P-10 x P-07
Gabungan: daftarkan pasar/token sendiri, pompa harganya di pasar kosong, habiskan nilainya di pasar SEHAT lain yang menerimanya sebagai kolateral.
- Mekanisme: (1) pasar A memperbolehkan aset buatan penyerang terdaftar (P-04); (2) di pasar A yang kosong, donasi menggelembungkan harga saham/kolateral (P-10/P-07); (3) saham yang menggelembung dipakai meminjam aset riil di pasar B yang mempercayai harga A (H1: angka dibaca di kontrak yang bukan penulisnya).
- Prasyarat: jalur pendaftaran tanpa izin di suatu tempat + konsumen harga/kolateral di tempat lain; tidak ada cap berbasis likuiditas riil.
- Tanda di kode: fungsi list/register/mint pasar baru; oracle yang membaca saldo/rate kontrak yang bisa dibuat siapa pun; kolateral diterima berdasarkan alamat yang bisa didaftarkan.
- Uji termurah: di fork, buat aset sendiri, daftarkan, donasikan, lalu coba pinjam di pasar kedua dengan kolateral hasil pompaan.
- Status: TERVALIDASI KASUS secara parsial (Sonne/Hundred/Resupply membuktikan kaki pompa pasar kosong; rantai dua pasar penuh adalah generalisasinya).

## K-03 Ambang Disewa di Jendela Telanjang — P-20 x P-21 x P-17
Gabungan: jendela aktivasi (pasar/fitur baru belum terkonfigurasi penuh) + prasyarat yang bisa disewa sesaat + ambang efektif yang lebih kecil dari ambang tertulis.
- Mekanisme: pada jam pertama sebuah pasar/fitur hidup — sebelum timelock, cap, atau daftar putih selesai — sewa aset governance/voting/kolateral sesaat untuk memenuhi ambang yang saat itu efektif kecil, lalu dorong keputusan (whitelist aset sendiri, ubah parameter, aktifkan jalur) yang mengunci keuntungan setelah jendela menutup.
- Prasyarat: aktivasi bertahap yang bisa diamati on-chain; keputusan berpengaruh bisa diambil di dalam jendela; aset ambang tersedia untuk disewa (flash loan / pasar kredit).
- Tanda di kode: transaksi deploy->init->seed->nilai masuk berurutan; governance yang langsung aktif tanpa timelock awal; parameter kritis masih default saat nilai pertama masuk.
- Uji termurah: rekonstruksi garis waktu blok deploy s.d. konfigurasi selesai; tandai keputusan apa saja yang SUDAH bisa diambil di tiap blok peralihan.
- Status: TERVALIDASI KASUS secara parsial (Radiant: eksploitasi 6 detik setelah aktivasi pasar Arbitrum; Beanstalk: governance disewa).

## K-04 Pembulatan Dipersenjatai Batch — P-11 x P-14 x H4
Galian 1 wei yang tidak berarti sendirian menjadi drain bila ada eksekutor yang bisa mengulanginya ribuan kali dalam satu transaksi.
- Mekanisme: temukan kesalahan pembulatan searah (selalu menguntungkan pemanggil sebesar debu), lalu pasangkan dengan kendaraan pengulang: multicall/batch bawaan, fungsi yang bisa memanggil dirinya lewat jalur sah, atau flash loan sebagai bahan bakar loop. Yang dicari bukan bug pembulatannya saja — melainkan PASANGANnya dengan pengulang.
- Prasyarat: pembulatan searah yang bisa dipicu pengguna; kendaraan pengulang dalam satu tx; biaya gas per iterasi < keuntungan per iterasi.
- Tanda di kode: div sebelum mul (atau sebaliknya) di jalur yang bisa dipanggil publik berulang; multicall; fungsi swap/mint/redeem tanpa batas frekuensi per blok.
- Uji termurah: hitung keuntungan per iterasi dari kode, kalikan iterasi maksimum yang muat dalam satu blok; bila hasilnya material, buktikan di fork dengan loop.
- Status: TERVALIDASI KASUS (Balancer 2025: pembulatan searah diulang sampai $116-128jt).

## K-05 Bootstrap Ulang di Sistem yang Sudah Berisi — P-12 x P-21 x P-16
Jalur "pengguna pertama" yang seharusnya hanya hidup sekali menjadi bisa dijangkau lagi setelah upgrade/modul baru, di atas saldo yang sudah ada.
- Mekanisme: upgrade memasang modul/pasar baru atau menginisialisasi ulang komponen yang terhubung ke vault/pool LAMA yang sudah bernilai; penyerang memainkan peran "pertama" (seeder/depositor pertama) di komponen baru itu dan memanen keuntungan bootstrap (harga saham awal, insentif seeder, rate awal) yang dihitung terhadap nilai lama.
- Prasyarat: komponen baru terhubung ke nilai lama; jalur bootstrap tidak memeriksa bahwa sistem sudah berjalan; initialize bisa dipanggil pada konteks yang sudah berisi.
- Tanda di kode: initialize/re-initialize pada proxy yang saldonya tidak nol; pasar baru ditambahkan ke vault yang sudah berumur; seed/mint pertama tanpa pagar minimum.
- Uji termurah: di fork pada blok setelah upgrade terakhir, jalankan jalur bootstrap sebagai akun baru dan ukur nilai yang berpindah.
- Status: TERVALIDASI KASUS secara parsial (Yearn yETH: jalur bootstrap terjangkau ulang; Sonne: pasar kosong hasil deploy ulang).

## K-06 Klaim Ganda Lintas Jalur Paralel — P-05 x P-15 x H1
Dua jalur sah untuk klaim/transfer yang sama (dua adapter bridge, dua relayer, dua fungsi rilis) yang masing-masing menyimpan bukti "sudah diklaim" SENDIRI.
- Mekanisme: satu deposit/bukti dipakai dua kali — sekali lewat tiap jalur — karena registry klaim tidak dibagi. Representasi "sudah diklaim" ada dua dan keduanya tidak sepakat (H1); pembersihan state asimetris antar jalur (P-05); pesan/bukti diperlakukan sebagai fakta yang bisa diserahkan ke jalur mana pun (P-15).
- Prasyarat: >=2 jalur rilis untuk nilai yang sama; registry penanda klaim per-jalur, bukan global; jalur kedua tidak memeriksa jalur pertama.
- Tanda di kode: dua adapter/relayer untuk bridge yang sama; mapping claimed/consumed/nonce di dalam kontrak adapter (bukan di vault inti); dua fungsi dengan nama berbeda yang membayar nilai yang sama.
- Uji termurah: di fork/lab, klaim bukti yang sama lewat jalur A lalu jalur B; yang kedua harus revert — bila tidak, komposit ini hidup.
- Status: TERVALIDASI LAB 2026-11-04 (~/workspace/immunefi-bounty/lab-komposit/: deposit 1 ETH diklaim lewat dua jalur menjadi 2 ETH, vault tekor dari backing korban; versi perbaikan registry-bersama menggagalkan klaim kedua — forge test 2/2 PASS). Catatan lapangan: Origin Protocol TIDAK kena komposit ini karena kedua adapternya berbeda ARAH (outbound CCIP, inbound Superbridge), bukan paralel — komposit ini memburu desain yang jalurnya benar-benar paralel.
- Aturan buruan permanen: SETIAP sistem dengan >=2 jalur untuk nilai yang sama wajib diuji klaim silang antar jalur sebelum dinyatakan bersih.

## Cara memakai seri K
1. Di Fase 0 target baru, selain analogi kasus tunggal, tanyakan: "pola-pola di target ini bisa BERTEMU di mana?" — titik temu itulah hipotesis K.
2. Urutan nilai: PROYEKSI yang prasyaratnya terpenuhi di target > TERVALIDASI yang belum diuji di target > pola tunggal.
3. Setiap target yang tuntas wajib menyetor komposit baru atau hasil uji komposit lama ke berkas ini (Fase 7 SKILL.md).

---

## Hasil uji lapangan — Origin Protocol (2026-11-04, Fase 9: aplikasi resmi pertama seri K)
- K-01: GUGUR — satu-satunya lag dua representasi (saldo laporan lintas-rantai) penulisnya tergating; tak ada sumber yang bisa digerakkan penyerang.
- K-02: GUGUR — nol permukaan pendaftaran tanpa izin di jalur nilai.
- K-03: GUGUR — jendela aktivasi 4 blok terbukti bernilai 0 dari data arsip on-chain (cek balanceOf pada blok deploy & blok authorise: teknik murah yang menutup kartu ini di target mana pun).
- K-04: GUGUR EMPIRIS — 50 round trip swap di fork: penyerang -0,009681 ETH; spread searah protokol, pengulangan = kerugian majemuk bagi penyerang.
- K-05: GUGUR EMPIRIS — initialize dari penyerang revert di gerbang governor pada kedua strategi.
- K-06: GUGUR STRUKTURAL — slot inboundAdapter tunggal per strategi (kode + live); Origin memang tidak punya jalur paralel.
Pelajaran metode: kartu K paling cepat gugur lewat tiga cek murah — (1) daftar permukaan pendaftaran, (2) saldo kontrak pada blok-blok jendela aktivasi, (3) jumlah slot jalur masuk di kode. Jalankan ketiganya di Fase 1 setiap target sebelum menulis PoC apa pun.

## K-07 Spiral Utang Macet (ditambah 2026-11-04 dari studi referensi)
Komposisi: P-04 (donasi menaikkan nilai tercatat kolateral) × P-10 (pasar/kolateral tipis) × kegagalan penutup likuidasi. Rantai: nilai kolateral dipompa (donasi ke vault yang harganya jadi acuan, atau pump spot aset ilikuid) → pinjam maksimum terhadap nilai hantu → likuidasi secara rasional TIDAK menutup utang (harga jual nyata < nilai pinjaman; likuidator abstain) → sisa utang macet disosialisasikan dan melemahkan protokol lebih jauh. Jangkar: Venus THE (Mar 2026 — RANTAI TERVERIFIKASI UJI KONTROL 2026-11-04: korban = pemegang 84,24% pasokan vTHE yang ter-leverage; persetujuan delegasi Comptroller + allowance tak terbatas dipanen 13 blok (±6 detik) sebelum serangan; donasi 36,10 jt THE dari 6 alamat ber-allowance menaikkan rate 1,0085→±3,9; borrowBehalf memisahkan utang (di korban) dari kas (ke penyerang): 1.581.454,96 USDC, lalu pinjam-donasi-balik 4.628.903,90 THE, lalu 913.858,26 CAKE + 1.972,53 WBNB; vektor donasinya sudah ditandai temuan Code4rena M-10 tahun 2023 dan dinilai tim "tanpa efek negatif"); Venus wUSDM (Feb 2025, donasi flash-loan mengubah rate 1,06→1,7, utang macet ±$717 rb); Aave CRV (Nov 2022, utang macet $1,6 jt karena likuidator tak bisa memperoleh CRV); Mango (2022, pump self-trade). Aturan buruan: setiap kolateral yang nilainya berasal dari harga saham vault ATAU pasar tipis wajib diuji tiga langkah sekaligus — (1) bisakah nilainya digerakkan donasi/pump murah, (2) apakah cap supply benar-benar mengikat jalur itu, (3) bila harga kembali normal, apakah likuidasi menutup utang pada likuiditas nyata.
