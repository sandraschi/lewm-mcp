"""Environment configuration for LeWM-MCP."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path


def _i(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return int(raw)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _discover_upstream_root() -> Path | None:
    explicit = os.getenv("LEWM_UPSTREAM_ROOT", "").strip()
    if explicit:
        p = Path(explicit).expanduser()
        if p.is_dir():
            return p.resolve()

    candidates = [
        _repo_root().parent / "external" / "le-wm",
        Path("D:/Dev/repos/external/le-wm"),
    ]
    for c in candidates:
        if c.is_dir() and (c / "train.py").is_file():
            return c.resolve()
    return None


def _discover_upstream_python(root: Path | None) -> Path | None:
    if root is None:
        return None
    if sys.platform == "win32":
        py = root / ".venv" / "Scripts" / "python.exe"
    else:
        py = root / ".venv" / "bin" / "python"
    return py if py.is_file() else None


@dataclass(frozen=True)
class LeWMConfig:
    """Runtime configuration (train/infer upstream + HTTP)."""

    upstream_root: str | None
    upstream_python: str | None
    stablewm_home: str | None
    checkpoint_path: str | None
    device: str
    default_data: str
    default_eval_config: str
    default_policy: str
    api_port: int
    frontend_port: int
    mcp_http_path: str
    single_gpu_lock: bool
    dry_run: bool

    @classmethod
    def from_env(cls) -> LeWMConfig:
        root = _discover_upstream_root()
        root_str = str(root) if root else None
        py = _discover_upstream_python(root)
        py_str = str(py) if py else (os.getenv("LEWM_UPSTREAM_PYTHON") or None)

        stablewm = os.getenv("LEWM_STABLEWM_HOME") or os.getenv("STABLEWM_HOME")
        if not stablewm and root:
            stablewm = str(root / ".stable-wm")

        return cls(
            upstream_root=root_str,
            upstream_python=py_str,
            stablewm_home=stablewm,
            checkpoint_path=os.getenv("LEWM_CHECKPOINT") or None,
            device=os.getenv("LEWM_DEVICE", "cuda:0"),
            default_data=os.getenv("LEWM_DEFAULT_DATA", "pusht"),
            default_eval_config=os.getenv("LEWM_DEFAULT_EVAL_CONFIG", "pusht.yaml"),
            default_policy=os.getenv("LEWM_DEFAULT_POLICY", "pusht/lewm"),
            api_port=_i("LEWM_API_PORT", 10927),
            frontend_port=_i("LEWM_FRONTEND_PORT", 10928),
            mcp_http_path=os.getenv("MCP_PATH", "/mcp"),
            single_gpu_lock=os.getenv("LEWM_SINGLE_GPU_LOCK", "1") == "1",
            dry_run=os.getenv("LEWM_DRY_RUN", "0") == "1",
        )


def get_config() -> LeWMConfig:
    return LeWMConfig.from_env()
