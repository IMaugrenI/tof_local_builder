# ToF Local Builder – Offline-Anleitung zum Quellpaket

**Pakettyp:** Quellpaket-Kandidat für Windows, Linux und macOS; **keine native Installation, kein freigegebener Produkt-Release**. Die Abnahme erfolgt erst nach abgeschlossenem Ausbau.

## Voraussetzungen

- Docker mit Docker Compose auf dem Zielrechner
- Python 3.11 oder neuer
- Windows: PowerShell 7 (`pwsh`), Linux/macOS: Bash
- Genügend lokaler Speicher für Container und ein lokales KI-Modell

Das ZIP enthält vorhandene Repository-Dateien und Startskripte. Es installiert Docker/Python nicht automatisch.

## Paket prüfen und entpacken

Das heruntergeladene ZIP hat das Format `tof_local_builder-source-candidate-<commit>.zip`.
Die Datei `CHECKSUMS.sha256` enthält den erwarteten SHA-256-Hash.

- Linux: im Downloadverzeichnis `sha256sum -c CHECKSUMS.sha256`
- macOS: `shasum -a 256 <zip-dateiname>` und mit `CHECKSUMS.sha256` vergleichen
- Windows: `Get-FileHash .\<zip-dateiname> -Algorithm SHA256` und vergleichen

Entpacke das ZIP und wechsle in den Ordner `tof_local_builder`.

## Erster Start: vorhandener Weg

Windows PowerShell 7:

```powershell
pwsh ./scripts/start_here.ps1
```

Linux:

```bash
bash scripts/start_here.sh
```

macOS:

```bash
bash scripts/start_here.command
```

Der vorhandene Ablauf verwendet weiterhin `run.py` und die im Repository definierten Docker-Compose-Dateien. **Nicht** parallel eigene Compose-Instanzen starten.

## Browser-Steuerung und Hilfe

Vom entpackten Projektordner aus:

```bash
python run.py ui
```

Unter Linux/macOS heißt der Python-Befehl häufig `python3`. Danach Projekt und separate Sandbox wählen, lokale Modelle prüfen und die generierten Dateien vor einer manuellen Übernahme sichten.

Bei einem Problem: `python run.py doctor` (gegebenenfalls `python3`). Weitere Hilfe: `START_HERE_DE.md` und `INSTALL_AND_FIRST_TEST.md`.

## Grenzen

Das Paket ist **kein Installer**, keine Bestätigung von Windows-/macOS-/Linux-Runtime-Funktion und keine Produktfreigabe. Es startet beim Entpacken nichts, enthält keine persönlichen lokalen Einstellungen oder private Dokumente und veröffentlicht nichts über GitHub Releases. Die vollständige Abnahme und spätere Release-Freigabe bleiben ausdrücklich ausstehend.
