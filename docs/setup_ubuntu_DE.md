# Ubuntu-Setup

> Der englische Primärtext ist `setup_ubuntu.md`. Diese Datei ist der deutsche Klon.

## 1. Docker installieren

Nutze Docker Engine und das Docker-Compose-Plugin.

## 2. Repo klonen

```bash
git clone https://github.com/IMaugrenI/tof_local_builder.git
cd tof_local_builder
```

## 3. Umgebung vorbereiten

```bash
cp .env.example .env
mkdir -p data/ollama data/open-webui
```

## 4. Stack starten

```bash
docker compose up -d
```

## 5. Modell laden

```bash
docker exec -it tof_local_builder_ollama ollama pull qwen2.5-coder:14b
```

## 6. Oberfläche öffnen

Öffne `http://localhost:3000`

## Hinweise

- Auf kleineren Maschinen zuerst mit 7b oder 8b starten.
- Auf stärkeren Maschinen 14b und höher nutzen.
- Mit NVIDIA-GPU-Support kann `compose.yml` später für GPU-Nutzung erweitert werden.
