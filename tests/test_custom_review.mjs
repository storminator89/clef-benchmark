/** Independent model-free review: Python is a pure parser/oracle, with no sockets. */
import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { exampleSuite, importSuite, parseBoundedJSON, PRESETS, suiteFingerprint, newReport, CustomEvaluator, exportSnapshot, csvCell } from '../web/custom-cases.js';
import { liveFixture, harness } from './helpers/dom.mjs';

const root = new URL('../', import.meta.url);
const clone = value => structuredClone(value);
const tick = () => new Promise(resolve => setImmediate(resolve));
const health = { inference_enabled: true, busy: false, requested_profile: 'cpu-nf4', revision: 'test-revision', model_key: 'flash-9b', model_id: 'Cloudflare/clef-flash', model: 'Cloudflare/clef-flash' };
function python(code, input) {
  const child = spawnSync('python3', ['-c', `import sys,json,copy\nfrom unittest.mock import patch\nfrom scripts import evaluate_custom as e\ndata=json.load(sys.stdin)\n${code}`], { cwd: root, input: JSON.stringify(input), encoding: 'utf8' });
  assert.equal(child.status, 0, child.stderr);
  return JSON.parse(child.stdout);
}
const importsInPython = cases => python(`
out=[]
for item in data:
    def read(path, maximum=e.MAX_INPUT_BYTES):
        if str(path)=='spec.json': return json.dumps(item.get('spec'))
        raw=item['raw'].encode('utf-8')
        if len(raw)>maximum: raise ValueError('size limit')
        return raw.decode('utf-8-sig')
    try:
        with patch.object(e,'read_text',read):
            value=e.load_suite('Parity.'+item['format'],item['format'],'spec.json' if item['format']=='csv' else None)
        out.append({'ok':True,'value':value})
    except (ValueError,TypeError): out.append({'ok':False})
print(json.dumps(out,ensure_ascii=False))`, cases);

test('review: JSON/JSONL/CSV parser accept/reject decisions and exact strings match Python', () => {
  const suite=exampleSuite(); suite.name='Parity';
  suite.cases[0].state='  Ä 😀 "quoted"\r\n\u2028 end\t  ';
  const json=JSON.stringify(suite), jsonl=suite.cases.map(c=>JSON.stringify(c)).join('\r\n');
  const corpus=[
    ...[json,'\ufeff'+json,'\ufeff\ufeff'+json,json.replace('"schema_version":1','"schema_version":1,"schema_version":1')].map(raw=>({format:'json',raw})),
    ...[jsonl,jsonl+'\n','\ufeff'+jsonl,'\ufeff\ufeff'+jsonl,jsonl+'\n\n',JSON.stringify(suite.cases[0])+'\n\ufeff'+JSON.stringify(suite.cases[1])].map(raw=>({format:'jsonl',raw})),
    ...['id,state\nx,"Ä, ""quoted""\r\n😀"\n','\ufeffid,state\nx,valid\r','\ufeff\ufeffid,state\nx,valid','id,state\nx,"x"suffix','id,state\nx,un"quoted','id,state\nx,text\n\n','id,state\nx,\u0085','id,state\nx,\ufeff'].map(raw=>({format:'csv',raw,spec:PRESETS.support})),
  ];
  for (const blank of ['\u0085','\ufeff','\u001c','\u001f',' \ufeff\u0085 ']) {
    for (const field of ['name','state','instructions','description']) {
      const item=clone(suite);
      if(field==='name')item.name=blank;
      else if(field==='state')item.cases[0].state=blank;
      else if(field==='instructions')item.cases[0].questions.intent.instructions=blank;
      else item.cases[0].questions.intent.criteria.zugang=blank;
      corpus.push({format:'json',raw:JSON.stringify(item)});
    }
  }
  const expected=importsInPython(corpus);
  corpus.forEach((item,i)=>{
    let actual;try{actual={ok:true,value:importSuite(item.raw,{format:item.format,name:'Parity',spec:item.spec})};}catch{actual={ok:false};}
    assert.deepEqual(actual,expected[i],`corpus row ${i} (${item.format})`);
  });
});

test('review: fingerprints agree cross-language including Unicode and question-order changes', async () => {
  const base=exampleSuite(), suites=[base];
  for(const text of ['\u0000\b\f\n\r\t','Ä 😀 \u2028 \u2029','\\ / "',' \ufeffwithin text']) {const s=clone(base);s.cases[0].state=text;suites.push(s);}
  const reverse=clone(base);reverse.cases[0].questions=Object.fromEntries(Object.entries(reverse.cases[0].questions).reverse());suites.push(reverse);
  const expected=python('print(json.dumps([e.suite_fingerprint(s) for s in data]))',suites);
  assert.deepEqual(await Promise.all(suites.map(s=>suiteFingerprint(s))),expected);
  assert.notEqual(expected[0],expected.at(-1));
});

test('review: depth, escaped quotes, forbidden keys and lone-surrogate parser decisions match Python', () => {
  const raw=[...Array.from({length:14},(_,n)=>'['.repeat(n)+'0'+']'.repeat(n)), '{"a":"escaped \\\" [ {"}', '{"constructor":1}', '{"__proto__":1}', '{"x":1,"\\u0078":2}', '"\\ud800"', '"\\ud83d\\ude00"', '1e999'];
  const expected=python(`
out=[]
for text in data:
    try: e.parse_json(text); out.append(True)
    except (ValueError,TypeError): out.append(False)
print(json.dumps(out))`,raw);
  const actual=raw.map(text=>{try{parseBoundedJSON(text);return true;}catch{return false;}});
  assert.deepEqual(actual,expected);
});

test('review: CSV formula escaping agrees on the union of Unicode whitespace', () => {
  const raw=['plain','"quote",comma','\tplain','\rplain','\nplain',...['',' ','\ufeff','\u0085','\u001c','\u001f',' \ufeff\u0085'].flatMap(prefix=>['=','+','-','@'].map(op=>prefix+op+'formula'))];
  const expected=python('print(json.dumps([e.escape_csv(s) for s in data],ensure_ascii=False))',raw);
  assert.deepEqual(raw.map(s=>csvCell(s).slice(1,-1).replaceAll('""','"')),expected);
});

test('review: browser in-flight snapshot resumes in Python with only pending requests and unverified provenance', async () => {
  const report=await newReport(exampleSuite());
  const ev=new CustomEvaluator({fetch:async(url,options)=>{
    if(url==='/api/health')return{ok:true,json:async()=>health};
    ev.cancel();return{ok:true,json:async()=>liveFixture(JSON.parse(options.body))};
  }});
  await ev.run(report);
  const snapshot=exportSnapshot(report,report.results[1].id);
  snapshot.result_provenance='verified';
  const result=python(`
with patch.object(e,'read_text',lambda *args:json.dumps(data)):
    report=e.load_resume('unused.json',data['suite'])
class Client:
    endpoint='http://127.0.0.1:8765'
    calls=[]
    def health(self): return {**report['model_identity'],'inference_enabled':True,'busy':False}
    def request(self,method,path,body):
        self.calls.append(json.loads(body));return 422,{'error':'review fixture'}
client=Client()
def checkpoint(report,*args): report['summary']=e.summarize(report['suite'],report['results'])
with patch.object(e,'save_report',checkpoint): e.run_evaluation(report,client,'unused.json')
print(json.dumps({'statuses':[r['status'] for r in report['results']],'provenance':report['result_provenance'],'calls':client.calls,'summary':report['summary']}))`,snapshot);
  assert.deepEqual(result.statuses,['success','error','error']);
  assert.equal(result.provenance,'user_supplied_resume_plus_local_execution');
  assert.deepEqual(result.calls,[{state:report.suite.cases[2].state,questions:report.suite.cases[2].questions}]);
  assert.equal(result.summary.completion_coverage,1);
  assert.equal(result.summary.field_coverage,2/3);
});

test('review: malformed health booleans never permit inference', async () => {
  for(const mutation of [{inference_enabled:'false'},{inference_enabled:1},{busy:null},{busy:0}, {busy:undefined}]) {
    let posts=0;const report=await newReport(exampleSuite());
    const ev=new CustomEvaluator({fetch:async(url,options)=>url==='/api/health'?{ok:true,json:async()=>({...health,...mutation})}:(posts++,{ok:true,json:async()=>liveFixture(JSON.parse(options.body))})});
    await assert.rejects(()=>ev.run(report));
    assert.equal(posts,0);assert.equal(report.status,'blocked');assert.equal(ev.busy,false);
    assert.ok(report.results.every(r=>r.status==='pending'));
  }
});

test('review: cancel during health preflight submits nothing and permits an explicit continuation', async () => {
  let release,firstHealth=true,posts=0;
  const gate=new Promise(resolve=>release=resolve),report=await newReport(exampleSuite());
  const ev=new CustomEvaluator({fetch:async(url,options)=>{
    if(url==='/api/health'){if(firstHealth){firstHealth=false;await gate;}return{ok:true,json:async()=>health};}
    posts++;return{ok:true,json:async()=>liveFixture(JSON.parse(options.body))};
  }});
  const pending=ev.run(report);while(firstHealth)await tick();ev.cancel();release();await pending;
  assert.equal(posts,0);assert.equal(report.status,'interrupted');assert.equal(report.summary.cases_pending,3);
  assert.equal(await ev.run(report),true);assert.equal(posts,3);
});

test('review: uncertain failed request is never retried on explicit pending-only continuation', async () => {
  let posts=0;const report=await newReport(exampleSuite());
  const ev=new CustomEvaluator({fetch:async(url,options)=>{
    if(url==='/api/health')return{ok:true,json:async()=>health};
    posts++;if(posts===1)return{ok:true,json:async()=>{throw Error('broken JSON');}};
    return{ok:true,json:async()=>liveFixture(JSON.parse(options.body))};
  }});
  assert.equal(await ev.run(report),false);assert.equal(posts,1);assert.equal(report.status,'blocked');
  assert.equal(await ev.run(report),true);assert.equal(posts,3);
  assert.deepEqual(report.results.map(r=>r.status),['error','success','success']);
  assert.equal(report.summary.field_accuracy,0);assert.equal(report.summary.field_coverage,1/3);
});

test('review: active playground blocks custom execution, edits and clearing symmetrically', async () => {
  let release,posts=0;const gate=new Promise(resolve=>release=resolve);
  const h=await harness({enabled:true,requestHandler:async request=>{posts++;await gate;return{ok:true,json:async()=>liveFixture(request)};}});
  await h.app.custom.importText(JSON.stringify(exampleSuite()));await h.app.custom.acceptPreview();
  const pending=h.app.runLive();while(!posts)await tick();
  assert.equal(await h.app.custom.start(),false);
  h.click('#custom-clear');assert.equal(h.app.custom.getState().suite.cases.length,3);
  assert.equal(h.$('custom-state').disabled,true);assert.equal(h.$('custom-apply').disabled,true);
  release();await pending;assert.equal(posts,1);assert.equal(h.$('custom-state').disabled,false);
});

test('privacy: clearing removes private state, gold and derived DOM content', async () => {
  const h = await harness();
  const suite = exampleSuite(); suite.name = 'PRIVATE_NAME_CANARY';
  suite.cases[0].state = 'PRIVATE_TEXT_CANARY';
  suite.cases[0].questions.intent.criteria.zugang = 'PRIVATE_OPTION_CANARY';
  await h.app.custom.importText(JSON.stringify(suite));
  assert.match(h.$('custom-preview-list').textContent, /PRIVATE_TEXT_CANARY/);
  await h.app.custom.acceptPreview();
  assert.equal(h.$('custom-preview-list').textContent, '');
  assert.equal(h.$('custom-preview-copy').textContent, '');
  assert.equal(h.$('custom-state').value, 'PRIVATE_TEXT_CANARY');
  h.click('#custom-clear');
  assert.equal(h.$('custom-confirm').hidden, false);
  h.click('#custom-confirm-action');
  assert.equal(h.app.custom.getState().suite, null);
  assert.equal(h.app.custom.getState().report, null);
  for (const id of ['custom-state', 'custom-questions', 'custom-gold']) assert.equal(h.$(id).value, '');
  for (const id of ['custom-suite-title', 'custom-case-id', 'custom-list', 'custom-preview-list', 'custom-preview-copy', 'custom-case-result', 'custom-metrics', 'custom-field-scores', 'custom-runtime', 'custom-progress-text', 'custom-score-note']) assert.equal(h.$(id).textContent, '', id);
  assert.equal(h.$('custom-progress').value, 0);
  assert.equal(h.$('custom-editor').hidden, true);
});

test('privacy: rejected or replaced import removes stale private preview DOM', async () => {
  const h = await harness();
  const suite = exampleSuite(); suite.name = 'STALE_NAME_CANARY'; suite.cases[0].state = 'STALE_TEXT_CANARY';
  await h.app.custom.importText(JSON.stringify(suite));
  assert.match(h.$('custom-preview-copy').textContent, /STALE_NAME_CANARY/);
  assert.equal(await h.app.custom.importText('{'), false);
  assert.equal(h.$('custom-preview-list').textContent, '');
  assert.equal(h.$('custom-preview-copy').textContent, '');
  await h.app.custom.importText(JSON.stringify(suite));
  await h.app.custom.importText(JSON.stringify(exampleSuite()));
  assert.doesNotMatch(h.$('custom-preview-list').textContent, /STALE_TEXT_CANARY/);
  assert.doesNotMatch(h.$('custom-preview-copy').textContent, /STALE_NAME_CANARY/);
});
