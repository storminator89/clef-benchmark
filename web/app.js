import {
  CATEGORY,
  SPLIT,
  escapeHTML as e,
  percent,
  decimal,
  fieldsForCase,
  fieldLabel,
  choiceLabel,
  outcome,
  filterCases,
  probabilities,
  validatePlayground,
  parseJSONStrict,
  validateLiveResult,
  validateDataset,
  requestFingerprint,
  suiteStats,
  bankPriorityCounts,
  evidenceIDs,
  documentForCase,
  InferenceSession,
  runtimeLabel,
} from "./core.js";
import { icon } from "./icons.js";
import { createCustomWorkspace } from "./custom-ui.js";
const SUITES = {
  insurance: { file: "insurance", label: "Versicherungsdokumente" },
  general: { file: "benchmark", label: "Allgemeine Entscheidungen" },
  finance: { file: "finance", label: "Finanzen & Makler" },
  clean72: { file: "clean72", label: "Alltagsnah ohne Manipulation" },
  "bank-support": { file: "bank-support", label: "Bank-Kundensupport" },
};
const EMPTY_SCHEMA = {
  decision: {
    type: "choice",
    instructions:
      "Ordne die Aussage ausschließlich anhand des mitgelieferten Textes ein. Wenn eine notwendige Information fehlt, wähle offen.",
    criteria: {
      ja: "Die Aussage wird durch den Text gestützt.",
      nein: "Die Aussage wird durch den Text widerlegt.",
      offen: "Die Angaben reichen für eine Entscheidung nicht aus.",
    },
  },
};
const chip = (c) => {
  const o = outcome(c),
    labels = {
      correct: "Alles richtig",
      partial: "Teilweise falsch",
      wrong: "Falsch",
      unscored: "Unbewertet",
    };
  return `<span class="status-chip ${o}">${icon(o === "correct" ? "check" : o === "unscored" ? "dot" : "x")}${labels[o]}</span>`;
};
const safeID = (value) => String(value).replace(/[^A-Za-z0-9_-]/g, "_");
const caseTitle = (c) =>
  c.title ||
  c.claim ||
  c.input?.split("\n").find((s) => s.trim() && !s.endsWith(":")) ||
  c.id;
const shortened = (value, max = 170) =>
  String(value || "").length > max
    ? String(value).slice(0, max - 1) + "…"
    : String(value || "");
function probabilityBars(probs, { schema, field, selected, gold } = {}) {
  return probabilities({ probabilities: probs })
    .map(
      ([key, value]) =>
        `<div class="prob-row ${key === selected ? "predicted" : ""} ${gold && selected !== gold ? "incorrect" : ""}"><div class="prob-label"><span title="${e(schema?.criteria?.[key] || key)}">${e(field === "evidence" ? schema?.criteria?.[key] || key : key)}${key === gold ? "<b>Gold</b>" : ""}</span><span class="prob-number">${percent(value, 2)}</span></div><div class="bar-track"><div class="bar-fill" style="width:${Math.min(100, Math.max(0, value * 100))}%"></div></div></div>`,
    )
    .join("");
}
export function createWorkbench({
  document: doc = globalThis.document,
  window: win = globalThis.window,
  fetch: fetcher = globalThis.fetch,
} = {}) {
  const $ = (id) => doc.getElementById(id),
    suites = Object.create(null),
    session = new InferenceSession();
  let suite = null,
    data = null,
    selected = null,
    field = "decision",
    example = null,
    health = { inference_enabled: false },
    backendConnected = false,
    healthGeneration = 0,
    pane = "cases",
    highlight = "both",
    activeClause = null,
    toastTimer = null,
    suppressRoute = false;
  let custom = null, customWasBusy = false;
  const filters = { split: "", category: "", tag: "", outcome: "", query: "" };
  const selectedCase = () => data?.cases.find((c) => c.id === selected) || null;
  function fillIcons() {
    doc
      .querySelectorAll("[data-icon]")
      .forEach((el) => (el.innerHTML = icon(el.dataset.icon)));
  }
  fillIcons();
  doc.querySelector(".skip").addEventListener("click", (event) => {
    event.preventDefault();
    $("main").focus({ preventScroll: true });
  });
  let savedTheme;
  try {
    savedTheme = win.localStorage.getItem("clef-theme");
  } catch {
    /* Optional theme persistence. */
  }
  if (["light", "dark"].includes(savedTheme))
    doc.documentElement.dataset.theme = savedTheme;
  function themeButton() {
    const light = doc.documentElement.dataset.theme !== "dark";
    $("theme-toggle").innerHTML = icon(light ? "moon" : "sun");
    $("theme-toggle").setAttribute(
      "aria-label",
      light ? "Dunkles Design aktivieren" : "Helles Design aktivieren",
    );
  }
  themeButton();
  $("theme-toggle").addEventListener("click", () => {
    doc.documentElement.dataset.theme =
      doc.documentElement.dataset.theme === "dark" ? "light" : "dark";
    try {
      win.localStorage.setItem("clef-theme", doc.documentElement.dataset.theme);
    } catch {
      /* Preference stays in this tab. */
    }
    themeButton();
  });
  function toast(message) {
    $("toast").textContent = message;
    $("toast").hidden = false;
    if (toastTimer) win.clearTimeout(toastTimer);
    toastTimer = win.setTimeout(() => ($("toast").hidden = true), 4500);
  }
  function setPane(value) {
    pane = ["cases", "document", "result"].includes(value) ? value : "cases";
    $("workbench-shell").dataset.mobilePane = pane;
    doc
      .querySelectorAll("[data-pane]")
      .forEach((b) =>
        b.setAttribute("aria-pressed", String(b.dataset.pane === pane)),
      );
  }
  doc
    .querySelectorAll("[data-pane]")
    .forEach((b) => b.addEventListener("click", () => setPane(b.dataset.pane)));
  function route() {
    const [raw, query = ""] = (win.location.hash.slice(1) || "explorer").split(
      "?",
    );
    return {
      view: ["explorer", "overview", "playground", "custom", "method"].includes(raw)
        ? raw
        : "explorer",
      params: new URLSearchParams(query),
    };
  }
  function navigate() {
    const { view, params } = route();
    suppressRoute = true;
    if (data) {
      if (
        params.has("suite") &&
        suites[params.get("suite")] &&
        params.get("suite") !== suite
      )
        selectSuite(params.get("suite"), { fromRoute: true });
      if (
        params.has("case") &&
        data.cases.some((c) => c.id === params.get("case"))
      ) {
        const next = params.get("case");
        if (
          next !== selected ||
          !filterCases(data.cases, filters).some((c) => c.id === next)
        ) {
          const target = data.cases.find((c) => c.id === next);
          resetFilters(false);
          filters.split = target.split;
          $("filter-split").value = target.split;
          selected = next;
          activeClause = null;
          renderCases();
        }
      }
      if (
        params.has("field") &&
        fieldsForCase(selectedCase()).some((f) => f.id === params.get("field"))
      ) {
        field = params.get("field");
        renderDetail();
      }
    }
    suppressRoute = false;
    if (data) updateRoute();
    doc.querySelector(".context-bar").hidden = view === "custom";
    $("suite-catalog").hidden = view === "custom";
    doc.title = `Clef Lab · ${{ explorer: "Workbench", overview: "Ergebnisse", playground: "Live testen", custom: "Eigene Tests", method: "Methodik" }[view]}`;
    doc.querySelectorAll(".view").forEach((v) => (v.hidden = v.id !== view));
    doc.querySelectorAll("[data-nav]").forEach((a) => {
      const active = a.dataset.nav === view;
      a.classList.toggle("active", active);
      if (active) a.setAttribute("aria-current", "page");
      else a.removeAttribute("aria-current");
    });
  }
  win.addEventListener("hashchange", navigate);
  win.addEventListener("popstate", navigate);
  navigate();
  function updateRoute() {
    if (suppressRoute || route().view !== "explorer") return;
    const params = new URLSearchParams({ suite });
    if (selected) params.set("case", selected);
    if (field) params.set("field", field);
    try {
      win.history.replaceState(null, "", `#explorer?${params}`);
    } catch {
      /* Navigation remains available without history writes. */
    }
  }
  function populateFilters() {
    const config = data.suite,
      groups = {};
    for (const c of data.cases) groups[c.split] = (groups[c.split] || 0) + 1;
    $("filter-split").innerHTML =
      Object.entries(groups)
        .map(
          ([id, n]) =>
            `<option value="${e(id)}">${e(config.splits?.[id] || SPLIT[id] || id)} (${n})</option>`,
        )
        .join("") + '<option value="">Alle Sprachvarianten</option>';
    $("filter-category").innerHTML =
      '<option value="">Alle Themen</option>' +
      Object.entries(config.categories || CATEGORY)
        .map(([id, label]) => `<option value="${e(id)}">${e(label)}</option>`)
        .join("");
    $("filter-tag").innerHTML =
      '<option value="">Alle Tags</option>' +
      [...new Set(data.cases.flatMap((c) => c.tags || []))]
        .sort()
        .map((t) => `<option value="${e(t)}">${e(t)}</option>`)
        .join("");
    const fieldIDs = [...new Set(data.cases.flatMap((c) => Object.keys(c.questions)))];
    $("filter-outcome").innerHTML =
      '<option value="">Alle Ergebnisse</option><option value="errors">Alle Fehler</option>' +
      fieldIDs.map((id) => `<option value="${e(id)}">${e(fieldLabel(id))} falsch</option>`).join("") +
      '<option value="correct">Alles richtig</option><option value="unscored">Ohne Ergebnis</option>';
    resetFilters(false);
  }
  function resetFilters(render = true) {
    if (!data) return;
    Object.assign(filters, {
      split: data.suite.primary_split,
      category: "",
      tag: "",
      outcome: "",
      query: "",
    });
    for (const [id, key] of [
      ["filter-split", "split"],
      ["filter-category", "category"],
      ["filter-tag", "tag"],
      ["filter-outcome", "outcome"],
      ["search", "query"],
    ])
      $(id).value = filters[key];
    if (render) renderCases();
  }
  function renderCases() {
    if (!data) return;
    const rows = filterCases(data.cases, filters);
    if (!rows.some((c) => c.id === selected)) {
      selected = rows[0]?.id || null;
      activeClause = null;
    }
    $("case-count").textContent = `${rows.length} / ${data.cases.length}`;
    $("filter-summary").textContent = filters.outcome
      ? `${rows.length} passende Fälle`
      : `${rows.length} Fälle in dieser Ansicht`;
    $("case-list").innerHTML = rows.length
      ? rows
          .map(
            (c) =>
              `<button class="case-item ${c.id === selected ? "selected" : ""}" data-case="${e(c.id)}" aria-pressed="${c.id === selected}" aria-label="${e(c.id)}: ${e(shortened(caseTitle(c), 110))}"><div class="case-top"><span class="case-index">${e(c.id.replace(/^de_|^german_/, ""))}</span>${chip(c)}</div><h3>${e(shortened(caseTitle(c), 120))}</h3><p>${e(shortened(c.message || c.scenario || c.input, 160))}</p><small>${e(data.suite.categories?.[c.category] || c.category)}</small></button>`,
          )
          .join("")
      : `<div class="empty-state">${icon("search")}<h3>Keine passenden Fälle</h3><p>Ändere den Suchbegriff oder setze die Filter zurück.</p></div>`;
    renderDocument();
    renderDetail();
    $("open-playground").disabled = !selected || session.busy;
    updateRoute();
  }
  function selectCase(id, { mobile = true } = {}) {
    if (!data?.cases.some((c) => c.id === id)) return;
    selected = id;
    activeClause = null;
    field = fieldsForCase(selectedCase()).some((f) => f.id === field)
      ? field
      : fieldsForCase(selectedCase())[0]?.id;
    renderCases();
    if (mobile) {
      setPane("document");
      $("document-header")
        .querySelector("h2")
        ?.focus?.({ preventScroll: true });
    }
  }
  function renderDocument() {
    const c = selectedCase();
    if (!c) {
      $("document-header").innerHTML = "<h2>Kein Fall ausgewählt</h2>";
      $("document-toolbar").innerHTML = "";
      $("document-content").innerHTML =
        `<div class="empty-state">${icon("document")}<h3>Platz für einen genauen Blick</h3><p>Wähle einen Fall aus der Bibliothek.</p></div>`;
      $("document-footer").textContent = "";
      return;
    }
    const d = documentForCase(c, data),
      rows = filterCases(data.cases, filters),
      index = rows.findIndex((r) => r.id === c.id),
      gold = evidenceIDs(c, "gold"),
      model = evidenceIDs(c, "model");
    const isBank = suite === "bank-support";
    const clauses = isBank
      ? [{ id: "Nachricht", title: "Kundennachricht", text: c.message },
         { id: "Servicerichtlinie", title: "Mitgelieferte fiktive Servicerichtlinie", text: c.service_policy }]
      : d?.clauses ||
      c.input
        .split(/\n\s*\n/)
        .filter(Boolean)
        .map((text, i) => ({ id: `Absatz ${i + 1}`, text }));
    $("document-header").innerHTML =
      `<span class="document-icon">${icon("document")}</span><div class="document-heading-text"><h2 tabindex="-1">${e(d?.title || data.suite.categories?.[c.category] || "Originaleingabe")}</h2><p>${e(d?.id || c.id)} · ${d ? `${clauses.length} Klauseln · synthetischer Auszug` : "Originaltext · synthetischer Fall"}</p></div><div class="case-nav"><button data-direction="-1" ${index < 1 ? "disabled" : ""} aria-label="Vorheriger Fall" title="Vorheriger Fall">‹</button><button data-direction="1" ${index >= rows.length - 1 ? "disabled" : ""} aria-label="Nächster Fall" title="Nächster Fall">›</button></div>`;
    $("document-toolbar").innerHTML =
      `<div class="document-tool-row"><label>Markierung <select id="highlight-select" aria-label="Evidenzmarkierung" ${!d ? "disabled" : ""}><option value="both">Gold &amp; Modell</option><option value="gold">Nur Goldreferenz</option><option value="model">Nur Modellwahl</option><option value="none">Keine</option></select></label><div class="evidence-legend"><span><i></i>Gold</span><span><i></i>Modell</span></div></div><nav class="clause-nav" aria-label="${d ? "Klauseln" : "Absätze"}">${clauses.map((cl) => `<button data-clause="${e(cl.id)}" class="${activeClause === cl.id ? "active" : ""}" title="${e(cl.id)} im Dokument anzeigen">${e(cl.id)}</button>`).join("")}</nav>`;
    if (isBank) $("document-toolbar").innerHTML =
      `<nav class="clause-nav" aria-label="Nachricht und Richtlinie">${clauses.map((cl) => `<button data-clause="${e(cl.id)}" class="${activeClause === cl.id ? "active" : ""}">${e(cl.id)}</button>`).join("")}</nav>`;
    else $("highlight-select").value = highlight;
    $("document-content").innerHTML =
      `<article class="document-page"><div class="document-kicker"><span>${e(d?.id || c.id)}</span><span>${isBank ? "FIKTIVER BANK-KUNDENSUPPORT" : d ? "FIKTIVE VERSICHERUNGSUNTERLAGEN" : "SYNTHETISCHER EINGABETEXT"}</span></div><h2 tabindex="-1">${e(d?.title || data.suite.categories?.[c.category] || "Dokument & Sachverhalt")}</h2><p class="document-deck">${isBank ? "Synthetische Kundennachricht mit fiktiver Servicerichtlinie in den Feldanweisungen. Keine reale Bankvorgabe oder Kundenakte. Anliegen, Priorität und nächster Schritt werden getrennt bewertet." : d ? "Ausschließlich die hier bereitgestellten Klauseln sind maßgeblich. Keine reale Police oder Rechtsauskunft." : "Unveränderter Eingabetext des ausgewählten Benchmark-Falls. Gold und Modellantwort stehen getrennt in der Prüfung."}</p>${d ? `<div class="scenario-card"><div class="eyebrow">DER SACHVERHALT · ${e(c.id)}</div><p>${e(c.scenario)}</p></div>` : ""}${clauses
        .map((cl) => {
          const g =
              gold.includes(cl.id) && ["both", "gold"].includes(highlight),
            m = model.includes(cl.id) && ["both", "model"].includes(highlight),
            klass =
              g && m
                ? "highlight-both"
                : g
                  ? "highlight-gold"
                  : m
                    ? "highlight-model"
                    : "";
          return `<section id="clause-${safeID(cl.id)}" class="document-section ${klass}" data-clause-id="${e(cl.id)}" tabindex="-1"><div class="clause-id">${e(cl.id)}</div>${g || m ? `<div class="clause-markers">${g ? "<span>Gold-Evidenz</span>" : ""}${m ? '<span class="model-marker">Modell-Evidenz</span>' : ""}</div>` : ""}${cl.title ? `<h3>${e(cl.title)}</h3>` : ""}<p>${e(cl.text)}</p></section>`;
        })
        .join(
          "",
        )}<details class="document-original"><summary>${isBank ? "Exakten Nachrichtentext (state) anzeigen" : "Exakte Modelleingabe anzeigen"}</summary><pre>${e(c.input)}</pre></details>${isBank ? `<details class="document-original"><summary>Alle nativen Feldanweisungen und Auswahloptionen</summary><pre>${e(JSON.stringify(c.questions, null, 2))}</pre></details>` : ""}</article>`;
    $("document-footer").innerHTML =
      `<span>${d ? "Markiert werden ganze, angebotene Klauseln." : "Zeilenumbrüche und Wortlaut bleiben erhalten."}</span><span>${Number.isInteger(c.input_tokens) ? `${c.input_tokens} Tokens` : "Noch keine Tokenmessung"}</span>`;
  }
  function renderDetail() {
    const c = selectedCase();
    if (!c) {
      $("inspection-header").innerHTML =
        '<div class="inspection-title"><h2>Prüfung</h2></div>';
      $("case-detail").innerHTML =
        '<div class="empty-state">Antwortfelder und Sollreferenzen erscheinen nach der Fallauswahl.</div>';
      return;
    }
    const fields = fieldsForCase(c);
    if (!fields.some((f) => f.id === field)) field = fields[0]?.id;
    const f = fields.find((f) => f.id === field);
    $("inspection-header").innerHTML =
      `<div class="inspection-title"><h2>Antwortprüfung</h2>${chip(c)}</div><p>${fields.length} ${fields.length === 1 ? "Antwortfeld" : "Antwortfelder"} · ${c.result ? "gespeicherter Benchmark-Lauf" : "noch keine geprüften Resultate"}</p>`;
    if (!f) {
      $("case-detail").innerHTML =
        '<div class="empty-state">Kein natives Fragenschema verfügbar.</div>';
      return;
    }
    const { schema, result, expected } = f,
      pred = result?.prediction,
      correct = result?.correct,
      gold = evidenceIDs(c, "gold"),
      model = evidenceIDs(c, "model");
    const question =
      f.id === "decision" && c.claim
        ? c.claim
        : f.id === "evidence"
          ? "Welche Klauseln tragen die Entscheidung?"
          : schema.instructions;
    $("case-detail").innerHTML =
      `<div class="field-tabs" role="group" aria-label="Antwortfeld">${fields.map((item) => `<button data-field="${e(item.id)}" class="${item.id === field ? "active" : ""}" aria-pressed="${item.id === field}">${icon(item.id === "evidence" ? "evidence" : "check")}${e(fieldLabel(item.id))}${item.result ? `<span aria-label="${item.result.correct ? "richtig" : "falsch"}">${item.result.correct ? "✓" : "×"}</span>` : ""}</button>`).join("")}</div><div class="field-kind"><span class="eyebrow">${f.id === "decision" ? "ZU PRÜFENDE AUSSAGE" : e(fieldLabel(f.id))}</span><span class="badge">choice · ${Object.keys(schema.criteria).length} Optionen</span></div><h3 class="question-title">${e(question)}</h3><div class="answer-comparison"><div class="answer-cell"><span>GOLD · SOLLREFERENZ</span><strong>${e(choiceLabel(f.id, expected, schema.criteria))}</strong><small>${e(expected)}</small></div><div class="answer-cell ${result ? (correct ? "model-correct" : "model-wrong") : "model-pending"}"><span>CLEF · MODELLWAHL</span><strong>${result ? e(choiceLabel(f.id, pred, schema.criteria)) : "Noch unbewertet"}</strong><small>${result ? `${e(pred)} · ${correct ? "richtig" : "falsch"}` : "Kein Ergebnis simuliert"}</small></div></div><div class="probs-heading"><span>Modellwahrscheinlichkeiten</span><span>Alle ${Object.keys(schema.criteria).length} Optionen</span></div>${result ? probabilityBars(result.probabilities, { schema, field: f.id, selected: pred, gold: expected }) : '<p class="probability-note">Wahrscheinlichkeiten erscheinen erst nach einem vollständig geprüften Lauf.</p>'}<p class="probability-note">${result ? `${decimal(c.latency_ms / 1000)} s Forward · ${Number.isInteger(c.input_tokens) ? c.input_tokens + " Tokens · " : ""}` : ""}Modellwerte, keine kalibrierte Richtigkeitsgarantie.</p>${gold.length ? `<div class="evidence-block"><h3>Belegstellen im Dokument</h3><button class="evidence-link" data-evidence="gold">${icon("link")}<span><small>Goldreferenz · vorab annotiert</small>${e(gold.join(" + "))}</span><span aria-hidden="true">↗</span></button>${model.length ? `<button class="evidence-link model-evidence" data-evidence="model">${icon("link")}<span><small>Vom Modell gewählte Klauselmenge</small>${e(model.join(" + "))}</span><span aria-hidden="true">↗</span></button>` : '<p class="evidence-explanation">Modell-Evidenz noch nicht verfügbar.</p>'}<p class="evidence-explanation">Auswahl aus vorgegebenen Belegmengen. Die Markierung ist keine freie Zitatgenerierung oder Modellbegründung.</p></div>` : ""}<div class="rationale"><div class="eyebrow">GOLD-REFERENZBEGRÜNDUNG · ANNOTATION</div><p>${e(c.gold_rationale || "Für diesen Fall ist keine Referenzbegründung hinterlegt.")}</p></div><details class="field-schema"><summary>Richtlinie &amp; Antwortschema</summary><pre>${e(JSON.stringify(schema, null, 2))}</pre></details>`;
  }
  function goClause(id, kind) {
    if (kind) {
      highlight = kind;
      renderDocument();
    }
    activeClause = id;
    doc
      .querySelectorAll("[data-clause]")
      .forEach((b) => b.classList.toggle("active", b.dataset.clause === id));
    setPane("document");
    const el = $("clause-" + safeID(id));
    if (el) {
      el.scrollIntoView?.({ behavior: "smooth", block: "center" });
      el.focus?.({ preventScroll: true });
    }
  }
  function renderOverview() {
    if (!data) return;
    const s = suiteStats(data),
      isInsurance = suite === "insurance",
      isBank = suite === "bank-support",
      rows = s.primary,
      done = s.complete,
      summary = data.summary;
    $("overview-title").innerHTML = isInsurance
      ? "Was versteht Clef<br><em>im Dokument?</em>"
      : isBank
        ? "Was erkennt Clef<br><em>im Bank-Support?</em>"
        : suite === "clean72"
        ? "Was entscheidet Clef<br><em>ohne Manipulation?</em>"
        : suite === "finance"
          ? "Was entscheidet Clef<br><em>im Makleralltag?</em>"
          : "Was entscheidet Clef<br><em>auf Deutsch?</em>";
    $("hero-copy").textContent = isInsurance
      ? "Eine Aussage einordnen und die passende Klauselmenge finden. Antworten und Evidenz getrennt prüfen, Fehler im Dokument nachvollziehen."
      : isBank
        ? "Typische deutschsprachige Kundenanfragen: Anliegen, Priorität und nächster Schritt nach mitgelieferten fiktiven Serviceregeln. Eigene, kleine synthetische Stichprobe ohne Manipulation."
        : suite === "clean72"
        ? "Alltagsnahe Bürofragen mit mehreren Anliegen, Dokumentabgleich, Rechenschritten und echten Informationslücken. Ein eigenständiger Test."
        : "Explizite Regeln, feste Auswahloptionen und nachvollziehbare Resultate. Sprachkontrollen werden nur auf den passenden Szenarien verglichen.";
    $("study-count").textContent = s.total;
    $("study-caption").textContent = "Synthetische deutsche Hauptfälle";
    const documents = data.documents?.length;
    $("study-details").innerHTML =
      `<div><b>${data.cases.length}</b>Requests in dieser Suite</div><div><b>${Object.keys(data.suite.categories || {}).length}</b>Aufgabenbereiche</div>${documents ? `<div><b>${documents}</b>gemeinsam genutzte Dokumente</div>` : ""}`;
    $("result-banner").className = "notice " + (done ? "" : "neutral");
    $("result-banner").innerHTML = done
      ? "<strong>Abgeschlossener Lauf · unabhängig gegengeprüft</strong><br>Experimentelle CPU-NF4-Konfiguration. Synthetische Auswahlaufgaben, kein Produktionstauglichkeitsnachweis."
      : "<strong>Testdaten verfügbar · Ergebnisse noch ausstehend</strong><br>Goldreferenzen lassen sich bereits prüfen. Bis zum vollständigen Lauf und seiner unabhängigen Verifikation werden keine Scores oder Modellantworten angezeigt.";
    let stats;
    if (isBank) {
      stats = Object.entries(s.fields).map(([id, metric]) => [
        fieldLabel(id), done ? percent(metric.correct / metric.total) : "—",
        done ? `${metric.correct} / ${metric.total} Felder richtig${id === "priority" ? ` · Routine-Baseline ${percent(rows.filter((c) => c.expected.priority === "routine").length / s.total)}` : ""}` : `${metric.total} geplante Felder`, "check",
      ]);
      stats.push(["Vollständig richtig", done ? percent(s.exact / s.total) : "—",
        done ? `${s.exact} / ${s.total} Fälle: alle drei Felder richtig` : "Anliegen, Priorität UND nächster Schritt", "layers"]);
    } else if (isInsurance) {
      stats = [
        [
          "Entscheidung",
          done
            ? percent(s.fields.decision.correct / s.fields.decision.total)
            : "—",
          done
            ? `${s.fields.decision.correct} / ${s.fields.decision.total} Aussagen richtig eingeordnet`
            : `${s.total} geplante Entscheidungen`,
          "check",
        ],
        [
          "Evidenzauswahl",
          done
            ? percent(s.fields.evidence.correct / s.fields.evidence.total)
            : "—",
          done
            ? `${s.fields.evidence.correct} / ${s.fields.evidence.total} Belegmengen richtig`
            : "Auswahl aus angebotenen Klauselmengen",
          "evidence",
        ],
        [
          "Vollständig richtig",
          done ? percent(s.exact / s.total) : "—",
          done
            ? `${s.exact} / ${s.total} Fälle: beide Felder richtig`
            : "Entscheidung und Evidenz zusammen",
          "layers",
        ],
        [
          "Schema-Gültigkeit",
          done ? percent(s.valid / s.total) : "—",
          done
            ? `${s.valid} / ${s.total} Requests gültig`
            : "2 native choice-Felder pro Request",
          "shield",
        ],
      ];
    } else {
      const score = data.scores?.splits?.[data.suite.primary_split],
        median =
          data.verification?.splits?.[data.suite.primary_split]?.timing
            ?.latency_ms?.median;
      stats = [
        [
          "Deutsche Genauigkeit",
          done ? percent(s.exact / s.total) : "—",
          done
            ? `${s.exact} / ${s.total} Entscheidungen richtig`
            : `${s.total} geplante Hauptfälle`,
          "check",
        ],
        [
          "Kategorie-Macro-F1",
          decimal(score?.category_macro_f1, 3),
          "Ungewichtet über die Kategorien",
          "chart",
        ],
        [
          "Schema-Gültigkeit",
          done ? percent(s.valid / s.total) : "—",
          done
            ? `${s.valid} / ${s.total} native Antworten gültig`
            : "Strenges choice-Schema",
          "shield",
        ],
        [
          "Median pro Request",
          Number.isFinite(median) ? `${decimal(median / 1000)} s` : "—",
          "CPU-Forward, ohne Laden & Warm-up",
          "clock",
        ],
      ];
    }
    $("stats").innerHTML = stats
      .map(
        ([label, value, caption, symbol]) =>
          `<article class="stat"><div class="stat-label">${e(label)}${icon(symbol)}</div><div class="stat-value">${e(value)}</div><div class="stat-caption">${e(caption)}</div></article>`,
      )
      .join("");
    $("category-size").textContent = `${s.total} Hauptfälle`;
    $("category-chart").innerHTML = Object.entries(data.suite.categories || {})
      .map(([id, label]) => {
        const subset = rows.filter((c) => c.category === id),
          n = subset.filter((c) => outcome(c) === "correct").length,
          v = done && subset.length ? n / subset.length : null;
        return `<div class="category-row"><span>${e(label)}</span><div class="bar-track"><div class="bar-fill" style="width:${v !== null ? v * 100 : 0}%"></div></div><span class="category-value">${v !== null ? `${n}/${subset.length}` : "—"}</span></div>`;
      })
      .join("");
    $("category-note").textContent = isInsurance
      ? "Vollständig richtige Fälle: Entscheidung UND Evidenzauswahl müssen stimmen. Je fünf Fälle teilen sich ein Dokument und sind deshalb nicht unabhängig."
      : isBank
        ? `Vollständig richtige Fälle: alle drei Felder müssen stimmen. ${s.total} synthetische Fälle nach fiktiven Serviceregeln; keine repräsentative Stichprobe. Andere Suiten werden nicht addiert.`
        : `Korrekte Entscheidungen auf allen ${s.total} geplanten deutschen Hauptfällen. Andere Suiten und Sprachvarianten werden nicht addiert.`;
    const errors = rows.filter((c) =>
        ["partial", "wrong"].includes(outcome(c)),
      ),
      high = errors.filter((c) =>
        fieldsForCase(c).some(
          (f) =>
            f.result?.correct === false &&
            Math.max(...Object.values(f.result.probabilities)) > 0.9,
        ),
      );
    $("diagnosis-content").innerHTML = done
      ? `<div class="diagnosis-item"><span>Fälle mit mindestens einem Fehler</span><strong>${errors.length} / ${s.total}</strong></div>${isInsurance ? `<div class="diagnosis-item"><span>Evidenz richtig, Entscheidung falsch</span><strong>${rows.filter((c) => fieldsForCase(c).find((f) => f.id === "evidence")?.result?.correct && fieldsForCase(c).find((f) => f.id === "decision")?.result?.correct === false).length}</strong></div><div class="diagnosis-item"><span>Entscheidung richtig, Evidenz falsch</span><strong>${rows.filter((c) => fieldsForCase(c).find((f) => f.id === "decision")?.result?.correct && fieldsForCase(c).find((f) => f.id === "evidence")?.result?.correct === false).length}</strong></div>` : ""}<div class="diagnosis-item"><span>Fehlerfall mit einem falschen Feld > 90 %</span><strong>${high.length}</strong></div><p>Konfidenz allein reicht nicht für eine Freigabe. Vergleiche die Modellwahl mit der Goldreferenz und dem genauen Wortlaut.</p>`
      : "<p>Ein Schema kann formal gültig sein und inhaltlich danebenliegen. Der Workbench trennt Antwortqualität, Evidenzauswahl und technische Gültigkeit.</p>";
    if (isBank && done) {
      const urgency = bankPriorityCounts(rows);
      const diagnostic = (label, value) => `<div class="diagnosis-item"><span>${e(label)}</span><strong>${e(value)}</strong></div>`;
      $("diagnosis-content").insertAdjacentHTML("afterbegin",
        diagnostic("Schema-gültige Requests", `${s.valid} / ${s.total}`) +
        (urgency ? diagnostic("Kritische Fälle: alle drei Felder richtig", `${urgency.critical_all_fields_correct} / ${urgency.gold_critical}`) +
         diagnostic("Kritische Fälle zu niedrig priorisiert", `${urgency.missed_critical} / ${urgency.gold_critical}`) +
         diagnostic("Kritische Fälle ohne Security-Handoff", `${urgency.critical_handoff_misses} / ${urgency.gold_critical}`) +
         diagnostic("Dringende Fälle als Routine eingestuft", `${urgency.missed_urgent} / ${urgency.gold_urgent}`) +
         diagnostic("Unnötig als kritisch eingestuft", `${urgency.unnecessary_critical} / ${s.total - urgency.gold_critical}`) +
         diagnostic("Unnötige Security-Handoffs", `${urgency.excess_security_handoffs} / ${rows.filter((c) => c.expected.next_step !== "security_handoff").length}`) +
         diagnostic("Unnötige Eskalationen", `${urgency.unnecessary_escalations} / ${urgency.gold_non_escalation}`) +
         diagnostic("Baseline: immer Routine", `${urgency.gold_routine} / ${s.total} · ${percent(urgency.gold_routine / s.total)}`) +
         '<p>Prioritätsfolge: critical &gt; urgent &gt; routine. Eine kritische Anfrage zählt auch bei urgent als zu niedrig priorisiert. Ein Security-Handoff ist unnötig, wenn die Goldreferenz einen anderen nächsten Schritt verlangt. Unnötige Eskalationen: Gold guidance/clarify, Modell specialist_review/security_handoff. Die Baseline gilt für diese gestaltete Stichprobe, nicht für Bank-Traffic.</p>' : ""));
    }
    $("inspect-errors").disabled = !done || !errors.length;
    const pairs = Object.values(data.scores?.paired_all_planned || {});
    $("paired-panel").hidden = !pairs.length;
    const pairLabels = {
      german_id: "Deutsch / Deutsch",
      english_id: "Englisch / Englisch",
      mixed_id: "Deutsch / Englisch",
    };
    $("paired-comparisons").innerHTML = pairs
      .map(
        (p) =>
          `<div class="paired-row"><div><span>${e(pairLabels[p.left] || p.left)}</span><strong>${percent(p.left_accuracy_all_planned)}</strong></div><span class="paired-vs">${e(p.n_pairs_planned)} gleiche Fälle</span><div><span>${e(pairLabels[p.right] || p.right)}</span><strong>${percent(p.right_accuracy_all_planned)}</strong></div><small>${e(p.counts.both_correct)} beide richtig · ${e(p.counts.left_only_correct)} nur links · ${e(p.counts.right_only_correct)} nur rechts · ${e(p.counts.both_wrong)} beide falsch</small></div>`,
      )
      .join("");
    $("method-scope").textContent = isInsurance
      ? "Diese Suite prüft das Verständnis kurzer, fiktiver Versicherungsunterlagen: eine Aussage anhand des Sachverhalts einordnen und aus fünf angebotenen Belegmengen wählen. Keine vollständigen Policen, OCR, Recherche, freie Antwortgenerierung oder arithmetische Leistungsprüfung."
      : isBank
        ? "Separater deutschsprachiger Test mit typischen, synthetischen Bank-Kundenanfragen ohne Manipulation. Drei native Auswahlfelder werden nach einer fiktiven, mitgelieferten Servicerichtlinie bewertet. Kein realer Kundendatenbestand, keine freie Antwortgenerierung, keine Ausführung von Bankvorgängen und kein Produktionsnachweis. Die kleine Stichprobe erlaubt keine belastbare Aussage über seltene Risiken; Fehlpriorisierungen werden gesondert gezeigt."
        : suite === "clean72"
        ? "Separater synthetischer Bürotest ohne Manipulationsanweisungen. Andere Aufgaben und Schwierigkeiten als die früheren Tests; Quotendifferenzen belegen keinen kausalen Manipulationseffekt."
        : "Synthetische, vorab definierte Auswahlaufgaben mit expliziten Regeln. Explorative Sprachkontrollen, keine repräsentative Feldstudie und keine Bewertung freier Beratung.";
    $("method-measures").textContent = isBank
      ? "Anliegen, Priorität und nächster Schritt werden getrennt bewertet. Vollständig richtig ist ein Fall nur mit allen drei richtigen Feldern. Eine hohe Prioritätsquote allein genügt nicht: Routine-Baseline und Fehlpriorisierungen gehören dazu."
      : isInsurance
        ? "Antwort, Evidenz und vollständig richtige Fälle werden getrennt ausgewiesen. Ein richtiger Beleg ersetzt keine richtige Antwort."
        : "Antwortqualität und technische Schema-Gültigkeit werden getrennt ausgewiesen. Jede Suite und Sprachvariante behält ihren eigenen Nenner.";
    $("method-synthetic").textContent = isBank
      ? "Die 80 Fälle sind KI-verfasst und gezielt gestaltet, keine repräsentative Stichprobe aus realem Bank-Traffic und kein BANKING77. Eine zweite KI-Prüfung ersetzt kein menschliches Annotationsteam. Die Serviceregeln sind fiktiv, keine Bank-, Finanz- oder Rechtsauskunft."
      : isInsurance
        ? "Die Fälle sind KI-verfasst und keine repräsentative Stichprobe aus dem Versicherungsalltag. Eine zweite KI-Prüfung ersetzt kein menschliches Annotationsteam. Fiktive Klauseln sind keine echte Versicherungs- oder Rechtsauskunft."
        : "Die Fälle sind KI-verfasst und keine repräsentative Feldstudie. Eine zweite KI-Prüfung ersetzt kein menschliches Annotationsteam. Die vorgegebenen Regeln gehören zu diesem synthetischen Test.";
    $("method-reference").textContent = (isInsurance
      ? "Die Auswahl einer vorgegebenen Evidenzstelle belegt keine freie Dokumentanalyse. "
      : "Die Auswahl fester Antwortoptionen belegt keine sichere Ausführung realer Vorgänge. ") +
      "Gold-Referenzbegründungen sind KI-verfasste und von einer zweiten KI geprüfte Annotationen, keine aus dem Modell gewonnenen Gedanken. Hohe Modellwahrscheinlichkeit ist keine kalibrierte Richtigkeitsgarantie.";
    $("method-scenarios").textContent =
      `${s.total} deutsche Hauptfälle · ${data.cases.length} Requests`;
    $("method-categories").textContent =
      `${Object.keys(data.suite.categories || {}).length} Aufgabenbereiche${documents ? ` · ${documents} Dokumente` : ""}`;
    $("method-scoring").textContent =
      data.scores?.scoring_version ||
      (summary
        ? "Native Feldgenauigkeit; vollständig richtige Fälle"
        : "Noch keine finale Auswertung");
    $("method-dataset").textContent = `${SUITES[suite].label} · eigener Nenner`;
  }
  function emptyOutput(
    title = "Bereit für einen neuen Blick",
    message = "Lade die unveränderte Benchmark-Antwort oder starte eine echte lokale Inferenz.",
    kind = "empty",
  ) {
    $("playground-output").innerHTML =
      `<div class="empty-output ${kind}">${icon(kind === "pending" ? "spark" : kind === "error" ? "x" : "flask")}<h3>${e(title)}</h3><p>${e(message)}</p>${kind === "pending" ? '<span class="pending-detail">Ein Tabwechsel stoppt die Berechnung nicht.</span>' : ""}</div>`;
  }
  function readEditor() {
    return validatePlayground(
      $("input-state").value,
      parseJSONStrict($("input-schema").value),
    );
  }
  function unchanged() {
    try {
      return (
        !!example &&
        requestFingerprint(readEditor()) ===
          requestFingerprint({
            state: example.input,
            questions: example.questions,
          })
      );
    } catch {
      return false;
    }
  }
  function updateEditorState() {
    const chars = [...$("input-state").value].length;
    $("char-count").textContent = `${decimal(chars, 0)} / 6.000`;
    try {
      const qs = parseJSONStrict($("input-schema").value);
      $("question-count").textContent =
        `${Object.keys(qs).length} choice-Fragen · JSON`;
    } catch {
      $("question-count").textContent = "Ungültiges JSON";
    }
    $("show-saved").disabled = session.busy || !example?.result || !unchanged();
    $("run-live").disabled = session.busy || custom?.isBusy() || !health.inference_enabled || health.busy === true;
  }
  function loadExample(id) {
    if (session.busy) {
      toast(
        "Die laufende Anfrage behält ihren Eingabetext. Danach kannst du einen anderen Fall laden.",
      );
      return false;
    }
    const found = data?.cases.find((c) => c.id === id);
    if (!found) return false;
    session.edit(() => {
      example = found;
      $("example-select").value = found.id;
      $("input-state").value = found.input;
      $("input-schema").value = JSON.stringify(found.questions, null, 2);
      $("editor-message").textContent = "";
      $("editor-message").classList.remove("error");
      $("output-kind").textContent = "Noch keine Anfrage";
      emptyOutput();
      updateEditorState();
    });
    return true;
  }
  function edited() {
    if (session.busy) return;
    updateEditorState();
    $("output-kind").textContent = "Eingabe geändert";
    emptyOutput(
      "Neue Eingabe. Neues Ergebnis.",
      "Die vorherige Antwort ist ausgeblendet. Nur echte lokale Inferenz kann diese Anfrage neu beantworten.",
    );
    $("editor-message").classList.remove("error");
    $("editor-message").textContent = unchanged()
      ? "Originaleingabe wiederhergestellt. Gespeicherte Antwort ist verfügbar."
      : "Für die bearbeitete Anfrage wird kein Benchmark-Ergebnis übernommen.";
  }
  function renderOutput(request, fields, info) {
    $("playground-output").innerHTML =
      Object.entries(request.questions)
        .map(([id, schema]) => {
          const value = fields[id];
          return `<article class="output-field" data-output-field="${e(id)}"><div class="output-field-head"><span>${e(fieldLabel(id))}</span><span class="badge">${e(id)}</span></div><h3 class="output-choice">${e(value.prediction)}</h3><p class="output-choice-label">${e(schema.criteria[value.prediction])}</p><p class="output-summary">${percent(value.probabilities[value.prediction], 2)} Modellwahrscheinlichkeit</p><details open><summary>Alle ${Object.keys(schema.criteria).length} Optionen</summary>${probabilityBars(value.probabilities, { schema, field: id, selected: value.prediction })}</details></article>`;
        })
        .join("") +
      `<div class="result-note">${e(info)}<br>Konfidenz ist keine Garantie. Neue Live-Tests verändern den Benchmark nicht.</div>`;
  }
  function saved() {
    if (session.busy || !unchanged() || !example?.result) return false;
    const fields = fieldsForCase(example);
    if (fields.some((f) => !f.result)) {
      toast("Die gespeicherte Antwort enthält nicht alle Felder.");
      return false;
    }
    $("output-kind").textContent = "Gespeicherte Inferenz";
    renderOutput(
      { state: example.input, questions: example.questions },
      Object.fromEntries(fields.map((f) => [f.id, f.result])),
      `Originalfall ${example.id} · ${decimal(example.latency_ms / 1000)} s CPU-Forward · ${example.input_tokens} Tokens`,
    );
    $("editor-message").textContent =
      "Unveränderte Antwort aus dem geprüften Benchmark-Lauf. Es wurde keine neue Inferenz ausgeführt.";
    $("editor-message").classList.remove("error");
    return true;
  }
  function renderBackend() {
    const enabled = health.inference_enabled === true,
      loaded = enabled && health.model_loaded === true,
      busy = health.busy === true || session.busy || custom?.isBusy();
    const headline = !backendConnected ? "Server nicht erreichbar" : !enabled ? "Ergebnismodus · Modell nicht aktiviert" : busy ? "Lokale Berechnung läuft" : loaded ? "Modell geladen" : "Inferenz freigegeben · Modell noch ungeladen";
    $("backend-state").classList.toggle("live", loaded);
    $("backend-state").classList.toggle("enabled", enabled && !loaded);
    $("backend-state").innerHTML = `<i></i>${!backendConnected ? "Offline-Ansicht" : busy ? "Berechnung läuft" : loaded ? "Modell geladen" : enabled ? "Modell ungeladen" : "Ergebnismodus"}`;
    $("backend-state").title = `${headline}. Lokalen Modellstatus ansehen.`;
    $("backend-summary").textContent = headline;
    $("custom-backend-summary").textContent = headline;
    const steps = [
      ["Server", backendConnected, backendConnected ? "Erreichbar" : "Nicht verbunden"],
      ["Inferenz", enabled, enabled ? "Explizit freigegeben" : "Nicht aktiviert"],
      ["Modell", loaded, loaded ? "Im Speicher geladen" : "Noch nicht geladen"],
    ];
    $("backend-readiness").innerHTML = steps.map(([label, ready, note], i) => `<li data-readiness="${i}" data-status="${ready ? "ready" : "pending"}"><span class="readiness-number" aria-hidden="true">${ready ? icon("check") : `0${i + 1}`}</span><div><strong>${label}</strong><small>${note}</small></div></li>`).join("");
    const runtime = loaded
      ? runtimeLabel(health.runtime)
      : enabled
        ? `Profil ${health.requested_profile || "unbekannt"} angefordert. Gerät noch nicht geladen/geprüft.`
        : "Live-Backend nicht aktiviert oder nicht erreichbar.";
    $("runtime-details").textContent = `${health.model_id || "Modell noch nicht bestätigt"} · ${runtime}`;
    $("playground-notice").innerHTML = enabled
      ? `<strong>Lokale Inferenz aktiviert</strong> · ${e(health.model_id || "Modell noch nicht bestätigt")} · ${e(runtime)}<br>Beim ersten Aufruf werden Dateien geprüft und das Modell geladen. Kein automatischer Geräte-Fallback. Geladen heißt nicht, dass jede Anfrage erfolgreich oder korrekt beantwortet wird.`
      : "<strong>Ergebnismodus · keine neue Inferenz verfügbar</strong><br>Gespeicherte Antworten lassen sich ansehen. Für neue Eingaben starte den lokalen Server ausdrücklich mit --enable-inference und --model-dir. Nur Text; kein Bild-Upload.";
    updateEditorState();
  }
  async function checkBackend() {
    const generation = ++healthGeneration;
    for (const id of ["refresh-backend", "custom-refresh-backend"]) { $(id).disabled = true; $(id).textContent = "Status wird geprüft …"; }
    try {
      const r = await fetcher("/api/health", { cache: "no-store" });
      if (!r.ok) throw Error();
      const value = await r.json();
      if (!value || typeof value !== "object" || typeof value.inference_enabled !== "boolean" || typeof value.model_loaded !== "boolean" || typeof value.busy !== "boolean") throw Error("Ungültiger Modellstatus");
      if (generation !== healthGeneration) return health;
      health = value; backendConnected = true;
    } catch {
      if (generation !== healthGeneration) return health;
      health = { inference_enabled: false }; backendConnected = false;
    } finally {
      if (generation === healthGeneration) {
        for (const id of ["refresh-backend", "custom-refresh-backend"]) { $(id).disabled = false; $(id).textContent = "Status aktualisieren"; }
        renderBackend(); custom?.refresh();
      }
    }
    return health;
  }
  for (const id of ["refresh-backend", "custom-refresh-backend"]) $(id).addEventListener("click", checkBackend);
  function renderSuiteCatalog() {
    const descriptions = {
      insurance: ["document", "Aussage und Beleg im Dokument"],
      "bank-support": ["panels", "Anliegen, Priorität und nächster Schritt"],
      general: ["layers", "Allgemeine Regeln und Sprachkontrollen"],
      finance: ["chart", "Finanzfragen und Maklerfälle"],
      clean72: ["shield", "Alltagstexte ohne Manipulationsanweisungen"],
    };
    $("suite-grid").innerHTML = Object.entries(descriptions).map(([id, [glyph, detail]]) => {
      const item = suites[id], stats = item && suiteStats(item), selected = suite === id;
      return `<button class="suite-card ${selected ? "selected" : ""}" data-suite="${id}" aria-pressed="${selected}" ${!item || session.busy || custom?.isBusy() ? "disabled" : ""}><span class="suite-card-icon">${icon(glyph)}</span><span class="suite-card-copy"><strong>${e(SUITES[id].label)}</strong><small>${e(detail)}</small><span>${item ? `${stats.total} deutsche Hauptfälle · ${item.status === "completed" ? "Gespeicherter Lauf" : "Testdaten ohne Ergebnisse"}` : "Nicht verfügbar"}</span></span><span class="suite-card-arrow" aria-hidden="true">${selected ? "✓" : "↗"}</span></button>`;
    }).join("");
  }
  $("suite-grid").addEventListener("click", event => {
    const button = event.target.closest("[data-suite]");
    if (!button || button.disabled || !selectSuite(button.dataset.suite)) return;
    $("suite-catalog").open = false;
    $("suite-select").focus({ preventScroll: true });
  });
  function setPending(busy) {
    for (const id of [
      "input-state",
      "input-schema",
      "example-select",
      "suite-select",
      "new-request",
    ])
      $(id).disabled = busy;
    $("open-playground").disabled = busy || !selected;
    $("run-live").disabled = busy || !health.inference_enabled || health.busy === true;
    $("show-saved").disabled = busy || !example?.result || !unchanged();
    renderSuiteCatalog();
  }
  async function runLive() {
    if (session.busy || custom?.isBusy() || !health.inference_enabled || health.busy === true) return false;
    let request;
    try {
      request = readEditor();
    } catch (err) {
      $("editor-message").textContent = `Schema prüfen: ${err.message}`;
      $("editor-message").classList.add("error");
      $("output-kind").textContent = "Ungültige Anfrage";
      emptyOutput(
        "Schema prüfen",
        "Es wurde keine Anfrage gesendet. Die Fehlermeldung steht unter dem Editor.",
        "error",
      );
      return false;
    }
    const token = session.begin(),
      fingerprint = requestFingerprint(request);
    setPending(true);
    renderBackend();
    custom?.refresh();
    $("output-kind").textContent = "Lokale Inferenz läuft";
    $("editor-message").textContent =
      "Dateien prüfen, ggf. Modell laden, dann alle Antwortfelder berechnen. Bitte keine parallele Anfrage starten.";
    $("editor-message").classList.remove("error");
    emptyOutput(
      "Clef prüft die Anfrage …",
      "Echte lokale Berechnung. Ein Ergebnis erscheint erst, wenn alle angefragten Felder vollständig vorliegen.",
      "pending",
    );
    try {
      const r = await fetcher("/api/infer", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-Clef-Request": "1" },
        body: JSON.stringify(request),
      });
      let result;
      try {
        result = await r.json();
      } catch {
        throw Error(
          "Das lokale Backend hat keine gültige JSON-Antwort gesendet.",
        );
      }
      if (!r.ok)
        throw Error(
          result.error || `Lokale Inferenz fehlgeschlagen (HTTP ${r.status}).`,
        );
      if (!session.isCurrent(token)) return false;
      if (requestFingerprint(readEditor()) !== fingerprint)
        throw Error(
          "Die Eingabe hat sich während der Anfrage geändert. Das Ergebnis wird nicht zugeordnet.",
        );
      validateLiveResult(result, request);
      renderOutput(
        request,
        Object.fromEntries(
          Object.keys(request.questions).map((id) => [
            id,
            {
              prediction: result.answers[id].choice,
              probabilities: result.probabilities_unrounded[id],
            },
          ]),
        ),
        `Neue lokale Inferenz · ${result.model || "Modell nicht angegeben"} · ${runtimeLabel(result.runtime)} · ${decimal(result.latency_ms / 1000)} s Forward · ${result.input_tokens} Tokens`,
      );
      $("output-kind").textContent = "Neue echte Inferenz";
      $("editor-message").textContent =
        `${Object.keys(request.questions).length} Antwortfelder erfolgreich lokal berechnet. Nicht Teil des eingefrorenen Benchmarks.`;
      return true;
    } catch (err) {
      if (session.isCurrent(token)) {
        $("output-kind").textContent = "Kein Ergebnis";
        emptyOutput(
          "Keine gültige Antwort",
          "Es wird kein Ersatz- oder Teilergebnis angezeigt. Prüfe die Fehlermeldung und gegebenenfalls das Server-Terminal.",
          "error",
        );
        $("editor-message").textContent = err.message;
        $("editor-message").classList.add("error");
      }
      return false;
    } finally {
      if (session.finish(token)) {
        setPending(false);
        await checkBackend();
      }
    }
  }
  function selectSuite(id, { fromRoute = false } = {}) {
    if (!suites[id]) return false;
    if (session.busy || custom?.isBusy()) {
      $("suite-select").value = suite;
      toast(
        "Die Testsuite bleibt bis zum Ende der laufenden Anfrage erhalten.",
      );
      return false;
    }
    suppressRoute = fromRoute;
    suite = id;
    data = suites[id];
    selected = null;
    field = "decision";
    highlight = "both";
    activeClause = null;
    $("suite-select").value = id;
    $("search").placeholder = id === "bank-support" ? "Fall, Thema, Nachricht …" : "Fall, Thema, Klausel …";
    const stats = suiteStats(data);
    $("suite-description").textContent =
      `${stats.total} deutsche Hauptfälle · ${data.cases.length} Requests · eigener Nenner`;
    $("workbench-source-title").textContent =
      data.status === "completed"
        ? "Gespeicherte, echte Inferenz"
        : "Eingefrorene Testdaten";
    $("workbench-source-note").textContent =
      data.status === "completed"
        ? "Keine Live-Berechnung beim Öffnen"
        : "Testdaten verfügbar · Modellresultate ausstehend";
    $("download-results").disabled = false;
    renderSuiteCatalog();
    populateFilters();
    $("example-select").innerHTML = data.cases
      .map(
        (c) =>
          `<option value="${e(c.id)}">${e(c.id)} · ${e(shortened(caseTitle(c), 100))}</option>`,
      )
      .join("");
    renderOverview();
    renderCases();
    loadExample(selected);
    suppressRoute = false;
    if (!fromRoute) updateRoute();
    return true;
  }
  // Delegated handlers remain valid after a panel is re-rendered.
  $("case-list").addEventListener("click", (event) => {
    const button = event.target.closest("[data-case]");
    if (button) selectCase(button.dataset.case);
  });
  $("document-header").addEventListener("click", (event) => {
    const b = event.target.closest("[data-direction]");
    if (!b || b.disabled) return;
    const rows = filterCases(data.cases, filters),
      index = rows.findIndex((c) => c.id === selected),
      next = rows[index + Number(b.dataset.direction)];
    if (next) {
      const direction = b.dataset.direction;
      selectCase(next.id, { mobile: false });
      const target =
        $("document-header").querySelector(
          `[data-direction="${direction}"]:not([disabled])`,
        ) || $("document-header").querySelector("h2");
      target?.focus?.({ preventScroll: true });
    }
  });
  $("document-toolbar").addEventListener("click", (event) => {
    const b = event.target.closest("[data-clause]");
    if (b) goClause(b.dataset.clause);
  });
  $("document-toolbar").addEventListener("change", (event) => {
    if (event.target.id === "highlight-select") {
      highlight = event.target.value;
      renderDocument();
      $("highlight-select").focus?.({ preventScroll: true });
    }
  });
  $("case-detail").addEventListener("click", (event) => {
    const f = event.target.closest("[data-field]"),
      ev = event.target.closest("[data-evidence]");
    if (f) {
      field = f.dataset.field;
      renderDetail();
      updateRoute();
      $("case-detail")
        .querySelector(`[data-field="${field}"]`)
        ?.focus?.({ preventScroll: true });
    }
    if (ev) {
      const kind = ev.dataset.evidence,
        ids = evidenceIDs(selectedCase(), kind);
      if (ids.length) goClause(ids[0], kind);
    }
  });
  $("open-playground").addEventListener("click", () => {
    if (loadExample(selected)) win.location.hash = "playground";
  });
  for (const [id, key] of [
    ["filter-split", "split"],
    ["filter-category", "category"],
    ["filter-tag", "tag"],
    ["filter-outcome", "outcome"],
  ])
    $(id).addEventListener("change", () => {
      filters[key] = $(id).value;
      renderCases();
    });
  $("search").addEventListener("input", () => {
    filters.query = $("search").value;
    renderCases();
  });
  $("reset-filters").addEventListener("click", () => resetFilters());
  $("suite-select").addEventListener("change", () =>
    selectSuite($("suite-select").value),
  );
  $("inspect-errors").addEventListener("click", () => {
    resetFilters(false);
    filters.outcome = "errors";
    $("filter-outcome").value = "errors";
    renderCases();
    setPane("cases");
    win.location.hash = "explorer";
  });
  for (const id of ["input-state", "input-schema"])
    $(id).addEventListener("input", edited);
  $("example-select").addEventListener("change", () =>
    loadExample($("example-select").value),
  );
  $("new-request").addEventListener("click", () => {
    if (session.busy) return;
    example = null;
    $("example-select").value = "";
    $("input-state").value = "";
    $("input-schema").value = JSON.stringify(EMPTY_SCHEMA, null, 2);
    edited();
    $("input-state").focus();
  });
  $("show-saved").addEventListener("click", saved);
  $("run-live").addEventListener("click", runLive);
  $("download-results").addEventListener("click", () => {
    if (!data) return;
    const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: "application/json",
      }),
      url = win.URL.createObjectURL(blob),
      a = doc.createElement("a");
    a.href = url;
    a.download = `clef-${suite}-${data.status === "completed" ? "verified" : "testdata-only"}.json`;
    a.click();
    win.setTimeout(() => win.URL.revokeObjectURL(url), 1000);
  });
  doc.addEventListener("keydown", (event) => {
    const target = event.target;
    if (
      ["INPUT", "TEXTAREA", "SELECT"].includes(target?.tagName) ||
      target?.isContentEditable ||
      event.ctrlKey ||
      event.metaKey ||
      event.altKey
    )
      return;
    if (event.key === "/" && route().view === "explorer") {
      event.preventDefault();
      setPane("cases");
      $("search").focus();
    }
    if (
      ["ArrowDown", "ArrowUp"].includes(event.key) &&
      target?.closest?.("#case-list")
    ) {
      event.preventDefault();
      const rows = filterCases(data.cases, filters),
        index = rows.findIndex((c) => c.id === selected),
        next = rows[index + (event.key === "ArrowDown" ? 1 : -1)];
      if (next) {
        selectCase(next.id, { mobile: false });
        $("case-list").querySelector(`[data-case="${next.id}"]`)?.focus();
      }
    }
  });
  async function init() {
    const failures = [];
    await Promise.all(
      Object.entries(SUITES).map(async ([id, definition]) => {
        const option = $("suite-select").querySelector(`[value="${id}"]`);
        try {
          const r = await fetcher(`./data/${definition.file}.json`, {
            cache: "no-store",
          });
          if (!r.ok) throw Error();
          const value = await r.json();
          validateDataset(value, id);
          suites[id] = value;
          option.disabled = false;
          option.textContent =
            definition.label +
            (value.status === "test_data_only"
              ? " · Ergebnisse ausstehend"
              : "");
        } catch {
          option.disabled = true;
          option.textContent = definition.label + " · nicht verfügbar";
          failures.push(id);
        }
      }),
    );
    const requested = route().params.get("suite"),
      initial = suites[requested]
        ? requested
        : suites.insurance
          ? "insurance"
          : Object.keys(SUITES).find((id) => suites[id]);
    if (!initial) {
      $("app-error").hidden = false;
      $("app-error").textContent =
        "Die Testdaten konnten nicht geladen werden. Starte python server.py im Repository und öffne die lokale Adresse. Das direkte Öffnen per file:// wird nicht unterstützt.";
      renderSuiteCatalog();
      await checkBackend();
      return false;
    }
    selectSuite(initial, { fromRoute: true });
    navigate();
    if (failures.length) {
      $("app-error").hidden = false;
      $("app-error").className = "notice neutral";
      $("app-error").textContent =
        `Nicht verfügbare Suiten: ${failures.map((id) => SUITES[id].label).join(", ")}. Verfügbare Tests können unabhängig davon geöffnet werden.`;
    }
    await checkBackend();
    return true;
  }
  custom = createCustomWorkspace({ document: doc, window: win, fetch: fetcher,
    isBusy: () => session.busy,
    getHealth: () => health,
    onBusy: (busy) => {
      const finished = customWasBusy && !busy;
      customWasBusy = busy;
      setPending(busy || session.busy); renderBackend();
      if (finished && !session.busy) void checkBackend();
    },
  });
  emptyOutput();
  return {
    custom,
    init,
    navigate,
    selectSuite,
    selectCase,
    setPane,
    loadExample,
    runLive,
    saved,
    checkBackend,
    resetFilters,
    getState: () => ({
      suite,
      selected,
      field,
      filters: { ...filters },
      pane,
      busy: session.busy,
      example: example?.id,
      health: { ...health },
    }),
  };
}
if (
  typeof document !== "undefined" &&
  typeof window !== "undefined" &&
  !globalThis.__CLEF_TEST__
) {
  createWorkbench().init();
}
