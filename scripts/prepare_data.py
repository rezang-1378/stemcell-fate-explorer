from __future__ import annotations

import argparse
import json
import platform
import sys
from pathlib import Path

import numpy as np
import pandas as pd


MARKER_GENES = [
    "CD34", "KIT", "GATA1", "GATA2", "KLF1", "TAL1",
    "SPI1", "MPO", "IRF8", "CEBPA", "RUNX1", "ELANE",
]


def dense(a):
    if hasattr(a, "toarray"):
        return a.toarray()
    return np.asarray(a)


def parse_args():
    p = argparse.ArgumentParser(description="Prepare CellRank hematopoiesis outputs for the dashboard.")
    p.add_argument("--raw-dir", default="data/raw")
    p.add_argument("--out-dir", default="data/processed")
    p.add_argument("--n-terminal", type=int, default=6)
    p.add_argument("--top-drivers", type=int, default=100)
    return p.parse_args()


def main():
    args = parse_args()

    import anndata
    import cellrank as cr
    import scanpy as sc

    raw_dir = Path(args.raw_dir)
    out_dir = Path(args.out_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    raw_path = raw_dir / "bone_marrow.h5ad"
    print("[1/7] Loading public CellRank human bone-marrow dataset...")
    adata = cr.datasets.bone_marrow(path=raw_path)
    adata.var_names_make_unique()

    print("[2/7] Scanpy preprocessing...")
    sc.pp.filter_genes(adata, min_cells=5)
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)
    sc.pp.highly_variable_genes(adata, n_top_genes=3000)
    sc.tl.pca(adata, random_state=0)
    sc.pp.neighbors(adata, random_state=0)
    sc.tl.umap(adata, random_state=0)

    print("[3/7] Building CellRank pseudotime transition kernel...")
    pk = cr.kernels.PseudotimeKernel(adata, time_key="palantir_pseudotime")
    pk.compute_transition_matrix()

    print("[4/7] Inferring terminal states and fate probabilities with GPCCA...")
    estimator = cr.estimators.GPCCA(pk)
    estimator.compute_schur()

    # CellRank GPCCA requires macrostates before terminal-state prediction.
    # The official CellRank bone-marrow tutorial uses 10 macrostates
    # followed by selection of the 6 most stable terminal states.
    estimator.compute_macrostates(n_states=10, cluster_key="clusters")
    estimator.predict_terminal_states(method="top_n", n_states=args.n_terminal)
    estimator.compute_fate_probabilities(use_petsc=False)

    fprob = estimator.fate_probabilities
    fate_names = [str(x) for x in fprob.names]
    fate_df = pd.DataFrame(fprob.X, index=adata.obs_names, columns=fate_names)
    fate_df.index.name = "cell_id"
    fate_df.to_parquet(out_dir / "fate_probabilities.parquet")

    print("[5/7] Computing putative lineage driver genes...")
    driver_frames = []
    for lineage in fate_names:
        d = estimator.compute_lineage_drivers(lineages=lineage).copy()
        corr = f"{lineage}_corr"
        pval = f"{lineage}_pval"
        qval = f"{lineage}_qval"
        ci_low = f"{lineage}_ci_low"
        ci_high = f"{lineage}_ci_high"
        keep = [c for c in [corr, pval, qval, ci_low, ci_high] if c in d.columns]
        d = d[keep].sort_values(corr, ascending=False).head(args.top_drivers)
        d = d.reset_index().rename(columns={d.index.name or "index": "gene"})
        if "gene" not in d.columns:
            d = d.rename(columns={d.columns[0]: "gene"})
        d.insert(1, "lineage", lineage)
        d = d.rename(columns={
            corr: "correlation", pval: "p_value", qval: "q_value",
            ci_low: "ci_low", ci_high: "ci_high",
        })
        driver_frames.append(d)
    pd.concat(driver_frames, ignore_index=True).to_csv(out_dir / "driver_genes.csv", index=False)

    print("[6/7] Exporting dashboard cell atlas and marker expression...")
    cells = pd.DataFrame(index=adata.obs_names)
    cells.index.name = "cell_id"
    cells["cluster"] = adata.obs["clusters"].astype(str).values
    cells["pseudotime"] = pd.to_numeric(adata.obs["palantir_pseudotime"], errors="coerce").values
    if "palantir_diff_potential" in adata.obs:
        cells["differentiation_potential"] = pd.to_numeric(
            adata.obs["palantir_diff_potential"], errors="coerce"
        ).values
    cells["umap_1"] = adata.obsm["X_umap"][:, 0]
    cells["umap_2"] = adata.obsm["X_umap"][:, 1]
    if "X_tsne" in adata.obsm:
        cells["tsne_1"] = adata.obsm["X_tsne"][:, 0]
        cells["tsne_2"] = adata.obsm["X_tsne"][:, 1]
    cells.to_parquet(out_dir / "dashboard_cells.parquet")

    present_markers = [g for g in MARKER_GENES if g in adata.var_names]
    marker_matrix = dense(adata[:, present_markers].X)
    marker_df = pd.DataFrame(marker_matrix, index=adata.obs_names, columns=present_markers)
    marker_df.index.name = "cell_id"
    marker_df.to_parquet(out_dir / "marker_expression.parquet")

    print("[7/7] Writing run metadata...")
    meta = {
        "project": "StemCell Fate Explorer",
        "dataset": "CellRank early human hematopoiesis (CD34+ bone marrow)",
        "n_cells": int(adata.n_obs),
        "n_genes_after_filtering": int(adata.n_vars),
        "n_terminal_states": len(fate_names),
        "terminal_states": fate_names,
        "marker_genes": present_markers,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "cellrank": getattr(cr, "__version__", "unknown"),
        "scanpy": getattr(sc, "__version__", "unknown"),
        "anndata": getattr(anndata, "__version__", "unknown"),
        "kernel": "PseudotimeKernel",
        "time_key": "palantir_pseudotime",
        "gpcca_terminal_method": "top_n",
    }
    (out_dir / "project_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print("Done. Run: streamlit run app.py")


if __name__ == "__main__":
    main()
