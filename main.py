#!/usr/bin/env python3
"""news-image-20261124: one-page newspaper front page summing up the world
news of Tuesday 24 November 2026.

Pure Python 3 standard library. Draws a 1024x1024 PNG from code only
(no network, no fonts, no image assets): a 5x7 bitmap font defined below,
vector primitives, and a hand-rolled PNG encoder. Deterministic: running
it twice produces byte-identical output.
"""

import os
import struct
import zlib

W, H = 1024, 1024
PAPER = (246, 241, 227)
INK = (17, 17, 17)
RED = (163, 18, 18)
BLUE = (26, 58, 107)
GREEN = (18, 110, 60)
GREY = (90, 86, 76)
LIGHT = (232, 226, 208)

# ---------------------------------------------------------------- canvas
buf = bytearray()
for _ in range(H):
    buf += bytes(PAPER) * W


def set_px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i], buf[i + 1], buf[i + 2] = c


def fill_rect(x, y, w, h, c):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    for yy in range(y0, y1):
        i = (yy * W + x0) * 3
        row = bytes(c) * (x1 - x0)
        buf[i:i + (x1 - x0) * 3] = row


def hline(x, y, w, c):
    fill_rect(x, y, w, 1, c)


def vline(x, y, h, c):
    fill_rect(x, y, 1, h, c)


def line(x0, y0, x1, y1, c):
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        set_px(x0, y0, c)
        if x0 == x1 and y0 == y1:
            return
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy


def fill_circle(cx, cy, r, c):
    for yy in range(cy - r, cy + r + 1):
        dx = int((r * r - (yy - cy) ** 2) ** 0.5) if abs(yy - cy) <= r else -1
        if dx >= 0:
            fill_rect(cx - dx, yy, 2 * dx + 1, 1, c)


def circle(cx, cy, r, c):
    x, y, d = 0, r, 3 - 2 * r
    while x <= y:
        for sx, sy in ((x, y), (y, x), (-x, y), (-y, x),
                       (x, -y), (y, -x), (-x, -y), (-y, -x)):
            set_px(cx + sx, cy + sy, c)
        if d < 0:
            d += 4 * x + 6
        else:
            d += 4 * (x - y) + 10
            y -= 1
        x += 1


def fill_triangle(x0, y0, x1, y1, x2, y2, c):
    ys = sorted(((y0, x0), (y1, x1), (y2, x2)))
    (ya, xa), (yb, xb), (yc, xc) = ys
    if ya == yc:
        return
    for y in range(ya, yc + 1):
        if y < yb:
            t1 = (y - ya) / (yb - ya) if yb != ya else 0.0
            xa_y = xa + (xb - xa) * t1
        else:
            t1 = (y - yb) / (yc - yb) if yc != yb else 0.0
            xa_y = xb + (xc - xb) * t1
        t2 = (y - ya) / (yc - ya)
        xb_y = xa + (xc - xa) * t2
        lo, hi = int(min(xa_y, xb_y)), int(max(xa_y, xb_y))
        fill_rect(lo, y, hi - lo + 1, 1, c)


# ---------------------------------------------------------------- 5x7 font
FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", ".#.#.", ".#.#.", "..#..", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '-': (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    '/': ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    '&': (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    '%': ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '+': (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    '$': ("..#..", ".####", "#.#.#", ".###.", "..#.#", "####.", "..#.."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    '=': (".....", ".....", ".###.", ".....", ".###.", ".....", "....."),
}


def text_w(s, sc):
    return len(s) * 6 * sc - sc


def draw_text(x, y, s, sc, c):
    cx = x
    for ch in s:
        g = FONT.get(ch, FONT[' '])
        for r in range(7):
            row = g[r]
            for col in range(5):
                if row[col] == '#':
                    fill_rect(cx + col * sc, y + r * sc, sc, sc, c)
        cx += 6 * sc
    return cx


def draw_text_centered(cx, y, s, sc, c):
    draw_text(cx - text_w(s, sc) // 2, y, s, sc, c)


def wrap(s, max_w, sc):
    words = s.split(' ')
    lines, cur = [], ''
    for w_ in words:
        trial = (cur + ' ' + w_).strip()
        if text_w(trial, sc) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def draw_para(x, y, s, max_w, sc, c, lh=None):
    lh = lh or (9 * sc)
    for ln in wrap(s, max_w, sc):
        draw_text(x, y, ln, sc, c)
        y += lh
    return y


# ---------------------------------------------------------------- icons
def icon_bars(x, y, w, h):
    vals = (22, 34, 30, 52, 66, 92)
    bw = w // 7
    for i, v in enumerate(vals):
        bh = int(h * v / 100)
        fill_rect(x + i * bw + 2, y + h - bh, bw - 4, bh, GREEN)
    hline(x, y + h, w, INK)
    line(x, y + h - int(h * 0.92), x + w, y + 2, RED)


def icon_flame(x, y, s):
    fill_triangle(x + s // 2, y, x, y + s, x + s, y + s, (214, 90, 20))
    fill_triangle(x + s // 2, y + s // 3, x + s // 5, y + s, x + 4 * s // 5, y + s, (240, 170, 30))
    fill_circle(x + s // 2, y + 3 * s // 4, s // 6, (250, 220, 90))


def icon_ship(x, y, w, h):
    fill_triangle(x + w // 6, y + h // 2, x + 5 * w // 6, y + h // 2, x + 4 * w // 6, y + h - 6, (60, 60, 60))
    vline(x + w // 2, y + 4, h // 2, INK)
    fill_triangle(x + w // 2, y + 4, x + w // 2, y + h // 3, x + 5 * w // 6, y + h // 3, RED)
    for i, yy in enumerate((y + h - 8, y + h - 3)):
        for k in range(4):
            line(x + k * (w // 3) + 4, yy, x + k * (w // 3) + w // 6, yy, BLUE)


def icon_globe(x, y, r):
    circle(x, y, r, BLUE)
    hline(x - r, y, 2 * r, BLUE)
    vline(x, y - r, 2 * r, BLUE)
    for dy in (-r // 2, r // 2):
        w_ = int((r * r - dy * dy) ** 0.5)
        hline(x - w_, y + dy, 2 * w_, BLUE)
    fill_circle(x - r // 3, y - r // 3, 3, GREEN)
    fill_circle(x + r // 4, y + r // 4, 4, GREEN)


def icon_bolt(x, y, s):
    fill_triangle(x + 3 * s // 5, y, x + s // 5, y + s // 2, x + s // 2, y + s // 2, (240, 180, 20))
    fill_triangle(x + 2 * s // 5, y + s, x + 4 * s // 5, y + s // 2, x + s // 2, y + s // 2, (240, 180, 20))


def icon_flags(x, y, w, h):
    # two small flags on poles: India (saffron/white/green) and Nepal (red/blue)
    vline(x + 6, y, h, INK)
    vline(x + w - 6, y, h, INK)
    fill_rect(x + 7, y + 2, 26, 7, (255, 153, 51))
    fill_rect(x + 7, y + 9, 26, 7, (255, 255, 255))
    fill_rect(x + 7, y + 16, 26, 7, (19, 136, 8))
    fill_rect(x + w - 33, y + 2, 26, 21, (220, 20, 60))
    fill_rect(x + w - 33, y + 2, 26, 3, (0, 56, 147))
    fill_rect(x + w - 33, y + 20, 26, 3, (0, 56, 147))


def icon_doc(x, y, w, h):
    fill_rect(x, y, w, h, (255, 255, 255))
    fill_rect(x, y, w, 2, INK)
    fill_rect(x, y + h - 2, w, 2, INK)
    fill_rect(x, y, 2, h, INK)
    fill_rect(x + w - 2, y, 2, h, INK)
    for i in range(3):
        fill_rect(x + 6, y + 8 + i * 8, w - 18, 3, GREY)
    fill_circle(x + w - 12, y + h - 12, 8, RED)


# ---------------------------------------------------------------- layout
M = 36
CW = W - 2 * M

# Masthead
draw_text_centered(W // 2, 30, "THE WORLD TODAY", 9, INK)
hline(M, 108, CW, INK)
hline(M, 112, CW, INK)
draw_text_centered(W // 2, 122, "TUESDAY, 24 NOVEMBER 2026", 3, RED)
draw_text_centered(W // 2, 146, "WORLD NEWS IN ONE PAGE", 2, GREY)
hline(M, 168, CW, INK)

# Lead story
LY = 184
draw_text(M, LY, "MARKETS  -  TECHNOLOGY", 2, RED)
draw_text(M, LY + 26, "HUANG RETURNS", 6, INK)
draw_text(M, LY + 68, "TO NVIDIA", 6, INK)
draw_para(M, LY + 118,
          "BOARD REINSTATES JENSEN HUANG AS CHIEF EXECUTIVE AFTER AN INQUIRY. "
          "SHARES SURGE 31% AND ADD ALMOST $1 TRILLION IN VALUE IN A SINGLE DAY.",
          600, 2, INK)
draw_para(M, LY + 196,
          "THE BOARD VOTED UNANIMOUSLY AFTER AN INDEPENDENT INVESTIGATION. "
          "A SENATE BANKING COMMITTEE HEARING IS SET FOR 3 DECEMBER.",
          600, 2, GREY)
icon_bars(680, LY + 30, 300, 190)
draw_text(680, LY + 228, "+31% IN A DAY", 2, GREEN)
draw_text(680, LY + 248, "NEARLY $1 TN ADDED", 2, INK)
hline(M, 452, CW, INK)

# Story panels: two rows of three
PANELS = [
    ("INDONESIA", "FACTORY FIRE KILLS 24",
     "AT LEAST 24 DEAD AND ABOUT 30 MISSING AFTER A HUGE FACTORY FIRE. RESCUERS KEEP SEARCHING.",
     "flame"),
    ("LIBYA", "RUSSIAN WARSHIP DESTROYED",
     "A RUSSIAN NAVY CORVETTE IS DESTROYED IN AN EXPLOSION AND FIRE AT THE PORT OF BENGHAZI.",
     "ship"),
    ("CLIMATE", "COP31 ENDS WITHOUT A DEAL",
     "CLIMATE TALKS COLLAPSE WITH NO AGREEMENT ON STRONGER FOSSIL-FUEL PHASE-OUT LANGUAGE.",
     "globe"),
    ("UKRAINE", "STRIKE HITS KYIV REGION",
     "UKRAINE REPORTS A RUSSIAN ATTACK IN THE KYIV REGION THAT KILLED SEVERAL PEOPLE.",
     "bolt"),
    ("INDIA - NEPAL", "MODI, SHAH SEAL 8 DEALS",
     "INDIA AND NEPAL SIGN 8 DEALS AS MODI ANNOUNCES A RS 15,000 CRORE PACKAGE.",
     "handshake"),
    ("BANGLADESH", "HASINA ARREST VOW",
     "BANGLADESH VOWS TO ARREST FORMER PM SHEIKH HASINA IF SHE RETURNS FROM INDIA.",
     "gavel"),
]
PW = (CW - 2 * 24) // 3
PH = 196
for idx, (kick, head, body, icon) in enumerate(PANELS):
    row, col = divmod(idx, 3)
    px0 = M + col * (PW + 24)
    py0 = 472 + row * (PH + 20)
    if col:
        vline(px0 - 12, py0, PH, LIGHT)
    draw_text(px0, py0, kick, 2, RED)
    y = draw_para(px0, py0 + 22, head, PW, 3, INK, lh=30)
    y = draw_para(px0, y + 6, body, PW, 2, INK, lh=17)
    iy = py0 + PH - 34
    if icon == "flame":
        icon_flame(px0, iy, 30)
    elif icon == "ship":
        icon_ship(px0, iy, 90, 30)
    elif icon == "globe":
        icon_globe(px0 + 18, iy + 15, 15)
    elif icon == "bolt":
        icon_bolt(px0, iy, 30)
    elif icon == "handshake":
        icon_flags(px0, iy, 70, 26)
    elif icon == "gavel":
        icon_doc(px0, iy - 4, 44, 30)

hline(M, 924, CW, INK)
draw_para(M, 938,
          "ALSO TODAY: FIFA PICKS HOSTS FOR THE 2031 AND 2035 WOMEN'S WORLD CUPS - "
          "INDIA V NEW ZEALAND TEST ENDS IN A DRAW - CHICAGO O'HARE GROUND STOP IN "
          "THANKSGIVING RUSH - CHINA SETS 2030 WELFARE TARGETS - SOUTH KOREA RESHUFFLES CABINET",
          CW, 2, INK, lh=17)
hline(M, 992, CW, INK)
draw_text_centered(W // 2, 1000, "THE WORLD TODAY  -  24 NOVEMBER 2026", 2, GREY)

# ---------------------------------------------------------------- PNG encode
def png_chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return out


raw = bytearray()
for yy in range(H):
    raw.append(0)
    raw += buf[yy * W * 3:(yy + 1) * W * 3]
ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
png = (b"\x89PNG\r\n\x1a\n"
       + png_chunk(b"IHDR", ihdr)
       + png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
       + png_chunk(b"IEND", b""))

out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
os.makedirs(out_dir, exist_ok=True)
with open(os.path.join(out_dir, "entry.png"), "wb") as f:
    f.write(png)
print("wrote %d bytes" % len(png))
