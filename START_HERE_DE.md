# Hier starten

Das ist der kürzeste Weg vom frischen Klon bis zum ersten sinnvoll nutzbaren lokalen KI-Arbeitsbereich.

> English version: [START_HERE.md](START_HERE.md)

## Wofür dieses Produkt gedacht ist

Wähle ein Projekt auf deinem Rechner, arbeite mit lokaler KI daran und halte das Originalprojekt geschützt.

Im normalen Ablauf bleibt das ausgewählte Projekt **nur lesbar**. Neue Arbeit entsteht getrennt davon, bis du selbst entscheidest, was du übernehmen möchtest.

## Was du brauchst

- Python 3.11+ (unter Windows über `py` oder `python`)
- Docker mit Docker Compose
- genügend lokalen Speicherplatz für das gewählte KI-Modell

Linux ist am tiefsten unterstützt. Für Windows und macOS gibt es eigene Starter.

## Erster Start

### Linux

```bash
git clone https://github.com/IMaugrenI/tof_local_builder.git
cd tof_local_builder
bash scripts/start_here.sh
```

### Windows PowerShell

```powershell
git clone https://github.com/IMaugrenI/tof_local_builder.git
cd tof_local_builder
pwsh ./scripts/start_here.ps1
```

### macOS

```bash
git clone https://github.com/IMaugrenI/tof_local_builder.git
cd tof_local_builder
./scripts/start_here.command
```

Beim ersten Start fragt ToF, mit welchem lokalen Projekt du arbeiten möchtest, und bereitet den Arbeitsbereich vor.

## Woran du erkennst, dass alles bereit ist

Du kannst anfangen, wenn die Steuerseite **Alles bereit** anzeigt und der Hauptbutton **Arbeitsbereich öffnen** anbietet.

Der normale Ablauf ist dann:

1. Projekt auswählen
2. Arbeitsbereich starten
3. prüfen, ob alles bereit ist
4. Arbeitsbereich öffnen und mit dem Projekt arbeiten
5. neue Dateien selbst prüfen, bevor du etwas übernimmst

Das Originalprojekt wird im normalen Ablauf nicht beschrieben.

## Wenn etwas nicht funktioniert

Öffne auf der Steuerseite **Probleme & technische Details → Problem finden**.

Im Terminal entspricht das:

```bash
python run.py doctor
```

Die normale Oberfläche zeigt dir den nächsten Schritt in verständlicher Sprache. Technische Ausgaben bleiben im Protokoll verfügbar, wenn du sie brauchst.

## Stoppen und später weitermachen

Stoppen:

```bash
python run.py down
```

Später wieder starten:

```bash
python run.py up
```

Die eigene Builder-Oberfläche wird über `up` unter `http://127.0.0.1:8795` geöffnet, sofern das automatische Browseröffnen aktiviert ist. Open WebUI wird nicht benötigt. Der aktuelle KI-Assistent liefert Planung und Analyse; autonome Dateibearbeitung ist noch nicht umgesetzt.

Dein ausgewähltes Projekt und die lokalen Einstellungen bleiben erhalten.

## Wo neue Arbeit landet

Für Nutzer gilt nur diese Regel:

- **Dein Projekt** bleibt geschützt.
- **Neue Arbeit** bleibt in einem getrennten lokalen Arbeitsbereich.
- **Du** entscheidest, was später übernommen oder geteilt wird.

Technische Pfade stehen in [docs/commands_DE.md](docs/commands_DE.md).

## Erweiterter Host-Reader

Für vertrauenswürdige lokale Nutzung gibt es einen optionalen erweiterten Host-Reader. Er ist mächtiger als der normale geschützte Projektablauf.

Lies vorher [STANDARD_START_HOST_READER.md](STANDARD_START_HOST_READER.md). Nicht ins LAN oder Internet freigeben.

## Beispiel aus echter Nutzung

[docs/USER_JOURNEY_DE.md](docs/USER_JOURNEY_DE.md) zeigt einen vollständigen ersten Ablauf inklusive eines typischen Fehlerfalls.

## Mehr Details

- [Einsteiger-Quickstart](docs/00_beginner_quickstart_DE.md)
- [Befehle](docs/commands_DE.md)
- [Technische Projektverbindung](docs/repo_bridge.md)
- [Product Constitution](docs/00_product/PRODUCT_CONSTITUTION_V2.md)
