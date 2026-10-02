# All case errors

9 incorrect complete two-field cases. No filtering or selective omission. Full native probabilities remain in results/predictions.jsonl and results/errors.jsonl.

## pair_tow_distance_records_b
Pair: pair_tow_distance_records (b)

Rule: Die fiktive Abschlepppauschale gilt genau dann, wenn die Panne gedeckt ist UND die Abschleppstrecke höchstens 20 Kilometer beträgt. Gleichrangige ungeklärte Streckenangaben haben keinen Vorrang.

Scenario: Die Panne ist gedeckt. Zwei gleichrangige aktuelle Belege nennen für dieselbe Abschleppstrecke 25 Kilometer und 25 Kilometer. Keiner ist als Korrektur markiert.

Question: Gilt die Abschlepppauschale nach dieser Regel?

Expected: answer / no
Predicted: ask_target / unresolved
Rationale: Beide Belege nennen 25 Kilometer; die 20-Kilometer-Grenze ist überschritten.
Technical issues: []

Unrounded native option scores:

{
  "action": {
    "answer": 0.19618135690689087,
    "ask_fact": 0.10770867764949799,
    "ask_target": 0.44469955563545227,
    "resolve_conflict": 0.2514103353023529
  },
  "determination": {
    "no": 0.3681071698665619,
    "unresolved": 0.6140601634979248,
    "yes": 0.017832638695836067
  }
}

## pair_report_delivery_target_b
Pair: pair_report_delivery_target (b)

Rule: Ein fiktiver Depotbericht ist genau dann elektronisch zustellbar, wenn er fertiggestellt ist UND für sein Depot der elektronische Versand aktiviert ist. Der interne Berichtstitel ist irrelevant.

Scenario: Bericht A ist fertiggestellt und sein Depot hat elektronischen Versand aktiviert. Bericht B ist fertiggestellt, aber der elektronische Versand seines Depots ist deaktiviert. Welchen der beiden Berichte ich meine, ist nicht festgelegt. Der interne Titel von A lautet „Bestandsübersicht“.

Question: Ist der angefragte Bericht nach der Regel elektronisch zustellbar?

Expected: ask_target / unresolved
Predicted: answer / yes
Rationale: Die Titeländerung legt das Ziel nicht fest; weiter erfragen.
Technical issues: []

Unrounded native option scores:

{
  "action": {
    "answer": 0.9236037731170654,
    "ask_fact": 0.025493904948234558,
    "ask_target": 0.040107544511556625,
    "resolve_conflict": 0.010794798843562603
  },
  "determination": {
    "no": 0.035739149898290634,
    "unresolved": 0.018833206966519356,
    "yes": 0.9454275965690613
  }
}

## pair_rental_days_conflict_b
Pair: pair_rental_days_conflict (b)

Rule: Ein fiktiver Mietersatzbaustein gilt genau dann, wenn die Mietdauer höchstens 5 Tage beträgt UND eine Rechnung vorliegt. Gleichrangige ungeklärte Angaben zur Dauer haben keinen Vorrang; die Lackfarbe ist irrelevant.

Scenario: Die Rechnung liegt vor. Zwei gleichrangige ungeklärte Belege nennen für denselben Mietvorgang 3 beziehungsweise 8 Tage. Das Mietfahrzeug ist grün lackiert.

Question: Gilt der Mietersatzbaustein nach dieser Regel?

Expected: resolve_conflict / unresolved
Predicted: ask_target / unresolved
Rationale: Der materielle Dauerkonflikt bleibt trotz geänderter Lackfarbe bestehen.
Technical issues: []

Unrounded native option scores:

{
  "action": {
    "answer": 0.08581468462944031,
    "ask_fact": 0.11105246096849442,
    "ask_target": 0.49770259857177734,
    "resolve_conflict": 0.30543026328086853
  },
  "determination": {
    "no": 0.07408957183361053,
    "unresolved": 0.8990769386291504,
    "yes": 0.026833467185497284
  }
}

## pair_statement_notification_a
Pair: pair_statement_notification (a)

Rule: Die fiktive Auszugsbenachrichtigung ist genau dann einschaltbar, wenn eine bestätigte E-Mail-Adresse hinterlegt ist UND die Zustimmung zu dieser Benachrichtigung vorliegt.

Scenario: Eine bestätigte E-Mail-Adresse ist hinterlegt. Der Zustimmungsstatus lautet: nicht angegeben.

Question: Ist die Benachrichtigung nach dieser Regel einschaltbar?

Expected: ask_fact / unresolved
Predicted: answer / no
Rationale: Die notwendige Zustimmung ist unbekannt.
Technical issues: []

Unrounded native option scores:

{
  "action": {
    "answer": 0.8001735210418701,
    "ask_fact": 0.14318329095840454,
    "ask_target": 0.04070345312356949,
    "resolve_conflict": 0.015939701348543167
  },
  "determination": {
    "no": 0.9270290732383728,
    "unresolved": 0.062167759984731674,
    "yes": 0.01080313604325056
  }
}

## pair_report_delivery_target_a
Pair: pair_report_delivery_target (a)

Rule: Ein fiktiver Depotbericht ist genau dann elektronisch zustellbar, wenn er fertiggestellt ist UND für sein Depot der elektronische Versand aktiviert ist. Der interne Berichtstitel ist irrelevant.

Scenario: Bericht A ist fertiggestellt und sein Depot hat elektronischen Versand aktiviert. Bericht B ist fertiggestellt, aber der elektronische Versand seines Depots ist deaktiviert. Welchen der beiden Berichte ich meine, ist nicht festgelegt. Der interne Titel von A lautet „Übersicht“.

Question: Ist der angefragte Bericht nach der Regel elektronisch zustellbar?

Expected: ask_target / unresolved
Predicted: answer / yes
Rationale: A ergibt Ja, B Nein; das Ziel fehlt.
Technical issues: []

Unrounded native option scores:

{
  "action": {
    "answer": 0.9157239198684692,
    "ask_fact": 0.027706528082489967,
    "ask_target": 0.04427490755915642,
    "resolve_conflict": 0.01229469757527113
  },
  "determination": {
    "no": 0.03815561532974243,
    "unresolved": 0.01918584667146206,
    "yes": 0.942658543586731
  }
}

## pair_rental_days_conflict_a
Pair: pair_rental_days_conflict (a)

Rule: Ein fiktiver Mietersatzbaustein gilt genau dann, wenn die Mietdauer höchstens 5 Tage beträgt UND eine Rechnung vorliegt. Gleichrangige ungeklärte Angaben zur Dauer haben keinen Vorrang; die Lackfarbe ist irrelevant.

Scenario: Die Rechnung liegt vor. Zwei gleichrangige ungeklärte Belege nennen für denselben Mietvorgang 3 beziehungsweise 8 Tage. Das Mietfahrzeug ist blau lackiert.

Question: Gilt der Mietersatzbaustein nach dieser Regel?

Expected: resolve_conflict / unresolved
Predicted: ask_target / unresolved
Rationale: 3 versus 8 Tage ändern die Entscheidung; den Konflikt klären.
Technical issues: []

Unrounded native option scores:

{
  "action": {
    "answer": 0.09383875131607056,
    "ask_fact": 0.11955367028713226,
    "ask_target": 0.4565093219280243,
    "resolve_conflict": 0.3300982713699341
  },
  "determination": {
    "no": 0.07904328405857086,
    "unresolved": 0.8940635919570923,
    "yes": 0.026893123984336853
  }
}

## pair_limit_order_price_step_a
Pair: pair_limit_order_price_step (a)

Rule: Ein fiktiver Limitauftrag wird genau dann in das Standardbuch aufgenommen, wenn sein Limit ein Vielfaches von 0,10 Euro ist UND das Handelsfenster offen ist.

Scenario: Das Limit beträgt 12,34 Euro. Zum Handelsfenster ist angegeben: Status unbekannt.

Question: Wird der Auftrag nach dieser Regel ins Standardbuch aufgenommen?

Expected: answer / no
Predicted: ask_fact / unresolved
Rationale: 12,34 ist kein Vielfaches von 0,10; das unbekannte Fenster ist unerheblich.
Technical issues: []

Unrounded native option scores:

{
  "action": {
    "answer": 0.053389716893434525,
    "ask_fact": 0.8063048720359802,
    "ask_target": 0.11661386489868164,
    "resolve_conflict": 0.02369154430925846
  },
  "determination": {
    "no": 0.045494381338357925,
    "unresolved": 0.9464754462242126,
    "yes": 0.008030234836041927
  }
}

## pair_gadget_theft_notice_a
Pair: pair_gadget_theft_notice (a)

Rule: Ein fiktiver Diebstahlbaustein leistet genau dann, wenn ein Kaufbeleg vorliegt UND die Meldung spätestens 48 Stunden nach dem Diebstahl eingeht. Die verstrichene Stundenzahl ist bereits vollständig berechnet.

Scenario: Der Kaufbeleg liegt vor. Die Meldung ging nach genau 48 Stunden ein.

Question: Sind die Bedingungen dieses Diebstahlbausteins erfüllt?

Expected: answer / yes
Predicted: answer / unresolved
Rationale: Die eingeschlossene 48-Stunden-Grenze wird eingehalten.
Technical issues: []

Unrounded native option scores:

{
  "action": {
    "answer": 0.48705869913101196,
    "ask_fact": 0.2014562338590622,
    "ask_target": 0.2373734563589096,
    "resolve_conflict": 0.07411161065101624
  },
  "determination": {
    "no": 0.252095490694046,
    "unresolved": 0.5484805107116699,
    "yes": 0.19942395389080048
  }
}

## pair_redemption_window_conflict_a
Pair: pair_redemption_window_conflict (a)

Rule: Eine fiktive Anteilrückgabe ist genau dann im aktuellen Fenster möglich, wenn das Rückgabefenster offen ist UND die Mindesthaltezeit erfüllt ist. Gleichrangige ungeklärte Fensterangaben haben keinen Vorrang.

Scenario: Die Mindesthaltezeit ist erfüllt. Zwei gleichrangige aktuelle Meldungen für dasselbe Fenster lauten „geschlossen“ und „geschlossen“. Keine ist als Korrektur markiert.

Question: Ist die Anteilrückgabe nach dieser Regel im aktuellen Fenster möglich?

Expected: answer / no
Predicted: resolve_conflict / no
Rationale: Beide Quellen bestätigen geschlossen; daher Nein.
Technical issues: []

Unrounded native option scores:

{
  "action": {
    "answer": 0.24767889082431793,
    "ask_fact": 0.11428502947092056,
    "ask_target": 0.22728292644023895,
    "resolve_conflict": 0.41075316071510315
  },
  "determination": {
    "no": 0.4884932339191437,
    "unresolved": 0.4706977605819702,
    "yes": 0.04080904647707939
  }
}

