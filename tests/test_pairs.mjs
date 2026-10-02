import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {parseHTML} from 'linkedom';
import {validatePairs,pairFacts,filterPairs,createPairsView} from '../web/pairs-ui.js';
const fixture=JSON.parse(await readFile(new URL('../web/data/minimal_pairs.json',import.meta.url)));
const clone=()=>structuredClone(fixture);
function harness(fetcher=async()=>({ok:true,json:async()=>clone()})) {
 const {document,window}=parseHTML('<html><body><select></select><section id="pairs"></section></body></html>');
 const proto=Object.getPrototypeOf(document.querySelector('select'));
 if(!Object.getOwnPropertyDescriptor(proto,'value')?.set)Object.defineProperty(proto,'value',{configurable:true,get(){return [...this.querySelectorAll('option')].find(o=>o.hasAttribute('selected'))?.value??this.querySelector('option')?.value??'';},set(v){for(const o of this.querySelectorAll('option'))o.toggleAttribute('selected',o.value===String(v));}});
 const urls=[],win={history:{replaceState(_s,_t,u){urls.push(u);}}};
 const view=createPairsView({document,window:win,fetch:fetcher});
 return {document,window,view,urls,$:id=>document.getElementById(id),change(id,value,type='change'){const el=document.getElementById(id);el.value=value;el.dispatchEvent(new window.Event(type));},click(selector){document.querySelector(selector).click();}};
}
test('minimal pairs validate unchanged source and separate correctness from stability',()=>{validatePairs(fixture);assert.equal(fixture.pairs.filter(p=>pairFacts(p).both).length,17);assert.equal(fixture.pairs.filter(p=>pairFacts(p).stableWrong).length,2);assert.equal(fixture.pairs.filter(p=>pairFacts(p).unjustified).length,1);});
for(const [name,mutate] of [
 ['missing summary',d=>delete d.summary],['deceptive aggregate',d=>d.summary.pair_metrics.both_correct.numerator++],['bad rate',d=>d.summary.case_metrics.action.rate=1],['duplicate pair',d=>d.pairs[1]=d.pairs[0]],['changed message',d=>d.pairs[0].a.message+='!'],['changed source rule',d=>d.pairs[0].a.rule+='!'],['untrue correctness',d=>d.pairs[0].a.result.correct=false],['rounded confidence',d=>d.pairs[0].a.result.fields.action.confidence=.9],['NaN score',d=>d.pairs[0].a.result.fields.action.probabilities.answer=NaN],['false stable success',d=>{const p=d.pairs.find(p=>pairFacts(p).stableWrong);p.outcome.both_correct=true;}]
])test(`pair admission rejects ${name}`,()=>{const d=clone();mutate(d);assert.throws(()=>validatePairs(d));});
test('pair filters retain their own pair denominators',()=>{assert.equal(filterPairs(fixture.pairs,{outcome:'errors'}).length,7);assert.equal(filterPairs(fixture.pairs,{kind:'flip',outcome:'errors'}).length,4);assert.equal(filterPairs(fixture.pairs,{outcome:'stable-wrong'}).length,2);assert.equal(filterPairs(fixture.pairs,{outcome:'unjustified'}).length,1);assert.equal(filterPairs(fixture.pairs,{domain:'banking'}).length,8);});
test('pair view shows rule, exact highlighted edit, two fields and all raw probabilities',async()=>{const h=harness();await h.view.show(new URLSearchParams({pair:'pair_report_delivery_target'}));assert.equal(h.document.querySelectorAll('[data-pair]').length,24);assert.equal(h.document.querySelectorAll('.pair-endpoint').length,2);assert.equal(h.document.querySelectorAll('.pair-field').length,4);assert.equal(h.document.querySelectorAll('.pair-prob').length,14);assert.equal(h.document.querySelectorAll('.pair-message mark').length,2);assert.match(h.$('pair-detail').textContent,/Stabil, aber falsch/);assert.match(h.$('pair-detail').textContent,/Welchen der beiden Berichte/);assert.match(h.$('pair-detail').textContent,/Bestandsübersicht/);});
test('filter, no-match, reset and pair selection clear stale details',async()=>{const h=harness();await h.view.show();h.change('pair-outcome','stable-wrong');assert.equal(h.document.querySelectorAll('[data-pair]').length,2);h.change('pair-search','no-match-for-this-query','input');assert.equal(h.document.querySelectorAll('.pair-endpoint').length,0);h.click('#pair-reset');assert.equal(h.document.querySelectorAll('[data-pair]').length,24);h.click('[data-pair="pair_gadget_theft_notice"]');assert.match(h.$('pair-detail').textContent,/Inkonsistente Feldkombination/);assert.match(h.urls.at(-1),/pair_gadget_theft_notice/);});
test('source text is escaped, never inserted as active markup',async()=>{const d=clone();d.pairs[0].changed_fact='<img src=x onerror=alert(1)>';const h=harness(async()=>({ok:true,json:async()=>d}));await h.view.show();assert.equal(h.document.querySelectorAll('#pairs img').length,0);assert.match(h.$('pairs').textContent,/<img src=x/);});
test('unavailable data exposes retry and recovers without fabricated results',async()=>{let calls=0;const h=harness(async()=>++calls===1?{ok:false}:{ok:true,json:async()=>clone()});assert.equal(await h.view.show(),false);assert.equal(h.document.querySelectorAll('.pair-endpoint').length,0);assert.ok(h.$('pairs-retry'));assert.equal(await h.view.show(),true);assert.equal(calls,2);});
test('hide and repeated navigation prevent stale async paints',async()=>{let resolve,calls=0;const h=harness(()=>{calls++;return new Promise(r=>resolve=r);});const a=h.view.show();h.view.hide();resolve({ok:true,json:async()=>clone()});assert.equal(await a,false);assert.equal(h.document.querySelectorAll('.pair-endpoint').length,0);assert.equal(await h.view.show(),true);assert.equal(calls,1);});

test('diagnostic routes coexist with suite state and Back/Forward navigation',async()=>{
 const {harness:workbench}=await import('./helpers/dom.mjs');
 const reliability=JSON.parse(await readFile(new URL('../web/data/reliability.json',import.meta.url)));
 const h=await workbench({hash:'#pairs?pair=pair_report_delivery_target',overrides:{minimal_pairs:fixture,reliability}});
 await new Promise(r=>setImmediate(r));
 assert.equal(h.$('pairs').hidden,false);assert.equal(h.$('explorer').hidden,true);assert.match(h.$('pair-detail').textContent,/Stabil, aber falsch/);
 const initial=h.app.getState().suite;
 h.window.location.hash='#reliability?suite=clean72';await new Promise(r=>setImmediate(r));
 assert.equal(h.$('reliability').hidden,false);assert.equal(h.app.getState().suite,initial);assert.equal(h.document.querySelector('.context-bar').hidden,true);
 h.window.history.back();await new Promise(r=>setImmediate(r));assert.equal(h.$('pairs').hidden,false);
 h.window.history.forward();await new Promise(r=>setImmediate(r));assert.equal(h.$('reliability').hidden,false);
 h.window.location.hash='#explorer';assert.equal(h.$('explorer').hidden,false);assert.equal(h.document.querySelector('.context-bar').hidden,false);
 assert.equal(h.calls.filter(c=>c.url==='/api/infer').length,0);
});


test('compact pair headings and named icon actions keep the method in closed disclosures',async()=>{
 const h=harness();await h.view.show();
 assert.equal(h.document.querySelector('.analysis-heading h1').textContent,'Minimalpaare');
 assert.equal(h.document.querySelectorAll('.analysis-heading br,.analysis-heading em').length,0);
 assert.match(h.document.querySelector('.analysis-heading').textContent,/24 Paare · 48 Ausgaben/);
 assert.match(h.document.querySelector('.analysis-scope').textContent,/Abhängige Paare/);
 assert.match(h.document.querySelector('.analysis-scope').textContent,/ohne Fachvalidierung/);
 assert.equal(h.document.querySelectorAll('.analysis-nav a .icon').length,2);
 assert.equal(h.document.querySelectorAll('#pair-reset .icon').length,1);
 assert.match(h.$('pair-reset').textContent,/Filter zurücksetzen/);
 for(const selector of ['.pair-reading','.pair-method','.pair-raw']) {
   const detail=h.document.querySelector(selector);
   assert.equal(detail.hasAttribute('open'),false);
   assert.ok(detail.querySelector('summary').textContent.trim());
 }
 assert.match(h.document.querySelector('.pair-method').textContent,/39 \/ 48 Fälle vollständig richtig/);
 assert.match(h.document.querySelector('.pair-method').textContent,/keine gemeinsame Korrektheitswahrscheinlichkeit/);
 for(const icon of h.document.querySelectorAll('.icon')) assert.equal(icon.getAttribute('aria-hidden'),'true');
});
