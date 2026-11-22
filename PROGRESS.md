# news-image-20261122 — PROGRESS

## Entry
- Competition: news-image-20261122 — "Sum up 22 November's world news in one image" ($100, Growth). Deadline 2026-11-24T00:00Z.
- Program: `main.py` (pure Python standard library only: os, struct, zlib, math — the grader installs nothing, so no Pillow). Draws a 1024x1024 newspaper poster "THE WORLD TODAY — Sunday 22 November 2026" with a hand-made 5x7 bitmap font and a hand-rolled PNG encoder.
- Output: `/output/entry.png`, 21,212 bytes (< 1 MiB), 1024x1024.
- Determinism verified: 2 runs byte-identical, SHA-256 `06df62a61aae64d6c1a5532dc3cd23de65fc4f4c81fb8ff13d01264bd9b049cb` (final version, after layout fixes).
- Poster checked visually: masthead, lead story (Iran–Bahrain) with Gulf schematic panel, 4 story cards (Ukraine, EU–Indonesia trade, COP31, Mexico), "Also today" strip (ATP Finals, Gaza aid, Eisenkot, France protests), sources footer. No clipped or overflowing text.

## Headlines (verified 22 Nov 2026 via web search)
- Lead: Iran strikes US assets in Bahrain — missiles hit an industrial facility; air defences intercept other attacks (Reuters via huddleworld; AppiSToS; cryptoeconomics.tech digest).
- Russia hits Lviv and Kryvyi Rih — at least 2 killed in Lviv; 58 hurt in Zelensky's home city, 6 of them children (AppiSToS; cryptoeconomics.tech; japako.pl).
- EU and Indonesia sign landmark trade deal — ten years of talks, tariffs on 98.5% of goods to go (European Commission via AppiSToS; cryptoeconomics.tech).
- COP31 climate talks deadlock — nearly 200 nations split over fossil fuels and finance; talks extended into overtime (cryptoeconomics.tech; japako.pl).
- Mexico captures 'El Chapo Isidro' (Reuters via huddleworld).
- Also today: Alcaraz faces Zverev for the ATP Finals title (BBC Sport via huddleworld); four nations call on Israel to let aid into flooded Gaza; Eisenkot tapped to form Israel's next government; France's fourth weekend of cost-of-living protests (thepariseye.com).

## Kit
- Official kit downloaded from `GET /c/news-image-20261122/kit`: `~/workspace/makefun/kits/news-image-20261122-kit.tar.gz` (6,915,770 bytes), extracted to `news-image-20261122-kit/news-image-20261122-kit/`. Manifest verified 11/11 file SHA-256 match kit.json; `cli/makefun.mjs` SHA-256 `bc425136…`.
- Requirements live: repo must be created after 2026-11-22T00:00Z; repo_readme needs 3 live badges; repo_about homepage `https://make.fun/bounty/news-image-20261122`, topics makefun, ai-agents, bounties, growth; thinking_reproduces min 30%; thinking_turns min 5; thinking_revised min 2 writes; thinking_priced min 1 usage row.

## Build notes
- Written fresh in this session (no code copied from the 20/21 Nov entries; only the layout pattern was reused as reference). `main.py` was revised 4 times in-session (draw_wrapped call fix, Gulf panel, layout shift, deck trim) — thinking_revised satisfied.
- The entry.png in `output/` is the program's own output (kept for visual checking only; the grader runs main.py and does not need it pushed).

## Status
- Bundle + check: see STATUS.md. NOT pushed, NOT submitted (parent handles repo + About + submit).
- Repo: new public repo needed from the user (created after 2026-11-22T00:00Z); README badges currently point at placeholder repo `news-image-20261122` — parent must replace with the real repo name before pushing.
