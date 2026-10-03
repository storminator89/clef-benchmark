import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { validateStudyIndex,validateStudyData,filterStudyCases } from '../web/studies-core.js';
const entry={id:'fixture',label:'Synthetic contract test only',status:'completed',planned_requests:1,unit:'Anfragen',methods:[],data_file:'./studies-data/fixture.json'};
const row={id:'TEST_ONLY_1',input:'<img src=x onerror=alert(1)>',group:'test',questions:{action:{type:'choice',criteria:{a:'Alpha',b:'Beta'}}},expected:{action:'a'},prediction:{action:'a'},probabilities:{action:{a:.7,b:.3}},valid:true,correct:true};
const data=()=>({format_version:1,id:'fixture',status:'completed',audit:{status:'passed',source_manifest_sha256:'0'.repeat(64)},metrics:[{kind:'ratio',label:'Synthetic test metric',numerator:1,denominator:1,unit:'Anfragen'}],cases:[structuredClone(row)]});
test('published index has no fake pending observations',async()=>{const index=JSON.parse(await readFile(new URL('../web/studies-data/index.json',import.meta.url)));validateStudyIndex(index);assert.deepEqual(new Set(index.studies.map(s=>s.id)),new Set(['language72','jev974','wahler580']));for(const x of index.studies){if(x.status!=='completed'){assert.equal(x.cases,undefined);assert.equal(x.metrics,undefined);assert.equal(x.data_file,undefined);}else{const data=JSON.parse(await readFile(new URL('../web/'+x.data_file.slice(2),import.meta.url)));validateStudyData(data,x);}}});
test('pending cards cannot expose data or metrics',()=>{for(const property of ['cases','metrics','data_file'])assert.throws(()=>validateStudyIndex({format_version:1,studies:[{...entry,status:'pending',[property]:[]}]}));});
test('completed paths remain same-origin fixed study paths',()=>{assert.throws(()=>validateStudyIndex({format_version:1,studies:[{...entry,data_file:'https://example.com/data.json'}]}));assert.equal(validateStudyIndex({format_version:1,studies:[entry]}).studies.length,1);});
test('native case contract and independent metric denominators accepted',()=>assert.equal(validateStudyData(data(),entry).cases.length,1));
test('different IDs, counts, missing audit or bad denominators rejected',()=>{for(const mutate of [x=>x.id='other',x=>x.cases.push(structuredClone(row)),x=>x.audit.status='pending',x=>x.metrics[0].denominator=0]){const x=data();mutate(x);assert.throws(()=>validateStudyData(x,entry));}});
test('missing probabilities or repaired result claims rejected',()=>{for(const mutate of [x=>delete x.cases[0].probabilities.action.b,x=>x.cases[0].probabilities.action.a=NaN,x=>x.cases[0].probabilities.action.a=.8,x=>x.cases[0].prediction.action='b',x=>x.cases[0].correct=false]){const x=data();mutate(x);assert.throws(()=>validateStudyData(x,entry));}});
test('technical rows cannot count as correct',()=>{const x=data();x.cases[0].valid=false;x.cases[0].technical_note='Synthetic invalid fixture';assert.throws(()=>validateStudyData(x,entry));x.cases[0].correct=false;assert.equal(validateStudyData(x,entry).cases[0].valid,false);});
test('search, error and grouping filters compose without mutation',()=>{const cases=[row,{...row,id:'TEST_ONLY_2',valid:false,correct:false,group:'other'},{...row,id:'TEST_ONLY_3',expected:{action:'b'},correct:false,group:'other'}];assert.equal(filterStudyCases(cases,{outcome:'errors'}).length,1);assert.equal(filterStudyCases(cases,{group:'test',query:'alpha'}).length,0);assert.equal(filterStudyCases(cases,{query:'img',group:'other'}).length,2);assert.equal(filterStudyCases(cases,{outcome:'technical'}).length,1);assert.equal(cases.length,3);});

test('structured native input remains structured and searchable',()=>{const x=data();x.cases[0].input={document:'Originalvertrag'};assert.deepEqual(validateStudyData(x,entry).cases[0].input,{document:'Originalvertrag'});assert.equal(filterStudyCases(x.cases,{query:'Originalvertrag'}).length,1);});

test('cancelled study cannot expose invented observations',()=>{for(const property of ['cases','metrics','data_file'])assert.throws(()=>validateStudyIndex({format_version:1,studies:[{...entry,status:'cancelled',[property]:[]}]}));});

test('direct analysis preserves planned denominators and narrowly identifies sum-only answers',async()=>{
 const index=JSON.parse(await readFile(new URL('../web/studies-data/index.json',import.meta.url)));const entry=index.studies.find(x=>x.id==='jev974');const value=JSON.parse(await readFile(new URL('../web/studies-data/jev974.json',import.meta.url)));validateStudyData(value,entry);
 assert.equal(value.cases.filter(x=>x.sum_only_deviation).length,35);assert.equal(value.cases.filter(x=>!x.valid).length,2);
 for(const mutate of [x=>x.audit.analysis_manifest_sha256='0'.repeat(64),x=>x.analysis='old-strict',x=>x.comparisons[0].jev_correct=999,x=>x.comparisons.find(r=>!r.baseline_ready).clef_correct=0,x=>x.cases.find(r=>!r.valid).correct=true]){const changed=structuredClone(value);mutate(changed);assert.throws(()=>validateStudyData(changed,entry));}
});
