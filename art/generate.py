"""
Elysium Balloons — generator for 10,000 pixel-art balloons floating in the sky, each with a face.

Usage:
    python3 art/generate.py                # writes public/nft/images/*.png + public/nft/metadata/*.json
    python3 art/generate.py --count 50     # quick preview run

Every token is built from traits (sky, clouds, extras, balloon shape, colour, pattern,
eyes, mouth, cheeks, headwear, eyewear). Each combination is unique (checked by DNA).
"""
import argparse, json, os, random, hashlib
import numpy as np
from PIL import Image

G = 48          # pixel grid
SCALE = 10      # 480 x 480 output
SEED = 20261106
COLLECTION = "Elysium Balloons"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_IMG = os.path.join(ROOT, "public", "nft", "images")
OUT_META = os.path.join(ROOT, "public", "nft", "metadata")

def hx(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i+2], 16) for i in (0, 2, 4)], dtype=np.int16)

def mix(a, b, t):
    return (a * (1 - t) + b * t).astype(np.int16)

def shade(c, f):
    return np.clip(c * f, 0, 255).astype(np.int16)

def wpick(rng, table):
    names = [n for n, _ in table]
    weights = [w for _, w in table]
    return rng.choices(names, weights=weights, k=1)[0]

# ---------------------------------------------------------------- traits
SKIES = {
    "Day Blue":     (["#7ec8f5", "#a9dcfa", "#d4effd"], 18),
    "Mint Sky":     (["#7fe0c8", "#aeeedd", "#dcf9f1"], 10),
    "Dawn Pink":    (["#f7a8c4", "#fbc9d6", "#fde6d8"], 10),
    "Sunset":       (["#ff7b54", "#ffb26b", "#ffd56b"], 10),
    "Golden Hour":  (["#f6b042", "#f9cf72", "#fbe7a8"], 8),
    "Lavender":     (["#a993e8", "#c6b6f2", "#e4dcfa"], 9),
    "Night":        (["#0d1b3e", "#1b2d5e", "#2b417c"], 10),
    "Storm":        (["#5d6878", "#7c8797", "#a1abb8"], 6),
    "Hyper Teal":   (["#0b3b3a", "#11615c", "#1a8c82"], 8),   # nod to Hyperliquid green-teal
    "Aurora":       (["#071c2c", "#0f4a4a", "#2f9b7a"], 5),
    "Elysian Gold": (["#5a3d0e", "#b8862b", "#f3d27a"], 4),
    "Deep Space":   (["#05030f", "#120a2c", "#24124d"], 2),
}
DARK_SKIES = {"Night", "Hyper Teal", "Aurora", "Deep Space", "Storm", "Elysian Gold"}

BALLOON_COLORS = {
    # name: (base, light, dark), weight
    "Cherry":    (("#e8394a", "#ff7a84", "#a01a2a"), 10),
    "Tangerine": (("#ff8a2a", "#ffb874", "#c4570c"), 9),
    "Lemon":     (("#ffd93b", "#fff08a", "#c9a10c"), 9),
    "Lime":      (("#7ed957", "#b5f08f", "#4a9a2c"), 8),
    "Ocean":     (("#2f80ed", "#76adf7", "#1a4fa6"), 9),
    "Sky":       (("#56ccf2", "#9ae4fa", "#2a8fb8"), 8),
    "Grape":     (("#9b51e0", "#c494f0", "#6527a0"), 8),
    "Bubblegum": (("#ff6fb5", "#ffa8d4", "#c43a80"), 9),
    "Mint":      (("#3ee6b8", "#97f5dc", "#1a9f7c"), 7),
    "Coral":     (("#ff6f61", "#ffa59c", "#c2443a"), 7),
    "Snow":      (("#eef2f7", "#ffffff", "#b4bfcc"), 5),
    "Onyx":      (("#2b2d3a", "#5a5d70", "#13141c"), 4),
    "Hyper":     (("#5ef2c9", "#b6fbe8", "#16a37e"), 4),
    "Gold":      (("#f2c230", "#fde88c", "#a87b0c"), 2),
    "Chrome":    (("#c9d3de", "#ffffff", "#7d8a99"), 1.5),
    "Rainbow":   ((None, None, None), 1.5),
}
SECOND = ["Cherry", "Tangerine", "Lemon", "Lime", "Ocean", "Sky", "Grape", "Bubblegum", "Mint", "Coral", "Snow", "Onyx"]

SHAPES = [("Party", 62), ("Hot Air", 26), ("Heart", 9), ("Twin Knot", 3)]
PATTERNS = [("Solid", 40), ("Stripes", 16), ("Polka", 14), ("Two Tone", 12), ("Zigzag", 8), ("Checker", 6), ("Sparkle", 4)]
CLOUDS = [("None", 18), ("Few", 45), ("Many", 27), ("Cloud Bed", 10)]
EXTRAS = [("None", 40), ("Birds", 14), ("Sun", 10), ("Moon", 8), ("Tiny Balloons", 12), ("Rainbow", 4), ("Plane", 5), ("Shooting Star", 7)]
EYES = [("Dots", 18), ("Shiny", 18), ("Happy", 12), ("Sleepy", 8), ("Wink", 8), ("Hearts", 6), ("Stars", 5),
        ("Angry", 6), ("X Eyes", 4), ("Googly", 7), ("Laser", 2), ("Teary", 6)]
MOUTHS = [("Smile", 22), ("Big Grin", 14), ("O", 10), ("Tongue", 10), ("Smirk", 9), ("Flat", 7), ("Frown", 6),
          ("Fangs", 5), ("Cat", 8), ("Bubblegum", 5), ("Teeth", 4)]
CHEEKS = [("None", 55), ("Blush", 40), ("Freckles", 5)]
HEADWEAR = [("None", 38), ("Party Hat", 10), ("Crown", 4), ("Beanie", 8), ("Cap", 8), ("Top Hat", 6), ("Halo", 4),
            ("Propeller", 6), ("Flower", 6), ("Bow", 6), ("Horns", 4), ("Antenna", 4), ("Cowboy", 4), ("Wizard", 3)]
EYEWEAR = [("None", 74), ("Shades", 10), ("3D Glasses", 5), ("Monocle", 4), ("Nerd Glasses", 5), ("VR", 2)]

# ---------------------------------------------------------------- canvas helpers
class Canvas:
    def __init__(self):
        self.a = np.zeros((G, G, 3), dtype=np.int16)

    def px(self, x, y, c):
        if 0 <= x < G and 0 <= y < G:
            self.a[y, x] = c

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.px(x, y, c)

    def img(self):
        im = Image.fromarray(np.clip(self.a, 0, 255).astype(np.uint8), "RGB")
        return im.resize((G * SCALE, G * SCALE), Image.NEAREST)

OUTLINE = hx("#1b1530")
WHITE = hx("#ffffff")
BLACK = hx("#14121f")

# ---------------------------------------------------------------- background
def draw_sky(cv, sky, rng):
    cols = [hx(c) for c in SKIES[sky][0]]
    for y in range(G):
        t = y / (G - 1)
        if t < 0.5:
            c = mix(cols[0], cols[1], t * 2)
        else:
            c = mix(cols[1], cols[2], (t - 0.5) * 2)
        # light ordered dithering between bands for a pixel look
        for x in range(G):
            d = ((x + y) % 2) * 3 - 1
            cv.a[y, x] = np.clip(c + d, 0, 255)
    if sky in ("Night", "Deep Space", "Aurora", "Hyper Teal"):
        n = {"Night": 26, "Deep Space": 55, "Aurora": 18, "Hyper Teal": 14}[sky]
        for _ in range(n):
            x, y = rng.randrange(G), rng.randrange(G)
            cv.px(x, y, hx("#ffffff") if rng.random() < 0.6 else hx("#fff3b0"))
    if sky == "Aurora":
        for x in range(G):
            y0 = int(10 + 4 * np.sin(x / 5.0))
            for k in range(5):
                cv.px(x, y0 + k, mix(cv.a[y0 + k if y0 + k < G else G - 1, x], hx("#5affb4"), 0.55 - k * 0.1))
    if sky == "Deep Space":
        # small planet
        cx, cy = rng.choice([(7, 7), (40, 8), (41, 40)])
        for y in range(cy - 3, cy + 4):
            for x in range(cx - 3, cx + 4):
                if (x - cx) ** 2 + (y - cy) ** 2 <= 10:
                    cv.px(x, y, hx("#e07a5f") if x + y < cx + cy else hx("#a34a3a"))
        for x in range(cx - 5, cx + 6):
            cv.px(x, cy + 1, hx("#f2cc8f"))

def cloud(cv, cx, cy, w, col, shadow):
    # rounded pixel cloud made of overlapping circles
    blobs = [(cx, cy, w // 3 + 1), (cx - w // 3, cy + 1, w // 4 + 1), (cx + w // 3, cy + 1, w // 4 + 1)]
    pts = set()
    for bx, by, r in blobs:
        for y in range(by - r, by + r + 1):
            for x in range(bx - r - 1, bx + r + 2):
                if ((x - bx) / (r + 1)) ** 2 + ((y - by) / r) ** 2 <= 1.0:
                    pts.add((x, y))
    maxy = max(p[1] for p in pts)
    for x, y in pts:
        cv.px(x, y, shadow if y >= maxy else col)

def draw_clouds(cv, kind, sky, rng, avoid_center=True):
    if kind == "None":
        return
    dark = sky in DARK_SKIES
    col = hx("#cfd8ea") if dark else hx("#ffffff")
    sh = hx("#8e9bb8") if dark else hx("#dbe6f3")
    if sky == "Storm":
        col, sh = hx("#c3cad4"), hx("#8a94a3")
    if kind == "Cloud Bed":
        for x in range(-4, G + 4, 7):
            cloud(cv, x + rng.randrange(-1, 2), 44 + rng.randrange(0, 2), 12, col, sh)
        n = rng.randrange(0, 2)
    else:
        n = {"Few": rng.randrange(2, 4), "Many": rng.randrange(4, 7)}[kind]
    slots = [(5, 6), (41, 5), (6, 40), (42, 38), (4, 24), (44, 22), (12, 46), (36, 45), (24, 2)]
    rng.shuffle(slots)
    for cx, cy in slots[:n]:
        cloud(cv, cx + rng.randrange(-2, 3), cy + rng.randrange(-2, 3), rng.randrange(7, 12), col, sh)

def tiny_balloon(cv, x, y, c):
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            if abs(dx) + abs(dy) < 2 or dy == 0:
                cv.px(x + dx, y + dy, c)
    cv.px(x, y - 2, c)
    cv.px(x - 1, y - 1, c); cv.px(x + 1, y - 1, c)
    cv.px(x, y + 2, shade(c, 0.6))
    cv.px(x, y + 3, hx("#d7d7d7")); cv.px(x + 1, y + 4, hx("#d7d7d7"))
    cv.px(x - 1, y - 1, shade(c, 1.35))

def draw_extras(cv, kind, sky, rng):
    if kind == "Sun":
        cx, cy = rng.choice([(6, 6), (41, 6)])
        for y in range(cy - 4, cy + 5):
            for x in range(cx - 4, cx + 5):
                d = (x - cx) ** 2 + (y - cy) ** 2
                if d <= 9:
                    cv.px(x, y, hx("#ffe14d"))
                elif d <= 16 and (x + y) % 2 == 0:
                    cv.px(x, y, hx("#fff3a6"))
    elif kind == "Moon":
        cx, cy = rng.choice([(6, 6), (41, 6)])
        for y in range(cy - 3, cy + 4):
            for x in range(cx - 3, cx + 4):
                if (x - cx) ** 2 + (y - cy) ** 2 <= 10 and (x - cx - 2) ** 2 + (y - cy + 1) ** 2 > 6:
                    cv.px(x, y, hx("#fff4c2"))
    elif kind == "Birds":
        for _ in range(rng.randrange(2, 4)):
            x, y = rng.choice([4, 8, 38, 42, 44]), rng.randrange(4, 30)
            c = hx("#2a2440") if sky not in DARK_SKIES else hx("#e9e6ff")
            cv.px(x, y, c); cv.px(x - 1, y - 1, c); cv.px(x + 1, y - 1, c); cv.px(x - 2, y - 1, c); cv.px(x + 2, y - 1, c)
    elif kind == "Tiny Balloons":
        for x, y in rng.sample([(5, 12), (42, 14), (6, 30), (43, 32), (40, 4)], rng.randrange(2, 4)):
            c = hx(BALLOON_COLORS[rng.choice(SECOND)][0][0])
            tiny_balloon(cv, x, y, c)
    elif kind == "Rainbow":
        cols = ["#ff5c5c", "#ffa64d", "#ffe14d", "#6be36b", "#4db8ff", "#9d6bff"]
        cx, cy = 24, 52
        for i, c in enumerate(cols):
            r = 30 - i
            for x in range(G):
                for y in range(G):
                    d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                    if r - 0.5 <= d < r + 0.5:
                        cv.px(x, y, mix(cv.a[y, x], hx(c), 0.75))
    elif kind == "Plane":
        x, y = rng.choice([(36, 6), (4, 8)])
        body = hx("#f4f4f8"); dark = hx("#9aa3b5")
        cv.rect(x, y, x + 6, y, body); cv.px(x + 7, y, dark)
        cv.px(x + 3, y - 1, body); cv.px(x + 2, y + 1, body); cv.px(x + 3, y + 1, body)
        cv.px(x, y - 1, body)
        for i in range(1, 4):
            if 0 <= x - i * 2:
                cv.px(x - i * 2, y, mix(cv.a[y, max(0, x - i * 2)], WHITE, 0.6))
    elif kind == "Shooting Star":
        x, y = rng.choice([(40, 4), (8, 6)])
        dirx = 1 if x > 24 else -1   # tail points away from the centre
        star = hx("#fff9c4")
        cv.px(x, y, WHITE)
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            cv.px(x + dx, y + dy, star)
        for i in range(1, 8):
            px_, py_ = x + dirx * i, y - (i + 1) // 2
            if 0 <= px_ < G and 0 <= py_ < G:
                cv.px(px_, py_, mix(cv.a[py_, px_], star, 1 - i / 9))

# ---------------------------------------------------------------- balloon body
CX, CY, RX, RY = 24, 23, 13, 14   # envelope centre / radii (top ≈ y9, bottom ≈ y37)

def envelope_mask(shape):
    m = np.zeros((G, G), dtype=bool)
    for y in range(G):
        for x in range(G):
            fx, fy = (x - CX + 0.5) / RX, (y - CY + 0.5) / RY
            if shape == "Heart":
                X = (x - CX + 0.5) / 15.5
                Y = -(y - CY - 1 + 0.5) / 15.5
                inside = (X * X + Y * Y - 0.42) ** 3 - X * X * Y ** 3 * 0.9 <= 0
                m[y, x] = inside and 8 <= y <= 39
            elif shape == "Hot Air":
                # wider on top, tapering into a neck
                if y <= CY:
                    m[y, x] = fx * fx + fy * fy <= 1.0
                else:
                    t = (y - CY) / 14.0
                    half = 13 * (1 - t ** 1.6 * 0.7)
                    m[y, x] = abs(x - CX + 0.5) <= half and y <= CY + 13
            else:
                m[y, x] = fx * fx + (fy * (1.0 + 0.10 * max(0, fy))) ** 2 <= 1.0
    return m

MASKS = {}

def get_mask(shape):
    if shape not in MASKS:
        MASKS[shape] = envelope_mask(shape)
    return MASKS[shape]

def rainbow_color(x, y):
    cols = ["#ff5c5c", "#ffa64d", "#ffe14d", "#6be36b", "#4db8ff", "#9d6bff"]
    return hx(cols[((y - 6) // 5) % len(cols)])

def body_color(x, y, pattern, base, second, rng_bits, shape):
    if pattern == "Stripes":
        band = ((x - CX + 40) // 4) % 2 if shape != "Hot Air" else ((x - CX + 40) // 3) % 2
        return second if band else base
    if pattern == "Polka":
        if ((x // 5) + (y // 5)) % 2 == 0 and (x % 5 in (1, 2)) and (y % 5 in (1, 2)):
            return second
        return base
    if pattern == "Two Tone":
        return base if y < CY else second
    if pattern == "Zigzag":
        zz = CY + (2 if (x // 3) % 2 == 0 else -1) + (x % 3 if (x // 3) % 2 == 0 else -(x % 3))
        return second if abs(y - zz) <= 1 else base
    if pattern == "Checker":
        return second if ((x // 4) + (y // 4)) % 2 else base
    if pattern == "Sparkle":
        return WHITE if (rng_bits.get((x, y))) else base
    return base

def draw_balloon(cv, shape, color, pattern, second_name, rng):
    m = get_mask(shape)
    if color == "Rainbow":
        base = light = dark = None
    else:
        b, l, d = BALLOON_COLORS[color][0]
        base, light, dark = hx(b), hx(l), hx(d)
    sec = hx(BALLOON_COLORS[second_name][0][0])
    sparkle = {}
    if pattern == "Sparkle":
        for _ in range(16):
            sparkle[(rng.randrange(CX - 10, CX + 10), rng.randrange(11, 34))] = True

    ys, xs = np.where(m)
    for y, x in zip(ys, xs):
        if color == "Rainbow":
            c = rainbow_color(x, y)
        else:
            c = body_color(x, y, pattern, base, sec, sparkle, shape)
        # shading: darken right / lower rim, lighten upper left
        dx, dy = (x - CX + 0.5) / RX, (y - CY + 0.5) / RY
        lightness = -0.55 * dx - 0.45 * dy
        if color in ("Chrome", "Gold"):
            lightness *= 1.6
        if lightness > 0.45:
            c = shade(c, 1.12)
        elif lightness < -0.62:
            c = shade(c, 0.72)
        elif lightness < -0.35:
            c = shade(c, 0.86)
        cv.a[y, x] = c

    # outline
    for y in range(G):
        for x in range(G):
            if not m[y, x]:
                nb = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
                if any(0 <= a < G and 0 <= b < G and m[b, a] for a, b in nb):
                    cv.px(x, y, OUTLINE)

    # glossy highlight (classic balloon shine)
    if shape != "Hot Air":
        for (x, y) in [(16, 13), (17, 13), (15, 14), (16, 14), (15, 15), (15, 16), (19, 12), (20, 12)]:
            if m[y, x]:
                cv.px(x, y, mix(cv.a[y, x], WHITE, 0.75))
    else:
        for (x, y) in [(15, 13), (16, 12), (14, 14), (14, 15)]:
            cv.px(x, y, mix(cv.a[y, x], WHITE, 0.6))

    bottom = int(max(ys))
    knot_c = shade(base if base is not None else hx("#ff5c5c"), 0.7)
    if shape in ("Party", "Heart", "Twin Knot"):
        # knot
        cv.px(CX - 1, bottom + 1, knot_c); cv.px(CX, bottom + 1, knot_c)
        cv.rect(CX - 2, bottom + 2, CX + 1, bottom + 2, knot_c)
        cv.px(CX - 3, bottom + 2, OUTLINE); cv.px(CX + 2, bottom + 2, OUTLINE)
        # wavy string
        string = hx("#f2f2f2") if True else None
        y = bottom + 3
        x = CX
        k = 0
        while y < G:
            cv.px(x, y, mix(string, OUTLINE, 0.15))
            k += 1
            if k % 3 == 0:
                x += 1 if (k // 3) % 2 else -1
            y += 1
        if shape == "Twin Knot":
            # a second little companion balloon tied on
            tiny_balloon(cv, CX + 9, 41, hx(BALLOON_COLORS[second_name][0][0]))
            for i in range(0, 6):
                cv.px(CX + 1 + i, 46 - i // 3, hx("#e8e8e8"))
    else:
        # hot air: ropes + basket
        rope = hx("#6b4b2a")
        for i in range(5):
            cv.px(CX - 6 + i // 2, 37 + i, rope)
            cv.px(CX + 5 - i // 2, 37 + i, rope)
        bx0, bx1, by0, by1 = CX - 5, CX + 4, 41, 46
        wood = hx("#b7793d"); wood_d = hx("#7d4a1e")
        cv.rect(bx0, by0, bx1, by1, wood)
        for x in range(bx0, bx1 + 1):
            if x % 2 == 0:
                for yy in range(by0 + 1, by1 + 1):
                    cv.px(x, yy, wood_d)
        cv.rect(bx0 - 1, by0, bx1 + 1, by0, hx("#5a3413"))
        cv.rect(bx0, by1 + 1, bx1, by1 + 1, OUTLINE)
        cv.px(bx0 - 1, by0 + 1, OUTLINE); cv.px(bx1 + 1, by0 + 1, OUTLINE)
        for yy in range(by0 + 1, by1 + 1):
            cv.px(bx0 - 1, yy, OUTLINE); cv.px(bx1 + 1, yy, OUTLINE)
        # burner flame
        cv.px(CX - 1, 39, hx("#ffb703")); cv.px(CX, 39, hx("#ffb703")); cv.px(CX, 38, hx("#fb8500"))

# ---------------------------------------------------------------- face
EY = 21   # eye row
LX, RXE = 19, 28  # left / right eye x (left pixel)

def draw_eyes(cv, kind, base_rgb):
    ink = BLACK
    if kind == "Dots":
        for ex in (LX, RXE):
            cv.rect(ex, EY, ex + 1, EY + 1, ink)
    elif kind == "Shiny":
        for ex in (LX, RXE):
            cv.rect(ex, EY - 1, ex + 2, EY + 2, ink)
            cv.px(ex, EY - 1, WHITE); cv.px(ex + 1, EY - 1, WHITE); cv.px(ex, EY, WHITE)
            cv.px(ex + 2, EY + 2, hx("#5a5a7a"))
    elif kind == "Happy":
        for ex in (LX, RXE):
            cv.px(ex, EY + 1, ink); cv.px(ex + 1, EY, ink); cv.px(ex + 2, EY + 1, ink)
    elif kind == "Sleepy":
        for ex in (LX, RXE):
            cv.rect(ex, EY + 1, ex + 2, EY + 1, ink); cv.px(ex, EY, ink); cv.px(ex + 2, EY, ink)
    elif kind == "Wink":
        cv.rect(LX, EY - 1, LX + 2, EY + 2, ink); cv.px(LX, EY - 1, WHITE); cv.px(LX + 1, EY - 1, WHITE)
        cv.px(RXE, EY, ink); cv.px(RXE + 1, EY + 1, ink); cv.px(RXE + 2, EY, ink)
    elif kind == "Hearts":
        r = hx("#ff2d55")
        for ex in (LX - 1, RXE):
            for (dx, dy) in [(0, 0), (1, 0), (3, 0), (4, 0), (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (1, 2), (2, 2), (3, 2), (2, 3)]:
                cv.px(ex + dx, EY - 1 + dy, r)
            cv.px(ex, EY - 1, hx("#ff8fa6"))
    elif kind == "Stars":
        y = hx("#ffd400")
        for ex in (LX, RXE):
            c = ex + 1
            for (dx, dy) in [(0, -2), (0, -1), (-2, 0), (-1, 0), (0, 0), (1, 0), (2, 0), (0, 1), (-1, 2), (1, 2)]:
                cv.px(c + dx, EY + dy, y)
            cv.px(c, EY, hx("#ff9f00"))
    elif kind == "Angry":
        for ex in (LX, RXE):
            cv.rect(ex, EY, ex + 2, EY + 2, ink); cv.px(ex + (0 if ex == LX else 2), EY, base_rgb)
        cv.px(LX - 1, EY - 2, ink); cv.px(LX, EY - 2, ink); cv.px(LX + 1, EY - 1, ink); cv.px(LX + 2, EY - 1, ink)
        cv.px(RXE + 3, EY - 2, ink); cv.px(RXE + 2, EY - 2, ink); cv.px(RXE + 1, EY - 1, ink); cv.px(RXE, EY - 1, ink)
    elif kind == "X Eyes":
        for ex in (LX, RXE):
            for d in range(3):
                cv.px(ex + d, EY - 1 + d, ink); cv.px(ex + 2 - d, EY - 1 + d, ink)
    elif kind == "Googly":
        for ex, off in ((LX - 1, 1), (RXE, 2)):
            cv.rect(ex, EY - 2, ex + 3, EY + 1, WHITE)
            cv.px(ex, EY - 2, OUTLINE); cv.px(ex + 3, EY - 2, OUTLINE); cv.px(ex, EY + 1, OUTLINE); cv.px(ex + 3, EY + 1, OUTLINE)
            cv.rect(ex + off, EY - 1 + (off - 1), ex + off + 1, EY + (off - 1), ink)
    elif kind == "Laser":
        for ex in (LX, RXE):
            cv.rect(ex, EY, ex + 2, EY + 1, hx("#ff1e1e")); cv.px(ex + 1, EY, hx("#ffd0d0"))
        for x in range(RXE + 3, G):
            cv.px(x, EY, hx("#ff3b3b")); cv.px(x, EY + 1, hx("#ff8080"))
        for x in range(0, LX):
            cv.px(x, EY, hx("#ff3b3b")); cv.px(x, EY + 1, hx("#ff8080"))
    elif kind == "Teary":
        for ex in (LX, RXE):
            cv.rect(ex, EY - 1, ex + 2, EY + 1, ink); cv.px(ex, EY - 1, WHITE)
        cv.px(LX, EY + 2, hx("#6fd3ff")); cv.px(LX, EY + 3, hx("#6fd3ff")); cv.px(LX - 1, EY + 4, hx("#a8e6ff"))

MY = 28  # mouth row

def draw_mouth(cv, kind):
    ink = BLACK
    red = hx("#c81d3a"); pink = hx("#ff7a9a")
    if kind == "Smile":
        cv.px(21, MY, ink); cv.rect(22, MY + 1, 26, MY + 1, ink); cv.px(27, MY, ink)
    elif kind == "Big Grin":
        cv.rect(20, MY, 28, MY, ink); cv.rect(21, MY + 1, 27, MY + 1, red); cv.rect(22, MY + 2, 26, MY + 2, ink)
        cv.px(20, MY + 1, ink); cv.px(28, MY + 1, ink); cv.px(21, MY + 2, ink); cv.px(27, MY + 2, ink)
        cv.rect(21, MY + 1, 27, MY + 1, WHITE) if False else None
        cv.rect(22, MY + 1, 26, MY + 1, red)
    elif kind == "O":
        cv.rect(23, MY, 25, MY + 2, ink); cv.px(24, MY + 1, red)
    elif kind == "Tongue":
        cv.px(21, MY, ink); cv.rect(22, MY + 1, 26, MY + 1, ink); cv.px(27, MY, ink)
        cv.rect(24, MY + 2, 25, MY + 3, pink); cv.px(24, MY + 2, red)
    elif kind == "Smirk":
        cv.rect(22, MY + 1, 26, MY + 1, ink); cv.px(27, MY, ink)
    elif kind == "Flat":
        cv.rect(22, MY + 1, 26, MY + 1, ink)
    elif kind == "Frown":
        cv.px(21, MY + 2, ink); cv.rect(22, MY + 1, 26, MY + 1, ink); cv.px(27, MY + 2, ink)
    elif kind == "Fangs":
        cv.px(21, MY, ink); cv.rect(22, MY + 1, 26, MY + 1, ink); cv.px(27, MY, ink)
        cv.px(22, MY + 2, WHITE); cv.px(26, MY + 2, WHITE)
    elif kind == "Cat":
        cv.px(21, MY, ink); cv.px(22, MY + 1, ink); cv.px(23, MY, ink); cv.px(24, MY - 1, ink)
        cv.px(25, MY, ink); cv.px(26, MY + 1, ink); cv.px(27, MY, ink)
    elif kind == "Bubblegum":
        cv.px(21, MY, ink); cv.rect(22, MY + 1, 24, MY + 1, ink)
        for y in range(MY - 1, MY + 4):
            for x in range(25, 31):
                if (x - 27.5) ** 2 + (y - MY - 1.5) ** 2 <= 7:
                    cv.px(x, y, hx("#ff8ecf"))
        cv.px(26, MY, hx("#ffd1ec"))
    elif kind == "Teeth":
        cv.rect(21, MY, 27, MY + 2, ink); cv.rect(22, MY + 1, 26, MY + 1, WHITE)
        cv.px(24, MY + 1, hx("#c8c8c8"))

def draw_cheeks(cv, kind):
    if kind == "Blush":
        for x in (16, 17, 31, 32):
            cv.px(x, 25, mix(cv.a[25, x], hx("#ff5f8a"), 0.6))
            cv.px(x, 26, mix(cv.a[26, x], hx("#ff5f8a"), 0.35))
    elif kind == "Freckles":
        for x, y in [(16, 25), (18, 26), (17, 24), (30, 25), (32, 26), (31, 24)]:
            cv.px(x, y, mix(cv.a[y, x], hx("#7a4a2a"), 0.7))

# ---------------------------------------------------------------- accessories
def draw_eyewear(cv, kind):
    if kind == "Shades":
        b = hx("#111118")
        cv.rect(17, EY - 1, 22, EY + 1, b); cv.rect(26, EY - 1, 31, EY + 1, b); cv.rect(23, EY - 1, 25, EY - 1, b)
        cv.px(18, EY - 1, hx("#6a6a90")); cv.px(27, EY - 1, hx("#6a6a90"))
        cv.px(16, EY - 1, b); cv.px(32, EY - 1, b)
    elif kind == "3D Glasses":
        f = hx("#f0f0f0")
        cv.rect(17, EY - 2, 31, EY - 2, f); cv.rect(17, EY + 2, 31, EY + 2, f)
        cv.rect(18, EY - 1, 22, EY + 1, hx("#ff3355")); cv.rect(26, EY - 1, 30, EY + 1, hx("#33c6ff"))
        for y in range(EY - 2, EY + 3):
            cv.px(17, y, f); cv.px(23, y, f); cv.px(25, y, f); cv.px(31, y, f)
        cv.px(24, EY - 1, f)
    elif kind == "Monocle":
        g = hx("#d9a400")
        for y in range(EY - 3, EY + 4):
            for x in range(RXE - 2, RXE + 5):
                d = (x - RXE - 1) ** 2 + (y - EY) ** 2
                if 8 <= d <= 12:
                    cv.px(x, y, g)
        for i in range(6):
            cv.px(RXE + 4, EY + 3 + i, g)
    elif kind == "Nerd Glasses":
        f = hx("#1e1a2e")
        for ex in (LX - 1, RXE - 1):
            cv.rect(ex, EY - 2, ex + 4, EY - 2, f); cv.rect(ex, EY + 2, ex + 4, EY + 2, f)
            for y in range(EY - 2, EY + 3):
                cv.px(ex, y, f); cv.px(ex + 4, y, f)
        cv.rect(LX + 4, EY - 1, RXE - 2, EY - 1, f)
    elif kind == "VR":
        v = hx("#e9ecf2"); d = hx("#2b2f3a")
        cv.rect(16, EY - 3, 32, EY + 2, v); cv.rect(17, EY - 2, 31, EY + 1, d)
        cv.rect(18, EY - 1, 30, EY - 1, hx("#5ef2c9"))
        cv.px(15, EY - 1, d); cv.px(33, EY - 1, d)

def top_y(shape):
    m = get_mask(shape)
    col = m[:, CX]
    return int(np.argmax(col))

def draw_headwear(cv, kind, shape, rng):
    t = top_y(shape)
    if shape == "Heart":
        t += 3
    if kind == "Party Hat":
        cols = [hx("#ff4fa3"), hx("#ffd43b")]
        for i in range(7):
            for x in range(CX - i // 2 - 1, CX + i // 2 + 1):
                cv.px(x, t - 7 + i, cols[(i // 2) % 2])
        cv.px(CX - 1, t - 8, WHITE); cv.px(CX, t - 8, WHITE); cv.px(CX, t - 9, WHITE)
    elif kind == "Crown":
        g = hx("#ffcc00"); gd = hx("#c98f00")
        cv.rect(CX - 5, t - 3, CX + 4, t, g); cv.rect(CX - 5, t, CX + 4, t, gd)
        for x in (CX - 5, CX - 1, CX + 3):
            cv.px(x, t - 4, g); cv.px(x + 1, t - 4, g); cv.px(x, t - 5, g)
        cv.px(CX - 3, t - 2, hx("#e63946")); cv.px(CX + 1, t - 2, hx("#2f80ed"))
    elif kind == "Beanie":
        c = rng.choice([hx("#e63946"), hx("#2a9d8f"), hx("#f4a261"), hx("#5b5bd6")])
        cv.rect(CX - 7, t - 3, CX + 6, t + 1, c)
        cv.rect(CX - 6, t - 5, CX + 5, t - 4, c)
        cv.rect(CX - 7, t + 1, CX + 6, t + 1, shade(c, 0.7))
        cv.rect(CX - 1, t - 7, CX, t - 6, WHITE)
    elif kind == "Cap":
        c = rng.choice([hx("#1d3557"), hx("#e63946"), hx("#2a9d8f"), hx("#111111")])
        cv.rect(CX - 6, t - 4, CX + 5, t + 1, c)
        cv.rect(CX - 5, t - 5, CX + 4, t - 5, c)
        cv.rect(CX + 2, t + 1, CX + 11, t + 2, shade(c, 0.75))
        cv.px(CX - 1, t - 2, hx("#5ef2c9")); cv.px(CX, t - 2, hx("#5ef2c9"))
    elif kind == "Top Hat":
        b = hx("#18151f")
        cv.rect(CX - 4, t - 9, CX + 3, t - 1, b)
        cv.rect(CX - 7, t, CX + 6, t + 1, b)
        cv.rect(CX - 4, t - 3, CX + 3, t - 2, hx("#c1121f"))
    elif kind == "Halo":
        g = hx("#ffe066")
        for x in range(CX - 6, CX + 6):
            cv.px(x, t - 5, g); cv.px(x, t - 2, g)
        for y in range(t - 4, t - 2):
            cv.px(CX - 7, y, g); cv.px(CX + 6, y, g)
    elif kind == "Propeller":
        cols = [hx("#e63946"), hx("#ffd43b"), hx("#2f80ed"), hx("#2a9d8f")]
        for i in range(4):
            cv.rect(CX - 6 + i * 3, t - 3, CX - 4 + i * 3, t, cols[i])
        cv.rect(CX - 6, t - 4, CX + 5, t - 4, cols[1])
        cv.px(CX, t - 5, hx("#555555")); cv.px(CX, t - 6, hx("#555555"))
        cv.rect(CX - 5, t - 7, CX + 4, t - 7, hx("#e63946"))
    elif kind == "Flower":
        p = rng.choice([hx("#ff6fb5"), hx("#ffffff"), hx("#ffd43b")])
        fx, fy = CX + 6, t + 1
        for dx, dy in [(0, -2), (-2, 0), (2, 0), (0, 2), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
            cv.px(fx + dx, fy + dy, p)
        cv.px(fx, fy, hx("#ffb703"))
        cv.px(fx - 2, fy + 3, hx("#4caf50")); cv.px(fx - 3, fy + 3, hx("#4caf50"))
    elif kind == "Bow":
        r = rng.choice([hx("#ff2d55"), hx("#7b2cbf"), hx("#ff8fab")])
        for dy in range(-2, 3):
            for dx in range(1, 5 - abs(dy)):
                cv.px(CX - 1 - dx, t + dy, r); cv.px(CX + dx, t + dy, r)
        cv.rect(CX - 1, t - 1, CX, t + 1, shade(r, 0.7))
    elif kind == "Horns":
        h = hx("#d62828")
        for i in range(4):
            cv.px(CX - 8 + i // 2, t + 2 - i, h); cv.px(CX - 7 + i // 2, t + 2 - i, h)
            cv.px(CX + 7 - i // 2, t + 2 - i, h); cv.px(CX + 6 - i // 2, t + 2 - i, h)
    elif kind == "Antenna":
        a = hx("#3a3a4a")
        for i in range(6):
            cv.px(CX - 3 - i // 3, t - i, a); cv.px(CX + 2 + i // 3, t - i, a)
        cv.rect(CX - 6, t - 7, CX - 5, t - 6, hx("#5ef2c9")); cv.rect(CX + 4, t - 7, CX + 5, t - 6, hx("#ff4fa3"))
    elif kind == "Cowboy":
        b = hx("#8b5a2b"); bd = hx("#5c3a18")
        cv.rect(CX - 4, t - 5, CX + 3, t, b)
        cv.rect(CX - 9, t + 1, CX + 8, t + 1, b)
        cv.px(CX - 9, t, b); cv.px(CX + 8, t, b)
        cv.rect(CX - 4, t - 1, CX + 3, t - 1, bd)
        cv.px(CX - 1, t - 5, bd); cv.px(CX, t - 5, bd)
    elif kind == "Wizard":
        w = hx("#3c2a8c"); s = hx("#ffd43b")
        for i in range(10):
            half = i // 2
            for x in range(CX - half - 1, CX + half + 1):
                cv.px(x + (2 if i < 3 else 0), t - 9 + i, w)
        cv.rect(CX - 8, t + 1, CX + 7, t + 1, w)
        cv.px(CX - 1, t - 3, s); cv.px(CX + 2, t - 6, s); cv.px(CX - 3, t - 1, s)

# ---------------------------------------------------------------- compose
def roll(rng):
    sky = wpick(rng, [(k, v[1]) for k, v in SKIES.items()])
    color = wpick(rng, [(k, v[1]) for k, v in BALLOON_COLORS.items()])
    shape = wpick(rng, SHAPES)
    pattern = "Solid" if color in ("Rainbow", "Chrome", "Gold") else wpick(rng, PATTERNS)
    second = rng.choice([c for c in SECOND if c != color])
    t = {
        "Sky": sky,
        "Clouds": wpick(rng, CLOUDS),
        "Sky Extra": wpick(rng, EXTRAS),
        "Balloon": shape,
        "Color": color,
        "Pattern": pattern,
        "Pattern Color": second if pattern not in ("Solid", "Sparkle") else "None",
        "Eyes": wpick(rng, EYES),
        "Mouth": wpick(rng, MOUTHS),
        "Cheeks": wpick(rng, CHEEKS),
        "Headwear": wpick(rng, HEADWEAR),
        "Eyewear": wpick(rng, EYEWEAR),
    }
    # keep things readable
    if t["Sky Extra"] == "Sun" and sky in ("Night", "Deep Space", "Aurora"):
        t["Sky Extra"] = "Moon"
    if t["Sky Extra"] == "Moon" and sky in ("Day Blue", "Sunset", "Golden Hour", "Mint Sky"):
        t["Sky Extra"] = "Sun"
    if t["Eyes"] in ("Laser", "Hearts", "Stars", "Googly") and t["Eyewear"] != "None":
        t["Eyewear"] = "None"
    if t["Eyewear"] == "VR":
        t["Eyes"] = "Hidden"
    if t["Balloon"] == "Hot Air" and t["Headwear"] in ("Horns", "Bow"):
        t["Headwear"] = "None"
    return t

def render(t, rng):
    cv = Canvas()
    draw_sky(cv, t["Sky"], rng)
    if t["Sky Extra"] == "Rainbow":
        draw_extras(cv, "Rainbow", t["Sky"], rng)
    draw_clouds(cv, t["Clouds"], t["Sky"], rng)
    if t["Sky Extra"] not in ("Rainbow",):
        draw_extras(cv, t["Sky Extra"], t["Sky"], rng)
    second = t["Pattern Color"] if t["Pattern Color"] != "None" else "Snow"
    draw_balloon(cv, t["Balloon"], t["Color"], t["Pattern"], second, rng)
    base = cv.a[26, 24].copy()
    draw_cheeks(cv, t["Cheeks"])
    if t["Eyes"] != "Hidden":
        draw_eyes(cv, t["Eyes"], base)
    draw_mouth(cv, t["Mouth"])
    draw_eyewear(cv, t["Eyewear"])
    draw_headwear(cv, t["Headwear"], t["Balloon"], rng)
    return cv

def dna(t):
    keys = ["Sky", "Clouds", "Sky Extra", "Balloon", "Color", "Pattern", "Pattern Color", "Eyes", "Mouth", "Cheeks", "Headwear", "Eyewear"]
    return hashlib.sha1("|".join(t[k] for k in keys).encode()).hexdigest()

LEGENDARY = [
    ("The Elysian", {"Sky": "Elysian Gold", "Color": "Gold", "Balloon": "Party", "Headwear": "Crown", "Eyes": "Stars", "Mouth": "Big Grin", "Eyewear": "None", "Clouds": "Cloud Bed", "Sky Extra": "Sun"}),
    ("Hyper Spirit", {"Sky": "Hyper Teal", "Color": "Hyper", "Balloon": "Party", "Headwear": "Halo", "Eyes": "Shiny", "Mouth": "Smile", "Eyewear": "VR", "Clouds": "Few", "Sky Extra": "Shooting Star"}),
    ("Cosmic Drifter", {"Sky": "Deep Space", "Color": "Chrome", "Balloon": "Hot Air", "Headwear": "Antenna", "Eyes": "Laser", "Mouth": "O", "Eyewear": "None", "Clouds": "None", "Sky Extra": "None"}),
    ("Rainbow King", {"Sky": "Day Blue", "Color": "Rainbow", "Balloon": "Heart", "Headwear": "Crown", "Eyes": "Hearts", "Mouth": "Big Grin", "Eyewear": "None", "Clouds": "Many", "Sky Extra": "Rainbow"}),
    ("Night Wizard", {"Sky": "Aurora", "Color": "Grape", "Balloon": "Party", "Headwear": "Wizard", "Eyes": "Stars", "Mouth": "Smirk", "Eyewear": "None", "Clouds": "Few", "Sky Extra": "Moon"}),
]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=10000)
    ap.add_argument("--image-base", default="https://YOUR-SITE-DOMAIN/nft/images/")
    args = ap.parse_args()
    os.makedirs(OUT_IMG, exist_ok=True)
    os.makedirs(OUT_META, exist_ok=True)

    rng = random.Random(SEED)
    traits, seen = [], set()
    # legendaries first, then shuffle positions
    for name, lt in LEGENDARY:
        t = {"Sky": "", "Clouds": "", "Sky Extra": "", "Balloon": "", "Color": "", "Pattern": "Solid", "Pattern Color": "None",
             "Eyes": "", "Mouth": "", "Cheeks": "Blush", "Headwear": "", "Eyewear": ""}
        t.update(lt)
        if t["Eyewear"] == "VR":
            t["Eyes"] = "Hidden"
        t["_legendary"] = name
        traits.append(t); seen.add(dna(t))
    while len(traits) < args.count:
        t = roll(rng)
        d = dna(t)
        if d in seen:
            continue
        seen.add(d); traits.append(t)
    rng.shuffle(traits)

    counts = {}
    for i, t in enumerate(traits):
        tid = i + 1
        r = random.Random(SEED * 31 + tid)
        cv = render(t, r)
        cv.img().save(os.path.join(OUT_IMG, f"{tid}.png"), optimize=True)
        attrs = [{"trait_type": k, "value": v} for k, v in t.items() if not k.startswith("_")]
        name = f"Elysium Balloon #{tid}"
        if "_legendary" in t:
            attrs.append({"trait_type": "Legendary", "value": t["_legendary"]})
            name = f"{t['_legendary']} — Elysium Balloon #{tid}"
        meta = {
            "name": name,
            "description": "10,000 happy balloons floating over the Elysian sky. Pixel art, on Elysium — the HYPE L2.",
            "image": f"{args.image_base}{tid}.png",
            "attributes": attrs,
        }
        with open(os.path.join(OUT_META, f"{tid}.json"), "w") as f:
            json.dump(meta, f, separators=(",", ":"))
        for a in attrs:
            counts.setdefault(a["trait_type"], {}).setdefault(a["value"], 0)
            counts[a["trait_type"]][a["value"]] += 1
        if tid % 1000 == 0:
            print("generated", tid, flush=True)

    with open(os.path.join(ROOT, "public", "nft", "traits.json"), "w") as f:
        json.dump({"total": args.count, "traits": counts}, f, indent=1)
    print("done:", args.count)

if __name__ == "__main__":
    main()
