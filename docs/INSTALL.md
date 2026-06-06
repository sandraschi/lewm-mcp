# Installation

## Prerequisites

- Windows 10/11 with PowerShell
- [uv](https://github.com/astral-sh/uv) on PATH
- Node.js + npm (for dashboard)
- NVIDIA GPU recommended for train/eval (CPU possible for smoke tests only)
- Git

## 1. MCP server (this repo)

```powershell
cd D:\Dev\repos\lewm-mcp
uv sync --extra test --extra dev
uv run pytest tests/ -q
```

## 2. Upstream le-wm

```powershell
.\tools\bootstrap_upstream.ps1
```

This clones `lucas-maes/le-wm` to `D:\Dev\repos\external\le-wm` (or uses existing), creates Python **3.10** venv, installs `stable-worldmodel[train,env]`.

## 3. PushT checkpoint (eval policy)

```powershell
.\tools\download_pusht_assets.ps1
```

Downloads `quentinll/lewm-pusht` HF weights and converts to `STABLEWM_HOME/pusht/lewm_object.ckpt` (ViT key remap for current transformers).

For full eval, add the expert dataset (~13 GB):

```powershell
.\tools\download_pusht_assets.ps1 -WithDataset
```

## 4. Paper depot (arxiv-mcp)

```powershell
.\tools\ingest_lewm_paper.ps1
```

Ingests [arXiv:2603.19312](https://arxiv.org/abs/2603.19312) into the local arxiv-mcp corpus for semantic search.

## 5. Start stack

```powershell
.\start.bat
```

- Backend + MCP: http://127.0.0.1:10927
- Dashboard: http://127.0.0.1:10928

## Environment (optional)

Copy `.env.example` or set:

```powershell
$env:LEWM_UPSTREAM_ROOT = "D:\Dev\repos\external\le-wm"
$env:LEWM_STABLEWM_HOME = "D:\Dev\repos\external\le-wm\.stable-wm"
$env:LEWM_DEVICE = "cuda:0"
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Upstream venv missing | Re-run `bootstrap_upstream.ps1` |
| Policy not ready | Run `download_pusht_assets.ps1` |
| Eval fails on dataset | Pass `-WithDataset` or place `pusht_expert_train.h5` under STABLEWM_HOME |
| Port in use | `webapp/start.ps1` clears 10927/10928 automatically |
