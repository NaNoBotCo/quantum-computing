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
