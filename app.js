const CATEGORIES = {
  museum: "Museum & Kultur",
  zoo: "Zoo & Tiere",
  bibliothek: "Bibliothek",
  park: "Park & Garten",
  baden: "Bad",
  umkreis: "Umkreis",
  event: "Special Event"
};

const grid = document.getElementById("cards");
const checkedEl = document.getElementById("checked");

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
    const card = document.createElement("article");
    card.className = "card";
    const facts = [
      e.age && `<div><span class="label">Alter</span>${e.age}</div>`,
      e.address && `<div><span class="label">Adresse</span>${e.address}</div>`,
      e.hours && `<div><span class="label">Öffnungszeiten</span>${e.hours}</div>`,
      e.price && `<div><span class="label">Kosten</span>${e.price}</div>`,
      e.booking && `<div><span class="label">Anmeldung</span>${e.booking}</div>`
    ].filter(Boolean).join("");
    const note = e.note ? `<div class="note">${e.note}</div>` : "";
    const link = e.url
      ? `<a class="card-link" href="${e.url}" target="_blank" rel="noopener noreferrer">${e.urlLabel || "Website"} →</a>`
      : "";
    card.innerHTML = `
      <div class="card-top">
        <span class="cat-badge">${CATEGORIES[e.category] || e.category}</span>
      </div>
      <h2>${e.name}</h2>
      <p class="highlight">${e.highlight || ""}</p>
      ${note}
      <div class="facts">${facts}</div>
      ${link}
    `;
    grid.appendChild(card);
  }
}

document.getElementById("filters").addEventListener("click", (ev) => {
  const btn = ev.target.closest(".filter-btn");
  if (!btn) return;
  document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  render(btn.dataset.filter);
});

// "Stand:" = neuestes Check-Datum
const newest = EVENTS.map(e => e.checked).filter(Boolean).sort().pop();
checkedEl.textContent = fmtDate(newest);

render("alle");
