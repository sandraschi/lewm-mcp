# Changelog

## v0.2.1 (2026-06-06)

- HF PushT checkpoint convert: ViT key remap for current transformers / vit_hf
- Fleet SOTA `webapp/start.ps1`: uv sync, smoke import, `/api/health` wait, npm install
- Root `start.bat` delegates to `webapp/start.ps1`
- `GET /api/health` for launcher probes
- Docs: `docs/` (INSTALL, MCP, WEBAPP, PAPER, UPSTREAM, PRD)
- `glama.json` manifest
- Dashboard paper link (arXiv 2603.19312 + arxiv-mcp depot note)
- `tools/ingest_lewm_paper.ps1` for fleet paper reading
- Central docs updated for real train/eval wiring

## v0.2.0 (2026-06-06)

- Clone upstream to `D:\Dev\repos\external\le-wm` with `tools/bootstrap_upstream.ps1`
- Real subprocess jobs: `train_run` → `train.py`, `eval_run` → `eval.py`
- Job supervisor: status, stop, logs under `logs/`
- Auto-discover upstream path + STABLEWM_HOME
- REST: `/api/jobs/train`, `/api/jobs/eval`, `/api/checkpoints`
- Dashboard: train/eval controls + job list
- Fleet `webapp/start.ps1` full-stack launcher

## v0.1.1 (2026-05-26)

- Fleet standards update: hatchling build, FastMCP 3.2, structlog
- Playwright e2e tests (fleet-audit.spec.ts)
- Tauri 2.0 native wrapper (native/)
- CI via GitHub Actions (ruff + pytest)
- Expanded smoke tests (mcp tools + api health)
- Standardized start.ps1, AGENTS.md, CHANGELOG.md

## v0.1.0 (2026-05-10)

- Initial repo structure
- FastMCP 3.1 server with 3 MCP tools (lewm_world, lewm_status, lewm_agentic_workflow)
- Glass dashboard (Vite React)
- UpstreamRunner bridge to lucas-maes/le-wm
