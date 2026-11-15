# Video dan Gambar

Skill ini merangkum dua postingan @okapi_fukugyo menjadi satu studio produksi. Postingan pertama tanggal 15 Nov 2026 mendaftar 18 repositori GitHub gratis untuk animasi. Postingan kedua tanggal 7 Nov 2026 memberi alur pemula membuat iklan anime 15 detik. Skill ini memadukan keduanya dengan kemampuan bawaan Muse sehingga satu permintaan video atau gambar bisa dikerjakan dari ujung ke ujung.

Sumbernya adalah https://x.com/okapi_fukugyo/status/2121725407867351215 dan https://x.com/okapi_fukugyo/status/2119064562284831078

## Pilih jalur produksi

- Tentukan jalur dari kebutuhan pengguna sebelum membuat apa pun. Jalur A memakai gambar AI lalu gerak Ken Burns ffmpeg dan paling cepat untuk iklan sosial 15 detik. Jalur B memakai animasi dari kode dan paling tepat untuk diagram, data, teks akurat di layar, dan hasil yang harus bisa diedit.

- Pilih jalur hybrid bila gambar perlu gaya AI tetapi teks dan timing harus presisi. Buat aset gambar lewat Jalur A lalu animasikan dan beri teks lewat Jalur B.

- Bila pengguna tidak menyebut jalur, pakai Jalur A untuk permintaan sekali jadi dan Jalur B bila pengguna menyebut edit, presisi, atau branding.

- Tanyakan satu hal hanya bila jalurnya tidak bisa ditentukan dari permintaan. Jangan menanyakan hal yang sudah jelas.

## Jalur A: gambar AI lalu video AI

- Susun dulu rancangan sebagai sutradara sebelum generate apa pun. Rancangan berisi tiga ide, pengaturan satu karakter utama, storyboard lima cut masing-masing tiga detik, dan satu prompt gambar berbahasa Inggris untuk tiap cut. Detail langkahnya ada di references/workflow-15-detik.md.

- Buat gambar diam dengan `media.generate_image` dari prompt tiap cut. Satu pesan pengguna dibatasi empat gambar, jadi storyboard lima cut perlu dua pesan atau potong menjadi empat cut.

- Gerakkan tiap gambar dengan ffmpeg Ken Burns memakai `scripts/kenburns-seg.sh`. Skrip itu memakai blurred-fill agar gambar tidak terpotong, zoompan untuk gerak lambat, dan drawtext untuk headline. Contoh jadi ada di ~/workspace/video-gambar/defence-steal-war/build.sh.

- Jaga konsistensi karakter dengan memakai gambar referensi yang sama dan `resume_from_snapshot_id` dari hasil sebelumnya pada generate berikutnya.

- Rakit segmen menjadi satu video dengan concat ffmpeg atau `scripts/stitch-clips.sh`. Video 15 detik biasanya terdiri dari tiga segmen lima detik.

- Sebutkan format vertikal 1080x1920 di prompt untuk Reels, Shorts, dan X. Sebutkan format 1920x1080 untuk YouTube landscape.

## Jalur B: animasi dari kode

- Baca katalog di references/katalog-18-tools.md dan pilih tool dari kebutuhan, bukan dari kebiasaan. Remotion adalah default untuk video dari kode React. Motion Canvas adalah default untuk animasi diagram dan penjelasan. Manim adalah default untuk matematika. Three.js, Babylon.js, dan LUME adalah pilihan untuk 3D.

- Baca README repositori tool yang dipilih sebelum memakainya pertama kali. Jangan mengandalkan ingatan tentang API-nya.

- Untuk Remotion, pasang dulu skill resminya dengan `npx skills add remotion-dev/skills` lalu ikuti sub skill yang sesuai. Mulai dari best practices bila ragu.

- Tulis kode animasi di folder proyek sendiri di bawah ~/workspace/video-gambar/<slug>/. Render ke berkas video, bukan sekadar pratinjau di layar.

- Ekstrak beberapa frame dari hasil render dengan ffmpeg lalu baca frame itu dengan `muse.read` untuk memeriksa visual sebelum menyerahkan hasil.

## Rakit, ekspor, dan periksa

- Simpan semua hasil di ~/workspace/video-gambar/<slug>/ dengan nama berkas bertanggal.

- Periksa durasi dan resolusi hasil akhir dengan ffprobe sebelum melapor. Jangan melaporkan durasi dari perkiraan.

- Jangan pernah menyatakan video selesai bila berkas final belum ada dan belum diperiksa. Pratinjau, storyboard, dan prompt bukan hasil akhir.

- Serahkan berkas final sebagai lampiran beserta durasi, resolusi, dan ukurannya.

- Bila satu generate gagal atau hasilnya kurang, ubah prompt berdasarkan kekurangan yang terlihat lalu coba lagi. Jangan mengulang prompt identik.

## Batasan yang harus diingat

- Muse membuat paling banyak empat gambar per pesan pengguna. Bila permintaan butuh lebih, buat sebanyak batasnya lalu beri tahu pengguna sisanya.

- `media.generate_video` diblokir wilayah untuk akun ini. Pemanggilan selalu gagal 403 dan blokirnya permanen, dikonfirmasi 5 Nov 2026, dikonfirmasi ulang 15 Nov 2026 pagi, dan dikonfirmasi ketiga kalinya 15 Nov 2026 ~12:10 WIB atas perintah user. Pesan error eksplisit: "not available for this account in its country or region" — gate mengikat wilayah terdaftar AKUN, bukan lokasi fisik pengguna (pengguna di Singapura, wilayah terbuka, tetap diblok). Ini restriksi permanen, bukan outage, dan sistem melarang request video lagi untuk akun ini. Jangan pernah memanggilnya lagi. Gerak video selalu dibuat dengan ffmpeg Ken Burns.

- Musik latar dibuat dengan sintesis lokal ffmpeg memakai resep aevalsrc di build.sh contoh. Bila pengguna menyediakan berkas audio sendiri, campur dengan amix.

- Blender dan Godot tidak terpasang di VM ini. Pakai keduanya hanya bila pengguna memintanya secara eksplisit, dan pasang dulu sebelum bekerja.

- ffmpeg, Node, dan Python tersedia di VM ini. Periksa ulang ketersediaan tool sebelum menjanjikan render berbasis kode.

## Available connectors

- [GitHub](/opt/hatch/connectors/github/CONNECTOR.md) for reading tool repositories, README files, and documentation before using a tool.

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

## Alternatives for better results

- Cari referensi gaya visual dulu dengan skill `image-search` sebelum generate, bila pengguna menyebut gaya atau referensi yang belum jelas.

- Pakai gambar referensi dari pengguna sebagai identitas atau gaya bila pengguna menyediakannya, mengikuti aturan media tentang foto referensi.

- Tawarkan potongan vertikal dan landscape dari satu proyek yang sama bila video akan tayang di lebih dari satu platform.
