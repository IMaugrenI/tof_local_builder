# Runtime-Image-Pinning

Dieses Repository legt die Runtime-Image-Referenzen bereits über `.env` offen:

```env
OLLAMA_IMAGE=ollama/ollama:latest
OPENWEBUI_IMAGE=ghcr.io/open-webui/open-webui:main
```

## Zweck

Das Ziel ist, von beweglichen Runtime-Referenzen auf ein bewusst getestetes Paar fester Tags umzusteigen.

## Sicherer Ablauf

1. einen Kandidaten-Tag für Ollama und einen Kandidaten-Tag für Open WebUI wählen
2. beide Tags in einer lokalen `.env` setzen
3. ausführen:

```bash
bash scripts/up.sh
bash scripts/check.sh
```

4. danach alles Folgende prüfen:
   - der Compose-Status ist healthy
   - das Standardmodell ist verfügbar
   - `repo_bridge` health ist grün
   - `repo_bridge` OpenAPI antwortet
   - Open WebUI öffnet sauber
5. erst dann das getestete Paar in die Operator-Basis übernehmen, die gehalten werden soll

## Warum das wichtig ist

Blind nur ein Image zu pinnen, ohne das Paar zu prüfen, kann unnötigen Drift zwischen Modellruntime, Web-Oberfläche und Operatorpfad erzeugen.

## Empfohlene Regel

- `latest` und `main` sind für Exploration okay
- explizite Tags sind besser für eine reproduzierbare Basis
- nur Tags pinnen, die wirklich zusammen getestet wurden

## Beispiel für die Übernahme

```env
OLLAMA_IMAGE=ollama/ollama:<getesteter-tag>
OPENWEBUI_IMAGE=ghcr.io/open-webui/open-webui:<getesteter-tag>
```

`<getesteter-tag>` erst ersetzen, wenn ein verifiziertes Paar vorliegt.
