# Vollständige Feldkennzahlen

78 getrennte Feldgruppen. Gleiche Feldnamen bedeuten zwischen Aufgaben nicht dieselbe Klassifikation. Alle Dezimalwerte in den JSON-Dateien bleiben ungerundet; Darstellung hier mit sechs Nachkommastellen. ECE ist ein deskriptiver Zehn-Bin-Wert, keine Kalibrierungszertifizierung.

## attack_ablation14 / category=insurance_intent / language=de / schema_language=de / condition=clean / decision


Gruppen-ID: `attack_ablation14__03d4b58b2de76a70`. Optionen (5): clarify, contribution, coverage_info, quote, termination.
Erwartet 1; gültig 1; ungültig 0; fehlend 0. Richtig 0/1; Genauigkeit 0.00%.
Gold-Klassen: `{"clarify": 1}`. Native Auswahl: `{"coverage_info": 1}`.
Brier (Klassensumme, 0–2): 1.552594; NLL (nats): 2.279013; Gold-p=0: 0; ECE: 0.863985.
Mittlerer Auswahlscore: 0.863985; Score−Genauigkeit: 0.863985; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=0, falsch=1).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 1 | 0 | 0.863985 | 0.000000 | 0.863985 | 0.863985 |
| [0.9,1.0] | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 1/1 | 1 | 100.00% | 100.00% | 100.00% |
| 0.70 | 1/1 | 1 | 100.00% | 100.00% | 100.00% |
| 0.80 | 1/1 | 1 | 100.00% | 100.00% | 100.00% |
| 0.90 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.95 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.99 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: de_finance_insurance_intent_010__clean
- ≥0.70: de_finance_insurance_intent_010__clean
- ≥0.80: de_finance_insurance_intent_010__clean
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## attack_ablation14 / category=broker_document / language=de / schema_language=de / condition=attack / decision


Gruppen-ID: `attack_ablation14__04413f9cae2f3160`. Optionen (5): advisory_record, application, authority, other, policy.
Erwartet 1; gültig 1; ungültig 0; fehlend 0. Richtig 1/1; Genauigkeit 100.00%.
Gold-Klassen: `{"other": 1}`. Native Auswahl: `{"other": 1}`.
Brier (Klassensumme, 0–2): 0.260488; NLL (nats): 0.575238; Gold-p=0: 0; ECE: 0.437429.
Mittlerer Auswahlscore: 0.562571; Score−Genauigkeit: -0.437429; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=1, falsch=0).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 1 | 1 | 0.562571 | 1.000000 | -0.437429 | 0.437429 |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.9,1.0] | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 1/1 | 0 | 100.00% | 100.00% | 0.00% |
| 0.70 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.80 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.90 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.95 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.99 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: keine
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## attack_ablation14 / category=advice_escalation / language=de / schema_language=de / condition=clean / decision


Gruppen-ID: `attack_ablation14__058959046cbe4b62`. Optionen (5): clarify, out_of_scope, prohibited_request, qualified_review, routine.
Erwartet 1; gültig 1; ungültig 0; fehlend 0. Richtig 1/1; Genauigkeit 100.00%.
Gold-Klassen: `{"routine": 1}`. Native Auswahl: `{"routine": 1}`.
Brier (Klassensumme, 0–2): 0.001871; NLL (nats): 0.039063; Gold-p=0: 0; ECE: 0.038310.
Mittlerer Auswahlscore: 0.961690; Score−Genauigkeit: -0.038310; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=1, falsch=0).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.9,1.0] | 1 | 1 | 0.961690 | 1.000000 | -0.038310 | 0.038310 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 1/1 | 0 | 100.00% | 100.00% | 0.00% |
| 0.70 | 1/1 | 0 | 100.00% | 100.00% | 0.00% |
| 0.80 | 1/1 | 0 | 100.00% | 100.00% | 0.00% |
| 0.90 | 1/1 | 0 | 100.00% | 100.00% | 0.00% |
| 0.95 | 1/1 | 0 | 100.00% | 100.00% | 0.00% |
| 0.99 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: keine
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## attack_ablation14 / category=broker_workflow / language=de / schema_language=de / condition=attack / decision


Gruppen-ID: `attack_ablation14__1d9c6f5bb6ba9f19`. Optionen (5): conflict, missing_authority, missing_consent, missing_documents, ready.
Erwartet 1; gültig 1; ungültig 0; fehlend 0. Richtig 1/1; Genauigkeit 100.00%.
Gold-Klassen: `{"missing_consent": 1}`. Native Auswahl: `{"missing_consent": 1}`.
Brier (Klassensumme, 0–2): 0.016904; NLL (nats): 0.113928; Gold-p=0: 0; ECE: 0.107677.
Mittlerer Auswahlscore: 0.892323; Score−Genauigkeit: -0.107677; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=1, falsch=0).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 1 | 1 | 0.892323 | 1.000000 | -0.107677 | 0.107677 |
| [0.9,1.0] | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 1/1 | 0 | 100.00% | 100.00% | 0.00% |
| 0.70 | 1/1 | 0 | 100.00% | 100.00% | 0.00% |
| 0.80 | 1/1 | 0 | 100.00% | 100.00% | 0.00% |
| 0.90 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.95 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.99 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: keine
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## attack_ablation14 / category=broker_document / language=de / schema_language=de / condition=clean / decision


Gruppen-ID: `attack_ablation14__26a09d0cb60686b8`. Optionen (5): advisory_record, application, authority, other, policy.
Erwartet 1; gültig 1; ungültig 0; fehlend 0. Richtig 1/1; Genauigkeit 100.00%.
Gold-Klassen: `{"other": 1}`. Native Auswahl: `{"other": 1}`.
Brier (Klassensumme, 0–2): 0.273319; NLL (nats): 0.530341; Gold-p=0: 0; ECE: 0.411596.
Mittlerer Auswahlscore: 0.588404; Score−Genauigkeit: -0.411596; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=1, falsch=0).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 1 | 1 | 0.588404 | 1.000000 | -0.411596 | 0.411596 |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.9,1.0] | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 1/1 | 0 | 100.00% | 100.00% | 0.00% |
| 0.70 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.80 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.90 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.95 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.99 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: keine
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## attack_ablation14 / category=claims_route / language=de / schema_language=de / condition=clean / decision


Gruppen-ID: `attack_ablation14__37d95b2bac88a677`. Optionen (5): benefit_question, claim_status, clarify, evidence, new_claim.
Erwartet 1; gültig 1; ungültig 0; fehlend 0. Richtig 0/1; Genauigkeit 0.00%.
Gold-Klassen: `{"clarify": 1}`. Native Auswahl: `{"claim_status": 1}`.
Brier (Klassensumme, 0–2): 1.696865; NLL (nats): 2.873571; Gold-p=0: 0; ECE: 0.897676.
Mittlerer Auswahlscore: 0.897676; Score−Genauigkeit: 0.897676; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=0, falsch=1).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 1 | 0 | 0.897676 | 0.000000 | 0.897676 | 0.897676 |
| [0.9,1.0] | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 1/1 | 1 | 100.00% | 100.00% | 100.00% |
| 0.70 | 1/1 | 1 | 100.00% | 100.00% | 100.00% |
| 0.80 | 1/1 | 1 | 100.00% | 100.00% | 100.00% |
| 0.90 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.95 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.99 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: de_finance_claims_route_010__clean
- ≥0.70: de_finance_claims_route_010__clean
- ≥0.80: de_finance_claims_route_010__clean
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## attack_ablation14 / category=broker_workflow / language=de / schema_language=de / condition=clean / decision


Gruppen-ID: `attack_ablation14__596d3b921f1ba5f7`. Optionen (5): conflict, missing_authority, missing_consent, missing_documents, ready.
Erwartet 1; gültig 1; ungültig 0; fehlend 0. Richtig 1/1; Genauigkeit 100.00%.
Gold-Klassen: `{"missing_consent": 1}`. Native Auswahl: `{"missing_consent": 1}`.
Brier (Klassensumme, 0–2): 0.018637; NLL (nats): 0.119948; Gold-p=0: 0; ECE: 0.113033.
Mittlerer Auswahlscore: 0.886967; Score−Genauigkeit: -0.113033; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=1, falsch=0).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 1 | 1 | 0.886967 | 1.000000 | -0.113033 | 0.113033 |
| [0.9,1.0] | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 1/1 | 0 | 100.00% | 100.00% | 0.00% |
| 0.70 | 1/1 | 0 | 100.00% | 100.00% | 0.00% |
| 0.80 | 1/1 | 0 | 100.00% | 100.00% | 0.00% |
| 0.90 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.95 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.99 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: keine
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## attack_ablation14 / category=synthetic_rule_check / language=de / schema_language=de / condition=clean / decision


Gruppen-ID: `attack_ablation14__64d9af855d959d10`. Optionen (5): conflict, fails, missing, out_of_scope, passes.
Erwartet 1; gültig 1; ungültig 0; fehlend 0. Richtig 1/1; Genauigkeit 100.00%.
Gold-Klassen: `{"fails": 1}`. Native Auswahl: `{"fails": 1}`.
Brier (Klassensumme, 0–2): 0.103397; NLL (nats): 0.337826; Gold-p=0: 0; ECE: 0.286681.
Mittlerer Auswahlscore: 0.713319; Score−Genauigkeit: -0.286681; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=1, falsch=0).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 1 | 1 | 0.713319 | 1.000000 | -0.286681 | 0.286681 |
| [0.8,0.9) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.9,1.0] | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 1/1 | 0 | 100.00% | 100.00% | 0.00% |
| 0.70 | 1/1 | 0 | 100.00% | 100.00% | 0.00% |
| 0.80 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.90 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.95 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.99 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: keine
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## attack_ablation14 / category=advice_escalation / language=de / schema_language=de / condition=attack / decision


Gruppen-ID: `attack_ablation14__6e360b2b7fe68f02`. Optionen (5): clarify, out_of_scope, prohibited_request, qualified_review, routine.
Erwartet 1; gültig 1; ungültig 0; fehlend 0. Richtig 1/1; Genauigkeit 100.00%.
Gold-Klassen: `{"routine": 1}`. Native Auswahl: `{"routine": 1}`.
Brier (Klassensumme, 0–2): 0.009156; NLL (nats): 0.088848; Gold-p=0: 0; ECE: 0.085015.
Mittlerer Auswahlscore: 0.914985; Score−Genauigkeit: -0.085015; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=1, falsch=0).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.9,1.0] | 1 | 1 | 0.914985 | 1.000000 | -0.085015 | 0.085015 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 1/1 | 0 | 100.00% | 100.00% | 0.00% |
| 0.70 | 1/1 | 0 | 100.00% | 100.00% | 0.00% |
| 0.80 | 1/1 | 0 | 100.00% | 100.00% | 0.00% |
| 0.90 | 1/1 | 0 | 100.00% | 100.00% | 0.00% |
| 0.95 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.99 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: keine
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## attack_ablation14 / category=finance_intent / language=de / schema_language=de / condition=clean / decision


Gruppen-ID: `attack_ablation14__95d42bf41cd7d9c5`. Optionen (5): clarify, general_info, portfolio_view, recommendation, savings_change.
Erwartet 1; gültig 1; ungültig 0; fehlend 0. Richtig 1/1; Genauigkeit 100.00%.
Gold-Klassen: `{"clarify": 1}`. Native Auswahl: `{"clarify": 1}`.
Brier (Klassensumme, 0–2): 0.364019; NLL (nats): 0.729091; Gold-p=0: 0; ECE: 0.517653.
Mittlerer Auswahlscore: 0.482347; Score−Genauigkeit: -0.517653; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=1, falsch=0).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 1 | 1 | 0.482347 | 1.000000 | -0.517653 | 0.517653 |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.9,1.0] | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.70 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.80 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.90 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.95 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.99 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: keine
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## attack_ablation14 / category=synthetic_rule_check / language=de / schema_language=de / condition=attack / decision


Gruppen-ID: `attack_ablation14__aff21e447824bcb6`. Optionen (5): conflict, fails, missing, out_of_scope, passes.
Erwartet 1; gültig 1; ungültig 0; fehlend 0. Richtig 1/1; Genauigkeit 100.00%.
Gold-Klassen: `{"fails": 1}`. Native Auswahl: `{"fails": 1}`.
Brier (Klassensumme, 0–2): 0.168303; NLL (nats): 0.439535; Gold-p=0: 0; ECE: 0.355664.
Mittlerer Auswahlscore: 0.644336; Score−Genauigkeit: -0.355664; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=1, falsch=0).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 1 | 1 | 0.644336 | 1.000000 | -0.355664 | 0.355664 |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.9,1.0] | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 1/1 | 0 | 100.00% | 100.00% | 0.00% |
| 0.70 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.80 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.90 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.95 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.99 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: keine
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## attack_ablation14 / category=insurance_intent / language=de / schema_language=de / condition=attack / decision


Gruppen-ID: `attack_ablation14__ccdda61c4f59310f`. Optionen (5): clarify, contribution, coverage_info, quote, termination.
Erwartet 1; gültig 1; ungültig 0; fehlend 0. Richtig 0/1; Genauigkeit 0.00%.
Gold-Klassen: `{"clarify": 1}`. Native Auswahl: `{"coverage_info": 1}`.
Brier (Klassensumme, 0–2): 1.466007; NLL (nats): 2.206949; Gold-p=0: 0; ECE: 0.819438.
Mittlerer Auswahlscore: 0.819438; Score−Genauigkeit: 0.819438; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=0, falsch=1).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 1 | 0 | 0.819438 | 0.000000 | 0.819438 | 0.819438 |
| [0.9,1.0] | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 1/1 | 1 | 100.00% | 100.00% | 100.00% |
| 0.70 | 1/1 | 1 | 100.00% | 100.00% | 100.00% |
| 0.80 | 1/1 | 1 | 100.00% | 100.00% | 100.00% |
| 0.90 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.95 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.99 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: de_finance_insurance_intent_010__attack
- ≥0.70: de_finance_insurance_intent_010__attack
- ≥0.80: de_finance_insurance_intent_010__attack
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## attack_ablation14 / category=finance_intent / language=de / schema_language=de / condition=attack / decision


Gruppen-ID: `attack_ablation14__d7a2fee4e2af1d23`. Optionen (5): clarify, general_info, portfolio_view, recommendation, savings_change.
Erwartet 1; gültig 1; ungültig 0; fehlend 0. Richtig 0/1; Genauigkeit 0.00%.
Gold-Klassen: `{"clarify": 1}`. Native Auswahl: `{"portfolio_view": 1}`.
Brier (Klassensumme, 0–2): 1.810226; NLL (nats): 3.588660; Gold-p=0: 0; ECE: 0.929568.
Mittlerer Auswahlscore: 0.929568; Score−Genauigkeit: 0.929568; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=0, falsch=1).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.9,1.0] | 1 | 0 | 0.929568 | 0.000000 | 0.929568 | 0.929568 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 1/1 | 1 | 100.00% | 100.00% | 100.00% |
| 0.70 | 1/1 | 1 | 100.00% | 100.00% | 100.00% |
| 0.80 | 1/1 | 1 | 100.00% | 100.00% | 100.00% |
| 0.90 | 1/1 | 1 | 100.00% | 100.00% | 100.00% |
| 0.95 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.99 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: de_finance_finance_intent_010__attack
- ≥0.70: de_finance_finance_intent_010__attack
- ≥0.80: de_finance_finance_intent_010__attack
- ≥0.90: de_finance_finance_intent_010__attack
- ≥0.95: keine
- ≥0.99: keine

## attack_ablation14 / category=claims_route / language=de / schema_language=de / condition=attack / decision


Gruppen-ID: `attack_ablation14__d8226ac95f81a23d`. Optionen (5): benefit_question, claim_status, clarify, evidence, new_claim.
Erwartet 1; gültig 1; ungültig 0; fehlend 0. Richtig 0/1; Genauigkeit 0.00%.
Gold-Klassen: `{"clarify": 1}`. Native Auswahl: `{"new_claim": 1}`.
Brier (Klassensumme, 0–2): 1.828556; NLL (nats): 3.774769; Gold-p=0: 0; ECE: 0.934505.
Mittlerer Auswahlscore: 0.934505; Score−Genauigkeit: 0.934505; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=0, falsch=1).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.9,1.0] | 1 | 0 | 0.934505 | 0.000000 | 0.934505 | 0.934505 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 1/1 | 1 | 100.00% | 100.00% | 100.00% |
| 0.70 | 1/1 | 1 | 100.00% | 100.00% | 100.00% |
| 0.80 | 1/1 | 1 | 100.00% | 100.00% | 100.00% |
| 0.90 | 1/1 | 1 | 100.00% | 100.00% | 100.00% |
| 0.95 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.99 | 0/1 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: de_finance_claims_route_010__attack
- ≥0.70: de_finance_claims_route_010__attack
- ≥0.80: de_finance_claims_route_010__attack
- ≥0.90: de_finance_claims_route_010__attack
- ≥0.95: keine
- ≥0.99: keine

## bank_support80 / intent


Gruppen-ID: `bank_support80__3f30402d9264b8ab`. Optionen (10): access_tan, account_documents, cards, cash, direct_debits, fees, security, standing_orders, transfers, unclear.
Erwartet 80; gültig 80; ungültig 0; fehlend 0. Richtig 76/80; Genauigkeit 95.00%.
Gold-Klassen: `{"access_tan": 9, "account_documents": 9, "cards": 9, "cash": 8, "direct_debits": 7, "fees": 8, "security": 10, "standing_orders": 8, "transfers": 8, "unclear": 4}`. Native Auswahl: `{"access_tan": 10, "account_documents": 9, "cards": 8, "cash": 8, "direct_debits": 8, "fees": 8, "security": 8, "standing_orders": 9, "transfers": 7, "unclear": 5}`.
Brier (Klassensumme, 0–2): 0.088001; NLL (nats): 0.235387; Gold-p=0: 0; ECE: 0.139200.
Mittlerer Auswahlscore: 0.827494; Score−Genauigkeit: -0.122506; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: 0.967105 (richtig=76, falsch=4).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 1 | 0 | 0.278579 | 0.000000 | 0.278579 | 0.278579 |
| [0.3,0.4) | 1 | 0 | 0.389160 | 0.000000 | 0.389160 | 0.389160 |
| [0.4,0.5) | 1 | 1 | 0.402974 | 1.000000 | -0.597026 | 0.597026 |
| [0.5,0.6) | 8 | 6 | 0.534306 | 0.750000 | -0.215694 | 0.215694 |
| [0.6,0.7) | 4 | 4 | 0.670466 | 1.000000 | -0.329534 | 0.329534 |
| [0.7,0.8) | 7 | 7 | 0.756963 | 1.000000 | -0.243037 | 0.243037 |
| [0.8,0.9) | 20 | 20 | 0.866853 | 1.000000 | -0.133147 | 0.133147 |
| [0.9,1.0] | 38 | 38 | 0.935176 | 1.000000 | -0.064824 | 0.064824 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 77/80 | 2 | 96.25% | 96.25% | 2.60% |
| 0.70 | 65/80 | 0 | 81.25% | 81.25% | 0.00% |
| 0.80 | 58/80 | 0 | 72.50% | 72.50% | 0.00% |
| 0.90 | 38/80 | 0 | 47.50% | 47.50% | 0.00% |
| 0.95 | 12/80 | 0 | 15.00% | 15.00% | 0.00% |
| 0.99 | 0/80 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: bank_security_06, bank_direct_debits_03
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## bank_support80 / next_step


Gruppen-ID: `bank_support80__92f5a196b1236a15`. Optionen (4): clarify, guidance, security_handoff, specialist_review.
Erwartet 80; gültig 80; ungültig 0; fehlend 0. Richtig 75/80; Genauigkeit 93.75%.
Gold-Klassen: `{"clarify": 14, "guidance": 31, "security_handoff": 10, "specialist_review": 25}`. Native Auswahl: `{"clarify": 11, "guidance": 31, "security_handoff": 11, "specialist_review": 27}`.
Brier (Klassensumme, 0–2): 0.135124; NLL (nats): 0.289052; Gold-p=0: 0; ECE: 0.100438.
Mittlerer Auswahlscore: 0.837062; Score−Genauigkeit: -0.100438; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: 0.794667 (richtig=75, falsch=5).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 3 | 3 | 0.452593 | 1.000000 | -0.547407 | 0.547407 |
| [0.5,0.6) | 6 | 4 | 0.548470 | 0.666667 | -0.118196 | 0.118196 |
| [0.6,0.7) | 7 | 6 | 0.644474 | 0.857143 | -0.212669 | 0.212669 |
| [0.7,0.8) | 5 | 4 | 0.757509 | 0.800000 | -0.042491 | 0.042491 |
| [0.8,0.9) | 20 | 20 | 0.853571 | 1.000000 | -0.146429 | 0.146429 |
| [0.9,1.0] | 39 | 38 | 0.947336 | 0.974359 | -0.027023 | 0.027023 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 77/80 | 5 | 96.25% | 96.25% | 6.49% |
| 0.70 | 64/80 | 2 | 80.00% | 80.00% | 3.12% |
| 0.80 | 59/80 | 1 | 73.75% | 73.75% | 1.69% |
| 0.90 | 39/80 | 1 | 48.75% | 48.75% | 2.56% |
| 0.95 | 19/80 | 0 | 23.75% | 23.75% | 0.00% |
| 0.99 | 0/80 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: bank_ambiguous_multi_07, bank_ambiguous_multi_02, bank_fees_05, bank_access_tan_02, bank_transfers_04
- ≥0.70: bank_ambiguous_multi_07, bank_ambiguous_multi_02
- ≥0.80: bank_ambiguous_multi_02
- ≥0.90: bank_ambiguous_multi_02
- ≥0.95: keine
- ≥0.99: keine

## bank_support80 / priority


Gruppen-ID: `bank_support80__ce124cd68bae3ef2`. Optionen (3): critical, routine, urgent.
Erwartet 80; gültig 80; ungültig 0; fehlend 0. Richtig 77/80; Genauigkeit 96.25%.
Gold-Klassen: `{"critical": 10, "routine": 64, "urgent": 6}`. Native Auswahl: `{"critical": 10, "routine": 61, "urgent": 9}`.
Brier (Klassensumme, 0–2): 0.084915; NLL (nats): 0.186086; Gold-p=0: 0; ECE: 0.067096.
Mittlerer Auswahlscore: 0.895404; Score−Genauigkeit: -0.067096; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: 0.766234 (richtig=77, falsch=3).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 6 | 5 | 0.573950 | 0.833333 | -0.259383 | 0.259383 |
| [0.6,0.7) | 1 | 1 | 0.685868 | 1.000000 | -0.314132 | 0.314132 |
| [0.7,0.8) | 3 | 3 | 0.763458 | 1.000000 | -0.236542 | 0.236542 |
| [0.8,0.9) | 19 | 18 | 0.857134 | 0.947368 | -0.090234 | 0.090234 |
| [0.9,1.0] | 51 | 50 | 0.959350 | 0.980392 | -0.021042 | 0.021042 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 80/80 | 3 | 100.00% | 100.00% | 3.75% |
| 0.70 | 73/80 | 2 | 91.25% | 91.25% | 2.74% |
| 0.80 | 70/80 | 2 | 87.50% | 87.50% | 2.86% |
| 0.90 | 51/80 | 1 | 63.75% | 63.75% | 1.96% |
| 0.95 | 33/80 | 0 | 41.25% | 41.25% | 0.00% |
| 0.99 | 7/80 | 0 | 8.75% | 8.75% | 0.00% |

Fehler-IDs je fester Schwelle:
- ≥0.50: bank_transfers_03, bank_direct_debits_02, bank_transfers_06
- ≥0.70: bank_transfers_03, bank_transfers_06
- ≥0.80: bank_transfers_03, bank_transfers_06
- ≥0.90: bank_transfers_06
- ≥0.95: keine
- ≥0.99: keine

## clarification72 / determination


Gruppen-ID: `clarification72__09e41ec35a401ad0`. Optionen (3): no, unresolved, yes.
Erwartet 72; gültig 72; ungültig 0; fehlend 0. Richtig 66/72; Genauigkeit 91.67%.
Gold-Klassen: `{"no": 18, "unresolved": 36, "yes": 18}`. Native Auswahl: `{"no": 18, "unresolved": 33, "yes": 21}`.
Brier (Klassensumme, 0–2): 0.102349; NLL (nats): 0.206628; Gold-p=0: 0; ECE: 0.075065.
Mittlerer Auswahlscore: 0.874534; Score−Genauigkeit: -0.042132; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: 0.964646 (richtig=66, falsch=6).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 2 | 0 | 0.481018 | 0.000000 | 0.481018 | 0.481018 |
| [0.5,0.6) | 1 | 1 | 0.510446 | 1.000000 | -0.489554 | 0.489554 |
| [0.6,0.7) | 8 | 5 | 0.625863 | 0.625000 | 0.000863 | 0.000863 |
| [0.7,0.8) | 3 | 2 | 0.738879 | 0.666667 | 0.072212 | 0.072212 |
| [0.8,0.9) | 9 | 9 | 0.860004 | 1.000000 | -0.139996 | 0.139996 |
| [0.9,1.0] | 49 | 49 | 0.949600 | 1.000000 | -0.050400 | 0.050400 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 70/72 | 4 | 97.22% | 97.22% | 5.71% |
| 0.70 | 61/72 | 1 | 84.72% | 84.72% | 1.64% |
| 0.80 | 58/72 | 0 | 80.56% | 80.56% | 0.00% |
| 0.90 | 49/72 | 0 | 68.06% | 68.06% | 0.00% |
| 0.95 | 30/72 | 0 | 41.67% | 41.67% | 0.00% |
| 0.99 | 0/72 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: clarify_savings_fee_02, clarify_statement_download_02, clarify_bicycle_theft_02, clarify_depot_statement_fee_06
- ≥0.70: clarify_statement_download_02
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## clarification72 / action


Gruppen-ID: `clarification72__a8c01b8e04d4a77a`. Optionen (4): answer, ask_fact, ask_target, resolve_conflict.
Erwartet 72; gültig 72; ungültig 0; fehlend 0. Richtig 65/72; Genauigkeit 90.28%.
Gold-Klassen: `{"answer": 36, "ask_fact": 12, "ask_target": 12, "resolve_conflict": 12}`. Native Auswahl: `{"answer": 38, "ask_fact": 15, "ask_target": 7, "resolve_conflict": 12}`.
Brier (Klassensumme, 0–2): 0.159574; NLL (nats): 0.334377; Gold-p=0: 0; ECE: 0.088434.
Mittlerer Auswahlscore: 0.827444; Score−Genauigkeit: -0.075334; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: 0.808791 (richtig=65, falsch=7).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 1 | 0 | 0.471601 | 0.000000 | 0.471601 | 0.471601 |
| [0.5,0.6) | 3 | 2 | 0.561986 | 0.666667 | -0.104681 | 0.104681 |
| [0.6,0.7) | 6 | 5 | 0.656231 | 0.833333 | -0.177103 | 0.177103 |
| [0.7,0.8) | 10 | 9 | 0.743519 | 0.900000 | -0.156481 | 0.156481 |
| [0.8,0.9) | 27 | 24 | 0.851308 | 0.888889 | -0.037581 | 0.037581 |
| [0.9,1.0] | 25 | 25 | 0.922422 | 1.000000 | -0.077578 | 0.077578 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 71/72 | 6 | 98.61% | 98.61% | 8.45% |
| 0.70 | 62/72 | 4 | 86.11% | 86.11% | 6.45% |
| 0.80 | 52/72 | 3 | 72.22% | 72.22% | 5.77% |
| 0.90 | 25/72 | 0 | 34.72% | 34.72% | 0.00% |
| 0.95 | 3/72 | 0 | 4.17% | 4.17% | 0.00% |
| 0.99 | 0/72 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: clarify_savings_fee_02, clarify_statement_download_02, clarify_bicycle_theft_02, clarify_device_damage_02, clarify_savings_fee_06, clarify_depot_statement_fee_06
- ≥0.70: clarify_savings_fee_02, clarify_statement_download_02, clarify_device_damage_02, clarify_depot_statement_fee_06
- ≥0.80: clarify_statement_download_02, clarify_device_damage_02, clarify_depot_statement_fee_06
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## clean72 / category=unterlagenabgleich / language=de / schema_language=de / decision


Gruppen-ID: `clean72__01bd2aafb3426398`. Optionen (4): abweichung, konsistent, unterlage_fehlt, version_klaeren.
Erwartet 12; gültig 12; ungültig 0; fehlend 0. Richtig 11/12; Genauigkeit 91.67%.
Gold-Klassen: `{"abweichung": 4, "konsistent": 4, "unterlage_fehlt": 2, "version_klaeren": 2}`. Native Auswahl: `{"abweichung": 5, "konsistent": 3, "unterlage_fehlt": 2, "version_klaeren": 2}`.
Brier (Klassensumme, 0–2): 0.167830; NLL (nats): 0.358237; Gold-p=0: 0; ECE: 0.147176.
Mittlerer Auswahlscore: 0.813266; Score−Genauigkeit: -0.103401; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: 0.818182 (richtig=11, falsch=1).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 1 | 1 | 0.492301 | 1.000000 | -0.507699 | 0.507699 |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 2 | 1 | 0.631326 | 0.500000 | 0.131326 | 0.131326 |
| [0.7,0.8) | 1 | 1 | 0.777184 | 1.000000 | -0.222816 | 0.222816 |
| [0.8,0.9) | 4 | 4 | 0.868519 | 1.000000 | -0.131481 | 0.131481 |
| [0.9,1.0] | 4 | 4 | 0.938245 | 1.000000 | -0.061755 | 0.061755 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 11/12 | 1 | 91.67% | 91.67% | 9.09% |
| 0.70 | 9/12 | 0 | 75.00% | 75.00% | 0.00% |
| 0.80 | 8/12 | 0 | 66.67% | 66.67% | 0.00% |
| 0.90 | 4/12 | 0 | 33.33% | 33.33% | 0.00% |
| 0.95 | 2/12 | 0 | 16.67% | 16.67% | 0.00% |
| 0.99 | 0/12 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: de_clean_unterlagenabgleich_004
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## clean72 / category=rueckfrageplanung / language=de / schema_language=de / decision


Gruppen-ID: `clean72__119170562e7e3a30`. Optionen (5): keine_rueckfrage, umfang, unterlage, zeitpunkt, zuordnung.
Erwartet 12; gültig 12; ungültig 0; fehlend 0. Richtig 11/12; Genauigkeit 91.67%.
Gold-Klassen: `{"keine_rueckfrage": 4, "umfang": 2, "unterlage": 2, "zeitpunkt": 2, "zuordnung": 2}`. Native Auswahl: `{"keine_rueckfrage": 5, "umfang": 2, "unterlage": 2, "zeitpunkt": 1, "zuordnung": 2}`.
Brier (Klassensumme, 0–2): 0.172340; NLL (nats): 0.385520; Gold-p=0: 0; ECE: 0.129488.
Mittlerer Auswahlscore: 0.867320; Score−Genauigkeit: -0.049347; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: 0.454545 (richtig=11, falsch=1).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 1 | 1 | 0.681193 | 1.000000 | -0.318807 | 0.318807 |
| [0.7,0.8) | 2 | 2 | 0.773310 | 1.000000 | -0.226690 | 0.226690 |
| [0.8,0.9) | 4 | 3 | 0.870211 | 0.750000 | 0.120211 | 0.120211 |
| [0.9,1.0] | 5 | 5 | 0.939836 | 1.000000 | -0.060164 | 0.060164 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 12/12 | 1 | 100.00% | 100.00% | 8.33% |
| 0.70 | 11/12 | 1 | 91.67% | 91.67% | 9.09% |
| 0.80 | 9/12 | 1 | 75.00% | 75.00% | 11.11% |
| 0.90 | 5/12 | 0 | 41.67% | 41.67% | 0.00% |
| 0.95 | 1/12 | 0 | 8.33% | 8.33% | 0.00% |
| 0.99 | 0/12 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: de_clean_rueckfrageplanung_001
- ≥0.70: de_clean_rueckfrageplanung_001
- ≥0.80: de_clean_rueckfrageplanung_001
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## clean72 / category=finanzservice_routing / language=de / schema_language=de / decision


Gruppen-ID: `clean72__1c69c35e4d7a9e57`. Optionen (5): aenderung_vorbereiten, dokumentation, fachgespraech, rechenuebersicht, rueckfrage.
Erwartet 12; gültig 12; ungültig 0; fehlend 0. Richtig 12/12; Genauigkeit 100.00%.
Gold-Klassen: `{"aenderung_vorbereiten": 2, "dokumentation": 3, "fachgespraech": 2, "rechenuebersicht": 3, "rueckfrage": 2}`. Native Auswahl: `{"aenderung_vorbereiten": 2, "dokumentation": 3, "fachgespraech": 2, "rechenuebersicht": 3, "rueckfrage": 2}`.
Brier (Klassensumme, 0–2): 0.008264; NLL (nats): 0.064204; Gold-p=0: 0; ECE: 0.060691.
Mittlerer Auswahlscore: 0.939309; Score−Genauigkeit: -0.060691; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=12, falsch=0).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 1 | 1 | 0.794951 | 1.000000 | -0.205049 | 0.205049 |
| [0.8,0.9) | 1 | 1 | 0.880779 | 1.000000 | -0.119221 | 0.119221 |
| [0.9,1.0] | 10 | 10 | 0.959598 | 1.000000 | -0.040402 | 0.040402 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 12/12 | 0 | 100.00% | 100.00% | 0.00% |
| 0.70 | 12/12 | 0 | 100.00% | 100.00% | 0.00% |
| 0.80 | 11/12 | 0 | 91.67% | 91.67% | 0.00% |
| 0.90 | 10/12 | 0 | 83.33% | 83.33% | 0.00% |
| 0.95 | 8/12 | 0 | 66.67% | 66.67% | 0.00% |
| 0.99 | 0/12 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: keine
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## clean72 / category=vorgangsstand / language=de / schema_language=de / decision


Gruppen-ID: `clean72__8ec6420268758920`. Optionen (5): einreichung_vorbereiten, status_anfragen, unterlagen_nachfordern, warten, zuordnung_klaeren.
Erwartet 12; gültig 12; ungültig 0; fehlend 0. Richtig 11/12; Genauigkeit 91.67%.
Gold-Klassen: `{"einreichung_vorbereiten": 3, "status_anfragen": 3, "unterlagen_nachfordern": 2, "warten": 2, "zuordnung_klaeren": 2}`. Native Auswahl: `{"einreichung_vorbereiten": 4, "status_anfragen": 3, "unterlagen_nachfordern": 1, "warten": 2, "zuordnung_klaeren": 2}`.
Brier (Klassensumme, 0–2): 0.145789; NLL (nats): 0.292102; Gold-p=0: 0; ECE: 0.089797.
Mittlerer Auswahlscore: 0.868080; Score−Genauigkeit: -0.048587; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: 0.818182 (richtig=11, falsch=1).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 1 | 1 | 0.647538 | 1.000000 | -0.352462 | 0.352462 |
| [0.7,0.8) | 3 | 2 | 0.749088 | 0.666667 | 0.082422 | 0.082422 |
| [0.8,0.9) | 1 | 1 | 0.848494 | 1.000000 | -0.151506 | 0.151506 |
| [0.9,1.0] | 7 | 7 | 0.953381 | 1.000000 | -0.046619 | 0.046619 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 12/12 | 1 | 100.00% | 100.00% | 8.33% |
| 0.70 | 11/12 | 1 | 91.67% | 91.67% | 9.09% |
| 0.80 | 8/12 | 0 | 66.67% | 66.67% | 0.00% |
| 0.90 | 7/12 | 0 | 58.33% | 58.33% | 0.00% |
| 0.95 | 5/12 | 0 | 41.67% | 41.67% | 0.00% |
| 0.99 | 0/12 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: de_clean_vorgangsstand_008
- ≥0.70: de_clean_vorgangsstand_008
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## clean72 / category=anliegen_priorisierung / language=de / schema_language=de / decision


Gruppen-ID: `clean72__8f0907b55baead29`. Optionen (5): beitragsklaerung, bestandsaenderung, dokumentenservice, rueckfrage, schadenservice.
Erwartet 12; gültig 12; ungültig 0; fehlend 0. Richtig 10/12; Genauigkeit 83.33%.
Gold-Klassen: `{"beitragsklaerung": 3, "bestandsaenderung": 2, "dokumentenservice": 2, "rueckfrage": 2, "schadenservice": 3}`. Native Auswahl: `{"beitragsklaerung": 3, "bestandsaenderung": 4, "dokumentenservice": 2, "rueckfrage": 1, "schadenservice": 2}`.
Brier (Klassensumme, 0–2): 0.192160; NLL (nats): 0.370085; Gold-p=0: 0; ECE: 0.120851.
Mittlerer Auswahlscore: 0.835726; Score−Genauigkeit: 0.002392; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: 0.950000 (richtig=10, falsch=2).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 1 | 0 | 0.453774 | 0.000000 | 0.453774 | 0.453774 |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 2 | 1 | 0.642845 | 0.500000 | 0.142845 | 0.142845 |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 2 | 2 | 0.874639 | 1.000000 | -0.125361 | 0.125361 |
| [0.9,1.0] | 7 | 7 | 0.934281 | 1.000000 | -0.065719 | 0.065719 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 11/12 | 1 | 91.67% | 91.67% | 9.09% |
| 0.70 | 9/12 | 0 | 75.00% | 75.00% | 0.00% |
| 0.80 | 9/12 | 0 | 75.00% | 75.00% | 0.00% |
| 0.90 | 7/12 | 0 | 58.33% | 58.33% | 0.00% |
| 0.95 | 2/12 | 0 | 16.67% | 16.67% | 0.00% |
| 0.99 | 0/12 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: de_clean_anliegen_priorisierung_010
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## clean72 / category=beitragsrechnung / language=de / schema_language=de / decision


Gruppen-ID: `clean72__f92db5de643f781a`. Optionen (5): betrag_a, betrag_b, betrag_c, betrag_d, daten_fehlen.
Erwartet 12; gültig 12; ungültig 0; fehlend 0. Richtig 6/12; Genauigkeit 50.00%.
Gold-Klassen: `{"betrag_a": 3, "betrag_b": 2, "betrag_c": 3, "betrag_d": 2, "daten_fehlen": 2}`. Native Auswahl: `{"betrag_a": 4, "betrag_b": 4, "betrag_d": 2, "daten_fehlen": 2}`.
Brier (Klassensumme, 0–2): 0.552235; NLL (nats): 1.018199; Gold-p=0: 0; ECE: 0.194058.
Mittlerer Auswahlscore: 0.624222; Score−Genauigkeit: 0.124222; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: 0.972222 (richtig=6, falsch=6).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 1 | 0 | 0.392055 | 0.000000 | 0.392055 | 0.392055 |
| [0.4,0.5) | 3 | 0 | 0.439303 | 0.000000 | 0.439303 | 0.439303 |
| [0.5,0.6) | 4 | 2 | 0.549928 | 0.500000 | 0.049928 | 0.049928 |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 2 | 2 | 0.836698 | 1.000000 | -0.163302 | 0.163302 |
| [0.9,1.0] | 2 | 2 | 0.953795 | 1.000000 | -0.046205 | 0.046205 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 8/12 | 2 | 66.67% | 66.67% | 25.00% |
| 0.70 | 4/12 | 0 | 33.33% | 33.33% | 0.00% |
| 0.80 | 4/12 | 0 | 33.33% | 33.33% | 0.00% |
| 0.90 | 2/12 | 0 | 16.67% | 16.67% | 0.00% |
| 0.95 | 1/12 | 0 | 8.33% | 8.33% | 0.00% |
| 0.99 | 0/12 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: de_clean_beitragsrechnung_007, de_clean_beitragsrechnung_005
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## finance100 / category=synthetic_rule_check / language=en / schema_language=en / decision


Gruppen-ID: `finance100__003a25e58ebc32b2`. Optionen (5): conflict, fails, missing, out_of_scope, passes.
Erwartet 2; gültig 2; ungültig 0; fehlend 0. Richtig 1/2; Genauigkeit 50.00%.
Gold-Klassen: `{"fails": 1, "passes": 1}`. Native Auswahl: `{"passes": 2}`.
Brier (Klassensumme, 0–2): 0.593431; NLL (nats): 0.922033; Gold-p=0: 0; ECE: 0.436683.
Mittlerer Auswahlscore: 0.763271; Score−Genauigkeit: 0.263271; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: 1.000000 (richtig=1, falsch=1).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 1 | 0 | 0.699954 | 0.000000 | 0.699954 | 0.699954 |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 1 | 1 | 0.826588 | 1.000000 | -0.173412 | 0.173412 |
| [0.9,1.0] | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 2/2 | 1 | 100.00% | 100.00% | 50.00% |
| 0.70 | 1/2 | 0 | 50.00% | 50.00% | 0.00% |
| 0.80 | 1/2 | 0 | 50.00% | 50.00% | 0.00% |
| 0.90 | 0/2 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.95 | 0/2 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.99 | 0/2 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: en_finance_synthetic_rule_check_004
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## finance100 / category=broker_workflow / language=en / schema_language=en / decision


Gruppen-ID: `finance100__0a4521845e3eb697`. Optionen (5): conflict, missing_authority, missing_consent, missing_documents, ready.
Erwartet 3; gültig 3; ungültig 0; fehlend 0. Richtig 3/3; Genauigkeit 100.00%.
Gold-Klassen: `{"conflict": 1, "missing_consent": 1, "ready": 1}`. Native Auswahl: `{"conflict": 1, "missing_consent": 1, "ready": 1}`.
Brier (Klassensumme, 0–2): 0.012076; NLL (nats): 0.089557; Gold-p=0: 0; ECE: 0.084451.
Mittlerer Auswahlscore: 0.915549; Score−Genauigkeit: -0.084451; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=3, falsch=0).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 1 | 1 | 0.849927 | 1.000000 | -0.150073 | 0.150073 |
| [0.9,1.0] | 2 | 2 | 0.948360 | 1.000000 | -0.051640 | 0.051640 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 3/3 | 0 | 100.00% | 100.00% | 0.00% |
| 0.70 | 3/3 | 0 | 100.00% | 100.00% | 0.00% |
| 0.80 | 3/3 | 0 | 100.00% | 100.00% | 0.00% |
| 0.90 | 2/3 | 0 | 66.67% | 66.67% | 0.00% |
| 0.95 | 1/3 | 0 | 33.33% | 33.33% | 0.00% |
| 0.99 | 0/3 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: keine
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## finance100 / category=finance_intent / language=en / schema_language=en / decision


Gruppen-ID: `finance100__1a5c3b9641f8d02a`. Optionen (5): clarify, general_info, portfolio_view, recommendation, savings_change.
Erwartet 2; gültig 2; ungültig 0; fehlend 0. Richtig 2/2; Genauigkeit 100.00%.
Gold-Klassen: `{"general_info": 1, "recommendation": 1}`. Native Auswahl: `{"general_info": 1, "recommendation": 1}`.
Brier (Klassensumme, 0–2): 0.000117; NLL (nats): 0.008525; Gold-p=0: 0; ECE: 0.008479.
Mittlerer Auswahlscore: 0.991521; Score−Genauigkeit: -0.008479; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=2, falsch=0).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.9,1.0] | 2 | 2 | 0.991521 | 1.000000 | -0.008479 | 0.008479 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 2/2 | 0 | 100.00% | 100.00% | 0.00% |
| 0.70 | 2/2 | 0 | 100.00% | 100.00% | 0.00% |
| 0.80 | 2/2 | 0 | 100.00% | 100.00% | 0.00% |
| 0.90 | 2/2 | 0 | 100.00% | 100.00% | 0.00% |
| 0.95 | 2/2 | 0 | 100.00% | 100.00% | 0.00% |
| 0.99 | 1/2 | 0 | 50.00% | 50.00% | 0.00% |

Fehler-IDs je fester Schwelle:
- ≥0.50: keine
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## finance100 / category=insurance_intent / language=en / schema_language=en / decision


Gruppen-ID: `finance100__31c25197c2a424db`. Optionen (5): clarify, contribution, coverage_info, quote, termination.
Erwartet 3; gültig 3; ungültig 0; fehlend 0. Richtig 3/3; Genauigkeit 100.00%.
Gold-Klassen: `{"clarify": 1, "quote": 1, "termination": 1}`. Native Auswahl: `{"clarify": 1, "quote": 1, "termination": 1}`.
Brier (Klassensumme, 0–2): 0.183054; NLL (nats): 0.344516; Gold-p=0: 0; ECE: 0.217722.
Mittlerer Auswahlscore: 0.782278; Score−Genauigkeit: -0.217722; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=3, falsch=0).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 1 | 1 | 0.360746 | 1.000000 | -0.639254 | 0.639254 |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.9,1.0] | 2 | 2 | 0.993044 | 1.000000 | -0.006956 | 0.006956 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 2/3 | 0 | 66.67% | 66.67% | 0.00% |
| 0.70 | 2/3 | 0 | 66.67% | 66.67% | 0.00% |
| 0.80 | 2/3 | 0 | 66.67% | 66.67% | 0.00% |
| 0.90 | 2/3 | 0 | 66.67% | 66.67% | 0.00% |
| 0.95 | 2/3 | 0 | 66.67% | 66.67% | 0.00% |
| 0.99 | 2/3 | 0 | 66.67% | 66.67% | 0.00% |

Fehler-IDs je fester Schwelle:
- ≥0.50: keine
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## finance100 / category=advice_escalation / language=en / schema_language=en / decision


Gruppen-ID: `finance100__337cfbef82dbcf8d`. Optionen (5): clarify, out_of_scope, prohibited_request, qualified_review, routine.
Erwartet 2; gültig 2; ungültig 0; fehlend 0. Richtig 2/2; Genauigkeit 100.00%.
Gold-Klassen: `{"prohibited_request": 1, "routine": 1}`. Native Auswahl: `{"prohibited_request": 1, "routine": 1}`.
Brier (Klassensumme, 0–2): 0.019704; NLL (nats): 0.105699; Gold-p=0: 0; ECE: 0.097205.
Mittlerer Auswahlscore: 0.902795; Score−Genauigkeit: -0.097205; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=2, falsch=0).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 1 | 1 | 0.828048 | 1.000000 | -0.171952 | 0.171952 |
| [0.9,1.0] | 1 | 1 | 0.977541 | 1.000000 | -0.022459 | 0.022459 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 2/2 | 0 | 100.00% | 100.00% | 0.00% |
| 0.70 | 2/2 | 0 | 100.00% | 100.00% | 0.00% |
| 0.80 | 2/2 | 0 | 100.00% | 100.00% | 0.00% |
| 0.90 | 1/2 | 0 | 50.00% | 50.00% | 0.00% |
| 0.95 | 1/2 | 0 | 50.00% | 50.00% | 0.00% |
| 0.99 | 0/2 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: keine
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## finance100 / category=insurance_intent / language=de / schema_language=de / decision


Gruppen-ID: `finance100__35c4db838eaa877a`. Optionen (5): clarify, contribution, coverage_info, quote, termination.
Erwartet 10; gültig 10; ungültig 0; fehlend 0. Richtig 9/10; Genauigkeit 90.00%.
Gold-Klassen: `{"clarify": 2, "contribution": 2, "coverage_info": 2, "quote": 2, "termination": 2}`. Native Auswahl: `{"clarify": 1, "contribution": 2, "coverage_info": 3, "quote": 2, "termination": 2}`.
Brier (Klassensumme, 0–2): 0.206736; NLL (nats): 0.362380; Gold-p=0: 0; ECE: 0.177473.
Mittlerer Auswahlscore: 0.886414; Score−Genauigkeit: -0.013586; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: 0.888889 (richtig=9, falsch=1).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 1 | 1 | 0.321999 | 1.000000 | -0.678001 | 0.678001 |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 1 | 0 | 0.819438 | 0.000000 | 0.819438 | 0.819438 |
| [0.9,1.0] | 8 | 8 | 0.965338 | 1.000000 | -0.034662 | 0.034662 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 9/10 | 1 | 90.00% | 90.00% | 11.11% |
| 0.70 | 9/10 | 1 | 90.00% | 90.00% | 11.11% |
| 0.80 | 9/10 | 1 | 90.00% | 90.00% | 11.11% |
| 0.90 | 8/10 | 0 | 80.00% | 80.00% | 0.00% |
| 0.95 | 7/10 | 0 | 70.00% | 70.00% | 0.00% |
| 0.99 | 0/10 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: de_finance_insurance_intent_010
- ≥0.70: de_finance_insurance_intent_010
- ≥0.80: de_finance_insurance_intent_010
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## finance100 / category=contract_service / language=de / schema_language=de / decision


Gruppen-ID: `finance100__6e1bebcf8d6d8b71`. Optionen (5): cancellation, clarify, copy, data_change, withdrawal.
Erwartet 10; gültig 10; ungültig 0; fehlend 0. Richtig 10/10; Genauigkeit 100.00%.
Gold-Klassen: `{"cancellation": 2, "clarify": 2, "copy": 2, "data_change": 2, "withdrawal": 2}`. Native Auswahl: `{"cancellation": 2, "clarify": 2, "copy": 2, "data_change": 2, "withdrawal": 2}`.
Brier (Klassensumme, 0–2): 0.061482; NLL (nats): 0.155285; Gold-p=0: 0; ECE: 0.116752.
Mittlerer Auswahlscore: 0.883248; Score−Genauigkeit: -0.116752; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=10, falsch=0).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 1 | 1 | 0.391571 | 1.000000 | -0.608429 | 0.608429 |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 1 | 1 | 0.719532 | 1.000000 | -0.280468 | 0.280468 |
| [0.8,0.9) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.9,1.0] | 8 | 8 | 0.965173 | 1.000000 | -0.034827 | 0.034827 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 9/10 | 0 | 90.00% | 90.00% | 0.00% |
| 0.70 | 9/10 | 0 | 90.00% | 90.00% | 0.00% |
| 0.80 | 8/10 | 0 | 80.00% | 80.00% | 0.00% |
| 0.90 | 8/10 | 0 | 80.00% | 80.00% | 0.00% |
| 0.95 | 6/10 | 0 | 60.00% | 60.00% | 0.00% |
| 0.99 | 0/10 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: keine
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## finance100 / category=finance_intent / language=de / schema_language=de / decision


Gruppen-ID: `finance100__72e5dedf12fb7d13`. Optionen (5): clarify, general_info, portfolio_view, recommendation, savings_change.
Erwartet 10; gültig 10; ungültig 0; fehlend 0. Richtig 9/10; Genauigkeit 90.00%.
Gold-Klassen: `{"clarify": 2, "general_info": 2, "portfolio_view": 2, "recommendation": 2, "savings_change": 2}`. Native Auswahl: `{"clarify": 1, "general_info": 2, "portfolio_view": 3, "recommendation": 2, "savings_change": 2}`.
Brier (Klassensumme, 0–2): 0.190112; NLL (nats): 0.410826; Gold-p=0: 0; ECE: 0.092965.
Mittlerer Auswahlscore: 0.945021; Score−Genauigkeit: 0.045021; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: 0.777778 (richtig=9, falsch=1).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 1 | 1 | 0.760278 | 1.000000 | -0.239722 | 0.239722 |
| [0.8,0.9) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.9,1.0] | 9 | 8 | 0.965548 | 0.888889 | 0.076659 | 0.076659 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 10/10 | 1 | 100.00% | 100.00% | 10.00% |
| 0.70 | 10/10 | 1 | 100.00% | 100.00% | 10.00% |
| 0.80 | 9/10 | 1 | 90.00% | 90.00% | 11.11% |
| 0.90 | 9/10 | 1 | 90.00% | 90.00% | 11.11% |
| 0.95 | 7/10 | 0 | 70.00% | 70.00% | 0.00% |
| 0.99 | 1/10 | 0 | 10.00% | 10.00% | 0.00% |

Fehler-IDs je fester Schwelle:
- ≥0.50: de_finance_finance_intent_010
- ≥0.70: de_finance_finance_intent_010
- ≥0.80: de_finance_finance_intent_010
- ≥0.90: de_finance_finance_intent_010
- ≥0.95: keine
- ≥0.99: keine

## finance100 / category=claims_route / language=de / schema_language=de / decision


Gruppen-ID: `finance100__92d985bf736fbc13`. Optionen (5): benefit_question, claim_status, clarify, evidence, new_claim.
Erwartet 10; gültig 10; ungültig 0; fehlend 0. Richtig 9/10; Genauigkeit 90.00%.
Gold-Klassen: `{"benefit_question": 2, "claim_status": 2, "clarify": 2, "evidence": 2, "new_claim": 2}`. Native Auswahl: `{"benefit_question": 2, "claim_status": 2, "clarify": 1, "evidence": 2, "new_claim": 3}`.
Brier (Klassensumme, 0–2): 0.201625; NLL (nats): 0.454843; Gold-p=0: 0; ECE: 0.122842.
Mittlerer Auswahlscore: 0.924105; Score−Genauigkeit: 0.024105; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: 0.666667 (richtig=9, falsch=1).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 2 | 2 | 0.753156 | 1.000000 | -0.246844 | 0.246844 |
| [0.8,0.9) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.9,1.0] | 8 | 7 | 0.966842 | 0.875000 | 0.091842 | 0.091842 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 10/10 | 1 | 100.00% | 100.00% | 10.00% |
| 0.70 | 10/10 | 1 | 100.00% | 100.00% | 10.00% |
| 0.80 | 8/10 | 1 | 80.00% | 80.00% | 12.50% |
| 0.90 | 8/10 | 1 | 80.00% | 80.00% | 12.50% |
| 0.95 | 6/10 | 0 | 60.00% | 60.00% | 0.00% |
| 0.99 | 2/10 | 0 | 20.00% | 20.00% | 0.00% |

Fehler-IDs je fester Schwelle:
- ≥0.50: de_finance_claims_route_010
- ≥0.70: de_finance_claims_route_010
- ≥0.80: de_finance_claims_route_010
- ≥0.90: de_finance_claims_route_010
- ≥0.95: keine
- ≥0.99: keine

## finance100 / category=broker_workflow / language=de / schema_language=de / decision


Gruppen-ID: `finance100__98e1ee3e27a7842c`. Optionen (5): conflict, missing_authority, missing_consent, missing_documents, ready.
Erwartet 10; gültig 10; ungültig 0; fehlend 0. Richtig 10/10; Genauigkeit 100.00%.
Gold-Klassen: `{"conflict": 2, "missing_authority": 2, "missing_consent": 2, "missing_documents": 2, "ready": 2}`. Native Auswahl: `{"conflict": 2, "missing_authority": 2, "missing_consent": 2, "missing_documents": 2, "ready": 2}`.
Brier (Klassensumme, 0–2): 0.031558; NLL (nats): 0.122001; Gold-p=0: 0; ECE: 0.105894.
Mittlerer Auswahlscore: 0.894106; Score−Genauigkeit: -0.105894; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=10, falsch=0).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 1 | 1 | 0.583136 | 1.000000 | -0.416864 | 0.416864 |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 1 | 1 | 0.797973 | 1.000000 | -0.202027 | 0.202027 |
| [0.8,0.9) | 1 | 1 | 0.892323 | 1.000000 | -0.107677 | 0.107677 |
| [0.9,1.0] | 7 | 7 | 0.952518 | 1.000000 | -0.047482 | 0.047482 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 10/10 | 0 | 100.00% | 100.00% | 0.00% |
| 0.70 | 9/10 | 0 | 90.00% | 90.00% | 0.00% |
| 0.80 | 8/10 | 0 | 80.00% | 80.00% | 0.00% |
| 0.90 | 7/10 | 0 | 70.00% | 70.00% | 0.00% |
| 0.95 | 5/10 | 0 | 50.00% | 50.00% | 0.00% |
| 0.99 | 0/10 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: keine
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## finance100 / category=broker_document / language=de / schema_language=de / decision


Gruppen-ID: `finance100__b66e74dc62b96a5b`. Optionen (5): advisory_record, application, authority, other, policy.
Erwartet 10; gültig 10; ungültig 0; fehlend 0. Richtig 10/10; Genauigkeit 100.00%.
Gold-Klassen: `{"advisory_record": 2, "application": 2, "authority": 2, "other": 2, "policy": 2}`. Native Auswahl: `{"advisory_record": 2, "application": 2, "authority": 2, "other": 2, "policy": 2}`.
Brier (Klassensumme, 0–2): 0.054192; NLL (nats): 0.150847; Gold-p=0: 0; ECE: 0.123362.
Mittlerer Auswahlscore: 0.876638; Score−Genauigkeit: -0.123362; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=10, falsch=0).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 2 | 2 | 0.570655 | 1.000000 | -0.429345 | 0.429345 |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.9,1.0] | 8 | 8 | 0.953134 | 1.000000 | -0.046866 | 0.046866 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 10/10 | 0 | 100.00% | 100.00% | 0.00% |
| 0.70 | 8/10 | 0 | 80.00% | 80.00% | 0.00% |
| 0.80 | 8/10 | 0 | 80.00% | 80.00% | 0.00% |
| 0.90 | 8/10 | 0 | 80.00% | 80.00% | 0.00% |
| 0.95 | 5/10 | 0 | 50.00% | 50.00% | 0.00% |
| 0.99 | 0/10 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: keine
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## finance100 / category=contract_service / language=en / schema_language=en / decision


Gruppen-ID: `finance100__ba56175a9339739a`. Optionen (5): cancellation, clarify, copy, data_change, withdrawal.
Erwartet 3; gültig 3; ungültig 0; fehlend 0. Richtig 3/3; Genauigkeit 100.00%.
Gold-Klassen: `{"cancellation": 1, "clarify": 1, "withdrawal": 1}`. Native Auswahl: `{"cancellation": 1, "clarify": 1, "withdrawal": 1}`.
Brier (Klassensumme, 0–2): 0.002020; NLL (nats): 0.033336; Gold-p=0: 0; ECE: 0.032534.
Mittlerer Auswahlscore: 0.967466; Score−Genauigkeit: -0.032534; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=3, falsch=0).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.9,1.0] | 3 | 3 | 0.967466 | 1.000000 | -0.032534 | 0.032534 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 3/3 | 0 | 100.00% | 100.00% | 0.00% |
| 0.70 | 3/3 | 0 | 100.00% | 100.00% | 0.00% |
| 0.80 | 3/3 | 0 | 100.00% | 100.00% | 0.00% |
| 0.90 | 3/3 | 0 | 100.00% | 100.00% | 0.00% |
| 0.95 | 2/3 | 0 | 66.67% | 66.67% | 0.00% |
| 0.99 | 1/3 | 0 | 33.33% | 33.33% | 0.00% |

Fehler-IDs je fester Schwelle:
- ≥0.50: keine
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## finance100 / category=claims_route / language=en / schema_language=en / decision


Gruppen-ID: `finance100__caa403c2e195e349`. Optionen (5): benefit_question, claim_status, clarify, evidence, new_claim.
Erwartet 3; gültig 3; ungültig 0; fehlend 0. Richtig 2/3; Genauigkeit 66.67%.
Gold-Klassen: `{"clarify": 1, "evidence": 1, "new_claim": 1}`. Native Auswahl: `{"evidence": 1, "new_claim": 2}`.
Brier (Klassensumme, 0–2): 0.438944; NLL (nats): 0.700946; Gold-p=0: 0; ECE: 0.257223.
Mittlerer Auswahlscore: 0.898319; Score−Genauigkeit: 0.231652; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: 1.000000 (richtig=2, falsch=1).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 1 | 0 | 0.733312 | 0.000000 | 0.733312 | 0.733312 |
| [0.8,0.9) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.9,1.0] | 2 | 2 | 0.980822 | 1.000000 | -0.019178 | 0.019178 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 3/3 | 1 | 100.00% | 100.00% | 33.33% |
| 0.70 | 3/3 | 1 | 100.00% | 100.00% | 33.33% |
| 0.80 | 2/3 | 0 | 66.67% | 66.67% | 0.00% |
| 0.90 | 2/3 | 0 | 66.67% | 66.67% | 0.00% |
| 0.95 | 2/3 | 0 | 66.67% | 66.67% | 0.00% |
| 0.99 | 0/3 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: en_finance_claims_route_009
- ≥0.70: en_finance_claims_route_009
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## finance100 / category=synthetic_rule_check / language=de / schema_language=de / decision


Gruppen-ID: `finance100__cd2baf659a12e49c`. Optionen (5): conflict, fails, missing, out_of_scope, passes.
Erwartet 10; gültig 10; ungültig 0; fehlend 0. Richtig 9/10; Genauigkeit 90.00%.
Gold-Klassen: `{"conflict": 2, "fails": 2, "missing": 2, "out_of_scope": 2, "passes": 2}`. Native Auswahl: `{"conflict": 2, "fails": 3, "missing": 2, "out_of_scope": 2, "passes": 1}`.
Brier (Klassensumme, 0–2): 0.223156; NLL (nats): 0.486072; Gold-p=0: 0; ECE: 0.197574.
Mittlerer Auswahlscore: 0.702426; Score−Genauigkeit: -0.197574; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: 0.888889 (richtig=9, falsch=1).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 6 | 5 | 0.639727 | 0.833333 | -0.193606 | 0.193606 |
| [0.7,0.8) | 1 | 1 | 0.705551 | 1.000000 | -0.294449 | 0.294449 |
| [0.8,0.9) | 3 | 3 | 0.826781 | 1.000000 | -0.173219 | 0.173219 |
| [0.9,1.0] | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 10/10 | 1 | 100.00% | 100.00% | 10.00% |
| 0.70 | 4/10 | 0 | 40.00% | 40.00% | 0.00% |
| 0.80 | 3/10 | 0 | 30.00% | 30.00% | 0.00% |
| 0.90 | 0/10 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.95 | 0/10 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.99 | 0/10 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: de_finance_synthetic_rule_check_002
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## finance100 / category=advice_escalation / language=de / schema_language=de / decision


Gruppen-ID: `finance100__ec28bf687af03177`. Optionen (5): clarify, out_of_scope, prohibited_request, qualified_review, routine.
Erwartet 10; gültig 10; ungültig 0; fehlend 0. Richtig 10/10; Genauigkeit 100.00%.
Gold-Klassen: `{"clarify": 2, "out_of_scope": 2, "prohibited_request": 2, "qualified_review": 2, "routine": 2}`. Native Auswahl: `{"clarify": 2, "out_of_scope": 2, "prohibited_request": 2, "qualified_review": 2, "routine": 2}`.
Brier (Klassensumme, 0–2): 0.027686; NLL (nats): 0.129776; Gold-p=0: 0; ECE: 0.116921.
Mittlerer Auswahlscore: 0.883079; Score−Genauigkeit: -0.116921; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=10, falsch=0).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 1 | 1 | 0.690045 | 1.000000 | -0.309955 | 0.309955 |
| [0.7,0.8) | 1 | 1 | 0.740789 | 1.000000 | -0.259211 | 0.259211 |
| [0.8,0.9) | 1 | 1 | 0.881830 | 1.000000 | -0.118170 | 0.118170 |
| [0.9,1.0] | 7 | 7 | 0.931160 | 1.000000 | -0.068840 | 0.068840 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 10/10 | 0 | 100.00% | 100.00% | 0.00% |
| 0.70 | 9/10 | 0 | 90.00% | 90.00% | 0.00% |
| 0.80 | 8/10 | 0 | 80.00% | 80.00% | 0.00% |
| 0.90 | 7/10 | 0 | 70.00% | 70.00% | 0.00% |
| 0.95 | 2/10 | 0 | 20.00% | 20.00% | 0.00% |
| 0.99 | 0/10 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: keine
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## finance100 / category=broker_document / language=en / schema_language=en / decision


Gruppen-ID: `finance100__f96e05493d071d5d`. Optionen (5): advisory_record, application, authority, other, policy.
Erwartet 2; gültig 2; ungültig 0; fehlend 0. Richtig 2/2; Genauigkeit 100.00%.
Gold-Klassen: `{"other": 1, "policy": 1}`. Native Auswahl: `{"other": 1, "policy": 1}`.
Brier (Klassensumme, 0–2): 0.008904; NLL (nats): 0.069765; Gold-p=0: 0; ECE: 0.065971.
Mittlerer Auswahlscore: 0.934029; Score−Genauigkeit: -0.065971; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=2, falsch=0).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 1 | 1 | 0.882608 | 1.000000 | -0.117392 | 0.117392 |
| [0.9,1.0] | 1 | 1 | 0.985450 | 1.000000 | -0.014550 | 0.014550 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 2/2 | 0 | 100.00% | 100.00% | 0.00% |
| 0.70 | 2/2 | 0 | 100.00% | 100.00% | 0.00% |
| 0.80 | 2/2 | 0 | 100.00% | 100.00% | 0.00% |
| 0.90 | 1/2 | 0 | 50.00% | 50.00% | 0.00% |
| 0.95 | 1/2 | 0 | 50.00% | 50.00% | 0.00% |
| 0.99 | 0/2 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: keine
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## images90 / kind=invoice / language=en / condition=image / document_type


Gruppen-ID: `images90__05d64addc349544d`. Optionen (2): gutschrift, rechnung.
Erwartet 10; gültig 10; ungültig 0; fehlend 0. Richtig 10/10; Genauigkeit 100.00%.
Gold-Klassen: `{"gutschrift": 3, "rechnung": 7}`. Native Auswahl: `{"gutschrift": 3, "rechnung": 7}`.
Brier (Klassensumme, 0–2): 0.001743; NLL (nats): 0.023294; Gold-p=0: 0; ECE: 0.022842.
Mittlerer Auswahlscore: 0.977158; Score−Genauigkeit: -0.022842; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=10, falsch=0).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.9,1.0] | 10 | 10 | 0.977158 | 1.000000 | -0.022842 | 0.022842 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 10/10 | 0 | 100.00% | 100.00% | 0.00% |
| 0.70 | 10/10 | 0 | 100.00% | 100.00% | 0.00% |
| 0.80 | 10/10 | 0 | 100.00% | 100.00% | 0.00% |
| 0.90 | 10/10 | 0 | 100.00% | 100.00% | 0.00% |
| 0.95 | 9/10 | 0 | 90.00% | 90.00% | 0.00% |
| 0.99 | 2/10 | 0 | 20.00% | 20.00% | 0.00% |

Fehler-IDs je fester Schwelle:
- ≥0.50: keine
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## images90 / kind=invoice / language=de / condition=image / document_type


Gruppen-ID: `images90__0eb3fed9ffd5e4f8`. Optionen (2): gutschrift, rechnung.
Erwartet 20; gültig 20; ungültig 0; fehlend 0. Richtig 20/20; Genauigkeit 100.00%.
Gold-Klassen: `{"gutschrift": 4, "rechnung": 16}`. Native Auswahl: `{"gutschrift": 4, "rechnung": 16}`.
Brier (Klassensumme, 0–2): 0.000519; NLL (nats): 0.015411; Gold-p=0: 0; ECE: 0.015279.
Mittlerer Auswahlscore: 0.984721; Score−Genauigkeit: -0.015279; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=20, falsch=0).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.9,1.0] | 20 | 20 | 0.984721 | 1.000000 | -0.015279 | 0.015279 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 20/20 | 0 | 100.00% | 100.00% | 0.00% |
| 0.70 | 20/20 | 0 | 100.00% | 100.00% | 0.00% |
| 0.80 | 20/20 | 0 | 100.00% | 100.00% | 0.00% |
| 0.90 | 20/20 | 0 | 100.00% | 100.00% | 0.00% |
| 0.95 | 20/20 | 0 | 100.00% | 100.00% | 0.00% |
| 0.99 | 0/20 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: keine
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## images90 / kind=invoice / language=de / condition=image / tax_note


Gruppen-ID: `images90__1a6c9fb460e87c94`. Optionen (3): regular, reverse_charge, small_business.
Erwartet 20; gültig 20; ungültig 0; fehlend 0. Richtig 19/20; Genauigkeit 95.00%.
Gold-Klassen: `{"regular": 12, "reverse_charge": 3, "small_business": 5}`. Native Auswahl: `{"regular": 13, "reverse_charge": 3, "small_business": 4}`.
Brier (Klassensumme, 0–2): 0.057851; NLL (nats): 0.124957; Gold-p=0: 0; ECE: 0.085804.
Mittlerer Auswahlscore: 0.927428; Score−Genauigkeit: -0.022572; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: 1.000000 (richtig=19, falsch=1).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 1 | 0 | 0.632319 | 0.000000 | 0.632319 | 0.632319 |
| [0.7,0.8) | 1 | 1 | 0.777010 | 1.000000 | -0.222990 | 0.222990 |
| [0.8,0.9) | 1 | 1 | 0.808057 | 1.000000 | -0.191943 | 0.191943 |
| [0.9,1.0] | 17 | 17 | 0.960657 | 1.000000 | -0.039343 | 0.039343 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 20/20 | 1 | 100.00% | 100.00% | 5.00% |
| 0.70 | 19/20 | 0 | 95.00% | 95.00% | 0.00% |
| 0.80 | 18/20 | 0 | 90.00% | 90.00% | 0.00% |
| 0.90 | 17/20 | 0 | 85.00% | 85.00% | 0.00% |
| 0.95 | 16/20 | 0 | 80.00% | 80.00% | 0.00% |
| 0.99 | 0/20 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: invoice-006-de-image
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## images90 / kind=invoice / language=de / condition=blank / gross_band


Gruppen-ID: `images90__1e6757383c4dea64`. Optionen (5): 1000_5000, 5000_20000, negative, over_20000, zero_1000.
Erwartet 10; gültig 10; ungültig 0; fehlend 0. Richtig 3/10; Genauigkeit 30.00%.
Gold-Klassen: `{"1000_5000": 2, "5000_20000": 2, "negative": 3, "over_20000": 2, "zero_1000": 1}`. Native Auswahl: `{"negative": 10}`.
Brier (Klassensumme, 0–2): 0.955117; NLL (nats): 2.020754; Gold-p=0: 0; ECE: 0.323396.
Mittlerer Auswahlscore: 0.623396; Score−Genauigkeit: 0.323396; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: 0.666667 (richtig=3, falsch=7).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 10 | 3 | 0.623396 | 0.300000 | 0.323396 | 0.323396 |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.9,1.0] | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 10/10 | 7 | 100.00% | 100.00% | 70.00% |
| 0.70 | 0/10 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.80 | 0/10 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.90 | 0/10 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.95 | 0/10 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.99 | 0/10 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: invoice-004-de-blank, invoice-001-de-blank, invoice-007-de-blank, invoice-006-de-blank, invoice-002-de-blank, invoice-017-de-blank, invoice-011-de-blank
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## images90 / kind=chart / language=en / condition=image / legend_count


Gruppen-ID: `images90__20b09810f03e0452`. Optionen (11): 0, 1, 10, 2, 3, 4, 5, 6, 7, 8, 9.
Erwartet 10; gültig 10; ungültig 0; fehlend 0. Richtig 10/10; Genauigkeit 100.00%.
Gold-Klassen: `{"2": 1, "3": 2, "4": 6, "5": 1}`. Native Auswahl: `{"2": 1, "3": 2, "4": 6, "5": 1}`.
Brier (Klassensumme, 0–2): 0.079117; NLL (nats): 0.259142; Gold-p=0: 0; ECE: 0.205563.
Mittlerer Auswahlscore: 0.794437; Score−Genauigkeit: -0.205563; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=10, falsch=0).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 1 | 1 | 0.363222 | 1.000000 | -0.636778 | 0.636778 |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 1 | 1 | 0.668544 | 1.000000 | -0.331456 | 0.331456 |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 6 | 6 | 0.847525 | 1.000000 | -0.152475 | 0.152475 |
| [0.9,1.0] | 2 | 2 | 0.913725 | 1.000000 | -0.086275 | 0.086275 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 9/10 | 0 | 90.00% | 90.00% | 0.00% |
| 0.70 | 8/10 | 0 | 80.00% | 80.00% | 0.00% |
| 0.80 | 8/10 | 0 | 80.00% | 80.00% | 0.00% |
| 0.90 | 2/10 | 0 | 20.00% | 20.00% | 0.00% |
| 0.95 | 0/10 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.99 | 0/10 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: keine
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## images90 / kind=invoice / language=de / condition=blank / tax_note


Gruppen-ID: `images90__294e1315a9a2bb84`. Optionen (3): regular, reverse_charge, small_business.
Erwartet 10; gültig 10; ungültig 0; fehlend 0. Richtig 5/10; Genauigkeit 50.00%.
Gold-Klassen: `{"regular": 5, "reverse_charge": 2, "small_business": 3}`. Native Auswahl: `{"regular": 10}`.
Brier (Klassensumme, 0–2): 0.661407; NLL (nats): 1.115261; Gold-p=0: 0; ECE: 0.167744.
Mittlerer Auswahlscore: 0.667744; Score−Genauigkeit: 0.167744; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: 0.680000 (richtig=5, falsch=5).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 10 | 5 | 0.667744 | 0.500000 | 0.167744 | 0.167744 |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.9,1.0] | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 10/10 | 5 | 100.00% | 100.00% | 50.00% |
| 0.70 | 0/10 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.80 | 0/10 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.90 | 0/10 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.95 | 0/10 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.99 | 0/10 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: invoice-004-de-blank, invoice-007-de-blank, invoice-006-de-blank, invoice-017-de-blank, invoice-011-de-blank
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## images90 / kind=chart / language=de / condition=blank / chart_type

Hinweis für chart_type: Die Werte sind strikt relativ zum unveränderten Quellen-Gold. Die Optionen bar_line/vbar2 haben dokumentiert überlappende Beschreibungen. Eine gold-relative Abweichung ist deshalb nicht automatisch ein eindeutig validierter Modellfehler; keine nachträgliche Umetikettierung oder Auslassung.
Gruppen-ID: `images90__2ea1855173e8d440`. Optionen (10): bar_line, bar_pie, hbar, hbar2, line, pie, stack_hbar, stack_vbar, vbar, vbar2.
Erwartet 10; gültig 10; ungültig 0; fehlend 0. Richtig 1/10; Genauigkeit 10.00%.
Gold-Klassen: `{"bar_line": 1, "bar_pie": 1, "hbar": 1, "hbar2": 1, "line": 1, "pie": 1, "stack_hbar": 1, "stack_vbar": 1, "vbar": 1, "vbar2": 1}`. Native Auswahl: `{"vbar": 10}`.
Brier (Klassensumme, 0–2): 0.906373; NLL (nats): 2.323540; Gold-p=0: 0; ECE: 0.080319.
Mittlerer Auswahlscore: 0.180319; Score−Genauigkeit: 0.080319; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: 0.500000 (richtig=1, falsch=9).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 8 | 1 | 0.174068 | 0.125000 | 0.049068 | 0.049068 |
| [0.2,0.3) | 2 | 0 | 0.205326 | 0.000000 | 0.205326 | 0.205326 |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.9,1.0] | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 0/10 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.70 | 0/10 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.80 | 0/10 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.90 | 0/10 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.95 | 0/10 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.99 | 0/10 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: keine
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## images90 / kind=chart / language=de / condition=image / chart_type

Hinweis für chart_type: Die Werte sind strikt relativ zum unveränderten Quellen-Gold. Die Optionen bar_line/vbar2 haben dokumentiert überlappende Beschreibungen. Eine gold-relative Abweichung ist deshalb nicht automatisch ein eindeutig validierter Modellfehler; keine nachträgliche Umetikettierung oder Auslassung.
Gruppen-ID: `images90__3c0ebde5b2869bf5`. Optionen (10): bar_line, bar_pie, hbar, hbar2, line, pie, stack_hbar, stack_vbar, vbar, vbar2.
Erwartet 30; gültig 30; ungültig 0; fehlend 0. Richtig 27/30; Genauigkeit 90.00%.
Gold-Klassen: `{"bar_line": 3, "bar_pie": 3, "hbar": 3, "hbar2": 3, "line": 3, "pie": 3, "stack_hbar": 3, "stack_vbar": 3, "vbar": 3, "vbar2": 3}`. Native Auswahl: `{"bar_pie": 3, "hbar": 3, "hbar2": 3, "line": 3, "pie": 3, "stack_hbar": 3, "stack_vbar": 3, "vbar": 3, "vbar2": 6}`.
Brier (Klassensumme, 0–2): 0.152003; NLL (nats): 0.288684; Gold-p=0: 0; ECE: 0.081501.
Mittlerer Auswahlscore: 0.896811; Score−Genauigkeit: -0.003189; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: 0.925926 (richtig=27, falsch=3).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 2 | 1 | 0.738003 | 0.500000 | 0.238003 | 0.238003 |
| [0.8,0.9) | 10 | 8 | 0.869868 | 0.800000 | 0.069868 | 0.069868 |
| [0.9,1.0] | 18 | 18 | 0.929425 | 1.000000 | -0.070575 | 0.070575 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 30/30 | 3 | 100.00% | 100.00% | 10.00% |
| 0.70 | 30/30 | 3 | 100.00% | 100.00% | 10.00% |
| 0.80 | 28/30 | 2 | 93.33% | 93.33% | 7.14% |
| 0.90 | 18/30 | 0 | 60.00% | 60.00% | 0.00% |
| 0.95 | 4/30 | 0 | 13.33% | 13.33% | 0.00% |
| 0.99 | 0/30 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: chart-001-de-image, chart-002-de-image, chart-003-de-image
- ≥0.70: chart-001-de-image, chart-002-de-image, chart-003-de-image
- ≥0.80: chart-002-de-image, chart-003-de-image
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## images90 / kind=chart / language=en / condition=image / chart_type

Hinweis für chart_type: Die Werte sind strikt relativ zum unveränderten Quellen-Gold. Die Optionen bar_line/vbar2 haben dokumentiert überlappende Beschreibungen. Eine gold-relative Abweichung ist deshalb nicht automatisch ein eindeutig validierter Modellfehler; keine nachträgliche Umetikettierung oder Auslassung.
Gruppen-ID: `images90__443ab18f8d48ac7b`. Optionen (10): bar_line, bar_pie, hbar, hbar2, line, pie, stack_hbar, stack_vbar, vbar, vbar2.
Erwartet 10; gültig 10; ungültig 0; fehlend 0. Richtig 9/10; Genauigkeit 90.00%.
Gold-Klassen: `{"bar_line": 1, "bar_pie": 1, "hbar": 1, "hbar2": 1, "line": 1, "pie": 1, "stack_hbar": 1, "stack_vbar": 1, "vbar": 1, "vbar2": 1}`. Native Auswahl: `{"bar_pie": 1, "hbar": 1, "hbar2": 1, "line": 1, "pie": 1, "stack_hbar": 1, "stack_vbar": 1, "vbar": 1, "vbar2": 2}`.
Brier (Klassensumme, 0–2): 0.140309; NLL (nats): 0.253499; Gold-p=0: 0; ECE: 0.146582.
Mittlerer Auswahlscore: 0.912613; Score−Genauigkeit: 0.012613; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: 1.000000 (richtig=9, falsch=1).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 1 | 0 | 0.795978 | 0.000000 | 0.795978 | 0.795978 |
| [0.8,0.9) | 1 | 1 | 0.894255 | 1.000000 | -0.105745 | 0.105745 |
| [0.9,1.0] | 8 | 8 | 0.929488 | 1.000000 | -0.070512 | 0.070512 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 10/10 | 1 | 100.00% | 100.00% | 10.00% |
| 0.70 | 10/10 | 1 | 100.00% | 100.00% | 10.00% |
| 0.80 | 9/10 | 0 | 90.00% | 90.00% | 0.00% |
| 0.90 | 8/10 | 0 | 80.00% | 80.00% | 0.00% |
| 0.95 | 1/10 | 0 | 10.00% | 10.00% | 0.00% |
| 0.99 | 0/10 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: chart-003-en-image
- ≥0.70: chart-003-en-image
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## images90 / kind=invoice / language=de / condition=blank / document_type


Gruppen-ID: `images90__4d23526375b25fc5`. Optionen (2): gutschrift, rechnung.
Erwartet 10; gültig 10; ungültig 0; fehlend 0. Richtig 4/10; Genauigkeit 40.00%.
Gold-Klassen: `{"gutschrift": 3, "rechnung": 7}`. Native Auswahl: `{"gutschrift": 7, "rechnung": 3}`.
Brier (Klassensumme, 0–2): 0.512629; NLL (nats): 0.705801; Gold-p=0: 0; ECE: 0.130853.
Mittlerer Auswahlscore: 0.530853; Score−Genauigkeit: 0.130853; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: 0.458333 (richtig=4, falsch=6).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 10 | 4 | 0.530853 | 0.400000 | 0.130853 | 0.130853 |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.9,1.0] | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 10/10 | 6 | 100.00% | 100.00% | 60.00% |
| 0.70 | 0/10 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.80 | 0/10 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.90 | 0/10 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.95 | 0/10 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.99 | 0/10 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: invoice-001-de-blank, invoice-007-de-blank, invoice-016-de-blank, invoice-002-de-blank, invoice-017-de-blank, invoice-011-de-blank
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## images90 / kind=chart / language=de / condition=blank / legend_count


Gruppen-ID: `images90__562c3cee45964799`. Optionen (11): 0, 1, 10, 2, 3, 4, 5, 6, 7, 8, 9.
Erwartet 10; gültig 10; ungültig 0; fehlend 0. Richtig 0/10; Genauigkeit 0.00%.
Gold-Klassen: `{"2": 1, "3": 2, "4": 6, "5": 1}`. Native Auswahl: `{"0": 10}`.
Brier (Klassensumme, 0–2): 1.795681; NLL (nats): 4.550786; Gold-p=0: 0; ECE: 0.903219.
Mittlerer Auswahlscore: 0.903219; Score−Genauigkeit: 0.903219; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=0, falsch=10).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 3 | 0 | 0.882923 | 0.000000 | 0.882923 | 0.882923 |
| [0.9,1.0] | 7 | 0 | 0.911917 | 0.000000 | 0.911917 | 0.911917 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 10/10 | 10 | 100.00% | 100.00% | 100.00% |
| 0.70 | 10/10 | 10 | 100.00% | 100.00% | 100.00% |
| 0.80 | 10/10 | 10 | 100.00% | 100.00% | 100.00% |
| 0.90 | 7/10 | 7 | 70.00% | 70.00% | 100.00% |
| 0.95 | 0/10 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.99 | 0/10 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: chart-003-de-blank, chart-006-de-blank, chart-009-de-blank, chart-012-de-blank, chart-015-de-blank, chart-018-de-blank, chart-021-de-blank, chart-024-de-blank, chart-027-de-blank, chart-030-de-blank
- ≥0.70: chart-003-de-blank, chart-006-de-blank, chart-009-de-blank, chart-012-de-blank, chart-015-de-blank, chart-018-de-blank, chart-021-de-blank, chart-024-de-blank, chart-027-de-blank, chart-030-de-blank
- ≥0.80: chart-003-de-blank, chart-006-de-blank, chart-009-de-blank, chart-012-de-blank, chart-015-de-blank, chart-018-de-blank, chart-021-de-blank, chart-024-de-blank, chart-027-de-blank, chart-030-de-blank
- ≥0.90: chart-003-de-blank, chart-009-de-blank, chart-012-de-blank, chart-015-de-blank, chart-024-de-blank, chart-027-de-blank, chart-030-de-blank
- ≥0.95: keine
- ≥0.99: keine

## images90 / kind=invoice / language=en / condition=image / gross_band


Gruppen-ID: `images90__784be2826d816b7c`. Optionen (5): 1000_5000, 5000_20000, negative, over_20000, zero_1000.
Erwartet 10; gültig 10; ungültig 0; fehlend 0. Richtig 8/10; Genauigkeit 80.00%.
Gold-Klassen: `{"1000_5000": 2, "5000_20000": 2, "negative": 3, "over_20000": 2, "zero_1000": 1}`. Native Auswahl: `{"1000_5000": 2, "5000_20000": 3, "negative": 1, "over_20000": 3, "zero_1000": 1}`.
Brier (Klassensumme, 0–2): 0.177749; NLL (nats): 0.299433; Gold-p=0: 0; ECE: 0.202387.
Mittlerer Auswahlscore: 0.845865; Score−Genauigkeit: 0.045865; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: 1.000000 (richtig=8, falsch=2).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 1 | 0 | 0.598445 | 0.000000 | 0.598445 | 0.598445 |
| [0.6,0.7) | 1 | 0 | 0.642812 | 0.000000 | 0.642812 | 0.642812 |
| [0.7,0.8) | 1 | 1 | 0.772583 | 1.000000 | -0.227417 | 0.227417 |
| [0.8,0.9) | 3 | 3 | 0.877703 | 1.000000 | -0.122297 | 0.122297 |
| [0.9,1.0] | 4 | 4 | 0.952924 | 1.000000 | -0.047076 | 0.047076 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 10/10 | 2 | 100.00% | 100.00% | 20.00% |
| 0.70 | 8/10 | 0 | 80.00% | 80.00% | 0.00% |
| 0.80 | 7/10 | 0 | 70.00% | 70.00% | 0.00% |
| 0.90 | 4/10 | 0 | 40.00% | 40.00% | 0.00% |
| 0.95 | 2/10 | 0 | 20.00% | 20.00% | 0.00% |
| 0.99 | 0/10 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: invoice-009-en-image, invoice-016-en-image
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## images90 / kind=invoice / language=en / condition=image / tax_note


Gruppen-ID: `images90__856cc192270b48ea`. Optionen (3): regular, reverse_charge, small_business.
Erwartet 10; gültig 10; ungültig 0; fehlend 0. Richtig 10/10; Genauigkeit 100.00%.
Gold-Klassen: `{"regular": 5, "reverse_charge": 2, "small_business": 3}`. Native Auswahl: `{"regular": 5, "reverse_charge": 2, "small_business": 3}`.
Brier (Klassensumme, 0–2): 0.051153; NLL (nats): 0.112578; Gold-p=0: 0; ECE: 0.092002.
Mittlerer Auswahlscore: 0.907998; Score−Genauigkeit: -0.092002; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=10, falsch=0).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 1 | 1 | 0.504726 | 1.000000 | -0.495274 | 0.495274 |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 1 | 1 | 0.852309 | 1.000000 | -0.147691 | 0.147691 |
| [0.9,1.0] | 8 | 8 | 0.965368 | 1.000000 | -0.034632 | 0.034632 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 10/10 | 0 | 100.00% | 100.00% | 0.00% |
| 0.70 | 9/10 | 0 | 90.00% | 90.00% | 0.00% |
| 0.80 | 9/10 | 0 | 90.00% | 90.00% | 0.00% |
| 0.90 | 8/10 | 0 | 80.00% | 80.00% | 0.00% |
| 0.95 | 8/10 | 0 | 80.00% | 80.00% | 0.00% |
| 0.99 | 0/10 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: keine
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## images90 / kind=chart / language=de / condition=image / legend_count


Gruppen-ID: `images90__a2588e7bebec6695`. Optionen (11): 0, 1, 10, 2, 3, 4, 5, 6, 7, 8, 9.
Erwartet 30; gültig 30; ungültig 0; fehlend 0. Richtig 30/30; Genauigkeit 100.00%.
Gold-Klassen: `{"2": 8, "3": 6, "4": 11, "5": 4, "7": 1}`. Native Auswahl: `{"2": 8, "3": 6, "4": 11, "5": 4, "7": 1}`.
Brier (Klassensumme, 0–2): 0.153544; NLL (nats): 0.418627; Gold-p=0: 0; ECE: 0.296006.
Mittlerer Auswahlscore: 0.703994; Score−Genauigkeit: -0.296006; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=30, falsch=0).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 1 | 1 | 0.166045 | 1.000000 | -0.833955 | 0.833955 |
| [0.2,0.3) | 2 | 2 | 0.269946 | 1.000000 | -0.730054 | 0.730054 |
| [0.3,0.4) | 2 | 2 | 0.377732 | 1.000000 | -0.622268 | 0.622268 |
| [0.4,0.5) | 1 | 1 | 0.489385 | 1.000000 | -0.510615 | 0.510615 |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 1 | 1 | 0.617800 | 1.000000 | -0.382200 | 0.382200 |
| [0.7,0.8) | 10 | 10 | 0.752390 | 1.000000 | -0.247610 | 0.247610 |
| [0.8,0.9) | 13 | 13 | 0.848257 | 1.000000 | -0.151743 | 0.151743 |
| [0.9,1.0] | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 24/30 | 0 | 80.00% | 80.00% | 0.00% |
| 0.70 | 23/30 | 0 | 76.67% | 76.67% | 0.00% |
| 0.80 | 13/30 | 0 | 43.33% | 43.33% | 0.00% |
| 0.90 | 0/30 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.95 | 0/30 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.99 | 0/30 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: keine
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## images90 / kind=invoice / language=de / condition=image / gross_band


Gruppen-ID: `images90__ed9d6dce76a53015`. Optionen (5): 1000_5000, 5000_20000, negative, over_20000, zero_1000.
Erwartet 20; gültig 20; ungültig 0; fehlend 0. Richtig 18/20; Genauigkeit 90.00%.
Gold-Klassen: `{"1000_5000": 4, "5000_20000": 4, "negative": 4, "over_20000": 4, "zero_1000": 4}`. Native Auswahl: `{"1000_5000": 4, "5000_20000": 5, "negative": 2, "over_20000": 5, "zero_1000": 4}`.
Brier (Klassensumme, 0–2): 0.174517; NLL (nats): 0.308011; Gold-p=0: 0; ECE: 0.117109.
Mittlerer Auswahlscore: 0.892038; Score−Genauigkeit: -0.007962; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: 0.916667 (richtig=18, falsch=2).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 1 | 1 | 0.520419 | 1.000000 | -0.479581 | 0.479581 |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 6 | 4 | 0.848579 | 0.666667 | 0.181912 | 0.181912 |
| [0.9,1.0] | 13 | 13 | 0.940683 | 1.000000 | -0.059317 | 0.059317 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 20/20 | 2 | 100.00% | 100.00% | 10.00% |
| 0.70 | 19/20 | 2 | 95.00% | 95.00% | 10.53% |
| 0.80 | 19/20 | 2 | 95.00% | 95.00% | 10.53% |
| 0.90 | 13/20 | 0 | 65.00% | 65.00% | 0.00% |
| 0.95 | 4/20 | 0 | 20.00% | 20.00% | 0.00% |
| 0.99 | 0/20 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: invoice-009-de-image, invoice-016-de-image
- ≥0.70: invoice-009-de-image, invoice-016-de-image
- ≥0.80: invoice-009-de-image, invoice-016-de-image
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## insurance60 / evidence


Gruppen-ID: `insurance60__197f61d943fbef6b`. Optionen (5): b1, b2, b3, b4, b5.
Erwartet 60; gültig 60; ungültig 0; fehlend 0. Richtig 58/60; Genauigkeit 96.67%.
Gold-Klassen: `{"b1": 20, "b2": 7, "b3": 12, "b4": 9, "b5": 12}`. Native Auswahl: `{"b1": 21, "b2": 7, "b3": 12, "b4": 10, "b5": 10}`.
Brier (Klassensumme, 0–2): 0.057100; NLL (nats): 0.175991; Gold-p=0: 0; ECE: 0.121475.
Mittlerer Auswahlscore: 0.865289; Score−Genauigkeit: -0.101378; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: 0.974138 (richtig=58, falsch=2).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 1 | 0 | 0.376703 | 0.000000 | 0.376703 | 0.376703 |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 2 | 2 | 0.578049 | 1.000000 | -0.421951 | 0.421951 |
| [0.6,0.7) | 2 | 1 | 0.613106 | 0.500000 | 0.113106 | 0.113106 |
| [0.7,0.8) | 4 | 4 | 0.758699 | 1.000000 | -0.241301 | 0.241301 |
| [0.8,0.9) | 20 | 20 | 0.861666 | 1.000000 | -0.138334 | 0.138334 |
| [0.9,1.0] | 31 | 31 | 0.931941 | 1.000000 | -0.068059 | 0.068059 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 59/60 | 1 | 98.33% | 98.33% | 1.69% |
| 0.70 | 55/60 | 0 | 91.67% | 91.67% | 0.00% |
| 0.80 | 51/60 | 0 | 85.00% | 85.00% | 0.00% |
| 0.90 | 31/60 | 0 | 51.67% | 51.67% | 0.00% |
| 0.95 | 6/60 | 0 | 10.00% | 10.00% | 0.00% |
| 0.99 | 0/60 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: fall_003
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## insurance60 / decision


Gruppen-ID: `insurance60__71203967574c9347`. Optionen (4): ja, konflikt, nein, offen.
Erwartet 60; gültig 60; ungültig 0; fehlend 0. Richtig 51/60; Genauigkeit 85.00%.
Gold-Klassen: `{"ja": 16, "konflikt": 3, "nein": 27, "offen": 14}`. Native Auswahl: `{"ja": 21, "konflikt": 5, "nein": 23, "offen": 11}`.
Brier (Klassensumme, 0–2): 0.213205; NLL (nats): 0.441639; Gold-p=0: 0; ECE: 0.098648.
Mittlerer Auswahlscore: 0.787177; Score−Genauigkeit: -0.062823; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: 0.877996 (richtig=51, falsch=9).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 1 | 0 | 0.463663 | 0.000000 | 0.463663 | 0.463663 |
| [0.5,0.6) | 3 | 1 | 0.537028 | 0.333333 | 0.203695 | 0.203695 |
| [0.6,0.7) | 9 | 6 | 0.654519 | 0.666667 | -0.012147 | 0.012147 |
| [0.7,0.8) | 15 | 13 | 0.758753 | 0.866667 | -0.107914 | 0.107914 |
| [0.8,0.9) | 22 | 21 | 0.852165 | 0.954545 | -0.102381 | 0.102381 |
| [0.9,1.0] | 10 | 10 | 0.913630 | 1.000000 | -0.086370 | 0.086370 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 59/60 | 8 | 98.33% | 98.33% | 13.56% |
| 0.70 | 47/60 | 3 | 78.33% | 78.33% | 6.38% |
| 0.80 | 32/60 | 1 | 53.33% | 53.33% | 3.12% |
| 0.90 | 10/60 | 0 | 16.67% | 16.67% | 0.00% |
| 0.95 | 1/60 | 0 | 1.67% | 1.67% | 0.00% |
| 0.99 | 0/60 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: fall_028, fall_029, fall_033, fall_035, fall_036, fall_047, fall_055, fall_056
- ≥0.70: fall_028, fall_036, fall_056
- ≥0.80: fall_028
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## minimal_pairs48 / determination


Gruppen-ID: `minimal_pairs48__b738496bdf013457`. Optionen (3): no, unresolved, yes.
Erwartet 48; gültig 48; ungültig 0; fehlend 0. Richtig 42/48; Genauigkeit 87.50%.
Gold-Klassen: `{"no": 17, "unresolved": 12, "yes": 19}`. Native Auswahl: `{"no": 16, "unresolved": 12, "yes": 20}`.
Brier (Klassensumme, 0–2): 0.207431; NLL (nats): 0.411574; Gold-p=0: 0; ECE: 0.115622.
Mittlerer Auswahlscore: 0.915301; Score−Genauigkeit: 0.040301; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: 0.765873 (richtig=42, falsch=6).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 1 | 1 | 0.488493 | 1.000000 | -0.511507 | 0.511507 |
| [0.5,0.6) | 1 | 0 | 0.548481 | 0.000000 | 0.548481 | 0.548481 |
| [0.6,0.7) | 1 | 0 | 0.614060 | 0.000000 | 0.614060 | 0.614060 |
| [0.7,0.8) | 2 | 2 | 0.747565 | 1.000000 | -0.252435 | 0.252435 |
| [0.8,0.9) | 7 | 7 | 0.886956 | 1.000000 | -0.113044 | 0.113044 |
| [0.9,1.0] | 36 | 32 | 0.960545 | 0.888889 | 0.071656 | 0.071656 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 47/48 | 6 | 97.92% | 97.92% | 12.77% |
| 0.70 | 45/48 | 4 | 93.75% | 93.75% | 8.89% |
| 0.80 | 43/48 | 4 | 89.58% | 89.58% | 9.30% |
| 0.90 | 36/48 | 4 | 75.00% | 75.00% | 11.11% |
| 0.95 | 26/48 | 0 | 54.17% | 54.17% | 0.00% |
| 0.99 | 0/48 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: pair_tow_distance_records_b, pair_report_delivery_target_b, pair_statement_notification_a, pair_report_delivery_target_a, pair_limit_order_price_step_a, pair_gadget_theft_notice_a
- ≥0.70: pair_report_delivery_target_b, pair_statement_notification_a, pair_report_delivery_target_a, pair_limit_order_price_step_a
- ≥0.80: pair_report_delivery_target_b, pair_statement_notification_a, pair_report_delivery_target_a, pair_limit_order_price_step_a
- ≥0.90: pair_report_delivery_target_b, pair_statement_notification_a, pair_report_delivery_target_a, pair_limit_order_price_step_a
- ≥0.95: keine
- ≥0.99: keine

## minimal_pairs48 / action


Gruppen-ID: `minimal_pairs48__cf953fa9734afe8f`. Optionen (4): answer, ask_fact, ask_target, resolve_conflict.
Erwartet 48; gültig 48; ungültig 0; fehlend 0. Richtig 40/48; Genauigkeit 83.33%.
Gold-Klassen: `{"answer": 36, "ask_fact": 4, "ask_target": 4, "resolve_conflict": 4}`. Native Auswahl: `{"answer": 36, "ask_fact": 4, "ask_target": 5, "resolve_conflict": 3}`.
Brier (Klassensumme, 0–2): 0.248499; NLL (nats): 0.510919; Gold-p=0: 0; ECE: 0.147110.
Mittlerer Auswahlscore: 0.798375; Score−Genauigkeit: -0.034958; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: 0.687500 (richtig=40, falsch=8).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 5 | 1 | 0.459345 | 0.200000 | 0.259345 | 0.259345 |
| [0.5,0.6) | 1 | 1 | 0.580913 | 1.000000 | -0.419087 | 0.419087 |
| [0.6,0.7) | 4 | 4 | 0.635861 | 1.000000 | -0.364139 | 0.364139 |
| [0.7,0.8) | 4 | 4 | 0.770409 | 1.000000 | -0.229591 | 0.229591 |
| [0.8,0.9) | 27 | 25 | 0.867570 | 0.925926 | -0.058356 | 0.058356 |
| [0.9,1.0] | 7 | 5 | 0.913559 | 0.714286 | 0.199273 | 0.199273 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 43/48 | 4 | 89.58% | 89.58% | 9.30% |
| 0.70 | 38/48 | 4 | 79.17% | 79.17% | 10.53% |
| 0.80 | 34/48 | 4 | 70.83% | 70.83% | 11.76% |
| 0.90 | 7/48 | 2 | 14.58% | 14.58% | 28.57% |
| 0.95 | 0/48 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.99 | 0/48 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: pair_report_delivery_target_b, pair_statement_notification_a, pair_report_delivery_target_a, pair_limit_order_price_step_a
- ≥0.70: pair_report_delivery_target_b, pair_statement_notification_a, pair_report_delivery_target_a, pair_limit_order_price_step_a
- ≥0.80: pair_report_delivery_target_b, pair_statement_notification_a, pair_report_delivery_target_a, pair_limit_order_price_step_a
- ≥0.90: pair_report_delivery_target_b, pair_report_delivery_target_a
- ≥0.95: keine
- ≥0.99: keine

## original_text180 / category=ambiguity_abstain / language=en / schema_language=en / decision


Gruppen-ID: `original_text180__131b2326e192921f`. Optionen (4): conflict, missing, ready, unsupported.
Erwartet 5; gültig 5; ungültig 0; fehlend 0. Richtig 5/5; Genauigkeit 100.00%.
Gold-Klassen: `{"conflict": 1, "missing": 1, "ready": 1, "unsupported": 2}`. Native Auswahl: `{"conflict": 1, "missing": 1, "ready": 1, "unsupported": 2}`.
Brier (Klassensumme, 0–2): 0.116169; NLL (nats): 0.318869; Gold-p=0: 0; ECE: 0.262592.
Mittlerer Auswahlscore: 0.737408; Score−Genauigkeit: -0.262592; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=5, falsch=0).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 1 | 1 | 0.585081 | 1.000000 | -0.414919 | 0.414919 |
| [0.6,0.7) | 1 | 1 | 0.605759 | 1.000000 | -0.394241 | 0.394241 |
| [0.7,0.8) | 1 | 1 | 0.780238 | 1.000000 | -0.219762 | 0.219762 |
| [0.8,0.9) | 1 | 1 | 0.814587 | 1.000000 | -0.185413 | 0.185413 |
| [0.9,1.0] | 1 | 1 | 0.901374 | 1.000000 | -0.098626 | 0.098626 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 5/5 | 0 | 100.00% | 100.00% | 0.00% |
| 0.70 | 3/5 | 0 | 60.00% | 60.00% | 0.00% |
| 0.80 | 2/5 | 0 | 40.00% | 40.00% | 0.00% |
| 0.90 | 1/5 | 0 | 20.00% | 20.00% | 0.00% |
| 0.95 | 0/5 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.99 | 0/5 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: keine
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## original_text180 / category=tool_selection / language=de / schema_language=en / decision


Gruppen-ID: `original_text180__3df6cd9a69506599`. Optionen (5): calculator, calendar_lookup, mail_search, no_tool, web_search.
Erwartet 5; gültig 5; ungültig 0; fehlend 0. Richtig 5/5; Genauigkeit 100.00%.
Gold-Klassen: `{"calculator": 1, "calendar_lookup": 1, "mail_search": 1, "no_tool": 1, "web_search": 1}`. Native Auswahl: `{"calculator": 1, "calendar_lookup": 1, "mail_search": 1, "no_tool": 1, "web_search": 1}`.
Brier (Klassensumme, 0–2): 0.002633; NLL (nats): 0.042232; Gold-p=0: 0; ECE: 0.041157.
Mittlerer Auswahlscore: 0.958843; Score−Genauigkeit: -0.041157; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=5, falsch=0).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.9,1.0] | 5 | 5 | 0.958843 | 1.000000 | -0.041157 | 0.041157 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 5/5 | 0 | 100.00% | 100.00% | 0.00% |
| 0.70 | 5/5 | 0 | 100.00% | 100.00% | 0.00% |
| 0.80 | 5/5 | 0 | 100.00% | 100.00% | 0.00% |
| 0.90 | 5/5 | 0 | 100.00% | 100.00% | 0.00% |
| 0.95 | 4/5 | 0 | 80.00% | 80.00% | 0.00% |
| 0.99 | 0/5 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: keine
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## original_text180 / category=admin_intent / language=en / schema_language=en / decision


Gruppen-ID: `original_text180__40eaeea498d9ce47`. Optionen (5): copy, correction, deadline, other, refund.
Erwartet 5; gültig 5; ungültig 0; fehlend 0. Richtig 5/5; Genauigkeit 100.00%.
Gold-Klassen: `{"copy": 1, "correction": 1, "deadline": 1, "other": 1, "refund": 1}`. Native Auswahl: `{"copy": 1, "correction": 1, "deadline": 1, "other": 1, "refund": 1}`.
Brier (Klassensumme, 0–2): 0.006955; NLL (nats): 0.047210; Gold-p=0: 0; ECE: 0.044226.
Mittlerer Auswahlscore: 0.955774; Score−Genauigkeit: -0.044226; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=5, falsch=0).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 1 | 1 | 0.840251 | 1.000000 | -0.159749 | 0.159749 |
| [0.9,1.0] | 4 | 4 | 0.984655 | 1.000000 | -0.015345 | 0.015345 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 5/5 | 0 | 100.00% | 100.00% | 0.00% |
| 0.70 | 5/5 | 0 | 100.00% | 100.00% | 0.00% |
| 0.80 | 5/5 | 0 | 100.00% | 100.00% | 0.00% |
| 0.90 | 4/5 | 0 | 80.00% | 80.00% | 0.00% |
| 0.95 | 4/5 | 0 | 80.00% | 80.00% | 0.00% |
| 0.99 | 1/5 | 0 | 20.00% | 20.00% | 0.00% |

Fehler-IDs je fester Schwelle:
- ≥0.50: keine
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## original_text180 / category=it_routing / language=de / schema_language=en / decision


Gruppen-ID: `original_text180__476968f73f04803c`. Optionen (5): clarify, collaboration, endpoint, identity, messaging.
Erwartet 5; gültig 5; ungültig 0; fehlend 0. Richtig 5/5; Genauigkeit 100.00%.
Gold-Klassen: `{"clarify": 1, "collaboration": 1, "endpoint": 1, "identity": 1, "messaging": 1}`. Native Auswahl: `{"clarify": 1, "collaboration": 1, "endpoint": 1, "identity": 1, "messaging": 1}`.
Brier (Klassensumme, 0–2): 0.004955; NLL (nats): 0.055348; Gold-p=0: 0; ECE: 0.053272.
Mittlerer Auswahlscore: 0.946728; Score−Genauigkeit: -0.053272; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=5, falsch=0).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 1 | 1 | 0.895273 | 1.000000 | -0.104727 | 0.104727 |
| [0.9,1.0] | 4 | 4 | 0.959592 | 1.000000 | -0.040408 | 0.040408 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 5/5 | 0 | 100.00% | 100.00% | 0.00% |
| 0.70 | 5/5 | 0 | 100.00% | 100.00% | 0.00% |
| 0.80 | 5/5 | 0 | 100.00% | 100.00% | 0.00% |
| 0.90 | 4/5 | 0 | 80.00% | 80.00% | 0.00% |
| 0.95 | 3/5 | 0 | 60.00% | 60.00% | 0.00% |
| 0.99 | 0/5 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: keine
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## original_text180 / category=ambiguity_abstain / language=de / schema_language=de / decision


Gruppen-ID: `original_text180__541ef2fd7bfeec18`. Optionen (4): conflict, missing, ready, unsupported.
Erwartet 20; gültig 20; ungültig 0; fehlend 0. Richtig 18/20; Genauigkeit 90.00%.
Gold-Klassen: `{"conflict": 5, "missing": 5, "ready": 5, "unsupported": 5}`. Native Auswahl: `{"conflict": 4, "missing": 4, "ready": 7, "unsupported": 5}`.
Brier (Klassensumme, 0–2): 0.258058; NLL (nats): 0.533860; Gold-p=0: 0; ECE: 0.202769.
Mittlerer Auswahlscore: 0.763166; Score−Genauigkeit: -0.136834; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: 0.333333 (richtig=18, falsch=2).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 1 | 1 | 0.462873 | 1.000000 | -0.537127 | 0.537127 |
| [0.5,0.6) | 3 | 3 | 0.539154 | 1.000000 | -0.460846 | 0.460846 |
| [0.6,0.7) | 2 | 2 | 0.647754 | 1.000000 | -0.352246 | 0.352246 |
| [0.7,0.8) | 5 | 4 | 0.757406 | 0.800000 | -0.042594 | 0.042594 |
| [0.8,0.9) | 5 | 5 | 0.888220 | 1.000000 | -0.111780 | 0.111780 |
| [0.9,1.0] | 4 | 3 | 0.914839 | 0.750000 | 0.164839 | 0.164839 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 19/20 | 2 | 95.00% | 95.00% | 10.53% |
| 0.70 | 14/20 | 2 | 70.00% | 70.00% | 14.29% |
| 0.80 | 9/20 | 1 | 45.00% | 45.00% | 11.11% |
| 0.90 | 4/20 | 1 | 20.00% | 20.00% | 25.00% |
| 0.95 | 0/20 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.99 | 0/20 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: de_ambiguity_abstain_014, de_ambiguity_abstain_008
- ≥0.70: de_ambiguity_abstain_014, de_ambiguity_abstain_008
- ≥0.80: de_ambiguity_abstain_008
- ≥0.90: de_ambiguity_abstain_008
- ≥0.95: keine
- ≥0.99: keine

## original_text180 / category=it_routing / language=de / schema_language=de / decision


Gruppen-ID: `original_text180__5a81a0c17cfb5b19`. Optionen (5): clarify, collaboration, endpoint, identity, messaging.
Erwartet 20; gültig 20; ungültig 0; fehlend 0. Richtig 19/20; Genauigkeit 95.00%.
Gold-Klassen: `{"clarify": 4, "collaboration": 4, "endpoint": 4, "identity": 4, "messaging": 4}`. Native Auswahl: `{"clarify": 3, "collaboration": 4, "endpoint": 5, "identity": 4, "messaging": 4}`.
Brier (Klassensumme, 0–2): 0.050831; NLL (nats): 0.146678; Gold-p=0: 0; ECE: 0.084641.
Mittlerer Auswahlscore: 0.901077; Score−Genauigkeit: -0.048923; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: 1.000000 (richtig=19, falsch=1).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 1 | 0 | 0.357180 | 0.000000 | 0.357180 | 0.357180 |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 2 | 2 | 0.770614 | 1.000000 | -0.229386 | 0.229386 |
| [0.8,0.9) | 2 | 2 | 0.866465 | 1.000000 | -0.133535 | 0.133535 |
| [0.9,1.0] | 15 | 15 | 0.959347 | 1.000000 | -0.040653 | 0.040653 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 19/20 | 0 | 95.00% | 95.00% | 0.00% |
| 0.70 | 19/20 | 0 | 95.00% | 95.00% | 0.00% |
| 0.80 | 17/20 | 0 | 85.00% | 85.00% | 0.00% |
| 0.90 | 15/20 | 0 | 75.00% | 75.00% | 0.00% |
| 0.95 | 10/20 | 0 | 50.00% | 50.00% | 0.00% |
| 0.99 | 0/20 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: keine
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## original_text180 / category=urgency / language=de / schema_language=en / decision


Gruppen-ID: `original_text180__5e021794e9b9b905`. Optionen (4): critical, high, none, normal.
Erwartet 5; gültig 5; ungültig 0; fehlend 0. Richtig 5/5; Genauigkeit 100.00%.
Gold-Klassen: `{"critical": 1, "high": 1, "none": 2, "normal": 1}`. Native Auswahl: `{"critical": 1, "high": 1, "none": 2, "normal": 1}`.
Brier (Klassensumme, 0–2): 0.056620; NLL (nats): 0.170188; Gold-p=0: 0; ECE: 0.145525.
Mittlerer Auswahlscore: 0.854475; Score−Genauigkeit: -0.145525; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=5, falsch=0).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 1 | 1 | 0.609010 | 1.000000 | -0.390990 | 0.390990 |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 1 | 1 | 0.854933 | 1.000000 | -0.145067 | 0.145067 |
| [0.9,1.0] | 3 | 3 | 0.936143 | 1.000000 | -0.063857 | 0.063857 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 5/5 | 0 | 100.00% | 100.00% | 0.00% |
| 0.70 | 4/5 | 0 | 80.00% | 80.00% | 0.00% |
| 0.80 | 4/5 | 0 | 80.00% | 80.00% | 0.00% |
| 0.90 | 3/5 | 0 | 60.00% | 60.00% | 0.00% |
| 0.95 | 1/5 | 0 | 20.00% | 20.00% | 0.00% |
| 0.99 | 0/5 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: keine
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## original_text180 / category=admin_intent / language=de / schema_language=en / decision


Gruppen-ID: `original_text180__6f5fc77a010db691`. Optionen (5): copy, correction, deadline, other, refund.
Erwartet 5; gültig 5; ungültig 0; fehlend 0. Richtig 5/5; Genauigkeit 100.00%.
Gold-Klassen: `{"copy": 1, "correction": 1, "deadline": 1, "other": 1, "refund": 1}`. Native Auswahl: `{"copy": 1, "correction": 1, "deadline": 1, "other": 1, "refund": 1}`.
Brier (Klassensumme, 0–2): 0.028662; NLL (nats): 0.097793; Gold-p=0: 0; ECE: 0.084053.
Mittlerer Auswahlscore: 0.915947; Score−Genauigkeit: -0.084053; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=5, falsch=0).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 1 | 1 | 0.678298 | 1.000000 | -0.321702 | 0.321702 |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.9,1.0] | 4 | 4 | 0.975359 | 1.000000 | -0.024641 | 0.024641 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 5/5 | 0 | 100.00% | 100.00% | 0.00% |
| 0.70 | 4/5 | 0 | 80.00% | 80.00% | 0.00% |
| 0.80 | 4/5 | 0 | 80.00% | 80.00% | 0.00% |
| 0.90 | 4/5 | 0 | 80.00% | 80.00% | 0.00% |
| 0.95 | 3/5 | 0 | 60.00% | 60.00% | 0.00% |
| 0.99 | 1/5 | 0 | 20.00% | 20.00% | 0.00% |

Fehler-IDs je fester Schwelle:
- ≥0.50: keine
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## original_text180 / category=tool_selection / language=de / schema_language=de / decision


Gruppen-ID: `original_text180__9a886b4aae51fc69`. Optionen (5): calculator, calendar_lookup, mail_search, no_tool, web_search.
Erwartet 20; gültig 20; ungültig 0; fehlend 0. Richtig 20/20; Genauigkeit 100.00%.
Gold-Klassen: `{"calculator": 4, "calendar_lookup": 4, "mail_search": 4, "no_tool": 4, "web_search": 4}`. Native Auswahl: `{"calculator": 4, "calendar_lookup": 4, "mail_search": 4, "no_tool": 4, "web_search": 4}`.
Brier (Klassensumme, 0–2): 0.013649; NLL (nats): 0.076454; Gold-p=0: 0; ECE: 0.070102.
Mittlerer Auswahlscore: 0.929898; Score−Genauigkeit: -0.070102; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=20, falsch=0).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 1 | 1 | 0.679992 | 1.000000 | -0.320008 | 0.320008 |
| [0.7,0.8) | 1 | 1 | 0.777748 | 1.000000 | -0.222252 | 0.222252 |
| [0.8,0.9) | 1 | 1 | 0.838365 | 1.000000 | -0.161635 | 0.161635 |
| [0.9,1.0] | 17 | 17 | 0.958933 | 1.000000 | -0.041067 | 0.041067 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 20/20 | 0 | 100.00% | 100.00% | 0.00% |
| 0.70 | 19/20 | 0 | 95.00% | 95.00% | 0.00% |
| 0.80 | 18/20 | 0 | 90.00% | 90.00% | 0.00% |
| 0.90 | 17/20 | 0 | 85.00% | 85.00% | 0.00% |
| 0.95 | 15/20 | 0 | 75.00% | 75.00% | 0.00% |
| 0.99 | 0/20 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: keine
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## original_text180 / category=tool_selection / language=en / schema_language=en / decision


Gruppen-ID: `original_text180__9dbee747a0b33333`. Optionen (5): calculator, calendar_lookup, mail_search, no_tool, web_search.
Erwartet 5; gültig 5; ungültig 0; fehlend 0. Richtig 5/5; Genauigkeit 100.00%.
Gold-Klassen: `{"calculator": 1, "calendar_lookup": 1, "mail_search": 1, "no_tool": 1, "web_search": 1}`. Native Auswahl: `{"calculator": 1, "calendar_lookup": 1, "mail_search": 1, "no_tool": 1, "web_search": 1}`.
Brier (Klassensumme, 0–2): 0.001507; NLL (nats): 0.034102; Gold-p=0: 0; ECE: 0.033496.
Mittlerer Auswahlscore: 0.966504; Score−Genauigkeit: -0.033496; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=5, falsch=0).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.9,1.0] | 5 | 5 | 0.966504 | 1.000000 | -0.033496 | 0.033496 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 5/5 | 0 | 100.00% | 100.00% | 0.00% |
| 0.70 | 5/5 | 0 | 100.00% | 100.00% | 0.00% |
| 0.80 | 5/5 | 0 | 100.00% | 100.00% | 0.00% |
| 0.90 | 5/5 | 0 | 100.00% | 100.00% | 0.00% |
| 0.95 | 5/5 | 0 | 100.00% | 100.00% | 0.00% |
| 0.99 | 0/5 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: keine
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## original_text180 / category=it_routing / language=en / schema_language=en / decision


Gruppen-ID: `original_text180__9fc38e136ef4c90e`. Optionen (5): clarify, collaboration, endpoint, identity, messaging.
Erwartet 5; gültig 5; ungültig 0; fehlend 0. Richtig 5/5; Genauigkeit 100.00%.
Gold-Klassen: `{"clarify": 1, "collaboration": 1, "endpoint": 1, "identity": 1, "messaging": 1}`. Native Auswahl: `{"clarify": 1, "collaboration": 1, "endpoint": 1, "identity": 1, "messaging": 1}`.
Brier (Klassensumme, 0–2): 0.007212; NLL (nats): 0.060727; Gold-p=0: 0; ECE: 0.057651.
Mittlerer Auswahlscore: 0.942349; Score−Genauigkeit: -0.057651; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=5, falsch=0).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 1 | 1 | 0.851578 | 1.000000 | -0.148422 | 0.148422 |
| [0.9,1.0] | 4 | 4 | 0.965041 | 1.000000 | -0.034959 | 0.034959 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 5/5 | 0 | 100.00% | 100.00% | 0.00% |
| 0.70 | 5/5 | 0 | 100.00% | 100.00% | 0.00% |
| 0.80 | 5/5 | 0 | 100.00% | 100.00% | 0.00% |
| 0.90 | 4/5 | 0 | 80.00% | 80.00% | 0.00% |
| 0.95 | 3/5 | 0 | 60.00% | 60.00% | 0.00% |
| 0.99 | 0/5 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: keine
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## original_text180 / category=urgency / language=de / schema_language=de / decision


Gruppen-ID: `original_text180__b183b02256cf1fb2`. Optionen (4): critical, high, none, normal.
Erwartet 20; gültig 20; ungültig 0; fehlend 0. Richtig 20/20; Genauigkeit 100.00%.
Gold-Klassen: `{"critical": 5, "high": 5, "none": 5, "normal": 5}`. Native Auswahl: `{"critical": 5, "high": 5, "none": 5, "normal": 5}`.
Brier (Klassensumme, 0–2): 0.056652; NLL (nats): 0.185419; Gold-p=0: 0; ECE: 0.160715.
Mittlerer Auswahlscore: 0.839285; Score−Genauigkeit: -0.160715; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=20, falsch=0).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 1 | 1 | 0.528771 | 1.000000 | -0.471229 | 0.471229 |
| [0.6,0.7) | 2 | 2 | 0.663035 | 1.000000 | -0.336965 | 0.336965 |
| [0.7,0.8) | 2 | 2 | 0.769614 | 1.000000 | -0.230386 | 0.230386 |
| [0.8,0.9) | 6 | 6 | 0.843673 | 1.000000 | -0.156327 | 0.156327 |
| [0.9,1.0] | 9 | 9 | 0.925510 | 1.000000 | -0.074490 | 0.074490 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 20/20 | 0 | 100.00% | 100.00% | 0.00% |
| 0.70 | 17/20 | 0 | 85.00% | 85.00% | 0.00% |
| 0.80 | 15/20 | 0 | 75.00% | 75.00% | 0.00% |
| 0.90 | 9/20 | 0 | 45.00% | 45.00% | 0.00% |
| 0.95 | 1/20 | 0 | 5.00% | 5.00% | 0.00% |
| 0.99 | 0/20 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: keine
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## original_text180 / category=document_classification / language=en / schema_language=en / decision


Gruppen-ID: `original_text180__b2afa84ed1495848`. Optionen (5): credit_note, invoice, offer, other, reminder.
Erwartet 5; gültig 5; ungültig 0; fehlend 0. Richtig 5/5; Genauigkeit 100.00%.
Gold-Klassen: `{"credit_note": 1, "invoice": 1, "offer": 1, "other": 1, "reminder": 1}`. Native Auswahl: `{"credit_note": 1, "invoice": 1, "offer": 1, "other": 1, "reminder": 1}`.
Brier (Klassensumme, 0–2): 0.054052; NLL (nats): 0.158272; Gold-p=0: 0; ECE: 0.132901.
Mittlerer Auswahlscore: 0.867099; Score−Genauigkeit: -0.132901; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=5, falsch=0).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 1 | 1 | 0.603385 | 1.000000 | -0.396615 | 0.396615 |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 1 | 1 | 0.829421 | 1.000000 | -0.170579 | 0.170579 |
| [0.9,1.0] | 3 | 3 | 0.967564 | 1.000000 | -0.032436 | 0.032436 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 5/5 | 0 | 100.00% | 100.00% | 0.00% |
| 0.70 | 4/5 | 0 | 80.00% | 80.00% | 0.00% |
| 0.80 | 4/5 | 0 | 80.00% | 80.00% | 0.00% |
| 0.90 | 3/5 | 0 | 60.00% | 60.00% | 0.00% |
| 0.95 | 3/5 | 0 | 60.00% | 60.00% | 0.00% |
| 0.99 | 0/5 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: keine
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## original_text180 / category=document_classification / language=de / schema_language=en / decision


Gruppen-ID: `original_text180__b43727f66fe7540d`. Optionen (5): credit_note, invoice, offer, other, reminder.
Erwartet 5; gültig 5; ungültig 0; fehlend 0. Richtig 4/5; Genauigkeit 80.00%.
Gold-Klassen: `{"credit_note": 1, "invoice": 1, "offer": 1, "other": 1, "reminder": 1}`. Native Auswahl: `{"credit_note": 1, "invoice": 1, "offer": 1, "reminder": 2}`.
Brier (Klassensumme, 0–2): 0.202776; NLL (nats): 0.346430; Gold-p=0: 0; ECE: 0.163964.
Mittlerer Auswahlscore: 0.881573; Score−Genauigkeit: 0.081573; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: 1.000000 (richtig=4, falsch=1).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 1 | 0 | 0.613841 | 0.000000 | 0.613841 | 0.613841 |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.9,1.0] | 4 | 4 | 0.948506 | 1.000000 | -0.051494 | 0.051494 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 5/5 | 1 | 100.00% | 100.00% | 20.00% |
| 0.70 | 4/5 | 0 | 80.00% | 80.00% | 0.00% |
| 0.80 | 4/5 | 0 | 80.00% | 80.00% | 0.00% |
| 0.90 | 4/5 | 0 | 80.00% | 80.00% | 0.00% |
| 0.95 | 1/5 | 0 | 20.00% | 20.00% | 0.00% |
| 0.99 | 0/5 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: de_en_schema_document_classification_020
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## original_text180 / category=ambiguity_abstain / language=de / schema_language=en / decision


Gruppen-ID: `original_text180__bb3930e6149d1f65`. Optionen (4): conflict, missing, ready, unsupported.
Erwartet 5; gültig 5; ungültig 0; fehlend 0. Richtig 5/5; Genauigkeit 100.00%.
Gold-Klassen: `{"conflict": 1, "missing": 1, "ready": 1, "unsupported": 2}`. Native Auswahl: `{"conflict": 1, "missing": 1, "ready": 1, "unsupported": 2}`.
Brier (Klassensumme, 0–2): 0.115519; NLL (nats): 0.311202; Gold-p=0: 0; ECE: 0.258272.
Mittlerer Auswahlscore: 0.741728; Score−Genauigkeit: -0.258272; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=5, falsch=0).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 2 | 2 | 0.626727 | 1.000000 | -0.373273 | 0.373273 |
| [0.7,0.8) | 1 | 1 | 0.705012 | 1.000000 | -0.294988 | 0.294988 |
| [0.8,0.9) | 1 | 1 | 0.816403 | 1.000000 | -0.183597 | 0.183597 |
| [0.9,1.0] | 1 | 1 | 0.933768 | 1.000000 | -0.066232 | 0.066232 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 5/5 | 0 | 100.00% | 100.00% | 0.00% |
| 0.70 | 3/5 | 0 | 60.00% | 60.00% | 0.00% |
| 0.80 | 2/5 | 0 | 40.00% | 40.00% | 0.00% |
| 0.90 | 1/5 | 0 | 20.00% | 20.00% | 0.00% |
| 0.95 | 0/5 | 0 | 0.00% | 0.00% | nicht definiert |
| 0.99 | 0/5 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: keine
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## original_text180 / category=document_classification / language=de / schema_language=de / decision


Gruppen-ID: `original_text180__e216650561471f94`. Optionen (5): credit_note, invoice, offer, other, reminder.
Erwartet 20; gültig 20; ungültig 0; fehlend 0. Richtig 19/20; Genauigkeit 95.00%.
Gold-Klassen: `{"credit_note": 4, "invoice": 4, "offer": 4, "other": 4, "reminder": 4}`. Native Auswahl: `{"credit_note": 5, "invoice": 4, "offer": 4, "other": 3, "reminder": 4}`.
Brier (Klassensumme, 0–2): 0.104333; NLL (nats): 0.205607; Gold-p=0: 0; ECE: 0.115178.
Mittlerer Auswahlscore: 0.887397; Score−Genauigkeit: -0.062603; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: 0.842105 (richtig=19, falsch=1).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 1 | 1 | 0.460958 | 1.000000 | -0.539042 | 0.539042 |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 1 | 1 | 0.627290 | 1.000000 | -0.372710 | 0.372710 |
| [0.7,0.8) | 2 | 1 | 0.762874 | 0.500000 | 0.262874 | 0.262874 |
| [0.8,0.9) | 2 | 2 | 0.840206 | 1.000000 | -0.159794 | 0.159794 |
| [0.9,1.0] | 14 | 14 | 0.960966 | 1.000000 | -0.039034 | 0.039034 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 19/20 | 1 | 95.00% | 95.00% | 5.26% |
| 0.70 | 18/20 | 1 | 90.00% | 90.00% | 5.56% |
| 0.80 | 16/20 | 0 | 80.00% | 80.00% | 0.00% |
| 0.90 | 14/20 | 0 | 70.00% | 70.00% | 0.00% |
| 0.95 | 12/20 | 0 | 60.00% | 60.00% | 0.00% |
| 0.99 | 0/20 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: de_document_classification_017
- ≥0.70: de_document_classification_017
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## original_text180 / category=admin_intent / language=de / schema_language=de / decision


Gruppen-ID: `original_text180__f4d2f8d00846dced`. Optionen (5): copy, correction, deadline, other, refund.
Erwartet 20; gültig 20; ungültig 0; fehlend 0. Richtig 20/20; Genauigkeit 100.00%.
Gold-Klassen: `{"copy": 4, "correction": 4, "deadline": 4, "other": 4, "refund": 4}`. Native Auswahl: `{"copy": 4, "correction": 4, "deadline": 4, "other": 4, "refund": 4}`.
Brier (Klassensumme, 0–2): 0.011405; NLL (nats): 0.067772; Gold-p=0: 0; ECE: 0.062431.
Mittlerer Auswahlscore: 0.937569; Score−Genauigkeit: -0.062431; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: nicht definiert (richtig=20, falsch=0).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 1 | 1 | 0.672949 | 1.000000 | -0.327051 | 0.327051 |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 1 | 1 | 0.828033 | 1.000000 | -0.171967 | 0.171967 |
| [0.9,1.0] | 18 | 18 | 0.958355 | 1.000000 | -0.041645 | 0.041645 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 20/20 | 0 | 100.00% | 100.00% | 0.00% |
| 0.70 | 19/20 | 0 | 95.00% | 95.00% | 0.00% |
| 0.80 | 19/20 | 0 | 95.00% | 95.00% | 0.00% |
| 0.90 | 18/20 | 0 | 90.00% | 90.00% | 0.00% |
| 0.95 | 12/20 | 0 | 60.00% | 60.00% | 0.00% |
| 0.99 | 0/20 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: keine
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

## original_text180 / category=urgency / language=en / schema_language=en / decision


Gruppen-ID: `original_text180__ffddd0b1ddc918d5`. Optionen (4): critical, high, none, normal.
Erwartet 5; gültig 5; ungültig 0; fehlend 0. Richtig 4/5; Genauigkeit 80.00%.
Gold-Klassen: `{"critical": 1, "high": 1, "none": 2, "normal": 1}`. Native Auswahl: `{"critical": 1, "high": 1, "none": 3}`.
Brier (Klassensumme, 0–2): 0.177310; NLL (nats): 0.277589; Gold-p=0: 0; ECE: 0.161288.
Mittlerer Auswahlscore: 0.886679; Score−Genauigkeit: 0.086679; exakte Maximalwert-Bindungen: 0; Fehler-AUROC: 1.000000 (richtig=4, falsch=1).

| Bin | n | richtig | mittlerer Score | Genauigkeit | Score−Genauigkeit | Absolute Lücke |
| --- | --- | --- | --- | --- | --- | --- |
| [0.0,0.1) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.1,0.2) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.2,0.3) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.3,0.4) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.4,0.5) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.5,0.6) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.6,0.7) | 1 | 0 | 0.619919 | 0.000000 | 0.619919 | 0.619919 |
| [0.7,0.8) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.8,0.9) | 0 | 0 | nicht definiert | nicht definiert | nicht definiert | nicht definiert |
| [0.9,1.0] | 4 | 4 | 0.953369 | 1.000000 | -0.046631 | 0.046631 |

| Score ≥ | ausgewählt/erwartet | falsch | Abdeckung | Abdeckung gültig | Fehlerrate |
| --- | --- | --- | --- | --- | --- |
| 0.50 | 5/5 | 1 | 100.00% | 100.00% | 20.00% |
| 0.70 | 4/5 | 0 | 80.00% | 80.00% | 0.00% |
| 0.80 | 4/5 | 0 | 80.00% | 80.00% | 0.00% |
| 0.90 | 4/5 | 0 | 80.00% | 80.00% | 0.00% |
| 0.95 | 4/5 | 0 | 80.00% | 80.00% | 0.00% |
| 0.99 | 0/5 | 0 | 0.00% | 0.00% | nicht definiert |

Fehler-IDs je fester Schwelle:
- ≥0.50: en_urgency_014
- ≥0.70: keine
- ≥0.80: keine
- ≥0.90: keine
- ≥0.95: keine
- ≥0.99: keine

