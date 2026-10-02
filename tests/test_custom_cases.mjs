import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { exampleSuite, importSuite, validateSuite, parseBoundedJSON, parseCSV, validateSpec, PRESETS, CUSTOM_LIMITS, suiteFingerprint, newReport, scoreSuite, resultsCSV, csvCell, CustomEvaluator, exportSnapshot, validateCustomResponse } from '../web/custom-cases.js';
import { liveFixture, harness } from './helpers/dom.mjs';
const clone = value => structuredClone(value);
const good = c => liveFixture({ state: c.state, questions: c.questions });
const health = { inference_enabled: true, busy: false, requested_profile: 'cpu-nf4', revision: 'test-revision', model_key:'flash-9b',model_id:'Cloudflare/clef-flash',model:'Cloudflare/clef-flash' };
const tick = () => new Promise(resolve => setImmediate(resolve));

test('JSON and JSONL preserve exact payloads and optional user gold without assumptions', () => {
  const suite = exampleSuite(); suite.cases[0].state = '  Ä, "Zitat"\r\n😀 Ende  ';
  assert.deepEqual(importSuite('\ufeff' + JSON.stringify(suite)), suite);
  assert.deepEqual(importSuite(suite.cases.map(c => JSON.stringify(c)).join('\r\n') + '\r\n', { format:'jsonl', name:suite.name }), suite);
  assert.equal(Object.hasOwn(suite.cases[2], 'gold'), false);
  const partial = scoreSuite(suite);
  assert.equal(partial.labelled_fields, 3); assert.equal(partial.fields_total, 6); assert.equal(partial.fully_labelled_cases, 1);
});
test('CSV handles BOM, escaped quotes, Unicode and quoted multiline cells with optional gold', () => {
  const text = '\ufeffid,state,gold.intent,gold.priority\r\ncase1,"Karte, \"\"Hallo\"\"\r\nzweite Zeile",karte,\r\ncase2,"Ä 😀",,\r\n';
  const suite = importSuite(text, {format:'csv', name:'csv', spec:PRESETS.support});
  assert.equal(suite.cases.length, 2); assert.equal(suite.cases[0].state, 'Karte, "Hallo"\r\nzweite Zeile');
  assert.deepEqual(suite.cases[0].gold, {intent:'karte'}); assert.equal(Object.hasOwn(suite.cases[1], 'gold'), false);
});
test('bad CSV rows are rejected with location; no blanks, surplus columns, duplicate headers or coercion', () => {
  for (const text of ['id,state\na,a\n\nb,b\n', 'id,state\na,a,extra', 'id,id,state\na,a,b', 'id,state,unknown\na,b,c', 'id,state,gold.intent\na,b,not-an-option', 'id,state\na,"unterminated', 'id,state\na,"abc"x', 'id,state\na,ab"cd']) assert.throws(() => importSuite(text, {format:'csv', spec:PRESETS.support}), /CSV|Goldlabel|Fall/);
  assert.throws(() => importSuite('id,state\na,b', {format:'csv'}), /Spezifikation/);
});
test('strict keys, safe IDs, duplicate IDs, invalid gold and media/trust fields never enter private suites', () => {
  for (const mutate of [s => s.status = 'verified', s => s.cases[0].result = good(s.cases[0]), s => s.cases[0].id = '../file', s => s.cases[1].id = s.cases[0].id, s => s.cases[0].gold.extra = 'x', s => s.cases[0].gold.intent = null, s => s.cases[0].questions.intent.type = 'image', s => s.cases[0].image_url = 'https://example.org/a.jpg']) {
    const suite = exampleSuite(); mutate(suite); assert.throws(() => validateSuite(suite));
  }
  assert.throws(() => importSuite('{"schema_version":1,"schema_version":1,"name":"x","cases":[]}'), /Doppelter/);
  assert.throws(() => parseBoundedJSON('{"__proto__":{"polluted":true}}'), /Reserviert/);
  assert.throws(() => parseBoundedJSON('{"questions":{"constructor":{}}}'), /Reserviert/);
  assert.equal({}.polluted, undefined);
});
test('byte, depth, row and per-request limits fail explicitly without truncating', () => {
  assert.throws(() => parseBoundedJSON('['.repeat(13) + '0' + ']'.repeat(13)), /Verschachtelung/);
  assert.throws(() => importSuite('x'.repeat(CUSTOM_LIMITS.bytes + 1)), /5 MiB/);
  const s = exampleSuite(); s.cases = Array.from({length:501}, (_, i) => ({...s.cases[0], id:'c' + i})); assert.throws(() => validateSuite(s), /500/);
  const long = exampleSuite(); long.cases[0].state = '😀'.repeat(6001); assert.throws(() => validateSuite(long), /6.000/);
  assert.throws(() => parseBoundedJSON('"\\ud800"'), /Surrogat/);
  assert.throws(() => importSuite(JSON.stringify(exampleSuite().cases[0]) + '\n\n', {format:'jsonl'}), /Leere Zeile/);
  assert.throws(() => validateSpec({...PRESETS.support, extra:true}), /genau/);
});
test('scores include failed and pending labelled requests and distinguish unlabelled fields', () => {
  const s = exampleSuite(), response = good(s.cases[0]); response.answers.priority.choice = 'normal';
  const results = [{id:s.cases[0].id,status:'success',response}, {id:s.cases[1].id,status:'error',response:null}];
  const stats = scoreSuite(s, results);
  assert.equal(stats.cases_succeeded,1); assert.equal(stats.cases_failed,1); assert.equal(stats.cases_pending,1);
  assert.equal(stats.correct_labelled_fields,2); assert.equal(stats.field_accuracy,2/3); assert.equal(stats.field_coverage,2/3);
  assert.equal(stats.case_accuracy,1); assert.equal(stats.case_coverage,1); assert.equal(stats.gold_coverage,1/2); assert.equal(stats.completion_coverage,2/3); assert.equal(stats.prediction_coverage,1/3);
  assert.deepEqual(stats.by_field.intent,{labelled:2,evaluated:1,correct:1,accuracy:.5,coverage:.5});
  s.cases.forEach(c => delete c.gold); assert.equal(scoreSuite(s,results).field_accuracy,null); assert.equal(scoreSuite(s,results).case_accuracy,null);
});
test('fingerprint detects changed input, labels and native question order', async () => {
  const s = exampleSuite(), original = await suiteFingerprint(s);
  const c = clone(s); c.cases[0].state += ' '; assert.notEqual(await suiteFingerprint(c),original);
  const g = clone(s); delete g.cases[0].gold.intent; assert.notEqual(await suiteFingerprint(g),original);
  const q = clone(s); q.cases[0].questions = Object.fromEntries(Object.entries(q.cases[0].questions).reverse()); assert.notEqual(await suiteFingerprint(q),original);
  assert.equal(await suiteFingerprint(clone(s)),original);
});
test('sequential evaluator sends only exact state/questions, guards repeated clicks and never predicts pending rows', async () => {
  const report = await newReport(exampleSuite()); let active = 0, peak = 0, posts = 0;
  const ev = new CustomEvaluator({fetch:async (url, options) => {
    if (url === '/api/health') return {ok:true,json:async()=>health};
    const request = JSON.parse(options.body); assert.deepEqual(Object.keys(request),['state','questions']); assert.equal(options.headers['X-Clef-Request'],'1');
    active++; peak = Math.max(peak,active); posts++; await tick(); active--; return {ok:true,json:async()=>liveFixture(request)};
  }});
  const pending = ev.run(report); assert.equal(await ev.run(report),false); await pending;
  assert.equal(posts,3); assert.equal(peak,1); assert.equal(report.status,'completed'); assert.equal(report.summary.cases_succeeded,3);
});
test('cancel waits for in-flight response then stops future calls, partial export and resume preserve completed rows', async () => {
  const report = await newReport(exampleSuite()); let release, posts = 0;
  const promise = new Promise(resolve => release = resolve);
  const ev = new CustomEvaluator({fetch:async (url, options) => {
    if (url === '/api/health') return {ok:true,json:async()=>health}; posts++; if (posts === 1) await promise; return {ok:true,json:async()=>liveFixture(JSON.parse(options.body))};
  }});
  const p = ev.run(report); while (!posts) await tick(); ev.cancel(); assert.equal(ev.busy,true); release(); await p;
  assert.equal(posts,1); assert.equal(report.status,'interrupted'); assert.equal(report.summary.cases_pending,2); assert.equal(report.results[1].response,null);
  const exported = JSON.parse(JSON.stringify(report)); assert.equal(exported.status,'interrupted');
  await ev.run(report); assert.equal(posts,3); assert.equal(report.status,'completed');
});
test('backend busy, unknown network completion and invalid output stop the suite honestly', async () => {
  for (const mode of ['busy','network','invalid','409']) {
    let posts = 0; const report = await newReport(exampleSuite());
    const ev = new CustomEvaluator({fetch:async (url, options) => {
      if (url === '/api/health') return {ok:true,json:async()=>({...health,busy:mode==='busy'})};
      posts++; if (mode==='network') throw Error('connection lost');
      if (mode==='409') return {ok:false,status:409,json:async()=>({error:'already busy'})};
      return {ok:true,json:async()=>({answers:{}})};
    }});
    try { await ev.run(report); } catch { /* busy is surfaced to the user */ }
    assert.equal(report.status,'blocked'); assert.equal(posts,mode==='busy'?0:1); assert.equal(ev.busy,false); assert.ok(report.results.slice(1).every(r=>r.status==='pending' && r.response===null));
  }
});
test('clear per-case runtime rejection stays in denominator and no expected label gets sent', async () => {
  const report = await newReport(exampleSuite()); let posts = 0;
  const ev = new CustomEvaluator({fetch:async (url, options) => url === '/api/health' ? {ok:true,json:async()=>health} : (posts++, {ok:false,status:422,json:async()=>({error:'Token budget exceeded'})})});
  await ev.run(report); assert.equal(posts,3); assert.equal(report.status,'completed'); assert.equal(report.summary.field_accuracy,0); assert.equal(report.summary.field_coverage,0); assert.equal(report.summary.cases_failed,3);
});
test('CSV result export is formula-safe while JSON retains every original string', async () => {
  for (const text of ['=SUM(1,2)', '+foo', '-2', '@x', '\tformula', '\rfoo', '\nfoo', '  =x']) assert.ok(csvCell(text).startsWith('"\''));
  const report = await newReport(exampleSuite()); report.results[0].status='error'; report.results[0].error={message:'=HYPERLINK("evil")'};
  const csv=resultsCSV(report); assert.ok(csv.startsWith('\ufeff')); assert.match(csv, /'=HYPERLINK/); assert.equal(JSON.parse(JSON.stringify(report)).results[0].error.message,'=HYPERLINK("evil")');
});
test('private UI previews without network, handles import errors atomically and never contaminates public suites', async () => {
  const h=await harness({hash:'#custom'}), before=h.calls.length;
  assert.equal(h.$('custom').hidden,false); assert.equal(h.$('explorer').hidden,true);
  assert.equal(await h.app.custom.importText(JSON.stringify(exampleSuite())),true); assert.equal(h.app.custom.getState().suite,null); assert.equal(h.calls.length,before);
  await h.app.custom.acceptPreview(); assert.equal(h.app.custom.getState().suite.cases.length,3); assert.equal(h.document.querySelectorAll('[data-custom-case]').length,3);
  assert.equal(h.app.getState().suite,'insurance'); assert.equal(h.$('suite-select').querySelectorAll('option').length,6);
  assert.equal(h.storage.size,0); assert.match(h.$('custom-score-note').textContent,/Vorläufig/);
  assert.equal(await h.app.custom.importText('{'),false); assert.equal(h.app.custom.getState().suite.cases.length,3); assert.equal(h.app.custom.getState().preview,null);
});
test('private UI performs real API requests, edits invalidate all previous results before applying', async () => {
  const h=await harness({hash:'#custom',enabled:true}); await h.app.custom.importText(JSON.stringify(exampleSuite())); await h.app.custom.acceptPreview();
  assert.equal(await h.app.custom.start(),true); assert.equal(h.document.querySelectorAll('[data-custom-answer]').length,2);
  assert.match(h.$('custom-case-result').textContent,/Nicht unabhängig geprüft/); assert.equal(h.app.custom.getState().report.summary.cases_succeeded,3);
  h.change('custom-state','Geänderter Text','input'); assert.equal(h.app.custom.getState().report,null); assert.equal(h.document.querySelectorAll('[data-custom-answer]').length,0); assert.equal(h.$('custom-run').disabled,true);
  h.change('custom-questions','{','input'); assert.equal(h.app.custom.applyEdit(),false); assert.equal(await h.app.custom.start(),false);
  h.click('#custom-discard'); assert.equal(h.app.custom.getState().dirty,false); assert.equal(h.app.custom.getState().report,null);
});
test('untrusted strings render as text and imported trust/result fields are rejected', async () => {
  const h=await harness({hash:'#custom'}), s=exampleSuite(); s.name='<img src=x onerror=alert(1)>'; s.cases[0].state='<script>alert(1)</script>';
  await h.app.custom.importText(JSON.stringify(s)); await h.app.custom.acceptPreview();
  assert.equal(h.$('custom-suite-title').textContent,s.name); assert.equal(h.$('custom-list').querySelector('script'),null); assert.equal(h.$('custom-preview-list').querySelector('script'),null);
  s.verification={status:'verified'}; assert.equal(await h.app.custom.importText(JSON.stringify(s)),false);
});
test('private sequential run blocks concurrent playground and stopping keeps current request visible', async () => {
  let resolve, posts=0; const deferred=new Promise(r=>resolve=r);
  const h=await harness({enabled:true,requestHandler:async request=>{posts++; await deferred; return {ok:true,json:async()=>liveFixture(request)};}});
  await h.app.custom.importText(JSON.stringify(exampleSuite())); await h.app.custom.acceptPreview();
  const p=h.app.custom.start(); while(!posts) await tick();
  assert.equal(h.$('run-live').disabled,true); assert.equal(await h.app.runLive(),false);
  h.app.custom.cancel(); assert.match(h.$('custom-progress-text').textContent,/Stop vorgemerkt/); assert.equal(posts,1); resolve(); await p;
  assert.equal(posts,1); assert.equal(h.app.custom.getState().report.status,'interrupted');
  h.click('#custom-export-json'); const exported=JSON.parse(await h.downloads.at(-1).text()); assert.equal(exported.summary.cases_pending,2);
});
test('templates and input suite export are genuine files; no localStorage for customer data', async () => {
  const h=await harness(); for(const id of ['custom-template-json','custom-template-jsonl','custom-template-csv','custom-template-spec']) h.click('#'+id);
  assert.equal(h.downloads.length,4); assert.equal(JSON.parse(await h.downloads[0].text()).schema_version,1);
  assert.equal(importSuite(await h.downloads[2].text(),{format:'csv',spec:JSON.parse(await h.downloads[3].text())}).cases.length,3); assert.equal(h.storage.size,0);
});


test('BOM handling and Unicode blank-only text are consistent and reject ambiguous inputs', () => {
  const suite=exampleSuite(), raw=JSON.stringify(suite);
  assert.deepEqual(importSuite('\ufeff'+raw),suite);
  assert.throws(()=>importSuite('\ufeff\ufeff'+raw));
  assert.throws(()=>importSuite('\ufeff\ufeff'+JSON.stringify(suite.cases[0]),{format:'jsonl'}));
  assert.throws(()=>importSuite(JSON.stringify(suite.cases[0])+'\n\ufeff'+JSON.stringify(suite.cases[1]),{format:'jsonl'}));
  assert.throws(()=>importSuite('\ufeff\ufeffid,state\nx,text',{format:'csv',spec:PRESETS.support}));
  for (const whitespace of ['\u0085','\ufeff','\u001c','\u001f','\u2000']) {
    const blank=exampleSuite();blank.cases[0].state=whitespace;assert.throws(()=>validateSuite(blank));
    blank.cases[0].state='synthetic';blank.name=whitespace;assert.throws(()=>validateSuite(blank));
  }
});
test('export during in-flight request preserves uncertainty and cannot silently resume that request',async()=>{
  const report=await newReport(exampleSuite()), snapshot=exportSnapshot(report,report.results[0].id);
  assert.equal(snapshot.results[0].status,'error');assert.equal(snapshot.results[0].error.kind,'in_flight');
  assert.equal(report.results[0].status,'pending');assert.equal(snapshot.summary.cases_pending,2);
});
test('model/profile change blocks continuation before any new POST and wrong response identity is rejected',async()=>{
  const report=await newReport(exampleSuite());let posts=0,currentHealth={...health};
  const ev=new CustomEvaluator({fetch:async(url,options)=>{if(url==='/api/health')return{ok:true,json:async()=>currentHealth};posts++;ev.cancel();return{ok:true,json:async()=>liveFixture(JSON.parse(options.body))};}});
  await ev.run(report);assert.equal(posts,1);assert.equal(report.status,'interrupted');
  currentHealth={...health,model_key:'clef-27b',model:'Cloudflare/clef',model_id:'Cloudflare/clef',revision:'27b-test-only'};
  await assert.rejects(()=>ev.run(report),/gewechselt/);assert.equal(posts,1);assert.equal(report.status,'blocked');
  const response=good(exampleSuite().cases[0]);response.runtime.revision='wrong';assert.throws(()=>validateCustomResponse(response,exampleSuite().cases[0]),/Modellmetadaten/);
});
test('native field-order and every timing/probability metadata field are checked',()=>{
  const c=exampleSuite().cases[0],response=good(c);response.answers=Object.fromEntries(Object.entries(response.answers).reverse());assert.throws(()=>validateCustomResponse(response,c),/umgeordnet/);
  for(const value of [undefined,NaN,Infinity,-1,true]){const r=good(c);r.latency_ms=value;assert.throws(()=>validateCustomResponse(r,c));}
});


test('CSV parser enforces row/column caps while scanning, including tiny adversarial records',()=>{
  assert.throws(()=>parseCSV('id,state\n'+'x,y\n'.repeat(501)),/500/);
  assert.throws(()=>parseCSV('id,state\n'+','.repeat(10000)),/10 Spalten/);
});
test('programmatic editor changes during disabled in-flight UI cannot retain a stale result',async()=>{
  let release,posts=0;const deferred=new Promise(r=>release=r);
  const h=await harness({enabled:true,requestHandler:async request=>{posts++;await deferred;return{ok:true,json:async()=>liveFixture(request)};}});
  await h.app.custom.importText(JSON.stringify(exampleSuite()));await h.app.custom.acceptPreview();
  const p=h.app.custom.start();while(!posts)await tick();
  h.$('custom-state').value='Changed while request was pending';h.app.custom.cancel();release();await p;
  assert.equal(h.app.custom.getState().report,null);assert.equal(h.app.custom.getState().dirty,true);
  assert.equal(h.document.querySelectorAll('[data-custom-answer]').length,0);
});

test('custom UX: empty results are not represented as a zero accuracy measurement', async () => {
  const h = await harness({hash:'#custom'});
  await h.app.custom.importText(JSON.stringify(exampleSuite())); await h.app.custom.acceptPreview();
  assert.equal(h.$('custom-import-box').open, false);
  assert.deepEqual([...h.document.querySelectorAll('.custom-metric strong')].map(el=>el.textContent), ['3/6','—','—','0/3']);
  assert.match(h.$('custom-field-scores').textContent, /noch nicht ausgewertet/);
  assert.equal(h.$('custom-run').disabled, true);
  assert.equal(h.document.querySelector('[aria-current="step"]').dataset.customStep, 'edit');
});

test('custom UX: cancelling clear or replacement preserves private suite and editor changes', async () => {
  const h = await harness({hash:'#custom'});
  await h.app.custom.importText(JSON.stringify(exampleSuite())); await h.app.custom.acceptPreview();
  h.change('custom-state','Private unsaved text','input');
  h.click('#custom-clear'); assert.equal(h.$('custom-confirm').hidden,false);
  h.click('#custom-confirm-cancel');
  assert.equal(h.$('custom-state').value,'Private unsaved text');
  assert.equal(h.app.custom.getState().dirty,true);
  const next=exampleSuite();next.name='Replacement';
  await h.app.custom.importText(JSON.stringify(next));
  assert.equal(await h.app.custom.acceptPreview(),false);
  assert.notEqual(h.app.custom.getState().suite.name,'Replacement');
  h.click('#custom-confirm-cancel');
  assert.equal(h.$('custom-state').value,'Private unsaved text');
  h.click('#custom-accept'); h.click('#custom-confirm-action');
  assert.equal(h.app.custom.getState().suite.name,'Replacement');
  assert.equal(h.app.custom.getState().dirty,false);
  assert.equal(h.$('custom-confirm').hidden,true);
  assert.equal(h.$('custom-preview-list').textContent,'');
});

test('custom UX: search and incomplete-gold filters have an accessible reset without changing the suite', async () => {
  const h = await harness({hash:'#custom'});
  await h.app.custom.importText(JSON.stringify(exampleSuite())); await h.app.custom.acceptPreview();
  h.change('custom-filter','unlabelled');
  assert.equal(h.document.querySelectorAll('[data-custom-case]').length,2);
  assert.equal(h.$('custom-list-count').textContent,'2 / 3');
  h.change('custom-search','cannotmatchthiscase','input');
  assert.equal(h.document.querySelectorAll('[data-custom-case]').length,0);
  h.click('[data-custom-reset]');
  assert.equal(h.document.querySelectorAll('[data-custom-case]').length,3);
  assert.equal(h.app.custom.getState().suite.cases.length,3);
  h.change('custom-search','SEARCH_PRIVATE_CANARY','input');
  h.click('#custom-clear');h.click('#custom-confirm-action');
  assert.equal(h.$('custom-search').value,'');
  assert.equal(h.$('custom-list-count').textContent,'');
  assert.equal(h.$('custom-confirm-copy').textContent,'');
});

test('custom UX: dirty state is visible, schema errors are announced and discard restores the accepted input', async () => {
  const h = await harness({hash:'#custom',enabled:true});
  await h.app.custom.importText(JSON.stringify(exampleSuite())); await h.app.custom.acceptPreview();
  h.change('custom-questions','{','input');
  assert.match(h.$('custom-editor-state').textContent,/noch nicht übernommen/);
  assert.equal(h.$('custom-run').disabled,true);
  h.click('#custom-apply');
  assert.equal(h.$('custom-message').getAttribute('role'),'alert');
  h.click('#custom-discard');
  assert.equal(h.app.custom.getState().dirty,false);
  assert.equal(h.$('custom-editor-state').classList.contains('dirty'),false);
  assert.equal(h.$('custom-message').getAttribute('role'),'status');
});

test('custom UX: arrow keys navigate from the focused row even before it was selected', async () => {
  const h=await harness({hash:'#custom'});
  await h.app.custom.importText(JSON.stringify(exampleSuite()));await h.app.custom.acceptPreview();
  const ids=exampleSuite().cases.map(c=>c.id), focused=h.document.querySelector(`[data-custom-case="${ids[1]}"]`);
  focused.focus(); const event=new h.window.Event('keydown',{bubbles:true});event.key='ArrowDown';focused.dispatchEvent(event);
  assert.equal(h.app.custom.getState().selected,ids[2]);
  assert.equal(h.document.__focused.dataset.customCase,ids[2]);
});
