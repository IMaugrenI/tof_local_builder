# Nutzerreise aus der Praxis

## Ziel

Mit lokaler KI an einem vorhandenen Projekt arbeiten, ohne dass der normale Builder-Ablauf das Originalprojekt verändert.

## Erster kompletter Ablauf

1. Repository klonen und den passenden `start_here`-Befehl starten.
2. Den Projektordner auswählen, mit dem du arbeiten möchtest.
3. ToF den lokalen Arbeitsbereich vorbereiten und starten lassen.
4. Warten, bis die Steuerseite **Alles bereit** zeigt.
5. **Arbeitsbereich öffnen** wählen.
6. Der lokalen KI eine Aufgabe für dein Projekt geben.
7. Die erzeugte Arbeit im getrennten Arbeitsbereich prüfen.
8. Nur das selbst in dein echtes Projekt übernehmen, was du wirklich behalten möchtest.

**Erfolgreiches Ergebnis:** Du hast nutzbare neue Arbeit, während das ausgewählte Originalprojekt vom normalen Builder-Ablauf nicht beschrieben wurde.

## Typischer Fehlerfall

Wenn die Steuerseite meldet, dass dein Projekt noch nicht bereit ist:

1. prüfen, ob der Projektordner noch existiert
2. **Probleme & technische Details** öffnen
3. **Problem finden** wählen
4. der verständlichen Empfehlung folgen
5. das technische Protokoll nur öffnen, wenn du mehr Details brauchst

## Stoppen und später zurückkehren

Stoppen mit `python run.py down`.

Später `python run.py up` und `python run.py ui` ausführen. Das Projekt musst du nicht erneut auswählen, solange du es nicht wechseln möchtest.
