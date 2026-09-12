from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


REQUIRED_FILES = {
    "cells": "dashboard_cells.parquet",
    "fates": "fate_probabilities.parquet",
    "drivers": "driver_genes.csv",
    "expression": "marker_expression.parquet",
    "meta": "project_meta.json",
}


def processed_paths(base: Path) -> dict[str, Path]:
    return {key: base / name for key, name in REQUIRED_FILES.items()}


def outputs_available(base: Path) -> bool:
    return all(path.exists() for path in processed_paths(base).values())


def load_outputs(base: Path):
    paths = processed_paths(base)
    cells = pd.read_parquet(paths["cells"])
    fates = pd.read_parquet(paths["fates"])
    drivers = pd.read_csv(paths["drivers"])
    expression = pd.read_parquet(paths["expression"])
    meta = json.loads(paths["meta"].read_text(encoding="utf-8"))
    return cells, fates, drivers, expression, meta
