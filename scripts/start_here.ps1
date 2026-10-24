$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (Get-Command py -ErrorAction SilentlyContinue) {
    $PythonCommand = "py"
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $PythonCommand = "python"
} else {
    Write-Error "Python 3.11+ was not found. Install Python and make either 'py' or 'python' available."
    exit 1
}

foreach ($Command in @("setup", "up", "check")) {
    & $PythonCommand run.py $Command
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}
