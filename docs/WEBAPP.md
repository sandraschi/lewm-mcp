# Web application

## Ports (fleet)

| Service | Port |
|---------|------|
| FastAPI `/api/*` + MCP `/mcp` | **10927** |
| Vite dev server | **10928** |

Defined in `src/lewm_mcp/config.py`.

## Stack

- **Frontend:** React 18, Vite 5, glass dark UI (`webapp/src/App.tsx`)
- **Backend:** FastAPI via `lewm_mcp.server:app` (uvicorn)

## API routes

| Path | Purpose |
|------|---------|
| `GET /api/health` | Fleet launcher probe |
| `GET /api/status` | Full health + MCP metadata |
| `GET /api/config` | Paths, device, arxiv id |
| `GET /api/checkpoints` | STABLEWM_HOME artifacts |
| `GET /api/jobs` | Job list |
| `GET /api/jobs/{id}` | Job detail + log tail |
| `POST /api/jobs/train` | Start train subprocess |
| `POST /api/jobs/eval` | Start eval subprocess |
| `POST /api/jobs/stop` | Stop active job |

## Startup

```powershell
.\webapp\start.ps1
# or from repo root:
.\start.bat
```

Flags: `-BackendOnly`, `-Headless`, `-NoOpen` / `-NoBrowser`.

Launcher flow: `uv sync` → `tools/smoke_import.py` → clear ports → uvicorn → Vite → wait `/api/health`.

## E2E

```powershell
cd webapp
npx playwright test
```

See `webapp/e2e/fleet-audit.spec.ts`.
