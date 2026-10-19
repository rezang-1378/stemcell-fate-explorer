# Data

The repository intentionally commits the lightweight processed outputs required by the dashboard. The large source dataset is excluded from Git.

| Location | Contents | Git handling |
| --- | --- | --- |
| `raw/` | Public CellRank `bone_marrow.h5ad`, downloaded when needed | Ignored |
| `processed/dashboard_cells.parquet` | Cell labels, embeddings, and pseudotime | Tracked |
| `processed/fate_probabilities.parquet` | Model-inferred terminal-fate probabilities | Tracked |
| `processed/driver_genes.csv` | Exported gene–fate associations | Tracked |
| `processed/marker_expression.parquet` | Selected marker-gene expression | Tracked |
| `processed/project_meta.json` | Recorded dimensions, terminal labels, and selected environment metadata | Tracked |

The source is CellRank's public early human hematopoiesis dataset, loaded through `cellrank.datasets.bone_marrow()`. Supplied Palantir pseudotime is reused; the preparation script does not calculate it anew.

After installing `requirements-analysis.txt`, regenerate from the repository root:

```bash
python scripts/prepare_data.py
```

This replaces files in `data/processed/`. For a separate comparison run, use an output directory outside the repository:

```bash
python scripts/prepare_data.py --out-dir /tmp/stemcell-fate-explorer-rerun
```

The app always reads `data/processed/`. Preserve the original outputs and run metadata when comparing analyses. The existing metadata does not constitute a complete environment lockfile or source-data checksum manifest.

Dataset terms and upstream attribution requirements remain separate from the repository's code license. Model outputs support exploration; they do not establish experimentally validated fates or causal regulators.
