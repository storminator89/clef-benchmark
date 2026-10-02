export const CATEGORY = {
  it_routing: "IT- & M365-Routing",
  urgency: "Priorität & Negation",
  tool_selection: "Werkzeugauswahl",
  document_classification: "Dokumentfunktion",
  admin_intent: "Verwaltungsabsicht",
  ambiguity_abstain: "Mehrdeutigkeit",
};
export const SPLIT = {
  german_primary: "Deutsch / Deutsch",
  english_control: "Englisch / Englisch",
  mixed_schema_diagnostic: "Deutsch / Englisch",
  german_clean_primary: "Deutsch · ohne Manipulation",
  german_insurance_primary: "Deutsch · Dokumente",
  german_multidoc_primary: "Deutsch · Mehrere Dokumente",
  german_clarification_primary: "Deutsch · Rückfragen",
  german_bank_support_primary: "Deutsch · Bank-Kundensupport",
};
export const LIMITS = Object.freeze({
  state: 6000,
  questions: 8,
  options: 12,
  bodyBytes: 32768,
  tokens: 2048,
});
export const escapeHTML = (value) =>
  String(value ?? "").replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );
export const percent = (value, digits = 1) =>
  Number.isFinite(value)
    ? new Intl.NumberFormat("de-DE", {
        style: "percent",
        maximumFractionDigits: digits,
      }).format(value)
    : "—";
export const decimal = (value, digits = 2) =>
  Number.isFinite(value)
    ? new Intl.NumberFormat("de-DE", { maximumFractionDigits: digits }).format(
        value,
      )
    : "—";
export const isObject = (value) =>
  value !== null && typeof value === "object" && !Array.isArray(value);
const FIELD_LABELS = Object.freeze({ source: "Maßgebliche Quelle", decision: "Entscheidung", evidence: "Evidenz",
  action: "Nächster Schritt", determination: "Feststellung",
  intent: "Anliegen", priority: "Priorität", next_step: "Nächster Schritt" });
export const fieldLabel = (id) => Object.hasOwn(FIELD_LABELS, id)
  ? FIELD_LABELS[id] : id.replace(/_/g, " ");
export const choiceLabel = (field, key, criteria = {}) =>
  field === "decision" && ["ja", "nein", "offen", "konflikt"].includes(key)
    ? {
        ja: "Aussage gestützt",
        nein: "Aussage widerlegt",
        offen: "Information fehlt",
        konflikt: "Regelwiderspruch",
      }[key]
    : criteria[key] || key || "Nicht verfügbar";
export function runtimeLabel(runtime) {
  if (!runtime?.device || !runtime?.precision)
    return "Gerät und Präzision noch nicht geprüft";
  const backend =
    runtime.backend === "rocm"
      ? "AMD ROCm"
      : runtime.backend === "cpu"
        ? "CPU"
        : "Lokales Backend";
  return `${backend} · ${runtime.device_name || runtime.device} (${runtime.device}) · ${runtime.precision}`;
}
export function fieldsForCase(c) {
  if (!c) return [];
  return Object.entries(c.questions || {}).map(([id, schema]) => {
    const result =
      c.result?.fields?.[id] ||
      (id === "decision" && c.result?.prediction !== undefined
        ? c.result
        : null);
    return {
      id,
      schema,
      expected: c.expected?.[id],
      result: result
        ? {
            prediction: result.prediction,
            correct: result.correct === true,
            probabilities: result.probabilities || {},
            schema_valid: result.schema_valid === true,
          }
        : null,
    };
  });
}
export function outcome(c) {
  const fields = fieldsForCase(c);
  if (!c?.result) return "unscored";
  if (!fields.length)
    return c.result.correct === true
      ? "correct"
      : c.result.correct === false
        ? "wrong"
        : "unscored";
  if (fields.some((f) => !f.result)) return "unscored";
  return fields.every((f) => f.result.correct)
    ? "correct"
    : fields.some((f) => f.result.correct)
      ? "partial"
      : "wrong";
}
export function filterCases(cases, filters = {}) {
  const query = (filters.query || "").trim().toLocaleLowerCase("de");
  return cases.filter((c) => {
    const fields = fieldsForCase(c),
      o = outcome(c),
      kind = filters.outcome || (filters.errors ? "errors" : "");
    const matches =
      !kind ||
      (kind === "errors" && ["partial", "wrong"].includes(o)) ||
      (kind === "correct" && o === "correct") ||
      (kind === "unscored" && o === "unscored") ||
      fields.some((f) => f.id === kind && f.result?.correct === false) ||
      (kind.startsWith("diagnostic:") && (c.diagnostic_events || []).includes(kind.slice(11))) ||
      (kind.startsWith("multidoc:") && multidocEvents(c).includes(kind.slice(9)));
    return (
      (!filters.split || c.split === filters.split) &&
      (!filters.category || c.category === filters.category) &&
      (!filters.tag || (c.tags || []).includes(filters.tag)) &&
      matches &&
      (!query ||
        [
          c.id,
          c.title,
          c.input,
          c.scenario,
          c.message,
          c.service_policy,
          c.precedence, c.facts, c.question, c.family, c.stratum, c.subtype, c.template_id,
          ...Object.values(c.document_texts || {}),
          c.claim,
          c.document_id,
          c.area,
          ...(c.tags || []),
          ...fields.flatMap((f) => [f.expected, f.result?.prediction]),
        ]
          .join(" ")
          .toLocaleLowerCase("de")
          .includes(query))
    );
  });
}
/** Field-pair diagnostics for this bounded suite, not a general consistency rule.
 * In particular, source uncertainty does not imply answer uncertainty. */
export function multidocEvents(c) {
  if (!c?.result || !Array.isArray(c.documents)) return [];
  const source = c.result.fields?.source, answer = c.result.fields?.determination;
  if (!source || !answer) return [];
  const concrete = answer.prediction !== "unresolved";
  const own = c.documents.find(d => d.id === source.prediction);
  return [
    source.correct && !answer.correct && "source_right_answer_wrong",
    c.material_clarification && concrete && "missed_clarification",
    !c.material_clarification && !concrete && "excess_clarification",
    !c.material_clarification && concrete && !answer.correct && "wrong_definite_answer",
    c.source_uncertain_answer_definite && "same_answer_control",
    (source.prediction === "not_unique"
      ? c.material_clarification && concrete
      : !own || own.outcome !== answer.prediction) && "inconsistent_visible_rules",
  ].filter(Boolean);
}
function validateMultidocDataset(data, fail) {
  const equal = (a, b) => canonicalJSON(a) === canonicalJSON(b);
  const text = v => typeof v === "string" && v.trim().length > 0;
  const labels = (map, keys) => isObject(map) && equal(Object.keys(map).sort(), keys.sort()) && Object.values(map).every(text);
  const rows = data.cases;
  if (!labels(data.suite.categories, ["banking", "insurance", "finance"]) ||
      !labels(data.suite.strata, ["authority", "effective_date", "scope", "unresolved"])) fail();
  for (const c of rows) {
    if (Object.keys(c.questions).join("|") !== "source|determination" ||
        Object.keys(c.questions.source.criteria).sort().join("|") !== "D1|D2|D3|not_unique" ||
        Object.keys(c.questions.determination.criteria).sort().join("|") !== "no|unresolved|yes" ||
        Object.keys(c.expected).sort().join("|") !== "determination|source" ||
        [c.precedence, c.facts, c.question, c.family, c.stratum, c.subtype, c.template_id, c.gold_rationale].some(v => !text(v)) ||
        !Object.hasOwn(data.suite.categories, c.category) || !Object.hasOwn(data.suite.strata, c.stratum) ||
        !c.tags.includes(c.stratum) || c.synthetic !== true || c.manipulation !== false || c.document_id !== undefined ||
        !Array.isArray(c.documents) || c.documents.length !== 3 ||
        c.documents.map(d => d.id).sort().join("|") !== "D1|D2|D3" ||
        !labels(c.document_texts, ["D1", "D2", "D3"]) ||
        !Array.isArray(c.plausible_source_ids) || !c.plausible_source_ids.length ||
        new Set(c.plausible_source_ids).size !== c.plausible_source_ids.length ||
        c.plausible_source_ids.some(id => !["D1", "D2", "D3"].includes(id))) fail();
    const domain = {insurance: ["Schadenbetrag", "erstattungsfähig"], banking: ["Überweisungsbetrag", "gebührenfrei"], finance: ["Änderungsbetrag", "serviceentgeltfrei"]}[c.category];
    for (const d of c.documents) {
      if (![d.title, d.scope, d.publication, d.effective].every(text) ||
          !Number.isFinite(d.threshold) || d.threshold < 0 || !["yes", "no"].includes(d.outcome)) fail();
      const block = `Dokument ${d.id} — ${d.title}\nVeröffentlicht: ${d.publication}. Gültig ab: ${d.effective}. Geltungsbereich: ${d.scope}.\nVollständige Regel: ${domain[0]} bis einschließlich ${d.threshold} EUR: ${domain[1]} (Ja). Höhere Beträge: nicht ${domain[1]} (Nein).`;
      if (c.document_texts[d.id] !== block) fail();
    }
    const state = `Fiktiver abgeschlossener Testfall, keine echten Geschäftsbedingungen. Alle zur Entscheidung nötigen Vorrangregeln stehen hier.\nVorrang und Geltung: ${c.precedence}\n\n${c.documents.map(d => c.document_texts[d.id]).join("\n\n")}\n\nBekannte Fakten: ${c.facts}\nKundenfrage: ${c.question}`;
    if (c.input !== state) fail();
    const source = c.plausible_source_ids.length === 1 ? c.plausible_source_ids[0] : "not_unique";
    const answers = [...new Set(c.documents.filter(d => c.plausible_source_ids.includes(d.id)).map(d => d.outcome))];
    const answer = answers.length === 1 ? answers[0] : "unresolved";
    if (c.expected.source !== source || c.expected.determination !== answer ||
        c.material_clarification !== (answer === "unresolved") ||
        c.source_uncertain_answer_definite !== (source === "not_unique" && answer !== "unresolved") ||
        c.source_position !== (source === "not_unique" ? null : c.documents.findIndex(d => d.id === source) + 1)) fail();
    if (data.status === "completed") {
      if (!isObject(c.native_answers) || !isObject(c.probabilities_unrounded) ||
          Object.keys(c.native_answers).sort().join("|") !== "determination|source" ||
          Object.keys(c.probabilities_unrounded).sort().join("|") !== "determination|source") fail();
      for (const f of fieldsForCase(c)) {
        const native = c.native_answers[f.id];
        if (!isObject(native) || native.type !== "choice" || native.choice !== f.result.prediction ||
            !equal(c.probabilities_unrounded[f.id], f.result.probabilities) ||
            !Number.isFinite(native.confidence) || native.confidence < 0 || native.confidence > 1 ||
            Math.abs(native.confidence - f.result.probabilities[native.choice]) > .0001 ||
            !isObject(native.probabilities) ||
            !equal(Object.keys(native.probabilities).sort(), Object.keys(f.schema.criteria).sort()) ||
            Object.entries(native.probabilities).some(([id, p]) => !Number.isFinite(p) || p < 0 || p > 1 || Math.abs(p - f.result.probabilities[id]) > .0001)) fail();
      }
    }
  }
  const groupSizes = [["category",3,16], ["stratum",4,12], ["family",12,4], ["template_id",16,3], ["subtype",16,3]];
  for (const [key, count, size] of groupSizes) {
    const groups = [...new Set(rows.map(c => c[key]))];
    if (groups.length !== count || groups.some(id => rows.filter(c => c[key] === id).length !== size)) fail();
  }
  if (data.status !== "completed") return;
  const summary = data.summary;
  if (!isObject(summary) || summary.case_count !== 48 || summary.family_count !== 12 || summary.paired_order_intervention !== false) fail();
  const count = (pred, subset = rows) => subset.filter(pred).length;
  const ratio = (n, d) => ({ numerator: n, denominator: d, rate: d ? n / d : null });
  const correct = (c, f) => c.result.fields[f].correct;
  const metrics = subset => ({ source: ratio(count(c => correct(c, "source"), subset), subset.length),
    determination: ratio(count(c => correct(c, "determination"), subset), subset.length),
    all_fields_exact: ratio(count(c => c.result.correct, subset), subset.length) });
  const base = metrics(rows);
  if (base.source.numerator !== 42 || base.determination.numerator !== 24 || base.all_fields_exact.numerator !== 24 ||
      !equal(summary.case_metrics, { ...base, all_field_decisions: ratio(base.source.numerator + base.determination.numerator, rows.length * 2) })) fail();
  const unique = rows.filter(c => c.expected.source !== "not_unique"), ambiguous = rows.filter(c => c.expected.source === "not_unique");
  const controls = rows.filter(c => c.source_uncertain_answer_definite), required = rows.filter(c => c.material_clarification), answerable = rows.filter(c => !c.material_clarification);
  if (unique.length !== 27 || ambiguous.length !== 21 || controls.length !== 9 || required.length !== 12) fail();
  const sources = {
    unique_source_correct: ratio(count(c => correct(c,"source"), unique), unique.length),
    wrong_concrete_source: ratio(count(c => !correct(c,"source") && c.result.fields.source.prediction !== "not_unique", unique), unique.length),
    unnecessary_source_uncertainty: ratio(count(c => c.result.fields.source.prediction === "not_unique", unique), unique.length),
    ambiguous_source_correct: ratio(count(c => correct(c,"source"), ambiguous), ambiguous.length),
    invented_unique_source: ratio(count(c => c.result.fields.source.prediction !== "not_unique", ambiguous), ambiguous.length),
    same_answer_ambiguous_source_exact: ratio(count(c => c.result.correct, controls), controls.length),
  };
  const has = (c, event) => multidocEvents(c).includes(event);
  const clarification = {
    missed: ratio(count(c => has(c,"missed_clarification")), required.length),
    excess: ratio(count(c => has(c,"excess_clarification")), answerable.length),
    wrong_definite_answer_on_answerable: ratio(count(c => has(c,"wrong_definite_answer")), answerable.length),
    invalid_on_required: ratio(0, required.length), invalid_on_answerable: ratio(0, answerable.length),
    same_answer_control_excess: ratio(count(c => has(c,"excess_clarification"), controls), controls.length),
  };
  if (!equal(summary.source_metrics, sources) || !equal(summary.clarification_metrics, clarification) ||
      !equal(summary.consistency?.field_pair_inconsistent_with_visible_rules, ratio(count(c => has(c,"inconsistent_visible_rules")), rows.length)) ||
      !text(summary.consistency?.scope) || !equal(summary.error_case_ids, rows.filter(c => !c.result.correct).map(c => c.id)) ||
      !isObject(summary.strata)) fail();
  for (const [key] of groupSizes) {
    const groups = Object.fromEntries([...new Set(rows.map(c => c[key]))].map(id => {
      const subset = rows.filter(c => c[key] === id), m = metrics(subset);
      return [id, { count: subset.length, all_fields_exact: m.all_fields_exact, source_correct: m.source,
        determination_correct: m.determination, invalid_or_missing: 0, wrong_source_including_unknown: subset.length - m.source.numerator }];
    }));
    if (!equal(summary.strata[key === "category" ? "domain" : key], groups)) fail();
  }
}
export function probabilities(c) {
  return Object.entries(c?.probabilities || {})
    .filter(([, v]) => Number.isFinite(v))
    .sort((a, b) => b[1] - a[1]);
}
export function canonicalJSON(value) {
  if (Array.isArray(value))
    return "[" + value.map(canonicalJSON).join(",") + "]";
  if (isObject(value))
    return (
      "{" +
      Object.keys(value)
        .sort()
        .map((k) => JSON.stringify(k) + ":" + canonicalJSON(value[k]))
        .join(",") +
      "}"
    );
  return JSON.stringify(value);
}
/** Vendor encodes question fields in insertion order but sorts option IDs. */
export function requestFingerprint(request) {
  return request
    ? canonicalJSON({
        state: request.state,
        questions: Object.entries(request.questions),
      })
    : null;
}
/** JSON.parse gives syntax validation; this additional walk rejects ambiguous duplicate object keys. */
export function parseJSONStrict(text) {
  const value = JSON.parse(text);
  let i = 0;
  const ws = () => {
    while (/\s/.test(text[i] || "") && i < text.length) i++;
  };
  function str() {
    const start = i++;
    while (i < text.length) {
      if (text[i] === "\\") {
        i += 2;
        continue;
      }
      if (text[i++] === '"') break;
    }
    return JSON.parse(text.slice(start, i));
  }
  function walk() {
    ws();
    if (text[i] === "{") {
      i++;
      ws();
      const keys = new Set();
      if (text[i] === "}") {
        i++;
        return;
      }
      while (i < text.length) {
        ws();
        const key = str();
        if (keys.has(key)) throw Error(`Doppelter JSON-Schlüssel: ${key}`);
        keys.add(key);
        ws();
        i++;
        walk();
        ws();
        if (text[i++] === "}") return;
      }
    } else if (text[i] === "[") {
      i++;
      ws();
      if (text[i] === "]") {
        i++;
        return;
      }
      while (i < text.length) {
        walk();
        ws();
        if (text[i++] === "]") return;
      }
    } else if (text[i] === '"') {
      str();
    } else {
      while (i < text.length && !/[\s,}\]]/.test(text[i])) i++;
    }
  }
  walk();
  return value;
}
export function validatePlayground(state, questions) {
  if (
    typeof state !== "string" ||
    !state.trim() ||
    [...state].length > LIMITS.state
  )
    throw Error("Bitte gib einen Text mit 1 bis 6.000 Zeichen ein.");
  if (
    !isObject(questions) ||
    Object.keys(questions).length < 1 ||
    Object.keys(questions).length > LIMITS.questions
  )
    throw Error("Das Schema muss 1 bis 8 choice-Fragen enthalten.");
  const id = /^[A-Za-z][A-Za-z0-9_-]{0,63}$/;
  for (const [name, q] of Object.entries(questions)) {
    if (
      !id.test(name) ||
      !isObject(q) ||
      Object.keys(q).sort().join(",") !== "criteria,instructions,type" ||
      q.type !== "choice"
    )
      throw Error(
        "Jede Frage braucht type: choice, instructions und criteria.",
      );
    if (
      typeof q.instructions !== "string" ||
      !q.instructions.trim() ||
      [...q.instructions].length > 4000
    )
      throw Error("Jede Richtlinie muss 1 bis 4.000 Zeichen enthalten.");
    if (
      !isObject(q.criteria) ||
      Object.keys(q.criteria).length < 2 ||
      Object.keys(q.criteria).length > LIMITS.options
    )
      throw Error("Jede Frage braucht 2 bis 12 Auswahloptionen.");
    for (const [key, description] of Object.entries(q.criteria))
      if (
        !id.test(key) ||
        typeof description !== "string" ||
        !description.trim() ||
        [...description].length > 300
      )
        throw Error(
          "Jede Option braucht eine ID und eine Beschreibung (1–300 Zeichen).",
        );
  }
  const request = { state, questions };
  if (
    new TextEncoder().encode(JSON.stringify(request)).length > LIMITS.bodyBytes
  )
    throw Error(
      "Die gesamte Anfrage ist größer als 32 KiB. Bitte Text oder Schema kürzen.",
    );
  return request;
}
/** Refuse partial, unknown or malformed fields instead of displaying a plausible first answer. */
export function validateLiveResult(result, request) {
  const fail = () => {
    throw Error(
      "Die Antwort ist unvollständig oder passt nicht zum angefragten Schema. Es wird kein Teilergebnis angezeigt.",
    );
  };
  if (
    !isObject(result) ||
    result.source !== "live_local_inference" ||
    result.truncated !== false ||
    !Number.isInteger(result.input_tokens) ||
    result.input_tokens < 1 ||
    result.input_tokens > LIMITS.tokens ||
    !Number.isFinite(result.latency_ms) ||
    result.latency_ms < 0
  )
    fail();
  const ids = Object.keys(request.questions).sort();
  if (
    !isObject(result.answers) ||
    !isObject(result.probabilities_unrounded) ||
    Object.keys(result.answers).sort().join("|") !== ids.join("|") ||
    Object.keys(result.probabilities_unrounded).sort().join("|") !==
      ids.join("|")
  )
    fail();
  for (const [id, q] of Object.entries(request.questions)) {
    const answer = result.answers[id],
      probs = result.probabilities_unrounded[id],
      options = Object.keys(q.criteria).sort();
    if (
      !isObject(answer) ||
      answer.type !== "choice" ||
      !options.includes(answer.choice) ||
      !isObject(probs) ||
      Object.keys(probs).sort().join("|") !== options.join("|")
    )
      fail();
    const values = Object.values(probs);
    if (
      values.some((v) => !Number.isFinite(v) || v < 0 || v > 1) ||
      Math.abs(values.reduce((a, b) => a + b, 0) - 1) > 1e-5 ||
      probs[answer.choice] !== Math.max(...values)
    )
      fail();
  }
  return result;
}
export function suiteStats(data) {
  const primary = data.cases.filter(
      (c) => c.split === data.suite.primary_split,
    ),
    complete = data.status === "completed",
    fieldIDs = [
      ...new Set(primary.flatMap((c) => Object.keys(c.questions || {}))),
    ];
  const fields = Object.fromEntries(
    fieldIDs.map((id) => {
      const rows = primary.filter((c) => id in c.questions);
      return [
        id,
        {
          correct: complete
            ? rows.filter(
                (c) =>
                  fieldsForCase(c).find((f) => f.id === id)?.result?.correct,
              ).length
            : null,
          total: rows.length,
        },
      ];
    }),
  );
  return {
    primary,
    complete,
    fields,
    exact: complete
      ? primary.filter((c) => outcome(c) === "correct").length
      : null,
    total: primary.length,
    valid: complete
      ? primary.filter((c) =>
          fieldsForCase(c).every((f) => f.result?.schema_valid),
        ).length
      : null,
  };
}
export const bankServicePolicy = (questions) =>
  ["intent", "priority", "next_step"].map((id) => questions[id]?.instructions || "").join("\n\n");
/** Defined priority ordering, recomputed from admitted case fields, never a supplied KPI. */
export function bankPriorityCounts(cases) {
  const rank = { routine: 0, urgent: 1, critical: 2 };
  const values = cases.map((c) => ({ gold: c.expected?.priority,
    predicted: fieldsForCase(c).find((f) => f.id === "priority")?.result?.prediction }));
  if (values.some((v) => !Object.hasOwn(rank, v.gold) || !Object.hasOwn(rank, v.predicted))) return null;
  const next = (c) => fieldsForCase(c).find((f) => f.id === "next_step")?.result?.prediction;
  return {
    gold_non_escalation: cases.filter((c) => ["guidance", "clarify"].includes(c.expected?.next_step)).length,
    unnecessary_escalations: cases.filter((c) => ["guidance", "clarify"].includes(c.expected?.next_step) &&
      ["specialist_review", "security_handoff"].includes(next(c))).length,
    critical_handoff_misses: cases.filter((c) => c.expected?.priority === "critical" && next(c) !== "security_handoff").length,
    unnecessary_critical: values.filter((v) => v.gold !== "critical" && v.predicted === "critical").length,
    critical_all_fields_correct: cases.filter((c) => c.expected?.priority === "critical" && outcome(c) === "correct").length,
    gold_routine: values.filter((v) => v.gold === "routine").length,
    excess_security_handoffs: cases.filter((c) => c.expected?.next_step !== "security_handoff" &&
      fieldsForCase(c).find((f) => f.id === "next_step")?.result?.prediction === "security_handoff").length,
    gold_critical: values.filter((v) => v.gold === "critical").length,
    missed_critical: values.filter((v) => v.gold === "critical" && v.predicted !== "critical").length,
    gold_urgent: values.filter((v) => v.gold === "urgent").length,
    missed_urgent: values.filter((v) => v.gold === "urgent" && v.predicted === "routine").length,
    undertriage: values.filter((v) => rank[v.predicted] < rank[v.gold]).length,
    overtriage: values.filter((v) => rank[v.predicted] > rank[v.gold]).length,
  };
}
export function evidenceIDs(c, kind) {
  const field = fieldsForCase(c).find((f) => f.id === "evidence");
  if (!field) return [];
  return kind === "gold"
    ? c.expected?.evidence_clauses || c.evidence_options?.[field.expected] || []
    : field.result
      ? c.result.actual_evidence_clauses ||
        c.evidence_options?.[field.result.prediction] ||
        []
      : [];
}
export function documentForCase(c, data) {
  return data.documents?.find((d) => d.id === c?.document_id) || null;
}
/** One request owns its editor snapshot, even when the explorer navigates elsewhere. */
export class InferenceSession {
  #active = null;
  #serial = 0;
  get busy() {
    return this.#active !== null;
  }
  begin() {
    if (this.busy) throw Error("Eine Inferenz läuft bereits.");
    this.#active = ++this.#serial;
    return this.#active;
  }
  isCurrent(token) {
    return this.#active === token;
  }
  finish(token) {
    if (!this.isCurrent(token)) return false;
    this.#active = null;
    return true;
  }
  edit(callback) {
    if (this.busy) return false;
    callback();
    return true;
  }
}
/** Recompute clarification presentation data from admitted native choices.
 * This verifies annotations; it never repairs inconsistent model field pairs. */
function validateClarificationSummary(data, fail) {
  const rows = data.cases, summary = data.summary;
  const fields = ["action", "determination"], thresholds = [0.8, 0.9, 0.95];
  const strata = ["ambiguous_target", "missing_fact", "conflicting_evidence",
    "complete_yes", "complete_no", "sufficient_despite_omission"];
  const equal = (actual, expected) => canonicalJSON(actual) === canonicalJSON(expected);
  const labels = (value, keys) => isObject(value) &&
    equal(Object.keys(value).sort(), [...keys].sort()) &&
    Object.values(value).every(v => typeof v === "string" && v.trim());
  if (!labels(data.suite.strata, strata) ||
      !labels(data.suite.categories, ["finance", "insurance", "banking"])) fail();
  if (data.status !== "completed") return;
  if (!isObject(summary) || summary.suite_id !== "clarification" ||
      summary.case_count !== rows.length || summary.field_count !== 2) fail();
  const ratio = (numerator, denominator) => ({ numerator, denominator,
    rate: denominator ? numerator / denominator : null });
  const correct = (c, f) => c.result.fields[f].prediction === c.expected[f];
  const metrics = group => Object.fromEntries([
    ...fields.map(f => [f, ratio(group.filter(c => correct(c, f)).length, group.length)]),
    ["all_fields_exact", ratio(group.filter(c => fields.every(f => correct(c, f))).length, group.length)],
  ]);
  const events = Object.fromEntries([
    "invalid_or_missing", "missed_required_clarifications",
    "required_clarifications_not_successfully_requested", "excess_clarifications",
    "wrong_clarification_kind", "inconsistent_fields", "substantive_answer_cases",
    "risky_wrong_answers", ...thresholds.flatMap(t =>
      [`confident_answers_${t}`, `confident_wrong_answers_${t}`]),
  ].map(name => [name, []]));
  for (const c of rows) {
    const action = c.result.fields.action, determination = c.result.fields.determination;
    const required = c.expected.action !== "answer", asked = action.prediction !== "answer";
    const concrete = !asked && determination.prediction !== "unresolved";
    const risky = concrete && (required || !correct(c, "determination"));
    const flags = {
      missed_required_clarifications: required && !asked,
      required_clarifications_not_successfully_requested: required && !asked,
      excess_clarifications: !required && asked,
      wrong_clarification_kind: required && asked && !correct(c, "action"),
      inconsistent_fields: asked ? determination.prediction !== "unresolved" : determination.prediction === "unresolved",
      substantive_answer_cases: concrete, risky_wrong_answers: risky,
    };
    for (const threshold of thresholds) {
      const confident = concrete && action.probabilities[action.prediction] >= threshold &&
        determination.probabilities[determination.prediction] >= threshold;
      flags[`confident_answers_${threshold}`] = confident;
      flags[`confident_wrong_answers_${threshold}`] = confident && risky;
    }
    const expectedEvents = Object.keys(flags).filter(name => flags[name]);
    if (!equal([...c.diagnostic_events].sort(), expectedEvents.sort()) ||
        !equal([...c.tags].sort(), [c.stratum, c.family].sort())) fail();
    for (const name of expectedEvents) events[name].push(c.id);
  }
  const count = name => events[name].length;
  const required = rows.filter(c => c.expected.action !== "answer").length;
  const answerable = rows.length - required, expectedMetrics = metrics(rows);
  expectedMetrics.all_field_decisions = ratio(fields.reduce((n, f) =>
    n + expectedMetrics[f].numerator, 0), rows.length * 2);
  const behavior = Object.fromEntries([
    ["missed_required_clarifications", required],
    ["required_clarifications_not_successfully_requested", required],
    ["excess_clarifications", answerable], ["wrong_clarification_kind", required],
    ["risky_wrong_answers_all_cases", rows.length],
    ["risky_wrong_answers_among_substantive", count("substantive_answer_cases")],
  ].map(([name, denominator]) => [name,
    ratio(count(name.startsWith("risky_wrong_answers_") ? "risky_wrong_answers" : name), denominator)]));
  const high = Object.fromEntries(thresholds.map(t => {
    const confident = count(`confident_answers_${t}`), wrong = count(`confident_wrong_answers_${t}`);
    return [t, { confident_answers: confident, confident_wrong: wrong,
      wrong_rate_among_confident: ratio(wrong, confident) }];
  }));
  const grouped = Object.fromEntries([["domain", "category"], ["stratum", "stratum"], ["family", "family"]]
    .map(([name, attribute]) => [name, Object.fromEntries([...new Set(rows.map(c => c[attribute]))].map(id => {
      const group = rows.filter(c => c[attribute] === id);
      return [id, { cases: group.length, ...metrics(group) }];
    }))]));
  // These balances also support the fixed explanatory copy for this frozen suite.
  if (required !== 36 || answerable !== 36 || count("inconsistent_fields") !== 3 ||
      high["0.9"].confident_answers !== 5 || high["0.9"].confident_wrong !== 0 ||
      !equal(Object.keys(grouped.domain).sort(), Object.keys(data.suite.categories).sort()) ||
      Object.values(grouped.domain).some(g => g.cases !== 24) ||
      !equal(Object.keys(grouped.stratum).sort(), [...strata].sort()) ||
      Object.values(grouped.stratum).some(g => g.cases !== 12) ||
      Object.keys(grouped.family).length !== 12 || Object.values(grouped.family).some(g => g.cases !== 6)) fail();
  for (const [key, expected] of Object.entries({
    metrics: expectedMetrics,
    denominators: { clarification_required: required, answerable, valid_cases: rows.length,
      substantive_answers: count("substantive_answer_cases") },
    behavior_rates: behavior, high_confidence: high, strata: grouped,
    events: Object.fromEntries(Object.entries(events).map(([name, ids]) => [name, { count: ids.length, ids }])),
  })) if (!isObject(summary[key]) || !equal(summary[key], expected)) fail();
}
/** Admit a stored suite only after full local structural checks. This supplements,
 * rather than replaces, the frozen-file/independent-hash importer gate. */
export function validateDataset(data, expectedID) {
  const fail = () => {
    throw Error("Der Datensatz ist unvollständig oder nicht verifiziert.");
  };
  if (
    !isObject(data) ||
    !["completed", "test_data_only"].includes(data.status) ||
    !isObject(data.suite) ||
    data.suite.id !== expectedID ||
    typeof data.suite.primary_split !== "string" ||
    !Array.isArray(data.cases) ||
    !data.cases.length
  )
    fail();
  const plans = {
    insurance: [60, 60, "german_insurance_primary"],
    general: [180, 120, "german_primary"],
    finance: [100, 80, "german_primary"],
    clean72: [72, 72, "german_clean_primary"],
    "bank-support": [80, 80, "german_bank_support_primary"],
    clarification: [72, 72, "german_clarification_primary"],
    multidoc: [48, 48, "german_multidoc_primary"],
  };
  const plan = plans[expectedID];
  if (
    !plan ||
    data.cases.length !== plan[0] ||
    data.suite.primary_split !== plan[2] ||
    data.cases.filter((c) => c.split === plan[2]).length !== plan[1]
  )
    fail();
  if (
    data.verification?.n_present !== undefined &&
    data.verification.n_present !== plan[0]
  )
    fail();
  const complete = data.status === "completed",
    ids = new Set(),
    documentIDs = new Set();
  if (
    complete &&
    data.verification?.status !==
      (expectedID === "insurance" ? "verified" : "pass")
  )
    fail();
  if (!complete && (data.summary !== undefined || data.scores !== undefined))
    fail();
  if (
    expectedID === "insurance" &&
    (!Array.isArray(data.documents) || data.documents.length !== 12)
  )
    fail();
  if (data.documents !== undefined) {
    if (!Array.isArray(data.documents)) fail();
    for (const d of data.documents) {
      if (
        !isObject(d) ||
        typeof d.id !== "string" ||
        documentIDs.has(d.id) ||
        typeof d.title !== "string" ||
        !Array.isArray(d.clauses) ||
        !d.clauses.length
      )
        fail();
      documentIDs.add(d.id);
      const clauseIDs = new Set();
      for (const cl of d.clauses) {
        if (
          !isObject(cl) ||
          typeof cl.id !== "string" ||
          !cl.id ||
          clauseIDs.has(cl.id) ||
          typeof cl.text !== "string"
        )
          fail();
        clauseIDs.add(cl.id);
      }
    }
  }
  for (const c of data.cases) {
    if (
      !isObject(c) ||
      typeof c.id !== "string" ||
      !/^[A-Za-z][A-Za-z0-9_-]{0,100}$/.test(c.id) ||
      ids.has(c.id) ||
      typeof c.split !== "string" ||
      typeof c.category !== "string" ||
      !Array.isArray(c.tags) ||
      c.tags.some((t) => typeof t !== "string") ||
      !isObject(c.expected)
    )
      fail();
    ids.add(c.id);
    try {
      validatePlayground(c.input, c.questions);
    } catch {
      fail();
    }
    if (
      expectedID === "insurance" &&
      (typeof c.document_id !== "string" ||
        !documentIDs.has(c.document_id) ||
        Object.keys(c.questions).sort().join("|") !== "decision|evidence" ||
        Object.keys(c.questions.decision.criteria).length !== 4 ||
        Object.keys(c.questions.evidence.criteria).length !== 5)
    )
      fail();
    if (
      !["insurance", "bank-support", "clarification", "multidoc"].includes(expectedID) &&
      Object.keys(c.questions).join("|") !== "decision"
    )
      fail();
    if (
      expectedID === "bank-support" &&
      (Object.keys(c.questions).join("|") !== "intent|priority|next_step" ||
        Object.keys(c.questions.priority?.criteria || {}).sort().join("|") !== "critical|routine|urgent" ||
        Object.keys(c.questions.next_step?.criteria || {}).sort().join("|") !== "clarify|guidance|security_handoff|specialist_review" ||
        Object.keys(c.expected).sort().join("|") !== "intent|next_step|priority" ||
        typeof c.message !== "string" || !c.message.trim() || c.input !== `Synthetische Kundennachricht:\n${c.message}` ||
        typeof c.service_policy !== "string" || !c.service_policy.trim() ||
        c.service_policy !== bankServicePolicy(c.questions) ||
        typeof c.gold_rationale !== "string" || !c.gold_rationale.trim() ||
        c.synthetic !== true || c.manipulation !== false ||
        c.document_id !== undefined)
    ) fail();
    if (expectedID === "clarification" && (
      Object.keys(c.questions).join("|") !== "action|determination" ||
      Object.keys(c.questions.action?.criteria || {}).sort().join("|") !== "answer|ask_fact|ask_target|resolve_conflict" ||
      Object.keys(c.questions.determination?.criteria || {}).sort().join("|") !== "no|unresolved|yes" ||
      Object.keys(c.expected).sort().join("|") !== "action|determination" ||
      [c.rule, c.message, c.question, c.gold_rationale, c.family, c.stratum].some(v => typeof v !== "string" || !v.trim()) ||
      c.input !== `Fiktive Testregel:\n${c.rule}\n\nSynthetische Anfrage und Unterlagen:\n${c.message}\n\nZu beurteilende Eigenschaft:\n${c.question}` ||
      !Array.isArray(c.diagnostic_events) || c.diagnostic_events.some(v => typeof v !== "string") ||
      c.synthetic !== true || c.manipulation !== false || c.document_id !== undefined
    )) fail();
    if (!complete && c.result !== undefined) fail();
    const fields = fieldsForCase(c),
      questionIDs = Object.keys(c.questions).sort();
    if (
      c.result?.fields &&
      Object.keys(c.result.fields).sort().join("|") !== questionIDs.join("|")
    )
      fail();
    for (const f of fields) {
      const choices = Object.keys(f.schema.criteria).sort();
      if (!choices.includes(f.expected)) fail();
      if (complete) {
        const result =
          c.result?.fields?.[f.id] || (f.id === "decision" ? c.result : null);
        if (
          !isObject(result) ||
          result.schema_valid !== true ||
          typeof result.correct !== "boolean" ||
          !choices.includes(result.prediction) ||
          result.correct !== (result.prediction === f.expected) ||
          !isObject(result.probabilities) ||
          Object.keys(result.probabilities).sort().join("|") !==
            choices.join("|")
        )
          fail();
        const probs = Object.values(result.probabilities);
        if (
          probs.some((p) => !Number.isFinite(p) || p < 0 || p > 1) ||
          Math.abs(probs.reduce((a, b) => a + b, 0) - 1) > 1e-5 ||
          result.probabilities[result.prediction] !== Math.max(...probs)
        )
          fail();
      }
    }
    if (
      complete &&
      (c.result.correct !== fields.every((f) => f.result?.correct) ||
        !Number.isInteger(c.input_tokens) ||
        c.input_tokens < 1 ||
        c.input_tokens > LIMITS.tokens ||
        !Number.isFinite(c.latency_ms) ||
        c.latency_ms < 0)
    )
      fail();
    if (c.document_id) {
      const d = data.documents?.find((d) => d.id === c.document_id);
      if (
        !d ||
        !isObject(c.evidence_options) ||
        !Array.isArray(c.expected.evidence_clauses)
      )
        fail();
      const allowed = new Set(d.clauses.map((cl) => cl.id));
      for (const clauseSet of Object.values(c.evidence_options)) {
        if (
          !Array.isArray(clauseSet) ||
          !clauseSet.length ||
          clauseSet.some((id) => !allowed.has(id))
        )
          fail();
      }
      const equal = (a, b) =>
        Array.isArray(a) &&
        Array.isArray(b) &&
        a.length === b.length &&
        [...a].sort().join("|") === [...b].sort().join("|");
      if (
        !equal(
          c.expected.evidence_clauses,
          c.evidence_options[c.expected.evidence],
        )
      )
        fail();
      if (
        complete &&
        !equal(
          c.result.actual_evidence_clauses,
          c.evidence_options[c.result.fields.evidence.prediction],
        )
      )
        fail();
    }
  }
  if (!data.cases.some((c) => c.split === data.suite.primary_split)) fail();
  if (expectedID === "clarification") validateClarificationSummary(data, fail);
  if (expectedID === "multidoc") validateMultidocDataset(data, fail);
  return data;
}
