#!/usr/bin/env python3
"""Generiert calendar-data.js für DresdenForKids (self-contained, holt Live-Daten).

Quellen (live geparst):
  - KINOLINO:      https://www.kinolino.de/programm          (Filmtag-Tabelle)
  - Zschoner Mühle: https://www.zschoner-muehle.de/puppentheater/  (Kalendarium)

Quellen (manuell gepflegt, im Code unter KEEP_CURRENT):
  - TSD Ferienprogramm, Bibo Herbstferienprogramm, Zoo (Treffpunkte/Zookasper/Ferien/Halloween)

Aufruf:  python3 scripts/generate-calendar.py
Prüfen:  node scripts/check-calendar.js
"""
import re, html as h, datetime, os, ssl, urllib.request, sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO_ROOT, "calendar-data.js")
ctx = ssl.create_default_context()

def to_text(raw: str) -> str:
    t = re.sub(r"<script.*?</script>", " ", raw, flags=re.S | re.I)
    t = re.sub(r"<style.*?</style>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<(br|/p|/div|/li|/h[1-6]|/tr|/td)[^>]*>", "\n", t, flags=re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = h.unescape(t)
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n", t)
    return t.strip()

def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=40, context=ctx) as r:
        return to_text(r.read().decode("utf-8", "ignore"))

# ---------- KINOLINO ----------
VENUE_NAMES = {
    "Deutsches Hygiene-Museum Dresden": "Deutsches Hygiene-Museum",
    "GEH8 KUNST RAUM": "GEH8 KUNST RAUM",
    "Theologisch-Pädagogisches Institut Moritzburg": "Moritzburg (TPI)",
    "Landesbühnen Sachsen": "Landesbühnen Sachsen",
    "Programmkino Ost": "Programmkino Ost",
    "JKS Passage": "JKS Passage",
    "Zentralwerk": "Zentralwerk",
    "Karl-May-Museum Radebeul": "Karl-May-Museum Radebeul",
    "Museumskino in den Technischen Sammlungen Dresden": "TSD Museumskino",
    "Zentralkino": "Zentralkino",
    "Städtische Bibliothek Weixdorf": "Bibliothek Weixdorf",
    "JohannStadthalle": "JohannstadtHalle",
    "Centrum Galerie Dresden": "Centrum Galerie",
    "Filmgalerie Striesen": "Filmgalerie Striesen",
    "Kinopolis": "Kinopolis",
    "Clubkino im Lingnerschloss": "Clubkino Lingnerschloss",
    "Städtische Bibliothek Weißig": "Bibliothek Weißig",
    "Städtische Bibliothek Leubnitz-Neuostra": "Bibliothek Leubnitz-Neuostra",
    "Städtische Bibliothek Cossebaude": "Bibliothek Cossebaude",
    "Johannstädter Kulturtreff": "Johannstädter Kulturtreff",
}

def parse_kinolino():
    lines = fetch("https://www.kinolino.de/programm").splitlines()
    venues = set(VENUE_NAMES.keys())
    day_re = re.compile(r"^(Mo|Di|Mi|Do|Fr|Sa|So), (\d{2})\.(\d{2})\.(\d{4})$")
    time_re = re.compile(r"^(\d{2}:\d{2}) Uhr$")
    events, cur = [], None
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        m = day_re.match(line)
        if m:
            cur = f"{m.group(4)}-{m.group(3)}-{m.group(2)}"
            i += 1
            continue
        t = time_re.match(line)
        if t and cur:
            tm = t.group(1)
            film_lines, j, venue = [], i + 1, None
            while j < len(lines) and len(film_lines) <= 3:
                l2 = lines[j].strip()
                if not l2 or l2 in ("Uhrzeit", "Film", "Veranstaltungsort"):
                    j += 1
                    continue
                if l2 in venues:
                    venue = l2
                    break
                film_lines.append(l2)
                j += 1
            if venue and " ".join(film_lines):
                events.append({
                    "d": cur, "t": tm, "title": " ".join(film_lines),
                    "venue": VENUE_NAMES[venue],
                    "cost": "1 € + Museumseintritt" if venue == "Museumskino in den Technischen Sammlungen Dresden"
                            else "je nach Spielstätte (Kino ~3–5 €, Bibliotheks-Vorführungen oft frei)",
                    "note": "KINOLINO – Kinderfilmfest (Oktober)",
                    "url": "https://www.kinolino.de/programm", "cat": "kinolino",
                })
            i = j + 1
            continue
        i += 1
    seen, out = set(), []
    for e in events:
        k = (e["d"], e["t"], e["title"], e["venue"])
        if k not in seen:
            seen.add(k)
            out.append(e)
    return out

# ---------- Zschoner Mühle ----------
def zschoner():
    lines = fetch("https://www.zschoner-muehle.de/puppentheater/").splitlines()
    # Kalendarium: "17. Oktober 2026" (oder "17 17. Oktober 2026") gefolgt von "●…" und "HH:MM: Titel"
    year = datetime.date.today().year
    date_re = re.compile(r"^(?:\d{1,2} )?(\d{1,2})\. (Oktober|November|Dezember|Januar|Februar|März|April|Mai|Juni|Juli|August|September) (\d{4})$")
    time_re = re.compile(r"^(\d{2}:\d{2}): (.+)$")
    MONTHS = {"Januar": 1, "Februar": 2, "März": 3, "April": 4, "Mai": 5, "Juni": 6,
              "Juli": 7, "August": 8, "September": 9, "Oktober": 10, "November": 11, "Dezember": 12}
    events, cur = [], None
    for line in lines:
        l = line.strip()
        m = date_re.match(l)
        if m:
            d, mo, y = int(m.group(1)), MONTHS[m.group(2)], int(m.group(3))
            if y < year:
                continue
            cur = f"{y}-{mo:02d}-{d:02d}"
            continue
        t = time_re.match(l)
        if t and cur:
            tm, title = t.group(1), t.group(2).strip()
            is_tour = "mühlenführung" in title.lower()
            events.append({
                "d": cur, "t": tm, "title": title, "venue": "Zschoner Mühle",
                "cost": "7 € / erm. 5 €" if is_tour else "Karten online (zschoner-muehle.de)",
                "note": "Erlebnismühlenführung – Dresdner Mühlenmuseum, Reservierung empfohlen" if is_tour
                        else "Puppentheater für die ganze Familie – Reservierung empfohlen",
                "url": "https://www.zschoner-muehle.de/puppentheater/", "cat": "muehle",
            })
    seen, out = set(), []
    for e in events:
        k = (e["d"], e["t"], e["title"])
        if k not in seen:
            seen.add(k)
            out.append(e)
    return out

# ---------- Manuell gepflegte Daten (Stand 14.10.2026) ----------
def tsd():
    B = "Technische Sammlungen (TSD)"
    U = "https://tsd.de/programm/veranstaltungen/ferienprogramm"
    A12 = "12–16 J."
    entries = [
        ("2026-10-14", "14:00–16:30", "Alles Trick – offenes Familienangebot", "offenes Angebot", "Museumseintritt", "Trickfilm-Workshop: Wie entsteht Bewegung aus Stillbildern? Ab Grundschulalter"),
        ("2026-10-15", "14:00–16:30", "Alles Trick – offenes Familienangebot", "offenes Angebot", "Museumseintritt", "Trickfilm-Workshop, ab Grundschulalter"),
        ("2026-10-16", "11:00–13:00", "Fotogramme – offenes Familienangebot", "offenes Angebot", "Museumseintritt", "Fotos ohne Kamera in der Dunkelkammer – eigene Fotogramme gestalten, ab Grundschulalter"),
        ("2026-10-16", "14:00", "MITMALFILM-Workshop (KINOLINO)", "Anmeldung nötig (0351 488 7272)", "frei", "5–9 J., ca. 2 h, max. 1 Begleitperson pro Kind: eigenes Bild wird zum Trickfilm"),
        ("2026-10-17", "13:00", "Party-Lights: LED-Lichtorgel bauen", "Anmeldung nötig (0351 488 7272)", "5 €", f"{A12}, 3 h Workshop"),
        ("2026-10-18", "13:00–17:00", "Familientüfteln: Bürstenroboter & Ozobots (MACHwerk)", "offenes Angebot", "Museumseintritt", "Eigenen Bürstenroboter bauen oder Miniroboter Ozobots programmieren"),
        ("2026-10-18", "14:00", "Farbenrausch: LED-Kreisel löten", "Anmeldung nötig (0351 488 7272)", "5 €", f"{A12}, 2 h Workshop"),
        ("2026-10-18", "15:00", "Flimmerkino: Filmkonzert „Aschenputtel“ (KINOLINO)", "Anmeldung nötig (0351 488 7272)", "1 € + Museumseintritt", "4–10 J., Mitmach-Filmkonzert mit Live-Klavier – Silhouettenfilm"),
        ("2026-10-20", "14:00", "Ferien-Show: Wasser, Seife, Luft", "Anmeldung nötig (0351 488 7272)", "5 €", "6–12 J., Science-Show, 1 h"),
        ("2026-10-20", "14:00–16:30", "Alles Trick – offenes Familienangebot", "offenes Angebot", "Museumseintritt", "Trickfilm-Workshop, ab Grundschulalter"),
        ("2026-10-21", "14:00", "Ferien-Show: Wasser, Seife, Luft", "Anmeldung nötig (0351 488 7272)", "5 €", "6–12 J., Science-Show, 1 h"),
        ("2026-10-21", "14:00–16:30", "Alles Trick – offenes Familienangebot", "offenes Angebot", "Museumseintritt", "Trickfilm-Workshop, ab Grundschulalter"),
        ("2026-10-22", "14:00–16:30", "Alles Trick – offenes Familienangebot", "offenes Angebot", "Museumseintritt", "Trickfilm-Workshop, ab Grundschulalter"),
        ("2026-10-23", "14:00–16:30", "Fotogramme – offenes Familienangebot", "offenes Angebot", "Museumseintritt", "Fotos ohne Kamera in der Dunkelkammer, ab Grundschulalter"),
        ("2026-10-24", "9:30–16:30", "3D-Druck für Anfänger*innen (Code Week)", "Anmeldung nötig (0351 488 7272)", "frei (Verpflegung inkl.)", "nur für Mädchen 12–16 J., TinkerCAD + 3D-Druck"),
        ("2026-10-24", "13:00", "Party-Lights: LED-Lichtorgel bauen", "Anmeldung nötig (0351 488 7272)", "5 €", f"{A12}, 3 h Workshop"),
        ("2026-10-24", "13:00–18:00", "ABSCHIEDSFEST TSD", "offen", "Museumseintritt", "Großes Abschiedsfest am letzten Oktober-Wochenende – danach Schließung zur Sanierung!"),
        ("2026-10-25", "13:00–17:00", "Familientüfteln: Pixel-Art (MACHwerk)", "offenes Angebot", "Museumseintritt", "Eigene Pixel-Art entwerfen und mit LEGO®-Steinen drucken"),
        ("2026-10-25", "14:00", "Farbenrausch: LED-Kreisel löten", "Anmeldung nötig (0351 488 7272)", "5 €", f"{A12}, 2 h Workshop"),
    ]
    return [{"d": d, "t": t, "title": ti, "venue": B, "cost": c,
             "note": f"{n} · {b}", "url": U, "cat": "tsd"} for d, t, ti, b, c, n in entries]

def bibo():
    U = "https://www.bibo-dresden.de/de/veranstaltungen/kinderveranstaltungen/Herbstferienprogramm.php"
    entries = [
        ("2026-10-14", "14:00–17:00", "Maker-Mittwoch (offen) – Gorbitz", "Bibliothek Gorbitz, Merianplatz 4", "frei", "Lego programmieren · 14.10. ohne Betreuung"),
        ("2026-10-14", "14:00–18:00", "MakerBox (offen) – Gruna & Johannstadt", "Bibl. Gruna / Bibl. Johannstadt", "frei", "ab 3 J., Roboter, Kugelbahn, Lego – ohne Anm."),
        ("2026-10-15", "9:00–12:00", "Scratch Junior (Code Week)", "Bibl. Leubnitz-Neuostra, Corinthstr. 8", "frei", "6–9 J., Anmeldung: leubnitz-neuostra@bibo-dresden.de"),
        ("2026-10-15", "10:00–13:00", "Game-Design: Point'n'Click Adventure (Code Week)", "Bibl. Gruna, Papstdorfer Str. 13", "frei", "10–16 J., Anmeldung: 0351/2561037"),
        ("2026-10-20", "9:30–12:30", "Der magische Stift (2-Tage-Workshop)", "Bibl. Strehlen, Otto-Dix-Ring 61", "frei", "8–10 J., Anmeldung: strehlen-odc@bibo-dresden.de"),
        ("2026-10-21", "9:30–12:30", "Der magische Stift (Tag 2)", "Bibl. Strehlen, Otto-Dix-Ring 61", "frei", "8–10 J., Fortsetzung des Workshops"),
        ("2026-10-21", "14:00–18:00", "MakerBox (offen) – Neustadt", "Bibl. Neustadt, Königsbrücker Str. 26", "frei", "ab 3 J., ohne Anm."),
        ("2026-10-21", "15:00–16:30", "Maker-Mittwoch (offen, mit Personal) – Gorbitz", "Bibliothek Gorbitz, Merianplatz 4", "frei", "VR-Brillen, Nintendo Switch, Sphero-Roboter"),
        ("2026-10-23", "ganz tags", "Gaming-Geheimtipps mit Gregor Kartsios (Rocket Beans)", "Zentralbibliothek im Kulturpalast", "frei", "Videospiele-Abenteuer für Groß & Klein, Uhrzeit auf der Bibo-Seite"),
    ]
    return [{"d": d, "t": t, "title": ti, "venue": f"bibo · {addr.split(',')[0]}",
             "cost": c, "note": n, "url": U, "cat": "bibo"} for d, t, ti, addr, c, n in entries]

def zoo():
    out = []
    d = datetime.date(2026, 10, 10)
    while d <= datetime.date(2026, 10, 25):
        iso = d.isoformat()
        out.append({"d": iso, "t": "ab 11:00", "title": "Reviertreffpunkte & Fütterungen", "venue": "Zoo Dresden",
                    "cost": "inkl. Zoo-Eintritt", "note": "Täglich, kostenlos, ohne Anm. – mit Quiz-Rallye",
                    "url": "https://www.zoo-dresden.de/besuch-planen/treffpunkte-fuetterungen/", "cat": "zoo"})
        if d.weekday() in (1, 3, 5, 6):  # Di, Do, Sa, So
            out.append({"d": iso, "t": "10:30/11:30/14:30/16:00", "title": "Zookasper", "venue": "Zoo Dresden (Kasperhaus)",
                        "cost": "inkl. Zoo-Eintritt", "note": "Kasperletheater bis Ende Oktober",
                        "url": "https://www.zoo-dresden.de/fuer-kinder/", "cat": "zoo"})
        d += datetime.timedelta(days=1)
    out.append({"d": "2026-10-10", "t": "8:30–17:30", "title": "Herbstferien im Zoo (10.–25.10.)", "venue": "Zoo Dresden",
                "cost": "Zoo-Eintritt", "note": "Ferienprogramm: Aktionen & Zooschule, Details auf der Zoo-Website",
                "url": "https://www.zoo-dresden.de/aktuelles/veranstaltungen/", "cat": "zoo"})
    out.append({"d": "2026-10-31", "t": "10:00–18:30", "title": "Halloween im Zoo", "venue": "Zoo Dresden",
                "cost": "Zoo-Eintritt", "note": "Zauberhaftes Halloween-Event im Zoo",
                "url": "https://www.zoo-dresden.de/aktuelles/veranstaltungen/", "cat": "zoo"})
    return out

# ---------- Zusammenbau ----------
kinolino = parse_kinolino()
muehle = zschoner()
tsd_l = tsd()
bibo_l = bibo()
zoo_l = zoo()
all_events = kinolino + muehle + tsd_l + bibo_l + zoo_l
all_events.sort(key=lambda e: (e["d"], e["t"]))
print(f"KINOLINO: {len(kinolino)}, Mühle: {len(muehle)}, TSD: {len(tsd_l)}, Bibo: {len(bibo_l)}, Zoo: {len(zoo_l)} → gesamt {len(all_events)}")

def js_escape(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')

today = datetime.date.today().isoformat()
lines = [
    "// GENERIERT von scripts/generate-calendar.py – nicht von Hand editieren!",
    f"// Live-Quellen: kinolino.de/programm, zschoner-muehle.de/puppentheater · manuell: TSD, Bibo, Zoo (Stand 14.10.2026)",
    "const CALENDAR_EVENTS = [",
]
for i, e in enumerate(all_events):
    comma = "," if i < len(all_events) - 1 else ""
    lines.append(
        f'  {{ d: "{e["d"]}", t: "{js_escape(e["t"])}", title: "{js_escape(e["title"])}", '
        f'venue: "{js_escape(e["venue"])}", cost: "{js_escape(e["cost"])}", '
        f'note: "{js_escape(e["note"])}", url: "{e["url"]}", cat: "{e["cat"]}" }}{comma}'
    )
lines.append("];")
open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("calendar-data.js geschrieben:", OUT)
if not all_events:
    sys.exit(1)
