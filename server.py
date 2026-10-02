"""Private, loopback-only Clef workbench. Python 3.12; no web dependencies."""
from __future__ import annotations
import argparse
import importlib
import json
import re
import threading
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent
MAX_BODY = 32768
ID = re.compile(r'^[A-Za-z][A-Za-z0-9_-]{0,63}$')
MIME = {'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json; charset=utf-8','.svg':'image/svg+xml'}

def validate_request(value):
    if not isinstance(value, dict) or set(value) != {'state', 'questions'}:
        raise ValueError('Erwartet werden ausschließlich state und questions.')
    if not isinstance(value['state'], str) or not value['state'].strip() or len(value['state']) > 6000:
        raise ValueError('Der Eingabetext muss 1 bis 6.000 Zeichen enthalten.')
    qs = value['questions']
    if not isinstance(qs, dict) or len(qs) != 1:
        raise ValueError('Dieser Playground unterstützt genau eine choice-Frage.')
    for name, q in qs.items():
        if not ID.fullmatch(name) or not isinstance(q, dict) or set(q) != {'type','instructions','criteria'}:
            raise ValueError('Ungültige Frage. Erwartet: type, instructions, criteria.')
        if q['type'] != 'choice':
            raise ValueError('Nur der native Fragetyp choice wird unterstützt.')
        if not isinstance(q['instructions'], str) or not q['instructions'].strip() or len(q['instructions']) > 4000:
            raise ValueError('Die Richtlinie muss 1 bis 4.000 Zeichen enthalten.')
        if not isinstance(q['criteria'], dict) or not 2 <= len(q['criteria']) <= 12:
            raise ValueError('Es sind 2 bis 12 Auswahlklassen erforderlich.')
        for key, description in q['criteria'].items():
            if not ID.fullmatch(key) or not isinstance(description, str) or not description.strip() or len(description) > 300:
                raise ValueError('Klassen brauchen eine kurze ID und eine Beschreibung (1–300 Zeichen).')
    return {'model':'clef-flash', **value}

class Workbench:
    def __init__(self, enabled=False, model_dir=None, factory=None):
        self.enabled = enabled
        self.model_dir = model_dir
        self.factory = factory
        self.runtime = None
        self.lock = threading.Lock()
        self.last_error = None
    def health(self):
        return {'inference_enabled':self.enabled,'model_loaded':bool(self.runtime and hasattr(self.runtime, 'status') and self.runtime.status().get('state') == 'ready'),'busy':self.lock.locked(),'mode':'local_cpu_nf4' if self.enabled else 'results_only','revision':'17f0b0ad64efb65d273590632833508766b2aae6'}
    def infer(self, request):
        if not self.enabled:
            return 503, {'error':'Live-Inferenz ist deaktiviert. Starte den Server explizit mit --enable-inference und --model-dir.'}
        if not self.lock.acquire(blocking=False):
            return 409, {'error':'Das Modell bearbeitet bereits eine Anfrage. Bitte warte auf deren Abschluss.'}
        try:
            if self.runtime is None:
                factory = self.factory or importlib.import_module('runtime.live_adapter').ClefRuntime
                self.runtime = factory(self.model_dir)
            result = self.runtime.infer(request)
            return 200, {'source':'live_local_inference','model':'Cloudflare/clef-flash','revision':self.health()['revision'], **result}
        except ValueError as error:
            return 422, {'error':str(error)}
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
            value = json.loads(self.rfile.read(size))
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
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535: parser.error('Use a port from 1024 through 65535.')
    if args.enable_inference and (not args.model_dir or not args.model_dir.is_dir()):
        parser.error('--enable-inference requires an existing --model-dir.')
    server = make_server(args.port, Workbench(args.enable_inference,args.model_dir))
    print(f'Clef Workbench: http://127.0.0.1:{args.port}',flush=True)
    print('Live inference enabled; ~19 GB local model download, ~8 GB free RAM recommended.' if args.enable_inference else 'Results-only mode. No model, GPU, network request, or additional packages required.',flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()

if __name__ == '__main__': main()
