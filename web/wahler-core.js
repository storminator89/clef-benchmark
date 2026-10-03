/** Audited three-model study. Native choices are never repaired or renormalized. */
export const WAHLER_GROUPS={original_text180:120,finance100:80,clean72:72,bank_support80:80,insurance60:60,clarification72:72,minimal_pairs48:48,multidoc48:48};
export const STUDY_MODELS={clef:'Clef Flash 9B',wahler:'Wähler 4B',jev:'Jev 1.13.0'};
const object=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
const check=(ok,message)=>{if(!ok)throw Error(message);};
const keys=(a,b)=>object(a)&&object(b)&&Object.keys(a).length===Object.keys(b).length&&Object.keys(a).every(k=>Object.hasOwn(b,k));
export function modelOutcome(row,model){const a=row.models[model];return a.status==='native_answer'?Object.keys(row.expected).every(f=>a.answers[f].choice===row.expected[f])?'correct':'errors':'technical';}
export function validateWahlerStudy(v,entry){
 check(v?.format_version===2&&v.id==='wahler580'&&entry.id===v.id&&entry.planned_requests===580&&v.status==='completed','Ungültige Vergleichsstudie.');
 check(v.audit?.status==='passed'&&/^[0-9a-f]{64}$/.test(v.audit.source_manifest_sha256||''),'Verifizierte Quellenbindung fehlt.');
 check(Array.isArray(v.cases)&&v.cases.length===580&&Array.isArray(v.comparisons)&&v.comparisons.length===8,'Geplante Fälle fehlen.');
 const counts=Object.fromEntries(Object.keys(WAHLER_GROUPS).map(s=>[s,0]));const totals={};const ids=new Set();let fields=0;
 for(const row of v.cases){
  check(object(row)&&Object.hasOwn(counts,row.suite)&&typeof row.id==='string'&&!ids.has(JSON.stringify([row.suite,row.id])),'Ungültiger oder doppelter Fall.');ids.add(JSON.stringify([row.suite,row.id]));counts[row.suite]++;
  const q=row.request?.questions;check(object(row.request)&&Object.hasOwn(row.request,'state')&&keys(q,row.expected)&&Object.keys(q).length>0&&keys(row.models,STUDY_MODELS),'Antwortfelder fehlen.');fields+=Object.keys(q).length;
  for(const [f,question]of Object.entries(q))check(object(question)&&question.type==='choice'&&object(question.criteria)&&typeof row.expected[f]==='string'&&Object.hasOwn(question.criteria,row.expected[f]),'Goldlabel fehlt.');
  for(const m of Object.keys(STUDY_MODELS)){
   const a=row.models[m];check(object(a),'Modellantwort fehlt.');
   if(a.status==='missing_or_structurally_invalid'){check(m==='jev'&&a.answers===null,'Fehlende Antwort wird als Ergebnis angezeigt.');}
   else{
    check(a.status==='native_answer'&&keys(a.answers,q),'Native Antwortfelder fehlen.');
    for(const [f,answer]of Object.entries(a.answers)){
     check(object(answer)&&answer.type==='choice'&&keys(answer.probabilities,q[f].criteria),'Native Optionen fehlen.');
     const p=answer.probabilities;check(Object.values(p).every(x=>Number.isFinite(x)&&x>=0&&x<=1)&&Object.hasOwn(p,answer.choice)&&p[answer.choice]===Math.max(...Object.values(p))&&Number.isFinite(answer.confidence)&&answer.confidence>=0&&answer.confidence<=1,'Ungültige native Auswahl.');
    }
   }
   const t=totals[row.suite]??={};const n=t[m]??={correct:0,classifiable:0,missing_or_structurally_invalid:0};if(a.status==='native_answer'){n.classifiable++;n.correct+=modelOutcome(row,m)==='correct';}else n.missing_or_structurally_invalid++;
  }
 }
 check(fields===968&&Object.entries(WAHLER_GROUPS).every(([s,n])=>counts[s]===n),'Gruppennenner stimmen nicht.');
 const seen=new Set();for(const g of v.comparisons){check(object(g)&&Object.hasOwn(WAHLER_GROUPS,g.suite)&&!seen.has(g.suite)&&typeof g.label==='string'&&g.planned===WAHLER_GROUPS[g.suite]&&keys(g.models,STUDY_MODELS),'Vergleichsgruppe fehlt.');seen.add(g.suite);for(const m of Object.keys(STUDY_MODELS)){const a=g.models[m],t=totals[g.suite][m];check(object(a)&&a.planned===g.planned&&Object.keys(t).every(k=>a[k]===t[k]),'Vergleichszähler stimmen nicht mit Fällen überein.');}}
 check(Object.entries(totals).every(([s,g])=>g.jev.missing_or_structurally_invalid===(['finance100','bank_support80'].includes(s)?1:0)),'Historische Jev-Antworten fehlen.');
 return v;
}
export function filterWahlerCases(rows,{query='',outcome='all',group='all',model='wahler'}={}){const search=query.trim().toLocaleLowerCase('de');return rows.filter(r=>(group==='all'||r.suite===group)&&(outcome==='all'||modelOutcome(r,model)===outcome)&&`${r.id} ${r.suite} ${JSON.stringify(r.request.state)} ${JSON.stringify(r.expected)}`.toLocaleLowerCase('de').includes(search));}
