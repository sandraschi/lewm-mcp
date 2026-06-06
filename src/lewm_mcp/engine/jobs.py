"""Supervised upstream train/eval subprocess jobs."""

from __future__ import annotations

import os
import subprocess
import threading
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_lock = threading.Lock()
_jobs: dict[str, JobRecord] = {}


def logs_dir() -> Path:
    root = Path(__file__).resolve().parents[3]
    d = root / "logs"
    d.mkdir(parents=True, exist_ok=True)
    return d


@dataclass
class JobRecord:
    job_id: str
    kind: str
    command: list[str]
    cwd: str
    log_path: str
    started_at_ms: int
    proc: subprocess.Popen[str] | None = None
    finished_at_ms: int | None = None
    exit_code: int | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def status(self) -> str:
        if self.proc is None:
            return "stopped"
        code = self.proc.poll()
        if code is None:
            return "running"
        return "completed" if code == 0 else "failed"

    def to_dict(self, *, tail_log: int = 0) -> dict[str, Any]:
        running = self.proc is not None and self.proc.poll() is None
        payload: dict[str, Any] = {
            "job_id": self.job_id,
            "kind": self.kind,
            "status": self.status,
            "running": running,
            "pid": self.proc.pid if self.proc else None,
            "exit_code": self.exit_code if self.exit_code is not None else (self.proc.poll() if self.proc else None),
            "command": self.command,
            "cwd": self.cwd,
            "log_path": self.log_path,
            "started_at_ms": self.started_at_ms,
            "finished_at_ms": self.finished_at_ms,
            **self.extra,
        }
        if tail_log > 0:
            payload["log_tail"] = tail_log_lines(self.log_path, tail_log)
        return payload


def tail_log_lines(log_path: str, n: int) -> list[str]:
    p = Path(log_path)
    if not p.exists():
        return []
    try:
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        return lines[-max(1, n) :]
    except OSError:
        return []


def active_job() -> JobRecord | None:
    with _lock:
        for job in _jobs.values():
            if job.proc is not None and job.proc.poll() is None:
                return job
    return None


def list_jobs() -> list[dict[str, Any]]:
    with _lock:
        return [j.to_dict() for j in sorted(_jobs.values(), key=lambda x: x.started_at_ms, reverse=True)]


def get_job(job_id: str) -> JobRecord | None:
    with _lock:
        return _jobs.get(job_id)


def start_job(
    *,
    kind: str,
    command: list[str],
    cwd: str,
    extra: dict[str, Any] | None = None,
    env: dict[str, str] | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    with _lock:
        for job in _jobs.values():
            if job.proc is not None and job.proc.poll() is None:
                return {
                    "success": False,
                    "error": "Another LeWM job is already running",
                    "active_job_id": job.job_id,
                    "recovery": ["Wait for completion", "lewm_world(operation='job_stop')"],
                }

    job_id = f"{kind}-{int(time.time() * 1000)}-{uuid.uuid4().hex[:6]}"
    log_path = logs_dir() / f"{job_id}.log"

    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "job_id": job_id,
            "command": command,
            "cwd": cwd,
            "log_path": str(log_path),
        }

    log_fh = open(log_path, "a", encoding="utf-8", errors="replace")
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)

    proc = subprocess.Popen(  # noqa: S603
        command,
        cwd=cwd,
        env=merged_env,
        stdout=log_fh,
        stderr=log_fh,
        text=True,
        bufsize=1,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
    )

    record = JobRecord(
        job_id=job_id,
        kind=kind,
        command=command,
        cwd=cwd,
        log_path=str(log_path),
        started_at_ms=int(time.time() * 1000),
        proc=proc,
        extra=extra or {},
    )

    def _watch() -> None:
        code = proc.wait()
        with _lock:
            record.exit_code = code
            record.finished_at_ms = int(time.time() * 1000)

    threading.Thread(target=_watch, name=f"lewm-job-{job_id}", daemon=True).start()

    with _lock:
        _jobs[job_id] = record

    return {
        "success": True,
        "job_id": job_id,
        "pid": proc.pid,
        "log_path": str(log_path),
        "command": command,
    }


def stop_active_job() -> dict[str, Any]:
    with _lock:
        target: JobRecord | None = None
        for job in _jobs.values():
            if job.proc is not None and job.proc.poll() is None:
                target = job
                break
    if target is None or target.proc is None:
        return {"success": False, "error": "No running job"}
    target.proc.terminate()
    try:
        target.proc.wait(timeout=5)
    except Exception:
        target.proc.kill()
    with _lock:
        target.exit_code = target.proc.poll()
        target.finished_at_ms = int(time.time() * 1000)
    return {"success": True, "job_id": target.job_id, "exit_code": target.exit_code}
