#!/usr/bin/env python3
"""Generate post-run prose without changing frozen inputs, scoring or outputs."""
from pathlib import Path
import subprocess,sys
R=Path(__file__).resolve().parents[1]
subprocess.run([sys.executable,str(R/'scripts/build_reports.py')],check=True)
p=R/'REPORT.md';s=p.read_text()
s=s.replace('Die Goldantworten wurden vor dem Lauf von einer anderen KI geprüft und nach zwei gefundenen Formulierungsproblemen korrigiert.','Die Goldantworten wurden vor dem Lauf von einer anderen KI geprüft; zwei Formulierungsprobleme in den Eingaben wurden korrigiert, die Labels blieben unverändert.')
addition='''Die 0,90-Schwelle erfasst nur 5 von 72 Testfällen (5 von 37 konkreten Modellantworten); bei 0,95 bleibt gar keine konkrete Antwort übrig. Null Fehler in so wenigen ausgewählten Fällen sind kein Zuverlässigkeits- oder Sicherheitsnachweis. Eine falsche Antwortaktion im unklaren Kontoauszug-Fall hatte bereits einen Score von 0,864; die gleichzeitig falsche Ja-Feststellung hatte 0,742. Die Zwei-Feld-Schwelle darf daher nicht als Aussage über jeden einzelnen hohen Feldscore gelesen werden.

## Beobachtetes Fehlermuster

Alle acht nicht in beiden Feldern korrekten Fälle liegen in zwei Gruppen: fünf Fälle mit unbestimmtem Zielvorgang und drei beantwortbare Fälle trotz einer Lücke. Bei vier unbestimmten Zielvorgängen wählte Clef eine Antwortaktion, obwohl zuerst geklärt werden musste, welcher Vorgang gemeint war. Bei zwei logisch bereits entschiedenen Nein-Fällen fragte es unnötig nach weiteren Angaben. Im Giro-Entgeltfall antwortete es fälschlich Ja, obwohl ausdrücklich kein Gehalt, sondern nur eine private Rückzahlung eingegangen war.

Die drei inkonsistenten Feldpaare sind zusätzlich wichtig: Eine Anfrage kann zugleich eine Rückfrageaktion und eine konkrete Feststellung erhalten oder eine Antwortaktion und „unresolved“. Strukturell gültige Einzelfelder garantieren keine gemeinsame inhaltliche Konsistenz. Der native Output wurde weder repariert noch durch nachgelagerte Regeln ersetzt.

'''
s=s.replace('## Teilgruppen\n',addition+'## Teilgruppen\n');p.write_text(s)
