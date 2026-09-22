# -*- coding: utf-8 -*-
"""svg.py — the still diagrams, drawn from the data at build time so the figures on them
are the figures in the files."""
from __future__ import annotations

import html
import math
from datetime import date

E = html.escape

ERA = {"quantum": "var(--e-quantum)", "computing": "var(--e-computing)", "idea": "var(--e-idea)",
       "build": "var(--e-build)", "correct": "var(--e-correct)", "now": "var(--e-now)"}
ERA_NAME = {"quantum": "the physics", "computing": "ordinary computing", "idea": "the ideas",
            "build": "building", "correct": "correcting", "now": "now"}


def strip(events: list[dict], recent: list[dict]) -> str:
    """A horizontal strip, 1900 to now, one tick per event, coloured by era."""
    y0, y1 = 1900, date.today().year + 1
    W, H = 1000, 150
    def x(y): return 40 + (y - y0) / (y1 - y0) * (W - 60)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="events by year, 1900 to now">']
    out.append(f'<line x1="{x(y0)}" y1="80" x2="{x(y1)}" y2="80" stroke="var(--mute)" stroke-width="2"/>')
    for y in range(1900, y1 + 1, 10):
        out.append(f'<line x1="{x(y):.1f}" y1="74" x2="{x(y):.1f}" y2="86" stroke="var(--mute)"/>')
        out.append(f'<text x="{x(y):.1f}" y="104" text-anchor="middle" font-size="12" fill="var(--mute)">{y}</text>')
    # stack ticks that share a year
    seen: dict[int, int] = {}
    for e in events:
        n = seen.get(e["year"], 0); seen[e["year"]] = n + 1
        cy = 66 - n * 14
        out.append(f'<circle cx="{x(e["year"]):.1f}" cy="{cy}" r="6" fill="{ERA.get(e["era"], "var(--teal)")}" stroke="var(--bg)" stroke-width="1.5"><title>{E(str(e["year"]))} — {E(e["title"])}</title></circle>')
    for r in recent:
        y = int(r["date"][:4]) + (int(r["date"][5:7]) - 1) / 12 if len(r["date"]) >= 7 else int(r["date"][:4])
        n = seen.get(int(y), 0); seen[int(y)] = n + 1
        cy = 66 - (n % 6) * 12
        out.append(f'<circle cx="{x(y):.1f}" cy="{cy}" r="4" fill="{ERA["now"]}" stroke="var(--bg)" stroke-width="1"><title>{E(r["date"])} — {E(r["who"])}</title></circle>')
    out.append("</svg>")
    return "".join(out)


def qubit_chart(events: list[dict], extra: list[dict]) -> str:
    """Physical qubit counts claimed, by year, log scale. Only rows that carry a count."""
    pts = [(e["year"], e["qubits"], e.get("machine", "")) for e in events if e.get("qubits")]
    pts += [(p["year"], p["qubits"], p["machine"]) for p in extra]
    pts.sort()
    W, H = 1000, 380
    y0, y1 = 1994, date.today().year + 1
    def x(y): return 60 + (y - y0) / (y1 - y0) * (W - 90)
    def yy(q): return 320 - (math.log10(q) / 4) * 290
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="qubits claimed per machine, by year, log scale">']
    for p in range(0, 5):
        out.append(f'<line x1="60" y1="{yy(10**p):.1f}" x2="{W-30}" y2="{yy(10**p):.1f}" stroke="var(--line)"/>')
        out.append(f'<text x="52" y="{yy(10**p)+4:.1f}" text-anchor="end" font-size="12" fill="var(--mute)">{10**p:,}</text>')
    for y in range(1995, y1, 5):
        out.append(f'<text x="{x(y):.1f}" y="345" text-anchor="middle" font-size="12" fill="var(--mute)">{y}</text>')
    path = " ".join(f'{"M" if i == 0 else "L"}{x(y):.1f} {yy(q):.1f}' for i, (y, q, _) in enumerate(pts))
    out.append(f'<path d="{path}" fill="none" stroke="var(--teal)" stroke-width="2" opacity=".5"/>')
    for i, (y, q, m) in enumerate(pts):
        anchor = "end" if i % 2 else "start"
        dx = -10 if i % 2 else 10
        out.append(f'<circle cx="{x(y):.1f}" cy="{yy(q):.1f}" r="6" fill="var(--gold)" stroke="var(--ink)" stroke-width="1.5"><title>{E(m)}: {q:,} qubits, {y}</title></circle>')
        out.append(f'<text x="{x(y)+dx:.1f}" y="{yy(q)-9:.1f}" text-anchor="{anchor}" font-size="11" fill="var(--ink)">{E(m)} {q:,}</text>')
    out.append(f'<text x="{W/2:.0f}" y="372" text-anchor="middle" font-size="12" fill="var(--mute)">physical qubits on one machine, as announced — a count, not a score</text>')
    out.append("</svg>")
    return "".join(out)


def per_month(items: list[dict]) -> str:
    """Developments per month in the hand-kept ledger."""
    months: dict[str, int] = {}
    for it in items:
        months[it["date"][:7]] = months.get(it["date"][:7], 0) + 1
    if not months:
        return ""
    keys = sorted(months)
    first = keys[0]; last = keys[-1]
    fy, fm = int(first[:4]), int(first[5:7]); ly, lm = int(last[:4]), int(last[5:7])
    seq = []
    y, m = fy, fm
    while (y, m) <= (ly, lm):
        seq.append(f"{y}-{m:02d}"); m += 1
        if m > 12: m = 1; y += 1
    W, H = 1000, 200; mx = max(months.values())
    bw = (W - 80) / len(seq)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="developments recorded per month">']
    for i, k in enumerate(seq):
        v = months.get(k, 0); h = v / mx * 130
        out.append(f'<rect x="{50+i*bw+2:.1f}" y="{160-h:.1f}" width="{bw-4:.1f}" height="{h:.1f}" fill="var(--e-now)" rx="3"><title>{k}: {v}</title></rect>')
        if v: out.append(f'<text x="{50+i*bw+bw/2:.1f}" y="{154-h:.1f}" text-anchor="middle" font-size="11" fill="var(--ink)">{v}</text>')
        if k.endswith("-01") or i == 0:
            out.append(f'<text x="{50+i*bw+bw/2:.1f}" y="182" text-anchor="middle" font-size="12" fill="var(--mute)">{k[:4]}</text>')
    out.append("</svg>")
    return "".join(out)


def families_chart(fams: list[dict]) -> str:
    """Gate time against coherence time, both log, one dot per family. Numbers from the
    rows' gate_s and life_s fields; a family with neither is left off."""
    W, H = 1000, 420
    pts = [f for f in fams if f.get("gate_s") and f.get("life_s")]
    def x(g): return 80 + (math.log10(g) + 9) / 5 * (W - 120)      # 1 ns .. 100 µs
    def y(l): return 340 - (math.log10(l) + 4) / 7 * 300           # 100 µs .. 1000 s
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="gate time against coherence time by hardware family">']
    for p, lab in ((-9, "1 ns"), (-8, "10 ns"), (-7, "100 ns"), (-6, "1 µs"), (-5, "10 µs"), (-4, "100 µs")):
        out.append(f'<line x1="{x(10**p):.1f}" y1="40" x2="{x(10**p):.1f}" y2="340" stroke="var(--line)"/><text x="{x(10**p):.1f}" y="360" text-anchor="middle" font-size="12" fill="var(--mute)">{lab}</text>')
    for p, lab in ((-4, "100 µs"), (-3, "1 ms"), (-2, "10 ms"), (-1, "0.1 s"), (0, "1 s"), (1, "10 s"), (2, "100 s"), (3, "1000 s")):
        out.append(f'<line x1="80" y1="{y(10**p):.1f}" x2="{W-40}" y2="{y(10**p):.1f}" stroke="var(--line)"/><text x="72" y="{y(10**p)+4:.1f}" text-anchor="end" font-size="12" fill="var(--mute)">{lab}</text>')
    for f in pts:
        cx, cy = x(f["gate_s"]), y(f["life_s"])
        out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="11" fill="var(--gold)" stroke="var(--ink)" stroke-width="2"><title>{E(f["name"])}</title></circle>')
        out.append(f'<text x="{cx+16:.1f}" y="{cy+5:.1f}" font-size="14" fill="var(--ink)">{E(f["name"])}</text>')
    out.append(f'<text x="{W/2:.0f}" y="392" text-anchor="middle" font-size="12" fill="var(--mute)">how long one two-qubit gate takes (across) against how long a qubit lasts (up); rough, one number per family</text>')
    out.append(f'<text x="{W/2:.0f}" y="410" text-anchor="middle" font-size="12" fill="var(--mute)">a machine wants to be far up and far left: many gates before the state is gone</text>')
    out.append("</svg>")
    return "".join(out)


def surface_code(d: int = 5) -> str:
    """A d×d surface code patch: data qubits on the dots, checks on the faces."""
    cell = 44; W = H = cell * (d + 1)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="a {d} by {d} surface code patch">']
    for i in range(d - 1):
        for j in range(d - 1):
            fill = "var(--teal)" if (i + j) % 2 == 0 else "var(--violet)"
            out.append(f'<rect x="{cell*(i+1)}" y="{cell*(j+1)}" width="{cell}" height="{cell}" fill="{fill}" opacity=".35"/>')
    for i in range(d):
        for j in range(d):
            out.append(f'<circle cx="{cell*(i+1)}" cy="{cell*(j+1)}" r="9" fill="var(--gold)" stroke="var(--ink)" stroke-width="2"/>')
    out.append("</svg>")
    return "".join(out)
