<!-- Integration note: insert after the repository link in README.md. -->

## Mit einem Repository-Link vom Agenten einrichten lassen

Ein Agent findet den vollständigen Einstieg in [`AGENTS.md`](../AGENTS.md) und
[`docs/AGENT_SETUP.md`](AGENT_SETUP.md): Hardware-/Ressourcenprüfung als JSON,
explizite Profilwahl, isolierte gepinnte Umgebung, offizieller revisionsfester
Download, SHA-256-Prüfung und ein echter synthetischer Modell-Smoke.

```bash
# Erst nur prüfen: keine Installation, kein Download, kein Modellladen
python3 -m runtime.setup --plan --profile cpu-nf4
# Nach Freigabe und erfolgreicher Prüfung: ein Befehl für Setup + Verifikation + Smoke
python3 -m runtime.setup --profile cpu-nf4 --execute --smoke
```

`cpu-nf4` ist **9B mit 4-Bit-Backbone**; `cpu-bf16` ist **dasselbe 9B-Modell
unquantisiert** und noch nicht mit vollem Modell auf Zielhardware validiert.
Die vorbereiteten AMD-GPU-Profile brauchen zusätzlich eine passende separate
ROCm-Umgebung. Das größere **27B-Modell ist mit `--model clef-27b` ausdrücklich auswählbar**,
aber nie Standard; alle 27B-Pfade sind vorbereitet und hardwareunvalidiert.
Pro Modell ist der Download bei 4 Bit und unquantisiert gleich: **19,08 GB für
Flash 9B**, **54,99 GB für Clef 27B**. 4 Bit wird erst beim Laden erzeugt.
[Hardware-, RAM-/VRAM- und Festplattenempfehlungen](HARDWARE.md) unterscheiden
gemessene Werte von Schätzungen. Ein unbekanntes Betriebssystem, fehlende
Rechte oder Treiber lassen sich nicht seriös vollautomatisch übergehen.

<!-- When inserting in the repository-root README, change ../AGENTS.md to
AGENTS.md and AGENT_SETUP.md to docs/AGENT_SETUP.md. Also replace the old live
setup command block with the new documented workflow; retain the historical
scripts only as reproduction references. Mention cpu-bf16 in the live profile
summary; leave existing CPU-NF4 measured results unchanged. -->
