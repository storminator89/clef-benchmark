import { escapeHTML as e, decimal, fieldLabel, choiceLabel } from './core.js';
import { icon } from './icons.js';
import { validateStudyIndex, validateStudyData, filterStudyCases } from './studies-core.js';
export function createStudiesView({document:doc=globalThis.document,window:win=globalThis.window,fetch:fetcher=globalThis.fetch}={}) {
  const root=doc.getElementById('studies');
  let index=null,indexPending=null,visible=false,generation=0,selected=null,current=null,displayLimit=100;
  const cached=new Map();
  const filters={query:'',outcome:'all',group:'all'};
  const $=id=>root.querySelector(`#${id}`);
  const reset=()=>{filters.query='';filters.outcome='all';filters.group='all';displayLimit=100;};
  const details=(title,body)=>`<details class="study-details"><summary>${e(title)}</summary>${body}</details>`;
  const json=(title,value)=>details(title,`<pre>${e(typeof value==='string'?value:JSON.stringify(value,null,2))}</pre>`);
  const route=()=>{try {win.history.replaceState(null,'',`#studies?study=${encodeURIComponent(selected)}`);} catch { /* Read-only view works without history writes. */ }};
  function shell() {
    root.innerHTML=`<div class="view-heading"><div><div class="eyebrow">GETRENNTE EXPERIMENTE</div><h1>Weitere Tests</h1><p class="section-intro">Sprachvarianten, Absichten und Gesprächskontext.</p></div></div><div class="study-cards" id="study-cards" aria-label="Experiment auswählen"></div><div id="study-content" aria-live="polite"></div>`;
    $('study-cards').innerHTML=index.studies.map(s=>`<button type="button" class="study-card" data-study="${e(s.id)}" aria-pressed="${s.id===selected}"><span class="study-card-top">${icon(s.status==='completed'?'check':'clock')}<span>${s.status==='completed'?'Geprüfter Lauf':s.status==='cancelled'?'Beendet / abgesagt':'Ergebnis ausstehend'}</span></span><strong>${e(s.label)}</strong><span>${e(s.subtitle)}</span><small>${s.status!=='completed'?'Ursprünglich geplant: ':''}${s.planned_requests} ${e(s.unit)} · eigener Nenner</small></button>`).join('');
  }
  function methods(entry,data) {
    const notes=[...entry.methods,...(data?.limitations||[]),...(data?.directional_note?[data.directional_note]:[])];
    return details('Methodik & Grenzen',`<ul>${notes.map(n=>`<li>${e(n)}</li>`).join('')}</ul>${data?.secondary_metrics?.length?`<ul>${data.secondary_metrics.map(m=>`<li>${e(m.label)}: ${m.numerator} / ${m.denominator} ${e(m.unit)}${m.note?` · ${e(m.note)}`:''}</li>`).join('')}</ul>`:''}${data?`<p>Unabhängige KI-Prüfung; kein Ersatz für menschliche Fachexpertise. Quellenmanifest: <code>${e(data.audit.source_manifest_sha256)}</code></p>`:''}`);
  }
  function comparisons(data) {
    if(!data?.comparisons?.length)return '';
    const table=rows=>`<div class="study-comparison-scroll" tabindex="0" aria-label="Modellvergleich"><table class="study-comparison"><thead><tr><th>Teilgruppe</th><th>Clef richtig</th><th>Jev richtig</th></tr></thead><tbody>${rows.map(r=>`<tr><th>${e(r.label)}</th><td>${r.baseline_ready?`${r.clef_correct} / ${r.expected}`:'nicht verfügbar'}</td><td>${r.jev_correct} / ${r.expected}${!r.baseline_ready?'<small>Einzelmodell, kein Paarvergleich</small>':''}</td></tr>`).join('')}</tbody></table></div>`;
    const primary=data.comparisons.filter(r=>r.primary);
    return `<section class="study-panel"><h2>Direkter Vergleich</h2><p class="study-comparison-note">Je Testgruppe dieselben geplanten Fälle für beide Modelle. Alle geforderten Felder müssen richtig sein.</p>${table(primary)}<p>Bei Jev fehlt im Bank- und Finanztest jeweils eine auswertbare Antwort. Sie zählen nicht als richtig; eine fachliche Fehlentscheidung ist damit nicht belegt.</p>${details(`Alle ${data.comparisons.length} Teilgruppen`,table(data.comparisons))}</section>`;
  }

  function renderHeader(entry,data) {
    const metrics=data?`<div class="study-metrics">${data.metrics.map(m=>`<article><span>${e(m.label)}</span><strong>${m.kind==='ratio'?`${m.numerator} / ${m.denominator}`:decimal(m.value,4)}</strong><small>${e(m.kind==='ratio'?m.unit:m.note)}</small>${m.kind==='ratio'&&m.note?`<p>${e(m.note)}</p>`:''}</article>`).join('')}</div>`:'';
    $('study-content').innerHTML=`<section class="study-panel"><div class="study-section-title"><h2>${e(entry.label)}</h2><span class="study-state">${icon(data?'check':'clock')}${data?'Vollständig geprüft':entry.status==='cancelled'?'Auf Nutzerwunsch beendet':'Noch keine vollständigen Ergebnisse'}</span></div>${metrics}${data?.findings?.length?`<p class="study-finding">${icon('search')}${e(data.findings.join(' '))}</p>`:''}${!data?`<div class="study-pending">${icon('clock')}<div><strong>Keine Messwerte freigegeben</strong><p>${e(entry.note)}</p></div></div>`:''}${methods(entry,data)}</section>${comparisons(data)}${data?`<section class="study-panel"><div class="study-section-title"><h2>Fälle prüfen</h2><span id="study-case-count" role="status"></span></div><div class="study-filters"><label>Darstellung<select id="study-group"><option value="all">Alle Gruppen</option>${[...new Set(data.cases.map(c=>c.group).filter(Boolean))].map(g=>`<option value="${e(g)}">${e(data.group_labels?.[g]||g)}</option>`).join('')}</select></label><label>Ergebnis<select id="study-outcome"><option value="all">Alle Fälle</option><option value="errors">Falsche Antworten</option><option value="correct">Vollständig richtig</option><option value="technical">Keine auswertbare Antwort</option></select></label><label class="study-search">Suche<input id="study-search" type="search" placeholder="Fall, Eingabe oder Sollantwort …"></label><button type="button" class="quiet-button" data-study-reset>Zurücksetzen</button></div><div id="study-cases"></div></section>`:''}`;
    if(data) renderCases();
  }
  function renderCases() {
    if(!current)return;
    const rows=filterStudyCases(current.cases,filters);
    $('study-case-count').textContent=`${rows.length} / ${current.cases.length} Anfragen`;
    $('study-cases').innerHTML=rows.length?rows.slice(0,displayLimit).map(row=>{
      const label=!row.valid?'Nicht auswertbar':row.correct?'Richtig':'Fehler';
      const fields=Object.keys(row.expected).map(field=>`<div class="study-field"><strong>${e(fieldLabel(field))}</strong><span><small>Soll</small>${e(choiceLabel(field,row.expected[field],row.questions[field].criteria))}</span><span><small>${e(current.model_label||'Clef')}</small>${row.valid?e(choiceLabel(field,row.prediction[field],row.questions[field].criteria)):'—'}</span></div>`).join('');
      return `<details class="study-case" data-study-case="${e(row.id)}"><summary><span class="study-outcome ${!row.valid?'unavailable':row.correct?'good':'bad'}">${icon(row.correct?'check':'x')}${label}</span><strong>${e(row.id)}</strong><span>${e(current.group_labels?.[row.group]||row.group||'')}${row.pair_id?` · ${e(row.pair_id)}`:''}</span></summary>${fields}${!row.valid?`<p>${e(row.technical_note)}</p>`:''}${json('Vollständige Eingabe',row.input)}${json('Fragen & Auswahloptionen',row.questions)}${row.rationale?json('Goldbegründung',row.rationale):''}${row.valid?json('Native Wahrscheinlichkeiten · ungerundet',row.probabilities):''}${row.native_answers?json('Native Antwortfelder · unverändert',row.native_answers):''}${row.native_quarantine?json('Zusätzliche native Werte · unverändert',row.native_quarantine):''}${row.baseline_result?json('Clef zum gleichen Fall',row.baseline_result):''}${row.source?json('Quellenzuordnung',row.source):''}</details>`;
    }).join('')+(rows.length>displayLimit?`<div class="study-more"><span>${displayLimit} von ${rows.length} Treffern angezeigt</span><button type="button" class="quiet-button" data-study-more>Weitere Fälle</button></div>`:''):'<p class="study-empty">Keine passenden Fälle. Setze die Filter zurück.</p>';
  }
  async function select(id,{writeRoute=true}={}) {
    const entry=index.studies.find(s=>s.id===id)||index.studies[0];if(!entry)return;
    selected=entry.id;current=null;reset();const token=++generation;shell();if(writeRoute)route();
    if(entry.status!=='completed'){renderHeader(entry,null);return;}
    $('study-content').innerHTML='<p class="study-loading" role="status">Geprüfte Ergebnisse werden geladen …</p>';
    try {
      if(!cached.has(entry.id)){const response=await fetcher(entry.data_file);if(!response.ok)throw Error('Datei nicht verfügbar.');cached.set(entry.id,validateStudyData(await response.json(),entry));}
      if(!visible||token!==generation)return;
      current=cached.get(entry.id);renderHeader(entry,current);
    } catch {
      if(visible&&token===generation)$('study-content').innerHTML='<div class="notice danger" role="alert">Ergebnisse konnten nicht verifiziert werden. Es werden keine Ersatzwerte angezeigt. <button type="button" data-study-retry>Erneut laden</button></div>';
    }
  }
  root.addEventListener('click',event=>{
    const card=event.target.closest('[data-study]');if(card){void select(card.dataset.study);return;}
    if(event.target.closest('[data-study-retry]')){void select(selected);return;}
    if(event.target.closest('[data-study-more]')&&current){displayLimit+=100;renderCases();return;}
    if(event.target.closest('[data-study-reset]')&&current){reset();$('study-search').value='';$('study-group').value='all';$('study-outcome').value='all';renderCases();}
  });
  root.addEventListener('input',event=>{if(event.target.id==='study-search'){filters.query=event.target.value;displayLimit=100;renderCases();}});
  root.addEventListener('change',event=>{if(event.target.id==='study-group')filters.group=event.target.value;else if(event.target.id==='study-outcome')filters.outcome=event.target.value;else return;displayLimit=100;renderCases();});
  return {
    async show(params=new URLSearchParams()) {
      visible=true;const token=++generation;
      if(!index) {
        root.innerHTML='<p class="study-loading" role="status">Experimente werden geladen …</p>';
        if(!indexPending)indexPending=(async()=>{const r=await fetcher('./studies-data/index.json');if(!r.ok)throw Error('Index fehlt');return validateStudyIndex(await r.json());})();
        try {index=await indexPending;} catch {indexPending=null;if(visible&&token===generation)root.innerHTML='<p class="notice danger" role="alert">Experimentübersicht nicht verfügbar. Öffne die Ansicht erneut.</p>';return;}
      }
      if(!visible||token!==generation)return;
      await select(params.get('study')||selected||index.studies[0]?.id,{writeRoute:false});
    },
    hide(){visible=false;generation++;},
  };
}
