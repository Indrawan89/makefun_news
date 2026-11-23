#!/usr/bin/env python3
"""THE WORLD TODAY - Sunday 22 November 2026.

A one-page newspaper poster generator. Pure Python standard library:
hand-drawn 5x7 bitmap glyphs, a bytearray canvas, and a from-scratch
PNG encoder (zlib + CRC32). No third-party packages, no network, no
randomness - two runs produce byte-identical output.

Run:  python3 main.py
Writes: output/entry.png  (1024x1024, deterministic)
"""

import os
import struct
import sys
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------------------
# 5x7 bitmap glyphs, drawn by hand for this poster.
# Each glyph is 7 rows of 5 cells; '#' is ink, '.' is empty.
# ---------------------------------------------------------------------------
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "%": ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..##", "#..##"),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "&": (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
}


# ---------------------------------------------------------------------------
# Palette (my own choices).
# ---------------------------------------------------------------------------
PAPER = (247, 241, 222)   # warm newsprint
INK = (26, 26, 26)        # near-black text
NAVY = (27, 42, 94)       # masthead + heat panel
GOLD = (201, 162, 39)     # masthead rule + date
RED = (176, 30, 40)       # lead red
WHITE = (255, 254, 247)
CHIP = (243, 217, 217)    # pale pink chip fill
PANEL = (238, 238, 238)   # "Also today" grey panel
HAIR = (200, 192, 172)    # hairline rules
TEAL = (0, 122, 110)
GREEN = (34, 122, 44)
OCHRE = (176, 132, 16)
PURPLE = (110, 66, 160)
GREY_TXT = (90, 86, 76)

# ---------------------------------------------------------------------------
# Canvas: a flat RGB bytearray with small drawing helpers.
# ---------------------------------------------------------------------------
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(w * h * 3)
        r, g, b = bg
        for i in range(0, len(self.px), 3):
            self.px[i] = r
            self.px[i + 1] = g
            self.px[i + 2] = b

    def dot(self, x, y, col):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = col

    def box(self, x, y, w, h, col):
        for yy in range(y, y + h):
            base = (yy * self.w + x) * 3
            for xx in range(w):
                j = base + xx * 3
                if 0 <= x + xx < self.w and 0 <= yy < self.h:
                    self.px[j], self.px[j + 1], self.px[j + 2] = col

    def disc(self, cx, cy, r, col):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.dot(xx, yy, col)

    def glyph(self, x, y, ch, scale, col):
        rows = FONT[ch]
        for r in range(7):
            line = rows[r]
            for c in range(5):
                if line[c] == "#":
                    self.box(x + c * scale, y + r * scale, scale, scale, col)

    def text(self, x, y, s, scale, col):
        s = s.upper()
        for ch in s:
            if ch not in FONT:
                raise ValueError("glyph missing: %r" % ch)
            self.glyph(x, y, ch, scale, col)
            x += 6 * scale
        return x

    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale

    def text_right(self, right, y, s, scale, col):
        self.text(right - self.text_w(s, scale), y, s, scale, col)

    def text_center(self, cx, y, s, scale, col):
        self.text(cx - self.text_w(s, scale) // 2, y, s, scale, col)


# ---------------------------------------------------------------------------
# PNG encoder, written from the format itself: signature, IHDR, one IDAT
# (zlib stream of filter-0 scanlines), IEND. No ancillary chunks, so the
# output is fully deterministic.
# ---------------------------------------------------------------------------
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def save_png(path, cv):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    blob = (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + _chunk(b"IEND", b"")
    )
    with open(path, "wb") as f:
        f.write(blob)


# ---------------------------------------------------------------------------
# Content: 33 dated stories from Sunday 22 November 2026.
# Each story is (headline, deck). Headlines render at scale 2, decks at 1.
# ---------------------------------------------------------------------------
LEAD_HEAD = "COP31 FAILS - NO DEAL"
LEAD_DECK = (
    "NEARLY 200 NATIONS LEAVE ANTALYA WITH NO CLIMATE",
    "PACT. THE FINAL TEXT NEVER MENTIONS FOSSIL FUELS.",
    "THE EU WALKS OUT. GUTERRES: DEEPLY DISAPPOINTED.",
)
LEAD_CHIPS = (("2 DAYS", "OVERTIME"), ("$120BN", "DROPPED"), ("200", "NATIONS"))

# (section title, swatch colour, [stories])
COLUMNS_LEFT = [
    ("EUROPE", RED, [
        ("RUSSIA FIRES 186 DRONES AT UKRAINE", "161 DOWNED; HITS AT 18 SITES"),
        ("DRONE HITS FLATS NEAR KYIV", "3 KILLED IN DYMER; 14 FEARED BURIED"),
        ("MISSILE HITS KRYVYI RIH", "BOY, 7, AMONG 2 KILLED; 60 HURT"),
        ("RUSSIAN MISSILES LAND IN POLAND", "2 MISSILES DOWN; NATO PROTESTS"),
        ("EU AND INDONESIA SIGN TRADE DEAL", "TARIFFS ON 98.5% OF GOODS TO GO"),
    ]),
    ("MIDDLE EAST", NAVY, [
        ("IRAN STRIKES US ASSETS IN BAHRAIN", "2 HURT; IRAN CLAIMS RADAR KILLS"),
        ("HORMUZ TANKERS HIT BY STRIKES", "3 TANKERS STRUCK NEAR THE STRAIT"),
        ("ISRAEL TOLD: LET AID INTO GAZA", "4 NATIONS DEMAND GAZA AID ACCESS"),
        ("EISENKOT TAPPED TO FORM GOVERNMENT", "OPPOSITION LEADER TO BUILD COALITION"),
    ]),
    ("ASIA", TEAL, [
        ("HONG KONG VOTES; TURNOUT 98.79%", "5,640 VOTE IN COMMITTEE POLLS"),
        ("WORLD COURT: MYANMAR GENOCIDE", "ROHINGYA RULING, FIRST OF ITS KIND"),
        ("FACTORY FIRE KILLS 3 IN CIKANDE", "34 MISSING AS RESCUERS DIG ON"),
        ("THAI COURT UPHOLDS MP TERM", "SENTENCE CUT TO 3 YEARS"),
    ]),
    ("AMERICAS", GREEN, [
        ("EL CHAPO ISIDRO CAPTURED", "11 DEAD IN SINALOA RAID"),
        ("TRUMP, PUTIN, XI MEET IN SHENZHEN", "JOINT DECLARATION; NO ARMS LIMITS"),
        ("ICE RAIDS SPARK GILROY PROTEST", "AGENTS SEIZE 2 AT SEATTLE AIRPORT"),
        ("ARMY TO BLAST LEAD CHEMICALS", "COURT ORDER SET ASIDE IN IOWA"),
    ]),
]

COLUMNS_RIGHT = [
    ("AFRICA", RED, [
        ("BOAT CAPSIZES IN NIGERIA, 24 DEAD", "MOURNERS DROWNED EN ROUTE TO FUNERAL"),
        ("24 CIVILIANS KILLED IN SOUTH SUDAN", "VIOLENCE IN WARRAP STATE"),
        ("KENYA AND DRC RESTORE TIES", "DEAL STRUCK AT OYO SUMMIT"),
        ("MLAMBO-NGCUKA DIES AT 71", "EX-SA DEPUTY PRESIDENT HONOURED"),
    ]),
    ("OCEANIA", OCHRE, [
        ("US-CHINA POWER GAP NARROWS", "LOWY: US LEAD IN ASIA SHRINKS"),
        ("AUSTRALIA WIN WOMEN'S RUGBY CROWN", "34-10 OVER NEW ZEALAND"),
        ("CYCLONE XAVIER FADES NEAR SAMOA", "WEAKENING STORM DRIFTS WEST"),
    ]),
    ("SPORT / TECH", PURPLE, [
        ("ALCARAZ WINS ATP FINALS CROWN", "6-2, 7-6 OVER ZVEREV IN TURIN"),
        ("VERSTAPPEN WINS LAS VEGAS THRILLER", "0.639S OVER NORRIS; 33 LEAD CHANGES"),
        ("INDIA POST RECORD 720/9D", "HIGHEST TEST TOTAL IN NEW ZEALAND"),
        ("NVIDIA FACES US PROBE ON CHINA CHIPS", "BESSENT DEMANDS ANSWERS ON SALES"),
    ]),
]

ALSO_TODAY = [
    ("FRANCE: COST-OF-LIVING PROTESTS", "FOURTH WEEKEND OF MARCHES"),
    ("AI SELL-OFF HITS WORLD MARKETS", "S&P -3.7%; NASDAQ -5.3% TODAY"),
    ("RUSSIAN CARGO SHIP ABLAZE", "FIRE IN BALTIC AFTER DRONE STRIKE"),
    ("SETTLERS TORCH WEST BANK HOMES", "12 VEHICLES BURNED IN NIGHT RAIDS"),
]

FOOTER_LEFT = "SOURCES: REUTERS - BBC - AP - AFP - THE HINDU - YONHAP - 22 NOV 2026"
FOOTER_RIGHT = "THE WORLD TODAY - 33 STORIES"


# ---------------------------------------------------------------------------
# Layout.
# ---------------------------------------------------------------------------
MARGIN = 24
COL_W = 478
LEFT_X = MARGIN
RIGHT_X = 522
ROW_H = 33          # one story: headline (14) + deck (7) + gaps
HEAD_H = 24         # region header block height


def draw_masthead(cv):
    cv.box(0, 0, W, 88, NAVY)
    cv.text(MARGIN, 16, "THE WORLD TODAY", 6, WHITE)
    cv.text(MARGIN, 66, "SUNDAY 22 NOVEMBER 2026", 2, GOLD)
    cv.text_right(1000, 18, "33 DATED STORIES - 7 REGIONS", 2, WHITE)
    cv.text_right(1000, 44, "THE DAY'S WORLD NEWS IN ONE IMAGE", 2, WHITE)
    cv.box(0, 88, W, 4, GOLD)


def draw_lead(cv):
    px, py, pw, ph = MARGIN, 100, 976, 196
    cv.box(px, py, pw, ph, WHITE)
    cv.box(px, py, pw, 5, RED)
    cv.text(px + 20, py + 16, "CLIMATE - LEAD STORY", 2, RED)
    cv.text(px + 20, py + 42, LEAD_HEAD, 4, INK)
    y = py + 76
    for line in LEAD_DECK:
        cv.text(px + 20, y, line, 2, INK)
        y += 20
    # fact chips, two lines each
    chip_w, chip_h, gap = 148, 42, 12
    cy = py + 144
    for i, (a, b) in enumerate(LEAD_CHIPS):
        cx = px + 20 + i * (chip_w + gap)
        cv.box(cx, cy, chip_w, chip_h, CHIP)
        cv.text_center(cx + chip_w // 2, cy + 5, a, 2, RED)
        cv.text_center(cx + chip_w // 2, cy + 23, b, 2, RED)
    # heat panel: thermometer + caption
    hx, hy, hw, hh = 700, 112, 276, 172
    cv.box(hx, hy, hw, hh, NAVY)
    cv.text(hx + 16, hy + 12, "THE HEAT", 2, WHITE)
    cv.text(hx + 16, hy + 34, "1.5C LIMIT", 2, GOLD)
    # tube and bulb
    tx, ty, tw, th = hx + 24, hy + 56, 14, 88
    cv.box(tx, ty, tw, th, WHITE)
    cv.box(tx + 2, ty + 34, tw - 4, th - 36, RED)
    cv.disc(tx + tw // 2, ty + th + 8, 12, RED)
    cv.disc(tx + tw // 2, ty + th + 8, 7, (255, 90, 90))
    cap = ["WORLD SET", "TO BREACH", "THE LIMIT", "FIRST TIME"]
    for i, line in enumerate(cap):
        col = GOLD if line == "THE LIMIT" else WHITE
        cv.text(hx + 52, hy + 60 + i * 22, line, 2, col)


def draw_section(cv, x, y, title, swatch, stories):
    cv.box(x, y + 2, 10, 10, swatch)
    cv.text(x + 16, y, title, 2, swatch)
    cv.box(x, y + 20, COL_W, 1, HAIR)
    y += HEAD_H
    for head, deck in stories:
        cv.box(x, y + 3, 7, 7, swatch)
        cv.text(x + 14, y, head, 2, INK)
        cv.text(x + 14, y + 18, deck, 1, GREY_TXT)
        y += ROW_H
    return y


def draw_also(cv, x, y):
    inner = len(ALSO_TODAY) * ROW_H + HEAD_H + 24
    cv.box(x - 12, y - 8, COL_W + 24, inner, PANEL)
    cv.text(x, y, "ALSO TODAY", 2, RED)
    cv.box(x, y + 20, COL_W, 1, HAIR)
    y += HEAD_H
    for head, deck in ALSO_TODAY:
        cv.box(x, y + 3, 7, 7, RED)
        cv.text(x + 14, y, head, 2, INK)
        cv.text(x + 14, y + 18, deck, 1, GREY_TXT)
        y += ROW_H
    return y + 16


def draw_footer(cv):
    cv.box(MARGIN, 992, W - 2 * MARGIN, 1, HAIR)
    cv.text(MARGIN, 1002, FOOTER_LEFT, 1, GREY_TXT)
    cv.text_right(1000, 1002, FOOTER_RIGHT, 1, GREY_TXT)


def build():
    cv = Canvas(W, H, PAPER)
    draw_masthead(cv)
    draw_lead(cv)
    y = 312
    for title, swatch, stories in COLUMNS_LEFT:
        y = draw_section(cv, LEFT_X, y, title, swatch, stories)
    y = 312
    for title, swatch, stories in COLUMNS_RIGHT:
        y = draw_section(cv, RIGHT_X, y, title, swatch, stories)
    draw_also(cv, RIGHT_X, y)
    draw_footer(cv)
    return cv


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(here, "output")
    os.makedirs(out_dir, exist_ok=True)
    save_png(os.path.join(out_dir, "entry.png"), build())
    print("wrote output/entry.png")


if __name__ == "__main__":
    main()
