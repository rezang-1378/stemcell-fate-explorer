# StemCell Fate Explorer

**Interactive single-cell fate mapping of early human hematopoiesis**  
A portfolio project for regenerative medicine / stem-cell bioinformatics.

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue)](https://www.python.org/)
[![CellRank](https://img.shields.io/badge/CellRank-2.3.2-5B4B8A)](https://cellrank.readthedocs.io/)
[![Scanpy](https://img.shields.io/badge/Scanpy-1.12.4-2E7D32)](https://scanpy.readthedocs.io/)
[![Streamlit](https://img.shields.io/badge/Streamlit-dashboard-FF4B4B)](https://streamlit.io/)

## Why this project?

Stem-cell and regenerative-medicine teams increasingly need reproducible workflows that connect single-cell transcriptomes with **cell-state transitions, differentiation potential, terminal fates, and candidate driver genes**. This project turns a validated public single-cell dataset into an interactive research dashboard.

The scientific demo uses the **CellRank early human hematopoiesis dataset** (CD34+ human bone-marrow cells, 10x Chromium; 5,780 cells × 27,876 genes) with precomputed Palantir pseudotime. The analysis follows the CellRank pseudotime workflow and uses a `PseudotimeKernel` plus `GPCCA` for terminal-state detection and fate probabilities.

## Portfolio story

This repository demonstrates that I can:

- work with real scRNA-seq data in `AnnData`;
- preprocess and visualize single-cell transcriptomes with Scanpy;
- model directional cell-state transitions with CellRank;
- estimate terminal states and cell fate probabilities;
- identify putative lineage-associated driver genes;
- separate a heavy analysis layer from a lightweight dashboard layer;
- build a reproducible, deployment-friendly scientific application.

## Dashboard

The Streamlit app contains six views:

1. **Overview** — dataset and analysis summary.
2. **Cell Atlas** — interactive UMAP/t-SNE colored by cell type or pseudotime.
3. **Fate Map** — cell-level probabilities of reaching inferred terminal states.
4. **Driver Genes** — top genes correlated with each terminal fate.
5. **Gene Explorer** — expression of curated hematopoietic markers across cells and pseudotime.
6. **Methods** — transparent workflow, limitations, and references.

## Architecture

```text
CellRank public human bone-marrow dataset
                 │
                 ▼
       Scanpy preprocessing
  filter → normalize → log1p → PCA → kNN → UMAP
                 │
                 ▼
      CellRank PseudotimeKernel
                 │
                 ▼
        GPCCA terminal states
                 │
        ┌────────┴────────┐
        ▼                 ▼
 fate probabilities   lineage drivers
        │                 │
        └────────┬────────┘
                 ▼
      portable parquet outputs
                 │
                 ▼
       Streamlit / Plotly UI
```

## Quick start

### 1) Analysis environment

CellRank 2.3.x requires Python 3.12+. On Windows, WSL/Linux is recommended for the analysis environment.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-analysis.txt
python scripts/prepare_data.py
```

The first analysis run downloads the public CellRank dataset and writes lightweight processed files under `data/processed/`.

### 2) Run the dashboard

```bash
pip install -r requirements.txt
streamlit run app.py
```

The dashboard intentionally does **not** recompute CellRank on every page load. Scientific analysis is run once and exported to portable files; the web app only reads those outputs.

## Reproducibility

Pinned reference versions for this portfolio build:

- CellRank `2.3.2`
- Scanpy `1.12.4`
- Python `>=3.12,<3.15`

The pipeline records package versions and key run parameters in `data/processed/project_meta.json`.

## Data policy

The large public `.h5ad` source file and processed binary artifacts are intentionally excluded from Git. They are downloaded/generated locally by `scripts/prepare_data.py`. This keeps the repository lightweight and avoids redistributing third-party data unnecessarily.

## Scientific interpretation

Fate probabilities are model-derived probabilities under the chosen Markov-chain representation of cellular dynamics. Driver genes are **putative lineage-associated genes** identified by correlation with fate probabilities; they are not automatically causal regulators and require biological validation.

## References

- CellRank documentation: https://cellrank.readthedocs.io/
- CellRank human bone-marrow getting-started tutorial: https://cellrank.readthedocs.io/en/stable/notebooks/tutorials/general/100_getting_started.html
- Setty et al. (2019), *Nature Biotechnology*: Palantir characterization of human hematopoiesis.
- Lange et al. (2022), *Nature Methods*: CellRank fate mapping.

## Author

**Reza Negahban**  
Bioinformatics / Computational Biology portfolio project.

## License

Code is released under the MIT License. Dataset and upstream software retain their original licenses/citations.
