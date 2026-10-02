"""Separate new-input live adapter smoke, excluded from all benchmark scores."""
from pathlib import Path
import importlib.util,json,time
P=Path(__file__).resolve().parent
file=P/'live_adapter.py'
if not file.exists():
 file=P.parent/'project/runtime/live_adapter.py'
spec=importlib.util.spec_from_file_location('clef_live_adapter_smoke',file)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
runtime=module.ClefRuntime(P/'model')
request={'model':'clef-flash','state':'Das Paket wurde noch nicht versandt. Bitte ändern Sie die Lieferadresse von Büro auf Privatadresse; am Produkt und am Preis soll sich nichts ändern.','questions':{'decision':{'type':'choice','instructions':'Welche Abteilung soll dieses Anliegen bearbeiten?','criteria':{'logistics':'Versand, Lieferadresse und Paketbeförderung','billing':'Rechnungen, Abbuchungen und Erstattungen','technical':'Fehlfunktionen des Produkts oder der Anwendung'}}}}
print('Before',runtime.status(),flush=True)
started=time.perf_counter();response=runtime.infer(request);elapsed=time.perf_counter()-started
result={'purpose':'new-input live adapter smoke only, excluded from all benchmark metrics','request':request,'response':response,'status':runtime.status(),'total_elapsed_seconds':elapsed}
assert response['benchmark_result'] is False and response['truncated'] is False
assert set(response['probabilities_unrounded']['decision'])==set(request['questions']['decision']['criteria'])
(P/'live_adapter_smoke.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
