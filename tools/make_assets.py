#!/usr/bin/env python3
"""Generate the README artwork for PARADIGMA.

Design system: adapted from the Cal.com DESIGN.md (VoltAgent/awesome-design-md),
with its neutral grays swapped for a light pink and white palette.
- White canvas, near-black ink for text, one sans-serif family.
- Display type at weight 600 with negative tracking.
- Soft-rounded cards (12-16px), 1px hairlines, no heavy shadows.
- Show the product (a constraint card from a report), not an illustration of it.

GitHub renders README images as <img>, so only system fonts are available.

    python3 tools/make_assets.py   -> writes assets/*.svg
"""
import os
import random

OUT = os.path.join(os.path.dirname(__file__), "..", "assets")
SANS = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"

C = dict(
    canvas="#FFFFFF",
    blush="#FFF6F8",      # surface-soft
    petal="#FDE8EE",      # surface-card
    rose="#F7CFDB",       # hairline / strong surface
    pink="#EE9AB3",       # soft accent
    deep="#C9406B",       # data accent (curves, highlights)
    ink="#111111",
    body="#3D3D44",
    muted="#7A7A85",
)


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-label="{title}" font-family="{SANS}">\n<title>{title}</title>\n{body}\n</svg>\n')


def t(x, y, s, size, fill, weight=400, anchor="start", extra=""):
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}" {extra}>{s}</text>')


def pill(x, y, label, fill, color, size=13, pad=12, h=26, weight=500):
    w = len(label) * size * 0.56 + pad * 2
    return (f'<rect x="{x}" y="{y}" width="{w:.0f}" height="{h}" rx="{h/2}" fill="{fill}"/>'
            + t(x + w / 2, y + h / 2 + size * 0.36, label, size, color, weight, "middle")), w


# ------------------------------------------------------------------ banner
def banner():
    W, H = 1280, 440
    b = [f'<rect width="{W}" height="{H}" rx="20" fill="{C["blush"]}"/>']

    # left: wordmark + statement
    b.append(t(72, 176, "PARADIGMA", 76, C["ink"], 600, extra='letter-spacing="-2" textLength="452" lengthAdjust="spacingAndGlyphs"'))
    b.append(t(74, 230, "Map how a field's constraints changed", 24, C["body"]))
    b.append(t(74, 262, "over the years you choose, and find", 24, C["body"]))
    b.append(t(74, 294, "what just became possible.", 24, C["body"]))
    x = 74
    for lab in ["Agent skill", "Claude Code", "OpenCode", "Codex"]:
        p, w = pill(x, 336, lab, C["canvas"], C["ink"], 14, 14, 32)
        b.append(f'<rect x="{x-0.5}" y="335.5" width="{w+1:.0f}" height="33" rx="16.5" fill="none" stroke="{C["rose"]}"/>')
        b.append(p)
        x += w + 10

    # right: a constraint card, as it appears in a report
    X, Y, CW, CH = 668, 56, 548, 328
    b.append(f'<rect x="{X}" y="{Y+4}" width="{CW}" height="{CH}" rx="16" fill="{C["rose"]}" opacity="0.45"/>')
    b.append(f'<rect x="{X}" y="{Y}" width="{CW}" height="{CH}" rx="16" fill="{C["canvas"]}" stroke="{C["rose"]}"/>')
    b.append(t(X + 28, Y + 44, "Industrial vibration sensor", 20, C["ink"], 600))
    b.append(t(X + 28, Y + 68, "Cost per measurement channel, USD", 14, C["muted"]))

    # mini log chart
    gx0, gy0, gx1, gy1 = X + 28, Y + 92, X + CW - 28, Y + 236
    for i in range(4):
        y = gy0 + i * (gy1 - gy0) / 3
        b.append(f'<line x1="{gx0}" y1="{y:.1f}" x2="{gx1}" y2="{y:.1f}" stroke="{C["petal"]}" stroke-width="1"/>')
    random.seed(4)
    n = 14
    pts = []
    for i in range(n):
        x = gx0 + 10 + i * (gx1 - gx0 - 20) / (n - 1)
        y = gy0 + 14 + i * (gy1 - gy0 - 30) / (n - 1) + random.uniform(-7, 7)
        pts.append((x, y))
    area = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    b.append(f'<polygon points="{pts[0][0]:.1f},{gy1} {area} {pts[-1][0]:.1f},{gy1}" fill="{C["petal"]}" opacity="0.7"/>')
    b.append(f'<polyline points="{area}" fill="none" stroke="{C["deep"]}" stroke-width="2.5" stroke-linejoin="round"/>')
    for x, y in pts[::3] + [pts[-1]]:
        b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{C["canvas"]}" stroke="{C["deep"]}" stroke-width="2"/>')
    ty = gy0 + 0.62 * (gy1 - gy0)
    b.append(f'<line x1="{gx0}" y1="{ty:.1f}" x2="{gx1}" y2="{ty:.1f}" stroke="{C["pink"]}" stroke-width="1.5" stroke-dasharray="5 5"/>')
    b.append(t(gx1, ty - 8, "viable below this cost", 12, C["muted"], 400, "end"))
    b.append(t(gx0, gy1 + 20, "2005", 12, C["muted"]))
    b.append(t(gx1, gy1 + 20, "2025", 12, C["muted"], 400, "end"))

    # stats row
    sy = Y + 286
    stats = [("−21% / yr", "robust trend"), ("110×", "cheaper"), ("A", "data grade"), ("3", "companies building")]
    colw = (CW - 56) / 4
    for i, (big, small) in enumerate(stats):
        sx = X + 28 + i * colw
        b.append(t(sx, sy, big, 20, C["ink"], 600))
        b.append(t(sx, sy + 20, small, 12, C["muted"]))
    b.append(t(X + CW - 20, Y + CH + 30, "Illustrative example", 12, C["muted"], 400, "end"))
    return svg(W, H, "\n".join(b), "PARADIGMA: map how a field's constraints changed over the years you choose, and find what just became possible")


# ---------------------------------------------------------------- pipeline
STEPS = [
    ("Map the field", "12–25 constraints, parts to laws"),
    ("Price curves", "Yearly medians, inflation removed"),
    ("Non-cost sweep", "Laws, patents, skills, norms"),
    ("Activity scan", "Who builds on each change"),
    ("Gap matrix", "How far it fell vs. who builds"),
    ("Why-not check", "Untried, too early, or blocked"),
    ("Independent check", "A fresh agent re-opens sources"),
    ("Report", "Panorama, charts, sourced data"),
]


def pipeline():
    W, H = 1200, 330
    b = [f'<rect width="{W}" height="{H}" rx="20" fill="{C["blush"]}"/>']
    cw, ch, gx, gy, x0, y0 = 264, 122, 24, 22, 36, 31
    for i, (name, desc) in enumerate(STEPS):
        r, c = divmod(i, 4)
        x, y = x0 + c * (cw + gx), y0 + r * (ch + gy)
        hl = i in (4, 5)
        b.append(f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="12" fill="{C["petal"] if hl else C["canvas"]}" stroke="{C["rose"]}"/>')
        b.append(f'<circle cx="{x+36}" cy="{y+38}" r="15" fill="{C["deep"] if hl else C["petal"]}"/>')
        b.append(t(x + 36, y + 43.5, str(i + 1), 15, C["canvas"] if hl else C["deep"], 600, "middle"))
        b.append(t(x + 22, y + 84, name, 19, C["ink"], 600))
        b.append(t(x + 22, y + 106, desc, 14, C["muted"]))
    return svg(W, H, "\n".join(b), "PARADIGMA in eight steps, from mapping the field to the report")


# -------------------------------------------------------------- gap matrix
def gap():
    W, H = 900, 600
    b = [f'<rect width="{W}" height="{H}" rx="20" fill="{C["blush"]}"/>']
    X0, Y0, cw, ch, g = 96, 40, 382, 232, 14
    cells = [
        (0, 0, "Open gap", "Dropped a lot · few use it yet", C["petal"], C["deep"]),
        (1, 0, "Crowded", "Dropped a lot · many already use it", C["canvas"], C["ink"]),
        (0, 1, "Dormant", "Barely moved · little activity", C["canvas"], C["muted"]),
        (1, 1, "Hype risk", "Barely moved · many building anyway", C["canvas"], C["ink"]),
    ]
    for cx, cy, name, sub, fill, col in cells:
        x, y = X0 + cx * (cw + g), Y0 + cy * (ch + g)
        b.append(f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="14" fill="{fill}" stroke="{C["rose"]}"/>')
        b.append(t(x + 24, y + 42, name, 22, col, 600))
        b.append(t(x + 24, y + 66, sub, 14, C["muted"]))
    # open-gap items, sorted by the why-not check
    items = [(150, 150, "untried", "fill"), (150, 186, "tried too early", "ring"), (150, 222, "blocked: watch list", "dash")]
    for x, y, lab, k in items:
        if k == "fill":
            b.append(f'<circle cx="{x}" cy="{y}" r="7" fill="{C["deep"]}"/>')
        elif k == "ring":
            b.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{C["canvas"]}" stroke="{C["deep"]}" stroke-width="2.5"/>')
        else:
            b.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{C["canvas"]}" stroke="{C["pink"]}" stroke-width="2.5" stroke-dasharray="3 2.5"/>')
        b.append(t(x + 16, y + 5, lab, 15, C["body"]))
    # plain-words reading of the other three quadrants, instead of decorative dots
    notes = {
        (1, 0): ["What most of the field already knows.", "The report lists who is there", "and how far each one got."],
        (1, 1): ["A warning sign: lots of activity", "with no real change underneath.", "Treat growth claims with caution."],
        (0, 1): ["Nothing moved and nobody is", "building. Kept for reference."],
    }
    for (cx, cy), lines in notes.items():
        x, y = X0 + cx * (cw + g), Y0 + cy * (ch + g)
        for i, line in enumerate(lines):
            b.append(t(x + 24, y + 112 + i * 24, line, 15, C["body"]))
    b.append(t(X0 + cw + g / 2, H - 46, "How many are building on it  →", 15, C["body"], 500, "middle"))
    b.append(t(56, Y0 + ch + g / 2, "How far the constraint dropped  →", 15, C["body"], 500, "middle",
               f'transform="rotate(-90 56 {Y0 + ch + g / 2})"'))
    return svg(W, H, "\n".join(b), "Gap matrix: how far each constraint fell against how many companies build on it")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith(".svg"):
            os.remove(os.path.join(OUT, f))
    for name, fn in [("banner", banner), ("pipeline", pipeline), ("gap-matrix", gap)]:
        p = os.path.join(OUT, f"{name}.svg")
        open(p, "w").write(fn())
        print("wrote", os.path.relpath(p))
