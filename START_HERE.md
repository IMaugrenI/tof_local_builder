# Start here

This is the shortest path from a fresh clone to your first useful local AI workspace.

> German version: [START_HERE_DE.md](START_HERE_DE.md)

## What this product is for

Choose a project on your computer, work with local AI, and keep the original project protected.

The normal workflow keeps the project you selected **read-only**. New work is created in a separate local work area until you decide what to keep.

## What you need

- Python 3.11+ (`py` or `python` on Windows)
- Docker with Docker Compose
- enough local disk space for the AI model you choose

Linux is the deepest-supported platform. Windows and macOS launchers are included.

## First start

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

On the first start, ToF asks you which local project you want to work with and prepares the local workspace.

## What success looks like

You are ready when the control page says **Everything ready** and the main button says **Open workspace**.

Your normal path is then:

1. choose your project
2. start the workspace
3. check that everything is ready
4. open the workspace and work with the project
5. review new files before moving anything yourself

Your original project is not written to by the normal builder path.

## If something does not work

Use the control page and choose **Problems & technical details → Find a problem**.

From the terminal, the same check is:

```bash
python run.py doctor
```

The normal UI gives you the plain-language next step. Technical output stays available in the activity log when you need it.

## Stop and come back later

Stop the local workspace with:

```bash
python run.py down
```

Later, return with:

```bash
python run.py up
python run.py ui
```

Your selected project and local settings remain in the local configuration.

## Where new work goes

The user-facing rule is simple:

- **Your project** stays protected.
- **New work** stays in a separate local work area.
- **You** decide what is later moved or shared.

For technical path details, see [docs/commands.md](docs/commands.md).

## Advanced host-reader mode

An optional advanced host-reader exists for trusted local use. It is more powerful than the normal protected-project workflow.

Read [STANDARD_START_HOST_READER.md](STANDARD_START_HOST_READER.md) before using it. Keep it local and do not expose it to a LAN or the internet.

## Real-life example

See [docs/USER_JOURNEY.md](docs/USER_JOURNEY.md) for one complete first-time journey, including a realistic failure path.

## More detail

- [Beginner quickstart](docs/00_beginner_quickstart.md)
- [Commands](docs/commands.md)
- [Technical project connection](docs/repo_bridge.md)
- [Product constitution](docs/00_product/PRODUCT_CONSTITUTION_V1.md)
