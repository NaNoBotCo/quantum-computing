#!/usr/bin/env python3
"""check_data.py — the data files, checked before a build.

Every timeline event and development carries a date, a source URL and a plain line.
Every theory chapter names a demo the script has, or none. Exit 1 on the first problem."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data"
_JS = (ROOT / "tools" / "anim.js").read_text(encoding="utf-8")
DEMOS = {x.split(":")[0].strip() for x in re.search(r"var DEMOS = \{([^}]*)\}", _JS).group(1).split(",")}
URL = re.compile(r"^https?://\S+$")
problems = []


def need(cond, msg):
    if not cond:
        problems.append(msg)


tl = json.loads((D / "timeline.json").read_text())["events"]
years = [e["year"] for e in tl]
need(years == sorted(years), "timeline: events out of year order")
for e in tl:
    need(URL.match(e.get("source", "")), f"timeline {e.get('year')}: bad source url")
    need(e.get("plain") and e.get("more") and e.get("title"), f"timeline {e.get('year')}: missing text")
    need(e.get("era") in ("quantum", "computing", "idea", "build", "correct"), f"timeline {e.get('year')}: era")

th = json.loads((D / "theory.json").read_text())["chapters"]
ids = [c["id"] for c in th]
need(len(ids) == len(set(ids)), "theory: duplicate ids")
for c in th:
    need(c.get("demo", "") in DEMOS | {""}, f"theory {c['id']}: demo '{c.get('demo')}' not in anim.js ({sorted(DEMOS)})")
    need(len(c["body"]) >= 3, f"theory {c['id']}: fewer than three paragraphs")
    for n, u in c["sources"]:
        need(URL.match(u), f"theory {c['id']}: bad source {u}")

dev = json.loads((D / "developments.json").read_text())["items"]
dates = [d["date"] for d in dev]
need(dates == sorted(dates, key=lambda x: x if len(x) == 10 else x + "-00"), "developments: not in date order")
for d in dev:
    need(re.match(r"^\d{4}-\d{2}(-\d{2})?$", d["date"]), f"developments: bad date {d['date']}")
    need(URL.match(d["source"]), f"developments {d['date']}: bad source")
    need(d.get("what") and d.get("why") and d.get("who") and d.get("source_name"), f"developments {d['date']}: missing field")

ma = json.loads((D / "machines.json").read_text())["families"]
for f in ma:
    for k in ("best", "quality"):
        need(URL.match(f[k]["source"]), f"machines {f['id']}: {k} source")
    need(isinstance(f["best"]["qubits"], int), f"machines {f['id']}: best.qubits not an int")

gl = json.loads((D / "glossary.json").read_text())["terms"]
for t in gl:
    need(t.get("see", "") in set(ids) | {"machines", ""}, f"glossary {t['term']}: see='{t.get('see')}'")

if problems:
    print("\n".join(problems)); sys.exit(1)
print(f"data ok: {len(tl)} events, {len(th)} chapters, {len(dev)} developments, {len(ma)} families, {len(gl)} terms")
