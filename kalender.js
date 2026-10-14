const CAT_LABELS = {
  tsd: "🔧 TSD",
  zoo: "🦁 Zoo",
  bibo: "📚 Bibo",
  kinolino: "🎬 KINOLINO",
  muehle: "⚙️ Zschoner Mühle"
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
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function render() {
  const t0 = todayISO();
  const events = CALENDAR_EVENTS.filter(e => e.d >= t0);
  document.getElementById("count").textContent = events.length;

  // Stand = neuestes Datum der Datenquelle (alle haben "checked" 2026-10-14)
  const newest = CALENDAR_EVENTS.map(e => e.d).sort().pop();
  const nd = parseDate(newest);
  document.getElementById("checked").textContent =
    nd.getDate() + "." + String(nd.getMonth() + 1).padStart(2, "0") + "." + nd.getFullYear() + " (Daten)";

  const byDay = {};
  for (const e of events) {
    (byDay[e.d] = byDay[e.d] || []).push(e);
  }
  // Innerhalb eines Tages nach Zeit sortieren (einfacher Zeitstring-Reichweite)
  const sortKey = t => {
    const m = /^(\d{2}):(\d{2})/.exec(t);
    return m ? m[1] + m[2] : "9999";
  };
  for (const d in byDay) byDay[d].sort((a, b) => sortKey(a.t).localeCompare(sortKey(b.t)));

  const wrap = document.getElementById("cal-days");
  const dayNames = Object.keys(byDay).sort();
  if (dayNames.length === 0) {
    wrap.innerHTML = '<p class="empty">Keine kommenden Events gelistet – Datenquelle wird gerade aktualisiert.</p>';
    return;
  }
  let html = "";
  for (const d of dayNames) {
    const isToday = d === t0;
    const isTomorrow = d === new Date(Date.now() + 86400000).toISOString().slice(0, 10);
    const label = isToday ? "Heute" : isTomorrow ? "Morgen" : fmtLong(d);
    html += `<section class="day-block${isToday ? " day-today" : ""}">`;
    html += `<h2 class="day-head">${label}${isToday ? " ⭐" : ""} <span class="day-count">${byDay[d].length} Events</span></h2>`;
    html += `<div class="day-events">`;
    for (const e of byDay[d]) {
      html += `<article class="cal-card cat-${e.cat}">
        <div class="cal-time">${esc(e.t)}</div>
        <div class="cal-body">
          <h3>${esc(e.title)}</h3>
          <p class="cal-venue">📍 ${esc(e.venue)}</p>
          <p class="cal-cost">💶 ${esc(e.cost)}</p>
          <p class="cal-note">ℹ️ ${esc(e.note)}</p>
        </div>
        <a class="cal-link" href="${e.url}" target="_blank" rel="noopener noreferrer">Details →</a>
      </article>`;
    }
    html += `</div></section>`;
  }
  wrap.innerHTML = html;
}

render();
