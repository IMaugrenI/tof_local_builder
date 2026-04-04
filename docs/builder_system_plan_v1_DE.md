# Builder-Systemplan v1

## Zweck

Dieses Dokument definiert den nächsten öffentlichen Produktschnitt für `tof_local_builder` nach der aktuellen Freeze-Basis.

Das Ziel ist **nicht**, den Builder in ein allgemeines lokales KI-Bundle zu verwandeln.
Das Ziel ist, den Builder zu einem klareren öffentlichen Produkt für lokale Arbeit mit geführter Modellauswahl zu machen.

## Produktlesart

`tof_local_builder` ist das lokale Builder-Produkt für:

- Chatten und Schreiben
- Repo-Lesen und kleine Code-Hilfe
- Textanalyse und Zusammenfassungen
- kontrollierte lokale Arbeit über Open WebUI und die Repo-Bridge
- optionale stärkere lokale Profile auf besserer Hardware

Der Builder ist **nicht** das Knowledge-System.
Knowledge, Embeddings, Retrieval und breitere RAG-Speicherlogik bleiben außerhalb des Builder-Produktschnitts.

## Warum dieser Plan existiert

Die aktuelle Wizard-Modellauswahl ist noch eine flache gemeinsame Liste.
Das ist für eine erste kuratierte Erweiterung in Ordnung, aber noch nicht die endgültige Produktform.

Der Builder soll nach der **Aufgabe** fragen und den Nutzer nicht zuerst Ollama-Tags verstehen lassen.

## Öffentliche Produktgrenze

Innerhalb des Builder-Produkts:

- allgemeine Chat- und Schreibmodelle
- Code-Helfermodelle
- Modelle für Textanalyse und Zusammenfassung
- optionale stärkere 3B-Profile
- optionales zukünftiges Vision-Profil
- manueller `custom`-Fallback

Außerhalb des Builder-Produkts:

- Embeddings
- reine Retrieval-Modelle
- Knowledge-Indexierung und Dokument-Stores
- breitere RAG-Pipelines
- Firmen-Knowledge-Systemlogik

## Builder-Modellpacks v1

Der erste öffentliche Pack-Schnitt soll auf dem aktuellen kuratierten Builder-Modellraum basieren.

### General / CPU-light

Nutzen, wenn die leichteste praktikable lokale Erfahrung gewünscht ist.

- `qwen2.5:0.5b`
- `llama3.2:1b`

### General / CPU-balanced

Nutzen, wenn ein besserer allgemeiner lokaler Assistent gewünscht ist, aber der Builder trotzdem im CPU-freundlichen Standardbereich bleiben soll.

- `qwen2.5:1.5b`
- `gemma2:2b`

### General / Optional 3B

Nur als bewusst stärkeres Profil nutzen, nicht als Standardpfad des Builders.

- `qwen2.5:3b`
- `llama3.2:3b`

### Code / CPU-light

Nutzen, wenn vor allem leichte Code-Hilfe, Snippets und kleine Fixes gebraucht werden.

- `qwen2.5-coder:0.5b`

### Code / CPU-balanced

Nutzen, wenn mehr brauchbare Repo- und Code-Hilfe gewünscht ist, ohne in die stärkere Stufe zu gehen.

- `qwen2.5-coder:1.5b`

### Code / Optional 3B

Nur als bewusst stärkeres Coding-Profil nutzen.

- `qwen2.5-coder:3b`

### Manueller Fallback

- `custom`

## Builder-Fragen im Wizard

Der nächste Wizard-Schritt soll von einer flachen Modellliste zu einem geführten Aufgabenfluss wechseln.

### Schritt 1 — Wofür brauchst du den Builder?

- Chatten und Schreiben
- Code und Repo-Hilfe
- Analysieren und Zusammenfassen
- Ich bin noch nicht sicher

### Schritt 2 — Wie leicht soll das Setup bleiben?

- sehr leicht
- ausgewogen
- stärkeres optionales Profil

### Schritt 3 — Builder-Empfehlung

Der Wizard soll dann zeigen:

- ein empfohlenes Modell
- eine kleine Zahl an Alternativen
- einen kurzen Grund in Klartext

Beispiel:

- Aufgabe: Code und Repo-Hilfe
- Hardware-Wunsch: ausgewogen
- Empfehlung: `qwen2.5-coder:1.5b`
- Alternativen: `qwen2.5-coder:0.5b`, `qwen2.5-coder:3b`

## Zielstruktur im Repo

Der Builder soll sich zu einem kleinen Modellkatalog bewegen statt zu einer langen hart verdrahteten Liste.

```text
model_catalog/
  builder_catalog.json
  catalog.schema.json
  general/
    cpu_light.json
    cpu_balanced.json
    optional_3b.json
  code/
    cpu_light.json
    cpu_balanced.json
    optional_3b.json
  analysis/
    cpu_light.json
    cpu_balanced.json
```

## Ziel-Datenform

Jeder Modelleintrag soll mehr Bedeutung tragen als nur den rohen Tag.

Vorgeschlagene Felder:

- `tag`
- `group`
- `profile`
- `task_labels`
- `recommended`
- `default_candidate`
- `notes`
- `visible_in_wizard`
- `experimental`

## Migrationspfad

### Phase 1

Die kuratierte Wizard-Modellerweiterung mergen.

### Phase 2

Die Builder-Modellkatalog-Dateien einführen und den aktuellen Setup-Fluss dabei noch kompatibel halten.

### Phase 3

Den Wizard ändern von:

- direkter Modellauswahl

zu:

- Aufgabenwahl
- Profilwahl
- Ausgabe eines empfohlenen Modells

### Phase 4

Einen fortgeschrittenen Ausweg behalten:

- alle kompatiblen Builder-Modelle anzeigen
- manueller `custom`-Tag-Eintrag

## Produktsprache

Der öffentliche Builder soll zuerst Produktsprache sprechen.

Gute Sprache:

- Chatten und Schreiben
- Code und Repo-Hilfe
- Analyse und Zusammenfassungen
- leichtes Profil
- ausgewogenes Profil
- stärkeres optionales Profil

Vermeiden als erste öffentliche Oberfläche:

- lange rohe Ollama-Tag-Listen
- Knowledge- oder Retrieval-Jargon
- embedding-zentrierte Auswahl im normalen Builder-Pfad

## Explizite Nicht-Ziele für v1

Dieser Plan führt **noch nicht** ein:

- ein Knowledge-Subsystem innerhalb des Builders
- Embedding-Packs im Standard-Builder-Wizard
- einen vollständigen All-Model-Browser
- Auto-Benchmarking oder hostbasierte Modell-Ranglisten
- ein zweites Produkt, das in das Builder-Repo hineingemischt wird

## Acceptance für Builder-Plan v1

Dieser Plan gilt als umgesetzt, wenn alle folgenden Punkte zutreffen:

1. die öffentliche Builder-Doku beschreibt den task-first-Modellschnitt
2. das Repo enthält einen klaren Zielpfad für gruppierte Modellpacks
3. der Wizard muss nicht dauerhaft an eine einzige flache Liste gebunden bleiben
4. der Builder bleibt standardmäßig CPU-first
5. stärkere 3B-Modelle bleiben optional und werden nicht zum neuen Default

## Zusammenfassung

Der Builder soll sich von einem lokalen Stack mit flachem Modellpicker zu einem geführten lokalen Builder-Produkt entwickeln.

Der Kernschritt ist einfach:

- weg von Modell-Tags als erstem Kontakt
- hin zu Aufgabe und Profil als erstem Kontakt

So bleibt der Builder öffentlich verständlich, CPU-freundlich und erweiterbar, ohne sich mit dem Knowledge-Produkt zu vermischen.
