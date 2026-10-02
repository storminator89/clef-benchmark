export const CATEGORY = {
  it_routing: 'IT- & M365-Routing', urgency: 'Priorität & Negation',
  tool_selection: 'Werkzeugauswahl', document_classification: 'Dokumentfunktion',
  admin_intent: 'Verwaltungsabsicht', ambiguity_abstain: 'Mehrdeutigkeit'
};
export const SPLIT = {german_primary:'Deutsch / Deutsch',english_control:'Englisch / Englisch',mixed_schema_diagnostic:'Deutsch / Englisch'};
export const escapeHTML = (value) => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export const percent = (value, digits=1) => Number.isFinite(value) ? new Intl.NumberFormat('de-DE',{style:'percent',maximumFractionDigits:digits}).format(value) : '—';
export const decimal = (value, digits=2) => Number.isFinite(value) ? new Intl.NumberFormat('de-DE',{maximumFractionDigits:digits}).format(value) : '—';
/** A requested profile alone must never be shown as verified GPU execution. */
export function runtimeLabel(runtime) {
  if (!runtime?.device || !runtime?.precision) return 'Gerät und Präzision noch nicht geprüft';
  const backend=runtime.backend==='rocm'?'AMD ROCm':runtime.backend==='cpu'?'CPU':'Lokales Backend';
  return `${backend} · ${runtime.device_name||runtime.device} (${runtime.device}) · ${runtime.precision}`;
}
export function filterCases(cases, filters={}) {
  const query = (filters.query || '').trim().toLocaleLowerCase('de');
  return cases.filter(c => (!filters.split || c.split === filters.split) && (!filters.category || c.category === filters.category) && (!filters.tag || c.tags.includes(filters.tag)) && (!filters.errors || c.result?.correct === false) && (!query || [c.id,c.input,c.expected?.decision,c.result?.prediction,...c.tags].join(' ').toLocaleLowerCase('de').includes(query)));
}
export function probabilities(c) { return Object.entries(c?.probabilities || {}).sort((a,b)=>b[1]-a[1]); }
export function validatePlayground(state, questions) {
  if (!state.trim() || state.length>6000) throw new Error('Bitte gib einen Text mit 1 bis 6.000 Zeichen ein.');
  if (!questions || typeof questions!=='object' || Array.isArray(questions) || Object.keys(questions).length!==1) throw new Error('Das Schema muss genau eine choice-Frage enthalten.');
  const id=/^[A-Za-z][A-Za-z0-9_-]{0,63}$/;
  for (const [name,q] of Object.entries(questions)) {
    if (!id.test(name) || !q || Object.keys(q).sort().join(',')!=='criteria,instructions,type' || q.type!=='choice') throw new Error('Erwartet: eine choice-Frage mit type, instructions und criteria.');
    if (typeof q.instructions!=='string' || !q.instructions.trim() || q.instructions.length>4000) throw new Error('Die Richtlinie muss 1 bis 4.000 Zeichen enthalten.');
    if (!q.criteria || Array.isArray(q.criteria) || typeof q.criteria!=='object' || Object.keys(q.criteria).length<2 || Object.keys(q.criteria).length>12) throw new Error('Bitte definiere 2 bis 12 Auswahlklassen.');
    for (const [key,text] of Object.entries(q.criteria)) if (!id.test(key) || typeof text!=='string' || !text.trim() || text.length>300) throw new Error('Jede Klasse braucht eine ID und eine Beschreibung (1–300 Zeichen).');
  }
  return {state,questions};
}
/** Own one in-flight request; navigation must not replace its editor snapshot. */
export class InferenceSession {
  #active=null;
  #serial=0;
  get busy(){return this.#active!==null;}
  begin(){if(this.busy)throw new Error('Eine Inferenz läuft bereits.');this.#active=++this.#serial;return this.#active;}
  isCurrent(token){return this.#active===token;}
  finish(token){if(!this.isCurrent(token))return false;this.#active=null;return true;}
  edit(callback){if(this.busy)return false;callback();return true;}
}
