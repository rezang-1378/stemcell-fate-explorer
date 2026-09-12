# Scientific scope and limitations

## Question

Can single-cell state-transition modeling provide an interpretable view of early human hematopoietic differentiation that is suitable for an interactive regenerative-medicine portfolio application?

## Dataset

The project uses the public CellRank early-human-hematopoiesis dataset: CD34+ human bone-marrow cells profiled by 10x Chromium. It contains spliced/unspliced counts, annotated clusters, and Palantir pseudotime.

## Modeling choice

The pipeline uses Palantir pseudotime to construct a directional `PseudotimeKernel`. This is intentionally chosen over RNA velocity for this demonstration because the official CellRank hematopoiesis tutorial discusses biological inconsistencies of velocity direction in this particular dataset and demonstrates pseudotime as a practical alternative.

## Outputs

- low-dimensional cell atlas;
- inferred terminal states;
- cell-level fate probabilities;
- putative lineage driver genes;
- expression of selected hematopoietic markers across pseudotime.

## Interpretation limits

This is a computational demonstration, not a clinical decision system. Terminal states depend on model assumptions and analysis parameters. Correlation with fate probability does not establish causal regulation. Any candidate gene requires independent biological and experimental validation.

## Relevance to regenerative medicine

The workflow is reusable for stem-cell differentiation, cell-therapy characterization, disease-state transitions, and quality-control studies when suitable scRNA-seq data are available. A future extension could apply the same interface to mesenchymal stem-cell differentiation or treatment-response datasets more directly related to regenerative medicine.
