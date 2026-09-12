from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.data_io import load_outputs, outputs_available


st.set_page_config(
    page_title="StemCell Fate Explorer",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      .block-container {padding-top: 1.5rem; padding-bottom: 3rem;}
      .hero {
        padding: 1.35rem 1.5rem; border-radius: 18px;
        background: linear-gradient(120deg, rgba(95,70,180,.16), rgba(0,150,136,.12));
        border: 1px solid rgba(140,140,160,.25); margin-bottom: 1.1rem;
      }
      .hero h1 {margin: 0 0 .25rem 0; font-size: 2.2rem;}
      .muted {opacity: .76;}
      div[data-testid="stMetric"] {border: 1px solid rgba(140,140,160,.18); padding: .7rem; border-radius: 14px;}
    </style>
    """,
    unsafe_allow_html=True,
)

BASE = Path(__file__).resolve().parent
PROCESSED = BASE / "data" / "processed"

st.markdown(
    """
    <div class="hero">
      <h1>🧬 StemCell Fate Explorer</h1>
      <div class="muted">Interactive single-cell fate mapping of early human hematopoiesis</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if not outputs_available(PROCESSED):
    st.warning("Processed scientific outputs are not present yet.")
    st.markdown(
        """
        This repository keeps large scientific data out of Git. Generate the real-data outputs once:

        ```bash
        pip install -r requirements-analysis.txt
        python scripts/prepare_data.py
        streamlit run app.py
        ```

        The preparation step downloads CellRank's public **human CD34+ bone-marrow** dataset and computes
        the cell atlas, terminal states, fate probabilities, and driver genes. The dashboard never fabricates
        scientific results if those outputs are missing.
        """
    )
    st.stop()


@st.cache_data(show_spinner=False)
def get_data():
    return load_outputs(PROCESSED)


cells, fates, drivers, expression, meta = get_data()

# Align indices robustly.
for df in (cells, fates, expression):
    if "cell_id" in df.columns:
        df.set_index("cell_id", inplace=True)
common = cells.index.intersection(fates.index).intersection(expression.index)
cells = cells.loc[common]
fates = fates.loc[common]
expression = expression.loc[common]

page = st.sidebar.radio(
    "Explore",
    [
        "Overview",
        "Cell Atlas",
        "Fate Map",
        "Putative Drivers",
        "Gene Explorer",
        "Biological Insights",
        "Methods",
    ],
)
st.sidebar.caption("Public scRNA-seq • Scanpy • CellRank • GPCCA")


def embedding_frame(embedding: str) -> tuple[pd.DataFrame, str, str]:
    if embedding == "t-SNE" and {"tsne_1", "tsne_2"}.issubset(cells.columns):
        return cells, "tsne_1", "tsne_2"
    return cells, "umap_1", "umap_2"


def scatter(df, x, y, color, title, continuous=False):
    kwargs = dict(data_frame=df, x=x, y=y, color=color, title=title, hover_name=df.index)
    if continuous:
        kwargs["color_continuous_scale"] = "Viridis"
    fig = px.scatter(**kwargs)
    fig.update_traces(marker={"size": 5, "opacity": 0.78})
    fig.update_layout(height=650, margin=dict(l=10, r=10, t=50, b=10), legend_title_text="")
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False, scaleanchor="x", scaleratio=1)
    return fig


if page == "Overview":
    st.subheader("Project snapshot")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Cells", f"{meta.get('n_cells', len(cells)):,}")
    c2.metric("Genes", f"{meta.get('n_genes_after_filtering', 0):,}")
    c3.metric("Cell states", cells["cluster"].nunique())
    c4.metric("Terminal fates", len(fates.columns))

    left, right = st.columns([1.35, 1])
    with left:
        fig = scatter(cells, "umap_1", "umap_2", "cluster", "Human hematopoietic cell atlas")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        counts = cells["cluster"].value_counts().rename_axis("cluster").reset_index(name="cells")
        fig2 = px.bar(counts, x="cells", y="cluster", orientation="h", title="Cell-state composition")
        fig2.update_layout(height=650, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown(
        """
        **Scientific question.** How do early human hematopoietic cells progress from progenitor states toward
        distinct mature fates, and which genes are most strongly associated with those fate decisions?

        The dashboard uses a directional Markov model driven by Palantir pseudotime. It is designed as a
        transparent research portfolio application rather than a clinical diagnostic tool.

        ### Data provenance

        **Dataset:** Public CellRank early human hematopoiesis dataset  
        **Biological material:** Human CD34+ bone-marrow cells  
        **Data type:** Single-cell RNA sequencing  
        **Cells analyzed:** 5,780  
        **Analysis:** Scanpy + CellRank + GPCCA  
        **Purpose:** Computational lineage-fate analysis and research portfolio demonstration  

        > This application is intended for research and educational use and is not a clinical decision-support system.
        """
    )

elif page == "Cell Atlas":
    st.subheader("Interactive cell atlas")
    c1, c2 = st.columns(2)
    embedding = c1.selectbox("Embedding", ["UMAP", "t-SNE"] if "tsne_1" in cells else ["UMAP"])
    color_mode = c2.selectbox("Color by", ["Cell state", "Pseudotime", "Differentiation potential"])
    _, x, y = embedding_frame(embedding)
    if color_mode == "Cell state":
        color, continuous = "cluster", False
    elif color_mode == "Pseudotime":
        color, continuous = "pseudotime", True
    else:
        color = "differentiation_potential" if "differentiation_potential" in cells else "pseudotime"
        continuous = True
    st.plotly_chart(scatter(cells, x, y, color, f"{embedding} • {color_mode}", continuous), use_container_width=True)

elif page == "Fate Map":
    st.subheader("Cell fate probabilities")

    st.markdown(
        """
        Each point represents one single cell. Color indicates the
        **CellRank-estimated probability** that the cell will reach the selected terminal fate.

        **Purple = low probability • Yellow = high probability**

        Terminal-fate names are inherited from the annotated cell-state structure
        and should not be interpreted as perfectly pure mature phenotypes.
        """
    )

    lineage = st.selectbox("Terminal fate", list(fates.columns))
    emb = st.radio("Embedding", ["UMAP", "t-SNE"] if "tsne_1" in cells else ["UMAP"], horizontal=True)
    _, x, y = embedding_frame(emb)
    df = cells.copy()
    df["fate_probability"] = fates[lineage]
    st.plotly_chart(
        scatter(df, x, y, "fate_probability", f"Probability of reaching {lineage}", True),
        use_container_width=True,
    )
    summary = (
        pd.DataFrame({"cluster": cells["cluster"], "prob": fates[lineage]})
        .groupby("cluster", observed=True)["prob"]
        .agg(["mean", "median", "count"])
        .sort_values("mean", ascending=False)
        .reset_index()
    )
    st.markdown("#### Fate bias by annotated cell state")
    st.dataframe(summary, use_container_width=True, hide_index=True)

elif page == "Putative Drivers":
    st.subheader("Putative lineage-associated driver genes")
    lineage = st.selectbox("Lineage", sorted(drivers["lineage"].dropna().unique()))
    n = st.slider("Top genes", 10, 60, 25, 5)
    d = drivers.loc[drivers["lineage"] == lineage].sort_values("correlation", ascending=False).head(n)
    fig = px.bar(d.sort_values("correlation"), x="correlation", y="gene", orientation="h", title=f"Top {lineage} associations")
    fig.update_layout(height=max(500, n * 24))
    st.plotly_chart(fig, use_container_width=True)
    display_d = d.copy()

    for col in ["p_value", "q_value"]:
        if col in display_d.columns:
            display_d[col] = display_d[col].map(
                lambda x: (
                    "<1e-300"
                    if pd.notna(x) and float(x) == 0.0
                    else f"{float(x):.2e}"
                    if pd.notna(x)
                    else ""
                )
            )

    st.dataframe(display_d, use_container_width=True, hide_index=True)

    st.download_button(
        label="⬇️ Download selected driver genes (CSV)",
        data=d.to_csv(index=False).encode("utf-8"),
        file_name=f"{lineage}_putative_driver_genes.csv",
        mime="text/csv",
    )

    st.info(
        "These genes are ranked by association with lineage fate probability. "
        "They should be interpreted as putative lineage-associated genes, "
        "not experimentally validated causal regulators."
    )

elif page == "Gene Explorer":
    st.subheader("Hematopoietic marker explorer")
    available = list(expression.columns)
    gene = st.selectbox("Gene", available)
    df = cells.copy()
    df["expression"] = expression[gene]
    left, right = st.columns([1.35, 1])
    with left:
        st.plotly_chart(scatter(df, "umap_1", "umap_2", "expression", f"{gene} expression", True), use_container_width=True)
    with right:
        ordered = df.sort_values("pseudotime")
        fig = px.scatter(ordered, x="pseudotime", y="expression", color="cluster", title=f"{gene} across pseudotime", opacity=0.45)
        fig.update_traces(marker={"size": 4})
        fig.update_layout(height=650, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    med = pd.DataFrame({"cluster": cells["cluster"], "expression": expression[gene]}).groupby("cluster", observed=True)["expression"].median().sort_values(ascending=False)
    st.markdown("#### Median expression by state")
    st.dataframe(med.rename("median_expression").reset_index(), use_container_width=True, hide_index=True)

elif page == "Biological Insights":
    st.subheader("Biological interpretation")

    st.markdown(
        """
        This section summarizes biologically interpretable patterns recovered
        from the CellRank fate model and gene–fate associations.

        ### Key lineage signatures

        **🩸 Erythroid commitment — `Ery_2`**  
        High fate probability is concentrated in erythroid populations.
        Top associated genes include **KLF1, ANK1, CA1, AHSP, SMIM1, and TFR2**,
        supporting a coherent erythroid differentiation program.

        **🟣 Megakaryocytic commitment — `Mega`**  
        The megakaryocyte terminal state shows strong enrichment for
        **GP9, VWF, CLEC1B, PF4, GP6, and ITGA2B**, consistent with platelet
        and megakaryocyte biology.

        **🔵 Lymphoid commitment — `CLP`**  
        The CLP fate is strongly associated with **VPREB1, VPREB3, CD79A,
        CD79B, DNTT, and EBF1**, consistent with early B-lineage specification.

        **🟠 Dendritic programs — `DCs_1` and `DCs_2`**  
        `DCs_1` contains markers such as **LILRA4, JCHAIN, IRF7, SPIB, and IRF8**,
        suggesting a strong plasmacytoid dendritic-cell-like program.
        `DCs_2` shows a broader myeloid/DC-associated profile including
        **AIF1, LSP1, CORO1A, and IRF8**.

        **🔴 `Mono_1` annotated fate**  
        Although the dataset-derived state is labeled `Mono_1`, its strongest
        fate-associated genes include **AZU1, MPO, ELANE, CTSG, and PRTN3**.
        This indicates a strong granulocytic/myeloid differentiation program,
        illustrating why computational state labels should be interpreted together
        with molecular signatures rather than as definitive mature-cell identities.
        """
    )

    st.markdown("### Fate-specific molecular signatures")

    selected = st.selectbox(
        "Inspect a terminal fate",
        list(fates.columns),
        key="insight_lineage",
    )

    dd = (
        drivers.loc[drivers["lineage"] == selected]
        .sort_values("correlation", ascending=False)
        .head(15)
    )

    c1, c2 = st.columns([1.15, 1])

    with c1:
        fig = px.bar(
            dd.sort_values("correlation"),
            x="correlation",
            y="gene",
            orientation="h",
            title=f"Top genes associated with {selected} fate",
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        summary = (
            pd.DataFrame({
                "cell_state": cells["cluster"],
                "fate_probability": fates[selected],
            })
            .groupby("cell_state", observed=True)["fate_probability"]
            .mean()
            .sort_values(ascending=False)
            .reset_index()
        )

        fig2 = px.bar(
            summary,
            x="fate_probability",
            y="cell_state",
            orientation="h",
            title=f"Mean {selected} fate probability by cell state",
        )
        fig2.update_layout(
            height=500,
            yaxis={"categoryorder": "total ascending"},
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.caption(
        "Interpretations are based on computational fate inference and "
        "gene–fate associations from this public dataset. Experimental validation "
        "would be required to establish causal regulatory mechanisms."
    )


elif page == "Methods":
    st.subheader("Methods & reproducibility")
    st.markdown(
        f"""
        **Dataset:** {meta.get('dataset', 'CellRank early human hematopoiesis')}  
        **Kernel:** `{meta.get('kernel', 'PseudotimeKernel')}`  
        **Pseudotime:** `{meta.get('time_key', 'palantir_pseudotime')}`  
        **Estimator:** `GPCCA`  
        **Terminal-state method:** `{meta.get('gpcca_terminal_method', 'top_n')}`  
        **CellRank:** `{meta.get('cellrank', 'unknown')}`  
        **Scanpy:** `{meta.get('scanpy', 'unknown')}`

        **Workflow**

        1. Filter genes detected in fewer than five cells.
        2. Library-size normalization to 10,000 counts/cell and `log1p` transform.
        3. Select 3,000 highly-variable genes for the neighborhood representation.
        4. PCA → k-nearest-neighbor graph → UMAP.
        5. Build a CellRank `PseudotimeKernel` from Palantir pseudotime.
        6. Use GPCCA to identify stable terminal macrostates.
        7. Compute cell-level fate probabilities.
        8. Correlate gene expression with fate probabilities to rank putative lineage drivers.

        **Limitations:** This is an educational/research portfolio workflow. Model-inferred states depend on
        parameters and the biological prior encoded by pseudotime. Driver-gene association is not proof of causality.
        """
    )
    st.json(meta)
