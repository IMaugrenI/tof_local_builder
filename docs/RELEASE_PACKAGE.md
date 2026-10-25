# ToF Local Builder – Offline source package guide

**Package type:** Source distribution candidate for Windows, Linux and macOS. **Not a native installer or an approved public release.** Final acceptance is deferred until all development work is complete.

## Requirements

- Docker with Docker Compose
- Python 3.11 or newer
- Windows: PowerShell 7 (`pwsh`); Linux/macOS: Bash
- Sufficient local storage for container images and an installed local AI model

The ZIP contains the existing source, Compose setup, and platform-specific starters. It does not install Python or Docker.

## Check and extract

The package is `tof_local_builder-source-candidate-<commit>.zip`, accompanied by `CHECKSUMS.sha256`.

- Linux: `sha256sum -c CHECKSUMS.sha256`
- macOS: `shasum -a 256 <zip-file>` and compare with the checksum file
- Windows: `Get-FileHash .\<zip-file> -Algorithm SHA256` and compare

Extract and enter `tof_local_builder`.

## Start using the existing scripts

Windows PowerShell 7:

```powershell
pwsh ./scripts/start_here.ps1
```

Linux:

```bash
bash scripts/start_here.sh
```

macOS:

```bash
bash scripts/start_here.command
```

These scripts retain the existing `run.py` and repository-defined Docker Compose startup path. Do not create a second stack.

## Use and troubleshoot

From the extracted project directory, open the local control UI with `python run.py ui` (often `python3` on Linux/macOS). Choose a source, separate sandbox and local model; review output before manually applying anything.

If needed, use `python run.py doctor` or read `START_HERE.md` and `INSTALL_AND_FIRST_TEST.md`.

## Release boundary

This is a **source package candidate**, not a native installer, completed platform validation, production certification, or public release. Extracting it does not launch services. No private local documents or credentials should be added to the package. Real system acceptance and public release authorization remain pending.
