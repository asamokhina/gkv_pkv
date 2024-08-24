# Setup
```bash
## Make .venv with the desired python version.
# curl -LsSf https://astral.sh/uv/install.sh | sh
uv python install 3.11.9
uv venv --python "$(uv python find 3.11.9)"

uv pip install -e '.[dev,test]'

source .venv/bin/activate
pre-commit install
```

# Check code
```bash
ruff check src --fix
mypy src tests
pytest
```

# Lock requirements
```
uv pip compile pyproject.toml --universal -o requirements.txt --quiet
uv pip install -r requirements.txt
uv pip install --no-deps -e '.[dev,test]'
```
