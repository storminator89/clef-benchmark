/** Small read-only contract for independently admitted scientific studies. */
const object = value => value !== null && typeof value === 'object' && !Array.isArray(value);
const fail = message => { throw new Error(message); };
export function validateStudyIndex(value) {
  if (!object(value) || value.format_version !== 1 || !Array.isArray(value.studies)) fail('Ungültiger Studienindex.');
  const ids = new Set();
  for (const item of value.studies) {
    if (!object(item) || !/^[a-z][a-z0-9_-]*$/.test(item.id) || ids.has(item.id)) fail('Ungültige Studien-ID.');
    ids.add(item.id);
    if (!['pending','completed','cancelled'].includes(item.status) || typeof item.label !== 'string' || !Number.isInteger(item.planned_requests) || item.planned_requests < 1) fail('Ungültiger Studienstatus.');
    if (!Array.isArray(item.methods) || !item.methods.every(x => typeof x === 'string')) fail('Methodik fehlt.');
    if (item.status !== 'completed' && ('metrics' in item || 'cases' in item || 'data_file' in item)) fail('Ausstehender Test enthält scheinbare Messwerte.');
    if (item.status === 'completed' && item.data_file !== `./studies-data/${item.id}.json`) fail('Ungültiger Ergebnisdateipfad.');
  }
  return value;
}
export function validateStudyData(value, entry) {
  if (!object(value) || value.format_version !== 1 || value.id !== entry.id || value.status !== 'completed') fail('Ergebnis gehört nicht zur ausgewählten Studie.');
  if (value.audit?.status !== 'passed' || !/^[0-9a-f]{64}$/.test(value.audit.source_manifest_sha256 || '')) fail('Verifizierte Quellenbindung fehlt.');
  if (!Array.isArray(value.cases) || value.cases.length !== entry.planned_requests || !Array.isArray(value.metrics)) fail('Geplanter Nenner stimmt nicht überein.');
  if (value.secondary_metrics !== undefined && !Array.isArray(value.secondary_metrics)) fail('Ungültige Detailkennzahlen.');
  for (const metric of [...value.metrics,...(value.secondary_metrics||[])]) {
    if (!object(metric) || typeof metric.label !== 'string' || !['ratio','decimal'].includes(metric.kind)) fail('Ungültige Kennzahl.');
    if (metric.kind === 'ratio' && (!Number.isInteger(metric.numerator) || !Number.isInteger(metric.denominator) || metric.denominator < 1 || metric.numerator < 0 || metric.numerator > metric.denominator || typeof metric.unit !== 'string')) fail('Kennzahl hat keinen gültigen eigenen Nenner.');
    if (metric.kind === 'decimal' && (!Number.isFinite(metric.value) || typeof metric.note !== 'string')) fail('Kennzahlkonvention fehlt.');
  }
  if (value.limitations !== undefined && (!Array.isArray(value.limitations) || !value.limitations.every(x=>typeof x==='string'))) fail('Ungültige Methodikhinweise.');
  if (value.findings !== undefined && (!Array.isArray(value.findings) || !value.findings.every(x=>typeof x==='string'))) fail('Ungültige Ergebnisnotiz.');
  if (value.directional_note !== undefined && typeof value.directional_note !== 'string') fail('Ungültige Paarnotiz.');
  if (value.comparisons !== undefined) {
    if (!Array.isArray(value.comparisons)) fail('Ungültige Vergleichsteilgruppen.');
    for (const row of value.comparisons) {
      if (typeof row.label !== 'string' || typeof row.baseline_ready !== 'boolean' || ![row.expected,row.matched,row.jev_valid,row.jev_correct_valid_only].every(Number.isInteger) || row.expected < 1 || row.matched < 0 || row.matched > row.jev_valid || row.jev_valid > row.expected || row.jev_correct_valid_only < 0 || row.jev_correct_valid_only > row.jev_valid) fail('Vergleichsnenner stimmen nicht überein.');
      if (row.matched && (![row.clef_correct,row.jev_correct].every(Number.isInteger) || row.clef_correct < 0 || row.jev_correct < 0 || row.clef_correct > row.matched || row.jev_correct > row.matched || !row.baseline_ready)) fail('Direkter Vergleich verwendet ungültige Fälle.');
      if (!row.baseline_ready && (row.matched || row.clef_correct !== null || row.jev_correct !== null)) fail('Fehlende Baseline wird als Modellresultat angezeigt.');
    }
  }
  const ids = new Set();
  for (const row of value.cases) {
    if (!object(row) || typeof row.id !== 'string' || ids.has(row.id) || !(typeof row.input === 'string' || object(row.input) || Array.isArray(row.input)) || !object(row.questions) || !object(row.expected)) fail('Ungültiger oder doppelter Fall.');
    ids.add(row.id);
    const fields = Object.keys(row.questions);
    if (!fields.length || Object.keys(row.expected).length !== fields.length || typeof row.valid !== 'boolean' || typeof row.correct !== 'boolean') fail('Antwortfelder fehlen.');
    for (const field of fields) {
      if (!Object.hasOwn(row.expected,field) || typeof row.expected[field] !== 'string' || !object(row.questions[field]) || row.questions[field].type !== 'choice' || !object(row.questions[field].criteria) || !Object.hasOwn(row.questions[field].criteria,row.expected[field])) fail('Goldlabel fehlt im nativen Schema.');
    }
    if (row.valid) {
      if (!object(row.prediction) || !object(row.probabilities) || Object.keys(row.prediction).length !== fields.length || Object.keys(row.probabilities).length !== fields.length) fail('Native Antwortfelder fehlen.');
      for (const field of fields) {
        const p = row.probabilities[field], criteria = row.questions[field].criteria;
        if (!object(p) || Object.keys(p).length !== Object.keys(criteria).length || !Object.keys(criteria).every(k => Object.hasOwn(p,k)) || !Object.values(p).every(v => Number.isFinite(v) && v >= 0 && v <= 1)) fail('Native Wahrscheinlichkeiten fehlen.');
        if (Math.abs(Object.values(p).reduce((a,b)=>a+b,0)-1) > 1e-5) fail('Native Verteilung verletzt den Normalisierungsvertrag.');
        if (!Object.hasOwn(p,row.prediction[field]) || p[row.prediction[field]] !== Math.max(...Object.values(p))) fail('Vorhersage stimmt nicht mit nativen Optionen überein.');
      }
      if (row.correct !== fields.every(f => row.expected[f] === row.prediction[f])) fail('Ergebnis stimmt nicht mit Gold überein.');
    } else if (row.correct || typeof row.technical_note !== 'string') fail('Technischer Ausfall wurde als richtig gewertet.');
  }
  return value;
}
export function filterStudyCases(rows, {query='',outcome='all',group='all'}={}) {
  const search = query.trim().toLocaleLowerCase('de');
  return rows.filter(row => (group === 'all' || row.group === group) &&
    (outcome === 'all' || (outcome === 'correct' && row.correct) || (outcome === 'errors' && row.valid && !row.correct) || (outcome === 'technical' && !row.valid)) &&
    `${row.id} ${row.group || ''} ${row.pair_id || ''} ${typeof row.input==='string'?row.input:JSON.stringify(row.input)} ${JSON.stringify(row.expected)} ${JSON.stringify(row.prediction || {})}`.toLocaleLowerCase('de').includes(search));
}
