# Repo Bridge

Die Repo-Bridge ist die kontrollierte Grenze zwischen der read-only Quelle und der schreibbaren Sandbox.

## Wurzeln

- `source`
- `workspace`
- `output`

## Operationen

- `roots` zeigt die verfügbaren Wurzeln
- `tree` listet ein Verzeichnis
- `read` liest eine Datei
- `find` findet Datei- und Ordnernamen
- `search` sucht Textinhalt in Dateien
- `mkdir` erstellt einen Sandbox-Ordner
- `write` schreibt eine Textdatei in die Sandbox
- `doit` ist ein kleiner geführter Wrapper für `mkdir` und `write`

## Write-Regel

Verwende den Root-Namen und den relativen Pfad getrennt.

Beispiel:

```json
{
  "target_root": "output",
  "relative_path": "test/chat_note.md",
  "content": "Bridge test ok",
  "overwrite": true
}
```
