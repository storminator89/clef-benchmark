import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import {
  harness,
  datasets,
  completeFixture,
  liveFixture,
  bankFixture,
} from "./helpers/dom.mjs";
import {
  fieldsForCase,
  fieldLabel,
  outcome,
  filterCases,
  parseJSONStrict,
  validatePlayground,
  validateLiveResult,
  requestFingerprint,
  suiteStats,
  bankPriorityCounts,
  bankServicePolicy,
  validateDataset,
  evidenceIDs,
} from "../web/core.js";
test("initial document workspace loads frozen insurance, both fields and no invented pending values", async () => {
  const pending = structuredClone(datasets.insurance);
  pending.status = "test_data_only";
  delete pending.summary;
  for (const c of pending.cases) {
    delete c.result;
    delete c.latency_ms;
    delete c.input_tokens;
  }
  const h = await harness({ insurance: pending });
  assert.equal(h.app.getState().suite, "insurance");
  assert.equal(h.document.querySelectorAll(".case-item").length, 60);
  assert.equal(h.document.querySelectorAll("[data-field]").length, 2);
  assert.match(h.$("case-detail").textContent, /Noch unbewertet/);
  assert.equal(h.document.querySelectorAll("#case-detail .prob-row").length, 0);
  assert.ok(
    [...h.document.querySelectorAll(".stat-value")].every(
      (el) => el.textContent === "—",
    ),
  );
  assert.match(h.$("workbench-source-title").textContent, /Testdaten/);
  assert.equal(h.$("run-live").disabled, true);
  assert.equal(h.$("show-saved").disabled, true);
});
test("deep link selects suite, exact case and evidence field without being overwritten", async () => {
  const h = await harness({
    hash: "#explorer?suite=insurance&case=fall_031&field=evidence",
  });
  assert.equal(h.app.getState().selected, "fall_031");
  assert.equal(h.app.getState().field, "evidence");
  assert.match(h.$("case-detail").textContent, /Welche Klauseln/);
  assert.equal(
    h.document
      .querySelector('[data-field="evidence"]')
      .getAttribute("aria-pressed"),
    "true",
  );
});
test("case selection, previous/next, field switching and mobile pane choice are real DOM flows", async () => {
  const h = await harness();
  h.click('[data-case="fall_002"]');
  assert.equal(h.app.getState().selected, "fall_002");
  assert.equal(h.app.getState().pane, "document");
  h.click('[data-direction="1"]');
  assert.equal(h.app.getState().selected, "fall_003");
  h.click('[data-pane="result"]');
  assert.equal(h.$("workbench-shell").dataset.mobilePane, "result");
  h.click('[data-field="evidence"]');
  assert.equal(h.app.getState().field, "evidence");
  h.click('[data-pane="cases"]');
  assert.equal(h.$("workbench-shell").dataset.mobilePane, "cases");
});
test("gold/model evidence links highlight only the actual selected clause sets", async () => {
  const fixture = completeFixture(),
    h = await harness({ insurance: fixture }),
    c = fixture.cases[0];
  h.click('[data-evidence="gold"]');
  assert.deepEqual(
    [...h.document.querySelectorAll(".highlight-gold")].map(
      (el) => el.dataset.clauseId,
    ),
    c.expected.evidence_clauses,
  );
  assert.equal(h.document.querySelectorAll(".highlight-model").length, 0);
  h.click('[data-evidence="model"]');
  assert.deepEqual(
    [...h.document.querySelectorAll(".highlight-model")].map(
      (el) => el.dataset.clauseId,
    ),
    c.result.actual_evidence_clauses,
  );
  assert.equal(h.app.getState().pane, "document");
  h.change("highlight-select", "none");
  assert.equal(
    h.document.querySelectorAll(
      ".highlight-model,.highlight-gold,.highlight-both",
    ).length,
    0,
  );
  const clause = fixture.documents.find((d) => d.id === c.document_id)
    .clauses[0];
  h.click(`[data-clause="${clause.id}"]`);
  assert.ok(
    h.document
      .querySelector(`[data-clause="${clause.id}"]`)
      .classList.contains("active"),
  );
});
test("error filters distinguish decision from evidence and zero results clear stale document/result", async () => {
  const h = await harness({ insurance: completeFixture() });
  h.change("filter-outcome", "evidence");
  assert.equal(h.document.querySelectorAll(".case-item").length, 1);
  h.change("filter-outcome", "decision");
  assert.equal(h.document.querySelectorAll(".case-item").length, 0);
  assert.equal(h.document.querySelectorAll(".document-section").length, 0);
  assert.equal(h.$("open-playground").disabled, true);
  h.click("#reset-filters");
  assert.equal(h.document.querySelectorAll(".case-item").length, 60);
  h.change("search", "unfindable-string-xyz", "input");
  assert.match(h.$("case-list").textContent, /Keine passenden Fälle/);
  h.click("#reset-filters");
  assert.equal(h.document.querySelectorAll(".case-item").length, 60);
});
test("all historical suites retain their denominators, scores, language pairs and separate counts", async () => {
  const h = await harness();
  for (const [id, n, accuracy, errors, pairs] of [
    ["general", 120, "96,7", 4, true],
    ["finance", 80, "95", 4, true],
    ["clean72", 72, "84,7", 11, false],
  ]) {
    assert.equal(h.app.selectSuite(id), true);
    assert.equal(h.document.querySelectorAll(".case-item").length, n);
    assert.ok(
      h.document.querySelector(".stat-value").textContent.startsWith(accuracy),
    );
    assert.equal(h.$("paired-panel").hidden, !pairs);
    h.change("filter-outcome", "errors");
    assert.equal(h.document.querySelectorAll(".case-item").length, errors);
  }
  h.app.selectSuite("general");
  h.change("filter-split", "english_control");
  assert.equal(h.document.querySelectorAll(".case-item").length, 30);
  h.change("filter-split", "mixed_schema_diagnostic");
  assert.equal(h.document.querySelectorAll(".case-item").length, 30);
});
test("stored replay renders every field; edits and malformed JSON immediately remove all old output", async () => {
  const h = await harness({ insurance: completeFixture() });
  h.click("#open-playground");
  assert.equal(h.window.location.hash, "#playground");
  h.click("#show-saved");
  assert.equal(h.document.querySelectorAll("[data-output-field]").length, 2);
  assert.equal(h.$("output-kind").textContent, "Gespeicherte Inferenz");
  const original = h.$("input-state").value;
  h.change("input-state", original + " Geändert.", "input");
  assert.equal(h.$("show-saved").disabled, true);
  assert.equal(h.document.querySelectorAll("[data-output-field]").length, 0);
  h.change("input-state", original, "input");
  assert.equal(h.$("show-saved").disabled, false);
  h.change("input-schema", "{", "input");
  assert.equal(h.$("show-saved").disabled, true);
  h.change("example-select", "fall_002");
  h.click("#show-saved");
  h.click("#show-saved");
  assert.equal(h.document.querySelectorAll("[data-output-field]").length, 2);
  h.click("#new-request");
  assert.equal(h.document.querySelectorAll("[data-output-field]").length, 0);
  assert.equal(h.$("input-state").value, "");
  assert.equal(h.$("show-saved").disabled, true);
});
test("multi-field live pending flow keeps its editor snapshot through navigation and repeated clicks", async () => {
  let resolve;
  const deferred = new Promise((r) => (resolve = r)),
    h = await harness({
      enabled: true,
      insurance: completeFixture(),
      requestHandler: () => deferred,
    });
  const original = h.$("input-state").value,
    originalSchema = h.$("input-schema").value;
  const run = h.app.runLive();
  assert.equal(h.app.getState().busy, true);
  assert.equal(h.$("input-state").disabled, true);
  assert.equal(h.$("suite-select").disabled, true);
  assert.equal(h.$("show-saved").disabled, true);
  assert.equal(await h.app.runLive(), false);
  h.app.selectCase("fall_002");
  assert.equal(h.app.loadExample("fall_002"), false);
  assert.equal(h.app.selectSuite("finance"), false);
  h.window.location.hash = "method";
  h.window.location.hash = "playground";
  assert.equal(h.$("input-state").value, original);
  assert.equal(h.$("input-schema").value, originalSchema);
  const request = JSON.parse(
    h.calls.find((c) => c.url === "/api/infer").options.body,
  );
  resolve({ ok: true, json: async () => liveFixture(request) });
  assert.equal(await run, true);
  assert.equal(h.document.querySelectorAll("[data-output-field]").length, 2);
  assert.equal(h.$("output-kind").textContent, "Neue echte Inferenz");
  assert.equal(h.app.getState().busy, false);
  assert.equal(h.$("input-state").disabled, false);
  assert.equal(h.calls.filter((c) => c.url === "/api/infer").length, 1);
  assert.equal(h.app.getState().example, "fall_001");
  assert.match(h.$("playground-output").textContent, /Test-only CPU fixture/);
});
test("live server errors clear replay, release locks and remain distinct from benchmark results", async () => {
  const h = await harness({
    enabled: true,
    insurance: completeFixture(),
    requestHandler: async () => ({
      ok: false,
      status: 422,
      json: async () => ({
        error: "Input exceeds 2048 tokens; nothing inferred.",
      }),
    }),
  });
  h.app.saved();
  assert.equal(await h.app.runLive(), false);
  assert.equal(h.document.querySelectorAll("[data-output-field]").length, 0);
  assert.equal(h.$("output-kind").textContent, "Kein Ergebnis");
  assert.match(h.$("editor-message").textContent, /2048/);
  assert.equal(h.$("input-state").disabled, false);
  assert.equal(h.app.getState().busy, false);
  assert.equal(h.$("show-saved").disabled, false);
});
test("missing second live field is rejected as a whole instead of displaying a first answer", async () => {
  const h = await harness({
    enabled: true,
    requestHandler: async (request) => {
      const r = liveFixture(request);
      delete r.answers.evidence;
      return { ok: true, json: async () => r };
    },
  });
  assert.equal(await h.app.runLive(), false);
  assert.equal(h.document.querySelectorAll("[data-output-field]").length, 0);
  assert.match(h.$("editor-message").textContent, /unvollständig/);
});
test("even programmatic edits during a pending request cannot attach stale output", async () => {
  let resolve;
  const h = await harness({
    enabled: true,
    requestHandler: () => new Promise((r) => (resolve = r)),
  });
  const run = h.app.runLive(),
    request = JSON.parse(
      h.calls.find((c) => c.url === "/api/infer").options.body,
    );
  h.$("input-state").value += " unexpected edit";
  resolve({ ok: true, json: async () => liveFixture(request) });
  assert.equal(await run, false);
  assert.equal(h.document.querySelectorAll("[data-output-field]").length, 0);
  assert.match(h.$("editor-message").textContent, /geändert/);
});
test("invalid schema and duplicate keys never trigger a model request", async () => {
  const h = await harness({ enabled: true });
  h.change("input-schema", '{"a":1,"a":2}', "input");
  assert.equal(await h.app.runLive(), false);
  assert.equal(h.calls.filter((c) => c.url === "/api/infer").length, 0);
  assert.match(h.$("editor-message").textContent, /Doppelter/);
  assert.equal(h.document.querySelectorAll("[data-output-field]").length, 0);
});
test("hash navigation, back/forward, unknown routes and theme persistence work with unavailable storage", async () => {
  const h = await harness({ theme: "dark" });
  assert.equal(h.document.documentElement.dataset.theme, "dark");
  h.click("#theme-toggle");
  assert.equal(h.storage.get("clef-theme"), "light");
  h.window.location.hash = "playground";
  h.window.location.hash = "method";
  assert.equal(h.$("method").hidden, false);
  h.window.history.back();
  assert.equal(h.$("playground").hidden, false);
  h.window.history.forward();
  assert.equal(h.$("method").hidden, false);
  h.window.location.hash = "not-a-route";
  assert.equal(h.$("explorer").hidden, false);
  assert.equal(
    h.document
      .querySelector('[data-nav="explorer"]')
      .getAttribute("aria-current"),
    "page",
  );
  const noStorage = await harness({ storageThrows: true });
  noStorage.click("#theme-toggle");
  assert.equal(noStorage.document.documentElement.dataset.theme, "dark");
});
test("unavailable suite falls back honestly, complete load failure gives a useful error", async () => {
  const h = await harness({ failFiles: ["insurance"] });
  assert.equal(h.app.getState().suite, "general");
  assert.equal(h.$("app-error").hidden, false);
  assert.match(h.$("app-error").textContent, /Versicherungsdokumente/);
  const all = await harness({
    failFiles: ["insurance", "benchmark", "finance", "clean72", "bank-support"],
  });
  assert.equal(all.app.getState().suite, null);
  assert.match(all.$("app-error").textContent, /python server.py/);
});
test("arbitrary document, rationale, schema and result strings remain text, never executable markup", async () => {
  const fixture = completeFixture(),
    attack = '<img src=x onerror="globalThis.pwned=1"><script>pwned=1</script>';
  fixture.cases[0].scenario = attack;
  fixture.cases[0].claim = attack;
  fixture.cases[0].title = attack;
  fixture.cases[0].gold_rationale = attack;
  fixture.cases[0].questions.decision.criteria[
    fixture.cases[0].result.fields.decision.prediction
  ] = attack;
  fixture.documents.find(
    (d) => d.id === fixture.cases[0].document_id,
  ).clauses[0].text = attack;
  const h = await harness({ insurance: fixture });
  assert.match(h.$("document-content").textContent, /<img/);
  assert.match(h.$("case-detail").textContent, /<script/);
  assert.equal(
    h.document.querySelectorAll(
      "#document-content img,#document-content script,#case-detail img,#case-detail script",
    ).length,
    0,
  );
  h.app.saved();
  assert.equal(
    h.document.querySelectorAll(
      "#playground-output img,#playground-output script",
    ).length,
    0,
  );
  assert.match(h.$("playground-output").textContent, /<img/);
});
test("responsive layout declares deliberate phone panes and protects shrinking columns, not a browser rendering pass", async () => {
  const css = await readFile(
    new URL("../web/styles.css", import.meta.url),
    "utf8",
  );
  assert.match(css.replace(/\s+/g, ""), /@media\(max-width:760px\)/);
  assert.match(
    css.replace(/\s+/g, ""),
    /grid-template-columns:250pxminmax\(320px,1fr\)335px/,
  );
  assert.match(css.replace(/\s+/g, ""), /max-width:1080px.*min-width:761px/);
  for (const pane of ["cases", "document", "result"])
    assert.ok(
      css.includes(`[data-mobile-pane="${pane}"]`) ||
        css.includes(`[data-mobile-pane=${pane}]`),
    );
  assert.match(css.replace(/\s+/g, ""), /prefers-reduced-motion:reduce/);
  assert.match(css.replace(/\s+/g, ""), /min-width:0/);
  assert.match(css.replace(/\s+/g, ""), /overflow-wrap:anywhere/);
  const h = await harness();
  for (const pane of ["cases", "document", "result"]) {
    h.click(`[data-pane="${pane}"]`);
    assert.equal(h.$("workbench-shell").dataset.mobilePane, pane);
    assert.equal(
      h.document
        .querySelector(`[data-pane="${pane}"]`)
        .getAttribute("aria-pressed"),
      "true",
    );
  }
  assert.ok(
    [...h.document.querySelectorAll("textarea,input,select")].every(
      (el) => el.id,
    ),
  );
  assert.equal(h.document.querySelectorAll('input[type="file"]').length, 2);
});
test("data-derived statistics distinguish fields, exact case and pending without pooling suites", () => {
  const fixture = completeFixture(),
    s = suiteStats(fixture);
  assert.equal(s.total, 60);
  assert.equal(s.fields.decision.correct, 60);
  assert.equal(s.fields.evidence.correct, 59);
  assert.equal(s.exact, 59);
  assert.equal(outcome(fixture.cases[0]), "partial");
  assert.equal(filterCases(fixture.cases, { outcome: "decision" }).length, 0);
  assert.equal(filterCases(fixture.cases, { outcome: "evidence" }).length, 1);
  assert.equal(fieldsForCase(fixture.cases[0]).length, 2);
  assert.deepEqual(
    evidenceIDs(fixture.cases[0], "model"),
    fixture.cases[0].result.actual_evidence_clauses,
  );
});
test("strict parser, multi-field limits and canonical replay comparison reject ambiguous/oversized data", () => {
  assert.deepEqual(parseJSONStrict('{"a":[{"b":"escaped \\" quote"}]}'), {
    a: [{ b: 'escaped " quote' }],
  });
  assert.throws(() => parseJSONStrict('{"a":1,"\\u0061":2}'), /Doppelter/);
  assert.throws(() => parseJSONStrict('{"a":{"b":1,"b":2}}'), /Doppelter/);
  const c = datasets.insurance.cases[0];
  assert.equal(
    Object.keys(validatePlayground(c.input, c.questions).questions).length,
    2,
  );
  const q = c.questions.decision;
  assert.throws(() =>
    validatePlayground(
      "x",
      Object.fromEntries(Array.from({ length: 9 }, (_, i) => ["q" + i, q])),
    ),
  );
  assert.throws(() => validatePlayground("x".repeat(6001), { a: q }));
  assert.notEqual(
    requestFingerprint({ state: "x", questions: { b: q, a: q } }),
    requestFingerprint({ state: "x", questions: { a: q, b: q } }),
  );
  assert.notEqual(
    requestFingerprint({ state: "x", questions: { a: q } }),
    requestFingerprint({ state: "x ", questions: { a: q } }),
  );
});
test("live response gates reject extra fields, nonfinite/unnormalized probabilities and unverified source", () => {
  const c = datasets.insurance.cases[0],
    request = { state: c.input, questions: c.questions },
    good = liveFixture(request);
  assert.equal(validateLiveResult(good, request), good);
  for (const change of [
    (r) => (r.source = "stored"),
    (r) => (r.truncated = true),
    (r) => delete r.probabilities_unrounded.evidence,
    (r) => (r.answers.extra = { type: "choice", choice: "x" }),
    (r) =>
      (r.probabilities_unrounded.decision[
        Object.keys(r.probabilities_unrounded.decision)[0]
      ] = Infinity),
    (r) => (r.input_tokens = 2049),
    (r) => (r.latency_ms = -1),
    (r) => (r.answers.decision.choice = "unknown"),
  ]) {
    const bad = structuredClone(good);
    change(bad);
    assert.throws(() => validateLiveResult(bad, request));
  }
});

test("failed verification, partial fields and wrong planned counts cannot enter stored replay", async () => {
  const original = completeFixture();
  for (const mutate of [
    (d) => (d.verification.status = "fail"),
    (d) => delete d.cases[0].result.fields.evidence,
    (d) => delete d.cases[0].result.fields.decision.schema_valid,
    (d) => (d.cases[0].result.fields.decision.prediction = "invented"),
    (d) => (d.cases[0].result.fields.evidence.probabilities = { invented: 1 }),
    (d) => d.cases.pop(),
    (d) => (d.cases[0].result.actual_evidence_clauses = ["invented"]),
  ]) {
    const bad = structuredClone(original);
    mutate(bad);
    assert.throws(() => validateDataset(bad, "insurance"));
    const h = await harness({ insurance: bad });
    assert.equal(h.app.getState().suite, "general");
    assert.equal(
      h.$("suite-select").querySelector('[value="insurance"]').disabled,
      true,
    );
    assert.match(h.$("app-error").textContent, /Versicherungsdokumente/);
  }
});

test("paired aggregate strings are escaped and cannot create markup", async () => {
  const general = structuredClone(datasets.benchmark),
    pairs = Object.values(general.scores.paired_all_planned);
  pairs[0].counts.both_correct = '<img id="xss-proof" src=x onerror="evil()">';
  const h = await harness({
    hash: "#overview?suite=general",
    overrides: { benchmark: general },
  });
  assert.equal(h.document.querySelector("#xss-proof"), null);
  assert.match(h.$("paired-comparisons").textContent, /<img/);
});

test("deep links into a control split preserve the intended case and field in the URL", async () => {
  const target = datasets.benchmark.cases.find(
    (c) => c.split === "english_control",
  );
  const h = await harness({
    hash: `#explorer?suite=general&case=${target.id}&field=decision`,
  });
  assert.equal(h.app.getState().selected, target.id);
  assert.equal(h.$("filter-split").value, "english_control");
  assert.equal(h.document.querySelectorAll(".case-item").length, 30);
  assert.ok(h.window.location.hash.includes(target.id));
  h.app.selectSuite("insurance");
  h.window.location.hash = `#explorer?suite=general&case=${target.id}&field=decision`;
  assert.equal(h.app.getState().selected, target.id);
  const i = await harness({
    hash: "#explorer?suite=insurance&case=fall_031&field=evidence",
  });
  assert.ok(i.window.location.hash.includes("field=evidence"));
});

test("replaced controls explicitly restore focus targets and phone pane switches stay meaningful", async () => {
  const h = await harness();
  h.click('[data-case="fall_002"]');
  assert.equal(
    h.document.__focused,
    h.$("document-header").querySelector("h2"),
  );
  assert.equal(h.document.__focused.getAttribute("tabindex"), "-1");
  h.click('[data-direction="1"]');
  assert.equal(h.document.__focused.dataset.direction, "1");
  h.change("highlight-select", "none");
  assert.equal(h.document.__focused, h.$("highlight-select"));
  h.click('[data-field="evidence"]');
  assert.equal(h.document.__focused.dataset.field, "evidence");
});

test("informative light/dark text tokens meet 4.5:1 contrast against their intended surfaces", async () => {
  const css = await readFile(
    new URL("../web/styles.css", import.meta.url),
    "utf8",
  );
  const light = css.slice(
      css.indexOf(":root {"),
      css.indexOf(":root[data-theme"),
    ),
    dark = css.slice(css.indexOf(":root[data-theme"), css.indexOf("* {"));
  const token = (part, name) =>
    part.match(new RegExp("--" + name + ":\\s*(#[0-9a-f]{3,6})"))[1];
  const luminance = (hex) => {
    if (hex.length === 4)
      hex = "#" + [...hex.slice(1)].map((c) => c + c).join("");
    const values = [1, 3, 5]
      .map((i) => parseInt(hex.slice(i, i + 2), 16) / 255)
      .map((v) => (v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4));
    return values.reduce((s, v, i) => s + v * [0.2126, 0.7152, 0.0722][i], 0);
  };
  for (const part of [light, dark])
    for (const [fg, bg] of [
      ["muted", "surface"],
      ["faint", "surface"],
      ["faint", "surface-soft"],
      ["faint", "page"],
      ["gold", "gold-soft"],
      ["accent-ink", "accent-soft"],
      ["red", "red-soft"],
    ]) {
      const values = [
        luminance(token(part, fg)),
        luminance(token(part, bg)),
      ].sort((a, b) => a - b);
      assert.ok((values[1] + 0.05) / (values[0] + 0.05) >= 4.5, `${fg}/${bg}`);
    }
});

test("insurance cannot lose a question/document link or exceed the frozen token limit", () => {
  const valid = completeFixture();
  for (const mutate of [
    (d) => {
      delete d.cases[0].document_id;
      delete d.cases[0].questions.evidence;
      delete d.cases[0].result.fields.evidence;
      d.cases[0].result.correct = true;
    },
    (d) => d.documents.pop(),
    (d) => (d.cases[0].input_tokens = 2049),
  ]) {
    const value = structuredClone(valid);
    mutate(value);
    assert.throws(() => validateDataset(value, "insurance"));
  }
});

test("reordering native fields invalidates stored replay because vendor encoder preserves field order", async () => {
  const h = await harness({ insurance: completeFixture() });
  h.app.saved();
  const original = JSON.parse(h.$("input-schema").value);
  h.change(
    "input-schema",
    JSON.stringify({
      evidence: original.evidence,
      decision: original.decision,
    }),
    "input",
  );
  assert.equal(h.$("show-saved").disabled, true);
  assert.equal(h.app.saved(), false);
  assert.equal(h.document.querySelectorAll("[data-output-field]").length, 0);
});

test("archived genuine HTTP smoke satisfies the frontend all-field contract without re-running inference", async () => {
  const proof = JSON.parse(
    await readFile(
      new URL("../qa/live_multifield_smoke.json", import.meta.url),
    ),
  );
  assert.equal(proof.status, "pass");
  assert.equal(proof.benchmark_inclusion, false);
  assert.equal(Object.values(proof.assertions).every(Boolean), true);
  assert.equal(
    validateLiveResult(proof.response, proof.request),
    proof.response,
  );
  assert.deepEqual(Object.keys(proof.response.answers), [
    "decision",
    "evidence",
  ]);
  assert.equal(proof.response.input_tokens, 442);
  assert.equal(proof.response.runtime.backend, "cpu");
});

test("final insurance data shows decision/evidence/whole-case truth separately with the recorded mismatch counts", async () => {
  const data = datasets.insurance;
  assert.equal(data.status, "completed");
  assert.equal(data.verification.status, "verified");
  const s = suiteStats(data);
  assert.equal(s.fields.decision.correct, 51);
  assert.equal(s.fields.evidence.correct, 58);
  assert.equal(s.exact, 50);
  assert.equal(s.total, 60);
  const h = await harness();
  assert.deepEqual(
    [...h.document.querySelectorAll(".stat-value")].map((el) =>
      el.textContent.replaceAll("\u00a0", " "),
    ),
    ["85 %", "96,7 %", "83,3 %", "100 %"],
  );
  const mismatch = [...h.document.querySelectorAll(".diagnosis-item")].find(
    (el) => el.textContent.includes("Evidenz richtig, Entscheidung falsch"),
  );
  assert.equal(mismatch.querySelector("strong").textContent, "8");
  assert.equal(h.document.querySelectorAll("#case-detail .prob-row").length, 4);
  h.click('[data-field="evidence"]');
  assert.equal(h.document.querySelectorAll("#case-detail .prob-row").length, 5);
  h.app.saved();
  assert.equal(h.document.querySelectorAll("[data-output-field]").length, 2);
});

test('skip link focuses the active workspace without changing the current route',async()=>{
 const h=await harness({hash:'#method'});h.click('.skip');assert.equal(h.window.location.hash,'#method');assert.equal(h.$('method').hidden,false);assert.equal(h.document.__focused,h.$('main'));
});

test("bank suite shows three field metrics and message/policy, without insurance terminology", async () => {
  const data = bankFixture();
  const h = await harness({ hash: "#explorer?suite=bank-support", overrides: { "bank-support": data } });
  assert.equal(h.app.getState().suite, "bank-support");
  assert.equal(h.document.querySelectorAll(".case-item").length, 80);
  assert.equal(h.document.querySelectorAll("[data-field]").length, 3);
  assert.equal(h.document.querySelectorAll("#document-content .document-section").length, 2);
  assert.match(h.$("document-content").textContent, /Kundennachricht/);
  assert.match(h.$("document-content").textContent, /fiktive Servicerichtlinie/);
  assert.doesNotMatch(h.$("document-content").textContent, /VERSICHERUNGSUNTERLAGEN/);
  assert.match(h.$("method-measures").textContent,/Anliegen, Priorität und nächster Schritt/);
  assert.doesNotMatch(h.$("method-synthetic").textContent,/Versicherungsalltag/);
  assert.match(h.$("method-synthetic").textContent,/kein BANKING77/);
  assert.equal(h.document.querySelectorAll("[data-evidence]").length, 0);
  assert.deepEqual([...h.document.querySelectorAll(".stat-label")].map(el => el.textContent),
    ["Anliegen", "Priorität", "Nächster Schritt", "Vollständig richtig"]);
  assert.deepEqual([...h.document.querySelectorAll(".stat-value")].map(el => el.textContent.replaceAll("\u00a0", " ")),
    ["100 %", "98,8 %", "100 %", "98,8 %"]);
  h.change("filter-outcome", "priority");
  assert.equal(h.document.querySelectorAll(".case-item").length, 1);
  h.change("filter-outcome", "intent");
  assert.equal(h.document.querySelectorAll(".case-item").length, 0);
  h.change("filter-outcome", "next_step");
  assert.equal(h.document.querySelectorAll(".case-item").length, 0);
});

test("bank pending data cannot pretend to be results and all three fields stay visible", async () => {
  const data = bankFixture({completed: false});
  const h = await harness({hash: "#explorer?suite=bank-support", overrides: {"bank-support":data}});
  assert.equal(h.document.querySelectorAll("[data-field]").length, 3);
  assert.ok([...h.document.querySelectorAll(".stat-value")].every(el => el.textContent === "—"));
  assert.equal(h.document.querySelectorAll("#case-detail .prob-row").length, 0);
  assert.equal(h.$("show-saved").disabled, true);
  assert.match(h.$("result-banner").textContent, /ausstehend/);
});

test("bank data admission rejects partial fields, reordered input, false truth and policy loss", () => {
  const base = bankFixture();
  assert.equal(validateDataset(base, "bank-support"), base);
  for (const mutate of [
    d => delete d.cases[0].questions.next_step,
    d => delete d.cases[0].result.fields.next_step,
    d => delete d.cases[0].service_policy,
    d => d.cases[0].message = "different from native state",
    d => d.cases[0].synthetic = false,
    d => d.cases[0].manipulation = true,
    d => d.cases[0].result.fields.priority.correct = true,
    d => d.cases[0].questions = {priority:d.cases[0].questions.priority,intent:d.cases[0].questions.intent,next_step:d.cases[0].questions.next_step},
    d => d.cases[0].expected = {decision: "first"},
    d => d.cases.pop(),
  ]) {
    const value = structuredClone(base); mutate(value);
    assert.throws(() => validateDataset(value, "bank-support"));
  }
});

test("bank replay uses all three fields and edits to message, policy or question order invalidate it", async () => {
  const h = await harness({hash:"#explorer?suite=bank-support",overrides:{"bank-support":bankFixture()}});
  assert.equal(h.app.saved(), true);
  assert.equal(h.document.querySelectorAll("[data-output-field]").length, 3);
  const input = h.$("input-state").value, schema = JSON.parse(h.$("input-schema").value);
  h.change("input-state", input + " changed message", "input");
  assert.equal(h.app.saved(), false);
  assert.equal(h.document.querySelectorAll("[data-output-field]").length, 0);
  h.change("input-state", input, "input");
  h.change("input-schema", JSON.stringify({priority:schema.priority,intent:schema.intent,next_step:schema.next_step}), "input");
  assert.equal(h.app.saved(), false);
  h.change("input-schema", JSON.stringify(schema), "input");
  assert.equal(h.app.saved(), true);
  const changedPolicy = structuredClone(schema);
  changedPolicy.priority.instructions += " Changed policy.";
  h.change("input-schema", JSON.stringify(changedPolicy), "input");
  assert.equal(h.app.saved(), false);
  assert.equal(h.document.querySelectorAll("[data-output-field]").length, 0);
});

test("bank pending live request retains its three-field snapshot through navigation and rejects missing third response", async () => {
  let resolve;
  const h = await harness({hash:"#explorer?suite=bank-support",enabled:true,
    overrides:{"bank-support":bankFixture()},requestHandler:()=>new Promise(r=>resolve=r)});
  const initial = h.$("input-state").value, run = h.app.runLive();
  assert.equal(h.app.selectSuite("insurance"), false);
  h.app.selectCase("bank_fixture_2");
  h.window.location.hash = "#method";
  h.window.location.hash = "#playground";
  h.window.history.back(); h.window.history.forward();
  assert.equal(h.$("input-state").value, initial);
  assert.equal(await h.app.runLive(), false);
  const request = JSON.parse(h.calls.find(c=>c.url==="/api/infer").options.body);
  assert.deepEqual(Object.keys(request.questions), ["intent","priority","next_step"]);
  const response = liveFixture(request); delete response.answers.next_step;
  resolve({ok:true,json:async()=>response});
  assert.equal(await run, false);
  assert.equal(h.document.querySelectorAll("[data-output-field]").length, 0);
  assert.equal(h.app.getState().busy, false);
  assert.match(h.$("editor-message").textContent, /unvollständig/);
});

test("bank priority undertriage is derived from case labels and includes critical-to-urgent misses", () => {
  const rows = [["critical","urgent"],["critical","routine"],["urgent","routine"],["routine","critical"],["routine","routine"]].map(([gold,prediction]) => ({
    expected:{priority:gold},questions:{priority:{type:"choice",criteria:{critical:"Critical",urgent:"Urgent",routine:"Routine"}}},
    result:{fields:{priority:{prediction,correct:prediction===gold,schema_valid:true,probabilities:{}}}},
  }));
  assert.deepEqual(bankPriorityCounts(rows), {gold_non_escalation:0,unnecessary_escalations:0,critical_handoff_misses:2,unnecessary_critical:1,critical_all_fields_correct:0,gold_routine:2,excess_security_handoffs:0,gold_critical:2,missed_critical:2,gold_urgent:1,missed_urgent:1,undertriage:3,overtriage:1});
  delete rows[0].result;
  assert.equal(bankPriorityCounts(rows),null);
});

test("field labels do not inherit Object prototype properties", () => {
  assert.equal(fieldLabel("constructor"),"constructor");
  assert.equal(fieldLabel("toString"),"toString");
  assert.equal(fieldLabel("next_step"),"Nächster Schritt");
});

test("stored and live choices must match the maximum unrounded probability", () => {
  const data = bankFixture();
  data.cases[0].result.fields.intent.probabilities = Object.fromEntries(Object.keys(data.cases[0].questions.intent.criteria).map(key=>[key,key==="transfers"?1:0]));
  assert.throws(()=>validateDataset(data,"bank-support"));
  const request = {state:"Test-only",questions:{intent:{type:"choice",instructions:"Test-only",criteria:{first:"First",second:"Second"}}}};
  const response = liveFixture(request);
  response.probabilities_unrounded.intent = {first:0.01,second:0.99};
  assert.throws(()=>validateLiveResult(response,request));
});

test("prototype-property suite routes fall back safely without corrupting navigation", async () => {
  for (const invalid of ["constructor","toString","__proto__"]) {
    const h = await harness({hash:`#explorer?suite=${invalid}`});
    assert.equal(h.app.getState().suite,"insurance");
    h.window.location.hash=`#explorer?suite=${invalid}`;
    assert.equal(h.app.getState().suite,"insurance");
    assert.equal(h.app.selectSuite(invalid),false);
    assert.equal(h.document.querySelectorAll("[data-field]").length,2);
  }
});

test("bank-specific message and supplied policy remain inert text and urgency ignores supplied summary counters", async () => {
  const bank = bankFixture();
  const literal = '<img src=x onerror="throw new Error(1)">';
  bank.cases[0].message = literal;
  bank.cases[0].input = `Synthetische Kundennachricht:\n${literal}`;
  bank.cases[0].questions.intent.instructions = literal;
  bank.cases[0].service_policy = bankServicePolicy(bank.cases[0].questions);
  bank.summary.urgent_routing = {missed_urgent:999,false_urgent:-20,gold_urgent:1,gold_non_urgent:0};
  const h = await harness({hash:"#explorer?suite=bank-support",overrides:{"bank-support":bank}});
  assert.equal(h.document.querySelectorAll("#document-content img").length,0);
  assert.ok(h.$("document-content").textContent.includes(literal));
  assert.doesNotMatch(h.$("diagnosis-content").textContent,/999|-20/);
  assert.match(h.$("diagnosis-content").textContent,/1 \/ 10/);
  assert.match(h.$("diagnosis-content").textContent,/64 \/ 80/);
});

test("final bank results keep field, exact-case and critical-case truths separate", async () => {
  const data = datasets["bank-support"];
  assert.equal(validateDataset(data,"bank-support"),data);
  const stats = suiteStats(data), risk = bankPriorityCounts(data.cases);
  assert.equal(stats.total,80);assert.equal(stats.exact,68);
  assert.deepEqual(Object.values(stats.fields).map(v=>v.correct),[76,77,75]);
  assert.equal(risk.missed_critical,0);assert.equal(risk.critical_handoff_misses,0);
  assert.equal(risk.missed_urgent,0);assert.equal(risk.critical_all_fields_correct,8);
  assert.equal(risk.excess_security_handoffs,1);assert.equal(risk.unnecessary_escalations,3);
  assert.equal(risk.gold_non_escalation,45);assert.equal(risk.gold_routine,64);
  const h=await harness({hash:"#explorer?suite=bank-support"});
  assert.equal(h.$("app-error").hidden,true);
  assert.deepEqual([...h.document.querySelectorAll(".stat-value")].map(el=>el.textContent.replaceAll("\u00a0"," ")),
    ["95 %","96,3 %","93,8 %","85 %"]);
  assert.match(h.$("diagnosis-content").textContent,/8 \/ 10/);
  for(const [field,n] of [["intent",4],["priority",3],["next_step",5],["errors",12]]){
    h.change("filter-outcome",field);assert.equal(h.document.querySelectorAll(".case-item").length,n);
  }
  h.click("#reset-filters");h.app.saved();
  assert.equal(h.document.querySelectorAll("[data-output-field]").length,3);
  for(const field of ["intent","priority","next_step"]){
    h.click(`[data-field="${field}"]`);
    assert.equal(h.document.querySelectorAll("#case-detail .prob-row").length,Object.keys(data.cases[0].questions[field].criteria).length);
  }
});

test("suite catalog offers separate denominators, selects honestly and never sums scores", async () => {
  const h = await harness();
  assert.equal(h.document.querySelectorAll('[data-suite]').length, 5);
  const bank = h.document.querySelector('[data-suite="bank-support"]');
  assert.match(bank.textContent, /80 deutsche Hauptfälle/);
  assert.match(bank.textContent, /Gespeicherter Lauf/);
  h.$('suite-catalog').open = true;
  h.click('[data-suite="bank-support"]');
  assert.equal(h.app.getState().suite, 'bank-support');
  assert.equal(h.$('suite-catalog').open, false);
  assert.equal(h.document.querySelector('[data-suite="bank-support"]').getAttribute('aria-pressed'), 'true');
  assert.equal(h.$('suite-select').value, 'bank-support');
  h.window.location.hash = 'custom';
  assert.equal(h.$('suite-catalog').hidden, true);
  assert.equal(h.document.title, 'Clef Lab · Eigene Tests');
});

test("readiness distinguishes server, explicit enablement and a loaded model without inferring readiness", async () => {
  const value = { inference_enabled: false, model_loaded: false, busy: false };
  const h = await harness({ healthHandler: async () => ({ ok: true, json: async () => ({ ...value }) }) });
  const statuses = () => [...h.document.querySelectorAll('[data-readiness]')].map(el => el.dataset.status);
  assert.deepEqual(statuses(), ['ready', 'pending', 'pending']);
  assert.equal(h.$('run-live').disabled, true);
  value.inference_enabled = true;
  await h.app.checkBackend();
  assert.deepEqual(statuses(), ['ready', 'ready', 'pending']);
  assert.match(h.$('backend-summary').textContent, /noch ungeladen/);
  assert.equal(h.$('run-live').disabled, false);
  value.model_loaded = true;
  await h.app.checkBackend();
  assert.deepEqual(statuses(), ['ready', 'ready', 'ready']);
  assert.match(h.$('backend-summary').textContent, /Modell geladen/);
  assert.equal(h.calls.filter(c => c.url === '/api/infer').length, 0);
});

test("malformed health booleans fail closed for playground and readiness UI", async () => {
  for (const mutation of [{inference_enabled:'false'}, {model_loaded:'true'}, {busy:0}]) {
    const h = await harness({healthHandler: async () => ({ok:true,json:async () => ({inference_enabled:true,model_loaded:false,busy:false,...mutation})})});
    assert.equal(h.$('run-live').disabled, true);
    assert.match(h.$('backend-summary').textContent, /Server nicht erreichbar/);
    assert.equal(await h.app.runLive(), false);
    assert.equal(h.calls.filter(c => c.url === '/api/infer').length, 0);
  }
});

test("newer health refresh wins if an older check finishes last", async () => {
  let call = 0, resolve;
  const deferred = new Promise(r => resolve = r);
  const h = await harness({healthHandler: async () => ++call === 2 ? deferred : ({ok:true,json:async()=>({inference_enabled:false,model_loaded:false,busy:false})})});
  const old = h.app.checkBackend();
  await h.app.checkBackend();
  resolve({ok:true,json:async()=>({inference_enabled:true,model_loaded:true,busy:false})});
  await old;
  assert.equal(h.app.getState().health.inference_enabled, false);
  assert.equal(h.$('refresh-backend').disabled, false);
  assert.equal(h.$('run-live').disabled, true);
});

test("failed benchmark loading does not block independent backend readiness or custom import", async () => {
  const h = await harness({ failFiles: ['insurance', 'benchmark', 'finance', 'clean72', 'bank-support'] });
  assert.equal(h.$('app-error').hidden, false);
  assert.match(h.$('backend-summary').textContent, /Ergebnismodus/);
  assert.equal(h.document.querySelectorAll('[data-suite]:disabled').length, 5);
  assert.equal(h.$('custom-example').disabled, false);
});

test('readiness immediately reflects a running single request and blocks a known busy backend', async () => {
  let release;
  const deferred=new Promise(resolve=>release=resolve), h=await harness({enabled:true,requestHandler:()=>deferred});
  const run=h.app.runLive();
  assert.match(h.$('backend-summary').textContent,/Berechnung läuft/);
  assert.match(h.$('backend-state').textContent,/Berechnung läuft/);
  const request=JSON.parse(h.calls.find(c=>c.url==='/api/infer').options.body);
  release({ok:true,json:async()=>liveFixture(request)});await run;
  const occupied=await harness({healthHandler:async()=>({ok:true,json:async()=>({inference_enabled:true,model_loaded:true,busy:true})})});
  assert.equal(occupied.$('run-live').disabled,true);
  assert.equal(await occupied.app.runLive(),false);
  assert.equal(occupied.calls.filter(c=>c.url==='/api/infer').length,0);
});


test('private import selects keep native labels/options and explicit shrinkable grid sizing', async () => {
  const h = await harness({hash:'#custom'});
  const css = await readFile(new URL('../web/styles.css', import.meta.url), 'utf8');
  assert.match(css, /\.custom-upload-grid label\s*\{[^}]*grid-template-columns:\s*minmax\(0,\s*1fr\)/);
  assert.match(css, /\.custom-upload-grid select\s*\{[^}]*width:\s*100%;[^}]*min-width:\s*0/);
  assert.equal(h.$('custom-format').tagName, 'SELECT');
  assert.match(h.$('custom-format').closest('label').textContent, /Dateiformat/);
  assert.match(h.$('custom-format').querySelector('[value="csv"]').textContent, /Textspalten.*Fragenschema/);
  h.change('custom-format','csv');
  assert.equal(h.$('custom-import-fields').hidden,false);
  assert.equal(h.$('custom-preset').tagName,'SELECT');
  assert.match(h.$('custom-preset').closest('label').textContent,/CSV-Fragenschema/);
});
