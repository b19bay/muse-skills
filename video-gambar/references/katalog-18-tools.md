# Katalog 18 Tools Animasi (sumber: @okapi_fukugyo, 15 Nov 2026)

Sumber daftar ini adalah postingan https://x.com/okapi_fukugyo/status/2121725407867351215
yang menyebut ke-18 tool di bawah ini gratis dan dipublikasikan di GitHub.

Status verifikasi per 15 Nov 2026: Remotion Skills dan Motion Canvas sudah
diverifikasi langsung dari GitHub (publik, jumlah bintang tercatat di bawah).
16 tool lainnya sesuai daftar di postingan. Baca README masing-masing repo
sebelum memakai tool itu pertama kali, dan jangan mengandalkan ingatan
tentang API-nya.

| No | Tool | Repo | Fungsi | Kapan dipakai | Catatan |
|----|------|------|--------|---------------|---------|
| 01 | Remotion Skills | github.com/remotion-dev/skills | Skill resmi agar AI membuat video dari kode Remotion | Default Jalur B untuk video dari kode React | Terverifikasi: publik, 7.147 bintang, 13 sub skill. Pasang dengan `npx skills add remotion-dev/skills` |
| 02 | Motion Canvas | github.com/motion-canvas/motion-canvas | Animasi diagram dan penjelasan dari kode TypeScript | Explainer, visualisasi, video edukasi | Terverifikasi: publik, lisensi MIT, 19.892 bintang. Butuh Node |
| 03 | Motion | github.com/motiondivision/motion | Gerakan transisi layar | Transisi antar scene atau komponen | Library JS, butuh Node |
| 04 | Ola | github.com/franciscop/ola | Menggerakkan angka secara halus | Angka yang berubah mulus seperti counter dan grafik | Library JS kecil |
| 05 | Anime.js | github.com/juliangarnier/anime | Gerakan timeline dan jeda waktu | Koreografi banyak elemen dalam satu timeline | Library JS |
| 06 | Manim | github.com/ManimCommunity/manim | Animasi rumus dan bentuk | Video matematika dan geometri | Python, butuh ffmpeg |
| 07 | Shifty | github.com/jeremyckahn/shifty | Easing dan tween | Kurva gerak halus antar nilai | Library JS |
| 08 | Two.js | github.com/jonobr1/two.js | Animasi vektor 2D | Bentuk dan garis 2D yang bergerak | Library JS |
| 09 | Lottie Web | github.com/airbnb/lottie-web | Memutar animasi vektor yang ringan | Animasi ringan hasil After Effects atau Bodymovin | Library JS |
| 10 | TweenJS | github.com/CreateJS/TweenJS | Animasi yang bergerak berurutan | Rangkaian gerak berurutan | Library JS |
| 11 | LUME | github.com/lume/lume | Scene 3D dari HTML | 3D deklaratif langsung di HTML | Library JS |
| 12 | gifenc | github.com/mattdesl/gifenc | Ekspor GIF | Keluaran GIF dari frame animasi | Library JS |
| 13 | Konva | github.com/konvajs/konva | Kanvas interaktif yang bergerak saat disentuh | Animasi yang merespons klik atau sentuhan | Library JS |
| 14 | Blender | github.com/blender/blender | Rig dan animasi karakter | Karakter 3D dan rig | Berat, tidak terpasang di VM ini. Pasang dulu bila perlu |
| 15 | Three.js | github.com/mrdoob/three.js | Scene 3D | 3D umum di web | Library JS |
| 16 | Godot | github.com/godotengine/godot | Animasi game | Animasi bergaya game | Berat, tidak terpasang di VM ini. Pasang dulu bila perlu |
| 17 | Babylon.js | github.com/BabylonJS/Babylon.js | Rendering dan animasi 3D | 3D dengan fitur lengkap | Library JS |
| 18 | Proton | github.com/drawcall/Proton | Partikel | Efek partikel seperti api, hujan, dan debu | Library JS |

## Alur kerja yang disarankan postingan

Instruksi, buat, gerakkan, perbaiki, ekspor. Semua tahap itu tercakup oleh
daftar di atas: Remotion dan Motion Canvas untuk membuat, library tween
untuk menggerakkan, editor dan pratinjau untuk memperbaiki, ffmpeg dan
gifenc untuk mengekspor.
