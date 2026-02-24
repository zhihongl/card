# AGENTS.md

## Cursor Cloud specific instructions

This is a Python CLI application (Credit Card Fraud Detector). No external services, databases, or Docker are required.

### Prerequisites

- **Python 3.9+** (Python 3.12 is pre-installed in the cloud environment)
- **pip** for dependency management

### Common commands

See `README.md` for full details. Key commands:

| Action | Command |
|--------|---------|
| Install deps | `pip install -r requirements.txt` |
| Run tests | `pytest -v` |
| Lint | `ruff check .` |
| Format check | `ruff format --check .` |
| Run app | `python3 -m fraud_detector <file_path> <threshold>` |

### Notes

- Use `python3` not `python` — the cloud environment may not have a `python` symlink.
- The sample input file is `transactions_file` at the repository root.
- Test resource files live in `tests/resources/`.
- `ruff` is used for both linting and formatting (configured in `pyproject.toml`).
