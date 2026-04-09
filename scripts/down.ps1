Param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ArgsList
)

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
$Command = [System.IO.Path]::GetFileNameWithoutExtension($MyInvocation.MyCommand.Name)
python run.py $Command @ArgsList
