Param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ArgsList
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
$Command = [System.IO.Path]::GetFileNameWithoutExtension($MyInvocation.MyCommand.Name)

if (Get-Command py -ErrorAction SilentlyContinue) {
    $PythonCommand = "py"
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $PythonCommand = "python"
} else {
    Write-Error "Python 3.11+ was not found. Install Python and make either 'py' or 'python' available."
    exit 1
}

& $PythonCommand run.py $Command @ArgsList
exit $LASTEXITCODE
