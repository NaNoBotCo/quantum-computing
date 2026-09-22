# Quantum Computing, plainly

The history and the theory of quantum computing in plain words, with the pictures
moving. A bit is a coin on the table; a qubit is a coin in the air.

**Live:** https://nanobotco.github.io/quantum-computing/

## What is in it

- **History** — events from 1900 to 2024, one line each, the rest under it, a source on every row.
- **Theory** — ten chapters in reading order: the qubit, the Bloch sphere, interference,
  entanglement and the Bell test, gates, Grover, Shor, decoherence, error correction, and
  what it is not. Nine of them have a demo to press.
- **Machines** — seven ways to build a qubit, each with its biggest machine and its best
  figure, dated and sourced.
- **Now** — a hand-kept ledger of developments since January 2025, one sentence each, and
  a feed of the week's arXiv papers and news that a GitHub Actions job refreshes every
  Monday.
- **Words** — the terms, defined.
- **Sources** — everything cited, once.

The counts on the pages are computed at build time from the data files. Every picture is
computed from an equation in `tools/draw.py`; there are no photographs.

## Build

```
python3 tools/draw.py            # the pictures, into build/img/ (numpy, pillow)
python3 tools/fetch_recent.py    # this week's papers and news → data/recent.json
./publish.sh                     # check data, build, check links, into docs/
python3 tools/serve.py 8834      # http://127.0.0.1:8834/quantum-computing/
```

`docs/` is what GitHub Pages serves. `.github/workflows/refresh.yml` runs the fetch and
the build on a Monday cron and commits the result.

## Adding a development

Edit `data/developments.json`. A row is a date, who, one plain sentence of what, one of
why, a source URL and the source's name. Mark it `"unconfirmed": true` if the source is
secondary. `tests/check_data.py` checks the shape; the Now page and the Atom feed are
built from it.

## Licence

Text, data and pictures CC BY 4.0. Code MIT. See `NOTICE.txt`.

Contact: Nan · nan@motdang.net

<!-- fleet-roster -->

## Elsewhere from the same publisher

- [Mot Dang](https://motdang.net/) — city directory for Chiang Mai and Chiang Rai
- [The Mae Hong Son Loop](https://nanobotco.github.io/mae-hong-son-loop/) — motorcycling the 600 km loop out of Chiang Mai — curves counted, air measured
- [Muay Thai](https://motdang.net/muay-thai/) — the eight limbs, the thirty named techniques, the ceremony, and every gym on the map
- [Roads of Chiang Mai](https://motdang.net/roads/) — the square of 1296, four rings, and what each one did to the city — counted from the map
- [wichaa](https://wichaa.net/) — Lanna manuscripts, the amulet market, and the traditions around them
- [Hand Poke](https://nanobotco.github.io/hand-poke/) — 28 traditions of marking skin by hand — the leg-tattoo zone of Burma, the Shan States and Lanna, counted
- [Black Holes, Drawn](https://nanobotco.github.io/black-holes/) — black holes modelled and drawn from the equations — generators, the past, present and future, the legends
- [Goin' Fast](https://nanobotco.github.io/goin-fast/) — a dirt-simple explainer about speed — twenty measured speeds from the ground under the house to light, and what each one costs
- [Amulet Atlas](https://nanobotco.github.io/amulet-atlas/) — amulets, charms and talismans worldwide
- [Carolina Barbecue](https://nanobotco.github.io/carolina-barbecue/) — barbecue in North and South Carolina
- [Wing Country](https://nanobotco.github.io/buffalo-wings/) — the American chicken wing
- [Pink Box](https://nanobotco.github.io/pink-box/) — the American mom-and-pop donut shop
- [Basque Tables](https://nanobotco.github.io/basque-tables/) — Basque dining rooms of California, Nevada and Idaho
- [Pinot Country](https://nanobotco.github.io/pinot-noir/) — pinot noir: the vine, the regions, the cellars
- [Care Abroad](https://nanobotco.github.io/care-abroad/) — treatment across borders, with published prices and their dates
- [Thai Roots](https://nanobotco.github.io/thairoots/) — a root dictionary of Thai, with a word decomposer
- [The index](https://nanobotco.github.io/index/) — every corpus, site and repository, counted
- [Uptake](https://nanobotco.github.io/uptake/) — a field manual on publishing for machines that copy
- [NaNoBotCo](https://nanobotco.github.io/) — the portal
- [ฮักฝรั่ง](https://hakfarang.net/) — เรื่องเงิน วีซ่า และชีวิตกับแฟนฝรั่ง
- [Offrampt](https://offrampt.net/) — turning crypto into spendable local money, Thailand first

All of it, counted: https://nanobotco.github.io/index/ · roster as JSON: https://nanobotco.github.io/index/fleet.json
