# Research paper

## Citation

**LeWorldModel: Stable End-to-End Joint-Embedding Predictive Architecture from Pixels**

Maes, Le Lidec, Scieur, LeCun, Balestriero — arXiv **[2603.19312](https://arxiv.org/abs/2603.19312)** (v3, 2026).

- PDF: https://arxiv.org/pdf/2603.19312
- Project site: https://le-wm.github.io/
- Upstream code: https://github.com/lucas-maes/le-wm

## Fleet reading (arxiv-mcp)

Repos based on a paper should ingest it into the **arxiv-mcp** local depot so agents and users can search full text.

```powershell
.\tools\ingest_lewm_paper.ps1
```

Then query via arxiv-mcp:

- Tool: `search_depot_corpus` with query about LeWM / JEPA / planning
- Paper id: `2603.19312`

## Why this paper

- Compact world model (~15M params), single-GPU training
- Stable JEPA from pixels with minimal loss set
- Planning and surprise evaluation in latent space
- LeCun co-author — joint-embedding predictive architecture line

## Dashboard links

The glass UI links to arXiv abs + notes that full text is in arxiv-mcp after ingest.
