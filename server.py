"""Private, loopback-only Clef workbench. Python 3.12; no web dependencies."""
from __future__ import annotations
import argparse
import importlib
import json
import math
import re
import threading
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

from runtime.device_profiles import BackendUnavailable, PROFILES, validate_profile
from runtime.model_registry import MODEL_KEYS, DEFAULT_MODEL, get_model

ROOT = Path(__file__).resolve().parent
MAX_BODY = 32768
MAX_QUESTIONS = 8
ID = re.compile(r'^[A-Za-z][A-Za-z0-9_-]{0,63}$')
MIME = {'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json; charset=utf-8','.svg':'image/svg+xml'}

def validate_request(value):
    if not isinstance(value, dict) or set(value) != {'state', 'questions'}:
        raise ValueError('Erwartet werden ausschließlich state und questions.')
    if not isinstance(value['state'], str) or not value['state'].strip() or len(value['state']) > 6000:
        raise ValueError('Der Eingabetext muss 1 bis 6.000 Zeichen enthalten.')
    qs = value['questions']
    if not isinstance(qs, dict) or not 1 <= len(qs) <= MAX_QUESTIONS:
        raise ValueError(f'Dieser Playground unterstützt 1 bis {MAX_QUESTIONS} choice-Fragen.')
    for name, q in qs.items():
        if not isinstance(name, str) or not ID.fullmatch(name) or not isinstance(q, dict) or set(q) != {'type','instructions','criteria'}:
            raise ValueError('Ungültige Frage. Erwartet: type, instructions, criteria.')
        if q['type'] != 'choice':
            raise ValueError('Nur der native Fragetyp choice wird unterstützt.')
        if not isinstance(q['instructions'], str) or not q['instructions'].strip() or len(q['instructions']) > 4000:
            raise ValueError('Die Richtlinie muss 1 bis 4.000 Zeichen enthalten.')
        if not isinstance(q['criteria'], dict) or not 2 <= len(q['criteria']) <= 12:
            raise ValueError('Es sind 2 bis 12 Auswahlklassen erforderlich.')
        for key, description in q['criteria'].items():
            if not isinstance(key, str) or not ID.fullmatch(key) or not isinstance(description, str) or not description.strip() or len(description) > 300:
                raise ValueError('Klassen brauchen eine kurze ID und eine Beschreibung (1–300 Zeichen).')
    return {'model':'clef-flash', **value}

def unique_json_object(pairs):
    """Never silently replace a repeated question, option, or input key."""
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError('Doppelte JSON-Schlüssel sind nicht erlaubt.')
        value[key] = item
    return value

def validate_result(request, result):
    """An incomplete runtime result must never become a successful live response."""
    questions = request['questions']
    if not isinstance(result, dict):
        raise RuntimeError('Runtime returned an invalid response')
    for field in ('answers', 'probabilities_unrounded'):
        if not isinstance(result.get(field), dict) or list(result[field]) != list(questions):
            raise RuntimeError('Runtime returned missing, extra, or reordered question answers')
    for name, question in questions.items():
        answer = result['answers'][name]
        probabilities = result['probabilities_unrounded'][name]
        if not isinstance(answer, dict) or answer.get('type') != 'choice' or answer.get('choice') not in question['criteria']:
            raise RuntimeError('Runtime returned an invalid choice answer')
        if not isinstance(probabilities, dict) or set(probabilities) != set(question['criteria']):
            raise RuntimeError('Runtime returned incomplete option probabilities')
        values = list(probabilities.values())
        if not all(isinstance(value, (int, float)) and not isinstance(value, bool)
                   and math.isfinite(value) and 0 <= value <= 1 for value in values) or abs(sum(values) - 1) > 1e-5:
            raise RuntimeError('Runtime returned invalid option probabilities')

class Workbench:
    def __init__(self, enabled=False, model_dir=None, factory=None,
                 profile='cpu-nf4', device_index=0, model_key=DEFAULT_MODEL):
        validate_profile(profile, device_index)
        self.model_spec = get_model(model_key)
        self.model_key = model_key
        self.enabled = enabled
        self.model_dir = model_dir
        self.factory = factory
        self.profile = profile
        self.device_index = device_index
        self.runtime = None
        self.lock = threading.Lock()
        self.last_error = None
    def health(self):
        status = self.runtime.status() if self.runtime and hasattr(self.runtime, 'status') else {}
        return {'inference_enabled':self.enabled,'model_loaded':status.get('state') == 'ready',
                'busy':self.lock.locked(),'mode':f'local_{self.profile.replace("-", "_")}' if self.enabled else 'results_only',
                'requested_profile':self.profile if self.enabled else None,
                'runtime_state':status.get('state', 'unloaded'),
                'runtime':status.get('runtime'),
                'model_key':self.model_key, 'model_id':self.model_spec['repo_id'],
                'model':self.model_spec['repo_id'], 'model_size':self.model_spec['model_size'],
                'revision':self.model_spec['revision']}
    def infer(self, request):
        if not self.enabled:
            return 503, {'error':'Live-Inferenz ist deaktiviert. Starte den Server explizit mit --enable-inference und --model-dir.'}
        if not self.lock.acquire(blocking=False):
            return 409, {'error':'Das Modell bearbeitet bereits eine Anfrage. Bitte warte auf deren Abschluss.'}
        try:
            if self.runtime is None:
                factory = self.factory or importlib.import_module('runtime.live_adapter').ClefRuntime
                # Preserve the one-argument factory contract for the old default.
                if self.model_key == DEFAULT_MODEL:
                    self.runtime = (factory(self.model_dir) if self.profile == 'cpu-nf4' else
                                    factory(self.model_dir, profile=self.profile, device_index=self.device_index))
                else:
                    self.runtime = factory(self.model_dir, profile=self.profile,
                                           device_index=self.device_index, model_key=self.model_key)
            result = self.runtime.infer(request)
            validate_result(request, result)
            return 200, {'source':'live_local_inference', 'model_key':self.model_key,
                         'model_id':self.model_spec['repo_id'], 'model':self.model_spec['repo_id'],
                         'revision':self.model_spec['revision'], 'requested_profile':self.profile, **result}
        except ValueError as error:
            return 422, {'error':str(error)}
        except BackendUnavailable as error:
            return 503, {'error':str(error), 'requested_profile':self.profile}
        except Exception:
            # Do not disclose filesystem locations or stack traces to the browser.
            import traceback
            traceback.print_exc()
            return 500, {'error':'Lokale Inferenz fehlgeschlagen. Details stehen im Server-Terminal. Es wurde kein Ergebnis erzeugt.'}
        finally:
            self.lock.release()

class Handler(BaseHTTPRequestHandler):
    server_version = 'ClefWorkbench/1.0'
    def __init__(self, *args, app, web_root, **kwargs):
        self.app, self.web_root = app, web_root.resolve()
        super().__init__(*args, **kwargs)
    def setup(self):
        super().setup()
        self.connection.settimeout(15)
    def log_message(self, format, *args):
        # Never log request bodies or user text.
        super().log_message(format, *args)
    def allowed_host(self):
        host = self.headers.get('Host','')
        port = self.server.server_address[1]
        return host in {f'127.0.0.1:{port}', f'localhost:{port}'}
    def respond(self, status, payload, content_type='application/json; charset=utf-8'):
        data = json.dumps(payload, ensure_ascii=False).encode() if isinstance(payload, dict) else payload
        self.send_response(status)
        self.send_header('Content-Type',content_type)
        self.send_header('Content-Length',str(len(data)))
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Referrer-Policy','no-referrer')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'")
        self.end_headers()
        try: self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError): pass
    def do_GET(self):
        if not self.allowed_host(): return self.respond(403, {'error':'Nur lokaler Zugriff ist erlaubt.'})
        path = unquote(urlsplit(self.path).path)
        if path == '/api/health': return self.respond(200,self.app.health())
        if path.startswith('/api/'): return self.respond(404,{'error':'Unbekannter Endpunkt.'})
        path = '/index.html' if path == '/' else path
        target = (self.web_root / path.lstrip('/')).resolve()
        if not target.is_relative_to(self.web_root) or target.suffix not in MIME or not target.is_file():
            return self.respond(404, {'error':'Datei nicht gefunden.'})
        self.respond(200, target.read_bytes(), MIME[target.suffix])
    def do_POST(self):
        if not self.allowed_host(): return self.respond(403, {'error':'Nur lokaler Zugriff ist erlaubt.'})
        if self.path != '/api/infer': return self.respond(404, {'error':'Unbekannter Endpunkt.'})
        origin = self.headers.get('Origin')
        if origin and origin != 'http://' + self.headers.get('Host',''):
            return self.respond(403, {'error':'Fremde Webseiten dürfen keine Inferenz auslösen.'})
        if self.headers.get('X-Clef-Request') != '1' or self.headers.get('Content-Type','').split(';')[0] != 'application/json':
            return self.respond(415, {'error':'JSON und X-Clef-Request: 1 sind erforderlich.'})
        try:
            size = int(self.headers.get('Content-Length','0'))
            if not 0 < size <= MAX_BODY: return self.respond(413,{'error':'Anfrage zu groß oder leer (max. 32 KiB).'})
            value = json.loads(self.rfile.read(size), object_pairs_hook=unique_json_object)
            request = validate_request(value)
        except (ValueError, TypeError, UnicodeDecodeError):
            return self.respond(400,{'error':'Ungültige Anfrage. Prüfe Eingabe und choice-Schema (Limits siehe README).'})
        status, result = self.app.infer(request)
        self.respond(status, result)
    def do_OPTIONS(self): self.respond(403,{'error':'Cross-Origin-Anfragen werden nicht unterstützt.'})

def make_server(port=8765, app=None, web_root=None):
    handler = partial(Handler,app=app or Workbench(),web_root=web_root or ROOT/'web')
    server = ThreadingHTTPServer(('127.0.0.1', port), handler)
    server.daemon_threads = True
    return server

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',type=int,default=8765)
    parser.add_argument('--enable-inference',action='store_true',help='Lazily load the locally downloaded, pinned Clef model')
    parser.add_argument('--model-dir',type=Path,help='Directory from runtime/download_model.py; never downloaded automatically')
    parser.add_argument('--inference-profile',choices=PROFILES,default='cpu-nf4',help='Explicit CPU NF4 or experimental native AMD ROCm BF16/FP16; no automatic fallback')
    parser.add_argument('--model', choices=MODEL_KEYS, default=DEFAULT_MODEL, help='Server-fixed model; Flash 9B default, Clef 27B explicit opt-in. No automatic download or fallback.')
    parser.add_argument('--device-index',type=int,default=0,help='Visible ROCm GPU index (default: 0)')
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535: parser.error('Use a port from 1024 through 65535.')
    if args.enable_inference and (not args.model_dir or not args.model_dir.is_dir()):
        parser.error('--enable-inference requires an existing --model-dir.')
    try:
        validate_profile(args.inference_profile, args.device_index)
    except ValueError as error:
        parser.error(str(error))
    server = make_server(args.port, Workbench(args.enable_inference,args.model_dir,
                         profile=args.inference_profile,device_index=args.device_index,model_key=args.model))
    print(f'Clef Workbench: http://127.0.0.1:{args.port}',flush=True)
    print(f'Live inference enabled; model: {args.model}; requested profile: {args.inference_profile}. Device is verified only on first model load. See README and docs/AMD_GPU.md for memory requirements.' if args.enable_inference else 'Results-only mode. No model, GPU, network request, or additional packages required.',flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()

if __name__ == '__main__': main()
