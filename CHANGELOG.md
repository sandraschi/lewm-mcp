
## [Unreleased] — 2026-07-13

### Added
- Prefab UI card: `show_lewm_status_card` with `@mcp.tool(app=True)`
- MCP resource: `status://lewm/config` for live config snapshot
- Tool annotations: `readonly` for `lewm_status`/`lewm_agentic_workflow`
- Session context injection: `.cursorrules` for tool-awareness
- `playwright.config.ts` for E2E test configuration

### Fixed
- Security: `build.ps1` now bundles `.env.example` instead of `.env` (was leaking dev API keys)
- Security: `tauri.conf.json` resources updated to `.env.example`
- Tauri: `hooks.nsh` process names fixed to match actual binaries (`lewm-mcp-backend.exe`)
- Tauri: `tauri.conf.json` targets changed from `"all"` to `["nsis"]`
- Tauri: `backend.rs` upgraded with `free_port()`, stream watching, health polling
- Version: `__init__.py` synced to match `pyproject.toml` (0.2.1)

## [Unreleased] — 2026-06-14

### Fixed
- Tauri build: resolved Rust crate conflict (brotli/alloc-no-stdlib)
- Tauri build: fixed PyInstaller path mismatch (hyphen to underscore in src dirs)
- Tauri build: fixed TypeScript errors (unused imports, useRef arg, import.meta.env)
- Tauri CORS: allow_origins includes tauri://localhost for WebView access

### Added
- CUA-NSIS: just cua-nsis-test recipe, smoke script, config
- CUA-NSIS: build.ps1 now copies NSIS installer to dist/
- CUA-NSIS: 11-phase smoke test (install, launch, WebView OCR, diagnostics, uninstall)
- CUA-NSIS: local certification — all 11 phases pass locally (2026-06-14)

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


