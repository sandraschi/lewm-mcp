# Bootstrap lucas-maes/le-wm upstream for lewm-mcp (Python 3.10 venv + stable-worldmodel).
param(
    [string]$UpstreamRoot = "D:\Dev\repos\external\le-wm"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$Uv = if ($env:UV_EXE) { $env:UV_EXE } else { "uv" }

Write-Host "lewm-mcp: upstream bootstrap" -ForegroundColor Cyan
Write-Host "Target: $UpstreamRoot" -ForegroundColor DarkGray

$Parent = Split-Path $UpstreamRoot -Parent
if (-not (Test-Path $Parent)) {
    New-Item -ItemType Directory -Force -Path $Parent | Out-Null
}

if (-not (Test-Path (Join-Path $UpstreamRoot ".git"))) {
    Write-Host "Cloning https://github.com/lucas-maes/le-wm.git ..."
    Set-Location $Parent
    git clone https://github.com/lucas-maes/le-wm.git (Split-Path $UpstreamRoot -Leaf)
}

Set-Location $UpstreamRoot

Write-Host "Creating Python 3.10 venv ..."
& $Uv venv --python 3.10
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$Py = Join-Path $UpstreamRoot ".venv\Scripts\python.exe"
& $Uv pip install --python $Py "stable-worldmodel[train,env]"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$StableHome = Join-Path $UpstreamRoot ".stable-wm"
if (-not (Test-Path $StableHome)) {
    New-Item -ItemType Directory -Force -Path $StableHome | Out-Null
}

Write-Host ""
Write-Host "Upstream ready." -ForegroundColor Green
Write-Host "  LEWM_UPSTREAM_ROOT=$UpstreamRoot"
Write-Host "  LEWM_STABLEWM_HOME=$StableHome"
Write-Host ""
Write-Host "Next: download datasets from https://huggingface.co/collections/quentinll/lewm"
Write-Host "Place .h5 files under $StableHome"
Write-Host ""
Write-Host "Start lewm-mcp: Set-Location $RepoRoot; .\start.ps1"
