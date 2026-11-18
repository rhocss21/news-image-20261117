#!/usr/bin/env python3
"""Render the front page for Tuesday 17 November 2026 as a 1024x1024 PNG.

Runs locally only (needs Pillow + a world GeoJSON for the map). The submitted
program main.py just copies the rendered entry.png; it needs no Pillow.
Every story below was first reported on Tuesday 17 November 2026 (sources:
Reuters, AP, Al Jazeera, NPR, BBC, Zark News, FeedCast, OneTurn, sports wires).
"""
import json
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 234)
INK = (18, 18, 18)
NAVY = (20, 33, 61)
RED = (178, 34, 34)
GREY = (110, 108, 100)
RULE = (150, 146, 134)
MAP_OCEAN = (232, 237, 240)
MAP_LAND = (206, 198, 176)
MAP_BORDER = (255, 255, 255)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)      # noqa: E731
SERIF = lambda s: font("DejaVuSerif.ttf", s)            # noqa: E731
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)        # noqa: E731
SANS = lambda s: font("DejaVuSans.ttf", s)               # noqa: E731


def wrap(d, text, f, max_w):
    """Greedy wrap to lines that fit max_w; returns list of lines."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_one_line(d, text, f, max_w):
    """Truncate with ellipsis to a single line that fits max_w."""
    if d.textlength(text, font=f) <= max_w:
        return text
    while text and d.textlength(text + "\u2026", font=f) > max_w:
        text = text[:-1]
    return text + "\u2026"


# --- stories: (kicker, headline, summary) for items 2..35 -------------------
BRIEF = [
    ("MIDDLE EAST", "THIRD US CARRIER REACHES GULF",
     "A third carrier joins the Gulf force; tankers mined."),
    ("ASIA", "TRUMP LANDS IN MANILA",
     "Asia trip opens at ASEAN and first Quad meet in years."),
    ("ASIA", "XI, TRUMP, PUTIN TO MEET THURSDAY",
     "China confirms a first three-way summit, in Shenzhen."),
    ("TECH", "NVIDIA IN TURMOIL AFTER HUANG EXIT",
     "Interim chiefs face a first earnings call since the exit."),
    ("EUROPE", "FIVE STATES PLAN RWANDA HUB",
     "Joint centre for rejected asylum seekers, from next year."),
    ("MIDDLE EAST", "HOUTHIS PUSH YEMEN ARMY TO ADEN",
     "Troops quit the Red Sea coast; Riyadh sacks commander."),
    ("USA", "PENTAGON FAILS AUDIT, YEAR NINE",
     "Auditors cannot verify $4.8 trillion in assets."),
    ("TECH", "US MOVES TO CLOSE CHIP LOOPHOLE",
     "US introduces licensing for AI chips in SE Asia."),
    ("ASIA", "JAPAN SCRAMBLES JETS AT RUSSIA",
     "Tokyo protests a suspected Russian airspace violation."),
    ("USA", "WHITE HOUSE VETS AGENCY TESTIMONY",
     "Agencies need approval before staff testify to Congress."),
    ("HEALTH", "13 US BABIES BORN WITH MEASLES",
     "Cases hit their highest total since 1991, CDC says."),
    ("USA", "JPMORGAN GLITCH HITS BANKING",
     "Online accounts and Zelle disrupted at major US banks."),
    ("USA", "FLIGHT DELAYS DRAG ON",
     "Air travel still recovering after Friday's grounding."),
    ("AFRICA", "17 KILLED IN TWO SA SHOOTINGS",
     "Separate attacks leave at least 17 dead, police say."),
    ("ASIA", "BUS PLUNGES INTO RAVINE IN INDIA",
     "Six to eight dead and 20+ hurt in Uttarakhand."),
    ("SPORT", "SRI LANKA ALL OUT FOR 98",
     "Pakistan on top in the Rawalpindi Test."),
    ("HEALTH", "ERITREA BEATS TRACHOMA",
     "WHO validates elimination of the blinding disease."),
    ("MIDDLE EAST", "BAHRAIN JAILS 64 FOR LIFE",
     "Shia Muslims sentenced over alleged Iran links."),
    ("AMERICAS", "CARNEY RETURNS TO CHINA",
     "Canada's PM returns to China a year on."),
    ("AMERICAS", "PERU AWAITS POPE LEO XIV",
     "A home for older residents prepares his return visit."),
    ("USA", "US COLLEGES LOSE FOREIGN STUDENTS",
     "International enrolment turns away; campuses struggle."),
    ("TECH", "CYBERCRIME TO COST $10.5 TRILLION",
     "Projected annual damage worldwide, Gulf News reports."),
    ("TECH", "MICROSOFT OUTAGE DISRUPTS WORK",
     "Workplace services hit amid FAA and banking disruption."),
    ("ASIA", "CHEAP SOLAR COOKING IN AFGHANISTAN",
     "Affordable method helps families cut energy costs."),
    ("MIDDLE EAST", "DRONE ALERT AT IRAQ GAS FIELD",
     "Drone alert reported at an Iraqi gas field."),
    ("ASIA", "TRUMP TEASES KIM MEETING",
     "President hints at talks with North Korea's leader."),
    ("ASIA", "SHENZHEN SHOWS OFF ROBOT CITY",
     "Driverless taxis and robots on show in the APEC host city."),
    ("SPORT", "CHARGERS 23, RAVENS 20",
     "Los Angeles take a first win of the season on MNF."),
    ("SPORT", "PELICANS 115, WARRIORS 94",
     "New Orleans rout Golden State in the NBA."),
    ("SPORT", "BENGALS 38, STEELERS 18",
     "NFL records its 1,100th unique final score."),
    ("SPORT", "IRELAND 3, KOSOVO 0",
     "Ireland ease past Kosovo in the Nations League."),
    ("SPORT", "GERMANY 5, NETHERLANDS 0",
     "Germany rout the Netherlands in European football."),
    ("SPORT", "PAKISTAN WOMEN BEAT ZIMBABWE",
     "Win by 51 runs: 150 for 6 plays 99 for 8."),
    ("ASIA", "TRUMP TO MEET MARCOS ON WEDNESDAY",
     "Bilateral talks in Manila before the Shenzhen flight."),
]

# Map pins: numbered by STORY number (two pins share 1: the lead covers both).
PINS = [
    (1, 36.4, 45.3, "Kerch Bridge"),
    (1, 30.5, 50.4, "Kyiv"),
    (2, 56.5, 26.5, "Hormuz"),
    (3, 121.0, 14.6, "Manila"),
    (4, 114.1, 22.5, "Shenzhen"),
    (6, 30.1, -1.9, "Kigali"),
    (7, 45.0, 12.8, "Aden"),
    (10, 139.7, 35.7, "Tokyo"),
    (12, -77.0, 38.9, "Washington"),
    (16, 79.5, 30.3, "Uttarakhand"),
    (17, 73.1, 33.6, "Rawalpindi"),
    (18, 38.9, 15.3, "Asmara"),
    (19, 50.6, 26.2, "Bahrain"),
    (20, 116.4, 39.9, "Beijing"),
]

LEAD_HEAD = "BRIDGES HIT IN KYIV AND CRIMEA"
LEAD_SUM = ("Ukraine hits the Kerch Bridge for a second day as Russian missiles strike "
            "Kyiv\u2019s two bridges over the Dnipro. Moscow claims 1,336 drones downed "
            "in Kyiv\u2019s biggest air attack of the war.")


def draw_map(d, box, geo_path="/tmp/countries.geo.json"):
    """Rasterise country polygons into box (x0, y0, x1, y1), equirectangular."""
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=MAP_OCEAN)
    lon0, lon1, lat0, lat1 = -168.0, 192.0, -58.0, 84.0  # lon1 > 180: wrap Asia

    def px(lon, lat):
        while lon < lon0:
            lon += 360.0
        while lon > lon1:
            lon -= 360.0
        return (x0 + (lon - lon0) / (lon1 - lon0) * (x1 - x0),
                y0 + (lat1 - lat) / (lat1 - lat0) * (y1 - y0))

    with open(geo_path) as fh:
        geo = json.load(fh)
    for feat in geo["features"]:
        geom = feat["geometry"]
        polys = []
        if geom["type"] == "Polygon":
            polys = [geom["coordinates"]]
        elif geom["type"] == "MultiPolygon":
            polys = geom["coordinates"]
        for poly in polys:
            for ring in poly:
                pts = [px(lon, lat) for lon, lat in ring]
                if len(pts) >= 3:
                    d.polygon(pts, fill=MAP_LAND, outline=MAP_BORDER)
    # graticule
    for lat in range(-60, 90, 30):
        _, yy = px(0, lat)
        d.line([(x0, yy), (x1, yy)], fill=(210, 216, 220), width=1)
    # pins (display offsets in px separate clustered pins; leader line to true spot)
    offsets = {"Kerch Bridge": (10, 10), "Kyiv": (-12, -10),
               "Hormuz": (10, 8), "Bahrain": (12, -8),
               "Aden": (10, 10), "Asmara": (-12, -8),
               "Uttarakhand": (-10, -10), "Rawalpindi": (12, 8)}
    for num, lon, lat, label in PINS:
        cx, cy = px(lon, lat)
        dx, dy = offsets.get(label, (0, 0))
        px_, py_ = cx + dx, cy + dy
        if (dx, dy) != (0, 0):
            d.line([(cx, cy), (px_, py_)], fill=RED, width=1)
            d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=RED)
        r = 10
        d.ellipse([px_ - r, py_ - r, px_ + r, py_ + r], fill=RED,
                  outline=(255, 255, 255), width=2)
        f = SANS_B(11)
        tw = d.textlength(str(num), font=f)
        d.text((px_ - tw / 2, py_ - 7.5), str(num), font=f, fill=(255, 255, 255))
    return px


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead ------------------------------------------------------
    d.rectangle([0, 0, W, 92], fill=NAVY)
    d.text((16, 8), "THE WORLD", font=SERIF_B(58), fill=(255, 255, 255))
    d.text((16, 70), "ONE DAY  \u00b7  EVERY STORY THAT MATTERED",
           font=SANS_B(12), fill=(196, 205, 224))
    right = "TUESDAY 17 NOVEMBER 2026"
    d.text((W - 16 - d.textlength(right, font=SERIF_B(24)), 18), right,
           font=SERIF_B(24), fill=(255, 255, 255))
    d.text((W - 16 - d.textlength("35 STORIES \u00b7 6 CONTINENTS", font=SANS_B(12)), 70),
           "35 STORIES \u00b7 6 CONTINENTS", font=SANS_B(12), fill=(255, 214, 130))
    d.line([(0, 92), (W, 92)], fill=RED, width=4)

    # ---- lead story ----------------------------------------------------
    y = 106
    d.text((16, y), "LEAD  \u00b7  EUROPE \u2014 CONFLICT", font=SANS_B(12), fill=RED)
    y += 22
    head_lines = wrap(d, LEAD_HEAD, SERIF_B(34), W - 32)
    for line in head_lines:
        d.text((16, y), line, font=SERIF_B(34), fill=INK)
        y += 40
    y += 2
    for line in wrap(d, LEAD_SUM, SERIF(16), W - 32):
        d.text((16, y), line, font=SERIF(16), fill=(40, 40, 40))
        y += 21
    d.line([(16, 252), (W - 16, 252)], fill=RULE, width=1)

    # ---- world map -----------------------------------------------------
    d.text((16, 260), "THE WORLD AT A GLANCE", font=SANS_B(12), fill=RED)
    d.text((W - 16 - d.textlength("Numbered pins mark the stories below",
                                  font=SANS(11)), 261),
           "Numbered pins mark the stories below", font=SANS(11), fill=GREY)
    draw_map(d, (16, 280, W - 16, 436))
    d.rectangle([16, 280, W - 16, 436], outline=RULE, width=1)
    legend = "  \u2022  ".join(f"{n} {lab}" for n, _lo, _la, lab in PINS)
    legend = legend.replace("1 Kerch Bridge  \u2022  1 Kyiv",
                            "1 Kerch Bridge & Kyiv")
    leg_lines = wrap(d, legend, SANS(11), W - 32)
    ly = 442
    for line in leg_lines:
        d.text((16, ly), line, font=SANS(11), fill=(60, 60, 60))
        ly += 14
    d.line([(16, 474), (W - 16, 474)], fill=RULE, width=1)

    # ---- brief: 34 stories, 3 columns ---------------------------------
    d.text((16, 482), "THE DAY IN BRIEF \u2014 34 MORE STORIES",
           font=SANS_B(13), fill=NAVY)
    d.text((W - 16 - d.textlength("All reported Tuesday 17 November 2026",
                                  font=SANS(11)), 484),
           "All reported Tuesday 17 November 2026", font=SANS(11), fill=GREY)
    cols = 3
    col_w = (W - 32 - (cols - 1) * 16) // cols
    rows = 12
    top, row_h = 506, 40
    truncated = []
    for idx, (kicker, head, summ) in enumerate(BRIEF):
        col, row = idx // rows, idx % rows
        x = 16 + col * (col_w + 16)
        yy = top + row * row_h
        num = idx + 2
        d.text((x, yy), f"{num:>2}.", font=SANS_B(12), fill=RED)
        tx = x + 26
        d.text((tx, yy), kicker, font=SANS_B(9), fill=RED)
        hline = fit_one_line(d, head, SANS_B(12), col_w - 26)
        if hline != head:
            truncated.append(f"headline {num}: {head}")
        d.text((tx, yy + 11), hline, font=SANS_B(12), fill=INK)
        sline = fit_one_line(d, summ, SANS(10), col_w - 26)
        if sline != summ:
            truncated.append(f"summary {num}: {summ}")
        d.text((tx, yy + 26), sline, font=SANS(10), fill=(70, 70, 70))
        if row < rows - 1:
            d.line([(x, yy + 36), (x + col_w, yy + 36)], fill=(226, 222, 210), width=1)
    if truncated:
        print("TRUNCATED (%d):" % len(truncated))
        for t in truncated:
            print("  ", t)

    # ---- footer --------------------------------------------------------
    d.line([(16, 992), (W - 16, 992)], fill=RULE, width=1)
    foot = ("BY THE NUMBERS: 1,336 drones claimed  \u00b7  3 US carriers in the Gulf  "
            "\u00b7  $4.8tn Pentagon assets unverified  \u00b7  13 babies born with measles")
    d.text((16, 998), foot, font=SANS_B(11), fill=NAVY)
    d.text((16, 1013), "Sources: Reuters, AP, Al Jazeera, NPR, BBC, Zark News, FeedCast, OneTurn \u2014 "
           "all stories reported Tuesday 17 November 2026.",
           font=SANS(9), fill=GREY)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
