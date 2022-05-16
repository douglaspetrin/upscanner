PYTHON_VERSION = python3.8
PYENV_VERSION = 3.8.10

install:
	poetry config cache-dir $(HOME)/.cache/pypoetry/
	poetry config virtualenvs.create true
	poetry config virtualenvs.in-project true
	poetry env use $(PYENV_VERSION)
	poetry install
	poetry run python setup.py install
	poetry run playwright install
	poetry run pre-commit install

test:
	poetry run pytest tests/

clean:
	rm -rf .venv build dist scanner.egg* .mypy_cache .vscode .pytest_cache high-chance.json reports

mypy:
	poetry run mypy scanner

flake8:
	poetry run flake8 scanner

vulture:
	poetry run vulture scanner

bandit:
	poetry run bandit scanner/*

first:
	poetry run python scanner/app.py
