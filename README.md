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
| `scripts/generate-calendar.py` | Generiert `calendar-data.js` aus geparsten Programmquellen |
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

1. `scripts/generate-calendar.py` anpassen (die Programm-Quellen aktualisieren/parsen).
2. `python3 scripts/generate-calendar.py` → schreibt `calendar-data.js` neu.
3. `node scripts/check-calendar.js` → Validierung (Dups, Format, Tages-Count).
4. PR öffnen.

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
