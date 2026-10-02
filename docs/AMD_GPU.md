# Optionale AMD-GPU-Inferenz

Stand der Quellenprüfung: **2. Oktober 2026**. Dies ist vorbereiteter Code mit modellfreien Tests, **kein erfolgreicher Clef-Lauf auf AMD-Hardware**. Das konkrete Rechner-, Prozessor-, Betriebssystem- und Speichermodell muss vor einer Installation geprüft werden. Aus einer Produktbezeichnung wie „Ryzen AI Max“ allein folgt keine verifizierte Systemkonfiguration.

Der neue Pfad nutzt die **Radeon-GPU über ROCm/PyTorch**, einschließlich einer unterstützten integrierten Radeon-GPU. Er nutzt **nicht die Ryzen-AI-NPU**. Eine NVIDIA-, DirectML-, Vulkan- oder NPU-Implementierung ist nicht enthalten.

## Drei explizite Profile

| Serveroption | Berechnung | Status |
| --- | --- | --- |
| `--inference-profile cpu-nf4` | CPU, NF4-Backbone, BF16-Head und lexikalisches Output-Embedding | Bisheriger Standard; ursprüngliche Benchmark-Konfiguration |
| `--inference-profile rocm-bf16` | AMD GPU, native BF16-Gewichte | Vorbereitet, Hardwareausführung nicht validiert |
| `--inference-profile rocm-fp16` | AMD GPU, explizite FP16-Konvertierung der Release-Gewichte | Vorbereitet, Hardwareausführung und numerische Stabilität nicht validiert |

Alle Profile verwenden denselben gepinnten vollständigen Release, denselben originalen Joint-Schema-Head und dasselbe lexikalische Output-Embedding. Es wird weder ein Textgenerator als Ersatz verwendet noch das Vision-Backbone entfernt. Der Playground bleibt auf Text beschränkt. Bei den GPU-Profilen müssen alle Modellparameter, einschließlich Head und Output-Embedding, dem ausdrücklich gewählten BF16-/FP16-Datentyp entsprechen. Temporäre FP32-Operatorberechnungen des Originalmodells sind davon unabhängig und bleiben erhalten.

BF16 ist der erste GPU-Versuch, weil dies der Release-Datentyp ist. FP16 ist eine eigene, explizite Versuchskonfiguration: Bei Überläufen oder ungültigen Wahrscheinlichkeiten wird keine Antwort ausgegeben. Die FP16-Option ist keine Zusage gleicher Qualität.

Es gibt **keinen automatischen Fallback**. Ein ROCm-Profil verlangt `torch.version.hip`, eine erreichbare GPU und ausreichend gemeldeten freien GPU-Speicher. NVIDIA-CUDA allein erfüllt das nicht. PyTorch verwendet auch bei AMD die Namen `torch.cuda` und `cuda:0`; das ist kein Nachweis einer NVIDIA-GPU. Siehe [PyTorch: HIP-Semantik](https://docs.pytorch.org/docs/2.14/notes/hip.html).

## Betriebssystem, Treiber und passende Pakete

Die [vereinheitlichte AMD-Kompatibilitätsmatrix für ROCm 10.0.0](https://rocm.docs.amd.com/en/docs-10.0.0/compatibility/compatibility-matrix.html) (Datumsangabe 25. August 2026) führt Ryzen-AI-Max-/Strix-Halo-Grafik unter `gfx1151`. Für Ryzen-APUs nennt sie Ubuntu 26.04 mit GA-Kernel 7.0 bzw. Ubuntu 24.04.4 mit OEM-Kernel 6.17, den passenden Inbox-Kerneltreiber sowie Windows 11 25H2 mit Adrenalin 26.8.1. Vor Einrichtung im Selektor das **exakte** Gerät und Betriebssystem wählen.

- **Linux Mint:** wird in dieser Ryzen-Matrix nicht als unterstütztes Betriebssystem genannt. Eine Ubuntu-Basis macht Mint nicht automatisch zu einer von AMD validierten Kombination. Ubuntu-Installationsbefehle nicht ungeprüft auf Mint übertragen. Benötigt werden zusammenpassende Firmware, Kernel, AMD-Treiber, Geräteberechtigungen und ROCm-PyTorch-Pakete.
- **Linux:** Die [AMD-Installationsanleitung](https://rocm.docs.amd.com/en/docs-10.0.0/install/rocm.html) enthält in ihrem OEM-Abschnitt noch 6.14 bzw. „6.14 oder neuer“. Das ist nicht dieselbe präzise Kombination wie die Matrix. Maßgeblich ist die für das konkrete Gerät und die gewählte Release-Version dokumentierte Kombination; kein pauschaler Kernelwechsel ist Teil dieses Projekts.
- **Windows:** native AMD-Wheels und Windows-Treiber verwenden; eine Linux-Umgebung oder WSL ist ein eigener Installationspfad. WSL-Unterstützung nicht aus allgemeiner Windows-Unterstützung ableiten. Alte HIP-SDK-, aktuelle ROCm- und PyTorch-Pakete nicht beliebig mischen.
- Es gibt hier **keinen Treiberinstaller, keine BIOS-/TTM-Änderung, keine Änderung von GPU-Gruppen oder Sicherheitseinstellungen**. Solche Schritte sind gesonderte Systemadministration. Auch wenn eine externe Anleitung Änderungen an Schutzfunktionen nennt, führt dieses Projekt sie nicht aus.

Die [ältere Radeon-/Ryzen-Dokumentation](https://rocm.docs.amd.com/projects/radeon-ryzen/en/latest/index.html) verweist für neuere Releases auf die vereinheitlichten ROCm-Seiten. „latest“ im alten URL-Pfad bedeutet daher nicht die neueste Installationsanleitung. Nightly-, Preview- und `main`-Dokumentation sind kein Ersatz für eine ausgewählte stabile Release.

## Speicher realistisch planen

Das [lokale Release-Indexfile](../runtime/model.safetensors.index.json) nennt rund **18,82 GB Backbone-Gewichte**; dazu kommen etwa **0,24 GB Head-Datei**. Native BF16/FP16 braucht erheblich mehr Speicher als CPU-NF4. Aktivierungen, temporäre Operatorpuffer, Treiber, Betriebssystem und Browser benötigen zusätzlich Platz.

Bei einer APU teilen CPU und GPU physischen RAM. **64 GB System-RAM sind nicht automatisch 64 GB verfügbarer GPU-Speicher.** Treiber-/Firmware-Zuweisung und gemeinsam nutzbarer Speicher begrenzen die tatsächlich nutzbare Menge. AMD beschreibt Windows-Grafikspeicherzuweisung und Linux-TTM-Speicher separat im [PyTorch-Playbook](https://developer.amd.com/playbooks/pytorch-rocm-llms/); dessen Halo-Standardwerte lassen sich nicht auf jeden Mini-PC übertragen.

Der Adapter prüft vor einem GPU-Ladevorgang mindestens **22 GiB von ROCm gemeldeten freien GPU-Speicher** und **2 GiB verfügbaren System-RAM**. Das sind konservative Startschranken, keine gemessene Clef-Anforderung und keine Erfolgsgarantie. Bei einer APU können sich diese Speicherangaben überlappen; sie dürfen nicht zu zusätzlichem physischem RAM addiert werden. 24 GiB oder mehr wirklich nutzbarer GPU-Speicher plus Reserven für den Rest des Rechners sind eine Planungshilfe, kein validierter Mindestwert. CPU-NF4 behält seine bisherige 7,5-GiB-System-RAM-Prüfung.

Einen bereits laufenden Modellprozess zuerst regulär beenden; keinen zweiten Modell-Ladevorgang parallel zu Benchmark oder Live-Server starten. Ein großes Browserfenster oder andere Modelle können den verfügbaren RAM stark reduzieren. Das Projekt beendet keine fremden Prozesse.

## Separate Python-Umgebung vorbereiten

Diese Schritte sind zur späteren manuellen Ausführung auf einem zuvor geprüften System gedacht. Für dieses Feature wurden **weder Pakete auf einem Benutzerrechner installiert noch Treiber geändert**.

1. Eine getrennte Umgebung mit einer von AMD unterstützten Python-Version anlegen. Die ursprüngliche CPU-Umgebung für Reproduktionen behalten.
2. ROCm-PyTorch und **passendes Torchvision** anhand der aktuellen offiziellen AMD-Anleitung für Gerät/OS installieren. Der Clef-Prozessor benötigt Torchvision auch beim Text-Playground.
3. Erst danach die Anwendungsabhängigkeiten aus `runtime/requirements_rocm.txt` installieren. Diese Datei ist eine vorgeschlagene Anwendungskonfiguration, **kein auf GPU validierter vollständiger Lockfile**. `runtime/requirements_frozen.txt` und `runtime/setup_runtime.sh` gehören zur CPU-Reproduktion und würden CPU-Torch installieren.

Beispiel für die Python-Umgebung unter Linux, ohne Treiberinstallation:

```bash
python3 -m venv .venv-rocm
.venv-rocm/bin/python -m pip --version
# Hier zuerst das für Gerät/OS verifizierte AMD-Torch/Torchvision-Paar installieren.
.venv-rocm/bin/python -m pip install -r runtime/requirements_rocm.txt
.venv-rocm/bin/python -m pip check
```

Unter Windows funktioniert die Umgebung ohne PowerShell-Aktivierung und ohne Änderung der Execution Policy:

```powershell
python -m venv .venv-rocm
.venv-rocm\Scripts\python.exe -m pip --version
# Hier zuerst das passende native Windows-Paar von AMD installieren.
.venv-rocm\Scripts\python.exe -m pip install -r runtime/requirements_rocm.txt
.venv-rocm\Scripts\python.exe -m pip check
```

Zur Orientierung: Das [AMD-PyTorch-Playbook, zuletzt validiert August 2026](https://developer.amd.com/playbooks/pytorch-rocm-llms/), nennt für `gfx1151` zum Prüfdatum `torch[device-gfx1151]==2.13.0+rocm10.0.0` und `torchvision[device-gfx1151]==0.28.0+rocm10.0.0` aus `https://stable.repo.amd.com/rocm/whl-next/`. Das ist eine AMD-Quellenangabe, **kein hier getesteter Installationsbefehl**. Nicht ungeprüft übernehmen, wenn System, Python-Version oder AMD-Anleitung abweichen; keine Nightly-Wheels als stabile Standardinstallation ausgeben.

Die GPU-Profile verwenden bewusst **kein bitsandbytes**. Die [stabile bitsandbytes-0.50.2-Anleitung](https://huggingface.co/docs/bitsandbytes/v0.50.2/en/installation) dokumentiert inzwischen ROCm-Pakete für verschiedene Ziele; daraus folgt nicht, dass jede vorhandene CPU-/CUDA-Installation oder Paketkombination auf einer bestimmten AMD-GPU funktioniert. Das [main-Handbuch](https://huggingface.co/docs/bitsandbytes/main/en/installation) ist separat als Entwicklungsstand gekennzeichnet. AMD-NF4 wäre ein eigener, noch nicht validierter Profilpfad.

## Prüfen und dann ausdrücklich starten

Alle folgenden Befehle werden aus dem Repository-Hauptverzeichnis ausgeführt. Unter Windows `.venv-rocm/bin/python` durch `.venv-rocm\Scripts\python.exe` ersetzen.

```bash
# Geräte-/Speicherprüfung, kein Modell und keine Modellgewichte:
.venv-rocm/bin/python -m runtime.check_backend --profile rocm-bf16

# Optional: winzige Matrixmultiplikation auf dem ausgewählten Gerät:
.venv-rocm/bin/python -m runtime.check_backend --profile rocm-bf16 --test-kernel

# Erst nach erfolgreicher Prüfung; identischer gepinnter Modellordner:
.venv-rocm/bin/python server.py --enable-inference --model-dir runtime/model --inference-profile rocm-bf16
```

`runtime/check_backend.py` lädt kein Clef-Modell und installiert nichts. Erfolg der winzigen Matrixmultiplikation beweist **nicht**, dass alle Qwen-/Clef-Operatoren funktionieren. Fehlende Operatoren, Speicherfehler oder inkompatible Pakete können beim tatsächlichen Laden/Forward weiterhin auftreten. Die erste Playground-Anfrage verifiziert alle gepinnten Dateien und lädt erst dann das Modell; ein fehlender Modellordner wird nicht automatisch heruntergeladen. Den bestehenden expliziten [Downloadablauf](../README.md#echte-lokale-inferenz-aktivieren) verwenden.

Bei mehreren sichtbaren GPUs wählt `--device-index 1` die zweite GPU. Der Wert bezieht sich auf die für den Prozess sichtbare Reihenfolge. FP16 muss ausdrücklich mit `--inference-profile rocm-fp16` bzw. beim Check mit `--profile rocm-fp16` gewählt werden. Für den CPU-Standard den alten Befehl verwenden oder `--inference-profile cpu-nf4` setzen. Dafür ist die separat eingerichtete CPU-Umgebung vorgesehen.

## Was Anzeige, Messung und Tests aussagen

- Vor dem Laden zeigt die UI nur das **angeforderte Profil**. Erst nach Prüfung der tatsächlichen Parameterplatzierung werden Gerät, Name, Backend und Präzision als geladen angezeigt.
- Live-Antworten enthalten `runtime` mit Profil, Backend, Gerät, Architektur (wenn vom Treiber verfügbar), Torch-/HIP-Version und der freien GPU-Speichermenge vor dem Laden. Das sind Laufzeitangaben, keine aktualisierten Benchmark-Scores.
- Der Forward-Timer wartet vor und nach GPU-Arbeit auf Synchronisation. Er umfasst keine Dateiprüfung, Modellladezeit oder Tokenisierung. Der erste Forward kann zusätzliche Initialisierung enthalten; für Leistungsbewertungen separate Warm-ups und wiederholte Messungen einplanen.
- Die **280 eingefrorenen Antworten bleiben unverändert**. GPU-BF16, GPU-FP16 und CPU-NF4 sind verschiedene Konfigurationen. Weder Genauigkeit noch Laufzeit der alten CPU-Ergebnisse darf als GPU-Ergebnis ausgegeben werden.
- Modellfreie Mocktests prüfen Profilwahl, fehlendes HIP, unerreichbare GPUs, falsche Geräteindizes, Speichergrenzen, explizite FP16-Wahl, Erhalt von Head/Embedding, keine versteckte CPU-Auslagerung, GPU-Timersynchronisation und API-/UI-Kennzeichnung.
- Nicht validiert: echter AMD-Ladevorgang, Clef-Forward auf ROCm, Leistungsgewinn, GPU-Genauigkeit, Windows-Lauf, Linux-Mint-Lauf und Live-Browserdarstellung auf diesen Systemen. Keine dieser Stufen wird durch Mocktests ersetzt.
