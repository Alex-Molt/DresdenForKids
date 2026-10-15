/* Tages-Kalender: Events aus CALENDAR_EVENTS nach Tag gruppiert,
   mit klickbarer Kategorie-Legende als Filter.
   Robust gegen fehlende Felder (cost/note/url/venue können leer sein). */

const CAT_LABELS = {
  tsd: "🔧 TSD",
  zoo: "🦁 Zoo",
  bibo: "📚 Bibo",
  kinolino: "🎬 KINOLINO",
  muehle: "⚙️ Zschoner Mühle",
  theater: "🎭 Theater & Puppenspiel",
  museum: "🏛️ Museum",
  umkreis: "🏰 Schloss & Burg (Umkreis)",
  event: "🎉 Event"
};

const WEEKDAYS = ["Sonntag", "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag"];

function todayISO() {
  const d = new Date();
  return d.getFullYear() + "-" +
    String(d.getMonth() + 1).padStart(2, "0") + "-" +
    String(d.getDate()).padStart(2, "0");
}

function parseDate(iso) {
  const [y, m, d] = iso.split("-").map(Number);
  return new Date(y, m - 1, d);
}

function fmtLong(iso) {
  const d = parseDate(iso);
  return WEEKDAYS[d.getDay()] + ", " +
    d.getDate() + "." + String(d.getMonth() + 1).padStart(2, "0") + "." + d.getFullYear();
}

function esc(s) {
  return String(s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// Feld vorhanden & sinnvoll? (leere Strings, undefined und reine Platzhalter raus)
function has(v) {
  if (v == null) return false;
  const s = String(v).trim();
  return s !== "" && s !== "–" && s !== "-";
}

const T0 = todayISO();
const TOMORROW = new Date(Date.now() + 86400000).toISOString().slice(0, 10);

// Einmalig: kommende Events nach Tag gruppieren und je Tag nach Zeit sortieren
const upcoming = (typeof CALENDAR_EVENTS !== "undefined" ? CALENDAR_EVENTS : [])
  .filter(e => e && e.d >= T0);

const sortKey = t => {
  const m = /^\s*(\d{1,2}):(\d{2})/.exec(t || "");
  return m ? m[1].padStart(2, "0") + m[2] : "9999";
};

const byDay = {};
for (const e of upcoming) (byDay[e.d] = byDay[e.d] || []).push(e);
for (const d in byDay) byDay[d].sort((a, b) => sortKey(a.t).localeCompare(sortKey(b.t)));

const dayNames = Object.keys(byDay).sort();

// Aktive Kategorien (anfangs alle, aber nur die wirklich vorkommenden sind klickbar relevant)
const activeCats = new Set(Object.keys(CAT_LABELS));

const legendEl = document.getElementById("cal-legend");
const wrap = document.getElementById("cal-days");
const countEl = document.getElementById("count");
const checkedEl = document.getElementById("checked");

// "Stand" = neuestes Datum in der Datenquelle
const newestAll = (typeof CALENDAR_EVENTS !== "undefined" ? CALENDAR_EVENTS : [])
  .map(e => e && e.d).filter(Boolean).sort().pop();
if (newestAll) {
  const nd = parseDate(newestAll);
  checkedEl.textContent =
    nd.getDate() + "." + String(nd.getMonth() + 1).padStart(2, "0") + "." + nd.getFullYear();
}

// Legende aufbauen – alle 9 Kategorien aus CAT_LABELS
function buildLegend() {
  legendEl.innerHTML = Object.entries(CAT_LABELS).map(([key, label]) =>
    `<button type="button" class="cat-chip cat-${key}" data-cat="${key}" aria-pressed="true">${esc(label)}</button>`
  ).join("");
}

function renderDays() {
  let visible = 0;
  let html = "";

  for (const d of dayNames) {
    const events = byDay[d].filter(e => activeCats.has(e.cat));
    if (events.length === 0) continue;
    visible += events.length;

    const isToday = d === T0;
    const isTomorrow = d === TOMORROW;
    const label = fmtLong(d);
    const badge = isToday
      ? '<span class="day-badge">Heute</span>'
      : isTomorrow ? '<span class="day-badge is-tomorrow">Morgen</span>' : "";

    html += `<section class="day-block${isToday ? " day-today" : ""}">`;
    html += `<h2 class="day-head">${badge}<span>${esc(label)}</span>` +
            `<span class="day-count">${events.length} ${events.length === 1 ? "Event" : "Events"}</span></h2>`;
    html += `<div class="day-events">`;

    for (const e of events) {
      const parts = [];
      if (has(e.venue)) parts.push(`<p class="cal-meta cal-venue"><span class="ic" aria-hidden="true">📍</span><span>${esc(e.venue)}</span></p>`);
      if (has(e.cost))  parts.push(`<p class="cal-meta cal-cost"><span class="ic" aria-hidden="true">💶</span><span>${esc(e.cost)}</span></p>`);
      if (has(e.note))  parts.push(`<p class="cal-meta cal-note"><span class="ic" aria-hidden="true">ℹ️</span><span>${esc(e.note)}</span></p>`);
      const link = has(e.url)
        ? `<a class="cal-link" href="${esc(e.url)}" target="_blank" rel="noopener noreferrer">Details →</a>`
        : "";
      const time = has(e.t) ? esc(e.t) : "–";

      html += `<article class="cal-card cat-${esc(e.cat)}">
        <div class="cal-time">${time}</div>
        <div class="cal-body">
          <h3>${esc(e.title || "Ohne Titel")}</h3>
          ${parts.join("")}
        </div>
        ${link}
      </article>`;
    }

    html += `</div></section>`;
  }

  if (visible === 0) {
    wrap.innerHTML = dayNames.length === 0
      ? '<p class="empty">Keine kommenden Events gelistet – die Datenquelle wird gerade aktualisiert.</p>'
      : '<p class="empty">Keine Events in den gewählten Kategorien. Tippe oben wieder Kategorien an.</p>';
  } else {
    wrap.innerHTML = html;
  }
  countEl.textContent = visible;
}

legendEl.addEventListener("click", (ev) => {
  const chip = ev.target.closest(".cat-chip");
  if (!chip) return;
  const cat = chip.dataset.cat;
  if (activeCats.has(cat)) {
    activeCats.delete(cat);
    chip.setAttribute("aria-pressed", "false");
  } else {
    activeCats.add(cat);
    chip.setAttribute("aria-pressed", "true");
  }
  renderDays();
});

buildLegend();
renderDays();
