# tof_local_builder

> Die englische Hauptfassung liegt in `README.md`.

Lokaler KI_Builder fuer kontrolliertes Arbeiten auf einem einzelnen Rechner oder in einem kleinen lokalen Team.

Ich habe dieses Repo gebaut, damit Quellzugriff read_only bleibt, Ausgaben sauber in einer Sandbox landen und der Einstieg moeglichst einfach ist.

## start_here

```bash
bash scripts/setup.sh
bash scripts/up.sh
bash scripts/check.sh
```

Nach dem Start oeffne `http://localhost:3000` und verbinde den Tool_Server unter `http://127.0.0.1:8099`.

## was_dieses_repo_macht

1. es fuehrt lokale Modelle ueber Ollama aus
2. es stellt eine Browser_GUI ueber Open WebUI bereit
3. es liest einen eingebundenen Quellpfad read_only
4. es schreibt gepruefte Artefakte nur in eine lokale Sandbox
5. es nutzt einen first_run Wizard fuer Setup und Modellwahl
6. es bleibt standardmaessig CPU_schonend, mit optionaler spaeterer Beschleunigung

## was_dieses_repo_zeigt

1. hands_on Arbeit mit Linux und Docker
2. klare Grenzen zwischen Quelle und Ausgabe
3. produktorientiertes Denken fuer lokale Workflows
4. praktische Repo_ und Dokumentationsdisziplin
5. kontrollierte Experimente ohne direkte Schreibzugriffe auf die Quelle

## grenze

1. das Quellrepo bleibt read_only
2. Schreibvorgaenge bleiben auf `sandbox/workspace` und `sandbox/output` begrenzt
3. das ist ein Builder_Stack und kein allgemeines Wissenssystem
4. lokaler Einsatz steht im Vordergrund

## zentrale_runtime_teile

- `ollama` = lokaler Modell_Runtime
- `open-webui` = Browser_GUI
- `repo-bridge` = kontrollierte read_write Grenze fuer Quelle und Sandbox
- `wizard.py` = einmaliger lokaler Setup_Leitfaden vor der Web_Uebergabe

## wichtige_dateien

- `compose.yml`
- `.env.example`
- `scripts/setup.sh`
- `scripts/up.sh`
- `scripts/check.sh`
- `scripts/down.sh`
- `scripts/wizard.py`
- `docs/product/START_HERE.md`
- `docs/product/WHY.md`
- `docs/repo_bridge.md`
- `services/repo_bridge/`

## verwandte_oeffentliche_repos

- [`tof_local_knowledge`](https://github.com/IMaugrenI/tof_local_knowledge) — lokale Dokumenten_Indexierung und belegte Antworten
- [`tof_showcase`](https://github.com/IMaugrenI/tof-showcase) — oeffentlicher Architektur_Einstieg
- [`tof_v7_public_frame`](https://github.com/IMaugrenI/tof-v7-public-frame) — reduzierter V7_Grenzrahmen
