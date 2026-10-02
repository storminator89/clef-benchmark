import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {escapeHTML,filterCases,percent,probabilities,validatePlayground,runtimeLabel} from '../web/core.js';
test('live runtime label uses actual backend and precision without assuming CPU or GPU',()=>{
  assert.equal(runtimeLabel(null),'Gerät und Präzision noch nicht geprüft');
  assert.equal(runtimeLabel({profile:'rocm-bf16'}),'Gerät und Präzision noch nicht geprüft');
  assert.match(runtimeLabel({backend:'rocm',device:'cuda:1',device_name:'Radeon',precision:'BF16'}),/AMD ROCm.*Radeon.*cuda:1.*BF16/);
  assert.match(runtimeLabel({backend:'cpu',device:'cpu',device_name:'CPU',precision:'NF4'}),/CPU.*NF4/);
});
test('untrusted input is escaped',()=>assert.equal(escapeHTML('<img src=x onerror="x">'), '&lt;img src=x onerror=&quot;x&quot;&gt;'));
test('unknown numbers never become fabricated statistics',()=>{assert.equal(percent(undefined),'—');assert.equal(percent(NaN),'—');assert.equal(percent(.8),'80 %');});
const cases=[{id:'de_1',input:'Überweisung nicht gewünscht',split:'german_primary',category:'a',tags:['negation'],expected:{decision:'no'},result:{correct:false,prediction:'yes'}},{id:'en_1',input:'no payment',split:'english_control',category:'a',tags:['negation'],expected:{decision:'no'},result:{correct:true,prediction:'no'}}];
test('filters combine without mutation',()=>{assert.equal(filterCases(cases,{split:'german_primary',errors:true,query:'ÜBER'}).length,1);assert.equal(filterCases(cases,{split:'english_control',errors:true}).length,0);assert.equal(cases.length,2);});
test('probabilities sorted descending',()=>assert.deepEqual(probabilities({probabilities:{a:.2,b:.8}}),[['b',.8],['a',.2]]));
const schema={decision:{type:'choice',instructions:'Ordne zu.',criteria:{a:'Eine Klasse',b:'Andere Klasse'}}};
test('native schema accepted',()=>assert.deepEqual(validatePlayground('Text',schema),{state:'Text',questions:schema}));
test('invalid schemas refused',()=>{assert.throws(()=>validatePlayground('',schema));assert.throws(()=>validatePlayground('Text',{}));assert.throws(()=>validatePlayground('Text',{decision:{...schema.decision,type:'number'}}));assert.throws(()=>validatePlayground('Text',{decision:{...schema.decision,criteria:{a:'A'}}}));assert.throws(()=>validatePlayground('Text',{decision:{...schema.decision,url:'https://example.com'}}));});
test('UI data is complete or explicitly results-free',async()=>{const data=JSON.parse(await readFile(new URL('../web/data/benchmark.json',import.meta.url)));assert.equal(data.cases.length,180);assert.equal(new Set(data.cases.map(c=>c.id)).size,180);if(data.status==='completed'){assert.equal(data.verification.status,'pass');assert.equal(data.verification.n_present,180);assert.ok(data.cases.every(c=>c.result));}else{assert.equal(data.status,'test_data_only');assert.ok(data.cases.every(c=>!c.result));assert.equal(data.scores,undefined);}});
test('website has no third-party script, font or tracking dependency',async()=>{const html=await readFile(new URL('../web/index.html',import.meta.url),'utf8'),css=await readFile(new URL('../web/styles.css',import.meta.url),'utf8');assert.equal(/<script[^>]+src=["']https?:/.test(html),false);assert.equal(/@import|https?:\/\//.test(css),false);});
test('both final suites preserve independent denominators and IDs',async()=>{
  const general=JSON.parse(await readFile(new URL('../web/data/benchmark.json',import.meta.url)));
  const finance=JSON.parse(await readFile(new URL('../web/data/finance.json',import.meta.url)));
  assert.equal(general.status,'completed');assert.equal(finance.status,'completed');
  assert.equal(general.suite.id,'general');assert.equal(finance.suite.id,'finance');
  assert.equal(finance.cases.length,100);assert.equal(finance.cases.filter(c=>c.split==='german_primary').length,80);
  assert.equal(finance.verification.n_present,100);assert.equal(finance.verification.status,'pass');
  assert.equal(general.cases.filter(c=>c.split==='german_primary').length,120);
  const generalIDs=new Set(general.cases.map(c=>c.id));assert.ok(finance.cases.every(c=>!generalIDs.has(c.id)));
  assert.equal(filterCases(finance.cases,{split:'german_primary',errors:true}).length,4);
  assert.equal(filterCases(general.cases,{split:'german_primary',errors:true}).length,4);
  assert.equal(finance.scores.splits.german_primary.choice_accuracy_all_planned,.95);
});
test('pending inference keeps editor ownership across navigation and example replacement',async()=>{
  const {InferenceSession}=await import('../web/core.js');
  const session=new InferenceSession();let editor='original request';
  const token=session.begin();
  assert.equal(session.busy,true);
  // Explorer navigation can try to load another case, but edit() refuses it.
  assert.equal(session.edit(()=>editor='different example'),false);
  assert.equal(editor,'original request');
  assert.throws(()=>session.begin());
  assert.equal(session.isCurrent(token),true);
  assert.equal(session.finish(token+1),false);
  assert.equal(session.busy,true);
  assert.equal(session.finish(token),true);
  assert.equal(session.edit(()=>editor='different example'),true);
  assert.equal(editor,'different example');
  const newToken=session.begin();
  assert.equal(session.isCurrent(token),false);
  assert.equal(session.isCurrent(newToken),true);
});
test('clean72 stays a separate completed German-only suite with exact recorded results',async()=>{
 const data=JSON.parse(await readFile(new URL('../web/data/clean72.json',import.meta.url)));
 assert.equal(data.status,'completed');assert.equal(data.suite.id,'clean72');assert.equal(data.cases.length,72);
 assert.equal(new Set(data.cases.map(c=>c.id)).size,72);assert.equal(data.verification.status,'pass');
 assert.equal(data.scores.splits.german_clean_primary.choice_accuracy_all_planned,61/72);
 assert.equal(filterCases(data.cases,{split:'german_clean_primary',errors:true}).length,11);
 assert.equal(filterCases(data.cases,{split:'german_clean_primary',category:'beitragsrechnung',errors:true}).length,6);
 assert.deepEqual(data.scores.paired_all_planned,{});
 for(const file of ['benchmark','finance']){
  const original=JSON.parse(await readFile(new URL(`../web/data/${file}.json`,import.meta.url)));
  const ids=new Set(original.cases.map(c=>c.id));assert.ok(data.cases.every(c=>!ids.has(c.id)));
 }
 assert.ok(data.cases.every(c=>c.result.schema_valid&&c.language==='de'));
});
test('follow-up report links and clean selector exist without an image upload control',async()=>{
 const html=await readFile(new URL('../web/index.html',import.meta.url),'utf8');
 assert.match(html,/value="clean72"/);assert.match(html,/experiments\/images\/README.md/);
 assert.match(html,/experiments\/attack_ablation14\/RESULTS.md/);assert.doesNotMatch(html,/<input[^>]+type=["']file/i);
 // Separate-pair visibility is behavior-tested in test_workbench_dom.mjs.

});
