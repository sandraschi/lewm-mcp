# Upstream integration (lucas-maes/le-wm)

## Layout

| Path | Role |
|------|------|
| `D:\Dev\repos\external\le-wm` | Upstream clone (auto-discovered) |
| `external/le-wm/.venv` | Python 3.10 — **train/eval run here** |
| `external/le-wm/.stable-wm` | `STABLEWM_HOME` — checkpoints + datasets |

## Bootstrap

`tools/bootstrap_upstream.ps1`:

1. Clone or update `https://github.com/lucas-maes/le-wm`
2. `uv venv` with Python 3.10
3. `pip install -e ".[train,env]"` (stable-worldmodel)

## Job runner

`src/lewm_mcp/engine/runner.py` builds commands:

- **Train:** `{upstream_python} train.py data={env}`
- **Eval:** `{upstream_python} eval.py --config-name=pusht.yaml policy={policy}`

Jobs are supervised by `engine/jobs.py` with logs in `lewm-mcp/logs/`.

## Checkpoints

Eval expects `STABLEWM_HOME/pusht/lewm_object.ckpt` for policy `pusht/lewm`.

Obtain via:

```powershell
.\tools\download_pusht_assets.ps1
```

HF hub `quentinll/lewm-pusht` → `convert_hf_pusht_ckpt.py` remaps legacy ViT keys to current `vit_hf` layout.

## Datasets

| File | Source | Size |
|------|--------|------|
| `pusht_expert_train.h5` | HF dataset `quentinll/lewm-pusht` | ~13 GB compressed |

Required for `eval.py` on PushT.

## Version coupling

Upstream pins `stable-worldmodel` and `stable-pretraining`. If HF convert fails after upstream upgrade, check transformers ViT key layout or use prebuilt checkpoints from the upstream README (Google Drive).

## Do not

- Run train/eval from lewm-mcp's Python 3.12 venv — always subprocess upstream 3.10 venv
- Claim metrics without real eval logs
