# CreditLens design

**World: the sanction note.** The reader is a credit analyst at a desk in daylight, reading figures for long stretches. The page reads like a bank credit paper: crisp white stock, cool-grey ledger panels, deep navy ink, ruled tables, and approval-stamp colours that carry meaning only. It is deliberately unlike the author's dark portfolio, so the tool reads as a product rather than a personal site.

| Token | Value | Use |
|---|---|---|
| paper | `#ffffff` / `#f6f7f9` / `#eef1f5` | work area / file rail / evidence rail |
| ink | `#0f1f3d` | text, primary actions, masthead rule |
| pass / watch / fail | `#1d7a4c` / `#a35f00` / `#b42318` | verified, watch-list, hard fail only |
| citation | `#2453a6` | `S#` source references |
| highlighter | `#fff1b8` | verified figures inside a source |
| type | Source Serif 4 (headings, verdicts), Public Sans (UI), JetBrains Mono (figures, sources) | self-hosted in `web/fonts` |

Signature moments: hover a claim → the evidence rail dims all but the cited page and highlighter-marks the verified figures. The memo carries a rubber stamp (Approved / Conditional / Referred / Declined).
Files: `web/ui.css` (shared structure), `web/app.css` (layout), `web/theme.css` (this world).
