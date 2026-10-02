# Sämtliche Abweichungen vom eingefrorenen Gold

12/80 Fälle haben mindestens ein falsches Feld. Alle Rohwahrscheinlichkeiten bleiben in results/predictions.jsonl und results/errors.jsonl erhalten.

Die unten stehende Begründung erläutert die Referenz nach der fiktiven Policy; sie erklärt nicht den internen Grund der Modellentscheidung. Gold oder Prompts wurden nach dem Lauf nicht angepasst.

## bank_transfers_03

Die von mir freigegebene Überweisung vom Montag steht als ausgeführt da, beim Empfänger fehlt sie noch. Bitte prüfen Sie diesen Auftrag.

| Feld | Gold | Clef | Wahrscheinlichkeit der Clef-Wahl |
|---|---|---|---:|
| intent | transfers | transfers | 0.804685 |
| priority | routine | urgent | 0.873464 |
| next_step | specialist_review | specialist_review | 0.913950 |

Falsche Felder: priority.

Referenzbegründung: Bestimmter Überweisungsstatus zur Prüfung, keine genannte heutige/morgige Fälligkeit.

## bank_security_06

Grad kommt eine TAN-Freigabe aufs Handy, obwohl ich gar nichts beauftragt habe. Soll ich die bestätigen?

| Feld | Gold | Clef | Wahrscheinlichkeit der Clef-Wahl |
|---|---|---|---:|
| intent | security | access_tan | 0.529769 |
| priority | critical | critical | 0.891970 |
| next_step | security_handoff | security_handoff | 0.949577 |

Falsche Felder: intent.

Referenzbegründung: Unerwartete TAN-Anforderung; nicht freigeben.

## bank_ambiguous_multi_07

Es geht um meinen Dauerauftrag und eine Kontogebühr. Beide sollen Sie prüfen, ohne dass einer wichtiger ist. Der Dauerauftrag für die morgen fällige Miete wird als abgelehnt angezeigt.

| Feld | Gold | Clef | Wahrscheinlichkeit der Clef-Wahl |
|---|---|---|---:|
| intent | unclear | unclear | 0.579097 |
| priority | urgent | urgent | 0.953559 |
| next_step | clarify | specialist_review | 0.727086 |

Falsche Felder: next_step.

Referenzbegründung: Zwei gleichrangige Routen ohne Sicherheitsvorrang; globale Priorität urgent wegen blockierter Miete morgen.

Erforderliche Rückfrage laut Testautor: Welches Anliegen sollen wir zuerst bearbeiten: den abgelehnten Dauerauftrag oder die Kontogebühr?

## bank_transfers_05

Die heute fällige Miete kann ich nicht überweisen: Nach meiner Freigabe kommt jedes Mal „Auftrag fehlgeschlagen“. Bitte prüfen Sie den Fehler.

| Feld | Gold | Clef | Wahrscheinlichkeit der Clef-Wahl |
|---|---|---|---:|
| intent | transfers | standing_orders | 0.278579 |
| priority | urgent | urgent | 0.962102 |
| next_step | specialist_review | specialist_review | 0.809154 |

Falsche Felder: intent.

Referenzbegründung: Freigegebener Zahlungsvorgang scheitert, notwendige Zahlung heute.

## bank_ambiguous_multi_02

Ich hätte gern eine Anleitung zur neuen Karte und außerdem zum Download der Kontoauszüge. Beides ist mir gleich wichtig. Womit fangen wir an?

| Feld | Gold | Clef | Wahrscheinlichkeit der Clef-Wahl |
|---|---|---|---:|
| intent | unclear | unclear | 0.697796 |
| priority | routine | routine | 0.990805 |
| next_step | clarify | guidance | 0.937516 |

Falsche Felder: next_step.

Referenzbegründung: Zwei gleichrangige unterschiedliche offene Routen.

Erforderliche Rückfrage laut Testautor: Möchten Sie zuerst die Kartenanleitung oder den Kontoauszug-Download besprechen?

## bank_direct_debits_02

Mein bekannter Stromanbieter hat seine Lastschrift diesen Monat zweimal eingezogen. Das Mandat stammt von mir. Bitte prüfen Sie die Doppelbelastung.

| Feld | Gold | Clef | Wahrscheinlichkeit der Clef-Wahl |
|---|---|---|---:|
| intent | direct_debits | direct_debits | 0.926512 |
| priority | routine | urgent | 0.566644 |
| next_step | specialist_review | specialist_review | 0.861344 |

Falsche Felder: priority.

Referenzbegründung: Autorisierter bekannter Einzug mit konkreter Betragsreklamation.

## bank_fees_05

Da ist irgendwo so eine Bankgebühr. Ich weiß gerade weder, wie sie heißt, noch auf welchem Auszug sie steht. Können Sie genau diese Gebühr prüfen?

| Feld | Gold | Clef | Wahrscheinlichkeit der Clef-Wahl |
|---|---|---|---:|
| intent | fees | fees | 0.956887 |
| priority | routine | routine | 0.984842 |
| next_step | clarify | specialist_review | 0.609691 |

Falsche Felder: next_step.

Referenzbegründung: Konkrete Prüfbitte ohne zuordenbare Gebührenposition.

Erforderliche Rückfrage laut Testautor: Wie heißt die Gebührenposition und auf welchem Auszug steht sie?

## bank_cards_05

Kann man das kontaktlose Bezahlen grundsätzlich ausschalten? Meine Karte funktioniert, ich möchte nur die Einstellung finden.

| Feld | Gold | Clef | Wahrscheinlichkeit der Clef-Wahl |
|---|---|---|---:|
| intent | cards | unclear | 0.389160 |
| priority | routine | routine | 0.991522 |
| next_step | guidance | guidance | 0.960572 |

Falsche Felder: intent.

Referenzbegründung: Allgemeine Einstellungssuche, kein Fehler.

## bank_transfers_06

hab glaub ich zweimal überwiesen. bin aber nicht sicher ob überhaupt eine raus ist. könnt ihr die doppelte zurückholen?

| Feld | Gold | Clef | Wahrscheinlichkeit der Clef-Wahl |
|---|---|---|---:|
| intent | transfers | transfers | 0.539515 |
| priority | routine | urgent | 0.931404 |
| next_step | clarify | clarify | 0.432181 |

Falsche Felder: priority.

Referenzbegründung: Absendung und Doppelung unbestätigt; keine sichere urgent-Bedingung.

Erforderliche Rückfrage laut Testautor: Zeigt die Auftragsübersicht keine, eine oder zwei ausgeführte Überweisungen?

## bank_access_tan_02

Nach drei vertippten Login-Versuchen steht „Zugang gesperrt“. Ich war das selbst. Bitte prüfen Sie, wie mein Zugang wiederhergestellt werden kann.

| Feld | Gold | Clef | Wahrscheinlichkeit der Clef-Wahl |
|---|---|---|---:|
| intent | access_tan | access_tan | 0.774017 |
| priority | routine | routine | 0.723013 |
| next_step | specialist_review | security_handoff | 0.587334 |

Falsche Felder: next_step.

Referenzbegründung: Konkrete technische Zugangssperre, kein Sicherheitsvorfall.

## bank_direct_debits_03

Auf dem Konto ist eine Lastschrift einer Firma, die ich überhaupt nicht kenne. Ich habe dafür nie ein Mandat erteilt. Noch ist nichts gesperrt oder geklärt.

| Feld | Gold | Clef | Wahrscheinlichkeit der Clef-Wahl |
|---|---|---|---:|
| intent | security | direct_debits | 0.554234 |
| priority | critical | critical | 0.555692 |
| next_step | security_handoff | security_handoff | 0.875522 |

Falsche Felder: intent.

Referenzbegründung: Ausdrücklich bestrittene Autorisierung hat Sicherheitsvorrang.

## bank_transfers_04

Vor dem Absenden meldet die Empfängerprüfung, dass Name und IBAN nicht zusammenpassen. Ich habe nicht freigegeben. Wie gehe ich mit dieser Meldung um?

| Feld | Gold | Clef | Wahrscheinlichkeit der Clef-Wahl |
|---|---|---|---:|
| intent | transfers | transfers | 0.894572 |
| priority | routine | routine | 0.800935 |
| next_step | guidance | specialist_review | 0.502319 |

Falsche Felder: next_step.

Referenzbegründung: Allgemeine Erläuterung einer Prüfung vor Freigabe; kein Geld als verloren behauptet.

