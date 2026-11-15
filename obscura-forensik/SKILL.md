---
name: obscura_forensik
description: Pemeriksaan keamanan link dan rekon Tier-0 berbasis browser headless Obscura: cek anti-phishing/anti-scam sebelum klik atau mint, bedah frontend sebelum forensik kontrak, dan tangkap bukti screenshot untuk laporan. Pakai skill ini setiap kali user mengirim link yang harus diverifikasi, saat butuh rekon permukaan web target bounty, atau saat menyiapkan bukti visual untuk laporan bug bounty.
---

# Obscura Forensik — Mata Browser untuk Skill Forensik

Obscura adalah browser headless Rust (V8 + CDP, tanpa Chromium) yang sudah
dibangun di VM ini. Skill ini memakainya sebagai **lapisan mata**: membuka
halaman seperti browser sungguhan (render JavaScript, tangkap network dan
screenshot), lalu menyerahkan temuannya ke skill forensik yang sudah ada.
Obscura tidak menggantikan analisis — ia memberi bahan yang sebelumnya buta
bagi tool CLI (curl tidak melihat DOM hasil render).

Binary: `/home/hatch/workspace/obscura/target/release/obscura`
(+ `obscura-worker` untuk `scrape` paralel), versi `0.1.0-dev+196d10c`,
fitur render. Varian stealth TIDAK dibangun (butuh clang/libclang-dev).

## Kapan memakai skill ini

- **Cek keamanan link** sebelum user mengklik atau mint apa pun — ini
  kegunaan utamanya (anti-phishing / anti-scam). Setiap link dari chat,
  grup Telegram, atau X yang mengarah ke mint/claim/airdrop WAJIB dicek
  dulu lewat `obscura_linkcheck.py`.
- **Rekon Tier-0** untuk target bounty (skill `bug-hunter` fase 1): peta
  permukaan web — link, aset, host eksternal, bundle script, form.
- **Bedah frontend sebelum forensik kontrak** (skill `forensik_kontrak`
  fase 0): ambil kontrak yang dinyatakan situs/docs, bandingkan dengan
  yang on-chain. Sesuai doktrin "bedah dulu": jangan menyimpulkan dari
  tebakan, petakan semua jalur.
- **Bukti screenshot** untuk laporan (Immunefi / XE / QoreChain): capture
  keadaan halaman sebagai lampiran PoC.

## Gerbang otorisasi 3-tier (warisan pentest-web, berlaku penuh)

- **Tier 0 — Pasif.** Membuka halaman publik, dump link/aset/teks,
  screenshot, eval read-only. Selalu diizinkan. Kedua script di skill ini
  HANYA Tier 0: tidak ada payload, login, submit form, atau perubahan
  state apa pun.
- **Tier 1 — Probe aman di akun sendiri.** Hanya di akun milik user / akun
  uji yang disediakan tugas, dan hanya aset in-scope. Misalnya menguji
  alur claim di dApp dengan wallet user — tetap butuh persetujuan nominal
  seperti biasa.
- **Tier 2 — Probe aktif.** Payload injeksi, akses objek akun lain,
  perubahan state, race request. HANYA dengan otorisasi tertulis
  (cakupan program bounty yang mengizinkan teknik itu, atau perintah
  tertulis pemilik). Di workspace ini frasa user **"lakukan simulasi
  nyata"** adalah gerbang Tier 2. Tanpa itu, berhenti di Tier 1 dan
  laporkan kandidat + rencana uji.
- **Larangan keras:** eksploitasi mainnet, menyentuh dana/data pengguna
  lain, menyimpan nilai PII pihak ketiga (catat keberadaan dan bentuknya,
  jangan nilainya), melanjutkan setelah program menyatakan out-of-scope.

## Script 1 — Cek link: obscura_linkcheck.py

```bash
python3 ~/workspace/custom-skills/obscura-forensik/scripts/obscura_linkcheck.py <URL> \
  [--source chat|dashboard|telegram-guard] \
  [--out-dir /home/hatch/workspace/obscura-guard/checks] \
  [--id <id-record>]
```

`--id` dipakai saat memproses antrean dashboard: isi dengan id record
PENDING dari `listPendingChecks` agar hasil submit menimpa baris antrean
itu, bukan membuat record duplikat. Tanpa `--id`, script membuat id baru
otomatis.

Alur (semua read-only): fetch halaman lewat Obscura (judul, HTML hasil
render, link, aset, screenshot) → ekstrak alamat EVM + form + ajakan
"connect wallet" → cek domain → cek kontrak → verdict + skor → tulis
record.

**Cek domain:** punycode (`xn--`), lookalike vs daftar resmi terkurasi
(binance.com, bnbchain.org, pancakeswap.finance, uniswap.org, bscscan.com,
etherscan.io, coingecko.com, coinmarketcap.com, binance.us) lewat jarak
edit kecil atau trik substring merek, daftar mirror terverifikasi
(bmwweb.biz/.me/.cloud/.academy, bsmkweb.com, marketwebb.io), http-only,
host berupa IP mentah.

**Cek kontrak (per alamat EVM yang ditemukan):** cocokkan dengan blocklist
pabrik spam `~/workspace/tools/crowd-scan/blocklist.json` (READ-ONLY —
script ini tidak pernah menulisnya; 57 operator, 781 alamat unik dari
deployer + operator + token + distributor + contract + daftar contracts),
lalu cek
`eth_getCode` BSC via curl ke `https://bsc-dataseed.binance.org/`. Bila RPC
gagal, `has_code=null` dan dicatat — pemeriksaan tidak gagal karenanya.

**Semantik verdict (skor risiko 0–100):**

| Verdict | Syarat | Skor |
|---|---|---|
| BLOKIR | Kontrak masuk blocklist ATAU domain mirror terverifikasi | 61–100 |
| WASPADA | Punycode, lookalike, http-only, host IP, atau alamat tanpa code | 21–60 |
| AMAN | Tidak ada temuan di atas dan fetch berhasil | 0–20 |
| GAGAL | Fetch gagal dan tidak ada temuan BLOKIR | null |

Urutan didahulukan: kecocokan BLOKIR yang bernama (mirror / kontrak
ter-blocklist) adalah fakta tentang domain/alamat dan tetap berlaku walau
fetch gagal — kegagalan fetch dicatat di `notes`.

**Aturan bukti (tidak bisa ditawar): inferensi bukan fakta.** WASPADA
adalah peringatan, bukan bukti penipuan — domain http-only atau alamat
tanpa code bisa jadi proyek sah yang ceroboh; sampaikan sebagai "patut
dicurigai, alasan: ..." dan jangan pernah menyebutnya scam tanpa bukti
tambahan. BLOKIR butuh kecocokan bernama (operator + proyek blocklist,
atau nama mirror) yang tertulis di record. Bila ragu, naikkan ke user
dengan bukti apa adanya, bukan dengan label yang dilebihkan.

**Output:** `<out-dir>/<id>.json` (record lengkap), baris JSON di
`<out-dir>/checks.jsonl`, screenshot `<out-dir>/<id>.png` bila berhasil
diambil. `id` berformat `chk_YYYYMMDD_HHMMSS_<6 hex>`. Exit 0 walau
BLOKIR (verdict adalah data); exit 1 hanya bila record tidak bisa
ditulis sama sekali.

Skema record (dipakai dashboard — jangan ubah nama key): `id`, `url`,
`domain`, `checked_at` (ISO-8601 UTC), `checked_at_wib`
(`YYYY-MM-DD HH:MM WIB`), `verdict`, `score`, `reasons` (list
`{code, severity, detail}`), `title`, `contracts` (list `{address,
chain, has_code, blocklisted, blocklist_operator, blocklist_project}`),
`domain_flags`, `links_count`, `assets_count`, `screenshot`, `source`,
`notes`.

## Script 2 — Rekon Tier-0: obscura_recon.py

```bash
python3 ~/workspace/custom-skills/obscura-forensik/scripts/obscura_recon.py <URL> \
  [--out-dir /home/hatch/workspace/obscura-guard/recon]
```

Fetch satu URL publik, tulis laporan permukaan ke
`<out-dir>/<domain>_<YYYYMMDD_HHMMSS>.json`: `url`, `domain`,
`fetched_at`, `title`, `links[]`, `assets[]`, `external_hosts[]`,
`scripts[]` (URL bundle script), `forms_count`, `emails[]`, `notes`.
Hasilnya adalah **daftar permukaan yang diprioritaskan, bukan temuan** —
teruskan ke `bug-hunter` fase 1 atau `forensik_kontrak` fase 0/1.
Exit 0 bila laporan tertulis, 1 bila semua fetch gagal.

## Script 3 — Jelajah: obscura_browse.py

```bash
python3 ~/workspace/custom-skills/obscura-forensik/scripts/obscura_browse.py <URL> \
  [--source dashboard] [--id <id-antrean>] \
  [--out-dir /home/hatch/workspace/obscura-guard/browse]
```

Fetch satu halaman untuk tab Jelajah dashboard: judul, isi teks hasil
render (maks 8.000 karakter), daftar link (maks 100, dengan teks
jangkar), screenshot PNG penuh + thumbnail JPEG 800px (via Pillow;
bila PIL tidak ada, thumbnail dilewati). Record 14 kunci ditulis ke
`<out-dir>/<id>.json` (+ `<id>.png`, `<id>_thumb.jpg`, `browse.jsonl`),
status `SELESAI` atau `GAGAL`. `--id` diisi id PENDING dari
`listpendingbrowse` agar submit menimpa baris antrean itu.

Saat submit ke dashboard (`submitbrowseresult`): kirim 13 kunci
(tanpa `screenshot_thumb`), dengan `screenshot` berupa data URL
thumbnail bila ada, data URL PNG penuh bila tidak, atau null.

## Alur hasil

- Cek link → `~/workspace/obscura-guard/checks/` (`<id>.json` +
  `checks.jsonl` + `<id>.png`) → dibaca dashboard Obscura Guard.
- Rekon → `~/workspace/obscura-guard/recon/` (`<domain>_<timestamp>.json`).
- Jelajah → `~/workspace/obscura-guard/browse/` (`<id>.json` +
  `browse.jsonl` + `<id>.png` + `<id>_thumb.jpg`) → disubmit ke
  dashboard lewat `submitbrowseresult`.
- Bila cek menemukan kandidat temuan bounty (bukan sekadar link scam):
  teruskan alamat/kontraknya ke `forensik_kontrak` (bukti fork read-only)
  atau `bug-hunter` (gerbang 7 pertanyaan sebelum menulis laporan).

## Sinkronisasi snapshot blocklist ke dashboard

Blocklist sumber (`~/workspace/tools/crowd-scan/blocklist.json`) bersifat
READ-ONLY dan tidak pernah diubah. Dashboard Obscura Guard tidak membaca
sumber itu langsung — ia membaca **snapshot ternormalisasi** di
`~/workspace/obscura-guard/blocklist_snapshot.json`.

**Normalisasi wajib sebelum sync:** sumber blocklist punya 13 proyek
dengan `name: null`, sementara action `syncblocklist` dashboard
mengharuskan setiap nama proyek berupa string. Sebelum sinkronisasi,
ganti setiap nama proyek `null` dengan placeholder
`"(nama tidak tercatat)"`. Tanpa langkah ini sync gagal.

Regenerasi snapshot (baca sumber, tulis snapshot — sumber tidak disentuh):

```bash
python3 ~/workspace/custom-skills/obscura-forensik/scripts/build_blocklist_snapshot.py
```

Script itu menangani semua varian skema sumber: daftar `projects`
(nama bisa `null`, alamat bisa di `token` atau `contract`), daftar
`contracts` datar (tiga entri, dua di antaranya tanpa kunci `projects`
sama sekali — kontrak datar diubah menjadi proyek bernama placeholder),
dan field `operator` yang berbeda dari alamat deployer. Jangan
menyalin mentah sumber ke snapshot: dashboard mengharapkan bentuk
`{operators, total_addresses, updated_at}`, bukan bentuk mentah
`{deployers, notes, rule, version}`.

Regenerasi snapshot setiap kali blocklist sumber berubah (operator/proyek
baru), lalu verifikasi: 0 nama `null` dan 0 nama non-string tersisa di
snapshot sebelum menjalankan `syncblocklist`. Acuan terakhir yang
terverifikasi: 57 operator, 712 proyek, 781 alamat unik (2 entri sumber
malformed 39 karakter, tidak dihitung).

## Referensi cepat Obscura CLI / MCP / CDP

Di VM ini **setiap fetch WAJIB** memakai `--allow-private-network` (atau
`OBSCURA_ALLOW_PRIVATE_NETWORK=1`): proxy egress resolve ke alamat ULA
privat yang diblokir gate SSRF Obscura tanpanya. Proxy env sudah ter-set
di shell dan diwariskan ke subprocess.

```bash
B=~/workspace/obscura/target/release/obscura
$B --allow-private-network fetch https://example.com --eval "document.title"
$B --allow-private-network fetch https://example.com --dump links      # html|text|links|markdown|assets|original|cookies
$B --allow-private-network fetch https://example.com -s page.png      # screenshot (butuh fitur render)
$B --allow-private-network scrape <url...> --eval "..." --format json  # paralel, pakai obscura-worker
$B --allow-private-network serve --port 9222                            # server CDP untuk Puppeteer/Playwright
$B --allow-private-network mcp                                          # server MCP (stdio)
$B --allow-private-network mcp --http --port 8080                       # server MCP (HTTP, endpoint /mcp)
```

Catatan gotcha: `--eval` multi-statement yang diawali `const`/`let`
mengembalikan `null` di V8 — bungkus snippet dalam IIFE
`(function(){ ...; return hasil; })()`. `--dump` dan `--eval` bisa
digabung dalam satu panggilan, tapi stdout hanya memuat dump-nya; judul
halaman terbaca dari baris banner `Page loaded: <url> - "<judul>"` —
yang keluar di **stderr** bila kedua stream ditangkap terpisah (hanya
kelihatan seperti stdout di bawah `2>&1`). Kedua script di skill ini
mem-parsing judul dari gabungan stdout+stderr; pesan error navigasi juga
ada di stderr, jadi deteksi gagal harus memeriksa kedua stream.
`--dump links` mengeluarkan `URL<TAB>teks` per baris; `--dump assets`
mengeluarkan NDJSON satu objek per baris.

Tool MCP: `browser_navigate`, `browser_snapshot`, `browser_screenshot`,
`browser_pdf`, `browser_click`, `browser_fill`, `browser_type`,
`browser_press_key`, `browser_select_option`, `browser_evaluate`,
`browser_wait_for`, `browser_network_requests`, `browser_console_messages`,
`browser_close`. Screencast streaming hanya lewat CDP
(`Page.startScreencast`).

## Skill terkait

- `forensik_kontrak` — bedah keamanan kontrak, pola serangan, PoC fork.
- `bug-hunter` — alur bounty end-to-end (Recon → Learn → Hunt → Validate
  → Report) + gerbang 3-tier.
- `pentest-web` — 26 kartu pola web (W-01..W-26), otoritas gerbang tier.
- `multichain-contract-audit` — audit mint multi-chain (gerbang exit,
  holder, LP lock, privilege).
