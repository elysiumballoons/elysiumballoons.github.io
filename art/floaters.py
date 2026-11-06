"""Transparent balloons (no sky) used for the drifting hero animation. Writes public/floaters/1..40.png"""
import os, random, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
import generate as g

KEY = np.array([255, 0, 255], dtype=np.int16)
out = os.path.join(g.ROOT, "public", "floaters")
os.makedirs(out, exist_ok=True)
rng = random.Random(7)
for i in range(1, 41):
    t = g.roll(rng)
    if t["Eyes"] == "Laser":
        t["Eyes"] = "Shiny"
    cv = g.Canvas()
    cv.a[:, :] = KEY
    second = t["Pattern Color"] if t["Pattern Color"] != "None" else "Snow"
    g.draw_balloon(cv, t["Balloon"], t["Color"], t["Pattern"], second, rng)
    base = cv.a[26, 24].copy()
    g.draw_cheeks(cv, t["Cheeks"])
    if t["Eyes"] != "Hidden":
        g.draw_eyes(cv, t["Eyes"], base)
    g.draw_mouth(cv, t["Mouth"])
    g.draw_eyewear(cv, t["Eyewear"])
    g.draw_headwear(cv, t["Headwear"], t["Balloon"], rng)
    rgb = np.clip(cv.a, 0, 255).astype(np.uint8)
    alpha = np.where((cv.a == KEY).all(axis=2), 0, 255).astype(np.uint8)
    im = Image.fromarray(np.dstack([rgb, alpha]), "RGBA").resize((g.G * 6, g.G * 6), Image.NEAREST)
    im.save(os.path.join(out, f"{i}.png"), optimize=True)
print("floaters done")
