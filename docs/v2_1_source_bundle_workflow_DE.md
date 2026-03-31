# V2.1 Source-Bundle-Workflow

## Was das ergänzt

V2 hat die sichere Laufzeit-Trennung gesetzt:

- read-only Quell-Repo
- beschreibbare Builder-Sandbox

V2.1 ergänzt die erste praktische Brücke für Open WebUI:

- ein lesbares Source-Bundle aus der Quell-Repo bauen
- das Bundle in `sandbox/output/source_bundle/` ablegen
- dieses erzeugte Bundle in Open WebUI hochladen und lokal auswerten lassen

## Warum das existiert

Ein Mount allein macht Dateien im Container sichtbar, aber Open WebUI liest und versteht den Quellbaum nicht automatisch von selbst.

Dieser Workflow erzeugt deshalb ein kontrolliertes Übergabe-Artefakt für die WebUI.

## Schritt für Schritt

1. V2 starten.
2. Mounts prüfen:

```bash
bash scripts/test_v2_mounts.sh
```

3. Source-Bundle bauen:

```bash
bash scripts/build_source_bundle.sh
```

4. Optional kleineres Bundle:

```bash
bash scripts/build_source_bundle.sh --name repo_small --max-files 80 --max-bytes 120000
```

5. Erzeugte Dateien öffnen unter:

- `sandbox/output/source_bundle/`

6. Die Datei `*_bundle.md` in Open WebUI hochladen.

7. Das Modell bitten, zusammenzufassen, zu auditieren oder Folge-Dateien für die Sandbox zu entwerfen.

## Erzeugte Artefakte

- `*_manifest.txt`
- `*_tree.txt`
- `*_bundle.md`

## Gedachte Nutzung

- Repo-Audits
- Drift-Checks
- Architektur-Reviews
- Markdown-Entwürfe
- Shell-Skript-Entwürfe
- Python-Helfer-Entwürfe

## Wichtige Grenze

Dieser Workflow ist absichtlich konservativ.
Er schreibt nicht in die Quell-Repo.
Er erzeugt zuerst überprüfbare Artefakte in der Builder-Sandbox.
