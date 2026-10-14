const fs = require("fs");
eval(fs.readFileSync(__dirname + "/../calendar-data.js", "utf8").replace("const CALENDAR_EVENTS", "global.CALENDAR_EVENTS"));
console.log("Events gesamt:", CALENDAR_EVENTS.length);
const f = CALENDAR_EVENTS.filter(e => e.d >= "2026-10-14");
console.log("ab 14.10.:", f.length);
const byDay = {};
for (const e of f) { byDay[e.d] = (byDay[e.d] || 0) + 1; }
console.log("Pro Tag:", Object.entries(byDay).map(([d, n]) => d + "=" + n).join(" "));
// Zeitformat check
const badT = f.filter(e => !/^(\d{2}:\d{2})/ .test(e.t) && !/^(\d{2}:\d{2})–/.test(e.t) && e.t.length < 6);
console.log("Sonder-Zeiten:", [...new Set(f.map(e => e.t))].filter(t => !/^\d{2}:\d{2}/.test(t)));
// Dups
const seen = new Set(); let dups = 0;
for (const e of f) { const k = e.d + e.t + e.title + e.venue; if (seen.has(k)) dups++; seen.add(k); }
console.log("Duplikate:", dups);
