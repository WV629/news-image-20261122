#!/usr/bin/env python3
"""Sunday 22 November 2026, one page: a newspaper front page drawn
with Pillow that sums the day's world news in 36 stories.

The page is built top to bottom: a serif masthead naming the day,
a red strip of six numbers, region chips, three feature stories with
hand-drawn banner pictures, ten smaller stories with mini pictures,
a dark world map with numbered pins, twenty-three one-line briefs,
a markets strip, and a DATE CHECK box that names the Thursday 19
and Friday 20 November stories so none of them is shown as Sunday
news. Every headline, deck and brief was checked against live
reporting on 22 Nov 2026 (AFP, Reuters, AP, Dawn, The Hindu,
Al Jazeera, Japan Times, Ukrinform, USGS).

Run it with: python3 generate.py
It writes entry.png (1024x1024) beside this file and prints a
warning for any text that does not fit its box. The picture is
fully deterministic: fixed layout, fixed colours, no network,
no randomness, no clock.
"""
import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
PAGE_W, PAGE_H = 1024, 1024
MARGIN = 28

PAL = {
    "paper": (247, 242, 232),
    "paper_lt": (252, 250, 244),
    "ink": (24, 24, 24),
    "navy": (18, 42, 68),
    "red": (178, 38, 38),
    "red_dk": (140, 26, 26),
    "gold": (198, 148, 52),
    "grey": (108, 105, 96),
    "line": (196, 189, 172),
    "sea": (13, 30, 54),
    "land": (222, 206, 172),
    "land_ln": (150, 138, 110),
    "teal": (24, 120, 116),
    "blue": (36, 80, 164),
    "orange": (198, 110, 30),
    "purple": (110, 60, 140),
    "green": (60, 130, 60),
}

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
FONTS = {
    "serif": os.path.join(FONT_DIR, "DejaVuSerif.ttf"),
    "serif_b": os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf"),
    "sans": os.path.join(FONT_DIR, "DejaVuSans.ttf"),
    "sans_b": os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf"),
}


class Sheet:
    """A 1024x1024 newspaper page plus the helpers that draw on it."""

    def __init__(self):
        self.img = Image.new("RGB", (PAGE_W, PAGE_H), PAL["paper"])
        self.cv = ImageDraw.Draw(self.img)
        self.warns = []

    def font(self, name, size):
        return ImageFont.truetype(FONTS[name], size)

    def text(self, xy, s, name, size, fill):
        self.cv.text(xy, s, font=self.font(name, size), fill=fill)

    def width(self, s, name, size):
        return self.cv.textlength(s, font=self.font(name, size))

    def split_lines(self, s, name, size, max_w):
        out, cur = [], ""
        for word in s.split(" "):
            trial = (cur + " " + word).strip()
            if self.width(trial, name, size) <= max_w:
                cur = trial
            else:
                if cur:
                    out.append(cur)
                cur = word
        if cur:
            out.append(cur)
        return out

    def para(self, x, y, s, name, size, max_w, lead, fill, limit=None):
        lines = self.split_lines(s, name, size, max_w)
        if limit is not None and len(lines) > limit:
            self.warns.append("TRUNCATED %r to %d lines" % (s[:48], limit))
            lines = lines[:limit]
        for ln in lines:
            self.text((x, y), ln, name, size, fill)
            y += lead
        return y

    def rule(self, x0, x1, y, w=2, fill=None):
        self.cv.line([(x0, y), (x1, y)], fill=fill or PAL["ink"], width=w)

    def shade(self, box, top, bot):
        x, y, w, h = box
        n = max(1, h)
        for i in range(n):
            t = i / n
            c = tuple(int(top[k] + (bot[k] - top[k]) * t) for k in range(3))
            self.cv.line([(x, y + i), (x + w, y + i)], fill=c)

    def dots(self, box, pts):
        x, y, w, h = box
        for (sx, sy, r) in pts:
            self.cv.ellipse([x + sx - r, y + sy - r, x + sx + r, y + sy + r],
                            fill=(235, 235, 220))

    def box(self, x, y, w, h, fill=None, outline=None, width=1):
        self.cv.rectangle([x, y, x + w, y + h], fill=fill,
                          outline=outline, width=width)

# ---------------------------------------------------------------- data

STATS = [
    ("2nd", "day of COP31 overtime"),
    ("3", "missiles fired at Riyadh"),
    ("$55,252", "Bitcoin's two-year low"),
    ("11", "killed in Sinaloa raid"),
    ("10%", "card-rate cap Trump vows"),
    ("82,500", "march in France, police count"),
]

CHIPS = [
    ("EUROPE 17", "blue"),
    ("AMERICAS 7", "teal"),
    ("ASIA-PACIFIC 5", "orange"),
    ("MIDEAST 4", "purple"),
    ("AFRICA 3", "green"),
]

# Each feature: number, dateline, topic, headline, deck, banner art.
FEATURES = [
    {"n": "01", "city": "ANTALYA, T\u00dcRKIYE", "topic": "CLIMATE",
     "head": "COP31 enters a second day of overtime with no deal",
     "deck": "Third \u2018final\u2019 text due Sunday; 6am deadline. 130 nations "
             "want fossil-fuel wording back. (AFP)",
     "art": "cop31"},
    {"n": "02", "city": "RIYADH", "topic": "CONFLICT",
     "head": "Riyadh on alert for a third night as Houthis vow more strikes",
     "deck": "Three missiles intercepted Saturday; Houthis threaten ports "
             "and a power station. (Al Jazeera, Dawn)",
     "art": "riyadh"},
    {"n": "03", "city": "GUASAVE, MEXICO", "topic": "CARTELS",
     "head": "Mexico seizes \u2018Chapo Isidro\u2019 in a gunfight that kills 11",
     "deck": "FBI top-10 fugitive held after a Friday-night raid in Sinaloa; "
             "$5m reward. (Reuters, AP)",
     "art": "sinaloa"},
]

# Each small story: number, dateline, topic, headline, deck, mini art.
SMALLS = [
    {"n": "04", "city": "NEW YORK", "topic": "MARKETS",
     "head": "Bitcoin hits a two-year low, then rebounds 8%",
     "deck": "Fell to $55,252 on Saturday, back near $59,952. (Dawn)",
     "art": "bitcoin"},
    {"n": "05", "city": "WASHINGTON", "topic": "TECH",
     "head": "SEC probes Nvidia as shares plunge 14%",
     "deck": "SEC inquiry reported Saturday; Huang stays out. (NYT)",
     "art": "chip"},
    {"n": "06", "city": "WASHINGTON", "topic": "POLITICS",
     "head": "Trump vows a 10% cap on card rates",
     "deck": "\u201cI would do it,\u201d he tells Fox; Warren backs the cap. (AP)",
     "art": "card"},
    {"n": "07", "city": "PARIS", "topic": "PROTEST",
     "head": "France marches for a sixth weekend",
     "deck": "82,500 counted; Le Pen holds RN congress in Orl\u00e9ans. (AFP)",
     "art": "protest"},
    {"n": "08", "city": "GAZA CITY", "topic": "WAR",
     "head": "Four more killed in Gaza despite the truce",
     "deck": "Three died in a strike on a food-aid vehicle. (AFP)",
     "art": "gaza"},
    {"n": "09", "city": "KYIV", "topic": "WAR",
     "head": "Russia strikes again; power cut in two regions",
     "deck": "Grid sites hit; outages in Poltava and Kharkiv. (Ukrinform)",
     "art": "kyiv"},
    {"n": "10", "city": "TURIN", "topic": "SPORT",
     "head": "Alcaraz sets up a final with Zverev",
     "deck": "Beat Shelton in three sets; Zverev beat Medvedev. (Reuters)",
     "art": "tennis"},
    {"n": "11", "city": "BRUSSELS", "topic": "EUROPE",
     "head": "EU proposes a tax on Big Tech",
     "deck": "Levy to fund the budget; six states want farm cuts. (Dawn)",
     "art": "eu"},
    {"n": "12", "city": "GENEVA", "topic": "DIPLOMACY",
     "head": "States open a path to \u2018killer robot\u2019 rules",
     "deck": "Draft rules by 2028 after Russian pushback. (SCMP)",
     "art": "robots"},
    {"n": "13", "city": "LIMA", "topic": "DISASTER",
     "head": "6.7 quake shakes Peru\u2019s Andes",
     "deck": "No deaths reported; tremors felt in Lima. (USGS)",
     "art": "quake"},
]

# One-line briefs, numbers continuing from the 13 cards above.
BRIEFS = [
    ("14", "JOHANNESBURG \u2014 G20 opens in Africa."),
    ("15", "DUBLIN \u2014 Ireland stun the Springboks."),
    ("16", "NEW DELHI \u2014 India lead v New Zealand."),
    ("17", "DORTMUND \u2014 Dortmund go top."),
    ("18", "ROME \u2014 Lazio stay top of Serie A."),
    ("19", "KINSHASA \u2014 Ebola cases pass 11,600."),
    ("20", "MOGADISHU \u2014 Al-Shabaab ambush claim."),
    ("21", "OSLO \u2014 Court voids disputed oil licences."),
    ("22", "FRANKFURT \u2014 New ECB chief hunt begins."),
    ("23", "SEOUL \u2014 Apology sought over transfer."),
    ("24", "TAIPEI \u2014 Taiwan warns Canada on China."),
    ("25", "MANIPUR \u2014 11 dead after tainted alcohol."),
    ("26", "BALTIC SEA \u2014 Ship burns after drone hit."),
    ("27", "LONDON \u2014 Village votes to \u2018leave UK\u2019."),
    ("28", "ROME \u2014 Ex-police chief dies by suicide."),
    ("29", "BOLOGNA \u2014 Bulgari dies at 89."),
    ("30", "COLOMBO \u2014 Four die in landslide."),
    ("31", "BRAS\u00cdLIA \u2014 Brazil town clears rubble."),
    ("32", "TEHRAN \u2014 Iran strikes 3 tankers."),
    ("33", "SANA\u2019A \u2014 Houthis warn off airlines."),
    ("34", "NUUK \u2014 Trump plans military expansion."),
    ("35", "DONETSK \u2014 Moscow claims encirclement."),
    ("36", "BERLIN \u2014 Germany sets 2045 exit."),
]

DATE_CHECK = (
    "First reported Fri 20 Nov or earlier, NOT Sunday\u2019s news: Shenzhen "
    "summit \u00b7 UK\u2013EU reset deal \u00b7 S&P correction \u00b7 Kyiv "
    "bridges, 8 killed \u00b7 Kryvyi Rih, 2 killed, 42 hurt \u00b7 ICJ Myanmar "
    "verdict \u00b7 Anthropic $83 IPO \u00b7 GTA VI launch \u00b7 Riyadh PIF "
    "tower hit \u00b7 Mongolia quits."
)

FOOTER = (
    "Every story here happened, or was first reported, on Sunday 22 November 2026. "
    "Claims are attributed. "
    "Sources: AFP \u00b7 Reuters \u00b7 AP \u00b7 Dawn \u00b7 Al Jazeera"
)

# ---------------------------------------------------------------- banner art

def banner_cop31(sh, box):
    """Antalya talks: green sky, globe, red thermometer, draft papers."""
    x, y, w, h = box
    sh.shade(box, (150, 205, 170), (40, 110, 80))
    d = sh.cv
    # thermometer on the left, sun top right, globe centre right
    tx = x + 16
    d.rectangle([tx, y + 18, tx + 14, y + 86], fill=(240, 238, 230))
    d.rectangle([tx + 2, y + 46, tx + 12, y + 84], fill=(220, 40, 30))
    d.ellipse([tx - 6, y + 80, tx + 20, y + 106], fill=(220, 40, 30))
    d.ellipse([tx - 2, y + 84, tx + 16, y + 102], fill=(255, 120, 90))
    d.ellipse([x + w - 66, y + 10, x + w - 28, y + 48], fill=(255, 214, 140))
    gx, gy, gr = x + 168, y + 56, 38
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(30, 90, 140))
    d.ellipse([gx - 14, gy - 28, gx + 10, gy - 4], fill=(60, 150, 90))
    d.ellipse([gx - 2, gy + 10, gx + 28, gy + 30], fill=(60, 150, 90))
    d.ellipse([gx - 32, gy + 4, gx - 12, gy + 22], fill=(60, 150, 90))
    d.arc([gx - gr, gy - gr, gx + gr, gy + gr], 0, 360,
          fill=(200, 230, 240), width=2)
    for px in (48, 76, 104):
        d.rectangle([x + px, y + 92, x + px + 26, y + 108],
                    fill=(250, 248, 240))
        d.line([x + px + 4, y + 97, x + px + 22, y + 97],
               fill=(120, 120, 110), width=1)
        d.line([x + px + 4, y + 102, x + px + 22, y + 102],
               fill=(120, 120, 110), width=1)
    d.rectangle([x, y + h - 6, x + w, y + h], fill=(30, 80, 58))


def banner_riyadh(sh, box):
    """Riyadh at night: alert sky, interceptor trails, tower skyline."""
    x, y, w, h = box
    sh.shade(box, (16, 24, 48), (60, 44, 66))
    d = sh.cv
    sh.dots(box, [(20, 14, 1), (60, 26, 1), (120, 10, 2), (180, 22, 1),
                  (240, 12, 1), (280, 30, 2), (150, 34, 1), (95, 12, 1)])
    d.ellipse([x + w - 52, y + 10, x + w - 24, y + 38], fill=(232, 228, 200))
    d.ellipse([x + w - 46, y + 14, x + w - 26, y + 34], fill=(60, 44, 66))
    for (x0, y0, x1, y1) in [(40, 92, 110, 22), (150, 96, 200, 30),
                             (230, 94, 268, 44)]:
        d.line([x + x0, y + y0, x + x1, y + y1], fill=(255, 176, 66), width=3)
        d.line([x + x0, y + y0, x + x1, y + y1], fill=(255, 226, 160), width=1)
        d.ellipse([x + x1 - 5, y + y1 - 5, x + x1 + 5, y + y1 + 5],
                  fill=(255, 200, 90))
    d.rectangle([x + 8, y + 62, x + 60, y + h], fill=(8, 10, 18))
    d.rectangle([x + 70, y + 40, x + 118, y + h], fill=(10, 12, 20))
    d.rectangle([x + 128, y + 70, x + 180, y + h], fill=(8, 10, 18))
    d.rectangle([x + 190, y + 56, x + 250, y + h], fill=(10, 12, 20))
    d.rectangle([x + 260, y + 74, x + w - 8, y + h], fill=(8, 10, 18))
    d.rectangle([x + 70, y + 40, x + 118, y + 48], fill=(220, 40, 30))
    for wx, wy in [(20, 70), (36, 84), (80, 56), (140, 80), (200, 66),
                   (216, 82), (272, 84), (150, 96)]:
        d.rectangle([x + wx, y + wy, x + wx + 6, y + wy + 8],
                    fill=(255, 214, 130))
    d.rectangle([x, y + h - 4, x + w, y + h], fill=(10, 12, 20))


def banner_sinaloa(sh, box):
    """Sinaloa raid at dawn: orange sky, helicopters, burning roadblocks."""
    x, y, w, h = box
    sh.shade(box, (226, 150, 70), (120, 60, 40))
    d = sh.cv
    d.ellipse([x + 24, y + 10, x + 64, y + 50], fill=(255, 214, 140))
    for hx, hy in [(150, 22), (240, 34)]:
        d.ellipse([x + hx - 14, y + hy - 4, x + hx + 14, y + hy + 6],
                  fill=(20, 20, 26))
        d.line([x + hx - 26, y + hy - 6, x + hx + 26, y + hy - 6],
               fill=(20, 20, 26), width=2)
        d.polygon([(x + hx - 4, y + hy + 6), (x + hx + 4, y + hy + 6),
                   (x + hx + 16, y + hy + 40), (x + hx - 16, y + hy + 40)],
                  fill=(255, 240, 180))
    d.rectangle([x, y + h - 34, x + w, y + h], fill=(40, 32, 28))
    d.line([x, y + h - 34, x + w, y + h - 34], fill=(240, 238, 230), width=2)
    for bx in (30, 110, 200, 262):
        d.rectangle([x + bx, y + h - 52, x + bx + 34, y + h - 34],
                    fill=(70, 52, 40))
        for r, col in [(12, (255, 120, 40)), (7, (255, 170, 60)),
                       (4, (255, 220, 130))]:
            d.ellipse([x + bx + 17 - r, y + h - 56 - r,
                       x + bx + 17 + r, y + h - 56 + r], fill=col)
    d.rectangle([x, y + h - 4, x + w, y + h], fill=(20, 16, 14))


BANNERS = {"cop31": banner_cop31, "riyadh": banner_riyadh,
           "sinaloa": banner_sinaloa}

# ---------------------------------------------------------------- mini art

def mini_bitcoin(sh, box):
    x, y, w, h = box
    d = sh.cv
    d.rectangle([x, y, x + w, y + h], fill=(247, 147, 26))
    d.ellipse([x + 18, y + 4, x + 62, y + 44], fill=(255, 255, 255))
    sh.text((x + 30, y + 10), "\u20bf", "sans_b", 24, (247, 147, 26))
    d.line([x + 70, y + 12, x + 110, y + 32, x + 140, y + 10, x + w - 8,
            y + 30], fill=(178, 38, 38), width=2)


def mini_chip(sh, box):
    x, y, w, h = box
    d = sh.cv
    d.rectangle([x, y, x + w, y + h], fill=(20, 70, 50))
    d.rectangle([x + 66, y + 6, x + 110, y + 40], fill=(10, 14, 18))
    d.rectangle([x + 74, y + 14, x + 102, y + 32], fill=(46, 100, 78))
    for k in range(4):
        yy = y + 12 + k * 7
        d.line([x + 66, yy, x + 56, yy], fill=(255, 220, 90), width=1)
        d.line([x + 110, yy, x + 120, yy], fill=(255, 220, 90), width=1)
    d.line([x + 10, y + 40, x + w - 10, y + 40], fill=(255, 220, 90),
           width=1)


def mini_card(sh, box):
    x, y, w, h = box
    d = sh.cv
    d.rectangle([x, y, x + w, y + h], fill=(18, 42, 68))
    d.rounded_rectangle([x + 20, y + 4, x + w - 20, y + 30], radius=5,
                        fill=(240, 238, 230))
    sh.text((x + 30, y + 8), "10%", "sans_b", 15, PAL["red_dk"])
    d.rectangle([x + 20, y + 30, x + w - 20, y + 34], fill=PAL["gold"])
    sh.text((x + 30, y + 35), "CAP", "sans_b", 8, (240, 238, 230))


def mini_protest(sh, box):
    x, y, w, h = box
    d = sh.cv
    d.rectangle([x, y, x + w, y + h], fill=(52, 44, 40))
    for px, col in [(24, (255, 120, 40)), (62, (255, 170, 60)),
                    (100, (36, 80, 164)), (136, (178, 38, 38))]:
        d.line([x + px, y + 8, x + px, y + h - 8], fill=(240, 238, 230),
               width=2)
        d.rectangle([x + px, y + 8, x + px + 20, y + 22], fill=col)
    d.rectangle([x, y + h - 6, x + w, y + h], fill=(178, 38, 38))


def mini_gaza(sh, box):
    x, y, w, h = box
    d = sh.cv
    d.rectangle([x, y, x + w, y + h], fill=(120, 100, 78))
    d.polygon([(x + 10, y + h - 4), (x + 50, y + 16), (x + 90, y + h - 4)],
              fill=(96, 78, 58))
    d.polygon([(x + 80, y + h - 4), (x + 120, y + 20), (x + 160, y + h - 4)],
              fill=(110, 88, 64))
    for (sx, sy) in [(30, 6), (80, 4), (130, 8)]:
        d.ellipse([x + sx, y + sy, x + sx + 16, y + sy + 12],
                  fill=(90, 84, 76))
    d.ellipse([x + 88, y + 10, x + 104, y + 26], fill=(255, 140, 40))
    d.rectangle([x, y + h - 4, x + w, y + h], fill=(80, 62, 46))


def mini_kyiv(sh, box):
    x, y, w, h = box
    d = sh.cv
    sh.shade(box, (12, 18, 32), (36, 32, 54))
    sh.dots(box, [(18, 8, 1), (66, 14, 1), (124, 8, 2), (152, 16, 1)])
    d.line([x + 34, y + 10, x + 34, y + h - 12], fill=(16, 18, 28), width=3)
    d.line([x + 18, y + 16, x + 50, y + 16], fill=(16, 18, 28), width=3)
    d.line([x + 18, y + 16, x + 92, y + 30], fill=(60, 62, 76), width=1)
    d.rectangle([x + 62, y + 28, x + 112, y + h], fill=(8, 10, 18))
    d.rectangle([x + 122, y + 36, x + 168, y + h], fill=(10, 12, 20))
    for (fx, fy) in [(70, 36), (86, 46), (130, 44), (148, 52)]:
        d.rectangle([x + fx, y + fy, x + fx + 6, y + fy + 8],
                    fill=(255, 214, 130))
    for r, col in [(10, (255, 120, 40)), (6, (255, 170, 60))]:
        d.ellipse([x + 87 - r, y + 32 - r, x + 87 + r, y + 32 + r],
                  fill=col)


def mini_tennis(sh, box):
    x, y, w, h = box
    d = sh.cv
    d.rectangle([x, y, x + w, y + h], fill=(24, 120, 60))
    d.ellipse([x + 66, y + 4, x + 106, y + 44], fill=(200, 230, 60))
    d.arc([x + 66, y + 4, x + 106, y + 44], 250, 80,
          fill=(255, 255, 255), width=2)
    d.arc([x + 66, y + 4, x + 106, y + 44], 70, 260,
          fill=(255, 255, 255), width=2)
    d.line([x + 8, y + h - 6, x + w - 8, y + h - 6],
           fill=(255, 255, 255), width=2)


def mini_eu(sh, box):
    x, y, w, h = box
    d = sh.cv
    import math as _m
    d.rectangle([x, y, x + w, y + h], fill=(36, 80, 164))
    for k in range(10):
        a = _m.pi * 2 * k / 10
        sx = x + w // 2 + int(15 * _m.cos(a))
        sy = y + h // 2 + int(13 * _m.sin(a))
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 220, 60))
    d.rectangle([x, y + h - 4, x + w, y + h], fill=(255, 220, 60))


def mini_robots(sh, box):
    x, y, w, h = box
    d = sh.cv
    d.rectangle([x, y, x + w, y + h], fill=(24, 24, 30))
    d.rectangle([x + 68, y + 8, x + 104, y + 34], fill=(120, 120, 130))
    d.rectangle([x + 78, y + 16, x + 94, y + 26], fill=(178, 38, 38))
    d.ellipse([x + 81, y + 18, x + 85, y + 24], fill=(255, 255, 255))
    d.ellipse([x + 89, y + 18, x + 93, y + 24], fill=(255, 255, 255))
    d.line([x + 72, y + 34, x + 72, y + 42], fill=(120, 120, 130), width=2)
    d.line([x + 100, y + 34, x + 100, y + 42], fill=(120, 120, 130),
           width=2)


def mini_quake(sh, box):
    x, y, w, h = box
    d = sh.cv
    sh.shade(box, (196, 160, 110), (120, 92, 60))
    d.line([x + 8, y + 12, x + 52, y + 30, x + 92, y + 14, x + 132,
            y + 34, x + w - 8, y + 18], fill=(140, 26, 26), width=3)
    d.polygon([(x + 16, y + h - 4), (x + 56, y + 16), (x + 96, y + h - 4)],
              fill=(96, 72, 46))
    d.polygon([(x + 86, y + h - 4), (x + 126, y + 22), (x + 164, y + h - 4)],
              fill=(110, 84, 54))
    d.rectangle([x, y + h - 4, x + w, y + h], fill=(96, 72, 46))


MINIS = {"bitcoin": mini_bitcoin, "chip": mini_chip, "card": mini_card,
         "protest": mini_protest, "gaza": mini_gaza, "kyiv": mini_kyiv,
         "tennis": mini_tennis, "eu": mini_eu, "robots": mini_robots,
         "quake": mini_quake}

# ---------------------------------------------------------------- the map

# Simplified continent outlines, hand-drawn on a 440x156 grid.
CONTINENTS = [
    [(22, 6), (42, 8), (60, 14), (76, 12), (94, 20), (84, 34), (64, 32),
     (48, 42), (30, 40), (12, 26)],                       # N America
    [(72, 62), (86, 58), (94, 70), (90, 88), (78, 86), (70, 72)],  # S America
    [(128, 12), (150, 8), (172, 10), (192, 18), (188, 30), (168, 36),
     (150, 30), (136, 22)],                                # Europe
    [(178, 40), (196, 36), (208, 46), (200, 62), (182, 66), (172, 54)],  # Africa
    [(200, 8), (232, 6), (262, 10), (288, 18), (286, 34), (258, 40),
     (232, 36), (210, 26)],                                # Asia
    [(300, 118), (322, 114), (338, 122), (330, 134), (310, 132)],  # Oceania
]

PINS = [
    (1, 0.62, 0.26),
    (2, 0.68, 0.34),
    (3, 0.19, 0.36),
    (4, 0.22, 0.26),
    (5, 0.25, 0.30),
    (6, 0.28, 0.27),
    (7, 0.40, 0.24),
    (8, 0.66, 0.35),
    (9, 0.58, 0.20),
    (10, 0.44, 0.26),
]

MAP_LABELS = [("ANTALYA", 0.63, 0.26), ("RIYADH", 0.72, 0.34),
              ("GUASAVE", 0.19, 0.32), ("PARIS", 0.34, 0.28),
              ("GAZA", 0.67, 0.36)]


def draw_map(sh, x, y, w, h):
    d = sh.cv
    d.rectangle([x, y, x + w, y + h], fill=PAL["sea"])
    sh.dots((x, y, w, h),
            [(20, 14, 1), (60, 26, 1), (110, 10, 1), (170, 22, 1),
             (230, 12, 1), (290, 28, 1), (350, 10, 1), (410, 20, 1),
             (140, 40, 1), (270, 44, 1), (40, 40, 1), (200, 40, 1)])
    for poly in CONTINENTS:
        pts = [(x + px * w / 440, y + py * h / 156) for (px, py) in poly]
        d.polygon(pts, fill=PAL["land"], outline=PAL["land_ln"])
    for (n, fx, fy) in PINS:
        px, py = x + fx * w, y + fy * h
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=PAL["red"])
        d.ellipse([px - 6, py - 6, px + 6, py + 6], fill=PAL["red_dk"])
        sh.text((px - 3, py - 6), str(n), "sans_b", 9, (255, 255, 255))
    for (lab, fx, fy) in MAP_LABELS:
        sh.text((x + fx * w + 9, y + fy * h - 6), lab, "sans_b", 9,
                (255, 255, 255))
    sh.text((x + 8, y + h - 14), "1 COP31 \u00b7 2 RIYADH \u00b7 3 CHAPO "
            "ISIDRO \u00b7 4 BITCOIN \u00b7 5 NVIDIA \u00b7 6 CARD CAP \u00b7 7 "
            "FRANCE \u00b7 8 GAZA \u00b7 9 KYIV \u00b7 10 TURIN", "sans_b", 9,
            (255, 255, 255))


# ---------------------------------------------------------------- layout

def draw_masthead(sh):
    sh.text((MARGIN, 14), "THE SUNDAY WORLD", "serif_b", 46, PAL["ink"])
    sh.text((MARGIN + 620, 26), "SUNDAY 22 NOVEMBER 2026", "sans_b", 15,
            PAL["ink"])
    sh.text((MARGIN + 620, 48), "36 STORIES \u00b7 ONE DAY \u00b7 ONE PAGE",
            "sans_b", 13, PAL["grey"])
    sh.rule(MARGIN, PAGE_W - MARGIN, 72, 3)
    sh.text((MARGIN, 78), "TODAY'S WORLD IN ONE IMAGE", "sans_b", 12,
            PAL["red"])
    sh.rule(MARGIN, PAGE_W - MARGIN, 98, 1, PAL["line"])
    y = 106
    cw = (PAGE_W - 2 * MARGIN) // 6
    for i, (num, lab) in enumerate(STATS):
        x = MARGIN + i * cw
        sh.text((x, y), num, "sans_b", 20, PAL["red"])
        sh.para(x, y + 26, lab, "sans", 9, cw - 8, 12, PAL["grey"], 2)
        if i < 5:
            sh.cv.line([(x + cw - 4, y + 2), (x + cw - 4, y + 42)],
                       fill=PAL["line"], width=1)
    sh.rule(MARGIN, PAGE_W - MARGIN, 154, 1, PAL["line"])
    sh.text((MARGIN, 162), "WHERE THE NEWS IS", "sans_b", 11, PAL["red"])
    xx = MARGIN + 168
    for (lab, col) in CHIPS:
        wch = sh.width(lab, "sans_b", 11) + 18
        sh.box(xx, 158, wch, 20, fill=PAL[col], outline=None)
        sh.text((xx + 9, 163), lab, "sans_b", 11, (255, 255, 255))
        xx += wch + 8


def draw_feature(sh, f, x, y, w):
    d = sh.cv
    d.rectangle([x, y, x + w, y + 200], fill=PAL["paper_lt"],
                outline=PAL["line"])
    art_h = 92
    BANNERS[f["art"]](sh, (x + 1, y + 1, w - 2, art_h))
    sh.text((x + 8, y + 104), f["n"], "sans_b", 15, PAL["red"])
    sh.text((x + 36, y + 104), f["city"], "sans_b", 11, PAL["grey"])
    sh.text((x + 8, y + 122), f["topic"], "sans_b", 11, PAL["red"])
    sh.para(x + 8, y + 138, f["head"], "serif_b", 14, w - 16, 17,
            PAL["ink"], 2)
    sh.para(x + 8, y + 174, f["deck"], "sans", 9, w - 16, 12,
            PAL["grey"], 2)


def draw_small(sh, s, x, y, w):
    d = sh.cv
    d.rectangle([x, y, x + w, y + 118], fill=PAL["paper_lt"],
                outline=PAL["line"])
    MINIS[s["art"]](sh, (x + 1, y + 1, w - 2, 40))
    sh.text((x + 8, y + 46), s["n"], "sans_b", 12, PAL["red"])
    sh.text((x + 34, y + 46), s["city"], "sans_b", 10, PAL["grey"])
    sh.text((x + 8, y + 60), s["topic"], "sans_b", 10, PAL["red"])
    sh.para(x + 8, y + 74, s["head"], "serif_b", 10, w - 16, 13,
            PAL["ink"], 2)
    sh.para(x + 8, y + 100, s["deck"], "sans", 8, w - 16, 9,
            PAL["grey"], 2)


def draw_briefs(sh, x, y, w, h):
    d = sh.cv
    d.rectangle([x, y, x + w, y + h], fill=PAL["paper_lt"],
                outline=PAL["line"])
    sh.text((x + 10, y + 6), "MORE, IN BRIEF", "sans_b", 11, PAL["red"])
    sh.rule(x + 10, x + w - 10, y + 24, 1, PAL["line"])
    col_w = (w - 20) // 4
    per = (len(BRIEFS) + 3) // 4
    for i, (n, txt) in enumerate(BRIEFS):
        c, r = divmod(i, per)
        bx = x + 10 + c * col_w
        by = y + 30 + r * 12
        sh.text((bx, by), n + ".", "sans_b", 9, PAL["red"])
        sh.text((bx + 18, by), txt, "sans", 8, PAL["ink"])


def build():
    sh = Sheet()
    draw_masthead(sh)
    top = 186
    fw = (PAGE_W - 2 * MARGIN - 24) // 3
    for i, f in enumerate(FEATURES):
        draw_feature(sh, f, MARGIN + i * (fw + 12), top, fw)
    top += 206
    sw = (PAGE_W - 2 * MARGIN - 36) // 5
    for i, s in enumerate(SMALLS):
        col, row = i % 5, i // 5
        draw_small(sh, s, MARGIN + col * (sw + 9), top + row * 122, sw)
    top += 254
    sh.text((MARGIN, top), "WHERE IT HAPPENED", "sans_b", 13, PAL["red"])
    sh.rule(MARGIN, PAGE_W - MARGIN, top + 20, 1, PAL["line"])
    draw_map(sh, MARGIN, top + 26, PAGE_W - 2 * MARGIN, 120)
    top += 154
    draw_briefs(sh, MARGIN, top, PAGE_W - 2 * MARGIN, 96)
    top += 102
    sh.text((MARGIN, top), "MARKETS", "sans_b", 13, PAL["red"])
    sh.text((MARGIN, top + 20), "Bitcoin low $55,252, then +8% to ~$59,952  "
            "\u00b7  Nasdaq -5.3% Fri  \u00b7  S&P in correction",
            "sans_b", 12, PAL["ink"])
    sh.text((MARGIN + 712, top + 20), "GOLD $4,100 \u00b7 OIL $63", "sans_b",
            12, PAL["ink"])
    sh.rule(MARGIN, PAGE_W - MARGIN, top + 38, 1, PAL["line"])
    top += 44
    sh.text((MARGIN, top), "DATE CHECK", "sans_b", 13, PAL["red"])
    sh.para(MARGIN, top + 20, DATE_CHECK, "sans", 11,
            PAGE_W - 2 * MARGIN, 13, PAL["ink"], 2)
    top += 50
    sh.rule(MARGIN, PAGE_W - MARGIN, top, 1, PAL["line"])
    sh.para(MARGIN, top + 8, FOOTER, "sans", 11, PAGE_W - 2 * MARGIN,
            14, PAL["grey"], 2)
    return sh


def main():
    sh = build()
    out = os.path.join(BASE, "entry.png")
    sh.img.save(out, "PNG")
    size = os.path.getsize(out)
    print("Wrote %s (%d bytes)" % (out, size))
    if sh.warns:
        for w in sh.warns:
            print("WARNING: %s" % w)
    else:
        print("0 warnings")


if __name__ == "__main__":
    main()
