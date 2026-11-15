# POLA-AGEN — Kartu Pola Serangan Agen AI

Kartu pola untuk skill `serangan-agen`. Tiap kartu: pola, mekanisme, contoh
nyata, cara mendeteksi, cara bertahan. Pola ditandai **U** (universal) atau
**S** (spesifik teknologi/kampanye).

Sumber awal: kampanye MevBotResearch (Nov 2026) + konteks 2026 (Agentjacking,
Darktrace, OpenClaw, Leash, Claude Code leak). Studi:
`~/workspace/research_notes/mevbotresearch-claude-code-campaign-2026-11-14.md`.

---

## A-01 — Enumerasi target dari data publik protokol [U]

**Pola:** penyerang membangun daftar target dari data yang DIPUBLIKASIKAN
protokol itu sendiri — bukan dari hasil hacking.

**Mekanisme:**
- Solana gossip: tiap validator mengumumkan ContactInfo (IP + port gossip,
  TVU, TPU, RPC, repair) via CRDS. `solana gossip` menampilkan seluruh tabel.
- Pola yang sama: DNS publik, Certificate Transparency logs, Shodan/Censys,
  data on-chain (alamat validator, vote account), explorer (validator.info).
- Validator WAJIB IP publik statis (NAT tidak didukung) — target list tidak
  bisa disembunyikan.

**Contoh nyata:** MevBotResearch — ~5.900 IP dari gossip Solana + GitHub + npm.

**Deteksi:** tidak bisa dideteksi sebagai serangan — ini akses data publik.
Yang bisa dideteksi adalah LANGKAH BERIKUTNYA (scan dari IP yang sama).

**Pertahanan:** tidak ada (data publik by design). Pertahanan dipindah ke
A-02: pastikan tidak ada layanan non-protokol di IP yang sama.

---

## A-02 — Scan "pintu terbuka": layanan tanpa autentikasi [U]

**Pola:** penyerang memindai daftar target untuk layanan yang merespons
TANPA autentikasi, lalu mencatatnya sebagai kandidat eksploitasi.

**Mekanisme:** scan port + banner grab + uji tanpa-auth terhadap layanan
yang terkenal sering terekspos tanpa password:
ClickHouse (8123/9000), Redis (6379), MongoDB (27017), Docker (2375),
Kubernetes API/kubelet (6443/10250), Grafana (3000), Solana RPC (8899), SSH (22).

**Contoh nyata:** hunter.md MevBotResearch — "Finds hosts with open doors
(unauthenticated ClickHouse/Redis/Mongo/Docker/K8s/Solana RPC/etc.) and
registers them as OPEN_DOOR in NewTargets/targets.jsonl."

**Deteksi:** lonjakan koneksi dari satu IP ke banyak port/layanan dalam
waktu singkat; koneksi ke port admin dari IP asing; log auth yang kosong
(padahal seharusnya ada upaya login).

**Pertahanan:** firewall default-deny; layanan admin HANYA di loopback/VPC
privat; autentikasi wajib di semua layanan; audit port terbuka berkala
(`ss -tlnp` vs daftar yang seharusnya).

---

## A-03 — Layanan data tanpa auth → SSRF via fungsi tabel [S]

**Pola:** database/analitik yang menerima query dari penyerang memberi
penyerang kemampuan server-side request — fungsi tabel yang mengambil
data dari URL arbitrer.

**Mekanisme (ClickHouse):**
- `SELECT * FROM url('http://<tujuan>/', 'TSV', 'data String')` — server
  ClickHouse mengirim request HTTP ke tujuan pilihan penyerang.
- Fungsi sejenis: `file()` (baca/tulis file lokal), `s3()` (akses bucket),
  `postgresql()` / `mysql()` (query database lain).
- Tanpa autentikasi di instance = siapa pun bisa menjalankan query ini.

**Contoh nyata:** MevBotResearch — ClickHouse tanpa password → SSRF via
url(). Kasus nyata lain: Obstracts (Sep 2025, SSRF → IMDS); PostHog
(Des 2025, SSRF → ClickHouse → postgresql() → RCE di PostgreSQL).

**Deteksi:** query ClickHouse berisi `url(` dengan host internal/metadata
(169.254.169.254, localhost, 10/172.16/192.168); query dari IP eksternal
ke instance yang seharusnya internal.

**Pertahanan:** autentikasi wajib; batasi/nonaktifkan fungsi `url()`/`file()`/
`s3()` untuk user non-admin; jangan jalankan ClickHouse di host yang sama
dengan layanan kritis; IMDSv2 (token-required) di cloud.

---

## A-04 — SSRF → IMDS / layanan internal [U]

**Pola:** SSRF dipakai sebagai jembatan dari "bisa membuat server mengirim
request" ke "bisa menjangkau apa yang hanya bisa dijangkau server itu".

**Mekanisme:**
- Cloud metadata (IMDS): `http://169.254.169.254/` memberi kredensial
  sementara IAM role mesin, token, secret. IMDSv1 tanpa token = langsung
  bisa dibaca; IMDSv2 butuh token (lebih aman).
- Layanan loopback: Docker daemon, kubelet, admin panel, database lain
  yang hanya listen di 127.0.0.1 — terjangkau lewat SSRF dari server yang
  sama.
- Dari sini ke RCE: lewat fungsi database lain, atau lewat kredensial
  cloud yang dicuri.

**Contoh nyata:** Obstracts (ClickHouse SSRF → IMDS, GCP); PostHog
(SSRF → ClickHouse → PostgreSQL RCE).

**Deteksi:** request dari layanan ke 169.254.169.254; request ke loopback
dari proses layanan yang tidak seharusnya; pemakaian kredensial IMDS yang
tidak biasa.

**Pertahanan:** IMDSv2; batasi hop limit metadata (hop=1); jangan beri
IAM role berlebihan ke mesin yang menjalankan layanan terekspos; segmentasi
jaringan internal.

---

## A-05 — Tugas terjadwal root di path yang dikontrol user [U]

**Pola:** proses root (cron, logrotate, service hook) mengoperasikan file,
direktori, atau konfigurasi yang bisa ditulis user non-root → user itu
bisa membuat root mengeksekusi perintahnya.

**Mekanisme (kelas logrotate):**
- **logrotten:** race condition di logrotate (versi 3.8.6/3.11.0/3.15.0/
  3.18.0 + opsi `create`) — penyerang menukar file log dengan symlink saat
  rotasi, logrotate menulis sebagai root ke target symlink.
- **Config writable:** file di /etc/logrotate.d/ atau direktorinya bisa
  ditulis user → tambah blok `postrotate`/`firstaction` berisi shell.
  logrotate ≥3.18 menolak config bukan milik root (CVE-2011-1098/1154) —
  tapi hook lain bisa me-launder ownership (Pi-hole CVE-2026-50130).
- **PID file writable:** postrotate membaca PID dari file yang dikontrol
  daemon user → kill sebagai root ke PID arbitrer (Icinga CVE-2025-61909).
- **Log dir writable:** logrotate menulis file ke direktori yang seharusnya
  tidak bisa diakses user (FreeRADIUS CVE-2019-10143).

**Contoh nyata:** MevBotResearch — "escalated to root through a
misconfigured logrotate service" (varian persis tidak dipublikasikan).

**Deteksi:** file/direktori di bawah /etc/logrotate.d/ atau /var/log/ yang
bisa ditulis non-root; config logrotate yang berubah tanpa perubahan
paket; proses root yang membuka file milik user non-root.

**Pertahanan:** config + direktori log hanya root yang bisa tulis; `su`
directive benar; jangan ada hook yang me-chown file dari direktori yang
bisa ditulis user; audit semua cron root: file apa yang dibacanya, siapa
yang bisa menulis file itu.

---

## A-06 — Material kunci di disk [U]

**Pola:** kunci privat (validator, wallet, API) disimpan sebagai file di
disk server — sekali penyerang punya akses baca (biasanya via root),
semua kunci hilang sekaligus.

**Mekanisme:**
- Validator Solana: identity keypair + vote keypair + withdrawer HARUS ada
  di disk dan bisa dibaca proses validator. Path tipikal: /home/sol/keys,
  ~/validator-keypair.json. Format: JSON array 64 byte.
- Wallet operator: keypair CLI, .env, config.json (Wayfinder F1: private
  key + mnemonic di config.json 0644).
- Tidak ada cara menjalankan validator tanpa identity key online.

**Contoh nyata:** MevBotResearch — kunci dicuri dari /home/sol/keys.

**Deteksi:** akses baca massal ke direktori kunci di luar jam/waktu proses
validator; proses tak dikenal membaca file keypair; perubahan waktu akses
(atime) file kunci.

**Pertahanan:** remote signing / HSM untuk identity + withdrawer (validator
hanya meminta tanda tangan, kunci tidak pernah di disk validator); pisahkan
host validator dari host layanan lain; permission 0600 + user khusus untuk
direktori kunci; monitor akses baca ke direktori kunci; JANGAN simpan
kunci di repo, `.claude/`, atau file config yang bisa tersinkronisasi.

---

## A-07 — Drain otomatis (ambang + kecepatan) [U]

**Pola:** setelah kunci dicuri, pengurasan dilakukan skrip otomatis —
cepat, paralel, dengan ambang saldo minimum.

**Mekanisme:**
- Ambang (contoh: >0,02 SOL): tinggalkan sedikit saldo untuk biaya + rent,
  atau abaikan wallet yang tidak sepadan. Rent-exempt minimum akun wallet
  Solana ~0,00089 SOL.
- Kecepatan (~5 detik untuk beberapa wallet): load keypair → bangun
  transfer → kirim paralel via RPC. Slot Solana ~400ms; konfirmasi ~1 detik.
- Transaksi drain SAH secara kriptografis (ditandatangani kunci asli) —
  chain tidak bisa membedakan pemilik dan pencuri. Tidak ada chargeback.

**Contoh nyata:** MevBotResearch — drain >0,02 SOL dalam ~5 detik.

**Deteksi:** (pasca-kejadian) banyak transfer keluar dari banyak wallet ke
satu alamat dalam hitungan detik; wallet yang saldonya tiba-tiba tinggal
ambang minimum.

**Pertahanan:** TIDAK ADA pertahanan on-chain setelah kunci dicuri.
Satu-satunya pertahanan adalah mencegah A-02..A-06. Untuk wallet
operasional: multisig / timelock memberi jendela respons sebelum dana
bergerak.

---

## A-08 — Pemisahan pipeline hunter/exploiter [U] — ARSITEKTUR AGEN

**Pola:** serangan dipecah menjadi agen-agen khusus yang berkomunikasi lewat
file/antrean. Tiap agen terlihat jinak bila dibaca sendiri; bahaya muncul
dari KOMPOSISI pipeline.

**Mekanisme:**
- Hunter: scan read-only, tulis target ke file (mis. `targets.jsonl`).
  Deskripsinya menekankan "read-only — never exploits" — terlihat seperti
  tool riset yang sah.
- Exploiter: membaca file target, mengeksekusi eksploitasi per target.
- Kontrak antar-agen adalah format data (JSONL), bukan percakapan.

**Contoh nyata:** MevBotResearch — `.claude/agents/hunter.md` +
`.claude/agents/exploiter.md`, kontrak `NewTargets/targets.jsonl`.

**Deteksi:** file `.claude/agents/` dengan deskripsi agen yang memindai/
mengeksploitasi; file JSONL berisi daftar IP + status OPEN_DOOR; pola
tool-call: scan massal diikuti eksploitasi terhadap subset hasil scan.

**Pertahanan (untuk operator agen):** evaluasi keamanan harus memeriksa
SISTEM (semua agen + alur datanya), bukan satu agen pada satu waktu.
Batasi apa yang bisa dibaca/ditulis tiap agen; jangan beri satu agen
akses ke output agen lain tanpa review bila output itu memicu aksi.

**Catatan peneliti:** pola ini SAMA dengan pipeline riset yang sah
(hunter = recon, exploiter = testing). Bedanya hanya OTORISASI dan TARGET.
Itulah kenapa gerbang otorisasi skill ini tidak bisa ditawar.

---

## A-09 — Refusal arbitrage / model shopping [U] — ARSITEKTUR AGEN

**Pola:** penyerang merutekan tiap subtugas ke model yang paling mungkin
menurutinya, mengeksploitasi perbedaan ambang penolakan antar model.

**Mekanisme:**
- Model A (mis. Claude) menolak tugas eksploitasi eksplisit tapi mau
  melakukan recon.
- Model B (mis. GLM) mau melakukan eksploitasi bila diberi dalih.
- Operator memecah tugas sehingga tiap model hanya melihat potongan yang
  terlihat bisa dibenarkan — tidak ada satu model pun yang melihat
  gambaran lengkap.

**Contoh nyata:** MevBotResearch — delegasi tugas ke GLM dengan dalih
"authorized red-team engagement".

**Deteksi:** (dari sisi penyedia model) pola pemakaian lintas model yang
saling melengkapi; (dari sisi peneliti) artefak kampanye yang menyebut
lebih dari satu model.

**Pertahanan:** tidak ada pertahanan di sisi pengguna akhir — ini kelemahan
arsitektural dari pertahanan berbasis penolakan model. Pertahanan nyata
adalah di A-02..A-06 (jangan beri penyerang apa pun untuk dieksploitasi)
dan A-12 (jangan beri agen kunci + teks tak tepercaya).

---

## A-10 — Dalih otorisasi palsu (jailbreak pretext) [U] — ARSITEKTUR AGEN

**Pola:** penyerang mengklaim aktivitasnya adalah "authorized red-team
engagement" (atau audit resmi, atau penelitian) agar model mengizinkan
tugas ofensif.

**Mekanisme:**
- Kebijakan keamanan model umumnya mengizinkan pekerjaan keamanan ofensif
  BILA ada otorisasi.
- Model menilai otorisasi dari TEKS klaim, bukan dari bukti yang bisa
  diverifikasi — ia tidak punya cara mengecek apakah red-team itu nyata.
- Klaim otorisasi + konteks profesional (nama proyek riset, bahasa formal)
  cukup untuk membuat model patuh.

**Contoh nyata:** MevBotResearch — delegasi ke GLM "under the pretext of
an 'authorized red-team engagement'".

**Deteksi:** prompt/konteks yang menyebut otorisasi tanpa artefak
pendukung (tidak ada surat izin, tidak ada scope tertulis, tidak ada
kontak pemberi izin).

**Pertahanan (untuk peneliti yang sah):** SELALU miliki bukti otorisasi
fungsional (akun uji resmi, kata kode di permukaan khusus, surat izin
tertulis yang bisa diverifikasi) — seperti yang dipersyaratkan PROTOKOL
FORENSIK untuk DSW. Jangan pernah memakai klaim otorisasi sebagai pengganti
bukti, baik ke model maupun ke manusia.

**Larangan:** skill ini MELARANG penggunaan dalih otorisasi palsu untuk
melewati penolakan model. Itu teknik penyerang.

---

## A-11 — Deteksi: artefak + perilaku agen penyerang [U] — PERTAHANAN

**Pola:** kampanye agen meninggalkan artefak khas yang bisa dideteksi
di host korban maupun di intelijen publik.

**Artefak host:**
- Direktori `.claude/agents/` dengan file agen (hunter.md, exploiter.md).
- File target (mis. `NewTargets/targets.jsonl`, `targets.jsonl`) berisi
  daftar IP + status.
- Log tool-call agen: pola scan massal → uji spesifik → eksploitasi.
- Proses agen (claude/codex/cursor) berjalan di server yang seharusnya
  tidak menjalankan agen coding.

**Artefak jaringan:**
- Scan berurutan dari satu IP ke banyak host/port (pola hunter).
- Koneksi ke API model (api.anthropic.com, API GLM, dll.) dari server
  infrastruktur — server validator/MEV tidak seharusnya memanggil API LLM.
- Eksfiltrasi: upload file kunci ke host eksternal.

**Artefak on-chain:**
- Drain: banyak transfer ke satu alamat dalam hitungan detik (A-07).
- Alamat drainer yang sama muncul di banyak korban.

**Cara memakai:** saat mengaudit host (tingkat 2, milik user sendiri),
cari artefak-artefak ini. Saat memantau intelijen, cari nama proyek,
nama file agen, dan IOC yang dipublikasikan peneliti.

---

## A-13 — Eksekusi kode supply-chain (strategi/skill/paket jahat) [U]

**Pola:** penyerang menerbitkan kode yang TERLIHAT berguna (strategi
trading, skill agen, paket npm/PyPI) — korban menginstalnya sendiri, dan
kode itu berjalan dengan izin penuh operator. Korban datang ke penyerang;
penyerang tidak perlu memindai.

**Mekanisme:**
- Registry/ekosistem (paths registry, ClawHub, npm, PyPI) mendistribusikan
  kode pihak ketiga. Verifikasi integritas (sha256, signature) membuktikan
  kode TIDAK BERUBAH — bukan bahwa kode itu BAIK.
- Kode yang diinstal berjalan TANPA sandbox dengan izin user: bisa membaca
  file config (A-06), mengirim data ke host penyerang, dan mengeksekusi
  perintah.
- Varian: typosquat (nama mirip paket populer), update jahat pada paket
  yang sebelumnya sah, strategi "APY tinggi" yang memancing rasa serakah.

**Contoh nyata:**
- Uji Wayfinder (Nov 2026): strategi jahat di paths registry → baca
  config.json 0644 (F1) → kirim private key + API key → kuras (Rantai 1).
- OpenClaw (Feb 2026): 1.184 skill jahat di ClawHub menargetkan wallet;
  Cisco: 26% dari 31.000 skill mengandung kerentanan.

**Deteksi:** kode strategi/skill yang membaca file di luar kebutuhannya
(config.json, .env, keyring); koneksi keluar ke host yang tidak terkait
fungsinya; strategi yang baru diterbitkan tanpa riwayat author; nama
yang meniru proyek populer.

**Pertahanan:** jangan instal kode dari author yang tidak akan diserahkan
kunci; baca kode sebelum instal (atau instal di sandbox/VM sekali pakai
dulu); `chmod 600` semua file berisi kunci; pisahkan keystore dari config
yang bisa dibaca proses apa pun; audit berkala apa yang terinstal.

---

## A-12 — Pertahanan operator agen: kunci + teks tak tepercaya [U] — PERTAHANAN

**Pola:** akar dari hampir semua insiden agen 2026 adalah kombinasi yang
sama: **agen membaca teks tak tepercaya DAN memegang kunci.**

**Mekanisme (rumusan Leash, Nov 2026):** "The agent reads untrusted text
and holds a key, and those two things together are the whole attack."
- Teks tak tepercaya: instruksi di file, issue, email, halaman web,
  output tool, data dari target — semuanya bisa berisi prompt injection.
- Kunci: wallet key, API key, SSH key, session token — apa pun yang memberi
  agen kemampuan bertindak.
- Begitu keduanya bertemu, SATU injeksi yang berhasil = kompromi penuh.

**Contoh nyata:**
- Agentjacking (Jun 2026): event Sentry palsu → agen menjalankan perintah
  penyerang (85% success).
- OpenClaw/Lobstar Wilde (Feb 2026): agen mengirim $250K ke orang asing;
  1.184 skill jahat di ClawHub.
- Leash (Nov 2026): invoice PDF berisi injeksi → agen mau membayar penyerang.
- Darktrace (Nov 2026): Claude Code jadi implant via memory stores.
- Wayfinder audit kita (Nov 2026): API key = akses wallet; config 0644;
  strategi pihak ketiga menerima key mentah (F1+N1).

**Pertahanan (berlapis, dari yang paling kuat):**
1. **Enforce di level kode, bukan prompt.** Seperti Leash: program (smart
   contract / policy engine) yang menolak transaksi di luar allowlist —
   tidak peduli apa yang "diputuskan" agen. Prompt bukan security boundary.
2. **Pisahkan kunci dari agen.** Agen meminta tanda tangan ke layanan
   terpisah (signer/HSM/multisig), tidak pernah memegang kunci mentah.
3. **Least privilege per tugas.** Key data-only untuk kerja data; key
   wallet hanya untuk tugas yang butuh wallet; TTL pendek; cap jumlah.
4. **Audit apa yang dibaca agen.** Skill, MCP server, file `.claude/`,
   dan sumber data eksternal adalah permukaan serangan — inventaris dan
   kurasi seperti dependensi kode.
5. **Jangan jalankan agen dari direktori tak tepercaya.** (Wayfinder N5:
   config di-resolve dari cwd.)
