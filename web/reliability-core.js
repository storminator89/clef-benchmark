/** Offline descriptive analysis. Each suite / field / partition / option set stays separate. */
export const FIXED_THRESHOLDS = Object.freeze([0.5, 0.7, 0.8, 0.9, 0.95, 0.99]);
export const BIN_EDGES = Object.freeze(Array.from({ length: 11 }, (_, i) => i / 10));
const object = o => o !== null && typeof o === 'object' && !Array.isArray(o);
const sameKeys = (a, b) => [...a].sort().join('\u0000') === [...b].sort().join('\u0000');
const countBy = (rows, key) => Object.fromEntries([...new Set(rows.map(r => r[key]))].sort().map(k => [k, rows.filter(r => r[key] === k).length]));
const mean = values => values.length ? values.reduce((a, b) => a + b, 0) / values.length : null;
const fail = detail => { throw new Error(`Ungültige Verlässlichkeitsdaten: ${detail}`); };
function str(value, where, max = 2000) {
  if (typeof value !== 'string' || !value.length || value.length > max || value.includes('\u0000')) fail(where);
  return value;
}
function array(value, where, max = 10000) {
  if (!Array.isArray(value) || value.length > max) fail(where);
  return value;
}
function options(value, where) {
  array(value, where, 1000);
  if (value.length < 2 || new Set(value).size !== value.length) fail(where);
  value.forEach(v => str(v, where));
}
function partition(value, where) {
  if (!object(value) || Object.values(value).some(v => typeof v !== 'string')) fail(where);
}
function sameValue(actual, expected, where) {
  if (typeof expected === 'number') {
    if (typeof actual !== 'number' || !Number.isFinite(actual) || Math.abs(actual - expected) > 2e-10 * Math.max(1, Math.abs(expected))) fail(where);
  } else if (Array.isArray(expected)) {
    if (!Array.isArray(actual) || actual.length !== expected.length) fail(where);
    expected.forEach((v, i) => sameValue(actual[i], v, `${where}[${i}]`));
  } else if (object(expected)) {
    if (!object(actual) || !sameKeys(Object.keys(actual), Object.keys(expected))) fail(where);
    for (const [k, v] of Object.entries(expected)) sameValue(actual[k], v, `${where}.${k}`);
  } else if (actual !== expected) fail(where);
}

export function observationMetrics(row) {
  const p = row.probabilities, confidence = p[row.choice], goldProbability = p[row.gold];
  return {
    confidence, correct: row.choice === row.gold,
    brier: Object.entries(p).reduce((sum, [k, v]) => sum + (v - Number(k === row.gold)) ** 2, 0),
    nll: goldProbability === 0 ? null : -Math.log(goldProbability),
    nll_is_infinite: goldProbability === 0,
    gold_probability: goldProbability,
    tied_maximum_count: Object.values(p).filter(v => v === confidence).length,
  };
}

/** The expected denominator includes missing/invalid observations; risk never does. */
export function summarizeField(rows) {
  const valid = rows.filter(r => r.status === 'valid').map(r => ({ ...r, ...observationMetrics(r) }));
  const n = valid.length, expected = rows.length, correct = valid.filter(r => r.correct).length;
  const bins = BIN_EDGES.slice(0, -1).map((lower, i) => {
    const upper = BIN_EDGES[i + 1], members = valid.filter(r => r.confidence >= lower && (r.confidence < upper || i === 9));
    const count = members.length, k = members.filter(r => r.correct).length;
    const score = mean(members.map(r => r.confidence)), accuracy = count ? k / count : null;
    return { lower, upper, upper_inclusive: i === 9, count, correct: k, mean_score: score, accuracy,
      signed_score_minus_accuracy_gap: count ? score - accuracy : null,
      absolute_gap: count ? Math.abs(score - accuracy) : null };
  });
  const risk_coverage = FIXED_THRESHOLDS.map(threshold => {
    const selected = valid.filter(r => r.confidence >= threshold), k = selected.filter(r => r.correct).length;
    return { threshold, selected_count: selected.length, correct: k, incorrect: selected.length - k,
      expected_count: expected, valid_count: n,
      coverage: expected ? selected.length / expected : null, valid_coverage: n ? selected.length / n : null,
      risk: selected.length ? (selected.length - k) / selected.length : null };
  });
  const good = valid.filter(r => r.correct), bad = valid.filter(r => !r.correct);
  const zeros = valid.filter(r => r.nll_is_infinite).map(r => r.id), finite = valid.filter(r => !r.nll_is_infinite).map(r => r.nll);
  return {
    option_count: rows[0]?.option_keys.length ?? 0,
    invalid_count: rows.filter(r => r.status === 'invalid').length,
    missing_count: rows.filter(r => r.status === 'missing').length,
    expected_gold_class_counts: countBy(rows, 'gold'),
    invalid_ids: rows.filter(r => r.status === 'invalid').map(r => r.id),
    missing_ids: rows.filter(r => r.status === 'missing').map(r => r.id),
    expected_count: expected, valid_count: n, correct, incorrect: n - correct,
    accuracy: n ? correct / n : null, correct_over_expected: expected ? correct / expected : null,
    brier_mean: mean(valid.map(r => r.brier)), nll_mean: n && !zeros.length ? mean(finite) : null,
    nll_is_infinite: !!zeros.length, zero_gold_probability_count: zeros.length, zero_gold_probability_ids: zeros,
    finite_nll_count: finite.length, finite_nll_mean: mean(finite),
    mean_selected_score: mean(valid.map(r => r.confidence)),
    signed_score_minus_accuracy_gap: n ? mean(valid.map(r => r.confidence)) - correct / n : null,
    gold_class_counts: countBy(valid, 'gold'), saved_choice_class_counts: countBy(valid, 'choice'),
    tie_count: valid.filter(r => r.tied_maximum_count > 1).length, bins,
    ece_10_equal_width: n ? bins.reduce((sum, b) => sum + b.count * (b.absolute_gap ?? 0), 0) / n : null,
    risk_coverage,
    error_detection_auroc: good.length && bad.length ? bad.reduce((sum, b) => sum + good.reduce((s, g) => s + (b.confidence < g.confidence ? 1 : b.confidence === g.confidence ? 0.5 : 0), 0), 0) / (bad.length * good.length) : null,
    error_auroc_correct_count: good.length, error_auroc_incorrect_count: bad.length,
    high_score_error_ids: Object.fromEntries(FIXED_THRESHOLDS.map(t => [t.toFixed(2), bad.filter(r => r.confidence >= t).map(r => r.id)])),
  };
}

/** Refuse inconsistent derived summaries; charts only consume recomputed quantities. */
export function validateReliability(payload) {
  if (!object(payload) || payload.schema_version !== 1 || payload.status !== 'completed' || payload.analysis_type !== 'post-hoc descriptive') fail('Format oder Status');
  sameValue(payload.thresholds, FIXED_THRESHOLDS, 'feste Schwellen');
  sameValue(payload.bin_edges, BIN_EDGES, 'Bin-Grenzen');
  array(payload.caveats, 'Grenzen', 100).forEach(c => str(c, 'Grenzen', 10000));
  if (!object(payload.definitions)) fail('Definitionen');
  for (const v of Object.values(payload.definitions)) str(v, 'Definition', 10000);
  const suites = array(payload.suites, 'Suiten', 100), groups = array(payload.field_groups, 'Feldgruppen', 1000);
  const observations = array(payload.observations, 'Feldbeobachtungen', 30000), cases = array(payload.cases, 'Fälle', 10000);
  if (!suites.length || !groups.length || !observations.length) fail('leerer Datensatz');
  const suiteMap = new Map(), groupMap = new Map(), caseMap = new Map(), rowsByGroup = new Map(), rowKeys = new Set();
  for (const suite of suites) {
    if (!object(suite)) fail('Suite');
    str(suite.id, 'Suite-ID'); str(suite.title, 'Suite-Titel');
    if (suiteMap.has(suite.id)) fail('doppelte Suite');
    suiteMap.set(suite.id, suite);
  }
  const groupIdentities = new Set();
  for (const group of groups) {
    if (!object(group)) fail('Feldgruppe');
    str(group.group_id, 'Gruppen-ID'); str(group.field, 'Feld');
    if (!suiteMap.has(group.suite_id) || groupMap.has(group.group_id)) fail('Suite oder doppelte Gruppe');
    options(group.option_keys, 'Gruppenoptionen'); partition(group.partition, 'Gruppenpartition');
    const identity = JSON.stringify([group.suite_id, group.field, Object.entries(group.partition).sort(), [...group.option_keys].sort()]);
    if (groupIdentities.has(identity)) fail('doppelte semantische Feldgruppe');
    groupIdentities.add(identity); groupMap.set(group.group_id, group); rowsByGroup.set(group.group_id, []);
  }
  for (const item of cases) {
    if (!object(item) || !suiteMap.has(item.suite_id)) fail('Fall');
    str(item.id, 'Fall-ID');
    if ((typeof item.input !== 'string' && !object(item.input) && !Array.isArray(item.input)) || JSON.stringify(item.input).length > 300000 || !object(item.questions) || !object(item.expected) || !object(item.metadata)) fail('Rohfall');
    const key = JSON.stringify([item.suite_id, item.id]);
    if (caseMap.has(key)) fail('doppelter Fall');
    caseMap.set(key, item);
  }
  const normalized = [];
  for (const row of observations) {
    if (!object(row)) fail('Feldbeobachtung');
    str(row.id, 'Beobachtungs-ID');
    const group = groupMap.get(row.group_id), item = caseMap.get(JSON.stringify([row.suite_id, row.id]));
    if (!group || !item || row.suite_id !== group.suite_id || row.field !== group.field) fail('Beobachtungszuordnung');
    sameValue(row.partition, group.partition, 'Beobachtungspartition');
    options(row.option_keys, 'Beobachtungsoptionen');
    if (!sameKeys(row.option_keys, group.option_keys)) fail('Optionssatz');
    const key = JSON.stringify([row.suite_id, row.id, row.field]);
    if (rowKeys.has(key)) fail('doppelte Feldbeobachtung');
    rowKeys.add(key);
    const question = item.questions[row.field];
    if (!object(question) || !object(question.criteria) || !sameKeys(Object.keys(question.criteria), row.option_keys) || !row.option_keys.includes(row.gold) || item.expected[row.field] !== row.gold) fail('Originalschema oder Gold');
    if (!['valid', 'invalid', 'missing'].includes(row.status)) fail('Beobachtungsstatus');
    array(row.issues, 'Beobachtungsprobleme', 100).forEach(issue => str(issue, 'Beobachtungsproblem'));
    let validated = { ...row };
    if (row.status === 'valid') {
      if (row.issues.length || !object(row.probabilities) || !sameKeys(Object.keys(row.probabilities), row.option_keys) || !row.option_keys.includes(row.choice)) fail('Optionsvektor');
      const values = Object.values(row.probabilities);
      if (values.some(v => typeof v !== 'number' || !Number.isFinite(v) || v < 0 || v > 1) || Math.abs(values.reduce((a, b) => a + b, 0) - 1) > 1e-5) fail('Wahrscheinlichkeit');
      if (row.probabilities[row.choice] !== Math.max(...values)) fail('gespeicherte Auswahl ist nicht das Maximum');
      const metrics = observationMetrics(row);
      for (const [key, value] of Object.entries(metrics)) sameValue(row[key], value, `Beobachtungsmetrik ${key}`);
      validated = { ...row, ...metrics };
    }
    normalized.push(validated); rowsByGroup.get(row.group_id).push(validated);
  }
  // All labelled case fields must be represented, including failed/missing results.
  for (const item of cases) {
    for (const field of Object.keys(item.expected)) if (!rowKeys.has(JSON.stringify([item.suite_id, item.id, field]))) fail('fehlende erwartete Feldbeobachtung');
  }
  const computedGroups = groups.map(group => {
    const rows = rowsByGroup.get(group.group_id);
    if (!rows.length) fail('Gruppe ohne Beobachtungen');
    const recomputed = summarizeField(rows);
    for (const [key, value] of Object.entries(recomputed)) sameValue(group[key], value, `${group.group_id}: ${key}`);
    return { ...group, ...recomputed, observations: rows };
  });
  for (const suite of suites) {
    const rows = normalized.filter(r => r.suite_id === suite.id), suiteCases = cases.filter(c => c.suite_id === suite.id);
    sameValue(suite.expected_count, suiteCases.length, 'Suite-Fallnenner');
    sameValue(suite.valid_field_count, rows.filter(r => r.status === 'valid').length, 'Suite-Feldnenner');
    sameValue(suite.invalid_field_count, rows.filter(r => r.status === 'invalid').length, 'Suite-ungültig');
    sameValue(suite.missing_field_count, rows.filter(r => r.status === 'missing').length, 'Suite-fehlend');
    if (!Array.isArray(suite.field_group_ids) || new Set(suite.field_group_ids).size !== suite.field_group_ids.length || !sameKeys(suite.field_group_ids, groups.filter(g => g.suite_id === suite.id).map(g => g.group_id))) fail('Suite-Gruppenliste');
  }
  return { ...payload, field_groups: computedGroups, observations: normalized, caseMap };
}

export function groupLabel(group) {
  const values = Object.entries(group.partition).map(([key, value]) => `${key}: ${value}`);
  return `${values.length ? values.join(' · ') : 'Alle Fälle dieses Feldes'} · ${group.option_count} Optionen`;
}

export function selectReliabilityGroup(data, params = {}) {
  const get = key => typeof params.get === 'function' ? params.get(key) : params[key];
  const requestedGroup = data.field_groups.find(g => g.group_id === get('group'));
  const suite = data.suites.find(s => s.id === get('suite')) || (requestedGroup && data.suites.find(s => s.id === requestedGroup.suite_id)) || data.suites.find(s => s.id === 'minimal_pairs48') || data.suites[0];
  const suiteGroups = data.field_groups.filter(g => g.suite_id === suite.id);
  const fields = [...new Set(suiteGroups.map(g => g.field))];
  const field = fields.includes(get('field')) ? get('field') : requestedGroup?.suite_id === suite.id ? requestedGroup.field : fields.includes('determination') ? 'determination' : fields[0];
  const candidates = suiteGroups.filter(g => g.field === field);
  const group = candidates.find(g => g.group_id === get('group')) || candidates.find(g => g.partition.condition === 'image' && g.partition.language === 'de') || candidates[0];
  const threshold = get('threshold') !== null && get('threshold') !== undefined && get('threshold') !== '' && FIXED_THRESHOLDS.includes(Number(get('threshold'))) ? Number(get('threshold')) : 0.9;
  return { suite: suite.id, field, group: group.group_id, threshold };
}
