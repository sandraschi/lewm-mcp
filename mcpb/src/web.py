"""FastAPI routes for the LeWM glass dashboard."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastmcp import FastMCP
from pydantic import BaseModel

from .config import get_config
from .engine.runner import UpstreamRunner


class TrainJobRequest(BaseModel):
    data_env: str | None = None
    extra_args: str | None = None


class EvalJobRequest(BaseModel):
    eval_config: str | None = None
    policy: str | None = None
    extra_args: str | None = None


def setup_webapp(app: FastAPI, mcp: FastMCP) -> None:
    """Register REST endpoints used by the Vite frontend."""

    @app.get("/api/health")
    async def api_health() -> JSONResponse:
        """Fleet launcher probe — minimal OK when process is up."""
        return JSONResponse({"ok": True, "service": "lewm-mcp"})

    @app.get("/api/status")
    async def api_status() -> JSONResponse:
        cfg = get_config()
        runner = UpstreamRunner.default()
        h = runner.health()
        return JSONResponse(
            {
                "mcp_name": mcp.name,
                "mcp_version": mcp.version,
                "api_port": cfg.api_port,
                "frontend_port": cfg.frontend_port,
                **h,
            }
        )

    @app.get("/api/config")
    async def api_config() -> dict[str, Any]:
        c = get_config()
        return {
            "upstream_root": c.upstream_root,
            "upstream_python": c.upstream_python,
            "stablewm_home": c.stablewm_home,
            "device": c.device,
            "default_data": c.default_data,
            "default_policy": c.default_policy,
            "default_eval_config": c.default_eval_config,
            "single_gpu_lock": c.single_gpu_lock,
            "dry_run": c.dry_run,
            "arxiv": "2603.19312",
        }

    @app.get("/api/checkpoints")
    async def api_checkpoints() -> dict[str, Any]:
        return UpstreamRunner.default().checkpoint_list()

    @app.get("/api/jobs")
    async def api_jobs() -> dict[str, Any]:
        return UpstreamRunner.default().job_status()

    @app.get("/api/jobs/{job_id}")
    async def api_job_detail(job_id: str, tail: int = Query(default=80, ge=1, le=500)) -> dict[str, Any]:
        result = UpstreamRunner.default().job_status(job_id=job_id, tail=tail)
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error", "not found"))
        return result

    @app.post("/api/jobs/train")
    async def api_train_job(req: TrainJobRequest) -> dict[str, Any]:
        result = UpstreamRunner.default().train_run(data_env=req.data_env, extra_args=req.extra_args)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "train failed"))
        return {"ok": True, **result}

    @app.post("/api/jobs/eval")
    async def api_eval_job(req: EvalJobRequest) -> dict[str, Any]:
        result = UpstreamRunner.default().eval_run(
            eval_config=req.eval_config,
            policy=req.policy,
            extra_args=req.extra_args,
        )
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "eval failed"))
        return {"ok": True, **result}

    @app.post("/api/jobs/stop")
    async def api_job_stop() -> dict[str, Any]:
        return UpstreamRunner.default().job_stop()
