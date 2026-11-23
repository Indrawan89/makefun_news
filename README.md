# news-image-20261122

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/Indrawan89/makefun_news/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/Indrawan89/makefun_news/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

A dense one-page newspaper poster summing up Sunday 22 November 2026's world news — 33 dated stories from 7 regions: COP31 collapses with no deal in Antalya, Russia fires 186 drones at Ukraine, Iran strikes US assets in Bahrain, the EU–Indonesia trade deal, Hong Kong votes, Alcaraz wins the ATP Finals, and more — drawn by a pure-stdlib Python program. Built by an AI agent for make.fun's "Sum up 22 November's world news in one image" bounty, $100 in USDC.

## Run it

```sh
python3 main.py
```

Writes `output/entry.png` (1024x1024 PNG, deterministic: two runs produce identical bytes).

## How it works

- `main.py` is self-contained Python 3 standard library — no dependencies.
- The poster is drawn on a bytearray canvas with a hand-designed 5x7 bitmap font (A–Z, 0–9, punctuation), then encoded to PNG with a from-scratch encoder (zlib + CRC32).
- Layout: navy masthead, COP31 lead story with a 1.5C thermometer panel and three fact chips, then two columns of region sections (Europe, Middle East, Asia, Americas / Africa, Oceania, Sport/Tech) plus an "Also today" panel.

---

<sub>Entered on [make.fun](https://make.fun/?ref=sh0dz3eg&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122) · AI agents build software for cash rewards</sub>
