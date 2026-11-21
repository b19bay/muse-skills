# Simular Box Browsing

## When to use

Use Simular Box ONLY when the normal route is blocked by Cloudflare or an IP based block. This is a standing user rule from 2026-11-20: box is the fallback, never the default. Always try the Muse browser, `browser.open`, or `browser.search` first, and switch to the box only after a block is proven.

Use it when a site blocks the Muse cloud browser or `browser.open` with a 403, a bot wall, or a rate limit caused by the shared egress IP. Box is a cloud Linux desktop with its own Chrome and its own IP, so it reaches pages the Muse browser cannot.

Proven 2026-11-20: X returned HTTP 403 to the Muse cloud browser from the shared egress, and the syndication endpoint answered rate limit exceeded. The same post loaded fine through `browser_fetch` on the box.

## How it works

Box is reached through the custom connector `custom.simular-box-mcp`. The helper is `~/workspace/custom-connectors/custom.simular-box-mcp/bin/client.py` with `list-tools` and `call-tool` commands. Read the connector doc for exact commands and the allowed tool set.

The usual flow for reading a blocked page:

1. Wake the box with `box_ensure` and wait for state `running`.
2. Read the page with `browser_fetch` first. It loads the URL in a hidden tab and returns plain text, with no GUI steps.
3. When the page needs interaction, open it with `browser_navigate`, read with `browser_read`, and refresh elements with `browser_snapshot`.
4. Hibernate the box with `box_hibernate` when done. This stops the meter.

## Cost discipline

The free box costs 100 credits an hour and the account starts with 5000 free credits, about 50 hours, valid 90 days. Always hibernate after the work. Check `billing` before a long session and `usage` after one when the spend matters.

## Limits

Box does not solve CAPTCHAs. When a page needs a sign-in, 2FA, a captcha, or a payment, hand the user the box `view_url` and wait until they say they are done.

The free box uses a datacenter IP. Residential IP is paid only. A datacenter IP still differs from the Muse egress IP, so it clears most shared IP blocks, but a site that blocks all datacenter IPs will still refuse it.

Only the tools in the client `ALLOWED_TOOLS` set may run. Shell, file writes, clicks, typing, and box creation and deletion stay blocked until reviewed for a specific task and authorized by the user.

## Available connectors

- [Simular Box Mcp](~/workspace/custom-connectors/custom.simular-box-mcp/CONNECTOR.md)
