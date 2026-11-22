#!/usr/bin/env python3
"""Sum up 22 November 2026's world news in one image.

Writes /output/entry.png (1024x1024 PNG, < 1 MiB). Deterministic:
no network, no clock, no randomness -- two runs produce identical bytes.
Pure standard library only (os, struct, zlib, math): the grader runs
the program with no packages installed, so nothing is imported that
is not in the standard library.

Draws a 1024x1024 newspaper-style poster for Sunday 22 November 2026
with a hand-made 5x7 bitmap font, simple drawing primitives, and a
hand-rolled PNG encoder (IHDR + IDAT + IEND).

Headlines verified 22 Nov 2026 via web search against several
independent aggregators (huddleworld citing Reuters, c54news.tv,
thepariseye.com, appistos.gr, news.cryptoeconomics.tech, japako.pl):
Iran strikes US assets in Bahrain; Russian strikes on Lviv and
Kryvyi Rih; EU-Indonesia trade deal signed; COP31 deadlock; Mexico
captures 'El Chapo Isidro'; Alcaraz vs Zverev in the ATP Finals.
See PROGRESS.md for the source list.
"""
import math
import os
import struct
import zlib

W, H = 1024, 1024
OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
OUT = os.path.join(OUT_DIR, "entry.png")

# ---------------------------------------------------------------- palette
PAPER = (246, 241, 227)   # off-white newsprint
NAVY = (10, 42, 94)
NAVY2 = (24, 52, 92)
GOLD = (201, 162, 39)
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
RED = (178, 34, 34)
DARKRED = (139, 0, 0)
GREY = (90, 96, 104)
DGREY = (60, 60, 60)
CARD = (255, 255, 255)
LINE = (205, 200, 190)
GREEN = (34, 120, 60)
TEAL = (0, 110, 110)
PALE_RED = (247, 232, 232)
PALE_RED_LINE = (220, 180, 180)
DARK_BG = (20, 20, 20)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 bits ('1' = ink). Hand-written classic 5x7
# pixel font. Text is normalised to upper case before drawing; only
# the glyphs below are needed.
FONT = {
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
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "~": ("00000", "00000", "01001", "10110", "00000", "00000", "00000"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    "|": ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "{": ("00110", "00100", "00100", "11100", "00100", "00100", "00110"),
    "}": ("01100", "00100", "00100", "00111", "00100", "00100", "01100"),
    "\\": ("10000", "01000", "01000", "00100", "00010", "00010", "00001"),
}


# ---------------------------------------------------------------- canvas
class Canvas:
    """An RGB pixel buffer with tiny drawing primitives."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg) * (w * h)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = color[0]
            self.px[i + 1] = color[1]
            self.px[i + 2] = color[2]

    def rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = yy * self.w * 3
            for xx in range(x0, x1):
                i = base + xx * 3
                self.px[i] = color[0]
                self.px[i + 1] = color[1]
                self.px[i + 2] = color[2]

    def hline(self, x, y, w, color):
        self.rect(x, y, w, 1, color)

    def vline(self, x, y, h, color):
        self.rect(x, y, 1, h, color)

    def line(self, x0, y0, x1, y1, color, width=1):
        """Bresenham line, with a square brush of the given width."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        half = width // 2
        while True:
            self.rect(x - half, y - half, width, width, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def disc(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, color)

    def ring(self, cx, cy, r, color, width=2):
        for yy in range(cy - r - 1, cy + r + 2):
            for xx in range(cx - r - 1, cx + r + 2):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if (r - width) ** 2 <= d2 <= r * r:
                    self.set(xx, yy, color)

    def rounded_rect(self, x, y, w, h, r, color, outline=None):
        self.rect(x + r, y, w - 2 * r, h, color)
        self.rect(x, y + r, w, h - 2 * r, color)
        for cx, cy in ((x + r, y + r), (x + w - r - 1, y + r),
                       (x + r, y + h - r - 1), (x + w - r - 1, y + h - r - 1)):
            self.disc(cx, cy, r, color)
        if outline is not None:
            self.hline(x + r, y, w - 2 * r, outline)
            self.hline(x + r, y + h - 1, w - 2 * r, outline)
            self.vline(x, y + r, h - 2 * r, outline)
            self.vline(x + w - 1, y + r, h - 2 * r, outline)

    # ---- text -----------------------------------------------------
    def text_width(self, text, scale):
        return len(self._normalise(text)) * 6 * scale - scale

    def _normalise(self, text):
        out = []
        for ch in text.upper():
            if ch in FONT:
                out.append(ch)
            elif ch in "—–":
                out.append("-")
            elif ch in "’‘":
                out.append("'")
            elif ch in "“”":
                out.append('"')
            elif ch == "•":
                out.append("*")
            elif ch == "é":
                out.append("E")
            elif ch == "ü":
                out.append("U")
            elif ch == "ö":
                out.append("O")
            elif ch == "ä":
                out.append("A")
            elif ch == "ñ":
                out.append("N")
            else:
                out.append(" ")
        return "".join(out)

    def draw_text(self, x, y, text, scale, color):
        """Draw text at top-left (x, y); glyphs are 5x7, scaled."""
        cx = x
        for ch in self._normalise(text):
            glyph = FONT.get(ch)
            if glyph is None:
                cx += 6 * scale
                continue
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += 6 * scale
        return cx

    def text_right(self, x, y, text, scale, color):
        self.draw_text(x - self.text_width(text, scale), y, text, scale,
                       color)

    def text_centre(self, cx, y, text, scale, color):
        self.draw_text(cx - self.text_width(text, scale) // 2, y, text,
                       scale, color)

    def wrap(self, text, scale, width):
        """Greedy word wrap to a pixel width; returns a list of lines."""
        lines, cur = [], ""
        for word in self._normalise(text).split(" "):
            trial = (cur + " " + word).strip()
            if self.text_width(trial, scale) <= width:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def draw_wrapped(self, x, y, text, scale, width, color, leading=None):
        leading = leading or int(7 * scale * 1.45)
        for line in self.wrap(text, scale, width):
            self.draw_text(x, y, line, scale, color)
            y += leading
        return y

    # ---- PNG ------------------------------------------------------
    def to_png(self):
        def chunk(kind, data):
            out = struct.pack(">I", len(data)) + kind + data
            out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
            return out

        ihdr = struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)
        raw = bytearray()
        for yy in range(self.h):
            raw.append(0)
            raw += self.px[yy * self.w * 3:(yy + 1) * self.w * 3]
        png = b"\x89PNG\r\n\x1a\n"
        png += chunk(b"IHDR", ihdr)
        png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        png += chunk(b"IEND", b"")
        return png


# ---------------------------------------------------------------- layout
def kicker(cv, x, y, text, color=RED):
    cv.draw_text(x, y, text, 2, color)
    return y + 22


def card(cv, x, y, w, h, fill=CARD):
    cv.rounded_rect(x, y, w, h, 10, fill, outline=LINE)
    return x + 22, y + 16


def story(cv, x, y, w, h, tag, headline, deck, accent=RED):
    """A half-width story card: kicker, headline, deck."""
    cx, cy = card(cv, x, y, w, h)
    cv.rect(x, y + 10, 6, h - 20, accent)
    cy = kicker(cv, cx, cy, tag, color=accent)
    cy = cv.draw_wrapped(cx, cy, headline, 3, w - 52, BLACK,
                         leading=30)
    cv.draw_wrapped(cx, cy + 6, deck, 2, w - 52, DGREY, leading=20)


def chip(cv, x, y, w, top, bottom):
    cv.rounded_rect(x, y, w, 52, 8, PALE_RED, outline=PALE_RED_LINE)
    cv.text_centre(x + w // 2, y + 7, top, 2, DARKRED)
    cv.text_centre(x + w // 2, y + 29, bottom, 2, (90, 40, 40))


def main():
    cv = Canvas(W, H, PAPER)

    # ---- Masthead -------------------------------------------------
    cv.rect(0, 0, W, 148, NAVY)
    cv.rect(0, 148, W, 6, GOLD)
    cv.draw_text(36, 26, "THE WORLD TODAY", 8, WHITE)
    cv.draw_text(36, 96, "SUNDAY  22  NOVEMBER  2026", 3, GOLD)
    cv.draw_text(36, 124, "THE DAY'S WORLD NEWS - IN ONE IMAGE", 2, (190, 200, 215))
    cv.text_right(W - 36, 96, "SUNDAY EDITION - ONE PAGE", 2, (190, 200, 215))
    cv.text_right(W - 36, 124, "22 NOV 2026 - $100 PRIZE", 2, (150, 165, 185))

    # ---- Lead story: Iran strikes Bahrain -------------------------
    lx, ly, lw, lh = 36, 170, 952, 264
    cv.rounded_rect(lx, ly, lw, lh, 10, CARD, outline=LINE)
    cv.rect(lx, ly, lw, 6, RED)
    tx, ty = lx + 24, ly + 20
    ty = kicker(cv, tx, ty, "MIDDLE EAST  -  LEAD STORY")
    ty = cv.draw_wrapped(tx, ty, "IRAN STRIKES US ASSETS IN BAHRAIN",
                         4, 590, BLACK, leading=38)
    ty = cv.draw_wrapped(tx, ty + 8,
                         "Missiles hit an industrial facility as air defences "
                         "intercept other attacks. Bahrain condemns the strikes.",
                         2, 590, (55, 55, 55), leading=21)
    chips = [("BAHRAIN", "FACILITY HIT"), ("IRAN", "BLAMED"),
             ("GULF", "ON ALERT")]
    cx = tx
    for top, bottom in chips:
        chip(cv, cx, ty + 10, 150, top, bottom)
        cx += 150 + 14

    # schematic Gulf panel (right of lead)
    mx, my, mw, mh = lx + 640, ly + 20, 288, 196
    cv.rounded_rect(mx, my, mw, mh, 8, NAVY2)
    cv.draw_text(mx + 14, my + 10, "THE GULF", 2, WHITE)
    cv.draw_text(mx + 14, my + 32, "IRAN", 2, GOLD)
    cv.disc(mx + 60, my + 92, 7, GOLD)
    cv.draw_text(mx + 76, my + 84, "TEHRAN", 2, WHITE)
    cv.disc(mx + 150, my + 130, 7, WHITE)
    cv.draw_text(mx + 166, my + 122, "BAHRAIN", 2, WHITE)
    cv.line(mx + 66, my + 96, mx + 144, my + 126, GOLD, width=3)
    for ang in range(0, 360, 45):
        x2 = mx + 150 + int(15 * math.cos(math.radians(ang)))
        y2 = my + 130 + int(15 * math.sin(math.radians(ang)))
        cv.line(mx + 150, my + 130, x2, y2, (255, 120, 90), width=2)
    cv.disc(mx + 150, my + 130, 4, (255, 80, 60))
    cv.draw_text(mx + 14, my + 158, "US 5TH FLEET BASED IN BAHRAIN", 1,
                 (200, 210, 225))

    # ---- Row 2: Ukraine + EU-Indonesia trade ----------------------
    story(cv, 36, 450, 468, 180, "WAR IN EUROPE",
          "RUSSIA HITS LVIV AND KRYVYI RIH",
          "At least two killed in Lviv; 58 hurt in Zelensky's home city, "
          "six of them children.", RED)
    story(cv, 520, 450, 468, 180, "TRADE  -  BRUSSELS / JAKARTA",
          "EU AND INDONESIA SIGN LANDMARK TRADE DEAL",
          "After ten years of talks, tariffs on 98.5% of goods to go in "
          "the bloc's biggest Asian pact.", NAVY2)

    # ---- Row 3: COP31 + Mexico ------------------------------------
    story(cv, 36, 646, 468, 180, "CLIMATE  -  COP31",
          "CLIMATE TALKS DEADLOCK AS SUMMIT RUNS OVER",
          "Nearly 200 nations split over fossil fuels and finance; "
          "the talks are extended into overtime.", GREEN)
    story(cv, 520, 646, 468, 180, "MEXICO  -  DRUG WAR",
          "MEXICO CAPTURES 'EL CHAPO ISIDRO'",
          "Top drug lord arrested in the latest in a string of "
          "high-profile busts.", RED)

    # ---- Also today ------------------------------------------------
    bx0, by0, bw0, bh0 = 36, 842, 952, 150
    cv.rounded_rect(bx0, by0, bw0, bh0, 10, (235, 233, 226), outline=LINE)
    cv.draw_text(bx0 + 18, by0 + 12, "ALSO TODAY", 2, RED)
    briefs = [
        "ALCARAZ FACES ZVEREV FOR THE ATP FINALS TITLE",
        "FOUR NATIONS TO ISRAEL: LET AID INTO FLOODED GAZA",
        "EISENKOT TAPPED TO FORM ISRAEL'S NEXT GOVERNMENT",
        "FRANCE: FOURTH WEEKEND OF COST-OF-LIVING PROTESTS",
    ]
    col_w = (bw0 - 36) // 2
    for i, b in enumerate(briefs):
        col = i // 2
        row = i % 2
        x = bx0 + 18 + col * col_w
        y = by0 + 42 + row * 52
        cv.draw_text(x, y, "*", 2, RED)
        cv.draw_wrapped(x + 16, y, b, 2, col_w - 40, (50, 50, 50),
                        leading=20)

    # ---- Footer ----------------------------------------------------
    cv.draw_text(36, 1000,
                 "SOURCES: REUTERS - BBC - AL JAZEERA - WASHINGTON POST - "
                 "EUROPEAN COMMISSION - 22 NOV 2026", 1, GREY)
    cv.text_right(W - 36, 1000, "THE WORLD TODAY", 1, GREY)

    os.makedirs(OUT_DIR, exist_ok=True)
    data = cv.to_png()
    with open(OUT, "wb") as f:
        f.write(data)
    print("Wrote %s (%dx%d, %d bytes)" % (OUT, W, H, len(data)))


if __name__ == "__main__":
    main()
