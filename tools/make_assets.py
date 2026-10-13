#!/usr/bin/env python3
"""Generate README artwork for PARADIGMA (light + dark variants).

Visual language: an engineering drawing sheet. Graph-paper grid, sheet frame
with zone markers, a title block, and a falling cost curve on a log scale that
crosses a viability threshold. Pure SVG, system fonts only (GitHub renders
README images as <img>, so web fonts and scripts are not available).

    python3 tools/make_assets.py   -> writes assets/*.svg
"""
import math
import os
import random

OUT = os.path.join(os.path.dirname(__file__), "..", "assets")
FONT = "Bahnschrift, 'DIN Alternate', 'DIN Condensed', 'Barlow Condensed', 'Roboto Condensed', 'Arial Narrow', Arial, sans-serif"

THEMES = {
    "light": dict(paper="#EDF1F4", ink="#1B2A38", soft="#5B6B7A", grid="#D3DCE4", grid2="#BAC7D3",
                  amber="#B97F00", teal="#0B7F6F", tealfill="#0B7F6F", dot="#1B2A38"),
    "dark": dict(paper="#0F2236", ink="#E4ECF3", soft="#9FB4C7", grid="#1C3550", grid2="#284767",
                 amber="#F0B23E", teal="#3CC9B0", tealfill="#3CC9B0", dot="#E4ECF3"),
}


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-label="{title}" font-family="{FONT}">\n<title>{title}</title>\n{body}\n</svg>\n')


def grid(x0, y0, x1, y1, step, c, minor, major, every=5):
    out = []
    i = 0
    x = x0
    while x <= x1 + 0.1:
        col = major if i % every == 0 else minor
        out.append(f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y1}" stroke="{col}" stroke-width="{0.9 if i % every == 0 else 0.5}"/>')
        x += step; i += 1
    i = 0
    y = y0
    while y <= y1 + 0.1:
        col = major if i % every == 0 else minor
        out.append(f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{col}" stroke-width="{0.9 if i % every == 0 else 0.5}"/>')
        y += step; i += 1
    return "\n".join(out)


# ------------------------------------------------------------------ banner
def banner(t):
    W, H = 1280, 420
    b = [f'<rect width="{W}" height="{H}" fill="{t["paper"]}"/>']
    # sheet frame with zone markers (like a drawing sheet)
    b.append(f'<rect x="16" y="16" width="{W-32}" height="{H-32}" fill="none" stroke="{t["ink"]}" stroke-width="1.6"/>')
    b.append(f'<rect x="30" y="30" width="{W-60}" height="{H-60}" fill="none" stroke="{t["ink"]}" stroke-width="0.8"/>')
    cols = 8
    for i in range(cols + 1):
        x = 30 + i * (W - 60) / cols
        if 0 < i < cols:
            b.append(f'<line x1="{x:.1f}" y1="16" x2="{x:.1f}" y2="30" stroke="{t["ink"]}" stroke-width="0.8"/>')
            b.append(f'<line x1="{x:.1f}" y1="{H-30}" x2="{x:.1f}" y2="{H-16}" stroke="{t["ink"]}" stroke-width="0.8"/>')
        if i < cols:
            cx = x + (W - 60) / cols / 2
            b.append(f'<text x="{cx:.1f}" y="27" font-size="10" fill="{t["soft"]}" text-anchor="middle">{i+1}</text>')
            b.append(f'<text x="{cx:.1f}" y="{H-19}" font-size="10" fill="{t["soft"]}" text-anchor="middle">{i+1}</text>')
    for j, r in enumerate("ABC"):
        y = 30 + j * (H - 60) / 3
        if j:
            b.append(f'<line x1="16" y1="{y:.1f}" x2="30" y2="{y:.1f}" stroke="{t["ink"]}" stroke-width="0.8"/>')
            b.append(f'<line x1="{W-30}" y1="{y:.1f}" x2="{W-16}" y2="{y:.1f}" stroke="{t["ink"]}" stroke-width="0.8"/>')
        cy = y + (H - 60) / 6 + 4
        b.append(f'<text x="23" y="{cy:.1f}" font-size="10" fill="{t["soft"]}" text-anchor="middle">{r}</text>')
        b.append(f'<text x="{W-23}" y="{cy:.1f}" font-size="10" fill="{t["soft"]}" text-anchor="middle">{r}</text>')

    # chart on graph paper
    X0, Y0, X1, Y1 = 640, 62, 1220, 322
    b.append(grid(X0, Y0, X1, Y1, 13, t["grid"], t["grid"], t["grid2"]))
    b.append(f'<line x1="{X0}" y1="{Y0}" x2="{X0}" y2="{Y1}" stroke="{t["ink"]}" stroke-width="1.2"/>')
    b.append(f'<line x1="{X0}" y1="{Y1}" x2="{X1}" y2="{Y1}" stroke="{t["ink"]}" stroke-width="1.2"/>')
    # log decade ticks
    for k, lab in enumerate(["10⁴", "10³", "10²"]):
        y = Y0 + 16 + k * 112
        b.append(f'<line x1="{X0-6}" y1="{y}" x2="{X0}" y2="{y}" stroke="{t["ink"]}" stroke-width="1"/>')
        b.append(f'<text x="{X0-10}" y="{y+4}" font-size="12" fill="{t["soft"]}" text-anchor="end">{lab}</text>')
    b.append(f'<text x="{X0-44}" y="{(Y0+Y1)/2}" font-size="12" fill="{t["soft"]}" text-anchor="middle" '
             f'transform="rotate(-90 {X0-44} {(Y0+Y1)/2})">cost per unit of performance · log</text>')
    b.append(f'<text x="{X1}" y="{Y1+22}" font-size="12" fill="{t["soft"]}" text-anchor="end">20 years</text>')

    random.seed(7)
    n = 15
    xs = [X0 + 30 + i * (X1 - X0 - 60) / (n - 1) for i in range(n)]
    trend = lambda x: Y0 + 30 + (x - X0 - 30) / (X1 - X0 - 60) * 236
    meds = []
    for i, x in enumerate(xs):
        ym = trend(x) + random.uniform(-9, 9)
        meds.append((x, ym))
        for _ in range(random.randint(1, 3)):
            b.append(f'<circle cx="{x + random.uniform(-6, 6):.1f}" cy="{ym + random.uniform(-14, 14):.1f}" r="2.2" '
                     f'fill="{t["soft"]}" opacity="0.55"/>')
    b.append(f'<circle cx="{xs[6]+2:.1f}" cy="{Y0+8}" r="2.2" fill="{t["soft"]}" opacity="0.55"/>')  # an outlier the median ignores
    b.append('<polyline fill="none" stroke="{}" stroke-width="1.6" points="{}"/>'.format(
        t["ink"], " ".join(f"{x:.1f},{y:.1f}" for x, y in meds)))
    for x, y in meds:
        b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.6" fill="{t["paper"]}" stroke="{t["ink"]}" stroke-width="1.6"/>')
    b.append(f'<line x1="{X0+30}" y1="{trend(X0+30):.1f}" x2="{X1-30}" y2="{trend(X1-30):.1f}" '
             f'stroke="{t["ink"]}" stroke-width="1.2" stroke-dasharray="7 5" opacity="0.7"/>')
    # viability threshold
    TY = 228
    b.append(f'<line x1="{X0}" y1="{TY}" x2="{X1}" y2="{TY}" stroke="{t["amber"]}" stroke-width="2" stroke-dasharray="2 5" stroke-linecap="round"/>')
    b.append(f'<text x="{X0+10}" y="{TY-9}" font-size="13" fill="{t["amber"]}">viable below this line</text>')
    cx = X0 + 30 + (TY - Y0 - 30) / 236 * (X1 - X0 - 60)
    b.append(f'<circle cx="{cx:.1f}" cy="{TY}" r="11" fill="none" stroke="{t["teal"]}" stroke-width="2.2"/>')
    b.append(f'<circle cx="{cx:.1f}" cy="{TY}" r="4" fill="{t["teal"]}"/>')
    b.append(f'<line x1="{cx-8:.1f}" y1="{TY+8}" x2="{cx-40:.1f}" y2="{TY+40}" stroke="{t["teal"]}" stroke-width="1.2"/>')
    b.append(f'<text x="{cx-44:.1f}" y="{TY+54}" font-size="14" fill="{t["teal"]}" text-anchor="end">the constraint stops being true</text>')

    # wordmark + statement
    b.append(f'<text x="64" y="138" font-size="84" font-weight="700" textLength="416" lengthAdjust="spacingAndGlyphs" fill="{t["ink"]}">PARADIGMA</text>')
    b.append(f'<line x1="66" y1="160" x2="482" y2="160" stroke="{t["ink"]}" stroke-width="1"/>')
    b.append(f'<text x="66" y="194" font-size="21" fill="{t["ink"]}">Find the constraints that stopped being true,</text>')
    b.append(f'<text x="66" y="222" font-size="21" fill="{t["ink"]}">and who is building on them.</text>')

    # title block
    TX, TYb, TW, TH = 66, 284, 420, 74
    b.append(f'<rect x="{TX}" y="{TYb}" width="{TW}" height="{TH}" fill="none" stroke="{t["ink"]}" stroke-width="1.2"/>')
    b.append(f'<line x1="{TX}" y1="{TYb+37}" x2="{TX+TW}" y2="{TYb+37}" stroke="{t["ink"]}" stroke-width="0.8"/>')
    for fx in (0.5, 0.75):
        b.append(f'<line x1="{TX+TW*fx}" y1="{TYb+37}" x2="{TX+TW*fx}" y2="{TYb+TH}" stroke="{t["ink"]}" stroke-width="0.8"/>')
    b.append(f'<text x="{TX+10}" y="{TYb+15}" font-size="10" fill="{t["soft"]}">drawing</text>')
    b.append(f'<text x="{TX+10}" y="{TYb+31}" font-size="15" fill="{t["ink"]}">Constraint-shift panorama of any field</text>')
    cells = [("method", "agent skill", 0), ("scale", "log", 0.5), ("rev", "0.1", 0.75)]
    for lab, val, fx in cells:
        x = TX + TW * fx + 10
        b.append(f'<text x="{x}" y="{TYb+52}" font-size="10" fill="{t["soft"]}">{lab}</text>')
        b.append(f'<text x="{x}" y="{TYb+68}" font-size="15" fill="{t["ink"]}">{val}</text>')
    return svg(W, H, "\n".join(b), "PARADIGMA: find the constraints that stopped being true, and who is building on them")


# ---------------------------------------------------------------- pipeline
STEPS = [
    ("Map the field", "Break it into constraints:", "parts, labor, law, norms"),
    ("Price curves", "Yearly medians, robust trend,", "inflation removed"),
    ("Non-cost sweep", "Laws, expiring patents,", "skills, norms, supply"),
    ("Activity scan", "Who builds on each one:", "announced, deployed, paying"),
    ("Gap matrix", "How far it fell versus", "how many are building"),
    ("Why-not check", "Untried, tried too early,", "or still blocked"),
    ("Independent check", "A fresh agent re-opens", "every source"),
    ("Report", "Panorama, charts, and a", "workbook with every link"),
]


def pipeline(t):
    W, H = 1200, 372
    b = [f'<rect width="{W}" height="{H}" fill="{t["paper"]}"/>']
    b.append(grid(0, 0, W, H, 12, t["grid"], t["grid"], t["grid"], every=1000))
    bw, bh, gap, x0 = 248, 118, 48, 26
    rows = [(26, [0, 1, 2, 3]), (228, [7, 6, 5, 4])]
    pos = {}
    for y, idxs in rows:
        for col, i in enumerate(idxs):
            pos[i] = (x0 + col * (bw + gap), y)
    # connectors
    def arrow(x1, y1, x2, y2):
        ang = math.atan2(y2 - y1, x2 - x1)
        a1 = (x2 - 9 * math.cos(ang - 0.45), y2 - 9 * math.sin(ang - 0.45))
        a2 = (x2 - 9 * math.cos(ang + 0.45), y2 - 9 * math.sin(ang + 0.45))
        return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{t["ink"]}" stroke-width="1.3"/>'
                f'<polygon points="{x2},{y2} {a1[0]:.1f},{a1[1]:.1f} {a2[0]:.1f},{a2[1]:.1f}" fill="{t["ink"]}"/>')
    for i in range(7):
        (xa, ya), (xb, yb) = pos[i], pos[i + 1]
        if ya == yb and xb > xa:
            b.append(arrow(xa + bw, ya + bh / 2, xb - 2, yb + bh / 2))
        elif ya == yb:
            b.append(arrow(xa, ya + bh / 2, xb + bw + 2, yb + bh / 2))
        else:
            b.append(arrow(xa + bw / 2, ya + bh, xb + bw / 2, yb - 2))
    for i, (name, l1, l2) in enumerate(STEPS):
        x, y = pos[i]
        stroke = t["teal"] if i in (4, 5) else t["ink"]
        sw = 2 if i in (4, 5) else 1.2
        b.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}" fill="{t["paper"]}" stroke="{stroke}" stroke-width="{sw}"/>')
        b.append(f'<text x="{x+16}" y="{y+40}" font-size="30" font-weight="700" fill="{t["amber"]}">{i+1}</text>')
        b.append(f'<text x="{x+48}" y="{y+38}" font-size="21" font-weight="700" fill="{t["ink"]}">{name}</text>')
        b.append(f'<line x1="{x+16}" y1="{y+54}" x2="{x+bw-16}" y2="{y+54}" stroke="{t["grid2"]}" stroke-width="1"/>')
        b.append(f'<text x="{x+16}" y="{y+80}" font-size="15.5" fill="{t["soft"]}">{l1}</text>')
        b.append(f'<text x="{x+16}" y="{y+101}" font-size="15.5" fill="{t["soft"]}">{l2}</text>')
    return svg(W, H, "\n".join(b), "PARADIGMA pipeline: eight steps from mapping the field to the report")


# -------------------------------------------------------------- gap matrix
def gap(t):
    W, H = 900, 560
    b = [f'<rect width="{W}" height="{H}" fill="{t["paper"]}"/>']
    X0, Y0, X1, Y1 = 110, 40, 860, 470
    MX, MY = (X0 + X1) / 2, (Y0 + Y1) / 2
    b.append(grid(X0, Y0, X1, Y1, 15, t["grid"], t["grid"], t["grid2"], every=5))
    b.append(f'<rect x="{X0}" y="{Y0}" width="{MX-X0}" height="{MY-Y0}" fill="{t["tealfill"]}" opacity="0.13"/>')
    b.append(f'<rect x="{X0}" y="{Y0}" width="{X1-X0}" height="{Y1-Y0}" fill="none" stroke="{t["ink"]}" stroke-width="1.3"/>')
    b.append(f'<line x1="{MX}" y1="{Y0}" x2="{MX}" y2="{Y1}" stroke="{t["ink"]}" stroke-width="1"/>')
    b.append(f'<line x1="{X0}" y1="{MY}" x2="{X1}" y2="{MY}" stroke="{t["ink"]}" stroke-width="1"/>')
    q = [("White space", "fell far, few are building", X0 + 18, Y0 + 32, t["teal"]),
         ("Crowded", "fell far, many are building", MX + 18, Y0 + 32, t["ink"]),
         ("Dormant", "little change, little activity", X0 + 18, MY + 32, t["soft"]),
         ("Hype risk", "little change, many are building", MX + 18, MY + 32, t["amber"])]
    for name, sub, x, y, c in q:
        b.append(f'<text x="{x}" y="{y}" font-size="24" font-weight="700" fill="{c}">{name}</text>')
        b.append(f'<text x="{x}" y="{y+22}" font-size="15" fill="{t["soft"]}">{sub}</text>')
    # white-space candidates sorted by the why-not check
    pts = [(170, 150, "untried", "solid"), (235, 205, "tried too early", "ring"), (290, 120, "blocked: watch list", "amber")]
    for x, y, lab, kind in pts:
        if kind == "solid":
            b.append(f'<circle cx="{x}" cy="{y}" r="8" fill="{t["teal"]}"/>')
        elif kind == "ring":
            b.append(f'<circle cx="{x}" cy="{y}" r="7.5" fill="{t["paper"]}" stroke="{t["teal"]}" stroke-width="2.6"/>')
        else:
            b.append(f'<rect x="{x-7}" y="{y-7}" width="14" height="14" fill="{t["paper"]}" stroke="{t["amber"]}" stroke-width="2.4" transform="rotate(45 {x} {y})"/>')
        b.append(f'<text x="{x+15}" y="{y+5}" font-size="15" fill="{t["ink"]}">{lab}</text>')
    for x, y in [(560, 130), (640, 175), (720, 115), (790, 200), (610, 225)]:
        b.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{t["soft"]}" opacity="0.7"/>')
    for x, y in [(640, 360), (760, 400), (700, 330)]:
        b.append(f'<circle cx="{x}" cy="{y}" r="6" fill="none" stroke="{t["amber"]}" stroke-width="2"/>')
    for x, y in [(190, 370), (300, 410), (380, 345)]:
        b.append(f'<circle cx="{x}" cy="{y}" r="5" fill="{t["soft"]}" opacity="0.35"/>')
    b.append(f'<text x="{(X0+X1)/2}" y="{Y1+40}" font-size="17" fill="{t["ink"]}" text-anchor="middle">How many companies are building on it  (funding, patents, launches)</text>')
    b.append(f'<text x="58" y="{(Y0+Y1)/2}" font-size="17" fill="{t["ink"]}" text-anchor="middle" transform="rotate(-90 58 {(Y0+Y1)/2})">How much the constraint fell</text>')
    b.append(f'<text x="{X0}" y="{Y1+40}" font-size="13" fill="{t["soft"]}">fewer</text>')
    b.append(f'<text x="{X1}" y="{Y1+40}" font-size="13" fill="{t["soft"]}" text-anchor="end">more</text>')
    return svg(W, H, "\n".join(b), "PARADIGMA gap matrix: how much each constraint fell against how many companies build on it")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, fn in [("banner", banner), ("pipeline", pipeline), ("gap-matrix", gap)]:
        for th, t in THEMES.items():
            p = os.path.join(OUT, f"{name}-{th}.svg")
            open(p, "w").write(fn(t))
            print("wrote", os.path.relpath(p))
