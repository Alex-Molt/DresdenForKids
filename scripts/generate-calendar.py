#!/usr/bin/env python3
"""Generiert calendar-data.js für DresdenForKids.

QUELLEN kommen aus der Registry in README.md (Abschnitt
"## Datenquellen für den Kalender (Registry)", JSON-Block).
Neue Quelle = neuer JSON-Eintrag in der README (per PR) + Parser-Schlüssel
aus PARSE_FNS. Nicht maschinenlesbare Seiten (JS-only): kind "browser"/"manual",
Ereignisse landen in calendar-extra.json (vom Cron/LLM gepflegt).

Aufruf:  python3 scripts/generate-calendar.py [--test <quelle-id>]
Prüfen:  node scripts/check-calendar.js
"""
import re, json, html as h, datetime, os, ssl, urllib.request, sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README = os.path.join(REPO_ROOT, "README.md")
EXTRA = os.path.join(REPO_ROOT, "calendar-extra.json")
OUT = os.path.join(REPO_ROOT, "calendar-data.js")
ctx = ssl.create_default_context()
TODAY = datetime.date.today()
WINDOW_START = TODAY - datetime.timedelta(days=10)
WINDOW_END = TODAY + datetime.timedelta(days=75)

MONTHS = {"jan": 1, "feb": 2, "märz": 3, "maerz": 3, "apr": 4, "mai": 5, "jun": 6,
          "jul": 7, "aug": 8, "sept": 9, "okt": 10, "nov": 11, "dez": 12,
          "januar": 1, "februar": 2, "maerz": 3, "märz": 3, "april": 4, "mai": 5,
          "juni": 6, "juli": 7, "august": 8, "september": 9, "oktober": 10,
          "november": 11, "dezember": 12}
KID_RE = re.compile(r"kinder|kind|familie|familien|jugend|ferien|schule|schule|halloween|fledermaus|puppent", re.I)


def raw_fetch(url, referer=None):
    headers = {"User-Agent": "Mozilla/5.0"}
    if referer:
        headers["Referer"] = referer
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=40, context=ctx) as r:
        raw = r.read().decode("utf-8", "ignore")
    # Wartungsseiten (HTTP 200, kein Event-Content): als Fehler behandeln,
    # damit der Backfill greift statt 0 Events in den Kalender zu schreiben.
    if "Wartungsarbeiten ist diese Seite momentan nicht erreichbar" in raw \
            or "Site down due to maintenance" in raw:
        raise RuntimeError("Quelle im Wartungsmodus (Maintenance-Page)")
    return raw


def to_text(raw):
    t = re.sub(r"<script.*?</script>", " ", raw, flags=re.S | re.I)
    t = re.sub(r"<style.*?</style>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<(br|/p|/div|/li|/h[1-6]|/tr|/td)[^>]*>", "\n", t, flags=re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = h.unescape(t)
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n", t)
    return t.strip()


def fetch(url, referer=None):
    return to_text(raw_fetch(url, referer))


def mk(d, t, title, venue, cost, note, url, cat):
    return {"d": d.isoformat() if hasattr(d, "isoformat") else d,
            "t": t, "title": title.strip(), "venue": venue,
            "cost": cost, "note": note, "url": url, "cat": cat}


def in_window(iso):
    return WINDOW_START.isoformat() <= iso <= WINDOW_END.isoformat()


def infer_year(day, month, ref=TODAY):
    """Nächstes Vorkommen von Tag.Monat ab (ref-30 Tage)."""
    for y in (ref.year, ref.year + 1):
        try:
            cand = datetime.date(y, month, day)
        except ValueError:
            continue
        if cand >= ref - datetime.timedelta(days=30):
            return y
    return ref.year + 1


# Veranstaltungenstypen, die per Definition nicht kindgerecht sind
# (auch wenn "Familie" etc. im Titel steht, z. B. Vortrag über die
# "Familie Simson" – das ist der Herstellername, kein Familien-Event).
ADULT_TYPE_RE = re.compile(r"vortrag|podiumsgespräch|symposium|fishbowl|unterhausdebatte|verkehrswende-duell", re.I)


def is_kid_event(title, cats=""):
    if ADULT_TYPE_RE.search(cats):
        return False
    return bool(KID_RE.search(title) or KID_RE.search(cats))


# ============================ PARSER ============================

def p_kinolino(src):
    U = "https://www.kinolino.de/programm"
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
    lines = fetch(U).splitlines()
    venues = set(VENUE_NAMES.keys())
    day_re = re.compile(r"^(Mo|Di|Mi|Do|Fr|Sa|So), (\d{2})\.(\d{2})\.(\d{4})$")
    time_re = re.compile(r"^(\d{2}:\d{2}) Uhr$")
    events, cur, i = [], None, 0
    while i < len(lines):
        line = lines[i].strip()
        m = day_re.match(line)
        if m:
            cur = f"{m.group(4)}-{m.group(3)}-{m.group(2)}"
            i += 1
            continue
        t = time_re.match(line)
        if t and cur:
            tm, j, venue, film_lines = t.group(1), i + 1, None, []
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
            if venue and " ".join(film_lines) and in_window(cur):
                events.append(mk(cur, tm, " ".join(film_lines), VENUE_NAMES[venue],
                                  "1 € + Museumseintritt" if venue.startswith("Museumskino")
                                  else "je nach Spielstätte (Kino ~3–5 €, Bibliotheksvorführungen oft frei)",
                                  "KINOLINO – Kinderfilmfest (Oktober)", U, "kinolino"))
            i = j + 1
            continue
        i += 1
    return events


def _month_num(name):
    """Monatname (voll oder abgekürzt, egal wie geschrieben) → Nummer."""
    n = name.lower().strip()
    if n in MONTHS:
        return MONTHS[n]
    for k, v in MONTHS.items():
        if n.startswith(k[:4]):
            return v
    return None


def p_muehle(src):
    U = "https://www.zschoner-muehle.de/puppentheater/"
    lines = fetch(U).splitlines()
    date_re = re.compile(r"^(?:\d{1,2} )?(\d{1,2})\. (\w+) (\d{4})$")
    time_re = re.compile(r"^(\d{2}:\d{2}): (.+)$")
    events, cur = [], None
    for line in lines:
        l = line.strip()
        m = date_re.match(l)
        if m:
            mon = _month_num(m.group(2))
            if mon:
                cur = f"{m.group(3)}-{mon:02d}-{int(m.group(1)):02d}"
            continue
        t = time_re.match(l)
        if t and cur and in_window(cur):
            tm, title = t.group(1), t.group(2).strip()
            is_tour = "mühlenführung" in title.lower()
            events.append(mk(cur, tm, title, "Zschoner Mühle",
                             "7 € / erm. 5 €" if is_tour else "Karten online (zschoner-muehle.de)",
                             "Erlebnismühlenführung – Dresdner Mühlenmuseum, Reservierung empfohlen" if is_tour
                             else "Puppentheater für die ganze Familie – Reservierung empfohlen",
                             U, "muehle"))
    return events


def p_tsd(src):
    U = src["url"]
    t = raw_fetch(U)
    blocks = re.split(r'<div class="event-list__event event-list__event--with-toggle', t)[1:]
    events, seen = [], set()
    for b in blocks:
        dm = re.search(r'event-list__date">(?:Mo|Di|Mi|Do|Fr|Sa|So)[^0-9]*(\d{1,2})\. (\w+?)\s*<div class="event-list__time">(\d{1,2}:\d{2})', b)
        tm = re.search(r'event-list__title">([^<]+)</h5>', b)
        st = re.search(r'event-list__status-info">([^<]*)</div>', b)
        if not (dm and tm):
            continue
        day, mon = int(dm.group(1)), dm.group(2).lower()[:4]
        if mon not in MONTHS:
            continue
        y = infer_year(day, MONTHS[mon])
        d = datetime.date(y, MONTHS[mon], day)
        if not in_window(d.isoformat()):
            continue
        title = h.unescape(tm.group(1)).strip()
        booking = h.unescape(st.group(1)).strip() if st else ""
        # Beschreibung (Alter, Dauer, Anm.) aus Akkordeon
        desc = ""
        acc = re.search(r'event-list__accordion-content[^>]*>(.*?)</div>\s*<div class="event-list__event ', b, re.S)
        if not acc:
            acc = re.search(r'event-list__accordion-content[^>]*>(.*)', b, re.S)
        if acc:
            desc = h.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", acc.group(1)))).strip()
            desc = re.sub(r"^Mit Spielen\s*", "", desc)
            desc = desc[:180]
        key = (d.isoformat(), dm.group(2), title)
        if key in seen:
            continue
        seen.add(key)
        note = booking if booking else "Offenes Angebot"
        if desc:
            note = f"{note} · {desc}" if booking else desc
        events.append(mk(d, dm.group(3), title, "Technische Sammlungen (TSD)",
                         "Museumseintritt (fr ab 12 Uhr frei)", note, U, "tsd"))
    return events


def p_zoo(src):
    """Zoo-Veranstaltungen: Zeile 1 'DD. Monat YYYY' (ggf. '- DD. Monat YYYY'),
    Zeile 2 'HH:MM [- HH:MM] Uhr Titel'."""
    U = src["url"]
    lines = fetch(U).splitlines()
    date_re = re.compile(r"^(\d{1,2})\. (\w+) (\d{4})(?:\s*-\s*(\d{1,2})\. (\w+) (\d{4}))?$")
    time_re = re.compile(r"^(\d{1,2}:\d{2}(?:\s*-\s*\d{1,2}:\d{2})?) Uhr\s+(.+)$")
    events, cur = [], None
    for line in lines:
        l = line.strip()
        m = date_re.match(l)
        if m:
            mon1 = _month_num(m.group(2))
            if not mon1:
                cur = None
                continue
            cur = f"{m.group(3)}-{mon1:02d}-{int(m.group(1)):02d}"
            cur_end = None
            if m.group(4):
                mon2 = _month_num(m.group(5))
                if mon2:
                    cur_end = f"{m.group(6)}-{mon2:02d}-{int(m.group(4)):02d}"
            cur = (cur, cur_end)
            continue
        t = time_re.match(l)
        if t and cur and in_window(cur[0]):
            tm, title = t.group(1), t.group(2).strip()
            if not is_kid_event(title):
                continue
            rng = f"{cur[0][8:]}–{cur[1][8:]}" if cur[1] and cur[1] != cur[0] else ""
            events.append(mk(cur[0], tm, title, "Zoo Dresden", "Zoo-Eintritt",
                             f"Veranstaltung {rng}" if rng else "Veranstaltung im Zoo",
                             U, "zoo"))
    return events


def p_tjg(src):
    # Kind-Filter: monatlicher Erwachsenen-Treff (kein Kinder-Event)
    EXCLUDE = ("freiraum",)
    items = []
    for page in range(0, 6):
        data = json.loads(raw_fetch(f"https://www.tjg-dresden.de/api/events?page={page}&limit=50"))
        batch = data.get("items", [])
        items += batch
        if len(batch) < 50:
            break
    events, seen = [], set()
    for i in items:
        if any(x in i.get("title", "").lower() for x in EXCLUDE):
            continue
        for dd in i.get("event_dates", []):
            iso = dd["start_date"][:10]
            if not in_window(iso):
                continue
            key = (iso, dd["start_date"][11:16], i["title"])
            if key in seen:
                continue
            seen.add(key)
            pr = i.get("prices", [])
            cost = "–"
            if pr:
                cost = f"{min(p['amount'] for p in pr)}–{max(p['amount'] for p in pr)} €"
            events.append(mk(iso, dd["start_date"][11:16], i["title"],
                             "tjg. Theater Junge Generation", cost,
                             "Tickets: tjg-dresden.de",
                             "https://www.tjg-dresden.de/spielplan/", "theater"))
    return events


def p_august(src):
    """AUGUST-Theater-Spielplan: Block = Titelzeile(n) / 'Wochentag, DD. Monat YYYY , HH.MM Uhr' / Preis / 'Für Kinder und Familien'."""
    U = src["url"]
    lines = fetch(U).splitlines()
    lines = [l.strip() for l in lines]
    date_re = re.compile(r"^(Montag|Dienstag|Mittwoch|Donnerstag|Freitag|Samstag|Sonntag), (\d{1,2})\. (\w+) (\d{4}) , (\d{1,2})\.(\d{2}) Uhr$")
    events, seen = [], set()
    for i, l in enumerate(lines):
        m = date_re.match(l)
        if not m:
            continue
        mon = _month_num(m.group(3))
        if not mon:
            continue
        d = f"{m.group(4)}-{mon:02d}-{int(m.group(2)):02d}"
        if not in_window(d):
            continue
        # Titel: Zeile(n) bis zur letzten 'Spielplan …' / vorherigen Datumszeile
        title = None
        for j in range(i - 1, max(i - 6, -1), -1):
            cand = lines[j]
            if not cand:
                continue
            if date_re.match(cand) or cand.startswith("Spielplan"):
                break
            if re.match(r"^[\d,]+(,\d+)? €", cand) or cand.startswith("Für ") or cand in ("Alle löschen", "Suche"):
                continue
            if len(cand) >= 4:
                title = cand
            break
        if not title:
            continue
        # Preis + Kinder-Marker: nächste 3 Zeilen
        tail = " ".join(lines[i + 1:i + 4])
        price_m = re.search(r"([\d,]+(?:,\d+)? €(?:\s*-\s*[\d,]+(?:,\d+)? €)?)", tail)
        kids = "Für Kinder und Familien" in tail
        if not kids:
            continue
        key = (d, m.group(5) + m.group(6), title)
        if key in seen:
            continue
        seen.add(key)
        events.append(mk(d, f"{m.group(5)}:{m.group(6)}", title, "AUGUST Theater",
                         price_m.group(1) if price_m else "–",
                         "Kinder- & Familienstück · August Theater, Bürgerstraße (Dresden-Plauen)",
                         "https://august-theater-dresden.de/spielplan/", "theater"))
    return events


def p_vollmann(src):
    U = src["url"]
    data = json.loads(raw_fetch(U, referer="https://www.puppentheater-vollmann.de/spielplan.html"))
    events = []
    for e in data:
        iso = e["start"][:10]
        if not in_window(iso):
            continue
        title = re.sub(r"\s*\(\d+ Restkarten\)$", "", e.get("title", "")).strip()
        events.append(mk(iso, e["start"][11:16], title, "Puppentheater Alte Feuerwache",
                         "Karten: puppentheater-vollmann.de",
                         "Puppentheater für die ganze Familie, Pillnitz",
                         "https://www.puppentheater-vollmann.de/spielplan.html", "theater"))
    return events


def _schl_base(url):
    m = re.match(r"(https?://[^/]+)", url)
    return m.group(1) if m else url


def p_schl_list(src):
    """Schlösserland list-item-Layout (eigene Subdomains: Moritzburg, Rochlitz, Gnandstein, Nossen, Albrechtsburg, Zwinger)."""
    U = src["url"]
    base = _schl_base(U)
    t = raw_fetch(U)
    blocks = re.split(r'<div class="grid-list-item ', t)[1:]
    date_re = re.compile(r"^(?:Mo|Di|Mi|Do|Fr|Sa|So) (\d{1,2})\.(\d{1,2})\.(\d{4})(?:\s+bis\s+\w{1,3} (\d{1,2})\.(\d{1,2})\.(\d{4}))?$")
    time_re = re.compile(r"^(\d{1,2}):(\d{2})(?:\s*-\s*(\d{1,2}):(\d{2}))?(?:\s*Uhr)?$")
    events = []
    for b in blocks:
        title = re.search(r'list-item-headline-inner">([^<]+)<', b)
        link = re.search(r'href="([^"]*detailseite/event/[^"]+)"', b)
        if not title:
            continue
        title = h.unescape(title.group(1)).strip()
        cats = " ".join(re.findall(r'class="category[^"]*"[^>]*title="([^"]*)"', b))
        metas = [h.unescape(re.sub(r"\s+", " ", m)).strip()
                 for m in re.findall(r'<p>([^<]*)</p>', b)]
        d = tm = None
        for meta in metas:
            dm = date_re.match(meta)
            if dm:
                if dm.group(4):  # Zeitraum (Dauerausstellung etc.)
                    try:
                        e2 = datetime.date(int(dm.group(6)), int(dm.group(5)), int(dm.group(4)))
                        d1 = datetime.date(int(dm.group(3)), int(dm.group(2)), int(dm.group(1)))
                        if (e2 - d1).days > 60:
                            continue  # Dauerausstellung überspringen
                    except ValueError:
                        continue
                d = datetime.date(int(dm.group(3)), int(dm.group(2)), int(dm.group(1)))
                continue
            tmm = time_re.match(meta)
            if tmm and not tm:
                tm = tmm.group(0).replace(" Uhr", "").strip()
        if not d or not in_window(d.isoformat()):
            continue
        if not is_kid_event(title, cats):
            continue
        url_d = (link.group(1) if link else U)
        if url_d.startswith("/"):
            url_d = base + url_d
        events.append(mk(d, tm or "–", title, src["venue"], "siehe Veranstaltungsdetailseite",
                         f"Kategorien: {cats}" if cats else "Veranstaltung", url_d, src.get("cat", "umkreis")))
    return events


def p_schl_acc(src):
    """Schlösserland Venue-Seiten mit Event-Akkordeon (Königstein, Freudenstein …)."""
    U = src["url"]
    t = raw_fetch(U)
    pat = re.compile(
        r'([MoDiMiFrSaSo]) (\d{1,2})\.(\d{1,2})\.(\d{4}) (\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2}) Uhr'
        r'[^|]*\|\s*([^<]+?)<br>\s*<a href="([^"]+)"[^>]*>([^<]+)<')
    events = []
    for m in pat.finditer(t):
        d = datetime.date(int(m.group(4)), int(m.group(3)), int(m.group(2)))
        if not in_window(d.isoformat()):
            continue
        title = h.unescape(m.group(11)).strip()
        cats = h.unescape(m.group(9)).strip()
        if not is_kid_event(title, cats):
            continue
        url_d = m.group(10)
        if url_d.startswith("/"):
            url_d = _schl_base(U) + url_d
        events.append(mk(d, f"{m.group(5)}:{m.group(6)}", title, src["venue"],
                         "siehe Veranstaltungsdetailseite",
                         f"Kategorien: {cats}", url_d, src.get("cat", "umkreis")))
    return events


# Kind-Events ohne typisches Kinder-Keyword im Titel (Museumsmausfest =
# Familienfest der Museumsmaus Flitzi; typisch nur "Aktion").
VM_KID_ALIAS = re.compile(r"Museumsmausfest|Flitzi", re.I)


def p_verkehrsmuseum(src):
    U = src["url"]
    t = raw_fetch(U)
    events = []
    for b in re.split(r'itemtype="http://schema.org/Event"', t)[1:]:
        name = re.search(r'<h3[^>]*itemprop="name"[^>]*>\s*(?:<a[^>]*>)?\s*([^<]+?)\s*(?:</a>)?\s*</h3>', b, re.S)
        tim = re.search(r'<time[^>]*itemprop="startDate"[^>]*>([^<]+)</time>', b)
        typ = re.search(r'<p class="type[^"]*">\s*([^<]+?)\s*</p>', b)
        link = re.search(r'href="(https?://[^"]+/de/termine/[^"]+)"', b)
        if not (name and tim):
            continue
        title = h.unescape(name.group(1)).strip()
        tm_raw = tim.group(1).strip()
        dm = re.match(r"(\d{1,2})\.(\d{1,2})\.(\d{4})(?:\s*,\s*(\d{1,2}:\d{2}(?:\s*-\s*\d{1,2}:\d{2})?))?", tm_raw)
        if not dm or dm.group(2) == "27":
            continue  # Zeitraum/Dauerausstellung (z. B. „29.05.2026 - 30.05.2027")
        d = datetime.date(int(dm.group(3)), int(dm.group(2)), int(dm.group(1)))
        if not in_window(d.isoformat()):
            continue
        if not (is_kid_event(title, typ.group(1) if typ else "") or VM_KID_ALIAS.search(title)):
            continue
        events.append(mk(d, dm.group(4) or "–", title, "Verkehrsmuseum Dresden",
                         "siehe Detailseite", (typ.group(1).strip() if typ else ""),
                         link.group(1) if link else U, "museum"))
    return events


# ============================ CODE WEEK (CrossMedia Tour) ============================

def p_codeweek(src):
    """Code Week Dresden (CrossMedia Tour e.V.): pro Kurs-Panel
    <h3.wp-block-post-title><a href>Titel</a></h3> + 2x <h6><span.value> (Datum, Ort).
    Mehr-tägige Kurse: '15.10. – 16.10.26'. Detailseite: Uhrzeit + Altersempfehlung."""
    U = src["url"]
    raw = raw_fetch(U)
    segs = re.split(r'kurstermin-panel', raw)[1:]
    events, seen = [], set()
    for s in segs:
        mt = re.search(r'<h3[^>]*wp-block-post-title[^>]*>\s*<a href="([^"]+)"[^>]*>([^<]+)</a>', s)
        if not mt:
            continue
        url_c, title = mt.group(1), h.unescape(mt.group(2)).strip()
        vals = re.findall(r'<h6[^>]*is-dynamic-field[^>]*>\s*<span class="value">\s*(.*?)\s*</span>\s*</h6>', s)
        if len(vals) < 2:
            continue
        dstr, venue = h.unescape(vals[0]).strip(), h.unescape(vals[1]).strip()
        # '15.10.26' oder '15.10. – 16.10.26'
        dm = re.match(r"(\d{1,2})\.(\d{1,2})\.\s*(?:–|-|&#8211;)?\s*(?:(\d{1,2})\.(\d{1,2})\.)?(\d{2})", dstr.replace("&#8211;", "–"))
        if not dm:
            continue
        y = 2000 + int(dm.group(5))
        d = datetime.date(y, int(dm.group(2)), int(dm.group(1)))
        if not in_window(d.isoformat()):
            continue
        rng = ""
        if dm.group(3):
            d_end = datetime.date(y, int(dm.group(4)), int(dm.group(3)))
            rng = f"–{d_end.day:02d}.{d_end.month:02d}"
        key = (d.isoformat(), title, venue)
        if key in seen:
            continue
        seen.add(key)
        # Detailseite: Uhrzeit + Altersempfehlung (Fehler → "–", Kurs bleibt gelistet)
        tm, age = "–", ""
        try:
            dtxt = fetch(url_c)
            # Zeit: 'HH:MM – HH:MM [Uhr]' (Uhr optional, auch bei 'Mo bis Fr 10:00 – 15:00')
            mtm = re.search(r"(\d{1,2}:\d{2})\s*[–-]\s*(\d{1,2}:\d{2})(?:\s*Uhr)?", dtxt)
            if not mtm:
                mtm = re.search(r"(\d{1,2}:\d{2})\s*Uhr", dtxt)
            if mtm:
                tm = mtm.group(1) + (f" - {mtm.group(2)}" if mtm.group(2) else "")
            mage = re.search(r"Altersempfehlung(?:\svon)?\s+([\d,– ]{1,20}?)\s*(?:Jahren|Jahre)\b", dtxt)
            if mage:
                age = mage.group(1).strip().rstrip(",")
        except Exception:
            pass
        note = "Code Week Dresden · kostenlos · CrossMedia Tour e.V."
        if age:
            note = f"Alter: {age} J. · {note}"
        if rng:
            note += f" · {d.day:02d}.{d.month:02d}{rng}"
        events.append(mk(d, tm, title, venue, "frei", note, url_c, "event"))
    return events


PARSE_FNS = {
    "kinolino": p_kinolino,
    "muehle": p_muehle,
    "tsd": p_tsd,
    "zoo": p_zoo,
    "tjg-api": p_tjg,
    "august": p_august,
    "vollmann-json": p_vollmann,
    "schloesserland-list": p_schl_list,
    "schloesserland-accordion": p_schl_acc,
    "verkehrsmuseum": p_verkehrsmuseum,
    "codeweek": p_codeweek,
}


# ============================ REGISTRY (README) ============================

def read_registry():
    md = open(README, encoding="utf-8").read()
    m = re.search(r"## Datenquellen für den Kalender \(Registry\).*?```json\s*\n(.*?)\n```", md, re.S)
    if not m:
        sys.exit("REGISTRY nicht gefunden: README.md, Abschnitt '## Datenquellen für den Kalender (Registry)' mit JSON-Block.")
    reg = json.loads(m.group(1))
    return [r for r in reg if r.get("enabled", True)]


def load_extra():
    """calendar-extra.json: manuelle Events (Quellen ohne parsebare Seiten, z. B. bibo)
    + optionale Anreicherung (gleiche d/t/title ersetzen live-Felder).
    Format: {"$note": "...", "events": [ {...} ]}  ODER  [ {...}, ... ]
    """
    if not os.path.exists(EXTRA):
        return []
    try:
        data = json.load(open(EXTRA, encoding="utf-8"))
        return data.get("events", []) if isinstance(data, dict) else data
    except Exception as e:
        print(f"⚠️ calendar-extra.json fehlerhaft, ignoriert: {e}")
        return []


def load_prev(path):
    """Vorheriges calendar-data.js (veröffentlichte Events) aus den JS-Zeilen
    parsen – für den Backfill, wenn eine Live-Quelle fehlt. Fehlende Felder
    (z. B. cost/note) kommen als leerer String zurück."""
    if not os.path.exists(path):
        return []
    out = []
    try:
        raw = open(path, encoding="utf-8").read()
    except Exception:
        return []
    for m in re.finditer(
        r'\{\s*d:\s*"([^"]+)"\s*,\s*t:\s*"([^"]*)"\s*,\s*title:\s*"((?:[^"\\]|\\.)*)"\s*,'
        r'\s*venue:\s*"((?:[^"\\]|\\.)*)"\s*,\s*cost:\s*"((?:[^"\\]|\\.)*)"\s*,'
        r'\s*note:\s*"((?:[^"\\]|\\.)*)"\s*,\s*url:\s*"((?:[^"\\]|\\.)*)"\s*,'
        r'\s*cat:\s*"((?:[^"\\]|\\.)*)"\s*\}',
        raw, re.S):
        d, t, title, venue, cost, note, url, cat = m.groups()

        def un(s):
            # jse() escapet nur \ → \\ und " → \" – Single-Pass-Rückgängig
            # (zwei sequentielle replaces würden \"-Sequenzen brechen).
            return re.sub(r"\\(.)", r"\1", s)

        out.append({"d": d, "t": t, "title": un(title), "venue": un(venue),
                    "cost": un(cost), "note": un(note), "url": un(url), "cat": cat})
    return out


def main():
    test_id = None
    if "--test" in sys.argv:
        test_id = sys.argv[sys.argv.index("--test") + 1]

    registry = read_registry()
    print(f"Registry: {len(registry)} aktive Quellen (aus README.md)")

    all_events = []
    stats = {}
    failed = set()
    for src in registry:
        if test_id and src["id"] != test_id:
            continue
        parser = PARSE_FNS.get(src["parser"])
        if parser is None:
            print(f"  ⚠️ {src['id']}: unbekannter Parser '{src['parser']}' – übersprungen")
            continue
        try:
            evs = parser(src)
            stats[src["id"]] = len(evs)
            all_events += evs
            print(f"  ✓ {src['id']:<28} {len(evs):>3} Events")
        except Exception as e:
            stats[src["id"]] = f"FEHLER: {e}"
            failed.add(src["id"])
            print(f"  ✗ {src['id']:<28} FEHLER: {e}")

    # Backfill: eine Quelle, die gefehlt hat, liefert sonst 0 Events.
    # Die vorherigen (veröffentlichten) Events derselben Quelle werden aus
    # calendar-data.js (Stand gestern) nachgeladen, damit ein temporärer
    # Source-Ausfall (Wartung, 503, Timeout) die Live-Daten NICHT löscht.
    # Zuordnung über die Herkunfts-Domain der Event-URL → Registry-URL,
    # weil viele Parser Detailseiten-URLs ausgeben (tjg, Vollmann,
    # Schlösserland, Code Week). Stale Events behalten ihren d/t; das
    # Fenster unten filtert überfällige weg, Dedupe entfernt Überschneidungen.
    def _origin(u):
        m2 = re.match(r"https?://([^/]+)", u or "")
        return m2.group(1) if m2 else ""

    if failed and not test_id:
        stale = load_prev(OUT)
        if stale:
            # origin → source-id für alle fehlgeschlagenen Quellen
            failed_origin = {_origin(s["url"]): s["id"] for s in registry if s["id"] in failed}
            by_src = {sid: [] for sid in failed}
            for e in stale:
                sid = failed_origin.get(_origin(e.get("url", "")))
                if sid and in_window(e["d"]):
                    by_src[sid].append(e)
            kept = 0
            for sid, evs in sorted(by_src.items()):
                if not evs:
                    continue
                all_events += evs
                stats[sid] = f"FEHLER→Backfill({len(evs)}): {stats.get(sid, '')}"
                print(f"  ↩ {sid:<28} Backfill {len(evs)} Events aus vorherigem calendar-data.js")
                kept += len(evs)
            print(f"  ↩ Backfill gesamt: {kept} Events aus {len(failed)} fehlgeschlagenen Quellen")

    extra = load_extra()
    if not test_id:
        print(f"  ✓ calendar-extra.json (manuell)      {len(extra):>3} Events")
        all_events += extra

    # Dedupe mit Vorrang für manuelle Events (calendar-extra):
    # Gleiche (d, t, title, venue) → das manuelle Event gewinnt (reichere Daten).
    for e in extra:
        e["_extra"] = True
    all_events.sort(key=lambda e: 0 if e.get("_extra") else 1)  # extra zuerst
    seen, out = set(), []
    for e in all_events:
        k = (e["d"], e["t"], e["title"].lower(), e["venue"].lower())
        if k in seen:
            continue
        seen.add(k)
        out.append(e)
    out.sort(key=lambda e: (e["d"], e["t"], e["title"]))
    for e in out:
        e.pop("_extra", None)

    if test_id:
        print(f"\nTEST {test_id}: {len(out)} Events")
        for e in out:
            print(f"  {e['d']} {e['t']:<12} {e['title'][:55]} | {e['venue'][:40]}")
        return

    def jse(s):
        return str(s).replace("\\", "\\\\").replace('"', '\\"')

    active = [s["id"] for s in registry]
    lines = [
        "// GENERIERT von scripts/generate-calendar.py – nicht von Hand editieren!",
        f"// Quellen: Registry in README.md ({len(active)} Quellen) + calendar-extra.json (Stand {TODAY.isoformat()})",
        "const CALENDAR_EVENTS = [",
    ]
    for i, e in enumerate(out):
        comma = "," if i < len(out) - 1 else ""
        lines.append(
            f'  {{ d: "{e["d"]}", t: "{jse(e["t"])}", title: "{jse(e["title"])}", '
            f'venue: "{jse(e["venue"])}", cost: "{jse(e["cost"])}", '
            f'note: "{jse(e["note"])}", url: "{jse(e["url"])}", cat: "{jse(e["cat"])}" }}{comma}'
        )
    lines.append("];")
    # Sanity-Guard: Ein massiver Event-Count-Abfall (z. B. > 40 %) deutet
    # auf einen Parser-Bug oder mehrere Source-Ausfälle hin – dann NICHT
    # schreiben, sondern abbrechen, damit die letzten guten Daten bleiben.
    prev = load_prev(OUT)
    if prev and len(out) < 0.6 * len(prev):
        print(f"\n⛔ ABORT: {len(out)} Events – aber vorher {len(prev)}. "
              f"Abfall > 40 %, calendar-data.js NICHT überschrieben.")
        sys.exit(1)
    open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(f"\ngesamt: {len(out)} unique Events → {OUT}")
    # Backfill-Quellen sind „gelöst" (alte Daten erhalten) → kein Fehlschlag.
    # Ein down-gegangener Source ohne Vor-Events verliert nichts. Der
    # 40%-Guard oben ist der eigentliche Schutz gegen massiven Datenverlust;
    # hart abbrechen, wenn garnichts mehr da wäre (katastrophaler Parser-Bug).
    if not out:
        print("⛔ KEINE Events generiert – calendar-data.js NICHT überschrieben.")
        sys.exit(1)


if __name__ == "__main__":
    main()
