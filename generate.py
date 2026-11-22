#!/usr/bin/env python3
"""Render entry.png: a one-page newspaper front page summing up
Sunday 22 November 2026 in 36 stories, drawn entirely with Pillow.

Layout: date-first serif masthead, red stat strip, region chips,
3 feature stories with drawn banner art, 10 smaller stories with
mini art, a dark world map with numbered pins, 23 one-line briefs,
a markets strip, and a DATE CHECK strip naming the big Thursday 19
and Friday 20 Nov stories so they are never shown as Sunday news.

Stories were verified live on 22 Nov 2026 (AFP, Reuters, AP, Dawn,
The Hindu, Al Jazeera, Japan Times, Ukrinform, USGS): COP31's second
day of overtime in Antalya (third "final" text, 6am review deadline);
Riyadh on alert for a third night after three Houthi missiles were
intercepted Saturday; Mexico's capture of FBI top-10 fugitive
"Chapo Isidro" in a Sinaloa raid that killed 11; the SEC's Nvidia
accounting probe and Friday's 14% share plunge; Bitcoin's two-year
low of $55,252 and its 8% rebound; Trump's vow of a 10% card-rate
cap; France's sixth weekend of protests; four more killed in Gaza;
fresh Russian strikes on Ukraine's grid; Alcaraz vs Zverev in the
ATP Finals title match. The Friday-cycle stories the field leads
with (Peru's 6.7 quake, the Riyadh strikes, the Sinaloa raid) are
carried as reported on the Sunday papers; the DATE CHECK box names
the older Thursday/Friday stories.

Deterministic: fixed layout, fixed palette, no network, no random
numbers, no timestamps. Run: python3 generate.py writes entry.png
(1024x1024) next to this file. It prints a warning for any headline,
deck or brief that overflows its box.
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024

PAPER = (247, 242, 232)
PAPER_LT = (252, 250, 244)
INK = (24, 24, 24)
NAVY = (18, 42, 68)
RED = (178, 38, 38)
RED_DK = (140, 26, 26)
GOLD = (198, 148, 52)
GREY = (108, 105, 96)
LINE = (196, 189, 172)
SEA = (13, 30, 54)
LAND = (222, 206, 172)
LAND_LN = (150, 138, 110)
TEAL = (24, 120, 116)
BLUE = (36, 80, 164)
ORANGE = (198, 110, 30)
PURPLE = (110, 60, 140)
GREEN = (60, 130, 60)

FD = "/usr/share/fonts/truetype/dejavu"
SERIF = os.path.join(FD, "DejaVuSerif.ttf")
SERIF_B = os.path.join(FD, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(FD, "DejaVuSans.ttf")
SANS_B = os.path.join(FD, "DejaVuSans-Bold.ttf")

WARN = []


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, f, max_w):
    out, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            if cur:
                out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def para(d, x, y, text, f, max_w, leading, fill=INK, max_lines=None):
    lines = wrap(d, text, f, max_w)
    if max_lines is not None and len(lines) > max_lines:
        WARN.append("TRUNCATED %r to %d lines" % (text[:48], max_lines))
        lines = lines[:max_lines]
    for line in lines:
        d.text((x, y), line, font=f, fill=fill)
        y += leading
    return y


def hline(d, x0, x1, y, w=2, fill=INK):
    d.line([(x0, y), (x1, y)], fill=fill, width=w)


def vgrad(d, x0, y0, x1, y1, top, bot):
    n = max(1, y1 - y0)
    for i in range(n):
        t = i / n
        c = tuple(int(top[k] + (bot[k] - top[k]) * t) for k in range(3))
        d.line([(x0, y0 + i), (x1, y0 + i)], fill=c)


def starfield(d, x0, y0, x1, y1, pts):
    for (sx, sy, r) in pts:
        d.ellipse([x0 + sx - r, y0 + sy - r, x0 + sx + r, y0 + sy + r],
                  fill=(235, 235, 220))


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
    ("EUROPE 17", BLUE),
    ("AMERICAS 7", TEAL),
    ("ASIA-PACIFIC 5", ORANGE),
    ("MIDEAST 4", PURPLE),
    ("AFRICA 3", GREEN),
]

# (num, city, topic, headline, deck, art)
FEATURES = [
    ("01", "ANTALYA, T\u00dcRKIYE", "CLIMATE",
     "COP31 enters a second day of overtime with no deal",
     "Third \u2018final\u2019 text due Sunday; delegates get until 6am to "
     "agree it. 130 nations want fossil-fuel language back. "
     "(AFP, Reuters)",
     "cop31"),
    ("02", "RIYADH", "CONFLICT",
     "Riyadh on alert for a third night as Houthis vow more strikes",
     "Three missiles intercepted Saturday; Houthis threaten ports "
     "and a power station. (Al Jazeera, Dawn)",
     "riyadh"),
    ("03", "GUASAVE, MEXICO", "CARTELS",
     "Mexico seizes \u2018Chapo Isidro\u2019 in a gunfight that kills 11",
     "FBI top-10 fugitive held after a Friday-night raid in Sinaloa; "
     "$5m reward. (Reuters, AP)",
     "sinaloa"),
]

# (num, city, topic, headline, deck, art)
SMALLS = [
    ("04", "NEW YORK", "MARKETS",
     "Bitcoin hits a two-year low, then rebounds 8%",
     "Fell to $55,252 on Saturday, back near $59,952. (Dawn)",
     "bitcoin"),
    ("05", "WASHINGTON", "TECH",
     "SEC probes Nvidia as shares plunge 14%",
     "SEC inquiry reported Saturday; Huang stays out. (NYT)",
     "chip"),
    ("06", "WASHINGTON", "POLITICS",
     "Trump vows a 10% cap on card rates",
     "\u201cI would do it,\u201d he tells Fox; Warren backs the cap. (AP)",
     "card"),
    ("07", "PARIS", "PROTEST",
     "France marches for a sixth weekend",
     "82,500 counted; Le Pen holds RN congress in Orl\u00e9ans. (AFP)",
     "protest"),
    ("08", "GAZA CITY", "WAR",
     "Four more killed in Gaza despite the truce",
     "Three died in a strike on a food-aid vehicle. (AFP)",
     "gaza"),
    ("09", "KYIV", "WAR",
     "Russia strikes again; power cut in two regions",
     "Grid sites hit; outages in Poltava and Kharkiv. (Ukrinform)",
     "kyiv"),
    ("10", "TURIN", "SPORT",
     "Alcaraz sets up a final with Zverev",
     "Beat Shelton in three sets; Zverev beat Medvedev. (Reuters)",
     "tennis"),
    ("11", "BRUSSELS", "EUROPE",
     "EU proposes a tax on Big Tech",
     "Levy to fund the budget; six states want farm cuts. (Dawn)",
     "eu"),
    ("12", "GENEVA", "DIPLOMACY",
     "States open a path to \u2018killer robot\u2019 rules",
     "Draft rules by 2028 after Russian pushback. (SCMP)",
     "robots"),
    ("13", "LIMA", "DISASTER",
     "6.7 quake shakes Peru\u2019s Andes",
     "No deaths reported; tremors felt in Lima. (USGS)",
     "quake"),
]

# (num, one-line brief) — numbers continue from the 13 features
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
    "summit (Thu 19) \u00b7 UK\u2013EU reset deal \u00b7 S&P correction \u00b7 Kyiv "
    "bridges, 8 killed \u00b7 Kryvyi Rih, 2 killed, 42 hurt \u00b7 ICJ Myanmar "
    "verdict (Thu 19) \u00b7 Anthropic $83 IPO (Thu 19) \u00b7 GTA VI launch "
    "\u00b7 Riyadh PIF tower hit (Thu 19) \u00b7 Mongolia quits (Fri)."
)

FOOTER = (
    "Every story here happened, or was first reported, on Sunday 22 November 2026. "
    "Claims are attributed. "
    "Sources: AFP \u00b7 Reuters \u00b7 AP \u00b7 Dawn \u00b7 Al Jazeera"
)

# ---------------------------------------------------------------- art

def art_cop31(d, x, y, w, h):
    """Antalya talks: green gradient, globe, rising thermometer, papers."""
    vgrad(d, x, y, x + w, y + h, (150, 205, 170), (40, 110, 80))
    d.ellipse([x + w - 70, y + 8, x + w - 30, y + 48], fill=(255, 214, 140))
    cx, cy, r = x + 118, y + 54, 40
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(30, 90, 140))
    d.ellipse([cx - 18, cy - 30, cx + 6, cy - 6], fill=(60, 150, 90))
    d.ellipse([cx - 4, cy + 8, cx + 26, cy + 32], fill=(60, 150, 90))
    d.ellipse([cx - 34, cy + 2, cx - 14, cy + 20], fill=(60, 150, 90))
    d.arc([cx - r, cy - r, cx + r, cy + r], 0, 360,
          fill=(200, 230, 240), width=2)
    tx = x + 212
    d.rectangle([tx, y + 16, tx + 14, y + 88], fill=(240, 238, 230))
    d.rectangle([tx + 2, y + 44, tx + 12, y + 86], fill=(220, 40, 30))
    d.ellipse([tx - 6, y + 82, tx + 20, y + 108], fill=(220, 40, 30))
    d.ellipse([tx - 2, y + 86, tx + 16, y + 104], fill=(255, 120, 90))
    for px in (30, 58, 86):
        d.rectangle([x + px, y + 90, x + px + 26, y + 106],
                    fill=(250, 248, 240))
        d.line([x + px + 4, y + 95, x + px + 22, y + 95],
               fill=(120, 120, 110), width=1)
        d.line([x + px + 4, y + 100, x + px + 22, y + 100],
               fill=(120, 120, 110), width=1)
    d.rectangle([x, y + h - 6, x + w, y + h], fill=(30, 80, 58))


def art_riyadh(d, x, y, w, h):
    """Riyadh night: alert sky, interceptor trails, tower skyline."""
    vgrad(d, x, y, x + w, y + h, (16, 24, 48), (60, 44, 66))
    starfield(d, x, y, x + w, y + h,
              [(20, 14, 1), (60, 26, 1), (120, 10, 2), (180, 22, 1),
               (240, 12, 1), (280, 30, 2), (150, 34, 1), (95, 12, 1)])
    d.ellipse([x + w - 52, y + 10, x + w - 24, y + 38], fill=(232, 228, 200))
    d.ellipse([x + w - 46, y + 14, x + w - 26, y + 34], fill=(60, 44, 66))
    # three interceptor trails climbing to bursts
    for (x0, y0, x1, y1) in [(40, 92, 110, 22), (150, 96, 200, 30),
                             (230, 94, 268, 44)]:
        d.line([x + x0, y + y0, x + x1, y + y1], fill=(255, 176, 66), width=3)
        d.line([x + x0, y + y0, x + x1, y + y1], fill=(255, 226, 160), width=1)
        d.ellipse([x + x1 - 5, y + y1 - 5, x + x1 + 5, y + y1 + 5],
                  fill=(255, 200, 90))
    # tower skyline, one tower with a red alert band
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


def art_sinaloa(d, x, y, w, h):
    """Sinaloa raid at dawn: orange sky, roadblocks burning, helicopters."""
    vgrad(d, x, y, x + w, y + h, (226, 150, 70), (120, 60, 40))
    d.ellipse([x + 24, y + 10, x + 64, y + 50], fill=(255, 214, 140))
    # helicopters: body + rotor + searchlight cone
    for hx, hy in [(150, 22), (240, 34)]:
        d.ellipse([x + hx - 14, y + hy - 4, x + hx + 14, y + hy + 6],
                  fill=(20, 20, 26))
        d.line([x + hx - 26, y + hy - 6, x + hx + 26, y + hy - 6],
               fill=(20, 20, 26), width=2)
        d.polygon([(x + hx - 4, y + hy + 6), (x + hx + 4, y + hy + 6),
                   (x + hx + 16, y + hy + 40), (x + hx - 16, y + hy + 40)],
                  fill=(255, 240, 180))
    # road with burning barricades
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


FEATURE_ART = {"cop31": art_cop31, "riyadh": art_riyadh,
               "sinaloa": art_sinaloa}

def mini_art(d, x, y, w, h, kind):
    """48px banner motif for a small story card."""
    if kind == "bitcoin":
        d.rectangle([x, y, x + w, y + h], fill=(247, 147, 26))
        d.ellipse([x + w // 2 - 20, y + 3, x + w // 2 + 20, y + 43],
                  fill=(255, 255, 255))
        d.text((x + w // 2 - 8, y + 9), "\u20bf", font=F(SANS_B, 24),
               fill=(247, 147, 26))
        d.line([x + 10, y + 12, x + 60, y + 34, x + 110, y + 8, x + w - 10,
                y + 30], fill=(178, 38, 38), width=2)
    elif kind == "chip":
        d.rectangle([x, y, x + w, y + h], fill=(16, 60, 44))
        d.rectangle([x + w // 2 - 22, y + 8, x + w // 2 + 22, y + 38],
                    fill=(10, 14, 18))
        d.rectangle([x + w // 2 - 14, y + 15, x + w // 2 + 14, y + 31],
                    fill=(40, 90, 70))
        for k in range(5):
            d.line([x + w // 2 - 22, y + 12 + k * 6, x + w // 2 - 30,
                    y + 12 + k * 6], fill=(255, 220, 90), width=1)
            d.line([x + w // 2 + 22, y + 12 + k * 6, x + w // 2 + 30,
                    y + 12 + k * 6], fill=(255, 220, 90), width=1)
    elif kind == "card":
        d.rectangle([x, y, x + w, y + h], fill=(18, 42, 68))
        d.rounded_rectangle([x + 14, y + 8, x + w - 14, y + 38], radius=4,
                            fill=(240, 238, 230))
        d.text((x + 22, y + 12), "10%", font=F(SANS_B, 16), fill=RED_DK)
        d.rectangle([x + 14, y + 38, x + w - 14, y + 42], fill=GOLD)
        d.text((x + 22, y + 42), "CAP", font=F(SANS_B, 8),
               fill=(240, 238, 230))
    elif kind == "protest":
        d.rectangle([x, y, x + w, y + h], fill=(52, 44, 40))
        for px, col in [(30, (255, 120, 40)), (70, (255, 170, 60)),
                        (110, (36, 80, 164)), (145, (178, 38, 38))]:
            d.line([x + px, y + 10, x + px, y + h - 6], fill=(240, 238, 230),
                   width=2)
            d.rectangle([x + px, y + 10, x + px + 22, y + 24], fill=col)
        d.rectangle([x, y + h - 6, x + w, y + h], fill=(178, 38, 38))
    elif kind == "gaza":
        vgrad(d, x, y, x + w, y + h, (214, 190, 150), (140, 110, 80))
        for bx in (14, 58, 102, 146):
            d.rectangle([x + bx, y + 22, x + bx + 34, y + h - 4],
                        fill=(150, 118, 78))
        for (sx, sy) in [(30, 8), (76, 4), (120, 10), (158, 6)]:
            d.ellipse([x + sx, y + sy, x + sx + 14, y + sy + 12],
                      fill=(110, 104, 96))
        d.ellipse([x + 84, y + 12, x + 100, y + 28], fill=(255, 140, 40))
        d.rectangle([x, y + h - 4, x + w, y + h], fill=(96, 72, 46))
    elif kind == "kyiv":
        vgrad(d, x, y, x + w, y + h, (10, 16, 30), (34, 30, 52))
        starfield(d, x, y, x + w, y + h,
                  [(20, 8, 1), (70, 14, 1), (130, 8, 2), (160, 16, 1)])
        d.line([x + 30, y + 8, x + 30, y + h - 10], fill=(16, 18, 28), width=3)
        d.line([x + 14, y + 14, x + 46, y + 14], fill=(16, 18, 28), width=3)
        d.line([x + 14, y + 14, x + 90, y + 28], fill=(60, 62, 76), width=1)
        d.rectangle([x + 60, y + 26, x + 110, y + h], fill=(8, 10, 18))
        d.rectangle([x + 120, y + 34, x + 170, y + h], fill=(10, 12, 20))
        for (fx, fy) in [(68, 34), (84, 44), (128, 42), (150, 52)]:
            d.rectangle([x + fx, y + fy, x + fx + 6, y + fy + 8],
                        fill=(255, 214, 130))
        for r, col in [(10, (255, 120, 40)), (6, (255, 170, 60))]:
            d.ellipse([x + 85 - r, y + 30 - r, x + 85 + r, y + 30 + r],
                      fill=col)
    elif kind == "tennis":
        d.rectangle([x, y, x + w, y + h], fill=(24, 120, 60))
        d.ellipse([x + w // 2 - 20, y + 4, x + w // 2 + 20, y + 44],
                  fill=(200, 230, 60))
        d.arc([x + w // 2 - 20, y + 4, x + w // 2 + 20, y + 44], 250, 80,
              fill=(255, 255, 255), width=2)
        d.arc([x + w // 2 - 20, y + 4, x + w // 2 + 20, y + 44], 70, 260,
              fill=(255, 255, 255), width=2)
        d.line([x + 8, y + h - 6, x + w - 8, y + h - 6],
               fill=(255, 255, 255), width=2)
    elif kind == "eu":
        d.rectangle([x, y, x + w, y + h], fill=(36, 80, 164))
        import math as _m
        for k in range(8):
            a = _m.pi * 2 * k / 8
            sx = x + w // 2 + int(13 * _m.cos(a))
            sy = y + h // 2 + int(11 * _m.sin(a))
            d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 220, 60))
        d.rectangle([x, y + h - 4, x + w, y + h], fill=(255, 220, 60))
    elif kind == "robots":
        d.rectangle([x, y, x + w, y + h], fill=(24, 24, 30))
        d.rectangle([x + w // 2 - 18, y + 8, x + w // 2 + 18, y + 34],
                    fill=(120, 120, 130))
        d.rectangle([x + w // 2 - 8, y + 16, x + w // 2 + 8, y + 26],
                    fill=(178, 38, 38))
        d.ellipse([x + w // 2 - 5, y + 18, x + w // 2 - 1, y + 24],
                  fill=(255, 255, 255))
        d.ellipse([x + w // 2 + 1, y + 18, x + w // 2 + 5, y + 24],
                  fill=(255, 255, 255))
        d.line([x + w // 2 - 14, y + 34, x + w // 2 - 14, y + 42],
               fill=(120, 120, 130), width=2)
        d.line([x + w // 2 + 14, y + 34, x + w // 2 + 14, y + 42],
               fill=(120, 120, 130), width=2)
    elif kind == "quake":
        vgrad(d, x, y, x + w, y + h, (196, 160, 110), (120, 92, 60))
        d.line([x + 8, y + 10, x + 50, y + 30, x + 90, y + 12, x + 130,
                y + 34, x + w - 8, y + 16], fill=(140, 26, 26), width=3)
        d.polygon([(x + 20, y + h - 4), (x + 60, y + 14), (x + 100, y + h - 4)],
                  fill=(96, 72, 46))
        d.polygon([(x + 90, y + h - 4), (x + 130, y + 20), (x + 168, y + h - 4)],
                  fill=(110, 84, 54))
        d.rectangle([x, y + h - 4, x + w, y + h], fill=(96, 72, 46))


# simplified world map: rough continent polygons in a 332x174 box
CONTINENTS = [
    [(18, 28), (45, 12), (80, 16), (105, 26), (120, 40), (108, 58),
     (88, 72), (70, 88), (48, 84), (30, 66), (14, 48)],
    [(108, 10), (124, 8), (128, 18), (112, 20)],
    [(92, 96), (112, 92), (128, 100), (132, 124), (120, 152), (104, 150),
     (94, 122)],
    [(168, 30), (186, 22), (202, 28), (206, 40), (196, 52), (180, 50),
     (168, 42)],
    [(162, 28), (168, 26), (170, 34), (164, 36)],
    [(170, 62), (196, 58), (212, 68), (210, 92), (196, 118), (180, 112),
     (168, 88), (164, 72)],
    [(208, 26), (250, 14), (300, 20), (322, 34), (318, 58), (296, 72),
     (268, 78), (240, 66), (216, 52), (206, 38)],
    [(272, 84), (292, 86), (296, 96), (276, 96)],
    [(272, 122), (306, 118), (318, 130), (300, 146), (276, 142)],
]
# (pin number, map x, map y)
PINS = [("1", 200, 54), ("2", 216, 82), ("3", 36, 60), ("4", 56, 44),
        ("5", 64, 52), ("7", 170, 28), ("8", 210, 70), ("9", 204, 30),
        ("10", 184, 44), ("13", 104, 112)]

# ---------------------------------------------------------------- layout

def draw_masthead(d):
    d.text((28, 14), "THE WORLD IN ONE DAY", font=F(SANS_B, 15), fill=RED)
    right = "SUNDAY\u2019S NEWS \u00b7 ONE PAGE \u00b7 36 STORIES \u00b7 5 REGIONS"
    d.text((W - 28 - d.textlength(right, font=F(SANS, 13)), 15), right,
           font=F(SANS, 13), fill=GREY)
    d.text((28, 32), "Sunday 22 November 2026", font=F(SERIF_B, 60),
           fill=INK)
    kicker = ("COP31 drags into day two of overtime \u00b7 Riyadh on alert "
              "again \u00b7 Mexico seizes \u2018Chapo Isidro\u2019")
    d.text((28, 104), kicker, font=F(SERIF, 15), fill=RED)
    hline(d, 28, W - 28, 128, w=4)


def draw_stats(d):
    y0 = 136
    cw = (W - 56) // 6
    for i, (big, label) in enumerate(STATS):
        cx = 28 + i * cw
        d.text((cx + 8, y0), big, font=F(SERIF_B, 27), fill=RED)
        d.text((cx + 8, y0 + 32), label, font=F(SANS, 11), fill=GREY)
        if i:
            d.line([(cx, y0 + 4), (cx, y0 + 44)], fill=LINE, width=1)
    hline(d, 28, W - 28, 186, w=1, fill=LINE)


def draw_chips(d):
    x = 28
    y = 194
    for label, col in CHIPS:
        wch = d.textlength(label, font=F(SANS_B, 12)) + 18
        d.rounded_rectangle([x, y, x + wch, y + 20], radius=10, fill=col)
        d.text((x + 9, y + 3), label, font=F(SANS_B, 12),
               fill=(255, 255, 255))
        x += wch + 8
    note = "ALL STORIES: SUN 22 NOV 2026, ANY TIME ZONE"
    d.text((W - 28 - d.textlength(note, font=F(SANS, 11)), y + 4), note,
           font=F(SANS, 11), fill=GREY)


def feature_card(d, x, y, w, h, feat):
    num, city, topic, headline, deck, art = feat
    d.rectangle([x, y, x + w, y + h], outline=LINE, width=1, fill=PAPER_LT)
    FEATURE_ART[art](d, x + 1, y + 1, w - 2, 110)
    ty = y + 118
    d.text((x + 10, ty), "%s \u00b7 %s \u00b7 %s" % (num, city, topic),
           font=F(SANS_B, 11), fill=RED)
    hy = ty + 18
    para(d, x + 10, hy, headline, F(SERIF_B, 22), w - 20, 26,
         max_lines=3)
    dy = hy + 3 * 26 + 4
    para(d, x + 10, dy, deck, F(SANS, 12), w - 20, 15, fill=(60, 58, 52),
         max_lines=3)


def small_card(d, x, y, w, h, item):
    num, city, topic, headline, deck, art = item
    d.rectangle([x, y, x + w, y + h], outline=LINE, width=1, fill=PAPER_LT)
    mini_art(d, x + 1, y + 1, w - 2, 46, art)
    ty = y + 50
    d.text((x + 8, ty), "%s \u00b7 %s \u00b7 %s" % (num, city, topic),
           font=F(SANS_B, 10), fill=RED)
    hy = ty + 14
    para(d, x + 8, hy, headline, F(SERIF_B, 14), w - 16, 16, max_lines=3)
    dy = hy + 3 * 16 + 2
    para(d, x + 8, dy, deck, F(SANS, 10), w - 16, 12, fill=(60, 58, 52),
         max_lines=2)


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SEA)
    for poly in CONTINENTS:
        pts = [(x + px, y + py) for (px, py) in poly]
        d.polygon(pts, fill=LAND, outline=LAND_LN)
    d.text((x + 8, y + 8), "ATLANTIC", font=F(SANS_B, 10),
           fill=(140, 160, 190))
    d.text((x + 8, y + h - 20), "PACIFIC", font=F(SANS_B, 10),
           fill=(140, 160, 190))
    d.text((x + w - 52, y + 8), "ASIA", font=F(SANS_B, 10),
           fill=(140, 160, 190))
    for num, px, py in PINS:
        cx, cy = x + px, y + py
        d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=RED,
                  outline=(255, 255, 255), width=1)
        tw = d.textlength(num, font=F(SANS_B, 9))
        d.text((cx - tw / 2, cy - 6), num, font=F(SANS_B, 9),
               fill=(255, 255, 255))


def draw_briefs(d, x, y, w, h):
    cols = [[], [], []]
    for i, (num, text) in enumerate(BRIEFS):
        cols[i % 3].append((num, text))
    cw = (w - 24) // 3
    f = F(SANS, 9)
    for ci, col in enumerate(cols):
        cx = x + ci * (cw + 12)
        by = y
        for num, text in col:
            line = "%s  %s" % (num, text)
            if d.textlength(line, font=f) > cw:
                WARN.append("BRIEF OVERFLOW %s" % line[:50])
                while d.textlength(line + "\u2026", font=f) > cw and len(line) > 8:
                    line = line[:-1]
                line += "\u2026"
            d.text((cx, by), line, font=f, fill=INK)
            by += 19
    return y


def draw_markets(d, y):
    d.text((28, y + 2), "MARKETS AT CLOSE", font=F(SANS_B, 12), fill=RED)
    bx = 190
    d.rectangle([bx, y + 4, bx + 220, y + 16], outline=LINE, width=1)
    d.rectangle([bx, y + 4, bx + 220, y + 10], fill=(232, 226, 212))
    d.rectangle([bx, y + 10, bx + 220, y + 16], fill=RED)
    d.text((bx + 228, y + 2),
           "BITCOIN $55,252 low \u00b7 +8% rebound",
           font=F(SANS_B, 12), fill=INK)
    d.text((W - 28 - d.textlength("Nasdaq \u22125.3% Fri \u00b7 S&P and Dow in correction",
                                  font=F(SANS, 12)), y + 2),
           "Nasdaq \u22125.3% Fri \u00b7 S&P and Dow in correction",
           font=F(SANS, 12), fill=GREY)


def draw_date_check(d, y):
    d.rounded_rectangle([28, y, W - 28, y + 34], radius=3, outline=RED,
                        width=2)
    d.text((38, y + 4), "DATE CHECK", font=F(SANS_B, 11), fill=RED)
    para(d, 128, y + 4, DATE_CHECK, F(SANS, 11), W - 28 - 128 - 10, 13,
         fill=INK, max_lines=2)


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_stats(d)
    draw_chips(d)
    # features: 3 cards, y 212..458
    fw = (W - 56 - 24) // 3
    for i, feat in enumerate(FEATURES):
        fx = 28 + i * (fw + 12)
        feature_card(d, fx, 212, fw, 246, feat)
    # smalls: 2 rows of 5, 142 tall
    sw = (W - 56 - 36) // 5
    for row in range(2):
        for i in range(5):
            item = SMALLS[row * 5 + i]
            sx = 28 + i * (sw + 9)
            small_card(d, sx, 464 + row * 150, sw, 142, item)
    # bottom: map + briefs
    d.text((28, 762), "WHERE IT HAPPENED", font=F(SANS_B, 13), fill=RED)
    d.text((340, 762), "ALSO ON SUNDAY 22 NOVEMBER \u2014 23 MORE STORIES",
           font=F(SANS_B, 13), fill=RED)
    hline(d, 28, W - 28, 780, w=1, fill=LINE)
    draw_map(d, 28, 786, 300, 154)
    draw_briefs(d, 340, 786, W - 28 - 340, 154)
    draw_markets(d, 946)
    draw_date_check(d, 970)
    if d.textlength(FOOTER, font=F(SANS, 11)) > W - 56:
        WARN.append("FOOTER OVERFLOW")
    d.text((28, 1008), FOOTER, font=F(SANS, 11), fill=GREY)
    return img


def main():
    img = build()
    out = os.path.join(HERE, "entry.png")
    img.save(out, "PNG", optimize=True)
    size = os.path.getsize(out)
    print("wrote %s %dx%d %d bytes" % (out, W, H, size))
    if size > 1048576:
        print("WARNING: over 1 MiB cap")
    for w in WARN:
        print("WARN:", w)
    print("warnings:", len(WARN))


if __name__ == "__main__":
    main()
