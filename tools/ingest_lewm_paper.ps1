# Ingest arXiv:2603.19312 into arxiv-mcp local depot for fleet reading.
$ErrorActionPreference = "Stop"
$ArxivRepo = Resolve-Path (Join-Path $PSScriptRoot "..\..\arxiv-mcp")
$PaperId = "2603.19312"

Write-Host "arxiv-mcp: ingesting $PaperId (LeWorldModel paper)" -ForegroundColor Cyan

if (-not (Test-Path $ArxivRepo)) {
    Write-Host "arxiv-mcp repo not found at $ArxivRepo" -ForegroundColor Red
    exit 1
}

Set-Location $ArxivRepo
$Uv = if ($env:UV_EXE) { $env:UV_EXE } else { "uv" }
& $Uv sync
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& $Uv run python -c @"
import asyncio, json
from arxiv_mcp.depot_service import ingest_and_analyze_paper

async def main():
    result = await ingest_and_analyze_paper('$PaperId', deep=True)
    print(json.dumps({k: result.get(k) for k in ('success','arxiv_id','title','message','chunk_count') if k in result or result.get(k) is not None}, indent=2, default=str))
    if not result.get('success'):
        raise SystemExit(1)

asyncio.run(main())
"@

if ($LASTEXITCODE -eq 0) {
    Write-Host "Paper ingested. Search via arxiv-mcp search_depot_corpus or MCP ingest tools." -ForegroundColor Green
}
