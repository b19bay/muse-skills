# Local amendment — binance-square-post (Muse)

Upstream files in this folder (`SKILL.md`, `README.md`, `scripts/`) are
verbatim from Binance's official skills hub
(`github.com/binance/binance-skills-hub`, `skills/binance/square-post`,
v2.0.0, installed 2026-11-21, sha256-verified against the repo). Do not
edit them; put local adaptations here.

## Auth here is NOT the upstream env/file flow

The upstream skill reads the key from `BINANCE_SQUARE_OPENAPI_KEY` or
`~/.config/binance-square/openapi-key`. **Do not use either here.** Both
accounts' posting-only keys live in Muse's Secure Vault behind the
registered connectors `custom.binance-square` (main, lail.ai) and
`custom.binance-square-b19` (akun 2, b19.ai). Never write a key to disk,
never pass a key (or a surrogate) as a CLI argument, never print one.

- **Text posts:** use the connector's Python client (proven path, no Node):
  `python3 ~/workspace/custom-connectors/custom.binance-square/bin/client.py post --text "..."`
  (b19: same path under `custom.binance-square-b19/`).
- **Image/video posts:** use the per-connector launcher, which fetches only
  an `hsurr:` surrogate from the vault and hands it to the official Node
  scripts via the child process environment:
  `python3 ~/workspace/custom-connectors/custom.binance-square/bin/post-media.py image --text "..." --images "./a.png,./b.png"`
  `python3 ~/workspace/custom-connectors/custom.binance-square/bin/post-media.py video --video "./v.mp4" [--duration S] [--text "..."]`
  (b19: same path under `custom.binance-square-b19/`.)
  The launcher validates files first, measures video duration with
  `ffprobe` when `--duration` is omitted, and streams the scripts'
  output through. `save-key.mjs` is NOT used here.

## Verified live 2026-11-21

- Node v24.22.1, ffmpeg/ffprobe 8.1.2 present on the VM.
- Node `fetch` reaches `www.binance.com` directly (no proxy flag needed).
- Surrogate → Node swap works for BOTH accounts: `/image/presignedUrl`
  (v2 media endpoint) returned a presigned URL + fileTicket for both keys
  — both keys valid, media path proven without publishing anything.
- Scripts audited before install: they only call
  `www.binance.com/bapi/composite/v1|v2/public/pgc/openApi` plus the
  presigned S3 upload URLs the API returns. No other hosts, no key
  exfiltration, keys masked in output.

## Routine posting includes self-made media (since 2026-11-21 ~19:20 WIB)

The two routines (`square-posting-routine-lail`,
`square-posting-routine-b19`) run every 2 hours, 12 posts/day per
account (6 COIN + 6 TREND, alternating). By explicit user order
("gambar dan video kamu buat aja sendiri sesuai dengan tema
postingan"), each routine post carries self-made media: COIN posts get
1 image from `media.generate_image` (thematic, no text/numbers in the
image); TREND posts get a 7-second ffmpeg Ken Burns clip (1080x1080)
rendered from that image. Media is posted via `post-media.py` (`image`
/ `video` subcommands); if media generation or upload fails, the run
falls back to a text-only post via `client.py` — a failed medium never
cancels the post. `media.generate_video` is REGION-BLOCKED 403 for this
account: never call it; routine video is ffmpeg motion clips only. The
upstream "do not auto-attach" rule is overridden here by the user's
explicit standing order to generate media per post. Media files live in
each goal's `hidden_files/media/` and are cleaned up after 7 days.

## Limits (from the official skill)

100 posts/day/key, 400 uploads/day. Max 4 images per post; article cover
is exactly 1 image; max 1 video per post; images and video are mutually
exclusive. HTTP 504 from `/content/add` = accepted, never retry.
