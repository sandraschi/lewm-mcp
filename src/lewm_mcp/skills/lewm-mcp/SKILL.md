# LeWM-MCP — Agent skill

**Description:** LeWorldModel (LeWM) MCP bridge. Spawns real `train.py` / `eval.py` jobs in upstream `lucas-maes/le-wm` Python 3.10 venv.

## Trigger Phrases

- "Train LeWM on PushT"
- "Run world model MPC eval"
- "List LeWM checkpoints"
- "Check LeWM job status"

## Tools

- `lewm_world(operation="health")` — upstream path, venv, STABLEWM_HOME, active job
- `lewm_world(operation="train_prepare")` — validate before training
- `lewm_world(operation="train_run", data_env="pusht")` — spawn `train.py` subprocess
- `lewm_world(operation="infer_prepare", policy="pusht/lewm")` — check policy checkpoint
- `lewm_world(operation="eval_run", policy="pusht/lewm")` — spawn `eval.py` MPC planning
- `lewm_world(operation="rollout")` — alias for eval_run
- `lewm_world(operation="checkpoint_list")` — glob STABLEWM_HOME checkpoints
- `lewm_world(operation="job_status")` — active + recent jobs
- `lewm_world(operation="job_stop")` — terminate running job
- `lewm_world(operation="job_logs", job_id="...")` — tail job log
- `lewm_agentic_workflow(goal="...")` — multi-step plan with sampling fallback

## Constraints

- Upstream at `LEWM_UPSTREAM_ROOT` (default `D:\Dev\repos\external\le-wm`)
- Bootstrap: `tools/bootstrap_upstream.ps1` (Python 3.10 + stable-worldmodel)
- Datasets: HF collection `quentinll/lewm` → `$STABLEWM_HOME/*.h5`
- **One GPU job at a time** when `LEWM_SINGLE_GPU_LOCK=1`
- Paper: arXiv **2603.19312** — MCP is a subprocess bridge, not a reimplementation

## Workflow

1. `health` — confirm upstream + venv
2. `checkpoint_list` — see available policies
3. Train: `train_prepare` → `train_run` → `job_status`
4. Plan: `infer_prepare` → `eval_run` → `job_status`
