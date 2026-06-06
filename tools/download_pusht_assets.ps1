# Download LeWM PushT checkpoint (+ optional 13GB dataset) into STABLEWM_HOME.
param(
    [string]$UpstreamRoot = "D:\Dev\repos\external\le-wm",
    [switch]$WithDataset
)

$ErrorActionPreference = "Stop"
$StableHome = Join-Path $UpstreamRoot ".stable-wm"
$Py = Join-Path $UpstreamRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $Py)) {
    Write-Host "Upstream venv missing. Run tools\bootstrap_upstream.ps1 first." -ForegroundColor Red
    exit 1
}

New-Item -ItemType Directory -Force -Path $StableHome | Out-Null
$HfModelDir = Join-Path $StableHome "hf_pusht"
New-Item -ItemType Directory -Force -Path $HfModelDir | Out-Null

Write-Host "Downloading LeWM PushT checkpoint (weights.pt + config.json) ..." -ForegroundColor Cyan
& $Py -c @"
from huggingface_hub import hf_hub_download
from pathlib import Path
dest = Path(r'$HfModelDir')
for name in ('weights.pt', 'config.json', 'README.md'):
    p = hf_hub_download(repo_id='quentinll/lewm-pusht', repo_type='model', filename=name, local_dir=str(dest))
    print('ok', p)
"@
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$env:LEWM_UPSTREAM_ROOT = $UpstreamRoot
$env:LEWM_STABLEWM_HOME = $StableHome
$env:STABLEWM_HOME = $StableHome

Write-Host "Converting HF weights to pusht/lewm_object.ckpt ..." -ForegroundColor Cyan
& $Py (Join-Path $RepoRoot "tools\convert_hf_pusht_ckpt.py")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if ($WithDataset) {
    Write-Host "Downloading pusht_expert_train.h5.zst (~13GB) - this takes a while ..." -ForegroundColor Yellow
    & $Py -c @"
from huggingface_hub import hf_hub_download
from pathlib import Path
import subprocess, sys
home = Path(r'$StableHome')
zst = hf_hub_download(
    repo_id='quentinll/lewm-pusht',
    repo_type='dataset',
    filename='pusht_expert_train.h5.zst',
    local_dir=str(home),
)
print('downloaded', zst)
out_h5 = home / 'pusht_expert_train.h5'
if not out_h5.exists():
    subprocess.run(['tar', '--zstd', '-xvf', str(zst), '-C', str(home)], check=True)
print('dataset ready', out_h5)
"@
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} else {
    Write-Host "Skipping dataset (pass -WithDataset for eval). Checkpoint is ready for infer_prepare." -ForegroundColor DarkGray
}

Write-Host "Done. STABLEWM_HOME=$StableHome" -ForegroundColor Green
