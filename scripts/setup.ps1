Param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ArgsList
)

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
python run.py setup @ArgsList
