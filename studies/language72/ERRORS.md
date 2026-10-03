# Alle Goldabweichungen

8 Fälle mit mindestens einer Goldabweichung, unveränderte Goldlabels.

## gv_b4_canonical

Domäne: banking; Gruppe: invariant; Ansicht: canonical.

Regel: Ein fiktiver Archivauftrag ist genau dann freigegeben, wenn er geprüft ist. Bei mehreren möglichen Aufträgen muss der gemeinte Auftrag feststehen, sofern ihre Ergebnisse verschieden sind.

Nachricht: Archivauftrag A ist geprüft. Archivauftrag B ist nicht geprüft. Welchen der beiden ich meine, ist nicht festgelegt.

Frage: Ist der gemeinte Archivauftrag freigegeben?

Gold: {"action": "ask_target", "determination": "unresolved"}

Vorhersage: {"action": "ask_target", "determination": "no"}

Alle ungerundeten Wahrscheinlichkeiten: {"action": {"answer": 0.21737508475780487, "ask_fact": 0.2846201956272125, "ask_target": 0.47664913535118103, "resolve_conflict": 0.021355556324124336}, "determination": {"no": 0.5472790002822876, "unresolved": 0.3652791678905487, "yes": 0.08744187653064728}}

Technische Probleme: []

## gv_b4_typo

Domäne: banking; Gruppe: invariant; Ansicht: typo.

Regel: Ein fiktiver Archivauftrag ist genau dann freigegeben, wenn er geprüft ist. Bei mehreren möglichen Aufträgen muss der gemeinte Auftrag feststehen, sofern ihre Ergebnisse verschieden sind.

Nachricht: Archivauftrag A ist geprüft. Archivauftrag B ist nicht geprüft. Welchen der beidne ich meine, ist nicht festgelegt.

Frage: Ist der gemeinte Archivauftrag freigegeben?

Gold: {"action": "ask_target", "determination": "unresolved"}

Vorhersage: {"action": "ask_target", "determination": "no"}

Alle ungerundeten Wahrscheinlichkeiten: {"action": {"answer": 0.3592072129249573, "ask_fact": 0.24543695151805878, "ask_target": 0.3641519844532013, "resolve_conflict": 0.031203806400299072}, "determination": {"no": 0.6397312879562378, "unresolved": 0.2625451982021332, "yes": 0.09772349148988724}}

Technische Probleme: []

## gv_b4_de_en_mix

Domäne: banking; Gruppe: invariant; Ansicht: de_en_mix.

Regel: Ein fiktiver Archivauftrag ist genau dann freigegeben, wenn er geprüft ist. Bei mehreren möglichen Aufträgen muss der gemeinte Auftrag feststehen, sofern ihre Ergebnisse verschieden sind.

Nachricht: Archivauftrag A ist checked. B ist not checked. Welchen Auftrag ich meine, ist nicht festgelegt.

Frage: Ist der gemeinte Archivauftrag freigegeben?

Gold: {"action": "ask_target", "determination": "unresolved"}

Vorhersage: {"action": "answer", "determination": "unresolved"}

Alle ungerundeten Wahrscheinlichkeiten: {"action": {"answer": 0.6797976493835449, "ask_fact": 0.1101103127002716, "ask_target": 0.1822517365217209, "resolve_conflict": 0.02784024551510811}, "determination": {"no": 0.1492132544517517, "unresolved": 0.4420018494129181, "yes": 0.4087848663330078}}

Technische Probleme: []

## gv_f4_canonical

Domäne: finance; Gruppe: invariant; Ansicht: canonical.

Regel: Ein fiktiver Depotbeleg ist genau dann digital abrufbar, wenn sein Digitalzugang aktiviert ist. Bei mehreren möglichen Belegen muss das Ziel feststehen, sofern ihre Ergebnisse verschieden sind.

Nachricht: Bei Depotbeleg A ist der Digitalzugang aktiviert. Bei Depotbeleg B ist er nicht aktiviert. Welchen Beleg ich meine, ist offen.

Frage: Ist der gemeinte Depotbeleg digital abrufbar?

Gold: {"action": "ask_target", "determination": "unresolved"}

Vorhersage: {"action": "answer", "determination": "unresolved"}

Alle ungerundeten Wahrscheinlichkeiten: {"action": {"answer": 0.6124475002288818, "ask_fact": 0.05217338725924492, "ask_target": 0.323368102312088, "resolve_conflict": 0.012010996229946613}, "determination": {"no": 0.10341385006904602, "unresolved": 0.6485093235969543, "yes": 0.2480769157409668}}

Technische Probleme: []

## gv_f4_de_en_mix

Domäne: finance; Gruppe: invariant; Ansicht: de_en_mix.

Regel: Ein fiktiver Depotbeleg ist genau dann digital abrufbar, wenn sein Digitalzugang aktiviert ist. Bei mehreren möglichen Belegen muss das Ziel feststehen, sofern ihre Ergebnisse verschieden sind.

Nachricht: Bei Depotbeleg A ist der Digitalzugang enabled. Bei B ist er not enabled. Welchen Beleg ich meine, ist offen.

Frage: Ist der gemeinte Depotbeleg digital abrufbar?

Gold: {"action": "ask_target", "determination": "unresolved"}

Vorhersage: {"action": "answer", "determination": "unresolved"}

Alle ungerundeten Wahrscheinlichkeiten: {"action": {"answer": 0.5436817407608032, "ask_fact": 0.04658752307295799, "ask_target": 0.3977660834789276, "resolve_conflict": 0.011964665725827217}, "determination": {"no": 0.08299419283866882, "unresolved": 0.6949018836021423, "yes": 0.22210398316383362}}

Technische Probleme: []

## gv_banking_missing_target_b

Domäne: banking; Gruppe: ambiguity_change; Ansicht: target_removed.

Regel: Ein fiktives Adressblatt ist genau dann verwendbar, wenn es geprüft ist.

Nachricht: Adressblatt A ist geprüft. Adressblatt B ist nicht geprüft. Welches der beiden ich meine, ist nicht festgelegt.

Frage: Ist das gemeinte Adressblatt verwendbar?

Gold: {"action": "ask_target", "determination": "unresolved"}

Vorhersage: {"action": "answer", "determination": "no"}

Alle ungerundeten Wahrscheinlichkeiten: {"action": {"answer": 0.8279700875282288, "ask_fact": 0.05407983437180519, "ask_target": 0.1058831736445427, "resolve_conflict": 0.01206684298813343}, "determination": {"no": 0.90253084897995, "unresolved": 0.06973176449537277, "yes": 0.02773738093674183}}

Technische Probleme: []

## gv_insurance_missing_target_b

Domäne: insurance; Gruppe: ambiguity_change; Ansicht: target_removed.

Regel: Ein fiktives Schadenblatt ist genau dann verwendbar, wenn es bestätigt ist.

Nachricht: Schadenblatt A ist bestätigt. Schadenblatt B ist nicht bestätigt. Welches der beiden ich meine, ist nicht festgelegt.

Frage: Ist das gemeinte Schadenblatt verwendbar?

Gold: {"action": "ask_target", "determination": "unresolved"}

Vorhersage: {"action": "answer", "determination": "no"}

Alle ungerundeten Wahrscheinlichkeiten: {"action": {"answer": 0.8356213569641113, "ask_fact": 0.04940494894981384, "ask_target": 0.10377635061740875, "resolve_conflict": 0.011197332292795181}, "determination": {"no": 0.7095847725868225, "unresolved": 0.11720197647809982, "yes": 0.17321328818798065}}

Technische Probleme: []

## gv_finance_missing_target_b

Domäne: finance; Gruppe: ambiguity_change; Ansicht: target_removed.

Regel: Ein fiktives Exportblatt ist genau dann verwendbar, wenn es freigegeben ist.

Nachricht: Exportblatt A ist freigegeben. Exportblatt B ist nicht freigegeben. Welches der beiden ich meine, ist nicht festgelegt.

Frage: Ist das gemeinte Exportblatt verwendbar?

Gold: {"action": "ask_target", "determination": "unresolved"}

Vorhersage: {"action": "answer", "determination": "no"}

Alle ungerundeten Wahrscheinlichkeiten: {"action": {"answer": 0.7129725217819214, "ask_fact": 0.04629657417535782, "ask_target": 0.22260089218616486, "resolve_conflict": 0.018129996955394745}, "determination": {"no": 0.590904951095581, "unresolved": 0.18305380642414093, "yes": 0.2260412871837616}}

Technische Probleme: []

