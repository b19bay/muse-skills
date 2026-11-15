# PROVENANCE — skill video-gambar

- Dibuat: 15 Nov 2026, atas perintah user ("buat skill khusus buat video
  dan gambar", "rangkum semua menjadi 1 skill sempurna").
- Sumber isi:
  - https://x.com/okapi_fukugyo/status/2121725407867351215 (15 Nov 2026):
    daftar 18 repositori GitHub gratis untuk animasi. Dibaca penuh lewat
    browser tanpa login, 15 Nov 2026 ~11:30 WIB.
  - https://x.com/okapi_fukugyo/status/2119064562284831078 (7 Nov 2026):
    alur 6 langkah membuat iklan anime 15 detik untuk pemula. Dibaca penuh
    lewat browser tanpa login, 15 Nov 2026 ~11:30 WIB.
- Isi skill adalah rangkuman dan adaptasi dengan kata-kata sendiri, bukan
  salinan teks postingan. Template prompt sutradara ditulis baru untuk Muse.
  Roadmap berbayar penulis di note.com tidak diambil isinya.
- Verifikasi saat pembuatan (15 Nov 2026):
  - Repo github.com/remotion-dev/skills: publik, 7.147 bintang, 13 sub skill.
  - Repo github.com/motion-canvas/motion-canvas: publik, MIT, 19.892 bintang.
  - 16 repo lainnya sesuai daftar di postingan, belum dicek satu per satu.
    Skill mewajibkan baca README sebelum pemakaian pertama.
  - Lingkungan VM: ffmpeg 8.1.2, Node v24.22.1, Python 3.12.3 tersedia.
    Blender dan Godot tidak terpasang.
  - scripts/stitch-clips.sh diuji dengan 2 klip sintetis 3 detik:
    hasil gabungan 6,02 detik, terverifikasi ffprobe.
- Penulis skill: Muse (dibuat baru, bukan impor dari katalog skill luar).

## Uji pertama: 15 Nov 2026 (Defence Steal & War)

- `media.generate_video` dicoba satu kali untuk klip pertama dan gagal 403
  (blokir wilayah, permanen). Temuan ini mengkonfirmasi ulang catatan
  5 Nov 2026. Tool itu tidak boleh dipanggil lagi untuk akun ini.
- Pivot ke Ken Burns ffmpeg (resep build2_fix.sh Housebets): video test
  15 detik, 1080x1920, 3 segmen 5 detik, musik latar sintesis lokal.
  Hasil: ~/workspace/video-gambar/defence-steal-war/defence-steal-war-2026-11-15.mp4
  (15,0 detik, 4.369.273 byte). QA 3 frame tengah tiap segmen lulus.
- SKILL.md, workflow-15-detik.md, dan scripts/kenburns-seg.sh diperbarui
  dengan temuan ini pada hari yang sama.
