import { escapeHTML as e } from './core.js';
import { icon } from './icons.js';
import { FIXED_THRESHOLDS, validateReliability, groupLabel, selectReliabilityGroup } from './reliability-core.js';

const pct = value => value === null || !Number.isFinite(value) ? 'nicht definiert' : `${(value * 100).toLocaleString('de-DE', { minimumFractionDigits: 1, maximumFractionDigits: 1 })} %`;
const dec = value => value === null || !Number.isFinite(value) ? 'nicht definiert' : value.toLocaleString('de-DE', { maximumFractionDigits: 6 });
const score = value => value.toFixed(2).replace('.', ',');
const fieldNames = { determination: 'Feststellung', action: 'Aktion', decision: 'Entscheidung', evidence: 'Beleg', intent: 'Anliegen', next_step: 'Nächster Schritt', priority: 'Priorität' };
const fieldName = field => fieldNames[field] ? `${fieldNames[field]} · ${field}` : field;
const option = (value, label, chosen) => `<option value="${e(value)}"${value === chosen ? ' selected' : ''}>${e(label)}</option>`;
const pairID = (data, row) => data.caseMap.get(JSON.stringify([row.suite_id, row.id]))?.metadata?.pair_id;
const shellHeader = `<nav class="analysis-nav" aria-label="Diagnostikansicht"><a href="#pairs">${icon('panels')}Minimalpaare</a><a href="#reliability" aria-current="page">${icon('chart')}Score & Fehler</a></nav><div class="reliability-heading"><div><h1 id="reliability-title">Score & Fehler</h1><p>Archivierte Ergebnisse · getrennt nach Feld und Gruppe</p></div></div>`;

/** Parent owns route visibility. Call hide() when leaving the view to invalidate pending renders. */
export function createReliabilityView({ document: doc = globalThis.document, window: win = globalThis.window, fetch: fetcher = globalThis.fetch } = {}) {
  const root = doc.getElementById('reliability');
  if (!root) throw new Error('Abschnitt #reliability fehlt');
  root.classList.add('reliability-view');
  root.setAttribute('aria-labelledby', 'reliability-title');
  let data = null, pending = null, generation = 0, active = false, params = {}, onlySelectedErrors = false;
  const $ = id => doc.getElementById(id);

  async function load() {
    if (data) return data;
    if (!pending) {
      pending = (async () => {
        const response = await fetcher('./data/reliability.json');
        if (!response.ok) throw new Error(`Ergebnisdatei nicht verfügbar (HTTP ${response.status ?? 'unbekannt'}).`);
        const payload = await response.json();
        data = validateReliability(payload);
        return data;
      })().finally(() => { pending = null; });
    }
    return pending;
  }

  function caveats(group, selected) {
    const notes = ['Kleine, abhängige Testsets. Meist KI-Referenzen ohne Fachvalidierung; keine repräsentative Produktionsstichprobe.', 'Hohe Scores und 0 beobachtete Fehler belegen weder Kalibrierung noch Sicherheit.'];
    if (group.suite_id === 'minimal_pairs48') {
      const allPairs = new Set(group.observations.map(r => pairID(data, r)).filter(Boolean));
      const bad = selected.filter(r => !r.correct), badPairs = new Set(bad.map(r => pairID(data, r)).filter(Boolean));
      notes.push(`${group.expected_count} Feldantworten${allPairs.size ? ` aus ${allPairs.size} abhängigen Paaren` : ' aus abhängigen Paaren'}; A und B sind nicht unabhängig.`);
      if (bad.length && badPairs.size) notes.push(`${bad.length} ausgewählte Feldfehler aus ${badPairs.size} ${badPairs.size === 1 ? 'Paar' : 'Paaren'}.`);
    }
    if (group.suite_id === 'clarification72') notes.push('Geteilte Regelfamilien; die Auswahl enthält Antworten, Rückfragen und unresolved.');
    if (['original_text180', 'finance100', 'clean72', 'attack_ablation14'].includes(group.suite_id)) notes.push('Verwandte Szenarien und Sprachkontrollen. Die Ablation nutzt sieben Finance-Szenarien erneut; keine unabhängige Replikation.');
    if (group.suite_id === 'insurance60') notes.push('60 Versicherungsfälle teilen zwölf Dokumentpakete. Belegoptionen b1–b5 sind falllokale Klauselmengen, keine stabilen semantischen Klassen.');
    if (group.suite_id === 'images90') {
      notes.push('Abhängige Bilder und Sprachkontrollen. 50 Quellbilder fehlen im Paket; nur archivierte Scores, ohne Pixelprüfung, neues Bild-Gold oder OCR.');
      if (group.partition.condition === 'blank') notes.push('Leerbild: Originalbild-Gold bleibt trotz fehlendem Inhalt bestehen. Abweichungen sind keine gewöhnlichen Fehler beantwortbarer Bildaufgaben.');
      if (group.partition.kind === 'chart') notes.push('Diagramme: bar_line/vbar2 haben überlappende Beschreibungen. Abweichungen können auf uneindeutige Annotationen zurückgehen.');
      if (group.partition.kind === 'invoice') notes.push('Rechnungen: Steuerlabel nach gedruckter Fußnote; Betragsklasse nach vorzeichenbehaftetem Gesamtbetrag.');
    }
    if (group.invalid_count || group.missing_count) notes.push(`${group.invalid_count} ungültig · ${group.missing_count} fehlend: im erwarteten Nenner, nicht in Risiko- oder Score-Metriken.`);
    return notes;
  }

  function errorCard(row, i) {
    const item = data.caseMap.get(JSON.stringify([row.suite_id, row.id]));
    const question = item.questions[row.field];
    const thresholdSelected = row.confidence >= params.threshold;
    return `<article class="reliability-error" data-reliability-error="${e(row.id)}"><div class="reliability-error-heading"><h3>${e(row.id)}</h3><span class="reliability-tag${thresholdSelected ? ' is-error' : ''}">${thresholdSelected ? 'Score ≥ Schwelle' : 'Score < Schwelle'}</span></div>
      <div class="reliability-error-values"><div><span>Gold</span><strong>${e(row.gold)}</strong></div><div><span>Modell</span><strong>${e(row.choice)}</strong></div><div><span>Nativer Score</span><strong>${pct(row.confidence)}</strong><small>${e(String(row.confidence))} ungerundet</small></div></div>
      ${pairID(data, row) ? `<p class="reliability-small">Abhängiges Paar: <a href="#pairs?pair=${e(encodeURIComponent(pairID(data, row)))}">${e(pairID(data, row))} · A/B vergleichen</a></p>` : ''}
      <details id="reliability-error-detail-${i}"><summary>Eingabe & ${row.option_keys.length} Optionscores</summary><div class="reliability-evidence">
        <p class="reliability-small">Unveränderte Referenz und native Modellantwort.</p>
        <dl class="reliability-probabilities">${row.option_keys.map(key => `<div><dt>${e(key)}${key === row.gold ? ' · Gold' : ''}${key === row.choice ? ' · Auswahl' : ''}<small>${e(question.criteria[key])}</small></dt><dd>${e(String(row.probabilities[key]))}</dd></div>`).join('')}</dl>
        <h4>Originaleingabe</h4><pre class="reliability-input">${e(typeof item.input === 'string' ? item.input : JSON.stringify(item.input, null, 2))}</pre>
        ${question.instructions ? `<h4>Feldanweisung</h4><p class="reliability-input">${e(question.instructions)}</p>` : ''}
        ${item.metadata.rationale ? `<h4>Referenzbegründung</h4><p>${e(item.metadata.rationale)}</p>` : ''}
      </div></details></article>`;
  }

  function renderErrors(group) {
    const all = group.observations.filter(r => r.status === 'valid' && !r.correct);
    const errors = onlySelectedErrors ? all.filter(r => r.confidence >= params.threshold) : all;
    $('reliability-error-count').textContent = `${errors.length} / ${all.length} Feldfehler`;
    $('reliability-errors-list').innerHTML = errors.map(errorCard).join('') || `<p class="reliability-empty">${onlySelectedErrors ? 'Keine Feldfehler in der Auswahl.' : 'Keine Feldfehler in dieser Gruppe.'}</p>`;
  }

  function render() {
    const focus = doc.activeElement?.id;
    const open = ['reliability-metrics', 'reliability-method'].filter(id => $(id)?.open);
    const group = data.field_groups.find(g => g.group_id === params.group);
    const suite = data.suites.find(s => s.id === params.suite);
    const suiteGroups = data.field_groups.filter(g => g.suite_id === params.suite);
    const fields = [...new Set(suiteGroups.map(g => g.field))];
    const candidates = suiteGroups.filter(g => g.field === params.field);
    const threshold = group.risk_coverage.find(r => r.threshold === params.threshold);
    const selected = group.observations.filter(r => r.status === 'valid' && r.confidence >= params.threshold);
    const selectedMean = selected.length ? selected.reduce((sum, r) => sum + r.confidence, 0) / selected.length : null;
    root.setAttribute('aria-busy', 'false');
    root.innerHTML = `${shellHeader}
      <p class="reliability-scope">${data.suites.length} Suiten · ${data.field_groups.length} Feldgruppen · einzeln ausgewertet</p>
      <div class="reliability-filters" role="group" aria-label="Getrennte Feldanalyse auswählen">
        <label for="reliability-suite">Suite<select id="reliability-suite">${data.suites.map(s => option(s.id, s.title, params.suite)).join('')}</select></label>
        <label for="reliability-field">Feld<select id="reliability-field">${fields.map(f => option(f, fieldName(f), params.field)).join('')}</select></label>
        <label for="reliability-group">Gruppe<select id="reliability-group">${candidates.map(g => option(g.group_id, groupLabel(g), params.group)).join('')}</select></label>
        <label for="reliability-threshold">Score-Schwelle<select id="reliability-threshold">${FIXED_THRESHOLDS.map(t => option(String(t), `Score ≥ ${score(t)}`, String(params.threshold))).join('')}</select></label>
      </div>
      <div class="reliability-selection"><div><h2>${e(suite.title)} <span>/ ${e(fieldName(group.field))}</span></h2><p>${e(groupLabel(group))}</p></div><span class="reliability-tag">${group.valid_count} / ${group.expected_count} gültige Feldantworten</span></div>
      <div id="reliability-selection-status" class="sr-only" role="status" aria-live="polite">${e(suite.title)}, ${e(group.field)}, Schwelle ${score(params.threshold)}. ${threshold.incorrect} von ${threshold.selected_count} ausgewählten Feldantworten falsch; Risiko ${pct(threshold.risk)}.</div>
      <div class="reliability-stats">
        <article class="reliability-stat reliability-risk"><span>Beobachtetes Fehlerrisiko</span><strong data-reliability-risk>${pct(threshold.risk)}</strong><p><b>${threshold.incorrect} / ${threshold.selected_count}</b> ausgewählte Feldantworten falsch</p>${threshold.selected_count ? '' : '<small>Keine Auswahl: 0/0 ist nicht definiert, kein 0-%-Risiko.</small>'}</article>
        <article class="reliability-stat"><span>Abdeckung</span><strong data-reliability-coverage>${pct(threshold.coverage)}</strong><p><b>${threshold.selected_count} / ${group.expected_count}</b> erwartete Feldantworten ausgewählt</p><small>${group.expected_count - threshold.selected_count} nicht ausgewählt · ${group.invalid_count} ungültig · ${group.missing_count} fehlend</small></article>
        <article class="reliability-stat"><span>Mittlerer nativer Score</span><strong data-reliability-confidence>${pct(selectedMean)}</strong><p><b>${threshold.correct} / ${threshold.selected_count}</b> ausgewählte Feldantworten richtig</p></article>
      </div>
      <aside class="reliability-caveats" aria-label="Grenzen dieser Gruppe"><h3>Grenzen</h3><ul>${caveats(group, selected).map(note => `<li>${e(note)}</li>`).join('')}</ul></aside>
      <div class="reliability-analysis-grid">
        <section class="reliability-card" aria-labelledby="reliability-threshold-title"><div class="reliability-card-heading"><div><h2 id="reliability-threshold-title">Schwellen</h2><p>Sechs feste Schwellen · dieselbe Feldgruppe</p></div></div>
          <div class="reliability-table-wrap" role="region" aria-label="Abdeckung und Fehler nach fester Schwelle" aria-describedby="reliability-scroll-hint" tabindex="0"><table class="reliability-table"><caption>Auswahl: nativer Score ≥ Schwelle. Abdeckung = Auswahl / ${group.expected_count} erwartet. Risiko = falsch / Auswahl.</caption><thead><tr><th scope="col">Schwelle</th><th scope="col">Auswahl / erwartet</th><th scope="col">Abdeckung</th><th scope="col">Falsch / Auswahl</th><th scope="col">Risiko</th></tr></thead><tbody>${group.risk_coverage.map(r => `<tr${r.threshold === params.threshold ? ' class="is-selected"' : ''}><th scope="row"><button type="button" data-reliability-threshold="${r.threshold}" aria-label="Feste Schwelle ${score(r.threshold)} auswählen" aria-pressed="${r.threshold === params.threshold}">≥ ${score(r.threshold)}</button></th><td>${r.selected_count} / ${r.expected_count}</td><td>${pct(r.coverage)}</td><td>${r.incorrect} / ${r.selected_count}</td><td>${pct(r.risk)}</td></tr>`).join('')}</tbody></table></div>
          <p id="reliability-scroll-hint" class="reliability-scroll-hint">Tabelle seitlich scrollen; per Tastatur fokussieren und Pfeiltasten nutzen.</p>
          <p class="reliability-small">Höhere Schwellen können die Auswahl leeren. Keine Empfehlung für den Produktionseinsatz.</p>
        </section>
        <section class="reliability-card" aria-labelledby="reliability-bin-title"><div class="reliability-card-heading"><div><h2 id="reliability-bin-title">Score-Verteilung</h2><p>Alle gültigen Feldantworten, ohne Schwellenfilter</p></div></div>
          <div class="reliability-bin-legend"><span><i class="is-score"></i>Mittlerer Score</span><span><i class="is-risk"></i>Fehleranteil</span></div>
          <div class="reliability-bins">${group.bins.map((b, i) => `<div class="reliability-bin${b.count ? '' : ' is-empty'}" data-reliability-bin="${i}"><div class="reliability-bin-label"><strong>${score(b.lower)}–${score(b.upper)}${b.upper_inclusive ? ' inkl.' : ''}</strong><span>${b.count - b.correct} / ${b.count} falsch</span></div>${b.count ? `<div class="reliability-bin-bars"><div><span class="sr-only">Mittlerer Score</span><span class="reliability-bar-track" aria-hidden="true"><i class="is-score" style="width:${b.mean_score * 100}%"></i></span><b>${pct(b.mean_score)}</b></div><div><span class="sr-only">Beobachtetes Fehlerrisiko</span><span class="reliability-bar-track" aria-hidden="true"><i class="is-risk" style="width:${(1 - b.accuracy) * 100}%"></i></span><b>${pct(1 - b.accuracy)}</b></div></div>` : '<span class="reliability-empty-bin">Leer · Score und Risiko nicht definiert</span>'}</div>`).join('')}</div>
          <p class="reliability-small">Kleine Gruppen sind instabil. Intervallgrenzen unter „Metriken & Definitionen“.</p>
        </section>
      </div>
      <details class="reliability-card reliability-details" id="reliability-metrics"><summary>Metriken & Definitionen</summary><div class="reliability-detail-body">
        <p>Nur <strong>${e(group.field)}</strong> in dieser Gruppe: <strong>${group.valid_count}</strong> gültige Feldantworten, <strong>${group.option_count}</strong> Optionen. Native ungerundete Vektoren, kein Fit und keine Rekalibrierung.</p>
        <p>Score-Bins: Untergrenze inklusive, Obergrenze exklusiv; der letzte Bin enthält 1. Leere Bins bleiben sichtbar.</p><dl class="reliability-metric-definitions"><div><dt>Brier · ${dec(group.brier_mean)}</dt><dd>Mittelwert der Summe über alle Optionen von (Optionswahrscheinlichkeit − Goldindikator)². Wertebereich 0–2; nicht durch die Optionsanzahl geteilt.</dd></div><div><dt>NLL · ${group.nll_is_infinite ? '∞' : dec(group.nll_mean)} nats</dt><dd>Mittelwert von −ln(Wahrscheinlichkeit der Goldoption). Natürlicher Logarithmus; bei Gold-Wahrscheinlichkeit 0 unendlich. ${group.zero_gold_probability_count} solche Beobachtungen; ${group.finite_nll_count} mit endlichem NLL.</dd></div><div><dt>ECE · ${dec(group.ece_10_equal_width)}</dt><dd>Zehn feste gleich breite Score-Bins: Summe aus Bin-Anteil × |mittlerer Score − beobachteter Richtig-Anteil|. Kleine oder abhängige Gruppen machen ECE instabil.</dd></div></dl>
        <p class="reliability-small">Optionsanzahl und Klassenmix unterscheiden sich. Kein Vergleich als bereinigte Rangliste über Suiten oder Felder. Belegoptionen bei Versicherungen sind falllokale Slots.</p>
        <p class="reliability-small">Optionen: ${group.option_keys.map(e).join(' · ')}<br>Gold-Klassenmix: ${Object.entries(group.gold_class_counts).map(([key, n]) => `${e(key)}: ${n}`).join(' · ')}</p>
      </div></details>
      <section class="reliability-card reliability-errors" aria-labelledby="reliability-errors-title"><div class="reliability-card-heading"><div><h2 id="reliability-errors-title">Fehler</h2><p id="reliability-error-count"></p></div></div><label class="reliability-check"><input id="reliability-selected-errors" type="checkbox"${onlySelectedErrors ? ' checked' : ''}>Nur Score ≥ ${score(params.threshold)}</label><div id="reliability-errors-list"></div></section>
      <details class="reliability-card reliability-details" id="reliability-method"><summary>Methode & Herkunft</summary><div class="reliability-detail-body"><p>Feste Schwellen, post-hoc beschrieben; keine optimierte Produktionsschwelle. Native Optionscores sind keine zugesicherten Korrektheitswahrscheinlichkeiten.</p><p>Zähler, Nenner und Vektoren werden auf Konsistenz geprüft, Kennzahlen aus gespeicherten Feldantworten neu berechnet. Keine neue Quellen- oder Goldvalidierung, keine unabhängigen Konfidenzintervalle.</p><p>Feldantworten, ganze Fälle und konkrete Antworten sind verschiedene Zielmengen. Ein Minimum mehrerer Feldscores ist eine Fallheuristik, keine gemeinsame Korrektheitswahrscheinlichkeit; diese Ansicht verwendet ausschließlich Feldschwellen.</p><ul>${data.caveats.map(c => `<li>${e(c)}</li>`).join('')}</ul><p><a href="./data/reliability.json" target="_blank" rel="noreferrer">${icon('document')}Ergebnisse als JSON</a></p><p class="reliability-small">Gruppen-ID: ${e(group.group_id)}<br>Suite: ${e(group.suite_id)} · Status: abgeschlossene archivierte Ergebnisse · Post-hoc deskriptiv</p></div></details>`;
    renderErrors(group);
    open.forEach(id => { if ($(id)) $(id).open = true; });
    if (focus && $(focus)) $(focus).focus({ preventScroll: true });
  }

  function update(next) {
    if (!data || !active) return;
    params = selectReliabilityGroup(data, { ...params, ...next });
    render();
    const query = new URLSearchParams({ suite: params.suite, field: params.field, group: params.group, threshold: params.threshold.toFixed(2) });
    // replaceState keeps filter changes local and avoids a second asynchronous route render.
    if (win?.history?.replaceState) win.history.replaceState(null, '', `#reliability?${query}`);
  }
  root.addEventListener('change', event => {
    const target = event.target;
    if (target.id === 'reliability-suite') update({ suite: target.value, field: undefined, group: undefined });
    if (target.id === 'reliability-field') update({ field: target.value, group: undefined });
    if (target.id === 'reliability-group') update({ group: target.value });
    if (target.id === 'reliability-threshold') update({ threshold: target.value });
    if (target.id === 'reliability-selected-errors' && active && data) {
      onlySelectedErrors = target.checked;
      renderErrors(data.field_groups.find(g => g.group_id === params.group));
    }
  });
  root.addEventListener('click', event => {
    const target = event.target.closest?.('[data-reliability-threshold], [data-reliability-retry]');
    if (!target || !root.contains(target)) return;
    if (target.hasAttribute('data-reliability-retry')) void show(params);
    else update({ threshold: target.dataset.reliabilityThreshold });
  });
  function hide() { active = false; generation++; }
  win?.addEventListener?.('hashchange', () => {
    if (active && win.location?.hash?.split('?')[0] !== '#reliability') hide();
  });
  async function show(routeParams = {}) {
    active = true;
    const ticket = ++generation;
    params = routeParams || {};
    if (!data) {
      root.setAttribute('aria-busy', 'true');
      root.innerHTML = `${shellHeader}<div class="reliability-loading" role="status">Ergebnisse laden und prüfen …</div>`;
    }
    try {
      await load();
      if (!active || ticket !== generation) return false;
      params = selectReliabilityGroup(data, routeParams);
      render();
      return true;
    } catch (error) {
      if (!active || ticket !== generation) return false;
      root.setAttribute('aria-busy', 'false');
      root.innerHTML = `${shellHeader}<div class="reliability-load-error" role="alert"><h2>Ergebnisse nicht geladen</h2><p>${e(error.message || 'Unbekannter Ladefehler')}</p><p>Lokale Ergebnisdatei prüfen oder erneut versuchen.</p><button type="button" class="button" data-reliability-retry>${icon('refresh')}Erneut versuchen</button></div>`;
      return false;
    }
  }
  return { show, hide };
}
