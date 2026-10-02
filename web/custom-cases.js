/** Private custom inputs. No network, persistence, model emulation, or benchmark trust. */
import { canonicalJSON, isObject, parseJSONStrict, validatePlayground, validateLiveResult } from './core.js';
export const CUSTOM_LIMITS = Object.freeze({ bytes: 5 * 1024 * 1024, cases: 500, depth: 12 });
const forbidden = new Set(['__proto__', 'prototype', 'constructor']);
const own = (o, k) => Object.hasOwn(o, k);
const blank = value => typeof value === 'string' && /^[\s\u0085\u001c-\u001f]*$/u.test(value);
function customBlanks(state, questions) {
  if (blank(state)) throw Error('Eingabetext darf nicht nur Leerraum enthalten.');
  if (isObject(questions)) for (const q of Object.values(questions)) {
    if (blank(q?.instructions)) throw Error('Richtlinie darf nicht nur Leerraum enthalten.');
    if (isObject(q?.criteria) && Object.values(q.criteria).some(blank)) throw Error('Klassenbeschreibung darf nicht nur Leerraum enthalten.');
  }
}
export class SuiteValidationError extends Error {
  constructor(errors) { super(errors.join('\n')); this.name = 'SuiteValidationError'; this.errors = errors; }
}
export function safeTree(value, depth = 0) {
  if (depth > CUSTOM_LIMITS.depth) throw Error(`Verschachtelung über ${CUSTOM_LIMITS.depth} Ebenen.`);
  if (typeof value === 'string' && /[\uD800-\uDBFF](?![\uDC00-\uDFFF])|(?<![\uD800-\uDBFF])[\uDC00-\uDFFF]/u.test(value)) throw Error('Ungültiges Unicode-Zeichen (einzelnes Surrogat).');
  if (typeof value === 'number' && !Number.isFinite(value)) throw Error('Nicht-endliche Zahlen sind nicht erlaubt.');
  if (value && typeof value === 'object') for (const [key, v] of Object.entries(value)) {
    if (forbidden.has(key)) throw Error(`Reservierter Schlüssel: ${key}`);
    safeTree(key, depth + 1); safeTree(v, depth + 1);
  }
  return value;
}
export function parseBoundedJSON(raw) {
  if (typeof raw !== 'string' || new TextEncoder().encode(raw).length > CUSTOM_LIMITS.bytes) throw Error('Datei ist größer als 5 MiB.');
  const text = raw.replace(/^\uFEFF/, '');
  // Check depth before the recursive strict-key parser, without confusing quoted braces.
  let depth = 0, quoted = false, escaped = false;
  for (const c of text) {
    if (quoted) { if (escaped) escaped = false; else if (c === '\\') escaped = true; else if (c === '"') quoted = false; }
    else if (c === '"') quoted = true;
    else if (c === '[' || c === '{') { if (++depth > CUSTOM_LIMITS.depth) throw Error(`Verschachtelung über ${CUSTOM_LIMITS.depth} Ebenen.`); }
    else if (c === ']' || c === '}') depth--;
  }
  return safeTree(parseJSONStrict(text));
}
function exactKeys(value, required, optional = []) {
  return isObject(value) && required.every(k => own(value, k)) && Object.keys(value).every(k => required.includes(k) || optional.includes(k));
}
export function validateCase(value) {
  safeTree(value);
  if (!exactKeys(value, ['id', 'state', 'questions'], ['gold'])) throw Error('Fall braucht genau id, state, questions und optional gold.');
  if (typeof value.id !== 'string' || !/^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$/.test(value.id)) throw Error('id muss eindeutig sein: 1–64 ASCII-Buchstaben/Ziffern, _ oder -; erstes Zeichen alphanumerisch.');
  customBlanks(value.state, value.questions);
  validatePlayground(value.state, value.questions);
  if (own(value, 'gold')) {
    if (!isObject(value.gold)) throw Error('gold muss ein Objekt mit vorhandenen Frage-IDs sein.');
    for (const [field, label] of Object.entries(value.gold)) if (!own(value.questions, field) || typeof label !== 'string' || !own(value.questions[field].criteria, label)) throw Error(`Ungültiges Goldlabel für ${field}: wähle eine vorhandene Option oder lasse das Feld weg.`);
  }
  return structuredClone(value);
}
export function validateSuite(value) {
  safeTree(value);
  if (!exactKeys(value, ['schema_version', 'name', 'cases']) || value.schema_version !== 1) throw new SuiteValidationError(['Erwartet: {schema_version:1, name, cases}. Andere Felder (auch gespeicherte Ergebnisse/Prüfsiegel) sind nicht erlaubt.']);
  if (typeof value.name !== 'string' || blank(value.name) || [...value.name].length > 200) throw new SuiteValidationError(['name muss 1–200 Zeichen enthalten.']);
  if (!Array.isArray(value.cases) || value.cases.length < 1 || value.cases.length > CUSTOM_LIMITS.cases) throw new SuiteValidationError(['cases muss 1–500 Fälle enthalten. Es wird nichts still abgeschnitten.']);
  const errors = [], ids = new Set(), cases = [];
  value.cases.forEach((c, i) => {
    try {
      const checked = validateCase(c);
      if (ids.has(checked.id)) throw Error(`Doppelte Fall-ID: ${checked.id}`);
      ids.add(checked.id); cases.push(checked);
    } catch (error) { errors.push(`Fall ${i + 1}${typeof c?.id === 'string' ? ` (${c.id})` : ''}: ${error.message}`); }
  });
  if (errors.length) throw new SuiteValidationError(errors);
  return { schema_version: 1, name: value.name, cases };
}
export function validateSpec(value) {
  safeTree(value);
  if (!exactKeys(value, ['schema_version', 'questions']) || value.schema_version !== 1) throw Error('CSV-Spezifikation braucht genau schema_version:1 und questions.');
  customBlanks('Schema-Prüfung', value.questions);
  validatePlayground('Schema-Prüfung', value.questions);
  return structuredClone(value);
}
/** RFC 4180-style CSV: commas, escaped quotes, BOM, CRLF/LF/CR and quoted newlines. */
export function parseCSV(raw) {
  if (typeof raw !== 'string' || new TextEncoder().encode(raw).length > CUSTOM_LIMITS.bytes) throw Error('Datei ist größer als 5 MiB.');
  const text = raw.replace(/^\uFEFF/, '');
  const rows = []; let row = [], cell = '', quoted = false, closed = false, line = 1, rowLine = 1;
  const addCell = () => { if (row.length >= 10) throw Error(`CSV-Zeile ${rowLine}: Höchstens 10 Spalten (id, state und bis zu 8 Goldfelder).`); row.push(cell); cell = ''; closed = false; };
  const addRow = () => { if (rows.length >= CUSTOM_LIMITS.cases + 1) throw Error('CSV enthält mehr als 500 Fälle.'); addCell(); rows.push({ cells: row, line: rowLine }); row = []; rowLine = line + 1; };
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (quoted) {
      if (c === '"') { if (text[i + 1] === '"') { cell += '"'; i++; } else { quoted = false; closed = true; } }
      else { cell += c; if (c === '\n' || (c === '\r' && text[i + 1] !== '\n')) line++; }
      continue;
    }
    if (c === ',') { addCell(); continue; }
    if (c === '\r' || c === '\n') { addRow(); if (c === '\r' && text[i + 1] === '\n') i++; line++; continue; }
    if (closed) throw Error(`CSV-Zeile ${line}: Nach einem schließenden Anführungszeichen sind nur Komma oder Zeilenende erlaubt.`);
    if (c === '"') { if (cell.length) throw Error(`CSV-Zeile ${line}: Unerwartetes Anführungszeichen.`); quoted = true; }
    else cell += c;
  }
  if (quoted) throw Error(`CSV-Zeile ${rowLine}: Nicht geschlossenes Anführungszeichen.`);
  if (row.length || cell.length || closed || (text.length && !/[\r\n]$/.test(text))) { if (rows.length >= CUSTOM_LIMITS.cases + 1) throw Error('CSV enthält mehr als 500 Fälle.'); addCell(); rows.push({ cells: row, line: rowLine }); }
  return rows;
}
export function importSuite(raw, { format = 'json', name = 'Eigene Tests', spec = null } = {}) {
  if (typeof raw !== 'string' || new TextEncoder().encode(raw).length > CUSTOM_LIMITS.bytes) throw new SuiteValidationError(['Datei ist größer als 5 MiB.']);
  const text = raw.replace(/^\uFEFF/, '');
  try {
    if (format === 'json') return validateSuite(parseBoundedJSON(raw));
    if (format === 'jsonl') {
      const lines = text.split(/\r\n|\n|\r/); if (lines.at(-1) === '') lines.pop();
      if (lines.length > CUSTOM_LIMITS.cases) throw Error('JSONL enthält mehr als 500 Fälle.');
      const errors = [], cases = [];
      lines.forEach((line, i) => { try { if (!line.trim()) throw Error('Leere Zeile ist kein Fall.'); if (line.startsWith('\uFEFF')) throw Error('BOM ist nur einmal am Dateianfang erlaubt.'); cases.push(parseBoundedJSON(line)); } catch (err) { errors.push(`JSONL-Zeile ${i + 1}: ${err.message}`); } });
      if (errors.length) throw new SuiteValidationError(errors);
      return validateSuite({ schema_version: 1, name, cases });
    }
    if (format !== 'csv') throw Error('Nur JSON, JSONL und CSV werden unterstützt.');
    const checkedSpec = validateSpec(spec), rows = parseCSV(raw);
    if (!rows.length) throw Error('CSV ist leer.');
    const header = rows.shift().cells;
    if (new Set(header).size !== header.length) throw Error('CSV enthält doppelte Spaltennamen.');
    if (!header.includes('id') || !header.includes('state')) throw Error('CSV braucht die Spalten id und state.');
    for (const key of header) if (!['id', 'state'].includes(key) && !(key.startsWith('gold.') && own(checkedSpec.questions, key.slice(5)))) throw Error(`Unbekannte CSV-Spalte: ${key}. Erlaubt sind id, state und gold.FRAGE.`);
    if (rows.length > CUSTOM_LIMITS.cases) throw Error('CSV enthält mehr als 500 Fälle.');
    const errors = [], cases = [];
    for (const row of rows) {
      try {
        if (row.cells.length !== header.length) throw Error(`Erwartet ${header.length} Spalten, erhalten ${row.cells.length}.`);
        const cells = Object.fromEntries(header.map((key, i) => [key, row.cells[i]]));
        const gold = Object.fromEntries(header.filter(key => key.startsWith('gold.') && cells[key] !== '').map(key => [key.slice(5), cells[key]]));
        const value = { id: cells.id, state: cells.state, questions: structuredClone(checkedSpec.questions), ...(Object.keys(gold).length ? { gold } : {}) };
        validateCase(value); cases.push(value);
      } catch (error) { errors.push(`CSV-Zeile ${row.line}: ${error.message}`); }
    }
    if (errors.length) throw new SuiteValidationError(errors);
    return validateSuite({ schema_version: 1, name, cases });
  } catch (error) { if (error instanceof SuiteValidationError) throw error; throw new SuiteValidationError([error.message]); }
}
export const PRESETS = Object.freeze({
  statement: { schema_version: 1, questions: { decision: { type: 'choice', instructions: 'Prüfe die im Text ausdrücklich genannte Aussage anhand des mitgelieferten Dokuments. Verwende nur diese Angaben.', criteria: { ja: 'Die Aussage wird gestützt.', nein: 'Die Aussage wird widerlegt.', offen: 'Die Informationen reichen nicht aus.' } } } },
  support: { schema_version: 1, questions: {
    intent: { type: 'choice', instructions: 'Ordne das Hauptanliegen des synthetischen Supporttexts ein.', criteria: { zugang: 'Anmeldung oder Passwort', karte: 'Zahlungskarte', sonstiges: 'Anderes Anliegen' } },
    priority: { type: 'choice', instructions: 'Ist ein akuter, im Text ausdrücklich beschriebener Schaden zu stoppen? Wunsch nach schneller Antwort allein ist nicht dringend.', criteria: { normal: 'Kein akuter Schaden beschrieben', dringend: 'Akuter Verlust, Missbrauch oder Schaden beschrieben' } },
  } },
});
export function exampleSuite() {
  return { schema_version: 1, name: 'Synthetische Supportbeispiele', cases: [
    { id: 'beispiel_001', state: 'Ich habe mein Passwort vergessen und kann mich nicht anmelden.', questions: structuredClone(PRESETS.support.questions), gold: { intent: 'zugang', priority: 'normal' } },
    { id: 'beispiel_002', state: 'Meine Karte wurde gestohlen. Bitte sperren.', questions: structuredClone(PRESETS.support.questions), gold: { intent: 'karte' } },
    { id: 'beispiel_003', state: 'Wann beginnt die nächste Sprechstunde?', questions: structuredClone(PRESETS.support.questions) },
  ] };
}
export const fingerprintText = suite => canonicalJSON({ suite, question_order: suite.cases.map(c => Object.keys(c.questions)) });
export async function suiteFingerprint(suite, crypto = globalThis.crypto) {
  if (!crypto?.subtle) throw Error('SHA-256 ist hier nicht verfügbar. Öffne den Workbench über http://127.0.0.1:8765.');
  return [...new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(fingerprintText(suite))))].map(n => n.toString(16).padStart(2, '0')).join('');
}
export const MODEL_IDENTITY_KEYS = ['model_key', 'model_id', 'model', 'revision', 'requested_profile'];
export function modelIdentity(health) {
  if (!isObject(health) || MODEL_IDENTITY_KEYS.some(k => typeof health[k] !== 'string' || !health[k].trim())) throw Error('Backend meldet keine vollständige Modellidentität. Bitte lokalen Server aktualisieren.');
  return Object.fromEntries(MODEL_IDENTITY_KEYS.map(k => [k, health[k]]));
}
export async function modelIdentityFingerprint(suite_sha256, model_identity) {
  const bytes = await globalThis.crypto.subtle.digest('SHA-256', new TextEncoder().encode(canonicalJSON({ suite_sha256, model_identity })));
  return [...new Uint8Array(bytes)].map(n => n.toString(16).padStart(2, '0')).join('');
}
export function validateCustomResponse(result, request, identity = null) {
  validateLiveResult(result, request);
  if (result.benchmark_result !== false || !isObject(result.runtime) || !['device', 'precision', 'profile'].every(k => typeof result.runtime[k] === 'string' && result.runtime[k].trim())) throw Error('Das Backend hat kein tatsächliches Gerät, Profil und keine Präzision angegeben.');
  modelIdentity(result);
  for (const field of ['answers', 'probabilities_unrounded']) if (Object.keys(result[field]).join('|') !== Object.keys(request.questions).join('|')) throw Error('Antwortfelder wurden umgeordnet.');
  if (identity && (MODEL_IDENTITY_KEYS.some(k => result[k] !== identity[k]) || result.runtime.profile !== identity.requested_profile)) throw Error('Antwort passt nicht zum Modell, zur Revision oder zum Profil dieses Laufs.');
  if (['model_key', 'model_id', 'revision'].some(k => result.runtime[k] !== result[k])) throw Error('Widersprüchliche Modellmetadaten.');
  for (const key of ['device', 'precision']) if (result[key] !== result.runtime[key]) throw Error('Widersprüchliche Geräte-/Präzisionsmetadaten.');
  for (const [field, q] of Object.entries(request.questions)) {
    const answer = result.answers[field], rounded = answer.probabilities, unrounded = result.probabilities_unrounded[field];
    if (Object.keys(answer).sort().join(',') !== 'choice,confidence,probabilities,type' || !isObject(rounded) || Object.keys(rounded).sort().join('|') !== Object.keys(q.criteria).sort().join('|')) throw Error('Unvollständige native Choice-Antwort.');
    if (Object.values(rounded).some(v => !Number.isFinite(v) || v < 0 || v > 1) || Math.abs(Object.values(rounded).reduce((a,b) => a+b,0)-1) > 0.00061 || Object.keys(rounded).some(k => Math.abs(rounded[k]-unrounded[k]) > 0.000051) || !Number.isFinite(answer.confidence) || Math.abs(answer.confidence-rounded[answer.choice]) > 0.000001) throw Error('Native Wahrscheinlichkeiten oder Konfidenz sind ungültig.');
  }
  return result;
}
export function scoreSuite(suite, results = []) {
  const byID = new Map(results.map(r => [r.id, r]));
  const s = { cases_total: suite.cases.length, cases_succeeded: 0, cases_failed: 0, cases_pending: 0, fields_total: 0, labelled_fields: 0, unlabelled_fields: 0, evaluated_labelled_fields: 0, correct_labelled_fields: 0, field_accuracy: null, field_coverage: null, fully_labelled_cases: 0, evaluated_fully_labelled_cases: 0, correct_fully_labelled_cases: 0, case_accuracy: null, case_coverage: null, by_field: {} };
  for (const c of suite.cases) {
    const r = byID.get(c.id), good = r?.status === 'success';
    s[good ? 'cases_succeeded' : r?.status === 'error' ? 'cases_failed' : 'cases_pending']++;
    const fields = Object.keys(c.questions), labelled = Object.keys(c.gold || {});
    s.fields_total += fields.length; s.labelled_fields += labelled.length;
    for (const f of fields) {
      if (!own(s.by_field, f)) s.by_field[f] = { labelled: 0, evaluated: 0, correct: 0, accuracy: null, coverage: null };
      if (!own(c.gold || {}, f)) continue;
      const fs = s.by_field[f]; fs.labelled++;
      if (good) { s.evaluated_labelled_fields++; fs.evaluated++; if (r.response.answers[f].choice === c.gold[f]) { s.correct_labelled_fields++; fs.correct++; } }
    }
    if (labelled.length === fields.length) {
      s.fully_labelled_cases++;
      if (good) { s.evaluated_fully_labelled_cases++; if (fields.every(f => r.response.answers[f].choice === c.gold[f])) s.correct_fully_labelled_cases++; }
    }
  }
  s.unlabelled_fields = s.fields_total - s.labelled_fields;
  s.completion_coverage = (s.cases_succeeded + s.cases_failed) / s.cases_total;
  s.prediction_coverage = s.cases_succeeded / s.cases_total;
  s.gold_coverage = s.labelled_fields / s.fields_total;
  if (s.labelled_fields) { s.field_accuracy = s.correct_labelled_fields / s.labelled_fields; s.field_coverage = s.evaluated_labelled_fields / s.labelled_fields; }
  if (s.fully_labelled_cases) { s.case_accuracy = s.correct_fully_labelled_cases / s.fully_labelled_cases; s.case_coverage = s.evaluated_fully_labelled_cases / s.fully_labelled_cases; }
  for (const f of Object.values(s.by_field)) if (f.labelled) { f.accuracy = f.correct / f.labelled; f.coverage = f.evaluated / f.labelled; }
  return s;
}
export async function newReport(suite, endpoint = null) {
  const copy = validateSuite(suite), now = new Date().toISOString();
  const results = copy.cases.map(c => ({ id: c.id, status: 'pending', response: null, error: null, elapsed_seconds: null }));
  return { schema_version: 1, report_type: 'custom_suite_evaluation', benchmark_result: false, suite: copy, suite_sha256: await suiteFingerprint(copy), created_at: now, updated_at: now, status: 'validated', endpoint, health_before: null, health_after: null, model_identity: null, model_identity_sha256: null, result_provenance: 'local_execution', results, summary: scoreSuite(copy, results) };
}
export function refreshReport(report) { report.summary = scoreSuite(report.suite, report.results); report.updated_at = new Date().toISOString(); return report; }
/** A file exported during HTTP must never allow a later resume to repeat that uncertain request. */
export function exportSnapshot(report, inFlightID = null) {
  const copy = structuredClone(report);
  if (inFlightID) {
    const row = copy.results.find(r => r.id === inFlightID);
    if (row?.status === 'pending') {
      row.status = 'error';
      row.error = { kind: 'in_flight', message: 'Export während eines laufenden Requests. Ergebnis zu diesem Zeitpunkt ungewiss; kein automatischer Wiederholungsversuch beim Resume.' };
    }
  }
  return refreshReport(copy);
}
export function csvCell(value) {
  let text = String(value ?? '');
  if (/^[\t\r\n]/.test(text) || /^[\s\u0085\u001c-\u001f]*[=+\-@]/u.test(text)) text = "'" + text;
  return '"' + text.replaceAll('"', '""') + '"';
}
export function resultsCSV(report) {
  const rows = [['id', 'field', 'status', 'gold', 'prediction', 'correct', 'forward_ms', 'elapsed_seconds', 'device', 'precision', 'model', 'revision', 'requested_profile', 'error']];
  for (const c of report.suite.cases) {
    const r = report.results.find(r => r.id === c.id);
    for (const field of Object.keys(c.questions)) {
      const gold = c.gold?.[field], choice = r?.status === 'success' ? r.response.answers[field].choice : '';
      rows.push([c.id, field, r?.status || 'pending', gold ?? '', choice, gold === undefined ? '' : r?.status === 'success' && choice === gold ? 'true' : 'false', r?.response?.latency_ms ?? '', r?.elapsed_seconds ?? '', r?.response?.runtime?.device ?? '', r?.response?.runtime?.precision ?? '', r?.response?.model ?? '', r?.response?.revision ?? '', r?.response?.requested_profile ?? '', r?.error?.message ?? '']);
    }
  }
  return '\uFEFF' + rows.map(row => row.map(csvCell).join(',')).join('\r\n') + '\r\n';
}
/** One in-flight request. Cancellation only stops the next case, never claims server abortion. */
export class CustomEvaluator {
  constructor({ fetch = globalThis.fetch, onChange = () => {}, isBusy = () => false } = {}) { this.fetch = fetch; this.onChange = onChange; this.isBusy = isBusy; this.busy = false; this.stopRequested = false; this.current = null; }
  cancel() { if (this.busy) { this.stopRequested = true; this.onChange(); } }
  async run(report) {
    if (this.busy || this.isBusy()) return false;
    this.busy = true; this.stopRequested = false; this.onChange();
    try {
      if (await suiteFingerprint(report.suite) !== report.suite_sha256) throw Error('Suite geändert. Die bisherigen Ergebnisse dürfen nicht fortgesetzt werden.');
      const h = await this.fetch('/api/health', { cache: 'no-store' });
      if (!h.ok) throw Error('Lokales Backend ist nicht erreichbar.');
      const health = await h.json();
      if (!isObject(health) || typeof health.inference_enabled !== 'boolean' || typeof health.busy !== 'boolean') throw Error('Ungültiger Backendstatus. Es wurde keine Anfrage gesendet.');
      if (!health.inference_enabled) throw Error('Lokale Inferenz ist deaktiviert. Starte den Server mit --enable-inference und --model-dir.');
      if (health.busy) throw Error('Das lokale Modell bearbeitet bereits eine andere Anfrage. Warte bis zu deren Ende.');
      const identity = modelIdentity(health);
      if (report.model_identity && canonicalJSON(report.model_identity) !== canonicalJSON(identity)) throw Error('Backend-Modell oder Profil hat gewechselt. Dieser Teillauf darf nicht vermischt werden. Starte für das neue Modell eine neue Suite-Auswertung.');
      if (!report.model_identity) {
        if (report.results.some(r => r.status !== 'pending')) throw Error('Teillauf hat keine sichere Modellzuordnung.');
        report.model_identity = identity;
        report.model_identity_sha256 = await modelIdentityFingerprint(report.suite_sha256, identity);
      } else if (report.model_identity_sha256 !== await modelIdentityFingerprint(report.suite_sha256, identity)) throw Error('Modell-Fingerprint dieses Laufs stimmt nicht.');
      report.health_before = health;
      delete report.run_error;
      report.status = 'running'; this.onChange(refreshReport(report));
      for (const c of report.suite.cases) {
        const row = report.results.find(r => r.id === c.id); if (row.status !== 'pending') continue;
        if (this.stopRequested) break;
        this.current = c.id; this.onChange(refreshReport(report));
        const request = validatePlayground(c.state, c.questions), started = Date.now();
        try {
          const r = await this.fetch('/api/infer', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Clef-Request': '1' }, body: JSON.stringify(request) });
          let result;
          try { result = await r.json(); } catch { throw Error('Das Backend lieferte keine gültige JSON-Antwort. Keine weitere Anfrage, da der Serverstatus unklar ist.'); }
          row.response = result;
          if (!r.ok) { row.status = 'error'; row.error = { kind: 'http', message: typeof result.error === 'string' ? result.error : `HTTP ${r.status}`, http_status: r.status }; if (r.status !== 422 && r.status !== 400 && r.status !== 413) report.status = 'blocked'; }
          else { validateCustomResponse(result, request, report.model_identity); row.status = 'success'; }
        } catch (error) { row.status = 'error'; row.error = { kind: 'client_or_network', message: error.message }; report.status = 'blocked'; }
        row.elapsed_seconds = (Date.now() - started) / 1000; this.current = null; this.onChange(refreshReport(report));
        if (report.status === 'blocked') break;
      }
      if (report.status !== 'blocked') report.status = this.stopRequested && report.results.some(r => r.status === 'pending') ? 'interrupted' : 'completed';
      try { const h = await this.fetch('/api/health', { cache: 'no-store' }); if (h.ok) report.health_after = await h.json(); } catch { /* Unknown is preserved, never invent a ready device. */ }
      return report.status === 'completed';
    } catch (error) { report.status = 'blocked'; report.run_error = { kind: 'health_or_configuration', message: error.message }; throw error; }
    finally { this.current = null; this.busy = false; this.onChange(refreshReport(report)); }
  }
}
