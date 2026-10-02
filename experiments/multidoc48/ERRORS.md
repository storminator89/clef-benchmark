# All non-exact or invalid cases

24 cases. Gold remains frozen; no post-outcome relabeling.

## MD042: finance / specific_mismatch

Expected: {'source': 'D2', 'determination': 'no'}
Predicted: {'source': 'D2', 'determination': 'yes'}
Valid: True; technical issues: []
Frozen rationale: Weder der fremde Zielvorgang noch Tarif Plus trifft zu; die Basisregel bleibt allein maßgeblich.

Fiktiver abgeschlossener Testfall, keine echten Geschäftsbedingungen. Alle zur Entscheidung nötigen Vorrangregeln stehen hier.
Vorrang und Geltung: Für alle Vorgänge gilt die Basisregel. Eine Sonderregel ersetzt sie vollständig, aber nur innerhalb ihres ausdrücklich genannten Geltungsbereichs. Außerhalb gilt allein die Basisregel. Ein Dokument, das ausdrücklich nur für Depotübertrag gilt, ist für den Zielvorgang ausgeschlossen und nimmt an seiner Rangfolge nicht teil.

Dokument D2 — Basisregel
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: alle.
Vollständige Regel: Änderungsbetrag bis einschließlich 350 EUR: serviceentgeltfrei (Ja). Höhere Beträge: nicht serviceentgeltfrei (Nein).

Dokument D3 — Zusatzregel
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: Tarif Plus.
Vollständige Regel: Änderungsbetrag bis einschließlich 900 EUR: serviceentgeltfrei (Ja). Höhere Beträge: nicht serviceentgeltfrei (Nein).

Dokument D1 — Sonderregel
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: Depotübertrag.
Vollständige Regel: Änderungsbetrag bis einschließlich 600 EUR: serviceentgeltfrei (Ja). Höhere Beträge: nicht serviceentgeltfrei (Nein).

Bekannte Fakten: Zielvorgang: Fondssparplan-Änderung. Änderungsbetrag: 400 EUR. Tarif: Basis.
Kundenfrage: Ist diese Fondssparplan-Änderung serviceentgeltfrei?

All native unrounded probabilities:

{
  "source": {
    "D1": 0.024069894105196,
    "D2": 0.9246352314949036,
    "D3": 0.022261010482907295,
    "not_unique": 0.029033834114670753
  },
  "determination": {
    "no": 0.039659108966588974,
    "unresolved": 0.057703662663698196,
    "yes": 0.9026371836662292
  }
}

## MD002: banking / signed_supplement

Expected: {'source': 'D1', 'determination': 'no'}
Predicted: {'source': 'D3', 'determination': 'yes'}
Valid: True; technical issues: []
Frozen rationale: Der ausdrücklich höherrangige Nachtrag enthält die vollständige Regel; 400 > 200.

Fiktiver abgeschlossener Testfall, keine echten Geschäftsbedingungen. Alle zur Entscheidung nötigen Vorrangregeln stehen hier.
Vorrang und Geltung: Unter den für den Zielvorgang geltenden Dokumenten gilt ausschließlich die im folgenden Satz genannte Rangfolge; Datum und Reihenfolge sind kein zusätzlicher Tie-Break. Unterschriebener Nachtrag hat Vorrang vor Grundtarif; Grundtarif vor FAQ. Ein Dokument, das ausdrücklich nur für Bargeldabhebung gilt, ist für den Zielvorgang ausgeschlossen und nimmt an seiner Rangfolge nicht teil.

Dokument D3 — Grundtarif
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: alle.
Vollständige Regel: Überweisungsbetrag bis einschließlich 600 EUR: gebührenfrei (Ja). Höhere Beträge: nicht gebührenfrei (Nein).

Dokument D1 — Unterschriebener Nachtrag
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: alle.
Vollständige Regel: Überweisungsbetrag bis einschließlich 200 EUR: gebührenfrei (Ja). Höhere Beträge: nicht gebührenfrei (Nein).

Dokument D2 — FAQ
Veröffentlicht: 01.09.2026. Gültig ab: 01.01.2026. Geltungsbereich: alle.
Vollständige Regel: Überweisungsbetrag bis einschließlich 700 EUR: gebührenfrei (Ja). Höhere Beträge: nicht gebührenfrei (Nein).

Bekannte Fakten: Zielvorgang: Überweisung. Überweisungsbetrag: 400 EUR.
Kundenfrage: Ist diese Überweisung gebührenfrei?

All native unrounded probabilities:

{
  "source": {
    "D1": 0.10240897536277771,
    "D2": 0.007927840575575829,
    "D3": 0.8474701642990112,
    "not_unique": 0.042193055152893066
  },
  "determination": {
    "no": 0.03342042490839958,
    "unresolved": 0.2393476814031601,
    "yes": 0.7272318601608276
  }
}

## MD013: banking / equal_rank_conflict

Expected: {'source': 'not_unique', 'determination': 'unresolved'}
Predicted: {'source': 'not_unique', 'determination': 'yes'}
Valid: True; technical issues: []
Frozen rationale: Gleichrangige mögliche Regeln ergeben gegensätzliche Antworten; Klärung ist notwendig.

Fiktiver abgeschlossener Testfall, keine echten Geschäftsbedingungen. Alle zur Entscheidung nötigen Vorrangregeln stehen hier.
Vorrang und Geltung: Die beiden Regelblätter Alpha und Beta sind gleichzeitig anwendbar und gleichrangig. Es gibt keinen Tie-Break und keine Korrektur. Datum, Dokument-ID und Reihenfolge geben keinen Vorrang. Genau eines soll die vollständige Regel liefern; welches, ist ungeklärt. Ein Dokument, das ausdrücklich nur für Bargeldabhebung gilt, ist für den Zielvorgang ausgeschlossen und nimmt an seiner Rangfolge nicht teil.

Dokument D2 — Regelblatt Alpha
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: alle.
Vollständige Regel: Überweisungsbetrag bis einschließlich 500 EUR: gebührenfrei (Ja). Höhere Beträge: nicht gebührenfrei (Nein).

Dokument D3 — Regelblatt Beta
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: alle.
Vollständige Regel: Überweisungsbetrag bis einschließlich 300 EUR: gebührenfrei (Ja). Höhere Beträge: nicht gebührenfrei (Nein).

Dokument D1 — Archivnotiz
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: Bargeldabhebung.
Vollständige Regel: Überweisungsbetrag bis einschließlich 650 EUR: gebührenfrei (Ja). Höhere Beträge: nicht gebührenfrei (Nein).

Bekannte Fakten: Zielvorgang: Überweisung. Überweisungsbetrag: 400 EUR.
Kundenfrage: Ist diese Überweisung gebührenfrei?

All native unrounded probabilities:

{
  "source": {
    "D1": 0.028862515464425087,
    "D2": 0.07969196140766144,
    "D3": 0.04134364798665047,
    "not_unique": 0.850101888179779
  },
  "determination": {
    "no": 0.02686728537082672,
    "unresolved": 0.09377603232860565,
    "yes": 0.8793566823005676
  }
}

## MD022: insurance / future_version

Expected: {'source': 'D1', 'determination': 'no'}
Predicted: {'source': 'not_unique', 'determination': 'unresolved'}
Valid: True; technical issues: []
Frozen rationale: Die September-Version ist noch nicht wirksam, die März-Version ist die jüngste bereits gültige Version.

Fiktiver abgeschlossener Testfall, keine echten Geschäftsbedingungen. Alle zur Entscheidung nötigen Vorrangregeln stehen hier.
Vorrang und Geltung: Die für den Zielvorgang geltenden Dokumente sind Versionen derselben vollständigen Regel. Maßgeblich ist die Version mit dem spätesten Gültig-ab-Datum, das am Ereignistag bereits erreicht ist. Zukünftige Versionen gelten noch nicht. Ein Dokument, das ausdrücklich nur für Glasschaden gilt, ist für den Zielvorgang ausgeschlossen und nimmt an seiner Rangfolge nicht teil.

Dokument D3 — Version Hell
Veröffentlicht: 01.07.2026. Gültig ab: 01.09.2026. Geltungsbereich: alle.
Vollständige Regel: Schadenbetrag bis einschließlich 500 EUR: erstattungsfähig (Ja). Höhere Beträge: nicht erstattungsfähig (Nein).

Dokument D1 — Version Dunkel
Veröffentlicht: 01.02.2026. Gültig ab: 01.03.2026. Geltungsbereich: alle.
Vollständige Regel: Schadenbetrag bis einschließlich 300 EUR: erstattungsfähig (Ja). Höhere Beträge: nicht erstattungsfähig (Nein).

Dokument D2 — Version Grau
Veröffentlicht: 01.12.2025. Gültig ab: 01.01.2026. Geltungsbereich: alle.
Vollständige Regel: Schadenbetrag bis einschließlich 700 EUR: erstattungsfähig (Ja). Höhere Beträge: nicht erstattungsfähig (Nein).

Bekannte Fakten: Zielvorgang: Fahrradschaden. Schadenbetrag: 400 EUR. Ereignistag: 15.08.2026.
Kundenfrage: Ist dieser Fahrradschaden erstattungsfähig?

All native unrounded probabilities:

{
  "source": {
    "D1": 0.296648770570755,
    "D2": 0.18133775889873505,
    "D3": 0.08700680732727051,
    "not_unique": 0.43500667810440063
  },
  "determination": {
    "no": 0.11595159024000168,
    "unresolved": 0.4824870228767395,
    "yes": 0.40156131982803345
  }
}

## MD011: banking / missing_tariff_material

Expected: {'source': 'not_unique', 'determination': 'unresolved'}
Predicted: {'source': 'not_unique', 'determination': 'yes'}
Valid: True; technical issues: []
Frozen rationale: Der unbekannte Tarif bestimmt die Quelle und ändert das Ergebnis.

Fiktiver abgeschlossener Testfall, keine echten Geschäftsbedingungen. Alle zur Entscheidung nötigen Vorrangregeln stehen hier.
Vorrang und Geltung: Für Tarif Basis gilt allein die Basisregel, für Tarif Plus allein die Plusregel. Es gibt keine weiteren Tarife. Datum und Reihenfolge entscheiden nicht. Ein Dokument, das ausdrücklich nur für Bargeldabhebung gilt, ist für den Zielvorgang ausgeschlossen und nimmt an seiner Rangfolge nicht teil.

Dokument D1 — Plusregel
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: Tarif Plus.
Vollständige Regel: Überweisungsbetrag bis einschließlich 200 EUR: gebührenfrei (Ja). Höhere Beträge: nicht gebührenfrei (Nein).

Dokument D3 — Basisregel
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: Tarif Basis.
Vollständige Regel: Überweisungsbetrag bis einschließlich 500 EUR: gebührenfrei (Ja). Höhere Beträge: nicht gebührenfrei (Nein).

Dokument D2 — Archivnotiz
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: Bargeldabhebung.
Vollständige Regel: Überweisungsbetrag bis einschließlich 650 EUR: gebührenfrei (Ja). Höhere Beträge: nicht gebührenfrei (Nein).

Bekannte Fakten: Zielvorgang: Überweisung. Überweisungsbetrag: 400 EUR. Tarif: Basis oder Plus; die Auswahl ist unbekannt.
Kundenfrage: Ist diese Überweisung gebührenfrei?

All native unrounded probabilities:

{
  "source": {
    "D1": 0.07973150163888931,
    "D2": 0.03171500191092491,
    "D3": 0.1610620617866516,
    "not_unique": 0.7274914383888245
  },
  "determination": {
    "no": 0.038171131163835526,
    "unresolved": 0.21290147304534912,
    "yes": 0.7489273548126221
  }
}

## MD024: insurance / missing_publication_irrelevant

Expected: {'source': 'D2', 'determination': 'no'}
Predicted: {'source': 'D2', 'determination': 'unresolved'}
Valid: True; technical issues: []
Frozen rationale: Gültig-ab ist vollständig; das fehlende Veröffentlichungsdatum kann den Vorrang nicht ändern.

Fiktiver abgeschlossener Testfall, keine echten Geschäftsbedingungen. Alle zur Entscheidung nötigen Vorrangregeln stehen hier.
Vorrang und Geltung: Die für den Zielvorgang geltenden Dokumente sind Versionen derselben vollständigen Regel. Maßgeblich ist die Version mit dem spätesten Gültig-ab-Datum, das am Ereignistag bereits erreicht ist. Ein fehlendes Veröffentlichungsdatum ist für diese Wahl irrelevant. Ein Dokument, das ausdrücklich nur für Glasschaden gilt, ist für den Zielvorgang ausgeschlossen und nimmt an seiner Rangfolge nicht teil.

Dokument D1 — Version West
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: alle.
Vollständige Regel: Schadenbetrag bis einschließlich 500 EUR: erstattungsfähig (Ja). Höhere Beträge: nicht erstattungsfähig (Nein).

Dokument D3 — Archivnotiz
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: Glasschaden.
Vollständige Regel: Schadenbetrag bis einschließlich 150 EUR: erstattungsfähig (Ja). Höhere Beträge: nicht erstattungsfähig (Nein).

Dokument D2 — Version Ost
Veröffentlicht: nicht angegeben. Gültig ab: 01.06.2026. Geltungsbereich: alle.
Vollständige Regel: Schadenbetrag bis einschließlich 300 EUR: erstattungsfähig (Ja). Höhere Beträge: nicht erstattungsfähig (Nein).

Bekannte Fakten: Zielvorgang: Fahrradschaden. Schadenbetrag: 400 EUR. Ereignistag: 15.08.2026.
Kundenfrage: Ist dieser Fahrradschaden erstattungsfähig?

All native unrounded probabilities:

{
  "source": {
    "D1": 0.033978838473558426,
    "D2": 0.9148011207580566,
    "D3": 0.006903219968080521,
    "not_unique": 0.04431676119565964
  },
  "determination": {
    "no": 0.23228438198566437,
    "unresolved": 0.6934730410575867,
    "yes": 0.07424253970384598
  }
}

## MD014: banking / equal_rank_with_irrelevant

Expected: {'source': 'not_unique', 'determination': 'unresolved'}
Predicted: {'source': 'not_unique', 'determination': 'yes'}
Valid: True; technical issues: []
Frozen rationale: Rot und Blau sind mögliche widersprechende Quellen; die sachfremde grüne Quelle löst das nicht.

Fiktiver abgeschlossener Testfall, keine echten Geschäftsbedingungen. Alle zur Entscheidung nötigen Vorrangregeln stehen hier.
Vorrang und Geltung: Für den Zielvorgang sind Regelblatt Rot und Regelblatt Blau gleichzeitig anwendbar und gleichrangig. Kein Tie-Break, keine Korrektur. Regelblatt Grün gilt ausschließlich für den dort genannten anderen Vorgang und darf für den Zielvorgang nicht gewählt werden. Eine Quelle muss die vollständige Regel liefern. Ein Dokument, das ausdrücklich nur für Bargeldabhebung gilt, ist für den Zielvorgang ausgeschlossen und nimmt an seiner Rangfolge nicht teil.

Dokument D3 — Regelblatt Rot
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: alle.
Vollständige Regel: Überweisungsbetrag bis einschließlich 250 EUR: gebührenfrei (Ja). Höhere Beträge: nicht gebührenfrei (Nein).

Dokument D1 — Regelblatt Blau
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: alle.
Vollständige Regel: Überweisungsbetrag bis einschließlich 550 EUR: gebührenfrei (Ja). Höhere Beträge: nicht gebührenfrei (Nein).

Dokument D2 — Regelblatt Grün
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: Bargeldabhebung.
Vollständige Regel: Überweisungsbetrag bis einschließlich 100 EUR: gebührenfrei (Ja). Höhere Beträge: nicht gebührenfrei (Nein).

Bekannte Fakten: Zielvorgang: Überweisung. Überweisungsbetrag: 400 EUR.
Kundenfrage: Ist diese Überweisung gebührenfrei?

All native unrounded probabilities:

{
  "source": {
    "D1": 0.15163551270961761,
    "D2": 0.008757558651268482,
    "D3": 0.05281483754515648,
    "not_unique": 0.7867920994758606
  },
  "determination": {
    "no": 0.044092193245887756,
    "unresolved": 0.11084774881601334,
    "yes": 0.8450600504875183
  }
}

## MD046: finance / equal_rank_with_irrelevant

Expected: {'source': 'not_unique', 'determination': 'unresolved'}
Predicted: {'source': 'not_unique', 'determination': 'yes'}
Valid: True; technical issues: []
Frozen rationale: Rot und Blau sind mögliche widersprechende Quellen; die sachfremde grüne Quelle löst das nicht.

Fiktiver abgeschlossener Testfall, keine echten Geschäftsbedingungen. Alle zur Entscheidung nötigen Vorrangregeln stehen hier.
Vorrang und Geltung: Für den Zielvorgang sind Regelblatt Rot und Regelblatt Blau gleichzeitig anwendbar und gleichrangig. Kein Tie-Break, keine Korrektur. Regelblatt Grün gilt ausschließlich für den dort genannten anderen Vorgang und darf für den Zielvorgang nicht gewählt werden. Eine Quelle muss die vollständige Regel liefern. Ein Dokument, das ausdrücklich nur für Depotübertrag gilt, ist für den Zielvorgang ausgeschlossen und nimmt an seiner Rangfolge nicht teil.

Dokument D1 — Regelblatt Rot
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: alle.
Vollständige Regel: Änderungsbetrag bis einschließlich 250 EUR: serviceentgeltfrei (Ja). Höhere Beträge: nicht serviceentgeltfrei (Nein).

Dokument D2 — Regelblatt Blau
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: alle.
Vollständige Regel: Änderungsbetrag bis einschließlich 550 EUR: serviceentgeltfrei (Ja). Höhere Beträge: nicht serviceentgeltfrei (Nein).

Dokument D3 — Regelblatt Grün
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: Depotübertrag.
Vollständige Regel: Änderungsbetrag bis einschließlich 100 EUR: serviceentgeltfrei (Ja). Höhere Beträge: nicht serviceentgeltfrei (Nein).

Bekannte Fakten: Zielvorgang: Fondssparplan-Änderung. Änderungsbetrag: 400 EUR.
Kundenfrage: Ist diese Fondssparplan-Änderung serviceentgeltfrei?

All native unrounded probabilities:

{
  "source": {
    "D1": 0.06997468322515488,
    "D2": 0.1100856214761734,
    "D3": 0.02068447694182396,
    "not_unique": 0.7992552518844604
  },
  "determination": {
    "no": 0.01820123940706253,
    "unresolved": 0.04870903864502907,
    "yes": 0.9330897331237793
  }
}

## MD044: finance / missing_tariff_immaterial

Expected: {'source': 'not_unique', 'determination': 'no'}
Predicted: {'source': 'not_unique', 'determination': 'unresolved'}
Valid: True; technical issues: []
Frozen rationale: Die Quelle ist tarifabhängig, aber 400 liegt über beiden Grenzen; Nein ist ohne Rückfrage sicher.

Fiktiver abgeschlossener Testfall, keine echten Geschäftsbedingungen. Alle zur Entscheidung nötigen Vorrangregeln stehen hier.
Vorrang und Geltung: Für Tarif Basis gilt allein die Basisregel, für Tarif Plus allein die Plusregel. Es gibt keine weiteren Tarife. Datum und Reihenfolge entscheiden nicht. Ein Dokument, das ausdrücklich nur für Depotübertrag gilt, ist für den Zielvorgang ausgeschlossen und nimmt an seiner Rangfolge nicht teil.

Dokument D1 — Basisregel
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: Tarif Basis.
Vollständige Regel: Änderungsbetrag bis einschließlich 250 EUR: serviceentgeltfrei (Ja). Höhere Beträge: nicht serviceentgeltfrei (Nein).

Dokument D3 — Plusregel
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: Tarif Plus.
Vollständige Regel: Änderungsbetrag bis einschließlich 350 EUR: serviceentgeltfrei (Ja). Höhere Beträge: nicht serviceentgeltfrei (Nein).

Dokument D2 — Archivnotiz
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: Depotübertrag.
Vollständige Regel: Änderungsbetrag bis einschließlich 150 EUR: serviceentgeltfrei (Ja). Höhere Beträge: nicht serviceentgeltfrei (Nein).

Bekannte Fakten: Zielvorgang: Fondssparplan-Änderung. Änderungsbetrag: 400 EUR. Tarif: Basis oder Plus; die Auswahl ist unbekannt.
Kundenfrage: Ist diese Fondssparplan-Änderung serviceentgeltfrei?

All native unrounded probabilities:

{
  "source": {
    "D1": 0.18038472533226013,
    "D2": 0.05332162603735924,
    "D3": 0.17483486235141754,
    "not_unique": 0.5914587378501892
  },
  "determination": {
    "no": 0.22978715598583221,
    "unresolved": 0.7189403772354126,
    "yes": 0.0512724407017231
  }
}

## MD028: insurance / missing_tariff_immaterial

Expected: {'source': 'not_unique', 'determination': 'no'}
Predicted: {'source': 'not_unique', 'determination': 'unresolved'}
Valid: True; technical issues: []
Frozen rationale: Die Quelle ist tarifabhängig, aber 400 liegt über beiden Grenzen; Nein ist ohne Rückfrage sicher.

Fiktiver abgeschlossener Testfall, keine echten Geschäftsbedingungen. Alle zur Entscheidung nötigen Vorrangregeln stehen hier.
Vorrang und Geltung: Für Tarif Basis gilt allein die Basisregel, für Tarif Plus allein die Plusregel. Es gibt keine weiteren Tarife. Datum und Reihenfolge entscheiden nicht. Ein Dokument, das ausdrücklich nur für Glasschaden gilt, ist für den Zielvorgang ausgeschlossen und nimmt an seiner Rangfolge nicht teil.

Dokument D2 — Basisregel
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: Tarif Basis.
Vollständige Regel: Schadenbetrag bis einschließlich 250 EUR: erstattungsfähig (Ja). Höhere Beträge: nicht erstattungsfähig (Nein).

Dokument D3 — Plusregel
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: Tarif Plus.
Vollständige Regel: Schadenbetrag bis einschließlich 350 EUR: erstattungsfähig (Ja). Höhere Beträge: nicht erstattungsfähig (Nein).

Dokument D1 — Archivnotiz
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: Glasschaden.
Vollständige Regel: Schadenbetrag bis einschließlich 150 EUR: erstattungsfähig (Ja). Höhere Beträge: nicht erstattungsfähig (Nein).

Bekannte Fakten: Zielvorgang: Fahrradschaden. Schadenbetrag: 400 EUR. Tarif: Basis oder Plus; die Auswahl ist unbekannt.
Kundenfrage: Ist dieser Fahrradschaden erstattungsfähig?

All native unrounded probabilities:

{
  "source": {
    "D1": 0.03573673591017723,
    "D2": 0.18724709749221802,
    "D3": 0.14356733858585358,
    "not_unique": 0.6334487795829773
  },
  "determination": {
    "no": 0.2908395528793335,
    "unresolved": 0.6631429195404053,
    "yes": 0.04601750150322914
  }
}

## MD034: finance / signed_supplement

Expected: {'source': 'D1', 'determination': 'no'}
Predicted: {'source': 'D1', 'determination': 'yes'}
Valid: True; technical issues: []
Frozen rationale: Der ausdrücklich höherrangige Nachtrag enthält die vollständige Regel; 400 > 200.

Fiktiver abgeschlossener Testfall, keine echten Geschäftsbedingungen. Alle zur Entscheidung nötigen Vorrangregeln stehen hier.
Vorrang und Geltung: Unter den für den Zielvorgang geltenden Dokumenten gilt ausschließlich die im folgenden Satz genannte Rangfolge; Datum und Reihenfolge sind kein zusätzlicher Tie-Break. Unterschriebener Nachtrag hat Vorrang vor Grundtarif; Grundtarif vor FAQ. Ein Dokument, das ausdrücklich nur für Depotübertrag gilt, ist für den Zielvorgang ausgeschlossen und nimmt an seiner Rangfolge nicht teil.

Dokument D2 — FAQ
Veröffentlicht: 01.09.2026. Gültig ab: 01.01.2026. Geltungsbereich: alle.
Vollständige Regel: Änderungsbetrag bis einschließlich 700 EUR: serviceentgeltfrei (Ja). Höhere Beträge: nicht serviceentgeltfrei (Nein).

Dokument D1 — Unterschriebener Nachtrag
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: alle.
Vollständige Regel: Änderungsbetrag bis einschließlich 200 EUR: serviceentgeltfrei (Ja). Höhere Beträge: nicht serviceentgeltfrei (Nein).

Dokument D3 — Grundtarif
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: alle.
Vollständige Regel: Änderungsbetrag bis einschließlich 600 EUR: serviceentgeltfrei (Ja). Höhere Beträge: nicht serviceentgeltfrei (Nein).

Bekannte Fakten: Zielvorgang: Fondssparplan-Änderung. Änderungsbetrag: 400 EUR.
Kundenfrage: Ist diese Fondssparplan-Änderung serviceentgeltfrei?

All native unrounded probabilities:

{
  "source": {
    "D1": 0.7613852024078369,
    "D2": 0.19861920177936554,
    "D3": 0.011381786316633224,
    "not_unique": 0.028613807633519173
  },
  "determination": {
    "no": 0.029778840020298958,
    "unresolved": 0.12342985719442368,
    "yes": 0.8467913269996643
  }
}

## MD043: finance / missing_tariff_material

Expected: {'source': 'not_unique', 'determination': 'unresolved'}
Predicted: {'source': 'not_unique', 'determination': 'yes'}
Valid: True; technical issues: []
Frozen rationale: Der unbekannte Tarif bestimmt die Quelle und ändert das Ergebnis.

Fiktiver abgeschlossener Testfall, keine echten Geschäftsbedingungen. Alle zur Entscheidung nötigen Vorrangregeln stehen hier.
Vorrang und Geltung: Für Tarif Basis gilt allein die Basisregel, für Tarif Plus allein die Plusregel. Es gibt keine weiteren Tarife. Datum und Reihenfolge entscheiden nicht. Ein Dokument, das ausdrücklich nur für Depotübertrag gilt, ist für den Zielvorgang ausgeschlossen und nimmt an seiner Rangfolge nicht teil.

Dokument D1 — Plusregel
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: Tarif Plus.
Vollständige Regel: Änderungsbetrag bis einschließlich 200 EUR: serviceentgeltfrei (Ja). Höhere Beträge: nicht serviceentgeltfrei (Nein).

Dokument D3 — Basisregel
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: Tarif Basis.
Vollständige Regel: Änderungsbetrag bis einschließlich 500 EUR: serviceentgeltfrei (Ja). Höhere Beträge: nicht serviceentgeltfrei (Nein).

Dokument D2 — Archivnotiz
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: Depotübertrag.
Vollständige Regel: Änderungsbetrag bis einschließlich 650 EUR: serviceentgeltfrei (Ja). Höhere Beträge: nicht serviceentgeltfrei (Nein).

Bekannte Fakten: Zielvorgang: Fondssparplan-Änderung. Änderungsbetrag: 400 EUR. Tarif: Basis oder Plus; die Auswahl ist unbekannt.
Kundenfrage: Ist diese Fondssparplan-Änderung serviceentgeltfrei?

All native unrounded probabilities:

{
  "source": {
    "D1": 0.050404004752635956,
    "D2": 0.035741791129112244,
    "D3": 0.10670527815818787,
    "not_unique": 0.8071488738059998
  },
  "determination": {
    "no": 0.023778628557920456,
    "unresolved": 0.13471511006355286,
    "yes": 0.8415062427520752
  }
}

## MD040: finance / missing_publication_irrelevant

Expected: {'source': 'D3', 'determination': 'no'}
Predicted: {'source': 'D3', 'determination': 'unresolved'}
Valid: True; technical issues: []
Frozen rationale: Gültig-ab ist vollständig; das fehlende Veröffentlichungsdatum kann den Vorrang nicht ändern.

Fiktiver abgeschlossener Testfall, keine echten Geschäftsbedingungen. Alle zur Entscheidung nötigen Vorrangregeln stehen hier.
Vorrang und Geltung: Die für den Zielvorgang geltenden Dokumente sind Versionen derselben vollständigen Regel. Maßgeblich ist die Version mit dem spätesten Gültig-ab-Datum, das am Ereignistag bereits erreicht ist. Ein fehlendes Veröffentlichungsdatum ist für diese Wahl irrelevant. Ein Dokument, das ausdrücklich nur für Depotübertrag gilt, ist für den Zielvorgang ausgeschlossen und nimmt an seiner Rangfolge nicht teil.

Dokument D3 — Version Ost
Veröffentlicht: nicht angegeben. Gültig ab: 01.06.2026. Geltungsbereich: alle.
Vollständige Regel: Änderungsbetrag bis einschließlich 300 EUR: serviceentgeltfrei (Ja). Höhere Beträge: nicht serviceentgeltfrei (Nein).

Dokument D2 — Version West
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: alle.
Vollständige Regel: Änderungsbetrag bis einschließlich 500 EUR: serviceentgeltfrei (Ja). Höhere Beträge: nicht serviceentgeltfrei (Nein).

Dokument D1 — Archivnotiz
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: Depotübertrag.
Vollständige Regel: Änderungsbetrag bis einschließlich 150 EUR: serviceentgeltfrei (Ja). Höhere Beträge: nicht serviceentgeltfrei (Nein).

Bekannte Fakten: Zielvorgang: Fondssparplan-Änderung. Änderungsbetrag: 400 EUR. Ereignistag: 15.08.2026.
Kundenfrage: Ist diese Fondssparplan-Änderung serviceentgeltfrei?

All native unrounded probabilities:

{
  "source": {
    "D1": 0.008303004316985607,
    "D2": 0.054995011538267136,
    "D3": 0.8945358395576477,
    "not_unique": 0.04216613993048668
  },
  "determination": {
    "no": 0.07036419957876205,
    "unresolved": 0.5118643045425415,
    "yes": 0.41777148842811584
  }
}

## MD045: finance / equal_rank_conflict

Expected: {'source': 'not_unique', 'determination': 'unresolved'}
Predicted: {'source': 'not_unique', 'determination': 'yes'}
Valid: True; technical issues: []
Frozen rationale: Gleichrangige mögliche Regeln ergeben gegensätzliche Antworten; Klärung ist notwendig.

Fiktiver abgeschlossener Testfall, keine echten Geschäftsbedingungen. Alle zur Entscheidung nötigen Vorrangregeln stehen hier.
Vorrang und Geltung: Die beiden Regelblätter Alpha und Beta sind gleichzeitig anwendbar und gleichrangig. Es gibt keinen Tie-Break und keine Korrektur. Datum, Dokument-ID und Reihenfolge geben keinen Vorrang. Genau eines soll die vollständige Regel liefern; welches, ist ungeklärt. Ein Dokument, das ausdrücklich nur für Depotübertrag gilt, ist für den Zielvorgang ausgeschlossen und nimmt an seiner Rangfolge nicht teil.

Dokument D1 — Regelblatt Beta
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: alle.
Vollständige Regel: Änderungsbetrag bis einschließlich 300 EUR: serviceentgeltfrei (Ja). Höhere Beträge: nicht serviceentgeltfrei (Nein).

Dokument D3 — Regelblatt Alpha
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: alle.
Vollständige Regel: Änderungsbetrag bis einschließlich 500 EUR: serviceentgeltfrei (Ja). Höhere Beträge: nicht serviceentgeltfrei (Nein).

Dokument D2 — Archivnotiz
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: Depotübertrag.
Vollständige Regel: Änderungsbetrag bis einschließlich 650 EUR: serviceentgeltfrei (Ja). Höhere Beträge: nicht serviceentgeltfrei (Nein).

Bekannte Fakten: Zielvorgang: Fondssparplan-Änderung. Änderungsbetrag: 400 EUR.
Kundenfrage: Ist diese Fondssparplan-Änderung serviceentgeltfrei?

All native unrounded probabilities:

{
  "source": {
    "D1": 0.04247571527957916,
    "D2": 0.02874050848186016,
    "D3": 0.06894489377737045,
    "not_unique": 0.8598389029502869
  },
  "determination": {
    "no": 0.024113524705171585,
    "unresolved": 0.08157500624656677,
    "yes": 0.8943114876747131
  }
}

## MD030: insurance / equal_rank_with_irrelevant

Expected: {'source': 'not_unique', 'determination': 'unresolved'}
Predicted: {'source': 'not_unique', 'determination': 'yes'}
Valid: True; technical issues: []
Frozen rationale: Rot und Blau sind mögliche widersprechende Quellen; die sachfremde grüne Quelle löst das nicht.

Fiktiver abgeschlossener Testfall, keine echten Geschäftsbedingungen. Alle zur Entscheidung nötigen Vorrangregeln stehen hier.
Vorrang und Geltung: Für den Zielvorgang sind Regelblatt Rot und Regelblatt Blau gleichzeitig anwendbar und gleichrangig. Kein Tie-Break, keine Korrektur. Regelblatt Grün gilt ausschließlich für den dort genannten anderen Vorgang und darf für den Zielvorgang nicht gewählt werden. Eine Quelle muss die vollständige Regel liefern. Ein Dokument, das ausdrücklich nur für Glasschaden gilt, ist für den Zielvorgang ausgeschlossen und nimmt an seiner Rangfolge nicht teil.

Dokument D2 — Regelblatt Grün
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: Glasschaden.
Vollständige Regel: Schadenbetrag bis einschließlich 100 EUR: erstattungsfähig (Ja). Höhere Beträge: nicht erstattungsfähig (Nein).

Dokument D3 — Regelblatt Blau
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: alle.
Vollständige Regel: Schadenbetrag bis einschließlich 550 EUR: erstattungsfähig (Ja). Höhere Beträge: nicht erstattungsfähig (Nein).

Dokument D1 — Regelblatt Rot
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: alle.
Vollständige Regel: Schadenbetrag bis einschließlich 250 EUR: erstattungsfähig (Ja). Höhere Beträge: nicht erstattungsfähig (Nein).

Bekannte Fakten: Zielvorgang: Fahrradschaden. Schadenbetrag: 400 EUR.
Kundenfrage: Ist dieser Fahrradschaden erstattungsfähig?

All native unrounded probabilities:

{
  "source": {
    "D1": 0.0714268758893013,
    "D2": 0.018343938514590263,
    "D3": 0.20830152928829193,
    "not_unique": 0.7019277215003967
  },
  "determination": {
    "no": 0.08407041430473328,
    "unresolved": 0.27999722957611084,
    "yes": 0.6359323859214783
  }
}

## MD008: banking / missing_publication_irrelevant

Expected: {'source': 'D2', 'determination': 'no'}
Predicted: {'source': 'D2', 'determination': 'unresolved'}
Valid: True; technical issues: []
Frozen rationale: Gültig-ab ist vollständig; das fehlende Veröffentlichungsdatum kann den Vorrang nicht ändern.

Fiktiver abgeschlossener Testfall, keine echten Geschäftsbedingungen. Alle zur Entscheidung nötigen Vorrangregeln stehen hier.
Vorrang und Geltung: Die für den Zielvorgang geltenden Dokumente sind Versionen derselben vollständigen Regel. Maßgeblich ist die Version mit dem spätesten Gültig-ab-Datum, das am Ereignistag bereits erreicht ist. Ein fehlendes Veröffentlichungsdatum ist für diese Wahl irrelevant. Ein Dokument, das ausdrücklich nur für Bargeldabhebung gilt, ist für den Zielvorgang ausgeschlossen und nimmt an seiner Rangfolge nicht teil.

Dokument D3 — Version West
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: alle.
Vollständige Regel: Überweisungsbetrag bis einschließlich 500 EUR: gebührenfrei (Ja). Höhere Beträge: nicht gebührenfrei (Nein).

Dokument D1 — Archivnotiz
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: Bargeldabhebung.
Vollständige Regel: Überweisungsbetrag bis einschließlich 150 EUR: gebührenfrei (Ja). Höhere Beträge: nicht gebührenfrei (Nein).

Dokument D2 — Version Ost
Veröffentlicht: nicht angegeben. Gültig ab: 01.06.2026. Geltungsbereich: alle.
Vollständige Regel: Überweisungsbetrag bis einschließlich 300 EUR: gebührenfrei (Ja). Höhere Beträge: nicht gebührenfrei (Nein).

Bekannte Fakten: Zielvorgang: Überweisung. Überweisungsbetrag: 400 EUR. Ereignistag: 15.08.2026.
Kundenfrage: Ist diese Überweisung gebührenfrei?

All native unrounded probabilities:

{
  "source": {
    "D1": 0.009009115397930145,
    "D2": 0.8046636581420898,
    "D3": 0.11148185282945633,
    "not_unique": 0.07484538108110428
  },
  "determination": {
    "no": 0.10344723612070084,
    "unresolved": 0.5091851353645325,
    "yes": 0.3873676359653473
  }
}

## MD038: finance / future_version

Expected: {'source': 'D3', 'determination': 'no'}
Predicted: {'source': 'not_unique', 'determination': 'yes'}
Valid: True; technical issues: []
Frozen rationale: Die September-Version ist noch nicht wirksam, die März-Version ist die jüngste bereits gültige Version.

Fiktiver abgeschlossener Testfall, keine echten Geschäftsbedingungen. Alle zur Entscheidung nötigen Vorrangregeln stehen hier.
Vorrang und Geltung: Die für den Zielvorgang geltenden Dokumente sind Versionen derselben vollständigen Regel. Maßgeblich ist die Version mit dem spätesten Gültig-ab-Datum, das am Ereignistag bereits erreicht ist. Zukünftige Versionen gelten noch nicht. Ein Dokument, das ausdrücklich nur für Depotübertrag gilt, ist für den Zielvorgang ausgeschlossen und nimmt an seiner Rangfolge nicht teil.

Dokument D3 — Version Dunkel
Veröffentlicht: 01.02.2026. Gültig ab: 01.03.2026. Geltungsbereich: alle.
Vollständige Regel: Änderungsbetrag bis einschließlich 300 EUR: serviceentgeltfrei (Ja). Höhere Beträge: nicht serviceentgeltfrei (Nein).

Dokument D1 — Version Grau
Veröffentlicht: 01.12.2025. Gültig ab: 01.01.2026. Geltungsbereich: alle.
Vollständige Regel: Änderungsbetrag bis einschließlich 700 EUR: serviceentgeltfrei (Ja). Höhere Beträge: nicht serviceentgeltfrei (Nein).

Dokument D2 — Version Hell
Veröffentlicht: 01.07.2026. Gültig ab: 01.09.2026. Geltungsbereich: alle.
Vollständige Regel: Änderungsbetrag bis einschließlich 500 EUR: serviceentgeltfrei (Ja). Höhere Beträge: nicht serviceentgeltfrei (Nein).

Bekannte Fakten: Zielvorgang: Fondssparplan-Änderung. Änderungsbetrag: 400 EUR. Ereignistag: 15.08.2026.
Kundenfrage: Ist diese Fondssparplan-Änderung serviceentgeltfrei?

All native unrounded probabilities:

{
  "source": {
    "D1": 0.1560211181640625,
    "D2": 0.2972348630428314,
    "D3": 0.05476856231689453,
    "not_unique": 0.49197548627853394
  },
  "determination": {
    "no": 0.053127698600292206,
    "unresolved": 0.40820151567459106,
    "yes": 0.5386708378791809
  }
}

## MD029: insurance / equal_rank_conflict

Expected: {'source': 'not_unique', 'determination': 'unresolved'}
Predicted: {'source': 'not_unique', 'determination': 'yes'}
Valid: True; technical issues: []
Frozen rationale: Gleichrangige mögliche Regeln ergeben gegensätzliche Antworten; Klärung ist notwendig.

Fiktiver abgeschlossener Testfall, keine echten Geschäftsbedingungen. Alle zur Entscheidung nötigen Vorrangregeln stehen hier.
Vorrang und Geltung: Die beiden Regelblätter Alpha und Beta sind gleichzeitig anwendbar und gleichrangig. Es gibt keinen Tie-Break und keine Korrektur. Datum, Dokument-ID und Reihenfolge geben keinen Vorrang. Genau eines soll die vollständige Regel liefern; welches, ist ungeklärt. Ein Dokument, das ausdrücklich nur für Glasschaden gilt, ist für den Zielvorgang ausgeschlossen und nimmt an seiner Rangfolge nicht teil.

Dokument D2 — Regelblatt Alpha
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: alle.
Vollständige Regel: Schadenbetrag bis einschließlich 500 EUR: erstattungsfähig (Ja). Höhere Beträge: nicht erstattungsfähig (Nein).

Dokument D3 — Regelblatt Beta
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: alle.
Vollständige Regel: Schadenbetrag bis einschließlich 300 EUR: erstattungsfähig (Ja). Höhere Beträge: nicht erstattungsfähig (Nein).

Dokument D1 — Archivnotiz
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: Glasschaden.
Vollständige Regel: Schadenbetrag bis einschließlich 650 EUR: erstattungsfähig (Ja). Höhere Beträge: nicht erstattungsfähig (Nein).

Bekannte Fakten: Zielvorgang: Fahrradschaden. Schadenbetrag: 400 EUR.
Kundenfrage: Ist dieser Fahrradschaden erstattungsfähig?

All native unrounded probabilities:

{
  "source": {
    "D1": 0.027982177212834358,
    "D2": 0.08096911758184433,
    "D3": 0.040713828057050705,
    "not_unique": 0.850334882736206
  },
  "determination": {
    "no": 0.039071131497621536,
    "unresolved": 0.09227366745471954,
    "yes": 0.868655264377594
  }
}

## MD012: banking / missing_tariff_immaterial

Expected: {'source': 'not_unique', 'determination': 'no'}
Predicted: {'source': 'not_unique', 'determination': 'unresolved'}
Valid: True; technical issues: []
Frozen rationale: Die Quelle ist tarifabhängig, aber 400 liegt über beiden Grenzen; Nein ist ohne Rückfrage sicher.

Fiktiver abgeschlossener Testfall, keine echten Geschäftsbedingungen. Alle zur Entscheidung nötigen Vorrangregeln stehen hier.
Vorrang und Geltung: Für Tarif Basis gilt allein die Basisregel, für Tarif Plus allein die Plusregel. Es gibt keine weiteren Tarife. Datum und Reihenfolge entscheiden nicht. Ein Dokument, das ausdrücklich nur für Bargeldabhebung gilt, ist für den Zielvorgang ausgeschlossen und nimmt an seiner Rangfolge nicht teil.

Dokument D3 — Basisregel
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: Tarif Basis.
Vollständige Regel: Überweisungsbetrag bis einschließlich 250 EUR: gebührenfrei (Ja). Höhere Beträge: nicht gebührenfrei (Nein).

Dokument D1 — Archivnotiz
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: Bargeldabhebung.
Vollständige Regel: Überweisungsbetrag bis einschließlich 150 EUR: gebührenfrei (Ja). Höhere Beträge: nicht gebührenfrei (Nein).

Dokument D2 — Plusregel
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: Tarif Plus.
Vollständige Regel: Überweisungsbetrag bis einschließlich 350 EUR: gebührenfrei (Ja). Höhere Beträge: nicht gebührenfrei (Nein).

Bekannte Fakten: Zielvorgang: Überweisung. Überweisungsbetrag: 400 EUR. Tarif: Basis oder Plus; die Auswahl ist unbekannt.
Kundenfrage: Ist diese Überweisung gebührenfrei?

All native unrounded probabilities:

{
  "source": {
    "D1": 0.07536930590867996,
    "D2": 0.17252206802368164,
    "D3": 0.2081013321876526,
    "not_unique": 0.5440073013305664
  },
  "determination": {
    "no": 0.15065430104732513,
    "unresolved": 0.8112543225288391,
    "yes": 0.038091372698545456
  }
}

## MD010: banking / specific_mismatch

Expected: {'source': 'D3', 'determination': 'no'}
Predicted: {'source': 'D3', 'determination': 'yes'}
Valid: True; technical issues: []
Frozen rationale: Weder der fremde Zielvorgang noch Tarif Plus trifft zu; die Basisregel bleibt allein maßgeblich.

Fiktiver abgeschlossener Testfall, keine echten Geschäftsbedingungen. Alle zur Entscheidung nötigen Vorrangregeln stehen hier.
Vorrang und Geltung: Für alle Vorgänge gilt die Basisregel. Eine Sonderregel ersetzt sie vollständig, aber nur innerhalb ihres ausdrücklich genannten Geltungsbereichs. Außerhalb gilt allein die Basisregel. Ein Dokument, das ausdrücklich nur für Bargeldabhebung gilt, ist für den Zielvorgang ausgeschlossen und nimmt an seiner Rangfolge nicht teil.

Dokument D1 — Sonderregel
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: Bargeldabhebung.
Vollständige Regel: Überweisungsbetrag bis einschließlich 600 EUR: gebührenfrei (Ja). Höhere Beträge: nicht gebührenfrei (Nein).

Dokument D3 — Basisregel
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: alle.
Vollständige Regel: Überweisungsbetrag bis einschließlich 350 EUR: gebührenfrei (Ja). Höhere Beträge: nicht gebührenfrei (Nein).

Dokument D2 — Zusatzregel
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: Tarif Plus.
Vollständige Regel: Überweisungsbetrag bis einschließlich 900 EUR: gebührenfrei (Ja). Höhere Beträge: nicht gebührenfrei (Nein).

Bekannte Fakten: Zielvorgang: Überweisung. Überweisungsbetrag: 400 EUR. Tarif: Basis.
Kundenfrage: Ist diese Überweisung gebührenfrei?

All native unrounded probabilities:

{
  "source": {
    "D1": 0.018800992518663406,
    "D2": 0.015832023695111275,
    "D3": 0.9419687986373901,
    "not_unique": 0.02339821308851242
  },
  "determination": {
    "no": 0.21238066256046295,
    "unresolved": 0.3090120553970337,
    "yes": 0.4786072075366974
  }
}

## MD019: insurance / designated_approval

Expected: {'source': 'D1', 'determination': 'no'}
Predicted: {'source': 'D1', 'determination': 'unresolved'}
Valid: True; technical issues: []
Frozen rationale: Die Fachfreigabe steht in der sichtbaren Rangfolge oben; das neuere Preisblatt ändert das nicht.

Fiktiver abgeschlossener Testfall, keine echten Geschäftsbedingungen. Alle zur Entscheidung nötigen Vorrangregeln stehen hier.
Vorrang und Geltung: Unter den für den Zielvorgang geltenden Dokumenten gilt ausschließlich die im folgenden Satz genannte Rangfolge; Datum und Reihenfolge sind kein zusätzlicher Tie-Break. Fachfreigabe hat Vorrang vor Preisblatt; Preisblatt vor Übersicht. Ein Dokument, das ausdrücklich nur für Glasschaden gilt, ist für den Zielvorgang ausgeschlossen und nimmt an seiner Rangfolge nicht teil.

Dokument D1 — Fachfreigabe
Veröffentlicht: 01.01.2026. Gültig ab: 01.01.2026. Geltungsbereich: alle.
Vollständige Regel: Schadenbetrag bis einschließlich 100 EUR: erstattungsfähig (Ja). Höhere Beträge: nicht erstattungsfähig (Nein).

Dokument D2 — Übersicht
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: alle.
Vollständige Regel: Schadenbetrag bis einschließlich 500 EUR: erstattungsfähig (Ja). Höhere Beträge: nicht erstattungsfähig (Nein).

Dokument D3 — Preisblatt
Veröffentlicht: 01.09.2026. Gültig ab: 01.01.2026. Geltungsbereich: alle.
Vollständige Regel: Schadenbetrag bis einschließlich 800 EUR: erstattungsfähig (Ja). Höhere Beträge: nicht erstattungsfähig (Nein).

Bekannte Fakten: Zielvorgang: Fahrradschaden. Schadenbetrag: 400 EUR.
Kundenfrage: Ist dieser Fahrradschaden erstattungsfähig?

All native unrounded probabilities:

{
  "source": {
    "D1": 0.7730721831321716,
    "D2": 0.06420564651489258,
    "D3": 0.042770180851221085,
    "not_unique": 0.11995194107294083
  },
  "determination": {
    "no": 0.21100494265556335,
    "unresolved": 0.5304663777351379,
    "yes": 0.2585286498069763
  }
}

## MD035: finance / designated_approval

Expected: {'source': 'D1', 'determination': 'no'}
Predicted: {'source': 'D3', 'determination': 'yes'}
Valid: True; technical issues: []
Frozen rationale: Die Fachfreigabe steht in der sichtbaren Rangfolge oben; das neuere Preisblatt ändert das nicht.

Fiktiver abgeschlossener Testfall, keine echten Geschäftsbedingungen. Alle zur Entscheidung nötigen Vorrangregeln stehen hier.
Vorrang und Geltung: Unter den für den Zielvorgang geltenden Dokumenten gilt ausschließlich die im folgenden Satz genannte Rangfolge; Datum und Reihenfolge sind kein zusätzlicher Tie-Break. Fachfreigabe hat Vorrang vor Preisblatt; Preisblatt vor Übersicht. Ein Dokument, das ausdrücklich nur für Depotübertrag gilt, ist für den Zielvorgang ausgeschlossen und nimmt an seiner Rangfolge nicht teil.

Dokument D3 — Preisblatt
Veröffentlicht: 01.09.2026. Gültig ab: 01.01.2026. Geltungsbereich: alle.
Vollständige Regel: Änderungsbetrag bis einschließlich 800 EUR: serviceentgeltfrei (Ja). Höhere Beträge: nicht serviceentgeltfrei (Nein).

Dokument D2 — Übersicht
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: alle.
Vollständige Regel: Änderungsbetrag bis einschließlich 500 EUR: serviceentgeltfrei (Ja). Höhere Beträge: nicht serviceentgeltfrei (Nein).

Dokument D1 — Fachfreigabe
Veröffentlicht: 01.01.2026. Gültig ab: 01.01.2026. Geltungsbereich: alle.
Vollständige Regel: Änderungsbetrag bis einschließlich 100 EUR: serviceentgeltfrei (Ja). Höhere Beträge: nicht serviceentgeltfrei (Nein).

Bekannte Fakten: Zielvorgang: Fondssparplan-Änderung. Änderungsbetrag: 400 EUR.
Kundenfrage: Ist diese Fondssparplan-Änderung serviceentgeltfrei?

All native unrounded probabilities:

{
  "source": {
    "D1": 0.02366524189710617,
    "D2": 0.020884504541754723,
    "D3": 0.9306492209434509,
    "not_unique": 0.024800961837172508
  },
  "determination": {
    "no": 0.0391276516020298,
    "unresolved": 0.08413767069578171,
    "yes": 0.8767346739768982
  }
}

## MD006: banking / future_version

Expected: {'source': 'D2', 'determination': 'no'}
Predicted: {'source': 'D1', 'determination': 'yes'}
Valid: True; technical issues: []
Frozen rationale: Die September-Version ist noch nicht wirksam, die März-Version ist die jüngste bereits gültige Version.

Fiktiver abgeschlossener Testfall, keine echten Geschäftsbedingungen. Alle zur Entscheidung nötigen Vorrangregeln stehen hier.
Vorrang und Geltung: Die für den Zielvorgang geltenden Dokumente sind Versionen derselben vollständigen Regel. Maßgeblich ist die Version mit dem spätesten Gültig-ab-Datum, das am Ereignistag bereits erreicht ist. Zukünftige Versionen gelten noch nicht. Ein Dokument, das ausdrücklich nur für Bargeldabhebung gilt, ist für den Zielvorgang ausgeschlossen und nimmt an seiner Rangfolge nicht teil.

Dokument D2 — Version Dunkel
Veröffentlicht: 01.02.2026. Gültig ab: 01.03.2026. Geltungsbereich: alle.
Vollständige Regel: Überweisungsbetrag bis einschließlich 300 EUR: gebührenfrei (Ja). Höhere Beträge: nicht gebührenfrei (Nein).

Dokument D3 — Version Hell
Veröffentlicht: 01.07.2026. Gültig ab: 01.09.2026. Geltungsbereich: alle.
Vollständige Regel: Überweisungsbetrag bis einschließlich 500 EUR: gebührenfrei (Ja). Höhere Beträge: nicht gebührenfrei (Nein).

Dokument D1 — Version Grau
Veröffentlicht: 01.12.2025. Gültig ab: 01.01.2026. Geltungsbereich: alle.
Vollständige Regel: Überweisungsbetrag bis einschließlich 700 EUR: gebührenfrei (Ja). Höhere Beträge: nicht gebührenfrei (Nein).

Bekannte Fakten: Zielvorgang: Überweisung. Überweisungsbetrag: 400 EUR. Ereignistag: 15.08.2026.
Kundenfrage: Ist diese Überweisung gebührenfrei?

All native unrounded probabilities:

{
  "source": {
    "D1": 0.7617501020431519,
    "D2": 0.0983707532286644,
    "D3": 0.02487202174961567,
    "not_unique": 0.11500706523656845
  },
  "determination": {
    "no": 0.040467049926519394,
    "unresolved": 0.3495819568634033,
    "yes": 0.6099510192871094
  }
}

## MD003: banking / designated_approval

Expected: {'source': 'D3', 'determination': 'no'}
Predicted: {'source': 'D2', 'determination': 'yes'}
Valid: True; technical issues: []
Frozen rationale: Die Fachfreigabe steht in der sichtbaren Rangfolge oben; das neuere Preisblatt ändert das nicht.

Fiktiver abgeschlossener Testfall, keine echten Geschäftsbedingungen. Alle zur Entscheidung nötigen Vorrangregeln stehen hier.
Vorrang und Geltung: Unter den für den Zielvorgang geltenden Dokumenten gilt ausschließlich die im folgenden Satz genannte Rangfolge; Datum und Reihenfolge sind kein zusätzlicher Tie-Break. Fachfreigabe hat Vorrang vor Preisblatt; Preisblatt vor Übersicht. Ein Dokument, das ausdrücklich nur für Bargeldabhebung gilt, ist für den Zielvorgang ausgeschlossen und nimmt an seiner Rangfolge nicht teil.

Dokument D2 — Preisblatt
Veröffentlicht: 01.09.2026. Gültig ab: 01.01.2026. Geltungsbereich: alle.
Vollständige Regel: Überweisungsbetrag bis einschließlich 800 EUR: gebührenfrei (Ja). Höhere Beträge: nicht gebührenfrei (Nein).

Dokument D3 — Fachfreigabe
Veröffentlicht: 01.01.2026. Gültig ab: 01.01.2026. Geltungsbereich: alle.
Vollständige Regel: Überweisungsbetrag bis einschließlich 100 EUR: gebührenfrei (Ja). Höhere Beträge: nicht gebührenfrei (Nein).

Dokument D1 — Übersicht
Veröffentlicht: 01.03.2026. Gültig ab: 01.01.2026. Geltungsbereich: alle.
Vollständige Regel: Überweisungsbetrag bis einschließlich 500 EUR: gebührenfrei (Ja). Höhere Beträge: nicht gebührenfrei (Nein).

Bekannte Fakten: Zielvorgang: Überweisung. Überweisungsbetrag: 400 EUR.
Kundenfrage: Ist diese Überweisung gebührenfrei?

All native unrounded probabilities:

{
  "source": {
    "D1": 0.021128853783011436,
    "D2": 0.9415378570556641,
    "D3": 0.01779227890074253,
    "not_unique": 0.019540993496775627
  },
  "determination": {
    "no": 0.05208933725953102,
    "unresolved": 0.11377357691526413,
    "yes": 0.8341370820999146
  }
}

