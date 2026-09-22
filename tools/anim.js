/* anim.js — the demos. Vanilla, no library, inlined into the theory pages.
   Each demo mounts into an element with data-demo="<name>". Continuous motion runs
   only when the reader has not asked for reduced motion; everything is also driven by
   buttons, so a still page is a working page. */
(function () {
  "use strict";
  var RM = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var NS = "http://www.w3.org/2000/svg";
  function el(tag, attrs, kids) {
    var e = document.createElement(tag);
    if (attrs) for (var k in attrs) { if (k === "text") e.textContent = attrs[k]; else if (k === "html") e.innerHTML = attrs[k]; else e.setAttribute(k, attrs[k]); }
    (kids || []).forEach(function (c) { e.appendChild(c); });
    return e;
  }
  function svg(tag, attrs) { var e = document.createElementNS(NS, tag); if (attrs) for (var k in attrs) e.setAttribute(k, attrs[k]); return e; }
  function btn(label, cls) { return el("button", { class: "btn" + (cls ? " " + cls : ""), type: "button", text: label }); }
  function range(min, max, val, step) { return el("input", { type: "range", min: min, max: max, value: val, step: step || 1 }); }
  function readout(t) { return el("span", { class: "readout", text: t }); }
  function fmt(x, d) { return (Math.round(x * Math.pow(10, d)) / Math.pow(10, d)).toFixed(d); }
  var css = getComputedStyle(document.documentElement);
  var C = { teal: css.getPropertyValue("--teal").trim() || "#0b7a76", gold: css.getPropertyValue("--gold").trim() || "#b7791f",
            violet: css.getPropertyValue("--violet").trim() || "#6d4fc4", red: css.getPropertyValue("--red").trim() || "#c8323c",
            ink: css.getPropertyValue("--ink").trim() || "#101418", mute: css.getPropertyValue("--mute").trim() || "#5b6570",
            line: css.getPropertyValue("--line").trim() || "#e2e0d6" };

  /* ---------------------------------------------------------------- 1  the coin */
  function coin(root) {
    var p = 0.5, heads = 0, tails = 0, landed = null;
    var s = svg("svg", { viewBox: "0 0 320 160", role: "img", "aria-label": "a coin, spinning until measured" });
    var g = svg("g", { transform: "translate(80 80)" });
    var disc = svg("circle", { r: 54, fill: C.gold, stroke: C.ink, "stroke-width": 3 });
    var face = svg("text", { "text-anchor": "middle", y: 16, "font-size": 44, "font-weight": 800, fill: C.ink, "font-family": "inherit" });
    face.textContent = "?";
    g.appendChild(disc); g.appendChild(face); g.setAttribute("class", "coin air"); s.appendChild(g);
    var lab = svg("text", { x: 170, y: 60, "font-size": 15, fill: C.mute, "font-family": "inherit" }); lab.textContent = "in the air"; s.appendChild(lab);
    var odds = svg("text", { x: 170, y: 90, "font-size": 15, fill: C.ink, "font-family": "inherit" }); s.appendChild(odds);
    var measure = btn("Measure"), reset = btn("Reset", "alt"), many = btn("Measure ×100", "alt");
    var lean = range(0, 100, 50); var leanOut = readout("");
    var tally = el("div", { class: "tally" });
    var hb = el("i"), tb = el("i");
    tally.appendChild(el("span", { text: "0 (heads)" })); tally.appendChild(el("div", { class: "bar" }, [hb])); var hn = el("span", { text: "0" }); tally.appendChild(hn);
    tally.appendChild(el("span", { text: "1 (tails)" })); tally.appendChild(el("div", { class: "bar t" }, [tb])); var tn = el("span", { text: "0" }); tally.appendChild(tn);
    function draw() {
      odds.textContent = "lean: " + Math.round(p * 100) + "% toward 0";
      leanOut.textContent = Math.round(p * 100) + "% / " + Math.round((1 - p) * 100) + "%";
      var n = heads + tails || 1;
      hb.style.setProperty("--v", heads / n); tb.style.setProperty("--v", tails / n);
      hn.textContent = heads + (n > 1 ? " (" + Math.round(100 * heads / n) + "%)" : ""); tn.textContent = tails + (n > 1 ? " (" + Math.round(100 * tails / n) + "%)" : "");
      if (landed === null) { g.setAttribute("class", RM ? "coin" : "coin air"); face.textContent = "?"; lab.textContent = RM ? "in the air (spin not shown)" : "in the air"; disc.setAttribute("fill", C.gold); }
      else { g.setAttribute("class", "coin"); face.textContent = landed; lab.textContent = "measured: it is " + landed + " now"; disc.setAttribute("fill", landed === "0" ? C.teal : C.violet); }
    }
    function once() { var r = Math.random() < p ? "0" : "1"; if (r === "0") heads++; else tails++; return r; }
    measure.onclick = function () { if (landed !== null) return; landed = once(); draw(); };
    many.onclick = function () { for (var i = 0; i < 100; i++) once(); landed = null; draw(); };
    reset.onclick = function () { landed = null; draw(); };
    lean.oninput = function () { p = lean.value / 100; landed = null; draw(); };
    root.appendChild(s);
    root.appendChild(el("div", { class: "row" }, [measure, reset, many]));
    root.appendChild(el("div", { class: "row" }, [el("label", { text: "lean toward 0" }, [lean]), leanOut]));
    root.appendChild(tally);
    root.appendChild(el("p", { class: "note", text: "The lean sets the odds. A measured coin stays put until you reset it; there is no second look at the same superposition." }));
    draw();
  }

  /* ---------------------------------------------------------------- 2  the Bloch sphere */
  function blochSvg(size) {
    var s = svg("svg", { viewBox: "0 0 200 200", width: size || 260, role: "img", "aria-label": "Bloch sphere" });
    s.appendChild(svg("circle", { cx: 100, cy: 100, r: 86, fill: "none", stroke: C.mute, "stroke-width": 1.5 }));
    s.appendChild(svg("ellipse", { cx: 100, cy: 100, rx: 86, ry: 26, fill: "none", stroke: C.mute, "stroke-width": 1, "stroke-dasharray": "3 3" }));
    s.appendChild(svg("line", { x1: 100, y1: 14, x2: 100, y2: 186, stroke: C.mute, "stroke-width": 1, "stroke-dasharray": "3 3" }));
    var t0 = svg("text", { x: 100, y: 10, "text-anchor": "middle", "font-size": 11, fill: C.ink, "font-family": "inherit" }); t0.textContent = "0"; s.appendChild(t0);
    var t1 = svg("text", { x: 100, y: 198, "text-anchor": "middle", "font-size": 11, fill: C.ink, "font-family": "inherit" }); t1.textContent = "1"; s.appendChild(t1);
    var shaft = svg("line", { x1: 100, y1: 100, x2: 100, y2: 14, stroke: C.gold, "stroke-width": 4, "stroke-linecap": "round" });
    var tip = svg("circle", { cx: 100, cy: 14, r: 7, fill: C.gold, stroke: C.ink, "stroke-width": 2 });
    var shadow = svg("ellipse", { cx: 100, cy: 100, rx: 0, ry: 0, fill: C.gold, opacity: .25 });
    s.appendChild(shadow); s.appendChild(shaft); s.appendChild(tip);
    s.set = function (theta, phi, len) {
      len = len === undefined ? 1 : len;
      var x = Math.sin(theta) * Math.cos(phi), y = Math.sin(theta) * Math.sin(phi), z = Math.cos(theta);
      var px = 100 + 86 * len * x, py = 100 - 86 * len * z + 26 * len * y;
      shaft.setAttribute("x2", px); shaft.setAttribute("y2", py); tip.setAttribute("cx", px); tip.setAttribute("cy", py);
      tip.setAttribute("r", 5 + 3 * (0.5 + 0.5 * -y));
      shadow.setAttribute("cx", 100 + 86 * len * x); shadow.setAttribute("cy", 100 + 26 * len * y); shadow.setAttribute("rx", 3 * len * Math.sin(theta) + 1); shadow.setAttribute("ry", 1.5);
    };
    return s;
  }
  function bloch(root) {
    var theta = 0, phi = 0;
    var s = blochSvg(280);
    var tilt = range(0, 180, 0), spin = range(0, 360, 0);
    var out = readout("");
    var X = btn("X  flip"), Z = btn("Z  half-turn of phase"), H = btn("H  tip into the air"), R = btn("Reset", "alt");
    function draw() {
      s.set(theta, phi);
      var p0 = Math.cos(theta / 2) * Math.cos(theta / 2);
      out.textContent = "P(0) = " + Math.round(p0 * 100) + "%   P(1) = " + Math.round((1 - p0) * 100) + "%   phase " + Math.round(phi * 180 / Math.PI) + "°";
      tilt.value = Math.round(theta * 180 / Math.PI); spin.value = Math.round(((phi * 180 / Math.PI) % 360 + 360) % 360);
    }
    tilt.oninput = function () { theta = tilt.value * Math.PI / 180; draw(); };
    spin.oninput = function () { phi = spin.value * Math.PI / 180; draw(); };
    X.onclick = function () { theta = Math.PI - theta; phi = -phi; draw(); };
    Z.onclick = function () { phi = phi + Math.PI; draw(); };
    H.onclick = function () {
      // H is a half-turn about the axis between x and z: (x,y,z) -> (z,-y,x)
      var x = Math.sin(theta) * Math.cos(phi), y = Math.sin(theta) * Math.sin(phi), z = Math.cos(theta);
      var nx = z, ny = -y, nz = x;
      theta = Math.acos(Math.max(-1, Math.min(1, nz))); phi = Math.atan2(ny, nx); draw();
    };
    R.onclick = function () { theta = 0; phi = 0; draw(); };
    root.appendChild(el("div", { class: "row" }, [s, el("div", {}, [
      el("div", { class: "row" }, [el("label", { text: "tilt (sets the odds)" }, [tilt])]),
      el("div", { class: "row" }, [el("label", { text: "spin (sets the phase)" }, [spin])]),
      el("div", { class: "row" }, [out]),
      el("div", { class: "row" }, [X, Z, H, R])])]));
    root.appendChild(el("p", { class: "note", text: "Straight up reads 0 every time; on the equator, 50-50. The spin slider changes nothing you could measure on this one qubit. Press H from the top and the arrow lands on the equator: the coin is in the air." }));
    draw();
  }

  /* ---------------------------------------------------------------- 3  waves + two slits */
  function waves(root) {
    var W = 640, Hh = 200, ph = 0;
    var s = svg("svg", { viewBox: "0 0 " + W + " " + Hh, role: "img", "aria-label": "two waves and their sum" });
    var a = svg("path", { fill: "none", stroke: C.teal, "stroke-width": 2, opacity: .8 });
    var b = svg("path", { fill: "none", stroke: C.violet, "stroke-width": 2, opacity: .8 });
    var c = svg("path", { fill: "none", stroke: C.gold, "stroke-width": 4 });
    var mid = svg("line", { x1: 0, y1: Hh / 2, x2: W, y2: Hh / 2, stroke: C.line });
    s.appendChild(mid); s.appendChild(a); s.appendChild(b); s.appendChild(c);
    var lab = svg("text", { x: 8, y: 18, "font-size": 13, fill: C.mute, "font-family": "inherit" }); s.appendChild(lab);
    var slider = range(0, 360, 0), out = readout("");
    function path(f) { var d = ""; for (var x = 0; x <= W; x += 4) { var y = Hh / 2 - f(x) ; d += (x ? "L" : "M") + x + " " + y.toFixed(1); } return d; }
    function draw() {
      var k = 2 * Math.PI / 80, A = 34, off = ph * Math.PI / 180;
      a.setAttribute("d", path(function (x) { return A * Math.sin(k * x); }));
      b.setAttribute("d", path(function (x) { return A * Math.sin(k * x + off); }));
      c.setAttribute("d", path(function (x) { return A * Math.sin(k * x) + A * Math.sin(k * x + off); }));
      var amp = Math.abs(2 * Math.cos(off / 2));
      out.textContent = "phase " + ph + "°  →  the sum is " + fmt(amp, 2) + "× one wave";
      lab.textContent = amp < 0.05 ? "flat: crest meets trough" : amp > 1.95 ? "double: crest meets crest" : "";
    }
    slider.oninput = function () { ph = +slider.value; draw(); };
    root.appendChild(s);
    root.appendChild(el("div", { class: "row" }, [el("label", { text: "phase of the second wave" }, [slider]), out]));
    draw();
    // the two-slit screen
    var cw = 640, chh = 220; var cv = el("canvas", { width: cw, height: chh, "aria-label": "electrons landing on a screen, one at a time" });
    var ctx = cv.getContext("2d"); var open = 2, n = 0, timer = null;
    var run = btn("Fire electrons"), stop = btn("Stop", "alt"), clear = btn("Clear", "alt"), slit = btn("Close one slit", "alt"), cnt = readout("0 landed");
    function pdf(x) { var u = (x - cw / 2) / cw * 22; var env = Math.pow(Math.sin(Math.PI * u / 3.2 + 1e-9) / (Math.PI * u / 3.2 + 1e-9), 2); return open === 2 ? Math.pow(Math.cos(u * 2.6), 2) * env : env; }
    function clearScreen() { ctx.fillStyle = "#070b13"; ctx.fillRect(0, 0, cw, chh); n = 0; cnt.textContent = "0 landed"; }
    function fire(k) {
      for (var i = 0; i < k; i++) {
        var x, y; do { x = Math.random() * cw; } while (Math.random() > pdf(x));
        y = chh / 2 + (Math.random() + Math.random() + Math.random() - 1.5) * chh * 0.5;
        ctx.fillStyle = open === 2 ? "rgba(168,145,242,.85)" : "rgba(47,196,189,.85)"; ctx.fillRect(x, y, 2, 2); n++;
      }
      cnt.textContent = n + " landed" + (open === 1 ? " (one slit)" : "");
    }
    run.onclick = function () { if (timer) return; if (RM) { fire(3000); return; } timer = setInterval(function () { fire(40); if (n > 30000) { clearInterval(timer); timer = null; } }, 40); };
    stop.onclick = function () { clearInterval(timer); timer = null; };
    clear.onclick = clearScreen;
    slit.onclick = function () { open = open === 2 ? 1 : 2; slit.textContent = open === 2 ? "Close one slit" : "Open both slits"; clearScreen(); };
    clearScreen();
    root.appendChild(el("h3", { text: "The two-slit screen" }));
    root.appendChild(cv);
    root.appendChild(el("div", { class: "row" }, [run, stop, clear, slit, cnt]));
    root.appendChild(el("p", { class: "note", text: "Each dot is one electron. With both slits open the dots build stripes: the electron went through both as a wave and interfered with itself. Close a slit and the stripes go." }));
  }

  /* ---------------------------------------------------------------- 4  the entangled pair + Bell */
  function pair(root) {
    var left = null, right = null, same = 0, runs = 0;
    var s = svg("svg", { viewBox: "0 0 360 150", role: "img", "aria-label": "two entangled coins" });
    function mk(x) { var g = svg("g", { transform: "translate(" + x + " 70)", class: RM ? "coin" : "coin air" }); var d = svg("circle", { r: 44, fill: C.gold, stroke: C.ink, "stroke-width": 3 }); var t = svg("text", { "text-anchor": "middle", y: 14, "font-size": 36, "font-weight": 800, fill: C.ink, "font-family": "inherit" }); t.textContent = "?"; g.appendChild(d); g.appendChild(t); s.appendChild(g); return { g: g, d: d, t: t }; }
    var link = svg("path", { d: "M130 70 Q180 20 230 70", fill: "none", stroke: C.violet, "stroke-width": 2, "stroke-dasharray": "5 4", class: "pulse" }); s.appendChild(link);
    var L = mk(86), Rr = mk(274);
    var mL = btn("Measure left"), mR = btn("Measure right"), re = btn("New pair", "alt"), twenty = btn("Run 20 pairs", "alt"), out = readout("");
    function show(o, v) { o.g.setAttribute("class", "coin"); o.t.textContent = v; o.d.setAttribute("fill", v === "0" ? C.teal : C.violet); }
    function land() { var v = Math.random() < 0.5 ? "0" : "1"; left = right = v; show(L, v); show(Rr, v); runs++; same++; draw(); }
    function draw() { out.textContent = runs + " pairs, matched " + same + " of " + runs; }
    mL.onclick = function () { if (left === null) land(); };
    mR.onclick = mL.onclick;
    re.onclick = function () { left = right = null; [L, Rr].forEach(function (o) { o.g.setAttribute("class", RM ? "coin" : "coin air"); o.t.textContent = "?"; o.d.setAttribute("fill", C.gold); }); };
    twenty.onclick = function () { for (var i = 0; i < 20; i++) { runs++; same++; } land(); };
    root.appendChild(s);
    root.appendChild(el("div", { class: "row" }, [mL, mR, re, twenty, out]));
    root.appendChild(el("p", { class: "note", text: "Measure either coin: 0 or 1 at random. The other lands to match. Neither had picked until the first was caught." }));
    // Bell: three angles, 0°, 120°, 240°. Same setting: always match. Different: quantum matches 25%; any pre-written plan matches at least 33%.
    var q = { same: 0, sameN: 0, diff: 0, diffN: 0 };
    var bo = readout(""), bell = btn("Run 300 Bell trials"), bclear = btn("Clear", "alt");
    var bars = el("div", { class: "tally" }); var bq = el("i"), bc = el("i");
    bars.appendChild(el("span", { text: "quantum, different angles" })); bars.appendChild(el("div", { class: "bar" }, [bq])); var bqn = el("span", { text: "–" }); bars.appendChild(bqn);
    bars.appendChild(el("span", { text: "lowest any hidden plan can go" })); bars.appendChild(el("div", { class: "bar t" }, [bc])); var bcn = el("span", { text: "33%" }); bars.appendChild(bcn);
    bc.style.setProperty("--v", 1 / 3);
    function trial() {
      var a = Math.floor(Math.random() * 3), b = Math.floor(Math.random() * 3);
      var d = Math.abs(a - b) * 120 * Math.PI / 180; var pm = Math.cos(d / 2) * Math.cos(d / 2);
      var m = Math.random() < pm;
      if (a === b) { q.sameN++; if (m) q.same++; } else { q.diffN++; if (m) q.diff++; }
    }
    function bdraw() {
      var r = q.diffN ? q.diff / q.diffN : 0; bq.style.setProperty("--v", r); bqn.textContent = q.diffN ? Math.round(r * 100) + "% of " + q.diffN : "–";
      bo.textContent = "same angle: " + q.same + "/" + q.sameN + " matched";
    }
    bell.onclick = function () { for (var i = 0; i < 300; i++) trial(); bdraw(); };
    bclear.onclick = function () { q = { same: 0, sameN: 0, diff: 0, diffN: 0 }; bdraw(); };
    root.appendChild(el("h3", { text: "The Bell test" }));
    root.appendChild(el("p", { class: "small", text: "Each side picks one of three angles at random, 120° apart, and measures. When both pick the same angle the coins always match. When they pick different angles, quantum mechanics says they match one time in four. If each coin carried a hidden plan for all three angles, the different-angle match rate could not fall below one in three. Run it." }));
    root.appendChild(el("div", { class: "row" }, [bell, bclear, bo]));
    root.appendChild(bars);
    bdraw();
  }

  /* ---------------------------------------------------------------- 5  the circuit */
  function circuit(root) {
    var step = 0; var states = [[1, 0, 0, 0], [0.7071, 0, 0.7071, 0], [0.7071, 0, 0, 0.7071]];
    var names = ["00", "01", "10", "11"];
    var s = svg("svg", { viewBox: "0 0 420 130", role: "img", "aria-label": "a two-qubit circuit: H then CNOT" });
    [40, 95].forEach(function (y, i) { s.appendChild(svg("line", { x1: 30, y1: y, x2: 400, y2: y, stroke: C.ink, "stroke-width": 2 })); var t = svg("text", { x: 8, y: y + 5, "font-size": 14, fill: C.ink, "font-family": "inherit" }); t.textContent = "q" + i; s.appendChild(t); });
    var hbox = svg("rect", { x: 110, y: 22, width: 36, height: 36, rx: 6, fill: C.teal, stroke: C.ink, "stroke-width": 2 }); s.appendChild(hbox);
    var ht = svg("text", { x: 128, y: 47, "text-anchor": "middle", "font-size": 20, "font-weight": 800, fill: "#fff", "font-family": "inherit" }); ht.textContent = "H"; s.appendChild(ht);
    var cl = svg("line", { x1: 240, y1: 40, x2: 240, y2: 95, stroke: C.ink, "stroke-width": 2 }); s.appendChild(cl);
    var cd = svg("circle", { cx: 240, cy: 40, r: 7, fill: C.ink }); s.appendChild(cd);
    var cx = svg("circle", { cx: 240, cy: 95, r: 13, fill: "none", stroke: C.ink, "stroke-width": 2 }); s.appendChild(cx);
    s.appendChild(svg("line", { x1: 240, y1: 82, x2: 240, y2: 108, stroke: C.ink, "stroke-width": 2 })); s.appendChild(svg("line", { x1: 227, y1: 95, x2: 253, y2: 95, stroke: C.ink, "stroke-width": 2 }));
    var cursor = svg("line", { x1: 70, y1: 10, x2: 70, y2: 120, stroke: C.gold, "stroke-width": 3, "stroke-dasharray": "6 4" }); s.appendChild(cursor);
    var b1 = blochSvg(150), b2 = blochSvg(150);
    var bars = el("div", { class: "tally" }); var ib = [], ns = [];
    names.forEach(function (nm) { bars.appendChild(el("span", { text: nm })); var i = el("i"); ib.push(i); bars.appendChild(el("div", { class: "bar" }, [i])); var n = el("span"); ns.push(n); bars.appendChild(n); });
    var next = btn("Step"), back = btn("Back", "alt"), out = readout("");
    var cap2 = el("div", { class: "small mute", text: "" });
    function draw() {
      cursor.setAttribute("x1", [70, 190, 330][step]); cursor.setAttribute("x2", [70, 190, 330][step]);
      var st = states[step];
      st.forEach(function (a, i) { ib[i].style.setProperty("--v", a * a); ns[i].textContent = Math.round(a * a * 100) + "%"; });
      out.textContent = ["start: both 0", "after H: q0 is in the air", "after CNOT: entangled"][step];
      b1.set(step === 0 ? 0 : Math.PI / 2, 0, step === 2 ? 0 : 1);
      b2.set(0, 0, step === 2 ? 0 : 1);
      cap2.textContent = step === 2 ? "After the CNOT neither qubit has an arrow of its own. The pair has one state, and it is not two arrows." : "";
    }
    next.onclick = function () { step = Math.min(2, step + 1); draw(); };
    back.onclick = function () { step = Math.max(0, step - 1); draw(); };
    root.appendChild(s);
    root.appendChild(el("div", { class: "row" }, [next, back, out]));
    root.appendChild(el("div", { class: "row" }, [el("div", {}, [el("div", { class: "small mute", text: "q0" }), b1]), el("div", {}, [el("div", { class: "small mute", text: "q1" }), b2]), el("div", {}, [el("div", { class: "small mute", text: "odds of each readout" }), bars])]));
    root.appendChild(cap2);
    draw();
  }

  /* ---------------------------------------------------------------- 6  Grover */
  function grover(root) {
    var N = 16, marked = 10, amp, steps;
    var W = 640, Hh = 220, s = svg("svg", { viewBox: "0 0 " + W + " " + Hh, role: "img", "aria-label": "sixteen amplitudes, one marked" });
    s.appendChild(svg("line", { x1: 20, y1: Hh / 2, x2: W - 10, y2: Hh / 2, stroke: C.line }));
    var rects = [];
    for (var i = 0; i < N; i++) { var r = svg("rect", { x: 24 + i * 38, width: 28, fill: i === marked ? C.gold : C.teal, rx: 3 }); rects.push(r); s.appendChild(r); }
    var lab = svg("text", { x: 24, y: 16, "font-size": 13, fill: C.mute, "font-family": "inherit" }); s.appendChild(lab);
    var stepB = btn("Step"), reset = btn("Reset", "alt"), out = readout("");
    function init() { amp = []; for (var i = 0; i < N; i++) amp.push(1 / Math.sqrt(N)); steps = 0; }
    function draw() {
      amp.forEach(function (a, i) { var h = a * 160; rects[i].setAttribute("y", h >= 0 ? Hh / 2 - h : Hh / 2); rects[i].setAttribute("height", Math.abs(h)); });
      var p = amp[marked] * amp[marked];
      out.textContent = "step " + steps + ": chance of reading the marked box " + Math.round(p * 100) + "%";
      lab.textContent = "bars are amplitudes; below the line is negative. The best number of steps for 16 boxes is 3.";
    }
    stepB.onclick = function () {
      amp[marked] = -amp[marked];                                   // the oracle: flip the sign of the marked one
      var mean = amp.reduce(function (a, b) { return a + b; }, 0) / N;
      amp = amp.map(function (a) { return 2 * mean - a; });        // reflect about the mean
      steps++; draw();
    };
    reset.onclick = function () { init(); draw(); };
    root.appendChild(s); root.appendChild(el("div", { class: "row" }, [stepB, reset, out]));
    root.appendChild(el("p", { class: "note", text: "Each step: flip the marked bar, then reflect every bar about the average. The marked one grows; go past the peak and it shrinks again." }));
    init(); draw();
  }

  /* ---------------------------------------------------------------- 7  the period wheel */
  function period(root) {
    var Nn = 15, base = 7, x = 0, visited = {}, timer = null;
    var s = svg("svg", { viewBox: "0 0 260 260", width: 300, role: "img", "aria-label": "remainders of powers of the base, divided by 15" });
    var spots = [];
    for (var i = 0; i < Nn; i++) { var a = -Math.PI / 2 + i * 2 * Math.PI / Nn; var cx = 130 + 100 * Math.cos(a), cy = 130 + 100 * Math.sin(a); var c = svg("circle", { cx: cx, cy: cy, r: 12, fill: C.line, stroke: C.ink, "stroke-width": 1.5 }); var t = svg("text", { x: cx, y: cy + 4, "text-anchor": "middle", "font-size": 11, "font-family": "inherit", fill: C.ink }); t.textContent = i; s.appendChild(c); s.appendChild(t); spots.push(c); }
    var hand = svg("line", { x1: 130, y1: 130, x2: 130, y2: 30, stroke: C.gold, "stroke-width": 4, "stroke-linecap": "round" }); s.appendChild(hand);
    var run = btn("Run"), stepB = btn("Step"), reset = btn("Reset", "alt"), sel = el("select");
    [2, 4, 7, 8, 11, 13].forEach(function (b) { var o = el("option", { value: b, text: b }); if (b === base) o.selected = true; sel.appendChild(o); });
    var out = readout(""), seq = el("div", { class: "mono small" }), fact = el("div", { class: "small" });
    function modpow(b, e, m) { var r = 1; for (var i = 0; i < e; i++) r = (r * b) % m; return r; }
    function gcd(a, b) { while (b) { var t = b; b = a % b; a = t; } return a; }
    function draw() {
      var v = modpow(base, x, Nn); var a = -Math.PI / 2 + v * 2 * Math.PI / Nn;
      hand.setAttribute("x2", 130 + 88 * Math.cos(a)); hand.setAttribute("y2", 130 + 88 * Math.sin(a));
      visited[v] = true; spots.forEach(function (c, i) { c.setAttribute("fill", visited[i] ? C.teal : C.line); });
      out.textContent = base + "^" + x + " mod 15 = " + v;
      var list = []; for (var i = 0; i <= Math.max(x, 8); i++) list.push(modpow(base, i, Nn)); seq.textContent = list.join("  ");
      var r = 1; while (modpow(base, r, Nn) !== 1) r++;
      var p = gcd(modpow(base, r / 2, Nn) - 1, Nn), q = gcd(modpow(base, r / 2, Nn) + 1, Nn);
      fact.textContent = r % 2 ? "period " + r + " is odd: pick another base" : "period " + r + ", so " + base + "^" + (r / 2) + " = " + modpow(base, r / 2, Nn) + "; gcd(" + (modpow(base, r / 2, Nn) - 1) + ", 15) = " + p + " and gcd(" + (modpow(base, r / 2, Nn) + 1) + ", 15) = " + q + "  →  15 = " + p + " × " + q;
    }
    stepB.onclick = function () { x++; draw(); };
    run.onclick = function () { if (timer) { clearInterval(timer); timer = null; run.textContent = "Run"; return; } if (RM) { for (var i = 0; i < 8; i++) { x++; } draw(); return; } run.textContent = "Pause"; timer = setInterval(function () { x++; draw(); if (x > 60) { clearInterval(timer); timer = null; run.textContent = "Run"; } }, 500); };
    reset.onclick = function () { x = 0; visited = {}; draw(); };
    sel.onchange = function () { base = +sel.value; x = 0; visited = {}; draw(); };
    root.appendChild(el("div", { class: "row" }, [s, el("div", {}, [el("div", { class: "row" }, [el("label", { text: "base" }, [sel]), run, stepB, reset]), el("div", { class: "row" }, [out]), seq, fact])]));
    root.appendChild(el("p", { class: "note", text: "The hand only ever lands on a few spots, and the repeat length is the period. A quantum computer finds that length for numbers too big to step through, by making every wrong length cancel." }));
    draw();
  }

  /* ---------------------------------------------------------------- 8  decoherence */
  function decay(root) {
    var s = blochSvg(280); var T = 1, t = 0, phase = 0, raf = null, last = 0;
    var temp = range(0, 100, 30), out = readout(""), start = btn("Start"), reset = btn("Reset", "alt"), stepB = btn("Step", "alt");
    function T2() { var u = temp.value / 100; return 0.4 + 24 * Math.pow(1 - u, 3); }   // seconds of demo time
    function draw() { var len = Math.exp(-t / T2()); phase += 0.02 * (0.2 + temp.value / 100) * (Math.random() - 0.5) * 8; s.set(Math.PI / 2, phase, len); out.textContent = "arrow length " + fmt(len, 2) + "  ·  t = " + fmt(t, 1) + " s  ·  T2 ≈ " + fmt(T2(), 1) + " s"; }
    function frame(now) { if (!last) last = now; var dt = (now - last) / 1000; last = now; t += dt; draw(); if (t < 4 * T2() + 2) raf = requestAnimationFrame(frame); else raf = null; }
    start.onclick = function () { if (raf) return; if (RM) { return; } last = 0; raf = requestAnimationFrame(frame); };
    stepB.onclick = function () { t += 0.5; draw(); };
    reset.onclick = function () { if (raf) cancelAnimationFrame(raf); raf = null; t = 0; phase = 0; draw(); };
    temp.oninput = draw;
    root.appendChild(el("div", { class: "row" }, [s, el("div", {}, [el("div", { class: "row" }, [el("label", { text: "cold ← drafts → warm" }, [temp])]), el("div", { class: "row" }, [RM ? stepB : start, RM ? start : stepB, reset]), el("div", { class: "row" }, [out])])]));
    root.appendChild(el("p", { class: "note", text: "The arrow starts on the equator, a coin in the air. Drafts jostle its phase and shrink it toward the centre, where it is a plain coin with no lean and no phase: decohered. The times are made up for the demo; the shape of the curve is not." }));
    draw();
  }

  /* ---------------------------------------------------------------- 9  the vote + the threshold */
  function vote(root) {
    var q = [0, 0, 0], logical = 0;
    var s = svg("svg", { viewBox: "0 0 360 120", role: "img", "aria-label": "three qubits and two checks" });
    var qs = [], cs = [];
    [60, 180, 300].forEach(function (x, i) { var c = svg("circle", { cx: x, cy: 40, r: 26, fill: C.teal, stroke: C.ink, "stroke-width": 2 }); var t = svg("text", { x: x, y: 48, "text-anchor": "middle", "font-size": 22, "font-weight": 800, fill: "#fff", "font-family": "inherit" }); s.appendChild(c); s.appendChild(t); qs.push({ c: c, t: t }); });
    [120, 240].forEach(function (x) { var r = svg("rect", { x: x - 22, y: 82, width: 44, height: 28, rx: 6, fill: C.line, stroke: C.ink, "stroke-width": 1.5 }); var t = svg("text", { x: x, y: 101, "text-anchor": "middle", "font-size": 13, "font-family": "inherit", fill: C.ink }); s.appendChild(svg("line", { x1: x - 60, y1: 66, x2: x, y2: 82, stroke: C.mute })); s.appendChild(svg("line", { x1: x + 60, y1: 66, x2: x, y2: 82, stroke: C.mute })); s.appendChild(r); s.appendChild(t); cs.push({ r: r, t: t }); });
    var set = btn("Store a 1"), noise = btn("Noise"), fix = btn("Fix"), reset = btn("Reset", "alt"), out = readout("");
    function draw() {
      qs.forEach(function (o, i) { o.t.textContent = q[i]; o.c.setAttribute("fill", q[i] ? C.violet : C.teal); });
      var s1 = q[0] ^ q[1], s2 = q[1] ^ q[2];
      cs[0].t.textContent = s1 ? "differ" : "agree"; cs[1].t.textContent = s2 ? "differ" : "agree";
      cs[0].r.setAttribute("fill", s1 ? C.red : C.line); cs[1].r.setAttribute("fill", s2 ? C.red : C.line);
      var where = s1 && s2 ? "middle" : s1 ? "left" : s2 ? "right" : null;
      out.textContent = where ? "the checks point at the " + where + " qubit, without reading any of them" : "all agree: stored " + logical;
    }
    set.onclick = function () { logical = 1 - logical; q = [logical, logical, logical]; draw(); };
    noise.onclick = function () { var i = Math.floor(Math.random() * 3); q[i] ^= 1; draw(); };
    fix.onclick = function () { var s1 = q[0] ^ q[1], s2 = q[1] ^ q[2]; if (s1 && s2) q[1] ^= 1; else if (s1) q[0] ^= 1; else if (s2) q[2] ^= 1; draw(); };
    reset.onclick = function () { logical = 0; q = [0, 0, 0]; draw(); };
    root.appendChild(s); root.appendChild(el("div", { class: "row" }, [set, noise, fix, reset, out]));
    root.appendChild(el("p", { class: "note", text: "Each check asks two neighbours whether they agree. It learns nothing about the value stored, only whether something changed. Two flips at once would fool it; a bigger code catches more." }));
    draw();
    // threshold
    var d = range(3, 15, 3, 2), p = range(1, 30, 5), o2 = readout("");
    var W = 640, Hh = 220, g = svg("svg", { viewBox: "0 0 " + W + " " + Hh, role: "img", "aria-label": "logical error against code size" });
    g.appendChild(svg("line", { x1: 50, y1: 190, x2: 620, y2: 190, stroke: C.mute })); g.appendChild(svg("line", { x1: 50, y1: 20, x2: 50, y2: 190, stroke: C.mute }));
    var yl = svg("text", { x: 6, y: 24, "font-size": 12, fill: C.mute, "font-family": "inherit" }); yl.textContent = "error"; g.appendChild(yl);
    var xl = svg("text", { x: 560, y: 210, "font-size": 12, fill: C.mute, "font-family": "inherit" }); xl.textContent = "code size d"; g.appendChild(xl);
    var pathA = svg("path", { fill: "none", stroke: C.gold, "stroke-width": 3 }); g.appendChild(pathA);
    var mark = svg("circle", { r: 7, fill: C.gold, stroke: C.ink, "stroke-width": 2 }); g.appendChild(mark);
    var thr = svg("line", { x1: 50, x2: 620, stroke: C.red, "stroke-dasharray": "5 4" }); g.appendChild(thr);
    var thrT = svg("text", { x: 560, "font-size": 12, fill: C.red, "font-family": "inherit" }); thrT.textContent = "physical error"; g.appendChild(thrT);
    function pl(pp, dd) { return 0.1 * Math.pow(pp / 0.01, (dd + 1) / 2); }   // the textbook shape: (p/p_th)^((d+1)/2)
    function y(v) { var lv = Math.log10(Math.max(v, 1e-12)); return 190 - (lv + 12) / 12 * 170; }
    function draw2() {
      var pp = p.value / 1000; var dd = +d.value; var path = "";
      for (var k = 3; k <= 15; k += 2) { var px = 50 + (k - 3) / 12 * 560; path += (k === 3 ? "M" : "L") + px + " " + y(pl(pp, k)); }
      pathA.setAttribute("d", path); mark.setAttribute("cx", 50 + (dd - 3) / 12 * 560); mark.setAttribute("cy", y(pl(pp, dd)));
      thr.setAttribute("y1", y(pp)); thr.setAttribute("y2", y(pp)); thrT.setAttribute("y", y(pp) - 5);
      var le = pl(pp, dd);
      o2.textContent = "physical error " + fmt(pp * 100, 1) + "%  ·  d = " + dd + "  ·  logical error " + (le < 1e-3 ? le.toExponential(1) : fmt(le, 3)) + (pp < 0.01 ? "  (under the line: bigger is better)" : pp > 0.01 ? "  (over the line: bigger is worse)" : "  (on the line)");
    }
    d.oninput = draw2; p.oninput = draw2;
    root.appendChild(el("h3", { text: "The threshold" }));
    root.appendChild(g);
    root.appendChild(el("div", { class: "row" }, [el("label", { text: "physical error per gate" }, [p]), el("label", { text: "code size" }, [d]), o2]));
    root.appendChild(el("p", { class: "note", text: "The curve is the textbook shape for a surface code with a 1% threshold, not a measurement. Under the line, each two steps of size cut the error by the same factor; over it, growing the code adds error. Willow, December 2024: 3×3 → 5×5 → 7×7, error halving each step." }));
    draw2();
  }

  var DEMOS = { coin: coin, bloch: bloch, waves: waves, pair: pair, circuit: circuit, grover: grover, period: period, decay: decay, vote: vote };
  document.querySelectorAll("[data-demo]").forEach(function (root) { var f = DEMOS[root.getAttribute("data-demo")]; if (f) { root.innerHTML = ""; f(root); } });

  // timeline reveal
  var tl = document.querySelector(".tl");
  if (tl) {
    if (!RM && "IntersectionObserver" in window) { tl.classList.remove("nojs"); var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } }); }, { rootMargin: "0px 0px -8% 0px" }); tl.querySelectorAll("li").forEach(function (li) { io.observe(li); }); }
  }
})();
