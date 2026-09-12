.PHONY: install-analysis prepare install-app app check

install-analysis:
	pip install -r requirements-analysis.txt

prepare:
	python scripts/prepare_data.py

install-app:
	pip install -r requirements.txt

app:
	streamlit run app.py

check:
	python -m compileall app.py scripts src tests
	python tests/test_repository_schema.py
