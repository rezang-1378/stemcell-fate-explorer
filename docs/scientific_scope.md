# Scientific scope and limitations

## Research question

How are early human hematopoietic cells organized under a pseudotime-directed transition model, and which expression patterns are associated with inferred terminal fates?

## Implemented workflow

The preparation script loads CellRank's public human CD34+ bone-marrow dataset, preprocesses expression with Scanpy, and constructs a CellRank `PseudotimeKernel` using the supplied `palantir_pseudotime` field. Palantir is not recomputed, and RNA velocity is not the transition model used in this repository.

GPCCA computes 10 macrostates using the dataset's cluster annotations. The default configuration selects six terminal states with `top_n`, computes fate probabilities, and exports the top 100 gene–fate associations for each lineage. The dashboard reads those outputs rather than recalculating the model interactively.

## Interpretation

- Fate probabilities describe absorption into terminal states under the selected model. They are not direct experimental observations or calibrated clinical predictions.
- Gene–fate correlations are associations, not evidence of causal regulation.
- Pseudotime is an inferred ordering, not measured elapsed time.
- Dataset-derived terminal labels can represent heterogeneous populations and should be interpreted alongside molecular patterns.
- Biological plausibility of a marker pattern is not independent experimental validation.

## Evidence and reproducibility limits

The committed metadata documents one analysis of one public hematopoietic dataset. The repository's syntax and schema checks do not rerun the analysis or validate its numerical or biological conclusions.

Some package versions are pinned and selected preprocessing steps use fixed seeds. Full dependency locking, comprehensive parameter provenance, source checksums, parameter-sensitivity analysis, and independent biological validation remain limitations.

## Intended use and future directions

The current implementation is a research and educational exploration tool. Applying the workflow to other stem-cell systems, disease states, or perturbations would require suitable data, reassessment of preprocessing and modeling assumptions, and independent validation. Such applications are future directions rather than demonstrated capabilities or validated clinical uses.
