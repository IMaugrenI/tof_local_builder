# VS-Code-Sandbox-Workflow

Dieses Dokument beschreibt den beabsichtigten sicheren Ablauf für editorbasierte Arbeit mit `tof_local_builder`.

## Prinzip

Nutze VS Code als Arbeitsoberfläche.
Nutze `tof_local_builder` als lokale Modell- und Prompt-Basis.
Nutze die Sandbox als einzigen schreibbaren Arbeitsraum für frühe Experimente.

## Warum diese Trennung

- VS Code ist der praktische Editor-Arbeitsraum
- `tof_local_builder` bleibt die lokale AI-/Tool-Basis
- die Sandbox hält Experimente von echten Repos und aktiven Stacks fern

## Sicherer Grundstand

Zeige editorbasierte AI-Tools am Anfang nicht auf echte Produktiv-Repos.
Starte in:

- `sandbox/workspace/`

Erzeugte Ausgaben können zusätzlich gesammelt werden in:

- `sandbox/output/`

## Beispielnutzung

Ein Modell oder Editor-Tool darf dort erzeugen:

- `sandbox/workspace/coinflip.pu`
- `sandbox/workspace/module_candidate.md`
- `sandbox/output/notes.txt`

## Regel

Erst Sandbox.
Echte Repo später.

Erst nach Review sollte etwas in eine echte Repo übernommen werden.
