# Ubuntu setup

## 1. Install Docker

Use Docker Engine and Docker Compose plugin.

## 2. Clone the repo

```bash
git clone https://github.com/IMaugrenI/tof_local_builder.git
cd tof_local_builder
```

## 3. Prepare env

```bash
cp .env.example .env
mkdir -p data/ollama data/open-webui
```

## 4. Start the stack

```bash
docker compose up -d
```

## 5. Pull a model

```bash
docker exec -it tof_local_builder_ollama ollama pull qwen2.5-coder:14b
```

## 6. Open UI

Open `http://localhost:3000`

## Notes

- On small machines, start with 7b or 8b models.
- On larger machines, use 14b and above.
- If you have NVIDIA GPU support on the host, you can extend `compose.yml` later for GPU runtime.
