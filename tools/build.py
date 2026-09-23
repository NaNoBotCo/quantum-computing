#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build.py — every page, from data/, into build/site/.

    SITE_URL=https://example.org python3 tools/build.py

Reads data/*.json, draws the still diagrams from them, inlines the stylesheet and the
demo script, and writes HTML plus the machine files (sitemap, feed, llms.txt, api/).
The counts on the pages are computed here, not typed."""
from __future__ import annotations

import html
import json
import os
import re
import shutil
import sys
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fleet  # noqa: E402
import svg as diagrams  # noqa: E402
from css import CSS  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
BUILD = ROOT / "build"
SITE = BUILD / "site"
IMG = BUILD / "img"
SITE_URL = os.environ.get("SITE_URL", "https://nanobotco.github.io/quantum-computing").rstrip("/")
SITE_NAME = "Quantum Computing, plainly"
SELF_ID = "quantum-computing"
LICENSE_URL = "https://creativecommons.org/licenses/by/4.0/"
REPO = "https://github.com/NaNoBotCo/quantum-computing"
TODAY = date.today().isoformat()
E = html.escape
JS = (ROOT / "tools" / "anim.js").read_text(encoding="utf-8")


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


TL = load("timeline.json")["events"]
TH = load("theory.json")["chapters"]
MA = load("machines.json")["families"]
GL = load("glossary.json")["terms"]
DEV = load("developments.json")
RECENT = load("recent.json") if (DATA / "recent.json").exists() else {}
ROSTER = fleet.load()

NAV = [("index.html", "Home"), ("history/index.html", "History"), ("theory/index.html", "Theory"),
       ("machines/index.html", "Machines"), ("now/index.html", "Now"), ("words/index.html", "Words"),
       ("sources/index.html", "Sources")]


def rel(depth):
    return "../" * depth


def page(title, body, depth=0, desc="", canonical="", jsonld=None, wide=False, current="", extra_js=""):
    r = rel(depth)
    ld = "".join(f'<script type="application/ld+json">{json.dumps(o, ensure_ascii=False)}</script>' for o in (jsonld or []))
    nav = " · ".join(f'<a href="{r}{h}"{" aria-current=page" if h == current else ""}>{n}</a>' for h, n in NAV)
    card = f"{SITE_URL}/img/card.jpg"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc[:300])}">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">
<meta name="color-scheme" content="light dark">
<meta property="og:site_name" content="{E(SITE_NAME)}"><meta property="og:locale" content="en_US">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc[:200])}"><meta property="og:type" content="website">
<meta property="og:image" content="{card}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{card}">
{f'<link rel="canonical" href="{E(canonical)}">' if canonical else ''}
<link rel="icon" href="{r}icon.svg" type="image/svg+xml">
<link rel="manifest" href="{r}manifest.webmanifest">
<meta name="theme-color" content="#0b7a76">
<link rel="alternate" type="application/atom+xml" title="{E(SITE_NAME)} — recent developments" href="{r}feed.xml">
<link rel="license" href="{LICENSE_URL}">
<style>{CSS}</style>
{ld}
</head>
<body>
<header class="top"><a class="brand" href="{r}index.html">Quantum <b>Computing</b></a>
<nav class="crumbs">{nav} · <a href="{r}llms.txt">llms.txt</a> · <a href="{REPO}">Source</a></nav></header>
<main{' class="wide"' if wide else ''}>
{body}
</main>
<footer>
<div class="bots">For the machines: <a href="{r}api/timeline.json">timeline.json</a> <a href="{r}api/theory.json">theory.json</a> <a href="{r}api/machines.json">machines.json</a> <a href="{r}api/developments.json">developments.json</a> <a href="{r}api/recent.json">recent.json</a> <a href="{r}api/glossary.json">glossary.json</a> <a href="{r}llms-full.txt">llms-full.txt</a> <a href="{r}sitemap.xml">sitemap.xml</a> <a href="{r}feed.xml">feed.xml</a></div>
<p>Text, data and pictures <a href="{LICENSE_URL}">CC BY 4.0</a>; code <a href="{REPO}/blob/main/LICENSE">MIT</a>. Every picture here is computed from an equation in <a href="{REPO}/blob/main/tools/draw.py">tools/draw.py</a>. Sources sit beside the facts they support and are listed at <a href="{r}sources/index.html">Sources</a>. Built {TODAY}.</p>
{fleet.row_html(SELF_ID, roster=ROSTER)}
{fleet.support_html(self_id="quantum-computing", roster=ROSTER)}
{fleet.maker_html(roster=ROSTER)}
</footer>
{f'<script>{JS}</script>' if extra_js == 'anim' else ''}
</body>
</html>
"""


def write(path, text):
    p = SITE / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def shot(href, img, label, sub="", cls="", depth=0):
    r = rel(depth)
    return (f'<a class="shot {cls}" href="{E(href)}"><span class="bg" style="background-image:url({r}img/{img})"></span>'
            f'<span class="scrim"></span><span class="sp"></span><span class="tx">{E(label)}{f"<small>{E(sub)}</small>" if sub else ""}</span></a>')


def band(img, kicker, h2, p, depth=0, big=""):
    r = rel(depth)
    inner = f'<p class="big">{big}</p>' if big else f'<h2>{E(h2)}</h2><p>{E(p)}</p>'
    return f'<section class="band" style="background-image:url({r}img/{img})"><div class="in"><span class="kicker">{E(kicker)}</span>{inner}</div></section>'


def prose(paras):
    out = []
    for p in paras:
        t = E(p)
        t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
        out.append(f"<p>{t}</p>")
    return "".join(out)


def sources_list(srcs):
    return "<ul class='small'>" + "".join(f'<li><a href="{E(u)}">{E(n)}</a></li>' for n, u in srcs) + "</ul>"


# ------------------------------------------------------------------ counts
DEVS = sorted(DEV["items"], key=lambda d: d["date"])
N_EVENTS = len(TL)
N_DEVS = len(DEVS)
N_CHAPTERS = len(TH)
N_DEMOS = sum(1 for c in TH if c.get("demo"))
N_FAMILIES = len(MA)
N_TERMS = len(GL)
FIRST_YEAR = min(e["year"] for e in TL)
LAST_DEV = DEVS[-1]["date"] if DEVS else ""
ALL_SOURCES: dict[str, str] = {}
for e in TL:
    ALL_SOURCES[e["source"]] = e["source_name"]
for c in TH:
    for n, u in c["sources"]:
        ALL_SOURCES[u] = n
for f in MA:
    for k in ("best", "quality"):
        ALL_SOURCES[f[k]["source"]] = f"{f['name']}: {f[k]['machine']}"
for d in DEVS:
    ALL_SOURCES[d["source"]] = f"{d['source_name']} ({d['date'][:7]})"
N_SOURCES = len(ALL_SOURCES)

# the extra machine points for the qubit chart, from the machines file
CHART_EXTRA = [{"year": int(f["best"]["date"][:4]), "qubits": f["best"]["qubits"], "machine": f["best"]["machine"]}
               for f in MA if f["id"] in ("atom", "ion") ]


# ------------------------------------------------------------------ pages
def home():
    latest = DEVS[-3:][::-1]
    latest_html = "".join(
        f'<li><span class="d">{E(d["date"])}</span><div><span class="w">{E(d["who"])}</span> — {E(d["what"])}</div></li>' for d in latest)
    body = f"""
<div class="hero">{shot("theory/index.html", "hero.jpg", "Quantum computing", "the history and the theory, in plain words, with the pictures moving", "hero")}</div>
<p class="lead">A bit is a coin on the table. A qubit is a coin in the air. This site is about what you can do with a coin in the air, who worked it out, and how far the machines have got.</p>
<p>{N_EVENTS} events since {FIRST_YEAR}, {N_CHAPTERS} chapters of theory with {N_DEMOS} things to press, {N_FAMILIES} ways of building a qubit, {N_DEVS} developments since 2025, {N_TERMS} words defined, {N_SOURCES} sources. The Now page refreshes itself each week from arXiv and the news.</p>
<div class="doors">
{shot("history/index.html", "band-sphere.jpg", "History", f"{FIRST_YEAR} to now, {N_EVENTS} events")}
{shot("theory/index.html", "band-slits.jpg", "Theory", f"{N_CHAPTERS} chapters, {N_DEMOS} demos")}
{shot("machines/index.html", "band-ions.jpg", "Machines", f"{N_FAMILIES} kinds of qubit")}
{shot("now/index.html", "band-lattice.jpg", "Now", f"{N_DEVS} developments, latest {LAST_DEV}")}
</div>
<h2>The whole idea in four sentences</h2>
<p>Everything small is a wave, and waves can add up or cancel. A qubit is the smallest thing you can hold in a mix of two states, and the mix has a phase, which is where in its rise and fall the wave is. A quantum program is a set of turns that gets the phases of the wrong answers to cancel and the right answer to pile up. Then you look, and most of the time you see the right answer.</p>
<p>The reason it is hard: anything that touches a qubit counts as looking. The reason it is worth it: chemistry, materials and codes are problems where the waves matter, and for those, a room full of ordinary computers cannot keep up with a few thousand good qubits.</p>
{band("band-lattice.jpg", "the milestone", "", "", big=f"1 in 100<small>the error rate below which bigger machines get better. Crossed in hardware, December 2024.</small>")}
<h2>Latest</h2>
<ul class="ledger">{latest_html}</ul>
<p><a class="btn" href="now/index.html">All {N_DEVS} developments →</a></p>
<h2>Start here</h2>
<ol>
<li><a href="theory/bit/index.html">A coin on the table, a coin in the air</a> — the qubit.</li>
<li><a href="theory/waves/index.html">Ripples that cancel</a> — the engine.</li>
<li><a href="theory/entangle/index.html">Two coins that always match</a> — the resource.</li>
<li><a href="theory/correct/index.html">Fixing errors without looking</a> — the problem that the whole field is.</li>
<li><a href="theory/myths/index.html">What it is not</a> — before the next headline.</li>
</ol>
"""
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": SITE_NAME, "url": SITE_URL + "/",
           "description": "The history and theory of quantum computing in plain words, with animations, kept current.",
           "license": LICENSE_URL, "publisher": fleet.publisher_ld(ROSTER), "inLanguage": "en", "dateModified": TODAY},
          fleet.catalog_ld(ROSTER)]
    write("index.html", page(f"{SITE_NAME} — the history and the theory", body, 0,
                             "The history and theory of quantum computing in plain words: qubits, interference, entanglement, Shor, Grover, error correction, the machines, and what changed this year.",
                             SITE_URL + "/", ld, current="index.html"))


def history():
    legend = "".join(f'<span style="--e:{diagrams.ERA[k]}">{E(v)}</span>' for k, v in diagrams.ERA_NAME.items())
    items = []
    for e in TL:
        items.append(f"""<li style="--e:{diagrams.ERA[e["era"]]}"><span class="dot"></span><span class="yr">{e["year"]}</span><div>
<span class="era">{E(diagrams.ERA_NAME[e["era"]])}</span><span class="who">{E(e.get("who", ""))}</span>
<h3>{E(e["title"])}</h3><p class="plain">{E(e["plain"])}</p>
<details><summary>more</summary><p>{E(e["more"])}</p><p class="small">Source: <a href="{E(e["source"])}">{E(e["source_name"])}</a></p></details></div></li>""")
    body = f"""
<h1>History</h1>
<p class="lead">{N_EVENTS} events from {FIRST_YEAR} to {TL[-1]["year"]}, then the <a href="../now/index.html">Now</a> page from 2025 on. Each one gets a line first and the rest under it.</p>
<div class="chart">{diagrams.strip(TL, DEVS)}<div class="legend">{legend}</div><p class="cap">The small blue dots at the right are the {N_DEVS} developments since 2025, from the Now page.</p></div>
{band("band-sphere.jpg", "the shape of it", "Physics first, then ideas, then machines, then corrections", "Thirty years of physics before anyone thought of a computer; fifteen years of ideas before anyone built two qubits; twenty-five years of building before an error-corrected qubit got better as it grew.", depth=1)}
<ul class="tl nojs">{"".join(items)}</ul>
<p><a class="btn" href="../now/index.html">2025 onward: the Now page →</a></p>
<h2>Qubits, counted</h2>
<div class="chart">{diagrams.qubit_chart(TL, CHART_EXTRA)}<p class="cap">Every point is a count a maker announced, from the events above and the Machines page. The line rises by a factor of a thousand in twenty-five years. Nothing on this chart says how good the qubits were, which is the number that matters; see <a href="../theory/myths/index.html">what it is not</a>.</p></div>
"""
    write("history/index.html", page("History — Quantum Computing", body, 1, f"{N_EVENTS} events in the history of quantum computing, from Planck in 1900 to Google's Willow chip in 2024, each in a line of plain English.", f"{SITE_URL}/history/", wide=False, current="history/index.html", extra_js="anim"))


def theory_index():
    items = "".join(f'<li><a href="{c["id"]}/index.html"><b>{E(c["title"])}</b></a><br><span class="mute">{E(c["line"])}</span></li>' for c in TH)
    body = f"""
<h1>Theory</h1>
<p class="lead">{N_CHAPTERS} chapters in the order to read them. {N_DEMOS} of them have something to press.</p>
<ol class="toc">{items}</ol>
{band("band-slits.jpg", "the only mystery", "One electron at a time, and still stripes", "Feynman's phrase for the two-slit experiment. Everything in these chapters comes back to it.", depth=1)}
<p>Nothing here needs any maths past squaring a number. Where a technical word appears, it is defined the first time and again at <a href="../words/index.html">Words</a>.</p>
"""
    write("theory/index.html", page("Theory — Quantum Computing", body, 1, "The theory of quantum computing in plain words: qubits, superposition, interference, entanglement, gates, Grover, Shor, decoherence, error correction, and the myths.", f"{SITE_URL}/theory/", current="theory/index.html"))


def theory_chapters():
    for i, c in enumerate(TH):
        prev = TH[i - 1] if i else None
        nxt = TH[i + 1] if i + 1 < len(TH) else None
        demo = ""
        if c.get("demo"):
            demo = f'<div class="demo" data-demo="{c["demo"]}"><p class="mute small">This demo runs in the browser with JavaScript on. The words above stand on their own.</p></div>'
        extra = ""
        if c["id"] == "correct":
            extra = f'<div class="chart">{diagrams.surface_code(5)}<p class="cap">A 5×5 surface-code patch: 25 data qubits on the dots, one check per coloured square. Each check asks its four corners whether they still agree. This board stores one logical qubit.</p></div>'
        if c["id"] == "myths":
            extra = ""
        nav = '<p class="row">' + (f'<a class="btn alt" href="../{prev["id"]}/index.html">← {E(prev["title"])}</a> ' if prev else "") + \
              (f'<a class="btn" href="../{nxt["id"]}/index.html">{E(nxt["title"])} →</a>' if nxt else '<a class="btn" href="../../machines/index.html">The machines →</a>') + "</p>"
        body = f"""
<p class="small mute">Theory · chapter {i + 1} of {N_CHAPTERS}</p>
<h1>{E(c["title"])}</h1>
<p class="line">{E(c["line"])}</p>
<div class="chapter{' myth' if c['id'] == 'myths' else ''}"><div class="body">{prose(c["body"])}</div></div>
{f'<div class="try"><b>Try it.</b> {E(c["try"])}</div>' if c.get("try") else ''}
{demo}
{extra}
<h3>Sources</h3>{sources_list(c["sources"])}
{nav}
"""
        ld = [{"@context": "https://schema.org", "@type": "Article", "headline": c["title"], "description": c["line"],
               "url": f"{SITE_URL}/theory/{c['id']}/", "license": LICENSE_URL, "inLanguage": "en",
               "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": SITE_URL + "/"}, "publisher": fleet.publisher_ld(ROSTER), "dateModified": TODAY}]
        write(f"theory/{c['id']}/index.html", page(f"{c['title']} — Quantum Computing", body, 2, c["line"], f"{SITE_URL}/theory/{c['id']}/", ld, current="theory/index.html", extra_js="anim"))


def machines():
    cards = []
    for f in MA:
        cards.append(f"""<article class="card" id="{f["id"]}"><h3>{E(f["name"])}</h3><p>{E(f["plain"])}</p>
<details><summary>how it works</summary><p>{E(f["how"])}</p></details>
<p class="pro">{E(f["good"])}</p><p class="con">{E(f["bad"])}</p>
<div class="kv"><b>cold</b><span>{E(f["cold"])}</span><b>gate</b><span>{E(f["gate"])}</span><b>lasts</b><span>{E(f["life"])}</span>
<b>biggest</b><span>{E(f["best"]["machine"])}, {f["best"]["qubits"]:,} qubits ({E(f["best"]["date"])}) — <a href="{E(f["best"]["source"])}">source</a>{f'. {E(f["best"]["note"])}' if f["best"].get("note") else ''}</span>
<b>quality</b><span>{E(f["quality"]["machine"])}: {E(f["quality"]["figure"])} ({E(f["quality"]["date"])}) — <a href="{E(f["quality"]["source"])}">source</a></span></div>
<p class="who">Who: {E(", ".join(f["who"]))}</p></article>""")
    body = f"""
<h1>Machines</h1>
<p class="lead">{N_FAMILIES} ways to build a qubit. Each has a biggest machine and a best number, dated and sourced, because both move.</p>
{band("band-ions.jpg", "the trade", "Fast and short-lived, or slow and long-lived", "A chip qubit does a gate in billionths of a second and is gone in a ten-thousandth. An ion takes a thousand times longer per gate and lasts minutes. Nobody has both yet.", depth=1)}
<div class="cards">{"".join(cards)}</div>
<h2>The trade, drawn</h2>
<div class="chart">{diagrams.families_chart(MA)}<p class="cap">Order-of-magnitude figures from the rows above; the numbers are in <a href="../api/machines.json">machines.json</a> with the text they were chosen to match.</p></div>
<h2>Reading a machine announcement</h2>
<ol>
<li><b>Which kind.</b> An annealer is not a gate machine. Neutral-atom counts often mean atoms trapped, not entangled.</li>
<li><b>Physical or logical.</b> A thousand physical qubits and a hundred logical qubits are different worlds; the second is worth far more.</li>
<li><b>The two-qubit error rate.</b> 99% is 2019. 99.9% is 2024. 99.99% is what error-correction plans assume.</li>
<li><b>The task.</b> A random-sampling benchmark shows the hardware works; it is not a use. Chemistry, materials and codes are uses.</li>
<li><b>Who checked.</b> A Nature paper, a company blog and a press release are three different levels of checking. The Now page names which.</li>
</ol>
"""
    write("machines/index.html", page("Machines — Quantum Computing", body, 1, f"{N_FAMILIES} ways to build a qubit: superconducting, trapped ions, neutral atoms, photons, spins, topological, annealers. Each with its biggest machine and best number, dated.", f"{SITE_URL}/machines/", wide=True, current="machines/index.html"))


def now():
    rows = []
    for d in DEVS[::-1]:
        unc = '<span class="unc">unconfirmed</span> ' if d.get("unconfirmed") else ""
        rows.append(f"""<li><span class="d">{E(d["date"])}</span><div>{unc}<span class="w">{E(d["who"])}</span> — {E(d["what"])}<div class="why">{E(d["why"])}</div><div class="src">Source: <a href="{E(d["source"])}">{E(d["source_name"])}</a>{f' · {E(d["note"])}' if d.get("note") else ''}</div></div></li>""")
    feed_html = ""
    if RECENT:
        papers = "".join(f'<li><span class="d">{E(p["date"][:10])}</span><div><a href="{E(p["url"])}">{E(p["title"])}</a><div class="s">{E(p.get("authors", ""))}</div></div></li>' for p in RECENT.get("arxiv", [])[:25])
        news = "".join(f'<li><span class="d">{E(n["date"][:10])}</span><div><a href="{E(n["url"])}">{E(n["title"])}</a><div class="s">{E(n.get("source", ""))}</div></div></li>' for n in RECENT.get("news", [])[:40])
        errs = RECENT.get("errors") or []
        feed_html = f"""
<h2>This week's feed</h2>
<p class="small mute">Fetched {E(RECENT.get("fetched", "")[:16].replace("T", " "))} UTC by <a href="{REPO}/blob/main/tools/fetch_recent.py">tools/fetch_recent.py</a>, which a GitHub Actions job runs every Monday. Titles as published; nothing here has been read by a person before it appears. Papers are from arXiv quant-ph; news is from the feeds named on each row.</p>
<h3>Papers</h3><ul class="feed">{papers or '<li><span class="d"></span><div class="s">none fetched</div></li>'}</ul>
<h3>News</h3><ul class="feed">{news or '<li><span class="d"></span><div class="s">none fetched</div></li>'}</ul>
{f'<p class="small mute">Sources that did not answer this week: {E("; ".join(errs))}</p>' if errs else ''}"""
    else:
        feed_html = f'<h2>This week\'s feed</h2><p class="mute">The weekly fetch has not run yet. <a href="{REPO}/blob/main/tools/fetch_recent.py">tools/fetch_recent.py</a> writes it.</p>'
    body = f"""
<h1>Now</h1>
<p class="lead">{N_DEVS} developments since January 2025, newest first, each in a sentence with a source. Below them, the raw feed of the week.</p>
<div class="chart">{diagrams.per_month(DEVS)}<p class="cap">Developments recorded per month in the hand-kept ledger. A quiet month is a month nothing was added, which is not the same as a quiet month.</p></div>
{band("band-lattice.jpg", "the two ledgers", "One kept by hand, one fetched by a script", "The ledger is written by a person, a sentence per item, with the source. The feed underneath is whatever arXiv and the news feeds carried this week, unread. Both are dated.", depth=1)}
<h2>The ledger</h2>
<ul class="ledger">{"".join(rows)}</ul>
{feed_html}
<h2>How this page changes</h2>
<p>The ledger is <a href="{REPO}/blob/main/data/developments.json">data/developments.json</a> in the repository, last edited {E(DEV.get("updated", ""))}. Anyone can open a pull request against it; a row needs a date, a source and one plain sentence. The feed is <a href="{REPO}/blob/main/data/recent.json">data/recent.json</a>, rewritten by the Monday job, which then rebuilds the site.</p>
"""
    write("now/index.html", page("Now — Quantum Computing", body, 1, f"{N_DEVS} developments in quantum computing since 2025, one sentence each with a source, plus this week's arXiv papers and news, fetched weekly.", f"{SITE_URL}/now/", wide=False, current="now/index.html"))


def words():
    chap = {c["id"]: c["title"] for c in TH}
    dl = []
    for t in sorted(GL, key=lambda t: t["term"].lower()):
        see = t.get("see", "")
        link = f'<a href="../theory/{see}/index.html">{E(chap[see])}</a>' if see in chap else (f'<a href="../machines/index.html">Machines</a>' if see == "machines" else "")
        dl.append(f'<dt id="{E(t["term"].lower().replace(" ", "-").replace("(", "").replace(")", ""))}">{E(t["term"])}</dt><dd>{E(t["plain"])}{f" — {link}" if link else ""}</dd>')
    body = f"""
<h1>Words</h1>
<p class="lead">{N_TERMS} words, each in a sentence or two, with the chapter that uses it.</p>
<dl class="gloss">{"".join(dl)}</dl>
"""
    write("words/index.html", page("Words — Quantum Computing", body, 1, f"{N_TERMS} quantum computing terms defined in plain English: qubit, superposition, entanglement, decoherence, surface code, logical qubit, and the rest.", f"{SITE_URL}/words/", current="words/index.html"))


def sources():
    rows = "".join(f'<li><a href="{E(u)}">{E(n)}</a> <span class="small mute">{E(u.split("/")[2] if "//" in u else u)}</span></li>' for u, n in sorted(ALL_SOURCES.items(), key=lambda kv: kv[1].lower()))
    body = f"""
<h1>Sources</h1>
<p class="lead">{N_SOURCES} sources, one line each. Every fact on the site sits next to one of these; this page lists them once.</p>
<p>Wikipedia is used for the settled history, where its articles carry the primary citations. For anything from 2019 on, the source is the paper, the company's own statement, or a named publication, and the Now page says which of those three it is. A row marked unconfirmed there rests on a secondary report.</p>
<ul>{rows}</ul>
<h2>Further reading, for the next step up</h2>
<ul>
<li>Scott Aaronson, <a href="https://www.scottaaronson.com/democritus/">Quantum Computing Since Democritus</a> — lecture notes, free online; the book of the same name.</li>
<li>Michael Nielsen and Isaac Chuang, <a href="https://en.wikipedia.org/wiki/Quantum_Computation_and_Quantum_Information">Quantum Computation and Quantum Information</a> — the textbook.</li>
<li>Andy Matuschak and Michael Nielsen, <a href="https://quantum.country/">Quantum Country</a> — a free essay course that teaches the maths a little at a time.</li>
<li>Richard Feynman, <a href="https://www.feynmanlectures.caltech.edu/III_toc.html">Lectures on Physics, volume III</a> — free online.</li>
<li>John Preskill, <a href="https://arxiv.org/abs/1801.00862">Quantum Computing in the NISQ era and beyond</a> (2018) — where the current era got its name.</li>
</ul>
"""
    write("sources/index.html", page("Sources — Quantum Computing", body, 1, f"The {N_SOURCES} sources behind the site, and five things to read next.", f"{SITE_URL}/sources/", current="sources/index.html"))


def machine_files():
    # api
    for name in ("timeline", "theory", "machines", "developments", "glossary"):
        shutil.copy(DATA / f"{name}.json", SITE / "api" / f"{name}.json") if (SITE / "api").mkdir(parents=True, exist_ok=True) is None else None
    if (DATA / "recent.json").exists():
        shutil.copy(DATA / "recent.json", SITE / "api" / "recent.json")
    else:
        write("api/recent.json", json.dumps({"fetched": None, "arxiv": [], "news": []}))
    write("api/index.json", json.dumps({"site": SITE_NAME, "url": SITE_URL + "/", "license": LICENSE_URL, "built": TODAY,
                                        "counts": {"events": N_EVENTS, "chapters": N_CHAPTERS, "demos": N_DEMOS, "families": N_FAMILIES,
                                                   "developments": N_DEVS, "terms": N_TERMS, "sources": N_SOURCES},
                                        "files": ["timeline.json", "theory.json", "machines.json", "developments.json", "recent.json", "glossary.json"]}, indent=1))
    # urls
    urls = ["", "history/", "theory/", "machines/", "now/", "words/", "sources/"] + [f"theory/{c['id']}/" for c in TH]
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
          "".join(f"<url><loc>{SITE_URL}/{u}</loc><lastmod>{TODAY}</lastmod></url>\n" for u in urls) + "</urlset>\n")
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    # atom feed from the ledger
    entries = []
    for d in DEVS[::-1][:30]:
        dt = d["date"] if len(d["date"]) == 10 else d["date"] + "-01"
        entries.append(f"""<entry><title>{E(d["who"])}: {E(d["what"][:90])}</title><link href="{E(d["source"])}"/><id>{SITE_URL}/now/#{E(dt)}-{E(re.sub(r"[^a-z0-9]+", "-", d["who"].lower()))}</id><updated>{dt}T00:00:00Z</updated><summary>{E(d["what"])} {E(d["why"])}</summary></entry>""")
    write("feed.xml", f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"><title>{E(SITE_NAME)} — recent developments</title><link href="{SITE_URL}/now/"/><link rel="self" href="{SITE_URL}/feed.xml"/><id>{SITE_URL}/</id><updated>{TODAY}T00:00:00Z</updated><author><name>NaNoBotCo</name></author>
{"".join(entries)}
</feed>
""")
    # llms
    chapters = "\n".join(f"- [{c['title']}]({SITE_URL}/theory/{c['id']}/): {c['line']}" for c in TH)
    write("llms.txt", f"""# {SITE_NAME}

> The history and theory of quantum computing in plain words, with animated demos, the hardware families compared, and a dated ledger of developments since 2025 that is refreshed weekly. CC BY 4.0.

- [History]({SITE_URL}/history/): {N_EVENTS} events, {FIRST_YEAR} to {TL[-1]['year']}, each with a source
- [Theory]({SITE_URL}/theory/): {N_CHAPTERS} chapters
{chapters}
- [Machines]({SITE_URL}/machines/): {N_FAMILIES} hardware families, biggest machine and best figure per family, dated
- [Now]({SITE_URL}/now/): {N_DEVS} developments since 2025-01, newest {LAST_DEV}; weekly arXiv and news feed
- [Words]({SITE_URL}/words/): {N_TERMS} terms
- [Sources]({SITE_URL}/sources/): {N_SOURCES} sources

## Data
- {SITE_URL}/api/timeline.json · {SITE_URL}/api/theory.json · {SITE_URL}/api/machines.json · {SITE_URL}/api/developments.json · {SITE_URL}/api/recent.json · {SITE_URL}/api/glossary.json
- {SITE_URL}/llms-full.txt — every chapter, event and development as text
- Repository: {REPO}
""")
    full = [f"# {SITE_NAME}\n\nBuilt {TODAY}. CC BY 4.0. {SITE_URL}/\n"]
    full.append("\n## Theory\n")
    for c in TH:
        full.append(f"\n### {c['title']}\n\n{c['line']}\n\n" + "\n\n".join(c["body"]) + "\n\nSources: " + "; ".join(f"{n} <{u}>" for n, u in c["sources"]) + "\n")
    full.append("\n## History\n")
    for e in TL:
        full.append(f"\n- {e['year']} — {e['title']}. {e['plain']} {e['more']} Source: {e['source_name']} <{e['source']}>")
    full.append("\n\n## Machines\n")
    for f in MA:
        full.append(f"\n### {f['name']}\n\n{f['plain']} {f['how']}\n\nGood: {f['good']}\nBad: {f['bad']}\nBiggest: {f['best']['machine']}, {f['best']['qubits']} qubits ({f['best']['date']}) <{f['best']['source']}>\nQuality: {f['quality']['machine']}: {f['quality']['figure']} ({f['quality']['date']}) <{f['quality']['source']}>\n")
    full.append("\n## Developments since 2025\n")
    for d in DEVS:
        full.append(f"\n- {d['date']} — {d['who']}: {d['what']} {d['why']} Source: {d['source_name']} <{d['source']}>{' (unconfirmed)' if d.get('unconfirmed') else ''}")
    full.append("\n\n## Words\n")
    for t in GL:
        full.append(f"\n- {t['term']}: {t['plain']}")
    write("llms-full.txt", "".join(full) + "\n")
    write("humans.txt", f"/* {SITE_NAME} */\nBuilt by NaNoBotCo. Every picture computed in tools/draw.py. {REPO}\n")
    write("manifest.webmanifest", json.dumps({"name": SITE_NAME, "short_name": "Quantum", "start_url": "./", "display": "standalone",
                                              "background_color": "#0d1117", "theme_color": "#0b7a76", "icons": [{"src": "icon.svg", "sizes": "any", "type": "image/svg+xml"}]}))
    write("icon.svg", '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#0b1220"/><circle cx="32" cy="32" r="22" fill="none" stroke="#2fc4bd" stroke-width="3"/><ellipse cx="32" cy="32" rx="22" ry="7" fill="none" stroke="#2fc4bd" stroke-width="2" opacity=".6"/><line x1="32" y1="32" x2="46" y2="16" stroke="#f0b545" stroke-width="4" stroke-linecap="round"/><circle cx="46" cy="16" r="4" fill="#f0b545"/></svg>')
    write("404.html", page("Not here — Quantum Computing", '<h1>Not here</h1><p class="lead">That address is in a superposition of never having existed and having moved. <a href="index.html">Home</a>, or the <a href="theory/index.html">theory</a>.</p>', 0, "Page not found."))
    fleet.decorate(SITE, SELF_ID, ROSTER)


def main():
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir(parents=True)
    if not (IMG / "hero.jpg").exists():
        import draw
        for k in draw.PICTURES:
            draw.PICTURES[k]()
    shutil.copytree(IMG, SITE / "img")
    home(); history(); theory_index(); theory_chapters(); machines(); now(); words(); sources(); machine_files()
    n = len(list(SITE.rglob("*.html")))
    print(f"built {n} pages into {SITE} for {SITE_URL}: {N_EVENTS} events, {N_CHAPTERS} chapters, {N_DEMOS} demos, {N_FAMILIES} families, {N_DEVS} developments, {N_TERMS} terms, {N_SOURCES} sources")


if __name__ == "__main__":
    main()
