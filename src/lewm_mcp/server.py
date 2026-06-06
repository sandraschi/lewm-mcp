"""LeWM-MCP — FastMCP server (train/infer bridge, agentic prep, web dashboard)."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import structlog
from fastapi import FastAPI
from fastmcp import Context, FastMCP

from .engine.runner import UpstreamRunner
from .web import setup_webapp

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

INSTRUCTIONS = (
    "You are LeWM-MCP: bridge to LeWorldModel (LeWM), JEPA world model arXiv:2603.19312. "
    "Use lewm_world for health, train_prepare, train_run, infer_prepare, eval_run, rollout, "
    "checkpoint_list, job_status, job_stop, job_logs. Upstream: lucas-maes/le-wm at "
    "LEWM_UPSTREAM_ROOT (default D:\\Dev\\repos\\external\\le-wm). Training runs train.py; "
    "planning runs eval.py in upstream Python 3.10 venv."
)


def build_mcp() -> FastMCP:
    mcp = FastMCP(
        "lewm-mcp",
        version="0.2.1",
        instructions=INSTRUCTIONS,
    )

    @mcp.tool()
    async def lewm_world(
        operation: str,
        extra_args: str | None = None,
        data_env: str | None = None,
        eval_config: str | None = None,
        policy: str | None = None,
        job_id: str | None = None,
        tail: int = 40,
    ) -> dict[str, Any]:
        """LEWM_WORLD — Portmanteau for upstream health, training, eval, and job control.

        Args:
            operation: health | status | train_prepare | train_run | infer_prepare |
                eval_run | rollout | checkpoint_list | job_status | job_stop | job_logs |
                surprise_stub
            extra_args: Hydra overrides (e.g. "trainer.max_epochs=2 loader.batch_size=32")
            data_env: Train dataset key: pusht | tworoom | dmc | ogb
            eval_config: Eval Hydra config file (e.g. pusht.yaml)
            policy: Policy path relative to STABLEWM_HOME without _object.ckpt (e.g. pusht/lewm)
            job_id: Job id for job_status / job_logs
            tail: Log lines to return for job_status / job_logs

        Returns:
            Structured dict with success, result fields, and recovery hints.
        """
        runner = UpstreamRunner.default()
        op = (operation or "").strip().lower()

        if op in ("health", "status"):
            h = runner.health()
            return {"success": True, "result": h, "message": "Upstream and job status."}
        if op == "train_prepare":
            return runner.train_prepare(extra_args=extra_args)
        if op == "train_run":
            return runner.train_run(data_env=data_env, extra_args=extra_args)
        if op in ("infer_prepare", "rollout_prepare"):
            return runner.infer_prepare(policy=policy)
        if op in ("eval_run", "rollout"):
            return runner.eval_run(eval_config=eval_config, policy=policy, extra_args=extra_args)
        if op == "checkpoint_list":
            return runner.checkpoint_list()
        if op == "job_status":
            return runner.job_status(job_id=job_id, tail=tail)
        if op == "job_stop":
            return runner.job_stop()
        if op == "job_logs":
            if not job_id:
                return {"success": False, "error": "job_id required for job_logs"}
            return runner.job_logs(job_id=job_id, tail=tail)
        if op == "surprise_stub":
            h = runner.health()
            return {
                "success": True,
                "message": "Use eval_run with a physically implausible scenario upstream; "
                "surprise scoring lives in stable-worldmodel eval hooks.",
                "upstream": h,
            }

        return {
            "success": False,
            "error": f"Unknown operation: {operation}",
            "recovery_options": [
                "health",
                "train_prepare",
                "train_run",
                "infer_prepare",
                "eval_run",
                "checkpoint_list",
                "job_status",
            ],
        }

    @mcp.tool()
    async def lewm_status() -> dict[str, Any]:
        """LEWM_STATUS — Snapshot of environment, upstream venv, and active jobs."""
        runner = UpstreamRunner.default()
        return {"success": True, "result": runner.health()}

    @mcp.tool()
    async def lewm_agentic_workflow(
        ctx: Context,
        goal: str,
        max_steps: int = 8,
    ) -> dict[str, Any]:
        """LEWM_AGENTIC_WORKFLOW — Multi-step LeWM session planning (SEP-1577 friendly)."""
        fallback_steps = [
            "lewm_world(operation='health')",
            "lewm_world(operation='checkpoint_list')",
            "lewm_world(operation='train_prepare') then train_run OR eval_run",
            "lewm_world(operation='job_status') to monitor GPU job",
        ]
        sample_ok = hasattr(ctx, "sample") or hasattr(ctx, "sample_step")
        plan: str | None = None
        if sample_ok:
            try:
                prompt = (
                    f"Goal: {goal}\nProduce a concise numbered plan (max {max_steps} steps) "
                    "for LeWM using lewm_world train_run / eval_run. No markdown fences."
                )
                if hasattr(ctx, "sample"):
                    sample_fn = ctx.sample
                    out = await sample_fn(prompt)  # type: ignore[misc]
                    plan = getattr(out, "text", None) or str(out)
            except Exception as e:
                logger.warning("agentic_sample_failed", error=str(e))
                plan = None
        return {
            "success": True,
            "goal": goal,
            "sampling_available": bool(sample_ok),
            "plan": plan,
            "fallback_steps": fallback_steps,
            "message": plan or "Use fallback_steps when sampling is unavailable.",
        }

    @mcp.prompt("prompt://lewm/session")
    def lewm_session_prompt() -> str:
        """Prompt template for LeWM + agent sessions."""
        return """Session: LeWorldModel (LeWM) via MCP.
1) lewm_world(operation='health')
2) Training: train_prepare → train_run(data_env='pusht') → job_status
3) Planning: infer_prepare → eval_run(policy='pusht/lewm') → job_status
4) Checkpoints: checkpoint_list
Paper: arXiv:2603.19312 · upstream: lucas-maes/le-wm"""

    _add_skills_provider(mcp)

    return mcp


def _add_skills_provider(mcp: FastMCP) -> None:
    try:
        from fastmcp.server.providers.skills import SkillsDirectoryProvider
    except ImportError:
        return
    roots = Path(__file__).resolve().parent / "skills"
    if not roots.is_dir():
        return
    try:
        mcp.add_provider(SkillsDirectoryProvider(roots=roots))
    except Exception as e:
        logger.warning("skills_provider_skipped", error=str(e))


mcp = build_mcp()

_mcp_http = mcp.http_app(path="/")
app = FastAPI(title="LeWM-MCP", lifespan=_mcp_http.lifespan)
setup_webapp(app, mcp)
app.mount("/mcp", _mcp_http)


def main() -> None:
    from .transport import run_server

    run_server(mcp, server_name="lewm-mcp")


if __name__ == "__main__":
    main()
