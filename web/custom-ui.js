import { escapeHTML as e, percent, decimal, runtimeLabel } from './core.js';
import { CUSTOM_LIMITS, PRESETS, CustomEvaluator, importSuite, parseBoundedJSON, validateSpec, validateSuite, newReport, scoreSuite, resultsCSV, exampleSuite, csvCell, exportSnapshot } from './custom-cases.js';

/** A separate private workspace: never registers user inputs as a trusted public suite. */
export function createCustomWorkspace({ document: doc, window: win, fetch: fetcher, isBusy = () => false, onBusy = () => {}, getHealth = () => null }) {
  const $ = id => doc.getElementById(id);
  let suite = null, report = null, preview = null, selected = null, dirty = false, loading = false, importGeneration = 0, pendingAction = null;
  const evaluator = new CustomEvaluator({ fetch: fetcher, isBusy, onChange: () => { render(); onBusy(evaluator.busy); } });
  const busy = () => evaluator.busy || isBusy() || loading;
  const selectedCase = () => suite?.cases.find(c => c.id === selected);
  function message(text, error = false) { $('custom-message').textContent = text; $('custom-message').classList.toggle('error', error); $('custom-message').setAttribute('role', error ? 'alert' : 'status'); }
  function errorMessage(error) { const errors = error.errors || [error.message]; $('custom-import-message').textContent = errors.join('\n'); $('custom-import-message').classList.add('error'); }
  function download(value, name, type = 'application/json') {
    const blob = new Blob([type === 'application/json' ? JSON.stringify(value, null, 2) : value], { type });
    const url = win.URL.createObjectURL(blob), a = doc.createElement('a'); a.href = url; a.download = name; a.click(); win.setTimeout(() => win.URL.revokeObjectURL(url), 1000);
  }
  function origin() {
    try { const u = new URL(win.location.href); return u.protocol === 'http:' && ['localhost', '127.0.0.1', '[::1]'].includes(u.hostname) ? u.origin : null; } catch { return null; }
  }
  function fillEditor() {
    const c = selectedCase(); $('custom-editor').hidden = !c;
    if (!c) return;
    $('custom-case-id').textContent = c.id;
    $('custom-state').value = c.state; $('custom-questions').value = JSON.stringify(c.questions, null, 2); $('custom-gold').value = JSON.stringify(c.gold || {}, null, 2);
    dirty = false;
  }
  function renderResult() {
    const c = selectedCase(), r = report?.results.find(r => r.id === selected);
    if (!c) { $('custom-case-result').innerHTML = ''; return; }
    if (dirty) { $('custom-case-result').textContent = 'Eingabe geändert. Vorherige Ergebnisse wurden verworfen. Erst Änderungen übernehmen oder verwerfen.'; return; }
    if (!r || r.status === 'pending') { $('custom-case-result').textContent = evaluator.current === c.id ? 'Dieser Fall wird gerade lokal berechnet. Der aktuelle Request kann nach Stop weiterlaufen.' : 'Keine Modellantwort für diesen Fall. Goldlabels sind vom Nutzer bereitgestellt.'; return; }
    if (r.status === 'error') { $('custom-case-result').innerHTML = `<div class="notice danger"><strong>Keine gültige Modellantwort</strong><br>${e(r.error?.message || 'Unbekannter Fehler')}<br>Beschriftete Felder bleiben im Nenner. Es wird keine Vorhersage erfunden.</div>`; return; }
    $('custom-case-result').innerHTML = Object.entries(c.questions).map(([id, q]) => {
      const a = r.response.answers[id], gold = c.gold?.[id], probs = r.response.probabilities_unrounded[id];
      return `<article class="custom-answer" data-custom-answer="${e(id)}"><div class="output-field-head"><strong>${e(id)}</strong><span class="status-chip ${gold === undefined ? 'unscored' : a.choice === gold ? 'correct' : 'wrong'}">${gold === undefined ? 'Ohne Gold' : a.choice === gold ? 'Richtig' : 'Falsch'}</span></div><div class="custom-answer-comparison"><div><span>Modellantwort</span><strong>${e(a.choice)}</strong></div><div><span>Nutzer-Gold</span><strong>${gold === undefined ? 'Nicht vorhanden' : e(gold)}</strong></div></div><p>${e(q.criteria[a.choice])}</p>${gold === undefined ? '<p class="input-help">Ohne Sollreferenz wird keine Richtigkeit behauptet.</p>' : ''}<details><summary>Alle Modellwahrscheinlichkeiten</summary>${Object.entries(probs).map(([k, v]) => `<div class="custom-probability ${k === a.choice ? 'chosen' : ''}" style="--probability:${Math.min(100, Math.max(0, v * 100))}%"><span>${e(k)}${k === a.choice ? ' · Modell' : ''}${k === gold ? ' · Gold' : ''}</span><span>${percent(v, 2)}</span></div>`).join('')}</details></article>`;
    }).join('') + `<p class="input-help">${e(r.response.model)} · Revision ${e(r.response.revision)}<br>${e(runtimeLabel(r.response.runtime))}<br>${decimal(r.response.latency_ms / 1000)} s Forward · ${decimal(r.elapsed_seconds)} s Request · ${r.response.input_tokens} Tokens<br>Privater lokaler Lauf. Nicht unabhängig geprüft; keine veröffentlichte Benchmark-Messung.</p>`;
  }
  function dismissConfirmation() {
    pendingAction = null; $('custom-confirm').hidden = true;
    for (const id of ['custom-confirm-title', 'custom-confirm-copy', 'custom-confirm-action']) $(id).textContent = '';
  }
  function confirmChange(action) {
    pendingAction = action; $('custom-confirm').hidden = false;
    $('custom-confirm-title').textContent = action === 'replace' ? 'Geladene Suite wirklich ersetzen?' : 'Private Suite aus diesem Tab entfernen?';
    $('custom-confirm-copy').textContent = 'Die vorhandenen Texte, Goldlabels, Editoränderungen und bisherigen Resultate gehen in diesem Tab verloren. Exportierte Dateien auf deinem Gerät bleiben erhalten. Du kannst die Suite jetzt noch behalten und zuerst exportieren.';
    $('custom-confirm-action').textContent = action === 'replace' ? 'Suite ersetzen' : 'Suite entfernen';
    $('custom-confirm-cancel').focus({ preventScroll: true });
    $('custom-confirm').scrollIntoView?.({ block: 'nearest', behavior: 'auto' });
  }
  function clearSuite() {
    if (busy()) return;
    dismissConfirmation(); importGeneration++; suite = report = preview = null; selected = null; dirty = false;
    for (const id of ['custom-file', 'custom-spec-file', 'custom-search']) $(id).value = '';
    $('custom-filter').value = 'all'; $('custom-import-message').textContent = ''; $('custom-import-message').classList.remove('error');
    $('custom-import-box').open = true;
    message('Private Suite aus diesem Tab entfernt. Bereits exportierte Dateien bleiben auf deinem Gerät.'); render();
    $('custom-file').focus({ preventScroll: true });
  }
  function render() {
    const locked = busy(), editorCase = selectedCase();
    if (!locked && !dirty && editorCase && ($('custom-state').value !== editorCase.state || $('custom-questions').value !== JSON.stringify(editorCase.questions, null, 2) || $('custom-gold').value !== JSON.stringify(editorCase.gold || {}, null, 2))) {
      dirty = true; report = null;
      message('Editorinhalt hat sich geändert. Vorherige Ergebnisse wurden verworfen; bitte Änderungen validieren.', true);
    }
    const s = suite ? scoreSuite(suite, report?.results) : null;
    for (const id of ['custom-file', 'custom-format', 'custom-preset', 'custom-spec-file', 'custom-parse', 'custom-example', 'custom-clear']) $(id).disabled = locked;
    $('custom-accept').disabled = locked || !preview;
    $('custom-run').disabled = locked || !suite || dirty || !origin() || (getHealth() !== null && (getHealth().inference_enabled !== true || getHealth().busy === true));
    $('custom-confirm-action').disabled = locked;
    $('custom-confirm-cancel').disabled = locked;
    for (const id of ['custom-search', 'custom-filter']) $(id).disabled = locked;
    $('custom-editor-state').textContent = dirty ? 'Änderungen noch nicht übernommen' : 'Nur dieser Tab';
    $('custom-editor-state').classList.toggle('dirty', dirty);
    $('custom-editor').setAttribute('aria-busy', String(locked));
    const currentStep = !suite ? 'import' : evaluator.busy || report?.status === 'interrupted' || report?.status === 'blocked' ? 'run' : report?.status === 'completed' ? 'export' : 'edit';
    doc.querySelectorAll('[data-custom-step]').forEach(el => { if (el.dataset.customStep === currentStep) el.setAttribute('aria-current', 'step'); else el.removeAttribute('aria-current'); });
    $('custom-cancel').disabled = !evaluator.busy || evaluator.stopRequested;
    $('custom-export-suite').disabled = locked || !suite || dirty;
    $('custom-export-json').disabled = !report || loading || dirty;
    $('custom-export-csv').disabled = !report || loading || dirty;
    for (const id of ['custom-state', 'custom-questions', 'custom-gold', 'custom-apply', 'custom-discard']) $(id).disabled = locked;
    $('custom-list').querySelectorAll('button').forEach(b => { b.disabled = locked; });
    $('custom-workspace').hidden = !suite;
    $('custom-empty').hidden = !!suite;
    $('custom-preview').hidden = !preview;
    if (!preview) { $('custom-preview-copy').textContent = ''; $('custom-preview-list').replaceChildren(); }
    $('custom-import-fields').hidden = $('custom-format').value !== 'csv' && !$('custom-file').files?.[0]?.name?.toLowerCase().endsWith('.csv');
    $('custom-stop-note').hidden = !evaluator.busy;
    $('custom-run').textContent = report?.results.some(r => r.status === 'pending') && report?.status !== 'validated' ? 'Verbleibende Fälle fortsetzen' : report?.status === 'completed' ? 'Neue Auswertung starten' : 'Suite lokal auswerten';
    $('custom-cancel').textContent = evaluator.stopRequested ? 'Stop vorgemerkt' : 'Nach diesem Fall stoppen';
    if (!suite) {
      for (const id of ['custom-state', 'custom-questions', 'custom-gold']) $(id).value = '';
      for (const id of ['custom-suite-title', 'custom-case-id', 'custom-list', 'custom-case-result', 'custom-metrics', 'custom-field-scores', 'custom-runtime', 'custom-progress-text', 'custom-score-note', 'custom-list-count']) $(id).replaceChildren();
      $('custom-editor').hidden = true;
      $('custom-progress').value = 0; $('custom-progress').max = 1;
      return;
    }
    $('custom-suite-title').textContent = suite.name;
    const query = $('custom-search').value.trim().toLocaleLowerCase('de'), filter = $('custom-filter').value;
    const rows = suite.cases.filter(c => {
      const r = report?.results.find(r => r.id === c.id);
      if (query && !`${c.id} ${c.state}`.toLocaleLowerCase('de').includes(query)) return false;
      if (filter === 'error') return r?.status === 'error';
      if (filter === 'pending') return !r || r.status === 'pending';
      if (filter === 'unlabelled') return Object.keys(c.gold || {}).length < Object.keys(c.questions).length;
      if (filter === 'wrong') return r?.status === 'success' && Object.entries(c.gold || {}).some(([id, gold]) => r.response.answers[id].choice !== gold);
      return true;
    });
    $('custom-list-count').textContent = `${rows.length} / ${suite.cases.length}`;
    $('custom-list').innerHTML = rows.map(c => {
      const r = report?.results.find(r => r.id === c.id), running = evaluator.current === c.id,
        wrong = r?.status === 'success' && Object.entries(c.gold || {}).some(([id, gold]) => r.response.answers[id].choice !== gold),
        status = running ? 'läuft' : r?.status === 'error' ? 'Fehler' : wrong ? 'Abweichung' : r?.status === 'success' ? 'Antwort da' : 'offen';
      return `<button class="custom-case-row ${c.id === selected ? 'selected' : ''}" data-status="${running ? 'running' : wrong ? 'wrong' : r?.status || 'pending'}" data-custom-case="${e(c.id)}" aria-pressed="${c.id === selected}" ${locked ? 'disabled' : ''}><span><strong>${e(c.id)}</strong><small>${e(c.state.slice(0, 115))}${c.state.length > 115 ? '…' : ''}</small></span><span class="badge">${e(status)}</span></button>`;
    }).join('') || '<div class="custom-list-empty">Keine passenden Fälle.<button type="button" class="quiet-button" data-custom-reset>Suche &amp; Filter zurücksetzen</button></div>';
    const total = s.cases_total, terminal = s.cases_succeeded + s.cases_failed;
    $('custom-progress').max = total; $('custom-progress').value = terminal;
    const statusText = evaluator.busy ? evaluator.stopRequested ? 'Stop vorgemerkt; aktueller Request darf fertig werden' : evaluator.current ? `Lokale Inferenz: ${evaluator.current}` : 'Lokales Backend wird geprüft' : report?.status === 'completed' ? s.cases_failed ? 'Lauf beendet, mit Fehlern' : 'Lauf beendet' : report?.status === 'interrupted' ? 'Gestoppt, Teillauf' : report?.status === 'blocked' ? 'Blockiert, Teillauf' : 'Bereit, noch nicht ausgeführt';
    $('custom-runtime').textContent = report?.model_identity ? `Für diesen Lauf festgehalten: ${report.model_identity.model} · ${report.model_identity.model_key} · ${report.model_identity.requested_profile} · Revision ${report.model_identity.revision}. Kein automatischer Modellwechsel.` : 'Modell und Profil werden vom lokalen Server bestimmt und vor dem Start festgehalten. Standard: Clef Flash 9B, CPU-NF4. 27B ist ein separater, expliziter Serverstart; nicht hier auf dieser Hardware geprüft.';
    $('custom-progress-text').textContent = `${statusText} · ${terminal}/${total} bearbeitet · ${s.cases_succeeded} Antworten · ${s.cases_failed} Fehler · ${s.cases_pending} offen`;
    $('custom-metrics').innerHTML = [
      ['Goldabdeckung', `${s.labelled_fields}/${s.fields_total}`, `${s.unlabelled_fields} Felder ohne Sollantwort`],
      ['Beschriftete Felder richtig', report ? `${s.correct_labelled_fields}/${s.labelled_fields}` : '—', report ? `${percent(s.field_accuracy)} · ${s.evaluated_labelled_fields}/${s.labelled_fields} mit gültiger Antwort` : 'Noch keine Auswertung gestartet'],
      ['Vollständige Fälle richtig', report ? `${s.correct_fully_labelled_cases}/${s.fully_labelled_cases}` : '—', report ? `${percent(s.case_accuracy)} · nur komplett beschriftete Fälle` : `${s.fully_labelled_cases} vollständig beschriftete Fälle`],
      ['Ausführung abgeschlossen', `${terminal}/${total}`, `${percent(terminal / total)} · Antwortabdeckung ${percent(s.cases_succeeded / total)}`],
    ].map(([label, value, note]) => `<div class="custom-metric"><span>${label}</span><strong>${value}</strong><small>${note}</small></div>`).join('');
    $('custom-score-note').textContent = `${report?.status === 'completed' ? 'Eigene Auswertung' : 'Vorläufiger Stand, kein Endergebnis'}. Gold kommt vom Nutzer und wird nie ergänzt. Fehlende oder fehlgeschlagene Antworten zählen bei beschrifteten Feldern nicht als richtig und bleiben im Nenner. Unbeschriftete Felder erhalten keinen Qualitätsscore.`;
    $('custom-field-scores').innerHTML = Object.entries(s.by_field).map(([id, f]) => `<div class="custom-probability"><strong>${e(id)}</strong><span>${report ? `${f.correct}/${f.labelled} richtig · ${percent(f.accuracy)} · ${f.evaluated}/${f.labelled} beantwortet` : `${f.labelled} Goldlabels · noch nicht ausgewertet`}</span></div>`).join('');
    renderResult();
  }
  async function importText(text, options) {
    if (busy()) return false;
    dismissConfirmation(); preview = null; $('custom-import-box').open = true; $('custom-import-message').classList.remove('error');
    try {
      preview = importSuite(text, options);
      const s = scoreSuite(preview);
      $('custom-preview-copy').textContent = `${preview.name}: ${s.cases_total} gültige Fälle · ${s.fields_total} Felder · ${s.labelled_fields} Goldlabels · ${s.fully_labelled_cases} vollständig beschriftete Fälle. Noch nichts an das Modell gesendet.`;
      $('custom-import-message').textContent = 'Validierung bestanden. Alle Zeilen werden übernommen. Prüfe die Vorschau und übernimm die Suite ausdrücklich.';
      $('custom-preview-list').innerHTML = preview.cases.map(c => `<li><strong>${e(c.id)}</strong> · ${e(c.state.slice(0, 180))}${c.state.length > 180 ? '… (vollständiger Text im Editor)' : ''} · ${Object.keys(c.gold || {}).length}/${Object.keys(c.questions).length} Goldlabels</li>`).join('');
      render(); return true;
    } catch (error) { errorMessage(error); render(); return false; }
  }
  async function readFile(file) {
    if (!file) throw Error('Bitte eine lokale Datei auswählen.');
    if (file.size > CUSTOM_LIMITS.bytes) throw Error('Datei ist größer als 5 MiB. Es wurde nichts eingelesen.');
    const bytes = new Uint8Array(await file.arrayBuffer());
    return new TextDecoder('utf-8', { fatal: true, ignoreBOM: true }).decode(bytes);
  }
  async function parseFile() {
    if (busy()) return false;
    dismissConfirmation();
    const generation = ++importGeneration; preview = null;
    try {
      const file = $('custom-file').files?.[0], format = $('custom-format').value === 'auto' ? file?.name.toLowerCase().split('.').at(-1) : $('custom-format').value;
      if (!['json', 'jsonl', 'csv'].includes(format)) throw Error('Bitte JSON, JSONL oder CSV wählen. ZIP, PDF und Bilder werden nicht eingelesen.');
      loading = true; render();
      const text = await readFile(file);
      let spec = null;
      if (format === 'csv') {
        if ($('custom-preset').value === 'file') spec = validateSpec(parseBoundedJSON(await readFile($('custom-spec-file').files?.[0])));
        else spec = PRESETS[$('custom-preset').value];
      }
      if (generation !== importGeneration) return false;
      loading = false;
      return await importText(text, { format, name: file.name.replace(/\.[^.]+$/, ''), spec });
    } catch (error) { errorMessage(error); return false; }
    finally { loading = false; render(); }
  }
  async function acceptPreview(confirmed = false) {
    if (busy() || !preview) return false;
    if (suite && !confirmed) { confirmChange('replace'); return false; }
    dismissConfirmation();
    suite = structuredClone(preview); preview = null; report = null; $('custom-file').value = ''; $('custom-spec-file').value = ''; selected = suite.cases[0].id; fillEditor();
    $('custom-import-box').open = false; $('custom-search').value = ''; $('custom-filter').value = 'all';
    message('Private Suite im Arbeitsspeicher dieses Tabs. Zum Aufbewahren ausdrücklich exportieren; beim Neuladen geht sie verloren.'); render(); $('custom-suite-title').focus({ preventScroll: true }); return true;
  }
  function edit() {
    if (busy()) return;
    dismissConfirmation(); dirty = true; report = null; message('Eingabe geändert. Alle bisherigen Resultate wurden entfernt, damit nichts einer bearbeiteten Suite zugeordnet wird.'); render();
  }
  function applyEdit() {
    if (busy() || !suite) return false;
    try {
      const next = structuredClone(suite), c = next.cases.find(c => c.id === selected);
      c.state = $('custom-state').value; c.questions = parseBoundedJSON($('custom-questions').value);
      const gold = parseBoundedJSON($('custom-gold').value || '{}'); c.gold = gold;
      suite = validateSuite(next); report = null; dirty = false; fillEditor(); message('Änderungen validiert und übernommen. Für diese Suite sind neue Modellanfragen nötig.'); render(); return true;
    } catch (error) { message(error.message, true); return false; }
  }
  async function start() {
    if (busy() || !suite || dirty) return false;
    if (!origin()) { message('Echte Inferenz ist hier nur über den lokalen Server auf http://127.0.0.1:8765 verfügbar.', true); return false; }
    dismissConfirmation(); loading = true; render(); onBusy(true);
    try {
      if (!report || !report.results.some(r => r.status === 'pending')) report = await newReport(suite, origin());
      loading = false;
      message('Eine Anfrage nach der anderen. Goldlabels bleiben im Browser; der lokale Server erhält nur state und questions.');
      return await evaluator.run(report);
    } catch (error) { message(error.message, true); return false; }
    finally { loading = false; render(); onBusy(false); }
  }
  $('custom-parse').addEventListener('click', parseFile);
  $('custom-accept').addEventListener('click', () => acceptPreview());
  $('custom-example').addEventListener('click', () => importText(JSON.stringify(exampleSuite()), { format: 'json' }));
  for (const id of ['custom-file', 'custom-format', 'custom-preset', 'custom-spec-file']) $(id).addEventListener('change', () => { if (!busy()) { dismissConfirmation(); preview = null; $('custom-import-message').textContent = 'Auswahl geändert. Bitte Datei erneut prüfen.'; render(); } });
  for (const id of ['custom-state', 'custom-questions', 'custom-gold']) $(id).addEventListener('input', edit);
  $('custom-apply').addEventListener('click', applyEdit);
  $('custom-discard').addEventListener('click', () => { if (!busy()) { fillEditor(); message('Editor auf die übernommene Suite zurückgesetzt. Alte Ergebnisse bleiben verworfen.'); render(); } });
  $('custom-run').addEventListener('click', start);
  $('custom-cancel').addEventListener('click', () => evaluator.cancel());
  $('custom-list').addEventListener('click', event => { const button = event.target.closest('[data-custom-case]'); if (!button || busy()) return; if (dirty) { message('Bitte Editoränderungen erst übernehmen oder verwerfen.', true); return; } selected = button.dataset.customCase; fillEditor(); render(); $('custom-list').querySelector(`[data-custom-case="${selected}"]`)?.focus({ preventScroll: true }); if (win.matchMedia?.('(max-width: 720px)').matches) $('custom-editor').scrollIntoView?.({ block: 'start', behavior: 'auto' }); });
  $('custom-list').addEventListener('keydown', event => {
    if (!['ArrowDown', 'ArrowUp', 'Home', 'End'].includes(event.key) || busy() || dirty || !event.target.closest('[data-custom-case]')) return;
    const buttons = [...$('custom-list').querySelectorAll('[data-custom-case]')], index = buttons.indexOf(event.target.closest('[data-custom-case]'));
    const target = event.key === 'Home' ? buttons[0] : event.key === 'End' ? buttons.at(-1) : buttons[index + (event.key === 'ArrowDown' ? 1 : -1)];
    if (!target) return;
    event.preventDefault(); selected = target.dataset.customCase; fillEditor(); render();
    $('custom-list').querySelector(`[data-custom-case="${selected}"]`)?.focus({ preventScroll: true });
  });
  $('custom-clear').addEventListener('click', () => { if (!busy() && suite) confirmChange('clear'); });
  $('custom-confirm-cancel').addEventListener('click', () => { if (busy()) return; const action = pendingAction; dismissConfirmation(); $(action === 'replace' ? 'custom-accept' : 'custom-clear').focus({ preventScroll: true }); });
  $('custom-confirm-action').addEventListener('click', () => { if (busy()) return; if (pendingAction === 'replace') acceptPreview(true); else if (pendingAction === 'clear') clearSuite(); });
  doc.addEventListener('keydown', event => { if (event.key === 'Escape' && pendingAction && !busy()) $('custom-confirm-cancel').click(); });
  for (const [id, event] of [['custom-search', 'input'], ['custom-filter', 'change']]) $(id).addEventListener(event, () => { if (!busy()) render(); });
  $('custom-list').addEventListener('click', event => { if (event.target.closest('[data-custom-reset]') && !busy()) { $('custom-search').value = ''; $('custom-filter').value = 'all'; render(); $('custom-search').focus(); } });
  $('custom-export-suite').addEventListener('click', () => { if (suite && !dirty && !busy()) download(suite, 'clef-private-suite.json'); });
  $('custom-export-json').addEventListener('click', () => { if (report && !dirty) download(exportSnapshot(report, evaluator.current), 'clef-private-run.json'); });
  $('custom-export-csv').addEventListener('click', () => { if (report && !dirty) download(resultsCSV(exportSnapshot(report, evaluator.current)), 'clef-private-results.csv', 'text/csv;charset=utf-8'); });
  $('custom-template-json').addEventListener('click', () => download(exampleSuite(), 'clef-custom-example.json'));
  $('custom-template-jsonl').addEventListener('click', () => download(exampleSuite().cases.map(c => JSON.stringify(c)).join('\n') + '\n', 'clef-custom-example.jsonl', 'application/x-ndjson'));
  $('custom-template-csv').addEventListener('click', () => { const rows = [['id', 'state', 'gold.intent', 'gold.priority'], ...exampleSuite().cases.map(c => [c.id, c.state, c.gold?.intent || '', c.gold?.priority || ''])]; download('\uFEFF' + rows.map(r => r.map(csvCell).join(',')).join('\r\n') + '\r\n', 'clef-custom-example.csv', 'text/csv;charset=utf-8'); });
  $('custom-template-spec').addEventListener('click', () => download(PRESETS.support, 'clef-custom-spec.json'));
  win.addEventListener('beforeunload', event => { if ((suite || evaluator.busy) && event?.preventDefault) { event.preventDefault(); event.returnValue = ''; } });
  render();
  return { importText, acceptPreview, applyEdit, start, cancel: () => evaluator.cancel(), refresh: render, isBusy: () => evaluator.busy || loading, getState: () => ({ suite: structuredClone(suite), report: structuredClone(report), preview: structuredClone(preview), selected, dirty, busy: busy() }) };
}
