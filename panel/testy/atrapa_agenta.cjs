// Atrapa programu Claude Code dla testów panelu — NIGDY nie łączy się z siecią ani z prawdziwym Claude.
// testy/atrapa_agenta.py kopiuje ten plik jako <katalog>/node_modules/@anthropic-ai/claude-code/cli.js obok
// <katalog>/claude.cmd, a serwer testowy dostaje agent.sciezka = <katalog>/claude.cmd. Panel (bc/agent.py,
// _program_argv) zamienia taki skrót npm na `node cli.js`, więc przebieg idzie tą samą drogą co z prawdziwym programem.
//
// Zachowanie:
//   --version                → wypisuje wersję atrapy;
//   wiadomość przez stdin    → wyjście stream-json jak `claude -p --output-format stream-json`: init, trzy kroki
//                              narzędzi (Read, Grep, Read), tekst przyrostami, pełna wiadomość, wynik;
//   „długo” w wiadomości     → długa odpowiedź (20 wierszy), inaczej jedno zdanie;
//   „powoli” w wiadomości    → czeka ok. 4 s przed tekstem (do sprawdzania rozmowy w toku).
// Zmienna BC_ATRAPA_AGENTA_LOG = katalog: każde wywołanie zapisuje tam {argv, wejscie} (testy czytają polecenie
// systemowe i listę narzędzi).
"use strict";
const fs = require("fs");
const path = require("path");

const argv = process.argv.slice(2);
if (argv.includes("--version")) {
  process.stdout.write("0.0.0-atrapa (atrapa testowa)\n");
  process.exit(0);
}

const pauza = (ms) => new Promise((r) => setTimeout(r, ms));
const wypisz = (o) => process.stdout.write(JSON.stringify(o) + "\n");
let wejscie = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (d) => { wejscie += d; });
process.stdin.on("end", async () => {
  const log = process.env.BC_ATRAPA_AGENTA_LOG;
  if (log) {
    fs.mkdirSync(log, { recursive: true });
    fs.writeFileSync(path.join(log, Date.now() + "-" + process.pid + ".json"), JSON.stringify({ argv, wejscie }), "utf8");
  }
  const sid = "atrapa-" + process.pid;
  wypisz({ type: "system", subtype: "init", session_id: sid });
  const kroki = [["Read", { file_path: "B&C/Produkcja/Rejestr decyzji.md" }], ["Grep", { pattern: "biom", path: "B&C" }],
    ["Read", { file_path: "B&C/Gra/Pety.md" }]];
  for (let i = 0; i < kroki.length; i++) {
    wypisz({ type: "assistant", message: { content: [{ type: "tool_use", id: "narz-" + i, name: kroki[i][0], input: kroki[i][1] }] } });
    await pauza(40);
  }
  if (/powoli/i.test(wejscie)) await pauza(4000);
  const tekst = /długo|dlugo/i.test(wejscie)
    ? ["Wniosek atrapy: koszt rośnie o 15% na poziom.", ""].concat(
      Array.from({ length: 18 }, (_, i) => "- Punkt " + (i + 1) + " długiej odpowiedzi atrapy.")).join("\n")
    : "Krótka odpowiedź atrapy.";
  wypisz({ type: "stream_event", event: { type: "content_block_start", content_block: { type: "text" } } });
  for (const kawalek of tekst.match(/[\s\S]{1,40}/g)) {
    wypisz({ type: "stream_event", event: { type: "content_block_delta", delta: { type: "text_delta", text: kawalek } } });
    await pauza(5);
  }
  wypisz({ type: "assistant", message: { content: [{ type: "text", text: tekst }] } });
  wypisz({ type: "result", subtype: "success", is_error: false, session_id: sid, result: tekst, total_cost_usd: 0,
    duration_ms: 900 });
});
