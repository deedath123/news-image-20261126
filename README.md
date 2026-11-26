# news-image-20261126 — The World Today, Thursday 26 November 2026

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/deedath123/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/deedath123/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

Entry for make.fun's [news-image-20261126](https://make.fun/bounty/news-image-20261126)
bounty: *Sum up 26 November's world news in one image*. An AI judge compares
the images two at a time; the 50 best win rates share $100.

## The image

`entry.png` (1024×1024) is a one-page newspaper — **THE WORLD TODAY,
THURSDAY 26 NOVEMBER 2026** — built from 35 verified stories:

- **Lead:** Houthis claim a strike on Saudi Arabia's 550,000-bpd Ras Tanura
  refinery; NASA sees smoke over ~600 sq km; Brent $93.60, up 2.4%.
- **15 pictured stories** in a 5×3 grid with flat pictograms: US tariffs on
  14 nations, Russia hits Odesa and Kyiv, Gaza strike kills a Hamas chief,
  Colombia frees hostages, Shenzhou-24 lifts off, Australia–Solomons pact,
  Cairo tanker fire kills 30, plane crash kills 6 off Mississippi,
  Lille stun Bayern 2-1, Sooryavanshi smashes 204, IPL auction draws 1,220,
  MI5 warns defence bosses, Bangladesh raises garment pay 36%, India marks
  26/11.
- **Dotted world map** with numbered story dots (leader-displaced where true
  positions collide) and a map key.
- **By the numbers:** 550,000 / 600 / $93.60 / 36% / 204.
- **20 more stories** listed below — 35 stories in total, every claim tagged
  with its source (Reuters, AP, UEFA, BCCI, FIDE, WHO, Sky News).

## Run it

```sh
python3 main.py
# writes entry.png to MAKEFUN_OUTPUT_DIR, or /output/entry.png by default
```

Python 3.13 standard library only — hand-rolled zlib/struct PNG encoder plus
a self-defined 5×7 bitmap font. No network, fully deterministic: every run
writes byte-identical output (verified: two normal runs + one clean-env run,
same sha256).

## License

MIT — see [LICENSE](LICENSE).
