# lewm-mcp Agent Context

FastMCP 3.2 server for LeWorldModel (LeWM): JEPA train/infer, planning hooks, agentic prep, fleet webapp.

## Standards

- FastMCP 3.2+ portmanteau tool pattern — tools use `operation` enum param
- Responses: structured dicts with `success`, `message`, domain-specific fields
- Dual transport: stdio (Claude Desktop) + HTTP (`MCP_TRANSPORT=http`)
- See [mcp-central-docs](https://github.com/sandraschi/mcp-central-docs) for fleet-wide coding standards
- Install docs: mcp-central-docs/standards/AGENT_INSTALL_REFERENCE.md

## Quick Ref

```powershell
# Full start (backend + frontend) — fleet canonical
.\start.bat
# or: .\webapp\start.ps1

# Backend dev
uv run uvicorn lewm_mcp.server:app --host 127.0.0.1 --port 10927

# Run all tests
uv run pytest tests/ -q

# Lint
uv run ruff check src/ tests/

# E2E audit (headless)
npx playwright test --config webapp/playwright.config.ts
```

## Ports

| Service | Port |
|---|---|
| Backend (FastAPI + FastMCP HTTP) | 10927 |
| Frontend (Vite React) | 10928 |

## Architecture

```
src/lewm_mcp/
  server.py          — FastMCP 3.2 server, 3 MCP tools
  web.py             — FastAPI REST (/api/health, /api/status, /api/jobs/*)
  engine/runner.py   — UpstreamRunner (LeWM upstream bridge)
  config.py          — Configuration (LEWM_UPSTREAM_ROOT, LEWM_DEVICE)
  transport.py       — Server transport setup
  skills/            — Optional SkillsDirectoryProvider
webapp/              — React glass dashboard (Vite)
  e2e/               — Playwright E2E tests
tests/               — pytest (smoke + mcp + api tests)
native/              — Tauri 2.0 desktop wrapper
```

## MCP Tools

| Tool | Operations |
|---|---|
| `lewm_world` | health, train_prepare, train_run, infer_prepare, eval_run, rollout, checkpoint_list, job_* |
| `lewm_status` | Config snapshot, device, upstream health |
| `lewm_agentic_workflow` | Multi-step planning with optional LLM sampling |

## Configuration

Set via .env or environment:
```powershell
$env:LEWM_UPSTREAM_ROOT = "path\to\le-wm-clone"
$env:LEWM_DEVICE = "cuda"  # or "cpu"
```

Defaults: upstream auto-discovered at `D:\Dev\repos\external\le-wm`, STABLEWM_HOME = `{upstream}/.stable-wm`.

Bootstrap upstream: `tools/bootstrap_upstream.ps1` or `just bootstrap-upstream`.

## E2E Audit

```powershell
# Start both services, then:
npx playwright test --config webapp/playwright.config.ts

# Or via just:
just e2e
```

Runs: backend health check + frontend loads and renders #root.
