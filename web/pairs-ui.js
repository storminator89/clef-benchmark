import { escapeHTML as e, percent } from './core.js';
const FIELDS = ['action', 'determination'];
const OPTIONS = {action:['answer','ask_fact','ask_target','resolve_conflict'],determination:['yes','no','unresolved']};
const DOMAIN = {banking:'Banking',insurance:'Versicherung',finance:'Finanzen'};
const LABEL = {answer:'Antwort geben',ask_fact:'Fakt nachfragen',ask_target:'Ziel klären',resolve_conflict:'Widerspruch klären',yes:'Ja',no:'Nein',unresolved:'Offen'};
const equal = (a,b) => FIELDS.every(f => a[f] === b[f]);
const fail = () => { throw Error('Ungültige oder widersprüchliche Paardaten'); };
const metric = (actual, n, d) => {
  if (!actual || actual.numerator !== n || actual.denominator !== d || Math.abs(actual.rate - n/d) > 1e-10) fail();
};
export function pairFacts(p) {
  const pa = Object.fromEntries(FIELDS.map(f=>[f,p.a.result.fields[f].prediction]));
  const pb = Object.fromEntries(FIELDS.map(f=>[f,p.b.result.fields[f].prediction]));
  const both = equal(pa,p.a.expected) && equal(pb,p.b.expected), changed = !equal(pa,pb);
  return {both, changed, stableWrong:p.kind === 'invariant' && !changed && !both, unjustified:p.kind === 'invariant' && changed, correctFlip:p.kind === 'flip' && both};
}
export function validatePairs(data) {
  if (data?.schema_version !== 1 || data.status !== 'completed' || !Array.isArray(data.pairs) || data.pairs.length !== 24) fail();
  const ids = new Set(), cases = new Set();
  for (const p of data.pairs) {
    if (typeof p.id !== 'string' || ids.has(p.id) || !['flip','invariant'].includes(p.kind) || !DOMAIN[p.domain]) fail();
    ids.add(p.id);
    if (![p.rule,p.question,p.changed_fact,p.change?.prefix,p.change?.span_a,p.change?.span_b,p.change?.suffix].every(x=>typeof x === 'string') || p.change.span_a === p.change.span_b) fail();
    for (const side of ['a','b']) {
      const c=p[side];
      if (!c || typeof c.id !== 'string' || cases.has(c.id) || c.rule !== p.rule || c.question !== p.question || c.message !== p.change.prefix + p.change[`span_${side}`] + p.change.suffix || c.result?.schema_valid !== true) fail();
      cases.add(c.id);
      let all = true;
      for (const f of FIELDS) {
        const r=c.result.fields?.[f], opts=OPTIONS[f];
        if (!r || !opts.includes(c.expected?.[f]) || !opts.includes(r.prediction) || !r.probabilities || Object.keys(r.probabilities).length !== opts.length || !opts.every(k=>Number.isFinite(r.probabilities[k]) && r.probabilities[k]>=0 && r.probabilities[k]<=1) || Math.abs(Object.values(r.probabilities).reduce((a,b)=>a+b,0)-1)>0.00001 || r.confidence !== r.probabilities[r.prediction] || r.correct !== (r.prediction === c.expected[f])) fail();
        all &&= r.correct;
      }
      if (c.result.correct !== all) fail();
    }
    if ((p.kind === 'invariant') !== equal(p.a.expected,p.b.expected)) fail();
    const s=pairFacts(p), o=p.outcome;
    if (!o || o.valid_pair !== true || o.both_correct !== s.both || o.observed_change !== s.changed || (p.kind==='flip' ? o.correct_directional_change !== s.correctFlip : o.stable !== !s.changed || o.stable_but_incorrect !== s.stableWrong || o.unjustified_change !== s.unjustified)) fail();
  }
  const flip=data.pairs.filter(p=>p.kind==='flip'), invariant=data.pairs.filter(p=>p.kind==='invariant');
  if (flip.length !== 12 || invariant.length !== 12) fail();
  const sum=(rows,key)=>rows.filter(p=>pairFacts(p)[key]).length, m=data.summary?.pair_metrics, cm=data.summary?.case_metrics;
  metric(m?.both_correct,sum(data.pairs,'both'),24);
  metric(m?.correct_directional_change,sum(flip,'correctFlip'),12);
  metric(m?.observed_change_on_flip,sum(flip,'changed'),12);
  metric(m?.unjustified_change,sum(invariant,'unjustified'),12);
  metric(m?.stable_invariant,12-sum(invariant,'changed'),12);
  metric(m?.stable_but_incorrect,sum(invariant,'stableWrong'),12);
  const endpoints=data.pairs.flatMap(p=>[p.a,p.b]);
  metric(cm?.all_fields_exact,endpoints.filter(c=>c.result.correct).length,48);
  FIELDS.forEach(f=>metric(cm?.[f],endpoints.filter(c=>c.result.fields[f].correct).length,48));
  return data;
}
export function filterPairs(rows,{domain='',kind='',outcome='',query=''}={}) {
  const q=query.toLocaleLowerCase('de');
  return rows.filter(p=> (!domain || p.domain===domain) && (!kind || p.kind===kind) && (!q || `${p.id} ${p.rule} ${p.changed_fact} ${p.a.message} ${p.b.message}`.toLocaleLowerCase('de').includes(q)) && (!outcome || (outcome==='errors' ? !pairFacts(p).both : outcome==='stable-wrong' ? pairFacts(p).stableWrong : outcome==='unjustified' ? pairFacts(p).unjustified : pairFacts(p).both)));
}
const badge=p=>{const s=pairFacts(p); return `<span class="pair-badge ${s.both?'good':'bad'}">${s.both?'Beide korrekt':s.stableWrong?'Stabil, aber falsch':s.unjustified?'Unbegründet verändert':'Übergang fehlerhaft'}</span>`;};
const report='https://github.com/storminator89/clef-benchmark/blob/main/experiments/minimal_pairs/REPORT.md';
export function createPairsView({document:doc=globalThis.document,window:win=globalThis.window,fetch:fetcher=globalThis.fetch}={}) {
  const root=doc.getElementById('pairs');
  let data=null, pending=null, visible=false, generation=0, selected=null;
  const filters={domain:'',kind:'',outcome:'',query:''};
  const $=id=>doc.getElementById(id);
  function updateURL(){const params=new URLSearchParams({pair:selected}); win.history.replaceState(null,'',`#pairs?${params}`);}
  function comparison(p) {
    return ['a','b'].map(side=>{
      const c=p[side], inconsistent=(c.result.fields.action.prediction==='answer') !== (c.result.fields.determination.prediction!=='unresolved');
      return `<article class="pair-endpoint"><div class="pair-endpoint-head"><span class="pair-letter">${side.toUpperCase()}</span><h3>Variante ${side.toUpperCase()}</h3><span class="pair-badge ${c.result.correct?'good':'bad'}">${c.result.correct?'Beide Felder richtig':'Fehler enthalten'}</span></div><p class="pair-message">${e(p.change.prefix)}<mark>${e(p.change[`span_${side}`])}</mark>${e(p.change.suffix)}</p><div class="pair-field-head"><span>Antwortfeld</span><span>Soll → Modell</span><span>Optionscore</span></div>${FIELDS.map(f=>{const r=c.result.fields[f];return `<div class="pair-field ${r.correct?'good':'bad'}"><strong>${f==='action'?'Aktion':'Feststellung'}</strong><span>${e(LABEL[c.expected[f]])}<span aria-hidden="true"> → </span><b>${e(LABEL[r.prediction])}</b><small>${e(c.expected[f])} → ${e(r.prediction)}</small></span><span class="pair-score">${percent(r.confidence,2)}<small>${r.correct?'richtig':'falsch'}</small></span></div>`;}).join('')}${inconsistent?'<p class="pair-warning">Inkonsistente Feldkombination: Antwort mit „offen“ oder Rückfrage mit einer konkreten Feststellung. Originalausgabe unverändert.</p>':''}<details class="pair-raw"><summary>Begründung & alle nativen Optionscores</summary><p>${e(typeof c.gold_rationale==='string'?c.gold_rationale:JSON.stringify(c.gold_rationale))}</p>${FIELDS.map(f=>`<h4>${f==='action'?'Aktion':'Feststellung'}</h4>${Object.entries(c.result.fields[f].probabilities).map(([k,v])=>`<div class="pair-prob"><span>${e(k)}</span><meter min="0" max="1" value="${v}">${v}</meter><span>${Number(v).toFixed(9)}</span></div>`).join('')}`).join('')}<small>Fall-ID: ${e(c.id)} · marginale native Wahrscheinlichkeiten, keine gemeinsame Korrektheitswahrscheinlichkeit</small></details></article>`;
    }).join('');
  }
  function renderDetail() {
    const p=data.pairs.find(p=>p.id===selected), node=$('pair-detail');
    if (!p) {node.innerHTML='<div class="analysis-empty">Keine passenden Paare. Setze die Filter zurück.</div>';return;}
    const s=pairFacts(p);
    node.innerHTML=`<div class="pair-detail-heading"><div><div class="eyebrow">${e(DOMAIN[p.domain])} · ${p.kind==='flip'?'SOLLANTWORT ÄNDERT SICH':'SOLLANTWORT BLEIBT GLEICH'}</div><h2>${e(p.changed_fact)}</h2></div>${badge(p)}</div><div class="pair-rule"><span>FIKTIVE REGEL · IDENTISCH IN A UND B</span><p>${e(p.rule)}</p><strong>${e(p.question)}</strong></div><div class="pair-comparison">${comparison(p)}</div><div class="pair-reading"><strong>${s.both?'Der Paarvergleich ist vollständig korrekt.':s.stableWrong?'Gleich geblieben heißt hier: zweimal falsch.':s.unjustified?'Die Ausgabe ändert sich, obwohl die Sollantwort gleich bleibt.':'Die Änderung wurde bemerkt. Der vollständige Übergang ist trotzdem falsch.'}</strong><p>${p.kind==='flip'?'Ein richtiger Richtungswechsel verlangt die korrekte Aktion und Feststellung an beiden Endpunkten.':'Bei invarianten Paaren prüfen wir Stabilität und Richtigkeit getrennt. Eine unveränderte falsche Antwort besteht den Test nicht.'} Das markierte Textstück ist die einzige Änderung; Regel, Frage und native Antwortoptionen bleiben gleich.</p></div>`;
  }
  function renderList() {
    const rows=filterPairs(data.pairs,filters);
    if (!rows.some(p=>p.id===selected)) selected=rows[0]?.id||null;
    $('pair-count').textContent=`${rows.length} / ${data.pairs.length}`;
    $('pair-list').innerHTML=rows.length?rows.map(p=>`<button class="pair-list-item ${selected===p.id?'active':''}" data-pair="${e(p.id)}" aria-pressed="${selected===p.id}"><span>${e(DOMAIN[p.domain])} · ${p.kind==='flip'?'Wechsel':'Invariant'}</span><strong>${e(p.changed_fact)}</strong>${badge(p)}</button>`).join(''):'<p class="analysis-empty">Keine Treffer</p>';
    $('pair-list').querySelectorAll('[data-pair]').forEach(b=>b.addEventListener('click',()=>{selected=b.dataset.pair;renderList();updateURL();[...$('pair-list').querySelectorAll('[data-pair]')].find(node=>node.dataset.pair===selected)?.focus({preventScroll:true});}));
    renderDetail();
  }
  function render() {
    const m=data.summary.pair_metrics;
    root.innerHTML=`<div class="analysis-nav"><a href="#pairs" aria-current="page">Minimalpaare</a><a href="#reliability">Score & Fehlerrisiko <span aria-hidden="true">↗</span></a></div><div class="analysis-heading"><div><div class="eyebrow">24 PAARE · 48 ECHTE MODELLAUSGABEN</div><h1>Ein Detail anders.<br><em>Die richtige Reaktion?</em></h1><p>Eine Zahl, ein Status, ein irrelevanter Titel: Wir verändern genau eine Textstelle und vergleichen beide Entscheidungen.</p></div><a class="source-link" href="${report}" target="_blank" rel="noreferrer">Vollständiger Bericht ↗</a></div><div class="pair-metrics"><article><span>Beide Varianten richtig</span><strong>${m.both_correct.numerator}<small> / 24 Paare</small></strong><p>Aktion und Feststellung an beiden Endpunkten</p></article><article><span>Korrekter Richtungswechsel</span><strong>${m.correct_directional_change.numerator}<small> / 12 Wechsel</small></strong><p>Alle 12 Ausgaben änderten sich; 4 Übergänge waren falsch</p></article><article><span>Unbegründete Änderung</span><strong>${m.unjustified_change.numerator}<small> / 12 Invarianten</small></strong><p>11 blieben stabil, davon 2 stabil falsch</p></article></div><p class="analysis-scope">Gezielt konstruierte, abhängige Paare mit fiktiven Regeln. KI-verfasst und separat KI-geprüft; keine Expertenvalidierung oder Produktionsrisiko-Schätzung. CPU NF4 · Original-Head · 39/48 Fälle vollständig richtig.</p><div class="pair-workspace"><aside class="pair-library" aria-label="Paarauswahl"><div class="panel-title"><h2>Paarbibliothek</h2><span id="pair-count" class="count-badge"></span></div><div class="pair-filters"><label for="pair-search">Suchen</label><input id="pair-search" type="search" placeholder="Regel oder Änderung …"><label for="pair-kind">Änderungsart</label><select id="pair-kind"><option value="">Alle Arten</option><option value="flip">Sollantwort ändert sich</option><option value="invariant">Sollantwort bleibt gleich</option></select><label for="pair-outcome">Ergebnis</label><select id="pair-outcome"><option value="">Alle Ergebnisse</option><option value="errors">Fehlerhafte Paare</option><option value="stable-wrong">Stabil, aber falsch</option><option value="unjustified">Unbegründet verändert</option><option value="correct">Beide korrekt</option></select><label for="pair-domain">Bereich</label><select id="pair-domain"><option value="">Alle Bereiche</option>${Object.entries(DOMAIN).map(([k,v])=>`<option value="${k}">${v}</option>`).join('')}</select><button id="pair-reset" class="text-button">Filter zurücksetzen</button></div><div id="pair-list" class="pair-list"></div></aside><div id="pair-detail" class="pair-detail" aria-live="polite"></div></div><p class="analysis-source">Gezeigte Optionscores sind die ungerundeten nativen Werte, hier zur Anzeige gerundet. Hohe Scores sind keine Sicherheitsgarantie. <a href="#reliability">Auswahlquote und beobachtete Fehler gemeinsam prüfen →</a></p>`;
    for(const [id,key,event] of [['pair-kind','kind','change'],['pair-outcome','outcome','change'],['pair-domain','domain','change'],['pair-search','query','input']]) {$ (id).value=filters[key];$(id).addEventListener(event,()=>{filters[key]=$(id).value;renderList();});}
    $('pair-reset').addEventListener('click',()=>{Object.keys(filters).forEach(k=>filters[k]='');render();});
    renderList();
  }
  async function show(params=new URLSearchParams()) {
    visible=true; const token=++generation;
    if (!data) {
      root.innerHTML='<p class="analysis-empty" role="status">Verifizierte Paarergebnisse werden geladen …</p>';
      try {pending ||= (async()=>{const r=await fetcher('./data/minimal_pairs.json',{cache:'no-store'});if(!r.ok)throw Error();return validatePairs(await r.json());})(); data=await pending;}
      catch {pending=null;if(visible&&token===generation){root.innerHTML='<div class="notice danger" role="alert">Die Paardaten fehlen oder haben die Integritätsprüfung nicht bestanden. <button id="pairs-retry" class="text-button">Erneut versuchen</button></div>'; $('pairs-retry').addEventListener('click',()=>show(params));}return false;}
    }
    if (!visible||token!==generation)return false;
    const requested=params.get('pair');
    if (requested && data.pairs.some(p=>p.id===requested)){selected=requested;Object.keys(filters).forEach(k=>filters[k]='');}
    render();return true;
  }
  return {show,hide(){visible=false;generation++;},getState:()=>({selected,filters:{...filters},loaded:!!data})};
}
