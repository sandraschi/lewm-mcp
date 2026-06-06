"""Bridge to official LeWorldModel code (lucas-maes/le-wm)."""

from __future__ import annotations

import os
import shlex
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..config import LeWMConfig, get_config
from .jobs import active_job, get_job, list_jobs, start_job, stop_active_job, tail_log_lines

EVAL_CONFIGS = {
    "pusht": "pusht.yaml",
    "cube": "cube.yaml",
    "tworoom": "tworoom.yaml",
    "tworooms": "tworoom.yaml",
    "reacher": "reacher.yaml",
}

TRAIN_DATA = {"pusht", "tworoom", "dmc", "ogb"}


@dataclass
class UpstreamRunner:
    """Runs train.py / eval.py in the upstream Python 3.10 venv via subprocess."""

    config: LeWMConfig

    @classmethod
    def default(cls) -> UpstreamRunner:
        return cls(config=get_config())

    def upstream_resolved(self) -> Path | None:
        if not self.config.upstream_root:
            return None
        p = Path(self.config.upstream_root).expanduser().resolve()
        return p if p.is_dir() else None

    def upstream_python(self) -> Path | None:
        if self.config.upstream_python:
            p = Path(self.config.upstream_python).expanduser()
            if p.is_file():
                return p.resolve()
        root = self.upstream_resolved()
        if root is None:
            return None
        if sys.platform == "win32":
            p = root / ".venv" / "Scripts" / "python.exe"
        else:
            p = root / ".venv" / "bin" / "python"
        return p.resolve() if p.is_file() else None

    def stablewm_home(self) -> Path | None:
        if self.config.stablewm_home:
            return Path(self.config.stablewm_home).expanduser().resolve()
        root = self.upstream_resolved()
        return root / ".stable-wm" if root else None

    def subprocess_env(self) -> dict[str, str]:
        env: dict[str, str] = {}
        home = self.stablewm_home()
        if home:
            env["STABLEWM_HOME"] = str(home)
            env["LEWM_STABLEWM_HOME"] = str(home)
        if self.config.device:
            env["LEWM_DEVICE"] = self.config.device
            if self.config.device.startswith("cuda"):
                env["CUDA_VISIBLE_DEVICES"] = os.getenv("CUDA_VISIBLE_DEVICES", "0")
        if sys.platform == "win32":
            env["MUJOCO_GL"] = os.getenv("MUJOCO_GL", "glfw")
        return env

    def health(self) -> dict[str, Any]:
        root = self.upstream_resolved()
        py = self.upstream_python()
        home = self.stablewm_home()
        ck = self.config.checkpoint_path
        ck_ok = bool(ck and Path(ck).expanduser().is_file())

        policy_path = None
        policy_ok = False
        if home:
            policy_rel = self.config.default_policy
            candidate = home / f"{policy_rel}_object.ckpt"
            policy_path = str(candidate)
            policy_ok = candidate.is_file()

        job = active_job()
        return {
            "upstream_configured": root is not None,
            "upstream_path": str(root) if root else None,
            "upstream_python": str(py) if py else None,
            "upstream_python_ready": py is not None,
            "train_py": str(root / "train.py") if root else None,
            "eval_py": str(root / "eval.py") if root else None,
            "stablewm_home": str(home) if home else None,
            "stablewm_exists": home.is_dir() if home else False,
            "checkpoint_set": ck is not None,
            "checkpoint_exists": ck_ok,
            "default_policy": self.config.default_policy,
            "default_policy_path": policy_path,
            "default_policy_ready": policy_ok,
            "device": self.config.device,
            "dry_run": self.config.dry_run,
            "active_job": job.to_dict() if job else None,
            "arxiv": "2603.19312",
            "paper_title": ("LeWorldModel: Stable End-to-End Joint-Embedding Predictive Architecture from Pixels"),
            "reference_repo": "https://github.com/lucas-maes/le-wm",
            "bootstrap_hint": "Run tools/bootstrap_upstream.ps1 in lewm-mcp repo",
        }

    def _require_ready(self) -> tuple[Path, Path]:
        root = self.upstream_resolved()
        if not root:
            raise RuntimeError(
                "LEWM_UPSTREAM_ROOT not configured. Clone le-wm to D:\\Dev\\repos\\external\\le-wm "
                "or run tools/bootstrap_upstream.ps1"
            )
        py = self.upstream_python()
        if not py:
            raise RuntimeError(
                "Upstream venv missing. Run tools/bootstrap_upstream.ps1 to create Python 3.10 venv "
                "and install stable-worldmodel[train,env]."
            )
        return root, py

    def _split_hydra_args(self, extra_args: str | None) -> list[str]:
        if not extra_args or not extra_args.strip():
            return []
        if sys.platform == "win32":
            return shlex.split(extra_args, posix=False)
        return shlex.split(extra_args)

    def train_prepare(self, extra_args: str | None = None) -> dict[str, Any]:
        try:
            root, py = self._require_ready()
        except RuntimeError as exc:
            return {"success": False, "error": str(exc)}

        data = self.config.default_data
        for token in self._split_hydra_args(extra_args):
            if token.startswith("data="):
                data = token.split("=", 1)[1]

        home = self.stablewm_home()
        dataset_hint = f"{data} dataset under STABLEWM_HOME (see HF quentinll/lewm collection)"
        return {
            "success": True,
            "message": "Ready to launch upstream train.py",
            "upstream": str(root),
            "python": str(py),
            "stablewm_home": str(home) if home else None,
            "suggested_command": [str(py), "train.py", f"data={data}", *self._split_hydra_args(extra_args)],
            "dataset_hint": dataset_hint,
            "extra_args": extra_args,
        }

    def train_run(
        self,
        *,
        data_env: str | None = None,
        extra_args: str | None = None,
    ) -> dict[str, Any]:
        try:
            root, py = self._require_ready()
        except RuntimeError as exc:
            return {"success": False, "error": str(exc)}

        data = (data_env or self.config.default_data).strip()
        if data not in TRAIN_DATA:
            return {
                "success": False,
                "error": f"Unknown data env: {data}",
                "recovery": [f"Use one of: {sorted(TRAIN_DATA)}"],
            }

        overrides = self._split_hydra_args(extra_args)
        cmd = [str(py), "train.py", f"data={data}", *overrides]
        return start_job(
            kind="train",
            command=cmd,
            cwd=str(root),
            env=self.subprocess_env(),
            dry_run=self.config.dry_run,
            extra={"data": data, "extra_args": extra_args},
        )

    def infer_prepare(self, policy: str | None = None) -> dict[str, Any]:
        try:
            root, py = self._require_ready()
        except RuntimeError as exc:
            return {"success": False, "error": str(exc)}

        pol = (policy or self.config.default_policy).strip()
        home = self.stablewm_home()
        ck_path = home / f"{pol}_object.ckpt" if home else None
        ready = ck_path.is_file() if ck_path else False

        return {
            "success": True,
            "message": "Ready for eval.py MPC planning" if ready else "Policy checkpoint not found yet",
            "upstream": str(root),
            "python": str(py),
            "policy": pol,
            "policy_checkpoint": str(ck_path) if ck_path else None,
            "policy_ready": ready,
            "suggested_command": [
                str(py),
                "eval.py",
                f"--config-name={self._eval_config_for_policy(pol)}",
                f"policy={pol}",
            ],
            "recovery": [] if ready else ["Train or download HF checkpoint into STABLEWM_HOME"],
        }

    def _eval_config_for_policy(self, policy: str) -> str:
        env_key = policy.split("/")[0].lower()
        return EVAL_CONFIGS.get(env_key, self.config.default_eval_config)

    def eval_run(
        self,
        *,
        eval_config: str | None = None,
        policy: str | None = None,
        extra_args: str | None = None,
    ) -> dict[str, Any]:
        try:
            root, py = self._require_ready()
        except RuntimeError as exc:
            return {"success": False, "error": str(exc)}

        pol = (policy or self.config.default_policy).strip()
        cfg_name = (eval_config or self._eval_config_for_policy(pol)).strip()
        if not cfg_name.endswith(".yaml"):
            cfg_name = f"{cfg_name}.yaml"

        overrides = self._split_hydra_args(extra_args)
        cmd = [str(py), "eval.py", f"--config-name={cfg_name}", f"policy={pol}", *overrides]
        return start_job(
            kind="eval",
            command=cmd,
            cwd=str(root),
            env=self.subprocess_env(),
            dry_run=self.config.dry_run,
            extra={"eval_config": cfg_name, "policy": pol, "extra_args": extra_args},
        )

    def checkpoint_list(self) -> dict[str, Any]:
        home = self.stablewm_home()
        if not home or not home.is_dir():
            return {
                "success": False,
                "error": "STABLEWM_HOME not configured or missing",
                "stablewm_home": str(home) if home else None,
            }

        patterns = ("**/*_object.ckpt", "**/weights_epoch_*.pt", "**/lewm_weights.ckpt")
        found: list[dict[str, Any]] = []
        for pattern in patterns:
            for p in home.glob(pattern):
                try:
                    rel = p.relative_to(home).as_posix()
                except ValueError:
                    rel = str(p)
                found.append(
                    {
                        "path": str(p),
                        "relative": rel,
                        "size_bytes": p.stat().st_size,
                        "kind": "object" if p.name.endswith("_object.ckpt") else "weights",
                    }
                )

        found.sort(key=lambda x: x["relative"])
        return {
            "success": True,
            "stablewm_home": str(home),
            "count": len(found),
            "checkpoints": found,
        }

    def job_status(self, job_id: str | None = None, tail: int = 40) -> dict[str, Any]:
        if job_id:
            job = get_job(job_id)
            if not job:
                return {"success": False, "error": f"Unknown job_id: {job_id}"}
            return {"success": True, "job": job.to_dict(tail_log=tail)}

        active = active_job()
        return {
            "success": True,
            "active_job": active.to_dict(tail_log=tail) if active else None,
            "jobs": list_jobs(),
        }

    def job_stop(self) -> dict[str, Any]:
        return stop_active_job()

    def job_logs(self, job_id: str, tail: int = 200) -> dict[str, Any]:
        job = get_job(job_id)
        if not job:
            return {"success": False, "error": f"Unknown job_id: {job_id}"}
        return {
            "success": True,
            "job_id": job_id,
            "log_path": job.log_path,
            "lines": tail_log_lines(job.log_path, tail),
        }

    # Back-compat aliases used by older MCP ops
    def train_stub(self, extra_args: str | None = None) -> dict[str, Any]:
        return self.train_prepare(extra_args=extra_args)

    def infer_stub(self, mode: str = "rollout") -> dict[str, Any]:
        prep = self.infer_prepare()
        prep["mode"] = mode
        return prep
