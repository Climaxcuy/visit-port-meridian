#!/usr/bin/env python3
"""PORT MERIDIAN — travel poster for a place that isn't there.

Draws a 1024x1024 vintage deco / risograph travel poster with Pillow:
a harbour where the sea flows UP into the sky, a tall ship climbing the
vertical current toward a golden sun. The only text in the picture is the
place name itself: "PORT MERIDIAN".

Writes /output/entry.png (PNG, 1024x1024, <= 1 MiB).
"""
import math
import os
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = Path("/output/entry.png")

BASE = Path(__file__).resolve().parent
# Fonts MUST load from inside the repo (the sandbox grader has no
# absolute user paths and no network). Both fonts live in assets/fonts/.
FONT_DIR = BASE / "assets" / "fonts"


def font(name, size):
    p = FONT_DIR / name
    if p.exists():
        return ImageFont.truetype(str(p), size)
    return ImageFont.load_default(size)


# ---- palette: deco blue & gold -------------------------------------------
NAVY_DEEP = (10, 27, 51)
NAVY = (16, 42, 78)
BLUE = (30, 74, 117)
TEAL = (27, 110, 140)
TEAL_LT = (64, 158, 178)
GOLD = (232, 180, 76)
GOLD_LT = (245, 209, 120)
CREAM = (245, 234, 208)
FOAM = (235, 246, 248)
INK = (8, 20, 38)
SEA_DARK = (13, 38, 66)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(size, stops):
    """Vertical gradient image. stops: list of (y_frac, color)."""
    w, h = size
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        f = y / max(h - 1, 1)
        for i in range(len(stops) - 1):
            f0, c0 = stops[i]
            f1, c1 = stops[i + 1]
            if f0 <= f <= f1:
                t = 0 if f1 == f0 else (f - f0) / (f1 - f0)
                col = lerp(c0, c1, t)
                break
        else:
            col = stops[-1][1]
        for x in range(w):
            px[x, y] = col
    return img


def bezier(p0, p1, p2, t):
    u = 1 - t
    return (
        u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
        u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1],
    )


def tracked_width(d, text, fnt, tracking=6):
    """Full drawn width of tracked text (glyphs + tracking gaps)."""
    return (sum(d.textlength(ch, font=fnt) for ch in text)
            + tracking * (len(text) - 1))


def draw_tracked_text(layer, center_x, y, text, fnt, fill, tracking=6):
    """Draw text with letter tracking, centred on center_x, top at y."""
    d = ImageDraw.Draw(layer)
    widths = [d.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = center_x - total / 2
    for ch, wch in zip(text, widths):
        d.text((x, y), ch, font=fnt, fill=fill)
        x += wch + tracking
    return total


def build_ship():
    """Tall ship, side view, bow pointing right, on its own layer.

    Hull has a deeply curved bottom (sampled quadratic bezier) so it reads
    as a ship's hull, not a plank, once rotated onto the diagonal current.
    """
    S = Image.new("RGBA", (520, 340), (0, 0, 0, 0))
    d = ImageDraw.Draw(S)
    hull = (20, 42, 56)
    # hull: straight sheer on top, curved belly below (bow -> stern)
    bottom = [bezier((452, 212), (240, 306), (30, 212), t)
              for t in [i / 24 for i in range(25)]]
    d.polygon([(30, 210), (452, 196)] + bottom, fill=hull)
    # gold sheer stripe following the deck line
    d.polygon([(30, 210), (452, 196), (452, 208), (30, 221)],
              fill=GOLD)
    # stern castle + bow
    d.polygon([(30, 210), (58, 168), (96, 196), (80, 214)], fill=(24, 52, 70))
    d.line([(452, 208), (500, 178)], fill=hull, width=7)  # bowsprit
    d.polygon([(500, 178), (512, 186), (496, 192)], fill=GOLD)  # pennant tip
    # masts: fore 150, main 255, mizzen 360
    for mx, top, sail_top in ((150, 78, 92), (255, 44, 58), (360, 92, 104)):
        d.line([(mx, 206), (mx, top)], fill=(52, 36, 24), width=6)
    # yards
    for mx, y in ((150, 96), (255, 66), (360, 110)):
        d.line([(mx - 52, y), (mx + 52, y)], fill=(52, 36, 24), width=5)
    # sails (cream, slightly billowed)
    def sail(cx, top, w, bot):
        d.polygon([(cx - w, top), (cx + w, top), (cx + w - 8, bot),
                   (cx - w + 8, bot)], fill=CREAM, outline=GOLD_LT)
    sail(150, 100, 46, 196)
    sail(255, 70, 62, 196)
    sail(360, 114, 40, 196)
    # top sails
    d.polygon([(228, 66), (282, 66), (276, 96), (234, 96)], fill=CREAM,
              outline=GOLD_LT)
    d.polygon([(128, 92), (172, 92), (168, 118), (132, 118)], fill=CREAM,
              outline=GOLD_LT)
    # flag on main mast
    d.polygon([(255, 44), (288, 52), (255, 62)], fill=GOLD)
    # portholes
    for px in (120, 180, 240, 300, 360):
        d.ellipse([(px - 5, 228), (px + 5, 238)], fill=GOLD_LT)
    return S


def main():
    random.seed(20261121)
    img = Image.new("RGB", (W, H), NAVY_DEEP)

    # ---- sky: deep navy -> blue -> gold band at the horizon --------------
    sky = vgrad((W, 700), [(0.0, NAVY_DEEP), (0.45, NAVY), (0.8, BLUE),
                           (1.0, (214, 164, 74))])
    img.paste(sky, (0, 0))

    # ---- stars in the upper sky ------------------------------------------
    d = ImageDraw.Draw(img, "RGBA")
    for _ in range(90):
        x = random.randint(20, 1004)
        y = random.randint(16, 300)
        r = random.choice([1, 1, 2])
        a = random.randint(90, 210)
        d.ellipse([(x - r, y - r), (x + r, y + r)], fill=(245, 234, 208, a))

    # ---- golden sun with deco rays, upper right --------------------------
    # Below the name band (rule line ~y180) and clear of the ship's bow:
    # the gold disc stays whole.
    sun_cx, sun_cy, sun_r = 880, 270, 80
    rays = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rays)
    for k in range(24):
        ang = math.radians(k * 15)
        wdt = math.radians(3.2)
        p1 = (sun_cx + math.cos(ang - wdt) * (sun_r + 8),
              sun_cy + math.sin(ang - wdt) * (sun_r + 8))
        p2 = (sun_cx + math.cos(ang + wdt) * (sun_r + 8),
              sun_cy + math.sin(ang + wdt) * (sun_r + 8))
        p3 = (sun_cx + math.cos(ang) * (sun_r + 150),
              sun_cy + math.sin(ang) * (sun_r + 150))
        rd.polygon([p1, p2, p3], fill=(245, 209, 120, 46))
    img = Image.alpha_composite(img.convert("RGBA"), rays)
    d = ImageDraw.Draw(img, "RGBA")
    for r, col in ((sun_r + 30, (232, 180, 76, 26)),
                   (sun_r + 18, (232, 180, 76, 40)),
                   (sun_r, (245, 209, 120, 255))):
        d.ellipse([(sun_cx - r, sun_cy - r), (sun_cx + r, sun_cy + r)], fill=col)
    # deco ring around the sun
    d.ellipse([(sun_cx - sun_r - 10, sun_cy - sun_r - 10),
               (sun_cx + sun_r + 10, sun_cy + sun_r + 10)],
              outline=(245, 234, 208, 200), width=3)

    # ---- clouds: thin, layered deco wisps (never flat solid ellipses) ----
    def cloud(cx, cy, w, alpha):
        # three overlapping thin ellipses, slightly offset: a soft layered wisp
        for (ox, oy, ww, hh, a) in ((-w * 0.30, 3, w * 0.58, 11, int(alpha * 0.75)),
                                    (0, 0, w, 13, alpha),
                                    (w * 0.32, 4, w * 0.52, 10, int(alpha * 0.7))):
            d.ellipse([(cx + ox - ww // 2, cy + oy - hh // 2),
                       (cx + ox + ww // 2, cy + oy + hh // 2)],
                      fill=(245, 234, 208, a))

    cloud(220, 300, 260, 44)
    cloud(180, 350, 190, 36)
    cloud(870, 470, 200, 40)
    cloud(175, 520, 220, 32)

    # ---- birds ------------------------------------------------------------
    for (bx, by, s) in ((330, 240, 14), (380, 210, 11), (300, 285, 9),
                        (850, 180, 12), (900, 220, 9)):
        d.arc([(bx - s, by - s // 2), (bx, by + s // 2)], 200, 340,
              fill=(245, 234, 208, 220), width=3)
        d.arc([(bx, by - s // 2), (bx + s, by + s // 2)], 200, 340,
              fill=(245, 234, 208, 220), width=3)

    # ---- sea: horizon at y=660 down to the harbour -----------------------
    sea = vgrad((W, H - 660), [(0.0, (58, 110, 140)), (0.35, (24, 74, 108)),
                               (1.0, SEA_DARK)])
    img.paste(sea, (0, 660))
    d = ImageDraw.Draw(img, "RGBA")
    d.line([(0, 660), (W, 660)], fill=(245, 209, 120, 220), width=3)
    # gold reflection streaks under the sun
    for i in range(14):
        y = 668 + i * 9
        wdt = 150 - i * 6
        x0 = sun_cx - wdt // 2 + random.randint(-8, 8)
        d.line([(x0, y), (x0 + wdt, y)], fill=(245, 209, 120, 130 - i * 6),
               width=3)
    # gentle wave strokes
    for _ in range(46):
        x = random.randint(20, 1000)
        y = random.randint(680, 800)
        ln = random.randint(24, 70)
        d.line([(x, y), (x + ln, y)], fill=(235, 246, 248, 70), width=2)

    # ---- the vertical current: sea flowing UP into the sky ---------------
    p0, p1, p2 = (628, 668), (788, 420), (700, 178)
    cur = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cur)
    steps = 60
    for i in range(steps):
        t = i / steps
        x, y = bezier(p0, p1, p2, t)
        r = 78 - 52 * t          # tapering ribbon
        col = lerp(TEAL, (214, 232, 238), t)
        cd.ellipse([(x - r, y - r * 0.62), (x + r, y + r * 0.62)],
                   fill=col + (235,))
    # bright core of the stream
    for i in range(steps):
        t = i / steps
        x, y = bezier(p0, p1, p2, t)
        r = (46 - 30 * t) * 0.8
        col = lerp((120, 196, 214), (250, 244, 224), t)
        cd.ellipse([(x - r, y - r * 0.55), (x + r, y + r * 0.55)],
                   fill=col + (215,))
    # foam flecks along the stream
    for _ in range(120):
        t = random.random()
        x, y = bezier(p0, p1, p2, t)
        spread = (78 - 52 * t) * 0.85
        fx = x + random.uniform(-spread, spread)
        fy = y + random.uniform(-spread * 0.5, spread * 0.5)
        r = random.randint(2, 6)
        cd.ellipse([(fx - r, fy - r), (fx + r, fy + r)],
                   fill=(255, 255, 255, random.randint(140, 235)))
    # spray where the stream meets the sky
    for _ in range(60):
        ang = random.uniform(0, 2 * math.pi)
        rr = random.uniform(20, 90)
        sx = p2[0] + math.cos(ang) * rr
        sy = p2[1] + math.sin(ang) * rr * 0.7 - 10
        r = random.randint(2, 5)
        cd.ellipse([(sx - r, sy - r), (sx + r, sy + r)],
                   fill=(250, 244, 224, random.randint(120, 220)))
    img = Image.alpha_composite(img, cur)
    d = ImageDraw.Draw(img, "RGBA")
    # foam ring where the current leaves the sea
    for r, a in ((96, 90), (80, 140), (64, 190)):
        d.ellipse([(p0[0] - r, p0[1] - 26), (p0[0] + r, p0[1] + 26)],
                  outline=(235, 246, 248, a), width=4)

    # ---- the tall ship climbing the current ------------------------------
    # 60 deg: diagonal enough to read as a ship sailing up, not a tower.
    # Scaled down a little so it clears the sun and the name.
    ship = build_ship().rotate(60, resample=Image.BICUBIC, expand=True)
    ship = ship.resize((int(ship.width * 0.8), int(ship.height * 0.8)),
                       Image.LANCZOS)
    sx, sy = bezier(p0, p1, p2, 0.40)
    img.paste(ship, (int(sx - ship.width // 2), int(sy - ship.height // 2)),
              ship)

    # ---- distant harbour silhouettes on the horizon, left ----------------
    for (hx, hw, hh) in ((60, 60, 26), (130, 44, 40), (182, 70, 22),
                         (260, 50, 32)):
        d.rectangle([(hx, 660 - hh), (hx + hw, 660)], fill=(16, 42, 78, 255))
    # one small ship far out on the sea
    d.polygon([(880, 700), (950, 700), (940, 716), (892, 716)], fill=INK)
    d.line([(915, 700), (915, 668)], fill=INK, width=3)
    d.polygon([(915, 668), (915, 696), (940, 696)], fill=(245, 234, 208, 230))

    # ---- foreground harbour: piers, warehouses, lighthouse ---------------
    d.rectangle([(0, 812), (W, H)], fill=INK)
    # quay edge with gold trim
    d.rectangle([(0, 812), (W, 820)], fill=GOLD)
    # warehouse row with arched glowing windows
    for (wx, ww, wh) in ((36, 150, 96), (206, 120, 72), (700, 150, 88),
                         (866, 120, 66)):
        d.rectangle([(wx, 1024 - wh), (wx + ww, 1024)], fill=(20, 48, 84))
        d.polygon([(wx, 1024 - wh), (wx + ww // 2, 1024 - wh - 26),
                   (wx + ww, 1024 - wh)], fill=(20, 48, 84))
        for k in range(ww // 34):
            ax = wx + 18 + k * 34
            ay = 1024 - wh + 26
            d.pieslice([(ax, ay), (ax + 18, ay + 30)], 180, 360,
                       fill=GOLD_LT)
            d.rectangle([(ax, ay + 15), (ax + 18, ay + 34)], fill=GOLD_LT)
    # lighthouse, left (beam removed: it read as a grey triangle over the sea)
    lx = 560
    d.polygon([(lx - 26, 1024), (lx - 14, 872), (lx + 14, 872),
               (lx + 26, 1024)], fill=(245, 234, 208))
    d.rectangle([(lx - 16, 856), (lx + 16, 876)], fill=INK)
    d.ellipse([(lx - 12, 838), (lx + 12, 862)], fill=GOLD_LT)
    d.polygon([(lx - 20, 838), (lx + 20, 838), (lx + 26, 830),
               (lx - 26, 830)], fill=INK)
    d = ImageDraw.Draw(img, "RGBA")
    # lamp posts along the quay
    for lpx in (120, 300, 470, 700, 880):
        d.line([(lpx, 1024), (lpx, 900)], fill=(245, 234, 208), width=4)
        d.ellipse([(lpx - 9, 884), (lpx + 9, 902)], fill=GOLD_LT)
        d.ellipse([(lpx - 4, 889), (lpx + 4, 897)], fill=(255, 244, 200))
    # moored rowboat
    d.polygon([(880, 786), (960, 786), (948, 802), (894, 802)], fill=(20, 48, 84))
    d.line([(920, 786), (920, 762)], fill=(20, 48, 84), width=3)

    # ---- poster frame: double deco border --------------------------------
    d.rectangle([(14, 14), (W - 15, H - 15)], outline=CREAM, width=5)
    d.rectangle([(30, 30), (W - 31, H - 31)], outline=GOLD, width=2)
    # corner diamonds
    for (cx, cy) in ((22, 22), (W - 23, 22), (22, H - 23), (W - 23, H - 23)):
        d.polygon([(cx, cy - 9), (cx + 9, cy), (cx, cy + 9), (cx - 9, cy)],
                  fill=GOLD)

    # ---- the name: PORT MERIDIAN, big and deliberate ---------------------
    name_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fnt = font("PlayfairDisplay-900.ttf", 112)
    # fit the FULL tracked width inside the inner frame (<= 900 px)
    nd = ImageDraw.Draw(name_layer)
    while (tracked_width(nd, "PORT MERIDIAN", fnt, 8) > 900
           and fnt.size > 60):
        fnt = font("PlayfairDisplay-900.ttf", fnt.size - 4)
    name_top = 62
    # soft shadow for legibility, then gold letters
    draw_tracked_text(name_layer, W // 2 + 3, name_top + 4, "PORT MERIDIAN",
                      fnt, (6, 16, 32, 235), tracking=8)
    draw_tracked_text(name_layer, W // 2, name_top, "PORT MERIDIAN",
                      fnt, GOLD_LT + (255,), tracking=8)
    img = Image.alpha_composite(img, name_layer)
    d = ImageDraw.Draw(img, "RGBA")
    # deco rule under the name: line — diamond — line
    ry = name_top + fnt.size + 26
    d.line([(150, ry), (462, ry)], fill=GOLD, width=3)
    d.line([(562, ry), (874, ry)], fill=GOLD, width=3)
    d.polygon([(512, ry - 9), (521, ry), (512, ry + 9), (503, ry)], fill=GOLD)
    d.ellipse([(496, ry - 3), (502, ry + 3)], fill=GOLD)
    d.ellipse([(522, ry - 3), (528, ry + 3)], fill=GOLD)

    # ---- risograph grain (coarse, so the PNG stays small) ----------------
    noise = Image.effect_noise((128, 128), 26).convert("L")
    noise = noise.resize((W, H), Image.BILINEAR)
    img = Image.blend(img.convert("RGB"),
                      Image.merge("RGB", (noise, noise, noise)), 0.05)

    # ---- save -------------------------------------------------------------
    img = img.convert("RGB")
    os.makedirs(OUT.parent, exist_ok=True)
    img.save(OUT, optimize=True)
    print(f"saved {OUT} {OUT.stat().st_size} bytes {img.size}")


if __name__ == "__main__":
    main()
