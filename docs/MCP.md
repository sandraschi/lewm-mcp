# MCP surface

**Server:** `lewm-mcp` · **FastMCP:** 3.2 · **Version:** 0.2.1

## Transports

| Mode | Command |
|------|---------|
| stdio (IDE) | `uv run python -m lewm_mcp` or `just mcp` |
| HTTP streamable | `http://127.0.0.1:10927/mcp` (colocated with FastAPI) |

## Tools

### `lewm_world` (portmanteau)

| Operation | Description |
|-----------|-------------|
| `health` | Upstream path, venv, checkpoint, device, active job |
| `train_prepare` | Checklist before training |
| `train_run` | Spawn upstream `train.py` (e.g. `data=pusht`) |
| `infer_prepare` | Checklist before inference/eval |
| `eval_run` | Spawn upstream `eval.py` with policy (default `pusht/lewm`) |
| `checkpoint_list` | Files under STABLEWM_HOME |
| `job_status` | Active/recent jobs + log tail |
| `job_stop` | Terminate supervised subprocess |
| `job_logs` | Tail job log file |

### `lewm_status`

Config snapshot: ports, upstream root, dry_run, single_gpu_lock.

### `lewm_agentic_workflow`

Multi-step planning when MCP sampling is available; fallback steps otherwise.

## Prompts & skills

- **Skill:** `skill://lewm-mcp/SKILL.md` (bundled under `src/lewm_mcp/skills/`)
- **AGENTS.md** at repo root for Cursor/agent constraints

## Dry run

Set `LEWM_DRY_RUN=1` to log commands without spawning GPU jobs (used in CI/tests).

## Fleet proxy

Optional access via **google-ai-mcp** `google_ai_world` at fleet port 11014.
