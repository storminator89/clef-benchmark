/** Offline consistency and DOM tests. No model or network requests. */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { parseHTML } from 'linkedom';
import { FIXED_THRESHOLDS, BIN_EDGES, observationMetrics, summarizeField, validateReliability, selectReliabilityGroup } from '../web/reliability-core.js';
import { createReliabilityView } from '../web/reliability-ui.js';
const archived = JSON.parse(await readFile(new URL('../web/data/reliability.json', import.meta.url), 'utf8'));
const tick = () => new Promise(resolve => setImmediate(resolve));
function fixture(specs = [{ id: 'a', confidence: 0.95, correct: true }, { id: 'b', confidence: 0.9, correct: false }]) {
  const rows = specs.map(({ id, confidence = 0.8, correct = true, status = 'valid' }) => {
    const row = { suite_id: 'fixture', id, group_id: 'fixture-group', field: 'decision', partition: {}, option_keys: ['no', 'yes'], status, issues: status === 'valid' ? [] : ['fixture'], gold: 'yes', choice: correct ? 'yes' : 'no', probabilities: { no: correct ? 1 - confidence : confidence, yes: correct ? confidence : 1 - confidence } };
    return status === 'valid' ? { ...row, ...observationMetrics(row) } : row;
  });
  return { schema_version: 1, status: 'completed', analysis_type: 'post-hoc descriptive', thresholds: [...FIXED_THRESHOLDS], bin_edges: [...BIN_EDGES], definitions: {}, caveats: ['Test fixture only'],
    suites: [{ id: 'fixture', title: 'Synthetic test fixture', expected_count: specs.length, valid_field_count: rows.filter(r => r.status === 'valid').length, invalid_field_count: rows.filter(r => r.status === 'invalid').length, missing_field_count: rows.filter(r => r.status === 'missing').length, field_group_ids: ['fixture-group'] }],
    field_groups: [{ group_id: 'fixture-group', suite_id: 'fixture', field: 'decision', partition: {}, option_keys: ['no', 'yes'], ...summarizeField(rows) }], observations: rows,
    cases: rows.map(row => ({ suite_id: 'fixture', id: row.id, input: 'Test-only input', questions: { decision: { type: 'choice', criteria: { no: 'No', yes: 'Yes' } } }, expected: { decision: 'yes' }, metadata: {} })) };
}
function harness({ payload = archived, fetcher } = {}) {
  const { document, window: dom } = parseHTML('<html><body><section id="reliability"></section><select id="primitive"></select></body></html>');
  const prototype = Object.getPrototypeOf(document.querySelector('select'));
  if (!Object.getOwnPropertyDescriptor(prototype, 'value')?.set) Object.defineProperty(prototype, 'value', {
    configurable: true,
    get() { return [...this.querySelectorAll('option')].find(o => o.hasAttribute('selected'))?.getAttribute('value') ?? this.querySelector('option')?.getAttribute('value') ?? ''; },
    set(value) { for (const o of this.querySelectorAll('option')) o.toggleAttribute('selected', o.getAttribute('value') === String(value)); },
  });
  const listeners = new Map(), calls = [];
  const window = { location: { hash: '#reliability' }, history: { replaceState(_state, _title, url) { window.location.hash = url; } }, addEventListener(name, fn) { listeners.set(name, [...(listeners.get(name) || []), fn]); } };
  const view = createReliabilityView({ document, window, fetch: async (...args) => { calls.push(args); return fetcher ? fetcher(...args) : { ok: true, json: async () => payload }; } });
  const $ = id => document.getElementById(id);
  return { view, document, window, calls, $, text: () => $('reliability').textContent,
    change(id, value) { const el = $(id); if (el.type === 'checkbox') el.checked = value; else el.value = value; el.dispatchEvent(new dom.Event('change', { bubbles: true })); },
    click(selector) { document.querySelector(selector).dispatchEvent(new dom.Event('click', { bubbles: true })); },
    leave() { window.location.hash = '#pairs'; for (const fn of listeners.get('hashchange') || []) fn(); },
  };
}

test('all archived summaries independently match all 1,186 observations without pooling', () => {
  const data = validateReliability(archived);
  assert.equal(data.field_groups.length, 78); assert.equal(data.suites.length, 9); assert.equal(data.observations.length, 1186);
  const determination = data.field_groups.find(g => g.suite_id === 'minimal_pairs48' && g.field === 'determination');
  const action = data.field_groups.find(g => g.suite_id === 'minimal_pairs48' && g.field === 'action');
  const d = determination.risk_coverage.find(r => r.threshold === 0.9), a = action.risk_coverage.find(r => r.threshold === 0.9);
  assert.deepEqual([d.incorrect, d.selected_count, d.expected_count, d.risk, d.coverage], [4, 36, 48, 4 / 36, 36 / 48]);
  assert.deepEqual([a.incorrect, a.selected_count, a.expected_count, a.risk], [2, 7, 48, 2 / 7]);
  const errors = action.observations.filter(r => !r.correct && r.confidence >= 0.9);
  assert.equal(new Set(errors.map(r => data.caseMap.get(JSON.stringify([r.suite_id, r.id])).metadata.pair_id)).size, 1);
  assert.equal(determination.bins.reduce((n, b) => n + b.count, 0), 48);
});

test('risk denominator differs from expected coverage with invalid or missing rows', () => {
  const p = fixture([{ id: 'a', confidence: 0.95, correct: false }, { id: 'b', confidence: 0.8 }, { id: 'c', status: 'missing' }, { id: 'd', status: 'invalid' }]);
  const g = validateReliability(p).field_groups[0], r = g.risk_coverage.find(r => r.threshold === 0.9);
  assert.deepEqual([r.expected_count, r.valid_count, r.selected_count, r.incorrect, r.coverage, r.valid_coverage, r.risk], [4, 2, 1, 1, 0.25, 0.5, 1]);
  assert.equal(g.invalid_count, 1); assert.equal(g.missing_count, 1);
});

test('empty selection and empty bins remain undefined; boundary .9 and exact 1 are included correctly', () => {
  const g = validateReliability(fixture([{ id: 'a', confidence: 0.9 }])).field_groups[0];
  assert.equal(g.bins[8].count, 0); assert.equal(g.bins[9].count, 1);
  assert.equal(g.bins[0].mean_score, null); assert.equal(g.bins[0].accuracy, null);
  assert.equal(g.risk_coverage.at(-1).risk, null); assert.equal(g.risk_coverage.at(-1).coverage, 0);
  const one = validateReliability(fixture([{ id: 'a', confidence: 1, correct: false }])).field_groups[0];
  assert.equal(one.bins[9].count, 1); assert.equal(one.nll_is_infinite, true); assert.equal(one.nll_mean, null); assert.equal(one.zero_gold_probability_count, 1); assert.equal(one.brier_mean, 2);
});

test('reject tampered derived scores, risk, bins, denominators, counts and error IDs', () => {
  const changes = [
    p => { p.field_groups[0].risk_coverage[3].risk = 0; },
    p => { p.field_groups[0].risk_coverage[3].selected_count++; },
    p => { p.field_groups[0].bins[9].count++; },
    p => { p.field_groups[0].brier_mean = 0; },
    p => { p.field_groups[0].expected_count++; },
    p => { p.field_groups[0].high_score_error_ids['0.90'] = []; },
    p => { p.observations[1].correct = true; },
    p => { p.observations[0].confidence = 0.9; },
    p => { p.suites[0].valid_field_count++; },
  ];
  for (const mutate of changes) { const p = fixture(); mutate(p); assert.throws(() => validateReliability(p), /Ungültige/); }
});

test('reject invalid vectors, duplicate or missing field observations, wrong group/gold/options, and tuned thresholds', () => {
  const changes = [
    p => { p.observations[0].probabilities.yes = Infinity; },
    p => { p.observations[0].probabilities.yes = true; },
    p => { p.observations[0].probabilities.yes = 0.1; },
    p => { p.observations.push(p.observations[0]); },
    p => { p.observations.pop(); },
    p => { p.observations[0].partition = { language: 'en' }; },
    p => { p.cases[0].expected.decision = 'no'; },
    p => { p.cases[0].questions.decision.criteria.maybe = 'Maybe'; },
    p => { p.field_groups[0].option_keys.push('yes'); },
    p => { p.thresholds[3] = 0.91; },
    p => { p.suites.push(p.suites[0]); },
    p => { p.cases.push(p.cases[0]); },
    p => { p.observations[0].choice = 'no'; },
    p => { p.observations[0].status = 'unknown'; },
  ];
  for (const mutate of changes) { const p = fixture(); mutate(p); assert.throws(() => validateReliability(p), /Ungültige/); }
});

test('route defaults, invalid fallback, direct group and supported thresholds never pool fields', () => {
  const data = validateReliability(archived);
  const s = selectReliabilityGroup(data, new URLSearchParams('suite=unknown&field=anything&threshold=0.91'));
  assert.equal(s.suite, 'minimal_pairs48'); assert.equal(s.field, 'determination'); assert.equal(s.threshold, 0.9);
  const image = data.field_groups.find(g => g.suite_id === 'images90' && g.partition.condition === 'blank');
  assert.equal(selectReliabilityGroup(data, { group: image.group_id }).group, image.group_id);
  assert.equal(selectReliabilityGroup(data, { suite: 'images90' }).suite, 'images90');
  assert.ok(data.field_groups.some(g => g.group_id === selectReliabilityGroup(data, { suite: 'bank_support80', field: 'bad', group: image.group_id }).group && g.suite_id === 'bank_support80'));
});

test('view is lazy, defaults to 4/36 determination, and switches field with correct dependent-pair evidence', async () => {
  const h = harness(); assert.equal(h.calls.length, 0);
  assert.equal(await h.view.show(), true); assert.equal(h.calls.length, 1); assert.equal(h.calls[0][0], './data/reliability.json');
  assert.equal(h.$('reliability-field').value, 'determination');
  assert.match(h.document.querySelector('[data-reliability-risk]').textContent, /11,1/);
  assert.match(h.text(), /4 \/ 36/); assert.match(h.text(), /36 \/ 48/); assert.match(h.text(), /3 Paare/);
  assert.equal(h.document.querySelectorAll('[data-reliability-bin]').length, 10);
  assert.equal(h.document.querySelectorAll('[data-reliability-error]').length, 6);
  h.change('reliability-field', 'action');
  assert.match(h.text(), /2 \/ 7/); assert.match(h.text(), /Beide Fehler gehören zum selben Paar/);
  assert.equal(h.document.querySelectorAll('[data-reliability-error]').length, 8);
  h.change('reliability-selected-errors', true);
  assert.equal(h.document.querySelectorAll('[data-reliability-error]').length, 2);
  assert.equal(h.document.querySelectorAll('a[href="#pairs?pair=pair_report_delivery_target"]').length, 2);
  assert.match(h.window.location.hash, /field=action/);
  assert.equal(h.calls.length, 1);
});

test('suite/group switching updates caveats and fixed threshold buttons; no stale field remains', async () => {
  const h = harness(); await h.view.show();
  h.change('reliability-suite', 'images90'); assert.equal(h.$('reliability-suite').value, 'images90'); assert.notEqual(h.$('reliability-field').value, 'determination');
  h.change('reliability-field', 'legend_count');
  const blank = archived.field_groups.find(g => g.suite_id === 'images90' && g.field === 'legend_count' && g.partition.condition === 'blank');
  h.change('reliability-group', blank.group_id);
  assert.match(h.text(), /BLANK-DIAGNOSTIK/); assert.match(h.text(), /bar_line\/vbar2/); assert.match(h.text(), /50 Quellbilder/);
  h.change('reliability-suite', 'insurance60');
  assert.match(h.text(), /falllokale Klauselmengen/); assert.doesNotMatch(h.document.querySelector('.reliability-caveats').textContent, /BLANK-DIAGNOSTIK/);
  h.click('[data-reliability-threshold="0.99"]'); assert.equal(h.$('reliability-threshold').value, '0.99');
  h.change('reliability-suite', 'minimal_pairs48');
  assert.equal(h.$('reliability-field').value, 'determination');
});

test('empty selection does not present zero risk; raw metrics and all empty bins are available', async () => {
  const h = harness({ payload: fixture([{ id: 'a', confidence: 0.8 }]) }); await h.view.show();
  assert.equal(h.document.querySelector('[data-reliability-risk]').textContent, 'nicht definiert');
  assert.match(h.text(), /0\/0 ist nicht definiert/);
  assert.equal(h.document.querySelectorAll('.reliability-empty-bin').length, 9);
  assert.match(h.$('reliability-metrics').textContent, /nicht durch die Optionsanzahl geteilt/);
  for (const id of ['reliability-suite','reliability-field','reliability-group','reliability-threshold','reliability-selected-errors']) assert.ok(h.document.querySelector(`label[for="${id}"]`) || h.$(id).closest('label'));
  assert.equal(h.$('reliability').getAttribute('aria-busy'), 'false');
});

test('untrusted labels, raw inputs, criteria, caveats and failure messages are escaped', async () => {
  const evil = '<img src=x onerror="globalThis.pwned=true"><script>alert(1)</script>';
  const p = fixture(); p.suites[0].title = evil; p.caveats.push(evil); p.cases[1].input = evil; p.cases[1].questions.decision.criteria.no = evil; p.cases[1].metadata.rationale = evil;
  const h = harness({ payload: p }); await h.view.show();
  assert.equal(h.document.querySelectorAll('img,script,[onerror]').length, 0); assert.ok(h.text().includes(evil));
  const bad = harness({ fetcher: async () => { throw new Error(evil); } }); await bad.view.show();
  assert.equal(bad.document.querySelectorAll('img,script,[onerror]').length, 0); assert.ok(bad.text().includes(evil));
});

test('failed fetch and invalid payload show accessible error and retry successfully', async () => {
  let attempt = 0;
  const h = harness({ fetcher: async () => ++attempt === 1 ? { ok: false, status: 503 } : { ok: true, json: async () => fixture() } });
  assert.equal(await h.view.show(), false); assert.match(h.text(), /503/); assert.ok(h.document.querySelector('[role="alert"]'));
  h.click('[data-reliability-retry]'); await tick(); assert.equal(attempt, 2); assert.ok(h.$('reliability-field'));
  const p = fixture(); p.field_groups[0].risk_coverage[3].risk = 0;
  const bad = harness({ payload: p }); assert.equal(await bad.view.show(), false); assert.match(bad.text(), /Ungültige/); assert.equal(bad.document.querySelectorAll('[data-reliability-risk]').length, 0);
});

test('overlapping routes share a fetch; latest route wins and route-away cannot render stale results', async () => {
  let resolve;
  const h = harness({ fetcher: () => new Promise(r => { resolve = r; }) });
  const first = h.view.show({ field: 'determination' }), second = h.view.show({ field: 'action' });
  assert.equal(h.calls.length, 1); assert.equal(h.$('reliability').getAttribute('aria-busy'), 'true');
  resolve({ ok: true, json: async () => archived });
  assert.equal(await first, false); assert.equal(await second, true); assert.equal(h.$('reliability-field').value, 'action');
  let resolveAgain;
  const away = harness({ fetcher: () => new Promise(r => { resolveAgain = r; }) });
  const showing = away.view.show(); away.leave(); const before = away.$('reliability').innerHTML;
  resolveAgain({ ok: true, json: async () => archived });
  assert.equal(await showing, false); assert.equal(away.$('reliability').innerHTML, before);
  assert.equal(await away.view.show({ field: 'action' }), true); assert.equal(away.calls.length, 1);
});
