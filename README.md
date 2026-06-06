# LeWM-MCP

<p align="center">
  <a href="https://github.com/casey/just"><img src="https://img.shields.io/badge/just-ready_to_go-7c5cfc?style=flat-square&logo=just&logoColor=white" alt="Just"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://biomejs.dev"><img src="https://img.shields.io/badge/Linted_with-Biome-60a5fa?style=flat-square&logo=biome&logoColor=white" alt="Biome"></a>
  <a href="https://github.com/PrefectHQ/fastmcp"><img src="https://img.shields.io/badge/FastMCP-3.2-7c5cfc?style=flat-square" alt="FastMCP"></a>
  <a href="https://playwright.dev"><img src="https://img.shields.io/badge/E2E-Playwright-45ba4b?style=flat-square&logo=playwright&logoColor=white" alt="Playwright"></a>
  <a href="https://tauri.app"><img src="https://img.shields.io/badge/Tauri-2.0-FFC131?style=flat-square&logo=tauri&logoColor=white" alt="Tauri"></a>
</p>

FastMCP **3.2** server bridging **LeWorldModel (LeWM)** — the compact JEPA world model from Maes et al. ([arXiv:2603.19312](https://arxiv.org/abs/2603.19312)) — into the fleet: **real upstream train/eval** subprocesses, **agentic** workflow prep, and a **glass** Vite dashboard.

Paper full text is ingested into **arxiv-mcp** via `tools/ingest_lewm_paper.ps1` so fleet users can read up easily.

## Quick Start

```powershell
uv sync --extra test --extra dev
.\tools\bootstrap_upstream.ps1
.\tools\download_pusht_assets.ps1
.\tools\ingest_lewm_paper.ps1
.\start.bat
```

- Backend + MCP: http://127.0.0.1:10927
- Dashboard: http://127.0.0.1:10928
- Upstream: `D:\Dev\repos\external\le-wm` (auto-discovered)

See [docs/INSTALL.md](docs/INSTALL.md) for eval dataset (`-WithDataset`, ~13 GB).

## MCP Tools

| Tool | Operations |
|---|---|
| `lewm_world` | health, train_prepare, **train_run**, infer_prepare, **eval_run**, checkpoint_list, job_status, job_stop, job_logs |
| `lewm_status` | Config snapshot, device, upstream venv, active job |
| `lewm_agentic_workflow` | Multi-step planning (optional LLM sampling) |

`train_run` spawns upstream `python train.py data=pusht`. `eval_run` spawns `python eval.py --config-name=pusht.yaml policy=pusht/lewm`.

## Documentation

| Doc | Topic |
|-----|-------|
| [docs/PRD.md](docs/PRD.md) | Product requirements |
| [docs/MCP.md](docs/MCP.md) | Tools and transports |
| [docs/WEBAPP.md](docs/WEBAPP.md) | Dashboard and API |
| [docs/PAPER.md](docs/PAPER.md) | Research paper + arxiv-mcp |
| [docs/UPSTREAM.md](docs/UPSTREAM.md) | le-wm integration |

## Fleet Integration

- Ports **10927** / **10928** in [mcp-central-docs](https://github.com/sandraschi/mcp-central-docs) registry
- Optional proxy via google-ai-mcp `google_ai_world` at http://127.0.0.1:11014

## Tests

```powershell
uv run pytest tests/ -q
cd webapp; npx playwright test
```

## Configuration

```powershell
$env:LEWM_UPSTREAM_ROOT = "D:\Dev\repos\external\le-wm"
$env:LEWM_STABLEWM_HOME = "D:\Dev\repos\external\le-wm\.stable-wm"
$env:LEWM_DEVICE = "cuda:0"
```

## Repository

https://github.com/sandraschi/lewm-mcp
