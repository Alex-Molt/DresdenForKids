# 🎪 Dresden for Kids

Statische Seite mit einer kuratierten Liste von **Events, Museen, Bibliotheken, Zoo & Ausflügen für Kinder in und um Dresden** – auf [GitHub Pages](https://alex-molt.github.io/DresdenForKids/) deployed.

- **Repo:** https://github.com/Alex-Molt/DresdenForKids
- **Seite:** https://alex-molt.github.io/DresdenForKids/

## Aufbau

| Datei | Zweck |
|---|---|
| `index.html` | Seiten-Shell (Hero, Filter, Grid, Footer) |
| `style.css` | Look & Feel |
| `events.js` | **Die ganze Datenquelle** – alle Events als JS-Array |
| `app.js` | Rendert die Karten + Filter-Logik |

## Neues Event hinzufügen

1. `events.js` öffnen.
2. Einen neuen Eintrag ans Ende des `EVENTS`-Arrays hängen (Template):

```js
{
  name: "Name des Events / Ortes",
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

3. Commit + Push auf `main` → GitHub Pages deployet automatisch (ohne Workflow-Datei, Pages liest direkt aus `main`).

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
- **Alter ehrlich labeln:** „ab X J.“, „ab Kl. Y“ (5 ≈ Kl. 1, 10 ≈ Kl. 5), „Jahrgang ZZZZ“ – bei Unsicherheit lieber breit formulieren.
- **Kürzere Warnungen** (Sanierung, Schließung, „letzte Ferien“ etc.) immer als `note` mitgeben.
- **Kontakt-/Anmeldedaten** (Telefon/E-Mail) nur mit, wenn die Anmeldung danach konkret weiterhilft.
