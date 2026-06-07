set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]

# ── Dashboard ─────────────────────────────────────────────────────────────────

# Open the interactive recipe dashboard in the browser
default:
    @just --list

# ── Quality ───────────────────────────────────────────────────────────────────

# Execute Ruff SOTA v13.1 linting
lint:
    Set-Location '{{justfile_directory()}}'
    uv run ruff check .
    Set-Location '{{justfile_directory()}}\webapp'
    npx @biomejs/biome ci .

# Execute Ruff SOTA v13.1 fix and formatting
fix:
    Set-Location '{{justfile_directory()}}'
    uv run ruff check . --fix --unsafe-fixes
    uv run ruff format .
    Set-Location '{{justfile_directory()}}\webapp'
    npx @biomejs/biome check --write .

# ── Hardening ─────────────────────────────────────────────────────────────────

# Execute Bandit security audit
check-sec:
    Set-Location '{{justfile_directory()}}'
    uv run bandit -r src/

# Execute safety audit of dependencies
audit-deps:
    Set-Location '{{justfile_directory()}}'
    uv run safety check

# LeWM-MCP — just recipes (Windows + uv)

set shell := ["powershell", "-NoProfile", "-Command"]

fmt:
    uv run ruff format src tests

test:
    uv run pytest tests -q

e2e:
    pwsh -NoLogo -NoProfile -ExecutionPolicy Bypass -File "D:\Dev\repos\mcp-central-docs\scripts\playwright-audit.ps1" -RepoPath "{{justfile_directory()}}"

# Full stack (canonical)
start dev web:
    Set-Location "{{justfile_directory()}}\webapp"
    .\start.ps1

bootstrap-upstream:
    pwsh -NoLogo -NoProfile -ExecutionPolicy Bypass -File "{{justfile_directory()}}\tools\bootstrap_upstream.ps1"

dev-api:
    uv run uvicorn lewm_mcp.server:app --host 127.0.0.1 --port 10927 --reload

dev-web:
    Set-Location webapp; npm run dev -- --port 10928 --host 127.0.0.1

