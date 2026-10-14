# 🎪 Dresden for Kids

Statische Seite mit einer kuratierten Liste von **Events, Museen, Bibliotheken, Zoo & Ausflügen für Kinder in und um Dresden** – auf [GitHub Pages](https://alex-molt.github.io/DresdenForKids/) deployed.

- **Repo:** https://github.com/Alex-Molt/DresdenForKids
- **Seite:** https://alex-molt.github.io/DresdenForKids/

## Aufbau

| Datei | Zweck |
|---|---|
| `index.html` | Seiten-Shell (Hero, Filter, Grid, Footer) |
| `kalender.html` / `kalender.js` | **Tages-Kalender-Subseite** – Events ab heute, pro Tag |
| `style.css` | Look & Feel |
| `events.js` | **Datenquelle: Orte & Locations** (Karten auf der Startseite) |
| `app.js` | Rendert die Karten + Filter-Logik |
| `calendar-data.js` | **Datenquelle: konkrete Termine** (Kalender-Subseite) – generiert |
| `calendar-extra.json` | **Manuelle Events** (Quellen ohne parsebare Seiten) – von Cron/PR gepflegt |
| `scripts/generate-calendar.py` | Generiert `calendar-data.js` aus der **Quellen-Registry in dieser README** |
| `scripts/check-calendar.js` | Validiert `calendar-data.js` (Dups, Format, Count) |
| `.github/workflows/deploy.yml` | GitHub-Pages-Deploy (bei jedem Push auf `main`) |

## Wie man Änderungen einbringt (nur per PR!)

**`main` ist geschützt: direkter Push ist für niemanden möglich – auch nicht für den Repo-Owner.** Änderungen laufen ausschließlich über einen Pull Request.

```bash
git clone https://github.com/Alex-Molt/DresdenForKids.git
cd DresdenForKids
git checkout -b change/beschreibung   # neue Branch
# … Dateien ändern …
git add -A
git commit -m "Beschreibung der Änderung"
git push origin change/beschreibung
# dann auf GitHub PR öffnen (GitHub zeigt einen „Compare & pull request“-Button an)
```

Nach Merge in `main` deployt der GitHub-Pages-Workflow automatisch.

### Neue Location / Karte (Startseite)

1. `events.js` öffnen.
2. Einen neuen Eintrag in das `EVENTS`-Array hängen (Template):

```js
{
  name: "Name des Ortes / Events",
  category: "museum", // museum | zoo | bibliothek | park | umkreis | event
  age: "Gut ab ca. X Jahren",
  address: "Straße, PLZ Ort",
  hours: "Di–Fr 9–17 Uhr …",
  price: "Erw. 8 €, Kinder frei …",
  highlight: "1–2 Sätze: Was macht das für Kinder spannend? Besonderheiten?",
  booking: "keine" | "Telefon …" | "Online über …",
  url: "https://…",
  urlLabel: "Website",        // optional
  checked: "2026-10-14",      // Datum der letzten Prüfung
  note: "⚠️ Optional: Warnhinweis (z. B. Schließung, Umbau)"  // optional
}
```

### Neue konkrete Termine (Kalender)

**Wichtig:** Der Generator liest seine Quellen aus der **Registry weiter unten** (JSON-Block in dieser README). Eine neue Quelle = neuer JSON-Eintrag hier + (falls kein Parser vorhanden) ein Parser in `scripts/generate-calendar.py` (`PARSE_FNS`) – beides in **einem PR**.

1. `scripts/generate-calendar.py` anpassen (falls neue Parser-Logik nötig).
2. `python3 scripts/generate-calendar.py` → schreibt `calendar-data.js` neu.
3. `node scripts/check-calendar.js` → Validierung (Dups, Format, Tages-Count).
4. PR öffnen.

## Datenquellen für den Kalender (Registry)

Der Generator (`scripts/generate-calendar.py`) liest **nur** diese Liste. Neue Quelle = JSON-Zeile hier ergänzen (per PR) und `parser` aus `PARSE_FNS` wählen.
`"enabled": false` deaktiviert eine Quelle ohne Löschen. `kind: "browser" | "manual"` = nicht maschinenlesbar (JS-only): Events dafür in `calendar-extra.json` pflegen (Format siehe dort), nicht in die Registry-Parserei.

```json
[
  {"id": "kinolino", "parser": "kinolino", "url": "https://www.kinolino.de/programm", "venue": "KINOLINO (diverse)", "cat": "kinolino", "enabled": true, "note": "Filmtage-Tabelle, ~2 Wochen im Oktober"},
  {"id": "muehle", "parser": "muehle", "url": "https://www.zschoner-muehle.de/puppentheater/", "venue": "Zschoner Mühle", "cat": "muehle", "enabled": true, "note": "Kalendarium: Datum-Zeile + HH:MM: Titel"},
  {"id": "tsd", "parser": "tsd", "url": "https://tsd.de/programm/veranstaltungen/ferienprogramm", "venue": "Technische Sammlungen (TSD)", "cat": "tsd", "enabled": true, "note": "event-list-Blöcke; Jahr wird inferiert; Anm. 0351 488 7272"},
  {"id": "zoo", "parser": "zoo", "url": "https://www.zoo-dresden.de/aktuelles/veranstaltungen/", "venue": "Zoo Dresden", "cat": "zoo", "enabled": true, "note": "Text-Liste 'TT. Monat YYYY … Uhr' + Titel; nur kindgerechte Einträge (Keyword-Filter)"},
  {"id": "tjg", "parser": "tjg-api", "url": "https://www.tjg-dresden.de/api/events?page=0&limit=50", "venue": "tjg. Theater Junge Generation", "cat": "theater", "enabled": true, "note": "JSON-API, paginiert (page=0..5); items[].event_dates[] mit allen Aufführungen, prices[]"},
  {"id": "august", "parser": "august", "url": "https://august-theater-dresden.de/spielplan/", "venue": "AUGUST Theater", "cat": "theater", "enabled": true, "note": "server-rendered; nur Stücke mit 'Für Kinder und Familien'"},
  {"id": "feuerwache", "parser": "vollmann-json", "url": "https://www.puppentheater-vollmann.de/pluginAppObj/pluginAppObj_35_63/fullcalendar.php?file=0", "venue": "Puppentheater Alte Feuerwache", "cat": "theater", "enabled": true, "note": "FullCalendar-JSON (Referer: /spielplan.html nötig); Titel kann '(N Restkarten)' enthalten"},
  {"id": "verkehrsmuseum", "parser": "verkehrsmuseum", "url": "https://www.verkehrsmuseum-dresden.de/de/termine", "venue": "Verkehrsmuseum Dresden", "cat": "museum", "enabled": true, "note": "schema.org-Event-Teaser (name/startDate/type)"},
  {"id": "moritzburg", "parser": "schloesserland-list", "url": "https://www.schloss-moritzburg.de/de/veranstaltungen-ausstellungen/", "venue": "Schloss Moritzburg", "cat": "umkreis", "enabled": true, "note": "grid-list-item-Layout; Dauerausstellungen (Laufzeit > 60 Tage) werden übersprungen"},
  {"id": "koenigstein", "parser": "schloesserland-accordion", "url": "https://www.schloesserland-sachsen.de/de/schloesser-burgen-gaerten/festung-koenigstein/", "venue": "Festung Königstein", "cat": "umkreis", "enabled": true, "note": "eigene Seite festung-koenigstein.de ist JS-only → Schlösserland-Venue-Seite mit Event-Akkordeon"},
  {"id": "freudenstein", "parser": "schloesserland-accordion", "url": "https://www.schloesserland-sachsen.de/de/schloesser-burgen-gaerten/schloss-freudenstein/", "venue": "Schloss Freudenstein (Freiberg)", "cat": "umkreis", "enabled": true, "note": "Schlösserland-Venue-Seite (Akkordeon)"},
  {"id": "rochlitz", "parser": "schloesserland-list", "url": "https://www.schloss-rochlitz.de/de/veranstaltungen-ausstellungen/", "venue": "Schloss Rochlitz", "cat": "umkreis", "enabled": true, "note": "grid-list-item-Layout"},
  {"id": "gnandstein", "parser": "schloesserland-list", "url": "https://www.burg-museum-gnandstein.de/de/veranstaltungen-ausstellungen/", "venue": "Burg Gnandstein", "cat": "umkreis", "enabled": true, "note": "grid-list-item-Layout"},
  {"id": "nossen", "parser": "schloesserland-list", "url": "https://www.schloss-nossen.de/de/veranstaltungen-ausstellungen/", "venue": "Schloss Nossen", "cat": "umkreis", "enabled": true, "note": "grid-list-item-Layout"},
  {"id": "albrechtsburg", "parser": "schloesserland-list", "url": "https://www.albrechtsburg-meissen.de/de/veranstaltungen-ausstellungen/", "venue": "Albrechtsburg Meissen", "cat": "umkreis", "enabled": true, "note": "grid-list-item-Layout"},
  {"id": "zwinger", "parser": "schloesserland-list", "url": "https://www.der-dresdner-zwinger.de/de/dresdner-zwinger/veranstaltungen-ausstellungen/", "venue": "Dresdner Zwinger", "cat": "museum", "enabled": true, "note": "grid-list-item-Layout; u. a. Kinderkonzerte im Wallpavillon"},
  {"id": "oskarshausen", "parser": null, "url": "https://www.oskarshausen.de/events/", "venue": "Oskarshausen (Freital)", "cat": "umkreis", "enabled": true, "kind": "browser", "note": "JS-only, keine Termine im HTML → Events via Browser-Check in calendar-extra.json (z. B. Schaudrechseln, Frühstück am So., Gruselhausen)"}
]
```

**Parser-Schlüssel (`PARSE_FNS` in `scripts/generate-calendar.py`):** `kinolino`, `muehle`, `tsd`, `zoo`, `tjg-api`, `august`, `vollmann-json`, `schloesserland-list` (grid-list-item), `schloesserland-accordion` (Venue-Seite), `verkehrsmuseum`. Neue Parser: Funktion mit Signatur `def p_name(src) -> [event-dicts]` schreiben und in `PARSE_FNS` eintragen.

**Event-Format (wird in `calendar-data.js` geschrieben):** `{"d": "YYYY-MM-DD", "t": "HH:MM", "title": …, "venue": …, "cost": …, "note": …, "url": …, "cat": "tsd|zoo|bibo|kinolino|muehle|theater|museum|umkreis|event"}`

**Kind-Filter:** Parser mit Keyword-Filter (Schlösserland, Zoo, Verkehrsmuseum, AUGUST) nehmen nur Einträge mit Kinder-/Familien-Keywords (Titel oder Kategorien) auf. Tjg./Vollmann/Mühle/KINOLINO sind per Definition kindgerecht.

## Kategorien

| Key | Label |
|---|---|
| `museum` | 🏛️ Museen & Kultur |
| `zoo` | 🦁 Zoo & Tiere |
| `bibliothek` | 📚 Bibliotheken |
| `park` | 🌳 Parks & Gärten |
| `umkreis` | 🚗 Umkreis (max. ~1,5 h) |
| `event` | 🎉 Special Events / Ferienprogramme |

## Regeln & Abspür-Prinzip

- **Alle Angaben ohne Gewähr** – jedes Event trägt ein `checked`-Datum (letzter Fakten-Check auf der Original-Website).
- **Fakten vor der Aufnahme:** Öffnungszeiten, Preise, Altersgrenzen und Schließungen immer auf der offiziellen Seite prüfen (dresden.de, tsd.de, zoo-dresden.de, bibo-dresden.de, …).
- **Kinder-/Familien-Filter:** Nur aufnehmen, was real für Kinder bzw. Familien relevant ist (Alter, Angebote, Kosten). Kein reiner Durchlauf.
- **Alter ehrlich labeln:** „ab X J.“, „ab Kl. Y“ (5 ≈ Kl. 1, 10 ≈ Kl. 5), „Jahrgang ZZZZ“ – bei Unsicherheit lieber breit formulieren.
- **Kürzere Warnungen** (Sanierung, Schließung, „letzte Ferien“ etc.) immer als `note` mitgeben.
- **Kontakt-/Anmeldedaten** (Telefon/E-Mail) nur mit, wenn die Anmeldung danach konkret weiterhilft.
