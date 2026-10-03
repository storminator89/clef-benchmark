### Modelle und Auswertung

Wähler 4B lief lokal mit Q8-Gewichten, acht CPU-Threads und nativer Kalibrierung. Clef Flash 9B lief im CPU-NF4-Profil mit BF16-Decision-Head; Jev 1.13.0 über eine gehostete API. Die Profile unterscheiden sich in Größe, Quantisierung und Ausführungsumgebung. Die Messung isoliert deshalb keinen Architektur- oder Quantisierungseffekt; lokale Forward-Zeiten und HTTP-Latenzen sind kein fairer Geschwindigkeitsvergleich.

Verglichen werden dieselben 580 vorab fixierten deutschen Fälle in acht getrennten Gruppen mit 968 Choice-Feldern. Maßgeblich sind die nativen Entscheidungen: Nur vollständig richtige Fälle zählen. Fehlende oder strukturell ungültige Antworten bleiben im geplanten Nenner. Reine Abweichungen der Wahrscheinlichkeitssumme werden separat diagnostiziert, nicht ausgeschlossen oder nachträglich normalisiert. Es gibt keine gepoolte Gesamtrangliste.

Wähler-Revision: `aeb171ee8ddd951cd8b4ee61cc0ed818d6b22cd8`; Modell-SHA-256: `7d9a13c147ed69e7b7f3e83c5f4034043936ba83aae3993dbbe436b885d84989`; JevAlt: `c0d443cba86e7f1e2545db79a37d546027ac321c`. Weitere Prüfsummen stehen in `comparison.json`. Die historischen Clef-/Jev-Ergebnisse bleiben unverändert.
