from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

required = [
    "app.py",
    "README.md",
    "requirements.txt",
    "requirements-analysis.txt",
    "scripts/prepare_data.py",
    "src/data_io.py",
    "docs/scientific_scope.md",
]

missing = [p for p in required if not (ROOT / p).exists()]
assert not missing, f"Missing repository files: {missing}"

readme = (ROOT / "README.md").read_text(encoding="utf-8")
for term in ["CellRank", "Scanpy", "GPCCA", "Streamlit", "human bone-marrow"]:
    assert term in readme, f"README missing expected term: {term}"

print("repository schema check: PASS")
