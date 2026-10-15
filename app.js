/* Startseite: Orts-/Event-Karten aus EVENTS rendern + Kategorie-Filter */

const CATEGORIES = {
  museum:     { label: "Museum & Kultur", icon: "🏛️" },
  zoo:        { label: "Zoo & Tiere",     icon: "🦁" },
  bibliothek: { label: "Bibliothek",      icon: "📚" },
  park:       { label: "Park & Garten",   icon: "🌳" },
  umkreis:    { label: "Umkreis",         icon: "🚗" },
  event:      { label: "Special Event",   icon: "🎉" }
};

const grid = document.getElementById("cards");
const checkedEl = document.getElementById("checked");
const filterBar = document.getElementById("filters");

function esc(s) {
  return String(s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function fmtDate(iso) {
  if (!iso) return "–";
  const [y, m, d] = iso.split("-");
  return `${d}.${m}.${y}`;
}

function render(filter) {
  const items = filter === "alle" ? EVENTS : EVENTS.filter(e => e.category === filter);
  grid.innerHTML = "";

  if (items.length === 0) {
    grid.innerHTML = '<p class="empty">Keine Einträge in dieser Kategorie – noch!</p>';
    return;
  }

  for (const e of items) {
    const meta = CATEGORIES[e.category] || { label: e.category, icon: "📌" };
    const facts = [
      e.age     && `<div><span class="label">Alter</span><span class="val">${esc(e.age)}</span></div>`,
      e.address && `<div><span class="label">Adresse</span><span class="val">${esc(e.address)}</span></div>`,
      e.hours   && `<div><span class="label">Öffnungszeiten</span><span class="val">${esc(e.hours)}</span></div>`,
      e.price   && `<div><span class="label">Kosten</span><span class="val">${esc(e.price)}</span></div>`,
      e.booking && `<div><span class="label">Anmeldung</span><span class="val">${esc(e.booking)}</span></div>`
    ].filter(Boolean).join("");

    const note = e.note ? `<div class="note">${esc(e.note)}</div>` : "";
    const link = e.url
      ? `<a class="card-link" href="${esc(e.url)}" target="_blank" rel="noopener noreferrer">${esc(e.urlLabel || "Website")} →</a>`
      : "";

    const card = document.createElement("article");
    card.className = `card cat-${e.category}`;
    card.innerHTML = `
      <div class="card-top">
        <span class="cat-badge">${meta.icon} ${esc(meta.label)}</span>
      </div>
      <h2>${esc(e.name)}</h2>
      ${e.highlight ? `<p class="highlight">${esc(e.highlight)}</p>` : ""}
      ${note}
      ${facts ? `<div class="facts">${facts}</div>` : ""}
      ${link}
    `;
    grid.appendChild(card);
  }
}

filterBar.addEventListener("click", (ev) => {
  const btn = ev.target.closest(".filter-btn");
  if (!btn) return;
  filterBar.querySelectorAll(".filter-btn").forEach(b => b.setAttribute("aria-pressed", "false"));
  btn.setAttribute("aria-pressed", "true");
  render(btn.dataset.filter);
});

// "Stand:" = neuestes Check-Datum
const newest = EVENTS.map(e => e.checked).filter(Boolean).sort().pop();
checkedEl.textContent = fmtDate(newest);

render("alle");
