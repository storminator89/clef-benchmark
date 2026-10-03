"""Read-only display adapter; preserves strict exclusions and matched denominators."""
import hashlib,json,math
from collections import defaultdict

def require(ok,message):
 if not ok:raise ValueError(message)
def load(path):return json.loads(path.read_text())
def lines(path):return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
def index(records,key):
 out={key(r):r for r in records};require(len(out)==len(records),'Duplicate Jev source identity');return out
def digest(value):return hashlib.sha256(json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()).hexdigest()
LABELS={'minimal_pairs48':'Minimalpaare','clarification72':'Rückfragen','bank_support80':'Bank-Support','original_text180':'Allgemeine Entscheidungen','finance100':'Finanzen','insurance60':'Versicherungen','clean72':'Alltagsnahe Regeln','attack_ablation14':'Angriffspaare','multidoc48':'Mehrere Dokumente','massive300':'MASSIVE Deutsch'}
SPLITS={'german_primary':'Deutsch','diagnostic_pairs':'Paare','mixed_schema_diagnostic':'Gemischtes Schema','english_control':'Englisch','german_clean_primary':'Deutsch','posthoc_attack/attack':'Manipuliert','posthoc_clean/clean':'Sauber','german_test_primary':'Deutsches Testset'}

def build(source,admission,root):
 frozen=root/'experiments/jev_comparison';lock=load(frozen/'FILE_SHA256.json')
 require(hashlib.sha256((frozen/'FILE_SHA256.json').read_bytes()).hexdigest()=='c62021bbcb33b94c653cc9649d7d06dcbdf1633d4dc7b7f19dee2db2cb8be2f4','Frozen comparison lock changed')
 for name,sha in lock.items():require(hashlib.sha256((frozen/name).read_bytes()).hexdigest()==sha,'Frozen comparison source changed')
 audit=load(source/'audit.json');verification=load(source/'verification.json');summary=load(source/'scoring/comparison_summary.json')
 require(audit['status']=='passed' and audit['cases_observed']==974 and audit['strict_valid']==937 and audit['technical_failed']==37 and audit['missing']==0,'Completed Jev audit differs')
 require(verification['local_audit_passed'] and verification['local_scorer_outputs_identical_to_ci'],'Jev reproduction verification missing')
 native=index(lines(source/'run/predictions.jsonl'),lambda r:(r['suite'],r['id']));flags=index(lines(source/'run/flagged_native.jsonl'),lambda r:(r['suite'],r['id']));scored=index(lines(source/'scoring/case_comparison.jsonl'),lambda r:(r['suite'],r['id']))
 require(len(native)==len(scored)==974 and len(flags)==35 and native.keys()==scored.keys(),'Jev observation inventory differs')
 output=[];partitions=defaultdict(list)
 for suite in load(frozen/'manifest.json')['suites']:
  sid=suite['id'];folder=frozen/'inputs'/sid;requests=index(lines(folder/'requests.jsonl'),lambda r:r['id']);gold=index(lines(folder/'gold.jsonl'),lambda r:r['id']);baseline=index(lines(folder/'predictions.jsonl'),lambda r:r['id']) if (folder/'predictions.jsonl').is_file() else {}
  for ident,q in requests.items():
   key=(sid,ident);p=native[key];score=scored[key];request=q['request'];expected=gold[ident]['expected'];valid=p['status']=='valid';predicted=None;probabilities=None
   require(expected==score['expected'] and set(expected)==set(request['questions']),'Jev gold/schema mismatch')
   if valid:
    require(p['provider_model']=='jev-1.13.0' and set(p['answers'])==set(request['questions']) and set(p['probabilities_unrounded'])==set(request['questions']),'Jev native field/model mismatch')
    require(p['request_body_sha256']==digest({**request,'model':'jev-1.13.0'}) and p['source_request_sha256']==digest(request),'Jev native request linkage mismatch')
    predicted={};probabilities=p['probabilities_unrounded']
    for field,question in request['questions'].items():
     a=p['answers'][field];v=probabilities[field]
     require(a['type']=='choice' and set(v)==set(question['criteria']) and a['probabilities']==v,'Jev native option maps differ')
     require(all(type(x)in(int,float) and math.isfinite(x) and 0<=x<=1 for x in v.values()) and abs(math.fsum(v.values())-1)<=1e-5,'Jev strict vector differs')
     require(a['choice'] in v and v[a['choice']]==max(v.values()) and type(a['confidence'])in(int,float) and math.isfinite(a['confidence']) and 0<=a['confidence']<=1,'Jev choice/confidence differs')
     predicted[field]=a['choice']
    require(all(type(p['usage'][k])is int and p['usage'][k]>=0 for k in ('input_tokens','output_tokens')) and p['usage']['input_tokens']<=65536,'Jev billing contract differs')
   exact=valid and predicted==expected
   require(score['choices']['jev']==predicted and score['exact']['jev']==(exact if valid else None),'Jev scored result differs from original observations')
   clef=baseline.get(ident);clef_choice={f:a['choice'] for f,a in clef['answers'].items()} if clef else None
   require(score['choices']['clef']==clef_choice and score['exact']['clef']==(clef_choice==expected if clef else None),'Clef baseline comparison differs')
   group=sid+' / '+score['split'];row={'id':sid+' / '+ident,'input':request['state'],'questions':request['questions'],'expected':expected,'prediction':predicted,'probabilities':probabilities,'valid':valid,'correct':exact,'group':group,'source':{'suite':sid,'split':score['split'],'native_case_id':ident,'model':'jev-1.13.0'}}
   if valid:row['native_answers']=p['answers']
   else:
    row['technical_note']='Nach dem eingefrorenen lokalen Antwortvertrag ausgeschlossen; keine gewertete Modellantwort.'
    if key in flags:
     flag=flags[key];require(flag['strict_scoring_eligible'] is False and p['error_code']=='probability_sum_outside_tolerance','Quarantine scope differs')
     row['technical_note']='Native Wahrscheinlichkeitssumme außerhalb der lokalen Toleranz 1e-5. Unverändert aufbewahrt, nicht normalisiert und nicht als richtig oder falsch bewertet.'
     row['native_quarantine']={'answers':flag['answers'],'probabilities_unrounded':flag['probabilities_unrounded'],'diagnostic':flag['diagnostic'],'strict_scoring_eligible':False}
    else:row['technical_note']='Historischer technischer Ausschluss; die ursprüngliche Antwort wurde nicht vollständig gespeichert.'
   if clef:row['baseline_result']={'model':'Clef','prediction':clef_choice,'probabilities_unrounded':clef['probabilities_unrounded'],'correct':clef_choice==expected}
   output.append(row);partitions[(sid,score['split'])].append(score)
 comparisons=[];labels={}
 for part in summary['partitions']:
  key=(part['suite'],part['split']);cases=partitions[key];matched=[r for r in cases if r['choices']['clef'] is not None and r['choices']['jev'] is not None];observed=[r for r in cases if r['choices']['jev'] is not None]
  require(len(cases)==part['expected'] and len(matched)==part['both_valid'] and len(observed)==part['jev_valid'],'Partition coverage differs')
  jev=sum(r['exact']['jev'] is True for r in matched);clef=sum(r['exact']['clef'] is True for r in matched);standalone=sum(r['exact']['jev'] is True for r in observed)
  require(standalone==part['jev_correct'],'Jev per-partition correct count differs')
  label=LABELS[key[0]]+' · '+SPLITS.get(key[1],key[1]);labels[key[0]+' / '+key[1]]=label
  comparisons.append({'suite':key[0],'split':key[1],'label':label,'matched':len(matched),'clef_correct':clef if matched else None,'jev_correct':jev if matched else None,'jev_valid':len(observed),'expected':len(cases),'jev_correct_valid_only':standalone,'baseline_ready':part['baseline_status']=='complete','primary':key[0] in ('multidoc48','clarification72','minimal_pairs48')})
 require(len(output)==974 and sum(r['valid'] for r in output)==937 and sum(r['valid'] is False for r in output)==37,'Jev display totals differ')
 return {'format_version':1,'id':'jev974','status':'completed','model_label':'Jev','normalization_rule':'inclusive','audit':{'status':'passed','source_manifest_sha256':admission['sha256']},'metrics':[{'kind':'ratio','label':'Bearbeitete Anfragen','numerator':974,'denominator':974,'unit':'Anfragen'},{'kind':'ratio','label':'Streng gültig','numerator':937,'denominator':974,'unit':'Jev-Antworten'},{'kind':'ratio','label':'Technisch ausgeschlossen','numerator':37,'denominator':974,'unit':'Jev-Antworten'}],'findings':['35 ausgeschlossene Summenabweichungen sind als native Werte erhalten. Die zwei älteren technischen Fehler bleiben gesondert dokumentiert.'],'limitations':['Die Summenregel ist eine lokale Benchmarkentscheidung, keine bestätigte Anbietergarantie. Ausschlüsse sind keine beobachteten semantischen Fehler.','Direkte Vergleiche verwenden ausschließlich gemeinsam gültige Fälle je Teilgruppe. Unbekannte oder fehlende Clef-Baselines werden nicht als null richtige Antworten angezeigt.','Andere Hardware, Präzision und Messgrenzen; keine gemeinsame Laufzeitkennzahl oder Signifikanzbehauptung.'],'comparisons':comparisons,'group_labels':labels,'cases':output}
