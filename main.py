#!/usr/bin/env python3
"""news-image-20261126 — Sum up 26 November 2026's world news in one image.

Fresh build for make.fun bounty news-image-20261126 ($100, free entry).
Python 3.13 stdlib only: hand-rolled zlib/struct PNG encoder + self-defined
5x7 bitmap font. No network, fully deterministic — every run writes the
same bytes. Writes entry.png (1024x1024) to MAKEFUN_OUTPUT_DIR or /output.
Layout (proven newspaper form): navy masthead, red lead banner on the
Ras Tanura refinery strike, 15 pictured stories in a 5x3 grid with flat
pictograms, dotted world map with numbered dots + key, by-the-numbers strip,
20 listed stories below — 35 stories total, all from stories.md.
"""
import os
import struct
import zlib

W, H = 1024, 1024

# ---- palette ------------------------------------------------------------
CREAM = (246, 239, 221)   # page
PAPER = (238, 230, 205)   # strip / panel
NAVY = (20, 38, 74)       # masthead, ink
INK = (28, 28, 32)        # body text
RED = (179, 39, 30)       # lead accent, numbered dots
GOLD = (186, 138, 12)     # rules, accents
TEAL = (31, 110, 107)
GREY = (122, 114, 96)     # faint map dots
RULE = (196, 184, 154)    # hairlines
WHITE = (255, 255, 255)
SOFT = (232, 224, 198)    # cell panel
BLUE = (52, 84, 138)      # pictogram blue
GREEN = (46, 125, 62)
ORANGE = (214, 106, 24)

# ---- 5x7 bitmap font (self-defined, uppercase + digits + punctuation) --
def _g(*rows):
    return [int(r.replace("#", "1").replace(".", "0"), 2) if set(r) <= set("01#.")
            else None for r in rows]

FONT = {}
_glyphs = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "~": ("00000", "00000", "00000", "01001", "10110", "00000", "00000"),
}
for _ch, _rows in _glyphs.items():
    FONT[_ch] = [int(r, 2) for r in _rows]

def clean(s):
    """Uppercase + map anything outside the font to a safe ASCII form."""
    s = (s.replace("\u2019", "'").replace("\u2018", "'")
          .replace("\u201c", '"').replace("\u201d", '"')
          .replace("\u2014", "-").replace("\u2013", "-")
          .replace("\u00d7", "X").replace("\u2026", "...")
          .replace("\u2022", "-").replace("\u00a0", " "))
    out = []
    for ch in s.upper():
        out.append(ch if ch in FONT else ("-" if ch in "\u2010\u2011" else "?"))
    return "".join(out)

# ---- canvas ----------------------------------------------------------------
buf = bytearray(W * H * 3)

def fill_bg(color):
    r, g, b = color
    buf[0::3] = bytes([r]) * (W * H)
    buf[1::3] = bytes([g]) * (W * H)
    buf[2::3] = bytes([b]) * (W * H)

def px(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i], buf[i + 1], buf[i + 2] = color

def rect(x, y, w, h, color):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    r, g, b = color
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        n = x1 - x0
        buf[base:base + n * 3:3] = bytes([r]) * n
        buf[base + 1:base + 1 + n * 3:3] = bytes([g]) * n
        buf[base + 2:base + 2 + n * 3:3] = bytes([b]) * n

def hline(x, y, w, color, t=1):
    rect(x, y, w, t, color)

def vline(x, y, h, color, t=1):
    rect(x, y, t, h, color)

def line(x0, y0, x1, y1, color):
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        px(x0, y0, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

def thick_line(x0, y0, x1, y1, color, t=2):
    line(x0, y0, x1, y1, color)
    if t > 1:
        line(x0 + 1, y0, x1 + 1, y1, color)
        line(x0, y0 + 1, x1, y1 + 1, color)

def circle(cx, cy, r, color, fill=True):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            d = (xx - cx) ** 2 + (yy - cy) ** 2
            if fill:
                if d <= r * r:
                    px(xx, yy, color)
            else:
                if r * r - 2 * r <= d <= r * r:
                    px(xx, yy, color)

def triangle(x0, y0, x1, y1, x2, y2, color):
    minx, maxx = min(x0, x1, x2), max(x0, x1, x2)
    miny, maxy = min(y0, y1, y2), max(y0, y1, y2)
    def sign(ax, ay, bx, by, cx, cy):
        return (ax - cx) * (by - cy) - (bx - cx) * (ay - cy)
    d = sign(x0, y0, x1, y1, x2, y2)
    if d == 0:
        return
    for yy in range(miny, maxy + 1):
        for xx in range(minx, maxx + 1):
            s1 = sign(xx, yy, x0, y0, x1, y1)
            s2 = sign(xx, yy, x1, y1, x2, y2)
            s3 = sign(xx, yy, x2, y2, x0, y0)
            if (d > 0 and s1 >= 0 and s2 >= 0 and s3 >= 0) or \
               (d < 0 and s1 <= 0 and s2 <= 0 and s3 <= 0):
                px(xx, yy, color)

# ---- text ------------------------------------------------------------------
def text_w(s, scale):
    return len(s) * 6 * scale

def draw_text(x, y, s, scale, color):
    s = clean(s)
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT["?"])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits & (1 << (4 - col)):
                    rect(cx + col * scale, y + row * scale, scale, scale, color)
        cx += 6 * scale
    return cx

def wrap(s, width_chars):
    s = clean(s)
    parts = []
    for w in s.split(" "):
        # split over-long hyphenated words at the hyphen so headlines
        # never break mid-word (e.g. AUSTRALIA- / SOLOMONS)
        while "-" in w and len(w) > width_chars:
            i = w.index("-")
            parts.append(w[:i + 1])
            w = w[i + 1:]
        parts.append(w)
    lines, cur = [], ""
    for w in parts:
        while len(w) > width_chars:
            lines.append(w[:width_chars])
            w = w[width_chars:]
        if not cur:
            cur = w
        elif len(cur) + 1 + len(w) <= width_chars:
            cur += " " + w
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

# ---- PNG encoder (zlib/struct, filter 0, RGB) ------------------------------
def write_png(path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += buf[y * W * 3:(y + 1) * W * 3]
    comp = zlib.compress(bytes(raw), 6)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        c += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return c

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

# ---- flat pictograms (drawn in a cx,cy-centred box, ~56x30) ----------------
def pic_fire(cx, cy):
    triangle(cx - 16, cy + 12, cx, cy - 14, cx + 16, cy + 12, RED)
    triangle(cx - 9, cy + 12, cx, cy - 4, cx + 9, cy + 12, ORANGE)
    triangle(cx - 4, cy + 12, cx, cy + 2, cx + 4, cy + 12, GOLD)

def pic_chart(cx, cy, up):
    rect(cx - 24, cy + 12, 48, 2, INK)
    rect(cx - 24, cy - 12, 2, 24, INK)
    pts = [(cx - 20, cy + 6), (cx - 10, cy - 2), (cx, cy + 4),
           (cx + 10, cy - 8), (cx + 20, cy - 12)] if up else \
          [(cx - 20, cy - 10), (cx - 10, cy - 2), (cx, cy - 6),
           (cx + 10, cy + 4), (cx + 20, cy + 10)]
    for a, b in zip(pts, pts[1:]):
        thick_line(a[0], a[1], b[0], b[1], RED if not up else TEAL, 2)
    for p in pts:
        circle(p[0], p[1], 2, NAVY)

def pic_missile(cx, cy):
    thick_line(cx - 20, cy + 10, cx + 16, cy - 10, NAVY, 3)
    triangle(cx + 16, cy - 10, cx + 24, cy - 6, cx + 12, cy - 2, RED)
    triangle(cx - 8, cy + 2, cx - 14, cy + 12, cx - 2, cy + 8, NAVY)
    circle(cx + 18, cy - 7, 2, GOLD)

def pic_shield(cx, cy):
    pts = [(cx - 14, cy - 12), (cx + 14, cy - 12), (cx + 14, cy + 2),
           (cx, cy + 14), (cx - 14, cy + 2)]
    for a, b in zip(pts, pts[1:] + [pts[0]]):
        thick_line(a[0], a[1], b[0], b[1], TEAL, 2)
    thick_line(cx - 7, cy, cx - 2, cy + 5, TEAL, 2)
    thick_line(cx - 2, cy + 5, cx + 8, cy - 6, TEAL, 2)

def pic_rocket(cx, cy):
    triangle(cx, cy - 14, cx - 7, cy + 2, cx + 7, cy + 2, NAVY)
    rect(cx - 7, cy + 2, 14, 10, NAVY)
    triangle(cx - 7, cy + 2, cx - 13, cy + 10, cx - 7, cy + 10, RED)
    triangle(cx + 7, cy + 2, cx + 13, cy + 10, cx + 7, cy + 10, RED)
    circle(cx, cy + 1, 3, WHITE)
    triangle(cx - 3, cy + 12, cx + 3, cy + 12, cx, cy + 18, ORANGE)

def pic_plane(cx, cy):
    rect(cx - 24, cy - 2, 46, 5, NAVY)
    triangle(cx + 22, cy - 2, cx + 28, cy, cx + 22, cy + 3, NAVY)
    triangle(cx - 4, cy - 2, cx - 12, cy - 12, cx - 2, cy - 2, NAVY)
    triangle(cx - 2, cy + 3, cx - 10, cy + 12, cx, cy + 3, NAVY)
    rect(cx - 18, cy - 2, 4, 5, WHITE)
    rect(cx - 10, cy - 2, 4, 5, WHITE)

def pic_football(cx, cy):
    circle(cx, cy, 13, WHITE)
    circle(cx, cy, 13, INK, fill=False)
    circle(cx, cy, 4, INK)
    for dx, dy in [(-10, -6), (10, -6), (-11, 6), (11, 6), (0, 11)]:
        circle(cx + dx, cy + dy, 2, INK)

def pic_ball(cx, cy):
    circle(cx, cy, 13, RED)
    circle(cx, cy, 13, INK, fill=False)
    for t in range(-2, 3):
        px(cx - 11 + t * 4, cy - 6 + abs(t), WHITE)
        px(cx - 11 + t * 4, cy + 6 - abs(t), WHITE)
    rect(cx - 2, cy - 13, 4, 4, WHITE)

def pic_lock(cx, cy):
    rect(cx - 5, cy - 10, 10, 4, GOLD)
    rect(cx - 12, cy - 6, 24, 18, NAVY)
    circle(cx, cy + 3, 3, GOLD)
    rect(cx - 1, cy + 3, 2, 6, GOLD)

def pic_candle(cx, cy):
    rect(cx - 4, cy - 2, 8, 16, NAVY)
    rect(cx - 6, cy + 12, 12, 3, GOLD)
    triangle(cx - 4, cy - 4, cx, cy - 14, cx + 4, cy - 4, ORANGE)
    triangle(cx - 2, cy - 4, cx, cy - 9, cx + 2, cy - 4, GOLD)

PICS = {
    "fire": pic_fire,
    "chart-down": lambda cx, cy: pic_chart(cx, cy, False),
    "missile": pic_missile,
    "shield": pic_shield,
    "rocket": pic_rocket,
    "plane": pic_plane,
    "football": pic_football,
    "ball": pic_ball,
    "chart-up": lambda cx, cy: pic_chart(cx, cy, True),
    "lock": pic_lock,
    "candle": pic_candle,
}

CAT_COLOR = [NAVY, RED, GOLD, TEAL, BLUE, GREEN]

# ---- story data (from stories.md, 26 Nov 2026) ----------------------------
LEAD_HEAD = "HOUTHIS HIT SAUDI'S BIGGEST REFINERY"
LEAD_SUM = ("HOUTHIS CLAIM A STRIKE ON THE 550,000-BPD RAS TANURA REFINERY; "
            "NASA SEES SMOKE OVER ~600 SQ KM; BRENT $93.60, UP 2.4%; "
            "COALITION DOWNED 4 DRONES. (REUTERS)")

# (headline, summary, lon, lat, pictogram)
PICTURED = [
    ("HOUTHIS HIT SAUDI'S BIGGEST REFINERY",
     "Houthis claim a strike on the 550,000-bpd Ras Tanura refinery; NASA images show smoke over ~600 sq km; Brent $93.60, up 2.4%. (Reuters)",
     50.2, 26.6, "fire"),
    ("US TARIFFS HIT 14 NATIONS",
     "Trump administration proposes new tariffs on 14 trading partners, highest on China; S&P futures -2.1%, Nasdaq -3.1%. (Reuters)",
     -77.0, 38.9, "chart-down"),
    ("RUSSIA HITS ODESA AND KYIV",
     "Fresh escalation as Russian attacks strike the Ukrainian cities Odesa and Kyiv, casualties reported. (Reuters)",
     30.7, 46.5, "missile"),
    ("GAZA STRIKE KILLS HAMAS CHIEF",
     "Israeli strike kills a Hamas internal security chief, Gaza ministry says; ceasefire under strain. (Reuters)",
     34.5, 31.5, "missile"),
    ("COLOMBIA FREES HOSTAGES",
     "Authorities free hostages in a Cartagena supermarket siege. (Reuters)",
     -75.5, 10.4, "shield"),
    ("SHENZHOU-24 LIFTS OFF",
     "China launches Shenzhou-24 with Pakistani astronaut Muhammad Zeeshan Ali, the first foreigner aboard Tiangong station. (Reuters)",
     100.3, 40.9, "rocket"),
    ("AUSTRALIA-SOLOMONS PACT",
     "Australia and Solomon Islands sign a new security treaty. (Reuters)",
     160.0, -9.6, "shield"),
    ("CAIRO TANKER FIRE KILLS 30",
     "Fuel tanker crash ignites a huge fire on Cairo's ring highway; at least 30 killed. (Reuters)",
     31.2, 30.0, "fire"),
    ("PLANE CRASH KILLS 6 OFF MISSISSIPPI",
     "Two children among six dead after a plane crashes off the Mississippi coast. (AP)",
     -89.0, 30.2, "plane"),
    ("LILLE STUN BAYERN 2-1",
     "Lille beat Bayern 2-1; Liverpool rout Brugge 3-0 with an Isak brace; Man Utd draw 2-2 at Sporting. (UEFA)",
     3.1, 50.6, "football"),
    ("SOORYAVANSHI SMASHES 204",
     "15-year-old Vaibhav Sooryavanshi hits 204 off 53 balls, the fastest List A double century, with a 28-ball hundred vs UAE. (BCCI)",
     51.5, 25.3, "ball"),
    ("IPL AUCTION DRAWS 1,220",
     "A total of 1,220 cricketers register for the IPL 2027 auction. (BCCI)",
     72.9, 19.1, "chart-up"),
    ("MI5 WARNS DEFENCE BOSSES",
     "MI5 warns UK defence chiefs of a Russian sabotage threat. (Reports)",
     -0.1, 51.5, "lock"),
    ("BANGLADESH RAISES GARMENT PAY 36%",
     "Minimum wage for garment workers up 36%. (Reuters)",
     90.4, 23.8, "chart-up"),
    ("INDIA MARKS 26/11",
     "18th anniversary of the Mumbai attacks, 160+ dead; Constitution Day observed. (Reuters)",
     72.9, 19.1, "candle"),
]

LISTED = [
    "Houthis claim attacks on Jeddah and Jizan ports; Jazan hit, no injuries. (Reuters/ISW)",
    "Qatar F1 Grand Prix goes ahead this weekend despite war; strikes hit Bahrain. (Reuters)",
    "Sudan drone strikes kill 19 civilians. (Reports)",
    "China urges Netherlands to offer fair business climate in Nexperia chip dispute. (Reuters)",
    "UK RAF moves aircraft to hangars at night over possible drone threats. (Sky News)",
    "India says 'cockroach' movement leader Das was told not to use his passport. (Reuters)",
    "AI metals meltdown: LME index down 15% in November; copper, tin, silver hit. (Reuters)",
    "Poundland preparing for administration, Sky News reports. (Reuters)",
    "Malaysia sues Google for $146M over YouTube content. (Reports)",
    "Indonesia gold mine flooding kills nine miners. (Reports)",
    "Lebanon plans a second airport at Kleiat. (Reports)",
    "WHO: 25 polio cases in Afghanistan in 2026. (WHO)",
    "Fed policymakers at odds over causes of high inflation. (Reuters)",
    "Flipkart CEO Kalyan Krishnamurthy to step down in December. (Reuters)",
    "Indian banks write off Rs 1.44 lakh crore in bad loans in FY26. (Reuters)",
    "Sheikh Hasina seeks return to Bangladesh on 16 December. (Reports)",
    "Brazil: Wolbachia mosquitoes cut viral infections 68%. (Reports)",
    "Duran Duran guitarist Andy Taylor dies at 65. (Reports)",
    "Asteroid defence test images reveal a new crater. (Reports)",
    "Gukesh draws game 2 of the World Chess Championship in 20 moves vs Sindarov. (FIDE)",
]

NUMBERS = [
    ("550,000", "BPD RAS TANURA OUTPUT"),
    ("600", "SQ KM OF SMOKE"),
    ("$93.60", "BRENT CRUDE"),
    ("36%", "GARMENT PAY RISE"),
    ("204", "OFF 53 BALLS, AGE 15"),
]

# coarse land boxes (lon_min, lon_max, lat_min, lat_max) for the dotted map
LAND = [
    (-168, -52, 15, 71), (-58, -20, 60, 83), (-80, -34, -56, 12),
    (-11, 40, 36, 70), (-18, 52, -35, 36), (40, 180, 5, 76),
    (95, 141, -11, 6), (113, 154, -40, -11), (166, 178, -47, -34),
]

# ---- layout ----------------------------------------------------------------
def draw_masthead():
    hline(24, 14, 976, NAVY, 3)
    t = "THE WORLD TODAY"
    draw_text((W - text_w(t, 5)) // 2, 20, t, 5, NAVY)
    s = "THURSDAY 26 NOVEMBER 2026"
    draw_text((W - text_w(s, 2)) // 2, 60, s, 2, INK)
    draw_text(24, 60, "NO. 331", 1, GREY)
    r = "PRICE: ONE DAY"
    draw_text(1000 - text_w(r, 1), 60, r, 1, GREY)
    hline(24, 80, 976, NAVY, 3)
    hline(24, 85, 976, GOLD, 1)

def draw_lead():
    rect(24, 92, 976, 76, NAVY)
    rect(24, 92, 976, 4, RED)
    draw_text(40, 102, LEAD_HEAD, 3, WHITE)
    lines = wrap(LEAD_SUM, 80)
    y = 128
    for ln in lines[:2]:
        draw_text(40, y, ln, 2, (226, 220, 196))
        y += 16
    tag = "LEAD"
    draw_text(1000 - text_w(tag, 1) - 16, 102, tag, 1, GOLD)

def draw_grid():
    x0, y0 = 26, 176
    cw, ch, gap = 188, 146, 8
    for idx, (head, summ, lon, lat, pic) in enumerate(PICTURED):
        col, row = idx % 5, idx // 5
        x = x0 + col * (cw + gap)
        y = y0 + row * (ch + 4)
        rect(x, y, cw, ch, SOFT)
        hline(x, y, cw, CAT_COLOR[idx % len(CAT_COLOR)], 4)
        # number badge
        circle(x + 14, y + 16, 10, NAVY)
        num = str(idx + 1)
        draw_text(x + 14 - text_w(num, 1) // 2, y + 13, num, 1, WHITE)
        # pictogram
        PICS[pic](x + cw // 2, y + 38)
        # headline, up to 3 lines at scale 2 (15 chars/line, 1px leading)
        hl = wrap(head, 15)
        yy = y + 58
        for ln in hl[:3]:
            draw_text(x + 8, yy, ln, 2, NAVY)
            yy += 15
        # summary, up to 5 lines at scale 1 (30 chars/line, 1px leading)
        sl = wrap(summ, 30)
        yy = y + 104
        for ln in sl[:5]:
            draw_text(x + 8, yy, ln, 1, INK)
            yy += 8

def draw_map():
    mx, my, mw, mh = 24, 656, 640, 130
    draw_text(mx, 634, "WHERE IT HAPPENED", 2, NAVY)
    hline(mx, 652, mw, RULE, 1)
    # graticule
    for lon in range(-150, 181, 30):
        gx = mx + int((lon + 180) / 360.0 * mw)
        for yy in range(my, my + mh):
            if yy % 4 == 0:
                px(gx, yy, RULE)
    for lat in range(-60, 91, 30):
        gy = my + int((90 - lat) / 150.0 * mh)
        for xx in range(mx, mx + mw):
            if xx % 4 == 0:
                px(xx, gy, RULE)
    # dotted land, 3-degree lon / 6-degree lat step (even dotted texture)
    lon = -180
    while lon <= 180:
        lat = -57
        while lat <= 84:
            on_land = any(a <= lon <= b and c <= lat <= d for a, b, c, d in LAND)
            if on_land:
                dx = mx + int((lon + 180) / 360.0 * mw)
                dy = my + int((90 - lat) / 150.0 * mh)
                rect(dx, dy, 2, 2, GREY)
            lat += 6
        lon += 3
    # numbered story dots: true point + badge, leader-displaced where
    # true points collide (Middle East cluster, UK/Lille, twin Mumbai)
    offsets = {1: (0, 0), 2: (0, -8), 3: (0, -14), 4: (16, 14), 5: (0, 0),
               6: (0, 0), 7: (0, 0), 8: (-16, 12), 9: (0, 0), 10: (14, 8),
               11: (16, 12), 12: (-16, -10), 13: (-16, -10), 14: (0, 0),
               15: (16, 10)}
    for idx, (head, summ, slon, slat, pic) in enumerate(PICTURED):
        dx = mx + int((slon + 180) / 360.0 * mw)
        dy = my + int((90 - slat) / 150.0 * mh)
        ox, oy = offsets[idx + 1]
        bx, by = dx + ox, dy + oy
        if ox or oy:
            line(dx, dy, bx, by, RED)
        rect(dx - 1, dy - 1, 3, 3, RED)
        circle(bx, by, 9, RED)
        circle(bx, by, 9, WHITE, fill=False)
        num = str(idx + 1)
        draw_text(bx - text_w(num, 1) // 2, by - 3, num, 1, WHITE)
    # map key / legend
    kx = 684
    draw_text(kx, 634, "MAP KEY", 2, NAVY)
    hline(kx, 652, 316, RULE, 1)
    yy = 660
    for idx, (head, summ, lon, lat, pic) in enumerate(PICTURED):
        num = str(idx + 1)
        draw_text(kx, yy + 1, num, 1, RED)
        short = clean(head)
        if len(short) > 42:
            short = short[:39] + "..."
        draw_text(kx + 20, yy + 1, short, 1, INK)
        yy += 8
    draw_text(kx, yy + 4, "RED DOTS: THE 15 PICTURED STORIES", 1, GREY)

def draw_numbers():
    y = 794
    rect(24, y, 976, 52, PAPER)
    hline(24, y, 976, NAVY, 2)
    hline(24, y + 50, 976, NAVY, 2)
    colw = 976 // 5
    for i, (big, label) in enumerate(NUMBERS):
        x = 24 + i * colw
        if i:
            vline(x, y + 6, 40, RULE, 1)
        draw_text(x + (colw - text_w(big, 3)) // 2, y + 8, big, 3, RED if i == 2 else NAVY)
        draw_text(x + (colw - text_w(label, 1)) // 2, y + 34, label, 1, INK)

def draw_listed():
    y = 856
    draw_text(24, y, "ALSO TODAY", 2, NAVY)
    hline(24, y + 16, 976, RULE, 1)
    cols = [LISTED[i::3] for i in range(3)]
    colw = 976 // 3
    for ci, items in enumerate(cols):
        x = 24 + ci * colw
        yy = y + 24
        for j, item in enumerate(items):
            n = str(16 + ci + j * 3)
            draw_text(x, yy, n + ".", 1, RED)
            lines = wrap(item, 46)
            ly = yy
            for ln in lines[:2]:
                draw_text(x + 24, ly, ln, 1, INK)
                ly += 8
            yy += 18

def grain():
    """Deterministic paper grain — adds texture and PNG entropy."""
    for y in range(H):
        row = y * W * 3
        for x in range(W):
            h = (x * 374761393 + y * 668265263) & 0xFFFFFFFF
            h ^= (h >> 13) & 0xFFFFFFFF
            h = (h * 1274126177) & 0xFFFFFFFF
            if h % 97 < 5:
                i = row + x * 3
                d = 5 if (h >> 7) & 1 else -5
                for k in range(3):
                    v = buf[i + k] + d
                    buf[i + k] = 255 if v > 255 else (0 if v < 0 else v)

def main():
    fill_bg(CREAM)
    draw_masthead()
    draw_lead()
    draw_grid()
    draw_map()
    draw_numbers()
    draw_listed()
    hline(24, 1012, 976, NAVY, 2)
    draw_text(24, 1016, "THE WORLD TODAY - THURSDAY 26 NOVEMBER 2026 - 35 STORIES",
              1, GREY)
    grain()
    out = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    path = os.path.join(out, "entry.png")
    size = write_png(path)
    print("wrote", path, size, "bytes")

if __name__ == "__main__":
    main()
