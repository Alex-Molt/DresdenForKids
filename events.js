/* ===== Datenquelle: alle Events & Orte =====
   Neues Event hinzufügen = einen neuen Objekt-Eintrag in dieses Array.
   Felder:
   - name:        Name (Pflicht)
   - category:    museum | zoo | bibliothek | park | umkreis | event
   - age:         Altersangabe (frei formuliert)
   - address:     Straße/Ort
   - hours:       Öffnungszeiten (frei formuliert)
   - price:       Eintritt/Kosten (frei formuliert)
   - highlight:   1–2 Sätze, was ist kinder-relevant
   - booking:     Anmeldung nötig? (z. B. "keine" oder "Telefon: ...")
   - url:         Website
   - urlLabel:    Linktext (optional, Standard "Website")
   - checked:     Datum letzter Prüfung (JJJJ-MM-TT)
*/
const EVENTS = [
  {
    name: "Technische Sammlungen (TSD)",
    category: "museum",
    age: "Gut ab ca. 5 Jahren",
    address: "Wilsdruffer Str. 2, 01217 Dresden (Überviehwiese)",
    hours: "Di–Fr 9:00–17:00, Sa/So/Feiertage 10:00–18:00",
    price: "Erw. 8 €, erm. 6 €, Kinder < 7 frei · Familienkarte „Maxi“ (2 Erw. + 1–4 Kinder) 20 € · Freitags ab 12 Uhr freier Eintritt",
    highlight: "Dresdner Museum zum Anfassen: Dampfmaschinen, Autos, Luftfahrt, Mathematik-Lab & Science-Center. Dazu MACHwerk-Workshops, Museumskino (KINOLINO-Kurzfilme, 1 € + Eintritt) und der Escape Room „Katze Q“.",
    booking: "Workshops oft mit Anmeldung: +49 351 488 7272",
    url: "https://tsd.de/",
    checked: "2026-10-14",
    note: "⚠️ WICHTIG: Ab 2. November 2026 Schließung wegen energetischer Sanierung (Neueröffnung 2. Q 2027 im Landhaus am Pirnaischen Platz). Am letzten Oktober-Wochenende 2026: großes Abschiedsfest!"
  },
  {
    name: "Zoo Dresden",
    category: "zoo",
    age: "Jedes Alter",
    address: "Lennéstr. 6, 01069 Dresden (direkt am Großen Garten)",
    hours: "365 Tage geöffnet · aktuell (5.10.–1.11.): 8:30–17:30 Uhr · ab 2.11.: 8:30–16:30 Uhr",
    price: "Erw. ca. 16–19 € je nach Saison, Kinder (3–16) ca. 10 €, Familienkarten & Online-Tickets günstiger",
    highlight: "204 Arten auf 13 Hektar im Herzen der Stadt. Täglich ab 11 Uhr Reviertreffpunkte mit Fütterungen & Quiz-Rallye (kostenlos, ohne Anmeldung). Zooschule & Tierhighlights für Kinder.",
    booking: "keine (Treffpunkte ohne Anmeldung)",
    url: "https://www.zoo-dresden.de/",
    checked: "2026-10-14"
  },
  {
    name: "Herbstferien im Zoo",
    category: "event",
    age: "Workshops ab ca. Kl. 5 (10 J.)",
    address: "Lennéstr. 6, 01069 Dresden",
    hours: "10.–25. Oktober 2026, Workshops 8:45–13:15 Uhr",
    price: "Workshops 20 € + Zoo-Eintritt · max. 15 Plätze pro Termin",
    highlight: "Das komplette Ferienprogramm im Zoo: Tagesworkshops rund um Tiere & Natur (Themen siehe Website). Reviertreffpunkte und Quiz-Rallye laufen während der Ferien weiter.",
    booking: "Online über zoo-dresden.de – Plätze sind begrenzt, früh anmelden!",
    url: "https://www.zoo-dresden.de/fuer-kinder/",
    checked: "2026-10-14"
  },
  {
    name: "Halloween im Zoo",
    category: "event",
    age: "Jedes Alter",
    address: "Lennéstr. 6, 01069 Dresden",
    hours: "31. Oktober 2026, 10:00–18:30 Uhr",
    price: "Zoo-Entritt (Tagespreis)",
    highlight: "Grusel- und Kürbis-Programm im Zoo am 31.10. – ein klassischer Dresdner Herbsttag mit den Kids.",
    booking: "keine",
    url: "https://www.zoo-dresden.de/veranstaltungen/",
    checked: "2026-10-14"
  },
  {
    name: "Städtische Bibliotheken Dresden (bibo)",
    category: "bibliothek",
    age: "Jedes Alter",
    address: "Zentralbibliothek: Südmannplatz 2, 01067 Dresden · 20 Standorte + Fahrbibliothek",
    hours: "je nach Standort (siehe Standorte-Seite)",
    price: "alle Kinder-Veranstaltungen frei",
    highlight: "Das beste kostenlose Kinderprogramm der Stadt: Drachenbande, Bilderbuch-Kino, Vorlesestunden & Kreativ-Workshops in fast jeder Filiale – plus MakerBox („offene“ Angebote ohne Anmeldung).",
    booking: "je nach Veranstaltung (Anmelde-E-Mail/Telefon steht auf der Veranstaltungsseite); MakerBox = ohne Anm.",
    url: "https://www.bibo-dresden.de/de/veranstaltungen.php",
    checked: "2026-10-14"
  },
  {
    name: "Großer Garten",
    category: "park",
    age: "Jedes Alter",
    address: "Am Grünen Gewölbe, 01067 Dresden",
    hours: "ganzjährig geöffnet (Tageszeit nach Saison)",
    price: "frei",
    highlight: "Dresdener Liebling für Familien: riesige Wiesen zum Toben, Spielplätze, Parkeisenbahn (Achtung: Kasse Parkeisenbahn nur als Ausgang nutzbar) – und direkt nebenan der Zoo. Bei gutem Wetter der Plan B schlechthin.",
    booking: "keine",
    url: "https://www.grosser-garten-dresden.de/",
    checked: "2026-10-14"
  },
  {
    name: "KINOLINO – Kinderfilmfest",
    category: "event",
    age: "5–13 Jahre",
    address: "mehrere Spielstätten in Dresden (u. a. Bibliotheken, frei)",
    hours: "jedes Jahr im Oktober (2 Wochen)",
    price: "Filme ab ca. 3 €, viele Vorführungen frei",
    highlight: "Das große Filmfestival für Kinder: Kurze & lange Filme fürs jüngste Publikum, oft mit Aftermovie-Talk. Ein kompletter Vorführtag ist eine prima halbe Ausflugs-Tagesplanung.",
    booking: "keine (freie Plätze an der Tageskasse)",
    url: "https://www.kinolino.de/programm",
    urlLabel: "Programm ansehen",
    checked: "2026-10-14"
  },
  {
    name: "Sachsenring Indoor-Kart",
    category: "umkreis",
    age: "ab 6 Jahren & 130 cm",
    address: "Oberlungwitz (ca. 1 h)",
    hours: "täglich 8:00–16:30 Uhr",
    price: "9,50 €/Runde unter 14, 12,50 € Erwachsene",
    highlight: "Indoor-Kartbahn mit Transponder-Zeitnahme & Monitor – die perfekte Gokart-Ausfahrt für den 10-Jährigen. Gruppenprogramm: Qualifying + Rennen + Finale mit Siegerehrung & Pokalen.",
    booking: "telefonisch: 03723 6533-0",
    url: "https://www.sachsenring.de/",
    checked: "2026-09-15"
  },
  {
    name: "Saxoniaring Freiberg",
    category: "umkreis",
    age: "je nach Kart (vorab prüfen)",
    address: "Freiberg (ca. 40 Min.)",
    hours: "witterungsabhängig (Outdoor)",
    price: "auf der Website",
    highlight: "Outdoor-Kart & Pocketbike auf 720 m – wenn das Wetter mitspielt. Alter & Mindestgröße vorab telefonisch prüfen.",
    booking: "vorab anrufen",
    url: "https://www.saxoniaring-freiberg.de/",
    checked: "2026-09-15"
  },
  {
    name: "Zschoner Mühle",
    category: "museum",
    age: "Jedes Alter (Puppentheater ab ca. 3)",
    address: "Zschonergrund 2, 01156 Dresden (Ockerwitz)",
    hours: "Puppentheater: Termine siehe Website (Sa/So 11:00 & 15:00) · Mühlenmuseum: saisonal, Führungen 12:00 & 13:30",
    price: "Puppentheater: Karten online · Mühlenführung 7 € / erm. 5 €",
    highlight: "Die einzige funktionsfähige Wassermühle Dresdens: Dresdner Mühlenmuseum (live laufende Mühlentechnik!), Puppentheater mit eigenen Märchenvorstellungen und im Sommer Bio-Sommerwirtschaft mit Biergarten. Auch Natur-Kulturbad Zschonergrund vor der Tür.",
    booking: "Puppentheater online reservieren (Plätze begrenzt)",
    url: "https://www.zschoner-muehle.de/",
    checked: "2026-10-14"
  },
  {
    name: "Schlösserland-Fernpass (Moritzburg & Co.)",
    category: "umkreis",
    age: "Jedes Alter",
    address: "Schlösser in ~1 h Umkreis: Moritzburg, Königstein, Stolpen, Weesenstein, Mildenstein",
    hours: "je nach Schloss (Ferienprogramme täglich)",
    price: "je nach Programm",
    highlight: "Die Schlösser rund um Dresden haben in den Ferien eigene Familien-Programme (Schmieden, Bogenschießen, Schlossrallye). Moritzburg mit Schlosspark am See ist ein ganztägiges Highlight.",
    booking: "je nach Programm (Ferienpass-Seite)",
    url: "https://www.schloesserland-sachsen.de/de/ferienspass/",
    checked: "2026-09-15"
  }
];
