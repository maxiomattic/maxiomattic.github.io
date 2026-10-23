"""Generate the site's SVG art: a starfield, an orrery, three diagrams, and the favicon.

Run from the site root: python3 tools/art.py
Every random draw comes from random.Random(7), so the output is repeatable.
"""
import math
import os
import random

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

VOID = "#060A1C"
DEEP = "#0C1433"
LAPIS = "#22336B"
BRASS = "#D9B26A"
BRASS_DIM = "#8E7444"
STAR = "#E9ECF5"
HAZE = "#96A0C3"
ION = "#8FDCEB"

FONT = '"Martian Mono", ui-monospace, monospace'
NS = 'xmlns="http://www.w3.org/2000/svg"'
MOTION = "@media (prefers-reduced-motion: no-preference)"


def n(v):
    """Round to one decimal place, dropping a trailing .0."""
    r = round(v, 1)
    return str(int(r)) if r == int(r) else f"{r:.1f}"


def pt(x, y):
    return f"{n(x)} {n(y)}"


def bearing(r, deg):
    """Point at radius r, measured clockwise from 12 o'clock (y grows downward)."""
    a = math.radians(deg)
    return r * math.sin(a), -r * math.cos(a)


def css(root, rules, motion=()):
    """Style block whose selectors all sit under the root class, so inline SVG styles stay local."""
    lines = [f".{root}{sel}{{{decl}}}" for sel, decl in rules]
    if motion:
        lines.append(MOTION + "{")
        lines.extend(motion)
        lines.append("}")
    return "<style>\n" + "\n".join(lines) + "\n</style>"


def svg_doc(open_tag, parts):
    return "\n".join([open_tag] + parts + ["</svg>", ""])


def walk(rng, x, y, count):
    """A zigzag chain of stars for a constellation sketch."""
    pts = [(x, y)]
    base = rng.uniform(-0.3, 0.3)
    for k in range(count - 1):
        a = base + (0.7 if k % 2 == 0 else -0.7) + rng.uniform(-0.2, 0.2)
        step = rng.uniform(38, 56)
        x, y = x + step * math.cos(a), y + step * math.sin(a)
        pts.append((x, y))
    return pts


# ---------------------------------------------------------------- starfield

STARFIELD_CSS = [
    (" circle", f"fill:{STAR}"),
    (" .cl", f"fill:none;stroke:{HAZE};stroke-width:.6;vector-effect:non-scaling-stroke;opacity:.35"),
]
STARFIELD_MOTION = [
    "@keyframes starfield-tw{0%,100%{opacity:.25}50%{opacity:1}}",
    ".starfield .tw{animation:starfield-tw var(--d) ease-in-out var(--b) infinite}",
]


def starfield(rng):
    W, H = 1600, 1000
    levels = (0.3, 0.5, 0.7, 0.9)
    layers = [[] for _ in levels]
    for k in range(150):
        if k < 110:  # most stars hug a soft diagonal band, the faint milky way
            while True:
                x = rng.uniform(0, W)
                y = 900 - 0.45 * x + rng.gauss(0, 95)
                if 0 <= y <= H:
                    break
        else:
            x, y = rng.uniform(0, W), rng.uniform(0, H)
        r = 0.5 + 1.5 * rng.random() ** 1.5
        layers[rng.randrange(len(levels))].append(
            f'<circle cx="{n(round(x))}" cy="{n(round(y))}" r="{n(round(r, 1))}"/>')
    body = [f'<g opacity="{n(op)}">' + "".join(items) + "</g>" for op, items in zip(levels, layers)]

    twinkle = []
    for _ in range(12):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        r = rng.uniform(1.2, 1.6)
        dur = rng.uniform(4, 9)
        delay = rng.uniform(0, 9)
        twinkle.append(
            f'<circle class="tw" cx="{n(round(x))}" cy="{n(round(y))}" r="{n(round(r, 1))}" opacity="0.9" '
            f'style="--d:{n(round(dur, 1))}s;--b:-{n(round(delay, 1))}s"/>')
    body.append("<g>" + "".join(twinkle) + "</g>")

    lines, dots = [], []
    for sx, sy, count in ((240, 230, 5), (1150, 600, 6)):
        pts = walk(rng, sx, sy, count)
        lines.append('<path class="cl" d="M' + "L".join(pt(x, y) for x, y in pts) + '"/>')
        dots += [f'<circle cx="{n(round(x))}" cy="{n(round(y))}" r="1.1" opacity="0.9"/>' for x, y in pts]
    body.append("<g>" + "".join(dots) + "</g>")

    head = (f'<svg class="starfield" {NS} viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice" '
            'aria-hidden="true" focusable="false">')
    return svg_doc(head, [css("starfield", STARFIELD_CSS, STARFIELD_MOTION)] + lines + body)


# ------------------------------------------------------------------ orrery

ORRERY_CSS = [
    (" .g0", f"stop-color:{BRASS};stop-opacity:.35"),
    (" .g1", f"stop-color:{BRASS};stop-opacity:0"),
    (" .grat *", f"fill:none;stroke:{LAPIS};stroke-width:.6;vector-effect:non-scaling-stroke"),
    (" .grat circle", "stroke-dasharray:2 6"),
    (" .disc", f"fill:{BRASS}"),
    (" .ring", f"fill:none;stroke:{BRASS};stroke-width:1.2"),
    (" .rays", f"fill:none;stroke:{BRASS};stroke-width:1.4;stroke-linecap:round"),
    (" .orbit", f"fill:none;stroke:{BRASS_DIM};stroke-width:1;vector-effect:non-scaling-stroke"),
    (" .dashed", "stroke-dasharray:1 5"),
    (" .comet", f"fill:none;stroke:{ION};stroke-width:1.2;stroke-linecap:round;opacity:.7"),
    (" .body", f"fill:{STAR}"),
    (" .ion", f"fill:none;stroke:{ION};stroke-width:1;vector-effect:non-scaling-stroke"),
    (" .bez", f"fill:none;stroke:{BRASS};stroke-width:1;vector-effect:non-scaling-stroke"),
    (" .mk", f"fill:none;stroke:{BRASS_DIM};stroke-width:1;vector-effect:non-scaling-stroke"),
    (" .mj", f"fill:none;stroke:{BRASS};stroke-width:1;vector-effect:non-scaling-stroke"),
    (" text", f"font-family:{FONT}"),
    (" .lbl", f"fill:{HAZE};font-size:11px;stroke:{VOID};stroke-width:3;paint-order:stroke"),
    (" .tk", f"fill:{HAZE};font-size:9px;stroke:{VOID};stroke-width:3;paint-order:stroke"),
]
ORRERY_MOTION = [
    "@keyframes orrery-pulse{0%,100%{opacity:.8}50%{opacity:1}}",
    ".orrery .glow{animation:orrery-pulse 6s ease-in-out infinite}",
]


def orrery():
    parts = [
        '<defs><radialGradient id="orr-glow" cx="0" cy="0" r="170" gradientUnits="userSpaceOnUse">'
        '<stop class="g0" offset="0"/><stop class="g1" offset="1"/></radialGradient></defs>',
        '<circle class="glow" r="170" fill="url(#orr-glow)"/>',
    ]

    # Polar graticule: dashed rings, twelve bearing lines, and bearing labels on the outer ring.
    grat = [f'<circle r="{r}"/>' for r in (120, 200, 280, 360)]
    segs = []
    for k in range(12):
        x1, y1 = bearing(100, 30 * k)
        x2, y2 = bearing(390, 30 * k)
        segs.append(f"M{pt(x1, y1)}L{pt(x2, y2)}")
    grat.append(f'<path d="{"".join(segs)}"/>')
    parts.append('<g class="grat">' + "".join(grat) + "</g>")
    for deg, text in ((0, "000"), (90, "090"), (180, "180"), (270, "270")):
        x, y = bearing(360, deg)
        parts.append(f'<text class="tk" x="{n(x)}" y="{n(y + 3)}" text-anchor="middle">{text}</text>')

    # The sun: disc, two rings, and 32 alternating rays.
    rays = []
    for i in range(32):
        deg = 360 * i / 32
        x1, y1 = bearing(68, deg)
        x2, y2 = bearing(96 if i % 2 == 0 else 82, deg)
        rays.append(f"M{pt(x1, y1)}L{pt(x2, y2)}")
    parts.append('<g class="sun"><circle class="disc" r="38"/><circle class="ring" r="50"/>'
                 '<circle class="ring" r="60"/>'
                 f'<path class="rays" d="{"".join(rays)}"/></g>')

    # Four orbits, each with a body moving along it (SMIL) and a label that stays upright.
    orbits = [
        (140, "70s", "-17s", 4, "lab"),
        (205, "110s", "-63s", 4, "careride"),
        (270, "160s", "-40s", 5, "fastdrive"),
        (340, "240s", "-150s", 5, "local-search"),
    ]
    for i, (rx, dur, begin, body_r, label) in enumerate(orbits):
        ry = rx * 0.42
        pid = f"orr-o{i + 1}"
        arc = f"A{n(rx)} {n(ry)} 0 1 0 "
        d = f"M{n(-rx)} 0{arc}{n(rx)} 0{arc}{n(-rx)} 0"
        ocls = "orbit dashed" if i == 3 else "orbit"
        group = [f'<path id="{pid}" class="{ocls}" d="{d}"/>']
        if i == 2:  # a faint probe trace on the third orbit
            t0, t1 = math.radians(196), math.radians(262)
            p0 = (270 * math.cos(t0), 113.4 * math.sin(t0))
            p1 = (270 * math.cos(t1), 113.4 * math.sin(t1))
            group.append(f'<path class="comet" stroke-dasharray="24 8" '
                         f'd="M{pt(*p0)}A270 113.4 0 0 1 {pt(*p1)}"/>')
        inner = [
            f'<animateMotion dur="{dur}" begin="{begin}" repeatCount="indefinite" rotate="0">'
            f'<mpath href="#{pid}"/></animateMotion>',
            f'<circle class="body" r="{body_r}"/>',
        ]
        if i == 1:
            inner.append('<circle class="ion" r="9"/>')
        inner.append(f'<text class="lbl" transform="rotate(16)" x="12" y="4">{label}</text>')
        group.append("<g>" + "".join(inner) + "</g>")
        parts.append('<g transform="rotate(-16)">' + "".join(group) + "</g>")

    # Instrument bezel: a thin ring with 72 ticks, every 30 degrees longer.
    minor, major = [], []
    for k in range(72):
        deg = 5 * k
        length = 12 if k % 6 == 0 else 6
        x1, y1 = bearing(392, deg)
        x2, y2 = bearing(392 - length, deg)
        (major if k % 6 == 0 else minor).append(f"M{pt(x1, y1)}L{pt(x2, y2)}")
    parts.append('<circle class="bez" r="392"/>')
    parts.append(f'<path class="mk" d="{"".join(minor)}"/>')
    parts.append(f'<path class="mj" d="{"".join(major)}"/>')

    head = f'<svg class="orrery" {NS} viewBox="-400 -400 800 800" aria-hidden="true" focusable="false">'
    return svg_doc(head, [css("orrery", ORRERY_CSS, ORRERY_MOTION)] + parts)


# ---------------------------------------------------------------- diagrams

def diagram(title, css_text, parts):
    head = f'<svg class="diagram" {NS} viewBox="0 0 640 300" role="img">'
    return svg_doc(head, [f"<title>{title}</title>", css_text] + parts)


FASTDRIVE_CSS = [
    (" text", f"font-family:{FONT};font-size:12px"),
    (" .fd-tag", f"fill:{HAZE}"),
    (" .fd-chunk", f"fill:{DEEP};stroke:{LAPIS};stroke-width:1"),
    (" .fd-diff", f"fill:{DEEP};stroke:{ION};stroke-width:1.4"),
    (" .fd-block", f"fill:{DEEP};stroke:{BRASS_DIM};stroke-width:1"),
    (" .fd-hex", f"fill:{STAR}"),
    (" .fd-link", f"fill:none;stroke:{BRASS_DIM};stroke-width:1"),
]


def fastdrive(rng):
    widths = [78, 102, 64, 96, 88, 88]          # six variable-width chunks, 516 units in all
    xs, x = [], 80
    for w in widths:
        xs.append((x, w))
        x += w
    bx = [80 + 75 * i for i in range(7)]          # seven store blocks, 66 wide
    v1_map = [0, 1, 2, 3, 5, 6]                   # v1 chunk 3 is stored in block 3
    v2_map = [0, 1, 2, 4, 5, 6]                   # v2 chunk 3 changed, so it is block 4
    hexes = [f"{rng.randrange(0x1000, 0x10000):x}" for _ in range(7)]

    parts = [
        '<text class="fd-tag" x="16" y="64">v1</text>',
        '<text class="fd-tag" x="16" y="244">v2</text>',
        '<text class="fd-tag" x="16" y="164">store</text>',
        '<text class="fd-tag" x="16" y="182">blake3</text>',
        '<path class="fd-link" d="' + "".join(
            [f"M{n(cx + w / 2)} 80C{n(cx + w / 2)} 110 {n(bx[v1_map[i]] + 33)} 110 "
             f"{n(bx[v1_map[i]] + 33)} 140" for i, (cx, w) in enumerate(xs)]
            + [f"M{n(cx + w / 2)} 220C{n(cx + w / 2)} 200 {n(bx[v2_map[i]] + 33)} 200 "
               f"{n(bx[v2_map[i]] + 33)} 180" for i, (cx, w) in enumerate(xs)]) + '"/>',
    ]
    for cx, w in xs:
        parts.append(f'<rect class="fd-chunk" x="{cx}" y="40" width="{w}" height="40"/>')
    for i, (cx, w) in enumerate(xs):
        cls = "fd-diff" if i == 3 else "fd-chunk"
        parts.append(f'<rect class="{cls}" x="{cx}" y="220" width="{w}" height="40"/>')
    for k, (x0, h) in enumerate(zip(bx, hexes)):
        cls = "fd-diff" if k == 4 else "fd-block"
        parts.append(f'<rect class="{cls}" x="{x0}" y="140" width="66" height="40"/>')
        parts.append(f'<text class="fd-hex" x="{x0 + 33}" y="164" text-anchor="middle">{h}</text>')
    return diagram("Two versions of a file split into content-defined chunks. "
                   "Chunks they share are stored once.",
                   css("diagram", FASTDRIVE_CSS), parts)


SEARCH_CSS = [
    (" text", f"font-family:{FONT};font-size:12px"),
    (" .ds-node", f"fill:{DEEP};stroke:{LAPIS};stroke-width:1.2"),
    (" .ds-q", f"fill:{DEEP};stroke:{BRASS};stroke-width:1.2"),
    (" .ds-rim", f"fill:none;stroke:{BRASS};stroke-width:1.2"),
    (" .ds-link", f"fill:none;stroke:{BRASS_DIM};stroke-width:1.2"),
    (" .ds-head", f"fill:{BRASS_DIM}"),
    (" .ds-bound", f"fill:none;stroke:{ION};stroke-width:1;stroke-dasharray:4 4"),
    (" .ds-ion", f"fill:{ION}"),
    (" .ds-t", f"fill:{STAR}"),
    (" .ds-muted", f"fill:{HAZE}"),
    (" .ds-cloud", f"fill:none;stroke:{HAZE};stroke-width:1.2;opacity:.5"),
]


def search():
    def box(cx, cy, w, label, cls="ds-node"):
        return [
            f'<rect class="{cls}" x="{n(cx - w / 2)}" y="{n(cy - 20)}" width="{n(w)}" height="40" rx="6"/>',
            f'<text class="ds-t" x="{n(cx)}" y="{n(cy + 4)}" text-anchor="middle">{label}</text>',
        ]

    parts = [
        '<defs><marker id="ds-arr" markerUnits="userSpaceOnUse" markerWidth="8" markerHeight="8" '
        'refX="8" refY="4" orient="auto"><path class="ds-head" d="M0 0L8 4L0 8Z"/></marker></defs>',
        '<rect class="ds-bound" x="14" y="36" width="480" height="236" rx="8"/>',
        '<text class="ds-ion" x="30" y="58">this computer, cpu only</text>',
    ]
    parts += box(80, 130, 90, "photos") + box(80, 210, 90, "documents")
    parts += box(198, 130, 90, "clip") + box(198, 210, 90, "ollama")
    parts += [
        '<path class="ds-q" d="M280 140A42 8 0 0 1 364 140V200A42 8 0 0 1 280 200Z"/>',
        '<path class="ds-rim" d="M280 140A42 8 0 0 0 364 140"/>',
        '<text class="ds-t" x="322" y="174" text-anchor="middle">qdrant</text>',
    ]
    parts += box(440, 170, 80, "query")
    for d in ("M125 130H153", "M125 210H153", "M243 130C262 130 262 160 280 160",
              "M243 210C262 210 262 180 280 180", "M364 170H400"):
        parts.append(f'<path class="ds-link" d="{d}" marker-end="url(#ds-arr)"/>')
    parts += [
        '<g class="ds-cloud"><path d="M536 170A12 12 0 0 1 534 149A18 18 0 0 1 564 138'
        'A18 18 0 0 1 594 150A11 11 0 0 1 592 170Z"/><path d="M520 124L610 184"/></g>',
        '<text class="ds-muted" x="566" y="200" text-anchor="middle"><tspan x="566">nothing</tspan><tspan x="566" dy="16">uploaded</tspan></text>',
    ]
    return diagram("Photos go through CLIP and documents through an embedding model; "
                   "both are indexed in Qdrant on the same computer.",
                   css("diagram", SEARCH_CSS), parts)


CHESS_CSS = [
    (" text", f"font-family:{FONT};font-size:12px"),
    (" .ch-board", f"fill:{DEEP}"),
    (" .ch-dark", f"fill:{LAPIS}"),
    (" .ch-frame", f"fill:none;stroke:{BRASS_DIM};stroke-width:1"),
    (" .ch-c", f"fill:{BRASS}"),
    (" .ch-s", f"fill:{BRASS_DIM}"),
    (" .ch-edge", f"fill:none;stroke:{LAPIS};stroke-width:1"),
    (" .ch-node", f"fill:{DEEP};stroke:{STAR};stroke-width:1"),
    (" .ch-out", f"fill:{BRASS};stroke:{BRASS};stroke-width:1"),
    (" .ch-eval", f"fill:{BRASS}"),
    (" .ch-link", f"fill:none;stroke:{BRASS_DIM};stroke-width:1.2"),
    (" .ch-head", f"fill:{BRASS_DIM}"),
]


def chess():
    bx, by, s = 20, 30, 30
    dark = [f"M{bx + c * s} {by + r * s}h{s}v{s}h-{s}z" for r in range(8) for c in range(8) if (r + c) % 2]
    parts = [
        '<defs><marker id="ch-arr" markerUnits="userSpaceOnUse" markerWidth="8" markerHeight="8" '
        'refX="8" refY="4" orient="auto"><path class="ch-head" d="M0 0L8 4L0 8Z"/></marker></defs>',
        '<rect class="ch-frame" x="14" y="24" width="252" height="252"/>',
        '<rect class="ch-board" x="20" y="30" width="240" height="240"/>',
        f'<path class="ch-dark" d="{"".join(dark)}"/>',
    ]
    pieces = [(0, 1, "s"), (1, 6, "c"), (3, 3, "s"), (4, 0, "c"), (5, 5, "c"), (6, 2, "s")]
    for r, c, kind in pieces:
        cx, cy = bx + c * s + s / 2, by + r * s + s / 2
        if kind == "c":
            parts.append(f'<circle class="ch-c" cx="{n(cx)}" cy="{n(cy)}" r="8"/>')
        else:
            parts.append(f'<rect class="ch-s" x="{n(cx - 7)}" y="{n(cy - 7)}" width="14" height="14"/>')

    # Network: 4 inputs, 6 hidden, one brass output.
    in_x, hid_x, out_x, out_y = 340, 456, 572, 150
    ins = [75, 125, 175, 225]
    hids = [60, 96, 132, 168, 204, 240]
    edges = [f"M{in_x} {y1}L{hid_x} {y2}" for y1 in ins for y2 in hids]
    edges += [f"M{hid_x} {y2}L{out_x} {out_y}" for y2 in hids]
    parts.append('<path class="ch-link" d="M270 150H326" marker-end="url(#ch-arr)"/>')
    parts.append(f'<path class="ch-edge" d="{"".join(edges)}"/>')
    parts += [f'<circle class="ch-node" cx="{in_x}" cy="{y}" r="6"/>' for y in ins]
    parts += [f'<circle class="ch-node" cx="{hid_x}" cy="{y}" r="6"/>' for y in hids]
    parts.append(f'<circle class="ch-out" cx="{out_x}" cy="{out_y}" r="8"/>')
    parts.append(f'<text class="ch-eval" x="{out_x}" y="186" text-anchor="middle">eval</text>')
    return diagram("A chessboard feeding a small neural network that scores the position.",
                   css("diagram", CHESS_CSS), parts)


CONDUCTOR_CSS = [
    (" text", f"font-family:{FONT};font-size:12px"),
    (" .cd-wave", f"fill:none;stroke:{ION};stroke-width:1.2;stroke-linejoin:round"),
    (" .cd-lbl", f"fill:{HAZE}"),
    (" .cd-hilbl", f"fill:{BRASS}"),
    (" .cd-t", f"fill:{STAR}"),
    (" .cd-node", f"fill:{DEEP};stroke:{BRASS};stroke-width:1.2"),
    (" .cd-link", f"fill:none;stroke:{BRASS_DIM};stroke-width:1.2"),
    (" .cd-head", f"fill:{BRASS_DIM}"),
    (" .cd-sec", f"fill:{DEEP};stroke:{LAPIS};stroke-width:1.2"),
    (" .cd-hi", f"fill:{BRASS};stroke:{BRASS};stroke-width:1.2"),
    (" .cd-star", f"fill:{STAR}"),
    (" .cd-baton", f"fill:none;stroke:{STAR};stroke-width:1;stroke-dasharray:3 3"),
]
CONDUCTOR_MOTION = [
    "@keyframes cd-cue{to{stroke-dashoffset:-6}}",
    ".diagram .cd-baton{animation:cd-cue 1.6s linear infinite}",
]


def conductor(rng):
    fx, fy, r1, r2 = 496, 232, 46, 96

    def at(r, deg):
        a = math.radians(deg)
        return fx + r * math.cos(a), fy + r * math.sin(a)

    wave = []
    for k in range(72):
        t = k / 71
        env = math.sin(math.pi * t) ** 0.7
        v = 0.55 * math.sin(k * 1.7) + 0.45 * rng.uniform(-1, 1)
        wave.append(pt(22 + 128 * t, 102 - 26 * env * v))
    parts = [
        '<defs><marker id="cd-arr" markerUnits="userSpaceOnUse" markerWidth="8" markerHeight="8" '
        'refX="8" refY="4" orient="auto"><path class="cd-head" d="M0 0L8 4L0 8Z"/></marker></defs>',
        f'<polyline class="cd-wave" points="{" ".join(wave)}"/>',
        '<text class="cd-lbl" x="86" y="150" text-anchor="middle">audio</text>',
        '<path class="cd-link" d="M154 102H220" marker-end="url(#cd-arr)"/>',
        '<rect class="cd-node" x="226" y="82" width="80" height="40" rx="6"/>',
        '<text class="cd-t" x="266" y="106" text-anchor="middle">gan</text>',
    ]
    ex, ey = at(100, 235)
    parts.append(f'<path class="cd-link" d="M306 102L{pt(ex, ey)}" marker-end="url(#cd-arr)"/>')

    # The fan: four sections across the upper half, with winds highlighted.
    for name, a0 in (("strings", 180), ("winds", 225), ("brass", 270), ("perc", 315)):
        a1 = a0 + 45
        p = [at(r2, a0 + 1), at(r2, a1 - 1), at(r1, a1 - 1), at(r1, a0 + 1)]
        d = f"M{pt(*p[0])}A{r2} {r2} 0 0 1 {pt(*p[1])}L{pt(*p[2])}A{r1} {r1} 0 0 0 {pt(*p[3])}Z"
        parts.append(f'<path class="{"cd-hi" if name == "winds" else "cd-sec"}" d="{d}"/>')
    for name, a0 in (("strings", 180), ("winds", 225), ("brass", 270), ("perc", 315)):
        mid = a0 + 22.5
        lx, ly = at(116, mid)
        c = math.cos(math.radians(mid))
        anchor = "end" if c < -0.5 else ("start" if c > 0.5 else "middle")
        cls = "cd-hilbl" if name == "winds" else "cd-lbl"
        parts.append(f'<text class="{cls}" x="{n(lx)}" y="{n(ly + 4)}" text-anchor="{anchor}">{name}</text>')

    # The conductor: a star at the fan's centre, and a dashed baton curve toward winds.
    bx, by = at(70, 247.5)
    parts.append(f'<path class="cd-baton" d="M{fx} {fy}Q{n(fx - 8)} {n(fy - 42)} {pt(bx, by)}"/>')
    parts.append(f'<circle class="cd-star" cx="{fx}" cy="{fy}" r="3.5"/>')
    return diagram("Audio comes in, the model detects which section is playing, "
                   "and the animated conductor cues it.",
                   css("diagram", CONDUCTOR_CSS, CONDUCTOR_MOTION), parts)


# ----------------------------------------------------------------- favicon

def favicon():
    # The orbit is tilted -20 degrees; place the star dot on it using the same rotation.
    t, a = math.radians(-60), math.radians(-20)
    lx, ly = 27 * math.cos(t), 15 * math.sin(t)
    dx = lx * math.cos(a) - ly * math.sin(a)
    dy = lx * math.sin(a) + ly * math.cos(a)
    rules = [
        (" .bg", f"fill:{VOID}"),
        (" .orb", f"fill:none;stroke:{BRASS_DIM};stroke-width:3.5"),
        (" .disc", f"fill:{BRASS}"),
        (" .ring", f"fill:none;stroke:{BRASS};stroke-width:3.5"),
        (" .dot", f"fill:{STAR}"),
    ]
    parts = [
        css("favicon", rules),
        '<rect class="bg" width="64" height="64" rx="12"/>',
        '<ellipse class="orb" cx="32" cy="32" rx="27" ry="15" transform="rotate(-20 32 32)"/>',
        '<circle class="ring" cx="32" cy="32" r="11"/>',
        '<circle class="disc" cx="32" cy="32" r="7"/>',
        f'<circle class="dot" cx="{n(32 + dx)}" cy="{n(32 + dy)}" r="2.8"/>',
    ]
    return svg_doc(f'<svg class="favicon" {NS} viewBox="0 0 64 64">', parts)


def main():
    rng = random.Random(7)
    outputs = {
        "_includes/starfield.svg": starfield(rng),
        "_includes/orrery.svg": orrery(),
        "_includes/diagram-fastdrive.svg": fastdrive(rng),
        "_includes/diagram-search.svg": search(),
        "_includes/diagram-chess.svg": chess(),
        "_includes/diagram-conductor.svg": conductor(rng),
        "assets/favicon.svg": favicon(),
    }
    for rel, text in outputs.items():
        with open(os.path.join(SITE, rel), "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"{rel}: {len(text.encode('utf-8'))} bytes")


if __name__ == "__main__":
    main()
