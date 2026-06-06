# LeWM-MCP — Product Requirements (v0.2)

**Status:** Active · **Paper:** [arXiv:2603.19312](https://arxiv.org/abs/2603.19312) · **Upstream:** [lucas-maes/le-wm](https://github.com/lucas-maes/le-wm)

## 1. Problem

Agents and operators need to **train and evaluate** LeWorldModel on a single GPU without hand-wiring subprocesses, env vars, and checkpoint paths every session. The official codebase is research-grade; the fleet needs a **standards-compliant MCP bridge** with honest health reporting and a glass dashboard.

## 2. Solution summary

| Surface | Role |
|---------|------|
| **MCP server** (`lewm_world`, `lewm_status`, `lewm_agentic_workflow`) | Health, train/eval job control, checkpoint listing, agentic planning |
| **FastAPI** (`/api/*`, `/mcp`) | REST for dashboard + streamable MCP on port **10927** |
| **Vite dashboard** | Train/eval controls, job list, paper links — port **10928** |
| **Upstream subprocess** | Real `train.py` / `eval.py` in Python 3.10 venv under `external/le-wm` |

This repo does **not** reimplement LeWM. It orchestrates the upstream project.

## 3. v0.2 scope (shipped)

| In scope | Out of scope |
|----------|--------------|
| Clone/bootstrap upstream via `tools/bootstrap_upstream.ps1` | Multi-GPU distributed training |
| Subprocess jobs with logs under `logs/` | Reimplementing JEPA architecture |
| HF PushT checkpoint download + ViT key remap convert | Full surprise/planning MCP surface |
| `eval_run` with `pusht/lewm` policy | Cloud training runners |
| Fleet `webapp/start.ps1` (uv sync, smoke import, health wait) | google-ai-mcp proxy hardening |
| arxiv-mcp depot ingest for paper **2603.19312** | |

## 4. Ports & startup

| Service | Port |
|---------|------|
| FastAPI + MCP HTTP `/mcp` | **10927** |
| Vite dashboard | **10928** |

**Start:** `.\start.bat` or `.\webapp\start.ps1` from repo root.

## 5. Configuration

| Variable | Purpose |
|----------|---------|
| `LEWM_UPSTREAM_ROOT` | Path to `le-wm` clone (default auto-discover `external/le-wm`) |
| `LEWM_STABLEWM_HOME` / `STABLEWM_HOME` | Checkpoints + datasets (default `.stable-wm` under upstream) |
| `LEWM_DEVICE` | e.g. `cuda:0` |
| `LEWM_DRY_RUN` | `1` = log commands without spawning (tests) |

## 6. Assets pipeline

1. `.\tools\bootstrap_upstream.ps1` — Python 3.10 venv + `stable-worldmodel[train,env]`
2. `.\tools\download_pusht_assets.ps1` — HF weights + convert to `pusht/lewm_object.ckpt`
3. `.\tools\download_pusht_assets.ps1 -WithDataset` — ~13GB expert dataset for eval
4. `.\tools\ingest_lewm_paper.ps1` — arxiv-mcp depot for fleet reading

## 7. Paper & research context

**LeWorldModel** — compact (~15M params) end-to-end JEPA from pixels; stable training with minimal losses. Maes, Le Lidec, Scieur, LeCun, Balestriero (2026).

Fleet users should read the paper via **arxiv-mcp** (`search_depot_corpus` on `2603.19312`) after running the ingest script.

## 8. Roadmap (v0.3+)

- `rollout` / surprise evaluation tools wired to upstream APIs
- Optional Anthropic sampling for `lewm_agentic_workflow`
- Prebuilt `_object.ckpt` mirror (Google Drive) when HF convert is brittle across transformer versions
- google-ai-mcp `google_ai_world` proxy parity

## 9. Success criteria

- [x] `uv run pytest` passes with `LEWM_DRY_RUN=1`
- [x] `/api/health` returns 200 for fleet launcher
- [x] `train_run` / `eval_run` spawn real upstream processes when upstream venv exists
- [x] PushT checkpoint converts from HF `weights.pt`
- [ ] Eval completes with downloaded dataset (operator GPU step)
